#! /usr/local/bin/python3.9

import sqlite3
from time import perf_counter
from contextlib import closing
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

from utils import alexa, wikipedia, wayback, whois_ as whois, creation_date, brandable

def db_ops(db_path,table_name):
	today=f'{datetime.today().strftime("%Y-%m-%d")}'
	with closing(sqlite3.connect(db_path)) as conn:
		cur_one=conn.cursor() # for reading
		cur_two=conn.cursor() # for updating
		total_rows = cur_two.execute(f'select count(*) from {table_name}').fetchone()[0]
		threaded = False
		start = perf_counter()
		if threaded:
			with ThreadPoolExecutor() as executor:
				for idx, row in enumerate(cur_one.execute(f'select * from {table_name} where date_added=?',(today,)), 1):
					common_args=conn,cur_two,table_name,row[0]
					futures = [executor.submit(func, *common_args) for func in (alexa,wikipedia,wayback,whois,creation_date,brandable)]
					for future in as_completed(futures):
						future.result()
					if not idx % 100:
						print(f'Completed {idx} of {total_rows} in {perf_counter() - start}')
						return
						start = perf_counter()
					else:
						print(f'{idx} is done')
		else:
			for idx, row in enumerate(cur_one.execute(f'select * from {table_name} where date_added=?',(today,)), 1):
				common_args=conn,cur_two,table_name,row[0]
				for func in (alexa,wikipedia,wayback,whois,creation_date,brandable):
					func(*common_args)
				if not idx % 100:
					print(f'Completed {idx} of {total_rows} in {perf_counter() - start}')
					return
					start = perf_counter()
				else:
					print(f'{idx} is done')

db_table_pairs = [('db/__godaddy_db.db', 'godaddy_details'), ('db/__sedo_db.db', 'sedo_details')]

db_table_pairs = [('db/__godaddy_db.db', 'godaddy_details')]

for source in db_table_pairs:
	db_ops(*source)