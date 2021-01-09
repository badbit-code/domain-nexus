#! /usr/local/bin/python3.9

import sqlite3
from datetime import datetime
from functools import partial
from utils import alexa, wikipedia, wayback, whois_ as whois, creation_date, brandable

today=f'{datetime.today().strftime("%Y-%m-%d")}'

def db_ops(db_path,table_name):
	conn=sqlite3.connect(db_path)
	cur_one=conn.cursor() # for reading
	cur_two=conn.cursor() # for updating
	for row in cur_one.execute(f'select * from {table_name} where date_added=?',(today,)):
		common_args=conn,cur_two,table_name,row[0]
		for func in alexa,wikipedia,wayback,whois,creation_date,brandable:
			func(*common_args)

	conn.close()

def godaddy():
	# establish and terminate a connection once `table_names` are retrieved
	# this is done so that the interface to `db_ops` need not be changed
	# establish a new connection there to work with
	conn=sqlite3.connect(db_path:='db/godaddy_db.db')
	cur=conn.cursor()
	cur.execute('select tbl_name from sqlite_master where type="table"')
	table_names=cur.fetchall()
	conn.close()

	for table_name,*_ in table_names:
		db_ops(db_path,table_name)


def sedo():
	db_ops('db/sedo_db.db','sedo_details')


# thread maybe?

# uncomment to run

# godaddy()
sedo()