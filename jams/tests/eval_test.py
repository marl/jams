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
                                namespace='onsets',
                                offset=0.01)

    yield raises(jams.NamespaceError)(jams.eval.beat), ref_ann, est_ann
    yield raises(jams.NamespaceError)(jams.eval.beat), est_ann, ref_ann

    est_ann = create_annotation(values=np.arange(9) % 4 + 1.,
                                namespace='beat',
                                offset=-10)
    yield raises(jams.SchemaError)(jams.eval.beat), ref_ann, est_ann
    yield raises(jams.SchemaError)(jams.eval.beat), est_ann, ref_ann

# Onset detection
def test_onset_valid():

    ref_ann = create_annotation(values=np.arange(10) % 4 + 1.,
                                namespace='onsets')

    est_ann = create_annotation(values=np.arange(9) % 4 + 1.,
                                namespace='onsets',
                                offset=0.01)

    jams.eval.onset(ref_ann, est_ann)

def test_onset_invalid():

    ref_ann = create_annotation(values=np.arange(10) % 4 + 1.,
                                namespace='onsets')

    est_ann = create_annotation(values=np.arange(9) % 4 + 1.,
                                namespace='beat',
                                offset=0.01)

    yield raises(jams.NamespaceError)(jams.eval.onset), ref_ann, est_ann
    yield raises(jams.NamespaceError)(jams.eval.onset), est_ann, ref_ann

    est_ann = create_annotation(values=np.arange(9) % 4 + 1.,
                                namespace='onsets',
                                offset=-10)
    yield raises(jams.SchemaError)(jams.eval.onset), ref_ann, est_ann
    yield raises(jams.SchemaError)(jams.eval.onset), est_ann, ref_ann


# Chord estimation
def test_chord_valid():

    ref_ann = create_annotation(values=['C', 'E', 'G:min7'],
                                namespace='chord_harte')

    est_ann = create_annotation(values=['D', 'E', 'G:maj'],
                                namespace='chord_harte')

    jams.eval.chord(ref_ann, est_ann)

def test_chord_invalid():

    def __test(ref, est):
        jams.eval.chord(ref, est)

    ref_ann = create_annotation(values=['C', 'E', 'G:min7'],
                                namespace='chord_harte')

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
                                namespace='segment_label_open')

    est_ann = create_annotation(values=['E', 'B', 'E', 'B'],
                                namespace='segment_label_open')

    jams.eval.segment(ref_ann, est_ann)

def test_segment_invalid():

    ref_ann = create_annotation(values=['A', 'B', 'A', 'C'],
                                namespace='segment_label_open')

    est_ann = create_annotation(values=['E', 'B', 'E', 'B'],
                                namespace='chord_harte')

    yield raises(jams.NamespaceError)(jams.eval.segment), ref_ann, est_ann
    yield raises(jams.NamespaceError)(jams.eval.segment), est_ann, ref_ann

    est_ann = create_annotation(values=['E', 'B', 'E', 'B'],
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

# Pattern discovery
