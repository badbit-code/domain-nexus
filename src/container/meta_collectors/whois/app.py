from collector_base import MetaCollectorBase
import aiohttp
import rdap
import datetime
import whois_kludge

rdap = rdap.RDAP()

epoch_date = datetime.datetime.utcfromtimestamp(0).strftime("%Y-%m-%dT%H:%M:%SZ")

class WhoisMetaCollector(
    MetaCollectorBase,
    aoc_table = "whois_data",
    table_schema = [
        "registered timestamptz not null",
        "expires timestamptz not null"
        ]

):
    async def process_batch(self, batch):

        import time

        for id, domain, tld in batch:

            #time.sleep(2)

            async with aiohttp.ClientSession() as session: 

                data = await rdap.get_registration_information(domain, tld, session);
                
                if data is None:
                    continue

                if data.get("no_auth", None):

                    try:

                        w = whois_kludge.whois(domain + "." + tld, flags=whois_kludge.NICClient.WHOIS_QUICK)

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

                                yield {"id":id, "registered":registered or epoch_date, "expires": expired or epoch_date}

                    except:

                        import traceback

                        print(w)

                        traceback.print_exc()

                        pass

                    yield {"id":id, "registered":epoch_date, "expires": epoch_date}

                if data.get("no_data", None):

                    yield {"id":id, "registered":epoch_date, "expires": epoch_date}

                else:

                    yield {"id":id, "registered":data.get("registered", epoch_date), "expires": data.get("expires", epoch_date)}

                
if __name__ == "__main__":

    collector = WhoisMetaCollector()

    collector.number_of_threads = 2

    collector.run()






    