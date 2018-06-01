#!/usr/bin/env python
# CREATED:2015-05-26 12:47:35 by Brian McFee <brian.mcfee@nyu.edu>
"""Namespace schema tests"""

import six
import numpy as np

import pytest

from jams import SchemaError

from jams import Annotation, Observation

from test_util import srand


xfail = pytest.mark.xfail
parametrize = pytest.mark.parametrize


def test_ns_time_valid():

    ann = Annotation(namespace='onset')

    for time in np.arange(5.0, 10.0):
        ann.append(time=time, duration=0.0, value=None, confidence=None)

    ann.validate()


@xfail(raises=SchemaError)
@parametrize('time, duration', [(-1, 0), (1, -1)])
def test_ns_time_invalid(time, duration):

    ann = Annotation(namespace='onset')

    # Bypass the safety checks in append
    ann.data.add(Observation(time=time, duration=duration,
                             value=None, confidence=None))

    ann.validate()


def test_ns_beat_valid():

    # A valid example
    ann = Annotation(namespace='beat')

    for time in np.arange(5.0):
        ann.append(time=time, duration=0.0, value=1, confidence=None)

    for time in np.arange(5.0, 10.0):
        ann.append(time=time, duration=0.0, value=None, confidence=None)

    ann.validate()


@xfail(raises=SchemaError)
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
@xfail(raises=SchemaError)
def test_ns_beat_position_invalid(key, value):

    data = dict(position=1, measure=1, num_beats=3, beat_units=4)
    data[key] = value

    ann = Annotation(namespace='beat_position')
    ann.append(time=0, duration=1.0, value=data)
    ann.validate()


@parametrize('key',
             ['position', 'measure', 'num_beats', 'beat_units'])
@xfail(raises=SchemaError)
def test_ns_beat_position_missing(key):

    data = dict(position=1, measure=1, num_beats=3, beat_units=4)
    del data[key]
    ann = Annotation(namespace='beat_position')
    ann.append(time=0, duration=1.0, value=data)
    ann.validate()


def test_ns_mood_thayer_valid():

    ann = Annotation(namespace='mood_thayer')

    ann.append(time=0, duration=1.0, value=[0.3, 2.0])

    ann.validate()


@parametrize('value', [[0], [0, 1, 2], ['a', 'b'], None, 0])
@xfail(raises=SchemaError)
def test_ns_mood_thayer_invalid(value):

    ann = Annotation(namespace='mood_thayer')
    ann.append(time=0, duration=1.0, value=value)
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
             ['Check yourself', six.u('before you wreck yourself'),
              xfail(23, raises=SchemaError),
              xfail(None, raises=SchemaError)])
def test_ns_lyrics(lyric):

    ann = Annotation(namespace='lyrics')
    ann.append(time=0, duration=1, value=lyric)
    ann.validate()


def test_ns_tempo_valid():

    ann = Annotation(namespace='tempo')

    ann.append(time=0, duration=0, value=1, confidence=0.85)

    ann.validate()


@xfail(SchemaError)
@parametrize('value, confidence',
             [(-1, 0.5), (-0.5, 0.5), ('a', 0.5),
              (120.0, -1), (120.0, -0.5),
              (120.0, 2.0), (120.0, 'a')])
def test_ns_tempo_invalid(value, confidence):

    ann = Annotation(namespace='tempo')
    ann.append(time=0, duration=0, value=value, confidence=confidence)
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
@xfail(raises=SchemaError)
def test_ns_note_hz_invalid(value):

    ann = Annotation(namespace='note_hz')
    ann.append(time=0, duration=0, value=value, confidence=0.5)
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
@xfail(raises=SchemaError)
def test_ns_pitch_hz_invalid(value):

    ann = Annotation(namespace='pitch_hz')
    ann.append(time=0, duration=0, value=value, confidence=0.5)
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
@xfail(raises=SchemaError)
def test_ns_note_midi_invalid(value):

    ann = Annotation(namespace='note_midi')
    ann.append(time=0, duration=0, value=value, confidence=0.5)
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
@xfail(raises=SchemaError)
def test_ns_pitch_midi_invalid(value):

    ann = Annotation(namespace='pitch_midi')
    ann.append(time=0, duration=0, value=value, confidence=0.5)
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
             ['B#:locrian', six.u('A:minor'), 'N', 'E',
              xfail('asdf', raises=SchemaError),
              xfail('A&:phrygian', raises=SchemaError),
              xfail(11, raises=SchemaError),
              xfail('', raises=SchemaError),
              xfail(':dorian', raises=SchemaError),
              xfail(None, raises=SchemaError)])
def test_ns_key_mode(value):

    ann = Annotation(namespace='key_mode')
    ann.append(time=0, duration=0, value=value, confidence=None)
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
@xfail(raises=SchemaError)
def test_ns_chord_invalid(value):

    ann = Annotation(namespace='chord')
    ann.append(time=0, duration=1.0, value=value)
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
@xfail(raises=SchemaError)
def test_ns_chord_harte_invalid(value):

    ann = Annotation(namespace='chord_harte')
    ann.append(time=0, duration=1.0, value=value)
    ann.validate()


@parametrize('value',
             [dict(tonic='B', chord='bII7'),
              dict(tonic=six.u('Gb'), chord=six.u('ii7/#V'))])
def test_ns_chord_roman_valid(value):

    ann = Annotation(namespace='chord_roman')
    ann.append(time=0, duration=1.0, value=value)
    ann.validate()


@xfail(SchemaError)
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
    ann.validate()


@xfail(SchemaError)
@parametrize('key', ['tonic', 'chord'])
def test_ns_chord_roman_missing(key):
    data = dict(tonic='E', chord='iv64')
    del data[key]

    ann = Annotation(namespace='chord_roman')
    ann.append(time=0, duration=1.0, value=data)
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
@xfail(raises=SchemaError)
def test_ns_pitch_class_invalid(key, value):

    data = dict(tonic='E', pitch=7)
    data[key] = value
    ann = Annotation(namespace='pitch_class')
    ann.append(time=0, duration=1.0, value=data)
    ann.validate()


@parametrize('key', ['tonic', 'pitch'])
@xfail(raises=SchemaError)
def test_ns_pitch_class_missing(key):
    data = dict(tonic='E', pitch=7)
    del data[key]
    ann = Annotation(namespace='pitch_class')
    ann.append(time=0, duration=1.0, value=data)
    ann.validate()


@parametrize('tag',
             ['Emotion-Angry_/_Aggressive',
              'Genre--_Metal/Hard_Rock',
              six.u('Genre-Best-Jazz'),
              xfail(23, raises=SchemaError),
              xfail(None, raises=SchemaError),
              xfail('GENRE-BEST-JAZZ', raises=SchemaError)])
def test_ns_tag_cal500(tag):

    ann = Annotation(namespace='tag_cal500')
    ann.append(time=0, duration=1, value=tag)
    ann.validate()


@parametrize('tag',
             ['a dub production', "boomin' kick drum",
              six.u('rock & roll ? roots'),
              xfail(23, raises=SchemaError),
              xfail(None, raises=SchemaError),
              xfail('A DUB PRODUCTION', raises=SchemaError)])
def test_ns_tag_cal10k(tag):

    ann = Annotation(namespace='tag_cal10k')

    ann.append(time=0, duration=1, value=tag)

    ann.validate()


@parametrize('tag',
             ['blues', 'classical', 'country', 'disco',
              'hip-hop', 'jazz', 'metal', 'pop',
              'reggae', six.u('rock'),
              xfail(23, raises=SchemaError),
              xfail(None, raises=SchemaError),
              xfail('ROCK', raises=SchemaError)])
def test_ns_tag_gtzan(tag):

    ann = Annotation(namespace='tag_gtzan')
    ann.append(time=0, duration=1, value=tag)
    ann.validate()


@parametrize('tag',
             ['reggae', 'pop/rock', 'rnb', 'jazz',
              'vocal', 'new age', 'latin', 'rap',
              'country', 'international', 'blues', 'electronic',
              six.u('folk'),
              xfail(23, raises=SchemaError),
              xfail(None, raises=SchemaError),
              xfail('FOLK', raises=SchemaError)])
@parametrize('confidence',
             [0.0, 1.0, None,
              xfail(1.2, raises=SchemaError),
              xfail(-0.1, raises=SchemaError)])
def test_ns_tag_msd_tagtraum_cd1(tag, confidence):

    ann = Annotation(namespace='tag_msd_tagtraum_cd1')

    ann.append(time=0, duration=1, value=tag, confidence=confidence)

    ann.validate()


@parametrize('tag',
             ['reggae', 'latin', 'metal',
              'rnb', 'jazz', 'punk', 'pop',
              'new age', 'country', 'rap', 'rock',
              'world', 'blues', 'electronic', six.u('folk'),
              xfail(23, raises=SchemaError),
              xfail(None, raises=SchemaError),
              xfail('FOLK', raises=SchemaError)])
@parametrize('confidence',
             [0.0, 1.0, None,
              xfail(1.2, raises=SchemaError),
              xfail(-0.1, raises=SchemaError)])
def test_ns_tag_msd_tagtraum_cd2(tag, confidence):

    ann = Annotation(namespace='tag_msd_tagtraum_cd2')
    ann.append(time=0, duration=1, value=tag, confidence=confidence)
    ann.validate()


@parametrize('tag',
             ['accordion', 'alto saxophone', six.u('fx/processed sound'),
              xfail(23, raises=SchemaError),
              xfail(None, raises=SchemaError),
              xfail('ACCORDION', raises=SchemaError)])
def test_ns_tag_medleydb(tag):

    ann = Annotation(namespace='tag_medleydb_instruments')
    ann.append(time=0, duration=1, value=tag)
    ann.validate()


@parametrize('tag',
             ['a tag', six.u('a unicode tag'),
              xfail(23, raises=SchemaError),
              xfail(None, raises=SchemaError)])
def test_ns_tag_open(tag):

    ann = Annotation(namespace='tag_open')
    ann.append(time=0, duration=1, value=tag)
    ann.validate()


@parametrize('segment',
             ['a segment', six.u('a unicode segment'),
              xfail(23, raises=SchemaError),
              xfail(None, raises=SchemaError)])
def test_segment_tag_open(segment):

    ann = Annotation(namespace='segment_open')
    ann.append(time=0, duration=1, value=segment)
    ann.validate()


@parametrize('label',
             ['a', "a'", "a'''", "silence", "Silence",
              six.u('a'), 'aa', "aa'", 'ab'] +
             [xfail(_, raises=SchemaError)
              for _ in [23, None, 'A', 'S', 'a23',
                        '  Silence  23', 'aba', 'aab']])
def test_ns_segment_salami_lower(label):

    ann = Annotation(namespace='segment_salami_lower')
    ann.append(time=0, duration=1, value=label)
    ann.validate()


@parametrize('label',
             ['A', "A'", "A'''", "silence", "Silence",
              six.u('A')] +
             [xfail(_, raises=SchemaError)
              for _ in [23, None, 'a', 'A23',
                        '  Silence  23', 'ABA', 'AAB', 'AA']])
def test_ns_segment_salami_upper(label):

    ann = Annotation(namespace='segment_salami_upper')
    ann.append(time=0, duration=1, value=label)
    ann.validate()


@parametrize('label',
             ['verse', "chorus", "theme", "voice",
              "silence", six.u('verse')] +
             [xfail(_, raises=SchemaError)
              for _ in [23, None, 'a', 'a', 'A23',
                        '  Silence  23', 'Some Garbage']])
def test_ns_segment_salami_function(label):

    ann = Annotation(namespace='segment_salami_function')
    ann.append(time=0, duration=1, value=label)
    ann.validate()


@parametrize('label',
             ['verse', "refrain", "Si", "bridge", "Bridge", six.u('verse')] +
             [xfail(_, raises=SchemaError)
              for _ in [23, None, 'chorus', 'a', 'a',
                        'A23', '  Silence  23', 'Some Garbage']])
def test_ns_segment_tut(label):

    ann = Annotation(namespace='segment_tut')
    ann.append(time=0, duration=1, value=label)
    ann.validate()


@parametrize('pattern', [dict(midi_pitch=3, morph_pitch=5, staff=1,
                              pattern_id=1, occurrence_id=1),
                         dict(midi_pitch=-3, morph_pitch=-1.5, staff=1.0,
                              pattern_id=1, occurrence_id=1)])
def test_ns_pattern_valid(pattern):
    ann = Annotation(namespace='pattern_jku')
    ann.append(time=0, duration=1.0, value=pattern)
    ann.validate()


@xfail(raises=SchemaError)
@parametrize('key', ['midi_pitch', 'morph_pitch', 'staff',
                     'pattern_id', 'occurrence_id'])
@parametrize('value', ['foo', None, dict(), list()])
def test_ns_pattern_invalid(key, value):

    data = dict(midi_pitch=3, morph_pitch=5,
                staff=1, pattern_id=1, occurrence_id=1)
    data[key] = value

    ann = Annotation(namespace='pattern_jku')
    ann.append(time=0, duration=1.0, value=data)
    ann.validate()


@xfail(raises=SchemaError)
@parametrize('key', ['pattern_id', 'occurrence_id'])
@parametrize('value', [-1, 0, 0.5])
def test_ns_pattern_invalid_bounded(key, value):
    data = dict(midi_pitch=3, morph_pitch=5,
                staff=1, pattern_id=1, occurrence_id=1)
    data[key] = value

    ann = Annotation(namespace='pattern_jku')
    ann.append(time=0, duration=1.0, value=data)
    ann.validate()


@parametrize('label', ['a tag', six.u('a unicode tag'), 23,
                       None, dict(), list()])
def test_ns_blob(label):
    ann = Annotation(namespace='blob')
    ann.append(time=0, duration=1, value=label)
    ann.validate()


@parametrize('label', [[1], [1, 2], np.asarray([1]), np.asarray([1, 2])] +
                      [xfail(_, raises=SchemaError) for _ in
                       ['a tag', six.u('a unicode tag'), 23,
                        None, dict(), list()]])
def test_ns_vector(label):

    ann = Annotation(namespace='vector')
    ann.append(time=0, duration=1, value=label)
    ann.validate()


@parametrize('label', ['a segment', six.u('a unicode segment'),
                       xfail(23, raises=SchemaError),
                       xfail(None, raises=SchemaError)])
@parametrize('level', [0, 2,
                       xfail(-1, raises=SchemaError),
                       xfail('foo', raises=SchemaError),
                       xfail(None, raises=SchemaError)])
def test_ns_multi_segment(label, level):

    ann = Annotation(namespace='multi_segment')
    ann.append(time=0, duration=1, value=dict(label=label, level=level))
    ann.validate()


@xfail(raises=SchemaError)
def test_ns_multi_segment_bad():
    ann = Annotation(namespace='multi_segment')
    ann.append(time=0, duration=1, value='a string')
    ann.validate()


@parametrize('label', [[['foo', 23]],
                       [['foo', 23], ['bar', 35]],
                       [['foo', 23], [['foo', 'bar'], 13]],
                       [],
                       xfail(('foo', 23), raises=SchemaError),
                       xfail([('foo', -23)], raises=SchemaError),
                       xfail([(23, 'foo')], raises=SchemaError)])
def test_ns_lyrics_bow(label):

    ann = Annotation(namespace='lyrics_bow')
    ann.append(time=0, duration=1, value=label)
    ann.validate()


@parametrize('tag',
             ['Accordion', 'Afrobeat', six.u('Cacophony'),
              xfail(23, raises=SchemaError),
              xfail(None, raises=SchemaError),
              xfail('ACCORDION', raises=SchemaError)])
def test_ns_tag_audioset(tag):

    ann = Annotation(namespace='tag_audioset')
    ann.append(time=0, duration=1, value=tag)
    ann.validate()


@parametrize('tag',
             ['Afrobeat', 'Disco', six.u('Opera'),
              xfail(23, raises=SchemaError),
              xfail(None, raises=SchemaError),
              xfail('Accordion', raises=SchemaError)])
def test_ns_tag_audioset_genre(tag):

    ann = Annotation(namespace='tag_audioset_genre')
    ann.append(time=0, duration=1, value=tag)
    ann.validate()


@parametrize('tag',
             ['Organ', 'Harmonica', six.u('Zither'),
              xfail(23, raises=SchemaError),
              xfail(None, raises=SchemaError),
              xfail('Afrobeat', raises=SchemaError)])
def test_ns_tag_audioset_instruments(tag):

    ann = Annotation(namespace='tag_audioset_instruments')
    ann.append(time=0, duration=1, value=tag)
    ann.validate()


@parametrize('tag',
             ['Blues', 'Classical', six.u('Soul-RnB'),
              xfail(23, raises=SchemaError),
              xfail(None, raises=SchemaError),
              xfail('Afrobeat', raises=SchemaError)])
def test_ns_tag_fma_genre(tag):

    ann = Annotation(namespace='tag_fma_genre')
    ann.append(time=0, duration=1, value=tag)
    ann.validate()


@parametrize('tag',
             ['Blues', 'British Folk', six.u('Klezmer'),
              xfail(23, raises=SchemaError),
              xfail(None, raises=SchemaError),
              xfail('title', raises=SchemaError)])
def test_ns_tag_fma_subgenre(tag):

    ann = Annotation(namespace='tag_fma_subgenre')
    ann.append(time=0, duration=1, value=tag)
    ann.validate()


@parametrize('tag',
             ['air_conditioner', 'car_horn', 'children_playing', 'dog_bark',
              'drilling', 'engine_idling', 'gun_shot', 'jackhammer', 'siren',
              six.u('street_music'),
              xfail(23, raises=SchemaError),
              xfail(None, raises=SchemaError),
              xfail('air conditioner', raises=SchemaError),
              xfail('AIR_CONDITIONER', raises=SchemaError)])
def test_ns_tag_urbansound(tag):

    ann = Annotation(namespace='tag_urbansound')
    ann.append(time=0, duration=1, value=tag)
    ann.validate()


@parametrize('source_time',
             [0, 5, 1.0,
              xfail(-1, raises=SchemaError),
              xfail(-1.0, raises=SchemaError),
              xfail('zero', raises=SchemaError),
              xfail(None, raises=SchemaError)])
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


@parametrize('event_duration',
             [0.5, 5, 1.0,
              xfail(0, raises=SchemaError),
              xfail(-1, raises=SchemaError),
              xfail(-1.0, raises=SchemaError),
              xfail('zero', raises=SchemaError),
              xfail(None, raises=SchemaError)])
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


@parametrize('event_time',
             [0, 5, 1.0,
              xfail(-1, raises=SchemaError),
              xfail(-1.0, raises=SchemaError),
              xfail('zero', raises=SchemaError),
              xfail(None, raises=SchemaError)])
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


@parametrize('time_stretch',
             [0.5, 5, 1.0, None,
              xfail(0, raises=SchemaError),
              xfail(-1, raises=SchemaError),
              xfail(-1.0, raises=SchemaError),
              xfail('zero', raises=SchemaError)])
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


@parametrize('pitch_shift',
             [0.5, 5, 1.0, -1, -3.5, 0, None,
              xfail('zero', raises=SchemaError)])
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


@parametrize('snr',
             [0.5, 5, 1.0, -1, -3.5, 0,
              xfail(None, raises=SchemaError),
              xfail('zero', raises=SchemaError)])
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


@parametrize('label',
             ['air_conditioner', 'car_horn', six.u('street_music'),
              'any string',
              xfail(23, raises=SchemaError),
              xfail(None, raises=SchemaError)])
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


@parametrize('role',
             ['foreground', 'background', six.u('background'),
              xfail('FOREGROUND', raises=SchemaError),
              xfail('BACKGROUND', raises=SchemaError),
              xfail('something', raises=SchemaError),
              xfail(23, raises=SchemaError),
              xfail(None, raises=SchemaError)])
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


@parametrize('source_file',
             ['filename', '/a/b/c.wav', six.u('filename.wav'),
              xfail(23, raises=SchemaError),
              xfail(None, raises=SchemaError)])
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
