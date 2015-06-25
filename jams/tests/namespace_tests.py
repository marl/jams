#!/usr/bin/env python
#CREATED:2015-05-26 12:47:35 by Brian McFee <brian.mcfee@nyu.edu>
"""Namespace schema tests"""

import numpy as np

from nose.tools import raises
from jams import SchemaError

from jams import Annotation


def test_ns_time_valid():

    ann = Annotation(namespace='onset')

    for time in np.arange(5.0, 10.0):
        ann.append(time=time, duration=0.0, value=None, confidence=None)

    ann.validate()


def test_ns_time_invalid():

    @raises(SchemaError)
    def __test(data):
        ann = Annotation(namespace='onset')
        ann.append(**data)

        ann.validate()

    # Check bad time
    yield __test, dict(time=-1, duration=0)

    # Check bad duration
    yield __test, dict(time=1, duration=-1)


def test_ns_beat_valid():

    # A valid example
    ann = Annotation(namespace='beat')
    
    for time in np.arange(5.0):
        ann.append(time=time, duration=0.0, value=1, confidence=None)

    for time in np.arange(5.0, 10.0):
        ann.append(time=time, duration=0.0, value=None, confidence=None)
    
    ann.validate()


@raises(SchemaError)
def test_ns_beat_invalid():

    ann = Annotation(namespace='beat')
    
    for time in np.arange(5.0):
        ann.append(time=time, duration=0.0, value='foo', confidence=None)

    ann.validate()


def test_ns_beat_position_valid():

    ann = Annotation(namespace='beat_position')

    ann.append(time=0, duration=1.0, value=dict(position=1,
                                                measure=1,
                                                num_beats=3,
                                                beat_units=4))
    
    ann.validate()


def test_ns_beat_position_invalid():

    @raises(SchemaError)
    def __test(value):
        ann = Annotation(namespace='beat_position')
        ann.append(time=0, duration=1.0, value=value)
        ann.validate()

    good_dict = dict(position=1, measure=1, num_beats=3, beat_units=4)

    # First, test the bad positions
    for pos in [-1, 0, 'a', None]:
        value = good_dict.copy()
        value['position'] = pos
        yield __test, value

    # Now test bad measures
    for measure in [-1, 1.0, 'a', None]:
        value = good_dict.copy()
        value['measure'] = measure
        yield __test, value

    # Now test bad num_beats
    for nb in [-1, 1.5, 'a', None]:
        value = good_dict.copy()
        value['num_beats'] = nb
        yield __test, value

    # Now test bad beat units
    for bu in [-1, 1.5, 3, 'a', None]:
        value = good_dict.copy()
        value['beat_units'] = bu
        yield __test, value

    # And test missing fields
    for field in good_dict.keys():
        value = good_dict.copy()
        del value[field]
        yield __test, value

    # And test non-object values
    yield __test, None


def test_ns_mood_thayer_valid():

    ann = Annotation(namespace='mood_thayer')

    ann.append(time=0, duration=1.0, value=[0.3, 2.0])

    ann.validate()


def test_ns_mood_thayer_invalid():

    @raises(SchemaError)
    def __test(value):
        ann = Annotation(namespace='mood_thayer')
        ann.append(time=0, duration=1.0, value=value)
        ann.validate()

    for value in [ [0], [0, 1, 2], ['a', 'b'], None, 0]:
        yield __test, value


def test_ns_onset():

    # A valid example
    ann = Annotation(namespace='onset')
    
    for time in np.arange(5.0):
        ann.append(time=time, duration=0.0, value=1, confidence=None)

    for time in np.arange(5.0, 10.0):
        ann.append(time=time, duration=0.0, value=None, confidence=None)
    
    ann.validate()


def test_ns_lyrics():

    def __test(lyric):
        ann = Annotation(namespace='lyrics')

        ann.append(time=0, duration=1, value=lyric)

        ann.validate()

    for line in ['Check yourself', u'before you wreck yourself']:
        yield __test, line

    for line in [23, None]:
        yield raises(SchemaError)(__test), line


def test_ns_tempo_valid():

    ann = Annotation(namespace='tempo')

    ann.append(time=0, duration=0, value=1, confidence=0.85)

    ann.validate()


def test_ns_tempo_invalid():

    @raises(SchemaError)
    def __test(value, confidence):
        ann = Annotation(namespace='tempo')

        ann.append(time=0, duration=0, value=value, confidence=confidence)

        ann.validate()


    for value in [-1, -0.5, 'a']:
        yield __test, value, 0.5

    for confidence in [-1, -0.5, 2.0, 'a']:
        yield __test, 120.0, confidence


def test_ns_pitch_hz_valid():

    ann = Annotation(namespace='pitch_hz')

    seq_len = 21 # should be odd
    times = np.arange(seq_len)
    durations = np.zeros(seq_len)
    values = np.linspace(-22050., 22050, seq_len) # includes 0 (odd symmetric)
    confidences = np.linspace(0, 1., seq_len)
    confidences[seq_len//2] = None # throw in a None confidence value

    for (t, d, v, c) in zip(times, durations, values, confidences):
        ann.append(time=t, duration=d, value=v, confidence=c)

    ann.validate()


def test_ns_pitch_hz_invalid():

    @raises(SchemaError)
    def __test(value):
        ann = Annotation(namespace='pitch_hz')
        ann.append(time=0, duration=0, value=value, confidence=0.5)
        ann.validate()

    # note: 1j should also be invalid, but currently not caught
    # by the schema validation and hence removed from the test
    for value in ['a', None, True]:
        yield __test, value


def test_ns_pitch_midi_valid():

    ann = Annotation(namespace='pitch_midi')

    seq_len = 21 # should be odd
    times = np.arange(seq_len)
    durations = np.zeros(seq_len)
    values = np.linspace(-108., 108, seq_len) # includes 0 (odd symmetric)
    confidences = np.linspace(0, 1., seq_len)
    confidences[seq_len//2] = None # throw in a None confidence value

    for (t, d, v, c) in zip(times, durations, values, confidences):
        ann.append(time=t, duration=d, value=v, confidence=c)

    ann.validate()


def test_ns_pitch_midi_invalid():

    @raises(SchemaError)
    def __test(value):
        ann = Annotation(namespace='pitch_midi')
        ann.append(time=0, duration=0, value=value, confidence=0.5)
        ann.validate()

    # note: 1j should also be invalid, but currently not caught
    # by the schema validation and hence removed from the test
    for value in ['a', None, True]:
        yield __test, value


def test_ns_key_mode():

    def __test(keymode):
        ann = Annotation(namespace='key_mode')

        ann.append(time=0, duration=0, value=keymode, confidence=None)

        ann.validate()

    for val in ['B#:locrian', u'A:minor', 'N', 'E']:
        yield __test, val

    for val in ['asdf', 'A&:phrygian', 11, '', ':dorian', None]:
        yield raises(SchemaError)(__test), val


def test_ns_chord_roman_valid():

    def __test(chord):
        ann = Annotation(namespace='chord_roman')

        ann.append(time=0, duration=1.0, value=chord)

        ann.validate()

    yield __test, dict(tonic='B', chord='bII7')

    yield __test, dict(tonic=u'Gb', chord=u'ii7/#V')


def test_ns_chord_roman_invalid():

    @raises(SchemaError)
    def __test(chord):
        ann = Annotation(namespace='chord_roman')

        ann.append(time=0, duration=1.0, value=chord)

        ann.validate()

    good_dict = dict(tonic='E', chord='iv64')

    # test bad tonics
    for tonic in [42, 'H', 'a', 'F#b', True, None]:
        value = good_dict.copy()
        value['tonic'] = tonic
        yield __test, value

    # test bad chords
    for chord in [64, 'z', 'i/V64', 'Ab', 'iiii', False, None]:
        value = good_dict.copy()
        value['chord'] = chord
        yield __test, value

    # test missing fields
    for field in good_dict.keys():
        value = good_dict.copy()
        del value[field]
        yield __test, value

    # test non-object values
    yield __test, None


def test_ns_pitch_class_valid():

    def __test(pitch):
        ann = Annotation(namespace='pitch_class')

        ann.append(time=0, duration=1.0, value=pitch)
        ann.append(time=1.0, duration=1.0, value=pitch)

        ann.validate()

    yield __test, dict(tonic='B', pitch=0)

    yield __test, dict(tonic=u'Gb', pitch=11)


def test_ns_pitch_class_invalid():

    @raises(SchemaError)
    def __test(pitch):
        ann = Annotation(namespace='pitch_class')

        ann.append(time=0, duration=1.0, value=pitch)
        ann.append(time=1.0, duration=1.0, value=pitch)

        ann.validate()

    good_dict = dict(tonic='E', pitch=7)

    # test bad tonics
    for tonic in [42, 'H', 'a', 'F#b', True, None]:
        value = good_dict.copy()
        value['tonic'] = tonic
        yield __test, value

    # test bad pitches
    for pitch in [1.5, 'xyz', '3', False, None]:
        value = good_dict.copy()
        value['pitch'] = pitch
        yield __test, value

    # test missing fields
    for field in good_dict.keys():
        value = good_dict.copy()
        del value[field]
        yield __test, value

    # test non-object values
    yield __test, None


def test_ns_segment_open():

    def __test(label):
        ann = Annotation(namespace='segment_open')

        ann.append(time=0, duration=1, value=label)

        ann.validate()

    for line in ['a segment', u'a unicode segment']:
        yield __test, line

    for line in [23, None]:
        yield raises(SchemaError)(__test), line

def test_ns_segment_salami_lower():

    def __test(label):
        ann = Annotation(namespace='segment_salami_lower')

        ann.append(time=0, duration=1, value=label)

        ann.validate()

    for line in ['a', "a'", "a'''", "silence", "Silence", u'a']:
        yield __test, line

    for line in [23, None, 'A', 'S', 'a23', '  Silence  23']:
        yield raises(SchemaError)(__test), line

def test_ns_segment_salami_upper():

    def __test(label):
        ann = Annotation(namespace='segment_salami_upper')

        ann.append(time=0, duration=1, value=label)

        ann.validate()

    for line in ['A', "A'", "A'''", "silence", "Silence", u'A']:
        yield __test, line

    for line in [23, None, 'a', 'a', 'A23', '  Silence  23']:
        yield raises(SchemaError)(__test), line

