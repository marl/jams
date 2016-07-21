#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

import jams
import jams.display

from nose.tools import raises
from jams import NamespaceError

# A simple run-without-fail test for plotting
def test_display():

    def __test(namespace, meta):

        fig = plt.figure()
        ann = jams.Annotation(namespace=namespace)
        jams.display.display(ann, meta=meta)


    for namespace in ['segment_open', 'chord', 'multi_segment', 'pitch_contour',
                      'beat_position', 'beat', 'onset', 'note_midi']:
        for meta in [False, True]:

            yield __test, namespace, meta
    yield raises(NamespaceError)(__test), 'tempo', False


def test_display_multi():

    jam = jams.JAMS()
    jam.annotations.append(jams.Annotation(namespace='beat'))
    jam.annotations.append(jams.Annotation(namespace='chord'))

    jams.display.display_multi(jam.annotations)


@raises(jams.ParameterError)
def test_display_multi_fail():

    anns = jams.AnnotationArray()
    jams.display.display_multi(anns)

