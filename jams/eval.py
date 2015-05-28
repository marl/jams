#!/usr/bin/env python
# CREATED:2015-02-04 16:39:00 by Brian McFee <brian.mcfee@nyu.edu>
r'''
Evaluation
==========

.. autosummary::
    :toctree: generated/

..    beat
..    chord
..    onset
..    segment
..    tempo
'''

from decorator import decorator
import numpydoc
import mir_eval

from .exceptions import *

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
                     r""">>> # Select the first relevant annotations""",
                     r""">>> ref_ann = ref_jam.search(namespace='{:s}')[0]""".format(namespace),
                     r""">>> est_ann = est_jam.search(namespace='{:s}')[0]""".format(namespace),
                     r""">>> scores = {:s}.{:s}(ref_ann, est_ann)""".format(__name__, function_name)]

    F['See Also'] = [(r"""{:s}.{:s}""".format(function.__module__,
                                              function.__name__),
                      '',
                      '')]

    return str(F)


def beat(ref, est, **kwargs):
    '''dynamically generated docstring'''

    namespace = 'beat'
    validate_annotation(ref, namespace)
    validate_annotation(est, namespace)
    ref_interval, _ = ref.data.to_interval_values()
    est_interval, _ = est.data.to_interval_values()

    return mir_eval.beat.evaluate(ref_interval[:, 0], est_interval[:, 0], **kwargs)
beat.__doc__ = jamsify_docstring(mir_eval.beat.evaluate, 'beat', 'beat')


def onset(ref, est, **kwargs):
    '''dynamically generated docstring'''
    namespace = 'onset'
    validate_annotation(ref, namespace)
    validate_annotation(est, namespace)
    ref_interval, _ = ref.data.to_interval_values()
    est_interval, _ = est.data.to_interval_values()

    return mir_eval.onset.evaluate(ref_interval[:, 0], est_interval[:, 0], **kwargs)
onset.__doc__ = jamsify_docstring(mir_eval.onset.evaluate, 'onset', 'onset')


def chord(ref, est, **kwargs):
    '''dynamically generated docstring'''

    namespace = 'chord_harte'
    validate_annotation(ref, namespace)
    validate_annotation(est, namespace)
    ref_interval, ref_value = ref.data.to_interval_values()
    est_interval, est_value = est.data.to_interval_values()

    return mir_eval.chord.evaluate(ref_interval, ref_value,
                                   est_interval, est_value, **kwargs)
chord.__doc__ = jamsify_docstring(mir_eval.chord.evaluate, 'chord', 'chord_harte')


def segment(ref, est, **kwargs):
    '''dynamically generated docstring'''
    namespace = 'segment_.*'
    validate_annotation(ref, namespace)
    validate_annotation(est, namespace)
    ref_interval, ref_value = ref.data.to_interval_values()
    est_interval, est_value = est.data.to_interval_values()

    return mir_eval.segment.evaluate(ref_interval, ref_value,
                                     est_interval, est_value, **kwargs)
segment.__doc__ = jamsify_docstring(mir_eval.segment.evaluate, 'segment', 'segment_.*')


def tempo(ref, est, **kwargs):
    '''dynamically generated docstring'''
    validate_annotation(ref, 'tempo')
    validate_annotation(est, 'tempo')
    ref_tempi = ref.data.values
    ref_weight = ref.data.confidence[0]
    est_tempi = est.data.values

    return mir_eval.tempo.evaluate(ref_tempi, ref_weight, est_tempi, **kwargs)
tempo.__doc__ = jamsify_docstring(mir_eval.tempo.evaluate, 'tempo', 'tempo')

# TODO
# melody
# pattern
