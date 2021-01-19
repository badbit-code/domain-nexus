import smtplib, ssl

port = 465
context = ssl.create_default_context()

with smtplib.SMTP_SSL('mail.tldquery.com', port, context=context) as server:
	server.login('reports@tldquery.com', ']PYu6wn;rXx$')
	server.send_message('reports@tldquery.com', 'ganesh-kumar@live.com', 'sent from script ssl')