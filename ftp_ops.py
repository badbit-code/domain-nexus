#! /usr/local/bin/python3.9

from ftplib import FTP

def factory(op, cwd):
	command = {'upload':'STOR', 'append':'APPE'}
	def inner(souce_dest):
		with FTP('ftp.mcdanieltechnologies.com','datamover@tldquery.com','7T5sUnu2dQ$g') as ftp:
			ftp.cwd(cwd)
			for from_, to_ in souce_dest:
				print(from_, to_)
				with open(from_,'rb') as f:
					print(ftp.storbinary(f'{command[op]} {to_}', f))
	return inner