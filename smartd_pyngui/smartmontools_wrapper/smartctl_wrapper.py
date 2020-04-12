#! /usr/bin/env python
#  -*- coding: utf-8 -*-
#
# This file is part of smartd_pyngui module

"""
smartd_pyngui is an application to read S.M.A.R.T state of disks
and output, and handle most errors that may happen

Versionning semantics:
    Major version: backward compatibility breaking changes
    Minor version: New functionnality
    Patch version: Backwards compatible bug fixes

"""

__intname__ = 'smartd_pyngui.smartctl_wrapper'
__author__ = 'Orsiris de Jong'
__copyright__ = 'Copyright (C) 2014-2020 Orsiris de Jong'
__licence__ = 'BSD 3 Clause'
__version__ = '2.0.0'
__build__ = '2020040201'

import json
from logging import getLogger
from command_runner import command_runner

logger = getLogger()


def get_disks():
    # Assume that we will use smartctl in order to detect disk types instead of WMI
    # use smartctl --scan-open to list drives

    # Contains array of disks like [name, type] where type = ssd, spinning or nvme
    disk_list = []

    result, output = command_runner('"smartctl" --scan-open --json')
    if result != 0:
        return None
    else:
        disks = json.loads(output)
        for disk in disks['devices']:
            # Before adding disks to disk list, we need to check whether the SMART attributes can be read
            # This is specially usefull to filter raid member drives

            result, output = command_runner(f'"smartctl" --info --json {disk["name"]}',
                                            valid_exit_codes=[0, 1], timeout=60)
            if result != 0:
                # Don't add drives that can't be opened
                continue
            else:
                # disk['type'] is already correct for nvme disks

                disk_detail = json.loads(output)

                try:
                    # set dtype for nvme disks
                    if disk['type'] == 'nvme':
                        disk['disk_type'] = 'nvme'
                    # Determnie if disk is spinning
                    elif disk_detail['rotation_rate'] == 'Solid State Device':
                        disk['disk_type'] = 'ssd'
                    elif int(disk_detail['rotation_rate']) != 0:
                        disk['disk_type'] = 'spinning'
                    else:
                        disk['disk_type'] = 'unknown'
                except (TypeError, KeyError):
                    disk['disk_type'] = 'unknown'
                    logger.debug('Trace', exc_info=True)
            disk_list.append(disk)
        return disk_list


def get_smart_state(disk_index):
    """
    Bit 0:
    Command line did not parse.
    Bit 1:
    Device open failed, device did not return an IDENTIFY DEVICE structure,
    or device is in a low-power mode (see '-n' option above).
    Bit 2:
    Some SMART or other ATA command to the disk failed,
    or there was a checksum error in a SMART data structure (see '-b' option above).
    Bit 3:
    SMART status check returned "DISK FAILING".
    Bit 4:
    We found prefail Attributes <= threshold.
    Bit 5:
    SMART status check returned "DISK OK" but we found that some (usage or prefail)
    Attributes have been <= threshold at some time in the past.
    Bit 6:
    The device error log contains records of errors.
    Bit 7:
    The device self-test log contains records of errors. [ATA only]
    Failed self-tests outdated by a newer successful extended self-test are ignored.

    return: (bool): True if state is OK, False if state is BAD, None if undefined

    """

    exitcode, _ = command_runner('smartctl -q silent /dev/pd%s' % str(disk_index),
                                 encoding='unicode_escape')
    if exitcode is not None:
        if exitcode >> 0 & 1:
            smartstate = None  # Command line dit not parse
        elif exitcode >> 1 & 1:
            smartstate = None  # Device open failed
        elif exitcode >> 3 & 1:
            smartstate = False  # DISK FAILING
        elif exitcode >> 4 & 1:
            smartstate = False  # PREFAIL ATTRIBUTES FAILING
        elif exitcode >> 5 & 1:
            smartstate = False  # PREVIOUS PREFAIL ATTRIBUTES FAILING
        elif exitcode >> 6 & 1:
            smartstate = False  # DEVICE ERROR LOG CONTAINS RECORDS
        elif exitcode >> 7 & 1:
            smartstate = False  # DEVICE SELF-TEST LOG CONTAINS ERRORS
        else:
            smartstate = True
        return smartstate
    else:
        return None


def get_smart_info(disk_name):
    result, output = command_runner('"smartctl" --all {0}'.format(disk_name))
    if result != 0:
        return output
    else:
        return None


def get_smart_info_old(disk_list):
    general_output = ""

    for disk in disk_list:
        if disk['disk_type'] != 'unknown':
            result, output = command_runner(f'"smartctl --all {disk["name"]}',
                                            valid_exit_codes=[0, 4], timeout=60)
            if result != 0:
                general_output = f'{general_output}\n\nDisk {disk["name"]}\n{output}'
    return general_output


def _selftest():
    print(get_disks())


if __name__ == '__main__':
    _selftest()