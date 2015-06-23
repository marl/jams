#!/usr/bin/env python
# CREATED:2015-02-04 16:39:00 by Brian McFee <brian.mcfee@nyu.edu>
r'''
Evaluation
==========

.. autosummary::
    :toctree: generated/

    beat
    chord
    melody
    onset
    segment
    tempo
    pattern
'''

from collections import defaultdict

import six
import numpy as np
import mir_eval

from .exceptions import NamespaceError

__all__ = ['beat', 'chord', 'melody', 'onset', 'segment', 'tempo']


def validate_annotation(ann, namespace):
    '''Validate that the annotation has the correct namespace,
    and is well-formed.

    Parameters
    ----------
    ann : jams.Annotation
        The annotation object in question

    namespace : str
        The namespace pattern to match `ann` against

    Returns
    -------
    valid : bool
        True if `ann` passes validation

    Raises
    ------
    NamespaceError
        If `ann` does not match the proper namespace

    SchemaError
        If `ann` fails schema validation
    '''

    if not ann.search(namespace=namespace):
        raise NamespaceError('Expected namespace="{:s}", found "{:s}"'
                             .format(namespace, ann.namespace))

    ann.validate(strict=True)

    return True


def beat(ref, est, **kwargs):
    r'''Beat tracking evaluation

    Parameters
    ----------
    ref : jams.Annotation
        Reference annotation object
    est : jams.Annotation
        Estimated annotation object
    kwargs
        Additional keyword arguments

    Returns
    -------
    scores : dict
        Dictionary of scores, where the key is the metric name (str) and
        the value is the (float) score achieved.

    See Also
    --------
    mir_eval.beat.evaluate

    Examples
    --------
    >>> # Load in the JAMS objects
    >>> ref_jam = jams.load('reference.jams')
    >>> est_jam = jams.load('estimated.jams')
    >>> # Select the first relevant annotations
    >>> ref_ann = ref_jam.search(namespace='beat')[0]
    >>> est_ann = est_jam.search(namespace='beat')[0]
    >>> scores = jams.eval.beat(ref_ann, est_ann)
    '''

    namespace = 'beat'
    validate_annotation(ref, namespace)
    validate_annotation(est, namespace)
    ref_interval, _ = ref.data.to_interval_values()
    est_interval, _ = est.data.to_interval_values()

    return mir_eval.beat.evaluate(ref_interval[:, 0], est_interval[:, 0], **kwargs)


def onset(ref, est, **kwargs):
    r'''Onset evaluation

    Parameters
    ----------
    ref : jams.Annotation
        Reference annotation object
    est : jams.Annotation
        Estimated annotation object
    kwargs
        Additional keyword arguments

    Returns
    -------
    scores : dict
        Dictionary of scores, where the key is the metric name (str) and
        the value is the (float) score achieved.

    See Also
    --------
    mir_eval.onset.evaluate

    Examples
    --------
    >>> # Load in the JAMS objects
    >>> ref_jam = jams.load('reference.jams')
    >>> est_jam = jams.load('estimated.jams')
    >>> # Select the first relevant annotations
    >>> ref_ann = ref_jam.search(namespace='onset')[0]
    >>> est_ann = est_jam.search(namespace='onset')[0]
    >>> scores = jams.eval.onset(ref_ann, est_ann)
    '''
    namespace = 'onset'
    validate_annotation(ref, namespace)
    validate_annotation(est, namespace)
    ref_interval, _ = ref.data.to_interval_values()
    est_interval, _ = est.data.to_interval_values()

    return mir_eval.onset.evaluate(ref_interval[:, 0], est_interval[:, 0], **kwargs)


def chord(ref, est, **kwargs):
    r'''Chord evaluation

    Parameters
    ----------
    ref : jams.Annotation
        Reference annotation object
    est : jams.Annotation
        Estimated annotation object
    kwargs
        Additional keyword arguments

    Returns
    -------
    scores : dict
        Dictionary of scores, where the key is the metric name (str) and
        the value is the (float) score achieved.

    See Also
    --------
    mir_eval.chord.evaluate

    Examples
    --------
    >>> # Load in the JAMS objects
    >>> ref_jam = jams.load('reference.jams')
    >>> est_jam = jams.load('estimated.jams')
    >>> # Select the first relevant annotations
    >>> ref_ann = ref_jam.search(namespace='chord_harte')[0]
    >>> est_ann = est_jam.search(namespace='chord_harte')[0]
    >>> scores = jams.eval.chord(ref_ann, est_ann)
    '''

    namespace = 'chord_harte'
    validate_annotation(ref, namespace)
    validate_annotation(est, namespace)
    ref_interval, ref_value = ref.data.to_interval_values()
    est_interval, est_value = est.data.to_interval_values()

    return mir_eval.chord.evaluate(ref_interval, ref_value,
                                   est_interval, est_value, **kwargs)


def segment(ref, est, **kwargs):
    r'''Segment evaluation

    Parameters
    ----------
    ref : jams.Annotation
        Reference annotation object
    est : jams.Annotation
        Estimated annotation object
    kwargs
        Additional keyword arguments

    Returns
    -------
    scores : dict
        Dictionary of scores, where the key is the metric name (str) and
        the value is the (float) score achieved.

    See Also
    --------
    mir_eval.segment.evaluate

    Examples
    --------
    >>> # Load in the JAMS objects
    >>> ref_jam = jams.load('reference.jams')
    >>> est_jam = jams.load('estimated.jams')
    >>> # Select the first relevant annotations
    >>> ref_ann = ref_jam.search(namespace='segment_.*')[0]
    >>> est_ann = est_jam.search(namespace='segment_.*')[0]
    >>> scores = jams.eval.segment(ref_ann, est_ann)
    '''
    namespace = 'segment_.*'
    validate_annotation(ref, namespace)
    validate_annotation(est, namespace)
    ref_interval, ref_value = ref.data.to_interval_values()
    est_interval, est_value = est.data.to_interval_values()

    return mir_eval.segment.evaluate(ref_interval, ref_value,
                                     est_interval, est_value, **kwargs)


def tempo(ref, est, **kwargs):
    r'''Tempo evaluation

    Parameters
    ----------
    ref : jams.Annotation
        Reference annotation object
    est : jams.Annotation
        Estimated annotation object
    kwargs
        Additional keyword arguments

    Returns
    -------
    scores : dict
        Dictionary of scores, where the key is the metric name (str) and
        the value is the (float) score achieved.

    See Also
    --------
    mir_eval.tempo.evaluate

    Examples
    --------
    >>> # Load in the JAMS objects
    >>> ref_jam = jams.load('reference.jams')
    >>> est_jam = jams.load('estimated.jams')
    >>> # Select the first relevant annotations
    >>> ref_ann = ref_jam.search(namespace='tempo')[0]
    >>> est_ann = est_jam.search(namespace='tempo')[0]
    >>> scores = jams.eval.tempo(ref_ann, est_ann)
    '''

    validate_annotation(ref, 'tempo')
    validate_annotation(est, 'tempo')
    ref_tempi = ref.data['value'].values
    ref_weight = ref.data['confidence'][0]
    est_tempi = est.data['value'].values

    return mir_eval.tempo.evaluate(ref_tempi, ref_weight, est_tempi, **kwargs)

# melody
def melody(ref, est, **kwargs):
    r'''Melody extraction evaluation

    Parameters
    ----------
    ref : jams.Annotation
        Reference annotation object
    est : jams.Annotation
        Estimated annotation object
    kwargs
        Additional keyword arguments

    Returns
    -------
    scores : dict
        Dictionary of scores, where the key is the metric name (str) and
        the value is the (float) score achieved.

    See Also
    --------
    mir_eval.melody.evaluate

    Examples
    --------
    >>> # Load in the JAMS objects
    >>> ref_jam = jams.load('reference.jams')
    >>> est_jam = jams.load('estimated.jams')
    >>> # Select the first relevant annotations
    >>> ref_ann = ref_jam.search(namespace='pitch_hz')[0]
    >>> est_ann = est_jam.search(namespace='pitch_hz')[0]
    >>> scores = jams.eval.melody(ref_ann, est_ann)
    '''

    namespace = 'pitch_hz'
    validate_annotation(ref, namespace)
    validate_annotation(est, namespace)
    ref_interval, ref_freq = ref.data.to_interval_values()
    est_interval, est_freq = est.data.to_interval_values()

    return mir_eval.melody.evaluate(ref_interval[:, 0], np.asarray(ref_freq),
                                    est_interval[:, 0], np.asarray(est_freq),
                                    **kwargs)


# pattern detection
def pattern_to_mireval(ann):
    '''Convert a pattern_jku annotation object to mir_eval format.

    Parameters
    ----------
    ann : jams.Annotation
        Must have `namespace='pattern_jku'`

    Returns
    -------
    patterns : list of list of tuples
        - `patterns[x]` is a list containing all occurrences of pattern x

        - `patterns[x][y]` is a list containing all notes for
           occurrence y of pattern x

        - `patterns[x][y][z]` contains a time-note tuple
          `(time, midi note)`
    '''

    # It's easier to work with dictionaries, since we can't assume
    # sequential pattern or occurrence identifiers

    patterns = defaultdict(lambda: defaultdict(list))

    # Iterate over the data in interval-value format
    for interval, observation in zip(*ann.data.to_interval_values()):

        pattern_id = observation['pattern_id']
        occurrence_id = observation['occurrence_id']
        obs = (interval[0], observation['midi_pitch'])

        # Push this note observation into the correct pattern/occurrence
        patterns[pattern_id][occurrence_id].append(obs)

    # Convert to list-list-tuple format for mir_eval
    return [list(_.values()) for _ in six.itervalues(patterns)]


def pattern(ref, est, **kwargs):
    r'''Pattern detection evaluation

    Parameters
    ----------
    ref : jams.Annotation
        Reference annotation object
    est : jams.Annotation
        Estimated annotation object
    kwargs
        Additional keyword arguments

    Returns
    -------
    scores : dict
        Dictionary of scores, where the key is the metric name (str) and
        the value is the (float) score achieved.

    See Also
    --------
    mir_eval.pattern.evaluate

    Examples
    --------
    >>> # Load in the JAMS objects
    >>> ref_jam = jams.load('reference.jams')
    >>> est_jam = jams.load('estimated.jams')
    >>> # Select the first relevant annotations
    >>> ref_ann = ref_jam.search(namespace='pattern_jku')[0]
    >>> est_ann = est_jam.search(namespace='pattern_jku')[0]
    >>> scores = jams.eval.pattern(ref_ann, est_ann)
    '''

    namespace = 'pattern_jku'
    validate_annotation(ref, namespace)
    validate_annotation(est, namespace)

    ref_patterns = pattern_to_mireval(ref)
    est_patterns = pattern_to_mireval(est)

    return mir_eval.pattern.evaluate(ref_patterns, est_patterns, **kwargs)
