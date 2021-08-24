#!/opt/anaconda3/bin/python
from typing import List
import smtplib
import mimetypes
from email.message import EmailMessage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os



def send_email(receivers:List[str], title:str, content=None, attachment=None):
    email_server_host = 'smtp.gmail.com'
    port = 587
    my_email_username = 'ai4healthybrains@gmail.com'
    my_email_password = 'experience.sample'

    # msg = MIMEMultipart('alternative')
    msg = EmailMessage()
    msg['From'] = my_email_username
    msg['To'] = receivers
    msg['Subject'] = title
    if content:
        msg.set_content(content)
    if attachment:
        mime_type, _ = mimetypes.guess_type(attachment)
        mime_type, mime_subtype = mime_type.split('/')
        with open(attachment, 'rb') as f:
            msg.add_attachment(
                f.read(),
                maintype=mime_type,
                subtype=mime_subtype,
                filename=attachment.split(os.sep)[-1])

    # msg.attach(MIMEText(content, 'html'))

    # create an instance of smtplib.SMTP, which encapsulates an SMTP connection and allows you access to its methods
    # server = smtplib.SMTP(email_server_host, port)
    # server.ehlo()
    # server.starttls()
    # server.login(my_email_username, my_email_password)

    # server.sendmail(my_email_username, receivers, msg.as_string())
    # server.close()

    # https://levelup.gitconnected.com/send-email-using-python-30fc1f203505
    mail_server = smtplib.SMTP_SSL('smtp.gmail.com')
    # mail_server.set_debuglevel(1)
    mail_server.login(my_email_username, my_email_password)
    mail_server.send_message(msg)
    mail_server.quit()

if __name__ == "__main__":
    receivers = ["tristan_wyl@hotmail.com", "tristan_wyl@cuhk.edu.hk"]
    title = "Weekly report of the network traffic of the TBS GPU server"
    content="Hello world!"
    send_email(receivers, title, content)