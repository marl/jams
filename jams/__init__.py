#!/usr/bin/env python
"""Top-level module for pyjams."""

# Import the necessary modules
from .pyjams import *
from . import util
from . import namespace
from . import eval
from .version import version as __VERSION__


# Populate the namespace mapping
from pkg_resources import resource_filename

for nsf in util.find_with_extension(resource_filename(__name__,
                                                      namespace._SCHEMA_DIR),
                                    'json'):
    namespace.add_namespace(nsf)
