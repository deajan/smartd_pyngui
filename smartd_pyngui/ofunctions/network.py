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

__intname__ = 'ofunctions.netowrk'
__author__ = 'Orsiris de Jong'
__copyright__ = 'Copyright (C) 2014-2020 Orsiris de Jong'
__licence__ = 'BSD 3 Clause'
__version__ = '0.2.5'
__build__ = '2020111601'

import os
from typing import List, Tuple, Union
from command_runner import command_runner
from requests import get
import warnings
import logging


logger = logging.getLogger()


def ping(servers: List[str] = None) -> bool:
    """
    Tests if ICMP ping works
    At least one good result gives a positive result
    """
    if servers is None:
        # Cloudflare, Google and OpenDNS dns servers
        servers = ['1.1.1.1', '8.8.8.8', '208.67.222.222']

    ping_success = False

    def _try_server(server):
        if os.name == 'nt':
            command = f'ping -n 2 {server}'
            encoding = 'cp437'
        else:
            command = f'ping -c 2 {server}'
            encoding = 'utf-8'
        result, _ = command_runner(command, encoding=encoding)
        if result == 0:
            return True
        else:
            return False

    for server in servers:
        if _try_server(server):
            ping_success = True
            break

    return ping_success


def test_http_internet(fqdn_servers: List[str] = None, ip_servers: List[str] = None,
                       proxy: str = None, timeout: int = 5) -> bool:
    """
    Tests if http(s) internet works
    At least one good result gives a positive result
    """
    if fqdn_servers is None:
        # Let's use some well known default servers
        fqdn_servers = ['http://www.google.com', 'https://www.google.com', 'http://kernel.org']
    if fqdn_servers is False:
        fqdn_servers = []
    if ip_servers is None:
        # Cloudflare dns servers respond to http requests, let's use them for ping checks
        ip_servers = ['http://1.1.1.1', 'https://1.0.0.1']
    if ip_servers is False:
        ip_servers = []

    fqdn_success = False
    ip_success = False
    diag_messages = ''

    def proxy_dict(proxy: str) -> Union[dict, None]:
        if proxy is not None:
            if proxy.startswith('http'):
                return {'http': proxy.strip('http://')}
            elif proxy.startswith('https'):
                return {'https': proxy.strip('https://')}
        return None

    def _try_server(server: str, proxy_dict: dict) -> Tuple[bool, str]:
        diag_messages = ''

        # With optional proxy
        try:
            with warnings.catch_warnings():
                warnings.filterwarnings("ignore", category=Warning)
                r = get(server, proxies=proxy_dict, verify=False, timeout=timeout)
            status_code = r.status_code
        except Exception as exc:
            diag_messages = '{0}\n{1}'.format(diag_messages, str(exc))
            status_code = -1
        if status_code == 200:
            return True, diag_messages
        else:
            # Check without proxy (if set)
            if proxy_dict is not None:
                try:
                    with warnings.catch_warnings():
                        warnings.filterwarnings("ignore", category=Warning)
                        r = get(server, verify=False, timeout=timeout)
                    status_code = r.status_code
                except Exception as exc:
                    diag_messages = '{0}\n{1}'.format(diag_messages, str(exc))
                    status_code = -2
                if status_code == 200:
                    # diag_messages = diag_messages + f'\nCould connect to [{server}].'
                    return True, diag_messages
            diag_messages = '{0}\nCould not connect to [{1}], http error {2}.'.format(diag_messages, server,
                                                                                      status_code)
            return False, diag_messages

    for fqdn_server in fqdn_servers:
        result, diag = _try_server(fqdn_server, proxy_dict(proxy))
        diag_messages = diag_messages + diag
        if result:
            fqdn_success = True
            break

    for ip_server in ip_servers:
        result, diag = _try_server(ip_server, proxy_dict(proxy))
        diag_messages = diag_messages + diag
        if result:
            ip_success = True
            break

    if (not (fqdn_servers and fqdn_success)) and ip_success:
        diag_messages = diag_messages + '\nLooks like a DNS resolving issue. Internet works by IP surfing.'
        logger.info(diag_messages)
        return True

    if not ((fqdn_servers and fqdn_success) or (ip_servers and ip_success)):
        logger.info(diag_messages)
        return False

    return True


def _selftest():
    logger.addHandler(logging.StreamHandler())
    logger.setLevel(logging.INFO)
    print('Example code for %s, %s, %s' % (__intname__, __version__, __build__))
    result = ping()
    print('Ping result: %s' % result)
    assert result is True, 'Cannot ping. This test may fail if the host' \
                           'does not have internet indeed.'

    # Make sure http://1.1.1.1 or http://1.0.0.1 (or whatever you want to test) works, at least one of those two
    result = test_http_internet(ip_servers=['http://1.1.1.1', 'http://1.0.0.1'])
    print('HTTP result: %s' % result)
    assert result is True, 'Cannot check http internet. This test may fail if the host' \
                           'does not have internet indeed.'

    # Hopefully these adresses don't exist
    result = test_http_internet(['http://example.not.existing'], ['http://192.168.90.256'])
    print('HTTP result: %s' % result)
    assert result is False, 'Bogus http check should give negative result'

    # This one should give positive result too
    result = test_http_internet(['http://www.google.com', 'http://example.not.existing'])
    print('HTTP result: %s' % result)
    assert result is True, 'At least one good result should trigger postive result. This test may fail if the host' \
                           'does not have internet indeed.'

if __name__ == '__main__':
    _selftest()
