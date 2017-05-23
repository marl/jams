#!/usr/bin/env python
# CHANGED:2015-03-05 17:53:32 by Brian McFee <brian.mcfee@nyu.edu>
"""Test the util module"""

import tempfile
import os
import pytest
import numpy as np

from jams import core, util


import six


def srand(seed=628318530):
    np.random.seed(seed)
    pass


@pytest.mark.parametrize('ns, lab, ints, y, infer_duration',
                         [('beat',
                           "1.0 1\n3.0 2",
                           np.array([[1.0, 3.0], [3.0, 3.0]]),
                           [1, 2],
                           True),
                          ('beat',
                           "1.0 1\n3.0 2",
                           np.array([[1.0, 1.0], [3.0, 3.0]]),
                           [1, 2],
                           False),
                          ('chord_harte',
                           "1.0 2.0 a\n2.0 4.0 b",
                           np.array([[1.0, 2.0], [2.0, 4.0]]),
                           ['a', 'b'],
                           True),
                          ('chord',
                           "1.0 1.0 c\n2.0 2.0 d",
                           np.array([[1.0, 2.0], [2.0, 4.0]]),
                           ['c', 'd'],
                           False)])
def test_import_lab(ns, lab, ints, y, infer_duration):
    ann = util.import_lab(ns, six.StringIO(lab),
                          infer_duration=infer_duration)

    assert len(ints) == len(ann.data)
    assert len(y) == len(ann.data)

    for yi, ival, obs in zip(y, ints, ann):
        assert obs.time == ival[0]
        assert obs.duration == ival[1] - ival[0]
        assert obs.value == yi


@pytest.mark.parametrize('query, prefix, sep, target',
                         [('al.beta.gamma', 'al', '.', 'beta.gamma'),
                          ('al/beta/gamma', 'al', '/', 'beta/gamma'),
                          ('al.beta.gamma', 'beta', '.', 'al.beta.gamma'),
                          ('al.beta.gamma', 'beta', '/', 'al.beta.gamma'),
                          ('al.pha.beta.gamma', 'al', '.', 'pha.beta.gamma')])
def test_query_pop(query, prefix, sep, target):
    assert target == core.query_pop(query, prefix, sep=sep)


@pytest.mark.parametrize('needle, haystack, result',
                         [('abcdeABCDE123', 'abcdeABCDE123', True),
                          ('.*cde.*', 'abcdeABCDE123', True),
                          ('cde$', 'abcdeABCDE123', False),
                          (r'.*\d+$', 'abcdeABCDE123', True),
                          (r'^\d+$', 'abcdeABCDE123', False),
                          (lambda x: True, 'abcdeABCDE123', True),
                          (lambda x: False, 'abcdeABCDE123', False),
                          (5, 5, True),
                          (5, 4, False)])
def test_match_query(needle, haystack, result):
    assert result == core.match_query(haystack, needle)


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


@pytest.mark.parametrize('query, target',
                         [('foo', 'foo'),
                          ('foo.txt', 'foo'),
                          ('/path/to/foo.txt', 'foo'),
                          ('/path/to/foo', 'foo')])
def test_filebase(query, target):
    assert target == util.filebase(query)


@pytest.fixture
def root_and_files():

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
        with open(fname, 'w'):
            pass

    yield root, files

    for fname, badfname in zip(files[::-1], badfiles[::-1]):
        os.remove(fname)
        os.remove(badfname)
        os.rmdir(os.path.dirname(fname))


@pytest.mark.parametrize('level', [1, 2, 3, 4])
@pytest.mark.parametrize('sort', [False, True])
def test_find_with_extension(root_and_files, level, sort):
    root, files = root_and_files
    results = util.find_with_extension(root, 'txt', depth=level, sort=sort)

    assert sorted(results) == sorted(files[:level])


def test_expand_filepaths():

    targets = ['foo.bar', 'dir/file.txt', 'dir2///file2.txt', '/q.bin']

    target_dir = '/tmp'

    paths = util.expand_filepaths(target_dir, targets)

    for search, result in zip(targets, paths):

        assert result == os.path.normpath(os.path.join(target_dir, search))
