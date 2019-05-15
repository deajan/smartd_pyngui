#   Copyright 2018-2019 by Orsiris de Jong - contact@netpower.fr
#
#   This is a dummy file to make the following directory a package

import sys
import os

# Fix so smartd_pyngui can be called outside from its directory (eg tests)
sys.path.insert(0, os.path.dirname(__file__))

from .smartd_pyngui import *
