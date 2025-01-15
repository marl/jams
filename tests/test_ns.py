#!/usr/bin/env python
# CREATED:2015-05-26 12:47:35 by Brian McFee <brian.mcfee@nyu.edu>
"""Namespace schema tests"""

import six
import numpy as np

import pytest

import jams
from jams import SchemaError

from jams import Annotation, Observation

from test_util import srand


parametrize = pytest.mark.parametrize


def test_ns_time_valid():

    ann = Annotation(namespace='onset')

    for time in np.arange(5.0, 10.0):
        ann.append(time=time, duration=0.0, value=None, confidence=None)

    ann.validate()


@parametrize('time, duration', [(-1, 0), (1, -1)])
def test_ns_time_invalid(time, duration):

    ann = Annotation(namespace='onset')

    # Bypass the safety checks in append
    ann.data.add(Observation(time=time, duration=duration,
                             value=None, confidence=None))

    with pytest.raises(jams.SchemaError):
        ann.validate()


def test_ns_beat_valid():

    # A valid example
    ann = Annotation(namespace='beat')

    for time in np.arange(5.0):
        ann.append(time=time, duration=0.0, value=1, confidence=None)

    for time in np.arange(5.0, 10.0):
        ann.append(time=time, duration=0.0, value=None, confidence=None)

    ann.validate()


def test_ns_beat_invalid():

    ann = Annotation(namespace='beat')

    for time in np.arange(5.0):
        ann.append(time=time, duration=0.0, value='foo', confidence=None)

    with pytest.raises(jams.SchemaError):
        ann.validate()


def test_ns_beat_position_valid():

    ann = Annotation(namespace='beat_position')

    ann.append(time=0, duration=1.0, value=dict(position=1,
                                                measure=1,
                                                num_beats=3,
                                                beat_units=4))

    ann.validate()


@parametrize('key, value',
             [('position', -1), ('position', 0),
              ('position', 'a'), ('position', None),
              ('measure', -1), ('measure', 1.0),
              ('measure', 'a'), ('measure', None),
              ('num_beats', -1), ('num_beats', 1.5),
              ('num_beats', 'a'), ('num_beats', None),
              ('beat_units', -1), ('beat_units', 1.5),
              ('beat_units', 3), ('beat_units', 'a'),
              ('beat_units', None)])
def test_ns_beat_position_invalid(key, value):

    data = dict(position=1, measure=1, num_beats=3, beat_units=4)
    data[key] = value

    ann = Annotation(namespace='beat_position')
    ann.append(time=0, duration=1.0, value=data)

    with pytest.raises(jams.SchemaError):
        ann.validate()


@parametrize('key',
             ['position', 'measure', 'num_beats', 'beat_units'])
def test_ns_beat_position_missing(key):

    data = dict(position=1, measure=1, num_beats=3, beat_units=4)
    del data[key]
    ann = Annotation(namespace='beat_position')
    ann.append(time=0, duration=1.0, value=data)

    with pytest.raises(jams.SchemaError):
        ann.validate()


def test_ns_mood_thayer_valid():

    ann = Annotation(namespace='mood_thayer')

    ann.append(time=0, duration=1.0, value=[0.3, 2.0])

    ann.validate()


@parametrize('value', [[0], [0, 1, 2], ['a', 'b'], None, 0])
def test_ns_mood_thayer_invalid(value):

    ann = Annotation(namespace='mood_thayer')
    ann.append(time=0, duration=1.0, value=value)
    with pytest.raises(jams.SchemaError):
        ann.validate()


def test_ns_onset():

    # A valid example
    ann = Annotation(namespace='onset')

    for time in np.arange(5.0):
        ann.append(time=time, duration=0.0, value=1, confidence=None)

    for time in np.arange(5.0, 10.0):
        ann.append(time=time, duration=0.0, value=None, confidence=None)

    ann.validate()


@parametrize('lyric',
             ['Check yourself', six.u('before you wreck yourself')])
def test_ns_lyrics(lyric):

    ann = Annotation(namespace='lyrics')
    ann.append(time=0, duration=1, value=lyric)
    ann.validate()


@parametrize('lyric', [23, None])
def test_ns_lyrics_invalid(lyric):
    ann = Annotation(namespace='lyrics')
    ann.append(time=0, duration=1, value=lyric)
    with pytest.raises(SchemaError):
        ann.validate()


def test_ns_tempo_valid():

    ann = Annotation(namespace='tempo')

    ann.append(time=0, duration=0, value=1, confidence=0.85)

    ann.validate()


@parametrize('value, confidence',
             [(-1, 0.5), (-0.5, 0.5), ('a', 0.5),
              (120.0, -1), (120.0, -0.5),
              (120.0, 2.0), (120.0, 'a')])
def test_ns_tempo_invalid(value, confidence):

    ann = Annotation(namespace='tempo')
    ann.append(time=0, duration=0, value=value, confidence=confidence)

    with pytest.raises(jams.SchemaError):
        ann.validate()


def test_ns_note_hz_valid():

    ann = Annotation(namespace='note_hz')

    seq_len = 21
    times = np.arange(seq_len)
    durations = np.zeros(seq_len)
    values = np.linspace(0, 22050, seq_len)  # includes 0 (odd symmetric)
    confidences = np.linspace(0, 1., seq_len)
    confidences[seq_len//2] = None  # throw in a None confidence value

    for (t, d, v, c) in zip(times, durations, values, confidences):
        ann.append(time=t, duration=d, value=v, confidence=c)

    ann.validate()


@parametrize('value', ['a', -23])
def test_ns_note_hz_invalid(value):

    ann = Annotation(namespace='note_hz')
    ann.append(time=0, duration=0, value=value, confidence=0.5)

    with pytest.raises(jams.SchemaError):
        ann.validate()


def test_ns_pitch_hz_valid():

    ann = Annotation(namespace='pitch_hz')

    seq_len = 21
    times = np.arange(seq_len)
    durations = np.zeros(seq_len)
    values = np.linspace(-22050., 22050, seq_len)  # includes 0 (odd symmetric)
    confidences = np.linspace(0, 1., seq_len)
    confidences[seq_len//2] = None  # throw in a None confidence value

    for (t, d, v, c) in zip(times, durations, values, confidences):
        ann.append(time=t, duration=d, value=v, confidence=c)

    ann.validate()


@parametrize('value', ['a'])
def test_ns_pitch_hz_invalid(value):

    ann = Annotation(namespace='pitch_hz')
    ann.append(time=0, duration=0, value=value, confidence=0.5)

    with pytest.raises(jams.SchemaError):
        ann.validate()


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


@parametrize('value', ['a'])
def test_ns_note_midi_invalid(value):

    ann = Annotation(namespace='note_midi')
    ann.append(time=0, duration=0, value=value, confidence=0.5)

    with pytest.raises(jams.SchemaError):
        ann.validate()


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


@parametrize('value', ['a'])
def test_ns_pitch_midi_invalid(value):

    ann = Annotation(namespace='pitch_midi')
    ann.append(time=0, duration=0, value=value, confidence=0.5)

    with pytest.raises(jams.SchemaError):
        ann.validate()


def test_ns_contour_valid():

    srand()

    ann = Annotation(namespace='pitch_contour')

    seq_len = 21
    times = np.arange(seq_len)
    durations = np.zeros(seq_len)
    values = np.linspace(0, 22050, seq_len)  # includes 0 (odd symmetric)
    ids = np.arange(len(values)) // 4
    voicing = np.random.randn(len(ids)) > 0

    confidences = np.linspace(0, 1., seq_len)
    confidences[seq_len//2] = None  # throw in a None confidence value

    for (t, d, v, c, i, b) in zip(times, durations, values,
                                  confidences, ids, voicing):
        ann.append(time=t, duration=d,
                   value={'pitch': v, 'id': i, 'voiced': b}, confidence=c)

    ann.validate()


def test_ns_contour_invalid():

    srand()

    ann = Annotation(namespace='pitch_contour')

    seq_len = 21
    times = np.arange(seq_len)
    durations = np.zeros(seq_len)
    values = np.linspace(0, 22050, seq_len)  # includes 0 (odd symmetric)
    ids = np.arange(len(values)) // 4
    voicing = np.random.randn(len(ids)) * 2

    confidences = np.linspace(0, 1., seq_len)
    confidences[seq_len//2] = None  # throw in a None confidence value

    for (t, d, v, c, i, b) in zip(times, durations, values,
                                  confidences, ids, voicing):
        ann.append(time=t, duration=d,
                   value={'pitch': v, 'id': i, 'voiced': b}, confidence=c)

    ann.validate()


@parametrize('value',
             ['B#:locrian', six.u('A:minor'), 'N', 'E'])
def test_ns_key_mode(value):

    ann = Annotation(namespace='key_mode')
    ann.append(time=0, duration=0, value=value, confidence=None)
    ann.validate()

@parametrize('value',
             ['asdf', 'A&:phrygian', 11, '', ':dorian', None])
def test_ns_key_mode_schema_error(value):

    ann = Annotation(namespace='key_mode')
    ann.append(time=0, duration=0, value=value, confidence=None)
    with pytest.raises(jams.SchemaError):
        ann.validate()


@parametrize('value',
             ['A:9', 'Gb:sus2(1,3,5)', 'X', 'C:13(*9)/b7'])
def test_ns_chord_valid(value):

    ann = Annotation(namespace='chord')
    ann.append(time=0, duration=1.0, value=value)
    ann.validate()


@parametrize('value',
             ['{}:maj'.format(_)
              for _ in [42, 'H', 'a', 'F1', True, None]] +
             ['C:{}'.format(_)
              for _ in [64, 'z', 'mj', 'Ab', 'iiii', False, None]] +
             ['C/{}'.format(_)
              for _ in ['A', 7.5, '8b']] + [None])
def test_ns_chord_invalid(value):

    ann = Annotation(namespace='chord')
    ann.append(time=0, duration=1.0, value=value)
    with pytest.raises(SchemaError):
        ann.validate()


@parametrize('value', ['B:7', 'Gb:(1,3,5)', 'A#:(*3)', 'C:sus4(*5)/b7'])
def test_ns_chord_harte_valid(value):

    ann = Annotation(namespace='chord_harte')
    ann.append(time=0, duration=1.0, value=value)
    ann.validate()


@parametrize('value',
             ['{}:maj'.format(_)
              for _ in [42, 'X', 'a', 'F1', True, None]] +
             ['C:{}'.format(_)
              for _ in [64, 'z', 'mj', 'Ab', 'iiii', False, None]] +
             ['C/{}'.format(_)
              for _ in ['A', 7.5, '8b']] + [None])
def test_ns_chord_harte_invalid(value):

    ann = Annotation(namespace='chord_harte')
    ann.append(time=0, duration=1.0, value=value)
    with pytest.raises(SchemaError):
        ann.validate()


@parametrize('value',
             [dict(tonic='B', chord='bII7'),
              dict(tonic=six.u('Gb'), chord=six.u('ii7/#V'))])
def test_ns_chord_roman_valid(value):

    ann = Annotation(namespace='chord_roman')
    ann.append(time=0, duration=1.0, value=value)
    ann.validate()


@parametrize('key, value',
             [('tonic', 42), ('tonic', 'H'),
              ('tonic', 'a'), ('tonic', 'F#b'),
              ('tonic', True), ('tonic', None),
              ('chord', 64), ('chord', 'z'),
              ('chord', 'i/V64'), ('chord', 'Ab'),
              ('chord', 'iiii'), ('chord', False),
              ('chord', None)])
def test_ns_chord_roman_invalid(key, value):

    data = dict(tonic='E', chord='iv64')
    data[key] = value

    ann = Annotation(namespace='chord_roman')
    ann.append(time=0, duration=1.0, value=data)
    with pytest.raises(SchemaError):
        ann.validate()


@parametrize('key', ['tonic', 'chord'])
def test_ns_chord_roman_missing(key):
    data = dict(tonic='E', chord='iv64')
    del data[key]

    ann = Annotation(namespace='chord_roman')
    ann.append(time=0, duration=1.0, value=data)
    with pytest.raises(SchemaError):
        ann.validate()


@parametrize('value',
             [dict(tonic='B', pitch=0),
              dict(tonic=six.u('Gb'), pitch=11)])
def test_ns_pitch_class_valid(value):

    ann = Annotation(namespace='pitch_class')
    ann.append(time=0, duration=1.0, value=value)
    ann.validate()


@parametrize('key, value',
             [('tonic', 42), ('tonic', 'H'),
              ('tonic', 'a'), ('tonic', 'F#b'),
              ('tonic', True), ('tonic', None),
              ('pitch', 1.5), ('pitch', 'xyz'),
              ('pitch', '3'), ('pitch', False),
              ('pitch', None)])
def test_ns_pitch_class_invalid(key, value):

    data = dict(tonic='E', pitch=7)
    data[key] = value
    ann = Annotation(namespace='pitch_class')
    ann.append(time=0, duration=1.0, value=data)
    with pytest.raises(SchemaError):
        ann.validate()


@parametrize('key', ['tonic', 'pitch'])
def test_ns_pitch_class_missing(key):
    data = dict(tonic='E', pitch=7)
    del data[key]
    ann = Annotation(namespace='pitch_class')
    ann.append(time=0, duration=1.0, value=data)
    with pytest.raises(SchemaError):
        ann.validate()


@parametrize('namespace,tag', [
    ('tag_cal500', 'Emotion-Angry_/_Aggressive' ),
    ('tag_cal500', 'Genre--_Metal/Hard_Rock' ),
    ('tag_cal500', six.u('Genre-Best-Jazz') ),
    ('tag_cal10k', 'a dub production'),
    ('tag_cal10k', "boomin' kick drum"),
    ('tag_cal10k', six.u('rock & roll ? roots')),
    ('tag_gtzan', 'blues'),
    ('tag_gtzan', 'classical'),
    ('tag_gtzan', 'country'),
    ('tag_gtzan', 'disco'),
    ('tag_gtzan', 'hip-hop'),
    ('tag_gtzan', 'jazz'),
    ('tag_gtzan', 'metal'),
    ('tag_gtzan', 'pop'),
    ('tag_gtzan', 'reggae'),
    ('tag_gtzan', six.u('rock')),
    ('tag_msd_tagtraum_cd1', 'reggae'),
    ('tag_msd_tagtraum_cd1', 'pop/rock'),
    ('tag_msd_tagtraum_cd1', 'rnb'),
    ('tag_msd_tagtraum_cd1', 'jazz'),
    ('tag_msd_tagtraum_cd1', 'vocal'),
    ('tag_msd_tagtraum_cd1', 'new age'),
    ('tag_msd_tagtraum_cd1', 'latin'),
    ('tag_msd_tagtraum_cd1', 'rap'),
    ('tag_msd_tagtraum_cd1', 'country'),
    ('tag_msd_tagtraum_cd1', 'international'),
    ('tag_msd_tagtraum_cd1', 'blues'),
    ('tag_msd_tagtraum_cd1', 'electronic'),
    ('tag_msd_tagtraum_cd1', six.u('folk')),
    ('tag_medleydb_instruments','accordion'),
    ('tag_medleydb_instruments','alto saxophone'),
    ('tag_medleydb_instruments',six.u('fx/processed sound')),
    ('tag_open', 'a tag'),
    ('segment_open', 'a segment'),
    ('segment_salami_lower','a'),
    ('segment_salami_lower',"a'"),
    ('segment_salami_lower',"a'''"),
    ('segment_salami_lower',"silence"),
    ('segment_salami_lower',"Silence"),
    ('segment_salami_lower',six.u('a')),
    ('segment_salami_lower','aa'),
    ('segment_salami_lower',"aa'"),
    ('segment_salami_lower','ab'),
    ('segment_salami_upper', 'A'),
    ('segment_salami_upper', "A'"),
    ('segment_salami_upper', "A'''"),
    ('segment_salami_upper', "silence"),
    ('segment_salami_upper', "Silence"),
    ('segment_salami_upper', six.u('A')),
    ('segment_salami_function', 'verse'),
    ('segment_salami_function', "chorus"),
    ('segment_salami_function', "theme"),
    ('segment_salami_function', "voice"),
    ('segment_salami_function', "silence"),
    ('segment_salami_function', six.u('verse')),
    ('segment_tut', 'verse'),
    ('segment_tut', "refrain"),
    ('segment_tut', "Si"),
    ('segment_tut', "bridge"),
    ('segment_tut', "Bridge"),
    ('segment_tut', six.u('verse')),
    ('vector', [1]),
    ('vector', [1, 2]),
    ('vector', np.asarray([1])),
    ('vector', np.asarray([1, 2])),
    ('blob', 'a tag'),
    ('blob', six.u('a unicode tag')),
    ('blob', 23),
    ('blob', None),
    ('blob', dict()),
    ('blob', list()),
    ('lyrics_bow', [['foo', 23]],),
    ('lyrics_bow', [['foo', 23], ['bar', 35]],),
    ('lyrics_bow', [['foo', 23], [['foo', 'bar'], 13]],),
    ('lyrics_bow', []),
    ('tag_audioset', 'Accordion'),
    ('tag_audioset', 'Afrobeat'),
    ('tag_audioset', six.u('Cacophony')),
    ('tag_audioset_genre', 'Afrobeat'),
    ('tag_audioset_genre', 'Disco'),
    ('tag_audioset_genre', six.u('Opera')),
    ('tag_audioset_instruments' ,'Organ'),
    ('tag_audioset_instruments' ,'Harmonica'),
    ('tag_audioset_instruments' ,six.u('Zither')),
    ('tag_fma_genre', 'Blues'),
    ('tag_fma_genre', 'Classical'),
    ('tag_fma_genre', six.u('Soul-RnB')),
    ('tag_fma_subgenre', 'Blues'),
    ('tag_fma_subgenre', 'British Folk'),
    ('tag_fma_subgenre', six.u('Klezmer')),
    ('tag_urbansound', 'air_conditioner'),
    ('tag_urbansound', 'car_horn'),
    ('tag_urbansound', 'children_playing'),
    ('tag_urbansound', 'dog_bark'),
    ('tag_urbansound', 'drilling'),
    ('tag_urbansound', 'engine_idling'),
    ('tag_urbansound', 'gun_shot'),
    ('tag_urbansound', 'jackhammer'),
    ('tag_urbansound', 'siren'),
    ('tag_urbansound', six.u('street_music')),
])
def test_ns_tag(namespace, tag):

    ann = Annotation(namespace=namespace)
    ann.append(time=0, duration=1, value=tag)
    ann.validate()


@parametrize('namespace', [
    'tag_cal500',
    'tag_cal10k',
    'tag_gtzan',
    'tag_msd_tagtraum_cd1',
    'tag_medleydb_instruments',
    'tag_open',
    'segment_open',
    'segment_salami_lower',
    'segment_salami_upper',
    'segment_salami_function',
    'segment_tut',
    'tag_audioset',
    'tag_audioset_genre',
    'tag_audioset_instruments',
    'tag_fma_genre',
    'tag_fma_subgenre',
    'tag_urbansound',
    'multi_segment',
])
@parametrize('value', [23, None])
def test_ns_tag_invalid_type(namespace, value):

    ann = Annotation(namespace=namespace)
    ann.append(time=0, duration=1, value=value)
    with pytest.raises(SchemaError):
        ann.validate()

@parametrize('namespace,value', [
    ('tag_cal500', 'GENRE-BEST-JAZZ'),
    ('tag_cal10k', 'A DUB PRODUCTION'),
    ('tag_gtzan', 'ROCK'),
    ('tag_msd_tagtraum_cd1', 'FOLK'),
    ('tag_medleydb_instruments', 'ACCORDION'),
    ('segment_salami_lower', 'A'),
    ('segment_salami_lower', 'S'),
    ('segment_salami_lower', 'a23'),
    ('segment_salami_lower', '  Silence  23'),
    ('segment_salami_lower', 'aba'),
    ('segment_salami_lower', 'aab'),
    ('segment_salami_upper', 'a'),
    ('segment_salami_upper', 'A23'),
    ('segment_salami_upper', '  Silence  23'),
    ('segment_salami_upper', 'ABA'),
    ('segment_salami_upper', 'AAB'),
    ('segment_salami_upper', 'AA'),
    ('segment_salami_function', 'a'),
    ('segment_salami_function', 'a'),
    ('segment_salami_function', 'A23'),
    ('segment_salami_function', '  Silence  23'),
    ('segment_salami_function', 'Some Garbage'),
    ('segment_tut', 'chorus'),
    ('segment_tut', 'a'),
    ('segment_tut', 'a'),
    ('segment_tut', 'A23'),
    ('segment_tut', '  Silence  23'),
    ('segment_tut', 'Some Garbage'),
    ('vector', 'a tag'),
    ('vector', six.u('a unicode tag')),
    ('vector', 23),
    ('vector', None),
    ('vector', dict()),
    ('vector', list()),
    ('lyrics_bow', ('foo', 23)),
    ('lyrics_bow', [('foo', -23)]),
    ('lyrics_bow', [(23, 'foo')]),
    ('tag_audioset', 'ACCORDION'),
    ('tag_audioset_genre', 'Accordion'),
    ('tag_audioset_instruments', 'Afrobeat'),
    ('tag_fma_genre', 'Afrobeat'),
    ('tag_fma_subgenre', 'title'),
    ('tag_urbansound', 'air conditioner'),
    ('tag_urbansound', 'AIR_CONDITIONER'),
])
def test_ns_invalid_value(namespace, value):
    ann = Annotation(namespace=namespace)
    ann.append(time=0, duration=1, value=value)
    with pytest.raises(SchemaError):
        ann.validate()


@parametrize('confidence', [0.0, 1.0, None])
def test_ns_tag_msd_tagtraum_cd1_confidence(confidence):
    ann = Annotation(namespace='tag_msd_tagtraum_cd1')
    ann.append(time=0, duration=1, value='rnb', confidence=confidence)
    ann.validate()


@parametrize('confidence', [1.2, -0.1])
def test_ns_tag_msd_tagtraum_cd1_bad_confidence(confidence):
    ann = Annotation(namespace='tag_msd_tagtraum_cd1')
    ann.append(time=0, duration=1, value='rnb', confidence=confidence)
    with pytest.raises(SchemaError):
        ann.validate()


@parametrize('pattern', [
    dict(midi_pitch=3, morph_pitch=5, staff=1, pattern_id=1, occurrence_id=1),
    dict(midi_pitch=-3, morph_pitch=-1.5, staff=1.0, pattern_id=1, occurrence_id=1)
])
def test_ns_pattern_valid(pattern):
    ann = Annotation(namespace='pattern_jku')
    ann.append(time=0, duration=1.0, value=pattern)
    ann.validate()


@parametrize('key', ['midi_pitch', 'morph_pitch', 'staff', 'pattern_id', 'occurrence_id'])
@parametrize('value', ['foo', None, dict(), list()])
def test_ns_pattern_invalid(key, value):

    data = dict(midi_pitch=3, morph_pitch=5,
                staff=1, pattern_id=1, occurrence_id=1)
    data[key] = value

    ann = Annotation(namespace='pattern_jku')
    ann.append(time=0, duration=1.0, value=data)

    with pytest.raises(SchemaError):
        ann.validate()


@parametrize('key', ['pattern_id', 'occurrence_id'])
@parametrize('value', [-1, 0, 0.5])
def test_ns_pattern_invalid_bounded(key, value):
    data = dict(midi_pitch=3, morph_pitch=5,
                staff=1, pattern_id=1, occurrence_id=1)
    data[key] = value

    ann = Annotation(namespace='pattern_jku')
    ann.append(time=0, duration=1.0, value=data)
    with pytest.raises(SchemaError):
        ann.validate()


@parametrize('label', ['a segment', six.u('a unicode segment')])
@parametrize('level', [0, 2])
def test_ns_multi_segment_label(label, level):

    ann = Annotation(namespace='multi_segment')
    ann.append(time=0, duration=1, value=dict(label=label, level=level))
    ann.validate()

@parametrize('label', [23, None])
def test_ns_multi_segment_invalid_label(label):
    ann = Annotation(namespace='multi_segment')
    ann.append(time=0, duration=1, value=dict(label=label, level=0))
    with pytest.raises(SchemaError):
        ann.validate()

@parametrize('level', [-1, 'foo', None])
def test_ns_multi_segment_invalid_level(level):
    ann = Annotation(namespace='multi_segment')
    ann.append(time=0, duration=1, value=dict(label='a segment', level=level))
    with pytest.raises(SchemaError):
        ann.validate()

def test_ns_multi_segment_invalid_both():
    ann = Annotation(namespace='multi_segment')
    ann.append(time=0, duration=1, value=dict(label=None, level=None))
    with pytest.raises(SchemaError):
        ann.validate()


def test_ns_multi_segment_bad_type():
    ann = Annotation(namespace='multi_segment')
    ann.append(time=0, duration=1, value='a string')
    with pytest.raises(SchemaError):
        ann.validate()


@pytest.fixture
def scraper_value():
    return {
        "source_time": 0.0,
        "event_duration": 0.5310546236891855,
        "event_time": 5.6543442662431795,
        "time_stretch": 0.8455598669219283,
        "pitch_shift": -1.2204911976305648,
        "snr": 7.790682558359417,
        "label": 'gun_shot',
        "role": "foreground",
        "source_file": "/audio/foreground/gun_shot/135544-6-17-0.wav"
    }



@parametrize('source_time', [0, 5, 1.0])
def test_ns_scaper_source_time(source_time):

    ann = Annotation(namespace='scaper')

    value = {
        "source_time": source_time,
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
    ann.validate()


@parametrize('source_time', [-1, -1.0, 'zero', None])
def test_ns_scraper_source_time_invalid(scraper_value, source_time):

    ann = Annotation(namespace='scaper')
    value = dict(scraper_value, source_time=source_time)
    ann.append(time=0, duration=1, value=value)

    with pytest.raises(SchemaError):
        ann.validate()


@parametrize('event_duration',
             [0.5, 5, 1.0])
def test_ns_scaper_event_duration(event_duration):

    ann = Annotation(namespace='scaper')

    value = {
        "source_time": 0.0,
        "event_duration": event_duration,
        "event_time": 5.6543442662431795,
        "time_stretch": 0.8455598669219283,
        "pitch_shift": -1.2204911976305648,
        "snr": 7.790682558359417,
        "label": 'gun_shot',
        "role": "foreground",
        "source_file": "/audio/foreground/gun_shot/135544-6-17-0.wav"
    }

    ann.append(time=0, duration=1, value=value)
    ann.validate()


@parametrize('event_duration', [0, -1, -1.0, 'zero', None])
def test_ns_scraper_event_duration_invalid(scraper_value, event_duration):

    ann = Annotation(namespace='scaper')
    value = dict(scraper_value, event_duration=event_duration)
    ann.append(time=0, duration=1, value=value)

    with pytest.raises(SchemaError):
        ann.validate()


@parametrize('event_time',
             [0, 5, 1.0])
def test_ns_scaper_event_time(event_time):

    ann = Annotation(namespace='scaper')

    value = {
        "source_time": 0.0,
        "event_duration": 0.5310546236891855,
        "event_time": event_time,
        "time_stretch": 0.8455598669219283,
        "pitch_shift": -1.2204911976305648,
        "snr": 7.790682558359417,
        "label": 'gun_shot',
        "role": "foreground",
        "source_file": "/audio/foreground/gun_shot/135544-6-17-0.wav"
    }

    ann.append(time=0, duration=1, value=value)
    ann.validate()


@parametrize('event_time', [-1, -1.0, 'zero', None])
def test_ns_scraper_event_time_invalid(scraper_value, event_time):

    ann = Annotation(namespace='scaper')
    value = dict(scraper_value, event_time=event_time)
    ann.append(time=0, duration=1, value=value)

    with pytest.raises(SchemaError):
        ann.validate()


@parametrize('time_stretch',
             [0.5, 5, 1.0, None])
def test_ns_scaper_time_stretch(time_stretch):

    ann = Annotation(namespace='scaper')

    value = {
        "source_time": 0.0,
        "event_duration": 0.5310546236891855,
        "event_time": 5.6543442662431795,
        "time_stretch": time_stretch,
        "pitch_shift": -1.2204911976305648,
        "snr": 7.790682558359417,
        "label": 'gun_shot',
        "role": "foreground",
        "source_file": "/audio/foreground/gun_shot/135544-6-17-0.wav"
    }

    ann.append(time=0, duration=1, value=value)
    ann.validate()


@parametrize('time_stretch', [0, -1, -1.0, 'zero'])
def test_ns_scraper_time_stretch_invalid(scraper_value, time_stretch):

    ann = Annotation(namespace='scaper')
    value = dict(scraper_value, time_stretch=time_stretch)
    ann.append(time=0, duration=1, value=value)

    with pytest.raises(SchemaError):
        ann.validate()


@parametrize('pitch_shift',
             [0.5, 5, 1.0, -1, -3.5, 0, None])
def test_ns_scaper_pitch_shift(pitch_shift):

    ann = Annotation(namespace='scaper')

    value = {
        "source_time": 0.0,
        "event_duration": 0.5310546236891855,
        "event_time": 5.6543442662431795,
        "time_stretch": 0.8455598669219283,
        "pitch_shift": pitch_shift,
        "snr": 7.790682558359417,
        "label": 'gun_shot',
        "role": "foreground",
        "source_file": "/audio/foreground/gun_shot/135544-6-17-0.wav"
    }

    ann.append(time=0, duration=1, value=value)
    ann.validate()


def test_ns_scraper_pitch_shift_invalid(scraper_value):

    ann = Annotation(namespace='scaper')
    value = dict(scraper_value, pitch_shift='zero')
    ann.append(time=0, duration=1, value=value)

    with pytest.raises(SchemaError):
        ann.validate()


@parametrize('snr',
             [0.5, 5, 1.0, -1, -3.5, 0])
def test_ns_scaper_snr(snr):

    ann = Annotation(namespace='scaper')

    value = {
        "source_time": 0.0,
        "event_duration": 0.5310546236891855,
        "event_time": 5.6543442662431795,
        "time_stretch": 0.8455598669219283,
        "pitch_shift": -1.2204911976305648,
        "snr": snr,
        "label": 'gun_shot',
        "role": "foreground",
        "source_file": "/audio/foreground/gun_shot/135544-6-17-0.wav"
    }

    ann.append(time=0, duration=1, value=value)
    ann.validate()


@parametrize('snr', ['zero', None])
def test_ns_scraper_snr_invalid(scraper_value, snr):

    ann = Annotation(namespace='scaper')
    value = dict(scraper_value, snr=snr)
    ann.append(time=0, duration=1, value=value)

    with pytest.raises(SchemaError):
        ann.validate()


@parametrize('label',
             ['air_conditioner', 'car_horn', six.u('street_music'), 'any string'])
def test_ns_scaper_label(label):

    ann = Annotation(namespace='scaper')

    value = {
        "source_time": 0.0,
        "event_duration": 0.5310546236891855,
        "event_time": 5.6543442662431795,
        "time_stretch": 0.8455598669219283,
        "pitch_shift": -1.2204911976305648,
        "snr": 7.790682558359417,
        "label": label,
        "role": "foreground",
        "source_file": "/audio/foreground/gun_shot/135544-6-17-0.wav"
    }

    ann.append(time=0, duration=1, value=value)
    ann.validate()


@parametrize('label', [23, None])
def test_ns_scraper_label_invalid(scraper_value, label):

    ann = Annotation(namespace='scaper')
    value = dict(scraper_value, label=label)
    ann.append(time=0, duration=1, value=value)

    with pytest.raises(SchemaError):
        ann.validate()


@parametrize('role',
             ['foreground', 'background', six.u('background'),
              ])
def test_ns_scaper_role(role):

    ann = Annotation(namespace='scaper')

    value = {
        "source_time": 0.0,
        "event_duration": 0.5310546236891855,
        "event_time": 5.6543442662431795,
        "time_stretch": 0.8455598669219283,
        "pitch_shift": -1.2204911976305648,
        "snr": 7.790682558359417,
        "label": "gun_shot",
        "role": role,
        "source_file": "/audio/foreground/gun_shot/135544-6-17-0.wav"
    }

    ann.append(time=0, duration=1, value=value)
    ann.validate()


@parametrize('role', ['FOREGROUND', 'BACKGROUND', 'something', 23, None])
def test_ns_scraper_role_invalid(scraper_value, role):

    ann = Annotation(namespace='scaper')
    value = dict(scraper_value, role=role)
    ann.append(time=0, duration=1, value=value)

    with pytest.raises(SchemaError):
        ann.validate()


@parametrize('source_file',
             ['filename', '/a/b/c.wav', six.u('filename.wav')])
def test_ns_scaper_source_file(source_file):

    ann = Annotation(namespace='scaper')

    value = {
        "source_time": 0.0,
        "event_duration": 0.5310546236891855,
        "event_time": 5.6543442662431795,
        "time_stretch": 0.8455598669219283,
        "pitch_shift": -1.2204911976305648,
        "snr": 7.790682558359417,
        "label": "gun_shot",
        "role": "foreground",
        "source_file": source_file
    }

    ann.append(time=0, duration=1, value=value)
    ann.validate()


@parametrize('source_file', [23, None])
def test_ns_scraper_source_file_invalid(scraper_value, source_file):

    ann = Annotation(namespace='scaper')
    value = dict(scraper_value, source_file=source_file)
    ann.append(time=0, duration=1, value=value)

    with pytest.raises(SchemaError):
        ann.validate()
