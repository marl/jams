#!/usr/bin/env python
# -*- encoding: utf-8 -*-
r"""
Utility functions
-----------------

.. autosummary::
    :toctree: generated/

    import_lab
    expand_filepaths
    smkdirs
    filebase
    find_with_extension
"""

import os
import glob
import pandas as pd

from . import core


def import_lab(namespace, filename, infer_duration=True, **parse_options):
    r'''Load a .lab file as an Annotation object.

    .lab files are assumed to have the following format:

        ``TIME_START\tTIME_END\tANNOTATION``

    By default, .lab files are assumed to have columns separated by one
    or more white-space characters, and have no header or index column
    information.

    If the .lab file contains only two columns, then an empty duration
    field is inferred.

    If the .lab file contains more than three columns, each row's
    annotation value is assigned the contents of last non-empty column.


    Parameters
    ----------
    namespace : str
        The namespace for the new annotation

    filename : str
        Path to the .lab file

    infer_duration : bool
        If `True`, interval durations are inferred from `(start, end)` columns,
        or difference between successive times.

        If `False`, interval durations are assumed to be explicitly coded as
        `(start, duration)` columns.  If only one time column is given, then
        durations are set to 0.

        For instantaneous event annotations (e.g., beats or onsets), this
        should be set to `False`.

    parse_options : additional keyword arguments
        Passed to ``pandas.DataFrame.read_csv``

    Returns
    -------
    annotation : Annotation
        The newly constructed annotation object

    See Also
    --------
    pandas.DataFrame.read_csv
    '''

    # Create a new annotation object
    annotation = core.Annotation(namespace)

    parse_options.setdefault('sep', r'\s+')
    parse_options.setdefault('engine', 'python')
    parse_options.setdefault('header', None)
    parse_options.setdefault('index_col', False)

    # This is a hack to handle potentially ragged .lab data
    parse_options.setdefault('names', range(20))

    data = pd.read_csv(filename, **parse_options)

    # Drop all-nan columns
    data = data.dropna(how='all', axis=1)

    # Do we need to add a duration column?
    # This only applies to event annotations
    if len(data.columns) == 2:
        # Insert a column of zeros after the timing
        data.insert(1, 'duration', 0)
        if infer_duration:
            data['duration'][:-1] = data.loc[:, 0].diff()[1:].values

    else:
        # Convert from time to duration
        if infer_duration:
            data.loc[:, 1] -= data[0]

    for row in data.itertuples():
        time, duration = row[1:3]

        value = [x for x in row[3:] if x is not None][-1]

        annotation.append(time=time,
                          duration=duration,
                          confidence=1.0,
                          value=value)

    return annotation


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
