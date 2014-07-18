"""Utility functions for parsing datasets."""


def loadlab(filename, num_columns):
    """Load the columns of a labfile.

    Note: Any data that can be interpreted as integer / float values will be.

    Parameters
    ----------
    filename: str
        Path to a labfile.
    num_columns: int
        Number of data columns in the file.

    Returns
    -------
    columns: tuple
        Columns of data in the labfile.
    """
    columns = [list() for _ in range(num_columns)]
    with open(filename, 'r') as input_file:
        for row_idx, line in enumerate(input_file, 1):
            if line == '\n':
                continue
            # By default, split cuts at all whitespace.
            data = line.split()
            if len(data) != num_columns:
                raise ValueError(
                    "Expected %d columns, received %d at line %d." %
                    (num_columns, len(data), row_idx))
            for col_idx, col in enumerate(data):
                try:
                    if "." in col:
                        col = float(col)
                    else:
                        col = int(col)
                except ValueError:
                    pass
                columns[col_idx].append(col)

    return tuple(columns)


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
    data.confidence = confidences
