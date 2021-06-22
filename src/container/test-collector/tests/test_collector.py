import pytest


def test_init():

    import os 

    assert os.getenv("POSTGRES_HOST", None) != None

    from db import DBConnector

    db = DBConnector();

    assert db.conn != None

    # create new collector 
    from collector_base import MetaCollectorBase

    class PingTest(MetaCollectorBase, 
        aoc_table = "test_table",
        table_schema = ["pingable bool NOT NULL"]):
        pass
    
    # Ensure the Source-of-truth table (sot) is present
    # in the subclass
    assert PingTest.sot_table == "domain"
    
    # Ensure Area of Concern table is present in class 
    # and DB ...
    assert PingTest.aoc_table == "test_table"

    conn = db.conn;

    GOT_TABLE = False

    with conn:

        with conn.cursor() as curs:
            
            curs.execute(f"SELECT * FROM pg_catalog.pg_tables WHERE tablename = '{PingTest.aoc_table}';");
            
            list = curs.fetchall();
            
            assert len(list) == 1;

            GOT_TABLE = True

    assert GOT_TABLE == True

def test_batch():
     
    from collector_base import MetaCollectorBase

    class PingTest(MetaCollectorBase, 
        aoc_table = "test_table",
        table_schema = ["pingable bool NOT NULL"]):
        
        def process_batch(self, batch):

            for id,domain,tld in batch:

                if(tld =="com"):
                    yield { "id": id, "pingable": True  }
                else:
                    yield { "id": id, "pingable": False  }            
        
    
    ping_test = PingTest()

    ping_test.run()


