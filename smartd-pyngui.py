#!/usr/bin/env python
# -*- coding: utf-8 -*-

#### BASIC FUNCTIONS & DEFINITIONS #########################################################################

class Constants:
	"""Simple class to use constants
	usage
	_CONST = Constants
	print(_CONST.NAME)
	"""
	APP_NAME="smartd-pyngui" # Stands for smart daemon python native gui
	APP_VERSION="0.2"
	APP_BUILD="2016110801"
	APP_DESCRIPTION="smartd v5.4+ daemon config utility"
	CONTACT="ozy@netpower.fr - http://www.netpower.fr"
	AUTHOR="Orsiris de Jong"

	IS_STABLE=False

	LOG_FILE=APP_NAME + ".log"

	SMARTD_SERVICE_NAME="smartd"
	SMARTD_CONF_FILENAME="smartd.conf"

	DEFAULT_UNIX_PATH="/etc/smartd"

	def __setattr__(self, *_):
		pass

_CONSTANT = Constants

#### LOGGING & DEBUG CODE ####################################################################################

import logging
from logging.handlers import RotatingFileHandler

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

# Set file log
logFileHandler = RotatingFileHandler(_CONSTANT.LOG_FILE, mode='a', encoding='utf-8', maxBytes=1000000, backupCount=1)
logFileHandler.setLevel(logging.DEBUG)
logFileHandler.setFormatter(logging.Formatter('%(asctime)s :: %(levelname)s :: %(message)s'))
logger.addHandler(logFileHandler)

# Set stdout log
logStdoutHandler = logging.StreamHandler()
logStdoutHandler.setLevel(logging.DEBUG) #TODO: Replace with logging.ERROR in production env
logger.addHandler(logStdoutHandler)

#### IMPORTS ################################################################################################

import sys, getopt
import os
import platform					# Detect OS
import re						# Regex handling
import time						# sleep command
import codecs					# unicode encoding

from datetime import datetime

# GUI
try:
	import tkinter as tk		# Python 3
	from tkinter import messagebox
except:
	logger.debug("Could not import tkinter for python3, trying Tkinter from python2")
	import Tkinter as tk		# Python 2
	import tkMessageBox as messagebox

try:
	import pygubu					# GUI builder
except:
	logger.critical("Cannot find pygubu module. Try installing it with python -m pip install pygubu")
	sys.exit(1)

# py2exe fails with win32serviceutil, nuitka does not
if platform.system() == "Windows":
	import win32serviceutil
	import win32service

logger.info("Running on python " + platform.python_version() + " / " + str(platform.uname()))

#### ACTUAL APPLICATION ######################################################################################

CONFIG = 0 # Contains full config as Configuration class

class Configuration:
	smartConfFile = ""

	def __init__(self, filePath = ''):
		"""Determine smartd configuration file path"""

		# __file__ variable doesn't exist in frozen py2exe mode, get appRoot
		try:
			self.appRoot = os.path.dirname(os.path.abspath(__file__))
		except:
			self.appRoot = os.path.dirname(os.path.abspath(sys.argv[0]))

		if len(filePath) > 0:
			self.smartConfFile = filePath
			if not os.path.isfile(self.smartConfFile):
				logger.info("Using new file [" + self.smartConfFile + "].")
		else:
			if platform.system() == "Windows":
				# Get program files environment
				try:
					programFilesX86=os.environ["ProgramFiles(x86)"]
				except:
					programFilesX86=os.environ["ProgramFiles"]

				try:
					programFilesX64=os.environ["ProgramW6432"]
				except:
					programFilesX64=os.environ["ProgramFiles"]

				if os.path.isfile(self.appRoot + os.sep + _CONSTANT.SMARTD_CONF_FILENAME):
					self.smartConfFile = self.appRoot + os.sep + _CONSTANT.SMARTD_CONF_FILENAME
				elif os.path.isfile(programFilesX64 + os.sep + "smartmontools for Windows" + os.sep + "bin" + os.sep + _CONSTANT.SMARTD_CONF_FILENAME):
					self.smartConfFile = programFilesX64 + os.sep + "smartmontools for Windows" + os.sep + "bin" + os.sep + _CONSTANT.SMARTD_CONF_FILENAME
				elif os.path.isfile(programFilesX86 + os.sep + "smartmontools for Windows" + os.sep + "bin" + os.sep + _CONSTANT.SMARTD_CONF_FILENAME):
					self.smartConfFile = programFilesX86 + os.sep + "smartmontools for Windows" + os.sep + "bin" + os.sep + _CONSTANT.SMARTD_CONF_FILENAME
				elif os.path.isfile(programFilesX64 + os.sep + "smartmontools" + os.sep + "bin" + os.sep + _CONSTANT.SMARTD_CONF_FILENAME):
					self.smartConfFile = programFilesX64 + os.sep + "smartmontools" + os.sep + "bin" + os.sep + _CONSTANT.SMARTD_CONF_FILENAME
				elif os.path.isfile(programFilesX86 + os.sep + "smartmontools" + os.sep + "bin" + os.sep + _CONSTANT.SMARTD_CONF_FILENAME):
					self.smartConfFile = programFilesX86 + os.sep + "smartmontools" + os.sep + "bin" + os.sep + _CONSTANT.SMARTD_CONF_FILENAME
			else:
				if os.path.isfile(self.appRoot + os.sep + _CONSTANT.SMARTD_CONF_FILENAME):
					self.smartConfFile = self.appRoot + os.sep + _CONSTANT.SMARTD_CONF_FILENAME
				elif os.path.isfile("/etc/smartmontools" + os.sep + _CONSTANT.SMARTD_CONF_FILENAME):
					self.smartConfFile = "/etc/smartmontools" + os.sep + _CONSTANT.SMARTD_CONF_FILENAME
				elif os.path.isfile("/etc/smartd" + os.sep + _CONSTANT.SMARTD_CONF_FILENAME):
					self.smartConfFile = "etc/smartd" + os.sep + _CONSTANT.SMARTD_CONF_FILENAME
				elif os.path.isfile("/etc" + os.sep + _CONSTANT.SMARTD_CONF_FILENAME):
					self.smartConfFile = "/etc" + os.sep + _CONSTANT.SMARTD_CONF_FILENAME

		if len(self.smartConfFile) == 0:
			self.smartConfFile = self.appRoot + os.sep + _CONSTANT.SMARTD_CONF_FILENAME
		else:
			if len(filePath) == 0:
				logger.debug("Found configuration file in [" + self.smartConfFile + "].")

class Application:
	"""pygubu tkinter GUI class"""

	# Standard definitions
	days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
	testTypes = ['Long', 'Short']
	energyModes = ['never', 'sleep', 'standby', 'idle']

	# Set defaults
	driveList = ['DEVICESCAN']
	configList = ['-H', '-C 197+', '-l error', '-U 198+', '-l selftest', '-t', '-f', '-I 194', '-n sleep,7', '-s (L/../../4/13|S/../../0,1,2,3,4,5,6/10)']
	testsRegex=""

	# Gui parameter mapping
	parameterMap = [('-H', 'CheckSmartHealth'), 
					('-C 197+', 'ReportNonZeroCurrentPendingSectors'),
					('-l error', 'ReportATAErrorIncrease'),
					('-U 198+', 'ReportOfflineUncorrectableSectorsIncrease'),
					('-l selftest', 'ReportSelftestErrorIncrease'),
					('-t', 'TrackUsageAndPrefailAttributesChanges'),
					('-f', 'CheckUsageAttributesFailures'),
					('-I 194', 'IgnoreTemperatureChanges')
	]

	def __init__(self, master):
		self.master = master
		self.builder = builder = pygubu.Builder()

		# Load GUI xml description file
		filePath = os.path.join(CONFIG.appRoot, _CONSTANT.APP_NAME + ".ui")
		try:
			self.builder.add_from_file(filePath)
		except Exception as e:
			logger.critical("Cannot find ui file [" + filePath + "].")
			logger.debug(e)
			sys.exit(1)

		self.mainwindow = builder.get_object('MainFrame', master)

		# Bind GUI actions to functions
		self.builder.connect_callbacks(self)
		callbacks = {
			'enableAutoDetection': self.enableAutoDetection,
			'disableAutoDetection': self.disableAutoDetection,
			'enableInternalMailer': self.enableInternalMailer,
			'disableInternalMailer': self.disableInternalMailer,
			'onSubmit': self.onSubmit,
			'onExit': self.onExit
		}
		self.builder.connect_callbacks(callbacks)

		try:
			self.driveList, self.configList = readSmartdConfFile(CONFIG.smartConfFile)
		except Exception as e:
			logger.info("Using default configuration")

		logger.debug("Drive list: " + str(self.driveList))
		logger.debug("Config list: " + str(self.configList))

		self.builder.get_object('Title', master).config(text = _CONSTANT.APP_NAME + " v" +  _CONSTANT.APP_VERSION + " - " + _CONSTANT.APP_DESCRIPTION)

		# Set name of the used configuration file
		self.builder.get_variable('configFilePath').set(CONFIG.smartConfFile)

		self.applyConfigToGui()

	def applyConfigToGui(self):
		# Apply config to GUI
		if "DEVICESCAN" in self.driveList[0]:
			self.builder.get_object('AutoDetectDrives', self.master).select()
			self.builder.get_object('ManualDriveList', self.master)['background'] = "#aaaaaa"
		else:
			self.builder.get_object('ManualDetectDrives', self.master).select()
			self.builder.get_object('ManualDriveList', self.master)['background'] = "#aaffaa"
			self.builder.get_object('ManualDriveList', self.master).delete("1.0", "end")
			for drive in self.driveList:
				self.builder.get_object('ManualDriveList', self.master).insert("end", drive + "\n")

		# Self test regex GUI setup
		if '-s' in '\t'.join(self.configList):
			for i, item in enumerate(self.configList):
				if '-s' in item:
					index = i

			#TODO: Add other regex parameter here (group 1 & 2 missing)
			longTest = re.search('L/(.+?)/(.+?)/(.+?)/([0-9]*)', self.configList[index])
			if longTest:
				#print(longTest.group(1))
				#print(longTest.group(2))
				if longTest.group(3):
					dayList = longTest.group(3).split(',')
					#Handle special case where . means all
					if dayList[0] == '.':
						for day in range(0,7):
							self.builder.get_object('LongTest' + self.days[day], self.master).select()
					else:
						for day in dayList:
							if day.strip("[]").isdigit():
								self.builder.get_object('LongTest' + self.days[int(day.strip("[]"))], self.master).select()
				if longTest.group(4):
					self.builder.get_object('LongTestHour', self.master).set(longTest.group(4))

			shortTest = re.search('S/(.+?)/(.+?)/(.+?)/([0-9]*)', self.configList[index])
			if longTest:
				#print(shortTest.group(1))
				#print(shortTest.group(2))
				if shortTest.group(3):
					dayList = shortTest.group(3).split(',')
					#Handle special case where . means all
					if dayList[0] == '.':
						for day in range(0,7):
							self.builder.get_object('ShortTest' + self.days[day], self.master).select()
					else:
						for day in dayList:
							if day.strip("[]").isdigit():
								self.builder.get_object('ShortTest' + self.days[int(day.strip("[]]"))], self.master).select()
				if shortTest.group(4):
					self.builder.get_object('ShortTestHour', self.master).set(shortTest.group(4))

		# Attribute checks GUI setup
		for map in self.parameterMap:
			if map[0] in self.configList:
				self.builder.get_object(map[1], self.master).select()

		# Energy saving GUI setup
		if '-n' in '\t'.join(self.configList):
			for i, item in enumerate(self.configList):
				if '-n' in item:
					index = i

			energySaving = self.configList[index].split(',')
			for mode in self.energyModes:
				if mode in energySaving[0]:
					self.builder.get_object('DiskModeSkipTests', self.master).set(mode)

			if energySaving[1].isdigit():
				self.builder.get_object('SkipTestsNumber', self.master).set(energySaving[1])
			#if energySaving[1] == 'q':
			#TODO: handle q parameter

		#TODO: -m and -M are not exclusive
		# Get mail options
		if '-m' in '\t'.join(self.configList):
			for i, item in enumerate(self.configList):
				if '-m' in item:
					index = i

			if '<nomailer>' in self.configList[index]:
				try:
					if '-M exec' in self.configList[index + 1]:
						self.builder.get_object('ExternalMailer', self.master).select()
						self.builder.get_object('ExternalScript', self.master).delete("1.0", "end")
						self.builder.get_object('ExternalScript', self.master).insert("end", self.configList[index + 1].lstrip('-M exec '))
						self.builder.get_object('ExternalScript', self.master)['background'] = "#aaffaa"
						self.builder.get_object('DestinationMails', self.master)['background'] = "#aaaaaa"
				except:
					pass
			else:
				self.builder.get_object('InternalMailer', self.master).select()
				self.builder.get_object('DestinationMails', self.master).delete("1.0", "end")
				self.builder.get_object('DestinationMails', self.master).insert("end", self.configList[index].lstrip('-m '))
				self.builder.get_object('ExternalScript', self.master)['background'] = "#aaaaaa"
				self.builder.get_object('DestinationMails', self.master)['background'] = "#aaffaa"

	def enableAutoDetection(self):
		AutoDetect = self.builder.get_variable('AutoDetectDrives').get()
		if (AutoDetect == True):
			self.builder.get_object('ManualDriveList', self.master)['background'] = "#aaaaaa"

	def disableAutoDetection(self):
		AutoDetect = self.builder.get_variable('AutoDetectDrives').get()
		if (AutoDetect == False):
			self.builder.get_object('ManualDriveList', self.master)['background'] = "#aaffaa"

	def enableInternalMailer(self):
		if self.builder.get_variable('InternalMailer').get() == True:
			self.builder.get_object('ExternalScript', self.master)['background'] = "#aaaaaa"
			self.builder.get_object('DestinationMails', self.master)['background'] = "#aaffaa"

	def disableInternalMailer(self):
		if self.builder.get_variable('InternalMailer').get() == False:
			self.builder.get_object('ExternalScript', self.master)['background'] = "#aaffaa"
			self.builder.get_object('DestinationMails', self.master)['background'] = "#aaaaaa"

	def prepareDriveList(self):
		self.driveList=[]

		if self.builder.get_variable('AutoDetectDrives').get() == True:
			self.driveList.append('DEVICESCAN')
		else:
			self.driveList = self.builder.get_object('ManualDriveList', self.master).get("1.0", "end").strip().split()
		#TODO: better bogus pattern detection
		if "examples" in self.driveList:
			#raise TypeInfo
			#TODO doesn't trigger error
			msg="Drive list contains bogus info"
			logger.error(msg)
			messagebox.showinfo("Error", msg)
			return False

	def prepareTestRegex(self):
		"""Transforms checkboxes into long / short tests expression for smartd"""
		#Still not a good implementation after the Inno Setup ugly implementation

		for testType in self.testTypes:
			regex = ""
			present = False
			for day in self.days:
				if self.builder.get_variable(testType + 'Test' + day).get():
					regex += str(self.days.index(day)) + ","
					present = True
			regex = regex.rstrip(',')
			if testType == self.testTypes[0] and present == True:
				longRegex = "L/../../" + regex + "/" + str(self.builder.get_variable('LongTestHour').get())
			elif testType == self.testTypes[1] and present == True:
				shortRegex = "S/../../" + regex + "/" + str(self.builder.get_variable('ShortTestHour').get())

		if ('longRegex' in locals()) and ('shortRegex' in locals()):
			self.testsRegex = "-s (" + longRegex + "|" + shortRegex + ")"
		elif 'longRegex' in locals():
			self.testsRegex = "-s " + longRegex
		elif 'shortRegex' in locals():
			self.testsRegex = "-s " + shortRegex

	def prepareConfigList(self):
		"""Prepare a list of arguments for smartd.conf file"""
		self.configList=[]

		for map in self.parameterMap:
			if self.builder.get_variable(map[1]).get():
				self.configList.append(map[0])

		energyMode = self.builder.get_variable('DiskModeSkipTests').get()
		if energyMode in self.energyModes:
			energyLine = '-n ' + energyMode
		skipTests = self.builder.get_variable('SkipTestsNumber').get()
		try:
			energyLine += ',' + str(skipTests)
		except:
			pass

		#TODO: handle -q parameter in GUI
		try:
			energyLine += ',q'
		except:
			pass

		if 'energyLine' in locals():
			self.configList.append(energyLine)

		self.prepareTestRegex()
		self.configList.append(self.testsRegex)

		#TODO: -m root -M exec /some/path can work toghether
		# Mailer options
		if self.builder.get_variable('InternalMailer').get() == True:
			mails = self.builder.get_object('DestinationMails', self.master).get("1.0", "end")
			if (len(mails) > 0):
				self.configList.append('-m ' + mails)
			else:
				messagebox.showinfo('Error', 'Bogus destination mail list')
				return False
		else:
			script = self.builder.get_object('ExternalScript', self.master).get("1.0", "end")
			script = script.strip()
			try:
				if script[0] != '"':
					script = '"' + script
				if script[-1:] != '"':
					script += '"'
				self.configList.append('-m <nomailer> -M exec ' + script)
			except:
				pass

	def onSubmit(self):
		try:
			self.prepareDriveList()
			self.prepareConfigList()

			try:
				#print(serviceHandler(_CONSTANT.SMARTD_SERVICE_NAME, "status"))
				serviceHandler(_CONSTANT.SMARTD_SERVICE_NAME, "stop")
				writeSmartdConfFile(CONFIG.smartConfFile, self.driveList, self.configList)
				serviceHandler(_CONSTANT.SMARTD_SERVICE_NAME, "start")
			except Exception as e:
				msg="Guru meditation failure !"
				logger.error(msg)
				logger.debug(e)
				messagebox.showinfo("Error", msg)
		except Exception as e:
			msg="Cannot prepare DriveList or ConfigList"
			logger.error(msg)
			logger.debug(e)

	def onExit(self):
		if messagebox.askquestion('Exiting', 'Are you sure ?', icon='warning') == "yes":
			sys.exit(0)

def readSmartdConfFile(fileName):
	if not os.path.isfile(fileName):
		msg="No suitable [" + _CONSTANT.SMARTD_CONF_FILENAME + "] file found, creating new file [" + CONFIG.smartConfFile + "]."
		print(fileName)
		logger.info(msg)
		messagebox.showinfo('Information', msg)
		return False

	try:
		fileHandle = open(fileName, 'r')
	except Exception as e:
		msg="Cannot open config file [" + fileName + "]."
		logger.error(msg)
		logger.debug(e)
		messagebox.showinfo("Error", msg)
		return False

	try:
		driveList = []
		for line in fileHandle.readlines():
			if not line[0] == "#" and line[0] != "\n" and line[0] != "\r" and line[0] != " ":
				configList = line.split(' -')
				configList = [ configList[0] ] + [ '-' + item for item in configList[1:] ]
				# Remove unnecessary blanks and newlines
				for i, item in enumerate(configList):
					configList[i] = configList[i].strip()
				driveList.append(configList[0])
				del configList[0]
	except Exception as e:
		msg="Cannot read in config file [ " + fileName + "]."
		logger.error(msg)
		logger.debug(e)
		messagebox.showinfo("Error", msg)
		return False

	try:
		fileHandle.close()
		return (driveList, configList)
	except Exception as e:
		logger.error("Cannot close file [" + fileName + "].")
		logger.debug(e)

def writeSmartdConfFile(fileName, driveList, configList):
	try:
		fileHandle = open(fileName, 'w')
	except Exception as e:
		msg="Cannot open config file [ " + fileName + "]."
		logger.error(msg)
		logger.debug(e)
		messagebox.showinfo("Error", msg)
		return False

	try:
		fileHandle.write("# This file was generated on " + str(datetime.now()) + " by " + _CONSTANT.APP_NAME + " " + _CONSTANT.APP_VERSION  + "\n# http://www.netpower.fr\n")
	except Exception as e:
		msg="Cannot write config file [ " + fileName + "]."
		logger.error(msg)
		logger.debug(e)
		messagebox.showinfo("Error", msg)
		return False

	for drive in driveList:
		line = drive
		for arg in configList:
			line += " " + arg
		fileHandle.write(line + "\n")

	try:
		fileHandle.close()
	except Exception as e:
		logger.error("Cannot close file [" + fileName + "].")
		logger.debug(e)


def serviceHandler(service, action):
	"""Handle Windows / Unix services
	Valid actions are start, stop, restart, status
	"""

	msgAlreadyRunning="Service [" + service + "] already running."
	msgNotRunning="Service [" + service + "] is not running."
	msgAction="Action: " + action + " for service [" + service + "]."
	msgSuccess="Success for action " + action
	msgFailure="Failure for action " + action

	if platform.system() == "Windows":
		# Returns list. If second entry = 4, service is running
		#TODO: handle other service states than 4
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
					return False

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
					return False

		elif action == "restart":
			serviceHandler(service, stop)
			serviceHandler(service, start)

		elif action == "status":
			return isRunning

	else:
		# Using lsb service X command on Unix variantsn, hopefully the most portable
		serviceStatus = os.system("service " + service + " status > /dev/null 2>&1")
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
					os.system("service " + service + " start > /dev/null 2>&1")
					logger.info(msgSuccess)
					return True
				except Exception as e:
					logger.info(msgFailure)
					logger.debug(e)
					return False

		elif action == "stop":
			if not isRunning:
				logger.info(msgNotRunning)
			else:
				logger.info(msgAction)
				try:
					os.system("service " + service + " stop > /dev/null 2>&1")
					logger.info(msgSuccess)
					return True
				except Exception as e:
					logger.error(msgFailure)
					logger.debug(e)
					return False

		elif action == "restart":
			serviceHandler(service, stop)
			serviceHandler(service, start)

		elif action == "status":
			return isRunning

def usage():
	print(_CONSTANT.APP_NAME + " v" + _CONSTANT.APP_VERSION + " " + _CONSTANT.APP_BUILD)
	print(_CONSTANT.AUTHOR)
	print(_CONSTANT.CONTACT)
	print("")
	print("Works on Windows / Linux / *BSD")
	print("Usage:\n")
	print(_CONSTANT.APP_NAME + " -c [/path/to/" + _CONSTANT.SMARTD_CONF_FILENAME + "]")
	print(_CONSTANT.APP_NAME + " -c [c:\\path\\to\\" + _CONSTANT.SMARTD_CONF_FILENAME + "]")
	print("")
	print("If given file doesn't exist, we'll try to create it.")
	print("If no path is provided, we'll search for " + _CONSTANT.SMARTD_CONF_FILENAME + " in the following order:")
	print("./smartd.conf")
	print("/etc/smartd/smartd/conf")
	print("/etc/smartd/conf")
	print("%programfiles%\smartmontools-win\bin\smartd.conf")
	print("%programfiles(x86)%\smartmontools-win\bin\smartd.conf")
	print("%programfiles%\smartmontools\bin\smartd.conf")
	print("%programfiles(x86)%\smartmontools-win\bin\smartd.conf")
	print("If no file is found, we'll create a new ./smartd.conf file")
	print("[OPTIONS]")
	print("--help, -h, -?		Will show this message")
	sys.exit(1)

def main(argv):
	global CONFIG

	if _CONSTANT.IS_STABLE == False:
		logger.debug("Warning: This is an unstable developpment version.")

	try:
		opts, args = getopt.getopt(argv, "h?c:")
	except getopt.GetoptError:
		usage()
	for opt, arg in opts:
		if opt == '-h' or opt == "--help" or opt == "-?":
			usage()
		elif opt == '-c':
			confFile = arg

	if 'confFile' in locals():
		CONFIG = Configuration(confFile)
	else:
		CONFIG = Configuration()

	try:
		root = tk.Tk()
		root.title(_CONSTANT.APP_NAME)
		app = Application(root)
		root.mainloop()
	except Exception as e:
		logger.critical("Cannot instanciate main tk app.")
		logger.debug(e)
		sys.exit(1)

if __name__ == '__main__':
	main(sys.argv[1:])

