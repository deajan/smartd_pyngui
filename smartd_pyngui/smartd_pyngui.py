#!/usr/bin/env python
# -*- coding: utf-8 -*-

#### BASIC FUNCTIONS & DEFINITIONS #########################################################################

APP_NAME = 'smartd_pyngui'  # Stands for smart daemon python native gui
APP_VERSION = '0.6-rc1'
APP_BUILD = '2019010205'
APP_DESCRIPTION = 'smartd v5.4+ configuration interface'
CONTACT = 'ozy@netpower.fr - http://www.netpower.fr'
COPYING = 'Written in 2012-2019'
AUTHOR = 'Orsiris de Jong'

LOG_FILE = APP_NAME + '.log'

SMARTD_SERVICE_NAME = 'smartd'
SMARTD_CONF_FILENAME = 'smartd.conf'

DEFAULT_UNIX_PATH = '/etc/smartd'

IS_STABLE = True  # TODO PROD

# FreeArt fa9737100
#ICON_FILE='smartd_pyngui.ico'
ICON_FILE = b'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\n'

#### IMPORTS ################################################################################################

import os
import sys, getopt
import platform  # Detect OS
import re  # Regex handling
import time  # sleep command
import traceback  # trace module
import subprocess # serviceHandler
if sys.version_info[0] >= 3:
    import PySimpleGUI as sg
else:
    import PySimpleGUI27 as sg
from datetime import datetime

# Logging modules
import tempfile
import logging
from logging.handlers import RotatingFileHandler

# Module pywin32
if platform.system() == "Windows":
    import win32serviceutil
    import win32service
    import ctypes  # In order to perform UAC call

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

#### LOGGING & DEBUG CODE ####################################################################################

# Logging functionality
try:
    os.environ["_DEBUG"]
    _DEBUG = True
except:
    if not IS_STABLE == False:
        _DEBUG = False
    else:
        _DEBUG = True

FORMATTER = logging.Formatter('%(asctime)s :: %(levelname)s :: %(message)s')

def logger_get_console_handler():
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(FORMATTER)
    return console_handler
def logger_get_file_handler():
    try:
        file_handler = logging.handlers.RotatingFileHandler(LOG_FILE, mode='a', encoding='utf-8', maxBytes=1024000, backupCount=3)
    except:
        try:
            tempLogFile = tempfile.gettempdir() + os.sep + APP_NAME + '.log'
            print('Cannot create logfile ' + LOG_FILE)
            print('Trying temporary log file in ' + tempLogFile)
            file_handler = RotatingFileHandler(tempLogFile, mode='a', encoding='utf-8', maxBytes=1000000, backupCount=1)
        except:
            print('Cannot create temporary log file either. Will not log.')
            return False
    file_handler.setFormatter(FORMATTER)
    return file_handler
def logger_get_logger(logger_name):
    logger = logging.getLogger(logger_name)
    if _DEBUG == True:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)
    logger.addHandler(logger_get_console_handler())
    logger.addHandler(logger_get_file_handler())
    #logger.propagate = false
    return logger

logger = logger_get_logger(APP_NAME)

#### ACTUAL APPLICATION ######################################################################################

# sg.ChangeLookAndFeel('NeutralBlue')
sg.SetOptions(element_padding=(0, 0), font=('Helvetica', 9), margins=(2, 1), icon=ICON_FILE)

class Configuration:
    smartConfFile = ""

    def __init__(self, filePath=None):
        """Determine smartd configuration file path"""

        # __file__ variable doesn't exist in frozen py2exe mode, get appRoot
        try:
            self.appRoot = os.path.dirname(os.path.abspath(__file__))
        except:
            self.appRoot = os.path.dirname(os.path.abspath(sys.argv[0]))

        if not filePath == None:
            self.smartConfFile = filePath
            if not os.path.isfile(self.smartConfFile):
                logger.info("Using new file [" + self.smartConfFile + "].")
        else:
            if platform.system() == "Windows":
                # Get program files environment
                try:
                    programFilesX86 = os.environ["ProgramFiles(x86)"]
                except:
                    programFilesX86 = os.environ["ProgramFiles"]

                try:
                    programFilesX64 = os.environ["ProgramW6432"]
                except:
                    programFilesX64 = os.environ["ProgramFiles"]

                if os.path.isfile(self.appRoot + os.sep + SMARTD_CONF_FILENAME):
                    self.smartConfFile = self.appRoot + os.sep + SMARTD_CONF_FILENAME
                elif os.path.isfile(
                        programFilesX64 + os.sep + "smartmontools for Windows" + os.sep + "bin" + os.sep + SMARTD_CONF_FILENAME):
                    self.smartConfFile = programFilesX64 + os.sep + "smartmontools for Windows" + os.sep + "bin" + os.sep + SMARTD_CONF_FILENAME
                elif os.path.isfile(
                        programFilesX86 + os.sep + "smartmontools for Windows" + os.sep + "bin" + os.sep + SMARTD_CONF_FILENAME):
                    self.smartConfFile = programFilesX86 + os.sep + "smartmontools for Windows" + os.sep + "bin" + os.sep + SMARTD_CONF_FILENAME
                elif os.path.isfile(
                        programFilesX64 + os.sep + "smartmontools" + os.sep + "bin" + os.sep + SMARTD_CONF_FILENAME):
                    self.smartConfFile = programFilesX64 + os.sep + "smartmontools" + os.sep + "bin" + os.sep + SMARTD_CONF_FILENAME
                elif os.path.isfile(
                        programFilesX86 + os.sep + "smartmontools" + os.sep + "bin" + os.sep + SMARTD_CONF_FILENAME):
                    self.smartConfFile = programFilesX86 + os.sep + "smartmontools" + os.sep + "bin" + os.sep + SMARTD_CONF_FILENAME
            else:
                if os.path.isfile(self.appRoot + os.sep + SMARTD_CONF_FILENAME):
                    self.smartConfFile = self.appRoot + os.sep + SMARTD_CONF_FILENAME
                elif os.path.isfile("/etc/smartmontools" + os.sep + SMARTD_CONF_FILENAME):
                    self.smartConfFile = "/etc/smartmontools" + os.sep + SMARTD_CONF_FILENAME
                elif os.path.isfile("/etc/smartd" + os.sep + SMARTD_CONF_FILENAME):
                    self.smartConfFile = "etc/smartd" + os.sep + SMARTD_CONF_FILENAME
                elif os.path.isfile("/etc" + os.sep + SMARTD_CONF_FILENAME):
                    self.smartConfFile = "/etc" + os.sep + SMARTD_CONF_FILENAME

        if len(self.smartConfFile) == 0:
            self.smartConfFile = self.appRoot + os.sep + SMARTD_CONF_FILENAME
            self.setDefaults()
        else:
            if not filePath == None:
                logger.debug("Found configuration file in [" + self.smartConfFile + "].")

    def setDefaults(self):
        self.driveList = ['DEVICESCAN']
        self.configList = ['-H', '-C 197+', '-l error', '-U 198+', '-l selftest', '-t', '-f', '-I 194', '-n sleep,7,q',
                      '-s (L/../../4/13|S/../../0,1,2,3,4,5,6/10)']
        if platform.system() == 'Windows':
            self.configList.append('-m <nomailer>')
            self.configList.append('-M exec "C:\\Program Files\\smartmontools for Windows\\bin\\erroraction.cmd"')

    def readSmartdConfFile(self):
        if not os.path.isfile(self.smartConfFile):
            msg = "No suitable [" + SMARTD_CONF_FILENAME + "] file found, creating new file [" + self.smartConfFile + "]."
            logger.info(msg)
            sg.Popup(msg)
        else:
            try:
                fileHandle = open(self.smartConfFile, 'r')
            except Exception as e:
                msg = "Cannot open config file [" + self.smartConfFile + "] for reading."
                logger.error(msg)
                logger.debug(e)
                sg.PopupError(msg)
                raise Exception

            try:
                driveList = []
                for line in fileHandle.readlines():
                    if not line[0] == "#" and line[0] != "\n" and line[0] != "\r" and line[0] != " ":
                        configList = line.split(' -')
                        configList = [configList[0]] + ['-' + item for item in configList[1:]]
                        # Remove unnecessary blanks and newlines
                        for i, item in enumerate(configList):
                            configList[i] = configList[i].strip()
                        driveList.append(configList[0])
                        del configList[0]

                self.driveList = driveList
                self.configList = configList
            except Exception as e:
                msg = "Cannot read in config file [ " + self.smartConfFile + "]."
                logger.error(msg)
                logger.debug(e)
                sg.PopupError(msg)
                raise Exception

            try:
                fileHandle.close()
                return True
            except Exception as e:
                logger.error("Cannot close file [" + self.smartConfFile + "] after reading.")
                logger.debug(e)
        return True

    def writeSmartdConfFile(self):
        try:
            fileHandle = open(self.smartConfFile, 'w')
        except Exception as e:
            msg = "Cannot open config file [ " + self.smartConfFile + "] for writing. Permissions denied."
            logger.error(msg)
            logger.debug(e)
            sg.PopupError(msg)
            raise Exception

        try:
            fileHandle.write('# This file was generated on ' + str(
                datetime.now()) + ' by ' + APP_NAME + ' ' + APP_VERSION + ' - http://www.netpower.fr\n')
            for drive in self.driveList:
                line = drive
                for arg in self.configList:
                    line += " " + arg
                fileHandle.write(line + "\n")
        except Exception as e:
            msg = "Cannot write config file [ " + self.smartConfFile + "]."
            logger.error(msg)
            logger.debug(e)
            sg.PopupError(msg)
            raise Exception

        try:
            fileHandle.close()
        except Exception as e:
            logger.error("Cannot close file [" + self.smartConfFile + "] after writing.")
            logger.debug(e)

        return True

class MainGui:
    def __init__(self, config):

        self.config = config

        #Colors
        self.enabledGreen = '#CCFFCC'
        self.disabledGrey = '#CCCCCC'

        self.days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        self.hours = ["%.2d" % i for i in range(24)]
        self.temperatureCelsius = ["%.2d" % i for i in range(99)]
        self.energyModes = ['never', 'sleep', 'standby', 'idle']
        self.testTypes = ['long', 'short']

        # Gui parameter mapping
        self.healthParameterMap = [('-H', 'Check SMART health'),
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

        self.temperatureParameterMap = [('-I 194', 'Ignore temperature changes'),
                                 ('-W', 'Report temperature changes with values :'),
                        ]

        self.manualDriveListTooltip = 'Even under Windows, smartd addresses disks as \'/dev/sda /dev/sdb ... /dev/sdX\'\n' \
                                 'Intel raid drives are addresses as /dev/csmiX,Y where X is the controller number\n' \
                                 'and Y is the drive number. See smartd documentation for more.\n' \
                                 'Example working config:\n'\
                                 '\n'\
                                 '/dev/sda\n'\
                                 '/dev/sdb\n'\
                                 '/dev/csmi0,1'
        self.infoImage = b'R0lGODlhFAAUAPcAAAAAAAEBAQICAgMDAwYGBggICAkJCQoKCgwMDA4ODhAQEBQUFBoaGhsbGxwcHB0dHR4eHh8fHyAgICEhISIiIiMjIyYmJioqKi4uLjIyMjU1NTg4OEVFRU5OTk9PT1BQUFJSUlRUVFVVVVZWVldXV1hYWGBgYGdnZ2lpaWpqamxsbG1tbW5ubm9vb3h4eAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACH5BAEAAP8ALAAAAAAUABQAAAifAP8JHPhvBAUDBiiMIMhwYIQAECNChNBQYAuJGCOuYHgxo8eNAzEeINgBo0OT/y4wELhB4gOBGQUKCBBS4j8SGQssgCjQBcYQFTxCxCBwAkYJBoQOEMghI4GkHkH8y+CRAAWhJlgIjSBCqNcAUj0qEAgV5YOMKgSWyNigpkQNAi3EHJgiYwIEGU8wRPEVot6KDYSurEjwg4MBAxx4qBgQADs=\n'

        self.spacerTweak = [sg.T(' ' * 702, font=('Helvetica', 1))]
        self.buttonSpacer = sg.T(' ' * 10, font=('Helvetica', 1))

        self.gui()

    def gui(self):
        headCol =[[sg.Text(APP_DESCRIPTION)],
                  [sg.Frame('Configuration file', [[sg.InputText(self.config.smartConfFile, key='smartConfFile', enable_events=True, do_not_clear=True, size=(90, 1)), self.buttonSpacer, sg.FileBrowse(target='smartConfFile')],
                                                   self.spacerTweak,
                                                   ])],
                 ]

        driveSelection = [[sg.Radio('Automatic', group_id='driveDetection', key='driveAuto', enable_events=True)],
                          [sg.Radio('Manual drive list', group_id='driveDetection', key='driveManual', enable_events=True, tooltip = self.manualDriveListTooltip), sg.Image(data=self.infoImage, key='manualDriveListTooltip', enable_events=True)]
                         ]
        driveList = [[sg.Multiline(size=(60,6), key='driveList', do_not_clear=True, background_color=self.disabledGrey)]]
        driveConfig = [[sg.Frame('Drive detection', [[sg.Column(driveSelection), sg.Column(driveList)],
                                                     self.spacerTweak,
                                                     ])]]


        # Long self-tests
        longTestTime = [[sg.T('Schedule a long test at '), sg.InputCombo(self.hours, key='longTestHour'), sg.T('H every')]]
        longTestDays = []
        for i in range(0, 7):
            key = 'longDay' + self.days[i]
            longTestDays.append(sg.Checkbox(self.days[i], key=key))
        longTestDays=[longTestDays]
        longTests = [[sg.Frame('Scheduled long self-tests', [[sg.Column(longTestTime)],
                                                             [sg.Column(longTestDays)],
                                                             self.spacerTweakF(343),
                                                    ])]]

        # Short self-tests
        shortTestTime = [[sg.T('Schedule a short test at '), sg.InputCombo(self.hours, key='shortTestHour'), sg.T('H every')]]
        shortTestDays = []
        for i in range(0, 7):
            key = 'shortDay' + self.days[i]
            shortTestDays.append(sg.Checkbox(self.days[i], key=key))
        shortTestDays=[shortTestDays]
        shortTests =[[sg.Frame('Scheduled short self-tests', [[sg.Column(shortTestTime)],
                                                              [sg.Column(shortTestDays)],
                                                              self.spacerTweakF(343),
                                                    ])]]

        # Attribute checks
        count = 1
        smartHealthCol1 = []
        smartHealthCol2 = []
        for key, description in self.healthParameterMap:
            if count <= 6:
                smartHealthCol1.append([sg.Checkbox(description + ' (' + key +')', key=key)])
            else:
                smartHealthCol2.append([sg.Checkbox(description + ' (' + key + ')', key=key)])
            count += 1

        attributesCheck = [[sg.Frame('Smart health Checks', [[sg.Column(smartHealthCol1), sg.Column(smartHealthCol2)],
                                                             self.spacerTweak,
                                                             ] ) ]]

        # Temperature checks
        temperatureCheck = []
        for key, description in self.temperatureParameterMap:
            temperatureCheck.append([sg.Checkbox(description + ' (' + key + ')', key=key)])
        temperaturesOptions = [[sg.Frame('Temperature settings',
                                         [[sg.Column(temperatureCheck),
                                           sg.Column([[sg.T('Temperature difference since last report')],
                                                      [sg.T('Info log when temperature reached')],
                                                      [sg.T('Critical log when temperature reached')],
                                                      ]),
                                           sg.Column([[sg.InputCombo(self.temperatureCelsius, key='tempDiff', default_value='20')],
                                                      [sg.InputCombo(self.temperatureCelsius, key='tempInfo', default_value='55')],
                                                      [sg.InputCombo(self.temperatureCelsius, key='tempCrit', default_value='60')],
                                                      ]),

                                           ],
                                           self.spacerTweak,
                                           ],
                                         )]]

        # Energy saving
        energyText = [[sg.T('Do not execute smart tests when disk energy mode is ')],
                      [sg.T('Force test execution after N skipped tests')],
                     ]
        energyChoices = [[sg.InputCombo(self.energyModes, key='energyMode')],
                         [sg.InputCombo(["%.1d" % i for i in range(8)], key='energySkips')],
                        ]
        energyOptions = [[sg.Frame('Energy saving', [[sg.Column(energyText), sg.Column(energyChoices)],
                                                     self.spacerTweak,
                                                     ] ) ]]

        # Email options
        alerts = [[sg.Radio('Use system mail command to send alerts to the following addresses (comma separated list) on Linux', group_id='alerts', key='useMailer', default=False, enable_events=True)],
                  [sg.InputText(key='mailAddresses', size=(98,1), do_not_clear=True)],
                  [sg.Radio('Use the following external alert handling script (erroraction.cmd in smartmontools-win)', group_id='alerts', key='useExternalScript', default=True, enable_events=True)],
                  [sg.InputText(key='externalScriptPath', size=(90,1),  do_not_clear=True), sg.FileBrowse()],
                  ]
        alertOptions = [[sg.Frame('Alert actions', [[sg.Column(alerts)],
                                                    self.spacerTweak,
                                                    ]) ]]

        # Supplementary options
        supOptionsCol = [[sg.InputText(key='supplementaryOptions', size=(98,1), do_not_clear=True)]]

        supOptions = [[sg.Frame('Supplementary smartd options', [[sg.Column(supOptionsCol)],
                                                          self.spacerTweak,
                                                           ] ) ]]

        fullLayout = [
                     [sg.Column(headCol)],
                     [sg.Column(driveConfig)],
                     [sg.Column(longTests), sg.Column(shortTests)],
                     [sg.Column(attributesCheck)],
                     [sg.Column(temperaturesOptions)],
                     [sg.Column(energyOptions)],
                     [sg.Column(alertOptions)],
                     [sg.Column(supOptions)],
                    ]

        layout = [[sg.Column(fullLayout, scrollable=True, vertical_scroll_only=True, size=(722, 550))],
                  [sg.T('')],
                  [sg.T(' ' * 70), sg.Button('Save changes'), self.buttonSpacer, sg.Button('Reload smartd service'), self.buttonSpacer, sg.Button('Exit')]
                  ]

        # Display the Window and get values

        try:
            self.window = sg.Window(APP_NAME + ' - ' + APP_VERSION + ' ' + APP_BUILD, icon=ICON_FILE, resizable=True, size=(750, 600),
                           text_justification='left').Layout(layout)
        except Exception as e:
            logger.critical(e)
            sys.exit(1)

        # Finalize window before Update functions can work
        self.window.Finalize()

        # Set defaults
        if platform.system() == 'Windows':
            self.window.FindElement('useExternalScript').Update(True)
            self.window.FindElement('mailAddresses').Update(disabled=True)
            self.window.FindElement('externalScriptPath').Update(disabled=False)
        else:
            self.window.FindElement('useMailer').Update(True)
            self.window.FindElement('mailAddresses').Update(disabled=False)
            self.window.FindElement('externalScriptPath').Update(disabled=False)

        self.UpdateGUIConfig()

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
                    self.serviceReload()
            elif event == 'Save changes':
                try:
                    self.getGUIConfig(values)
                    self.config.writeSmartdConfFile()
                except:
                    sg.PopupError('Cannot save configuration', icon=None)
                else:
                    sg.Popup('Changes saved to configuration file')
            elif event == 'driveAuto':
                self.window.FindElement('driveList').Update(disabled=True, background_color=self.disabledGrey)
            elif event == 'driveManual':
                self.window.FindElement('driveList').Update(disabled=False, background_color=self.enabledGreen)
            elif event == 'useMailer' or event == 'useExternalScript':
                if values['useMailer'] == True:
                    self.window.FindElement('mailAddresses').Update(disabled=False)
                    self.window.FindElement('externalScriptPath').Update(disabled=True)
                if values['useExternalScript'] == True:
                    self.window.FindElement('mailAddresses').Update(disabled=True)
                    self.window.FindElement('externalScriptPath').Update(disabled=False)
            elif event == 'smartConfFile':
                self.config.smartConfFile = values['smartConfFile']
            elif event == 'manualDriveListTooltip':
                sg.Popup(self.manualDriveListTooltip)


    def spacerTweakF(self, pixels=10):
        return [sg.T(' ' * pixels, font=('Helvetica', 1))]

    def UpdateGUIConfig(self):
        # Apply drive config
        if self.config.driveList == ['DEVICESCAN']:
            self.window.FindElement('driveAuto').Update(True)
        else:
            self.window.FindElement('driveManual').Update(True)
            for drive in self.config.driveList:
                drives = drive + '\n'
                self.window.FindElement('driveList').Update(drives)

        # Self test regex GUI setup
        if '-s' in '\t'.join(self.config.configList):
            for i, item in enumerate(self.config.configList):
                if '-s' in item:
                    index = i

            # TODO: Add other regex parameter here (group 1 & 2 missing)
            longTest = re.search('L/(.+?)/(.+?)/(.+?)/([0-9]*)', self.config.configList[index])
            if longTest:
                # print(longTest.group(1))
                # print(longTest.group(2))
                # print(longTest.group(3))
                if longTest.group(3):
                    dayList = list(longTest.group(3))
                    # Handle special case where . means all
                    if dayList[0] == '.':
                        for day in range(0, 7):
                            self.window.FindElement('longDay' + self.days[day]).Update(True)
                    else:
                        for day in dayList:
                            if day.strip("[]").isdigit():
                                self.window.FindElement('longDay' + self.days[int(day.strip("[]")) - 1]).Update(True)
                if longTest.group(4):
                    self.window.FindElement('longTestHour').Update(longTest.group(4))

            shortTest = re.search('S/(.+?)/(.+?)/(.+?)/([0-9]*)', self.config.configList[index])
            if shortTest:
                # print(shortTest.group(1))
                # print(shortTest.group(2))
                if shortTest.group(3):
                    dayList = list(shortTest.group(3))
                    # Handle special case where . means all
                    if dayList[0] == '.':
                        for day in range(0, 7):
                            self.window.FindElement('shortDay' + self.days[day]).Update(True)
                    else:
                        for day in dayList:
                            if day.strip("[]").isdigit():
                                self.window.FindElement('shortDay' + self.days[int(day.strip("[]")) - 1]).Update(True)
                if shortTest.group(4):
                    self.window.FindElement('shortTestHour').Update(shortTest.group(4))


        # Attribute checks GUI setup
        for key, value in self.healthParameterMap:
            if key in self.config.configList:
                self.window.FindElement(key).Update(True)
                # Handle specific dependancy cases (-C 197+ depends on -C 197 and -U 198+ depends on -U 198)
                if key == '-C 197+':
                    self.window.FindElement('-C 197').Update(True)
                elif key == '-U 198+':
                    self.window.FindElement('-U 198').Update(True)

        # Handle temperature specific cases
        for i, item in enumerate(self.config.configList):
            if re.match(r'^-W [0-9]{1,2},[0-9]{1,2},[0-9]{1,2}$', item):
                self.window.FindElement('-W').Update(True)
                self.window.FindElement('-I 194').Update(False)
                temperatures = item.split(' ')[1]
                temperatures = temperatures.split(',')
                self.window.FindElement('tempDiff').Update(temperatures[0])
                self.window.FindElement('tempInfo').Update(temperatures[1])
                self.window.FindElement('tempCrit').Update(temperatures[2])

        # Energy saving GUI setup
        if '-n' in '\t'.join(self.config.configList):
            for i, item in enumerate(self.config.configList):
                if '-n' in item:
                    index = i

            energySaving = self.config.configList[index].split(',')
            for mode in self.energyModes:
                if mode in energySaving[0]:
                    self.window.FindElement('energyMode').Update(mode)

            if energySaving[1].isdigit():
                self.window.FindElement('energySkips').Update(energySaving[1])
        # if energySaving[1] == 'q':
        # TODO: handle q parameter

        # Get alert options
        if '-m' in '\t'.join(self.config.configList):
            for i, item in enumerate(self.config.configList):
                if '-m' in item:
                    index = i

            mailAddresses = self.config.configList[index].replace('-m ', '', 1)
            self.window.FindElement('useMailer').Update(True)
            if not mailAddresses == '<nomailer>':
                self.window.FindElement('mailAddresses').Update(mailAddresses, disabled=False)
            self.window.FindElement('externalScriptPath').Update(disabled=True)
        else:
            self.window.FindElement('useExternalScript').Update(True)

        if '-M' in '\t'.join(self.config.configList):
            for i, item in enumerate(self.config.configList):
                if '-M' in item:
                    index = i

            self.window.FindElement('useExternalScript').Update(True)
            self.window.FindElement('mailAddresses').Update(disabled=True)
            self.window.FindElement('externalScriptPath').Update(self.config.configList[index].replace('-M exec ', '', 1), disabled=False)
        else:
            self.window.FindElement('useMailer').Update(True)
            self.window.FindElement('mailAddresses').Update(disabled=False)

    def getGUIConfig(self, values):
        driveList = []
        configList = []


        if values['driveAuto'] == True:
            driveList.append('DEVICESCAN')
        else:
            driveList = values['driveList'].split()

            # TODO: better bogus pattern detection
            # TODO: needs to raise exception

            if driveList == []:
                msg = "Drive list is empty"
                logger.error(msg)
                sg.PopupError(msg)
                return False

            if "example" in driveList or "exemple" in driveList:
                msg = "Drive list contains example !!!"
                logger.error(msg)
                sg.PopupError(msg)
                return False

            for item in driveList:
                if not item[0] == "/":
                    msg = "Drive list doesn't start with slash [" + item + "]."
                    logger.error(msg)
                    sg.PopupError(msg)
                    return False

        # smartd health parameters
        try:
            for key, description in self.healthParameterMap:
                if values[key]:
                    # Handle dependancies
                    if key == '-C 197+':
                        if '-C 197' in configList:
                            for (i, item) in enumerate(configList):
                                if item == '-C 197':
                                    configList[i] = '-C 197+'
                        else:
                            configList.append(key)
                    elif key == '-U 198+':
                        if '-U 198' in configList:
                            for (i, item) in enumerate(configList):
                                if item == '-U 198':
                                    configList[i] = '-U 198+'
                        else:
                            configList.append(key)
                    else:
                        configList.append(key)

        except Exception as e:
            msg = "Bogus configuration in [" + key + "]."
            logger.error(msg)
            logger.debug(e)
            logger.debug(configList)
            sg.PopupError(msg)

        try:
            for key, description in self.temperatureParameterMap:
                if values[key]:
                    if key == '-W':
                        configList.append(key + ' ' + str(values['tempDiff']) + ',' + str(values['tempInfo']) + ',' + str(values['tempCrit']))
                    elif key == '-I 194':
                        configList.append(key)
        except Exception as e:
            msg = "Bogus configuration in [" + key + "] and temperatures."
            logger.error(msg)
            logger.debug(e)
            logger.debug(configList)
            sg.PopupError(msg)

        try:
            energyMode = values['energyMode']
            if energyMode in self.energyModes:
                energyLine = '-n ' + energyMode
            skipTests = values['energySkips']
            try:
                energyLine += ',' + str(skipTests)
            except:
                pass

            # TODO: handle -q parameter in GUI
            try:
                energyLine += ',q'
            except:
                pass

            try:
                energyLine
            except:
                pass
            else:
                configList.append(energyLine)
        except Exception as e:
            msg = 'Energy config error'
            logger.error(msg)
            logger.debug(e)
            sg.PopupError(msg)

        # Transforms selftest checkboxes into long / short tests expression for smartd
        # Still not a good implementation after the Inno Setup ugly implementation
        try:
            for testType in self.testTypes:
                regex = "["
                present = False

                for day in self.days:
                    if values[testType + 'Day' + day] == True:
                        regex += str(self.days.index(day) + 1)
                        present = True
                regex += "]"
                # regex = regex.rstrip(',')

                longTestHour = values['longTestHour']
                shortTestHour = values['shortTestHour']

                if testType == self.testTypes[0] and present == True:
                    longRegex = "L/../../" + regex + "/" + str(longTestHour)
                elif testType == self.testTypes[1] and present == True:
                    shortRegex = "S/../../" + regex + "/" + str(shortTestHour)

            if ('longRegex' in locals()) and ('shortRegex' in locals()):
                testsRegex = "-s (" + longRegex + "|" + shortRegex + ")"
            elif 'longRegex' in locals():
                testsRegex = "-s " + longRegex
            elif 'shortRegex' in locals():
                testsRegex = "-s " + shortRegex

            try:
                configList.append(testsRegex)
            except:
                pass

        except Exception as e:
            msg = 'Test regex creation error'
            logger.error(msg)
            logger.debug(e)
            sg.PopupError(msg)

        # TODO: -M can't exist without -m
        # Mailer options
        if values['useMailer'] == True:
            mailAddresses = values['mailAddresses']
            if len(mailAddresses) > 0:
                configList.append('-m ' + mailAddresses)
            else:
                msg = 'Missing mail addresses'
                logger.error(msg)
                sg.PopupError(msg)
                raise AttributeError
        else:
            configList.append('-m <nomailer>')
            externalScriptPath = values['externalScriptPath']
            externalScriptPath = externalScriptPath.strip('\"\'')
            if not externalScriptPath == "":
                externalScriptPath = '"' + externalScriptPath + '"'
                configList.append('-M exec ' + externalScriptPath)

        logger.debug(driveList)
        logger.debug(configList)
        self.config.driveList=driveList
        self.config.configList=configList

    def serviceReload(self):
        try:
            serviceHandler(SMARTD_SERVICE_NAME, "restart")
        except Exception as e:
            msg = "Cannot restart [" + SMARTD_SERVICE_NAME + "]. Running as admin ? See logs for details."
            logger.error(msg)
            logger.debug(e)
            sg.PopupError(msg)
            return False
        else:
            sg.Popup('Successfully reloaded smartd service.', title='Info')

def commandRunner(command, validExitCodes=[]):
    """
    Runs system command, returns exit code and logs output on error
    validExitCodes is a list of codes that don't trigger an error
    """
    try:
        output = subprocess.check_output(command, stderr=subprocess.STDOUT, shell=True , timeout=3, universal_newlines=True)
    except subprocess.CalledProcessError as e:
        exitCode = e.returncode
        if exitCode in validExitCodes:
            logger.debug('Command [' + command + '] returned with exit code [0]. Command output was:')
            logger.debug(e.output)
            return e.returncode
        else:
            logger.error('Command [' + command + '] failed with exit code [' + str(e.returncode) + ']. Command output was:')
            logger.error(e.output)
            return e.returncode
    else:
        logger.debug('Command [' + command + '] returned with exit code [0]. Command output was:')
        logger.debug(output)
        return 0

def serviceHandler(service, action):
    """Handle Windows / Unix services
    Valid actions are start, stop, restart, status
    Returns True if action succeeded or service is running, False if service does not run
    """

    msgAlreadyRunning = "Service [" + service + "] already running."
    msgNotRunning = "Service [" + service + "] is not running."
    msgAction = "Action " + action + " for service [" + service + "]."
    msgSuccess = "Action " + action + " succeeded."
    msgFailure = "Action " + action + " failed."

    if platform.system() == "Windows":
        # Returns list. If second entry = 4, service is running
        # TODO: handle other service states than 4
        serviceStatus = win32serviceutil.QueryServiceStatus(service)
        if serviceStatus[1] == 4:
            isRunning = True
        else:
            isRunning = False

        if action == "start":
            if isRunning:
                logger.info(msgAlreadyRunning)
                return True
            else:
                logger.info(msgAction)
                try:
                    win32serviceutil.StartService(service)
                    logger.info(msgSuccess)
                    return True
                except Exception as e:
                    logger.error(msgFailure)
                    # str conversion needed from pywintypes.error for logger
                    logger.debug(str(e).encode('utf-8'))
                    raise Exception

        elif action == "stop":
            if not isRunning:
                logger.info(msgNotRunning)
                return True
            else:
                logger.info(msgAction)
                try:
                    win32serviceutil.StopService(service)
                    logger.info(msgSuccess)
                    return True
                except Exception as e:
                    logger.error(msgFailure)
                    logger.debug(str(e).encode('utf-8'))
                    raise Exception

        elif action == "restart":
            serviceHandler(service, 'stop')
            time.sleep(1)
            serviceHandler(service, 'start')

        elif action == "status":
            return isRunning

    else:
        # Using lsb service X command on Unix variants, hopefully the most portable

        #serviceStatus = os.system("service " + service + " status > /dev/null 2>&1")

        # Valid exit code are 0 and 3 (because of systemctl using a service redirect)
        serviceStatus = commandRunner('service ' + service + ' status')
        if serviceStatus == 0:
            isRunning = True
        else:
            isRunning = False

        if action == "start":
            if isRunning:
                logger.info(msgAlreadyRunning)
                return True
            else:
                logger.info(msgAction)
                try:
                    #result = os.system('service ' + service + ' start > /dev/null 2>&1')
                    result = commandRunner('service ' + service + ' start')
                    if result == 0:
                        logger.info(msgSuccess)
                        return True
                    else:
                        logger.error('Could not start service, code [' + str(result) + '].')
                        raise Exception
                except Exception as e:
                    logger.info(msgFailure)
                    logger.debug(e)
                    raise Exception

        elif action == "stop":
            if not isRunning:
                logger.info(msgNotRunning)
            else:
                logger.info(msgAction)
                try:
                    #result = os.system('service ' + service + ' stop > /dev/null 2>&1')
                    result = commandRunner('service ' + service + ' stop')
                    if result == 0:
                        logger.info(msgSuccess)
                        return True
                    else:
                        logger.error('Could not start service, code [' + str(result) + '].')
                        raise Exception
                except Exception as e:
                    logger.error(msgFailure)
                    logger.debug(e)
                    raise Exception

        elif action == "restart":
            serviceHandler(service, 'stop')
            serviceHandler(service, 'start')

        elif action == "status":
            return isRunning

def main(argv):
    if IS_STABLE == False:
        logger.warning("Warning: This is an unstable developpment version.")


    config = Configuration()

    try:
        config.readSmartdConfFile()
        logger.debug(str(config.driveList))
        logger.debug(str(config.configList))
    except Exception as e:
        logger.info("Using default configuration")

    try:
        gui = MainGui(config)
    except Exception as e:
        logger.critical("Cannot instanciate main app.")
        logger.debug(e)
        traceback.print_exc()
        sys.exit(1)


# Improved answer I have done in https://stackoverflow.com/a/49759083/2635443
def is_admin():
    if _DEBUG == True: #TODO #WIP
        return True

    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except Exception as e:
        logger.critical("Cannot get admin privileges.")
        logger.debug(e)
        raise Exception


if __name__ == '__main__':

    logger.info("Running on python " + platform.python_version() + " / " + str(platform.uname()))

    if platform.system() == "Windows":
        if is_admin():
            # Detect if running frozen version, where one more argument exists (filename)
            if getattr(sys, "frozen", False):
                main(sys.argv[2:])
            else:
                main(sys.argv[1:])
        else:
            # Re-run the program with admin rights, don't use __file__ since py2exe won't know about it
            # Use sys.argv[0] as script path and sys.argv[1:] as arguments, join them as lpstr, quoting each parameter or spaces will divide parameters
            # lpParameters = sys.argv[0] + " "
            lpParameters = ""
            for i, item in enumerate(sys.argv[0:]):
                lpParameters += '"' + item + '" '
            try:
                # See https://docs.microsoft.com/en-us/windows/desktop/api/shellapi/nf-shellapi-shellexecutew
                # int 0 means SH_HIDE window, 1 is SW_SHOWNORMAL
                ctypes.windll.shell32.ShellExecuteW(None, 'runas', sys.executable, lpParameters, None, 0)

            except Exception as e:
                logger.critical(e)
                print('Unable to request UAC elevation. %s' % e)
                sys.exit(1)
    else:
        main(sys.argv[1:])
