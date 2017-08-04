.. jams documentation master file, created by
   sphinx-quickstart on Mon Dec  8 10:34:40 2014.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

####
JAMS
####
A JSON Annotated Music Specification for Reproducible MIR Research.

JAMS provides:
    * A formal JSON schema for generic annotations
    * The ability to store multiple annotations per file
    * Schema definitions for a wide range of annotation types (beats, chords, segments, tags, etc.)
    * Error detection and validation
    * A translation layer to interface with `mir_eval <https://craffel.github.io/mir_eval>`_ for evaluating annotations

For the most recent information, please refer to `JAMS on github <https://github.com/marl/jams>`_.

.. toctree:: 
    :maxdepth: 2

    quickstart
    jams_structure
    namespace_structure
    examples

*************
API reference
*************
.. toctree:: 
    :maxdepth: 2

    jams
    namespace

**********
Contribute
**********
- `Issue Tracker <http://github.com/marl/jams/issues>`_
- `Source Code <http://github.com/marl/jams>`_


*********
Changelog
*********
.. toctree::
    :maxdepth: 2

    changes

* :ref:`genindex`

