Mood
----

mood_thayer
~~~~~~~~~~~

Time-varying emotion measurements as ordered pairs of ``(valence, arousal)``

    ===== ======== ================== ==========
    time  duration value              confidence
    ===== ======== ================== ==========
    [sec] [sec]    (valence, arousal) --
    ===== ======== ================== ==========

The ``value`` field is an ordered pair of numbers measuring the ``valence`` and
``arousal`` positions in the Thayer mood model [3]_.

.. [3] Thayer, Robert E. The biopsychology of mood and arousal.
       Oxford University Press, 1989.

*Example*

    ===== ======== =========== ==========
    time  duration value       confidence
    ===== ======== =========== ==========
    0.500 0.250    (-0.5, 1.0) null
    0.750 0.250    (-0.3, 0.6) null
    1.000 0.750    (-0.1, 0.1) null
    1.750 0.500    (0.3, -0.5) null
    ===== ======== =========== ==========


.. note::
    ``confidence`` is an unconstrained field, and may contain arbitrary data.
