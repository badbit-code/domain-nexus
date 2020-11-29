#! /usr/local/bin/python3.9

from ftplib import FTP

def upload(souce_dest):
	for from_, to_ in souce_dest:
		with FTP('ftp.mcdanieltechnologies.com','datamover@tldquery.com','7T5sUnu2dQ$g') as ftp:
			ftp.cwd('/wp-content/uploads/2020/11/reportfolder')
			with open(from_,'rb') as f:
				print(ftp.storbinary(f'STOR {to_}', f))