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
