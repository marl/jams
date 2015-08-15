#!/usr/bin/env python
#CREATED:2015-07-15 10:21:30 by Brian McFee <brian.mcfee@nyu.edu>
'''Namespace management tests'''

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
