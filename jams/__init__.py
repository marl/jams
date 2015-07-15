#!/usr/bin/env python
"""Top-level module for JAMS"""

# Import the necessary modules
from .exceptions import *
from . import util
from . import _schema as schema
from . import eval
from .version import version as __version__

from .core import *

# Populate the namespace mapping
from pkg_resources import resource_filename

for _ in util.find_with_extension(resource_filename(__name__, schema.NS_SCHEMA_DIR),
                                  'json'):
    schema.add_namespace(_)

