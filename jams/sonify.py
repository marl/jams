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


def pitch_contour(annotation, sr=22050, length=None, **kwargs):
    '''Sonify pitch contours in Hz'''

    times, values = annotation.data.to_interval_values()

    indices = np.unique([v['index'] for v in values])

    y_out = 0.0
    for ix in indices:
        rows = annotation.data.value.apply(lambda x: x['index'] == ix).nonzero()[0]

        freqs = np.asarray([values[r]['frequency'] for r in rows])
        unv = ~np.asarray([values[r]['voiced'] for r in rows])
        freqs[unv] *= -1

        y_out = y_out + filter_kwargs(mir_eval.sonify.pitch_contour,
                                      times[rows, 0],
                                      freqs,
                                      fs=sr, length=length,
                                      **kwargs)

    return y_out


def piano_roll(annotation, sr=22050, length=None, **kwargs):
    '''Sonify a piano-roll'''

    intervals, pitches = annotation.data.to_interval_values()

    # Construct the pitchogram
    pitch_map = {f: idx for idx, f in enumerate(np.unique(pitches))}

    gram = np.zeros((len(pitch_map), len(intervals)))

    for col, f in enumerate(pitches):
        gram[pitch_map[f], col] = 1

    return filter_kwargs(mir_eval.sonify.time_frequency,
                         gram, pitches, intervals,
                         sr, length=length, **kwargs)


SONIFY_MAPPING = OrderedDict()
SONIFY_MAPPING['beat'] = clicks
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
            ann = coerce_annotation(annotation, namespace)
            return func(ann, sr=sr, length=length, **kwargs)
        except NamespaceError:
            pass

    raise NamespaceError('Unable to sonify annotation of namespace="{:s}"'
                         .format(annotation.namespace))
