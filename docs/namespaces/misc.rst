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

