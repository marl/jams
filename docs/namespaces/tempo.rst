Tempo
-----

tempo
~~~~~
Tempo measurements in beats per minute (BPM).

    ===== ======== ====== ==========
    time  duration value  confidence
    ===== ======== ====== ==========
    [sec] [sec]    number number          
    ===== ======== ====== ==========

The ``value`` field is a non-negative number (floating point), indicated the tempo measurement.
The ``confidence`` field is a number in the range ``[0, 1]``, following the format used by MIREX [5]_.

.. [5] http://www.music-ir.org/mirex/wiki/2014:Audio_Tempo_Estimation

*Example*

    ===== ======== ====== ==========
    time  duration value  confidence
    ===== ======== ====== ==========
    0.00  60.00    180.0  0.8
    0.00  60.00    90.0   0.2
    ===== ======== ====== ==========


.. note::
    MIREX requires that tempo measurements come in pairs, and that the confidence values sum to 1.
    This is not enforced at the schema level.

