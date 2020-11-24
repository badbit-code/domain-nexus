import sqlite3
from json import load
from ftplib import FTP
from tempfile import TemporaryFile
from zipfile import ZipFile

limiter=200 # set this to None for writing all rows to db

create_query='''create table if not exists {}
(domain_name text, available timestamp, domain_length text,
wiki integer default 0, alexa integer DEFAULT -999,
archive_count integer default 0,
com integer default 0, net integer default 0,
org integer default 0, io integer default 0,
edu integer default 0, gov integer default 0,
site integer default 0, biz integer default 0,
brandable integer default 0,
date_added timestamp default CURRENT_DATE)'''

conn=sqlite3.connect('db/godaddy_db.db',detect_types=sqlite3.PARSE_DECLTYPES)
cur=conn.cursor()

def download_and_extract(file_name):
	print(f'Downloading {file_name}')
	with TemporaryFile() as tempfile:
		ftp.retrbinary(f'RETR {file_name}',tempfile.write)
		with ZipFile(tempfile) as zip_:
			file_to_extract=file_name.rsplit('.',1)[0]
			zip_.extract(file_to_extract)
	add_to_db(file_name)

def add_to_db(file_name):
	print(f'Adding {file_name}')
	file_name=file_name.rsplit('.',1)[0]
	with open(file_name,encoding='utf-8') as zip_: 
		data=[(x['domainName'],x['auctionEndTime']) for x in load(zip_)['data']][:limiter] 

	table_name=f'godaddy_{file_name.split(".")[0]}'
	cur.execute(create_query.format(table_name))
	cur.executemany(f'insert into {table_name} (domain_name,available) values (?,?)',data)
	conn.commit()

with FTP('ftp.godaddy.com','auctions') as ftp:
	files_needed=(x for x in ftp.nlst() if x.endswith('json.zip'))
	
	for file_ in files_needed: 
		print(f'{file_=}')
		download_and_extract(file_)

conn.close()