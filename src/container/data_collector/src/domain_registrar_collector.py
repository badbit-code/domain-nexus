#import pandas as pd
#import requests
from io import StringIO
from datetime import datetime
from psycopg2.extras import RealDictCursor, execute_values
from psycopg2 import DatabaseError
import numpy as np


class DomainRegistrarCollector:
    """
    Base class for a collector object that gathers domain data from a domain registrar's
    database
    """

    def __init__(self):

        self.pending_domains = []
        self.tld = {}
        self.registrar = {}

        self.batch_files = []

        self.batch_size = 100000

        self.batch_limit = 5

        self.batch_file_count = 0

    @property 
    def HAS_PENDING_UPLOADS(self):
        return len(self.pending_domains) > 0
    
    @property 
    def HAS_PENDING_BATCH_FILES(self):
        return len(self.batch_files) > 0

    def add_raw_entry(self, entry):
        
        self.pending_domains.append(entry)

        if len (self.pending_domains) >= self.batch_size:

            self.create_temp_batch_file()


    def create_temp_batch_file(self):

        if self.HAS_PENDING_UPLOADS:

            batch_count = len(self.pending_domains)

            batch = [self.map_to_internal_schema(row) for row in self.pending_domains]

            batch_fn = f"temp_batch_{self.batch_file_count}"

            self.batch_file_count += 1

            with open(batch_fn,"w+") as file:

                file.write(
                        "\n".join([",".join([str(v) for v in d.values()]) for d in batch])
                    )

            self.batch_files.append(batch_fn)

            print(f"Created temp file {batch_fn} with {batch_count} pending domain entries")

            self.pending_domains.clear()


    def upload_batch_files(self, cursor, max_number_of_files = 500):

        import os

        for batch_fn in self.batch_files[:max_number_of_files]:

            print(f"Uploading {batch_fn}")

            with open(batch_fn,"r") as file:

                cursor.copy_from(
                    file,
                    "temp_domains",
                    sep=",",
                    columns=("name", "tld", "registrar", "expired", "registered"),
                )
            
            print(f"Clearing and deleting {batch_fn}")

            os.remove(batch_fn)

            self.batch_files.remove(batch_fn)

    def gather(self):
        """
        Connect to registrar's service and collect a list of domains. Separate results
        into a list of dicts
        """
        pass

    def map_to_internal_schema(self, row:dict) -> dict:
        """
        Map the pending domains to a list of dicts that adhere to the internal
        DB schema

        Minimum values MUST be
        {
            name: str, #Name of the domain following TLD
            tld: str,
            registrar: int, # The registrar id value in the registrar table
            expired: epoch_int, # Can be 0, indicating that a subsequent DB pass must be made to gather the expirer information
            registered: epoch_int, # Can be 0, indicating that a subsequent DB pass must be made to gather the created information
        }
        """
        return row

    @property 
    def HAS_PENDING_UPLOADS(self):
        return len(self.pending_domains) > 0

    def get_tld_mapping(self, tld:str, conn):

        if tld not in self.tld:
            
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            try:
                cursor.execute(f"INSERT INTO top_level_domain(name) VALUES ('{tld}')")    
            
                conn.commit()
            except:
                conn.rollback()
                pass

            cursor.execute(f"SELECT name,id FROM top_level_domain")

            result = cursor.fetchall()
            
            print(result)

            self.tld = { row["name"]:row["id"] for row in result}

            print(self.tld)

        return self.tld[tld]

    def get_registrar_mapping(self, registrar:str, conn):

        if registrar not in self.registrar:
            
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            try:
                cursor.execute(f"INSERT INTO registrar(name) VALUES ('{registrar}')")    
            
                conn.commit()
            except:
                conn.rollback()
                pass

            cursor.execute(f"SELECT name,id FROM registrar")

            result = cursor.fetchall()
            
            print(result)

            self.registrar = { row["name"]:row["id"] for row in result}

            print(self.registrar)

        return self.registrar[registrar]


    def upload_to_db(self, conn):

        import math

        from io import StringIO

        cursor = conn.cursor(cursor_factory=RealDictCursor)

        new_domains = self.map_to_internal_schema(conn)

            print(f"Uploading {len(self.pending_domains)} domain names from Godaddy. Current number of entries is {start_count}")

            print("Creating temporary table")

            # Using a temporary table to reduce network overhead and exploit local data processing on
            # PostgreSQL DB
            cursor.execute(
                """
                CREATE TEMPORARY TABLE temp_domains(
                    name text,
                    tld int,
                    registrar int,
                    expired timestamp,
                    registered timestamp
                )
            """
            )

            # Make sure any pending batch data is added
            self.create_temp_batch_file()

            self.upload_batch_files(cursor, self.batch_limit)
            
            # Update registrar table. Get batch of registrar names that do not have corresponding rows in 
            # registrar and create new rows for this batch. Make sure all names are lowercase
            cursor.execute(
                """
                WITH reg AS(
                    SELECT DISTINCT (LOWER(registrar)) r 
                    FROM temp_domains as td 
                    WHERE NOT EXISTS( SELECT * from registrar WHERE name=LOWER(td.registrar) ) 
                )
                INSERT INTO registrar(name)
                SELECT r FROM reg
                ON CONFLICT (name) DO NOTHING
                """
            )
            conn.commit()

            # Update top_level_domain table. Get batch of tld names that do not have corresponding rows in 
            # top_level_domain and create new rows for this batch. Make sure all names are lowercase
            cursor.execute(
                """
                WITH tld AS(
                    SELECT DISTINCT (LOWER(tld)) t 
                    FROM temp_domains as td 
                    WHERE NOT EXISTS( SELECT * from top_level_domain WHERE name=LOWER(td.tld) ) 
                )
                INSERT INTO top_level_domain(name)
                SELECT t FROM tld
                ON CONFLICT (name) DO NOTHING
            """
            )
            conn.commit()

            # Finally insert any new domains.  
            cursor.execute(
                """
                INSERT INTO domain (name,tld,registrar)
                SELECT 
                    LOWER(name),
                    (SELECT id from top_level_domain WHERE name=LOWER(temp_domains.tld)),
                    (SELECT id from registrar WHERE name=LOWER(temp_domains.registrar))
                FROM temp_domains
                ON CONFLICT (id) DO NOTHING
            """
            )

            conn.commit()

            print("Dropping temporary table")

            cursor.execute("""DROP TABLE temp_domains""")

            conn.commit()

            end_count = get_row_count("domain", cursor)

            delta_count = end_count - start_count

            print(f"Uploaded {delta_count} domains. Current number of entries is {end_count}")

            if self.HAS_PENDING_UPLOADS:
                print(f"{len(self.pending_domains)} pending domains reamain to be processed")

    def insert_new_domains(self, conn, df: pd.DataFrame):
        """
        Using psycopg2.extras.execute_values() to insert the dataframe
        """
        # Create a list of tupples from the dataframe values
        tuples = [tuple(x) for x in df.to_numpy()]
        cursor = conn.cursor()
        values = [
            cursor.mogrify(
                """(%s, (SELECT id FROM top_level_domain WHERE name = %s), (SELECT id FROM registrar WHERE name = %s))""",
                tup,
            ).decode("utf8")
            for tup in tuples
        ]
        # SQL quert to execute
        query = f"""INSERT INTO domain (name, tld, registrar) 
                    VALUES {",".join(values)} ON CONFLICT DO NOTHING"""

        # try:
        cursor.execute(query, tuples)
        conn.commit()
        # except (Exception, DatabaseError) as error:
        #    print("Error: %s" % error)
        #    conn.rollback()
        #    cursor.close()
        #    return 1
        print("execute_values() done")
        cursor.close()

    def insert_new_tlds(self, conn, tld_names: np.ndarray):
        """
        Using cursor.mogrify() to build the bulk insert query
        then cursor.execute() to execute the query
        """
        # SQL quert to execute
        cursor = conn.cursor()
        values = [cursor.mogrify("(%s)", (tld,)).decode("utf8") for tld in tld_names]
        query = f"""INSERT INTO top_level_domain (name) 
                    SELECT 
                    NewTLD.name 
                    FROM 
                    (
                        VALUES 
                        {",".join(values)}
                    ) AS NewTLD (name) 
                    WHERE 
                    NOT EXISTS (
                        SELECT 
                        1 
                        FROM 
                        top_level_domain AS TLD 
                        WHERE 
                        TLD.name = NewTLD.name
                    )"""
        try:
            cursor.execute(query, (tuple(tld_names),))
            conn.commit()
        except (Exception, DatabaseError) as error:
            print("Error: %s" % error)
            conn.rollback()
            cursor.close()
            return 1
        print("update_tld() done")
        cursor.close()


class GoDaddyCollector(DomainRegistrarCollector):
    def map_to_internal_schema(self, conn) -> [dict]:
        from datetime import datetime

        return [
            {
                "name": domain["domainName"].split(".")[0],
                "tld": self.get_tld_mapping(domain["domainName"].split(".")[1], conn),
                "registrar": self.get_registrar_mapping("godaddy", conn),
                "expired": datetime.fromtimestamp(0).strftime("%m/%d/%Y %H:%M:%S"),
                "registered": datetime.fromtimestamp(0).strftime("%m/%d/%Y %H:%M:%S"),
            }
    
    def stream_json_file(self, json_file_path):

        print(f"Creating upload batches from {json_file_path}")

        with open(json_file_path, "r", encoding = 'utf-8') as file:

            pos = 0

            file.seek(pos)

            file.tell
            
            while True:
                str = file.read(1)

                if str == "":
                    break
                
                if str == "m" and file.read(3) == "eta":
                    print("Collecting Meta Information")
                    meta= get_json_object_from_pos(file)
                    print(meta)

                if str == "d" and file.read(3) == "ata":
                    while True:
                        entry = get_json_object_from_pos(file)
                        if entry is None:
                            break
                        self.add_raw_entry(entry)

    def test_gather(self):

    
    def fetch_data(self):

        from ftplib import FTP
        from zipfile import ZipFile
        from io import BytesIO
        import json
        import os

        godaddy_domains = []
        with FTP("ftp.godaddy.com", "auctions") as ftp:
            files_needed = [
                x
                for x in ftp.nlst()
                if x.startswith("all_listings") and not x.startswith("all_listings_")
            ]
            for file_name in files_needed:
                print(f"Downloading {file_name}")
                with BytesIO() as tempfile:
                    ftp.retrbinary(f"RETR {file_name}", tempfile.write)
                    with ZipFile(tempfile) as zip_:
                        file_to_extract = file_name.rsplit(".", 1)[0]
                        with zip_.open(file_to_extract) as json_contents:
                            file_to_extract = file_name.rsplit(".", 1)[0]
                            json_data = json.loads(json_contents.read().decode("utf-8"))
                            godaddy_domains.extend(json_data["data"])
        return godaddy_domains

    def add_registrar(self, conn):
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO registrar (name) VALUES ('godaddy') ON CONFLICT DO NOTHING"
        )
        conn.commit()


class SedoCollector(DomainRegistrarCollector):

    def fetch_data(self) -> StringIO:
        sedo_url = "https://sedo.com/fileadmin/documents/resources/expiring_domain_auctions.csv"
        response = requests.get(sedo_url)
        return StringIO(response.content.decode("utf-16"))

    def preprocess_data(self, sedo_csv) -> pd.DataFrame:
        sedo_df = pd.read_csv(sedo_csv, delimiter=";", encoding="utf-16", skiprows=1)

        # We don't need the links for each domain
        sedo_df.drop(["Link"], axis=1, inplace=True)
        # tld is removed from domain name since it's stored seperately
        sedo_df["Domain Name"] = sedo_df["Domain Name"].apply(lambda x: x.split(".")[0])
        # rename columns to match db column names
        sedo_df.rename(
            columns={
                "Domain Name": "name",
                "Start Time": "start_time",
                "End Time": "end_time",
                "Reserve Price": "reserve_price",
                "Domain is IDN": "domain_is_idn",
                "Domain has hyphen": "domain_has_hyphen",
                "Domain has numbers": "domain_has_numbers",
                "Domain Length": "domain_length",
                "TLD": "tld",
                "Traffic": "traffic",
            },
            inplace=True,
        )
        sedo_df["registrar"] = "sedo"

        return sedo_df

    def add_registrar(self, conn):
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO registrar (name) VALUES ('sedo') ON CONFLICT DO NOTHING"
        )
        conn.commit()

    def insert_new_domains(self, conn, df: pd.DataFrame):
        """
        Using psycopg2.extras.execute_values() to insert the dataframe
        """
        # Create a list of tupples from the dataframe values
        tuples = [tuple(x) for x in df.to_numpy()]
        cursor = conn.cursor()
        values = [
            cursor.mogrify(
                """(%s, (SELECT id FROM top_level_domain WHERE name = %s), (SELECT id FROM registrar WHERE name = %s))""",
                tup,
            ).decode("utf8")
            for tup in tuples
        ]
        # SQL quert to execute
        query = f"""INSERT INTO domain (name, tld, registrar) 
                    VALUES {",".join(values)} ON CONFLICT DO NOTHING"""

        # try:
        cursor.execute(query, tuples)
        conn.commit()
        # except (Exception, DatabaseError) as error:
        #    print("Error: %s" % error)
        #    conn.rollback()
        #    cursor.close()
        #    return 1
        print("execute_values() done")
        cursor.close()
