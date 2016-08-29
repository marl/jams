#!/usr/bin/env python
# CREATED:2016-02-11 12:07:58 by Brian McFee <brian.mcfee@nyu.edu>
"""Sonification tests"""

import six
import numpy as np

from nose.tools import raises, eq_

import jams

@raises(jams.NamespaceError)
def test_no_sonify():

    ann = jams.Annotation(namespace='vector')
    jams.sonify.sonify(ann)


@raises(jams.SchemaError)
def test_bad_sonify():
    ann = jams.Annotation(namespace='chord')
    ann.append(time=0, duration=1, value='not a chord')

    jams.sonify.sonify(ann)

def test_duration():

    def __test(ns, duration, sr):
        ann = jams.Annotation(namespace=ns)
        ann.append(time=3, duration=1, value='C')

        y = jams.sonify.sonify(ann, sr=sr, duration=duration)

        if duration is not None:
            eq_(len(y), int(sr * duration))


    for ns in ['segment_open', 'chord']:
        for sr in [8000, 11025]:
            for dur in [None, 5.0, 10.0]:
                yield __test, ns, dur, sr


def test_pitch_hz():
    ann = jams.Annotation(namespace='pitch_hz')
    ann.append(time=0, duration=1, value=261.0)
    y = jams.sonify.sonify(ann, sr=8000, duration=2.0)

    eq_(len(y), 8000 * 2)

def test_pitch_midi():
    ann = jams.Annotation(namespace='pitch_midi')
    ann.append(time=0, duration=1, value=60)
    y = jams.sonify.sonify(ann, sr=8000, duration=2.0)

    eq_(len(y), 8000 * 2)


def test_chord():

    def __test(namespace, value):
        ann = jams.Annotation(namespace=namespace)
        ann.append(time=0.5, duration=1.0, value=value)
        y = jams.sonify.sonify(ann, sr=8000, duration=2.0)
    
        eq_(len(y), 8000 * 2)

    yield __test, 'chord', 'C:maj/5'
    yield __test, 'chord_harte', 'C:maj/5'


def test_event():

    def __test(namespace, value):
        ann = jams.Annotation(namespace=namespace)
        ann.append(time=0.5, duration=0, value=value)
        y = jams.sonify.sonify(ann, sr=8000, duration=2.0)
    
        eq_(len(y), 8000 * 2)

    yield __test, 'beat', 1
    yield __test, 'segment_open', 'C'
    yield __test, 'onset', 1
