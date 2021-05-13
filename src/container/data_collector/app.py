from domain_registrar_collector import GoDaddyCollector
import os
from psycopg2 import connect, extras

print("Hello World", os.getenv("POSTGRES_DB"), os.getenv("POSTGRES_USER"), os.getenv("POSTGRES_PASSWORD"))

if __name__ == "__main__":
    from time import sleep

    sleep(2)


    # Simple "job" based execution that runs every 24 hours to collect 
    # Godaddy data. Straight forward and dumb. Should maybe replace with cron
    # job soon. 

    while True: 

        #sleep(10)

        conn = connect(
            host=os.getenv("POSTGRES_HOST"),
            dbname=os.getenv("POSTGRES_DB"),
            user=os.getenv("POSTGRES_USER"),
            password=os.getenv("POSTGRES_PASSWORD"),
            port=os.getenv("POSTGRES_PORT", 5432),
            sslmode=os.getenv("POSTGRES_SSL_MODE", None) or None,
            sslrootcert=os.getenv("POSTGRES_ROOT_CERT_PATH", None),
        )
    
        gd_collector = GoDaddyCollector()

        gd_collector.batch_size = 100000
        gd_collector.batch_limit = 5
        
        gd_collector.gather()
        #gd_collector.test_gather()

        while gd_collector.HAS_PENDING_BATCH_FILES:

            gd_collector.upload_to_domain_table(conn)

            sleep(5)

        sleep(24*3600)