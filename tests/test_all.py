from smartd_pyngui.smartd_pyngui import *

SMARTD_TEST_FILE='tests/smartd.conf'
SMARTD_TEST_FILE_NEW='tests/smartd_new.conf'

config=Configuration(SMARTD_TEST_FILE)


def test_readSmartdConfFile():
	assert readSmartdConfFile() == True
	assert isinstance(config.driveList, list)
	assert isinstance(config.configList, list)

	assert config.driveList == ['DEVICESCAN']
	print(config.driveList)
	print(config.configList)

def test_writeSmartdConfFile():
	testDrives = ['DEVICESCAN']
	testConf = ['-H', '-l error', '-f', '-C 197+', '-U 198+', '-t', '-l selftest', '-I 194', '-m <nomailer>', '-M exec "[PATH]\\erroraction.cmd"', '-n sleep,7,q', '-s (S/../.././10|L/../../[5]/13)']

	config.driveList = testDrives
	config.configList = testConf
	res = writeSmartdConfFile()
	assert res == True
	assert os.path.isfile(SMARTD_TEST_FILE_NEW) == True

def test_compareConfFiles():
	pass
