Miscellaneous
-------------

Vector
~~~~~~

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

