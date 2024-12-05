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

import pytest
import numpy as np

import jams


xfail = pytest.mark.xfail
parametrize = pytest.mark.parametrize


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

    assert data == jdict


def test_jobject_serialize():

    data = dict(key1='value 1', key2='value 2')

    json_data = json.dumps(data, indent=2)

    J = jams.JObject(**data)

    # Stick a dummy _value in for testing
    J._dummy = True

    json_jobject = J.dumps(indent=2)

    # De-serialize into dicts
    assert json.loads(json_data) == json.loads(json_jobject)


def test_jobject_deserialize():

    data = dict(key1='value 1', key2='value 2')

    J = jams.JObject(**data)

    json_jobject = J.dumps(indent=2)

    assert J == jams.JObject.loads(json_jobject)


@parametrize('d1', [dict(key1='value 1', key2='value 2')])
@parametrize('d2, match',
             [(dict(key1='value 1', key2='value 2'), True),
              (dict(key1='value 1', key2='value 3'), False)])
def test_jobject_eq(d1, d2, match):
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


@parametrize('data, value', [({'key': True}, True), ({}, False)])
def test_jobject_nonzero(data, value):

    J = jams.JObject(**data)
    assert J.__nonzero__() == value


def test_jobject_repr():
    assert (repr(jams.JObject(foo=1, bar=2)) ==
            '<JObject(bar=2,\n         foo=1)>')


def test_jobject_repr_html():
    # Test once with empty
    J2 = jams.JObject()
    J2._repr_html_()

    # And once with some nested values
    J = jams.JObject(foo=1, bar=dict(baz=3), qux=[1], quux=None)
    J._repr_html_()


# Sandbox
def test_sandbox():

    data = dict(key1='value 1', key2='value 2')

    J = jams.Sandbox(**data)

    for key, value in six.iteritems(data):
        assert value == J[key]


def test_sandbox_contains():
    d = dict(foo=5, bar=9)
    S = jams.Sandbox(**d)

    for key in d:
        assert key in S


# Curator
def test_curator():

    c = jams.Curator(name='myself', email='you@me.com')

    assert c.name == 'myself'
    assert c.email == 'you@me.com'


# AnnotationMetadata
@pytest.fixture
def ann_meta_dummy():
    return dict(version='0',
                corpus='test',
                annotation_tools='nose',
                annotation_rules='brains',
                validation='unnecessary',
                data_source='null')


@parametrize('curator', [None, jams.Curator(name='nobody',
                                            email='none@none.com')])
@parametrize('annotator', [None, jams.Sandbox(description='desc')])
def test_annotation_metadata(ann_meta_dummy, curator, annotator):

    md = jams.AnnotationMetadata(curator=curator, annotator=annotator,
                                 **ann_meta_dummy)

    if curator is not None:
        assert dict(md.curator) == dict(curator)

    if annotator is not None:
        assert dict(md.annotator) == dict(annotator)

    real_data = dict(md)
    real_data.pop('curator')
    real_data.pop('annotator')
    assert real_data == ann_meta_dummy


# Annotation
@pytest.fixture(scope='module')
def tag_data():
    return [dict(time=0, duration=0.5, value='one', confidence=0.9),
            dict(time=1.0, duration=0.5, value='two', confidence=0.9)]


@pytest.fixture(scope='module')
def ann_sandbox():
    return jams.Sandbox(description='ann_sandbox')


@pytest.fixture(scope='module')
def ann_metadata():
    return jams.AnnotationMetadata(corpus='test collection')


@parametrize('namespace', ['tag_open'])
def test_annotation(namespace, tag_data, ann_metadata, ann_sandbox):
    ann = jams.Annotation(namespace, data=tag_data,
                          annotation_metadata=ann_metadata,
                          sandbox=ann_sandbox)

    assert namespace == ann.namespace

    assert dict(ann_metadata) == dict(ann.annotation_metadata)

    assert dict(ann_sandbox) == dict(ann.sandbox)

    assert len(ann.data) == len(tag_data)
    for obs1, obs2 in zip(ann.data, tag_data):
        assert obs1._asdict() == obs2


def test_annotation_append():

    data = [dict(time=0, duration=0.5, value='one', confidence=0.9),
            dict(time=1.0, duration=0.5, value='two', confidence=0.9)]

    namespace = 'tag_open'

    ann = jams.Annotation(namespace, data=data)

    update = dict(time=2.0, duration=1.0, value='three', confidence=0.8)

    ann.append(**update)

    assert ann.data[-1]._asdict() == update


def test_annotation_eq(tag_data):
    namespace = 'tag_open'

    ann1 = jams.Annotation(namespace, data=tag_data)
    ann2 = jams.Annotation(namespace, data=tag_data)

    assert ann1 == ann2

    # Test the type-check in equality
    assert not (ann1 == tag_data)

    update = dict(time=2.0, duration=1.0, value='three', confidence=0.8)

    ann2.append(**update)

    assert not (ann1 == ann2)


def test_annotation_iterator():

    data = [dict(time=0, duration=0.5, value='one', confidence=0.2),
            dict(time=1, duration=1, value='two', confidence=0.5)]

    namespace = 'tag_open'

    ann = jams.Annotation(namespace, data=data)

    for obs, obs_raw in zip(ann, data):
        assert isinstance(obs, jams.Observation)
        assert obs._asdict() == obs_raw, (obs, obs_raw)


def test_annotation_interval_values(tag_data):

    ann = jams.Annotation(namespace='tag_open', data=tag_data)

    intervals, values = ann.to_interval_values()

    assert np.allclose(intervals, np.array([[0.0, 0.5], [1.0, 1.5]]))
    assert values == ['one', 'two']


@xfail(raises=jams.JamsError)
def test_annotation_badtype():

    an = jams.Annotation(namespace='tag_open')
    # This should throw a jams error because NoneType can't be indexed
    an.data.add(None)


# FileMetadata
def test_filemetadata():

    meta = dict(title='Test track',
                artist='Test artist',
                release='Test release',
                duration=31.3)
    fm = jams.FileMetadata(**meta)
    dict_fm = dict(fm)

    for k in meta:
        assert meta[k] == dict_fm[k]


@parametrize('strict', [False, xfail(True, raises=jams.SchemaError)])
def test_filemetadata_validation(strict):

    # This should fail validation because null duration is not allowed
    fm = jams.FileMetadata(title='Test track',
                           artist='Test artist',
                           release='Test release',
                           duration=None)

    clean_warning_registry()

    with warnings.catch_warnings(record=True) as out:
        fm.validate(strict=strict)

        assert len(out) > 0
        assert out[0].category is UserWarning
        assert 'failed validating' in str(out[0].message).lower()


# AnnotationArray
def test_annotation_array():

    arr = jams.AnnotationArray()

    assert len(arr) == 0


def test_annotation_array_data(tag_data):

    ann = jams.Annotation('tag_open', data=tag_data)
    arr = jams.AnnotationArray(annotations=[ann, ann])

    assert len(arr) == 2
    arr.append(ann)

    assert len(arr) == 3

    for t_ann in arr:
        assert ann.data == t_ann.data


def test_annotation_array_serialize(tag_data):

    namespace = 'tag_open'
    ann = jams.Annotation(namespace, data=tag_data)

    arr = jams.AnnotationArray(annotations=[ann, ann])

    arr_js = arr.__json__

    arr2 = jams.AnnotationArray(annotations=arr_js)

    assert arr == arr2


def test_annotation_array_index_simple():

    jam = jams.JAMS()

    anns = [jams.Annotation('beat') for _ in range(5)]

    for ann in anns:
        jam.annotations.append(ann)

    assert len(jam.annotations) == len(anns)
    for i in range(5):
        a1, a2 = anns[i], jam.annotations[i]
        assert a1 == a2


def test_annotation_array_slice_simple():

    jam = jams.JAMS()

    anns = [jams.Annotation('beat') for _ in range(5)]

    for ann in anns:
        jam.annotations.append(ann)

    res = jam.annotations[:3]
    assert len(res) == 3
    assert anns[0] in res


def test_annotation_array_index_fancy():

    jam = jams.JAMS()
    ann = jams.Annotation(namespace='beat')
    jam.annotations.append(ann)

    # We should have exactly one beat annotation
    res = jam.annotations['beat']
    assert len(res) == 1
    assert res[0] == ann

    # Any other namespace should give an empty list
    assert jam.annotations['segment'] == []


def test_annotation_array_composite():

    jam = jams.JAMS()
    for _ in range(10):
        ann = jams.Annotation(namespace='beat')
        jam.annotations.append(ann)

    assert len(jam.annotations['beat', :3]) == 3
    assert len(jam.annotations['beat', 3:]) == 7
    assert len(jam.annotations['beat', 2::2]) == 4


@xfail(raises=IndexError)
def test_annotation_array_index_error():

    jam = jams.JAMS()
    ann = jams.Annotation(namespace='beat')
    jam.annotations.append(ann)
    jam.annotations[None]


# JAMS
@pytest.fixture(scope='module')
def file_metadata():
    return jams.FileMetadata(title='Test track', artist='Test artist',
                             release='Test release', duration=31.3)


def test_jams(tag_data, file_metadata, ann_sandbox):
    ann = jams.Annotation('tag_open', data=tag_data)
    annotations = jams.AnnotationArray(annotations=[ann])

    jam = jams.JAMS(annotations=annotations,
                    file_metadata=file_metadata,
                    sandbox=ann_sandbox)

    assert dict(file_metadata) == dict(jam.file_metadata)
    assert dict(ann_sandbox) == dict(jam.sandbox)
    assert annotations == jam.annotations


@pytest.fixture(params=['jams', 'jamz'])
def output_path(request):

    _, jam_out = tempfile.mkstemp(suffix='.{:s}'.format(request.param))

    yield jam_out

    os.unlink(jam_out)


@pytest.fixture(scope='module')
def input_jam():
    return jams.load('tests/fixtures/valid.jams')


def test_jams_save(input_jam, output_path):

    input_jam.save(output_path)
    reload_jam = jams.load(output_path)
    assert input_jam == reload_jam


def test_jams_add(tag_data):

    fn = 'tests/fixtures/valid.jams'

    # The original jam
    jam_orig = jams.load(fn)
    jam = jams.load(fn)

    # Make a new jam with the same metadata and different data
    jam2 = jams.load(fn)
    ann = jams.Annotation('tag_open', data=tag_data)
    jam2.annotations = jams.AnnotationArray(annotations=[ann])

    # Add the two
    jam.add(jam2)

    assert len(jam.annotations) == 3
    assert jam.annotations[:-1] == jam_orig.annotations
    assert jam.annotations[-1] == jam2.annotations[0]


@parametrize('on_conflict',
             ['overwrite', 'ignore',
              xfail('fail', raises=jams.JamsError),
              xfail('bad_fail_mdoe', raises=jams.ParameterError)])
def test_jams_add_conflict(on_conflict):
    fn = 'tests/fixtures/valid.jams'

    # The original jam
    jam = jams.load(fn)
    jam_orig = jams.load(fn)

    # The copy
    jam2 = jams.load(fn)

    jam2.file_metadata = jams.FileMetadata()

    jam.add(jam2, on_conflict=on_conflict)

    if on_conflict == 'overwrite':
        assert jam.file_metadata == jam2.file_metadata
    elif on_conflict == 'ignore':
        assert jam.file_metadata == jam_orig.file_metadata


@pytest.fixture(scope='module')
def jam_search():
    jam = jams.load('tests/fixtures/valid.jams', validate=False)
    jam.annotations[0].sandbox.foo = None
    return jam


@parametrize('query, expected',
             [(dict(corpus='SMC_MIREX'), jam_search().annotations),
              (dict(), []),
              (dict(namespace='beat'), jam_search().annotations[:1]),
              (dict(namespace='tag_open'), jam_search().annotations[1:]),
              (dict(namespace='segment_tut'), jams.AnnotationArray()),
              (dict(foo='bar'), jams.AnnotationArray())])
def test_jams_search(jam_search, query, expected):

    result = jam_search.search(**query)

    assert result == expected


def test_jams_validate_good():

    fn = 'tests/fixtures/valid.jams'
    j1 = jams.load(fn, validate=False)

    j1.validate()

    j1.file_metadata.validate()


@pytest.fixture(scope='module')
def jam_validate():
    j1 = jams.load('tests/fixtures/invalid.jams', validate=False)
    return j1


@parametrize('strict', [False, xfail(True, raises=jams.SchemaError)])
def test_jams_validate_bad(jam_validate, strict):

    clean_warning_registry()

    with warnings.catch_warnings(record=True) as out:
        jam_validate.validate(strict=strict)

    assert len(out) > 0
    assert out[0].category is UserWarning
    assert 'failed validating' in str(out[0].message).lower()


@xfail(raises=jams.SchemaError)
def test_jams_bad_field():
    jam = jams.JAMS()

    jam.out_of_schema = None


@parametrize('strict', [False, xfail(True, raises=jams.SchemaError)])
def test_jams_bad_annotation(strict):
    jam = jams.JAMS()
    jam.file_metadata.duration = 10

    jam.annotations.append('not an annotation')

    clean_warning_registry()

    with warnings.catch_warnings(record=True) as out:
        jam.validate(strict=strict)

    assert len(out) > 0
    assert out[0].category is UserWarning
    assert 'is not a well-formed jams annotation' in str(out[0].message).lower()


@parametrize('strict', [False, xfail(True, raises=jams.SchemaError)])
def test_jams_bad_jam(strict):
    jam = jams.JAMS()

    clean_warning_registry()

    with warnings.catch_warnings(record=True) as out:
        jam.validate(strict=strict)

    assert len(out) > 0
    assert out[0].category is UserWarning
    assert 'failed validating' in str(out[0].message).lower()


def test_jams_repr(input_jam):
    repr(input_jam)


def test_jams_repr_html(input_jam):
    input_jam._repr_html_()


def test_jams_str(input_jam):
    str(input_jam)


# Load
def test_load_fail():
    # 1. test bad file path
    # 2. test non-json file
    # 3. test bad extensions
    # 4. test bad codecs

    # Make a non-existent file
    tdir = tempfile.mkdtemp()
    with pytest.raises(IOError):
        jams.load(os.path.join(tdir, 'nonexistent.jams'), fmt='jams')
    os.rmdir(tdir)

    # Make a non-json file
    tdir = tempfile.mkdtemp()
    badfile = os.path.join(tdir, 'nonexistent.jams')
    with open(badfile, mode='w') as fp:
        fp.write('some garbage')

    with pytest.raises(ValueError):
        jams.load(os.path.join(tdir, 'nonexistent.jams'), fmt='jams')

    os.unlink(badfile)
    os.rmdir(tdir)

    tdir = tempfile.mkdtemp()
    for ext in ['txt', '']:
        badfile = os.path.join(tdir, 'nonexistent')
        with pytest.raises(jams.ParameterError):
            jams.load('{:s}.{:s}'.format(badfile, ext), fmt='auto')
        with pytest.raises(jams.ParameterError):
            jams.load('{:s}.{:s}'.format(badfile, ext), fmt=ext)
        with pytest.raises(jams.ParameterError):
            jams.load('{:s}.jams'.format(badfile, ext), fmt=ext)

    # one last test, trying to load form a non-file-like object
    with pytest.raises(jams.ParameterError):
        jams.load(None, fmt='auto')

    os.rmdir(tdir)


def test_load_valid():

    # 3. test good jams file with strict validation
    # 4. test good jams file without strict validation
    fn = 'tests/fixtures/valid'

    for ext in ['jams', 'jamz']:
        for validate in [False, True]:
            for strict in [False, True]:
                jams.load('{:s}.{:s}'.format(fn, ext),
                          validate=validate,
                          strict=strict)


def test_load_invalid():

    def __test_warn(filename, valid, strict):
        clean_warning_registry()

        with warnings.catch_warnings(record=True) as out:
            jams.load(filename, validate=valid, strict=strict)

        assert len(out) > 0
        assert out[0].category is UserWarning
        assert 'failed validating' in str(out[0].message).lower()

    # 5. test bad jams file with strict validation
    # 6. test bad jams file without strict validation
    fn = 'tests/fixtures/invalid.jams'

    # Test once with no validation
    jams.load(fn, validate=False, strict=False)

    # With validation, failure can either be a warning or an exception
    with pytest.raises(jams.SchemaError):
        jams.load(fn, validate=True, strict=True)

    __test_warn(fn, True, False)


@xfail(raises=jams.ParameterError)
def test_annotation_trim_bad_params():

    # end_time must be greater than start_time
    ann = jams.Annotation('tag_open')
    ann.trim(5, 3, strict=False)


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

    assert ann_trim.data == expected_ann.data


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

    assert ann_trim.data == expected_ann.data

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

    assert ann_trim.data == expected_ann.data


def test_annotation_trim_partial_overlap_beginning():
    # When the trim region only partially overlaps with the annotation time
    # range: at the beginning
    # strict=False
    namespace = 'tag_open'
    data = dict(time=[4.0, 5.0, 5.0, 5.0, 10.0],
                duration=[1.0, 0.0, 2.0, 4.0, 4.0],
                value=['none', 'zero', 'one', 'two', 'three'],
                confidence=[1, 0.1, 0.9, 0.9, 0.9])
    ann = jams.Annotation(namespace, data=data, time=5.0, duration=10.0)

    ann_trim = ann.trim(1, 8, strict=False)

    assert ann_trim.time == 5
    assert ann_trim.duration == 3
    assert ann_trim.sandbox.trim == [{'start_time': 1, 'end_time': 8,
                                      'trim_start': 5, 'trim_end': 8}]
    assert ann_trim.namespace == ann.namespace
    assert ann_trim.annotation_metadata == ann.annotation_metadata

    expected_data = dict(time=[5.0, 5.0, 5.0],
                         duration=[0.0, 2.0, 3.0],
                         value=['zero', 'one', 'two'],
                         confidence=[0.1, 0.9, 0.9])
    expected_ann = jams.Annotation(namespace, data=expected_data, time=5.0,
                                   duration=3.0)

    assert ann_trim.data == expected_ann.data

    # strict=True
    ann_trim = ann.trim(1, 8, strict=True)

    assert ann_trim.time == 5
    assert ann_trim.duration == 3
    assert ann_trim.sandbox.trim == [{'start_time': 1, 'end_time': 8,
                                      'trim_start': 5, 'trim_end': 8}]
    assert ann_trim.namespace == ann.namespace
    assert ann_trim.annotation_metadata == ann.annotation_metadata

    expected_data = dict(time=[5.0, 5.0],
                         duration=[0.0, 2.0],
                         value=['zero', 'one'],
                         confidence=[0.1, 0.9])
    expected_ann = jams.Annotation(namespace, data=expected_data, time=5.0,
                                   duration=3.0)

    assert ann_trim.data == expected_ann.data


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

    assert ann_trim.data == expected_ann.data

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

    assert ann_trim.data == expected_ann.data


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

    assert ann_trim.data == expected_ann.data

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

    assert ann_trim.data == expected_ann.data


@xfail(raises=jams.JamsError)
def test_jams_trim_no_duration():

    # Empty jam has no file metadata, can't trim!
    jam = jams.JAMS()
    jam.trim(0, 1, strict=False)


def test_jams_trim_bad_params():
    # If trim parameters aren't contained in file's duration, or if end time is
    # smaller than start time, can't trim.
    jam = jams.JAMS()
    jam.file_metadata.duration = 15

    # Can only trim if values are within time range spanned by jam and end_time
    # > start_time
    trim_times = [(-5, -1), (-5, 10), (-5, 20), (5, 20), (18, 20), (10, 8)]
    for tt in trim_times:
        with pytest.raises(jams.ParameterError):
            jam.trim(tt[0], tt[1], strict=False)


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
        assert ann.data == ann_trim.data

    assert jam_trim.file_metadata.duration == jam.file_metadata.duration
    assert jam_trim.sandbox.trim == [{'start_time': 0, 'end_time': 10}]

    # Multiple trims
    jam_trim = jam.trim(0, 10).trim(8, 10)
    ann_trim = ann_copy.trim(0, 10).trim(8, 10)

    for ann in jam_trim.annotations:
        assert ann.data == ann_trim.data

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

    assert ann_slice.data == expected_ann.data
    assert ann_slice.sandbox.slice == [{'start_time': 8,
                                        'end_time': 10,
                                        'slice_start': 8,
                                        'slice_end': 10}]
    assert ann_slice.time == expected_ann.time
    assert ann_slice.duration == expected_ann.duration

    # Slice out range that's partially inside the time range spanned by the
    # annotation (starts BEFORE annotation starts)
    ann_slice = ann.slice(3, 10, strict=False)
    expected_data = dict(time=[2.0, 3.0],
                         duration=[2.0, 4.0],
                         value=['one', 'two'],
                         confidence=[0.9, 0.9])

    expected_ann = jams.Annotation(namespace, data=expected_data, time=2.0,
                                   duration=5.0)
    assert ann_slice.time == expected_ann.time
    assert ann_slice.duration == expected_ann.duration

    assert ann_slice.data == expected_ann.data
    assert ann_slice.sandbox.slice == [{'start_time': 3,
                                        'end_time': 10,
                                        'slice_start': 5,
                                        'slice_end': 10}]

    # Slice out range that's partially inside the time range spanned by the
    # annotation (starts AFTER annotation starts)
    ann_slice = ann.slice(8, 20, strict=False)
    expected_data = dict(time=[0.0, 2.0],
                         duration=[2.0, 4.0],
                         value=['two', 'three'],
                         confidence=[0.9, 0.9])

    expected_ann = jams.Annotation(namespace, data=expected_data, time=0,
                                   duration=7.0)

    assert ann_slice.data == expected_ann.data
    assert ann_slice.sandbox.slice == (
        [{'start_time': 8, 'end_time': 20, 'slice_start': 8, 'slice_end': 15}])
    assert ann_slice.time == expected_ann.time
    assert ann_slice.duration == expected_ann.duration

    # Multiple slices
    ann_slice = ann.slice(0, 10).slice(8, 10)
    expected_data = dict(time=[0.0],
                         duration=[2.0],
                         value=['two'],
                         confidence=[0.9])

    expected_ann = jams.Annotation(namespace, data=expected_data, time=0,
                                   duration=2.0)

    assert ann_slice.data == expected_ann.data
    assert ann_slice.sandbox.slice == (
        [{'start_time': 0, 'end_time': 10, 'slice_start': 5, 'slice_end': 10},
         {'start_time': 8, 'end_time': 10, 'slice_start': 8, 'slice_end': 10}])
    assert ann_slice.time == expected_ann.time
    assert ann_slice.duration == expected_ann.duration


def test_jams_slice():

    # Empty jam has no file metadata, can't slice!
    jam = jams.JAMS()
    with pytest.raises((jams.ParameterError, jams.JamsError)):
        jam.slice(0, 1, strict=False)

    jam.file_metadata.duration = 15

    # Can only trim if values are within time range spanned by jam and end_time
    # > start_time
    slice_times = [(-5, -1), (-5, 10), (-5, 20), (5, 20), (18, 20), (10, 8)]
    for tt in slice_times:
        with pytest.raises((jams.ParameterError, jams.JamsError)):
            jam.slice(tt[0], tt[1], strict=False)

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
        assert ann.data == ann_slice.data

    assert jam_slice.file_metadata.duration == 10
    assert jam_slice.sandbox.slice == [{'start_time': 0, 'end_time': 10}]


    # Multiple trims
    jam_slice = jam.slice(0, 10).slice(8, 10)
    ann_slice = ann_copy.slice(0, 10).slice(8, 10)

    for ann in jam_slice.annotations:
        assert ann.data == ann_slice.data

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

    assert list(df.columns) == ['time', 'duration', 'value', 'confidence']

    for i, row in df.iterrows():
        assert row.time == data['time'][i]
        assert row.duration == data['duration'][i]
        assert row.value == data['value'][i]
        assert row.confidence == data['confidence'][i]


def test_deprecated():

    @jams.core.deprecated('old version', 'new version')
    def _foo():
        pass

    warnings.resetwarnings()
    warnings.simplefilter('always')
    with warnings.catch_warnings(record=True) as out:
        _foo()

        # And that the warning triggered
        assert len(out) > 0

        # And that the category is correct
        assert out[0].category is DeprecationWarning

        # And that it says the right thing (roughly)
        assert 'deprecated' in str(out[0].message).lower()


def test_numpy_serialize():
    # Test to trigger issue #159 - serializing numpy dtypes
    jobj = jams.JObject(key=np.float32(1.0))
    jobj.dumps()


def test_annotation_serialize():
    # Secondary test to trigger #159 on observation data
    ann = jams.Annotation(namespace='tag_open', duration=1.0)
    ann.append(time=np.float32(0), duration=np.float32(1),
               value=np.float32(5), confidence=np.float32(0.5))
    ann.dumps()


@pytest.mark.parametrize('confidence', [False, True])
def test_annotation_to_samples(confidence):

    ann = jams.Annotation('tag_open')

    ann.append(time=0, duration=0.5, value='one', confidence=0.1)
    ann.append(time=0.25, duration=0.5, value='two', confidence=0.2)
    ann.append(time=0.75, duration=0.5, value='three', confidence=0.3)
    ann.append(time=1.5, duration=0.5, value='four', confidence=0.4)

    values = ann.to_samples([0.2, 0.4, 0.75, 1.25, 1.75, 1.4], confidence=confidence)

    if confidence:
        values, confs = values
        assert confs == [[0.1], [0.1, 0.2], [0.2, 0.3], [0.3], [0.4], []]

    assert values == [['one'], ['one', 'two'], ['two', 'three'], ['three'], ['four'], []]

@pytest.mark.xfail(raises=jams.ParameterError)
def test_annotation_to_samples_fail_neg():

    ann = jams.Annotation('tag_open')

    ann.append(time=0, duration=0.5, value='one', confidence=0.1)
    ann.append(time=0.25, duration=0.5, value='two', confidence=0.2)
    ann.append(time=0.75, duration=0.5, value='three', confidence=0.3)
    ann.append(time=1.5, duration=0.5, value='four', confidence=0.4)

    values = ann.to_samples([-0.2, 0.4, 0.75, 1.25, 1.75, 1.4])


@pytest.mark.xfail(raises=jams.ParameterError)
def test_annotation_to_samples_fail_shape():

    ann = jams.Annotation('tag_open')

    ann.append(time=0, duration=0.5, value='one', confidence=0.1)
    ann.append(time=0.25, duration=0.5, value='two', confidence=0.2)
    ann.append(time=0.75, duration=0.5, value='three', confidence=0.3)
    ann.append(time=1.5, duration=0.5, value='four', confidence=0.4)

    values = ann.to_samples([[0.2, 0.4, 0.75, 1.25, 1.75, 1.4]])

