from mail import send

try:
	import only_import
except Exception as e:
	print('Exception')
	send(str(e), 'ganesh-kumar@live.com')
else:
	send('Completed', 'ganesh-kumar@live.com')