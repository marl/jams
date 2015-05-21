#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''JAMS task-specific namespaces'''

import json
import os

__NAMESPACE__ = dict()


def add_namespace(filename):
    '''Add a namespace definition to our working set.

    Parameters
    ----------
    filename : str
        Path to json file defining the namespace object
    '''
    with open(filename, mode='r') as fileobj:
        __NAMESPACE__.update(json.load(fileobj))


def ns_schema(namespace):
    '''Construct a validation schema for a given namespace.

    Parameters
    ----------
    namespace : str
        Namespace key identifier (eg, 'beat' or 'segment_tut')

    Returns
    -------
    schema : dict
        JSON schema of `namespace`
    '''

    properties = dict()

    for key in ['value', 'confidence']:
        try:
            properties[key] = __NAMESPACE__[namespace][key]
        except KeyError:
            pass

    return dict(type='object', properties=properties)


def is_dense(namespace):
    '''Determine whether a namespace has dense formatting.

    Parameters
    ----------
    namespace : str
        Namespace key identifier

    Returns
    -------
    dense : bool
        True if `namespace` has a dense packing
        False otherwise.
    '''

    return __NAMESPACE__[namespace]['dense']


# Populate the schemata
_SCHEMA_DIR = os.path.join('schema', 'namespaces')
