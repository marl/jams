Tag
---

tag_cal10k
~~~~~~~~~~
Tags from the CAL10K_ vocabulary.

    ===== ======== ================== ==========
    time  duration value              confidence
    ===== ======== ================== ==========
    [sec] [sec]    string             --
    ===== ======== ================== ==========

.. _CAL10K: http://theremin.ucsd.edu/~gert/datasets/cal10k/README_CAL_10K.txt

The ``value`` is constrained to a set of 1053 terms, spanning mood, instrumentation,
style, and genre.

    ===== ======== ================= ==========
    time  duration value             confidence
    ===== ======== ================= ==========
    0.000 30.000   "bop influences"  null
    0.000 30.000   "bright beats"    null
    0.000 30.000   "hip hop roots"   null
    ===== ======== ================= ==========


tag_cal500
~~~~~~~~~~
Tags from the CAL500_ vocabulary.

    ===== ======== ================== ==========
    time  duration value              confidence
    ===== ======== ================== ==========
    [sec] [sec]    string             --
    ===== ======== ================== ==========

.. _CAL500: http://theremin.ucsd.edu/~gert/datasets/cal500/

The ``value`` is constrained to a set of 174 terms, spanning mood, instrumentation, and
genre.

    ===== ======== ================= ==========
    time  duration value             confidence
    ===== ======== ================= ==========
    0.000 30.000   "Genre-Best-Rock" null
    0.000 30.000   "Vocals-Monotone" null
    0.000 30.000   "Usage-At_work"   null
    ===== ======== ================= ==========


tag_gtzan
~~~~~~~~~
Genre classes from the GTZAN_ dataset.

    ===== ======== ================== ==========
    time  duration value              confidence
    ===== ======== ================== ==========
    [sec] [sec]    string             --
    ===== ======== ================== ==========

The ``value`` field is constrained to one of ten strings:

    - ``blues``
    - ``classical``
    - ``country``
    - ``disco``
    - ``hip-hop``
    - ``jazz``
    - ``metal``
    - ``pop``
    - ``reggae``
    - ``rock``

.. _GTZAN: http://marsyasweb.appspot.com/download/data_sets/

By convention, only one tag is applied per track in this namespace.  This is not enforced
by the schema.

*Example*

    ===== ======== ======== ==========
    time  duration value    confidence
    ===== ======== ======== ==========
    0.000 30.000   "reggae" null
    ===== ======== ======== ==========



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
tag data, such as tags from Last.FM or Magnatagatune.

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


