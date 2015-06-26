Chord
-----

chord_harte
~~~~~~~~~~~
Chord annotations described according to the grammar defined by Harte, et al. [1]_

    ===== ======== ====== ==========
    time  duration value  confidence
    ===== ======== ====== ==========
    [sec] [sec]    string --
    ===== ======== ====== ==========

.. [1] Harte, Christopher, Mark B. Sandler, Samer A. Abdallah, and Emilia Gómez.
    "Symbolic Representation of Musical Chords: A Proposed Syntax for Text Annotations."
    In ISMIR, vol. 5, pp. 66-71. 2005.


Each observed value is a text representation of a chord annotation.

    * ``N`` specifies a *no chord* observation
    * Notes are annotated in the usual way: ``A-G`` followed by optional sharps (``#``) and flats (``b``)
    * Chord qualities are denoted by abbreviated strings:
        - *maj*, *min*, *dim*, *aug*
        - *maj7*, *min7*, *7*, *dim7*, *hdim7*, *minmaj7*
        - *maj6*, *min6*
        - *9*, *maj9*, *min9*
        - *sus4*, *sus2*
        - *5*, *1*
    * Inversions are specified by a slash (``/``) followed by the interval number, e.g., ``G/3``.
    * Extensions are denoted in parentheses, e.g., ``G(b11,13)``.
      Suppressed notes are indicated with an asterisk, e.g., ``G(*3)``

A complete description of the chord grammar is provided in [1]_, table 1.

*Example*

    ===== ======== ========= ==========
    time  duration value     confidence
    ===== ======== ========= ==========
    0.000 1.000    N         null
    0.000 1.000    Bb        null
    0.000 1.000    E:(*5)    null
    0.000 1.000    E#:min9/9 null
    0.000 1.000    G#:maj6   null
    0.000 1.000    D/6       null
    0.000 1.000    A:sus2    null
    ===== ======== ========= ==========


.. note::
    The grammar defined in [1]_ has been extended to support ``sus2``, ``5`` and ``1`` qualities.

    ``confidence`` is an unconstrained field, and may contain arbitrary data.

chord_roman
~~~~~~~~~~~

