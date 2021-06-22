from typing import List
from db import DBConnector

class MetaCollectorBase:

    aoc_table = ""

    sot_table = ""

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

        table_schema.insert(0, "id UUID PRIMARY KEY")

        table_query = ",\n".join(table_schema)

        table_query = f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            {table_query},
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


    def getBatch(size:int=500):
        """
        Returns a batch of domain names that do not have entries
        within the table this class is responsible for. 

        size = Maximum number of entries to return. 
        """

    def updateBatch():
        """
        Takes a list of data elements and pushes to table. 
        """

    def clearData():
        """
        Remove any rows that do not have matching entries in the SoT 
        table.
        """

    def registerJob(
        max_collectors:int = 1,
        max_timeout_seconds:int = 120
    ):
        """
        Register with job handler to ensure there is an active collector

        max_collector:int - Maximum number of Job instances for this type 
        of service. 
        """
