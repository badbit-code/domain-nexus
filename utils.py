from json import load
import sqlite3
import requests
import whois
from bs4 import BeautifulSoup

# for use with `brandable` function
with open('words.json') as f:
	words=load(f)

starts_with=('anti', 'de', 'dis', 'em', 'en', 'fore', 'il', 'im', 'in', 'inter', 'ir', 'mid', 'mis', 'non', 'over', 'pre', 're', 'semi', 'sub', 'super', 'trans', 'un', 'under')
ends_with=('able', 'al', 'ation', 'ative', 'ed', 'en', 'eous', 'er', 'es', 'est', 'ful', 'ial', 'ible', 'ic', 'ing', 'ion', 'ious', 'ition', 'itive', 'ity', 'ive', 'less', 'ly', 'ment', 'ness', 'ous', 's', 'tion', 'y')

def update_table(column_name):
	def outer(func):
		def inner(conn,cur,table_name,domain_name,func_arg=None):
			func_arg=func_arg or domain_name
			print(f'{func.__name__=}{func_arg=}')
			if result:=func(func_arg):
				while True: # quick fix, need to check if it works
					try:
						cur.execute(f'update {table_name} set {column_name}=(?) where domain_name=(?)',(result,domain_name))
						conn.commit()
					except sqlite3.OperationalError as Exception:
						print(f'Excpetion {e} in {func.__name__} for {domain_name = }')
					else:
						break

		return inner
	return outer

def get_alexa(url):
	soup=BeautifulSoup(requests.get(url).text,'lxml')
	if country:=soup.find('country'):
		return country['rank']

def get_wiki_count(url):
	return len(requests.get(url).json()[1])

def get_archive_count(url):
	while True:
		try:
			response=requests.get(url).text
		except requests.exceptions.ConnectionError:
			pass
		else:
			return int(response.count(','))
'creation_date_2021-01-19.csv,534,2021-01-19 18:09:32.638000+00:00', 'creation_date_2021-01-20.csv,534,2021-01-19 19:21:28.013000+00:00', 'currentreport.csv,2660342,2021-01-19 19:21:17.700000+00:00', 'df.csv,10,2021-01-21 03:10:41.523000+00:00', 'length_2021-01-19.csv,2613084,2021-01-19 18:09:30.995000+00:00', 'length_2021-01-20.csv,2613084,2021-01-19 19:21:20.809000+00:00']
def get_whois(domain_name, get_date = False):
	try:
		w=whois.whois(domain_name)
	except whois.parser.PywhoisError:
		pass # do not do anything
	else:
		return w.get('creation_date') if get_date else int(w['domain_name'] is not None)

@update_table('alexa')
def alexa(domain_name):
	return get_alexa(f'http://data.alexa.com/data?cli=2&url={domain_name}')

@update_table('wiki')
def wikipedia(domain_name):
	return get_wiki_count(f'https://en.wikipedia.org/w/api.php?action=opensearch&search={domain_name}&limit=max&namespace=0&format=json&profile=strict')

@update_table('archive_count')
def wayback(domain_name):
	return get_archive_count(f'https://web.archive.org/cdx/search/cdx?url={domain_name}&output=json&fl=statuscode')

@update_table('brandable')
def brandable(domain_name):
	domain,tld=domain_name.split('.',1)
	return len(domain)<=6 or domain in words or domain.endswith(ends_with) or domain.startswith(starts_with) # db saves this as 1 or 0, cool

@update_table('creation_date')
def creation_date(domain_name):
	if res := get_whois(domain_name, True):
		return res[-1] if isinstance(res, list) else res

def whois_(conn,cur,table_name,domain_name):
	similar_tld={'com': 0, 'net': 0, 'org': 0, 'io': 0, 'edu': 0, 'gov': 0, 'site': 0, 'biz': 0}
	domain,original_tld=domain_name.split('.',1)
	for tld in similar_tld:
		update_table(tld)(get_whois)(conn,cur,table_name,domain_name,f'{domain}.{tld}')