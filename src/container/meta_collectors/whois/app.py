from db import DBConnector
from async_meta_api_gatherer import AsyncMetaAPIGatherer
import whois

class WhoisMetaGatherer(AsyncMetaAPIGatherer):

    def __init__(self, conn):
        AsyncMetaAPIGatherer.__init__(
            self,
            conn,
            get_batch_query = """
                SELECT domain.name as domain, top_level_domain.name as tld
                FROM domain, top_level_domain 
                WHERE (domain.registered is NULL  OR domain.expired is NULL )
                AND top_level_domain.id = domain.tld
                ORDER BY domain.updated_at 
                LIMIT 500
                OFFSET 0;""",

            update_batch_query = """
                UPDATE domain
                SET registered = temp.registered, expired = temp.expired
                FROM (VALUES %s) AS temp(registered, expired, domain, tld)
                WHERE domain.id = uuid_generate_v3(uuid_ns_url(), temp.domain || '.' || temp.tld)
                """,
            USE_THREADS = True,
            max_concurrent_tasks=50,
            sleep=0.5 
        )

    def threaded_job(self, query_tuple):

        domain, tld_string = query_tuple

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

            return (registered, expired, domain, tld_string)

        return None

def scheduledJob():

    dbm = DBConnector()
    
    conn = dbm.conn

    gatherer = WhoisMetaGatherer(conn)

    for i in range(100): 

        gatherer.run()


if __name__ == "__main__":
    
    from time import sleep

    while True:

        scheduledJob()

        sleep(60)







    