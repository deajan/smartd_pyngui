#! /usr/bin/env python
#  -*- coding: utf-8 -*-

from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
import ssl

def mailer(source_mail=None, destination_mails=None, split_mails=False, smtp_server=None, smtp_port=25, smtp_user=None,
           smtp_password=None, security=None, subject=None, body=None, attachment=None, html_enabled=False,
           debug=False):

    if subject is None:
        raise ValueError('No subject set')

    if destination_mails is None:
        raise ValueError('No destination mails set')

    # Create a multipart message and set headers
    message = MIMEMultipart()
    message["From"] = source_mail
    message["To"] = destination_mails
    message["Subject"] = subject
   # message["Bcc"] = receiver_email  # Recommended for mass emails

    # Add body to email
    message.attach(MIMEText(body, "plain"))
    if html_enabled:
        message.attach(MIMEText(body, "html"))
    if attachment is not None:
        with open(attachment, 'rb') as h_attachment:
            # Add file as application/octet-stream
            # Email client can usually download this automatically as attachment
            part = MIMEBase("application", "octet-stream")
            part.set_payload(h_attachment.read())

            # Encode file in ASCII characters to send by email
            encoders.encode_base64(part)

            # Add header as key/value pair to attachment part
            part.add_header(
                "Content-Disposition",
                f"attachment; filename= {attachment}",
            )

            # Add attachment to message and convert message to string
            message.attach(part)

    text = message.as_string()

    # Not working yet, check on port 465 necessary
    if security == 'ssl':
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(smtp_server, smtp_port, context=context) as remote_server:
            if debug:
                remote_server.set_debuglevel(True)
            remote_server.ehlo()
            remote_server.login(smtp_user, smtp_password)
            remote_server.sendmail(source_mail, destination_mails, text)

    elif security == 'tls':
        # TLS
        context = ssl.create_default_context()
        with smtplib.SMTP(smtp_server, smtp_port) as remote_server:
            if debug:
                remote_server.set_debuglevel(True)
            remote_server.ehlo()
            remote_server.starttls(context=context)
            remote_server.ehlo()
            remote_server.login(smtp_user, smtp_password)
            remote_server.sendmail(source_mail, destination_mails, text)

    else:
        with smtplib.SMTP(smtp_server, smtp_port) as remote_server:
            if debug:
                remote_server.set_debuglevel(True)
            remote_server.ehlo()
            remote_server.login(smtp_user, smtp_password)
            remote_server.sendmail(source_mail, destination_mails, text)
