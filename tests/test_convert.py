#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''namespace conversion tests'''

import numpy as np
import numpy.testing as npt
import pandas.util.testing as pdt

from nose.tools import raises, eq_
import jams
from jams import NamespaceError


@raises(NamespaceError)
def test_bad_target():

    ann = jams.Annotation(namespace='tag_open')
    ann.append(time=0, duration=1, value='foo', confidence=1)

    jams.convert(ann, 'bad namespace')


def test_bad_sources():

    @raises(NamespaceError)
    def __test(ann, target):
        jams.convert(ann, target)

    ann = jams.Annotation(namespace='vector')
    for target in ['pitch_hz', 'pitch_midi', 'segment_open', 'tag_open', 'beat', 'chord']:
        yield __test, ann, target


def test_noop():

    def __test(ns):
        ann = jams.Annotation(namespace=ns)
        a2 = jams.convert(ann, ns)
        eq_(ann, a2)

    for ns in jams.schema.__NAMESPACE__:
        yield __test, ns


def test_pitch_hz_to_contour():

    ann = jams.Annotation(namespace='pitch_hz')
    values = np.linspace(110, 220, num=100)
    # Unvoice the first half
    values[::len(values)//2] *= -1

    times = np.linspace(0, 1, num=len(values))

    for t, v in zip(times, values):
        ann.append(time=t, value=v, duration=0)

    ann2 = jams.convert(ann, 'pitch_contour')
    ann.validate()
    ann2.validate()
    eq_(ann2.namespace, 'pitch_contour')

    # Check index values
    eq_(ann2.data.obs[0].value['index'], 0)
    eq_(ann2.data.obs[-1].value['index'], 0)

    # Check frequency
    eq_(np.abs(ann2.data.obs[0].value['frequency']), np.abs(values[0]))
    eq_(np.abs(ann2.data.obs[-1].value['frequency']), np.abs(values[-1]))

    # Check voicings
    assert not ann2.data.obs[0].value['voiced']
    assert ann2.data.obs[-1].value['voiced']


def test_pitch_midi_to_contour():

    ann = jams.Annotation(namespace='pitch_midi')
    values = np.arange(100)

    times = np.linspace(0, 1, num=len(values))

    for t, v in zip(times, values):
        ann.append(time=t, value=v, duration=0)

    ann2 = jams.convert(ann, 'pitch_contour')
    ann.validate()
    ann2.validate()
    eq_(ann2.namespace, 'pitch_contour')

    # Check index values
    eq_(ann2.data.obs[0].value['index'], 0)
    eq_(ann2.data.obs[-1].value['index'], 0)

    # Check voicings
    assert ann2.data.obs[-1].value['voiced']


def test_pitch_midi_to_hz():

    ann = jams.Annotation(namespace='pitch_midi')
    ann.append(time=0, duration=1, value=69, confidence=0.5)
    ann2 = jams.convert(ann, 'pitch_hz')
    ann.validate()
    ann2.validate()

    # Check the namespace
    eq_(ann2.namespace, 'pitch_hz')
    # midi 69 = 440.0 Hz
    eq_(ann2.data.obs[0].value, 440.0)

    # Check all else is equal
    eq_(len(ann.data), len(ann2.data))

    for obs1, obs2 in zip(ann.data, ann2.data):
        eq_(obs1.time, obs2.time)
        eq_(obs1.duration, obs2.duration)
        eq_(obs1.confidence, obs2.confidence)


def test_pitch_hz_to_midi():

    ann = jams.Annotation(namespace='pitch_hz')
    ann.append(time=0, duration=1, value=440.0, confidence=0.5)
    ann2 = jams.convert(ann, 'pitch_midi')
    ann.validate()
    ann2.validate()

    # Check the namespace
    eq_(ann2.namespace, 'pitch_midi')
    # midi 69 = 440.0 Hz
    eq_(ann2.data.obs[0].value, 69)

    # Check all else is equal
    eq_(len(ann.data), len(ann2.data))

    for obs1, obs2 in zip(ann.data, ann2.data):
        eq_(obs1.time, obs2.time)
        eq_(obs1.duration, obs2.duration)
        eq_(obs1.confidence, obs2.confidence)


def test_note_midi_to_hz():

    ann = jams.Annotation(namespace='note_midi')
    ann.append(time=0, duration=1, value=69, confidence=0.5)
    ann2 = jams.convert(ann, 'note_hz')
    ann.validate()
    ann2.validate()

    # Check the namespace
    eq_(ann2.namespace, 'note_hz')
    # midi 69 = 440.0 Hz
    eq_(ann2.data.obs[0].value, 440.0)

    # Check all else is equal
    eq_(len(ann.data), len(ann2.data))

    for obs1, obs2 in zip(ann.data, ann2.data):
        eq_(obs1.time, obs2.time)
        eq_(obs1.duration, obs2.duration)
        eq_(obs1.confidence, obs2.confidence)


def test_note_hz_to_midi():

    ann = jams.Annotation(namespace='note_hz')
    ann.append(time=0, duration=1, value=440.0, confidence=0.5)
    ann2 = jams.convert(ann, 'note_midi')
    ann.validate()
    ann2.validate()

    # Check the namespace
    eq_(ann2.namespace, 'note_midi')
    # midi 69 = 440.0 Hz
    eq_(ann2.data.obs[0].value, 69)

    # Check all else is equal
    eq_(len(ann.data), len(ann2.data))

    for obs1, obs2 in zip(ann.data, ann2.data):
        eq_(obs1.time, obs2.time)
        eq_(obs1.duration, obs2.duration)
        eq_(obs1.confidence, obs2.confidence)


def test_segment_open():

    ann = jams.Annotation(namespace='segment_salami_upper')
    ann.append(time=0, duration=1, value='A', confidence=0.5)
    ann2 = jams.convert(ann, 'segment_open')
    ann.validate()
    ann2.validate()

    # Check the namespace
    eq_(ann.namespace, 'segment_salami_upper')
    eq_(ann2.namespace, 'segment_open')

    # Check all else is equal
    eq_(ann.data, ann2.data)


def test_tag_open():

    ann = jams.Annotation(namespace='tag_gtzan')
    ann.append(time=0, duration=1, value='reggae', confidence=0.5)
    ann2 = jams.convert(ann, 'tag_open')
    ann.validate()
    ann2.validate()

    # Check the namespace
    eq_(ann.namespace, 'tag_gtzan')
    eq_(ann2.namespace, 'tag_open')

    # Check all else is equal
    eq_(ann.data, ann2.data)


def test_chord():

    ann = jams.Annotation(namespace='chord_harte')
    ann.append(time=0, duration=1, value='C:maj6', confidence=0.5)
    ann2 = jams.convert(ann, 'chord')
    ann.validate()
    ann2.validate()

    # Check the namespace
    eq_(ann.namespace, 'chord_harte', ann)
    eq_(ann2.namespace, 'chord', ann2)

    # Check all else is equal
    assert ann.data == ann2.data


def test_beat_position():

    ann = jams.Annotation(namespace='beat_position')
    ann.append(time=0, duration=0, confidence=0.5,
               value=dict(position=1, measure=0, num_beats=4, beat_units=4))
    ann.append(time=0.5, duration=0, confidence=0.5,
               value=dict(position=2, measure=0, num_beats=4, beat_units=4))
    ann.append(time=1, duration=0, confidence=0.5,
               value=dict(position=3, measure=0, num_beats=4, beat_units=4))
    ann.append(time=1.5, duration=0, confidence=0.5,
               value=dict(position=4, measure=0, num_beats=4, beat_units=4))

    ann2 = jams.convert(ann, 'beat')

    ann.validate()
    ann2.validate()

    # Check the namespace
    eq_(ann2.namespace, 'beat')

    # Check all else is equal
    eq_(len(ann), len(ann2))
    for obs1, obs2 in zip(ann.data, ann2.data):
        eq_(obs1.time, obs2.time)
        eq_(obs1.duration, obs2.duration)
        eq_(obs1.confidence, obs2.confidence)


def test_can_convert_equal():

    ann = jams.Annotation(namespace='chord')

    assert jams.nsconvert.can_convert(ann, 'chord')


def test_can_convert_cast():

    ann = jams.Annotation(namespace='tag_gtzan')

    assert jams.nsconvert.can_convert(ann, 'tag_open')


def test_can_convert_fail():

    ann = jams.Annotation(namespace='tag_gtzan')

    assert not jams.nsconvert.can_convert(ann, 'chord')

