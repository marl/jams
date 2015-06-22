#!/usr/bin/env python
"""Top-level module for pyjams."""

# Import the necessary modules
from .exceptions import *
from . import util
from . import ns
from . import eval
from .version import version as __version__

from .pyjams import *

# Populate the namespace mapping
from pkg_resources import resource_filename

for _ in util.find_with_extension(resource_filename(__name__, ns.SCHEMA_DIR),
                                  'json'):
    ns.add_namespace(_)

