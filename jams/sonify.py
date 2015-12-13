#!/usr/bin/env python
# CREATED:2015-12-12 18:20:37 by Brian McFee <brian.mcfee@nyu.edu>
r'''
Sonification
============

.. autosummary::
    :toctree: generated/

    sonify
'''

import six
import numpy as np
import mir_eval.sonify
from mir_eval.util import filter_kwargs
from .eval import validate_annotation
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


def pitch_midi(annotation, sr=22050, length=None, **kwargs):
    '''Sonify midi pitches'''

    intervals, notes = annotation.data.to_interval_values()

    freqs = 440.0 * (2.0 ** ((np.arange(128) - 69.0)/12.0))

    gram = np.zeros((len(freqs), len(notes)))

    for t, n in enumerate(notes):
        gram[n, t] = 1.0

    # Compress for efficiency
    idx = gram.max(axis=1) > 0

    gram = gram[idx]
    freqs = freqs[idx]

    return filter_kwargs(mir_eval.sonify.time_frequency,
                         gram, freqs, intervals,
                         fs=sr, length=length,
                         **kwargs)


SONIFY_MAPPING = {'beat.*|segment.*|onset.*': clicks,
                  'chord|chord_harte': chord,
                  'pitch_midi': pitch_midi}


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
            validate_annotation(annotation, namespace)
            return func(annotation, sr=sr, length=length, **kwargs)
        except NamespaceError:
            pass

    raise NamespaceError('Unable to sonify annotation of namespace="{:s}"'
                         .format(annotation.namespace))
