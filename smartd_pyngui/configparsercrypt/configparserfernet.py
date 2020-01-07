"""Configuration file parser

A child class of configparser that reads and writes AES encrypted configuration files
See configparser for usage

ConfigParserCrypt behaves excactly like ConfigParser, except it has the following functions:

aes_key = generate_key()
set_key(aes_key)
read_scrambled()
write_scrambled()

(C) 2019-2020 by Orsiris de Jong - www.netpower.fr
"""

from configparser import ConfigParser
import os
from cryptography.fernet import Fernet
from base64 import urlsafe_b64decode

VERSION = '0.1.1'
BUILD = 2020010701


class ConfigParserCrypt(ConfigParser):
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

    def read_encrypted(self, filenames, encoding=None):
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
                        cipher = Fernet(self.aes_key)
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

    def write_encrypted(self, fp, space_around_delimiters=True):
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

        self.commit_write(fp)

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

    def commit_write(self, fp):
        try:
            cipher = Fernet(self.aes_key)
            fp.write(cipher.encrypt(self.randomHeader + self.to_write_data.encode('utf-8')
                                    + self.nullBytes + self.randomFooter))
        except Exception as exc:
            raise ValueError('Cannot write AES data: %s' % exc)
