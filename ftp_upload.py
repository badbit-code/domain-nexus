#! /usr/local/bin/python3.9

from ftplib import FTP
from pathlib import Path
from datetime import datetime
import export_csv
import live_reports

reports=Path('reports')
history=reports/Path('history')

today=f'{datetime.today().strftime("%Y-%m-%d")}'

def upload(souce_dest):
	with FTP('ftp.mcdanieltechnologies.com','datamover@tldquery.com','7T5sUnu2dQ$g') as ftp:
		ftp.cwd('/wp-content/uploads/2020/11/reportfolder')
		for from_, to_ in souce_dest:
			# print(from_, to_)
			with open(from_,'rb') as f:
				print(ftp.storbinary(f'STOR {to_}', f))

source_dest=[(reports/'currentreport.csv', 'current/currentreport.csv'),(file_name:=(history/f'{today}.csv'),file_name.stem),(reports/'premium.csv','premium.csv')]

upload(source_dest)