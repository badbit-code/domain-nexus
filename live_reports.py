#! /usr/local/bin/python3.9

from math import ceil
import csv
from pathlib import Path
from operator import itemgetter
from io import StringIO

import requests
import pandas as pd

from upload_ftp import upload

reports=Path('reports')

def archive_count(domain_name):
	return 0
	while True:
		try:
			response=requests.get(f'https://web.archive.org/cdx/search/cdx?url={domain_name}&output=json&fl=statuscode').text
		except requests.exceptions.ConnectionError:
			pass
		else:
			return int(response.count(','))

def seo_data(domain_name):
	return 0 # stud method for now

url='https://sedo.com/txt/auctions_us.txt'

response = requests.get(url)

file_like = StringIO(response.content.decode('ISO-8859-1'))

def currency_converter(rate):
	def converter(amount):
		return ceil(int(amount)*rate)
	return converter

currency_map={'&#163':currency_converter(1.34), 'EUR':currency_converter(1.21), '$US':lambda x:x}

res=[]
for row in csv.reader(file_like,delimiter=';'):
	domain_name, cost, currency = itemgetter(0,3,4)(row)
	archive_count_=archive_count(domain_name)
	seo_data_=seo_data(domain_name)
	currency_=f'${currency_map[currency](cost)}'
	buy=f'<a class="button" href="https://sedo.com/search/details/?domain={domain_name}&origin=export">Buy</a>' # this is a placeholder, later there will be new ones for every new source

	res.append((domain_name,currency_,archive_count_,seo_data_, buy))

df=pd.DataFrame(res,columns=['Domain Name','Cost','Archive Count', 'SEO Data', 'Buy'])
df.to_csv(reports/'premium.csv',index=False)

upload([(reports/'premium.csv','premium.csv')])