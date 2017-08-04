***************
Task namespaces
***************
In JAMS v0.2.0, the concept of task `namespaces` was introduced.  Broadly speaking, a `namespace`
defines the syntax (and some semantics) of a particular type of annotation.

For example, the `chord` namespace requires that all observed `value` fields are valid strings within a
pre-defined grammar.  Similarly, the `tempo` namespace requires that `value` fields be non-negative numbers,
and the `confidence` fields lie within the range `[0, 1]`.

JAMS ships with 26 pre-defined namespaces, covering a variety of common music informatics tasks.  This
collection should not be assumed to be complete, however, and more namespaces may be added in subsequent
versions.  Please refer to :ref:`namespace` for a comprehensive description of the existing namespaces.


Namespace specification format
==============================

In this section, we'll demonstrate how to define a task namespace, using `tempo` as our running example.
Namespaces are defined by JSON objects that contain partial `JSON schema <http://json-schema.org/>`_
specifications for the `value` and `confidence` fields of the :ref:`Annotation`, as well as additional meta-data to
describe the namespace and encoding.

`tempo.json` is reproduced here:

.. code-block:: json
    :linenos:

    {"tempo":
        {
            "value": {
                "type": "number", 
                "minimum": 0
            },
            "confidence": {
                "type": "number",
                "minimum": 0,
                "maximum": 1.0
            },
            "dense": false,
            "description": "Tempo measurements, in beats per minute (BPM)"
        }
    }

The key `"tempo"` at line 1 is the string with which this namespace will be identified in JAMS objects by the
annotation's `namespace` field.  This string must be a unique identifier.

Lines 3--6 specify the valid contents of the `value` field for tempo annotations.  In this case, values must
be numeric and non-negative.  Any valid JSON schema definition can be substituted here, allowing for
structured observation objects.  (See :ref:`pattern_jku <patternjku>` for an example of this.)

Similarly, lines 7--11 specify valid contents of the `confidence` field.  Most namespaces do not enforce
specific constraints on confidence, so this block is optional.  In the case of `tempo`, confidence must be a
numeric value in the range `[0, 1]`.

Line 12 `dense` is a boolean which specifies whether the annotation should be densely encoded during 
serialization or not.  There is functionally no difference between dense and sparse encoding, 
but dense coding is more space-efficient for high-frequency observations such as melody contours.

Finally, line 13 contains a brief description of the namespace and corresponding task.


Local namespaces
================

The JAMS namespace management architecture is modular and extensible, so it is relatively straightforward 
to create a new namespace schema and add it to JAMS at run-time:

    >>> jams.schema.add_namespace('/path/to/my/new/namespace.json')

Beginning with JAMS 0.2.1, a custom schema directory can be provided by setting the
``JAMS_SCHEMA_DIR`` environment variable prior to importing ``jams``.  This allows local
customizations to be added automatically at run-time without having to manually add each
schema file individually.
