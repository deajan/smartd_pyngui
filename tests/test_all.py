from smartd_pyngui.smartd_pyngui import *

SMARTD_TEST_FILE='tests/smartd.conf'
SMARTD_TEST_FILE_NEW='tests/smartd_new.conf'
CONFIG=Configuration()


def test_readSmartdConfFile():
	global CONFIG

	#assert readSmartdConfFile('nope') == False
	conf = readSmartdConfFile(SMARTD_TEST_FILE)
	assert isinstance(conf, tuple)
	assert isinstance(conf[0], list)
	assert isinstance(conf[1], list)

	assert conf[0] == ['DEVICESCAN']
	print(conf)

def test_writeSmartdConfFile():
	global CONFIG

	testDrives = ['DEVICESCAN']
	testConf = ['-H', '-l error', '-f', '-C 197+', '-U 198+', '-t', '-l selftest', '-I 194', '-m <nomailer>', '-M exec "[PATH]\\erroraction.cmd"', '-n sleep,7,q', '-s (S/../.././10|L/../../[5]/13)']

	res = writeSmartdConfFile(SMARTD_TEST_FILE_NEW, testDrives, testConf)
	assert res == None
	assert os.path.isfile(SMARTD_TEST_FILE_NEW) == True

def test_compareConfFiles():
	pass
