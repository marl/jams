#!/usr/bin/env python
"""Top-level module for JAMS"""

# Import the necessary modules
from .exceptions import *
from . import util
from . import schema
from . import eval
from . import sonify
from .version import version as __version__

from .core import *
from .nsconvert import convert

# Populate the namespace mapping
from pkg_resources import resource_filename

for _ in util.find_with_extension(resource_filename(__name__, schema.NS_SCHEMA_DIR),
                                  'json'):
    schema.add_namespace(_)

# Populate local namespaces
import os

try:
    for _ in util.find_with_extension(os.environ['JAMS_SCHEMA_DIR'], 'json'):
        schema.add_namespace(_)
except KeyError:
    pass
