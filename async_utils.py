from json import load
import asyncio

import aiohttp
import asyncwhois
from bs4 import BeautifulSoup

# for use with `brandable` function
with open('words.json') as f:
	words=load(f)

starts_with = ('anti', 'de', 'dis', 'em', 'en', 'fore', 'il', 'im', 'in', 'inter', 'ir', 'mid', 'mis', 'non', 'over', 'pre', 're', 'semi', 'sub', 'super', 'trans', 'un', 'under')
ends_with = ('able', 'al', 'ation', 'ative', 'ed', 'en', 'eous', 'er', 'es', 'est', 'ful', 'ial', 'ible', 'ic', 'ing', 'ion', 'ious', 'ition', 'itive', 'ity', 'ive', 'less', 'ly', 'ment', 'ness', 'ous', 's', 'tion', 'y')

def rename(func):
	func.__name__ = f'internal call for {func.__name__.strip("_")}'
	return func

def logger(func):
	if asyncio.iscoroutinefunction(func):
		async def wrapper(*args):
			print(f'{func.__name__} was called for {args[0]}')
			return await func(*args)
		return wrapper

	def wrapper(*args):
		print(f'{func.__name__} was called for {args[0]}')
		return func(*args)
	return wrapper

@rename
def __alexa(response):
	# blocking, needs to be run in `run_in_executor`
	soup = BeautifulSoup(response, 'lxml')
	if country := soup.find('country'):
		return country['rank']
	return -999

@logger
async def brandable(domain_name, session):
	domain, tld = domain_name.split('.', 1)
	return len(domain) <= 6 or domain in words or domain.endswith(ends_with) or domain.startswith(starts_with) # db saves this as 1 or 0, cool

@logger
async def alexa(domain_name, session):
	url = f'http://data.alexa.com/data?cli=2&url={domain_name}'
	response = await session.get(url)
	loop = asyncio.get_running_loop()
	return await loop.run_in_executor(None, __alexa, await response.text())

@logger
async def wikipedia(domain_name, session):
	url = f'https://en.wikipedia.org/w/api.php?action=opensearch&search={domain_name}&limit=max&namespace=0&format=json&profile=strict'
	response = await session.get(url)
	return len((await response.json())[1])

@logger
async def wayback(domain_name, session):
	url = f'https://web.archive.org/cdx/search/cdx?url={domain_name}&output=json&fl=statuscode'
	while True:
		try:
			response = await session.get(url)
		# except (aiohttp.client_exceptions.ClientConnectorError, aiohttp.client_exceptions.ClientOSError):
		except Exception as e:
			print(f'wayback exception for {domain_name}', e)
			await asyncio.sleep(0)
		else:
			return (await response.text()).count(',')
@logger
@rename
async def __whois(domain_name):
	try:
		response = await asyncwhois.aio_lookup(domain_name)
	# except (asyncwhois.errors.WhoIsQueryConnectError, asyncwhois.errors.WhoIsQueryParserError):
	except Exception as e:
		print(f'whois exception for {domain_name}', e)
		await asyncio.sleep(0)
	else:
		response = response.parser_output
		return domain_name.split('.', 1)[-1].lower(), response.get('domain_name') is not None, response.get('created')
	return None, None, None

async def whois(domain_name):
	similar_tld = {'site', 'net', 'org', 'com', 'gov', 'io', 'edu', 'biz'}
	domain,original_tld = domain_name.split('.', 1)
	similar_tld.add(original_tld)
	tasks = [asyncio.create_task(__whois(f'{domain}.{tld}')) for tld in similar_tld]
	return await asyncio.gather(*tasks)

async def fetch_details(domain_name, session):
	functions = (alexa, wikipedia, wayback, brandable)
	tasks = [asyncio.create_task(fun(domain_name, session)) for fun in functions]
	return await asyncio.gather(*tasks)
	