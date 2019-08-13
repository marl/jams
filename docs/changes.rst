Changes
=======

v0.3.4
------

- Added support for jsonschema version 3.0 (`PR #202
  <https://github.com/marl/jams/pull/202>`_)

- Added converter script `jams_to_mirex_pattern.py` (`PR #194 
  <https://github.com/marl/jams/pull/194>`_)

v0.3.3
------

- Pinned jsonschema dependency to version 2.6 (`PR #200
  <https://github.com/marl/jams/pull/200>`_)

v0.3.2
------

- Added schemata for ``tag_urbansound`` and ``scaper`` (`PR #191 <https://github.com/marl/jams/pull/191>`_)
- Fixed a timing bug in ``Annotation.slice`` (`PR #189 <https://github.com/marl/jams/pull/189>`_)
- Added ``display`` mapping for ``tag_open`` namespaces (`PR #188 <https://github.com/marl/jams/pull/188>`_)
- Updated `sortedcontainers` dependency to avoid deprecations (`PR #187 <https://github.com/marl/jams/pull/187>`_)

v0.3.1
------

- Improved documentation (`PR #176 <https://github.com/marl/jams/pull/176>`_)
- Added ``Annotation.to_samples`` (`PR #173 <https://github.com/marl/jams/pull/173>`_)
- Added schemata for FMA genre tags (`PR #172 <https://github.com/marl/jams/pull/172>`_)
- Accelerated validation (`PR #170 <https://github.com/marl/jams/pull/170>`_)
- Added schemata for AudioSet tags (`PR #168 <https://github.com/marl/jams/pull/168>`_)
- Added ``jams.list_namespaces()`` (`PR #166 <https://github.com/marl/jams/pull/166>`_)

v0.3.0
------

- Removed the `JamsFrame` class and replaced the underlying observation storage data
  structure (`PR #149 <https://github.com/marl/jams/pull/149>`_).

- `import_lab` now returns only an `Annotation` and does not construct a `JAMS` object
  (`PR #154 <https://github.com/marl/jams/pull/154>`_)

- Accelerated pitch contour sonification
  (`PR #155 <https://github.com/marl/jams/pull/155>`_)

- Migrated all tests from nosetest to py.test
  (`PR #157 <https://github.com/marl/jams/pull/157>`_)

- Improved `repr()` and added HTML rendering for JAMS objects in notebooks
  (`PR #158 <https://github.com/marl/jams/pull/158>`_)

- Fixed a JSON serialization bug with numpy datatypes
  (`PR #160 <https://github.com/marl/jams/pull/160>`_)
  
v0.2.3
------

- Deprecated the `JamsFrame` class 
  (`PR #153 <https://github.com/marl/jams/pull/153>`_):

  - Moved `JamsFrame.to_interval_values()` to `Annotation.to_interval_values()`

  - Any code that uses `pandas.DataFrame` methods on `Annotation.data` will cease to work
    starting in 0.3.0.

- Forward compatibility with 0.3.0
  (`PR #153 <https://github.com/marl/jams/pull/153>`_):
  
  - Added the `jams.Observation` type

  - Added iteration support to `Annotation` objects

- added type safety check in regexp search (`PR #146 <https://github.com/marl/jams/pull/146>`_).
- added support for `pandas=0.20` (`PR #150 <https://github.com/marl/jams/pull/150>`_).

v0.2.2
------
- added ``__contains__`` method to ``JObject``
  (`PR #139 <https://github.com/marl/jams/pull/139>`_).
- Implemented ``JAMS.trim()`` method
  (`PR #136 <https://github.com/marl/jams/pull/136>`_).
- Updates to the SALAMI tag namespaces
  (`PR #134 <https://github.com/marl/jams/pull/134>`_).
- added `infer_duration` flag to ``import_lab``
  (`PR #125 <https://github.com/marl/jams/pull/125>`_).
- namespace conversion validates input
  (`PR #123 <https://github.com/marl/jams/pull/123>`_).
- Refactored the ``pitch`` namespaces
  (`PR #121 <https://github.com/marl/jams/pull/121>`_).
- Fancy indexing for annotation arrays
  (`PR #120 <https://github.com/marl/jams/pull/120>`_).
- ``jams.schema.values`` function to access enumerated types
  (`PR #119 <https://github.com/marl/jams/pull/119>`_).
- ``jams.display`` submodule
  (`PR #115 <https://github.com/marl/jams/pull/115>`_).
- support for `mir_eval >= 0.3`
  (`PR #106 <https://github.com/marl/jams/pull/106>`_).
- Automatic conversion between namespaces
  (`PR #105 <https://github.com/marl/jams/pull/105>`_).
- Fixed a type error in ``jams_to_lab``
  (`PR #94 <https://github.com/marl/jams/pull/94>`_).
- ``jams.sonify`` module for sonification
  (`PR #91 <https://github.com/marl/jams/pull/91>`_).

v0.2.1
------
New features
  - ``eval`` support for hierarchical segmentation via the ``multi_segment`` namespace
    (`PR #79 <https://github.com/marl/jams/pull/79>`_).
  - Local namespace management
    (`PR #75 <https://github.com/marl/jams/pull/75>`_).
  - Python 3.5 support
    (`PR #73 <https://github.com/marl/jams/pull/73>`_).
  - ``jams.search()`` now allows matching objects by equality
    (`PR #71 <https://github.com/marl/jams/pull/71>`_).
  - ``multi_segment`` namespace for multi-level structural segmentations.
    (`PR #69 <https://github.com/marl/jams/pull/69>`_).
  - ``vector`` namespace for numerical vector data
    (`PR #64 <https://github.com/marl/jams/pull/64>`_).
  - ``blob`` namespace for unstructured, time-keyed observation data
    (`PR #63 <https://github.com/marl/jams/pull/63>`_).
  - ``tag_msd_tagtraum_cd1`` and ``tag_msd_tagtraum_cd2`` namespaces for genre tags
    (`PR #83 <https://github.com/marl/jams/pull/83>`_).

Schema changes
  - ``Annotation`` objects now have ``time`` and ``duration`` fields which encode the
    interval over which the annotation is valid.
    (`PR #67 <https://github.com/marl/jams/pull/67>`_).

Bug fixes
  - Appending data to ``Annotation`` or ``JamsFrame`` objects now fails if ``time`` or ``duration`` are
    ill-specified.
    (`PR #87 <https://github.com/marl/jams/pull/87>`_).

