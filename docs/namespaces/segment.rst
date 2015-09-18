Segment
-------

segment_open
~~~~~~~~~~~~
Structural segmentation with an open vocabulary of segment labels.

    ===== ======== ================== ==========
    time  duration value              confidence
    ===== ======== ================== ==========
    [sec] [sec]    string             --
    ===== ======== ================== ==========

The ``value`` field contains string descriptors for each segment, e.g., "verse" or
"bridge".

*Example*
    ===== ======== ==================== ==========
    time  duration value                confidence
    ===== ======== ==================== ==========
    0.000 20.000   intro                null
    20.00 30.000   verse                null
    30.00 50.000   refrain              null
    50.00 70.000   verse (alternate)    null
    ===== ======== ==================== ==========


segment_salami_function
~~~~~~~~~~~~~~~~~~~~~~~
Segment annotations with functional labels from the SALAMI guidelines.

    ===== ======== ================== ==========
    time  duration value              confidence
    ===== ======== ================== ==========
    [sec] [sec]    string             --
    ===== ======== ================== ==========

The ``value`` field must be one of the allowable strings in the SALAMI function
vocabulary_.

.. _vocabulary: https://github.com/DDMAL/salami-data-public/blob/master/funct_vocab_dictionary.txt

*Example*
    ===== ======== ==================== ==========
    time  duration value                confidence
    ===== ======== ==================== ==========
    0.000 20.000   applause             null
    20.00 30.000   count-in             null
    30.00 50.000   introduction         null
    50.00 70.000   verse                null
    ===== ======== ==================== ==========


segment_salami_upper
~~~~~~~~~~~~~~~~~~~~
Segment annotations with SALAMI's upper-case (large) label format.

    ===== ======== ================== ==========
    time  duration value              confidence
    ===== ======== ================== ==========
    [sec] [sec]    string             --
    ===== ======== ================== ==========

The ``value`` field must be a string of the following format:

    - "silence" or "Silence"
    - One or more upper-case letters, followed by zero or more apostrophes

*Example*
    ===== ======== ==================== ==========
    time  duration value                confidence
    ===== ======== ==================== ==========
    0.000 20.000   silence              null
    20.00 30.000   A                    null
    30.00 50.000   B                    null
    50.00 70.000   A'                   null
    ===== ======== ==================== ==========


segment_salami_lower
~~~~~~~~~~~~~~~~~~~~
Segment annotations with SALAMI's lower-case (small) label format.

    ===== ======== ================== ==========
    time  duration value              confidence
    ===== ======== ================== ==========
    [sec] [sec]    string             --
    ===== ======== ================== ==========

The ``value`` field must be a string of the following format:

    - "silence" or "Silence"
    - One or more lower-case letters, followed by zero or more apostrophes

*Example*
    ===== ======== ==================== ==========
    time  duration value                confidence
    ===== ======== ==================== ==========
    0.000 20.000   silence              null
    20.00 30.000   a                    null
    30.00 50.000   b                    null
    50.00 70.000   a'                   null
    ===== ======== ==================== ==========

segment_tut
~~~~~~~~~~~
Segment annotations using the TUT_ vocabulary.

    ===== ======== ================== ==========
    time  duration value              confidence
    ===== ======== ================== ==========
    [sec] [sec]    string             --
    ===== ======== ================== ==========

.. _TUT: http://www.cs.tut.fi/sgn/arg/paulus/structure.html

The ``value`` field is a string describing the function of the segment.

*Example*
    ===== ======== ==================== ==========
    time  duration value                confidence
    ===== ======== ==================== ==========
    0.000 20.000   Intro                null
    20.00 30.000   Verse                null
    30.00 50.000   bridge               null
    50.00 70.000   RefrainA             null
    ===== ======== ==================== ==========


multi_segment
~~~~~~~~~~~~~
Multi-level structural segmentations.

    ===== ======== ================== ==========
    time  duration value              confidence
    ===== ======== ================== ==========
    [sec] [sec]    * label : string   --
                   * level : int >= 0
    ===== ======== ================== ==========

In a multi-level segmentation, the track is partitioned many times --- 
possibly recursively --- which results in a collection of segmentations of varying degrees
of specificity.  In the ``multi_segment`` namespace, all of the resulting segments are
collected together, and the ``level`` field is used to encode the segment's corresponding
partition.

Level values must be non-negative, and ordered by increasing specificity.  For example,
``level==0`` may correspond to a single segment spanning the entire track, and each
subsequent level value corresponds to a more refined segmentation.

*Example*
    ===== ======== ================== ==========
    time  duration value              confidence
    ===== ======== ================== ==========
    0.000 60.000   * label : A        null
                   * level : 0
    0.000 30.000   * label : B        null
                   * level : 1
    30.00 60.000   * label : C        null
                   * level : 1
    0.000 15.000   * label : a        null
                   * level : 2
    15.00 30.000   * label : b        null
                   * level : 2
    30.00 45.000   * label : a        null
                   * level : 2
    45.00 60.000   * label : c        null
                   * level : 2
    ===== ======== ================== ==========


