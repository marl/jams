Pitch
-----

pitch_contour
~~~~~~~~~~~~~
Pitch contours in the format ``(index, frequency, voicing)``.

    +-------+----------+---------------+------------+
    | time  | duration | value         | confidence |
    +=======+==========+===============+============+
    | [sec] | [--]     | - index       | --         |
    |       |          | - frequency   |            |
    |       |          | - voiced      |            |
    +-------+----------+---------------+------------+

Each ``value`` field is a structure containing a contour ``index`` (an integer indicating which contour the observation belongs to), a ``frequency`` value in Hz, and a boolean indicating if the values is ``voiced``. The ``confidence`` field is unconstrained.


*Example*

    +--------+----------+--------------------+------------+
    | time   | duration | value              | confidence |
    +========+==========+====================+============+
    | 0.0000 | 0.0000   | - index: 0         | null       |
    |        |          | - frequency: 442.1 |            |
    |        |          | - voiced: True     |            |
    +--------+----------+--------------------+------------+
    | 0.0058 | 0.0000   | - index: 0         | null       |
    |        |          | - frequency: 457.8 |            |
    |        |          | - voiced: False    |            |
    +--------+----------+--------------------+------------+
    | 2.5490 | 0.0000   | - index: 1         | null       |
    |        |          | - frequency: 89.4  |            |
    |        |          | - voiced: True     |            |
    +--------+----------+--------------------+------------+
    | 2.5548 | 0.0000   | - index: 1         | null       |
    |        |          | - frequency: 90.0  |            |
    |        |          | - voiced: True     |            |
    +--------+----------+--------------------+------------+


note_hz
~~~~~~~
Note events with (non-negative) frequencies measured in Hz.

    +-------+----------+---------------+------------+
    | time  | duration | value         | confidence |
    +=======+==========+===============+============+
    | [sec] | [sec]    | - number      | --         |
    +-------+----------+---------------+------------+

Each ``value`` field gives the frequency of the note in Hz.

*Example*

    +-------+----------+---------------+------------+
    | time  | duration | value         | confidence |
    +=======+==========+===============+============+
    | 12.34 | 0.287    | 189.9         | null       |
    +-------+----------+---------------+------------+
    | 2.896 | 3.000    | 74.0          | null       |
    +-------+----------+---------------+------------+
    | 10.12 | 0.5.     | 440.0         | null       |
    +-------+----------+---------------+------------+


note_midi
~~~~~~~~~
Note events with pitches measured in (fractional) MIDI note numbers.

    +-------+----------+---------------+------------+
    | time  | duration | value         | confidence |
    +=======+==========+===============+============+
    | [sec] | [sec]    | - number      | --         |
    +-------+----------+---------------+------------+

Each ``value`` field gives the pitch of the note in MIDI note numbers.

*Example*

    +-------+----------+---------------+------------+
    | time  | duration | value         | confidence |
    +=======+==========+===============+============+
    | 12.34 | 0.287    | 52.0          | null       |
    +-------+----------+---------------+------------+
    | 2.896 | 3.000    | 20.7          | null       |
    +-------+----------+---------------+------------+
    | 10.12 | 0.5.     | 42.0          | null       |
    +-------+----------+---------------+------------+


pitch_class
~~~~~~~~~~~
Pitch measurements in ``(tonic, pitch class)`` format.

    +-------+----------+---------------+------------+
    | time  | duration | value         | confidence |
    +=======+==========+===============+============+
    | [sec] | [sec]    | - tonic       | --         |
    |       |          | - pitch class |            |
    +-------+----------+---------------+------------+

Each ``value`` field is a structure containing a ``tonic`` (note string, e.g., ``"A#"`` or
``"D"``)
and a pitch class ``pitch`` as an integer scale degree.  The ``confidence`` field is unconstrained.


*Example*

    +-------+----------+------------------+------------+
    | time  | duration | value            | confidence |
    +=======+==========+==================+============+
    | 0.000 | 30.0     | - tonic: ``C``   | null       |
    |       |          | - pitch: 0       |            |
    +-------+----------+------------------+------------+
    | 0.000 | 30.0     | - tonic: ``C``   | null       |
    |       |          | - pitch: 4       |            |
    +-------+----------+------------------+------------+
    | 0.000 | 30.0     | - tonic: ``C``   | null       |
    |       |          | - pitch: 7       |            |
    +-------+----------+------------------+------------+
    | 30.00 | 35.0     | - tonic: ``G``   | null       |
    |       |          | - pitch: 0       |            |
    +-------+----------+------------------+------------+


pitch_hz
~~~~~~~~
.. warning:: Deprecated, use ``pitch_contour``.

Pitch measurements in Hertz (Hz). Pitch (a subjective sensation) is represented
as fundamental frequency (a physical quantity), a.k.a. "f0".

    +-------+----------+---------------+------------+
    | time  | duration | value         | confidence |
    +=======+==========+===============+============+
    | [sec] | --       | - number      | --         |
    +-------+----------+---------------+------------+

The ``time`` field represents the instantaneous time in which the pitch f0 was
estimated. By convention, this (usually) represents the center time of the
analysis frame. Note that this is different from pitch_midi and pitch_class,
where ``time`` represents the onset time. As a consequence, the ``duration``
field is undefined and should be ignored. The ``value`` field is a number
representing the f0 in Hz. By convention, values that are equal to or less than
zero are used to represent silence (no pitch). Some algorithms (e.g. melody
extraction algorithms that adhere to the MIREX convention) use negative f0
values to represent the algorithm's pitch estimate for frames where it thinks
there is no active pitch (e.g. no melody), to allow the independent evaluation
of pitch activation detection (a.k.a. "voicing detection") and pitch frequency
estimation. The ``confidence`` field is unconstrained.

*Example*

    +-------+----------+---------------+------------+
    | time  | duration | value         | confidence |
    +=======+==========+===============+============+
    | 0.000 | 0.000    | 300.00        | null       |
    +-------+----------+---------------+------------+
    | 0.010 | 0.000    | 305.00        | null       |
    +-------+----------+---------------+------------+
    | 0.020 | 0.000    | 310.00        | null       |
    +-------+----------+---------------+------------+
    | 0.030 | 0.000    | 0.00          | null       |
    +-------+----------+---------------+------------+
    | 0.040 | 0.000    | -280.00       | null       |
    +-------+----------+---------------+------------+
    | 0.050 | 0.000    | -290.00       | null       |
    +-------+----------+---------------+------------+


pitch_midi
~~~~~~~~~~
.. warning:: Deprecated, use ``note_midi`` or ``pitch_contour``.

Pitch measurements in (fractional) MIDI note number notation.

    ===== ======== ====== ==========
    time  duration value  confidence
    ===== ======== ====== ==========
    [sec] [sec]    number  --
    ===== ======== ====== ==========

The ``value`` field is a number representing the pitch in MIDI notation.
Numbers can be negative (for notes below ``C-1``) or fractional.

*Example*

    ===== ======== ===== ==========
    time  duration value confidence
    ===== ======== ===== ==========
    0.000 30.000   24    null
    0.000 30.000   43.02 null
    15.00 45.000   26    null
    ===== ======== ===== ==========

