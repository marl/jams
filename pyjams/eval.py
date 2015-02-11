#!/usr/bin/env python
# CREATED:2015-02-04 16:39:00 by Brian McFee <brian.mcfee@nyu.edu>
'''mir_eval integration'''

from decorator import decorator
import numpydoc
import mir_eval
from . import namespace as ns

__all__ = ['beat', 'chord', 'onset', 'segment', 'tempo']


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


def jamsify_docstring(function, function_name, namespace):
    '''Modify the docstring for an existing function.

    This changes the documented call signature, parameters,
    and example strings for the function in question.

    Parameters
    ----------
    function : callable
        The function from which to get the original docstring

    function_name : str
        The name of the new function

    namespace : str
        The namespace for the target annotation objects

    Returns
    -------
    docstring : str
        A numpydoc-style docstring, jamsified.
    '''
    F = numpydoc.docscrape.FunctionDoc(function)

    F['Parameters'] = [('reference_annotation',
                        'pyjams.Annotation',
                        ['Reference annotation object']),
                       ('estimated_annotation',
                        'pyjams.Annotation',
                        ['Estimated annotation object']),
                       ('kwargs',
                        '',
                        ['Additional keyword arguments'])]

    F['Signature'] = r''

    F['Examples'] = [r""">>> # Load in the JAMS objects""",
                     r""">>> ref_jam = pyjams.load('reference.jams')""",
                     r""">>> est_jam = pyjams.load('estimated.jams')""",
                     r""">>> # Select out the first relevant annotation from each jam""",
                     r""">>> ref_ann = ref_jam.search(namespace='{:s}')[0]""".format(namespace),
                     r""">>> est_ann = est_jam.search(namespace='{:s}')[0]""".format(namespace),
                     r""">>> scores = {:s}.{:s}(ref_ann, est_ann)""".format(__name__, function_name)]

    F['See Also'] = [(r"""{:s}.{:s}""".format(function.__module__,
                                              function.__name__),
                      '',
                      '')]

    return str(F)


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
        validate_annotation(ref, namespace)
        validate_annotation(est, namespace)
        ref_tempi = ref.data.values
        ref_weight = ref.data.weight[0]
        est_tempi = est.data.values

        return f_eval(ref_tempi, ref_weight, est_tempi, **kwargs)

    return decorator(evaluator)


beat = __events('beat')(mir_eval.beat.evaluate)
beat.__doc__ = jamsify_docstring(mir_eval.beat.evaluate, 'beat', 'beat')

chord = __labeled_intervals('chord_harte')(mir_eval.chord.evaluate)
chord.__doc__ = jamsify_docstring(mir_eval.chord.evaluate,
                                  'chord',
                                  'chord_harte')

onset = __events('onset')(mir_eval.onset.evaluate)
onset.__doc__ = jamsify_docstring(mir_eval.onset.evaluate,
                                  'onset',
                                  'onset')

segment = __labeled_intervals('segment_.*')(mir_eval.segment.evaluate)
segment.__doc__ = jamsify_docstring(mir_eval.segment.evaluate,
                                    'segment',
                                    'segment_.*')

tempo = __tempo('tempo')(mir_eval.tempo.evaluate)
tempo.__doc__ = jamsify_docstring(mir_eval.tempo.evaluate,
                                  'tempo',
                                  'tempo_.*')

# TODO
# melody = __labeled_intervals('melody_hz', 'melody')(mir_eval.melody.evaluate)
#  pattern
