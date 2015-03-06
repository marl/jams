#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''JAMS task-specific namespaces'''

import json
import jsonschema
from jsonschema import ValidationError
import six
import sys

import os
import warnings

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


def validate_jamsframe(frame, namespace):
    '''Validate a JamsFrame J against a namespace key.

    Parameters
    ----------
    frame : pyjams.JamsFrame
        A JamsFrame

    Returns
    -------
    valid : bool
        True if `frame` passes validation against `namespace`

    Raises
    ------
    KeyError
        If `namespace` is unknown

    jsonschema.ValidationError
        If `frame` fails to validate
    '''

    schema = ns_schema(namespace)

    for rec in frame.to_dict(orient='record'):
        jsonschema.validate(rec, schema)

    return True


def validate_annotation(annotation, strict=True):
    '''Validate a JAMS annotation object against its namespace.

    Parameters
    ----------
    annotation : pyjams.Annotation
        The object to validate

    strict : bool
        Force strict validation

    Returns
    -------
    valid : bool
        True if `annotation` passes validation
        False if `annotation` fails validation and `strict == False`


    Raises
    ------
    jsonschema.ValidationError
        If `annotation` fails validation and `strict == True``
    '''

    try:
        validate_jamsframe(annotation.data, annotation.namespace)
    except ValidationError as invalid:
        if strict:
            six.reraise(*sys.exc_info())
        else:
            warnings.warn(str(invalid))

        return False

    return True

# Populate the schemata
_SCHEMA_DIR = os.path.join('schema', 'namespaces')
