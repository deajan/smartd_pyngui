import os
import sys

# Fix so tests include parent directory for package search
sys.path.insert(0, os.path.normpath(os.path.join(os.path.dirname(__file__), "..")))

from smartd_pyngui.smartd_pyngui import *

config = Configuration()


def test_load_app():
    assert APP_VERSION is not None
    assert os.path.isdir(config.app_root) is True
    assert os.path.isfile(config.app_executable) is True


def test_read_smartd_conf_file():
    pass


def test_write_smartd_conf_file():
    pass


def test_read_alert_conf_file():
    pass


def test_write_alert_conf_file():
    pass


def test_compare_smartd_conf_files():
    pass


def test_compare_alert_conf_files():
    pass



# TODO Write smartd & alert conf file RW tests
# smartd conf file needs to be compared with basic one