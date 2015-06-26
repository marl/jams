Key
---

key_mode
~~~~~~~~
Key and optional mode (major/minor or Greek modes)

    ===== ======== ====== ==========
    time  duration value  confidence
    ===== ======== ====== ==========
    [sec] [sec]    string --
    ===== ======== ====== ==========

The ``value`` field is a string matching one of the three following patterns:

    * ``N`` : no key
    * ``Ab, A, A#, Bb, ... G#`` : tonic note, upper case
    * ``tonic:MODE`` where ``tonic`` is as described above, and ``MODE`` is one of: ``major, minor, ionian, dorian,
      phrygian, lydian, mixolydian, aeolian, locrian``.

*Example*

    ===== ======== ========= ==========
    time  duration value     confidence
    ===== ======== ========= ==========
    0.000 30.0     C:minor   null
    30.0  5.00     N         null
    35.0  15.0     C#:dorian null
    50.0  10.0     Eb        null
    60.0  10.0     A:lydian  null
    ===== ======== ========= ==========


.. note::

    ``confidence`` is an unconstrained field, and may contain arbitrary data.
    
