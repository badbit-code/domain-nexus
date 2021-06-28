"""
WHOIS information lookup using RDAP REST protocol
"""
import http.client
import json
from aiohttp import ClientSession


class RDAP:

    bootstrap_file = None

    auth_servers = {}

    def __init__(self):

        bootstrap_domain = r"data.iana.org"

        conn = http.client.HTTPConnection(bootstrap_domain)

        conn.request("GET", r"/rdap/dns.json");

        response = conn.getresponse()

        headers = response.getheaders()

        bytes = response.read()

        data = json.loads(bytes)

        self.auth_servers = {key:{"host":val, "PAUSED_FOR_RETRY": False} for key, val in [(name, hosts[0]) for names, hosts in data["services"] for name in names]}

        print(self.auth_servers)

    async def get_registration_information(self, domain_name:str, tld:str, session: ClientSession) -> dict:

        auth = self.auth_servers.get(tld, None)

        try:
            if auth is not None:

                if auth["PAUSED_FOR_RETRY"]:
                    return None

                async with session.get(f"{auth['host']}domain/{domain_name}.{tld}") as response:

                    status = response.status

                    data = None

                    try:

                        data = await response.json()

                    except:
                        
                        pass

                    if status == 429: # Rate limit exceeded

                        auth["PAUSED_FOR_RETRY"] = True

                        # pause for a short amount of time and restart
                        import time
                        import random

                        time_buffer = random.randint(1,30)

                        print(data, response)

                        if response.headers.get("Retry-After", None) or response.headers.get("retry-after", None):
                            time_buffer = int(response.headers.get("Retry-After", None) or response.headers.get("retry-after", 0))

                        time.sleep(30 + time_buffer)

                        auth["PAUSED_FOR_RETRY"] = False

                        return await self.get_registration_information(domain_name, tld, session)

                    elif status == 404 or data == None or data.get("title", "") == "Not Found":
                        return  {"no_data":True}
                    
                
                    else:
                        registration = [event for event in data["events"] if event["eventAction"] == "registration"][0]
                        expiration = [event for event in data["events"] if event["eventAction"] == "expiration"][0]

                        expire_date = expiration.get("eventDate", None)
                        register_date = registration.get("eventDate", None)
                        
                        return {"registered": register_date, "expires": expire_date, "no_data": False}

            else:

                print(f"Could not get data for {domain_name} {tld}")

                return  {"no_data":True}

        except:

            return None
            

# rdap = RDAP()
# 
# 
# async def test():
# 
#     async with aiohttp.ClientSession() as session:
# 
#         data = await rdap.get_registration_information("xcxzcsdf", "com", session)
# 
#         print(data)
# 
#         await session.close()
# 
# future = asyncio.ensure_future(test())
# 
# asyncio.get_event_loop().run_until_complete(future)