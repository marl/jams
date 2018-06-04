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

tag_msd_tagtraum_cd1
~~~~~~~~~~~~~~~~~~~~
Genre classes from the `msd tagtraum cd1`_ dataset.

    ===== ======== ================== ==========
    time  duration value              confidence
    ===== ======== ================== ==========
    [sec] [sec]    string             --
    ===== ======== ================== ==========

The ``value`` field is constrained to one of 13 strings:

    - ``reggae``
    - ``pop/rock``
    - ``rnb``
    - ``jazz``
    - ``vocal``
    - ``new age``
    - ``latin``
    - ``rap``
    - ``country``
    - ``international``
    - ``blues``
    - ``electronic``
    - ``folk``

.. _msd tagtraum cd1: http://www.tagtraum.com/msd_genre_datasets.html

By convention, one or two tags per track are possible in this namespace.
The sum of the confidence values should equal ``1.0``.
This is not enforced by the schema.


*Example*

    ===== ======== ======== ==========
    time  duration value    confidence
    ===== ======== ======== ==========
    0.000 0.000    "reggae" 1.0
    ===== ======== ======== ==========

tag_msd_tagtraum_cd2
~~~~~~~~~~~~~~~~~~~~
Genre classes from the `msd tagtraum cd2`_ dataset.

    ===== ======== ================== ==========
    time  duration value              confidence
    ===== ======== ================== ==========
    [sec] [sec]    string             --
    ===== ======== ================== ==========

The ``value`` field is constrained to one of 15 strings:

    - ``reggae``
    - ``latin``
    - ``metal``
    - ``rnb``
    - ``jazz``
    - ``punk``
    - ``pop``
    - ``new age``
    - ``country``
    - ``rap``
    - ``rock``
    - ``world``
    - ``blues``
    - ``electronic``
    - ``folk``

.. _msd tagtraum cd2: http://www.tagtraum.com/msd_genre_datasets.html

By convention, one or two tags per track are possible in this namespace.
The sum of the confidence values should equal ``1.0``.
This is not enforced by the schema.


*Example*

    ===== ======== ======== ==========
    time  duration value    confidence
    ===== ======== ======== ==========
    0.000 0.000    "reggae" 0.6666667
    0.000 0.000    "rock"   0.3333333
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

tag_audioset
~~~~~~~~~~~~
Tags from the full AudioSet (v1) ontology.

    ===== ======== ================== ==========
    time  duration value              confidence
    ===== ======== ================== ==========
    [sec] [sec]    string             --
    ===== ======== ================== ==========

The ``value`` field is constrained to the vocabulary of the AudioSet_ ontology.

*Example*

    ===== ======== ================== ==========
    time  duration value              confidence
    ===== ======== ================== ==========
    0.000 20.000   "Air brake"        null
    5.000 25.000   "Yodeling"         null
    9.000 35.000   "Steam whistle"    null
    ===== ======== ================== ==========

.. _AudioSet: https://research.google.com/audioset/ontology/index.html


tag_audioset_genre
~~~~~~~~~~~~~~~~~~
Tags from the musical genre subset of the AudioSet (v1) ontology.

    ===== ======== ================== ==========
    time  duration value              confidence
    ===== ======== ================== ==========
    [sec] [sec]    string             --
    ===== ======== ================== ==========

The ``value`` field is constrained to the 66 musical genres of the AudioSet-genre_ ontology.

*Example*

    ===== ======== ================== ==========
    time  duration value              confidence
    ===== ======== ================== ==========
    0.000 20.000   "Oldschool jungle" null
    ===== ======== ================== ==========

.. _AudioSet-genre: https://research.google.com/audioset/ontology/music_genre_1.html

tag_audioset_instrument
~~~~~~~~~~~~~~~~~~~~~~~
Tags from the musical instrument subset of the AudioSet (v1) ontology.

    ===== ======== ================== ==========
    time  duration value              confidence
    ===== ======== ================== ==========
    [sec] [sec]    string             --
    ===== ======== ================== ==========

The ``value`` field is constrained to the 91 musical instruments 
of the AudioSet-instruments_ ontology.

*Example*

    ===== ======== ================== ==========
    time  duration value              confidence
    ===== ======== ================== ==========
    0.000 20.000   "Ukulele"          null
    5.000 25.000   "Piano"            null
    9.000 35.000   "Tuning fork"      null
    ===== ======== ================== ==========

.. _AudioSet-instruments: https://research.google.com/audioset/ontology/musical_instrument_1.html

tag_fma_genre
~~~~~~~~~~~~~
Tags from the Free Music Archive (FMA) 16-class genre taxonomy.

    ===== ======== ================== ==========
    time  duration value              confidence
    ===== ======== ================== ==========
    [sec] [sec]    string             --
    ===== ======== ================== ==========

The ``value`` field is constrained to the 16 genres 
of the FMA_ data-set.

*Example*

    ===== ======== ================== ==========
    time  duration value              confidence
    ===== ======== ================== ==========
    0.000 20.000   "Blues"            null
    5.000 25.000   "Instrumental"     null
    9.000 35.000   "Soul-RnB"         null
    ===== ======== ================== ==========

.. _FMA: https://github.com/mdeff/fma

tag_fma_subgenre
~~~~~~~~~~~~~~~~
Tags from the Free Music Archive (FMA) 163-class genre and sub-genre taxonomy.

    ===== ======== ================== ==========
    time  duration value              confidence
    ===== ======== ================== ==========
    [sec] [sec]    string             --
    ===== ======== ================== ==========

The ``value`` field is constrained to the 163 genres and sub-genres of the FMA_ data-set.

*Example*

    ===== ======== ================== ==========
    time  duration value              confidence
    ===== ======== ================== ==========
    0.000 20.000   "Pop"              null
    5.000 25.000   "Power-Pop"        null
    9.000 35.000   "Nerdcore"         null
    ===== ======== ================== ==========

tag_urbansound
~~~~~~~~~~~~~~
Genre classes from the UrbanSound_ dataset.

    ===== ======== ================== ==========
    time  duration value              confidence
    ===== ======== ================== ==========
    [sec] [sec]    string             --
    ===== ======== ================== ==========

The ``value`` field is constrained to one of ten strings:

    - ``air_conditioner``
    - ``car_horn``
    - ``children_playing``
    - ``dog_bark``
    - ``drilling``
    - ``engine_idling``
    - ``gun_shot``
    - ``jackhammer``
    - ``siren``
    - ``street_music``

.. _UrbanSound: https://serv.cusp.nyu.edu/projects/urbansounddataset/

*Example*

    ===== ======== ============== ==========
    time  duration value          confidence
    ===== ======== ============== ==========
    0.000 30.000   "street_music" null
    ===== ======== ============== ==========

