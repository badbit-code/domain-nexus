from psycopg2 import connect, extras
import os
from async_meta_api_gatherer import AsyncMetaAPIGatherer
import whois

class WhoisMetaGatherer(AsyncMetaAPIGatherer):

    def __init__(self, conn):
        AsyncMetaAPIGatherer.__init__(
            self,
            conn,
            get_batch_query = """
                SELECT domain.name as domain, top_level_domain.name as tld, domain.id as id
                FROM domain, top_level_domain 
                WHERE (domain.registered < timestamp '1980-01-01 00:00:00' OR domain.expired < timestamp '1980-01-01 00:00:00')
                AND top_level_domain.id = domain.tld
                ORDER BY domain.updated_at 
                LIMIT 500
                OFFSET 0;""",

            update_batch_query = """
                UPDATE domain
                SET registered = temp.registered, expired = temp.expired
                FROM (VALUES %s) AS temp(registered, expired, domain_id)
                WHERE domain.id = uuid(domain_id)
                """,
            USE_THREADS = True
        )

    def threaded_job(self, query_tuple):

        domain, tld_string, domain_id = query_tuple

        domain_name = (domain + "." + tld_string).lower()

        w = whois.whois(domain_name)

        if w:
            if type(w["expiration_date"]) is list:
                expired = w["expiration_date"][0]
            else:
                expired = w["expiration_date"]

            if type(w["creation_date"]) is list:
                registered = w["creation_date"][0]
            else:
                registered = w["creation_date"]

            return (registered, expired, domain_id)

        

        return None

if __name__ == "__main__":
    conn = connect(
        host="database",
        dbname=os.getenv("POSTGRES_DB"),
        user=os.getenv("POSTGRES_USER"),
        password=os.getenv("POSTGRES_PASSWORD"),
        port=os.getenv("DB_PORT", 5432),
        sslmode=os.getenv("DB_SSL_MODE", None),
        sslrootcert=os.getenv("DB_SSL_CERT_PATH", None),
    )

    gatherer = WhoisMetaGatherer(conn)

    for i in range(1):
        gatherer.run()







    