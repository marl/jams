#!/usr/bin/env python
# -*- encoding: utf-8 -*-
r"""
Utility functions
-----------------

.. autosummary::
    :toctree: generated/

    expand_filepaths
    smkdirs
    filebase
    find_with_extension
"""

import os
import glob
import pandas as pd


def expand_filepaths(base_dir, rel_paths):
    """Expand a list of relative paths to a give base directory.

    Parameters
    ----------
    base_dir : str
        The target base directory

    rel_paths : list (or list-like)
        Collection of relative path strings

    Returns
    -------
    expanded_paths : list
        `rel_paths` rooted at `base_dir`

    Examples
    --------
    >>> jams.util.expand_filepaths('/data', ['audio', 'beat', 'seglab'])
    ['/data/audio', '/data/beat', '/data/seglab']

    """
    return [os.path.join(base_dir, os.path.normpath(rp)) for rp in rel_paths]


def smkdirs(dpath, mode=0o777):
    """Safely make a full directory path if it doesn't exist.

    Parameters
    ----------
    dpath : str
        Path of directory/directories to create

    mode : int [default=0777]
        Permissions for the new directories

    See also
    --------
    os.makedirs
    """
    if not os.path.exists(dpath):
        os.makedirs(dpath, mode=mode)


def filebase(filepath):
    """Return the extension-less basename of a file path.

    Parameters
    ----------
    filepath : str
        Path to a file

    Returns
    -------
    base : str
        The name of the file, with directory and extension removed

    Examples
    --------
    >>> jams.util.filebase('my_song.mp3')
    'my_song'

    """
    return os.path.splitext(os.path.basename(filepath))[0]


def find_with_extension(in_dir, ext, depth=3, sort=True):
    """Naive depth-search into a directory for files with a given extension.

    Parameters
    ----------
    in_dir : str
        Path to search.
    ext : str
        File extension to match.
    depth : int
        Depth of directories to search.
    sort : bool
        Sort the list alphabetically

    Returns
    -------
    matched : list
        Collection of matching file paths.

    Examples
    --------
    >>> jams.util.find_with_extension('Audio', 'wav')
    ['Audio/LizNelson_Rainfall/LizNelson_Rainfall_MIX.wav',
     'Audio/LizNelson_Rainfall/LizNelson_Rainfall_RAW/LizNelson_Rainfall_RAW_01_01.wav',
     'Audio/LizNelson_Rainfall/LizNelson_Rainfall_RAW/LizNelson_Rainfall_RAW_02_01.wav',
     ...
     'Audio/Phoenix_ScotchMorris/Phoenix_ScotchMorris_STEMS/Phoenix_ScotchMorris_STEM_02.wav',
     'Audio/Phoenix_ScotchMorris/Phoenix_ScotchMorris_STEMS/Phoenix_ScotchMorris_STEM_03.wav',
    'Audio/Phoenix_ScotchMorris/Phoenix_ScotchMorris_STEMS/Phoenix_ScotchMorris_STEM_04.wav']

    """
    assert depth >= 1
    ext = ext.strip(os.extsep)
    match = list()
    for n in range(1, depth+1):
        wildcard = os.path.sep.join(["*"]*n)
        search_path = os.path.join(in_dir, os.extsep.join([wildcard, ext]))
        match += glob.glob(search_path)

    if sort:
        match.sort()
    return match
