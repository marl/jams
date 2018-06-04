Miscellaneous
-------------

Vector
~~~~~~

Numerical vector data.  This is useful for generic regression problems where the output is
a vector of numbers.

    ===== ======== ================== ==========
    time  duration value              confidence
    ===== ======== ================== ==========
    [sec] [sec]    [array of numbers]    --
    ===== ======== ================== ==========

Each observation value must be an array of at least one number.  Different observations
may have different length arrays, so it is up to the user to verify that arrays have the
desired length.


Blob
~~~~

Arbitrary data blobs.

    ===== ======== ===== ==========
    time  duration value confidence
    ===== ======== ===== ==========
    [sec] [sec]    --    --
    ===== ======== ===== ==========

This namespace can be used to encode arbitrary data.  The value and confidence fields have no schema
constraints, and may contain any structured (but serializable) data.  This can be useful for storing complex
output data that does not fit any particular task schema, such as regression targets or geolocation data.

It is strongly advised that the AnnotationMetadata for blobs be as explicit as possible.


Scaper
~~~~~~

Structured representation for soundscapes synthesized by the Scaper_ package.

    ===== ======== ================ ==========
    time  duration value            confidence
    ===== ======== ================ ==========
    [sec] [sec]    - label          --
                   - source_file
                   - source_time
                   - event_time
                   - event_duration
                   - snr
                   - time_stretch
                   - pitch_shift
                   - role
    ===== ======== ================ ==========

Each ``value`` field contains a dictionary with the following keys:

    * ``label``: a string indicating the label of the sound source
    * ``source_file``: a full path to the original sound source (on disk)
    * ``source_time``: a non-negative number indicating the time offset within ``source_file`` of the sound
    * ``event_time``: the start time of the event in the synthesized soundscape
    * ``event_duration``: a strictly positive number indicating the duration of the event
    * ``snr``: the signal-to-noise ratio (in LUFS) of the sound compared to the background
    * ``time_stetch``: (optional) a strictly positive number indicating the amount of time-stretch applied to
      the source
    * ``pitch_shift``: (optional) the amount of pitch-shift applied to the source
    * ``role``: one of ``background`` or ``foreground``

.. _Scaper: https://scaper.readthedocs.io/en/latest/
