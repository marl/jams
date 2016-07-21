#!/usr/bin/env python
# -*- encoding: utf-8 -*-
r'''
Namespace management
====================

.. autosummary::
    :toctree: generated/

    add_namespace
    namespace
    is_dense
    values
'''

import json
import os
import copy
from pkg_resources import resource_filename

from .exceptions import NamespaceError, JamsError

__all__ = ['add_namespace', 'namespace', 'is_dense', 'values']

__NAMESPACE__ = dict()


def add_namespace(filename):
    '''Add a namespace definition to our working set.

    Namespace files consist of partial JSON schemas defining the behavior
    of the `value` and `confidence` fields of an Annotation.

    Parameters
    ----------
    filename : str
        Path to json file defining the namespace object
    '''
    with open(filename, mode='r') as fileobj:
        __NAMESPACE__.update(json.load(fileobj))


def namespace(ns_key):
    '''Construct a validation schema for a given namespace.

    Parameters
    ----------
    ns_key : str
        Namespace key identifier (eg, 'beat' or 'segment_tut')

    Returns
    -------
    schema : dict
        JSON schema of `namespace`
    '''

    if ns_key not in __NAMESPACE__:
        raise NamespaceError('Unknown namespace: {:s}'.format(ns_key))

    sch = copy.deepcopy(JAMS_SCHEMA['definitions']['SparseObservation'])

    for key in ['value', 'confidence']:
        try:
            sch['properties'][key] = __NAMESPACE__[ns_key][key]
        except KeyError:
            pass

    return sch


def is_dense(ns_key):
    '''Determine whether a namespace has dense formatting.

    Parameters
    ----------
    ns_key : str
        Namespace key identifier

    Returns
    -------
    dense : bool
        True if `ns_key` has a dense packing
        False otherwise.
    '''

    if ns_key not in __NAMESPACE__:
        raise NamespaceError('Unknown namespace: {:s}'.format(ns_key))

    return __NAMESPACE__[ns_key]['dense']


def values(ns_key):
    '''Return the allowed values for an enumerated namespace.

    Parameters
    ----------
    ns_key : str
        Namespace key identifier

    Returns
    -------
    values : list

    Raises
    ------
    NamespaceError
        If `ns_key` is not found, or does not have enumerated values

    Examples
    --------
    >>> jams.schema.values('tag_gtzan')
    ['blues', 'classical', 'country', 'disco', 'hip-hop', 'jazz',
     'metal', 'pop', 'reggae', 'rock']
    '''

    if ns_key not in __NAMESPACE__:
        raise NamespaceError('Unknown namespace: {:s}'.format(ns_key))

    if 'enum' not in __NAMESPACE__[ns_key]['value']:
        raise NamespaceError('Namespace {:s} is not enumerated'.format(ns_key))

    return copy.copy(__NAMESPACE__[ns_key]['value']['enum'])


def __load_jams_schema():
    '''Load the schema file from the package.'''

    schema_file = os.path.join(SCHEMA_DIR, 'jams_schema.json')

    jams_schema = None
    with open(resource_filename(__name__, schema_file), mode='r') as fdesc:
        jams_schema = json.load(fdesc)

    if jams_schema is None:
        raise JamsError('Unable to load JAMS schema')

    return jams_schema

# Populate the schemata
SCHEMA_DIR = 'schemata'
NS_SCHEMA_DIR = os.path.join(SCHEMA_DIR, 'namespaces')

JAMS_SCHEMA = __load_jams_schema()

