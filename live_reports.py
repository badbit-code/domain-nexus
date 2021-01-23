#! /usr/local/bin/python3.9

from math import ceil
import csv
from pathlib import Path
from operator import itemgetter
from io import StringIO

import requests
import pandas as pd

from ftp_ops import factory

reports=Path('reports')

def archive_count(domain_name):
	return 1
	while True:
		try:
			response=requests.get(f'https://web.archive.org/cdx/search/cdx?url={domain_name}&output=json&fl=statuscode').text
		except requests.exceptions.ConnectionError:
			pass
		else:
			return int(response.count(','))

url='https://sedo.com/txt/auctions_us.txt'

response = requests.get(url)

file_like = StringIO(response.content.decode('ISO-8859-1'))

def currency_converter(rate):
	def converter(amount):
		return ceil(int(amount)*rate)
	return converter

currency_map={'&#163':currency_converter(1.34), 'EUR':currency_converter(1.21), '$US':currency_converter(1)}

res=[]
for row in csv.reader(file_like,delimiter=';'):
	domain_name, cost, currency = itemgetter(0,3,4)(row)
	archive_count_=archive_count(domain_name)
	last_updated='Today'
	currency_=currency_map[currency](cost)
	buy=f'<a class="button" href="https://sedo.com/search/details/?domain={domain_name}&origin=export&campaignId=326646" target="_blank">Buy</a>' # this is a placeholder, later there will be new ones for every new source

	res.append((domain_name,currency_,archive_count_,last_updated, buy))

df=pd.DataFrame(res,columns=['Domain Name','Cost','Archive Count', 'Last Updated', 'Buy'])
df.to_csv(reports/'premium.csv',index=False)

source_dest=[(file_name:=(reports/'premium.csv'),f'premium/{file_name.name}')]

upload = factory('upload', '/wp-content/uploads/2020/11/reportfolder') # upload to ftp
upload(source_dest) # or factory('upload', '/wp-content/uploads/2020/11/reportfolder')(source_dest) :p