import time
import schedule
from domain_registrar_collector import GoDaddyCollector, SedoCollector

if __name__ == '__main__':
    godaddy_collector = GoDaddyCollector()
    sedo_collector = SedoCollector()

    schedule.every().day.at("08:00").do(godaddy_collector.gather(),'It is 01:00')
    schedule.every().day.at("09:00").do(sedo_collector.gather(),'It is 01:00')

    while True:
        
        schedule.run_pending()

        time.sleep(60) # wait one minute
