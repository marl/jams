#!/usr/bin/env python
# CREATED:2015-02-04 16:39:00 by Brian McFee <brian.mcfee@nyu.edu>
'''mir_eval integration'''

import mir_eval


def __events(f):

    def evaluator(ref, est, **kwargs):
    
        ref_interval, ref_value = ref.data.to_interval_values()
        est_interval, est_value = est.data.to_interval_values()

        return f(ref_interval[:, 0], est_interval[:, 0], **kwargs)

    return evaluator


def __labeled_intervals(f):

    def evaluator(ref, est, **kwargs):

        ref_interval, ref_value = ref.data.to_interval_values()
        est_interval, est_value = est.data.to_interval_values()

        return f(ref_interval, ref_value, est_interval, est_value, **kwargs)

    return evaluator


def __tempo(f):

    def evaluator(ref, est, **kwargs):
        ref_tempi = ref.data.values
        ref_weight = ref.data.weight[0]
        est_tempi = est.data.values

        return f(ref_tempi, ref_weight, est_tempi, **kwargs)

    return evaluator


beat = __events(mir_eval.beat.evaluate)
chord = __labeled_intervals(mir_eval.chord.evaluate)
melody = __labeled_intervals(mir_eval.melody.evaluate)
onset = __events(mir_eval.onset.evaluate)
segment = __labeled_intervals(mir_eval.segment.evaluate)
tempo = __tempo(mir_eval.tempo.evaluate)

# TODO
#  pattern
#  separation
