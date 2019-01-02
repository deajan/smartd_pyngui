from smartd_pyngui import *

SMARTD_TEST_FILE='tests/smartd.conf'
SMARTD_TEST_FILE_COMPARAISON='tests/smartd-vanilla.conf'

config=Configuration(SMARTD_TEST_FILE)


def test_readSmartdConfFile():
	#print(config.readSmartdConfFile())
	assert config.readSmartdConfFile() == True
	config.readSmartdConfFile()
	assert isinstance(config.driveList, list)
	assert isinstance(config.configList, list)

	assert config.driveList == ['DEVICESCAN']
	print(config.driveList)
	print(config.configList)

def test_writeSmartdConfFile():
	testDrives = ['DEVICESCAN']
	testConf = ['-H', '-C 197+', '-l error', '-U 198+', '-l selftest', '-t', '-f', '-n sleep,7,q', '-s (L/../../[4]/13|S/../../[1234567]/10)', '-m root']

	config.driveList = testDrives
	config.configList = testConf
	assert config.writeSmartdConfFile() == True

def test_compareConfFiles():
	handle = open(SMARTD_TEST_FILE, 'r')
	handleCompare = open(SMARTD_TEST_FILE_COMPARAISON, 'r')
	
	comparaisonResult = True

	for line in handle.readlines():
		lineCompare = handleCompare.readline()
		if not line[0] == "#" and line[0] != "\n" and line[0] != "\r" and line[0] != " ":
			if not line == lineCompare:
				comparaisonResult = False
				print('Error in comparaison')
				print(line)
				print(lineCompare)

	handle.close()
	handleCompare.close()
	
	assert comparaisonResult == True
