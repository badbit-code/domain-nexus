#! /usr/local/bin/python3.9

from ftplib import FTP
from pathlib import Path
from datetime import datetime

import sedo_collector
import godaddy_collector
import db_ops

import expired_reports
import live_reports

reports=Path('reports')
history=reports/Path('history')

today=datetime.today().strftime("%Y-%m-%d")

def upload(souce_dest):
	with FTP('ftp.mcdanieltechnologies.com','datamover@tldquery.com','7T5sUnu2dQ$g') as ftp:
		ftp.cwd('/wp-content/uploads/2020/11/reportfolder')
		for from_, to_ in souce_dest:
			print(from_, to_)
			with open(from_,'rb') as f:
				print(ftp.storbinary(f'STOR {to_}', f))

source_dest=[(file_name:=(reports/'currentreport.csv'), f'current/{file_name.name}'),(file_name:=(history/f'{today}.csv'),f'history/{file_name.name}'),(file_name:=(reports/'premium.csv'),f'premium/{file_name.name}')]
upload(source_dest)