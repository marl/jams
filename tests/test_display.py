#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import numpy as np

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

import pytest
import jams
import jams.display

from jams import NamespaceError


# A simple run-without-fail test for plotting
@pytest.mark.parametrize(
    "namespace",
    [
        "segment_open",
        "chord",
        "multi_segment",
        "pitch_contour",
        "beat_position",
        "beat",
        "onset",
        "note_midi",
        "tag_open",
    ],
)
@pytest.mark.parametrize("meta", [False, True])
def test_display(namespace, meta):

    ann = jams.Annotation(namespace=namespace)
    jams.display.display(ann, meta=meta)


@pytest.mark.parametrize("namespace", ["tempo"])
@pytest.mark.parametrize("meta", [False, True])
def test_display_exception(namespace, meta):
    with pytest.raises(NamespaceError):
        ann = jams.Annotation(namespace=namespace)
        jams.display.display(ann, meta=meta)


def test_display_multi():

    jam = jams.JAMS()
    jam.annotations.append(jams.Annotation(namespace="beat"))
    jams.display.display_multi(jam.annotations)


def test_display_multi_multi():

    jam = jams.JAMS()
    jam.annotations.append(jams.Annotation(namespace="beat"))
    jam.annotations.append(jams.Annotation(namespace="chord"))

    jams.display.display_multi(jam.annotations)


def test_display_pitch_contour():

    ann = jams.Annotation(namespace="pitch_hz", duration=5)

    values = np.arange(100, 200)
    times = np.linspace(0, 2, num=len(values))

    for t, v in zip(times, values):
        ann.append(time=t, value=v, duration=0)

    jams.display.display(ann)


@pytest.mark.parametrize("namespace", ["onset", "beat", "beat_position"])
def test_display_labeled_events(namespace):
    times = [0.25, 0.75, 1.5]
    labels = ["kick", "snare", "hat"] if namespace == "onset" else [1, 2, 3]
    values = labels
    if namespace == "beat_position":
        values = [
            dict(position=label, measure=1, num_beats=4, beat_units=4)
            for label in labels
        ]

    ann = jams.Annotation(namespace=namespace)
    for t, v in zip(times, values):
        ann.append(time=t, value=v, duration=0)

    fig, ax = plt.subplots()
    try:
        jams.display.display(ann, ax=ax, meta=False)
        segments = ax.collections[0].get_segments()
        assert [segment[0, 0] for segment in segments] == times
        assert [(text.get_text(), text.xy[0]) for text in ax.texts] == [
            (str(label), time) for label, time in zip(labels, times)
        ]
    finally:
        plt.close(fig)


def test_display_multi_fail():
    anns = jams.AnnotationArray()

    with pytest.raises(jams.ParameterError):
        jams.display.display_multi(anns)
