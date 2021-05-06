import asyncio
import queue
import aiohttp
import re
from psycopg2 import connect, extras
import requests
import os

class AsyncMetaAPIGatherer:

    def __init__(
        self, 
        conn,
        get_batch_query:str,
        update_batch_query:str,
    ):

        self.get_batch_query = get_batch_query
        self.update_batch_query = update_batch_query
        self.max_concurrent_requests = 100
        self.batch_query_queue = queue.Queue()
        self.conn = conn
        self.cursor = conn.cursor()
        self.start_time = 0

    

    async def job(self, query_tuple, sessionZZ):
        """
        Receives query tuple that matches single row result from get_batch_query
        and should return a query tuple that matches the format for the update_batch_query.

        May return None, indicating there is no result and applicable row should not be updated. 
        """
        
        return None

    async def task(self, query_results, updated_results, session):
        try:
            while True:
                tuple = query_results.get(block=False);
                try:

                    result = await self.job(tuple, session, updated_results)

                    if result is not None:

                        updated_results.append(result)
                except:

                    print("failed to get results for: ", *tuple)

        except queue.Empty:
            pass

    async def aio_run(self, query_results, updated_results):

        tasks = []
    
        async with aiohttp.ClientSession() as session: 

            for i in range(self.max_concurrent_requests):

                t = self.task(query_results, updated_results, session)

                tasks.append(t)

            await asyncio.gather(*tasks)

    def get_batch(self):

        self.cursor.execute(self.get_batch_query)

        query_results = queue.Queue()

        for tuple in self.cursor.fetchall():
            query_results.put(tuple)

        return query_results

    def update_batch(self, updated_results):

        extras.execute_values(self.cursor, self.update_batch_query, updated_results)

        self.conn.commit()

    def run(self):

        import time

        self.start_time = time.time()

        query_results = self.get_batch()

        updated_results = []

        future = asyncio.ensure_future(self.aio_run(query_results, updated_results))
    
        asyncio.get_event_loop().run_until_complete(future)

        self.update_batch(updated_results)

        print(f"Batch took {time.time()-self.start_time} seconds")


regex = re.compile(r'RANK="(\d+)"')

class AlexaMetaGatherer(AsyncMetaAPIGatherer):

    def __init__(self, conn):
        AsyncMetaAPIGatherer.__init__(
            self,
            conn,
            get_batch_query = """
                SELECT domains.name as domain, top_level_domain.name as tld, domains.tld as tld_id
                FROM domains, top_level_domain 
                WHERE domains.alexa_score is NULL 
                AND top_level_domain.id = domains.tld
                ORDER BY domains.updated_at 
                LIMIT 500
                OFFSET 0;""",

            update_batch_query = """
                UPDATE domains
                SET alexa_score = temp.score
                FROM (VALUES %s) AS temp(score, domain, tld)
                WHERE domains.id = uuid_generate_v3(uuid_ns_url(), temp.domain || '.' || temp.tld)
                """
        )

    async def job(self, query_tuple, session, results):

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
        # sslmode='verify-ca',
        # sslrootcert="./root.crt"
    )

    gatherer = AlexaMetaGatherer(conn)

    for i in range(10):
        gatherer.run()







    