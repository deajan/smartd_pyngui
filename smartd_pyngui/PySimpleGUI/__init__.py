#   Copyright 2018-2019 by Orsiris de Jong - contact@netpower.fr
#
#   This is a dummy file to make the following directory a package

import sys

if sys.version_info[0] >= 3:
    from .PySimpleGUI import *
else:
    from .PySimpleGUI27 import *


