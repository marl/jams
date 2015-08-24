Lyrics
------

lyrics
~~~~~~
Time-aligned lyrical annotations.

    ===== ======== ====== ==========
    time  duration value  confidence
    ===== ======== ====== ==========
    [sec] [sec]    string --
    ===== ======== ====== ==========

The required ``value`` field can contain arbitrary text data, e.g., lyrics.

*Example*

    ===== ======== ======================== ==========
    time  duration value                    confidence
    ===== ======== ======================== ==========
    0.500 4.000    "Row row row your boat"  null
    4.500 2.000    "gently down the stream" null
    7.000 1.000    "merrily"                null
    8.000 1.000    "merrily"                null
    9.000 1.000    "merrily"                null
    10.00 1.000    "merrily"                null
    ===== ======== ======================== ==========

.. note::
    ``confidence`` is an unconstrained field, and may contain arbitrary data.

