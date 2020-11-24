from pathlib import Path
from ftplib import FTP
from datetime import datetime
import export_csv


reports=Path('reports')
history=reports/Path('history')

today=f'{datetime.today().strftime("%Y-%m-%d")}'
# today='2020-11-16'

with FTP('ftp.mcdanieltechnologies.com','datamover@tldquery.com','7T5sUnu2dQ$g') as ftp:
	ftp.cwd('/wp-content/uploads/2020/11/reportfolder')
	with open(reports/'currentreport.csv','rb') as f:
		print(ftp.storbinary(f'STOR current/currentreport.csv', f) )

	with open(file_name:=(history/f'{today}.csv'),'rb') as f:
		print(ftp.storbinary(f'STOR history/{file_name.name}', f) )