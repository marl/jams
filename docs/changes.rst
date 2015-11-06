Changes
=======

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

Schema changes
  - ``Annotation`` objects now have ``time`` and ``duration`` fields which encode the
    interval over which the annotation is valid.
    (`PR #67 <https://github.com/marl/jams/pull/67>`_).

Bug fixes
  - Appending data to ``Annotation`` or ``JamsFrame`` objects now fails if ``time`` or ``duration`` are
    ill-specified.
    (`PR #87 <https://github.com/marl/jams/pull/87>`_).

