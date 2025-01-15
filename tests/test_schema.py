#!/usr/bin/env python
# CREATED:2015-07-15 10:21:30 by Brian McFee <brian.mcfee@nyu.edu>
'''Namespace management tests'''

from six.moves import reload_module

import pytest
import os

from jams import NamespaceError
import jams


@pytest.mark.parametrize('ns_key', ['pitch_hz', 'beat'])
def test_schema_namespace(ns_key):
    if ns_key == 'DNE':
        pytest.xfail(reason="Namespace 'DNE' does not exist")
    else:
        # Get the schema
        schema = jams.schema.namespace(ns_key)
        # Make sure it has the correct properties
        valid_keys = set(['time', 'duration', 'value', 'confidence'])
        for key in schema['properties']:
            assert key in valid_keys
        for key in ['time', 'duration']:
            assert key in schema['properties']

@pytest.mark.parametrize('ns_key', ['DNE'])
def test_schema_namespace_exception(ns_key):
    with pytest.raises(NamespaceError):
        jams.schema.namespace(ns_key)



@pytest.mark.parametrize('ns, dense', [('pitch_hz', True), ('beat', False), ('DNE', False)])
def test_schema_is_dense(ns, dense):
    if ns == 'DNE':
        pytest.xfail(reason="Namespace 'DNE' does not exist")
    else:
        assert dense == jams.schema.is_dense(ns)

@pytest.mark.parametrize('ns', ['DNE'])
def test_schema_is_dense_exception(ns):
    with pytest.raises(NamespaceError):
        jams.schema.is_dense(ns)


@pytest.fixture
def local_namespace():

    os.environ['JAMS_SCHEMA_DIR'] = os.path.join('tests', 'fixtures', 'schema')
    reload_module(jams)

    # This one should pass
    yield 'testing_tag_upper', True

    # Cleanup
    del os.environ['JAMS_SCHEMA_DIR']
    reload_module(jams)


def test_schema_local(local_namespace):

    ns_key, exists = local_namespace

    # Get the schema
    if exists:
        schema = jams.schema.namespace(ns_key)

        # Make sure it has the correct properties
        valid_keys = set(['time', 'duration', 'value', 'confidence'])
        for key in schema['properties']:
            assert key in valid_keys

        for key in ['time', 'duration']:
            assert key in schema['properties']
    else:
        with pytest.raises(NamespaceError):
            schema = jams.schema.namespace(ns_key)


def test_schema_values_pass():

    values = jams.schema.values('tag_gtzan')

    assert values == ['blues', 'classical', 'country',
                      'disco', 'hip-hop', 'jazz', 'metal',
                      'pop', 'reggae', 'rock']


def test_schema_values_missing():
    with pytest.raises(NamespaceError):
        jams.schema.values('imaginary namespace')


def test_schema_values_notenum():
    with pytest.raises(NamespaceError):
        jams.schema.values('chord_harte')


def test_schema_dtypes():

    for n in jams.schema.__NAMESPACE__:
        jams.schema.get_dtypes(n)


def test_schema_dtypes_badns():
    with pytest.raises(NamespaceError):
        jams.schema.get_dtypes('unknown namespace')


def test_list_namespaces():
    jams.schema.list_namespaces()
