#! /usr/bin/env python
#  -*- coding: utf-8 -*-

import os
import shutil
import time
import hashlib
import json
from fnmatch import fnmatch
from contextlib import contextmanager
from threading import Lock

BUILD = '2019052101'

file_lock_token = None


@contextmanager
def _file_lock():
    # pylint: disable=global-statement
    global file_lock_token

    if file_lock_token is None:
        file_lock_token = Lock()
    file_lock_token.acquire()
    yield
    if file_lock_token is not None:
        file_lock_token.release()


def make_path(path):

    with _file_lock():
        if not os.path.isdir(path):
            os.makedirs(path)


def remove_file(path):
    with _file_lock():
        if os.path.isfile(path):
            os.remove(path)


def remove_dir(path):
    with _file_lock():
        if os.path.isdir(path):
            shutil.rmtree(path)


def glob_path_match(path, pattern_list):
    """
    Checks if path is in a list of glob style wildcard paths
    :param path: path of file / directory
    :param pattern_list: list of wildcard patterns to check for
    :return: Boolean
    """
    return any(fnmatch(os.path.basename(path), pattern) for pattern in pattern_list)


def get_files_recursive(root, d_exclude_list=None, f_exclude_list=None, ext_exclude_list=None, primary_root=None):
    """
    Walk a path to recursively find files
    Modified version of https://stackoverflow.com/a/24771959/2635443 that includes exclusion lists
    and accepts glob style wildcards on files and directories
    :param root: path to explore
    :param d_exclude_list: list of root relative directories paths to exclude
    :param f_exclude_list: list of filenames without paths to exclude
    :param ext_exclude_list: list of file extensions to exclude, ex: ['.log', '.bak']
    :param primary_root: Only used for internal recursive exclusion lookup, don't pass an argument here
    :return: list of files found in path
    """

    if d_exclude_list is not None:
        # Make sure we use a valid os separator for exclusion lists, this is done recursively :(
        d_exclude_list = [os.path.normpath(d) for d in d_exclude_list]
    else:
        d_exclude_list = []
    if f_exclude_list is None:
        f_exclude_list = []
    if ext_exclude_list is None:
        ext_exclude_list = []

    files = [os.path.join(root, f) for f in os.listdir(root) if os.path.isfile(os.path.join(root, f))
             and not glob_path_match(f, f_exclude_list) and os.path.splitext(f)[1] not in ext_exclude_list]
    dirs = [d for d in os.listdir(root) if os.path.isdir(os.path.join(root, d))]
    for d in dirs:
        p_root = os.path.join(primary_root, d) if primary_root is not None else d
        if not glob_path_match(p_root, d_exclude_list):
            files_in_d = get_files_recursive(os.path.join(root, d), d_exclude_list, f_exclude_list, ext_exclude_list,
                                             primary_root=p_root)
            if files_in_d:
                for f in files_in_d:
                    files.append(os.path.join(root, f))
    return files


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
    # Source: https://stackoverflow.com/a/39501288/2635443
    Try to get the date that a file was created, falling back to when it was
    last modified if that isn't possible.
    See http://stackoverflow.com/a/39501288/1709587 for explanation.

    """
    if os.name == 'nt':
        return os.path.getctime(path_to_file)
    else:
        stat = os.stat(path_to_file)
        try:
            return stat.st_birthtime
        except AttributeError:
            # We're probably on Linux. No easy way to get creation dates here,
            # so we'll settle for when its content was last modified.
            return stat.st_mtime


def remove_files_older_than(days, directory):
    if not os.path.isdir(directory):
        raise FileNotFoundError('[%s] not found.' % directory)
    else:
        for root, _, filenames in os.walk(directory):
            for filename in filenames:
                if os.path.isfile(filename) and (
                        ((time.time() - (days * 86400)) - file_creation_date(filename)) < 0):
                    os.remove(filename)


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


def sha256sum(file):
    sha256 = hashlib.sha256()

    try:
        with open(file, 'rb') as fp:
            while True:
                data = fp.read(65536)
                if not data:
                    break
                sha256.update(data)
        return sha256.hexdigest()
    except IOError:
        raise IOError


def check_file_hash(file, hashsum):
    hashsum = hashsum.lower()
    if os.path.isfile(file):
        calculated_hashsum = sha256sum(file).lower()
        if hashsum == calculated_hashsum:
            return True
        else:
            raise ValueError('File [%s] has an invalid sha256sum [%s]. Reference sum is [%s].'
                             % (file, calculated_hashsum, hashsum))
    else:
        return False


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
    :param file:
    :return:
    """
    if os.path.isfile(file):
        with open(file, 'r', encoding='utf-8') as fp:
            file_content = json.load(fp)
            return file_content
    else:
        return None
