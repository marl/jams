#!/usr/bin/env python
# CREATED:2015-07-15 10:21:30 by Brian McFee <brian.mcfee@nyu.edu>
'''Namespace management tests'''

from six.moves import reload_module

import os

from nose.tools import raises, eq_
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

    os.environ['JAMS_SCHEMA_DIR'] = os.path.join('fixtures', 'schema')

    # Namespace should not exist yet
    test_ns = 'testing_tag_upper'
    yield raises(NamespaceError)(__test), test_ns

    reload_module(jams)

    # Now it should
    yield __test, test_ns

    del os.environ['JAMS_SCHEMA_DIR']


def test_schema_values_pass():

    values = jams.schema.values('tag_gtzan')

    eq_(values, ['blues', 'classical', 'country',
                 'disco', 'hip-hop', 'jazz', 'metal',
                 'pop', 'reggae', 'rock'])


@raises(NamespaceError)
def test_schema_values_missing():
    jams.schema.values('imaginary namespace')


@raises(NamespaceError)
def test_schema_values_notenum():
    jams.schema.values('chord_harte')



def test_schema_dtypes():

    for n in jams.schema.__NAMESPACE__:
        jams.schema.get_dtypes(n)


@raises(NamespaceError)
def test_schema_dtypes_badns():
    jams.schema.get_dtypes('unknown namespace')

