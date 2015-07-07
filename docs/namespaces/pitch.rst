Pitch
-----

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
and a pitch class as an integer scale degree.  The ``confidence`` field is unconstrained.


*Example*

    +-------+----------+------------------+------------+
    | time  | duration | value            | confidence |
    +=======+==========+==================+============+
    | 0.000 | 30.0     | - tonic: ``C``   | null       |
    |       |          | - pitch class: 0 |            |
    +-------+----------+------------------+------------+
    | 0.000 | 30.0     | - tonic: ``C``   | null       |
    |       |          | - pitch class: 4 |            |
    +-------+----------+------------------+------------+
    | 0.000 | 30.0     | - tonic: ``C``   | null       |
    |       |          | - pitch class: 7 |            |
    +-------+----------+------------------+------------+
    | 30.00 | 35.0     | - tonic: ``G``   | null       |
    |       |          | - pitch class: 0 |            |
    +-------+----------+------------------+------------+


pitch_hz
~~~~~~~~

pitch_midi
~~~~~~~~~~
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

