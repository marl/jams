#!/usr/bin/env python

import sys
import jams

from pprint import pprint

def compare_beats(f_ref, f_est):

    # f_ref contains the reference annotations
    j_ref = jams.load(f_ref)

    # f_est contains the estimated annotations
    j_est = jams.load(f_est)

    # Get the first reference beats
    beat_ref = j_ref.search(namespace='beat')[0]
    beat_est = j_est.search(namespace='beat')[0]

    # Get the scores
    return jams.eval.beat(beat_ref, beat_est)


if __name__ == '__main__':

    f_ref, f_est = sys.argv[1:]
    scores = compare_beats(f_ref, f_est)

    # Print them out
    pprint(dict(scores))

