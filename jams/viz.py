#!/usr/bin/env python
# CREATED: 4/15/16 3:31 PM by Justin Salamon <justin.salamon@nyu.edu>
r'''
Visualization
=============
'''

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import cnames
import matplotlib.patches as mpatches
import seaborn as sns

__colornames__ = cnames.keys()


def plot(annotation_list, annotation_labels=None):
    r'''Plot annotations

    Parameters
    ----------
    annotation_list : list of jams.Annotation
        List of annotation objects
    annotation_labels : list of str or None
        List of annotation labels for plot legend. If None, annotations will be
        labeled with integers (starting at 0) based on their order in the
        annotation list.
    '''
    # if labels are not provided, create them
    if annotation_labels is None:
        labels = [str(n) for n in range(len(annotation_list))]
    else:
        labels = annotation_labels

    # group annotations by namespace
    annotations = {}
    for ann, label in zip(annotation_list, labels):
        if ann.namespace in annotations.keys():
            annotations[ann.namespace][0].append(ann)
            annotations[ann.namespace][1].append(label)
        else:
            annotations[ann.namespace] = ([ann], [label])

    # plot each group of annotations with same namespace
    for namespace in annotations.keys():
        if namespace in __namespace__.keys():
            __namespace__[namespace](*annotations[namespace])


def _plot_pitch_midi(annotation_list, annotation_labels):
    r'''Plot pitch_midi annotations

    Parameters
    ----------
    annotation_list : list of jams.Annotation
        List of annotation objects
    annotation_labels : list of str
        List of annotation labels for plot legend
    '''
    fig = plt.figure()
    ax = fig.add_subplot(111)

    onsets = []
    offsets = []

    for i, ann in enumerate(annotation_list):
        for n, note in enumerate(ann.data.values):
            t = note[0].total_seconds()
            d = note[1].total_seconds()
            p = note[2] - 0.25
            if n == 0:
                r = mpatches.Rectangle(
                    (t, p), d, 0.5, fill=True, alpha=0.5,
                    color=__colornames__[i], label=annotation_labels[i])
            else:
                r = mpatches.Rectangle(
                    (t, p), d, 0.5, fill=True, alpha=0.5,
                    color=__colornames__[i])
            ax.add_patch(r)
            onsets.append(t)
            offsets.append(t+d)

    starttime = np.min(onsets) - 1
    endtime = np.max(offsets) + 1
    minpitch = np.min([ann.data.value.min() for ann in annotation_list]) - 1
    maxpitch = np.max([ann.data.value.max() for ann in annotation_list]) + 1
    plt.xlim([starttime, endtime])
    plt.ylim([minpitch, maxpitch])
    plt.xlabel('Time (s)')
    plt.ylabel('Pitch (MIDI number)')
    plt.legend()
    plt.show()


__namespace__ = {
    'pitch_midi': _plot_pitch_midi
}
