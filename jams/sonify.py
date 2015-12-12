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
import mir_eval.sonify
from .eval import validate_annotation
from .exceptions import NamespaceError

__all__ = ['sonify']


def clicks(annotation, sr=22050, duration=None, **kwargs):
    '''Sonify clicks timings

    '''

    ref_interval, _ = annotation.data.to_interval_values()

    length = None
    if duration is not None:
        length = int(duration * sr)

    return mir_eval.sonify.clicks(ref_interval[:, 0], fs=sr, length=length, **kwargs)

def chord(annotation, sr=22050, duration=None, **kwargs):
    '''Sonify chords

    '''

    intervals, chords = annotation.data.to_interval_values()

    length = None
    if duration is not None:
        length = int(duration * sr)

    return mir_eval.sonify.chords(chords, intervals, fs=sr, length=length, **kwargs)

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

    # TODO: add pitch contour sonification here
    SONIFY_MAPPING = {'beat.*|segment.*|onset.*': clicks,
                      'chord|chord_harte': chord}

    for namespace, func in six.iteritems(SONIFY_MAPPING):
        try:
            validate_annotation(annotation, namespace)
            return func(annotation, sr=sr, duration=duration, **kwargs)
        except NamespaceError:
            pass

    raise NamespaceError('Unable to sonify annotation of namespace="{:s}"'
                         .format(annotation.namespace))
