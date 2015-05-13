#!/usr/bin/env python
# CHANGED:2015-03-05 17:53:32 by Brian McFee <brian.mcfee@nyu.edu>
"""Test the util module"""

import tempfile
import os
from nose.tools import eq_, raises
import numpy as np
import pandas as pd

from jams import pyjams, util

import six


def test_import_lab():

    labs = [r'''1.0 1
3.0 2''', r'''1.0 2.0 a
2.0 4.0 b''']

    intervals = [np.array([[1.0, 1.0], [3.0, 3.0]]),
                 np.array([[1.0, 2.0], [2.0, 4.0]])]

    labels = [[1, 2], ['a', 'b']]

    namespace = ['beat', 'chord_harte']

    def __test(ns, lab, ints, y):
        _, ann = util.import_lab(ns, six.StringIO(lab))

        assert np.allclose(pyjams.timedelta_to_float(ann.data['time'].values),
                           ints[:, 0])
        assert np.allclose(pyjams.timedelta_to_float(ann.data['duration'].values),
                           ints[:, 1] - ints[:, 0])
        for y1, y2 in zip(list(ann.data['value'].values), y):
            eq_(y1, y2)

    for ns, lab, ints, y in zip(namespace, labs, intervals, labels):
        yield __test, ns, lab, ints, y


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


def test_find_with_extension():
    root = tempfile.mkdtemp()

    files = [[root, 'file1.txt'],
             [root, 'sub1', 'file2.txt'],
             [root, 'sub1', 'sub2', 'file3.txt'],
             [root, 'sub1', 'sub2', 'sub3', 'file4.txt']]

    files = [os.sep.join(_) for _ in files]
    badfiles = [_.replace('.txt', '.csv') for _ in files]

    # Create all the necessary directories
    util.smkdirs(os.path.dirname(files[-1]))

    # Create the dummy files
    for fname in files + badfiles:
        with open(fname, 'w') as _:
            pass

    def __test(level, sort):
        results = util.find_with_extension(root, 'txt', depth=level, sort=sort)

        eq_(sorted(results), sorted(files[:level]))

    for level in [1, 2, 3, 4]:
        for sort in [False, True]:
            yield __test, level, sort

    # Cleanup
    for fname, badfname in zip(files, badfiles)[::-1]:
        os.remove(fname)
        os.remove(badfname)
        os.rmdir(os.path.dirname(fname))


def test_expand_filepaths():

    targets = ['foo.bar', 'dir/file.txt', 'dir2///file2.txt', '/q.bin']

    target_dir = '/tmp'

    paths = util.expand_filepaths(target_dir, targets)

    for search, result in zip(targets, paths):

        eq_(os.path.normpath(os.path.join(target_dir, search)), result)
