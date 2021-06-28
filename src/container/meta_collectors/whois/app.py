from collector_base import MetaCollectorBase
import whois


class WhoisMetaCollector(
    MetaCollectorBase,
    aoc_table = "whois_data",
    table_schema = [
        "registered timestamptz not null",
        "expires timestamptz not null"
        ]

):
    async def process_batch(self, batch):

        for id, domain, tld in batch:

            try:

                w = whois.whois(domain + "." + tld)

                if w:
                    if type(w["expiration_date"]) is list:
                        expired = w["expiration_date"][0]
                    else:
                        expired = w["expiration_date"]

                    if type(w["creation_date"]) is list:
                        registered = w["creation_date"][0]
                    else:
                        registered = w["creation_date"]


                    if registered and expired:

                        yield {"id":id, "registered":registered, "expires": expired}
            
            except:
                
                pass


if __name__ == "__main__":

    collector = WhoisMetaCollector()

    collector.number_of_threads = 16

    collector.run()






    