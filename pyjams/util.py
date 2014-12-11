"""Utility functions for parsing datasets."""

import os
import glob
import pandas as pd
import numpy as np


def frame_to_dict(data, **kwargs):
    '''Custom semi-serializer for dataframe objects, allowing
    decoding into primitive javascript types.

    See also: serialize_obj()
    '''

    def __recursive_simplify(D):
        '''A simplifier for nested dictionary structures'''

        if isinstance(D, list):
            return [__recursive_simplify(Di) for Di in D]

        dict_out = {}
        for key, value in D.iteritems():
            if isinstance(value, dict):
                dict_out[key] = __recursive_simplify(value)
            else:
                dict_out[key] = serialize_obj(value)
        return dict_out

    return __recursive_simplify(data.to_dict(**kwargs))


def serialize_obj(obj):
    '''
    Custom serialization functionality for working with advanced data types.

    - Timedelta objects are convered to floats (in seconds)
    - numpy arrays are converted to lists

    '''
    if isinstance(obj, pd.tslib.Timedelta):
        return obj.total_seconds()

    elif isinstance(obj, np.ndarray):
        return obj.tolist()

    return obj


def read_lab(filename, num_columns, delimiter=None, comment='#', header=False):
    """Read the rows of a labfile into memory.

    An effort is made to infer datatypes, and therefore numerical values will
    be mapped to ints / floats accordingly.

    Note: Any row with fewer than `num_columns` values will be back-filled
    with empty strings.

    Parameters
    ----------
    filename : str
        Path to a labfile.
    num_columns : int
        Number of columns in lab file.
    delimiter : str
        lab file delimiter
    comment : str
        lab file comment character
    header : bool
        if true, the first line will be skipped

    Returns
    -------
    columns : list of lists
        Columns of data in the labfile.
    """
    data = [list() for _ in range(num_columns)]
    first_row = True
    with open(filename, 'r') as input_file:
        for row_idx, line in enumerate(input_file, 1):
            if line.strip() == '':
                continue
            if line.startswith(comment):
                continue
            values = line.strip().split(delimiter, num_columns - 1)
            while len(values) < num_columns:
                values.append('')
            if header and first_row:
                first_row = False
                continue
            for idx, value in enumerate(values):
                try:
                    if "." in value:
                        value = float(value)
                    else:
                        value = int(value)
                except ValueError:
                    pass
                data[idx].append(value)

    return data


def load_textlist(filename):
    """Return a list of lines in a text file."""
    with open(filename, 'r') as fp:
        return [line.strip("\n") for line in fp]


def expand_filepaths(base_dir, rel_paths):
    """Expand a list of relative paths to a give base directory."""
    return [os.path.join(base_dir, rp.strip("./")) for rp in rel_paths]


def smkdirs(dpath):
    """Safely make a directory path if it doesn't exist."""
    if not os.path.exists(dpath):
        os.makedirs(dpath)


def filebase(filepath):
    """Return the extension-less basename of a file path."""
    return os.path.splitext(os.path.basename(filepath))[0]


def find_with_extension(in_dir, ext, depth=3):
    """Naive depth-search into a directory for files with a given extension.

    Parameters
    ----------
    in_dir : str
        Path to search.
    ext : str
        File extension to match.
    depth : int
        Depth of directories to search.

    Returns
    -------
    matched : list
        Collection of matching file paths.
    """
    assert depth >= 1
    ext = ext.strip('.')
    match = list()
    for n in range(1, depth+1):
        wildcard = "/".join(["*"]*n)
        search_path = os.path.join(in_dir, "%s.%s" % (wildcard, ext))
        match += glob.glob(search_path)

    return match


def fill_observation_annotation_data(values, confidences, secondary_values,
                                     observation_annotation):
    """Add a collection of data to an event annotation (in-place).

    Parameters
    ----------
    value: list of values
        Obervation values.
    confidence: list
        The corresponding confidence values for each event.
    secondary_value: list of values
        Secondary observation values.
    observation_annotation: ObservationAnnotation
        An instantiated observation annotation to populate.
    """
    for v, c, sv in zip(values, confidences, secondary_values):
        data = observation_annotation.create_datapoint()
        data.value = v
        data.confidence = c
        data.secondary_value = sv


def fill_event_annotation_data(times, labels, event_annotation):
    """Add a collection of data to an event annotation (in-place).

    Parameters
    ----------
    times: list of scalars
        Event times in seconds.
    labels: list
        The corresponding labels for each event.
    event_annotation: EventAnnotation
        An instantiated event annotation to populate.
    """
    for t, l in zip(times, labels):
        data = event_annotation.create_datapoint()
        data.time.value = t
        data.label.value = l


def fill_range_annotation_data(start_times, end_times, labels,
                               range_annotation):
    """Add a collection of data to a range annotation (in-place).

    Parameters
    ----------
    start_times: list of scalars
        Start times of each range, in seconds.
    end_times: list of scalars
        End times of each range, in seconds.
    labels: list
        The corresponding labels for each range.
    range_annotation: RangeAnnotation
        An instantiated range annotation to populate.
    """
    for t0, t1, l in zip(start_times, end_times, labels):
        data = range_annotation.create_datapoint()
        data.start.value = t0
        data.end.value = t1
        data.label.value = l


def fill_timeseries_annotation_data(times, values, confidences,
                                    timeseries_annotation):
    """Add a collection of data to a time-series annotation (in-place).

    Parameters
    ----------
    times: list of scalars
        Time points in seconds.
    values: list
        The corresponding values for each time point.
    confidences: list
        The corresponding confidence for each time point.
    timeseries_annotation: TimeSeriesAnnotation
        An instantiated event annotation to populate.
    """
    data = timeseries_annotation.create_datapoint()
    data.value = values
    data.time = times
    if confidences is not None:
        data.confidence = confidences
