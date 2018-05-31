#!/usr/bin/env python
r'''
Display
-------

.. autosummary::
    :toctree: generated/

    display
    display_multi
'''

from collections import OrderedDict

import json
import re
import six

import numpy as np

import matplotlib.pyplot as plt
from matplotlib.offsetbox import AnchoredText

import mir_eval.display

from .eval import hierarchy_flatten
from .exceptions import NamespaceError, ParameterError
from .eval import coerce_annotation
from .nsconvert import can_convert


def pprint_jobject(obj, **kwargs):
    '''Pretty-print a jobject.

    Parameters
    ----------
    obj : jams.JObject

    kwargs
        additional parameters to `json.dumps`

    Returns
    -------
    string
        A simplified display of `obj` contents.
    '''

    obj_simple = {k: v for k, v in six.iteritems(obj.__json__) if v}

    string = json.dumps(obj_simple, **kwargs)

    # Suppress braces and quotes
    string = re.sub(r'[{}"]', '', string)

    # Kill trailing commas
    string = re.sub(r',\n', '\n', string)

    # Kill blank lines
    string = re.sub(r'^\s*$', '', string)

    return string


def intervals(annotation, **kwargs):
    '''Plotting wrapper for labeled intervals'''
    times, labels = annotation.to_interval_values()

    return mir_eval.display.labeled_intervals(times, labels, **kwargs)


def hierarchy(annotation, **kwargs):
    '''Plotting wrapper for hierarchical segmentations'''
    htimes, hlabels = hierarchy_flatten(annotation)

    htimes = [np.asarray(_) for _ in htimes]
    return mir_eval.display.hierarchy(htimes, hlabels, **kwargs)


def pitch_contour(annotation, **kwargs):
    '''Plotting wrapper for pitch contours'''
    ax = kwargs.pop('ax', None)

    # If the annotation is empty, we need to construct a new axes
    ax = mir_eval.display.__get_axes(ax=ax)[0]

    times, values = annotation.to_interval_values()

    indices = np.unique([v['index'] for v in values])

    for idx in indices:
        rows = [i for (i, v) in enumerate(values) if v['index'] == idx]
        freqs = np.asarray([values[r]['frequency'] for r in rows])
        unvoiced = ~np.asarray([values[r]['voiced'] for r in rows])
        freqs[unvoiced] *= -1

        ax = mir_eval.display.pitch(times[rows, 0], freqs, unvoiced=True,
                                    ax=ax,
                                    **kwargs)
    return ax


def event(annotation, **kwargs):
    '''Plotting wrapper for events'''

    times, values = annotation.to_interval_values()

    if any(values):
        labels = values
    else:
        labels = None

    return mir_eval.display.events(times, labels=labels, **kwargs)


def beat_position(annotation, **kwargs):
    '''Plotting wrapper for beat-position data'''

    times, values = annotation.to_interval_values()

    labels = [_['position'] for _ in values]

    # TODO: plot time signature, measure number
    return mir_eval.display.events(times, labels=labels, **kwargs)


def piano_roll(annotation, **kwargs):
    '''Plotting wrapper for piano rolls'''
    times, midi = annotation.to_interval_values()

    return mir_eval.display.piano_roll(times, midi=midi, **kwargs)


VIZ_MAPPING = OrderedDict()

VIZ_MAPPING['segment_open'] = intervals
VIZ_MAPPING['chord'] = intervals
VIZ_MAPPING['multi_segment'] = hierarchy
VIZ_MAPPING['pitch_contour'] = pitch_contour
VIZ_MAPPING['beat_position'] = beat_position
VIZ_MAPPING['beat'] = event
VIZ_MAPPING['onset'] = event
VIZ_MAPPING['note_midi'] = piano_roll
VIZ_MAPPING['tag_open'] = intervals


def display(annotation, meta=True, **kwargs):
    '''Visualize a jams annotation through mir_eval

    Parameters
    ----------
    annotation : jams.Annotation
        The annotation to display

    meta : bool
        If `True`, include annotation metadata in the figure

    kwargs
        Additional keyword arguments to mir_eval.display functions

    Returns
    -------
    ax
        Axis handles for the new display

    Raises
    ------
    NamespaceError
        If the annotation cannot be visualized
    '''

    for namespace, func in six.iteritems(VIZ_MAPPING):
        try:
            ann = coerce_annotation(annotation, namespace)

            axes = func(ann, **kwargs)

            # Title should correspond to original namespace, not the coerced version
            axes.set_title(annotation.namespace)
            if meta:
                description = pprint_jobject(annotation.annotation_metadata, indent=2)

                anchored_box = AnchoredText(description.strip('\n'),
                                            loc=2,
                                            frameon=True,
                                            bbox_to_anchor=(1.02, 1.0),
                                            bbox_transform=axes.transAxes,
                                            borderpad=0.0)
                axes.add_artist(anchored_box)

                axes.figure.subplots_adjust(right=0.8)

            return axes
        except NamespaceError:
            pass

    raise NamespaceError('Unable to visualize annotation of namespace="{:s}"'
                         .format(annotation.namespace))


def display_multi(annotations, fig_kw=None, meta=True, **kwargs):
    '''Display multiple annotations with shared axes

    Parameters
    ----------
    annotations : jams.AnnotationArray
        A collection of annotations to display

    fig_kw : dict
        Keyword arguments to `plt.figure`

    meta : bool
        If `True`, display annotation metadata for each annotation

    kwargs
        Additional keyword arguments to the `mir_eval.display` routines

    Returns
    -------
    fig
        The created figure
    axs
        List of subplot axes corresponding to each displayed annotation
    '''
    if fig_kw is None:
        fig_kw = dict()

    fig_kw.setdefault('sharex', True)
    fig_kw.setdefault('squeeze', True)

    # Filter down to coercable annotations first
    display_annotations = []
    for ann in annotations:
        for namespace in VIZ_MAPPING:
            if can_convert(ann, namespace):
                display_annotations.append(ann)
                break

    # If there are no displayable annotations, fail here
    if not len(display_annotations):
        raise ParameterError('No displayable annotations found')

    fig, axs = plt.subplots(nrows=len(display_annotations), ncols=1, **fig_kw)

    # MPL is stupid when making singleton subplots.
    # We catch this and make it always iterable.
    if len(display_annotations) == 1:
        axs = [axs]

    for ann, ax in zip(display_annotations, axs):
        kwargs['ax'] = ax
        display(ann, meta=meta, **kwargs)

    return fig, axs
