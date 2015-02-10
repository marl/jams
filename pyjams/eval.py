#!/usr/bin/env python
# CREATED:2015-02-04 16:39:00 by Brian McFee <brian.mcfee@nyu.edu>
'''mir_eval integration'''

from . import namespace as ns

import mir_eval

__all__ = ['beat', 'chord', 'melody', 'onset', 'segment', 'tempo']


def validate_annotation(ann, namespace):
    '''Validate that the annotation has the correct namespace,
    and is well-formed.

    Parameters
    ----------
    ann : pyjams.Annotation
        The annotation object in question

    namespace : str
        The namespace pattern to match `ann` against

    Returns
    -------
    valid : bool
        True if `ann` passes validation

    Raises
    ------
    RuntimeError
        If `ann` does not match the proper namespace

    jsonschema.ValidationError
        If `ann` fails schema validation
    '''

    if not ann.search(namespace=namespace):
        raise RuntimeError('Incorrect namespace in annotation. '
                           'Expected "{:s}", found "{:s}"'
                           .format(namespace, ann.namespace))

    ns.validate_annotation(ann, strict=True)

    return True


def __events(f, namespace):
    '''Wrapper function for event evaluation metrics.

    Parameters
    ----------
    f : callable
        The evaluator function

    namespace : str or callable
        The namespace against which to match annotation objects

    Returns
    -------
    f_wrapped : function
        `f` decorated to accept JAMS input
    '''

    def evaluator(ref, est, **kwargs):
    
        validate_annotation(ref, namespace)
        validate_annotation(est, namespace)
        ref_interval, ref_value = ref.data.to_interval_values()
        est_interval, est_value = est.data.to_interval_values()

        return f(ref_interval[:, 0], est_interval[:, 0], **kwargs)

    return evaluator


def __labeled_intervals(f, namespace):
    '''Wrapper function for labeled interval evaluation metrics.

    Parameters
    ----------
    f : callable
        The evaluator function

    namespace : str or callable
        The namespace against which to match annotation objects

    Returns
    -------
    f_wrapped : function
        `f` decorated to accept JAMS input
    '''

    def evaluator(ref, est, **kwargs):

        validate_annotation(ref, namespace)
        validate_annotation(est, namespace)
        ref_interval, ref_value = ref.data.to_interval_values()
        est_interval, est_value = est.data.to_interval_values()

        return f(ref_interval, ref_value, est_interval, est_value, **kwargs)

    return evaluator


def __tempo(f, namespace):
    '''Wrapper function for tempo evaluation metrics.

    Parameters
    ----------
    f : callable
        The evaluator function

    namespace : str or callable
        The namespace against which to match annotation objects

    Returns
    -------
    f_wrapped : function
        `f` decorated to accept JAMS input
    '''

    def evaluator(ref, est, **kwargs):
        validate_annotation(ref, namespace)
        validate_annotation(est, namespace)
        ref_tempi = ref.data.values
        ref_weight = ref.data.weight[0]
        est_tempi = est.data.values

        return f(ref_tempi, ref_weight, est_tempi, **kwargs)

    return evaluator


beat = __events(mir_eval.beat.evaluate,
                namespace='beat')

chord = __labeled_intervals(mir_eval.chord.evaluate,
                            namespace='chord_harte')

melody = __labeled_intervals(mir_eval.melody.evaluate,
                             namespace='melody_hz')

onset = __events(mir_eval.onset.evaluate,
                 namespace='onset')

segment = __labeled_intervals(mir_eval.segment.evaluate,
                              namespace='segment_.*')

tempo = __tempo(mir_eval.tempo.evaluate,
                namespace='tempo')

# TODO
#  pattern
#  separation
