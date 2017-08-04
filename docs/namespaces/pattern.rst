Pattern
-------

.. _patternjku:

pattern_jku
~~~~~~~~~~~

Each note of the pattern contains ``(pattern_id, midi_pitch, occurrence_id, morph_pitch, 
staff)``, following the format described in [4]_.

    +-------+----------+------------------+------------+
    | time  | duration | value            | confidence |
    +=======+==========+==================+============+
    | [sec] | [sec]    | - pattern_id     | --         |
    |       |          | - midi_pitch     |            |
    |       |          | - occurrence_id  |            |
    |       |          | - morph_pitch    |            |
    |       |          | - staff          |            |
    +-------+----------+------------------+------------+

.. [4] Collins T., Discovery of Repeated Themes & Sections, Music Information Retrieval 
    Evalaluation eXchange (MIReX), 2013 (Accessed on July 7th 2015). Available `here
    <http://www.music-ir.org/mirex/wiki/2013:Discovery_of_Repeated_Themes_&_Sections>`_.

Each ``value`` field contains a dictionary with the following keys:

    * ``pattern_id``: The integer that identifies the current pattern, \
        starting from 1.
    * ``midi_pitch``: The float representing the midi pitch.
    * ``occurrence_id``: The integer that identifies the current occurrence, \
        starting from 1.
    * ``morph_pitch``: The float representing the morphological pitch.
    * ``staff``: The integer representing the staff where the current note of the \
        patter is found, starting from 0.


*Example*

    +-------+----------+--------------------+------------+
    | time  | duration | value              | confidence |
    +=======+==========+====================+============+
    | 62.86 | 0.09     | - pattern_id: 1    | null       |
    |       |          | - midi_pitch: 50   |            |
    |       |          | - occurrence_id: 1 |            |
    |       |          | - morph_pitch: 54  |            |
    |       |          | - staff: 1         |            |
    +-------+----------+--------------------+------------+
    | 62.86 | 0.36     | - pattern_id: 1    | null       |
    |       |          | - midi_pitch: 77   |            |
    |       |          | - occurrence_id: 1 |            |
    |       |          | - morph_pitch: 70  |            |
    |       |          | - staff: 0         |            |
    +-------+----------+--------------------+------------+
    | 36.34 | 0.09     | - pattern_id: 1    | null       |
    |       |          | - midi_pitch: 71   |            |
    |       |          | - occurrence_id: 2 |            |
    |       |          | - morph_pitch: 66  |            |
    |       |          | - staff: 0         |            |
    +-------+----------+--------------------+------------+
    | 36.43 | 0.36     | - pattern_id: 1    | null       |
    |       |          | - midi_pitch: 69   |            |
    |       |          | - occurrence_id: 2 |            |
    |       |          | - morph_pitch: 65  |            |
    |       |          | - staff: 0         |            |
    +-------+----------+--------------------+------------+

