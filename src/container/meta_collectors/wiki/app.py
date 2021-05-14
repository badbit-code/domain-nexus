from db import DBConnector
from async_meta_api_gatherer import AsyncMetaAPIGatherer

class WikiMetaGatherer(AsyncMetaAPIGatherer):

    def __init__(self, conn):
        AsyncMetaAPIGatherer.__init__(
            self,
            conn,
            get_batch_query = """
                SELECT domain.name as domain, top_level_domain.name as tld
                FROM domain
                , top_level_domain 
                WHERE domain.HAS_WIKI is NULL 
                AND top_level_domain.id = domain.tld
                ORDER BY domain
                .updated_at 
                LIMIT 500
                OFFSET 0;""",

            update_batch_query = """
                UPDATE domain
                SET HAS_WIKI = temp.HAS_WIKI
                FROM (VALUES %s) AS temp(HAS_WIKI, domain, tld)
                WHERE domain.id = uuid_generate_v3(uuid_ns_url(), temp.domain || '.' || temp.tld)
                """,
            sleep = 1.0
            #USE_THREADS = True
        )

    async def session_job(self, query_tuple, session):

        domain, tld_string = query_tuple

        domain_name = (domain + "." + tld_string).lower()

        async with session.get(f"https://en.wikipedia.org/w/api.php?action=opensearch&search={domain_name}&limit=max&namespace=0&format=json&profile=strict") as response:
            
            
            try:
                if len((await response.json())[1]) > 0:
                    print("HAVE TRUE  for", domain_name)
                    return (True, domain, tld_string)
            except:
                print("Query Failed")
                print(str(await response.read()))

                return None
            
            return (False, domain, tld_string)

        return None

def scheduledJob():

    dbm = DBConnector()
    
    conn = dbm.conn

    gatherer = WikiMetaGatherer(conn)

    for i in range(100): 

        gatherer.run()


if __name__ == "__main__":
    
    from time import sleep

    print("Running")

    while True:

        scheduledJob()

        sleep(60)







    