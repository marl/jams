jams
====
[![PyPI](https://img.shields.io/pypi/v/jams.svg)](https://pypi.python.org/pypi/jams)
[![License](https://img.shields.io/pypi/l/jams.svg)](https://github.com/marl/jams/blob/master/LICENSE.md)
[![Build Status](https://travis-ci.org/marl/jams.svg?branch=master)](https://travis-ci.org/marl/jams)
[![Coverage Status](https://coveralls.io/repos/marl/jams/badge.svg?branch=master)](https://coveralls.io/r/marl/jams?branch=master)
[![Dependency Status](https://dependencyci.com/github/marl/jams/badge)](https://dependencyci.com/github/marl/jams)

A JSON Annotated Music Specification for Reproducible MIR Research.

Please, refer to [documentation](http://jams.readthedocs.io/en/stable/) for a comprehensive
description of JAMS.

What
----
JAMS is a JSON-based music annotation format.

We provide:
* A formal JSON schema for generic annotations
* The ability to store multiple annotations per file
* Schema definitions for a wide range of annotation types (beats, chords, segments, tags, etc.)
* Error detection and validation for annotations
* A translation layer to interface with [mir eval](https://craffel.github.io/mir_eval)
    for evaluating annotations

Why
----
Music annotations are traditionally provided as plain-text files employing
simple formatting schema (comma or tab separated) when possible. However, as
the field of MIR has continued to evolve, such annotations have become
increasingly complex, and more often custom conventions are employed to
represent this information. And, as a result, these custom conventions can be
unwieldy and non-trivial to parse and use.

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

The full documentation can be found [here](http://jams.readthedocs.io/en/stable/).

Who
----
To date, the initial JAMS effort has evolved out of internal needs at MARL@NYU,
with some great feedback from our friends at LabROSA.

If you want to get involved, do let us know!

Details
-------
JAMS is proposed in the following publication:

[1] Eric J. Humphrey, Justin Salamon, Oriol Nieto, Jon Forsyth, Rachel M. Bittner,
and Juan P. Bello, "[JAMS: A JSON Annotated Music Specification for Reproducible
MIR Research](http://marl.smusic.nyu.edu/papers/humphrey_jams_ismir2014.pdf)",
Proceedings of the 15th International Conference on Music Information Retrieval,
2014.

The JAMS schema and data representation used in the API were overhauled significantly between versions 0.1 (initial proposal) and 0.2 (overhauled), see the following technical report for details:

[2] B. McFee, E. J. Humphrey, O. Nieto, J. Salamon, R. Bittner, J. Forsyth, J. P. Bello, "[Pump Up The JAMS: V0.2 And Beyond](http://www.justinsalamon.com/uploads/4/3/9/4/4394963/mcfee_jams_ismir_lbd2015.pdf)", Technical report, October 2015.
