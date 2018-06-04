#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''namespace conversion tests'''

import numpy as np

import pytest
import jams
from jams import NamespaceError


@pytest.mark.xfail(raises=NamespaceError)
def test_bad_target():

    ann = jams.Annotation(namespace='tag_open')
    ann.append(time=0, duration=1, value='foo', confidence=1)

    jams.convert(ann, 'bad namespace')


@pytest.mark.parametrize('target',
                         ['pitch_hz', 'pitch_midi', 'segment_open',
                          'tag_open', 'beat', 'chord'])
@pytest.mark.xfail(raises=NamespaceError)
def test_bad_sources(target):

    ann = jams.Annotation(namespace='vector')
    jams.convert(ann, target)


@pytest.mark.parametrize('namespace', list(jams.schema.__NAMESPACE__.keys()))
def test_noop(namespace):

    ann = jams.Annotation(namespace=namespace)
    a2 = jams.convert(ann, namespace)
    assert ann == a2


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
    assert ann2.namespace == 'pitch_contour'

    # Check index values
    assert ann2.data[0].value['index'] == 0
    assert ann2.data[-1].value['index'] == 0

    # Check frequency
    assert np.abs(ann2.data[0].value['frequency'] == np.abs(values[0]))
    assert np.abs(ann2.data[-1].value['frequency'] == np.abs(values[-1]))

    # Check voicings
    assert not ann2.data[0].value['voiced']
    assert ann2.data[-1].value['voiced']


def test_pitch_midi_to_contour():

    ann = jams.Annotation(namespace='pitch_midi')
    values = np.arange(100)

    times = np.linspace(0, 1, num=len(values))

    for t, v in zip(times, values):
        ann.append(time=t, value=v, duration=0)

    ann2 = jams.convert(ann, 'pitch_contour')
    ann.validate()
    ann2.validate()
    assert ann2.namespace == 'pitch_contour'

    # Check index values
    assert ann2.data[0].value['index'] == 0
    assert ann2.data[-1].value['index'] == 0

    # Check voicings
    assert ann2.data[-1].value['voiced']


def test_pitch_midi_to_hz():

    ann = jams.Annotation(namespace='pitch_midi')
    ann.append(time=0, duration=1, value=69, confidence=0.5)
    ann2 = jams.convert(ann, 'pitch_hz')
    ann.validate()
    ann2.validate()

    # Check the namespace
    assert ann2.namespace == 'pitch_hz'
    # midi 69 = 440.0 Hz
    assert ann2.data[0].value == 440.0

    # Check all else is equal
    assert len(ann.data) == len(ann2.data)

    for obs1, obs2 in zip(ann.data, ann2.data):
        assert obs1.time == obs2.time
        assert obs1.duration == obs2.duration
        assert obs1.confidence == obs2.confidence


def test_pitch_hz_to_midi():

    ann = jams.Annotation(namespace='pitch_hz')
    ann.append(time=0, duration=1, value=440.0, confidence=0.5)
    ann2 = jams.convert(ann, 'pitch_midi')
    ann.validate()
    ann2.validate()

    # Check the namespace
    assert ann2.namespace == 'pitch_midi'
    # midi 69 = 440.0 Hz
    assert ann2.data[0].value == 69

    # Check all else is equal
    assert len(ann.data) == len(ann2.data)

    for obs1, obs2 in zip(ann.data, ann2.data):
        assert obs1.time == obs2.time
        assert obs1.duration == obs2.duration
        assert obs1.confidence == obs2.confidence


def test_note_midi_to_hz():

    ann = jams.Annotation(namespace='note_midi')
    ann.append(time=0, duration=1, value=69, confidence=0.5)
    ann2 = jams.convert(ann, 'note_hz')
    ann.validate()
    ann2.validate()

    # Check the namespace
    assert ann2.namespace == 'note_hz'
    # midi 69 = 440.0 Hz
    assert ann2.data[0].value == 440.0

    # Check all else is equal
    assert len(ann.data) == len(ann2.data)

    for obs1, obs2 in zip(ann.data, ann2.data):
        assert obs1.time == obs2.time
        assert obs1.duration == obs2.duration
        assert obs1.confidence == obs2.confidence


def test_note_hz_to_midi():

    ann = jams.Annotation(namespace='note_hz')
    ann.append(time=0, duration=1, value=440.0, confidence=0.5)
    ann2 = jams.convert(ann, 'note_midi')
    ann.validate()
    ann2.validate()

    # Check the namespace
    assert ann2.namespace == 'note_midi'
    # midi 69 = 440.0 Hz
    assert ann2.data[0].value == 69

    # Check all else is equal
    assert len(ann.data) == len(ann2.data)

    for obs1, obs2 in zip(ann.data, ann2.data):
        assert obs1.time == obs2.time
        assert obs1.duration == obs2.duration
        assert obs1.confidence == obs2.confidence


def test_segment_open():

    ann = jams.Annotation(namespace='segment_salami_upper')
    ann.append(time=0, duration=1, value='A', confidence=0.5)
    ann2 = jams.convert(ann, 'segment_open')
    ann.validate()
    ann2.validate()

    # Check the namespace
    assert ann.namespace == 'segment_salami_upper'
    assert ann2.namespace == 'segment_open'

    # Check all else is equal
    assert ann.data == ann2.data


def test_tag_open():

    ann = jams.Annotation(namespace='tag_gtzan')
    ann.append(time=0, duration=1, value='reggae', confidence=0.5)
    ann2 = jams.convert(ann, 'tag_open')
    ann.validate()
    ann2.validate()

    # Check the namespace
    assert ann.namespace == 'tag_gtzan'
    assert ann2.namespace == 'tag_open'

    # Check all else is equal
    assert ann.data == ann2.data


def test_chord():

    ann = jams.Annotation(namespace='chord_harte')
    ann.append(time=0, duration=1, value='C:maj6', confidence=0.5)
    ann2 = jams.convert(ann, 'chord')
    ann.validate()
    ann2.validate()

    # Check the namespace
    assert ann.namespace == 'chord_harte'
    assert ann2.namespace == 'chord'

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
    assert ann2.namespace == 'beat'

    # Check all else is equal
    assert len(ann) == len(ann2)
    for obs1, obs2 in zip(ann.data, ann2.data):
        assert obs1.time == obs2.time
        assert obs1.duration == obs2.duration
        assert obs1.confidence == obs2.confidence


def test_scaper_tag_open():
    ann = jams.Annotation(namespace='scaper')

    value = {
        "source_time": 5,
        "event_duration": 0.5310546236891855,
        "event_time": 5.6543442662431795,
        "time_stretch": 0.8455598669219283,
        "pitch_shift": -1.2204911976305648,
        "snr": 7.790682558359417,
        "label": 'gun_shot',
        "role": "foreground",
        "source_file": "/audio/foreground/gun_shot/135544-6-17-0.wav"
    }

    ann.append(time=0, duration=1, value=value)

    ann2 = jams.convert(ann, 'tag_open')

    ann.validate()
    ann2.validate()
    assert ann2.namespace == 'tag_open'

    assert len(ann) == len(ann2)
    for obs1, obs2 in zip(ann.data, ann2.data):
        assert obs1.time == obs2.time
        assert obs1.duration == obs2.duration
        assert obs1.confidence == obs2.confidence
        assert obs1.value['label'] == obs2.value


def test_can_convert_equal():

    ann = jams.Annotation(namespace='chord')
    assert jams.nsconvert.can_convert(ann, 'chord')


def test_can_convert_cast():

    ann = jams.Annotation(namespace='tag_gtzan')
    assert jams.nsconvert.can_convert(ann, 'tag_open')


def test_can_convert_fail():

    ann = jams.Annotation(namespace='tag_gtzan')
    assert not jams.nsconvert.can_convert(ann, 'chord')
