import smtplib
import ssl
from email.message import EmailMessage
from email.headerregistry import Address


PORT = 465 # For SSL
REPORTS_EMAIL: str = "reports@tldquery.com"
REPORTS_PASS: str = "]PYu6wn;rXx$"
DEFAULT_ADDRESS: str = Address("TLD Query Admin", "reports@tldquery.com")
EMAIL_HOST: str = "mail.tldquery.com"

def send(content, email_host: str = EMAIL_HOST, sent_from: Address = DEFAULT_ADDRESS, send_to: Address = DEFAULT_ADDRESS, port: int = PORT subject: str ="Report Upload Status"):
    msg = EmailMessage()
    msg["from"] = sent_from
    msg["to"] = send_to
    msg["subject"] = subject
    msg.set_content(content)
    with smtplib.SMTP_SSL(
        email_host, port, ssl.create_default_context()
    ) as server:
        server.login(REPORTS_EMAIL, REPORTS_PASS)
        server.send_message(msg)
