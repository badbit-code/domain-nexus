from psycopg2 import connect
import os


class DBConnector:
    """
    Simple class that creates and destroys a psycopg2 connection
    to a database.

    Database connection details should be specified with these environment
    variables:
    POSTGRES_HOST=
    POSTGRES_USER=
    POSTGRES_PASSWORD=
    POSTGRES_DB=
    POSTGRES_PORT=
    POSTGRES_SSL_MODE=
    POSTGRES_ROOT_CERT_PATH=
    """

    def __init__(self):
        retries = 0
        max_retries = 5
        self.conn = None

        while True:
            try:
                self.conn = connect(
                    host=os.getenv("POSTGRES_HOST"),
                    dbname=os.getenv("POSTGRES_DB"),
                    user=os.getenv("POSTGRES_USER"),
                    password=os.getenv("POSTGRES_PASSWORD"),
                    port=os.getenv("POSTGRES_PORT", 5432),
                    sslmode=os.getenv("POSTGRES_SSL_MODE", None) or None,
                    sslrootcert=os.getenv("POSTGRES_ROOT_CERT_PATH", None),
                )
                break;

            except Exception as e:

                print(e)

                if retries < max_retries:
                    
                    retries += 1

                    import time

                    time.sleep(2* retries)
                
                else:
                    raise Exception("Unable to make connection to DB") 
                    
            

    def close(self):
        self.conn.close()