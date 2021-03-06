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

__intname__ = 'ofunctions.process'
__author__ = 'Orsiris de Jong'
__copyright__ = 'Copyright (C) 2014-2020 Orsiris de Jong'
__licence__ = 'BSD 3 Clause'
__version__ = '0.1.1'
__build__ = '2020102801'


import psutil
from typing import NoReturn


def kill_childs(pid: int, itself: bool = False) -> NoReturn:
    """
    Kills all childs of pid (current pid can be obtained with os.getpid()
    Good idea when using multiprocessing, is to call with atexit.register(ofunctions.kill_childs, os.getpid(),)

    :param pid: Which pid tree we'll kill
    :param itself: Should parent be killed too ?
    :return:
    """
    parent = psutil.Process(pid)

    for child in parent.children(recursive=True):
        child.kill()
    if itself:
        parent.kill()