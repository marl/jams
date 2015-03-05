#!/usr/bin/env python
# CHANGED:2015-03-05 17:53:32 by Brian McFee <brian.mcfee@nyu.edu>
"""Test the util module"""

import tempfile
from jams import util
import os
from nose.tools import eq_


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


