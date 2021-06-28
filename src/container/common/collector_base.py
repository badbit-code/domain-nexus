from typing import List, Tuple
from db import DBConnector
from psycopg2.extensions import AsIs
import psycopg2.extras
from typing import Generator
import asyncio
import queue
import threading

psycopg2.extras.register_uuid()

class MetaCollectorBase:

    aoc_table = ""

    sot_table = ""

    def __init__(self):
        self.schedule = None
        self.number_of_threads = 4;
        self.queue = queue.Queue()

    def __init_subclass__(sub_class, *, aoc_table:str="",  table_schema = [], sot_table:str = "domain"):
        """
        aoc_table       =   name of the table this collector controls

        table_schema    =   table should contain a list of column
                            definitions which will defined the PostgreSQL table
                            that the collector sublass will manage. 
                        
                            In addition to the defined columns, the table's primary
                            will match the SoT domain table's primary.
        """


        sub_class.sot_table = sot_table    
        sub_class.aoc_table = aoc_table    

        if aoc_table and table_schema:
            MetaCollectorBase._createTable(aoc_table, table_schema)

        
    def _createTable(table_name:str, table_schema: List[str]):

        table_schema.insert(0, "id UUID NOT NULL")

        table_query = ",\n".join(table_schema)

        table_query = f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            primary_id bigserial primary key, 
            {table_query},
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            CONSTRAINT cstr_{table_name}
                FOREIGN KEY(id)
                    REFERENCES domain(id)
                    ON DELETE SET NULL
        )
        """
        
        #Use default DB connection
        db = DBConnector();

        #Query the DB with new data table
        conn = db.conn;

        with conn:
            with conn.cursor() as curs:
                curs.execute(table_query);
        
        #Close the db until the next query 
        db.close()

    def _clearData():
        """
        Remove any rows that do not have matching entries in the SoT 
        table.
        """

    def _getBatches(self, size:int=500) -> List[List[dict]]:
        """
        Returns a batch of domain names that do not have entries
        within the table this class is responsible for. 

        size = Maximum number of entries to return. 
        """
        batches = []
        
        db = DBConnector();

        #Query the DB with new data table
        conn = db.conn;

        with conn:
            with conn.cursor() as curs:

                batch_size = size * self.number_of_threads

                curs.execute(f"Select l.id,l.name,l.tld from {self.sot_table} l where NOT EXISTS ( SELECT NULL from {self.aoc_table} r where r.id = l.id ) LIMIT {batch_size} ")

                batch = curs.fetchall()

                batch_size = int(len(batch) / self.number_of_threads);

                for i in range(self.number_of_threads):
                    if i == (self.number_of_threads - 1):
                        print(i, batch_size)
                        batches.append(batch[i*batch_size:])
                    else:
                        batches.append(batch[i*batch_size:i*batch_size+batch_size])

        
        #Close the db until the next query 
        db.close()
    
        return batches

    def registerJob(
        max_collectors:int = 1,
        max_timeout_seconds:int = 120
    ):
        """
        Register with job handler to ensure there is an active collector

        max_collector:int - Maximum number of Job instances for this type 
        of service. 
        """

    async def process_batch(self, batch:List[Tuple[str, ] ] ) -> Generator[dict, None, None]:
        """
        Process a batch of domains. Receives a list of 
        tuples that represent domains that have yet to be added to 
        the aoc table.

        This tuple is comprised of => (str: domain_uuid, str: domain_name, str:domain_tld)

        Expects function to yield either dicts or list of dicts whose structure matches
        the layout of table schema, with the addition of the id key/value
        """

        raise Exception("Not Implemented")

    def _thread_run(self, batch:List[dict]):

        loop = asyncio.new_event_loop();

        asyncio.set_event_loop(loop)

        future = asyncio.ensure_future(self._async_run(batch))
        
        # Wait for the result:
        loop.run_until_complete(future)

    async def _async_run(self, batch:List[dict]):

        async for row_dict in self.process_batch(batch) :            
            if row_dict :
                self.queue.put(row_dict)

    def run(self):
        """
        Runs batch jobs according to the run schedule

        If there is no run schedule then runs once
        """

        if(self.schedule):

            raise Exception("Not Implemented")

        else:
            # Run indefinitely
            while True:
                
                batches = self._getBatches(500);

                threads = [];

                for batch in batches:

                    thread =  threading.Thread(target=self._thread_run, args=(batch,))

                    thread.start();

                    threads.append(thread);

                while True:

                    SHOULD_CONTINUE = False

                    for thread in threads:
                        if thread.is_alive():
                            SHOULD_CONTINUE = True
                            break
                    

                    # This should be determined by the rate at which we
                    # receive rows. 
                    db = DBConnector();
                    # We have a choice to batch up the results and 
                    # do a mass insert or insert each row individually 
                    # as we go.

                    #Query the DB with new data table
                    conn = db.conn;
                    
                    while not self.queue.empty():

                        try:
                            row_dict = self.queue.get(timeout=2)


                            with conn:
                                with conn.cursor() as curs:

                                    keys = row_dict.keys();
                                    values = [row_dict[key] for key in keys];
                                    
                                    query = curs.mogrify(f"Insert into {self.aoc_table} (%s) values %s", (AsIs(",".join(keys)), tuple(values)))
                                    
                                    curs.execute(query);

                        except queue.Empty:
                            break;
                    
                    #Close the db until the next query 
                    db.close()

                    if not SHOULD_CONTINUE:
                        break

                for thread in threads:
                    thread.join();


                






