#!/usr/bin/env python
#CREATED:2015-05-26 12:47:35 by Brian McFee <brian.mcfee@nyu.edu>
"""Namespace schema tests"""

import numpy as np

from nose.tools import eq_, raises
from jsonschema import ValidationError
import six

import jams


def test_ns_time_valid():

    ann = jams.Annotation(namespace='beat')

    for time in np.arange(5.0, 10.0):
        ann.append(time=time, duration=0.0, value=None, confidence=None)

    ann.validate()


def test_ns_time_invalid():

    @raises(ValidationError)
    def __test(data):
        ann = jams.Annotation(namespace='beat')
        ann.append(**data)

        print ann
        ann.validate()

    # Check bad time
    yield __test, dict(time=-1, duration=0)

    # Check bad duration
    yield __test, dict(time=1, duration=-1)

def test_ns_beat_valid():

    # A valid example
    ann = jams.Annotation(namespace='beat')
    
    for time in np.arange(5.0):
        ann.append(time=time, duration=0.0, value=1, confidence=None)

    for time in np.arange(5.0, 10.0):
        ann.append(time=time, duration=0.0, value=None, confidence=None)
    
    ann.validate()


@raises(ValidationError)
def test_ns_beat_invalid():

    ann = jams.Annotation(namespace='beat')
    
    for time in np.arange(5.0):
        ann.append(time=time, duration=0.0, value='foo', confidence=None)

    ann.validate()


def test_ns_beat_position_valid():

    ann = jams.Annotation(namespace='beat_position')

    ann.append(time=0, duration=1.0, value=dict(position=1,
                                                measure=1,
                                                num_beats=3,
                                                beat_units=4))
    
    ann.validate()


def test_ns_beat_position_invalid():

    @raises(ValidationError)
    def __test(value):
        ann = jams.Annotation(namespace='beat_position')
        ann.append(time=0, duration=1.0, value=value)
        ann.validate()

    good_dict = dict(position=1, measure=1, num_beats=3, beat_units=4)

    # First, test the bad positions
    for pos in [-1, 0, 'a', None]:
        value = good_dict.copy()
        value['position'] = pos
        yield __test, value

    # Now test bad measures
    for measure in [-1, 1.0, 'a', None]:
        value = good_dict.copy()
        value['measure'] = measure
        yield __test, value

    # Now test bad num_beats
    for nb in [-1, 1.5, 'a', None]:
        value = good_dict.copy()
        value['num_beats'] = nb
        yield __test, value

    # Now test bad beat units
    for bu in [-1, 1.5, 3, 'a', None]:
        value = good_dict.copy()
        value['beat_units'] = bu
        yield __test, value

    # And test missing fields
    for field in good_dict.keys():
        value = good_dict.copy()
        del value[field]
        yield __test, value

