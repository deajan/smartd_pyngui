#! /usr/bin/env python
#  -*- coding: utf-8 -*-
#
# This file is part of cryptidy module

"""
Asymmetric encryption using RSA private + public keys that encrypt a session key for
AES-256 symmetric encryption routines based on pycryptodomex / pycryptodome
This library may encrypt / decrypt strings, bytes or python objects that support pickling

Versionning semantics:
    Major version: backward compatibility breaking changes
    Minor version: New functionnality
    Patch version: Backwards compatible bug fixes

"""

__intname__ = 'cryptidy.asymmetric_encryption'
__author__ = 'Orsiris de Jong'
__copyright__ = 'Copyright (C) 2020 Orsiris de Jong'
__licence__ = 'BSD 3 Clause'
__version__ = '1.0.3'
__build__ = '2020110302'


from base64 import b64encode, b64decode
from binascii import Error as binascii_Error
from datetime import datetime
from Cryptodome.PublicKey import RSA
from Cryptodome.Random import get_random_bytes
from Cryptodome.Cipher import PKCS1_OAEP
# Make sure we use a solid Hash algorithm, industry standard is SHA256, don't use SHA3 yet as of Nov 2020
from Cryptodome.Hash import SHA384 as HASH_ALGO
# Try to import as absolute when used as module, import as relative for autotests
try:
    from cryptidy.symmetric_encryption import aes_encrypt_message, aes_decrypt_message
except ImportError:
    from .symmetric_encryption import aes_encrypt_message, aes_decrypt_message
from logging import getLogger
from typing import Any, Tuple, Union, NoReturn

logger = getLogger(__name__)


def generate_keys(length: int = 2048) -> Tuple[str, str]:
    """
    RSA key pair generator

    :param length: key size, can be 1024, 2048 or 4096 bits
    :return: (tuple) private_key, public_key as PEM format
    """
    if length < 1024:
        raise ValueError('RSA key length must be >= 1024')
    private_key = RSA.generate(length)
    public_key = private_key.publickey()
    return private_key.export_key().decode(), public_key.export_key().decode()


def verify_private_key(private_key: str) -> NoReturn:
    """
    Simple key type verification to make decryption debugging easier
    """
    if private_key is None:
        raise TypeError('No private key provided.')

    if not '-----BEGIN RSA PRIVATE KEY-----\n' in private_key:
        raise TypeError('Wrong private key provided. Does not look like a PEM encoded key.')


def verify_public_key(public_key: str) -> NoReturn:
    """
    Simple key type verification to make decryption debugging easier
    """
    if public_key is None:
        raise TypeError('No private key provided.')

    if not '-----BEGIN PUBLIC KEY-----\n' in public_key:
        raise TypeError('Wrong private key provided. Does not look like a PEM encoded key.')


def encrypt_message(msg: Any, public_key: str) -> bytes:
    """
    Simple base64 wrapper for rsa_encrypt_message

    :param msg: original encrypted message
    :param public_key: rsa public key
    :return: (bytes) base64 encoded aes encrypted message
    """
    verify_public_key(public_key)
    return b64encode(rsa_encrypt_message(msg, public_key))


def rsa_encrypt_message(msg: Any, public_key: str) -> bytes:
    """
    RSA encrypt a python object / bytes / string and add an encryption timestamp

    :param msg: original data
    :param public_key: rsa public key
    :return: (bytes): encrypted data
    """
    # Note: No need to pickle the message, since this will be done in symmetric encryption

    # Triggers ValueError on invalid pubkey
    public_key = RSA.import_key(public_key)
    cipher_rsa = PKCS1_OAEP.new(key=public_key, hashAlgo=HASH_ALGO)

    # Let's create an aes encryption key based on the RSA pubkey size
    session_key_size = int(public_key.size_in_bits() / 64)
    # Allowed Cryptodomex session_key_sizes are 16, 24 and 32
    session_key_size = 32 if session_key_size > 32 else session_key_size
    session_key = get_random_bytes(session_key_size)

    # RSA encrypt the aes encryption key and use the original key to encrypt our message using AES
    enc_session_key = cipher_rsa.encrypt(session_key)
    return enc_session_key + aes_encrypt_message(msg, session_key)


def decrypt_message(msg: Union[bytes, str], private_key: str) -> Tuple[datetime, Any]:
    """
    Simple base64 wrapper for rsa_decrypt_message

    :param msg: b64 encoded original rsa encrypted data
    :param private_key: rsa private key
    :return: (bytes): rsa decrypted data
    """
    verify_private_key(private_key)
    try:
        decoded_msg = b64decode(msg)
    except (TypeError, binascii_Error):
        raise TypeError('decrypt_message accepts b64 encoded byte objects')

    return rsa_decrypt_message(decoded_msg, private_key)


def rsa_decrypt_message(msg: bytes, private_key: str) -> Tuple[datetime, Any]:
    """
    RSA decrypt a python object / bytes / string and check the encryption timestamp

    :param msg: original rsa encrypted data
    :param private_key: rsa encryption key
    :return: original data
    """
    private_key = RSA.import_key(private_key)
    enc_session_key_size = int(private_key.size_in_bits() / 8)

    cipher_rsa = PKCS1_OAEP.new(key=private_key, hashAlgo=HASH_ALGO)
    enc_session_key, aes_encrypted_msg = \
        (msg[0:enc_session_key_size], msg[enc_session_key_size:])
    try:
        session_key = cipher_rsa.decrypt(enc_session_key)
    except TypeError:
        raise TypeError('You need a private key to decrypt data.')
    except ValueError:
        raise ValueError('RSA Integrity check failed, cannot decrypt data.')

    return aes_decrypt_message(aes_encrypted_msg, session_key)


def _selftest():
    """
    Self test function
    """
    print('Example code for %s, %s' % (__intname__, __build__))
    print('Example RSA private and public key generation and data encryption using AES-256-EAX')
    for key_size in [1024, 2048, 4096]:
        print('\nTesting with %s bits RSA key.\n' % key_size)
        priv_key, pub_key = generate_keys(key_size)

        assert '-----END RSA PRIVATE KEY-----' in priv_key, 'Bogus privkey generated.'
        assert '-----END PUBLIC KEY-----' in pub_key, 'Bogus pubkey generated.'

        msg = b'This string will be encrypted'
        enc_msg = encrypt_message(msg, pub_key)
        print('Encrypted message: %s ' % enc_msg)
        timestamp, dec_msg = decrypt_message(enc_msg, priv_key)
        print('Decrypted message from %s: %s ' % (timestamp, dec_msg))

        assert msg == dec_msg, 'Original message and decrypted one should be the same.'

        test_list = ['This list', 'will be', 'encrypted too !']
        enc_test_list = encrypt_message(test_list, pub_key)
        print('Encrypted list: %s ' % enc_test_list)
        timestamp, dec_test_list = decrypt_message(enc_test_list, priv_key)
        print('Decrypted message from %s: %s ' % (timestamp, dec_test_list))

        assert test_list == dec_test_list, 'Original list and decrypted one should be the same.'

        # Make a "double pickle" test since symmetric encryption already pickles the message
        import pickle
        data = pickle.dumps(('a', 'b', 'c'))
        enc_data = encrypt_message(data, pub_key)
        print('Encrypted data: %s ' % enc_data)
        timestamp, dec_data = decrypt_message(enc_data, priv_key)
        print('Decrypted message from %s: %s ' % (timestamp, pickle.loads(dec_data)))

        assert data == dec_data, 'Original data and decrypted one should be the same.'

        print('Test done with %s bits RSA key.' % key_size)


if __name__ == '__main__':
    _selftest()
