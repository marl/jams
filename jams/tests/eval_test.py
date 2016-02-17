#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''mir_eval integration tests'''

import numpy as np
from nose.tools import raises
import jams


# Beat tracking
def create_annotation(values, namespace='beat', offset=0.0, duration=1, confidence=1):
    ann = jams.Annotation(namespace=namespace)

    time = np.arange(offset, offset + len(values))

    if np.isscalar(duration):
        time = time * duration
        duration = [duration] * len(time)

    if np.isscalar(confidence):
        confidence = [confidence] * len(time)

    for t, d, v, c in zip(time, duration, values, confidence):
        ann.append(time=t, duration=d, value=v, confidence=c)

    return ann

def test_beat_valid():

    ref_ann = create_annotation(values=np.arange(10) % 4 + 1.,
                                namespace='beat')

    est_ann = create_annotation(values=np.arange(9) % 4 + 1.,
                                namespace='beat',
                                offset=0.01)

    jams.eval.beat(ref_ann, est_ann)

def test_beat_invalid():

    ref_ann = create_annotation(values=np.arange(10) % 4 + 1.,
                                namespace='beat')

    est_ann = create_annotation(values=np.arange(9) % 4 + 1.,
                                namespace='onset',
                                offset=0.01)

    yield raises(jams.NamespaceError)(jams.eval.beat), ref_ann, est_ann
    yield raises(jams.NamespaceError)(jams.eval.beat), est_ann, ref_ann


# Onset detection
def test_onset_valid():

    ref_ann = create_annotation(values=np.arange(10) % 4 + 1.,
                                namespace='onset')

    est_ann = create_annotation(values=np.arange(9) % 4 + 1.,
                                namespace='onset',
                                offset=0.01)

    jams.eval.onset(ref_ann, est_ann)

def test_onset_invalid():

    ref_ann = create_annotation(values=np.arange(10) % 4 + 1.,
                                namespace='onset')

    est_ann = create_annotation(values=np.arange(9) % 4 + 1.,
                                namespace='beat',
                                offset=0.01)

    yield raises(jams.NamespaceError)(jams.eval.onset), ref_ann, est_ann
    yield raises(jams.NamespaceError)(jams.eval.onset), est_ann, ref_ann


# Chord estimation
def test_chord_valid():

    ref_ann = create_annotation(values=['C', 'E', 'G:min7'],
                                namespace='chord')

    est_ann = create_annotation(values=['D', 'E', 'G:maj'],
                                namespace='chord_harte')

    jams.eval.chord(ref_ann, est_ann)

def test_chord_invalid():

    ref_ann = create_annotation(values=['C', 'E', 'G:min7'],
                                namespace='chord')

    est_ann = create_annotation(values=[{'tonic': 'C', 'chord': 'I'}],
                                namespace='chord_roman')

    yield raises(jams.NamespaceError)(jams.eval.chord), ref_ann, est_ann
    yield raises(jams.NamespaceError)(jams.eval.chord), est_ann, ref_ann

    est_ann = create_annotation(values=['D', 'E', 'not at all a chord'],
                                namespace='chord_harte',
                                offset=0.01)

    yield raises(jams.SchemaError)(jams.eval.chord), ref_ann, est_ann
    yield raises(jams.SchemaError)(jams.eval.chord), est_ann, ref_ann


# Segmentation
def test_segment_valid():

    ref_ann = create_annotation(values=['A', 'B', 'A', 'C'],
                                namespace='segment_open')

    est_ann = create_annotation(values=['E', 'B', 'E', 'B'],
                                namespace='segment_open')

    jams.eval.segment(ref_ann, est_ann)

def test_segment_invalid():

    ref_ann = create_annotation(values=['A', 'B', 'A', 'C'],
                                namespace='segment_open')

    est_ann = create_annotation(values=['E', 'B', 'E', 'B'],
                                namespace='chord_harte')

    yield raises(jams.NamespaceError)(jams.eval.segment), ref_ann, est_ann
    yield raises(jams.NamespaceError)(jams.eval.segment), est_ann, ref_ann

    est_ann = create_annotation(values=[['F'], 'E', 'B', 'E', 'B'],
                                namespace='segment_tut')

    yield raises(jams.SchemaError)(jams.eval.segment), ref_ann, est_ann
    yield raises(jams.SchemaError)(jams.eval.segment), est_ann, ref_ann

# Tempo estimation
def test_tempo_valid():

    ref_ann = create_annotation(values=[120.0, 60.0], confidence=[0.75, 0.25],
                                namespace='tempo')

    est_ann = create_annotation(values=[120.0, 80.0], confidence=[0.5, 0.5],
                                namespace='tempo')

    jams.eval.tempo(ref_ann, est_ann)


def test_tempo_invalid():

    ref_ann = create_annotation(values=[120.0, 60.0], confidence=[0.75, 0.25],
                                namespace='tempo')

    est_ann = create_annotation(values=[120.0, 80.0], confidence=[0.5, 0.5],
                                namespace='tag_open')

    yield raises(jams.NamespaceError)(jams.eval.tempo), ref_ann, est_ann
    yield raises(jams.NamespaceError)(jams.eval.tempo), est_ann, ref_ann

    est_ann = create_annotation(values=[120.0, 80.0], confidence=[-5, 1.5],
                                namespace='tempo')

    yield raises(jams.SchemaError)(jams.eval.tempo), ref_ann, est_ann
    yield raises(jams.SchemaError)(jams.eval.tempo), est_ann, ref_ann

# Melody
def test_melody_valid():

    f1 = np.linspace(110.0, 440.0, 10)
    v1 = np.sign(np.random.randn(len(f1)))
    v2 = np.sign(np.random.randn(len(f1)))

    ref_ann = create_annotation(values=f1 * v1,
                                confidence=1.0,
                                duration=0.01,
                                namespace='pitch_hz')

    est_ann = create_annotation(values=f1 * v2,
                                confidence=1.0,
                                duration=0.01,
                                namespace='pitch_hz')

    jams.eval.melody(ref_ann, est_ann)

def test_melody_invalid():

    f1 = np.linspace(110.0, 440.0, 10)
    v1 = np.sign(np.random.randn(len(f1)))
    v2 = np.sign(np.random.randn(len(f1)))

    ref_ann = create_annotation(values=f1 * v1,
                                confidence=1.0,
                                duration=0.01,
                                namespace='pitch_hz')

    est_ann = create_annotation(values=f1 * v2,
                                confidence=1.0,
                                duration=0.01,
                                namespace='blob')


    yield raises(jams.NamespaceError)(jams.eval.melody), ref_ann, est_ann
    yield raises(jams.NamespaceError)(jams.eval.melody), est_ann, ref_ann

    est_ann = create_annotation(values=['a', 'b', 'c'],
                                confidence=1.0,
                                duration=0.01,
                                namespace='pitch_hz')

    yield raises(jams.SchemaError)(jams.eval.melody), ref_ann, est_ann
    yield raises(jams.SchemaError)(jams.eval.melody), est_ann, ref_ann

# Pattern discovery
def test_pattern_valid():

    ref_jam = jams.load('fixtures/pattern_data.jams')

    ref_ann = ref_jam.search(namespace='pattern_jku')[0]

    jams.eval.pattern(ref_ann, ref_ann)


def test_pattern_invalid():

    ref_jam = jams.load('fixtures/pattern_data.jams')
    ref_ann = ref_jam.search(namespace='pattern_jku')[0]

    est_ann = create_annotation(values=np.arange(9) % 4 + 1.,
                                namespace='beat',
                                offset=0.01)


    yield raises(jams.NamespaceError)(jams.eval.pattern), ref_ann, est_ann
    yield raises(jams.NamespaceError)(jams.eval.pattern), est_ann, ref_ann

    # Check for failure on a badly formed pattern
    pattern = {'midi_pitch': 3, 'morph_pitch': 5, 'staff': 1,
               'pattern_id': None, 'occurrence_id': 1}

    est_ann = create_annotation(values=[pattern],
                                confidence=1.0,
                                duration=0.01,
                                namespace='pattern_jku')

    yield raises(jams.SchemaError)(jams.eval.pattern), ref_ann, est_ann
    yield raises(jams.SchemaError)(jams.eval.pattern), est_ann, ref_ann



# Hierarchical segmentation
def create_hierarchy(values, offset=0.0, duration=20):
    ann = jams.Annotation(namespace='multi_segment')

    for level, labels in enumerate(values):
        times = np.linspace(offset, offset + duration, num=len(labels), endpoint=False)

        durations = list(np.diff(times))
        durations.append(duration + offset - times[-1])

        for t, d, v in zip(times, durations, labels):
            ann.append(time=t, duration=d, value=dict(label=v, level=level))

    return ann

def test_hierarchy_valid():

    ref_ann = create_hierarchy(values=['AB', 'abac'])
    est_ann = create_hierarchy(values=['ABCD', 'abacbcbd'])

    jams.eval.hierarchy(ref_ann, est_ann)


def test_hierarchy_invalid():

    ref_ann = create_hierarchy(values=['AB', 'abac'])
    est_ann = create_hierarchy(values=['ABCD', 'abacbcbd'])

    est_ann.namespace = 'segment_open'

    yield raises(jams.NamespaceError)(jams.eval.hierarchy), ref_ann, est_ann
    yield raises(jams.NamespaceError)(jams.eval.hierarchy), est_ann, ref_ann

    est_ann = create_annotation(values=['E', 'B', 'E', 'B'],
                                namespace='segment_tut')
    est_ann.namespace = 'multi_segment'

    yield raises(jams.SchemaError)(jams.eval.hierarchy), ref_ann, est_ann
    yield raises(jams.SchemaError)(jams.eval.hierarchy), est_ann, ref_ann

