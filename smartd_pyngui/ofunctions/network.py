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
__version__ = '0.2.0'
__build__ = '2020040601'


import os
from command_runner import command_runner
from requests import get
import warnings



def ping(servers=None):
    if servers is None:
        # Cloudflare, Google and OpenDNS dns servers
        servers = ['1.1.1.1', '8.8.8.8', '208.67.222.222']

    ping_success = False

    def _try_server(server):
        if os.name == 'nt':
            command = f'ping -n 2 {server}'
        else:
            command = f'ping -c 2 {server}'
        result, _ = command_runner(command)
        if result == 0:
            return True
        else:
            return False

    for server in servers:
        if _try_server(server):
            ping_success = True
            break

    return ping_success


def test_http_internet(fqdn_servers=None, ip_servers=None, proxy=None):
    if fqdn_servers is None:
        fqdn_servers = ['http://www.google.com', 'https://www.google.com', 'http://kernel.org']
    if ip_servers is None:
        # Cloudflare dns servers respond to http requests
        ip_servers = ['http://1.1.1.1', 'https://1.0.0.1']

    fqdn_success = False
    ip_success = False
    diag_messages = ''

    def proxy_dict(proxy):
        if proxy is not None:
            if proxy.startswith('http'):
                return {'http': proxy.strip('http://')}
            elif proxy.startswith('https'):
                return {'https': proxy.strip('https://')}
        return None

    def _try_server(server, proxy_dict):
        diag_messages = ''

        # With optional proxy
        try:
            with warnings.catch_warnings():
                warnings.filterwarnings("ignore", category=Warning)
                r = get(server, proxies=proxy_dict, verify=False)
            status_code = r.status_code
        except Exception as e:
            diag_messages = diag_messages + e
            status_code = 0
        if status_code == 200:
            return True, diag_messages
        else:
            # Check without proxy (if set)
            if proxy_dict is not None:
                try:
                    with warnings.catch_warnings():
                        warnings.filterwarnings("ignore", category=Warning)
                        r = get(server, verify=False)
                    status_code = r.status_code
                except Exception as e:
                    diag_messages = diag_messages + e
                    status_code = 0
                if status_code == 200:
                    # diag_messages = diag_messages + f'\nCould connect to [{server}].'
                    return True, diag_messages
            diag_messages = diag_messages + f'\nCould not connect to [{server}].'
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

    if (not fqdn_success) and ip_success:
        diag_messages = diag_messages + '\nLooks like a DNS resolving issue to me. Internet works by IP surfing.'
        return True, diag_messages

    if not (fqdn_success and ip_success):
        return False, diag_messages

    return True, diag_messages


def _selftest():
    print('Example code for %s, %s, %s' % (__intname__, __version__, __build__))
    result = ping()
    print('Ping result: %s' % result)
    assert result == True, 'Cannot ping'
    
    result, output = test_http_internet()
    print('HTTP result: %s, msg: %s' % (result, output))
    assert result == True, 'Cannot check http internet'
    

if __name__ == '__main__':
    _selftest()