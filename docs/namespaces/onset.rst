Onset
-----

onset
~~~~~
Note onset event markers.

    ===== ======== ===== ==========
    time  duration value confidence
    ===== ======== ===== ==========
    [sec] [sec]    --    --
    ===== ======== ===== ==========

This namespace can be used to encode timing of arbitrary instantaneous events.
Most commonly, this is applied to note onsets.

*Example*

    ===== ======== ===== ==========
    time  duration value confidence
    ===== ======== ===== ==========
    0.500 0.000    null  null
    1.000 0.000    null  null
    1.500 0.000    null  null
    2.000 0.000    null  null
    ===== ======== ===== ==========

.. note::
    ``duration`` is typically zero for instantaneous events, but this is not enforced.

    ``value`` and ``confidence`` fields are unconstrained, and may contain arbitrary data.
