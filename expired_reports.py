#! /usr/local/bin/python3.9

from pathlib import Path
from datetime import datetime
# import export_csv

from upload_ftp import upload

reports=Path('reports')
history=reports/Path('history')

today=f'{datetime.today().strftime("%Y-%m-%d")}'
# today='2020-11-16'

source_dest=[(reports/'currentreport.csv', 'current/currentreport.csv'),(file_name:=(history/f'{today}.csv'),file_name)]

upload(source_dest)