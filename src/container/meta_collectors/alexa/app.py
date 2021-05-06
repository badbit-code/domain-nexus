import asyncio
import queue
import aiohttp
import re
from psycopg2 import connect, extras
import requests
import os
from async_meta_api_gatherer import AsyncMetaAPIGatherer

regex = re.compile(r'RANK="(\d+)"')

class AlexaMetaGatherer(AsyncMetaAPIGatherer):

    def __init__(self, conn):
        AsyncMetaAPIGatherer.__init__(
            self,
            conn,
            get_batch_query = """
                SELECT domain.name as domain, top_level_domain.name as tld, domain.tld as tld_id
                FROM domain, top_level_domain 
                WHERE domain.alexa_score is NULL 
                AND top_level_domain.id = domain.tld
                ORDER BY domain.updated_at 
                LIMIT 500
                OFFSET 0;""",

            update_batch_query = """
                UPDATE domain
                SET alexa_score = temp.score
                FROM (VALUES %s) AS temp(score, domain, tld)
                WHERE domain.id = uuid_generate_v3(uuid_ns_url(), temp.domain || '.' || temp.tld)
                """
        )

    async def session_job(self, query_tuple, session):

        domain, tld_string, tld_id = query_tuple

        domain_name = (domain + "." + tld_string).lower()

        async with session.get(f"http://data.alexa.com/data?cli=2&url={domain_name}") as response:
            
            result = str(await response.read())

            re_result = re.search(regex, result)

            if re_result:

                return (int(re_result.groups()[0]), domain, tld_id)

            return (0, domain, tld_id)

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

    gatherer = AlexaMetaGatherer(conn)

    for i in range(10):
        gatherer.run()







    