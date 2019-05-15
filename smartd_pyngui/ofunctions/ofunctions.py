#! /usr/bin/env python
#  -*- coding: utf-8 -*-

"""
ofunctions is a general library for basic repetitive tasks that should not require brain :)
Written in 2019 by Orsiris de Jong - http://www.netpower.fr
"""

import subprocess
import os
import sys
import re
import logging
import tempfile
import time
from logging.handlers import RotatingFileHandler

VERSION = '0.1.3'
BUILD = '2019051501'

import ofunctions.FileUtils as FileUtils

if os.name == 'nt':
    try:
        import ctypes
    except ImportError:
        raise ImportError('Cannot import ctypes for checking admin privileges on Windows platform.')

logger = logging.getLogger(__name__)

# Logging functions ########################################################

FORMATTER = logging.Formatter('%(asctime)s :: %(levelname)s :: %(message)s')


def is_admin():
    """
    Checks whether current program has administrative privileges in OS
    Works with Windows XP SP2+ and most Unixes

    :return: Boolean, True if admin privileges present
    """
    current_os_name = os.name

    # Works with XP SP2 +
    if current_os_name == 'nt':
        try:
            return ctypes.windll.shell32.IsUserAnAdmin() == 1
        except Exception:
            raise EnvironmentError('Cannot check admin privileges')
    elif current_os_name == 'posix':
        # Check for root on Posix
        return os.getuid() == 0
    else:
        raise EnvironmentError('OS does not seem to be supported for admin check. OS: %s' % current_os_name)


def logger_get_console_handler():
    try:
        console_handler = logging.StreamHandler(sys.stdout)
    except OSError as exc:
        print('Cannot log to stdout, trying stderr. Message %s' % exc)
        try:
            console_handler = logging.StreamHandler(sys.stderr)
            console_handler.setFormatter(FORMATTER)
            return console_handler
        except OSError as exc:
            print('Cannot log to stderr neither. Message %s' % exc)
            return False
    else:
        console_handler.setFormatter(FORMATTER)
        return console_handler


def logger_get_file_handler(log_file):
    err_output = None
    try:
        file_handler = RotatingFileHandler(log_file, mode='a', encoding='utf-8', maxBytes=1024000, backupCount=3)
    except OSError as exc:
        try:
            print('Cannot create logfile. Trying to obtain temporary log file.\nMessage: %s' % exc)
            err_output = str(exc)
            temp_log_file = tempfile.gettempdir() + os.sep + __name__ + '.log'
            print('Trying temporary log file in ' + temp_log_file)
            file_handler = RotatingFileHandler(temp_log_file, mode='a', encoding='utf-8', maxBytes=1000000,
                                               backupCount=1)
            file_handler.setFormatter(FORMATTER)
            err_output += '\nUsing [%s]' % temp_log_file
            return file_handler, err_output
        except OSError as exc:
            print('Cannot create temporary log file either. Will not log to file. Message: %s' % exc)
            return False
    else:
        file_handler.setFormatter(FORMATTER)
        return file_handler, err_output


def logger_get_logger(log_file=None, temp_log_file=None, debug=False):
    # If a name is given to getLogger, than modules can't log to the root logger
    _logger = logging.getLogger()
    if debug is True:
        _logger.setLevel(logging.DEBUG)
    else:
        _logger.setLevel(logging.INFO)
    console_handler = logger_get_console_handler()
    if console_handler:
        _logger.addHandler(console_handler)
    if log_file is not None:
        file_handler, err_output = logger_get_file_handler(log_file)
        if file_handler:
            _logger.addHandler(file_handler)
            _logger.propagate = False
            if err_output is not None:
                print(err_output)
                _logger.warning('Failed to use log file [%s], %s.', log_file, err_output)
    if temp_log_file is not None:
        if os.path.isfile(temp_log_file):
            try:
                os.remove(temp_log_file)
            except OSError:
                logger.warning('Cannot remove temp log file [%s].' % temp_log_file)
        file_handler, err_output = logger_get_file_handler(temp_log_file)
        if file_handler:
            _logger.addHandler(file_handler)
            _logger.propagate = False
            if err_output is not None:
                print(err_output)
                _logger.warning('Failed to use log file [%s], %s.', log_file, err_output)
    return _logger


# Platform specific functions ###################################################


def get_os():
    if os.name == 'nt':
        return 'Windows'
    elif os.name == 'posix':
        result = os.uname()[0]

        if result.startswith('MSYS_NT-'):
            result = 'Windows'

        return result
    else:
        raise OSError("Cannot get os, os.name=[%s]." % os.name)


def python_arch():
    if get_os() == "Windows":
        if 'AMD64' in sys.version:
            return 'x64'
        else:
            return 'x86'
    else:
        return os.uname()[4]


# Standard functions ############################################################

def time_is_between(current_time, time_range):
    """
    https://stackoverflow.com/a/45265202/2635443
    print(is_between("11:00", ("09:00", "16:00")))  # True
    print(is_between("17:00", ("09:00", "16:00")))  # False
    print(is_between("01:15", ("21:30", "04:30")))  # True
    """

    if time_range[1] < time_range[0]:
        return time >= time_range[0] or time <= time_range[1]
    return time_range[0] <= current_time <= time_range[1]


def bytes_to_string(bytes_to_convert):
    """
    Litteral bytes to string
    :param bytes_to_convert: list of bytes
    :return: resulting string
    """
    if not bytes_to_convert:
        return False
    try:
        return ''.join(chr(i) for i in bytes_to_convert)
    except ValueError:
        return False


def command_runner(command, valid_exit_codes=[], timeout=30, shell=False, decoder='utf-8'):
    """
    command_runner 2019011001
    Whenever we can, we need to avoid shell=True in order to preseve better security
    Runs system command, returns exit code and stdout/stderr output, and logs output on error
    valid_exit_codes is a list of codes that don't trigger an error
    """
    try:
        # universal_newlines=True makes netstat command fail under windows
        # timeout may not work on linux
        # decoder may be unicode_escape for dos commands or utf-8 for powershell
        output = subprocess.check_output(command, stderr=subprocess.STDOUT, shell=shell,
                                         timeout=timeout, universal_newlines=False)
        output = output.decode(decoder, errors='ignore')
    except subprocess.CalledProcessError as exc:
        exit_code = exc.returncode
        try:
            output = exc.output
            try:
                output = output.decode(decoder, errors='ignore')
            except Exception as subexc:
                logger.debug(subexc, exc_info=True)
                logger.debug('Cannot properly decode error. Text is %s' % output)
        except:
            output = "command_runner: Could not obtain output from command."
        if exit_code in valid_exit_codes:
            logger.debug('Command [%s] returned with exit code [%s]. Command output was:' % (command, exit_code))
            if output:
                logger.debug(output)
            return exc.returncode, output
        else:
            logger.error('Command [%s] failed with exit code [%s]. Command output was:' %
                         (command, exc.returncode))
            logger.error(output)
            return exc.returncode, output
    # OSError if not a valid executable
    except OSError as exc:
        logger.error('Command [%s] returned:\n%s.' % (command, exc))
        return None, exc
    except subprocess.TimeoutExpired:
        logger.error('Timeout [%s seconds] expired for command [%s] execution.' % (timeout, command))
        return None, 'Timeout of %s seconds expired.' % timeout
    else:
        logger.debug('Command [%s] returned with exit code [0]. Command output was:' % command)
        if output:
            logger.debug(output)
        return 0, output


class PowerShellRunner:
    def __init__(self, powershell_interpreter=None):
        self.powershell_interpreter = powershell_interpreter

        if powershell_interpreter is not None and os.path.isfile(powershell_interpreter):
            return
        else:
            # Try to guess powershell path if no valid path given
            interpreter_executable = 'powershell.exe'
            try:
                # Let's try native powershell (64 bit) first or else Import-Module may fail when running 32 bit powershell on 64 bit arch
                best_guess = os.environ[
                                 'SYSTEMROOT'] + '\\sysnative\\WindowsPowerShell\\v1.0\\' + interpreter_executable
                if os.path.isfile(best_guess):
                    self.powershell_interpreter = best_guess
                else:
                    best_guess = os.environ[
                                     'SYSTEMROOT'] + '\\System32\\WindowsPowerShell\\v1.0\\' + interpreter_executable
                    if os.path.isfile(best_guess):
                        self.powershell_interpreter = best_guess
            except KeyError:
                pass
            if self.powershell_interpreter is None:
                try:
                    ps_paths = os.path.dirname(os.environ['PSModulePath']).split(';')
                    for ps_path in ps_paths:
                        if ps_path.endswith('Modules'):
                            ps_path = ps_path.strip('Modules')
                        possible_ps_path = os.path.join(ps_path, interpreter_executable)
                        if os.path.isfile(possible_ps_path):
                            self.powershell_interpreter = possible_ps_path
                            break
                except KeyError:
                    pass

            if not self.powershell_interpreter is None:
                logger.debug('Found powershell interpreter in: %s' % self.powershell_interpreter)
            else:
                raise OSError('Could not find any valid powershell interpreter')

    def run_script(self, script, *args):
        if self.powershell_interpreter is None:
            logger.debug('I do not have a powershell interpreter ready. I cannot cast that here.')
            return False

        logger.debug('Running [%s]' % script)
        # Welcome in Powershell hell where -Command gives exit codes 0 or 1 and -File gives whatever your script did
        command = self.powershell_interpreter + ' -executionPolicy Bypass -NonInteractive -NoLogo -NoProfile -File ' \
                  + script + (' ' if len(args) > 0 else ' ') + ' '.join('"' + arg + '"' for arg in args)

        exit_code, output = command_runner(command, timeout=360, valid_exit_codes=[0, 66], decoder='unicode_escape')
        return exit_code, output


def create_manifest_from_dict(manifest_file, manifest_dict):
    """
    Creates a manifest file in the way sha256sum would do under linux

    :param manifest_file: Target file for manifest
    :param manifest_dict: Manifest dict like {sha256sum : filename}
    :return:
    """
    try:
        with open(manifest_file, 'w', encoding='utf-8') as fp:
            for key, value in manifest_dict.items():
                fp.write('%s  %s\n' % (key, value))
    except IOError:
        logger.error('Cannot write manifest file [%s].' % manifest_file)
        logger.debug('Trace:', exc_info=True)


def create_manifest_from_dir(manifest_file, path, remove_prefix=None):
    """
    Creates a bash like file manifest with sha256sum and filenames


    :param manifest_file: path of resulting manifest file
    :param path: path of directory to create manifest for
    :param remove_prefix: optional path prefix to remove from files in manifest
    :return:
    """
    if not os.path.isdir(path):
        raise NotADirectoryError('Path [%s] does not exist.' % path)

    files = FileUtils.get_files_recursive(path)
    with open(manifest_file, 'w', encoding='utf-8') as fp:
        for file in files:
            sha256 = FileUtils.sha256sum(file)
            if file.startswith(remove_prefix):
                file = file[len(remove_prefix):].lstrip(os.sep)
            fp.write('%s  %s\n' % (sha256, file))


def check_for_virtualization(product_id):
    """
    Tries to find hypervisors, needs various WMI results as argument, ie:
    product_id = [computersystem.Manufacturer, baseboard.Manufacturer, baseboard.Product,
              bios.Manufacturer, bios.SerialNumber, bios.Version]

    Basic detection
    Win32_BIOS.Manufacturer could contain 'XEN'
    Win32_BIOS.SMBIOSBIOSVersion could contain 'VBOX', 'bochs', 'qemu', 'VirtualBox', 'VMWare' or 'Hyper-V'

    ovirt adds oVirt to Win32_computersystem.Manufacturer (tested on Win7 oVirt 4.2.3 guest)
    HyperV may add 'Microsoft Corporation' to Win32_baseboard.Manufacturer
        and 'Virtual Machine' to Win32_baseboard.Product (tested on Win2012 R2 guest/host)
    HyperV may add 'VERSION/ VRTUAL' to Win32_BIOS.SMBIOSBIOSVersion (tested on Win2012 R2 guest/host)
        (yes, the error to 'VRTUAL' is real)
    VMWare adds 'VMWare to Win32_BIOS.SerialNumber (tested on Win2012 R2 guest/ VMWare ESXI 6.5 host)
    Xen adds 'Xen' to Win32_BIOS.Version (well hopefully)
    """

    for id in product_id:
        # First try to detect oVirt before detecting Qemu/KVM
        if re.search('oVirt', id, re.IGNORECASE):
            return True, 'oVirt'
        elif re.search('VBOX', id, re.IGNORECASE):
            return True, 'VirtualNox'
        elif re.search('VMWare', id, re.IGNORECASE):
            return True, 'VMWare'
        elif re.search('Hyper-V', id, re.IGNORECASE):
            return True, 'Hyper-V'
        elif re.search('Xen', id, re.IGNORECASE):
            return True, 'Xen'
        elif re.search('KVM', id, re.IGNORECASE):
            return True, 'KVM'
        elif re.search('qemu', id, re.IGNORECASE):
            return True, 'qemu'
        elif re.search('bochs', id, re.IGNORECASE):
            return True, 'bochs'
        # Fuzzy detection
        elif re.search('VRTUAL', id, re.IGNORECASE):
            return True, 'HYPER-V'
    return False, 'Physical / Unknown hypervisor'


# https: // stackoverflow.com / a / 12578715
@property
def is_windows_64bit(self):
    if 'PROCESSOR_ARCHITEW6432' in os.environ:
        return True
    return os.environ['PROCESSOR_ARCHITECTURE'].endswith('64')
