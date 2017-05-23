#!/usr/bin/env python
# CREATED:2016-02-11 12:07:58 by Brian McFee <brian.mcfee@nyu.edu>
"""Sonification tests"""

import numpy as np
import pytest
from test_eval import create_hierarchy

import jams


@pytest.mark.xfail(raises=jams.NamespaceError)
def test_no_sonify():

    ann = jams.Annotation(namespace='vector')
    jams.sonify.sonify(ann)


@pytest.mark.xfail(raises=jams.SchemaError)
def test_bad_sonify():
    ann = jams.Annotation(namespace='chord')
    ann.append(time=0, duration=1, value='not a chord')

    jams.sonify.sonify(ann)


@pytest.mark.parametrize('ns', ['segment_open', 'chord'])
@pytest.mark.parametrize('sr', [8000, 11025])
@pytest.mark.parametrize('duration', [None, 5.0, 1.0])
def test_duration(ns, sr, duration):

    ann = jams.Annotation(namespace=ns)
    ann.append(time=3, duration=1, value='C')

    y = jams.sonify.sonify(ann, sr=sr, duration=duration)

    if duration is not None:
        assert len(y) == int(sr * duration)


def test_note_hz():
    ann = jams.Annotation(namespace='note_hz')
    ann.append(time=0, duration=1, value=261.0)
    y = jams.sonify.sonify(ann, sr=8000, duration=2.0)

    assert len(y) == 8000 * 2


def test_note_hz_nolength():
    ann = jams.Annotation(namespace='note_hz')
    ann.append(time=0, duration=1, value=261.0)
    y = jams.sonify.sonify(ann, sr=8000)

    assert len(y) == 8000 * 1
    assert np.any(y)


def test_note_midi():
    ann = jams.Annotation(namespace='note_midi')
    ann.append(time=0, duration=1, value=60)
    y = jams.sonify.sonify(ann, sr=8000, duration=2.0)

    assert len(y) == 8000 * 2


@pytest.fixture(scope='module')
def ann_contour():
    ann = jams.Annotation(namespace='pitch_contour')

    duration = 5.0
    fs = 0.01
    # Generate a contour with deep vibrato and no voicing from 3s-4s
    times = np.linspace(0, duration, num=int(duration / fs))
    rate = 5
    vibrato = 220 + 20 * np.sin(2 * np.pi * times * rate)

    for t, v in zip(times, vibrato):
        ann.append(time=t, duration=fs, value={'frequency': v,
                                               'index': 0,
                                               'voiced': (t < 3 or t > 4)})

    return ann


@pytest.mark.parametrize('duration', [None, 5.0, 10.0])
@pytest.mark.parametrize('sr', [8000])
def test_contour(ann_contour, duration, sr):
    y = jams.sonify.sonify(ann_contour, sr=sr, duration=duration)
    if duration is not None:
        assert len(y) == sr * duration


@pytest.mark.parametrize('namespace', ['chord', 'chord_harte'])
@pytest.mark.parametrize('sr', [8000])
@pytest.mark.parametrize('duration', [2.0])
@pytest.mark.parametrize('value', ['C:maj/5'])
def test_chord(namespace, sr, duration, value):

    ann = jams.Annotation(namespace=namespace)
    ann.append(time=0.5, duration=1.0, value=value)
    y = jams.sonify.sonify(ann, sr=sr, duration=duration)

    assert len(y) == sr * duration


@pytest.mark.parametrize('namespace, value',
                         [('beat', 1),
                          ('segment_open', 'C'),
                          ('onset', 1)])
@pytest.mark.parametrize('sr', [8000])
@pytest.mark.parametrize('duration', [2.0])
def test_event(namespace, sr, duration, value):

    ann = jams.Annotation(namespace=namespace)
    ann.append(time=0.5, duration=0, value=value)
    y = jams.sonify.sonify(ann, sr=sr, duration=duration)
    assert len(y) == sr * duration


@pytest.fixture(scope='module')
def beat_pos_ann():
    ann = jams.Annotation(namespace='beat_position')

    for i, t in enumerate(np.arange(0, 10, 0.25)):
        ann.append(time=t, duration=0,
                   value=dict(position=1 + i % 4,
                              measure=1 + i // 4,
                              num_beats=4,
                              beat_units=4))
    return ann


@pytest.mark.parametrize('sr', [8000])
@pytest.mark.parametrize('duration', [None, 5, 15])
def test_beat_position(beat_pos_ann, sr, duration):

    yout = jams.sonify.sonify(beat_pos_ann, sr=sr, duration=duration)
    if duration is not None:
        assert len(yout) == duration * sr


@pytest.fixture(scope='module')
def ann_hier():
    return create_hierarchy(values=['AB', 'abac', 'xxyyxxzz'], duration=30)


@pytest.mark.parametrize('sr', [8000])
@pytest.mark.parametrize('duration', [None, 15, 30])
def test_multi_segment(ann_hier, sr, duration):
    y = jams.sonify.sonify(ann_hier, sr=sr, duration=duration)
    if duration:
        assert len(y) == duration * sr
