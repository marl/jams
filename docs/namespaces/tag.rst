Tag
---

tag_cal10k
~~~~~~~~~~

tag_cal500
~~~~~~~~~~

tag_gtzan
~~~~~~~~~

tag_medleydb_instruments
~~~~~~~~~~~~~~~~~~~~~~~~
MedleyDB instrument source annotations.

    ===== ======== ================== ==========
    time  duration value              confidence
    ===== ======== ================== ==========
    [sec] [sec]    string             --
    ===== ======== ================== ==========

The ``value`` field is constrained to the set of instruments defined
in MedleyDB_ instrument taxonomy_.

.. _MedleyDB: http://medleydb.weebly.com/
.. _taxonomy: http://marl.smusic.nyu.edu/medleydb_webfiles/taxonomy.yaml

*Example*

    ===== ======== ================== ==========
    time  duration value              confidence
    ===== ======== ================== ==========
    0.000 20.000   "darbuka"          null
    0.000 20.000   "flute section"    null
    0.000 20.000   "oud"              null
    ===== ======== ================== ==========

tag_open
~~~~~~~~
Open vocabulary tags.  This namespace is appropriate for unconstrained
tag data, such as social tags from Last.FM.

    ===== ======== ================== ==========
    time  duration value              confidence
    ===== ======== ================== ==========
    [sec] [sec]    string             --
    ===== ======== ================== ==========

The ``value`` field is unconstrained, and can contain any string value.

*Example*

    ===== ======== ================== ==========
    time  duration value              confidence
    ===== ======== ================== ==========
    0.000 20.000   "rocking"          null
    0.000 20.000   "rockin'"          null
    0.000 20.000   ""                 null
    0.000 20.000   "favez^^^"         null
    ===== ======== ================== ==========


