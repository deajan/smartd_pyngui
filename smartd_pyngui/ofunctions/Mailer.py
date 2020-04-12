#! /usr/bin/env python
#  -*- coding: utf-8 -*-
#
# This file is part of ofunctions module

"""
ofunctions is a general library for basic repetitive tasks that should be no brainers :)

Versionning semantics:
    Major version: backward compatibility breaking changes
    Minor version: New functionnality
    Patch version: Backwards compatible bug fixes

"""

__intname__ = 'ofunctions.mailer'
__author__ = 'Orsiris de Jong'
__copyright__ = 'Copyright (C) 2014-2020 Orsiris de Jong'
__licence__ = 'BSD 3 Clause'
__version__ = '0.2.0'
__build__ = '2020041001'


import os
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
import ssl
import socket
import re


def send_email(source_mail=None, destination_mails=None, split_mails=False, smtp_server='localhost', smtp_port=25,
               smtp_user=None, smtp_password=None, security=None, subject=None, body=None, attachment=None,
               filename=None, html_enabled=False, bcc_mails=None,priority=False, debug=False):
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
    :param filename: If filename is given, we suppose attachment is inline binary data
    :param html_enabled:
    :param bcc_mails:
    :param priority: (bool) set to true to add a high priority flag
    :param debug:
    :return:
    """

    if subject is None:
        raise ValueError('No subject set')

    # Fix for empty passed auth strings
    if len(smtp_user) == 0:
        smtp_user = None
    if len(smtp_password) == 0:
        smtp_password = None

    if destination_mails is None:
        raise ValueError('No destination mails set')
    elif isinstance(list, destination_mails):
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

        if priority:
            message["X-Priority"] = 2

        # Add body to email
        if body is not None:
            if html_enabled:
                message.attach(MIMEText(body, "html"))
            else:
                message.attach(MIMEText(body, "plain"))

        if attachment is not None:
            if filename is not None:
                # Let's suppose we directly attach binary data
                payload = attachment
            else:
                with open(attachment, 'rb') as f_attachment:
                    payload = f_attachment.read()
                    filename = os.path.basename(attachment)

            # Add file as application/octet-stream
            # Email client can usually download this automatically as attachment
            part = MIMEBase("application", "octet-stream")
            part.set_payload(payload)

            # Encode file in ASCII characters to send by email
            encoders.encode_base64(part)

            # Add header as key/value pair to attachment part
            part.add_header(
                "Content-Disposition",
                "attachment; filename=%s" % filename,
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


def is_mail_address(string):
    if re.match(r'[^@\s]+@[^@\s]+\.[a-zA-Z0-9]+$', string):
        return True
    else:
        return False