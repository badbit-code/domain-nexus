from psycopg2 import connect, extras
import os
from async_meta_api_gatherer import AsyncMetaAPIGatherer

class WikiMetaGatherer(AsyncMetaAPIGatherer):

    def __init__(self, conn):
        AsyncMetaAPIGatherer.__init__(
            self,
            conn,
            get_batch_query = """
                SELECT domain.name as domain, top_level_domain.name as tld, domain.id as id
                FROM domain, top_level_domain 
                WHERE domain.HAS_WIKI is NULL 
                AND top_level_domain.id = domain.tld
                ORDER BY domain.updated_at 
                LIMIT 500
                OFFSET 0;""",

            update_batch_query = """
                UPDATE domain
                SET HAS_WIKI = temp.HAS_WIKI
                FROM (VALUES %s) AS temp(HAS_WIKI, domain_id)
                WHERE domain.id = uuid(domain_id)
                """,
            sleep = 1.0
            #USE_THREADS = True
        )

    async def session_job(self, query_tuple, session):

        domain, tld_string, tld_id = query_tuple

        domain_name = (domain + "." + tld_string).lower()

        async with session.get(f"https://en.wikipedia.org/w/api.php?action=opensearch&search={domain_name}&limit=max&namespace=0&format=json&profile=strict") as response:
            
            
            try:
                if len((await response.json())[1]) > 0:
                    print("HAVE TRUE  for", domain_name)
                    return (True, tld_id)
            except:
                print("Query Failed")
                print(str(await response.read()))

                return None
            
            return (False, tld_id)

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

    gatherer = WikiMetaGatherer(conn)

    for i in range(10):
        gatherer.run()







    