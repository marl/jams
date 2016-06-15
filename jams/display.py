#!/usr/bin/env python
r'''
Display
=======

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
from matplotlib.offsetbox import AnchoredOffsetbox, TextArea

import mir_eval.display

from .eval import hierarchy_flatten
from .exceptions import NamespaceError
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
    times, labels = annotation.data.to_interval_values()

    return mir_eval.display.labeled_intervals(times, labels, **kwargs)


def hierarchy(annotation, **kwargs):
    '''Plotting wrapper for hierarchical segmentations'''
    htimes, hlabels = hierarchy_flatten(annotation)

    htimes = [np.asarray(_) for _ in htimes]
    return mir_eval.display.hierarchy(htimes, hlabels, **kwargs)


def pitch(annotation, **kwargs):
    '''Plotting wrapper for monophonic pitch contours'''
    times, values = annotation.data.to_interval_values()

    return mir_eval.display.pitch(times[:, 0], values, unvoiced=True, **kwargs)


def event(annotation, **kwargs):
    '''Plotting wrapper for events'''

    times, values = annotation.data.to_interval_values()

    if any(values):
        labels = values
    else:
        labels = None

    return mir_eval.display.events(times, labels=labels, **kwargs)


def beat_position(annotation, **kwargs):
    '''Plotting wrapper for beat-position data'''

    times, values = annotation.data.to_interval_values()

    labels = [_['position'] for _ in values]

    # TODO: plot time signature, measure number
    return mir_eval.display.events(times, labels=labels, **kwargs)


VIZ_MAPPING = OrderedDict()

VIZ_MAPPING['segment_open'] = intervals
VIZ_MAPPING['chord'] = intervals
VIZ_MAPPING['multi_segment'] = hierarchy
VIZ_MAPPING['pitch_hz'] = pitch
VIZ_MAPPING['beat_position'] = beat_position
VIZ_MAPPING['beat'] = event
VIZ_MAPPING['onset'] = event


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
            coerce_annotation(annotation, namespace)

            ax = func(annotation, **kwargs)

            ax.set_title(annotation.namespace)
            if meta:
                description = pprint_jobject(annotation.annotation_metadata, indent=2)

                anchored_box = AnchoredOffsetbox(loc=2,
                                                 child=TextArea(description.strip()),
                                                 frameon=True,
                                                 bbox_to_anchor=(1.02, 1.0),
                                                 bbox_transform=ax.transAxes,
                                                 borderpad=0.)
                ax.add_artist(anchored_box)

                ax.figure.subplots_adjust(right=0.8)

            return ax
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

    fig, axs = plt.subplots(nrows=len(display_annotations), ncols=1, **fig_kw)

    for ann, ax in zip(display_annotations, axs):
        kwargs['ax'] = ax
        display(ann, meta=meta, **kwargs)

    return fig, axs
