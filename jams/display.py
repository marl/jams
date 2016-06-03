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

import six

import matplotlib.pyplot as plt
import mir_eval.display

from .eval import hierarchy_flatten
from .exceptions import NamespaceError
from .eval import coerce_annotation
from .nsconvert import can_convert


def intervals(annotation, **kwargs):
    '''Plotting wrapper for labeled intervals'''
    times, labels = annotation.data.to_interval_values()

    return mir_eval.display.labeled_intervals(times, labels, **kwargs)


def hierarchy(annotation, **kwargs):
    '''Plotting wrapper for hierarchical segmentations'''
    htimes, hlabels = hierarchy_flatten(annotation)

    return mir_eval.display.hierarchy(htimes, hlabels, **kwargs)


def pitch(annotation, **kwargs):
    '''Plotting wrapper for monophonic pitch contours'''
    times, values = annotation.data.to_interval_values()

    return mir_eval.display.pitch(times[:, 0], values, unvoiced=True, **kwargs)


VIZ_MAPPING = OrderedDict()

VIZ_MAPPING['segment_open'] = intervals
VIZ_MAPPING['chord'] = intervals
VIZ_MAPPING['multi_segment'] = hierarchy
VIZ_MAPPING['pitch_hz'] = pitch



def display(annotation, **kwargs):
    '''Visualize a jams annotation through mir_eval

    Parameters
    ----------
    annotation : jams.Annotation
        The annotation to display

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
            ax.set_title('{} | {}'.format(annotation.namespace,
                                          annotation.annotation_metadata.annotator.name))
            return ax
        except NamespaceError:
            pass

    raise NamespaceError('Unable to visualize annotation of namespace="{:s}"'
                         .format(annotation.namespace))


def display_multi(annotations, fig_kw=None, **kwargs):
    '''Display multiple annotations with shared axes

    Parameters
    ----------
    annotations : jams.AnnotationArray
        A collection of annotations to display

    fig_kw : dict
        Keyword arguments to `plt.figure`

    kwargs
        Additional keyword arguments to the `mir_eval.display` routines

    Returns
    -------
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

    _, axs = plt.subplots(nrows=len(display_annotations), ncols=1, **fig_kw)

    for ann, ax in zip(display_annotations, axs):
        kwargs['ax'] = ax
        display(ann, **kwargs)

    return axs
