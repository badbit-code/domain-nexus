import re
from collector_base import MetaCollectorBase
import aiohttp

regex = re.compile(r'RANK="(\d+)"')

class AlexMetaCollector(
    MetaCollectorBase,
    aoc_table = "alexa_data",
    table_schema = [
        "alexa_score bigint not null"
        ]

):
    async def process_batch(self, batch):

        async with aiohttp.ClientSession() as session: 

            for id, domain, tld in batch:

                try:

                    domain_name = (domain + "." + tld)

                    async with session.get(f"http://data.alexa.com/data?cli=2&url={domain_name}") as response:
                        
                        result = str(await response.read())

                        re_result = re.search(regex, result)

                        if re_result:

                            yield ({"id":id, "alexa_score": int(re_result.groups()[0])})

                        else:

                            yield ({"id":id, "alexa_score": 0})
                
                except:
                    
                    pass


if __name__ == "__main__":

    collector = AlexMetaCollector()

    collector.number_of_threads = 4

    collector.run()

    