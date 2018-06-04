#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# CREATED:2016-02-16 15:40:04 by Brian McFee <brian.mcfee@nyu.edu>
r'''
Namespace conversion
--------------------

.. autosummary::
    :toctree: generated

    convert
'''

import numpy as np

from copy import deepcopy
from collections import defaultdict

from .exceptions import NamespaceError


# The structure that handles all conversion mappings
__CONVERSION__ = defaultdict(defaultdict)

__all__ = ['convert', 'can_convert']


def _conversion(target, source):
    '''A decorator to register namespace conversions.

    Usage
    -----
    >>> @conversion('tag_open', 'tag_.*')
    ... def tag_to_open(annotation):
    ...     annotation.namespace = 'tag_open'
    ...     return annotation
    '''

    def register(func):
        '''This decorator registers func as mapping source to target'''
        __CONVERSION__[target][source] = func
        return func

    return register


def convert(annotation, target_namespace):
    '''Convert a given annotation to the target namespace.

    Parameters
    ----------
    annotation : jams.Annotation
        An annotation object

    target_namespace : str
        The target namespace

    Returns
    -------
    mapped_annotation : jams.Annotation
        if `annotation` already belongs to `target_namespace`, then
        it is returned directly.

        otherwise, `annotation` is copied and automatically converted
        to the target namespace.

    Raises
    ------
    SchemaError
        if the input annotation fails to validate

    NamespaceError
        if no conversion is possible

    Examples
    --------
    Convert frequency measurements in Hz to MIDI

    >>> ann_midi = jams.convert(ann_hz, 'note_midi')

    And back to Hz

    >>> ann_hz2 = jams.convert(ann_midi, 'note_hz')
    '''

    # First, validate the input. If this fails, we can't auto-convert.
    annotation.validate(strict=True)

    # If we're already in the target namespace, do nothing
    if annotation.namespace == target_namespace:
        return annotation

    if target_namespace in __CONVERSION__:
        # Otherwise, make a copy to mangle
        annotation = deepcopy(annotation)

        # Look for a way to map this namespace to the target
        for source in __CONVERSION__[target_namespace]:
            if annotation.search(namespace=source):
                return __CONVERSION__[target_namespace][source](annotation)

    # No conversion possible
    raise NamespaceError('Unable to convert annotation from namespace='
                         '"{0}" to "{1}"'.format(annotation.namespace,
                                                 target_namespace))


def can_convert(annotation, target_namespace):
    '''Test if an annotation can be mapped to a target namespace

    Parameters
    ----------
    annotation : jams.Annotation
        An annotation object

    target_namespace : str
        The target namespace

    Returns
    -------
    True
        if `annotation` can be automatically converted to
        `target_namespace`

    False
        otherwise
    '''

    # If we're already in the target namespace, do nothing
    if annotation.namespace == target_namespace:
        return True

    if target_namespace in __CONVERSION__:
        # Look for a way to map this namespace to the target
        for source in __CONVERSION__[target_namespace]:
            if annotation.search(namespace=source):
                return True
    return False


@_conversion('pitch_contour', 'pitch_hz')
def pitch_hz_to_contour(annotation):
    '''Convert a pitch_hz annotation to a contour'''
    annotation.namespace = 'pitch_contour'
    data = annotation.pop_data()

    for obs in data:
        annotation.append(time=obs.time, duration=obs.duration,
                          confidence=obs.confidence,
                          value=dict(index=0,
                                     frequency=np.abs(obs.value),
                                     voiced=obs.value > 0))
    return annotation


@_conversion('pitch_contour', 'pitch_midi')
def pitch_midi_to_contour(annotation):
    '''Convert a pitch_hz annotation to a contour'''
    annotation = pitch_midi_to_hz(annotation)
    return pitch_hz_to_contour(annotation)


@_conversion('note_hz', 'note_midi')
def note_midi_to_hz(annotation):
    '''Convert a pitch_midi annotation to pitch_hz'''

    annotation.namespace = 'note_hz'
    data = annotation.pop_data()

    for obs in data:
        annotation.append(time=obs.time, duration=obs.duration,
                          confidence=obs.confidence,
                          value=440 * (2.0**((obs.value - 69.0)/12.0)))

    return annotation


@_conversion('note_midi', 'note_hz')
def note_hz_to_midi(annotation):
    '''Convert a pitch_hz annotation to pitch_midi'''

    annotation.namespace = 'note_midi'

    data = annotation.pop_data()

    for obs in data:
        annotation.append(time=obs.time, duration=obs.duration,
                          confidence=obs.confidence,
                          value=12 * (np.log2(obs.value) - np.log2(440.0)) + 69)

    return annotation


@_conversion('pitch_hz', 'pitch_midi')
def pitch_midi_to_hz(annotation):
    '''Convert a pitch_midi annotation to pitch_hz'''

    annotation.namespace = 'pitch_hz'

    data = annotation.pop_data()

    for obs in data:
        annotation.append(time=obs.time, duration=obs.duration,
                          confidence=obs.confidence,
                          value=440 * (2.0**((obs.value - 69.0)/12.0)))

    return annotation


@_conversion('pitch_midi', 'pitch_hz')
def pitch_hz_to_midi(annotation):
    '''Convert a pitch_hz annotation to pitch_midi'''

    annotation.namespace = 'pitch_midi'

    data = annotation.pop_data()

    for obs in data:
        annotation.append(time=obs.time, duration=obs.duration,
                          confidence=obs.confidence,
                          value=12 * (np.log2(obs.value) - np.log2(440.0)) + 69)
    return annotation


@_conversion('segment_open', 'segment_.*')
def segment_to_open(annotation):
    '''Convert any segmentation to open label space'''

    annotation.namespace = 'segment_open'
    return annotation


@_conversion('tag_open', 'tag_.*')
def tag_to_open(annotation):
    '''Convert any tag annotation to open label space'''

    annotation.namespace = 'tag_open'
    return annotation


@_conversion('tag_open', 'scaper')
def scaper_to_tag(annotation):
    '''Convert scaper annotations to tag_open'''

    annotation.namespace = 'tag_open'

    data = annotation.pop_data()
    for obs in data:
        annotation.append(time=obs.time, duration=obs.duration,
                          confidence=obs.confidence, value=obs.value['label'])

    return annotation


@_conversion('beat', 'beat_position')
def beat_position(annotation):
    '''Convert beat_position to beat'''

    annotation.namespace = 'beat'
    data = annotation.pop_data()
    for obs in data:
        annotation.append(time=obs.time, duration=obs.duration,
                          confidence=obs.confidence,
                          value=obs.value['position'])

    return annotation


@_conversion('chord', 'chord_harte')
def chordh_to_chord(annotation):
    '''Convert Harte annotation to chord'''

    annotation.namespace = 'chord'
    return annotation
