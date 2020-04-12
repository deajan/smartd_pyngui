#! /usr/bin/env python
#  -*- coding: utf-8 -*-

# This file is part of configparser_crypt module

"""
The configparsercrypt module is a dropin replacement for configparser
that allows read/write of symmetric encrypted ini files
This submodule works with ciphers module
 
"""

__intname__ = 'configparser_crypt.fernet_backend'
__author__ = 'Orsiris de Jong'
__copyright__ = 'Copyright (C) 2019-2020 Orsiris de Jong'
__licence__ = 'BSD 3 Clause'
__version__ = '0.2.0'
__build__ = '2020032701'


from configparser import ConfigParser
import os
from cryptography.fernet import Fernet
from base64 import urlsafe_b64decode


class ConfigParserCrypt(ConfigParser):
    """Configuration file parser
    
    A child class of configparser that reads and writes AES encrypted configuration files
    See configparser for usage
    
    ConfigParserFernet behaves excactly like ConfigParser, except it has the following functions:
    
    aes_key = generate_key()
    set_key(aes_key)
    read_scrambled()
    write_scrambled()
    
    (C) 2019-2020 by Orsiris de Jong - www.netpower.fr
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # By default, configparser sets all strings to lowercase, this option let's keep the case
        self.optionxform = str
        self.to_write_data = ''

        # AES cypto key with added random bytes
        self.aes_key = None
        self.randomHeader = os.urandom(1337)
        self.nullBytes = ('\x12' * 8192).encode()
        self.randomFooter = os.urandom(421)

    def set_key(self, aes_key):
        if len(urlsafe_b64decode(aes_key)) is not 32:
            raise ValueError('AES Key should be 16 or 32 bytes, %s bytes given.' % len(urlsafe_b64decode(aes_key)))
        self.aes_key = aes_key

    def generate_key(self):
        try:
            self.aes_key = Fernet.generate_key()
            return self.aes_key
        except Exception as exc:
            raise ValueError('Cannot generate AES key: %s' % exc)

    def read_encrypted(self, filenames, encoding=None, aes_key=None):
        """Read and parse a filename or an iterable of filenames.

        Files that cannot be opened are silently ignored; this is
        designed so that you can specify an iterable of potential
        configuration file locations (e.g. current directory, user's
        home directory, systemwide directory), and all existing
        configuration files in the iterable will be read.  A single
        filename may also be given.

        Return list of successfully read files.
        """
        if isinstance(filenames, (str, bytes, os.PathLike)):
            filenames = [filenames]
        read_ok = []
        for filename in filenames:
            try:
                with open(filename, 'rb') as fp:
                    try:
                        if aes_key is not None:
                            cipher = Fernet(aes_key)
                        elif self.aes_key is not None:
                            cipher = Fernet(self.aes_key)
                        else:
                            raise ValueError('No aes key provided.')
                        aes_key = None
                        rawdata = cipher.decrypt(fp.read())
                        # Remove extra bytes, decode bytes to string, split into list as if lines were read from file
                        data = (rawdata[1337:][:-8192][:-421]).decode('utf-8').split('\n')
                    except Exception as exc:
                        raise ValueError('Cannot read AES data: %s' % exc)
                    self._read(data, filename)
            except OSError:
                continue
            if isinstance(filename, os.PathLike):
                filename = os.fspath(filename)
            read_ok.append(filename)
        return read_ok

    def write_encrypted(self, fp, space_around_delimiters=True, aes_key=None):
        """Write an .ini-format representation of the configuration state.

        If `space_around_delimiters' is True (the default), delimiters
        between keys and values are surrounded by spaces.
        """

        self.to_write_data = ''

        if space_around_delimiters:
            d = " {} ".format(self._delimiters[0])
        else:
            d = self._delimiters[0]
        if self._defaults:
            self._write_section_encrypted(self.default_section, self._defaults.items(), d)
        for section in self._sections:
            self._write_section_encrypted(section, self._sections[section].items(), d)

        self.commit_write(fp, aes_key=aes_key)

    def _write_section_encrypted(self, section_name, section_items, delimiter):
        """Write a single section to the specified `fp'."""
        self.to_write_data += "[{}]\n".format(section_name)
        for key, value in section_items:
            value = self._interpolation.before_write(self, section_name, key,
                                                     value)
            if value is not None or not self._allow_no_value:
                value = delimiter + str(value).replace('\n', '\n\t')
            else:
                value = ""
            self.to_write_data += "{}{}\n".format(key, value)
        self.to_write_data += "\n"

    def commit_write(self, fp, aes_key=None):
        try:
            if aes_key is not None:
                cipher = Fernet(aes_key)
            elif self.aes_key is not None:
                cipher = Fernet(self.aes_key)
            else:
                raise('No AES key provided.')
            aes_key = None
            fp.write(cipher.encrypt(self.randomHeader + self.to_write_data.encode('utf-8')
                                    + self.nullBytes + self.randomFooter))
        except Exception as exc:
            raise ValueError('Cannot write AES data: %s' % exc)


def _selftest():
    print('Example code for %s, %s, %s' % (__intname__, __version__, __build__))
    c = ConfigParserCrypt()
    c.generate_key()
    test_file = 'test_file'
    c.add_section('TEST')
    c['TEST']['spam'] = 'eggs'
    with open(test_file, 'wb') as fp:
        c.write_encrypted(fp)
    c['TEST']['spam'] = 'No'
    c.read_encrypted(test_file)
    print('spam = %s' % c['TEST']['spam'])


if __name__ == '__main__':
    _selftest()