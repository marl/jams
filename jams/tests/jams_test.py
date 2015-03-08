#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# CREATED:2015-03-06 14:24:58 by Brian McFee <brian.mcfee@nyu.edu>
'''Unit tests for JAMS core objects'''

import json
from nose.tools import raises, eq_

import jams


def test_jobject_dict():

    data = dict(key1='value 1', key2='value 2')

    J = jams.JObject(**data)

    jdict = J.__dict__

    eq_(data, jdict)


def test_jobject_serialize():

    data = dict(key1='value 1', key2='value 2')

    json_data = json.dumps(data, indent=2)

    J = jams.JObject(**data)

    json_jobject = J.dumps(indent=2)

    eq_(json_data, json_jobject)


def test_jobject_deserialize():

    data = dict(key1='value 1', key2='value 2')

    json_data = json.dumps(data, indent=2)

    J = jams.JObject.loads(json_data)

    json_jobject = J.dumps(indent=2)

    eq_(json_data, json_jobject)


def test_jobject_eq():

    def __test(d1, d2, match):

        J1 = jams.JObject(**d1)
        J2 = jams.JObject(**d2)

        # Test self-equivalence
        assert J1 == J1
        assert J2 == J2

        # Test equivalence in both directions
        assert (J1 == J2) == match
        assert (J2 == J1) == match

    data_1 = dict(key1='value 1', key2='value 2')
    data_2 = dict(key1='value 1', key2='value 2')
    data_3 = dict(key1='value 1', key2='value 3')

    yield __test, data_1, data_1, True
    yield __test, data_1, data_2, True
    yield __test, data_1, data_3, False

