#!/usr/bin/env python
# -*- coding: utf-8 -*-

# WIP #TODO reload gui on conf file change

# IMPORTS ################################################################################################

import os
import sys
# import getopt
import platform  # Detect OS
import re  # Regex handling
import time  # sleep command
import subprocess  # system_service_handler
from datetime import datetime
import ofunctions
import ofunctions.Mailer
from scrambledconfigparser.scrambledconfigparser import ScrambledConfigParser

if sys.version_info[0] >= 3:
    import PySimpleGUI.PySimpleGUI as sg
else:
    import PySimpleGUI.PySimpleGUI27 as sg

# Module pywin32
if platform.system() == "Windows":
    import win32serviceutil
    import ctypes  # In order to perform UAC check
    import win32event  # monitor process
    import win32process  # monitor process
    from win32com.shell.shell import ShellExecuteEx
    from win32com.shell import shellcon

# BASIC FUNCTIONS & DEFINITIONS #########################################################################

APP_NAME = 'smartd_pyngui'  # Stands for smart daemon python native gui
APP_VERSION = '0.7-dev'
APP_BUILD = '2019051301'
APP_DESCRIPTION = 'smartd v5.4+ configuration interface'
CONTACT = 'ozy@netpower.fr - http://www.netpower.fr'
COPYING = 'Written in 2012-2019'
AUTHOR = 'Orsiris de Jong'

LOG_FILE = APP_NAME + '.log'

SMARTD_SERVICE_NAME = 'smartd'
SMARTD_CONF_FILENAME = 'smartd.conf'
ALERT_CONF_FILENAME = 'alerts.conf'

DEFAULT_UNIX_PATH = '/etc/smartd'

IS_STABLE = False  # TODO PROD

# FreeArt fa9737100
ICON_FILE = b'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\n'
# ICON_FILE='smartd_pyngui.ico'

# Generate key via c = ScrambledConfigParser()
# c.generate_key()
AES_ENCRYPTION_KEY = b'*\xc2\xc8\x93Ob\xa6-\xcfq5\x8e\xe9V7\xba\x17\xc0dq\xaa\xfa5\x92\xa1\xf86\x97\x1e\x1e\x00\x07'


#### DEV NOTES ###############################################################################################

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

# Use for logging tracebacks
# except Exception as e:
#     logger.error('Failed to open file', exc_info=True)
# You can also call logger.exception(msg, *args), it equals to logger.error(msg, exc_info=True, *args)

logger = ofunctions.logger_get_logger(LOG_FILE, debug=_DEBUG)


# ACTUAL APPLICATION ######################################################################################


class Configuration:
    smart_conf_file = ""

    def __init__(self, file_path=None): # TODO investigate file_path usage here (which refers to both smartd and alert conf files)
        """Determine smartd configuration file path"""

        # TODO: app_root might be bad because of nuitka sys.argv[0] might not be the same
        # __file__ variable doesn't exist in frozen py2exe mode, get app_root
        try:
            self.app_executable = os.path.abspath(__file__)
            self.app_root = os.path.dirname(self.app_executable)
        except OSError:
            self.app_executable = os.path.abspath(sys.argv[0])
            self.app_root = os.path.dirname(self.app_executable)

        self.smart_conf_file = None
        self.alert_conf_file = None

        self.int_alert_config = ScrambledConfigParser()
        self.int_alert_config.set_key(AES_ENCRYPTION_KEY)

        if file_path is not None:
            self.smart_conf_file = file_path
            if not os.path.isfile(self.smart_conf_file):
                logger.info("Using new file [" + self.smart_conf_file + "].")
        else:
            if platform.system() == "Windows":
                # Get program files environment
                try:
                    program_files_x86 = os.environ["ProgramFiles(x86)"]
                except:
                    program_files_x86 = os.environ["ProgramFiles"]

                try:
                    program_files_x64 = os.environ["ProgramW6432"]
                except:
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
            self.set_smartd_defaults()
        else:
            logger.debug('Found configuration file in [%s].' % self.smart_conf_file)

        if self.alert_conf_file is None:
            self.alert_conf_file = os.path.join(self.app_root, ALERT_CONF_FILENAME)
            self.set_alert_defaults()
        else:
            logger.debug('Found alert config file in [%s].' % self.alert_conf_file)

    def set_smartd_defaults(self):
        self.drive_list = ['DEVICESCAN']
        self.config_list = ['-H', '-C 197+', '-l error', '-U 198+', '-l selftest', '-t', '-f', '-I 194', '-n sleep,7,q',
                            '-s (L/../../4/13|S/../../0,1,2,3,4,5,6/10)']

        # Default behavior is to for smartmontools to launch this app with --alert
        self.config_list.append('-m <nomailer>')
        self.config_list.append('-M exec "%s --alert"' % self.app_executable)

    def set_alert_defaults(self):
        self.int_alert_config.add_section('ALERT')
        self.int_alert_config['ALERT']['conf_file'] = os.path.join(
            os.path.dirname(self.smart_conf_file), '%s-alert.conf' % APP_NAME)
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

    def read_smartd_conf_file(self, conf_file=None):
        if conf_file is None:
            conf_file = self.smart_conf_file
        """   
        if not os.path.isfile(self.smart_conf_file):
            msg = "No suitable [%s] file found, creating new file [%s]." % \
                  (SMARTD_CONF_FILENAME, self.smart_conf_file)
            logger.info(msg)
            sg.Popup(msg)
        else:
        """
        try:
            with open(conf_file, 'r') as fp:

                try:
                    drive_list = []
                    for line in fp.readlines():
                        if not line[0] == "#" and line[0] != "\n" and line[0] != "\r" and line[0] != " ":
                            config_list = line.split(' -')
                            config_list = [config_list[0]] + ['-' + item for item in config_list[1:]]
                            # Remove unnecessary blanks and newlines
                            for i, item in enumerate(config_list):
                                config_list[i] = config_list[i].strip()
                            drive_list.append(config_list[0])
                            del config_list[0]

                    self.drive_list = drive_list
                    self.config_list = config_list
                    self.smart_conf_file = conf_file
                    return True
                except Exception:
                    msg = "Cannot read in config file [%s]." % conf_file
                    logger.error(msg)
                    logger.debug('Trace:', exc_info=True)
                    sg.PopupError(msg)
                    return False
        except:
            msg = 'Cannot read from config file [%s].' % conf_file
            logger.error(msg)
            logger.debug('Trace:', exc_info=True)
            sg.PopupError(msg)
            return False

    def write_smartd_conf_file(self):
        try:
            with open(self.smart_conf_file, 'w') as fp:
                try:
                    fp.write('# This file was generated on ' + str(
                        datetime.now()) + ' by ' + APP_NAME + ' ' + APP_VERSION + ' - http://www.netpower.fr\n')
                    for drive in self.drive_list:
                        line = drive
                        for arg in self.config_list:
                            line += " " + arg
                        fp.write(line + "\n")
                except Exception as e:
                    msg = "Cannot write data in config file [%s]." % self.smart_conf_file
                    logger.error(msg)
                    logger.error(e)
                    logger.debug('Trace', exc_info=True)
                    sg.PopupError(msg)
                    raise Exception
                return True  # TODO do we need this here
        except Exception as e:
            logger.error("Cannot write to config file [%s]." % self.smart_conf_file)
            logger.error(e)
            logger.debug('Trace', exc_info=True)
            raise Exception

    def write_alert_config_file(self):
        if os.path.isdir(os.path.dirname(self.alert_conf_file)):
            with open(self.alert_conf_file, 'wb') as fp:
                self.int_alert_config.write_scrambled(fp)
        else:
            msg = 'Cannot write [%s]. Directory maybe be missing.' % self.alert_conf_file

    def read_alert_config_file(self, conf_file=None):
        if conf_file is None:
            conf_file = self.alert_conf_file
        try:
            self.int_alert_config.read_scrambled(conf_file)
            self.alert_conf_file = conf_file
            return True
        except:
            msg = 'Cannot read [%s].' % conf_file
            logger.error(msg)
            sg.PopupError(msg)
            return False

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
                                          ('-W', 'Report temperature changes with values :'),
                                          ]

        self.manual_drive_list_tooltip = 'Even under Windows, smartd addresses disks as \'/dev/sda /dev/sdb ... /dev/sdX\'\n' \
                                         'Intel raid drives are addresses as /dev/csmiX,Y where X is the controller number\n' \
                                         'and Y is the drive number. See smartd documentation for more.\n' \
                                         'Example working config:\n' \
                                         '\n' \
                                         '/dev/sda\n' \
                                         '/dev/sdb\n' \
                                         '/dev/csmi0,1'
        self.tooltip_image = b'R0lGODlhFAAUAPcAAAAAAAEBAQICAgMDAwYGBggICAkJCQoKCgwMDA4ODhAQEBQUFBoaGhsbGxwcHB0dHR4eHh8fHyAgICEhISIiIiMjIyYmJioqKi4uLjIyMjU1NTg4OEVFRU5OTk9PT1BQUFJSUlRUVFVVVVZWVldXV1hYWGBgYGdnZ2lpaWpqamxsbG1tbW5ubm9vb3h4eAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACH5BAEAAP8ALAAAAAAUABQAAAifAP8JHPhvBAUDBiiMIMhwYIQAECNChNBQYAuJGCOuYHgxo8eNAzEeINgBo0OT/y4wELhB4gOBGQUKCBBS4j8SGQssgCjQBcYQFTxCxCBwAkYJBoQOEMghI4GkHkH8y+CRAAWhJlgIjSBCqNcAUj0qEAgV5YOMKgSWyNigpkQNAi3EHJgiYwIEGU8wRPEVot6KDYSurEjwg4MBAxx4qBgQADs=\n'

        self.spacer_tweak = [sg.T(' ' * 702, font=('Helvetica', 1))]
        self.button_spacer = sg.T(' ' * 10, font=('Helvetica', 1))

        self.main_gui()

    def main_gui(self):
        current_conf_file = None

        head_col = [[sg.Text(APP_DESCRIPTION)],
                    [sg.Frame('Configuration file', [[sg.InputText(self.config.smart_conf_file, key='smart_conf_file',
                                                                   enable_events=True, do_not_clear=True, size=(90, 1)),
                                                      self.button_spacer, sg.FileBrowse(target='smart_conf_file')],
                                                     self.spacer_tweak,
                                                     ])],
                    ]

        drive_selection = [[sg.Radio('Automatic', group_id='driveDetection', key='drive_auto', enable_events=True)],
                           [sg.Radio('Manual drive list', group_id='driveDetection', key='drive_manual',
                                     enable_events=True, tooltip=self.manual_drive_list_tooltip),
                            sg.Image(data=self.tooltip_image, key='manual_drive_list_tooltip', enable_events=True)]
                           ]
        drive_list = [[sg.Multiline(size=(60, 6), key='drive_list', do_not_clear=True,
                                    background_color=self.color_grey_disabled)]]
        drive_config = [[sg.Frame('Drive detection', [[sg.Column(drive_selection), sg.Column(drive_list)],
                                                      self.spacer_tweak,
                                                      ])]]

        # Long self-tests
        long_test_time = [
            [sg.T('Schedule a long test at '), sg.InputCombo(self.hours, key='long_test_hour'), sg.T('H every')]]
        long_test_days = []
        for i in range(0, 7):
            key = 'long_day_' + self.days[i]
            long_test_days.append(sg.Checkbox(self.days[i], key=key))
        long_test_days = [long_test_days]
        long_tests = [[sg.Frame('Scheduled long self-tests', [[sg.Column(long_test_time)],
                                                              [sg.Column(long_test_days)],
                                                              self.spacer_tweakf(343),
                                                              ])]]

        # Short self-tests
        short_test_time = [
            [sg.T('Schedule a short test at '), sg.InputCombo(self.hours, key='short_test_hour'), sg.T('H every')]]
        short_test_days = []
        for i in range(0, 7):
            key = 'short_day_' + self.days[i]
            short_test_days.append(sg.Checkbox(self.days[i], key=key))
        short_test_days = [short_test_days]
        short_tests = [[sg.Frame('Scheduled short self-tests', [[sg.Column(short_test_time)],
                                                                [sg.Column(short_test_days)],
                                                                self.spacer_tweakf(343),
                                                                ])]]

        # Attribute checks
        count = 1
        smart_health_col1 = []
        smart_health_col2 = []
        for key, description in self.health_parameter_map:
            if count <= 6:
                smart_health_col1.append([sg.Checkbox(description + ' (' + key + ')', key=key)])
            else:
                smart_health_col2.append([sg.Checkbox(description + ' (' + key + ')', key=key)])
            count += 1

        attributes_check = [
            [sg.Frame('Smart health Checks', [[sg.Column(smart_health_col1), sg.Column(smart_health_col2)],
                                              self.spacer_tweak,
                                              ])]]

        # Temperature checks
        temperature_check = []
        for key, description in self.temperature_parameter_map:
            temperature_check.append([sg.Checkbox(description + ' (' + key + ')', key=key)])
        temperature_options = [[sg.Frame('Temperature settings',
                                         [[sg.Column(temperature_check),
                                           sg.Column([[sg.T('Temperature difference since last report')],
                                                      [sg.T('Info log when temperature reached')],
                                                      [sg.T('Critical log when temperature reached')],
                                                      ]),
                                           sg.Column([[sg.InputCombo(self.temperature_celsius, key='temp_diff',
                                                                     default_value='20')],
                                                      [sg.InputCombo(self.temperature_celsius, key='temp_info',
                                                                     default_value='55')],
                                                      [sg.InputCombo(self.temperature_celsius, key='temp_crit',
                                                                     default_value='60')],
                                                      ]),

                                           ],
                                          self.spacer_tweak,
                                          ],
                                         )]]

        # Energy saving
        energy_text = [[sg.T('Do not execute smart tests when disk energy mode is ')],
                       [sg.T('Force test execution after N skipped tests')],
                       ]
        energy_choices = [[sg.InputCombo(self.energy_modes, key='energy_mode')],
                          [sg.InputCombo(["%.1d" % i for i in range(8)], key='energy_skips')],
                          ]
        energy_options = [[sg.Frame('Energy saving', [[sg.Column(energy_text), sg.Column(energy_choices)],
                                                      self.spacer_tweak,
                                                      ])]]
        
        # Email options
        alerts = [[sg.Radio('Use %s internal alert system' % APP_NAME, group_id='alerts', key='use_internal_alert', default=True,
                            enable_events=True), sg.Button('Configure')],
                  [sg.Radio(
                      'Use system mail command to send alerts to the following addresses (comma separated list) on Unixes',
                      group_id='alerts', key='use_system_mailer', default=False, enable_events=True)],
                  [sg.InputText(key='mail_addresses', size=(98, 1), do_not_clear=True)],
                  [sg.Radio('Use the following external alert handling script', group_id='alerts',
                            key='use_external_script', default=False, enable_events=True)],
                  [sg.InputText(key='external_script_path', size=(90, 1), do_not_clear=True), sg.FileBrowse()],
                  ]
        alert_options = [[sg.Frame('Alert actions', [[sg.Column(alerts)],
                                                     self.spacer_tweak,
                                                     ])]]

        # Supplementary options
        sup_options_col = [[sg.InputText(key='supplementary_options', size=(98, 1), do_not_clear=True)]]

        sup_options = [[sg.Frame('Supplementary smartd options', [[sg.Column(sup_options_col)],
                                                                  self.spacer_tweak,
                                                                  ])]]

        full_layout = [
            [sg.Column(head_col)],
            [sg.Column(drive_config)],
            [sg.Column(long_tests), sg.Column(short_tests)],
            [sg.Column(attributes_check)],
            [sg.Column(temperature_options)],
            [sg.Column(energy_options)],
            [sg.Column(alert_options)],
            [sg.Column(sup_options)],
        ]

        layout = [[sg.Column(full_layout, scrollable=True, vertical_scroll_only=True, size=(722, 550))],
                  [sg.T('')],
                  [sg.T(' ' * 70), sg.Button('Save changes'), self.button_spacer, sg.Button('Reload smartd service'),
                   self.button_spacer, sg.Button('Exit')]
                  ]

        # Display the Window and get values

        try:
            self.window = sg.Window(APP_NAME + ' - ' + APP_VERSION + ' ' + APP_BUILD, icon=ICON_FILE, resizable=True,
                                    size=(750, 600),
                                    text_justification='left').Layout(layout)
        except Exception as e:
            logger.critical(e)
            logger.debug('Trace', exc_info=True)
            sys.exit(1)

        # Finalize window before Update functions can work
        self.window.Finalize()

        # Set defaults
        if platform.system() == 'Windows':
            self.window.Element('use_external_script').Update(True)
            self.window.Element('mail_addresses').Update(disabled=True)
            self.window.Element('external_script_path').Update(disabled=False)
        else:
            self.window.Element('use_system_mailer').Update(True)
            self.window.Element('mail_addresses').Update(disabled=False)
            self.window.Element('external_script_path').Update(disabled=False)

        self.update_main_gui_config()

        event, values = self.window.Read(timeout=1)
        # Store current config filename
        if current_conf_file is None:
            current_conf_file = values['smart_conf_file']

        while True:
            event, values = self.window.Read(timeout=1000)  # Please try and use a timeout when possible

            # Event (buttons and enable_event enabled controls) hancling
            if event is None:
                break
            if event == 'Exit':  # if user closed the window using X or clicked Quit button
                action = sg.Popup('Are you sure ?', custom_text=('Cancel', 'Exit'), icon=None)
                if action == 'Cancel':
                    pass
                elif action == 'Exit':
                    break
            elif event == 'Reload smartd service':
                self.service_reload()
            elif event == 'Save changes':
                try:
                    self.get_main_gui_config(values)
                    self.config.write_smartd_conf_file()
                except:
                    sg.PopupError('Cannot save configuration', icon=None)
                else:
                    sg.Popup('Changes saved to configuration file')
            elif event == 'drive_auto':
                self.window.Element('drive_list').Update(disabled=True, background_color=self.color_grey_disabled)
            elif event == 'drive_manual':
                self.window.Element('drive_list').Update(disabled=False, background_color=self.color_green_enabled)
            elif event == 'use_system_mailer' or event == 'use_internal_alert' or event == 'use_external_script':
                self.alert_switcher(values)
            elif event == 'smart_conf_file':
                ret = self.config.read_smartd_conf_file(values['smart_conf_file'])
                if ret is True:
                    self.update_main_gui_config()
                    current_conf_file = values['smart_conf_file']
                else:
                    self.window.Element('smart_conf_file').Update(current_conf_file)
            elif event == 'manual_drive_list_tooltip':
                sg.Popup(self.manual_drive_list_tooltip)
            elif event == 'Configure':
                self.configure_internal_alerts()

        self.window.Close()

    def alert_switcher(self, values):
        if values['use_system_mailer'] is True:
            self.window.Element('mail_addresses').Update(disabled=False)
            self.window.Element('external_script_path').Update(disabled=True)
        if values['use_internal_alert'] is True:
            self.window.Element('mail_addresses').Update(disabled=True)
            self.window.Element('external_script_path').Update(disabled=True)
        if values['use_external_script'] is True:
            self.window.Element('mail_addresses').Update(disabled=True)
            self.window.Element('external_script_path').Update(disabled=False)


    def spacer_tweakf(self, pixels=10):
        return [sg.T(' ' * pixels, font=('Helvetica', 1))]


    def update_main_gui_config(self):
        # Apply drive config
        if self.config.drive_list == ['DEVICESCAN']:
            self.window.Element('drive_auto').Update(True)
        else:
            self.window.Element('drive_manual').Update(True)
            for drive in self.config.drive_list:
                drives = drive + '\n'
                self.window.Element('drive_list').Update(drives)

        # Self test regex GUI setup
        if '-s' in '\t'.join(self.config.config_list):
            for i, item in enumerate(self.config.config_list):
                if '-s' in item:
                    index = i

                    # TODO: Add other regex parameter here (group 1 & 2 missing)
                    long_test = re.search('L/(.+?)/(.+?)/(.+?)/([0-9]*)', self.config.config_list[index])
                    if long_test:
                        # print(long_test.group(1))
                        # print(long_test.group(2))
                        # print(long_test.group(3))
                        if long_test.group(3):
                            day_list = list(long_test.group(3))
                            # Handle special case where . means all
                            if day_list[0] == '.':
                                for day in range(0, 7):
                                    self.window.Element('long_day_' + self.days[day]).Update(True)
                            else:
                                for day in day_list:
                                    if day.strip("[]").isdigit():
                                        self.window.Element('long_day_' + self.days[int(day.strip("[]")) - 1]).Update(True)
                        if long_test.group(4):
                            self.window.Element('long_test_hour').Update(long_test.group(4))

                    short_test = re.search('S/(.+?)/(.+?)/(.+?)/([0-9]*)', self.config.config_list[index])
                    if short_test:
                        # print(short_test.group(1))
                        # print(short_test.group(2))
                        if short_test.group(3):
                            day_list = list(short_test.group(3))
                            # Handle special case where . means all
                            if day_list[0] == '.':
                                for day in range(0, 7):
                                    self.window.Element('short_day_' + self.days[day]).Update(True)
                            else:
                                for day in day_list:
                                    if day.strip("[]").isdigit():
                                        self.window.Element('short_day_' + self.days[int(day.strip("[]")) - 1]).Update(True)
                        if short_test.group(4):
                            self.window.Element('short_test_hour').Update(short_test.group(4))

                    break

        # Attribute checks GUI setup
        for key, value in self.health_parameter_map:
            if key in self.config.config_list:
                self.window.Element(key).Update(True)
                # Handle specific dependancy cases (-C 197+ depends on -C 197 and -U 198+ depends on -U 198)
                if key == '-C 197+':
                    self.window.Element('-C 197').Update(True)
                elif key == '-U 198+':
                    self.window.Element('-U 198').Update(True)

        # Handle temperature specific cases
        for i, item in enumerate(self.config.config_list):
            if re.match(r'^-W [0-9]{1,2},[0-9]{1,2},[0-9]{1,2}$', item):
                self.window.Element('-W').Update(True)
                self.window.Element('-I 194').Update(False)
                temperatures = item.split(' ')[1]
                temperatures = temperatures.split(',')
                self.window.Element('temp_diff').Update(temperatures[0])
                self.window.Element('temp_info').Update(temperatures[1])
                self.window.Element('temp_crit').Update(temperatures[2])

        # Energy saving GUI setup
        if '-n' in '\t'.join(self.config.config_list):
            for i, item in enumerate(self.config.config_list):
                if '-n' in item:
                    index = i

                    energy_savings = self.config.config_list[index].split(',')
                    for mode in self.energy_modes:
                        if mode in energy_savings[0]:
                            self.window.Element('energy_mode').Update(mode)

                    if energy_savings[1].isdigit():
                        self.window.Element('energy_skips').Update(energy_savings[1])
                    # if energy_savings[1] == 'q':
                    # TODO: handle q parameter
                    break

        #self.alert_switcher((['use_internal_alert'] = True))
        # Get alert options
        # -m <nomailer> -M exec PATH/smartd_pyngui = use internal alert
        # -m mail@addr.tld = use system mailer
        # -m <nomailer> -M exec PATH/script = use external_script

        config_list_flat = '\t'.join(self.config.config_list)
        print(config_list_flat)
        if '-m <nomailer> -M exec' in config_list_flat:
            # TODO Remove fuzzy detection here
            if APP_NAME in config_list_flat:
                v = {'use_internal_alert' : True, 'use_system_mailer' : False, 'use_external_script' : False}
            else:
                v = {'use_internal_alert': False, 'use_system_mailer': False, 'use_external_script': True}
            self.alert_switcher(v)

        # else assume we use system mailer
        else:
            v = {'use_internal_alert': DEFAULT_UNIX_PATH, 'use_system_mailer': True, 'use_external_script': False}

        """
        if '-m' in '\t'.join(self.config.config_list):
            for i, item in enumerate(self.config.config_list):
                if '-m' in item:
                    index = i

                    mail_addresses = self.config.config_list[index].replace('-m ', '', 1)
                    self.window.Element('use_system_mailer').Update(True)
                    if not mail_addresses == '<nomailer>':
                        self.window.Element('mail_addresses').Update(mail_addresses, disabled=False)
                    self.window.Element('external_script_path').Update(disabled=True)
                    break
        else:
            self.window.Element('use_external_script').Update(True)

        if '-M' in '\t'.join(self.config.config_list):
            for i, item in enumerate(self.config.config_list):
                if '-M' in item:
                    index = i

                    self.window.Element('use_external_script').Update(True)
                    self.window.Element('mail_addresses').Update(disabled=True)
                    self.window.Element('external_script_path').Update(
                        self.config.config_list[index].replace('-M exec ', '', 1), disabled=False)
                    break
        else:
            self.window.Element('use_system_mailer').Update(True)
            self.window.Element('mail_addresses').Update(disabled=False)
        """


    def get_main_gui_config(self, values):
        drive_list = []
        config_list = []

        if values['drive_auto'] is True:
            drive_list.append('DEVICESCAN')
        else:
            drive_list = values['drive_list'].split()

            # TODO: better bogus pattern detection
            # TODO: needs to raise exception

            if drive_list == []:
                msg = "Drive list is empty"
                logger.error(msg)
                sg.PopupError(msg)
                return False

            if "example" in drive_list or "exemple" in drive_list:
                msg = "Drive list contains example !!!"
                logger.error(msg)
                sg.PopupError(msg)
                return False

            for item in drive_list:
                if not item[0] == "/":
                    msg = "Drive list doesn't start with slash [%s]." % item
                    logger.error(msg)
                    sg.PopupError(msg)
                    return False

        # smartd health parameters
        try:
            for key, description in self.health_parameter_map:
                if values[key]:
                    # Handle dependancies
                    if key == '-C 197+':
                        if '-C 197' in config_list:
                            for (i, item) in enumerate(config_list):
                                if item == '-C 197':
                                    config_list[i] = '-C 197+'
                        else:
                            config_list.append(key)
                    elif key == '-U 198+':
                        if '-U 198' in config_list:
                            for (i, item) in enumerate(config_list):
                                if item == '-U 198':
                                    config_list[i] = '-U 198+'
                        else:
                            config_list.append(key)
                    else:
                        config_list.append(key)

        except KeyError:
            try:
                key
                msg = "Bogus configuration in [%s]." % key
            except:
                msg = "Bogus configuration in health parameters."
            logger.error(msg)
            logger.debug('Trace:', exc_info=True)
            logger.debug(config_list)
            sg.PopupError(msg)

        try:
            for key, description in self.temperature_parameter_map:
                if values[key]:
                    if key == '-W':
                        config_list.append(
                            key + ' ' + str(values['temp_diff']) + ',' + str(values['temp_info']) + ',' + str(
                                values['temp_crit']))
                    elif key == '-I 194':
                        config_list.append(key)
        except Exception:
            if key:
                msg = "Bogus configuration in [%s] and temperatures." % key
            else:
                msg = "Bogus configuration in temperatures. Cannot read keys."
            logger.error(msg)
            logger.debug('Trace:', exc_info=True)
            logger.debug(config_list)
            sg.PopupError(msg)

        try:
            energy_list = False
            energy_mode = values['energy_mode']
            if energy_mode in self.energy_modes:
                energy_list = '-n ' + energy_mode
            skip_tests = values['energy_skips']
            if energy_list:
                energy_list += ',' + str(skip_tests)
                # TODO: handle -q parameter in GUI
                energy_list += ',q'

                config_list.append(energy_list)
        except Exception as e:
            msg = 'Energy config error'
            logger.error(msg)
            logger.error(e)
            logger.debug('Trace', exc_info=True)
            sg.PopupError(msg)

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
                    if values[test_type + '_day_' + day] is True:
                        regex += str(self.days.index(day) + 1)
                        present = True
                regex += "]"
                # regex = regex.rstrip(',')

                long_test_hour = values['long_test_hour']
                short_test_hour = values['short_test_hour']

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


        except Exception as e:
            msg = 'Test regex creation error'
            logger.error(msg)
            logger.error(e)
            logger.debug('Trace', exc_info=True)
            sg.PopupError(msg)

        # TODO: -M can't exist without -m
        # Mailer options
        if values['use_system_mailer'] is True:
            mail_addresses = values['mail_addresses']
            if len(mail_addresses) > 0:
                config_list.append('-m ' + mail_addresses)
            else:
                msg = 'Missing mail addresses'
                logger.error(msg)
                sg.PopupError(msg)
                raise AttributeError
        else:
            config_list.append('-m <nomailer>')
            external_script_path = values['external_script_path']
            external_script_path = external_script_path.strip('\"\'')
            if not external_script_path == "":
                external_script_path = '"%s"' % external_script_path
                config_list.append('-M exec ' + external_script_path)

        logger.debug(drive_list)
        logger.debug(config_list)
        self.config.drive_list = drive_list
        self.config.config_list = config_list

    def service_reload(self):
        try:
            system_service_handler(SMARTD_SERVICE_NAME, "restart")
        except Exception as e:
            msg = "Cannot restart [" + SMARTD_SERVICE_NAME + "]. Running as admin ? See logs for details."
            logger.error(msg)
            logger.error(e)
            logger.debug('Trace', exc_info=True)
            sg.PopupError(msg)
            return False
        else:
            sg.Popup('Successfully reloaded smartd service.', title='Info')

    def configure_internal_alerts(self):
        current_conf_file = None

        head_col = [[sg.Text(APP_DESCRIPTION)],
                    [sg.Frame('Configuration file',
                              [[sg.InputText('', key='conf_file',
                                             enable_events=True, do_not_clear=True, size=(55, 1)),
                                self.button_spacer, sg.FileBrowse(target='conf_file')],
                               self.spacer_tweak,
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
                                                   [sg.Input(key='SMTP_PASSWORD', size=(35, 1), do_not_clear=True)],
                                                   [sg.InputCombo(['none', 'ssl', 'tls'], key='SECURITY')]
                                               ]),

                                           ],
                                           ],
                                          )]]

        local_alert_settings = [[sg.Frame('Local alert settings',
                                          [[sg.Checkbox('Send local alerts on screen', key='LOCAL_ALERT')],
                                           self.spacer_tweak
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
                  [sg.T(' ' * 70), sg.Button('Save & trigger test alert'), self.button_spacer, sg.Button('Save & exit')]
                  ]

        # Display the Window and get values
        try:
            self.alert_window = sg.Window(APP_NAME + ' - ' + APP_VERSION + ' ' + APP_BUILD, icon=ICON_FILE, resizable=True,
                                    size=(500, 600),
                                    text_justification='left').Layout(layout)
        except Exception as e:
            logger.critical(e)
            logger.debug('Trace', exc_info=True)
            sys.exit(1)

        # Finalize window before Update functions can work
        self.alert_window.Finalize()
        # self.config.readErrorConfigFile()
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
                self.get_alert_gui_config(values)
                self.config.write_alert_config_file()
                trigger_alert(self.config, 'test')
            elif event == 'Save & exit':
                self.get_alert_gui_config(values)
                self.config.write_alert_config_file()
                break
            elif event == 'conf_file':
                ret = self.config.read_alert_config_file(values['conf_file'])
                if ret is True:
                    self.update_alert_gui_config()
                    current_conf_file = values['conf_file']
                else:
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
            except:
                msg = 'Cannot update [%s] value.' % key
                sg.PopupError(msg)
                logger.error(msg)
                logger.debug('Trace:', exc_info=True)

    def get_alert_gui_config(self, values):
        for key, value in values.items():
            if value == True:
                value = 'yes'
            elif value == False:
                value = 'no'
            self.config.int_alert_config['ALERT'][key] = value


def system_service_handler(service, action):
    """Handle Windows / Unix services
    Valid actions are start, stop, restart, status
    Returns True if action succeeded or service is running, False if service does not run
    """

    msg_already_running = "Service [%s] already running." % service
    msg_not_running = "Service [%s] is not running." % service
    msg_action = "Action %s for service [%s]." % (action, service)
    msg_success = "Action %s succeeded." % action
    msg_failure = "Action %s failed." % action

    if platform.system() == "Windows":
        # Returns list. If second entry = 4, service is running
        # TODO: handle other service states than 4
        service_status = win32serviceutil.QueryServiceStatus(service)
        if service_status[1] == 4:
            is_running = True
        else:
            is_running = False

        if action == "start":
            if is_running:
                logger.info(msg_already_running)
                return True
            else:
                logger.info(msg_action)
                try:
                    win32serviceutil.StartService(service)
                    logger.info(msg_success)
                    return True
                except Exception:
                    logger.error(msg_failure)
                    logger.debug('Trace', exc_info=True)
                    raise Exception

        elif action == "stop":
            if not is_running:
                logger.info(msg_not_running)
                return True
            else:
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
            time.sleep(1)
            system_service_handler(service, 'start')

        elif action == "status":
            return is_running

    else:
        # Using lsb service X command on Unix variants, hopefully the most portable

        # service_status = os.system("service " + service + " status > /dev/null 2>&1")

        # Valid exit code are 0 and 3 (because of systemctl using a service redirect)
        service_status, service_output = ofunctions.command_runner('service %s status' % service)
        if service_status == 0:
            is_running = True
        else:
            is_running = False

        if action == "start":
            if is_running:
                logger.info(msg_already_running)
                return True
            else:
                logger.info(msg_action)
                try:
                    # result = os.system('service ' + service + ' start > /dev/null 2>&1')
                    result, output = ofunctions.command_runner('service %s start' % service)
                    if result == 0:
                        logger.info(msg_success)
                        return True
                    else:
                        logger.error('Could not start service, code [%s].' % result)
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
                    result, output = ofunctions.command_runner('service %s stop' % service)
                    if result == 0:
                        logger.info(msg_success)
                        return True
                    else:
                        logger.error('Could not start service, code [%s].' % result)
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


def trigger_alert(config, mode=None): #  TODO write alerts

    src = None
    dst = None
    smtp_server = None
    smtp_port = None

    if mode == 'test':
        subject = 'Smartmontools email test'
        warning_message = "Smartmontools Alert Test"
    elif mode == 'installmail':
        subject = 'Smartmontools installation test'
        warning_message = 'Smartmontools installation confirmation.'
    else:
        subject = 'Smartmontools alert'
        try:
            warning_message = config.int_alert_config['ALERT']['WARNING_MESSAGE']
        except KeyError:
            warning_message = 'Default warning message not set !'

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

        if len(src) > 0 and len(dst) > 0 and len(smtp_server) > 0 and len(smtp_port) > 0:
            try:
                ofunctions.Mailer.send_email(source_mail=src, destination_mails=dst, smtp_server=smtp_server, smtp_port=smtp_port,
                                     smtp_user=smtp_user, smtp_password=smtp_password, security=security, subject=subject,
                                     body=warning_message)

            # TODO Attachment is needed here (complete with smartctl output and env variables)

            except Exception as e:
                logger.error('Cannot send email: %s' % e)
                logger.debug('Trace', exc_info=True)
        else:
            logger.critical('Cannot trigger mail alert. Essential parameters missing.')
            logger.critical('src: %s, dst: %s, smtp_server: %s, smtp_port; %s.' % (src, dst, smtp_server, smtp_port))

    if config.int_alert_config['ALERT']['LOCAL_ALERT'] != 'no':
        try:
            exit_code, output = ofunctions.command_runner('wtssendmsg.exe %s' % warning_message)
            if exit_code != 0:
                logger.error('Running local alert failed with exit codd [%s].' % exit_code)
                logger.error('Additional output: %s' % output)
        except Exception as e:
            logger.error('Cannot run alert program: %s' % e)
            logger.debug('Trace', exc_info=True)

    sys.exit()


def main(argv):
    logger.info("Running on python " + platform.python_version() + " / " + str(platform.uname()))

    if IS_STABLE is False:
        logger.warning("Warning: This is an unstable developpment version.")

    # sg.ChangeLookAndFeel('Reds')
    sg.SetOptions(element_padding=(0, 0), font=('Helvetica', 9), margins=(2, 1), icon=ICON_FILE)

    config = Configuration()

    try:
        config.read_smartd_conf_file()
        logger.debug(str(config.drive_list))
        logger.debug(str(config.config_list))
    except Exception:
        logger.info('Using default smartd configuration.')

    try:
        config.read_alert_config_file()
    except Exception:
        logger.info('Using default alert configuration.')

    if len(argv) > 1:
        if argv[1] == '--alert':
            trigger_alert(config)
        elif argv[1] == '--testalert':
            trigger_alert(config, 'test')
        elif argv[1] == '--installmail':
            trigger_alert(config, 'install')
        sys.exit() # TODO define exit code

    try:
        MainGuiApp(config)
    except Exception:
        logger.critical("Cannot instanciate main app.")
        logger.debug('Trace:', exc_info=True)
        sys.exit(1)


# Improved answer I have done in https://stackoverflow.com/a/49759083/2635443
if __name__ == '__main__':
    current_os_name = os.name
    if ofunctions.is_admin() is True:  # TODO # WIP
        main(sys.argv)
    else:
        # UAC elevation code working for CPython, Nuitka >= 0.6.2, PyInstaller, PyExe, CxFreeze

        # Regardless of the runner (CPython, Nuitka or frozen CPython), sys.argv[0] is the relative path to script,
        # sys.argv[1] are the arguments
        # The only exception being CPython on Windows where sys.argv[0] contains absolute path to script
        # Regarless of OS, sys.executable will contain full path to python binary for CPython and Nuitka,
        # and full path to frozen executable on frozen CPython

        # Recapitulative table create with
        # (CentOS 7x64 / Python 3.4 / Nuitka 0.6.1 / PyInstaller 3.4) and
        # (Windows 10 x64 / Python 3.7x32 / Nuitka 0.6.2.10 / PyInstaller 3.4)
        # --------------------------------------------------------------------------------------------------------------
        # | OS  | Variable       | CPython                       | Nuitka               | PyInstaller                  |
        # |------------------------------------------------------------------------------------------------------------|
        # | Lin | argv           | ['./script.py', '-h']         | ['./test', '-h']     | ['./test.py', -h']           |
        # | Lin | sys.executable | /usr/bin/python3.4            | /usr/bin/python3.4   | /absolute/path/to/test       |
        # | Win | argv           | ['C:\\Python\\test.py', '-h'] | ['test', '-h']       | ['test', '-h']               |
        # | Win | sys.executable | C:\Python\python.exe          | C:\Python\Python.exe | C:\absolute\path\to\test.exe |
        # --------------------------------------------------------------------------------------------------------------

        # Nuitka 0.6.2 and newer define builtin __nuitka_binary_dir
        # Nuitka does not set the frozen attribute on sys
        # Nuitka < 0.6.2 can be detected in sloppy ways, ie if not sys.argv[0].endswith('.py') or len(sys.path) < 3
        # Let's assume this will only be compiled with newer nuitka, and remove sloppy detections
        try:
            __nuitka_binary_dir
            is_nuitka_compiled = True
        except NameError:
            is_nuitka_compiled = False

        if is_nuitka_compiled:
            # On nuitka, sys.executable is the python binary, even if it does not exist in standalone,
            # so we need to fill runner with sys.argv[0] absolute path
            runner = os.path.abspath(sys.argv[0])
            arguments = sys.argv[1:]
            # current_dir = os.path.dirname(runner)

            logger.debug('Running as Nuitka with runner [%s]' % runner)
            logger.debug('Arguments are %s' % arguments)

        # If a freezer is used (PyInstaller, cx_freeze, py2exe)
        elif getattr(sys, "frozen", False):
            runner = os.path.abspath(sys.executable)
            arguments = sys.argv[1:]
            # current_dir = os.path.dirname(runner)

            logger.debug('Running as Frozen with runner [%s]' % runner)
            logger.debug('Arguments are %s' % arguments)

        # If standard interpreter CPython is used
        else:
            runner = os.path.abspath(sys.executable)
            arguments = [os.path.abspath(sys.argv[0])] + sys.argv[1:]
            # current_dir = os.path.abspath(sys.argv[0])

            logger.debug('Running as CPython with runner [%s]' % runner)
            logger.debug('Arguments are %s' % arguments)

        if current_os_name == 'nt':
            # Re-run the program with admin rights, don't use __file__ since frozen python won't know about it
            # Use sys.argv[0] as script path and sys.argv[1:] as arguments, join them as lpstr, quoting each parameter
            # or spaces in parameters will divide parameters
            # lpParameters = sys.argv[0] + " "

            arguments = ' '.join('"' + arg + '"' for arg in arguments)
            try:
                # Method using ctypes which does not wait for executable to exit nor deos get exit code
                # See https://docs.microsoft.com/en-us/windows/desktop/api/shellapi/nf-shellapi-shellexecutew
                # int 0 means SH_HIDE window, 1 is SW_SHOWNORMAL
                # needs the followng imports
                # import ctypes

                # ctypes.windll.shell32.ShellExecuteW(None, 'runas', runner, arguments, None, 0)

                # Version with exit code that waits for executable to exit, needs the following imports
                # import ctypes  # In order to perform UAC check
                # import win32event  # monitor process
                # import win32process  # monitor process
                # from win32com.shell.shell import ShellExecuteEx
                # from win32com.shell import shellcon

                childProcess = ShellExecuteEx(nShow=0, fMask=shellcon.SEE_MASK_NOCLOSEPROCESS,
                                              lpVerb='runas', lpFile=runner, lpParameters=arguments)
                procHandle = childProcess['hProcess']
                obj = win32event.WaitForSingleObject(procHandle, -1)
                exit_code = win32process.GetExitCodeProcess(procHandle)
                logger.debug('Child exited with code: %s' % exit_code)
                sys.exit(exit_code)

            except Exception as e:
                logger.info(e)
                logger.debug('Trace', exc_info=True)
                sys.exit(255)
        # Linux and hopefully others
        else:
            command = 'sudo "%s"%s%s' % (
                runner,
                (' ' if len(arguments) > 0 else ''),
                ' '.join('"%s"' % argument for argument in arguments)
            )
            # TODO : test new command generation
            # command = 'sudo ' + runner + (' ' if len(arguments) > 0 else '') + \
            #          ' '.join('"' + argument + '"' for argument in arguments)
            try:
                # TODO command to command_runner ?
                # Don't specify timeout=X since we don't wan't the program to finish at any moment
                output = subprocess.check_output(command, stderr=subprocess.STDOUT,
                                                 shell=True, universal_newlines=False)
                try:
                    output = output.decode('unicode_escape', errors='ignore')
                except Exception as exc:
                    pass
                logger.debug('Child output: %s' % output)
                sys.exit(0)
            except subprocess.CalledProcessError as exc:
                exit_code = exc.returncode
                logger.debug('Child exited with code: %s' % exit_code)
                try:
                    logger.debug('Child outout: %s' % exc.output)
                except Exception as exc:
                    logger.debug(exc, exc_info=True)
                sys.exit(exit_code)
