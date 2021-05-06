#import pandas as pd
#import requests
from io import StringIO
from datetime import datetime
from psycopg2 import connect
from psycopg2.extras import RealDictCursor

class DomainRegistrarCollector:
    """
    Base class for a collector object that gathers domain data from a domain registrar's
    database
    """

    def __init__(self):

        self.pending_domains = []
        self.tld = {}
        self.registrar = {}

    def gather(self):
        """
        Connect to registrar's service and collect a list of domains. Separate results
        into a list of dicts
        """
        pass

    def map_to_internal_schema(self) -> [dict]:
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
        return []

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

        from psycopg2.extras import RealDictCursor, execute_values

        cursor = conn.cursor(cursor_factory=RealDictCursor)

        new_domains = self.map_to_internal_schema(conn)

        if len(new_domains) > 0:

            # Insert in batches of 100
            batch_size = 200000

            # columns=new_domains[0].keys()

            # cursor.execute("""DROP TABLE temp_domains""")
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

            for batch_id in range(math.ceil(len(self.pending_domains) / batch_size)):

                if batch_id > 5:
                    break

                batch = new_domains[
                    (batch_id * batch_size) : (
                        min(len(new_domains), batch_id * batch_size + batch_size)
                    )
                ]

                data = StringIO()

                data.write(
                    "\n".join([",".join([str(v) for v in d.values()]) for d in batch])
                )

                data.seek(0)

                cursor.copy_from(
                    data,
                    "temp_domains",
                    sep=",",
                    columns=("name", "tld", "registrar", "expired", "registered"),
                )

            cursor.execute(
                """
                INSERT INTO domains (name,tld,registrar,expired,registered)
                SELECT name,tld,registrar,expired,registered FROM temp_domains
                ON CONFLICT (id) DO NOTHING
            """
            )

            conn.commit()

            self.pending_domains.clear()


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
            for domain in self.pending_domains
        ]

    def test_gather(self):

        from ftplib import FTP
        from zipfile import ZipFile
        from io import BytesIO
        import json
        import os
        from typing import Generator

        with open("./all_listings3.json", "r") as file:

            json_data = json.loads(file.read())

            self.pending_domains.extend(json_data["data"])

    def gather(self):

        from ftplib import FTP
        from zipfile import ZipFile
        from io import BytesIO
        import json
        import os
        from typing import Generator

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

                            self.pending_domains.extend(json_data["data"])
                break;


#class SedoCollector(DomainRegistrarCollector):
#
#    def fetch_data(self) -> StringIO:
#        sedo_url = "https://sedo.com/fileadmin/documents/resources/expiring_domain_auctions.csv"
#        response = requests.get(sedo_url)
#        return StringIO(response.content.decode("utf-16"))
#
#    def preprocess_data(self, sedo_csv) -> pd.DataFrame:
#        sedo_df = pd.read_csv(sedo_csv, delimiter=';', encoding='utf-16', skiprows=1)
#        
#        # We don't need the links for each domain
#        sedo_df.drop(['Link'], axis=1, inplace=True)
#        # tld is removed from domain name since it's stored seperately
#        sedo_df['Domain Name'] = sedo_df['Domain Name'].apply(lambda x: x.split('.')[0])
#        # rename columns to match db column names
#        sedo_df.rename(columns={"Domain Name": "name",
#                                  "Start Time":"start_time",
#                                  "End Time":"end_time",
#                                  "Reserve Price":"reserve_price",
#                                  "Domain is IDN": "domain_is_idn",
#                                  "Domain has hyphen": "domain_has_hyphen",
#                                  "Domain has numbers": "domain_has_numbers",
#                                  "Domain Length": "domain_length",
#                                  "TLD": "tld",
#                                  "Traffic": "traffic"})
#
#        return sedo_df