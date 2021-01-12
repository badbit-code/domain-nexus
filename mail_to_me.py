import smtplib, ssl

port = 465  # For SSL

# Create a secure SSL context
context = ssl.create_default_context()

with smtplib.SMTP_SSL('mail.tldquery.com', port, context=context) as server:
	server.login('reports@tldquery.com', ']PYu6wn;rXx$')
	server.sendmail('reports@tldquery.com', 'reports@tldquery.com', 'sent from script ssl')