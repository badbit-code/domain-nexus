#! /usr/local/bin/python3.9

from pathlib import Path
from datetime import datetime
import requests
import csv
import sqlite3
from io import StringIO

Path('db').mkdir(exist_ok=True)

limiter=None # set this to None for writing all rows to db

conn=sqlite3.connect('db/sedo_db.db',detect_types=sqlite3.PARSE_DECLTYPES)
cur=conn.cursor()

cur.execute('''create table if not exists sedo_details
(domain_name text primary key, available timestamp, domain_length text,
wiki integer default 0, alexa integer DEFAULT -999,
archive_count integer default 0,
com integer default 0, net integer default 0,
org integer default 0, io integer default 0,
edu integer default 0, gov integer default 0,
site integer default 0, biz integer default 0,
brandable integer default 0,
creation_date timestamp NULL,
date_added timestamp default CURRENT_DATE)''')

csv_url='https://sedo.com/fileadmin/documents/resources/expiring_domain_auctions.csv'

response=requests.get(csv_url)

file_like=StringIO(response.content.decode('utf-16'),newline='')
next(file_like) # sep=;
next(file_like) # "Domain Name";"Start Time";"End Time";"Reserve Price";"Domain is IDN";"Domain has hyphen";"Domain has numbers";"Domain Length";TLD;Traffic;Link
for idx,row in enumerate(csv.reader(file_like,delimiter=';')):
	if limiter is not None and idx==limiter: break# limiter for testing
	row_=row[0],row[2],row[7]
	cur.execute('insert or ignore into sedo_details (domain_name, available, domain_length) values (?,?,?)',row_)
	
conn.commit()
conn.close()