JAMS Structure
--------------

This section describes the anatomy of JAMS objects.

JAMS
~~~~

A JAMS object consists of three basic properties:
    * ``file_metadata``, which describes the audio file to which these annotations are attached;
    * ``annotations``, a list of Annotation_ objects (described below); and
    * ``sandbox``, an un-restricted place to store any additional data.


FileMetadata
~~~~~~~~~~~~
The ``file_metadata`` field contains the following properties:
    * ``identifiers``: an unstructured ``sandbox``-type object for storing identifier mappings, e.g., MusicBrainz
      ID;
    * ``artist``, ``title``, ``release`` : meta-data strings for the track in question;
    * ``duration`` : non-negative number describing the length (in seconds) of the track; and
    * ``jams_version`` : string describing the JAMS version for this file.

Annotation
~~~~~~~~~~
.. _Annotation:
Each annotation object contains the following properties:
    * ``namespace`` : a string describing the type of this annotation;
    * ``data`` : a list of observations, each containing:
        * ``time`` : non-negative number denoting the time of the observation (in seconds)
        * ``duration`` : non-negative number denoting the duration of the observation (in seconds)
        * ``value`` : actual annotation (e.g., chord, segment label)
        * ``confidence`` : certainty of the annotation
    * ``annotation_metadata`` : see Annotation_Metadata_; and
    * ``sandbox`` : additional un-structured storage space for this annotation.

The permissible contents of the ``value`` and ``confidence`` fields are defined by the ``namespace``.

Annotation_Metadata
~~~~~~~~~~~~~~~~~~~
The metadata associated with each annotation describes the process by which the annotation was generated.
The ``annotation_metadata`` property has the following fields:

    * ``corpus``: a string describing a corpus to which this annotation belongs;
    * ``version`` : string or number, the version of this annotation;
    * ``curator`` : a structured object containing contact information (``name`` and ``email``) for the curator of this data;
    * ``annotator`` : a ``sandbox`` object to describe the individual annotator --- which can be a person or a program --- that generated this annotation;
    * ``annotation_tools``, ``annotation_rules``, ``validation``: strings to describe the process by which
      annotations were collected and pre-processed; and
    * ``data_source`` : string describing the type of annotator, e.g., "program", "expert human",
      "crowdsource".

