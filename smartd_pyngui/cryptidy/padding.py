#! /usr/bin/env python
#  -*- coding: utf-8 -*-
#
# This file is part of cryptidy module

"""
Padding functions for cryptography usage

Versionning semantics:
    Major version: backward compatibility breaking changes
    Minor version: New functionnality
    Patch version: Backwards compatible bug fixes

"""

__intname__ = 'cryptidy.padding'
__author__ = 'Orsiris de Jong'
__copyright__ = 'Copyright (C) 2020 Orsiris de Jong'
__licence__ = 'BSD 3 Clause'
__version__ = '0.1.1'
__build__ = '2020102801'


def pad(s: str, pad_len: int = 32) -> str:
    return s + (pad_len - len(s) % pad_len) * chr(pad_len - len(s) % pad_len)

def unpad(s: str) -> str:
    return s[0:-ord(s[-1])]


# lambda function version
# pad_len = 32
# pad = (lambda s: s + (pad_len - len(s) % pad_len) * chr(pad_len - len(s) % pad_len))
# unpad = lambda s: s[0:-ord(s[-1])]


def _selftest():
    print('Example code for %s, %s' % (__intname__, __build__))
    from datetime import datetime
    msg = '%s' % datetime.now()
    padded_msg = pad(msg)
    unpadded_msg = unpad(padded_msg)
    print('Original timestamp: %s' % msg)
    print('Padded timestamp: %s' % padded_msg)
    print('Unpadded timestamp: %s' % unpadded_msg)

    assert len(padded_msg) == 32, 'Padded message is not 32 chars long.'
    assert msg == unpadded_msg, 'Original message and unpadded one should be the same.'

if __name__ == '__main__':
    _selftest()
