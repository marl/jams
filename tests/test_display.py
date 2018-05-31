#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import numpy as np

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

import pytest
import jams
import jams.display

from jams import NamespaceError


# A simple run-without-fail test for plotting
@pytest.mark.parametrize('namespace',
                         ['segment_open', 'chord', 'multi_segment',
                          'pitch_contour', 'beat_position', 'beat',
                          'onset', 'note_midi', 'tag_open',
                          pytest.mark.xfail('tempo', raises=NamespaceError)])
@pytest.mark.parametrize('meta', [False, True])
def test_display(namespace, meta):

    ann = jams.Annotation(namespace=namespace)
    jams.display.display(ann, meta=meta)


def test_display_multi():

    jam = jams.JAMS()
    jam.annotations.append(jams.Annotation(namespace='beat'))
    jams.display.display_multi(jam.annotations)


def test_display_multi_multi():

    jam = jams.JAMS()
    jam.annotations.append(jams.Annotation(namespace='beat'))
    jam.annotations.append(jams.Annotation(namespace='chord'))

    jams.display.display_multi(jam.annotations)


def test_display_pitch_contour():

    ann = jams.Annotation(namespace='pitch_hz', duration=5)

    values = np.arange(100, 200)
    times = np.linspace(0, 2, num=len(values))

    for t, v in zip(times, values):
        ann.append(time=t, value=v, duration=0)

    jams.display.display(ann)


def test_display_labeled_events():

    times = np.arange(40)
    values = times % 4

    ann = jams.Annotation(namespace='beat', duration=60)

    for t, v in zip(times, values):
        ann.append(time=t, value=v, duration=0)

    jams.display.display(ann)


@pytest.mark.xfail(raises=jams.ParameterError)
def test_display_multi_fail():

    anns = jams.AnnotationArray()
    jams.display.display_multi(anns)
