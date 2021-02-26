#!/usr/bin/env python
"""Top-level module for JAMS"""

import os
from pkg_resources import resource_filename

# Import the necessary modules
from .exceptions import *
from . import util
from . import schema
from . import eval
from . import sonify
from .version import version as __version__

from .core import *
from .nsconvert import convert
