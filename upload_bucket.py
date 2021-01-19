from contextlib import contextmanager
from io import BytesIO
from boto3 import session
from botocore.client import Config


ACCESS_ID = 'NT5YMFT4HB6MN4MQKQQT'
SECRET_KEY = 'CQKY0Tn3GrfMWlCGwyKOzCOHvDQ7klDww+HLqr50t7c'

def df2io(df):
	(io:= BytesIO(df.to_csv(index=False).encode())).seek(0) # file pointer back to 0
	return io

@contextmanager
def spaces_upload(access_id = ACCESS_ID, secret_key = SECRET_KEY, region_name='sfo2', bucket = 'downloads.tldquery'):
	spaces_session = session.Session(access_id, secret_key, region_name = region_name)
	resource = spaces_session.resource('s3', endpoint_url='https://sfo2.digitaloceanspaces.com')
	try:
		yield resource.Bucket(bucket)
	finally:
		pass # just to use this as a context manager


def upload(files):
	with spaces_upload() as space:
		for source, target in files:
			space.upload_fileobj(df2io(source), target, ExtraArgs = {'ACL':'public-read'})
			print(f'Uploaded {target}')