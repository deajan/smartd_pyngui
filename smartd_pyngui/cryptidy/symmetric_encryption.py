#! /usr/bin/env python
#  -*- coding: utf-8 -*-
#
# This file is part of cryptidy module

"""
AES-256 symmetric encryption routines based on pycryptodomex / pycryptodome
This library may encrypt / decrypt strings, bytes or python objects that support pickling


Versionning semantics:
    Major version: backward compatibility breaking changes
    Minor version: New functionnality
    Patch version: Backwards compatible bug fixes

"""

__intname__ = 'cryptidy.symmetric_encryption'
__author__ = 'Orsiris de Jong'
__copyright__ = 'Copyright (C) 2018-2020 Orsiris de Jong'
__licence__ = 'BSD 3 Clause'
__version__ = '1.0.3-imfcompat' # Remove all # COMPAT comments to remove earlier comapt shim
__build__ = '2020110302'

from base64 import b64encode, b64decode
from binascii import Error as binascii_Error
from datetime import datetime
import pickle
# Try to import as absolute when used as module, import as relative for autotests
try:
    from cryptidy.padding import pad, unpad
except ImportError:
    from .padding import pad, unpad
try:
    from cryptidy.aes_encryption import aes_encrypt, aes_decrypt, generate_key
except ImportError:
    from .aes_encryption import aes_encrypt, aes_decrypt, generate_key
from logging import getLogger
from typing import Any, Union, Tuple, NoReturn

logger = getLogger(__name__)


def verify_key(aes_key: bytes) -> NoReturn:
    """
    Simple key length and type verification to make decryption debugging easier
    """

    if not len(aes_key) in [16, 24, 32]:
        raise TypeError('Wrong encryption key provided. Allowed key sizes are 16, 24 or 32 bytes.')
    if 'BEGIN' in aes_key.decode('utf-8', errors='backslashreplace'):
        raise TypeError('Wrong encryption key provided. This looks like an RSA key.')
    if not isinstance(aes_key, bytes):
        raise TypeError('Wrong encryption key provided. Key type should be binary.')


def encrypt_message(msg: Any, aes_key: bytes) -> bytes:
    """
    Simple base64 wrapper for aes_encrypt_message
    """
    verify_key(aes_key)
    return b64encode(aes_encrypt_message(msg, aes_key))


def aes_encrypt_message(msg: Any, aes_key: bytes) -> bytes:
    """
    AES encrypt a python object / bytes / string and add an encryption timestamp

    :param msg: original data, can be a python object, bytes, str or else
    :param aes_key: aes encryption key
    :return: (bytes): encrypted data
    """

    try:
        try:
            # Always try to pickle whatever we receive
            nonce, tag, ciphertext = aes_encrypt(pickle.dumps(msg), aes_key)
        except (TypeError, pickle.PicklingError, OverflowError):
            # Allow a fallback solution when object is not pickable
            # msg accepts bytes or text
            if isinstance(msg, bytes):
                nonce, tag, ciphertext = aes_encrypt(msg, aes_key)
            elif isinstance(msg, str):
                nonce, tag, ciphertext = aes_encrypt(msg.encode('utf-8'), aes_key)
            else:
                raise ValueError('Invalid type of data given for AES encryption.')

        timestamp = pad(str(datetime.now().timestamp())).encode('utf-8')
        return nonce + tag + timestamp + ciphertext
    except Exception as exc:
        raise ValueError('Cannot AES encrypt data: %s.' % exc)


def decrypt_message(msg: Union[bytes, str], aes_key: bytes) -> Tuple[datetime, Any]:
    """
    Simple base64 wrapper for aes_decrypt_message
    """
    verify_key(aes_key)
    try:  # COMPAT
        try:
            decoded_msg = b64decode(msg)
        except (TypeError, binascii_Error):
            raise TypeError('decrypt_message accepts b64 encoded byte objects')

        return aes_decrypt_message(decoded_msg, aes_key)
    except:  # COMPAT
        return aes_decrypt_message(msg, aes_key)  # COMPAT


def aes_decrypt_message(msg: bytes, aes_key: bytes) -> Tuple[datetime, Any]:
    """
    AES decrypt a python object / bytes / string and check the encryption timestamp

    :param msg: original aes encrypted data
    :param aes_key: aes encryption key
    :return: original data
    """
    nonce, tag, timestamp, ciphertext = (msg[0:16],
                                         msg[16:32],
                                         msg[32:64],
                                         msg[64:])

    #  COMPAT-IMF3 <3.6.0 PATCH
    try:  # COMPAT
        source_timestamp = float(unpad(timestamp.decode('utf-8')))
        if source_timestamp > datetime.now().timestamp():
            raise ValueError('Timestamp is in future')
        source_timestamp = datetime.fromtimestamp(source_timestamp)
    except:  # COMPAT
        source_timestamp = None  # COMPAT
        ciphertext = msg[32:]  # COMPAT

    try:
        data = aes_decrypt(aes_key, nonce, tag, ciphertext)
        try:
            data = pickle.loads(data)
        # May happen on unpickled encrypted data when pickling failed on encryption and fallback was used
        except (pickle.UnpicklingError, TypeError, OverflowError, KeyError):
            pass
        except Exception as exc:
            logger.error('cryptidy unpicke error: {0}. Is data pickled ?'.format(exc))
            logger.info('Trace:', exc_info=True)
        return source_timestamp, data
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
        print('\nKey is %s bytes long\n' % key_size)

        assert len(key) == key_size, 'Encryption key should be 32 bytes long.'

        msg = ['This list shall be encrypted', 'This string in list will be encrypted']
        print(msg)
        enc_msg = encrypt_message(msg, key)
        print('Encrypted message: %s ' % enc_msg)
        timestamp, dec_msg = decrypt_message(enc_msg, key)
        print('Decrypted message: date=%s: %s ' % (timestamp, dec_msg))

        assert msg == dec_msg, 'Original message and decrypted one should be the same.'

        test_list = ['This list', 'will be', 'encrypted too !']
        print(test_list)
        enc_list = encrypt_message(test_list, key)
        print('Encrypted list: %s ' % enc_list)
        timestamp, dec_list = decrypt_message(enc_list, key)
        print('Decrypted list: date=%s: %s ' % (timestamp, dec_list))

        assert test_list == dec_list, 'Original list and decrypted one should be the same.'

        # We shall also check for multiline strings that shall be encrypted / decrypted as one
        test_mlstring = "Hello\nWorld"
        print(test_mlstring)
        enc_mlstring = encrypt_message(test_mlstring, key)
        print('Encrypted multiline string: %s ' % enc_mlstring)
        timestap, dec_mlstring = decrypt_message(enc_mlstring, key)
        print('Decrypted multiline string: date=%s: %s ' % (timestamp, dec_mlstring))

        assert test_mlstring == dec_mlstring, 'Original multiline string and decrypted one should be the same.'


if __name__ == '__main__':
    _selftest()
