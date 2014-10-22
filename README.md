jams
====

A JSON Annotated Music Specification for Reproducible MIR Research.

What
----
JAMS is a JSON-based music annotation format.

We provide:
* A formal JSON schema
* Python and MATLAB software libraries
* Some popular datasets in JAMS format
* Python scripts demonstrating how to convert datasets into the JAMS format

Why
----
Music annotations are traditionally provided as plain-text files employing
simple formatting schema (comma or tab separated) when possible. However, as
the field of MIR has continued to evolve, such annotations have become
increasingly complex, and more often custom conventions are employed to
represent this information. And, as a result, these custom conventions can be
unweildy and non-trivial to parse and use.

Therefore, JAMS provides a simple, structured, and sustainable approach to
representing rich information in a human-readable, language agnostic format.
Importantly, JAMS supports the following use-cases:
* multiple types annotations
* multiple annotations for a given task
* rich file level and annotation level metadata

How
----
This library is offered as a proof-of-concept, demonstrating the promise of a
JSON-based schema to meet the needs of the MIR community. To install, clone the
repository into a working directory and proceed thusly.

Who
----
To date, the initial JAMS effort has evolved out of internal needs at MARL@NYU,
with some great feedback from our friends at LibROSA. Having reached a
reasonable state, we're now actively seeking greater input from the larger MIR
community, in any of the following roles:
* Users
* Designers
* Collaborators

If you want to get involved, do let us know!

Details
-------
JAMS is proposed in the following publication:

Eric J. Humphrey, Justin Salamon, Oriol Nieto, Jon Forsyth, Rachel M. Bittner,
and Juan P. Bello, "[JAMS: A JSON Annotated Music Specification for Reproducible
MIR Research](http://marl.smusic.nyu.edu/papers/humphrey_jams_ismir2014.pdf)",
Proceedings of the 15th International Conference on Music Information Retrieval,
2014.
