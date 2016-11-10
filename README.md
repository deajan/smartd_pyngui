## smartd-pyngui

Portable GUI written in python to configure the smart daemon from smartmontools project.
Should write smartd.conf files compatible with every smartmontools release since 5.43
Works on Windows NT 5+, Linux, *BSD (and maybe Mac ?)

Tested with Python 2.7 and 3.4.4

## Usage

Make sure that the main .py file and .ui file are in the same path.

python smartd-pyngui.py

Windows executables are created with py2exe (using setup-smartd-pyngui.py)

