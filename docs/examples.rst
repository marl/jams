*************
Example usage
*************

Storing annotations
===================

This section demonstrates a complete use-case of JAMS for storing estimated annotations.
The example uses `librosa <https://bmcfee.github.io/librosa/>`_ to estimate global tempo 
and beat timings.

example_beat.py
---------------

The following script loads the librosa example audio clip, estimates the track duration,
tempo, and beat timings, and constructs a JAMS object to store the estimations.

.. literalinclude:: examples/example_beat.py
    :linenos:

example_beat_output.jams
------------------------
The above script generates the following JAMS object.

.. literalinclude:: examples/example_beat_output.jams
    :linenos:
    :language: javascript

Evaluating annotations
======================

The following script illustrates how to evaluate one JAMS annotation object against another using the
built-in `eval` submodule to wrap `mir_eval <https://craffel.github.io/mir_eval>`_.

Given two jams files, say, `reference.jams` and `estimate.jams`, the script first loads them as objects
(``j_ref`` and ``j_est``, respectively).  It then uses the `JAMS.search` method to locate all
annotations of namespace ``"beat"``.  If no matching annotations are found, an empty list is returned.

In this example, we are assuming that each JAMS file contains only a
single annotation of interest, so the first result is taken by indexing the results at 0.  (In general, you
may want to use `annotation_metadata` to select a specific annotation from the JAMS object, if multiple are
present.)

Finally, the two annotations are compared by calling `jams.eval.beat`, which returns an ordered
dictionary of evaluation metrics for the annotations in question.

example_eval.py
---------------

.. literalinclude:: examples/example_eval.py
    :linenos:


Data conversion
===============

JAMS provides some basic functionality to help convert from flat file formats (e.g., CSV or LAB).

example_chord_import.py
-----------------------

.. literalinclude:: examples/example_chord_import.py
    :linenos:

chord_output.jams
-----------------

Calling the above script on `01_-_I_Saw_Her_Standing_There.lab
<http://isophonics.net/files/annotations/chordlab/The%20Beatles/01_-_Please_Please_Me/01_-_I_Saw_Her_Standing_There.lab>`_
from `IsoPhonics <http://isophonics.net/>`_ should produce the following JAMS object:

.. literalinclude:: examples/example_chord.jams
    :linenos:
    :language: javascript


More examples
=============
In general, converting a dataset to JAMS format will require a bit more work to ensure that value fields
conform to the specified namespace schema, but the import script above should serve as a simple starting
point.

For further reference, a separate repository `jams-data <https://github.com/marl/jams-data>`_ has been 
created to house conversion scripts for publicly available datasets.
Note that development of converters is a work in progress, so proceed with caution!
