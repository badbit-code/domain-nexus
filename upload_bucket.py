'''
NT5YMFT4HB6MN4MQKQQT
CQKY0Tn3GrfMWlCGwyKOzCOHvDQ7klDww+HLqr50t7c
'''

from boto3 import session
from botocore.client import Config

ACCESS_ID = 'NT5YMFT4HB6MN4MQKQQT'
SECRET_KEY = 'CQKY0Tn3GrfMWlCGwyKOzCOHvDQ7klDww+HLqr50t7c'

# Initiate session

session = session.Session()
client = session.client('s3',region_name='sfo2',endpoint_url='https://sfo2.digitaloceanspaces.com',aws_access_key_id=ACCESS_ID,aws_secret_access_key=SECRET_KEY)

# Upload a file to your Space
client.upload_file('templates/file_list.html', 'downloads.tldquery', 'file_list.html', ExtraArgs = {'ACL':'public-read'})

# print(client.list_buckets())
# print(*client.list_objects_v2(Bucket='downloads.tldquery')['Contents'], sep = '\n')

# for i in client.list_objects_v2(Bucket='downloads.tldquery')['Contents']:
	# print(i['Key'])
# print(session.get_available_services())
# https://downloads.tldquery.sfo2.cdn.digitaloceanspaces.com/file_list.html