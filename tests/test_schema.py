#!/usr/bin/env python
# CREATED:2015-07-15 10:21:30 by Brian McFee <brian.mcfee@nyu.edu>
'''Namespace management tests'''

from six.moves import reload_module

import pytest
import os

from jams import NamespaceError
import jams


@pytest.mark.parametrize('ns_key',
                         ['pitch_hz', 'beat',
                          pytest.mark.xfail('DNE', raises=NamespaceError)])
def test_schema_namespace(ns_key):

    # Get the schema
    schema = jams.schema.namespace(ns_key)
    obs_schema = jams.schema.OBSERVATIONS_SCHEMA["definitions"]

    # Check that its fields match one of the observation types
    matched = False
    for _, obs in obs_schema.items():
        obs_properties = obs['properties']
        matched |= all( key in obs_properties for key in schema['properties']['data']['items']['properties'].keys() )

    assert matched


def test_schema_values_pass():

    values = jams.schema.values('tag_gtzan')

    assert values == ['blues', 'classical', 'country',
                      'disco', 'hip-hop', 'jazz', 'metal',
                      'pop', 'reggae', 'rock']


@pytest.mark.xfail(raises=NamespaceError)
def test_schema_values_missing():
    jams.schema.values('imaginary namespace')


@pytest.mark.xfail(raises=NamespaceError)
def test_schema_values_notenum():
    jams.schema.values('chord_harte')


def test_schema_dtypes():

    for n, _ in jams.schema.NAMESPACES.items():
        jams.schema.get_dtypes(n)


@pytest.mark.xfail(raises=NamespaceError)
def test_schema_dtypes_badns():
    jams.schema.get_dtypes('unknown namespace')


def test_list_namespaces():
    jams.schema.list_namespaces()
