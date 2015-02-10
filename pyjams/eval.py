#!/usr/bin/env python
# CREATED:2015-02-04 16:39:00 by Brian McFee <brian.mcfee@nyu.edu>
'''mir_eval integration'''

from decorator import decorator
import mir_eval
from . import namespace as ns

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


def __events(namespace):
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

    def evaluator(f_eval, ref, est, **kwargs):
        '''The working decorator'''
        # TODO:   2015-02-10 10:00:27 by Brian McFee <brian.mcfee@nyu.edu>
        #   mangle the docstring here
        validate_annotation(ref, namespace)
        validate_annotation(est, namespace)
        ref_interval, _ = ref.data.to_interval_values()
        est_interval, _ = est.data.to_interval_values()

        return f_eval(ref_interval[:, 0], est_interval[:, 0], **kwargs)

    return decorator(evaluator)


def __labeled_intervals(namespace):
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

    def evaluator(f_eval, ref, est, **kwargs):
        '''The working decorator'''
        # TODO:   2015-02-10 10:00:27 by Brian McFee <brian.mcfee@nyu.edu>
        #   mangle the docstring here
        validate_annotation(ref, namespace)
        validate_annotation(est, namespace)
        ref_interval, ref_value = ref.data.to_interval_values()
        est_interval, est_value = est.data.to_interval_values()

        return f_eval(ref_interval, ref_value,
                      est_interval, est_value, **kwargs)

    return decorator(evaluator)


def __tempo(namespace):
    '''Wrapper function for tempo evaluation metrics.

    Parameters
    ----------
    namespace : str or callable
        The namespace against which to match annotation objects

    Returns
    -------
    f_wrapped : function
        `f` decorated to accept JAMS input
    '''

    def evaluator(f_eval, ref, est, **kwargs):
        '''The working decorator'''
        # TODO:   2015-02-10 10:00:27 by Brian McFee <brian.mcfee@nyu.edu>
        #   mangle the docstring here
        validate_annotation(ref, namespace)
        validate_annotation(est, namespace)
        ref_tempi = ref.data.values
        ref_weight = ref.data.weight[0]
        est_tempi = est.data.values

        return f_eval(ref_tempi, ref_weight, est_tempi, **kwargs)

    return decorator(evaluator)


beat = __events('beat')(mir_eval.beat.evaluate)

chord = __labeled_intervals('chord_harte')(mir_eval.chord.evaluate)

melody = __labeled_intervals('melody_hz')(mir_eval.melody.evaluate)

onset = __events('onset')(mir_eval.onset.evaluate)

segment = __labeled_intervals('segment_.*')(mir_eval.segment.evaluate)

tempo = __tempo('tempo')(mir_eval.tempo.evaluate)

# TODO
#  pattern
#  separation
