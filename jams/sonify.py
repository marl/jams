#!/usr/bin/env python
# CREATED:2015-12-12 18:20:37 by Brian McFee <brian.mcfee@nyu.edu>
r'''
Sonification
------------

.. autosummary::
    :toctree: generated/

    sonify
'''

from itertools import product
from collections import OrderedDict, defaultdict
import six
import numpy as np
import mir_eval.sonify
from mir_eval.util import filter_kwargs
from .eval import coerce_annotation, hierarchy_flatten
from .exceptions import NamespaceError

__all__ = ['sonify']


def mkclick(freq, sr=22050, duration=0.1):
    '''Generate a click sample.

    This replicates functionality from mir_eval.sonify.clicks,
    but exposes the target frequency and duration.
    '''

    times = np.arange(int(sr * duration))
    click = np.sin(2 * np.pi * times * freq / float(sr))
    click *= np.exp(- times / (1e-2 * sr))

    return click


def clicks(annotation, sr=22050, length=None, **kwargs):
    '''Sonify events with clicks.

    This uses mir_eval.sonify.clicks, and is appropriate for instantaneous
    events such as beats or segment boundaries.
    '''

    interval, _ = annotation.to_interval_values()

    return filter_kwargs(mir_eval.sonify.clicks, interval[:, 0],
                         fs=sr, length=length, **kwargs)


def downbeat(annotation, sr=22050, length=None, **kwargs):
    '''Sonify beats and downbeats together.
    '''

    beat_click = mkclick(440 * 2, sr=sr)
    downbeat_click = mkclick(440 * 3, sr=sr)

    intervals, values = annotation.to_interval_values()

    beats, downbeats = [], []

    for time, value in zip(intervals[:, 0], values):
        if value['position'] == 1:
            downbeats.append(time)
        else:
            beats.append(time)

    if length is None:
        length = int(sr * np.max(intervals)) + len(beat_click) + 1

    y = filter_kwargs(mir_eval.sonify.clicks,
                      np.asarray(beats),
                      fs=sr, length=length, click=beat_click)

    y += filter_kwargs(mir_eval.sonify.clicks,
                       np.asarray(downbeats),
                       fs=sr, length=length, click=downbeat_click)

    return y


def multi_segment(annotation, sr=22050, length=None, **kwargs):
    '''Sonify multi-level segmentations'''

    # Pentatonic scale, because why not
    PENT = [1, 32./27, 4./3, 3./2, 16./9]
    DURATION = 0.1

    h_int, _ = hierarchy_flatten(annotation)

    if length is None:
        length = int(sr * (max(np.max(_) for _ in h_int) + 1. / DURATION) + 1)

    y = 0.0
    for ints, (oc, scale) in zip(h_int, product(range(3, 3 + len(h_int)),
                                                PENT)):
        click = mkclick(440.0 * scale * oc, sr=sr, duration=DURATION)
        y = y + filter_kwargs(mir_eval.sonify.clicks,
                              np.unique(ints),
                              fs=sr, length=length,
                              click=click)
    return y


def chord(annotation, sr=22050, length=None, **kwargs):
    '''Sonify chords

    This uses mir_eval.sonify.chords.
    '''

    intervals, chords = annotation.to_interval_values()

    return filter_kwargs(mir_eval.sonify.chords,
                         chords, intervals,
                         fs=sr, length=length,
                         **kwargs)


def pitch_contour(annotation, sr=22050, length=None, **kwargs):
    '''Sonify pitch contours.

    This uses mir_eval.sonify.pitch_contour, and should only be applied
    to pitch annotations using the pitch_contour namespace.

    Each contour is sonified independently, and the resulting waveforms
    are summed together.
    '''

    # Map contours to lists of observations

    times = defaultdict(list)
    freqs = defaultdict(list)

    for obs in annotation:
        times[obs.value['index']].append(obs.time)
        freqs[obs.value['index']].append(obs.value['frequency'] *
                                         (-1)**(~obs.value['voiced']))

    y_out = 0.0
    for ix in times:
        y_out = y_out + filter_kwargs(mir_eval.sonify.pitch_contour,
                                      np.asarray(times[ix]),
                                      np.asarray(freqs[ix]),
                                      fs=sr, length=length,
                                      **kwargs)
        if length is None:
            length = len(y_out)

    return y_out


def piano_roll(annotation, sr=22050, length=None, **kwargs):
    '''Sonify a piano-roll

    This uses mir_eval.sonify.time_frequency, and is appropriate
    for sparse transcription data, e.g., annotations in the `note_midi`
    namespace.
    '''

    intervals, pitches = annotation.to_interval_values()

    # Construct the pitchogram
    pitch_map = {f: idx for idx, f in enumerate(np.unique(pitches))}

    gram = np.zeros((len(pitch_map), len(intervals)))

    for col, f in enumerate(pitches):
        gram[pitch_map[f], col] = 1

    return filter_kwargs(mir_eval.sonify.time_frequency,
                         gram, pitches, intervals,
                         sr, length=length, **kwargs)


SONIFY_MAPPING = OrderedDict()
SONIFY_MAPPING['beat_position'] = downbeat
SONIFY_MAPPING['beat'] = clicks
SONIFY_MAPPING['multi_segment'] = multi_segment
SONIFY_MAPPING['segment_open'] = clicks
SONIFY_MAPPING['onset'] = clicks
SONIFY_MAPPING['chord'] = chord
SONIFY_MAPPING['note_hz'] = piano_roll
SONIFY_MAPPING['pitch_contour'] = pitch_contour


def sonify(annotation, sr=22050, duration=None, **kwargs):
    '''Sonify a jams annotation through mir_eval

    Parameters
    ----------
    annotation : jams.Annotation
        The annotation to sonify

    sr = : positive number
        The sampling rate of the output waveform

    duration : float (optional)
        Optional length (in seconds) of the output waveform

    kwargs
        Additional keyword arguments to mir_eval.sonify functions

    Returns
    -------
    y_sonified : np.ndarray
        The waveform of the sonified annotation

    Raises
    ------
    NamespaceError
        If the annotation has an un-sonifiable namespace
    '''

    length = None

    if duration is None:
        duration = annotation.duration

    if duration is not None:
        length = int(duration * sr)

    # If the annotation can be directly sonified, try that first
    if annotation.namespace in SONIFY_MAPPING:
        ann = coerce_annotation(annotation, annotation.namespace)
        return SONIFY_MAPPING[annotation.namespace](ann,
                                                    sr=sr,
                                                    length=length,
                                                    **kwargs)

    for namespace, func in six.iteritems(SONIFY_MAPPING):
        try:
            ann = coerce_annotation(annotation, namespace)
            return func(ann, sr=sr, length=length, **kwargs)
        except NamespaceError:
            pass

    raise NamespaceError('Unable to sonify annotation of namespace="{:s}"'
                         .format(annotation.namespace))
