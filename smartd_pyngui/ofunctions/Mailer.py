#! /usr/bin/env python
#  -*- coding: utf-8 -*-

from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
import ssl
import socket
import os


def send_email(source_mail=None, destination_mails=None, split_mails=False, smtp_server='localhost', smtp_port=25,
               smtp_user=None, smtp_password=None, security=None, subject=None, body=None, attachment=None,
               html_enabled=False, bcc_mails=None, debug=False):
    """

    :param source_mail:
    :param destination_mails: Accepts space separated email addresses or list of email addresses
    :param split_mails: When multiple mails exist, shall we create an email per addresss or an unique one
    :param smtp_server:
    :param smtp_port:
    :param smtp_user:
    :param smtp_password:
    :param security:
    :param subject:
    :param body:
    :param attachment:
    :param html_enabled:
    :param bcc_mails:
    :param debug:
    :return:
    """

    if subject is None:
        raise ValueError('No subject set')

    if destination_mails is None:
        raise ValueError('No destination mails set')
    elif type(destination_mails) is not list:
        # Make sure destination mails is a list
        destination_mails = destination_mails.split(' ')

    for destination_mail in destination_mails:

        # Create a multipart message and set headers
        message = MIMEMultipart()
        message["From"] = source_mail
        if split_mails:
            message["To"] = destination_mail
        else:
            message["To"] = ' '.join(destination_mails)
        message["Subject"] = subject

        if bcc_mails is not None:
            message["Bcc"] = bcc_mails  # Recommended for mass emails

        # Add body to email
        if body is not None:
            if html_enabled:
                message.attach(MIMEText(body, "html"))
            else:
                message.attach(MIMEText(body, "plain"))

        if attachment is not None:
            with open(attachment, 'rb') as f_attachment:
                # Add file as application/octet-stream
                # Email client can usually download this automatically as attachment
                part = MIMEBase("application", "octet-stream")
                part.set_payload(f_attachment.read())

                # Encode file in ASCII characters to send by email
                encoders.encode_base64(part)

                # Add header as key/value pair to attachment part
                part.add_header(
                    "Content-Disposition",
                    f"attachment; filename= {os.path.basename(attachment)}",
                )

                # Add attachment to message and convert message to string
                message.attach(part)

        text = message.as_string()

        try:
            if security == 'ssl':
                context = ssl.create_default_context()
                with smtplib.SMTP_SSL(smtp_server, smtp_port, context=context) as remote_server:
                    if debug:
                        remote_server.set_debuglevel(True)
                    remote_server.ehlo()
                    if smtp_user is not None and smtp_password is not None:
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
                    if smtp_user is not None and smtp_password is not None:
                        remote_server.login(smtp_user, smtp_password)
                    remote_server.sendmail(source_mail, destination_mails, text)

            else:
                with smtplib.SMTP(smtp_server, smtp_port) as remote_server:
                    if debug:
                        remote_server.set_debuglevel(True)
                    remote_server.ehlo()
                    if smtp_user is not None and smtp_password is not None:
                        remote_server.login(smtp_user, smtp_password)
                    remote_server.sendmail(source_mail, destination_mails, text)
        except ConnectionRefusedError as e:
            return e
        except ConnectionAbortedError as e:
            return e
        except ConnectionResetError as e:
            return e
        except ConnectionError as e:
            return e
        except socket.gaierror as e:
            return e
        except smtplib.SMTPNotSupportedError as e:
            # Server does not support STARTTLS
            return e
        except ssl.SSLError as e:
            return e
        except smtplib.SMTPAuthenticationError as e:
            return e

        if not split_mails:
            break

    return True
