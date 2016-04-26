#!/usr/bin/env python
# CREATED:2015-12-12 18:20:37 by Brian McFee <brian.mcfee@nyu.edu>
r'''
Sonification
============

.. autosummary::
    :toctree: generated/

    sonify
'''

from collections import OrderedDict
import six
import numpy as np
import mir_eval.sonify
from mir_eval.util import filter_kwargs
from .eval import coerce_annotation
from .exceptions import NamespaceError

__all__ = ['sonify']



def clicks(annotation, sr=22050, length=None, **kwargs):
    '''Sonify clicks timings

    '''

    interval, _ = annotation.data.to_interval_values()

    return filter_kwargs(mir_eval.sonify.clicks, interval[:, 0],
                         fs=sr, length=length, **kwargs)


def chord(annotation, sr=22050, length=None, **kwargs):
    '''Sonify chords'''

    intervals, chords = annotation.data.to_interval_values()

    return filter_kwargs(mir_eval.sonify.chords,
                         chords, intervals,
                         fs=sr, length=length,
                         **kwargs)


def pitch_hz(annotation, sr=22050, length=None, **kwargs):
    '''Sonify pitches in Hz'''

    intervals, pitches = annotation.data.to_interval_values()

    # Handle instantaneous pitch measurements: if at least 98% of
    # observations have zero duration, call it continuous
    if np.percentile(intervals[:, 0] - intervals[:, 1], 98) == 0:
        intervals[:-1, 1] = intervals[:-1, 0] + np.diff(intervals[:, 0])
        if annotation.duration is not None:
            intervals[-1, 1] = annotation.duration
        elif length is not None:
            intervals[-1, 1] = length / float(sr)

    if length is None:
        if np.any(intervals):
            length = int(np.max(intervals[:, 1]) * sr)
        else:
            length = 0

    # Discard anything unvoiced or zero-duration
    pitches = np.asarray(pitches)
    good_idx = (intervals[:, 1] > intervals[:, 0]) & (pitches > 0)
    intervals = intervals[good_idx]
    pitches = pitches[good_idx]

    # Collapse down to a unique set of frequency values
    freqs = np.unique(pitches)

    if freqs.size == 0:
        # We have no usable data.  Return an empty signal
        return np.zeros(length)

    # Build the piano roll
    pitch_index = {p: i for i, p in enumerate(freqs)}
    gram = np.zeros((len(freqs), len(pitches)))
    for t, n in enumerate(pitches):
        gram[pitch_index[n], t] = 1.0

    return filter_kwargs(mir_eval.sonify.time_frequency,
                         gram, freqs, intervals,
                         fs=sr, length=length,
                         **kwargs)


SONIFY_MAPPING = OrderedDict()
SONIFY_MAPPING['beat'] = clicks
SONIFY_MAPPING['segment_open'] = clicks
SONIFY_MAPPING['onset'] = clicks
SONIFY_MAPPING['chord'] = chord
SONIFY_MAPPING['pitch_hz'] = pitch_hz


def sonify(annotation, sr=22050, duration=None, **kwargs):
    '''Sonify a jams annotation through mir_eval

    Parameters
    ----------
    annotation : jams.Annotation
        The annotation to sonify

    sr = : int > 0
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
    if duration is not None:
        length = int(duration * sr)

    for namespace, func in six.iteritems(SONIFY_MAPPING):
        try:
            coerce_annotation(annotation, namespace)
            return func(annotation, sr=sr, length=length, **kwargs)
        except NamespaceError:
            pass

    raise NamespaceError('Unable to sonify annotation of namespace="{:s}"'
                         .format(annotation.namespace))
