from collector_base import MetaCollectorBase
import aiohttp


class WikiMetaCollector(
    MetaCollectorBase,
    aoc_table = "wiki_data",
    table_schema = [
        "has_wiki boolean not null"
        ]

):
    async def process_batch(self, batch):

        async with aiohttp.ClientSession() as session: 

            for id, domain, tld in batch:

                try:

                    domain_name = (domain + "." + tld)

                    async with session.get(f"https://en.wikipedia.org/w/api.php?action=opensearch&search={domain_name}&limit=max&namespace=0&format=json&profile=strict") as response:
            
                            try:
                                if len((await response.json())[1]) > 0:
                                    print("HAVE TRUE  for", domain_name)
                                    yield ({"id":id, "has_wiki": True })
                            except:
                                print("Query Failed")
                                print(str(await response.read()))
                                continue
                            
                            yield ({"id":id, "has_wiki": False })
                
                except:
                    
                    pass


if __name__ == "__main__":

    collector = WikiMetaCollector()

    collector.number_of_threads = 4

    collector.run()

    