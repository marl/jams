#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# CREATED:2015-03-06 14:24:58 by Brian McFee <brian.mcfee@nyu.edu>
'''Unit tests for JAMS core objects'''

import os
import tempfile
import json
import jsonschema
import six
import warnings
import numpy as np
import pandas as pd

from nose.tools import raises, eq_

import jams


# JObject

def test_jobject_dict():

    data = dict(key1='value 1', key2='value 2')

    J = jams.JObject(**data)

    jdict = J.__dict__

    eq_(data, jdict)


def test_jobject_serialize():

    data = dict(key1='value 1', key2='value 2')

    json_data = json.dumps(data, indent=2)

    J = jams.JObject(**data)

    json_jobject = J.dumps(indent=2)

    eq_(json_data, json_jobject)


def test_jobject_deserialize():

    data = dict(key1='value 1', key2='value 2')

    json_data = json.dumps(data, indent=2)

    J = jams.JObject.loads(json_data)

    json_jobject = J.dumps(indent=2)

    eq_(json_data, json_jobject)


def test_jobject_eq():

    def __test(d1, d2, match):

        J1 = jams.JObject(**d1)
        J2 = jams.JObject(**d2)

        # Test self-equivalence
        assert J1 == J1
        assert J2 == J2

        # Test equivalence in both directions
        assert (J1 == J2) == match
        assert (J2 == J1) == match

    data_1 = dict(key1='value 1', key2='value 2')
    data_2 = dict(key1='value 1', key2='value 2')
    data_3 = dict(key1='value 1', key2='value 3')

    yield __test, data_1, data_1, True
    yield __test, data_1, data_2, True
    yield __test, data_1, data_3, False


def test_jobject_nonzero():

    def __test(d, value):
        J = jams.JObject(**d)

        eq_(J.__nonzero__(), value)

    yield __test, {'key': True}, True
    yield __test, {'key': False}, False
    yield __test, {}, False


# Sandbox

def test_sandbox():

    data = dict(key1='value 1', key2='value 2')

    J = jams.Sandbox(**data)

    for key, value in six.iteritems(data):
        eq_(value, J[key])



# JamsFrame

def test_jamsframe_fields():

    eq_(jams.JamsFrame.fields(), ['time', 'duration', 'value', 'confidence'])


def test_jamsframe_from_df():

    df = pd.DataFrame(data=[[0.0, 1.0, 'a', 0.0],
                            [1.0, 2.0, 'b', 0.0]],
                      columns=['time', 'duration', 'value', 'confidence'])

    jf = jams.JamsFrame.from_dataframe(df)

    # 1. type check
    assert isinstance(jf, jams.JamsFrame)

    # 2. check field order
    eq_(list(jf.keys().values),
        jams.JamsFrame.fields())

    # 3. check field types
    assert jf['time'].dtype == np.dtype('<m8[ns]')
    assert jf['duration'].dtype == np.dtype('<m8[ns]')

    # 4. Check the values
    eq_(list(jf['time']),
        list(pd.to_timedelta([0.0, 1.0], unit='s')))
    eq_(list(jf['duration']), 
        list(pd.to_timedelta([1.0, 2.0], unit='s')))
    eq_(list(jf['value']), ['a', 'b'])
    eq_(list(jf['confidence']), [0.0, 0.0])


# Curator

# AnnotationMetadata

# Annotation

# FileMetadata

# AnnotationArray

# JAMS

def test_load_fail():
    # 1. test bad file path
    # 2. test non-json file

    def __test(filename):
        jams.load(filename)

    # Make a non-existent file
    tdir = tempfile.mkdtemp()
    yield raises(IOError)(__test), os.path.join(tdir, 'nonexistent.jams')
    os.rmdir(tdir)
    
    # Make a non-json file
    tdir = tempfile.mkdtemp()
    badfile = os.path.join(tdir, 'nonexistent.jams')
    with open(badfile, mode='w') as fp:
        fp.write('some garbage')
    yield raises(ValueError)(__test), os.path.join(tdir, 'nonexistent.jams')
    os.unlink(badfile)
    os.rmdir(tdir)


def test_load_valid():

    # 3. test good jams file with strict validation
    # 4. test good jams file without strict validation

    def __test(filename, valid, strict):
        jams.load(filename, validate=valid, strict=strict)


    fn = 'fixtures/valid.jams'

    for validate in [False, True]:
        for strict in [False, True]:
            yield __test, fn, validate, strict

def test_load_invalid():

    def __test(filename, valid, strict):
        jams.load(filename, validate=valid, strict=strict)

    def __test_warn(filename, valid, strict):
        warnings.resetwarnings()
        with warnings.catch_warnings(record=True) as out:
            jams.load(filename, validate=valid, strict=strict)

        assert len(out) > 0
        assert out[0].category is UserWarning
        assert 'failed validating' in str(out[0].message).lower()

    # 5. test bad jams file with strict validation
    # 6. test bad jams file without strict validation
    fn = 'fixtures/invalid.jams'

    # Test once with no validation
    yield __test, fn, False, False

    # With validation, failure can either be a warning or an exception
    yield raises(jsonschema.ValidationError)(__test), fn, True, True

    yield __test_warn, fn, True, False


