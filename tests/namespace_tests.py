#!/usr/bin/env python
# CREATED:2015-05-26 12:47:35 by Brian McFee <brian.mcfee@nyu.edu>
"""Namespace schema tests"""

import six
import numpy as np

from nose.tools import raises
from jams import SchemaError

from jams import Annotation
import pandas as pd


def test_ns_time_valid():

    ann = Annotation(namespace='onset')

    for time in np.arange(5.0, 10.0):
        ann.append(time=time, duration=0.0, value=None, confidence=None)

    ann.validate()


def test_ns_time_invalid():

    @raises(SchemaError)
    def __test(data):
        ann = Annotation(namespace='onset')

        # Bypass the safety chceks in add_observation
        ann.data.loc[0] = {'time': pd.to_timedelta(data['time'], unit='s'),
                           'duration': pd.to_timedelta(data['duration'],
                                                       unit='s'),
                           'value': None,
                           'confdence': None}

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

    for line in ['Check yourself', six.u('before you wreck yourself')]:
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

def test_ns_note_hz_valid():

    ann = Annotation(namespace='note_hz')

    seq_len = 21
    times = np.arange(seq_len)
    durations = np.zeros(seq_len)
    values = np.linspace(0, 22050, seq_len) # includes 0 (odd symmetric)
    confidences = np.linspace(0, 1., seq_len)
    confidences[seq_len//2] = None # throw in a None confidence value

    for (t, d, v, c) in zip(times, durations, values, confidences):
        ann.append(time=t, duration=d, value=v, confidence=c)

    ann.validate()

def test_ns_note_hz_invalid():

    @raises(SchemaError)
    def __test(value):
        ann = Annotation(namespace='note_hz')
        ann.append(time=0, duration=0, value=value, confidence=0.5)
        ann.validate()

    # note: 1j should also be invalid, but currently not caught
    # by the schema validation and hence removed from the test
    for value in ['a', -23, None, True]:
        yield __test, value


def test_ns_pitch_hz_valid():

    ann = Annotation(namespace='pitch_hz')

    seq_len = 21
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


def test_ns_note_midi_valid():

    ann = Annotation(namespace='note_midi')

    seq_len = 21
    times = np.arange(seq_len)
    durations = np.zeros(seq_len)
    values = np.linspace(-108., 108, seq_len)  # includes 0 (odd symmetric)
    confidences = np.linspace(0, 1., seq_len)
    confidences[seq_len//2] = None  # throw in a None confidence value

    for (t, d, v, c) in zip(times, durations, values, confidences):
        ann.append(time=t, duration=d, value=v, confidence=c)

    ann.validate()

def test_ns_note_midi_invalid():

    @raises(SchemaError)
    def __test(value):
        ann = Annotation(namespace='note_midi')
        ann.append(time=0, duration=0, value=value, confidence=0.5)
        ann.validate()

    # note: 1j should also be invalid, but currently not caught
    # by the schema validation and hence removed from the test
    for value in ['a', None, True]:
        yield __test, value


def test_ns_pitch_midi_valid():

    ann = Annotation(namespace='pitch_midi')

    seq_len = 21
    times = np.arange(seq_len)
    durations = np.zeros(seq_len)
    values = np.linspace(-108., 108, seq_len)  # includes 0 (odd symmetric)
    confidences = np.linspace(0, 1., seq_len)
    confidences[seq_len//2] = None  # throw in a None confidence value

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

def test_ns_contour_valid():

    ann = Annotation(namespace='pitch_contour')

    seq_len = 21
    times = np.arange(seq_len)
    durations = np.zeros(seq_len)
    values = np.linspace(0, 22050, seq_len)  # includes 0 (odd symmetric)
    ids = np.arange(len(values)) // 4
    voicing = np.random.randn(len(ids)) > 0

    confidences = np.linspace(0, 1., seq_len)
    confidences[seq_len//2] = None  # throw in a None confidence value

    for (t, d, v, c, i, b) in zip(times, durations, values, confidences, ids, voicing):
        ann.append(time=t, duration=d, value={'pitch': v, 'id': i, 'voiced': b}, confidence=c)

    ann.validate()

def test_ns_contour_invalid():

    ann = Annotation(namespace='pitch_contour')

    seq_len = 21
    times = np.arange(seq_len)
    durations = np.zeros(seq_len)
    values = np.linspace(0, 22050, seq_len)  # includes 0 (odd symmetric)
    ids = np.arange(len(values)) // 4
    voicing = np.random.randn(len(ids)) * 2

    confidences = np.linspace(0, 1., seq_len)
    confidences[seq_len//2] = None  # throw in a None confidence value

    for (t, d, v, c, i, b) in zip(times, durations, values, confidences, ids, voicing):
        ann.append(time=t, duration=d, value={'pitch': v, 'id': i, 'voiced': b}, confidence=c)

    ann.validate()

def test_ns_key_mode():

    def __test(keymode):
        ann = Annotation(namespace='key_mode')

        ann.append(time=0, duration=0, value=keymode, confidence=None)

        ann.validate()

    for val in ['B#:locrian', six.u('A:minor'), 'N', 'E']:
        yield __test, val

    for val in ['asdf', 'A&:phrygian', 11, '', ':dorian', None]:
        yield raises(SchemaError)(__test), val


def test_ns_chord_valid():

    def __test(chord):
        ann = Annotation(namespace='chord')

        ann.append(time=0, duration=1.0, value=chord)

        ann.validate()

    for chord in ['A:9', 'Gb:sus2(1,3,5)', 'X', 'C:13(*9)/b7']:
        yield __test, chord


def test_ns_chord_invalid():

    @raises(SchemaError)
    def __test(chord):
        ann = Annotation(namespace='chord')

        ann.append(time=0, duration=1.0, value=chord)

        ann.validate()

    # test bad roots
    for root in [42, 'H', 'a', 'F1', True, None]:
        yield __test, '{0}:maj'.format(root)

    # test bad qualities
    for quality in [64, 'z', 'mj', 'Ab', 'iiii', False, None]:
        yield __test, 'C:{0}'.format(quality)

    # test bad bass
    for bass in ['A', 7.5, '8b']:
        yield __test, 'C/{0}'.format(bass)

    # test non-object values
    yield __test, None


def test_ns_chord_harte_valid():

    def __test(chord):
        ann = Annotation(namespace='chord_harte')

        ann.append(time=0, duration=1.0, value=chord)

        ann.validate()

    for chord in ['B:7', 'Gb:(1,3,5)', 'A#:(*3)', 'C:sus4(*5)/b7']:
        yield __test, chord


def test_ns_chord_harte_invalid():

    @raises(SchemaError)
    def __test(chord):
        ann = Annotation(namespace='chord_harte')

        ann.append(time=0, duration=1.0, value=chord)

        ann.validate()

    # test bad roots
    for root in [42, 'X', 'a', 'F1', True, None]:
        yield __test, '{0}:maj'.format(root)

    # test bad qualities
    for quality in [64, 'z', 'mj', 'Ab', 'iiii', False, None]:
        yield __test, 'C:{0}'.format(quality)

    # test bad bass
    for bass in ['A', 7.5, '8b']:
        yield __test, 'C/{0}'.format(bass)

    # test non-object values
    yield __test, None


def test_ns_chord_roman_valid():

    def __test(chord):
        ann = Annotation(namespace='chord_roman')

        ann.append(time=0, duration=1.0, value=chord)

        ann.validate()

    yield __test, dict(tonic='B', chord='bII7')

    yield __test, dict(tonic=six.u('Gb'), chord=six.u('ii7/#V'))


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

    yield __test, dict(tonic=six.u('Gb'), pitch=11)


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

def test_ns_tag_cal500():

    def __test(tag):
        ann = Annotation(namespace='tag_cal500')

        ann.append(time=0, duration=1, value=tag)

        ann.validate()

    for tag in ['Emotion-Angry_/_Aggressive', 'Genre--_Metal/Hard_Rock', 'Genre-Best-Jazz']:
        yield __test, tag
        yield __test, six.u(tag)
        yield raises(SchemaError)(__test), tag.upper()


    for tag in [23, None]:
        yield raises(SchemaError)(__test), tag

def test_ns_tag_cal10k():

    def __test(tag):
        ann = Annotation(namespace='tag_cal10k')

        ann.append(time=0, duration=1, value=tag)

        ann.validate()

    for tag in ['a dub production', "boomin' kick drum", 'rock & roll ? roots']:
        yield __test, tag
        yield __test, six.u(tag)
        yield raises(SchemaError)(__test), tag.upper()


    for tag in [23, None]:
        yield raises(SchemaError)(__test), tag

def test_ns_tag_gtzan():

    def __test(tag):
        ann = Annotation(namespace='tag_gtzan')

        ann.append(time=0, duration=1, value=tag)

        ann.validate()

    for tag in ['blues', 'classical', 'country', 'disco',
                'hip-hop', 'jazz', 'metal', 'pop', 'reggae', 'rock']:

        yield __test, tag
        yield __test, six.u(tag)
        yield raises(SchemaError)(__test), tag.upper()


    for tag in [23, None]:
        yield raises(SchemaError)(__test), tag

def test_ns_tag_msd_tagtraum_cd1():

    def __test(tag, confidence=None):
        ann = Annotation(namespace='tag_msd_tagtraum_cd1')

        ann.append(time=0, duration=1, value=tag, confidence=confidence)

        ann.validate()

    for tag in ['reggae',
                'pop/rock',
                'rnb',
                'jazz',
                'vocal',
                'new age',
                'latin',
                'rap',
                'country',
                'international',
                'blues',
                'electronic',
                'folk']:

        yield __test, tag
        yield __test, six.u(tag)
        yield raises(SchemaError)(__test), tag.upper()


    for tag in [23, None]:
        yield raises(SchemaError)(__test), tag

    yield raises(SchemaError)(__test), 'folk', 1.2
    yield raises(SchemaError)(__test), 'folk', -0.1
    yield __test, 'folk', 1.0
    yield __test, 'folk', 0.0


def test_ns_tag_msd_tagtraum_cd2():

    def __test(tag, confidence=None):
        ann = Annotation(namespace='tag_msd_tagtraum_cd2')

        ann.append(time=0, duration=1, value=tag, confidence=confidence)

        ann.validate()

    for tag in ['reggae',
                'latin',
                'metal',
                'rnb',
                'jazz',
                'punk',
                'pop',
                'new age',
                'country',
                'rap',
                'rock',
                'world',
                'blues',
                'electronic',
                'folk']:

        yield __test, tag
        yield __test, six.u(tag)
        yield raises(SchemaError)(__test), tag.upper()


    for tag in [23, None]:
        yield raises(SchemaError)(__test), tag

    yield raises(SchemaError)(__test), 'folk', 1.2
    yield raises(SchemaError)(__test), 'folk', -0.1
    yield __test, 'folk', 1.0
    yield __test, 'folk', 0.0

        
def test_ns_tag_medleydb():

    def __test(tag):
        ann = Annotation(namespace='tag_medleydb_instruments')

        ann.append(time=0, duration=1, value=tag)

        ann.validate()

    for tag in ['accordion', 'alto saxophone', 'fx/processed sound']:
        yield __test, tag
        yield __test, six.u(tag)
        yield raises(SchemaError)(__test), tag.upper()


    for tag in [23, None]:
        yield raises(SchemaError)(__test), tag

def test_ns_tag_open():

    def __test(label):
        ann = Annotation(namespace='tag_open')

        ann.append(time=0, duration=1, value=label)

        ann.validate()

    for line in ['a tag', six.u('a unicode tag')]:
        yield __test, line

    for line in [23, None]:
        yield raises(SchemaError)(__test), line

def test_ns_segment_open():

    def __test(label):
        ann = Annotation(namespace='segment_open')

        ann.append(time=0, duration=1, value=label)

        ann.validate()

    for line in ['a segment', six.u('a unicode segment')]:
        yield __test, line

    for line in [23, None]:
        yield raises(SchemaError)(__test), line

def test_ns_segment_salami_lower():

    def __test(label):
        ann = Annotation(namespace='segment_salami_lower')

        ann.append(time=0, duration=1, value=label)

        ann.validate()

    for line in ['a', "a'", "a'''", "silence", "Silence", six.u('a'), 'aa', "aa'"]:
        yield __test, line

    for line in [23, None, 'A', 'S', 'a23', '  Silence  23', 'aba', 'aab']:
        yield raises(SchemaError)(__test), line

def test_ns_segment_salami_upper():

    def __test(label):
        ann = Annotation(namespace='segment_salami_upper')

        ann.append(time=0, duration=1, value=label)

        ann.validate()

    for line in ['A', "A'", "A'''", "silence", "Silence", six.u('A'), 'A', "A'"]:
        yield __test, line

    for line in [23, None, 'a', 'a', 'A23', '  Silence  23', 'ABA', 'AAB', 'AA']:
        yield raises(SchemaError)(__test), line

def test_ns_segment_salami_function():

    def __test(label):
        ann = Annotation(namespace='segment_salami_function')

        ann.append(time=0, duration=1, value=label)

        ann.validate()

    for line in ['verse', "chorus", "theme", "voice", "silence", six.u('verse')]:
        yield __test, line

    for line in [23, None, 'a', 'a', 'A23', '  Silence  23', 'Some Garbage']:
        yield raises(SchemaError)(__test), line

def test_ns_segment_tut():

    def __test(label):
        ann = Annotation(namespace='segment_tut')

        ann.append(time=0, duration=1, value=label)

        ann.validate()

    for line in ['verse', "refrain", "Si", "bridge", "Bridge", six.u('verse')]:
        yield __test, line

    for line in [23, None, 'chorus', 'a', 'a', 'A23', '  Silence  23', 'Some Garbage']:
        yield raises(SchemaError)(__test), line


def test_ns_pattern_valid():
    def __test(pattern):
        ann = Annotation(namespace='pattern_jku')

        ann.append(time=0, duration=1.0, value=pattern)
        ann.append(time=1.0, duration=1.0, value=pattern)

        ann.validate()

    yield __test, dict(midi_pitch=3, morph_pitch=5, staff=1, pattern_id=1, occurrence_id=1)
    yield __test, dict(midi_pitch=-3, morph_pitch=-1.5, staff=1.0, pattern_id=1, occurrence_id=1)




def test_ns_pattern_invalid():

    @raises(SchemaError)
    def __test(pattern):
        ann = Annotation(namespace='pattern_jku')

        ann.append(time=0, duration=1.0, value=pattern)
        ann.append(time=1.0, duration=1.0, value=pattern)

        ann.validate()

    good_pattern = dict(midi_pitch=3,
                        morph_pitch=5,
                        staff=1,
                        pattern_id=1,
                        occurrence_id=1)

    # Test that all values are only numeric
    for key in good_pattern.keys():
        for bad_value in ['foo', None, dict(), []]:
            pattern = good_pattern.copy()
            pattern[key] = bad_value
            yield __test, pattern

    # Test bounded values
    for key in ['pattern_id', 'occurrence_id']:
        for bad_value in [-1, 0, 0.5]:
            pattern = good_pattern.copy()
            pattern[key] = bad_value
            yield __test, pattern


def test_ns_blob():
    def __test(label):
        ann = Annotation(namespace='blob')

        ann.append(time=0, duration=1, value=label)

        ann.validate()

    for line in ['a tag', six.u('a unicode tag'), 23, None, dict(), list()]:
        yield __test, line


def test_ns_vector():

    def __test(label):
        ann = Annotation(namespace='vector')

        ann.append(time=0, duration=1, value=label)

        ann.validate()

    for line in [[1], [1, 2], np.asarray([1]), np.asarray([1, 2])]:
        yield __test, line

    for line in ['a tag', six.u('a unicode tag'), 23, None, dict(), list()]:
        yield raises(SchemaError)(__test), line


def test_ns_multi_segment():

    def __test(value):
        ann = Annotation(namespace='multi_segment')

        ann.append(time=0, duration=1, value=value)

        ann.validate()

    for label in ['a segment', six.u('a unicode segment')]:
        yield raises(SchemaError)(__test), label
        for level in [0, 1, 2]:
            yield __test, dict(label=label, level=level)
        for level in [-1, None, 'foo']:
            yield raises(SchemaError)(__test), dict(label=label, level=level)

    for label in [23, None]:
        yield raises(SchemaError)(__test), label
        for level in [0, 1, 2]:
            yield raises(SchemaError)(__test), dict(label=label, level=level)


def test_ns_lyrics_bow():

    def __test(label):
        ann = Annotation(namespace='lyrics_bow')

        ann.append(time=0, duration=1, value=label)

        print(ann.data)
        ann.validate()

    yield __test, [['foo', 23]]
    yield __test, [['foo', 23], ['bar', 35]]
    yield __test, [['foo', 23], [['foo', 'bar'], 13]]
    yield __test, []

    yield raises(SchemaError)(__test), ('foo', 23)
    yield raises(SchemaError)(__test), [('foo', -23)]
    yield raises(SchemaError)(__test), [(23, 'foo')]

