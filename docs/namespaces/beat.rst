Beat
----

beat
~~~~
Beat event markers with optional metrical position.

    ===== ======== ================== ==========
    time  duration value              confidence
    ===== ======== ================== ==========
    [sec] [sec]    [number] or [null] --
    ===== ======== ================== ==========

Each observation corresponds to a single beat event.

The ``value`` field can be a number (positive or negative, integer or floating point),
indicating the metrical position within the bar of the observed beat.

If no metrical position is provided for the annotation, the ``value`` field will be
``null``.

*Example*

    ===== ======== ===== ==========
    time  duration value confidence
    ===== ======== ===== ==========
    0.500 0.000    1     null
    1.000 0.000    2     null
    1.500 0.000    3     null
    2.000 0.000    4     null
    2.500 0.000    1     null
    ===== ======== ===== ==========

.. note::
    ``duration`` is typically zero for beat events, but this is not enforced.

    ``confidence`` is an unconstrained field for beat annotations, and may contain
    arbitrary data.


beat_position
~~~~~~~~~~~~~
Beat events with time signature information.

    +-------+----------+--------------+------------+
    | time  | duration | value        | confidence |
    +=======+==========+==============+============+
    | [sec] | [sec]    | - position   | --         |
    |       |          | - measure    |            |
    |       |          | - num_beats  |            |
    |       |          | - beat_units |            |
    +-------+----------+--------------+------------+

Each observation corresponds to a single beat event.

The ``value`` field is a structure containing the following fields:

  - ``position`` : the position of the beat within the measure.  Can be any number greater
    than or equal to 1.
  - ``measure`` : the index of the measure containing this beat.  Can be any non-negative
    integer.
  - ``num_beats`` : the number of beats per measure : can be any strictly positive
    integer.
  - ``beat_units`` : the note value for beats in this measure.  Must be one of: 
    ``1, 2, 4, 8, 16, 32, 64, 128, 256``.

All fields are required for each observation.

*Example*

    +-------+----------+-----------------+------------+
    | time  | duration | value           | confidence |
    +=======+==========+=================+============+
    | 0.500 | 0.000    | - position: 1   | null       |
    |       |          | - measure: 0    |            |
    |       |          | - num_beats: 4  |            |
    |       |          | - beat_units: 4 |            |
    +-------+----------+-----------------+------------+
    | 1.000 | 0.000    | - position: 2   | null       |
    |       |          | - measure: 0    |            |
    |       |          | - num_beats: 4  |            |
    |       |          | - beat_units: 4 |            |
    +-------+----------+-----------------+------------+
    | 1.500 | 0.000    | - position: 3   | null       |
    |       |          | - measure: 0    |            |
    |       |          | - num_beats: 4  |            |
    |       |          | - beat_units: 4 |            |
    +-------+----------+-----------------+------------+
    | 2.000 | 0.000    | - position: 4   | null       |
    |       |          | - measure: 0    |            |
    |       |          | - num_beats: 4  |            |
    |       |          | - beat_units: 4 |            |
    +-------+----------+-----------------+------------+
    | 2.500 | 0.000    | - position: 1   | null       |
    |       |          | - measure: 1    |            |
    |       |          | - num_beats: 4  |            |
    |       |          | - beat_units: 4 |            |
    +-------+----------+-----------------+------------+

.. note::
    ``duration`` is typically zero for beat events, but this is not enforced.

    ``confidence`` is an unconstrained field for beat annotations, and may contain
    arbitrary data.

    ``position`` should lie in the range ``[1, beat_units]``, but the upper bound is not
    enforced at the schema level.
