import asyncio
import queue
import aiohttp
import re
from psycopg2 import connect, extras
import requests
import os
import time

class AsyncMetaAPIGatherer:

    def __init__(
        self, 
        conn,
        get_batch_query:str,
        update_batch_query:str,
        USE_THREADS: bool = False,
        sleep: float = 0,
        max_concurrent_tasks: int = 100

    ):
        """
        get_batch_query: The query to send to DB to receive a batch of rows to update
        update_batch_query: The query to send to DB to update rows after tasks have completed
        USE_THREAD: If True, threads are used instead of asyncio tasks
        sleep - Amount of time to delay requests in a single task. 
        max_concurrent_requests - Maximum number of simultaneous tasks. 
        """

        self.get_batch_query = get_batch_query
        self.update_batch_query = update_batch_query
        self.max_concurrent_requests = max_concurrent_tasks
        self.batch_query_queue = queue.Queue()
        self.conn = conn
        self.cursor = conn.cursor()
        self.start_time = 0
        self.USE_THREADS = USE_THREADS
        self.sleep = sleep

    

    async def session_job(self, query_tuple, session):
        """
        Receives query tuple that matches single row result from get_batch_query
        and should return a query tuple that matches the format for the update_batch_query.

        May return None, indicating there is no result and applicable row should not be updated. 
        """
        
        return None

    async def session_task(self, query_results,updated_results, session):
        try:
            while True:
                
                if self.sleep > 0:
                    await asyncio.sleep(self.sleep)

                tuple = query_results.get(block=False);
                try:

                    result = await self.session_job(tuple, session)

                    if result is not None:

                        updated_results.append(result)
                except:

                    import traceback

                    print("failed to get results for: ", *tuple)
                    
                    traceback.print_exc()

        except queue.Empty:
            pass

    async def aio_run(self, query_results, updated_results):

        tasks = []
    
        async with aiohttp.ClientSession() as session: 

            for i in range(self.max_concurrent_requests):

                t = self.session_task(query_results, updated_results, session)

                tasks.append(t)

            await asyncio.gather(*tasks)

    def threaded_job(self, query_tuple):
        """
        Receives query tuple that matches single row result from get_batch_query
        and should return a query tuple that matches the format for the update_batch_query.

        May return None, indicating there is no result and applicable row should not be updated. 
        """
        
        return None

    def threaded_task(self, query_results, updated_results):
        try:
            while True:

                if self.sleep > 0:
                    time.sleep(self.sleep)

                tuple = query_results.get(block=False);
                
                try:

                    result = self.threaded_job(tuple)

                    if result is not None:

                        updated_results.append(result)
                except:

                    import traceback

                    print("failed to get results for: ", *tuple)
                    
                    traceback.print_exc()

        except queue.Empty:
            pass


    def threaded_run(self, query_results, updated_results):

        from threading import Thread

        tasks = []

        for i in range(self.max_concurrent_requests):
            thread_task = Thread(target=self.threaded_task, args=(query_results, updated_results))
            thread_task.start()
            tasks.append(thread_task)

        for task in tasks:
            task.join()

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

        if self.USE_THREADS:

            self.threaded_run(query_results, updated_results)

        else:

            future = asyncio.ensure_future(self.aio_run(query_results, updated_results))
    
            asyncio.get_event_loop().run_until_complete(future)

        self.update_batch(updated_results)

        print(f"Batch took {time.time()-self.start_time} seconds")
