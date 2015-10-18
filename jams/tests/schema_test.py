#!/usr/bin/env python
#CREATED:2015-07-15 10:21:30 by Brian McFee <brian.mcfee@nyu.edu>
'''Namespace management tests'''

from pkg_resources import resource_filename

from six.moves import reload_module

import os

from nose.tools import raises
from jams import NamespaceError
import jams


def test_schema_namespace():

    def __test(ns_key):

        # Get the schema
        schema = jams.schema.namespace(ns_key)

        # Make sure it has the correct properties
        valid_keys = set(['time', 'duration', 'value', 'confidence'])
        for key in schema['properties']:
            assert key in valid_keys

        for key in ['time', 'duration']:
            assert key in schema['properties']


    yield __test, 'pitch_hz'
    yield __test, 'beat'
    yield raises(NamespaceError)(__test), 'made up namespace'


def test_schema_is_dense():

    def __test(ns, dense):
        assert dense == jams.schema.is_dense(ns)

    yield __test, 'pitch_hz', True
    yield __test, 'beat', False
    yield raises(NamespaceError)(__test), 'made up namespace', False


def test_schema_local():
    def __test(ns_key):

        # Get the schema
        schema = jams.schema.namespace(ns_key)

        # Make sure it has the correct properties
        valid_keys = set(['time', 'duration', 'value', 'confidence'])
        for key in schema['properties']:
            assert key in valid_keys

        for key in ['time', 'duration']:
            assert key in schema['properties']

    os.environ['JAMS_SCHEMA_DIR'] = resource_filename(jams.__name__, 
                                                      os.path.join('tests',
                                                                   'fixtures',
                                                                   'schema'))
    reload(jams)

    yield __test, 'testing_tag_upper'
    
    del os.environ['JAMS_SCHEMA_DIR']

