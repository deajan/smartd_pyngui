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

__intname__ = 'ofunctions.file_utils'
__author__ = 'Orsiris de Jong'
__copyright__ = 'Copyright (C) 2017-2020 Orsiris de Jong'
__licence__ = 'BSD 3 Clause'
__version__ = '0.6.0'
__build__ = '2020040501'


import os
import shutil
from datetime import datetime
import json
import re
from fnmatch import fnmatch
from itertools import chain
from contextlib import contextmanager
from threading import Lock
from command_runner import command_runner

FILE_LOCK = None


@contextmanager
def _file_lock():
    # pylint: disable=global-statement
    global FILE_LOCK

    if FILE_LOCK is None:
        FILE_LOCK = Lock()
    FILE_LOCK.acquire()
    yield
    if FILE_LOCK is not None:
        FILE_LOCK.release()


def make_path(path):
    with _file_lock():
        # May be false even if dir exists but ACLs deny
        if not os.path.isdir(path):
            os.makedirs(path)


def remove_file(path):
    with _file_lock():
        # May be false even if dir exists but ACLs deny
        if os.path.isfile(path):
            os.remove(path)


def remove_dir(path):
    with _file_lock():
        # May be false even if dir exists but ACLs deny
        if os.path.isdir(path):
            shutil.rmtree(path)


def glob_path_match(path, pattern_list):
    """
    Checks if path is in a list of glob style wildcard paths
    :param path: path of file / directory
    :param pattern_list: list of wildcard patterns to check for
    :return: Boolean
    """
    return any(fnmatch(path, pattern) for pattern in pattern_list)


def get_files_recursive(root, d_exclude_list=None, f_exclude_list=None,
                        ext_exclude_list=None, ext_include_list=None,
                        depth=0, primary_root=None, fn_on_perm_error=None,
                        include_dirs=False):
    """
    Walk a path to recursively find files
    Modified version of https://stackoverflow.com/a/24771959/2635443 that includes exclusion lists
    and accepts glob style wildcards on files and directories
    :param root: (str) path to explore
    :param include_dirs: (bool) should output list include directories
    :param d_exclude_list: (list) list of root relative directories paths to exclude
    :param f_exclude_list: (list) list of filenames without paths to exclude
    :param ext_exclude_list: list() list of file extensions to exclude, ex: ['.log', '.bak'],
           takes precedence over ext_include_list
    :param ext_include_lsit: (list) only include list of file extensions, ex: ['.py']
    :param depth: (int) depth of recursion to acheieve, 0 means unlimited, 1 is just the current dir...
    :param primary_root: (str) Only used for internal recursive exclusion lookup, don't pass an argument here
    :param fn_on_perm_error: (function) Optional function to pass, which argument will be the file / directory that has permission errors
    :return: list of files found in path
    """

    # Make sure we don't get paths with antislashes on Windows
    if os.path.isdir(root):
        root = os.path.normpath(root)
    else:
        return root

    # Check if we are allowed to read directory, if not, try to fix permissions if fn_on_perm_error is passed
    try:
        os.listdir(root)
    except PermissionError:
        if fn_on_perm_error is not None:
            fn_on_perm_error(root)

    # Make sure we clean d_exclude_list only on first function call
    if primary_root is None:
        if d_exclude_list is not None:
            # Make sure we use a valid os separator for exclusion lists
            d_exclude_list = [os.path.normpath(d) for d in d_exclude_list]
        else:
            d_exclude_list = []
    if f_exclude_list is None:
        f_exclude_list = []
    if ext_exclude_list is None:
        ext_exclude_list = []

    def _find_files():
        try:
            if include_dirs:
                yield root
            for f in os.listdir(root):
                file_ext = os.path.splitext(f)[1]
                if os.path.isfile(os.path.join(root, f)) and not glob_path_match(f, f_exclude_list) \
                    and file_ext not in ext_exclude_list \
                    and (file_ext in ext_include_list if ext_include_list is not None else True):
                    yield os.path.join(root, f)

        except PermissionError:
            pass

    def _find_files_in_dirs(depth):
        if depth == 0 or depth > 1:
            depth = depth - 1 if depth > 1 else 0
            try:
                for d in os.listdir(root):
                    d_full_path = os.path.join(root, d)
                    if os.path.isdir(d_full_path):
                        # p_root is the relative root the function has been called with recursively
                        # Let's check if p_root + d is in d_exclude_list
                        p_root = os.path.join(primary_root, d) if primary_root is not None else d
                        if not glob_path_match(p_root, d_exclude_list):
                            files_in_d = get_files_recursive(d_full_path,
                                                             d_exclude_list=d_exclude_list,
                                                             f_exclude_list=f_exclude_list,
                                                             ext_exclude_list=ext_exclude_list,
                                                             ext_include_list=ext_include_list,
                                                             depth=depth, primary_root=p_root,
                                                             fn_on_perm_error=fn_on_perm_error,
                                                             include_dirs=include_dirs)
                            if include_dirs:
                                yield d
                            if files_in_d:
                                for f in files_in_d:
                                    yield f

            except PermissionError:
                pass

    # Chain both generators
    return chain(_find_files(), _find_files_in_dirs(depth))



def replace_in_file(source_file, text_to_search, replacement_text, dest_file=None, backup_ext=None):
    """

    :param source_file: source file to replace text in
    :param text_to_search: text to search
    :param replacement_text: text to replace the text to search with
    :param dest_file: optional destination file if inplace replace is not wanted
    :param backup_ext: optional backup extension if no dest_file is given (inplace)
    :return:
    """
    with open(source_file, 'r') as fp:
        data = fp.read()

    if dest_file is not None:
        file = dest_file
    elif backup_ext is not None:
        file = source_file
        backup_file = source_file + backup_ext
        with open(backup_file, 'w') as fp:
            fp.write(data)
    else:
        file = source_file

    data = data.replace(text_to_search, replacement_text)

    with open(file, 'w') as fp:
        fp.write(data)


def file_creation_date(path_to_file):
    """
    Modified version of:
    Source: https://stackoverflow.com/a/39501288/2635443
    Try to get the date that a file was created, falling back to when it was
    last modified if that isn't possible.
    See http://stackoverflow.com/a/39501288/1709587 for explanation.
    """
    try:
        return os.path.getctime(path_to_file)
    # Some linxes may not have os.path.getctime ?
    except AttributeError:
        stat = os.stat(path_to_file)
        try:
            return stat.st_ctime
        except AttributeError:
            # We're probably on Linux. No easy way to get creation dates here,
            # so we'll settle for when its content was last modified.
            return stat.st_mtime


def is_file_older_than(days, file):
    if not os.path.isfile(file):
        raise FileNotFoundError('[%s] not found.' % file)

    return bool((datetime.today().timestamp() - (days * 86400) - file_creation_date(file)) > 0)


def remove_files_older_than(days, directory):
    """
    Is not recursive
    :param days:
    :param directory:
    :return:
    """
    if not os.path.isdir(directory):
        raise FileNotFoundError('[%s] not found.' % directory)

    for _, _, filenames in os.walk(directory):
        for filename in filenames:
            filename = os.path.join(directory, filename)
            try:
                if is_file_older_than(days, filename):
                    os.remove(filename)
            except FileNotFoundError:
                pass
            except (IOError, OSError):
                raise OSError('Cannot remove file [%s].' % filename)


def remove_bom(file):
    """Remove BOM from existing UTF-8 file"""
    if os.path.isfile(file):
        try:
            with open(file, 'rb') as fp_in:
                data = fp_in.read(3)
                with open(file + '.tmp', 'wb') as fp_out:
                    if data == b'\xef\xbb\xbf':
                        data = fp_in.read(32768)
                    while len(data) > 0:
                        fp_out.write(data)
                        data = fp_in.read(32768)
        except Exception:
            raise OSError
        if os.path.isfile(file + '.tmp'):
            os.replace(file + '.tmp', file)
    else:
        raise FileNotFoundError('[%s] not found.' % file)



def write_json_to_file(file, data):
    """
    Creates a manifest to the file containing it's sha256sum and the installation result

    :param file: File to write to
    :param data: Dict to write
    :return:
    """

    with open(file, 'w', encoding='utf-8') as fp:
        json.dump(data, fp, ensure_ascii=False)


def read_json_from_file(file):
    """
    Verifies exit code of the file manifest and returns True if installed successfully
    :param file: (str) path to file
    :return:
    """

    if os.path.isfile(file):
        with open(file, 'r', encoding='utf-8') as fp:
            file_content = json.load(fp)
            return file_content
    else:
        return None


def get_lzma_dict_size(directory):
    # Returns lzma dict (in MB) size based on approx of files size

    # Get dist size (bytes to MB by shr 20)
    # Lets assume that dict should be 2 <= dist_size <= 128 MB
    total_dist_size = 0
    for file in get_files_recursive(directory):
        if not os.path.islink(file):
            total_dist_size += os.path.getsize(file) >> 20

    # Compute best dict size for compression
    factor = 2
    while (total_dist_size / factor > 1) and factor < 128:
        factor *= 2
    return "%i" % factor


def grep(file, pattern):
    if os.path.isfile(file):
        result = []
        with open(file, 'r') as fp:
            for line in fp:
                if re.search(pattern, line):
                    result.append(line)
        return result

    raise FileNotFoundError(file)


def hide_windows_file(file, hidden=True):
    if os.name == 'nt':
        if hidden:
            symbol = '+'
        else:
            symbol = '-'
        result, _ = command_runner('attrib %sh "%s"' % (symbol, file))
        if result != 0:
            raise IOError(file)


def _selftest():
    print('Example code for %s, %s, %s' % (__intname__, __version__, __build__))

    match = glob_path_match(os.path.dirname(__file__), ['*ofunc*'])
    assert match == True, 'glob_path_match test failed'

    def print_perm_error(f):
        print('Perm error on: %s' % f)

    files = get_files_recursive(os.path.dirname(__file__), fn_on_perm_error=print_perm_error)

    print('Current files in folder: %s' % files)
    assert isinstance(files, chain)
    for file in files:
        print(file)
    files = get_files_recursive(os.path.dirname(__file__))
    assert '__init__.py' in [os.path.basename(f) for f in files], 'get_files_recursive test failed'

    # Include directories in output
    files = get_files_recursive(os.path.dirname(__file__), include_dirs=True)
    assert 'ofunctions' in [os.path.basename(f) for f in files], 'get_files_recursive with dirs test failed'

    # Try d_exclude_list
    files = get_files_recursive(os.path.dirname(__file__), d_exclude_list=['__pycache__'], include_dirs=True)
    assert '__pycache__' not in [os.path.basename(f) for f in files], 'get_files_recursive with d_exclude_list failed'

    # Try f_exclude_list
    files = get_files_recursive(os.path.dirname(__file__), f_exclude_list=['file_utils.py'])
    assert 'file_utils.py' not in [os.path.basename(f) for f in files], 'get_files_recursive with f_exclude_list failed'

    # Try ext_exclude_list
    files = get_files_recursive(os.path.dirname(__file__), ext_exclude_list=['.py'])
    for f in files:
        if f.endswith('.py'):
            assert False, 'get_files_recursive failed with ext_exclude_list'

    # Try ext_include_list
    files = get_files_recursive(os.path.dirname(__file__), ext_include_list=['.py'])
    for f in files:
        if not f.endswith('.py'):
            assert False, 'get_files_recursive failed with ext_include_list'


if __name__ == '__main__':
    _selftest()
