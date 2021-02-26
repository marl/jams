#!/usr/bin/env python
# -*- encoding: utf-8 -*-
r'''
Namespace management
--------------------

.. autosummary::
    :toctree: generated/

    values
    get_dtypes
    namespace
    list_namespaces
'''

from __future__ import print_function

import json
import os
import copy
from pkg_resources import resource_filename

import numpy as np
import jsonschema

from .exceptions import NamespaceError, JamsError
from .util import find_with_extension

__all__ = ['values', 'get_dtypes', 'namespace', 'list_namespaces', 'VALIDATOR']


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

    if ns_key not in NAMESPACES.keys():
        raise NamespaceError('Unknown namespace: {:s}'.format(ns_key))

    if 'enum' not in NAMESPACES[ns_key]['definitions']['value']:
        raise NamespaceError('Namespace {:s} is not enumerated'.format(ns_key))

    return copy.deepcopy(NAMESPACES[ns_key]['definitions']['value']['enum'])


def get_dtypes(ns_key):
    '''Get the dtypes associated with the value and confidence fields
    for a given namespace.

    Parameters
    ----------
    ns_key : str
        The namespace key in question

    Returns
    -------
    value_dtype, confidence_dtype : numpy.dtype
        Type identifiers for value and confidence fields.
    '''

    # First, get the schema
    if ns_key not in NAMESPACES.keys():
        raise NamespaceError('Unknown namespace: {:s}'.format(ns_key))

    value_dtype = __get_dtype(NAMESPACES[ns_key]['definitions'].get('value', {}))
    confidence_dtype = __get_dtype(NAMESPACES[ns_key]['definitions'].get('confidence', {}))

    return value_dtype, confidence_dtype


def namespace(ns_key):
    '''Retrieve a schema for a namespace'''
    try:
        schema = NAMESPACES[ns_key]
    except KeyError:
        raise NamespaceError('No such namespace: {}'.format(ns_key))
    return schema


def list_namespaces():
    '''Print out a listing of available namespaces'''
    print('{:30s}\t{:40s}'.format('NAME', 'DESCRIPTION'))
    print('-' * 78)
    for name, sch in sorted(NAMESPACES.items()):
        desc = sch['description']
        desc = (desc[:44] + '..') if len(desc) > 46 else desc
        print('{:30s}\t{:40s}'.format(name, desc))


# Mapping of js primitives to numpy types
__TYPE_MAP__ = dict(integer=np.int_,
                    boolean=np.bool_,
                    number=np.float_,
                    object=np.object_,
                    array=np.object_,
                    string=np.object_,
                    null=np.float_)


def __get_dtype(typespec):
    '''Get the dtype associated with a jsonschema type definition

    Parameters
    ----------
    typespec : dict
        The schema definition

    Returns
    -------
    dtype : numpy.dtype
        The associated dtype
    '''

    if 'type' in typespec:
        return __TYPE_MAP__.get(typespec['type'], np.object_)

    elif 'enum' in typespec:
        # Enums map to objects
        return np.object_

    elif 'oneOf' in typespec:
        # Recurse
        types = [__get_dtype(v) for v in typespec['oneOf']]

        # If they're not all equal, return object
        if all([t == types[0] for t in types]):
            return types[0]

    return np.object_


def __load_schema(schema_file):
    '''Load the schema file from the package.'''

    schema = None
    with open(schema_file, mode='r') as fdesc:
        schema = json.load(fdesc)

    if schema is None:
        raise JamsError('Unable to load schema: {}'.format(schema_file))

    return schema


def __load_namespaces():
    '''Loads all schema stored in the namespace directory'''

    namespaces = {}
    top_schemas = [os.path.basename(next(iter(ns_file.values())))[:-1] for ns_file in JAMS_SCHEMA['definitions']['Annotation']['oneOf']]

    for ns in find_with_extension(NS_SCHEMA_DIR, 'json'):
        if os.path.basename(ns) in top_schemas:
            schema = __load_schema(ns)
            namespaces[schema['definitions']['name']['const']] = schema
    
    return namespaces


# Declare schema resources
SCHEMA_DIR = resource_filename(__name__, 'schemata')
NS_SCHEMA_DIR = os.path.join(SCHEMA_DIR, 'namespaces')

# Load all schema
JAMS_SCHEMA =           __load_schema(os.path.join(SCHEMA_DIR, 'jams_schema.json'))
OBSERVATIONS_SCHEMA =   __load_schema(os.path.join(SCHEMA_DIR, 'observations.json'))
NAMESPACES =            __load_namespaces()

# Construct validator
JAMS_RESOLVER = jsonschema.RefResolver(
        base_uri = "file://" + os.path.abspath(os.path.join(SCHEMA_DIR, 'jams_schema.json')),
        referrer = JAMS_SCHEMA
    )
VALIDATOR = jsonschema.Draft7Validator(
    JAMS_SCHEMA,
    resolver = JAMS_RESOLVER
)
