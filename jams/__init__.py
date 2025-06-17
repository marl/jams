#!/usr/bin/env python
"""Top-level module for JAMS"""

import os
import sys
from importlib import resources
from itertools import chain

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
if sys.version_info < (3, 10):
    from pkg_resources import resource_filename

    for _ in util.find_with_extension(
        resource_filename(__name__, schema.NS_SCHEMA_DIR), "json"
    ):
        schema.add_namespace(_)

else:
    for ns in chain(
        *map(
            lambda p: p.rglob("*.json"),
            resources.files("jams.schemata.namespaces").iterdir(),
        )
    ):
        schema.add_namespace(ns)

# Populate local namespaces
if "JAMS_SCHEMA_DIR" in os.environ:
    for ns in util.find_with_extension(os.environ["JAMS_SCHEMA_DIR"], "json"):
        schema.add_namespace(ns)
