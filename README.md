## smartd-pyngui

Portable GUI written in python to configure the smart daemon from smartmontools project.
Should write smartd.conf files compatible with every smartmontools release since 5.43
Works on Windows NT 5+, Linux, *BSD (and maybe Mac ?)

Tested with Python 2.7 and 3.4.4

## Installation

smartd-pyngui needs tkinter and pygubu in order to work.
tkinter should be available with a large range of distributions

Example for Redhat / CentOS / Fedora:

for Python2.7.x: ```yum install tkinter```
for Python3.4.x: ```yum install python34-tkinter```

Example for Debian / Ubuntu / Mint:

for Python 2.x: ```apt-get install python-tk```
for Python 3.x: ```apt-get install python3-tk```

The easyiest way to get pygubu is using pip.

If not installed, get pip by with the following command:

```wget https://bootstrap.pypa.io/get-pip.py && python get-pip.py```

After that, you may install pygubu with pip using ```pip install pygubu```

## Usage

Make sure that the main .py file and .ui file are in the same path and run:
```python smartd-pyngui.py```

## Executable files

smartd-pyngui may be freezed or compiled after it has been converted to C code.
As of today it has been tested under Windows with py2exe and nuitka.

To freeze and create an executable on windows, install py2exe (via pip) and run ```setup-smartd-pyngui.py```
Executable file will be created in dist directory.

To compile and create an executable on windows, install nuitka (via pip) and run 
```nuitka --standalone --portable smartd-pyngui.py```
Executable file will be created in smart-pyngui.dist directory. Don't forget to add the ui file.

