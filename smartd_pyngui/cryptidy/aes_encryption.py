#! /usr/bin/env python
#  -*- coding: utf-8 -*-
#
# This file is part of cryptidy module

"""
Simple AES encryption wrapper used by symmetric and asymmetric encryption modules

Versionning semantics:
    Major version: backward compatibility breaking changes
    Minor version: New functionnality
    Patch version: Backwards compatible bug fixes

"""

__intname__ = 'cryptidy.aes_encryption'
__author__ = 'Orsiris de Jong'
__copyright__ = 'Copyright (C) 2020 Orsiris de Jong'
__licence__ = 'BSD 3 Clause'
__version__ = '1.0.0'
__build__ = '2020062801'


from typing import Union, Tuple
from Cryptodome.Cipher import AES
from Cryptodome.Random import get_random_bytes
from logging import getLogger


logger = getLogger(__name__)


def generate_key(size: int = 32) -> bytes:
    """
    AES key generator


    :param size: (int) key size, can be 16, 24 or 32 bytes
    :return: (bytes) aes key
    """
    try:
        aes_key = get_random_bytes(size)
        return aes_key
    except Exception as exc:
        raise ValueError('Cannot generate AES key: %s' % exc)


def aes_encrypt(msg: bytes, aes_key: bytes) -> Tuple[Union[bytes, bytearray, memoryview], bytes, bytes]:
    """
    Encrypt a bytes message

    :param msg:  Message to encrypt
    :param aes_key: AES encryption key

    :return: (tuple) encrypted message composed of nonce, tag and ciphertext
    """
    try:
        if aes_key is not None:
            cipher = AES.new(aes_key, AES.MODE_EAX)
            # wipe key from memory as soon as it's been used
            aes_key = None
        else:
            raise ValueError('No AES key provided.')

        ciphertext, tag = cipher.encrypt_and_digest(msg)
        return cipher.nonce, tag, ciphertext
    except Exception as exc:
        raise ValueError('Cannot encode AES data: %s' % exc)


def aes_decrypt(aes_key: bytes, nonce: bytes, tag: bytes, ciphertext: bytes) -> bytes:
    """
    Decrypt a bytes message

    :param aes_key: AES encryption key
    :param nonce: encryption nonce
    :param tag: encryption tag
    :param ciphertext: message to decrypt
    :return: (bytes) original message
    """

    try:
        if aes_key is not None:
            cipher = AES.new(aes_key, AES.MODE_EAX, nonce)
            # wipe key from memory as soon as it's been used
            aes_key = None
        else:
            raise ValueError('No aes key provided.')

        data = cipher.decrypt_and_verify(ciphertext, tag)
        return data
    except Exception as exc:
        raise ValueError('Cannot read AES data: %s' % exc)


def _selftest():
    """
    Self test function
    """
    print('Example code for %s, %s' % (__intname__, __build__))
    print('Example key generation and data encryption using AES-256-EAX')
    for key_size in [16, 32]:
        key = generate_key(key_size)
        print('Key is %s' % key_size)

        assert len(key) == key_size, 'Encryption key should be 32 bytes long.'

        msg = b'This is a meessage'
        print('Original message: {0}'.format(msg))
        enc_msg = aes_encrypt(msg, key)
        print('Encoded message: {0}'.format(enc_msg))
        dec_msg = aes_decrypt(key, *enc_msg)
        print('Decoded message: {0}'.format(dec_msg))

        assert msg == dec_msg, 'Original message and decrypted one should be the same.'


if __name__ == '__main__':
    _selftest()
