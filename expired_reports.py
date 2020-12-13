#! /usr/local/bin/python3.9

import sqlite3
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from pathlib import Path

reports=Path('reports')
history=reports/Path('history')

history.mkdir(parents=True,exist_ok=True)

conn=sqlite3.connect('db/godaddy_db.db')
cur=conn.cursor()

cur.execute('select tbl_name from sqlite_master where type="table"')

today=f'{datetime.today().strftime("%Y-%m-%d")}'
# today='2020-11-17'

godaddy_df=pd.concat(pd.read_sql_query(f'select * from {table_name} where date_added=?',con=conn,params=(today,)) for table_name, *_ in cur)
conn.close()

conn=sqlite3.connect('db/sedo_db.db')
cur=conn.cursor()
sedo_df=pd.read_sql_query(f'select * from sedo_details where date_added=?',con=conn,params=(today,))
conn.close()

combined_df=pd.concat((godaddy_df,sedo_df)).drop_duplicates('domain_name') # combine and remove duplicate rows based on domain_name column

combined_df.alexa.where(combined_df.alexa!=-999, 'NA', inplace=True)
combined_df.brandable.replace(to_replace={0:'Unknown',1:'Yes'},inplace=True)

for col in ('com', 'net', 'org', 'io', 'edu', 'gov', 'site', 'biz'):
	combined_df[col].replace(to_replace={1:'Y',0:'N'}, inplace=True)

combined_df.available=pd.to_datetime(combined_df.available).dt.strftime('%Y-%m-%d')

new_names={'domain_name': 'Domain', 'available': 'Released', 'domain_length': 'Length', 'alexa': 'Alexa', 'archive_count': 'Archive Count', 'brandable': 'Brandable','wiki':'Wiki','date_added': 'Collected'}

combined_df.rename(columns=new_names,inplace=True)

buy='<a class="button" href="https://sedo.com/search/details/?domain={}&origin=export" target="_blank">Buy</a>' # this is a placeholder, later there will be new ones for every new source

combined_df['Buy']=combined_df.apply(lambda x:buy.format(x.Domain),1)

cols=combined_df.columns.tolist() # column list

combined_df=combined_df[cols[:4]+[cols[-2]]+cols[4:-2]+[cols[-1]]] # new col order

current_report=combined_df.drop(columns=cols[9:14])# drop "similar domains"

current_report.to_csv(reports/'currentreport.csv',index=False)

combined_df.to_csv(f'{history}/{datetime.today().strftime("%Y-%m-%d")}.csv',index=False)