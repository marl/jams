Chord
-----

chord
~~~~~
Chord annotations described by an extended version of the grammar defined by Harte, et al. [1]_

    ===== ======== ====== ==========
    time  duration value  confidence
    ===== ======== ====== ==========
    [sec] [sec]    string --
    ===== ======== ====== ==========

.. [1] Harte, Christopher, Mark B. Sandler, Samer A. Abdallah, and Emilia Gómez.
    "Symbolic Representation of Musical Chords: A Proposed Syntax for Text Annotations."
    In ISMIR, vol. 5, pp. 66-71. 2005.

This namespace is similar to `chord_harte`, with the following modifications:

    * Sharps and flats may not be mixed in a note symbol.  For instance, `A#b#` is legal in `chord_harte` but
      not in `chord`.  `A###` is legal in both.
    * The following quality values have been added: 
        - *sus2*, *1*, *5*
        - *aug7*
        - *11*, *maj11*, *min11*
        - *13*, *maj13*, *min13*

*Example*

    ===== ======== ============= ==========
    time  duration value         confidence
    ===== ======== ============= ==========
    0.000 1.000    ``N``         null
    0.000 1.000    ``Bb:5``      null
    0.000 1.000    ``E:(*5)``    null
    0.000 1.000    ``E#:min9/9`` null
    0.000 1.000    ``G##:maj6``  null
    0.000 1.000    ``D:13/6``    null
    0.000 1.000    ``A:sus2``    null
    ===== ======== ============= ==========

.. note::
    ``confidence`` is an unconstrained field, and may contain arbitrary data.


chord_harte
~~~~~~~~~~~
Chord annotations described according to the grammar defined by Harte, et al. [1]_

    ===== ======== ====== ==========
    time  duration value  confidence
    ===== ======== ====== ==========
    [sec] [sec]    string --
    ===== ======== ====== ==========

Each observed value is a text representation of a chord annotation.

    * ``N`` specifies a *no chord* observation
    * Notes are annotated in the usual way: ``A-G`` followed by optional sharps (``#``) and flats (``b``)
    * Chord qualities are denoted by abbreviated strings:
        - *maj*, *min*, *dim*, *aug*
        - *maj7*, *min7*, *7*, *dim7*, *hdim7*, *minmaj7*
        - *maj6*, *min6*
        - *9*, *maj9*, *min9*
        - *sus4*
    * Inversions are specified by a slash (``/``) followed by the interval number, e.g., ``G/3``.
    * Extensions are denoted in parentheses, e.g., ``G(b11,13)``.
      Suppressed notes are indicated with an asterisk, e.g., ``G(*3)``

A complete description of the chord grammar is provided in [1]_, table 1.

*Example*

    ===== ======== ============= ==========
    time  duration value         confidence
    ===== ======== ============= ==========
    0.000 1.000    ``N``         null
    0.000 1.000    ``Bb``        null
    0.000 1.000    ``E:(*5)``    null
    0.000 1.000    ``E#:min9/9`` null
    0.000 1.000    ``G#b:maj6``  null
    0.000 1.000    ``D/6``       null
    0.000 1.000    ``A:sus4``    null
    ===== ======== ============= ==========


.. note::
    ``confidence`` is an unconstrained field, and may contain arbitrary data.


chord_roman
~~~~~~~~~~~
Chord annotations in roman numeral format, as described by [2]_.

    +-------+----------+------------+------------+
    | time  | duration | value      | confidence |
    +=======+==========+============+============+
    | [sec] | [sec]    | - tonic    | --         |
    |       |          | - chord    |            |
    +-------+----------+------------+------------+

The ``value`` field is a structure containing the following fields:

  - ``tonic`` : (string) the tonic note of the chord, e.g., ``A`` or ``Gb``.
  - ``chord`` : (string) the scale degree of the chord in roman numerals (1--7), along with
    inversions, extensions, and qualities.

    - Scale degrees are encoded with optional leading sharps and flats, e.g., ``V``, ``bV`` or
      ``#VII``.  Upper-case numerals indicate major, lower-case numeral indicate minor.
    
    - Qualities are encoded as one of the following symbols:
    
        - ``o`` : diminished (triad)
        - ``+`` : augmented (triad)
        - ``s`` : suspension
        - ``d`` : dominant (seventh)
        - ``h`` : half-diminished (seventh)
        - ``x`` : fully-diminished (seventh)
    - Inversions are encoded by arabic numerals, e.g., ``V6`` for a first-inversion triad, ``V64``
      for second inversion.
    
    - Applied chords are encoded by a ``/`` followed by a roman numeral encoding of the scale degree,
      e.g., ``V7/IV``.

.. [2] http://theory.esm.rochester.edu/rock_corpus/harmonic_analyses.html

*Example*
    +-------+----------+--------------+------------+
    | time  | duration | value        | confidence |
    +=======+==========+==============+============+
    | 0.000 | 0.500    | - tonic: C   | --         |
    |       |          | - chord: I6  |            |
    +-------+----------+--------------+------------+
    | 0.500 | 0.500    | - tonic: C   | --         |
    |       |          | - chord: bIV |            |
    +-------+----------+--------------+------------+
    | 1.000 | 0.500    | - tonic: C   | --         |
    |       |          | - chord: Vh7 |            |
    +-------+----------+--------------+------------+

.. note::
    The grammar defined in [2]_ has been constrained to support only the quality symbols listed
    above.

    ``confidence`` is an unconstrained field, and may contain arbitrary data.

