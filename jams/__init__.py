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
from .schema import list_namespaces


# Populate the namespace mapping
for _ in util.find_with_extension(resource_filename(__name__, schema.NS_SCHEMA_DIR),
                                  'json'):
    schema.add_namespace(_)

# Populate local namespaces

try:
    for _ in util.find_with_extension(os.environ['JAMS_SCHEMA_DIR'], 'json'):
        schema.add_namespace(_)
except KeyError:
    pass
