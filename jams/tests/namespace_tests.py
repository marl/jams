#!/usr/bin/env python
#CREATED:2015-05-26 12:47:35 by Brian McFee <brian.mcfee@nyu.edu>
"""Namespace schema tests"""

import numpy as np

from nose.tools import eq_, raises
from jsonschema import ValidationError
import six

import jams


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
