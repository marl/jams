#!/usr/bin/env python
# CHANGED:2015-03-05 17:53:32 by Brian McFee <brian.mcfee@nyu.edu>
"""Test the util module"""

import tempfile
import os
from nose.tools import eq_
import numpy as np

from jams import util


def test_read_lab():
    fid, fpath = tempfile.mkstemp(suffix='.lab')

    lab_data = [[0, 1.5, 'a\tblah blah'],
                [],
                ['# I am a comment'],
                ['b', -2, -5.5]]

    text = ["\t".join(["%s" % _ for _ in row]) + "\n" for row in lab_data]

    fhandle = os.fdopen(fid, 'w')
    fhandle.writelines(text)
    fhandle.close()

    result = util.read_lab(fpath, 3, delimiter='\t', comment='#')

    eq_(result[0], [0, 'b'])
    eq_(result[1], [1.5, -2])
    eq_(result[2], ['a\tblah blah', -5.5])

    result = util.read_lab(fpath, 4, delimiter='\t', comment='#')
    # FIXME:  2015-03-05 17:52:48 by Brian McFee <brian.mcfee@nyu.edu>
    # this file only gets nuked if the first test passes
    # this test should be refactored into two tests

    os.remove(fpath)

    eq_(result[0], [0, 'b'])
    eq_(result[1], [1.5, -2])
    eq_(result[2], ['a', -5.5])
    eq_(result[3], ['blah blah', ''])


def test_timedelta_to_float():

    # 30 seconds
    t = 30.0

    # in nanoseconds
    x = np.timedelta64(int(t * 1e9))

    # convert back
    tn = util.timedelta_to_float(x)

    assert np.allclose(t, tn)


def test_query_pop():

    def __test(query, prefix, sep, target):
        eq_(util.query_pop(query, prefix, sep=sep), target)

    yield __test, 'alpha.beta.gamma', 'alpha', '.', 'beta.gamma'
    yield __test, 'alpha/beta/gamma', 'alpha', '/', 'beta/gamma'
    yield __test, 'alpha.beta.gamma', 'beta', '.', 'alpha.beta.gamma'
    yield __test, 'alpha.beta.gamma', 'beta', '/', 'alpha.beta.gamma'
    yield __test, 'alpha.alpha.beta.gamma', 'alpha', '.', 'alpha.beta.gamma'
