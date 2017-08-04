#!/usr/bin/env python
# CREATED:2015-02-04 16:39:00 by Brian McFee <brian.mcfee@nyu.edu>
r'''
Evaluation
----------

.. autosummary::
    :toctree: generated/

    beat
    chord
    melody
    onset
    segment
    tempo
    pattern
    hierarchy
    transcription
'''

from collections import defaultdict

import six
import numpy as np
import mir_eval

from .nsconvert import convert

__all__ = ['beat', 'chord', 'melody', 'onset',
           'segment', 'hierarchy', 'tempo',
           'pattern', 'transcription']


def coerce_annotation(ann, namespace):
    '''Validate that the annotation has the correct namespace,
    and is well-formed.

    If the annotation is not of the correct namespace, automatic conversion
    is attempted.

    Parameters
    ----------
    ann : jams.Annotation
        The annotation object in question

    namespace : str
        The namespace pattern to match `ann` against

    Returns
    -------
    ann_coerced: jams.Annotation
        The annotation coerced to the target namespace

    Raises
    ------
    NamespaceError
        If `ann` does not match the proper namespace

    SchemaError
        If `ann` fails schema validation

    See Also
    --------
    jams.nsconvert.convert
    '''

    ann = convert(ann, namespace)
    ann.validate(strict=True)

    return ann


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
    ref = coerce_annotation(ref, namespace)
    est = coerce_annotation(est, namespace)

    ref_times, _ = ref.to_event_values()
    est_times, _ = est.to_event_values()

    return mir_eval.beat.evaluate(ref_times, est_times, **kwargs)


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
    ref = coerce_annotation(ref, namespace)
    est = coerce_annotation(est, namespace)

    ref_times, _ = ref.to_event_values()
    est_times, _ = est.to_event_values()

    return mir_eval.onset.evaluate(ref_times, est_times, **kwargs)


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
    >>> ref_ann = ref_jam.search(namespace='chord')[0]
    >>> est_ann = est_jam.search(namespace='chord')[0]
    >>> scores = jams.eval.chord(ref_ann, est_ann)
    '''

    namespace = 'chord'
    ref = coerce_annotation(ref, namespace)
    est = coerce_annotation(est, namespace)
    ref_interval, ref_value = ref.to_interval_values()
    est_interval, est_value = est.to_interval_values()

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
    namespace = 'segment_open'
    ref = coerce_annotation(ref, namespace)
    est = coerce_annotation(est, namespace)
    ref_interval, ref_value = ref.to_interval_values()
    est_interval, est_value = est.to_interval_values()

    return mir_eval.segment.evaluate(ref_interval, ref_value,
                                     est_interval, est_value, **kwargs)


def hierarchy_flatten(annotation):
    '''Flatten a multi_segment annotation into mir_eval style.

    Parameters
    ----------
    annotation : jams.Annotation
        An annotation in the `multi_segment` namespace

    Returns
    -------
    hier_intervalss : list
        A list of lists of intervals, ordered by increasing specificity.

    hier_labels : list
        A list of lists of labels, ordered by increasing specificity.
    '''

    intervals, values = annotation.to_interval_values()

    ordering = dict()

    for interval, value in zip(intervals, values):
        level = value['level']
        if level not in ordering:
            ordering[level] = dict(intervals=list(), labels=list())

        ordering[level]['intervals'].append(interval)
        ordering[level]['labels'].append(value['label'])

    levels = sorted(list(ordering.keys()))
    hier_intervals = [ordering[level]['intervals'] for level in levels]
    hier_labels = [ordering[level]['labels'] for level in levels]

    return hier_intervals, hier_labels


def hierarchy(ref, est, **kwargs):
    r'''Multi-level segmentation evaluation

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
    mir_eval.hierarchy.evaluate

    Examples
    --------
    >>> # Load in the JAMS objects
    >>> ref_jam = jams.load('reference.jams')
    >>> est_jam = jams.load('estimated.jams')
    >>> # Select the first relevant annotations
    >>> ref_ann = ref_jam.search(namespace='multi_segment')[0]
    >>> est_ann = est_jam.search(namespace='multi_segment')[0]
    >>> scores = jams.eval.hierarchy(ref_ann, est_ann)
    '''
    namespace = 'multi_segment'
    ref = coerce_annotation(ref, namespace)
    est = coerce_annotation(est, namespace)
    ref_hier, ref_hier_lab = hierarchy_flatten(ref)
    est_hier, est_hier_lab = hierarchy_flatten(est)

    return mir_eval.hierarchy.evaluate(ref_hier, ref_hier_lab,
                                       est_hier, est_hier_lab,
                                       **kwargs)


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

    ref = coerce_annotation(ref, 'tempo')
    est = coerce_annotation(est, 'tempo')

    ref_tempi = np.asarray([o.value for o in ref])
    ref_weight = ref.data[0].confidence
    est_tempi = np.asarray([o.value for o in est])

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
    >>> ref_ann = ref_jam.search(namespace='pitch_contour')[0]
    >>> est_ann = est_jam.search(namespace='pitch_contour')[0]
    >>> scores = jams.eval.melody(ref_ann, est_ann)
    '''

    namespace = 'pitch_contour'
    ref = coerce_annotation(ref, namespace)
    est = coerce_annotation(est, namespace)

    ref_times, ref_p = ref.to_event_values()
    est_times, est_p = est.to_event_values()

    ref_freq = np.asarray([p['frequency'] * (-1)**(~p['voiced']) for p in ref_p])
    est_freq = np.asarray([p['frequency'] * (-1)**(~p['voiced']) for p in est_p])

    return mir_eval.melody.evaluate(ref_times, ref_freq,
                                    est_times, est_freq,
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

    for time, observation in zip(*ann.to_event_values()):

        pattern_id = observation['pattern_id']
        occurrence_id = observation['occurrence_id']
        obs = (time, observation['midi_pitch'])

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
    ref = coerce_annotation(ref, namespace)
    est = coerce_annotation(est, namespace)

    ref_patterns = pattern_to_mireval(ref)
    est_patterns = pattern_to_mireval(est)

    return mir_eval.pattern.evaluate(ref_patterns, est_patterns, **kwargs)


def transcription(ref, est, **kwargs):
    r'''Note transcription evaluation

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
    mir_eval.transcription.evaluate

    Examples
    --------
    >>> # Load in the JAMS objects
    >>> ref_jam = jams.load('reference.jams')
    >>> est_jam = jams.load('estimated.jams')
    >>> # Select the first relevant annotations. You can use any annotation
    >>> # type that can be converted to pitch_contour (such as pitch_midi)
    >>> ref_ann = ref_jam.search(namespace='pitch_contour')[0]
    >>> est_ann = est_jam.search(namespace='note_hz')[0]
    >>> scores = jams.eval.transcription(ref_ann, est_ann)
    '''

    namespace = 'pitch_contour'
    ref = coerce_annotation(ref, namespace)
    est = coerce_annotation(est, namespace)
    ref_intervals, ref_p = ref.to_interval_values()
    est_intervals, est_p = est.to_interval_values()

    ref_pitches = np.asarray([p['frequency'] * (-1)**(~p['voiced']) for p in ref_p])
    est_pitches = np.asarray([p['frequency'] * (-1)**(~p['voiced']) for p in est_p])

    return mir_eval.transcription.evaluate(
        ref_intervals, ref_pitches, est_intervals, est_pitches, **kwargs)
