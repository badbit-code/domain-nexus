import pytest
import mailtest
from src import mail

def test_mail_send():
    with mailtest.Server(smtp_port=465) as mt:
        mail.send("test", 'localhost')
        assert len(mt.emails) == 1