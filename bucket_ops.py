from csv import DictWriter
from contextlib import contextmanager
from io import BytesIO, TextIOWrapper
from boto3 import session
from botocore.client import Config
from datetime import datetime

from ftplib import FTP

ACCESS_ID = 'NT5YMFT4HB6MN4MQKQQT'
SECRET_KEY = 'CQKY0Tn3GrfMWlCGwyKOzCOHvDQ7klDww+HLqr50t7c'


@contextmanager
def spaces_upload(access_id = ACCESS_ID, secret_key = SECRET_KEY, region_name='sfo2', bucket = 'downloads.tldquery'):
	spaces_session = session.Session(access_id, secret_key, region_name = region_name)
	resource = spaces_session.resource('s3', endpoint_url='https://sfo2.digitaloceanspaces.com')
	try:
		yield resource.Bucket(bucket)
	finally:
		pass # just to use this as a context manager

def df2io(df):
	(io:= BytesIO(df.to_csv(index=False).encode())).seek(0) # file pointer back to 0
	return io

def upload(files):
	with spaces_upload() as space:
		for source, target in files:
			space.upload_fileobj(df2io(source), target, ExtraArgs = {'ACL':'public-read'})
			print(f'Uploaded {target}')

def gen_csv():
	today = datetime.now().date()
	with spaces_upload() as spaces, FTP('ftp.mcdanieltechnologies.com','datamover@tldquery.com','7T5sUnu2dQ$g') as ftp:
		print(ftp.cwd('/wp-content/uploads/2020/11/reportfolder'))
		file_wrapper = TextIOWrapper((file_buffer := BytesIO()), encoding='utf-8')
		
		if 'file_links.csv' not in ftp.nlst():
			file_wrapper.write('File Name,Date,Size\n')

		base_url = 'https://downloads.tldquery.sfo2.cdn.digitaloceanspaces.com/{}'

		data_gen = ((base_url.format(i.key), i.size, i.last_modified.date()) for i in spaces.objects.all() if i.key.endswith('.csv'))
		data_gen_str = (','.join(map(str, i)) for i in data_gen)

		file_wrapper.writelines('\n'.join(data_gen_str))
		# file_wrapper.writelines('\n'.join(','.join(map(str, (base_url.format(i.key), i.size, i.last_modified.date()))) for i in spaces.objects.all() if i.key.endswith('.csv'))
		file_wrapper.seek(0)
		print(ftp.storbinary('APPE file_links.csv', file_buffer))