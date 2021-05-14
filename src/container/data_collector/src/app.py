from domain_registrar_collector import GoDaddyCollector
import os
from db import DBConnector

if __name__ == "__main__":
    from time import sleep

    sleep(2)

    # Simple "job" based execution that runs every 24 hours to collect 
    # Godaddy data. Straight forward and dumb. Should maybe replace with cron
    # job soon. 

    while True: 

        dbm = DBConnector()
    
        gd_collector = GoDaddyCollector()

        gd_collector.batch_size = 100000
        gd_collector.batch_limit = 5
        
        gd_collector.gather()
        #gd_collector.test_gather()

        while gd_collector.HAS_PENDING_BATCH_FILES:

            gd_collector.upload_to_domain_table(dbm.conn)

            sleep(5)

        sleep(24*3600)