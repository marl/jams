#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# CREATED:2015-03-06 14:24:58 by Brian McFee <brian.mcfee@nyu.edu>
'''Unit tests for JAMS core objects'''

import os
import tempfile
import json
import six
import sys
import warnings

from nose.tools import raises, eq_

import jams


# Borrowed from sklearn
def clean_warning_registry():
    """Safe way to reset warnings """
    warnings.resetwarnings()
    reg = "__warningregistry__"
    for mod_name, mod in list(sys.modules.items()):
        if 'six.moves' in mod_name:
            continue
        if hasattr(mod, reg):
            getattr(mod, reg).clear()


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

    # De-serialize into dicts
    eq_(json.loads(json_data), json.loads(json_jobject))


def test_jobject_deserialize():

    data = dict(key1='value 1', key2='value 2')

    J = jams.JObject(**data)

    json_jobject = J.dumps(indent=2)

    eq_(J, jams.JObject.loads(json_jobject))


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

        # Test type safety
        J3 = jams.Sandbox(**d1)
        assert not J1 == J3

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
    yield __test, {}, False


# Sandbox

def test_sandbox():

    data = dict(key1='value 1', key2='value 2')

    J = jams.Sandbox(**data)

    for key, value in six.iteritems(data):
        eq_(value, J[key])


def test_sandbox_contains():
    d = dict(foo=5, bar=9)
    S = jams.Sandbox(**d)

    for key in d:
        assert key in S


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
            eq_(len(ann.data), len(data))
            for obs1, obs2 in zip(ann.data, data):
                eq_(obs1._asdict(), obs2)

    real_sandbox = jams.Sandbox(description='none')
    real_amd = jams.AnnotationMetadata(corpus='test collection')

    real_data = [dict(time=0, duration=0.5, value='one', confidence=0.9),
                 dict(time=1.0, duration=0.5, value='two', confidence=0.9)]

    namespace = 'tag_open'

    for data in [None, real_data]:
        for amd in [None, real_amd]:
            for sandbox in [None, real_sandbox]:
                yield __test, namespace, data, amd, sandbox


def test_annotation_append():

    data = [dict(time=0, duration=0.5, value='one', confidence=0.9),
            dict(time=1.0, duration=0.5, value='two', confidence=0.9)]

    namespace = 'tag_open'

    ann = jams.Annotation(namespace, data=data)

    update = dict(time=2.0, duration=1.0, value='three', confidence=0.8)

    ann.append(**update)

    eq_(ann.data[-1]._asdict(), update)


def test_annotation_eq():

    data = dict(time=[0.0, 1.0],
                duration=[0.5, 0.5],
                value=['one', 'two'],
                confidence=[0.9, 0.9])

    namespace = 'tag_open'

    ann1 = jams.Annotation(namespace, data=data)
    ann2 = jams.Annotation(namespace, data=data)

    eq_(ann1, ann2)

    # Test the type-check in equality
    assert not (ann1 == data)

    update = dict(time=2.0, duration=1.0, value='three', confidence=0.8)

    ann2.append(**update)

    assert not (ann1 == ann2)


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
        eq_(ann.data, t_ann.data)


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


def test_annotation_array_index_simple():

    jam = jams.JAMS()

    anns = [jams.Annotation('beat') for _ in range(5)]

    for ann in anns:
        jam.annotations.append(ann)

    assert len(jam.annotations) == len(anns)
    for i in range(5):
        a1, a2 = anns[i], jam.annotations[i]
        eq_(a1, a2)


def test_annotation_array_slice_simple():

    jam = jams.JAMS()

    anns = [jams.Annotation('beat') for _ in range(5)]

    for ann in anns:
        jam.annotations.append(ann)

    res = jam.annotations[:3]
    eq_(len(res), 3)
    assert anns[0] in res


def test_annotation_array_index_fancy():

    jam = jams.JAMS()
    ann = jams.Annotation(namespace='beat')
    jam.annotations.append(ann)
    # We should have exactly one beat annotation
    res = jam.annotations['beat']
    eq_(len(res), 1)
    eq_(res[0], ann)
    # Any other namespace should give an empty list
    eq_(jam.annotations['segment'], [])


def test_annotation_array_composite():

    jam = jams.JAMS()
    for _ in range(10):
        ann = jams.Annotation(namespace='beat')
        jam.annotations.append(ann)

    eq_(len(jam.annotations['beat', :3]), 3)

    eq_(len(jam.annotations['beat', 3:]), 7)

    eq_(len(jam.annotations['beat', 2::2]), 4)


@raises(IndexError)
def test_annotation_array_index_error():

    jam = jams.JAMS()
    ann = jams.Annotation(namespace='beat')
    jam.annotations.append(ann)

    res = jam.annotations[None]


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

    def __test(ext):
        fn = 'fixtures/valid.{:s}'.format(ext)
        jam = jams.load(fn)

        # Save to a temp file
        _, jam_out = tempfile.mkstemp(suffix='.{:s}'.format(ext))

        try:
            jam.save(jam_out)

            jam2 = jams.load(jam_out)

            eq_(jam, jam2)
        finally:
            os.unlink(jam_out)

    for ext in ['jams', 'jamz']:
        yield __test, ext


def test_jams_add():

    def __test():

        fn = 'fixtures/valid.jams'

        # The original jam
        jam_orig = jams.load(fn)
        jam = jams.load(fn)

        # Make a new jam with the same metadata and different data
        jam2 = jams.load(fn)
        data = dict(time=[0.0, 1.0],
                    duration=[0.5, 0.5],
                    value=['one', 'two'],
                    confidence=[0.9, 0.9])
        ann = jams.Annotation('tag_open', data=data)
        jam2.annotations = jams.AnnotationArray(annotations=[ann])

        # Add the two
        jam.add(jam2)

        eq_(len(jam.annotations), 3)
        eq_(jam.annotations[:-1], jam_orig.annotations)
        eq_(jam.annotations[-1], jam2.annotations[0])

    def __test_conflict(on_conflict):
        fn = 'fixtures/valid.jams'

        # The original jam
        jam = jams.load(fn)
        jam_orig = jams.load(fn)

        # The copy
        jam2 = jams.load(fn)

        jam2.file_metadata = jams.FileMetadata()

        jam.add(jam2, on_conflict=on_conflict)

        if on_conflict == 'overwrite':
            eq_(jam.file_metadata, jam2.file_metadata)
        elif on_conflict == 'ignore':
            eq_(jam.file_metadata, jam_orig.file_metadata)

    yield __test

    for on_conflict in ['overwrite', 'ignore']:
        yield __test_conflict, on_conflict

    for on_conflict in ['fail']:
        yield raises(jams.JamsError)(__test_conflict), on_conflict

    for on_conflict in ['bad_fail_mode']:
        yield raises(jams.ParameterError)(__test_conflict), on_conflict


def test_jams_search():
    def __test(jam, query, expected):
        
        result = jam.search(**query)

        eq_(result, expected)

    fn = 'fixtures/valid.jams'
    jam = jams.load(fn)

    jam.annotations[0].sandbox.foo = None

    yield __test, jam, dict(corpus='SMC_MIREX'), jam.annotations
    yield __test, jam, dict(), []
    yield __test, jam, dict(namespace='beat'), jam.annotations[0:1]
    yield __test, jam, dict(namespace='tag_open'), jam.annotations[1:]
    yield __test, jam, dict(namespace='segment_tut'), jams.AnnotationArray()
    yield __test, jam.file_metadata, dict(duration=40.0), True
    yield __test, jam.file_metadata, dict(duration=39.0), False
    yield __test, jam, dict(foo='bar'), jams.AnnotationArray()


def test_jams_validate_good():

    fn = 'fixtures/valid.jams'
    j1 = jams.load(fn, validate=False)

    j1.validate()


def test_jams_validate_bad():

    def __test(strict):
        fn = 'fixtures/invalid.jams'
        j1 = jams.load(fn, validate=False)

        clean_warning_registry()

        with warnings.catch_warnings(record=True) as out:
            j1.validate(strict=strict)

        assert len(out) > 0
        assert out[0].category is UserWarning
        assert 'failed validating' in str(out[0].message).lower()

    yield __test, False
    yield raises(jams.SchemaError)(__test), True


@raises(jams.SchemaError)
def test_jobject_bad_field():
    jam = jams.JAMS()

    jam.out_of_schema = None


# Load
def test_load_fail():
    # 1. test bad file path
    # 2. test non-json file
    # 3. test bad extensions
    # 4. test bad codecs

    def __test(filename, fmt):
        jams.load(filename, fmt=fmt)

    # Make a non-existent file
    tdir = tempfile.mkdtemp()
    yield raises(IOError)(__test), os.path.join(tdir, 'nonexistent.jams'), 'jams'
    os.rmdir(tdir)

    # Make a non-json file
    tdir = tempfile.mkdtemp()
    badfile = os.path.join(tdir, 'nonexistent.jams')
    with open(badfile, mode='w') as fp:
        fp.write('some garbage')
    yield raises(ValueError)(__test), os.path.join(tdir, 'nonexistent.jams'), 'jams'
    os.unlink(badfile)
    os.rmdir(tdir)

    tdir = tempfile.mkdtemp()
    for ext in ['txt', '']:
        badfile = os.path.join(tdir, 'nonexistent')
        yield raises(jams.ParameterError)(__test), '{:s}.{:s}'.format(badfile, ext), 'auto'
        yield raises(jams.ParameterError)(__test), '{:s}.{:s}'.format(badfile, ext), ext
        yield raises(jams.ParameterError)(__test), '{:s}.jams'.format(badfile), ext
    os.rmdir(tdir)


def test_load_valid():

    # 3. test good jams file with strict validation
    # 4. test good jams file without strict validation

    def __test(filename, valid, strict):
        jams.load(filename, validate=valid, strict=strict)


    fn = 'fixtures/valid'

    for ext in ['jams', 'jamz']:
        for validate in [False, True]:
            for strict in [False, True]:
                yield __test, '{:s}.{:s}'.format(fn, ext), validate, strict


def test_load_invalid():

    def __test(filename, valid, strict):
        jams.load(filename, validate=valid, strict=strict)

    def __test_warn(filename, valid, strict):
        clean_warning_registry()

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
    yield raises(jams.SchemaError)(__test), fn, True, True

    yield __test_warn, fn, True, False


def test_annotation_trim_bad_params():

    @raises(jams.ParameterError, jams.JamsError)
    def __test_error(ann, start_time, end_time, strict=False):
        return ann.trim(start_time, end_time, strict=strict)

    # end_time must be greater than start_time
    ann = jams.Annotation('tag_open')
    __test_error(ann, 5, 3)


def test_annotation_trim_no_duration():
    # When ann.duration is not set prior to trim should raise warning
    ann = jams.Annotation('tag_open')
    ann.duration = None

    clean_warning_registry()
    with warnings.catch_warnings(record=True) as out:
        ann_trim = ann.trim(3, 5)

    assert len(out) > 0
    assert out[0].category is UserWarning
    assert 'annotation.duration is not defined' in str(out[0].message).lower()

    # When duration is not defined trim should keep all observations in the
    # user-specified trim range.
    namespace = 'tag_open'
    ann = jams.Annotation(namespace)
    ann.time = 100
    ann.duration = None
    ann.append(time=5, duration=2, value='one')

    clean_warning_registry()
    with warnings.catch_warnings(record=True) as out:
        ann_trim = ann.trim(5, 8)

    assert len(out) > 0
    assert out[0].category is UserWarning
    assert 'annotation.duration is not defined' in str(out[0].message).lower()

    expected_data = dict(time=[5.0],
                         duration=[2.0],
                         value=['one'],
                         confidence=[None])
    expected_ann = jams.Annotation(namespace, data=expected_data, time=5.0,
                                   duration=3.0)
    eq_(ann_trim.data, expected_ann.data)


def test_annotation_trim_no_overlap():
    # when there's no overlap, a warning is raised and the
    # returned annotation should be empty
    ann = jams.Annotation('tag_open')
    ann.time = 5
    ann.duration = 10

    trim_times = [(1, 2), (16, 20)]

    for tt in trim_times[:2]:

        clean_warning_registry()
        with warnings.catch_warnings(record=True) as out:
            ann_trim = ann.trim(*tt)

        assert len(out) > 0
        assert out[0].category is UserWarning
        assert 'does not intersect' in str(out[0].message).lower()

        assert len(ann_trim.data) == 0
        assert ann_trim.time == ann.time
        assert ann_trim.duration == 0


def test_annotation_trim_complete_overlap():
    # For a valid scenario, ensure everything behaves as expected
    namespace = 'tag_open'
    data = dict(time=[5.0, 5.0, 10.0],
                duration=[2.0, 4.0, 4.0],
                value=['one', 'two', 'three'],
                confidence=[0.9, 0.9, 0.9])
    ann = jams.Annotation(namespace, data=data, time=5.0, duration=10.0)

    # When the trim region is completely inside the annotation time range

    # with strict=False
    ann_trim = ann.trim(8, 12, strict=False)

    assert ann_trim.time == 8
    assert ann_trim.duration == 4
    assert ann_trim.sandbox.trim == [{'start_time': 8, 'end_time': 12,
                                      'trim_start': 8, 'trim_end': 12}]
    assert ann_trim.namespace == ann.namespace
    assert ann_trim.annotation_metadata == ann.annotation_metadata

    expected_data = dict(time=[8.0, 10.0],
                         duration=[1.0, 2.0],
                         value=['two', 'three'],
                         confidence=[0.9, 0.9])
    expected_ann = jams.Annotation(namespace, data=expected_data, time=8.0,
                                   duration=4.0)
    eq_(ann_trim.data, expected_ann.data)

    # with strict=True
    ann_trim = ann.trim(8, 12, strict=True)

    assert ann_trim.time == 8
    assert ann_trim.duration == 4
    assert ann_trim.sandbox.trim == [{'start_time': 8, 'end_time': 12,
                                      'trim_start': 8, 'trim_end': 12}]
    assert ann_trim.namespace == ann.namespace
    assert ann_trim.annotation_metadata == ann.annotation_metadata

    expected_data = None
    expected_ann = jams.Annotation(namespace, data=expected_data, time=8.0,
                                   duration=4.0)
    eq_(ann_trim.data, expected_ann.data)


def test_annotation_trim_partial_overlap_beginning():
    # When the trim region only partially overlaps with the annotation time
    # range: at the beginning
    # strict=False
    namespace = 'tag_open'
    data = dict(time=[5.0, 5.0, 10.0],
                duration=[2.0, 4.0, 4.0],
                value=['one', 'two', 'three'],
                confidence=[0.9, 0.9, 0.9])
    ann = jams.Annotation(namespace, data=data, time=5.0, duration=10.0)

    ann_trim = ann.trim(0, 8, strict=False)

    assert ann_trim.time == 5
    assert ann_trim.duration == 3
    assert ann_trim.sandbox.trim == [{'start_time': 0, 'end_time': 8,
                                      'trim_start': 5, 'trim_end': 8}]
    assert ann_trim.namespace == ann.namespace
    assert ann_trim.annotation_metadata == ann.annotation_metadata

    expected_data = dict(time=[5.0, 5.0],
                         duration=[2.0, 3.0],
                         value=['one', 'two'],
                         confidence=[0.9, 0.9])
    expected_ann = jams.Annotation(namespace, data=expected_data, time=5.0,
                                   duration=3.0)
    eq_(ann_trim.data, expected_ann.data)

    # strict=True
    ann_trim = ann.trim(0, 8, strict=True)

    assert ann_trim.time == 5
    assert ann_trim.duration == 3
    assert ann_trim.sandbox.trim == [{'start_time': 0, 'end_time': 8,
                                      'trim_start': 5, 'trim_end': 8}]
    assert ann_trim.namespace == ann.namespace
    assert ann_trim.annotation_metadata == ann.annotation_metadata

    expected_data = dict(time=[5.0],
                         duration=[2.0],
                         value=['one'],
                         confidence=[0.9])
    expected_ann = jams.Annotation(namespace, data=expected_data, time=5.0,
                                   duration=3.0)
    eq_(ann_trim.data, expected_ann.data)


def test_annotation_trim_partial_overlap_end():
    # When the trim region only partially overlaps with the annotation time
    # range: at the end
    # strict=False
    namespace = 'tag_open'
    data = dict(time=[5.0, 5.0, 10.0],
                duration=[2.0, 4.0, 4.0],
                value=['one', 'two', 'three'],
                confidence=[0.9, 0.9, 0.9])
    ann = jams.Annotation(namespace, data=data, time=5.0, duration=10.0)

    ann_trim = ann.trim(8, 20, strict=False)

    assert ann_trim.time == 8
    assert ann_trim.duration == 7
    assert ann_trim.sandbox.trim == [{'start_time': 8, 'end_time': 20,
                                      'trim_start': 8, 'trim_end': 15}]
    assert ann_trim.namespace == ann.namespace
    assert ann_trim.annotation_metadata == ann.annotation_metadata

    expected_data = dict(time=[8.0, 10.0],
                         duration=[1.0, 4.0],
                         value=['two', 'three'],
                         confidence=[0.9, 0.9])
    expected_ann = jams.Annotation(namespace, data=expected_data, time=8.0,
                                   duration=7.0)
    eq_(ann_trim.data, expected_ann.data)

    # strict=True
    ann_trim = ann.trim(8, 20, strict=True)

    assert ann_trim.time == 8
    assert ann_trim.duration == 7
    assert ann_trim.sandbox.trim == [{'start_time': 8, 'end_time': 20,
                                      'trim_start': 8, 'trim_end': 15}]
    assert ann_trim.namespace == ann.namespace
    assert ann_trim.annotation_metadata == ann.annotation_metadata

    expected_data = dict(time=[10.0],
                         duration=[4.0],
                         value=['three'],
                         confidence=[0.9])
    expected_ann = jams.Annotation(namespace, data=expected_data, time=8.0,
                                   duration=7.0)
    eq_(ann_trim.data, expected_ann.data)


def test_annotation_trim_multiple():
    # Multiple trims
    # strict=False
    namespace = 'tag_open'
    data = dict(time=[5.0, 5.0, 10.0],
                duration=[2.0, 4.0, 4.0],
                value=['one', 'two', 'three'],
                confidence=[0.9, 0.9, 0.9])
    ann = jams.Annotation(namespace, data=data, time=5.0, duration=10.0)

    ann_trim = ann.trim(0, 10, strict=False).trim(8, 20, strict=False)
    assert ann_trim.time == 8
    assert ann_trim.duration == 2
    assert ann_trim.sandbox.trim == (
        [{'start_time': 0, 'end_time': 10, 'trim_start': 5, 'trim_end': 10},
         {'start_time': 8, 'end_time': 20, 'trim_start': 8, 'trim_end': 10}])
    assert ann_trim.namespace == ann.namespace
    assert ann_trim.annotation_metadata == ann.annotation_metadata

    expected_data = dict(time=[8.0],
                         duration=[1.0],
                         value=['two'],
                         confidence=[0.9])

    expected_ann = jams.Annotation(namespace, data=expected_data, time=8.0,
                                   duration=2.0)
    eq_(ann_trim.data, expected_ann.data)

    # strict=True
    ann_trim = ann.trim(0, 10, strict=True).trim(8, 20, strict=True)
    assert ann_trim.time == 8
    assert ann_trim.duration == 2
    # assert ann_trim.sandbox.trim == [(0, 10, 5, 10), (8, 20, 8, 10)]
    assert ann_trim.sandbox.trim == (
        [{'start_time': 0, 'end_time': 10, 'trim_start': 5, 'trim_end': 10},
         {'start_time': 8, 'end_time': 20, 'trim_start': 8, 'trim_end': 10}])
    assert ann_trim.namespace == ann.namespace
    assert ann_trim.annotation_metadata == ann.annotation_metadata

    expected_data = None
    expected_ann = jams.Annotation(namespace, data=expected_data, time=8.0,
                                   duration=2.0)
    eq_(ann_trim.data, expected_ann.data)


def test_jams_trim_no_duration():
    # If file duration not set, can't trim.
    @raises(jams.JamsError)
    def __test_error(jam, start_time, end_time, strict=False):
        return jam.trim(start_time, end_time, strict=strict)

    # Empty jam has no file metadata, can't trim!
    jam = jams.JAMS()
    __test_error(jam, 0, 1)


def test_jams_trim_bad_params():
    # If trim parameters aren't contained in file's duration, or if end time is
    # smaller than start time, can't trim.
    @raises(jams.ParameterError)
    def __test_error(jam, start_time, end_time, strict=False):
        return jam.trim(start_time, end_time, strict=strict)

    jam = jams.JAMS()
    jam.file_metadata.duration = 15

    # Can only trim if values are within time range spanned by jam and end_time
    # > start_time
    trim_times = [(-5, -1), (-5, 10), (-5, 20), (5, 20), (18, 20), (10, 8)]
    for tt in trim_times:
        yield __test_error, jam, tt[0], tt[1]


def test_jams_trim_valid():
    # For a valid scenario, ensure everything behaves as expected
    jam = jams.JAMS()
    jam.file_metadata.duration = 15

    namespace = 'tag_open'
    data = dict(time=[5.0, 5.0, 10.0],
                duration=[2.0, 4.0, 4.0],
                value=['one', 'two', 'three'],
                confidence=[0.9, 0.9, 0.9])
    ann = jams.Annotation(namespace, data=data, time=5.0, duration=10.0)
    for _ in range(5):
        jam.annotations.append(ann)

    ann_copy = jams.Annotation(namespace, data=data, time=5.0, duration=10.0)
    ann_trim = ann_copy.trim(0, 10, strict=False)
    jam_trim = jam.trim(0, 10, strict=False)

    for ann in jam_trim.annotations:
        eq_(ann.data, ann_trim.data)

    assert jam_trim.file_metadata.duration == jam.file_metadata.duration
    assert jam_trim.sandbox.trim == [{'start_time': 0, 'end_time': 10}]

    # Multiple trims
    jam_trim = jam.trim(0, 10).trim(8, 10)
    ann_trim = ann_copy.trim(0, 10).trim(8, 10)

    for ann in jam_trim.annotations:
        eq_(ann.data, ann_trim.data)

    assert jam_trim.sandbox.trim == (
        [{'start_time': 0, 'end_time': 10}, {'start_time': 8, 'end_time': 10}])

    # Make sure file metadata copied over correctly
    assert jam_trim.file_metadata == jam.file_metadata


def test_annotation_slice():

    namespace = 'tag_open'
    data = dict(time=[5.0, 6.0, 10.0],
                duration=[2.0, 4.0, 4.0],
                value=['one', 'two', 'three'],
                confidence=[0.9, 0.9, 0.9])
    ann = jams.Annotation(namespace, data=data, time=5.0, duration=10.0)

    # Slice out range that's completely inside the time range spanned by the
    # annotation
    ann_slice = ann.slice(8, 10, strict=False)
    expected_data = dict(time=[0.0],
                         duration=[2.0],
                         value=['two'],
                         confidence=[0.9])

    expected_ann = jams.Annotation(namespace, data=expected_data, time=0,
                                   duration=2.0)
    eq_(ann_slice.data, expected_ann.data)
    eq_(ann_slice.sandbox.slice,
        [{'start_time': 8, 'end_time': 10, 'slice_start': 8, 'slice_end': 10}])

    # Slice out range that's partially inside the time range spanned by the
    # annotation (starts BEFORE annotation starts)
    ann_slice = ann.slice(3, 10, strict=False)
    expected_data = dict(time=[2.0, 3.0],
                         duration=[2.0, 4.0],
                         value=['one', 'two'],
                         confidence=[0.9, 0.9])

    expected_ann = jams.Annotation(namespace, data=expected_data, time=2.0,
                                   duration=5.0)
    eq_(ann_slice.data, expected_ann.data)
    assert ann_slice.sandbox.slice == (
        [{'start_time': 3, 'end_time': 10, 'slice_start': 5, 'slice_end': 10}])

    # Slice out range that's partially inside the time range spanned by the
    # annotation (starts AFTER annotation starts)
    ann_slice = ann.slice(8, 20, strict=False)
    expected_data = dict(time=[0.0, 2.0],
                         duration=[2.0, 4.0],
                         value=['two', 'three'],
                         confidence=[0.9, 0.9])

    expected_ann = jams.Annotation(namespace, data=expected_data, time=0,
                                   duration=2.0)
    eq_(ann_slice.data, expected_ann.data)
    assert ann_slice.sandbox.slice == (
        [{'start_time': 8, 'end_time': 20, 'slice_start': 8, 'slice_end': 15}])

    # Multiple slices
    ann_slice = ann.slice(0, 10).slice(8, 10)
    expected_data = dict(time=[0.0],
                         duration=[2.0],
                         value=['two'],
                         confidence=[0.9])

    expected_ann = jams.Annotation(namespace, data=expected_data, time=0,
                                   duration=2.0)
    eq_(ann_slice.data, expected_ann.data)
    assert ann_slice.sandbox.slice == (
        [{'start_time': 0, 'end_time': 10, 'slice_start': 5, 'slice_end': 10},
         {'start_time': 8, 'end_time': 10, 'slice_start': 8, 'slice_end': 10}])


def test_jams_slice():

    @raises(jams.ParameterError, jams.JamsError)
    def __test_error(jam, start_time, end_time, strict=False):
        return jam.slice(start_time, end_time, strict=strict)

    # Empty jam has no file metadata, can't slice!
    jam = jams.JAMS()
    __test_error(jam, 0, 1)

    jam.file_metadata.duration = 15

    # Can only trim if values are within time range spanned by jam and end_time
    # > start_time
    slice_times = [(-5, -1), (-5, 10), (-5, 20), (5, 20), (18, 20), (10, 8)]
    for tt in slice_times:
        yield __test_error, jam, tt[0], tt[1]

    # For a valid scenario, ensure everything behaves as expected
    namespace = 'tag_open'
    data = dict(time=[5.0, 5.0, 10.0],
                duration=[2.0, 4.0, 4.0],
                value=['one', 'two', 'three'],
                confidence=[0.9, 0.9, 0.9])
    ann = jams.Annotation(namespace, data=data, time=5.0, duration=10.0)
    for _ in range(5):
        jam.annotations.append(ann)

    ann_copy = jams.Annotation(namespace, data=data, time=5.0, duration=10.0)
    ann_slice = ann_copy.slice(0, 10, strict=False)
    jam_slice = jam.slice(0, 10, strict=False)

    for ann in jam_slice.annotations:
        eq_(ann.data, ann_slice.data)

    assert jam_slice.file_metadata.duration == 10
    assert jam_slice.sandbox.slice == [{'start_time': 0, 'end_time': 10}]

    # Multiple trims
    jam_slice = jam.slice(0, 10).slice(8, 10)
    ann_slice = ann_copy.slice(0, 10).slice(8, 10)

    for ann in jam_slice.annotations:
        eq_(ann.data, ann_slice.data)

    assert jam_slice.sandbox.slice == (
        [{'start_time': 0, 'end_time': 10}, {'start_time': 8, 'end_time': 10}])

    # Make sure file metadata copied over correctly (except for duration)
    orig_metadata = dict(jam.file_metadata)
    slice_metadata = dict(jam_slice.file_metadata)
    del orig_metadata['duration']
    del slice_metadata['duration']
    assert slice_metadata == orig_metadata
    assert jam_slice.file_metadata.duration == 2


def test_annotation_data_frame():
    namespace = 'tag_open'
    data = dict(time=[5.0, 5.0, 10.0],
                duration=[2.0, 4.0, 4.0],
                value=['one', 'two', 'three'],
                confidence=[0.9, 0.9, 0.9])
    ann = jams.Annotation(namespace, data=data, time=5.0, duration=10.0)

    df = ann.to_dataframe()

    eq_(list(df.columns), ['time', 'duration', 'value', 'confidence'])

    for i, row in df.iterrows():
        eq_(row.time, data['time'][i])
        eq_(row.duration, data['duration'][i])
        eq_(row.value, data['value'][i])
        eq_(row.confidence, data['confidence'][i])
