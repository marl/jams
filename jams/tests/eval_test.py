#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''mir_eval integration tests'''

import numpy as np
from nose.tools import raises
import jams


# Beat tracking
def create_annotation(values, namespace='beat', offset=0.0):
    ann = jams.Annotation(namespace=namespace)

    time = np.arange(offset, offset + len(values))
    duration = [1] * len(time)

    for t, d, v in zip(time, duration, values):
        ann.append(time=t, duration=d, value=v)

    return ann

def test_beat_valid():

    ref_ann = create_annotation(values=np.arange(10) % 4 + 1.,
                                namespace='beat')

    est_ann = create_annotation(values=np.arange(9) % 4 + 1.,
                                namespace='beat',
                                offset=0.01)

    jams.eval.beat(ref_ann, est_ann)

def test_beat_invalid():

    def __test(ref, est):
        jams.eval.beat(ref, est)

    ref_ann = create_annotation(values=np.arange(10) % 4 + 1.,
                                namespace='beat')

    est_ann = create_annotation(values=np.arange(9) % 4 + 1.,
                                namespace='onsets',
                                offset=0.01)

    yield raises(jams.NamespaceError)(__test), ref_ann, est_ann
    yield raises(jams.NamespaceError)(__test), est_ann, ref_ann

    est_ann = create_annotation(values=np.arange(9) % 4 + 1.,
                                namespace='beat',
                                offset=-10)
    yield raises(jams.SchemaError)(__test), ref_ann, est_ann
    yield raises(jams.SchemaError)(__test), est_ann, ref_ann

# Onset detection
def test_onset_valid():

    ref_ann = create_annotation(values=np.arange(10) % 4 + 1.,
                                namespace='onsets')

    est_ann = create_annotation(values=np.arange(9) % 4 + 1.,
                                namespace='onsets',
                                offset=0.01)

    jams.eval.onset(ref_ann, est_ann)

def test_onset_invalid():

    def __test(ref, est):
        jams.eval.onset(ref, est)

    ref_ann = create_annotation(values=np.arange(10) % 4 + 1.,
                                namespace='onsets')

    est_ann = create_annotation(values=np.arange(9) % 4 + 1.,
                                namespace='beat',
                                offset=0.01)

    yield raises(jams.NamespaceError)(__test), ref_ann, est_ann
    yield raises(jams.NamespaceError)(__test), est_ann, ref_ann

    est_ann = create_annotation(values=np.arange(9) % 4 + 1.,
                                namespace='onsets',
                                offset=-10)
    yield raises(jams.SchemaError)(__test), ref_ann, est_ann
    yield raises(jams.SchemaError)(__test), est_ann, ref_ann


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

    yield raises(jams.NamespaceError)(__test), ref_ann, est_ann
    yield raises(jams.NamespaceError)(__test), est_ann, ref_ann

    est_ann = create_annotation(values=['D', 'E', 'not at all a chord'],
                                namespace='chord_harte',
                                offset=0.01)

    yield raises(jams.SchemaError)(__test), ref_ann, est_ann
    yield raises(jams.SchemaError)(__test), est_ann, ref_ann


# Segmentation

# Tempo estimation

# Melody

# Pattern discovery
