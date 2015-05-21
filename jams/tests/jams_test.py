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


def test_jamsframe_add_observation():
    df = pd.DataFrame(data=[[0.0, 1.0, 'a', 0.0],
                            [1.0, 2.0, 'b', 0.0]],
                      columns=['time', 'duration', 'value', 'confidence'])

    jf = jams.JamsFrame.from_dataframe(df)

    jf.add_observation(time=3.0, duration=1.0, value='c', confidence=0.0)

    eq_(list(jf['time']),
        list(pd.to_timedelta([0.0, 1.0, 3.0], unit='s')))
    eq_(list(jf['duration']), 
        list(pd.to_timedelta([1.0, 2.0, 1.0], unit='s')))
    eq_(list(jf['value']), ['a', 'b', 'c'])
    eq_(list(jf['confidence']), [0.0, 0.0, 0.0])


def test_jamsframe_interval_values():

    df = pd.DataFrame(data=[[0.0, 1.0, 'a', 0.0],
                            [1.0, 2.0, 'b', 0.0]],
                      columns=['time', 'duration', 'value', 'confidence'])

    jf = jams.JamsFrame.from_dataframe(df)

    intervals, values = jf.to_interval_values()

    assert np.allclose(intervals, np.array([[0.0, 1.0], [1.0, 3.0]]))
    eq_(values, ['a', 'b'])


def test_jamsframe_serialize():

    def __test(dense, data):
        df = pd.DataFrame(data=data,
                          columns=['time', 'duration', 'value', 'confidence'])

        jf = jams.JamsFrame.from_dataframe(df)
        jf.dense = dense

        jf_s = jf.__json__

        jf2 = jams.JamsFrame.from_dict(jf_s)


        for key in jams.JamsFrame.fields():
            eq_(list(jf[key]), list(jf2[key]))

    values = [['a', 'b'], [dict(a=1), dict(b=2)]]

    for value in values:
        data = [[0.0, 1.0, value[0], 0.0],
                [1.0, 2.0, value[1], 0.0]]
        for dense in [False, True]:
            yield __test, dense, data


# Curator
def test_curator():

    c = jams.Curator(name='myself', email='you@me.com')

    eq_(c.name, 'myself')
    eq_(c.email, 'you@me.com')


# AnnotationMetadata

def test_annotation_metadata():


    def __test(data, curator, annotator):

        md = jams.AnnotationMetadata(curator=curator, annotator=annotator,
                                     **data)

        if curator is not None:
            eq_(dict(md.curator), dict(curator))

        if annotator is not None:
            eq_(dict(md.annotator), dict(annotator))

        real_data = dict(md)
        real_data.pop('curator')
        real_data.pop('annotator')
        eq_(real_data, data)


    dummies = dict(version='0',
                   corpus='test',
                   annotation_tools='nose',
                   annotation_rules='brains',
                   validation='unnecessary',
                   data_source='null')

    real_curator = jams.Curator(name='nobody', email='none@none.com')

    real_annotator = jams.Sandbox(description='none')

    for curator in [None, real_curator]:
        for annotator in [None, real_annotator]:
            yield __test, dummies, curator, annotator


# Annotation
def test_annotation():

    def __test(namespace, data, amd, sandbox):
        ann = jams.Annotation(namespace,
                              data=data,
                              annotation_metadata=amd,
                              sandbox=sandbox)

        eq_(namespace, ann.namespace)

        if amd is not None:
            eq_(dict(amd), dict(ann.annotation_metadata))

        if sandbox is not None:
            eq_(dict(sandbox), dict(ann.sandbox))

        if data is not None:
            assert ann.data.equals(jams.JamsFrame.from_dict(data))

    real_sandbox = jams.Sandbox(description='none')
    real_amd = jams.AnnotationMetadata(corpus='test collection')
    real_data = dict(time=[0.0, 1.0],
                     duration=[0.5, 0.5],
                     value=['one', 'two'],
                     confidence=[0.9, 0.9])

    namespace = 'tag_open'

    for data in [None, real_data]:
        for amd in [None, real_amd]:
            for sandbox in [None, real_sandbox]:
                yield __test, namespace, data, amd, sandbox


def test_annotation_append():

    data = dict(time=[0.0, 1.0],
                duration=[0.5, 0.5],
                value=['one', 'two'],
                confidence=[0.9, 0.9])

    namespace = 'tag_open'

    ann = jams.Annotation(namespace, data=data)

    update = dict(time=2.0, duration=1.0, value='three', confidence=0.8)

    ann.append(**update)

    jf = jams.JamsFrame.from_dict(data)
    jf.add_observation(**update)

    assert ann.data.equals(jf)


# FileMetadata

def test_filemetadata():

    meta = dict(title='Test track',
                artist='Test artist',
                release='Test release',
                duration=31.3)
    fm = jams.FileMetadata(**meta)
    dict_fm = dict(fm)

    for k in meta:
        eq_(meta[k], dict_fm[k])

# AnnotationArray

def test_annotation_array():

    arr = jams.AnnotationArray()

    eq_(len(arr), 0)


def test_annotation_array_data():

    data = dict(time=[0.0, 1.0],
                duration=[0.5, 0.5],
                value=['one', 'two'],
                confidence=[0.9, 0.9])
    ann = jams.Annotation('tag_open', data=data)
    arr = jams.AnnotationArray(annotations=[ann, ann])

    eq_(len(arr), 2)
    arr.append(ann)

    eq_(len(arr), 3)

    for t_ann in arr:
        assert ann.data.equals(t_ann.data)


def test_annotation_array_serialize():

    data = dict(time=[0.0, 1.0],
                duration=[0.5, 0.5],
                value=['one', 'two'],
                confidence=[0.9, 0.9])

    namespace = 'tag_open'
    ann = jams.Annotation(namespace, data=data)

    arr = jams.AnnotationArray(annotations=[ann, ann])

    arr_js = arr.__json__

    arr2 = jams.AnnotationArray(annotations=arr_js)

    eq_(arr, arr2)


# JAMS
def test_jams():

    data = dict(time=[0.0, 1.0],
                duration=[0.5, 0.5],
                value=['one', 'two'],
                confidence=[0.9, 0.9])

    real_ann = jams.AnnotationArray(annotations=[jams.Annotation('tag_open',
                                                                 data=data)])
    meta = dict(title='Test track',
                artist='Test artist',
                release='Test release',
                duration=31.3)
    real_fm = jams.FileMetadata(**meta)

    real_sandbox = jams.Sandbox(description='none')


    def __test(annotations, file_metadata, sandbox):
        jam = jams.JAMS(annotations=annotations,
                        file_metadata=file_metadata,
                        sandbox=sandbox)

        if file_metadata is not None:
            eq_(dict(file_metadata), dict(jam.file_metadata))

        if sandbox is not None:
            eq_(dict(sandbox), dict(jam.sandbox))

        if annotations is not None:
            eq_(annotations, jam.annotations)

    for ann in [None, real_ann]:
        for fm in [None, real_fm]:
            for sandbox in [None, real_sandbox]:
                yield __test, ann, fm, sandbox


def test_jams_save():

    fn = 'fixtures/valid.jams'


    jam = jams.load(fn)

    # Save to a temp file
    _, jam_out = tempfile.mkstemp()

    try:
        jam.save(jam_out)

        jam2 = jams.load(jam_out)

        print jam.__dict__
        print jam2.__dict__
        eq_(jam, jam2)
    finally:
        os.unlink(jam_out)


# Load
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


