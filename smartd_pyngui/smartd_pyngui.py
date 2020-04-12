#!/usr/bin/env python
# -*- coding: utf-8 -*-

# TEMPERATURE DOES NOT WORK #TODO

# IMPORTS ################################################################################################

import os
import sys
import platform  # Detect OS
import re  # Regex handling
from time import sleep
import json
from datetime import datetime
import zlib
from command_runner.elevate import elevate
from command_runner import command_runner
import ofunctions.Mailer
from configparser_crypt.fernet_backend import ConfigParserCrypt
from smartmontools_wrapper import smartctl_wrapper

import PySimpleGUI.PySimpleGUI as sg
from icon import ICON_FILE, TOOLTIP_IMAGE

from PRIVATE.aes_key import AES_ENCRYPTION_KEY


# Module pywin32
if os.name == 'nt':
    import win32serviceutil

# On Windows nuitka distribs, set the tkinter library path below the distribution
if sys.argv[0].endswith(".exe") or sys.argv[0].endswith(".EXE"):
    os.environ['TCL_LIBRARY'] = os.path.abspath(os.path.dirname(sys.argv[0])) + os.sep + 'tcl'
    os.environ['TK_LIBRARY'] = os.path.abspath(os.path.dirname(sys.argv[0])) + os.sep + 'tk'

# BASIC FUNCTIONS & DEFINITIONS #########################################################################

APP_NAME = 'smartd_pyngui'  # Stands for smart daemon python native gui
APP_VERSION = '1.0-dev'
APP_BUILD = '2020041201'
APP_DESCRIPTION = 'smartd v5.4+ configuration interface'
CONTACT = 'ozy@netpower.fr - http://www.netpower.fr'
APP_URL = 'https://www.netpower.fr/smartmontools-win'
COPYING = 'Written in 2012-2020'
AUTHOR = 'Orsiris de Jong'

LOG_FILE = APP_NAME + '.log'

SMARTD_SERVICE_NAME = 'smartd'
SMARTD_CONF_FILENAME = 'smartd.conf'
ALERT_CONF_FILENAME = APP_NAME + '_alerts.conf'

DEFAULT_UNIX_PATH = '/etc/smartd'

IS_STABLE = False


# DEV NOTES ###############################################################################################

# TODO: get smartd version in order to enable / disable various features
# TODO: improve smartd.conf syntax

# -d TYPE = auto,ata,scsi,sat[,auto][,N],...
# sat,auto is new... since version ?
# maybe leave TYPE as free entry ?


# powermode ,q support missing

# -T TYPE = normal, permissive  - Maybe not used, old disks only
# -o VALUE = on, off            - Maybe not used, not part of the ATA sepcs

# -S VALUE = on, off  ???

# improve -l support

# -e NAME,VALUE is new since version ?

# LOGGING & DEBUG CODE ####################################################################################

_DEBUG = os.environ.get('_DEBUG', False)
if IS_STABLE is False:
    _DEBUG = True

logger = ofunctions.logger_get_logger(LOG_FILE, debug=_DEBUG)


# ACTUAL APPLICATION ######################################################################################


class Configuration:
    """
    This class can read / write smartd.conf files

    Standard smartd.conf files are read into 'default' section
    If the file has been written by this class, it will have

    - A header: '# smartd_pyngui 1.0 conf file'
    - a Disk type list: '# __spinning /dev/sda /dev/sdb\n# __nvme /dev/sdc\n __ssd /dev/sdd
    - Various sections of configuration settings per disk type (eg /dev/sdX [config])
    - If no disk type list exists, than the __spinning type will be used

    """
    smart_conf_file = ""

    def __init__(self, file_path=None):
        # TODO investigate file_path usage here (which refers to both smartd and alert conf files)
        """Determine smartd configuration file path"""

        # __file__ variable doesn't exist in frozen py2exe mode, get app_root
        try:
            self.app_executable = os.path.abspath(__file__)
            self.app_root = os.path.dirname(self.app_executable)
        except OSError:
            self.app_executable = os.path.abspath(sys.argv[0])
            self.app_root = os.path.dirname(self.app_executable)

        ##*# Multi drive type config enabled ##*#
        self.multi_drive_config_explanation = '# Since smartd cannot set different settings per drive type, ' \
                                              'we analyzed the drives on your computer and assigned settings ' \
                                              'corresponding to the drive types. When drives change, a re-run ' \
                                              'of the tool is required.'
        self.smart_conf_file = None
        self.alert_conf_file = None

        # Use __spinning drive settings for all drive types
        self.global_drive_settings = False

        # Drive types
        # Default gets populated when no other configs exist
        self.drive_types = ['__spinning', '__ssd', '__nvme', '__removable']

        # Contains smartd drive configurations
        self.config_list = {}
        # Contains lists of drives per drive_types
        self.drive_list = {}
        for drive_type in self.drive_types:
            self.config_list[drive_type] = []
            self.drive_list[drive_type] = []

        # Contains smartd global alert configuration
        self.config_list_alerts = []

        # Contains smartd_pyngui alert settings
        self.int_alert_config = ConfigParserCrypt()
        self.int_alert_config.set_key(ofunctions.revac(AES_ENCRYPTION_KEY))

        self.set_smartd_defaults()
        self.set_alert_defaults()

        if file_path is not None:
            self.smart_conf_file = file_path
            if not os.path.isfile(self.smart_conf_file):
                logger.info("Using new file [" + self.smart_conf_file + "].")
        else:
            if platform.system() == "Windows":
                # Get program files environment
                try:
                    program_files_x86 = os.environ["ProgramFiles(x86)"]
                except KeyError:
                    program_files_x86 = os.environ["ProgramFiles"]

                try:
                    program_files_x64 = os.environ["ProgramW6432"]
                except KeyError:
                    program_files_x64 = os.environ["ProgramFiles"]

                smart_conf_file_possible_paths = [
                    os.path.join(self.app_root, SMARTD_CONF_FILENAME),
                    os.path.join(program_files_x64, 'smartmontools for Windows', 'bin', SMARTD_CONF_FILENAME),
                    os.path.join(program_files_x86, 'smartmontools for Windows', 'bin', SMARTD_CONF_FILENAME),
                    os.path.join(program_files_x64, 'smartmontools', 'bin', SMARTD_CONF_FILENAME),
                    os.path.join(program_files_x86, 'smartmontools', 'bin', SMARTD_CONF_FILENAME)
                ]

                alert_conf_file_possible_paths = [
                    os.path.join(self.app_root, ALERT_CONF_FILENAME),
                    os.path.join(program_files_x64, 'smartmontools for Windows', 'bin', ALERT_CONF_FILENAME),
                    os.path.join(program_files_x86, 'smartmontools for Windows', 'bin', ALERT_CONF_FILENAME),
                    os.path.join(program_files_x64, 'smartmontools', 'bin', ALERT_CONF_FILENAME),
                    os.path.join(program_files_x86, 'smartmontools', 'bin', ALERT_CONF_FILENAME)
                ]

                for possible_smartd_path in smart_conf_file_possible_paths:
                    if os.path.isfile(possible_smartd_path):
                        self.smart_conf_file = possible_smartd_path
                        break

                for possible_alert_path in alert_conf_file_possible_paths:
                    if os.path.isfile(possible_alert_path):
                        self.alert_conf_file = possible_alert_path
                        break

            else:
                smart_conf_file_possible_paths = [
                    os.path.join(self.app_root, SMARTD_CONF_FILENAME),
                    os.path.join('/etc/smartmontools', SMARTD_CONF_FILENAME),
                    os.path.join('/etc/smartd', SMARTD_CONF_FILENAME),
                    os.path.join('/etc', SMARTD_CONF_FILENAME),
                    os.path.join('etc/smartmontools', SMARTD_CONF_FILENAME),
                    os.path.join('etc/smartd', SMARTD_CONF_FILENAME),
                    os.path.join('/etc', SMARTD_CONF_FILENAME)
                ]

                alert_conf_file_possible_paths = [
                    os.path.join(self.app_root, ALERT_CONF_FILENAME),
                    os.path.join('/etc/smartmontools', ALERT_CONF_FILENAME),
                    os.path.join('/etc/smartd', ALERT_CONF_FILENAME),
                    os.path.join('/etc', ALERT_CONF_FILENAME),
                    os.path.join('etc/smartmontools', ALERT_CONF_FILENAME),
                    os.path.join('etc/smartd', ALERT_CONF_FILENAME),
                    os.path.join('/etc', ALERT_CONF_FILENAME)
                ]

                for possible_smartd_path in smart_conf_file_possible_paths:
                    if os.path.isfile(possible_smartd_path):
                        self.smart_conf_file = possible_smartd_path
                        break

                for possible_alert_path in alert_conf_file_possible_paths:
                    if os.path.isfile(possible_alert_path):
                        self.alert_conf_file = possible_alert_path
                        break

        if self.smart_conf_file is None:
            self.smart_conf_file = os.path.join(self.app_root, SMARTD_CONF_FILENAME)
        else:
            logger.debug('Found configuration file in [%s].' % self.smart_conf_file)

        if self.alert_conf_file is None:
            self.alert_conf_file = os.path.join(self.app_root, ALERT_CONF_FILENAME)
        else:
            logger.debug('Found alert config file in [%s].' % self.alert_conf_file)

    def set_smartd_defaults(self):
        self.drive_list['__spinning'] = ['DEVICESCAN']
        self.drive_list['__ssd'] = []
        self.drive_list['__nvme'] = []
        self.drive_list['__removable'] = []

        self.config_list['__spinning'] = ['-H', '-C 197+', '-l error', '-U 198+', '-l selftest', '-t', '-f', '-I 194',
                                          '-W 20,55,60', '-n sleep,7,q',
                                          '-s (L/../../4/13|S/../../0,1,2,3,4,5,6/10)']
        self.config_list['__ssd'] = ['-H', '-C 197+', '-l error', '-U 198+', '-l selftest', '-t', '-f', '-I 194',
                                     '-W 40,65,75', '-n sleep,7,q',
                                     '-s (L/../../4/13|S/../../0,1,2,3,4,5,6/10)']
        self.config_list['__nvme'] = ['-H', '-C 197+', '-l error', '-U 198+', '-l selftest', '-t', '-f', '-I 194',
                                      '-W 40,80,85', '-n sleep,7,q',
                                      '-s (L/../../4/13|S/../../0,1,2,3,4,5,6/10)']
        self.config_list['__removable'] = ['-H', '-C 197+', '-l error', '-U 198+', '-l selftest', '-t', '-f', '-I 194',
                                           '-W 20,55,60', '-n sleep,7,q',
                                           '-s (L/../../4/13|S/../../0,1,2,3,4,5,6/10)']

        # Default behavior is to for smartmontools to launch this app with --alert
        self.config_list_alerts = ['-m <nomailer>', '-M exec "%s --alert"' % self.app_executable]

    def set_alert_defaults(self):
        self.int_alert_config.add_section('ALERT')
        self.int_alert_config['ALERT']['WARNING_MESSAGE'] = 'Warning message goes here '  # TODO
        self.int_alert_config['ALERT']['MAIL_ALERT'] = 'yes'
        self.int_alert_config['ALERT']['SOURCE_MAIL'] = ''
        self.int_alert_config['ALERT']['DESTINATION_MAILS'] = ''
        self.int_alert_config['ALERT']['SMTP_SERVER'] = ''
        self.int_alert_config['ALERT']['SMTP_PORT'] = '25'
        self.int_alert_config['ALERT']['SMTP_USER'] = ''
        self.int_alert_config['ALERT']['SMTP_PASSWORD'] = ''
        self.int_alert_config['ALERT']['SECURITY'] = 'none'
        self.int_alert_config['ALERT']['COMPRESS_LOGS'] = 'yes'
        self.int_alert_config['ALERT']['LOCAL_ALERT'] = 'no'

    # TODO use 4 different config lists
    def read_smartd_conf_file(self, conf_file=None):
        current_drive_type = '__spinning'
        # Contains smartd drive configurations
        config_list = {}
        # Contains lists of drives per drive_types
        drive_list = {}
        for drive_type in self.drive_types:
            config_list[drive_type] = []
            drive_list[drive_type] = []
        if conf_file is None:
            conf_file = self.smart_conf_file
        try:
            with open(conf_file, 'r') as conf:
                for line in conf:
                    if line[0] != "\n" and line[0] != "\r" and line[0] != " ":
                        if line.startswith('##*# Multi drive type config enabled ##*#'):
                            self.global_drive_settings = True
                        elif line.startswith('##*# __spinning drives type ##*#'):
                            current_drive_type = '__spinning'
                        elif line.startswith('##*# __nvme drives type ##*#'):
                            current_drive_type = '__nvme'
                        elif line.startswith('##*# __ssd drives type ##*#'):
                            current_drive_type = '__ssd'
                        elif line.startswith('##*# __removable drives type ##*#'):
                            current_drive_type = '__removable'
                        elif not line[0] == "#":
                            try:
                                cfg = line.split(' -')
                                cfg = [cfg[0]] + ['-' + item for item in cfg[1:]]
                                #  Remove unnecessary blanks and newlines
                                for i, _ in enumerate(cfg):
                                    cfg[i] = cfg[i].strip()
                                drive_list[current_drive_type].append(cfg[0])
                                del cfg[0]
                                config_list[current_drive_type] = cfg
                            except Exception:
                                msg = "Cannot read in config file [%s]." % conf_file
                                logger.error(msg)
                                logger.debug('Trace:', exc_info=True)
                                raise ValueError(msg)
                self.smart_conf_file = conf_file
            self.drive_list = drive_list
            self.config_list = config_list
            sg.Popup('Read configuration succeed')
        except IOError:
            msg = 'Cannot read from config file [%s].' % conf_file
            logger.error(msg)
            logger.debug('Trace:', exc_info=True)
            sg.Popup('Read configuration fialed: {0}.'.format(msg))

    def write_smartd_conf_file(self):
        try:
            with open(self.smart_conf_file, 'w') as conf:
                try:
                    conf.write(f'# This file was generated on {datetime.now():%d-%B-%Y %H:%m:%S} by '
                             f'{APP_NAME} {APP_VERSION} - {APP_URL}\n')
                    if self.global_drive_settings:
                        drive_types = self.drive_types
                        conf.write(f'##*# Multi drive type config enabled ##*#\n')
                        conf.write(self.multi_drive_config_explanation + '\n\n')
                    else:
                        drive_types = ['__spinning']
                    conf.write('\n\n')
                    for drive_type in drive_types:
                        conf.write(f'\n##*# {drive_type} drives type ##*#\n')
                        for drive in self.drive_list[drive_type]:
                            line = drive
                            for arg in self.config_list[drive_type]:
                                line += " " + arg
                            conf.write(line + "\n")
                except ValueError as exc:
                    msg = 'Cannot write data in config file [{0}]: {1}'.format(self.smart_conf_file, exc)
                    logger.error(msg)
                    logger.debug('Trace', exc_info=True)
                    raise ValueError(msg)
        except Exception as exc:
            msg = 'Cannot write to config file [{0}]: {1}'.format(self.smart_conf_file, exc)
            logger.error(msg)
            logger.debug('Trace', exc_info=True)
            raise ValueError(msg)

    def write_alert_config_file(self):
        if os.path.isdir(os.path.dirname(self.alert_conf_file)):
            with open(self.alert_conf_file, 'wb') as conf:
                self.int_alert_config.write_encrypted(conf)
        else:
            msg = f'Cannot write [{self.alert_conf_file}]. Directory maybe be missing.'
            logger.error(msg)
            raise ValueError(msg)

    def read_alert_config_file(self, conf_file=None):
        if conf_file is None:
            conf_file = self.alert_conf_file
        try:
            self.int_alert_config.read_encrypted(conf_file)
            self.alert_conf_file = conf_file
        except Exception:
            msg = f'Cannot read alert config file [{conf_file}].'
            logger.error(msg)
            raise ValueError(msg)


class MainGuiApp:
    def __init__(self, config):

        self.config = config

        # Colors
        self.color_green_enabled = '#CCFFCC'
        self.color_grey_disabled = '#CCCCCC'

        self.days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        self.hours = ["%.2d" % i for i in range(24)]
        self.temperature_celsius = ["%.2d" % i for i in range(99)]
        self.energy_modes = ['never', 'sleep', 'standby', 'idle']
        self.test_types = ['long', 'short']

        # Gui parameter mapping
        self.health_parameter_map = [('-H', 'Check SMART health'),
                                     ('-C 197', 'Report non zero current pending sectors'),
                                     ('-C 197+', 'Only report increases in current pending sectors'),
                                     ('-l error', 'Report ATA error increases'),
                                     ('-U 198', 'Report non zero offline uncorrectable sectors'),
                                     ('-U 198+', 'Only report increases in offline uncorrectable sectors'),
                                     ('-l selftest', 'Report increases in selftest errors'),
                                     ('-l offlinets', 'Report increases in offline test errors'),
                                     ('-t', 'Track prefailure / usage attributes changes'),
                                     ('-f', 'Report failures of usage attributes'),
                                     ('-r 5!', 'Report RAW value reallocated sectors (ATA)'),
                                     ('-R 5!', 'Report RAW value new reallocated sectors (ATA)')
                                     ]

        self.temperature_parameter_map = [('-I 194', 'Ignore temperature changes'),
                                          ('-W', 'Report temperature thresholds'),
                                          ]

        self.manual_drive_list_tooltip = \
            'Even under Windows, smartd addresses disks as \'/dev/sda /dev/sdb ... /dev/sdX\'\n' \
            'Intel & AMD raid drives are addresses as /dev/csmiX,Y where X is the controller number\n' \
            'and Y is the drive number. See smartd documentation for more.\n' \
            'Example working config:\n' \
            '\n' \
            '/dev/sda\n' \
            '/dev/sdb\n' \
            '/dev/csmi0,1'

        self.disk_types = \
            'Disk detection:\n\nDisk types are nvme, ssd or spinning.' \
            'Unknown disk types maybe raid members or smart unaware disks.\n\n'

        self.tooltip_image = TOOLTIP_IMAGE

        self.window = None
        self.alert_window = None

        self.main_gui()

    def main_gui(self):
        current_conf_file = None

        head_col = [[sg.Text(APP_DESCRIPTION)],
                    [sg.Frame('Configuration file', [[sg.InputText(self.config.smart_conf_file, key='smart_conf_file',
                                                                   enable_events=True, do_not_clear=True, size=(75, 1)),
                                                      self.spacer_tweakf(), sg.FileBrowse(target='smart_conf_file'),
                                                      self.spacer_tweakf(), sg.Button('Raw view', key='raw_view'),
                                                      self.spacer_tweakf(), sg.Button('Reload')
                                                      ],
                                                     [self.spacer_tweakf(720)],
                                                     ])],
                    ]

        # Email options
        alerts = [[sg.Radio('Use %s internal alert system' % APP_NAME, group_id='alerts', key='use_internal_alert',
                            default=True, enable_events=True), self.spacer_tweakf(), sg.Button('Configure')],
                  [sg.Radio('Use system mail command to send alerts to the following addresses'
                            ' (comma separated list) on Unixes',
                            group_id='alerts', key='use_system_mailer', default=False, enable_events=True)],
                  [sg.InputText(key='mail_addresses', size=(98, 1), do_not_clear=True)],
                  [sg.Radio('Use the following external alert handling script', group_id='alerts',
                            key='use_external_script', default=False, enable_events=True)],
                  [sg.InputText(key='external_script_path', size=(90, 1), do_not_clear=True), self.spacer_tweakf(),
                   sg.FileBrowse(target='external_script_path')],
                  ]
        alert_options = [[sg.Frame('Alert actions', [[sg.Column(alerts)],
                                                     [self.spacer_tweakf(720)],
                                                     ])]]

        # Tab content
        tab_layout = {}
        for drive_type in self.config.drive_types:
            if drive_type == '__spinning':
                drive_selection = [[sg.Radio('All found', group_id='drive_detection' + drive_type,
                                             key='drive_auto' + drive_type, enable_events=True)],
                                   [sg.Radio('Manual drive list', group_id='drive_detection' + drive_type,
                                             key='drive_manual' + drive_type,
                                             enable_events=True, tooltip=self.manual_drive_list_tooltip),
                                    sg.Image(data=self.tooltip_image, key='manual_drive_list_tooltip' + drive_type,
                                             enable_events=True)]
                                   ]
            else:
                drive_selection = [[sg.Text('Please enter drive list or launch drive detection')]]
            drive_list_widget = [[sg.Multiline(size=(60, 6), key='drive_list_widget' + drive_type, do_not_clear=True,
                                               background_color=self.color_grey_disabled)]]
            drive_config = [[sg.Frame('Drive detection', [[sg.Column(drive_selection), sg.Column(drive_list_widget)],
                                                          [self.spacer_tweakf(702)],
                                                          ])]]

            # Long self-tests
            long_test_time = [
                [sg.T('Schedule a long test at '), sg.InputCombo(self.hours, key='long_test_hour' + drive_type),
                 sg.T('H every')]]
            long_test_days = []
            for i in range(0, 7):
                key = 'long_day_' + self.days[i] + drive_type
                long_test_days.append(sg.Checkbox(self.days[i], key=key))
            long_test_days = [long_test_days]
            long_tests = [[sg.Frame('Scheduled long self-tests', [[sg.Column(long_test_time)],
                                                                  [sg.Column(long_test_days)],
                                                                  [self.spacer_tweakf(343)],
                                                                  ])]]

            # Short self-tests
            short_test_time = [
                [sg.T('Schedule a short test at '), sg.InputCombo(self.hours, key='short_test_hour' + drive_type),
                 sg.T('H every')]]
            short_test_days = []
            for i in range(0, 7):
                key = 'short_day_' + self.days[i] + drive_type
                short_test_days.append(sg.Checkbox(self.days[i], key=key))
            short_test_days = [short_test_days]
            short_tests = [[sg.Frame('Scheduled short self-tests', [[sg.Column(short_test_time)],
                                                                    [sg.Column(short_test_days)],
                                                                    [self.spacer_tweakf(343)],
                                                                    ])]]

            # Attribute checks
            count = 1
            smart_health_col1 = []
            smart_health_col2 = []
            for key, description in self.health_parameter_map:
                if count <= 6:
                    smart_health_col1.append([sg.Checkbox(description + ' (' + key + ')', key=key + drive_type)])
                else:
                    smart_health_col2.append([sg.Checkbox(description + ' (' + key + ')', key=key + drive_type)])
                count += 1

            attributes_check = [
                [sg.Frame('Smart health Checks', [[sg.Column(smart_health_col1), sg.Column(smart_health_col2)],
                                                  [self.spacer_tweakf(702)],
                                                  ])]]

            # Temperature checks
            temperature_check = []
            for key, description in self.temperature_parameter_map:
                temperature_check.append([sg.Checkbox(description + ' (' + key + ')', key=key + drive_type)])
            temperature_options = [[sg.Frame('Temperature settings',
                                             [[sg.Column(temperature_check),
                                               sg.Column([[sg.T('Temperature difference since last report')],
                                                          [sg.T('Info log when temperature reached')],
                                                          [sg.T('Critical log when temperature reached')],
                                                          ]),
                                               sg.Column([[sg.InputCombo(self.temperature_celsius,
                                                                         key='temp_diff' + drive_type,
                                                                         default_value='20')],
                                                          [sg.InputCombo(self.temperature_celsius,
                                                                         key='temp_info' + drive_type,
                                                                         default_value='55')],
                                                          [sg.InputCombo(self.temperature_celsius,
                                                                         key='temp_crit' + drive_type,
                                                                         default_value='60')],
                                                          ]),

                                               ],
                                              [self.spacer_tweakf(702)],
                                              ],
                                             )]]

            # Energy saving
            energy_text = [[sg.T('Do not execute smart tests when disk energy mode is ')],
                           [sg.T('Force test execution after N skipped tests')],
                           ]
            energy_choices = [[sg.InputCombo(self.energy_modes, key='energy_mode' + drive_type)],
                              [sg.InputCombo(["%.1d" % i for i in range(8)], key='energy_skips' + drive_type)],
                              ]
            energy_options = [[sg.Frame('Energy saving', [[sg.Column(energy_text), sg.Column(energy_choices)],
                                                          [self.spacer_tweakf(702)],
                                                          ])]]

            # Supplementary options
            sup_options_col = [
                [sg.InputText(key='supplementary_options' + drive_type, size=(98, 1), do_not_clear=True)]]

            sup_options = [[sg.Frame('Supplementary smartd options', [[sg.Column(sup_options_col)],
                                                                      [self.spacer_tweakf(702)],
                                                                      ])]]

            tab_layout[drive_type] = [
                [sg.Column(drive_config)],
                [sg.Column(long_tests), sg.Column(short_tests)],
                [sg.Column(attributes_check)],
                [sg.Column(temperature_options)],
                [sg.Column(energy_options)],
                [sg.Column(sup_options)],
            ]

        tabs = [
            [sg.Tab('Spinning disk drives', tab_layout['__spinning'], key='spinning_tab')],
            [sg.Tab('SSD drives', tab_layout['__ssd'], key='ssd_tab')],
            [sg.Tab('NVME drives', tab_layout['__nvme'], key='nvme_tab')],
            [sg.Tab('Removable drives', tab_layout['__removable'], key='removable_tab')],
        ]

        tabgroup = [[sg.Frame('Disk type options',
                              [
                                  [sg.Checkbox('Use spinning disk settings for all disk types', default=False,
                                               key='global_drive_settings',
                                               enable_events=True), self.spacer_tweakf(),
                                   sg.Button('Autodetect drives per type')],
                                  [sg.TabGroup(tabs, pad=0)]
                              ])]]

        full_layout = [
            [sg.Column(head_col)],
            [sg.Column(alert_options)],
            [sg.Column(tabgroup)],
        ]

        layout = [[sg.Column(full_layout, scrollable=True, vertical_scroll_only=True, size=(740, 550))],
                  [sg.T('')],
                  [self.spacer_tweakf(160), sg.Button('Show disk detection'), self.spacer_tweakf(),
                   sg.Button('Save changes'), self.spacer_tweakf(), sg.Button('Reload smartd service'),
                   self.spacer_tweakf(), sg.Button('Exit')]
                  ]

        # Display the Window and get values

        try:
            self.window = sg.Window(APP_NAME + ' - ' + APP_VERSION + ' ' + APP_BUILD, icon=ICON_FILE, resizable=True,
                                    size=(766, 600),
                                    text_justification='left').Layout(layout)
        except Exception as exc:
            logger.critical(exc)
            logger.debug('Trace', exc_info=True)
            sys.exit(1)

        # Finalize window before Update functions can work
        self.window.Finalize()

        self.update_main_gui_config()

        event, values = self.window.Read(timeout=1)
        # Store current config filename
        if current_conf_file is None:
            current_conf_file = values['smart_conf_file']

        while True:
            event, values = self.window.Read(timeout=1000)  # Please try and use a timeout when possible
            # Event (buttons and enable_event enabled controls) handling
            if event is None:
                action = sg.Popup('Do you want to save settings and reload service', custom_text=('Yes', 'No'))
                if action == 'Yes':
                    try:
                        if self.get_main_gui_config(values):
                            self.config.write_smartd_conf_file()
                            sg.Popup('Changes saved to configuration file')
                    except ValueError as msg:
                        sg.PopupError('Cannot save configuration. %s' % msg, icon=None)
                        logger.debug('Trace', exc_info=True)
                    finally:
                        self.service_reload()
                break
            if event == 'Exit':  # Todo ask service reload and save question
                action = sg.Popup('Are you sure ?', custom_text=('Cancel', 'Exit'), icon=None)
                if action == 'Cancel':
                    pass
                elif action == 'Exit':
                    break
            elif event == 'Show disk detection':
                sg.Popup('%s%s' % (self.disk_types, json.dumps(smartctl_wrapper.get_disks(), indent=4)))
            elif event == 'Reload smartd service':
                self.service_reload()
            elif event == 'Save changes':
                try:
                    if self.get_main_gui_config(values):
                        self.config.write_smartd_conf_file()
                        sg.Popup('Changes saved to configuration file')
                except ValueError as msg:
                    sg.PopupError('Cannot save configuration. %s' % msg, icon=None)
                    logger.debug('Trace', exc_info=True)
            elif event == 'drive_auto':
                self.window.Element('drive_list_widget').Update(disabled=True,
                                                                background_color=self.color_grey_disabled)
            elif event == 'drive_manual':
                self.window.Element('drive_list_widget').Update(disabled=False,
                                                                background_color=self.color_green_enabled)
            elif event in ['use_system_mailer', 'use_internal_alert', 'use_external_script']:
                self.alert_switcher(values)
            elif event == 'smart_conf_file':
                try:
                    self.config.read_smartd_conf_file(values['smart_conf_file'])
                    print(self.config.smart_conf_file)
                    self.update_main_gui_config()
                    current_conf_file = values['smart_conf_file']
                except ValueError as msg:
                    sg.PopupError(msg)
                    self.window.Element('smart_conf_file').Update(current_conf_file)
            elif event == 'Reload':
                self.config.read_smartd_conf_file()
                self.update_main_gui_config()
            elif 'manual_drive_list_tooltip' in event:
                sg.Popup(self.manual_drive_list_tooltip)
            elif event == 'Configure':
                self.configure_internal_alerts()
            elif event == 'raw_view':
                self.raw_smartd_view()
            elif event == 'global_drive_settings':
                if values['global_drive_settings']:
                    self.window.Element('ssd_tab').Update(disabled=True)
                    self.window.Element('nvme_tab').Update(disabled=True)
                    self.window.Element('removable_tab').Update(disabled=True)
                else:
                    self.window.Element('ssd_tab').Update(disabled=False)
                    self.window.Element('nvme_tab').Update(disabled=False)
                    self.window.Element('removable_tab').Update(disabled=False)
            elif event == 'Autodetect drives per type':
                drive_list = smartctl_wrapper.get_disks()
                # Empty earlier drives
                for drive_type in self.config.drive_types:
                    self.window.Element('drive_list_widget' + drive_type).Update('')
                for drive in drive_list:
                    if drive['disk_type'] == 'nvme':
                        self.window.Element('drive_list_widget__nvme').Update(
                            drive['name'] + '\n' + self.window.Element('drive_list_widget__nvme').Get())
                    elif drive['disk_type'] == 'ssd':
                        self.window.Element('drive_list_widget__ssd').Update(
                            drive['name'] + '\n' + self.window.Element('drive_list_widget__ssd').Get())
                    elif drive['disk_type'] == 'spinning':
                        self.window.Element('drive_list_widget__spinning').Update(
                            drive['name'] + '\n' + self.window.Element('drive_list_widget__spinning').Get())
                    elif drive['disk_type'] == 'removable':
                        self.window.Element('drive_list_widget__removable').Update(
                            drive['name'] + '\n' + self.window.Element('drive_list_widget__removable').Get())
        self.window.Close()

    def alert_switcher(self, values):
        if values['use_system_mailer'] is True:
            self.window.Element('use_system_mailer').Update(True)
            self.window.Element('mail_addresses').Update(disabled=False)
            self.window.Element('external_script_path').Update(disabled=True)
        if values['use_internal_alert'] is True:
            self.window.Element('use_internal_alert').Update(True)
            self.window.Element('mail_addresses').Update(disabled=True)
            self.window.Element('external_script_path').Update(disabled=True)
        if values['use_external_script'] is True:
            self.window.Element('use_external_script').Update(True)
            self.window.Element('mail_addresses').Update(disabled=True)
            self.window.Element('external_script_path').Update(disabled=False)

    @staticmethod
    def spacer_tweakf(pixels=10):
        return sg.T(' ' * pixels, font=('Helvetica', 1))

    def update_main_gui_config(self):
        if self.config.global_drive_settings is True:
            drive_types = self.config.drive_types
        else:
            drive_types = ['__spinning']
        for drive_type in drive_types:
            try:
                # Per drive_type drive_list and config_list
                drive_list = self.config.drive_list[drive_type]
                config_list = self.config.config_list[drive_type]
            except KeyError:
                logger.error('No drive list for %s' % drive_type)
                break

            try:
                if drive_type == '__spinning':
                    if drive_list == ['DEVICESCAN']:  # TODO devicescan must be disabled if multi disk types is used
                        self.window.Element('drive_auto' + drive_type).Update(True)
                    else:
                        self.window.Element('drive_manual' + drive_type).Update(True)
                drives = ''
                for drive in drive_list:
                    drives = drives + drive + '\n'
                self.window.Element('drive_list_widget' + drive_type).Update(drives)
            except KeyError:
                logger.error('No drive set yet')

            # Self test regex GUI setup
            if '-s' in '\t'.join(config_list):
                for i, item in enumerate(config_list):
                    if '-s' in item:
                        index = i

                        # TODO: Add other regex parameter here (group 1 & 2 missing)
                        long_test = re.search('L/(.+?)/(.+?)/(.+?)/([0-9]*)', config_list[index])
                        if long_test:
                            # print(long_test.group(1))
                            # print(long_test.group(2))
                            # print(long_test.group(3))
                            if long_test.group(3):
                                day_list = list(long_test.group(3))
                                # Handle special case where . means all
                                if day_list[0] == '.':
                                    for day in range(0, 7):
                                        self.window.Element('long_day_' + self.days[day] + drive_type).Update(True)
                                else:
                                    for day in day_list:
                                        if day.strip("[]").isdigit():
                                            self.window.Element(
                                                'long_day_' + self.days[int(day.strip("[]")) - 1] + drive_type).Update(
                                                True)
                            if long_test.group(4):
                                self.window.Element('long_test_hour' + drive_type).Update(long_test.group(4))

                        short_test = re.search('S/(.+?)/(.+?)/(.+?)/([0-9]*)', config_list[index])
                        if short_test:
                            # print(short_test.group(1))
                            # print(short_test.group(2))
                            if short_test.group(3):
                                day_list = list(short_test.group(3))
                                # Handle special case where . means all
                                if day_list[0] == '.':
                                    for day in range(0, 7):
                                        self.window.Element('short_day_' + self.days[day] + drive_type).Update(True)
                                else:
                                    for day in day_list:
                                        if day.strip("[]").isdigit():
                                            self.window.Element(
                                                'short_day_' + self.days[int(day.strip("[]")) - 1] + drive_type).Update(
                                                True)
                            if short_test.group(4):
                                self.window.Element('short_test_hour' + drive_type).Update(short_test.group(4))
                        config_list.pop(index)
                        break

            # Attribute checks GUI setup
            for key, _ in self.health_parameter_map:
                if key in config_list:
                    self.window.Element(key + drive_type).Update(True)
                    config_list.remove(key)
                    # Handle specific dependancy cases (-C 197+ depends on -C 197 and -U 198+ depends on -U 198)
                    if key == '-C 197+':
                        self.window.Element('-C 197' + drive_type).Update(True)
                    elif key == '-U 198+':
                        self.window.Element('-U 198' + drive_type).Update(True)

            # Handle temperature specific cases
            for index, item in enumerate(config_list):
                if item == '-I 194':
                    self.window.Element('-I 194' + drive_type).Update(True)
                    config_list.pop(index)
                    break

            for index, item in enumerate(config_list):
                if re.match(r'^-W [0-9]{1,2},[0-9]{1,2},[0-9]{1,2}$', item):
                    self.window.Element('-W' + drive_type).Update(True)
                    temperatures = item.split(' ')[1]
                    temperatures = temperatures.split(',')
                    self.window.Element('temp_diff' + drive_type).Update(temperatures[0])
                    self.window.Element('temp_info' + drive_type).Update(temperatures[1])
                    self.window.Element('temp_crit' + drive_type).Update(temperatures[2])
                    config_list.pop(index)
                    break
            # Energy saving GUI setup
            if '-n' in '\t'.join(config_list):
                for index, item in enumerate(config_list):
                    if '-n' in item:
                        energy_savings = config_list[index].split(',')
                        for mode in self.energy_modes:
                            if mode in energy_savings[0]:
                                self.window.Element('energy_mode' + drive_type).Update(mode)

                        if energy_savings[1].isdigit():
                            self.window.Element('energy_skips' + drive_type).Update(energy_savings[1])
                        # if energy_savings[1] == 'q':
                        # TODO: handle q parameter
                        config_list.pop(index)
                        break

            # We need to pop every other element from config_list before to keep only supplementary options
            self.window.Element('supplementary_options' + drive_type).Update(' '.join(config_list))

        # self.alert_switcher((['use_internal_alert'] = True))
        # Get alert options
        # -m <nomailer> -M exec PATH/smartd_pyngui = use internal alert
        # -m mail@addr.tld = use system mailer
        # -m <nomailer> -M exec PATH/script = use external_script

        # By default, let's assume we use the internal mailer
        alert_action = {'use_internal_alert': DEFAULT_UNIX_PATH, 'use_system_mailer': True, 'use_external_script': False}
        for index, value in enumerate(self.config.config_list_alerts):
            if '-M exec' in value:
                ext_script = self.config.config_list_alerts[index].replace('-M exec ', '', 1)
                if APP_NAME in ext_script:
                    alert_action = {'use_internal_alert': True, 'use_system_mailer': False, 'use_external_script': False}
                else:
                    alert_action = {'use_internal_alert': False, 'use_system_mailer': False, 'use_external_script': True}
                    self.window.Element('external_script_path').Update(ext_script)
            elif '-m' in value:
                mail_addresses = self.config.config_list_alerts[index].replace('-m ', '', 1)
                self.window.Element('mail_addresses').Update(mail_addresses)
                alert_action = {'use_internal_alert': DEFAULT_UNIX_PATH, 'use_system_mailer': True, 'use_external_script': False}
        self.alert_switcher(alert_action)

    def get_main_gui_config(self, values):
        if values['global_drive_settings'] is True:
            self.config.global_drive_settings = True
            drive_types = ['__spinning']
        else:
            drive_types = self.config.drive_types
        for drive_type in drive_types:
            # Per drive_type list
            drive_list = []
            config_list = []

            if drive_type == '__spinning':
                if values['drive_auto' + drive_type] is True:
                    drive_list.append('DEVICESCAN')
                else:
                    drive_list = values['drive_list_widget' + drive_type].split()
            else:
                drive_list = values['drive_list_widget' + drive_type].split()

                # TODO: better bogus pattern detection
                # TODO: needs to raise exception

                if "example" in drive_list or "exemple" in drive_list:
                    msg = "Drive list contains example  for type [{drive_type}] !!!"
                    logger.error(msg)
                    sg.PopupError(msg)
                    return False

                for drive in drive_list:
                    if not drive[0] == "/":
                        msg = f"Drive list doesn't start with slash but [{drive}]."
                        logger.error(msg)
                        sg.PopupError(msg)
                        return False

            # smartd health parameters
            try:
                for key, _ in self.health_parameter_map:
                    try:
                        if values[key + drive_type]:
                            # Handle dependancies
                            if key + drive_type == '-C 197+':
                                if '-C 197' in config_list:
                                    for (i, item) in enumerate(config_list):
                                        if item == '-C 197':
                                            config_list[i] = '-C 197+'
                                else:
                                    config_list.append(key)
                            elif key + drive_type == '-U 198+':
                                if '-U 198' in config_list:
                                    for (i, item) in enumerate(config_list):
                                        if item == '-U 198':
                                            config_list[i] = '-U 198+'
                                else:
                                    config_list.append(key)
                            else:
                                config_list.append(key)
                    except KeyError:
                        logger.debug(f'No key [{key}] found in health parameters.')

            except KeyError:
                msg = "Bogus configuration in health parameters."
                logger.error(msg)
                logger.debug('Trace:', exc_info=True)
                logger.debug(config_list)
                sg.PopupError(msg)
                return False

            try:
                for key, _ in self.temperature_parameter_map:
                    try:
                        if values[key + drive_type]:
                            if key + drive_type == '-W':
                                config_list.append(
                                    key + ' ' + str(values['temp_diff' + drive_type]) + ',' + str(
                                        values['temp_info' + drive_type]) + ',' + str(
                                        values['temp_crit' + drive_type]))
                            elif key + drive_type == '-I 194':
                                config_list.append(key)
                    except KeyError:
                        logger.debug(f'No key [{key}] found in temperature parameters.')
            except Exception:
                if key:
                    msg = "Bogus configuration in [%s] and temperatures." % key
                else:
                    msg = "Bogus configuration in temperatures. Cannot read keys."
                logger.error(msg)
                logger.debug('Trace:', exc_info=True)
                logger.debug(config_list)
                sg.PopupError(msg)
                return False

            try:
                energy_list = False
                energy_mode = values['energy_mode' + drive_type]
                if energy_mode in self.energy_modes:
                    energy_list = '-n ' + energy_mode
                skip_tests = values['energy_skips' + drive_type]
                if energy_list:
                    energy_list += ',' + str(skip_tests)
                    # TODO: handle -q parameter in GUI
                    energy_list += ',q'

                    config_list.append(energy_list)
            except Exception as exc:
                msg = 'Energy config error: {0}'.format(exc)
                logger.error(msg)
                logger.debug('Trace', exc_info=True)
                sg.PopupError(msg)
                return False

            # Transforms selftest checkboxes into long / short tests expression for smartd
            # Still not a good implementation after the Inno Setup ugly implementation
            try:
                long_regex = None
                short_regex = None
                tests_regex = None

                for test_type in self.test_types:
                    regex = "["
                    present = False

                    for day in self.days:
                        if values[test_type + '_day_' + day + drive_type] is True:
                            regex += str(self.days.index(day) + 1)
                            present = True
                    regex += "]"
                    # regex = regex.rstrip(',')

                    long_test_hour = values['long_test_hour' + drive_type]
                    short_test_hour = values['short_test_hour' + drive_type]

                    if test_type == self.test_types[0] and present is True:
                        long_regex = "L/../../" + regex + "/" + str(long_test_hour)
                    elif test_type == self.test_types[1] and present is True:
                        short_regex = "S/../../" + regex + "/" + str(short_test_hour)

                if long_regex is not None and short_regex is not None:
                    tests_regex = "-s (%s|%s)" % (long_regex, short_regex)
                elif long_regex is not None:
                    tests_regex = "-s %s" % long_regex
                elif short_regex is not None:
                    tests_regex = "-s %s" % short_regex

                if tests_regex is not None:
                    config_list.append(tests_regex)

            except Exception as exc:
                msg = 'Test regex creation error: {0}'.format(exc)
                logger.error(msg)
                logger.debug('Trace', exc_info=True)
                sg.PopupError(msg)
                return False

            if values['supplementary_options' + drive_type]:
                config_list.append(values['supplementary_options' + drive_type])

            logger.debug(drive_type)
            logger.debug(drive_list)
            logger.debug(config_list)
            self.config.drive_list[drive_type] = drive_list
            self.config.config_list[drive_type] = config_list

        drive_list_empty = True
        for drive_type in self.config.drive_types:
            if self.config.drive_list[drive_type] != []:
                drive_list_empty = False
        if drive_list_empty:
            msg = f"No drives defined in lists."
            logger.error(msg)
            sg.PopupError(msg)
            return False

        config_list_alerts = []

        # TODO: -M can't exist without -m
        # Mailer options
        if values['use_system_mailer'] is True:
            mail_addresses = values['mail_addresses']
            if len(mail_addresses) > 0:
                config_list_alerts.append('-m ' + mail_addresses)
            else:
                msg = 'Missing mail addresses'
                logger.error(msg)
                sg.PopupError(msg)
                raise AttributeError
        else:
            config_list_alerts.append('-m <nomailer>')
            if values['use_internal_alert'] is True:
                config_list_alerts.append('-M exec "%s"' % self.config.app_executable)
            if values['use_external_script'] is True:
                external_script_path = values['external_script_path']
                if len(external_script_path) > 0:
                    config_list_alerts.append('-M exec "%s"' % values['external_script_path'])
                else:
                    config_list_alerts.append('-M exec "%s"' % self.config.app_executable)
        self.config.config_list_alerts = config_list_alerts

        return True

    @staticmethod
    def service_reload():
        try:
            system_service_handler(SMARTD_SERVICE_NAME, "restart")
        except Exception as exc:
            msg = 'Cannot restart [" + SMARTD_SERVICE_NAME + "]. Running as admin ? {0}'.format(exc)
            logger.error(msg)
            logger.debug('Trace', exc_info=True)
            sg.PopupError(msg)
            return False
        else:
            sg.Popup('Successfully reloaded smartd service.', title='Info')

    def raw_smartd_view(self):
        if os.path.isfile(self.config.smart_conf_file):
            with open(self.config.smart_conf_file) as conf:
                smartd_text = conf.read()

            col = [[sg.Text(smartd_text, background_color='#FFFFFF')]]

            layout = [[sg.Column(col, scrollable=True, size=(722, 550), background_color='#FFFFFF')],
                      [sg.T(' ' * 70), sg.Button('Back')]
                      ]

            raw_view_window = sg.Window(APP_NAME + ' - ' + APP_VERSION + ' ' + APP_BUILD, icon=ICON_FILE,
                                        resizable=True,
                                        size=(500, 600),
                                        text_justification='left', layout=layout)

            while True:
                event, _ = raw_view_window.Read(timeout=1000)
                if event == 'Back' or event is None:
                    raw_view_window.Close()
                    break

    def configure_internal_alerts(self):
        current_conf_file = None

        head_col = [[sg.Text(APP_DESCRIPTION)],
                    [sg.Frame('Configuration file',
                              [[sg.InputText('', key='conf_file',
                                             enable_events=True, do_not_clear=True, size=(55, 1)),
                                self.spacer_tweakf(), sg.FileBrowse(target='conf_file')],
                               [self.spacer_tweakf(500)],
                               ])]
                    ]

        alert_message = [
            [sg.Frame('Alert message', [[sg.Multiline('', key='WARNING_MESSAGE', size=(62, 6), do_not_clear=True)]]
                      )]]

        email_alert_settings = [[sg.Frame('Email alert settings',
                                          [[sg.Checkbox('Send email alerts', key='MAIL_ALERT')],
                                           [sg.Column([
                                               [sg.Text('Source email address')],
                                               [sg.Text('Destination email addresses')],
                                               [sg.Text('SMTP Server')],
                                               [sg.Text('SMTP Port')],
                                               [sg.Checkbox('Use SMTP Authentication', key='useSmtpAuth')],
                                               [sg.Text('SMTP Username')],
                                               [sg.Text('STMP Password')],
                                               [sg.Text('Security')],
                                               [sg.Checkbox('Compress logs before sending', key='COMPRESS_LOGS')],
                                           ]),
                                               sg.Column([
                                                   [sg.Input(key='SOURCE_MAIL', size=(35, 1), do_not_clear=True)],
                                                   [sg.Input(key='DESTINATION_MAILS', size=(35, 1), do_not_clear=True)],
                                                   [sg.Input(key='SMTP_SERVER', size=(35, 1), do_not_clear=True)],
                                                   [sg.Input(key='SMTP_PORT', size=(35, 1), do_not_clear=True)],
                                                   [sg.T('')],
                                                   [sg.Input(key='SMTP_USER', size=(35, 1), do_not_clear=True)],
                                                   [sg.Input(key='SMTP_PASSWORD', size=(35, 1), password_char='*',
                                                             do_not_clear=True)],
                                                   [sg.InputCombo(['none', 'ssl', 'tls'], key='SECURITY')]
                                               ]),

                                           ],
                                           [self.spacer_tweakf(550)],
                                           ],
                                          )]]

        local_alert_settings = [[sg.Frame('Local alert settings',
                                          [[sg.Checkbox('Send local alerts on screen / RDS Session',
                                                        key='LOCAL_ALERT')],
                                           [self.spacer_tweakf(600)],
                                           ],
                                          )]]
        full_layout = [
            [sg.Column(head_col)],
            [sg.Column(alert_message)],
            [sg.Column(email_alert_settings)],
            [sg.Column(local_alert_settings)]
        ]

        layout = [[sg.Column(full_layout, scrollable=True, vertical_scroll_only=True, size=(470, 550))],
                  [sg.T('')],
                  [sg.T(' ' * 70), sg.Button('Save & trigger test alert'), self.spacer_tweakf(),
                   sg.Button('Save & go back')]
                  ]

        # Display the Window and get values
        try:
            self.alert_window = sg.Window(APP_NAME + ' - ' + APP_VERSION + ' ' + APP_BUILD, icon=ICON_FILE,
                                          resizable=True,
                                          size=(500, 600),
                                          text_justification='left').Layout(layout)
        except Exception as exc:
            logger.critical(exc)
            logger.debug('Trace', exc_info=True)
            sys.exit(1)

        # Finalize window before Update functions can work
        self.alert_window.Finalize()
        self.update_alert_gui_config()

        event, values = self.alert_window.Read(timeout=1)
        # Store initial conf file path before it may be modified
        if current_conf_file is None:
            current_conf_file = values['conf_file']

        while True:
            event, values = self.alert_window.Read(timeout=1000)  # Please try and use a timeout when possible
            # Event (buttons and enable_event enabled controls) handling
            if event is None:
                break
            if event == 'Save & trigger test alert':
                try:
                    self.get_alert_gui_config(values)
                    self.config.write_alert_config_file()
                    trigger_alert(self.config, 'test')
                except ValueError as msg:
                    sg.PopupError(msg)
            elif event == 'Save & go back':
                try:
                    self.get_alert_gui_config(values)
                    self.config.write_alert_config_file()
                    self.alert_window.Close()
                except ValueError as msg:
                    sg.PopupError(msg)
                break
            elif event == 'conf_file':
                try:
                    self.config.read_alert_config_file(values['conf_file'])
                    self.update_alert_gui_config()
                    current_conf_file = values['conf_file']
                except ValueError as msg:
                    sg.PopupError(msg)
                    self.alert_window.Element('conf_file').Update(current_conf_file)

    def update_alert_gui_config(self):
        for key in self.config.int_alert_config['ALERT']:
            value = self.config.int_alert_config['ALERT'][key]
            try:
                if value == 'yes':
                    self.alert_window.Element(key).Update(True)
                elif value == 'no':
                    self.alert_window.Element(key).Update(False)
                else:
                    self.alert_window.Element(key).Update(value)
            except KeyError:
                msg = 'Cannot update [%s] value.' % key
                sg.PopupError(msg)
                logger.error(msg)
                logger.debug('Trace:', exc_info=True)

    def get_alert_gui_config(self, values):
        for key, value in values.items():
            if value is True:
                value = 'yes'
            elif value is False:
                value = 'no'
            if key != 'Browse' and key != 'conf_file' and key != 'useSmtpAuth':
                self.config.int_alert_config['ALERT'][key] = value


def system_service_handler(service, action):
    """Handle Windows / Unix services
    Valid actions are start, stop, restart, status
    Returns True if action succeeded or service is running, False if service does not run
    """

    loops = 0  # Number of seconds elapsed since we started Windows service
    max_wait = 6  # Number of seconds we'll wait for Windows service to start

    msg_already_running = f'Service [{service}] already running.'
    msg_not_running = f'Service [{service}] is not running.'
    msg_action = f'Action {action} for service [{service}].'
    msg_success = f'Action {action} succeeded.'
    msg_failure = f'Action {action} failed.'
    msg_too_long = f'Action {action} took more than {max_wait} seconds and seems to have failed.'

    def nt_service_status(service):
        # Returns list. If second entry = 4, service is running
        # TODO: handle other service states than 4
        service_status = win32serviceutil.QueryServiceStatus(service)
        if service_status[1] == 4:
            return True
        return False

    if os.name == 'nt':
        is_running = nt_service_status(service)

        if action == "start":
            if is_running:
                logger.info(msg_already_running)
                return True
            logger.info(msg_action)
            try:
                # Does not provide return code, so we need to check manually
                win32serviceutil.StartService(service)
                while not is_running and loops < max_wait:
                    is_running = nt_service_status(service)
                    if is_running:
                        logger.info(msg_success)
                        return True
                    else:
                        sleep(2)
                        loops += 2
                logger.error(msg_too_long)
                raise Exception
            except Exception:
                logger.error(msg_failure)
                logger.debug('Trace', exc_info=True)
                raise Exception

        elif action == "stop":
            if not is_running:
                logger.info(msg_not_running)
                return True
            logger.info(msg_action)
            try:
                win32serviceutil.StopService(service)
                logger.info(msg_success)
                return True
            except Exception:
                logger.error(msg_failure)
                logger.debug('Trace:', exc_info=True)
                raise Exception

        elif action == "restart":
            system_service_handler(service, 'stop')
            sleep(1)  # arbitrary sleep between
            system_service_handler(service, 'start')

        elif action == "status":
            return is_running

    else:
        # Using lsb service X command on Unix variants, hopefully the most portable

        # service_status = os.system("service " + service + " status > /dev/null 2>&1")

        # Valid exit code are 0 and 3 (because of systemctl using a service redirect)
        service_status, _ = command_runner(f'service "{service}" status')
        if service_status == 0:
            is_running = True
        else:
            is_running = False

        if action == "start":
            if is_running:
                logger.info(msg_already_running)
                return True

            logger.info(msg_action)
            try:
                # result = os.system('service ' + service + ' start > /dev/null 2>&1')
                result, output = command_runner(f'service "{service} start')
                if result == 0:
                    logger.info(msg_success)
                    return True
                logger.error(f'Could not start service, code [{result}].')
                logger.error(f'Output:\n{output}')
                raise Exception
            except Exception:
                logger.info(msg_failure)
                logger.debug('Trace:', exc_info=True)
                raise Exception

        elif action == "stop":
            if not is_running:
                logger.info(msg_not_running)
            else:
                logger.info(msg_action)
                try:
                    # result = os.system('service ' + service + ' stop > /dev/null 2>&1')
                    result, output = command_runner(f'service "{service}" stop')
                    if result == 0:
                        logger.info(msg_success)
                        return True
                    logger.error(f'Could not start service, code [{result}].')
                    logger.error(f'Output:\n{output}')
                    raise Exception
                except Exception:
                    logger.error(msg_failure)
                    logger.debug('Trace:', exc_info=True)
                    raise Exception

        elif action == "restart":
            system_service_handler(service, 'stop')
            system_service_handler(service, 'start')

        elif action == "status":
            return is_running


def trigger_alert(config, mode=None):
    src = None
    dst = None
    smtp_server = None
    smtp_port = None

    # Get environment variables set by smartd (see man smartd.conf)
    smartd_info = {}
    smartd_info['device'] = os.environ.get('SMARTD_DEVICE', 'Unknown')
    smartd_info['devicetype'] = os.environ.get('SMARTD_DEVICETYPE', 'Unknown')
    smartd_info['devicestring'] = os.environ.get('SMARTD_DEVICESTRING', 'Unknown')
    smartd_info['deviceinfo'] = os.environ.get('SMARTD_DEVICEINFO', 'Unknown')
    smartd_info['failtype'] = os.environ.get('SMARTD_FAILTYPE', 'Unknown')
    smartd_info['first'] = os.environ.get('SMARTD_TFIRST', 'Unknown')
    smartd_info['prevcnt'] = os.environ.get('SMARTD_PREVCNT', 'Unknown')
    smartd_info['nextdays'] = os.environ.get('SMARTD_NEXTDAYS', 'Unknown')

    if mode == 'test':
        subject = 'Smartmontools-win email test'
        warning_message = "Smartmontools-win Alert Test"
    elif mode == 'installmail':
        subject = 'Smartmontools-win installation test'
        warning_message = 'Smartmontools-win installation confirmation.'
    else:
        subject = 'Smartmontools-win alert'
        try:
            warning_message = config.int_alert_config['ALERT']['WARNING_MESSAGE']
        except KeyError:
            warning_message = 'Default warning message not set !'

    # TODO integrate smartd_info with warning message tidier
    warning_message = f'{warning_message}\n{smartd_info}'

    if config.int_alert_config['ALERT']['MAIL_ALERT'] != 'no':
        src = config.int_alert_config['ALERT']['SOURCE_MAIL']
        dst = config.int_alert_config['ALERT']['DESTINATION_MAILS']
        smtp_server = config.int_alert_config['ALERT']['SMTP_SERVER']
        smtp_port = config.int_alert_config['ALERT']['SMTP_PORT']

        try:
            smtp_user = config.int_alert_config['ALERT']['SMTP_USER']
        except KeyError:
            smtp_user = None

        try:
            smtp_password = config.int_alert_config['ALERT']['SMTP_PASSWORD']
        except KeyError:
            smtp_password = None

        try:
            security = config.int_alert_config['ALERT']['SECURITY']
        except KeyError:
            security = None

        # Try to run smartctl diag for all disks
        try:
            smartctl_output = ''
            disks = smartctl_wrapper.get_disks()
            for disk in disks:
                if disk['type'] != 'unknown':
                    smartctl_output = smartctl_output + smartctl_wrapper.get_smart_info(disk['name'])
            attachment = zlib.compress(smartctl_output.encode('utf-8'))
        except Exception:
            logger.error('Cannot get smartctl output.')
            logger.debug('Trace', exc_info=True)
            attachment = None

        if len(src) > 0 and len(dst) > 0 and len(smtp_server) > 0 and len(smtp_port) > 0:
            try:
                ret = ofunctions.Mailer.send_email(source_mail=src, destination_mails=dst, smtp_server=smtp_server,
                                                   smtp_port=smtp_port,
                                                   smtp_user=smtp_user, smtp_password=smtp_password, security=security,
                                                   subject=subject, attachment=attachment,
                                                   filename='smartctl_output.zip',
                                                   body=warning_message, debug=True)  # TODO remove debug True
                # WIP
                logger.info(f'Mailer result [{ret}].')

            except Exception as exc:
                msg = 'Cannot send email: {0}'.format(exc)
                logger.error(msg)
                logger.debug('Trace', exc_info=True)
                raise ValueError(msg)
        else:
            msg = 'Cannot trigger mail alert. Essential parameters missing.'
            logger.critical(msg)
            logger.critical(f'src: {src}, dst: {dst}, smtp_server: {smtp_server}, smtp_port; {smtp_port}.')
            raise ValueError(msg)

    if config.int_alert_config['ALERT']['LOCAL_ALERT'] != 'no':
        if os.name == 'nt':
            # Make a popup appear on all sessions including console
            # TODO add CURRENT_DIR
            command = f'wtssendmsg.exe -a "{warning_message}"'
        else:
            # Alert all users on terminal
            command = f'wall "{warning_message}"'
        try:
            exit_code, output = command_runner(command)
            if exit_code != 0:
                msg = f'Running local alert failed with exit code [{exit_code}].'
                logger.error(msg)
                logger.error(f'Additional output:\n{output}')
                raise ValueError(msg)
        except Exception as exc:
            msg = 'Cannot run alert program: {0}'.format(exc)
            logger.error(msg)
            logger.debug('Trace', exc_info=True)
            raise ValueError(msg)


def main(argv):
    logger.info(f'{APP_NAME} {APP_VERSION} {APP_BUILD}')
    logger.info(f'Running on {" ".join(platform.uname())} {platform.python_version()} py={ofunctions.python_arch()}')

    if IS_STABLE is False:
        logger.warning('Warning: This is an unstable developpment version.')

    sg.ChangeLookAndFeel('Material2')
    sg.SetOptions(element_padding=(0, 0), font=('Helvetica', 9), margins=(2, 1), icon=ICON_FILE)

    config = Configuration()

    try:
        config.read_smartd_conf_file()
        for drive_type in config.drive_types:
            logger.debug(f'Drive list for {drive_type}:{config.drive_list[drive_type]}')
            logger.debug(f'Config for {drive_type}:{config.config_list[drive_type]}')
    except ValueError:
        msg = 'No smartd config file found, using default smartd configuration.'
        logger.info(msg)
        sg.Popup(msg)

    try:
        config.read_alert_config_file()
    except ValueError:
        msg = 'No alert config file found, using default alert configuration.'
        logger.info(msg)
        sg.Popup(msg)

    try:
        if len(argv) > 1:
            if argv[1] == '--alert':
                trigger_alert(config)
            elif argv[1] == '--testalert':
                trigger_alert(config, 'test')
            elif argv[1] == '--installmail':
                trigger_alert(config, 'install')
    except ValueError as msg:
        logger.error(msg)
        sys.exit(1)

    try:
        MainGuiApp(config)
    except Exception:
        logger.critical("Cannot instanciate main app.")
        logger.debug('Trace:', exc_info=True)
        sys.exit(1)


# Improved answer I have done in https://stackoverflow.com/a/49759083/2635443
if __name__ == '__main__':
    elevate(main, sys.argv)
