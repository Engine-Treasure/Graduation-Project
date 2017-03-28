#!/usr/bin/python

import os
import smtplib
from email.mime.text import MIMEText


password = os.getenv("EMAIL_PASSWORD_163")


server = smtplib.SMTP("smtp.163.com")


def send_email(sender="cwf773810@163.com", recipient="me@kissg.org",
        subject="Mission Complete", body="Mission Complete"):

    msg = MIMEText(body)

    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = recipient
    

    server.login(msg["From"], password)
    
    try:
        server.sendmail(msg["From"], [msg["To"]], msg.as_string())
    except Exception as e:
        print(e.message)
    finally:
        server.quit()

if __name__ == "__main__":
    send_email()
