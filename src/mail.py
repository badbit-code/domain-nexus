import smtplib
import ssl
from email.message import EmailMessage
from email.headerregistry import Address


def send(content, to=None):
    msg = EmailMessage()
    msg["from"] = Address("TLD Query Admin", "reports@tldquery.com")
    msg["to"] = Address("TLD Query Admin", "reports@tldquery.com" if to is None else to)
    msg["subject"] = "Report Upload Status"
    msg.set_content(content)
    with smtplib.SMTP_SSL(
        "mail.tldquery.com", 465, ssl.create_default_context()
    ) as server:
        server.login("reports@tldquery.com", "]PYu6wn;rXx$")
        server.send_message(msg)
