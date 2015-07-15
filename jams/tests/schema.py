#!/usr/bin/env python
#CREATED:2015-07-15 10:21:30 by Brian McFee <brian.mcfee@nyu.edu>
'''Namespace management tests'''

from nose.tools import raises
from jams import NamespaceError
import jams


def test_schema_is_dense():

    def __test(ns, dense):
        assert dense == jams.schema.is_dense(ns)

    yield __test, 'pitch_hz', True
    yield __test, 'beat', False
    yield raises(NamespaceError)(__test), 'made up namespace', False
