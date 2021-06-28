"""
Transfers data from the primary collection database to the 
front-end database.

This is a PostgreSQL to MySQL transfer to support the default 
built-in MySQL DB of the front-end.
"""
from psycopg2.extras import RealDictCursor, execute_values
from db import DBConnector
import tempfile
from sqlalchemy import create_engine, types
import pandas as pd

"""
A data dump file is created from the following query,
which is the used to do a batch upload to the mysql 
data base. 
"""
db = DBConnector()
conn = db.conn
cursor = conn.cursor(cursor_factory=RealDictCursor)


# Create a temporary table and copy all acceptable domains to it. 
cursor.execute(
"""
CREATE TEMPORARY TABLE transfer_table(
    domain text,
    available text,
    ACE int,
    search boolean,
    expired timestamptz,
    registered timestamptz,
    category text
)
"""
)
conn.commit()

cursor.execute(
"""
INSERT INTO transfer_table (domain, registered, expired, ACE)
SELECT
    (name || '.' || tld) as domain, 
    whois_data.registered as registered, 
    whois_data.expires as expired, 
    alexa_data.alexa_score as ACE
FROM domain, whois_data, alexa_data
WHERE whois_data.id = domain.id AND alexa_data.id = domain.id
"""
)

conn.commit()

# Copy table to tempfile

transfer_file = tempfile.TemporaryFile("w+")

cursor.copy_to(transfer_file,"transfer_table", sep=",")

transfer_file.seek(0)

conn.close()

# Transfer the file to the remote server.
# Clear Existing DB first ?
engine = create_engine('mysql+pymysql://mcdanie1_nexus:22*x$KoFRHfy@domain-nex.us/mcdanie1_nexus') # enter your password and database names here

df = pd.read_csv(transfer_file,sep=',', encoding='utf8', names=("domain", "available", "ACE", "search", "expired", "registered", "category"))

df.to_sql('domains',con=engine,index=False,if_exists='append') 

"""
domain = string (google.com)
available = month/day = word/number (expiration date based on registrar expire, godaddy = 90, sedo = 70)
unique = yes/no (is there other domains in .org .net .com space with same name)
ACE = yes/no (has wiki or alexa results, ace = accredited, cited, or ... its just marketing )
age = how old is the domain vs registered last
category = string from fuzzing ticket
Search = good / neutral (does it result in its own domain name search on google in top 100 results, if yes then good, if no then neurtral)
"""

transfer_file.close()


    