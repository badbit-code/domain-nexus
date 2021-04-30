class CollectorManager:

    def __init__(self, Collector):

        self.collector = Collector

    def run_collection(self):

        from time import sleep

        while True:

            self.collector.update()

            sleep(1800)


if __name__ == "__main__":

    from collector import Collector
    
    collector = Collector

    collector_manager = CollectorManager(collector)

    collector_manager.run_collection()
