#!/usr/bin/env python
# CHANGED:2015-03-05 17:53:32 by Brian McFee <brian.mcfee@nyu.edu>
"""Test the util module"""

import tempfile
import os
from nose.tools import eq_, raises
import numpy as np

from jams import pyjams, util


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

    # 2.5 seconds
    t = 2.5
    x = np.timedelta64(int(t * 1e9))
    tn = pyjams.timedelta_to_float(x)

    # convert back
    assert np.allclose(t, tn)


def test_query_pop():

    def __test(query, prefix, sep, target):
        eq_(pyjams.query_pop(query, prefix, sep=sep), target)

    yield __test, 'alpha.beta.gamma', 'alpha', '.', 'beta.gamma'
    yield __test, 'alpha/beta/gamma', 'alpha', '/', 'beta/gamma'
    yield __test, 'alpha.beta.gamma', 'beta', '.', 'alpha.beta.gamma'
    yield __test, 'alpha.beta.gamma', 'beta', '/', 'alpha.beta.gamma'
    yield __test, 'alpha.alpha.beta.gamma', 'alpha', '.', 'alpha.beta.gamma'


def test_match_query():

    def __test(needle, haystack, result):
        eq_(pyjams.match_query(haystack, needle), result)

    haystack = 'abcdeABCDE123'

    yield __test, haystack, haystack, True
    yield __test, '.*cde.*', haystack, True
    yield __test, 'cde$', haystack, False
    yield __test, r'.*\d+$', haystack, True
    yield __test, r'^\d+$', haystack, False

    yield __test, lambda x: True, haystack, True
    yield __test, lambda x: False, haystack, False

    yield raises(TypeError)(__test), None, haystack, False


def test_smkdirs():

    root = tempfile.mkdtemp()
    my_dirs = [root, 'level1', 'level2', 'level3']

    try:
        target = os.sep.join(my_dirs)
        util.smkdirs(target)

        for i in range(1, len(my_dirs)):
            tmpdir = os.sep.join(my_dirs[:i])
            assert os.path.exists(tmpdir)
            assert os.path.isdir(tmpdir)
    finally:
        for i in range(len(my_dirs), 0, -1):
            tmpdir = os.sep.join(my_dirs[:i])
            os.rmdir(tmpdir)


def test_filebase():

    def __test(query, target):

        eq_(util.filebase(query), target)

    yield __test, 'foo', 'foo'
    yield __test, 'foo.txt', 'foo'
    yield __test, '/path/to/foo.txt', 'foo'
    yield __test, '/path/to/foo', 'foo'
