"""
"""

import unittest

from pyjams.pyjams import _loads
from pyjams.pyjams import _dumps
from pyjams.pyjams import JObject
from pyjams.pyjams import Observation
from pyjams.pyjams import Event
from pyjams.pyjams import Range
from pyjams.pyjams import TimeSeries
from pyjams.pyjams import FileMetadata
from pyjams.pyjams import AnnotationMetadata
from pyjams.pyjams import Curator
from pyjams.pyjams import ObservationAnnotation
from pyjams.pyjams import EventAnnotation
from pyjams.pyjams import RangeAnnotation
from pyjams.pyjams import TimeSeriesAnnotation
from pyjams.pyjams import JAMS


class JamsTests(unittest.TestCase):

    def setUp(self):
        self.jobj = JObject(a=1, b=None, _c='a', d='')
        self.obs = Observation(value='monkey',
                               confidence=1.0,
                               secondary_value=7)

        self.event = Event(time=Observation(0.5, 1.0),
                           label=Observation('dog bark', 0.5))
        self.chord = Range(start=Observation(0.0, 1.0),
                           end=Observation(0.6, 0.8),
                           label=Observation('C:maj', 0.15))
        self.series = TimeSeries(value=[x for x in 'abc'],
                                 time=[0.1, 0.5, 0.9])
        self.curator = Curator(name='J. Doe', email="jdoe@gmail.com")
        self.ameta = AnnotationMetadata(
            curator=self.curator, version='0.0.1', corpus='testing')

        self.obs_annot = ObservationAnnotation(
            data=[self.obs],
            annotation_metadata=self.ameta,
            sandbox=self.jobj)

        self.event_annot = EventAnnotation(data=[self.event])
        self.range_annot = RangeAnnotation(data=[self.chord])
        self.series_annot = TimeSeriesAnnotation(data=[self.series])
        self.fmeta = FileMetadata(
            title='Pachuca Sunrise', artist='Minus the Bear')

    def tearDown(self):
        pass

    def test_JObject_equivalence(self):

        self.assertEqual(self.jobj.a, 1, "Failed to initialize properly.")
        self.assertEqual(self.jobj.b, None, "Failed to initialize properly.")
        self.assertEqual(self.jobj._c, 'a', "Failed to initialize properly.")
        self.assertEqual(self.jobj.d, '', "Failed to initialize properly.")
        self.assertEqual(self.jobj.type, 'JObject', "Failed to encode type.")

        # Equivalence Tests
        self.assertNotEqual(self.jobj, None)
        self.assertNotEqual(self.jobj, dict(a=1))
        self.assertEqual(self.jobj, JObject(a=1))

    def test_JObject_serialization(self):
        # JObjects do not serialize Nones, private vars (_xxx), or empty strs.
        self.assertEqual(
            self.jobj.__json__,
            dict(a=1),
            "Failed to properly serialize.")

        # Verify pass-through loop.
        jobj2 = JObject(**_loads(_dumps(self.jobj)))
        self.assertEqual(
            self.jobj,
            jobj2,
            "Failed to properly recreate the object."
            "Expected: %s\nReceived: %s" % (self.jobj, jobj2))

        self.jobj.e = 1234
        self.assertNotEqual(
            self.jobj,
            jobj2,
            "Assigned attribute failed to propagate."
            "Expected: %s\nReceived: %s" % (self.jobj, jobj2))

    def test_Observation_init(self):
        self.assertEqual(
            self.obs.value,
            'monkey',
            "Failed to initialize 'value' properly.")
        self.assertEqual(
            self.obs.confidence,
            1.0,
            "Failed to initialize 'confidence' properly.")
        self.assertEqual(
            self.obs.secondary_value,
            7,
            "Failed to initialize 'value' properly.")

    def test_Observation_init_none(self):
        obs2 = Observation('monkey', 1.0)
        self.assertEqual(
            obs2.secondary_value,
            None,
            "Failed to initialize 'secondary_value' with None.")

    def test_Observation_serialization(self):
        obs2 = Observation(**_loads(_dumps(self.obs)))
        self.assertEqual(
            self.obs,
            obs2,
            "Failed to properly recreate the object."
            "Expected: %s\nReceived: %s" % (self.obs, obs2))

    def test_Observation_invalid_attr(self):
        obs = Observation()
        with self.assertRaises(ValueError):
            obs.bad_attr = 'some value'

    def test_Event_init(self):
        self.assertEqual(
            self.event.time.value,
            0.5,
            "Failed to initialize 'time.value' properly.")
        self.assertEqual(
            self.event.time.confidence,
            1.0,
            "Failed to initialize 'time.confidence' properly.")
        self.assertEqual(
            self.event.time.secondary_value,
            None,
            "Failed to assign None to 'time.secondary_value'.")
        self.assertEqual(
            self.event.label.value,
            'dog bark',
            "Failed to initialize 'label.value' properly.")
        self.assertEqual(
            self.event.label.confidence,
            0.5,
            "Failed to initialize 'label.confidence' properly.")

    def test_Event_serialization(self):
        event2 = Event(**_loads(_dumps(self.event)))
        self.assertEqual(
            self.event,
            event2,
            "Failed to properly recreate the object."
            "Expected: %s\nReceived: %s" % (self.event, event2))

    def test_Event_invalid_attr(self):
        event = Event()
        with self.assertRaises(ValueError):
            event.bad_attr = 'some value'

    def test_Range_init(self):
        self.assertEqual(
            self.chord.start.value,
            0.0,
            "Failed to initialize 'start.value' properly.")
        self.assertEqual(
            self.chord.end.value,
            0.6,
            "Failed to initialize 'start.value' properly.")
        self.assertEqual(
            self.chord.label.value,
            'C:maj',
            "Failed to initialize 'label.value' properly.")

    def test_Range_serialization(self):
        chord2 = Range(**_loads(_dumps(self.chord)))
        self.assertEqual(
            self.chord,
            chord2,
            "Failed to properly recreate the object."
            "Expected: %s\nReceived: %s" % (self.chord, chord2))

    def test_Range_duration(self):
        expected_duration = 0.6
        self.assertEqual(
            self.chord.duration,
            expected_duration,
            "Failed to compute duration correctly."
            "Expected: %s\nReceived: %s" % (self.chord.duration,
                                            expected_duration))

    def test_Range_inc_monotonic(self):
        # Start / End times should be monotonically increasing.
        with self.assertRaises(ValueError):
            Range(Observation(1.0), Observation(0.0))

    def test_Range_invalid_attr(self):
        arange = Range()
        with self.assertRaises(ValueError):
            arange.bad_attr = 'some value'

    def test_TimeSeries_init(self):
        value = [x for x in 'abc']
        time = [0.1, 0.5, 0.9]
        self.assertEqual(
            self.series.value,
            value,
            "Failed to initialize 'value' properly.")
        self.assertEqual(
            self.series.time,
            time,
            "Failed to initialize 'start.value' properly.")
        self.assertEqual(
            self.series.confidence,
            [],
            "Failed to initialize 'label.value' properly.")

    def test_TimeSeries_serialization(self):
        series2 = TimeSeries(**_loads(_dumps(self.series)))
        self.assertEqual(
            self.series,
            series2,
            "Failed to properly recreate the object."
            "Expected: %s\nReceived: %s" % (self.series, series2))

    def test_TimeSeries_observation_lengths_match(self):
        # Lists of different lengths should raise a ValueError.
        self.assertRaises(
            ValueError,
            TimeSeries,
            range(3),
            range(2))

    def test_TimeSeries_invalid_attr(self):
        tseries = TimeSeries()
        with self.assertRaises(ValueError):
            tseries.bad_attr = 'some value'

    def test_ObservationAnnotation_init(self):
        self.assertEqual(
            self.obs_annot.data,
            [self.obs],
            "Failed to initialize 'data' properly.")
        self.assertEqual(
            self.obs_annot.annotation_metadata,
            self.ameta,
            "Failed to initialize 'annotation_metadata' properly.")
        self.assertEqual(
            self.obs_annot.sandbox.__json__,
            {'a': 1},
            "Failed to initialize 'sandbox' properly. ")

    def test_ObservationAnnotation_serialization(self):
        # Test that Annotations can be deserialized without a class wrapper.
        annot2 = _loads(_dumps(self.obs_annot))
        self.assertEqual(
            self.obs_annot,
            annot2,
            "Failed to properly recreate the object."
            "Expected: %s\nReceived: %s" % (self.obs_annot, annot2))

    def test_ObservationAnnotation_factory(self):
        # Verify persistence of objects created via the factory method.
        exp_value = 'testing'
        obs2 = self.obs_annot.create_datapoint()
        obs2.value = exp_value
        self.assertEqual(
            self.obs_annot.data[1].value,
            exp_value,
            "Failed to maintain a handle of the factory-created datapoint."
            "Expected: %s\nReceived: %s" % (exp_value,
                                            self.obs_annot.data[1].value))

    def test_ObservationAnnotation_datatype_validation(self):
        # Annotations should fail if the data types are not Observations.
        self.assertRaises(
            TypeError,
            ObservationAnnotation,
            [self.event])

        self.assertRaises(
            TypeError,
            ObservationAnnotation,
            [self.chord])

        self.assertRaises(
            TypeError,
            ObservationAnnotation,
            [self.series])

    def test_ObservationAnnotation_invalid_attr(self):
        annot = ObservationAnnotation()
        with self.assertRaises(ValueError):
            annot.bad_attr = 'some value'

    def test_EventAnnotation_init(self):
        self.assertEqual(
            self.event_annot.data,
            [self.event],
            "Failed to initialize 'data' properly.")

    def test_EventAnnotation_serialization(self):
        # Test that Annotations can be deserialized without a class wrapper.
        annot2 = _loads(_dumps(self.event_annot))
        self.assertEqual(
            self.event_annot,
            annot2,
            "Failed to properly recreate the object."
            "Expected: %s\nReceived: %s" % (self.event_annot, annot2))

    def test_EventAnnotation_factory(self):
        # Verify persistence of objects created via the factory method.
        event2 = self.event_annot.create_datapoint()
        event2.label = self.event.label
        event2.time = self.event.time

        self.assertEqual(
            self.event_annot.data[1],
            self.event,
            "Failed to maintain a handle of the factory-created datapoint. "
            "Expected: %s\nReceived: %s" % (self.event,
                                            self.event_annot.data[1]))
        del self.event_annot.data[1]

    def test_EventAnnotation_datatype_validation(self):
        # Annotations should fail if the data types are not Events.
        self.assertRaises(
            TypeError,
            EventAnnotation,
            [Observation(1.0)])

        self.assertRaises(
            TypeError,
            EventAnnotation,
            [Range(Observation(1.0))])

        self.assertRaises(
            TypeError,
            EventAnnotation,
            [TimeSeries(range(10))])

    def test_EventAnnotation_labels(self):
        # Populate
        expected_labels = Observation(
            value=['dog bark'],
            confidence=[0.5],
            secondary_value=[None])
        self.assertEqual(
            self.event_annot.labels,
            expected_labels,
            "Failed to collect all label fields properly.\n"
            "Expected:\n%s\nReceived:\n%s" % (expected_labels,
                                              self.event_annot.labels))

    def test_EventAnnotation_times(self):
        expected_times = Observation(
            value=[0.5],
            confidence=[1.0],
            secondary_value=[None])
        self.assertEqual(
            self.event_annot.times,
            expected_times,
            "Failed to collect all label fields properly. \n"
            "Expected:\n%s\nReceived:\n%s" % (expected_times,
                                              self.event_annot.times))

    def test_EventAnnotation_invalid_attr(self):
        annot = EventAnnotation()
        with self.assertRaises(ValueError):
            annot.bad_attr = 'some value'

    def test_RangeAnnotation_init(self):
        self.assertEqual(
            self.range_annot.data,
            [self.chord],
            "Failed to initialize 'data' properly.")

    def test_RangeAnnotation_serialization(self):
        # Test that Annotations can be deserialized without a class wrapper.
        annot2 = _loads(_dumps(self.range_annot))
        self.assertEqual(
            self.range_annot,
            annot2,
            "Failed to properly recreate the object."
            "Expected:\n%s\nReceived:\n%s" % (self.range_annot, annot2))

    def test_RangeAnnotation_factory(self):
        # Verify persistence of objects created via the factory method.
        chord2 = self.range_annot.create_datapoint()
        chord2.label.value = 'blah blah'
        self.assertEqual(
            chord2.label.value,
            self.range_annot.data[1].label.value,
            "Failed to maintain a handle of the factory-created datapoint. "
            "Expected:\n%s\nReceived:\n%s" % (
                chord2.label.value, self.range_annot.data[1].label.value))
        self.range_annot.data = self.range_annot.data[:1]

    def test_RangeAnnotation_datatype_validation(self):
        # Annotations should fail if the data types are not Events.
        self.assertRaises(
            TypeError,
            RangeAnnotation,
            [Observation(1.0)])

        self.assertRaises(
            TypeError,
            RangeAnnotation,
            [Event(Observation(1.0))])

        self.assertRaises(
            TypeError,
            RangeAnnotation,
            [TimeSeries(range(10))])

    def test_RangeAnnotation_labels(self):
        # Populate
        expected_labels = Observation(
            value=['C:maj'],
            confidence=[0.15],
            secondary_value=[None])
        self.assertEqual(
            self.range_annot.labels,
            expected_labels,
            "Failed to collect all label fields properly. "
            "Expected: %s\nReceived: %s" % (expected_labels,
                                            self.range_annot.labels))

    def test_RangeAnnotation_starts(self):
        expected_starts = Observation(
            value=[0.0],
            confidence=[1.0],
            secondary_value=[None])
        self.assertEqual(
            self.range_annot.starts,
            expected_starts,
            "Failed to collect all start fields properly. "
            "Expected: %s\nReceived: %s" % (expected_starts,
                                            self.range_annot.starts))

    def test_RangeAnnotation_ends(self):
        expected_ends = Observation(
            value=[0.6],
            confidence=[0.8],
            secondary_value=[None])
        self.assertEqual(
            self.range_annot.ends,
            expected_ends,
            "Failed to collect all end fields properly. "
            "Expected: %s\nReceived: %s" % (expected_ends,
                                            self.range_annot.ends))

    def test_RangeAnnotation_intervals(self):
        expected_intervals = [(0.0, 0.6)]
        self.assertEqual(
            self.range_annot.intervals,
            expected_intervals,
            "Failed to collect all start fields properly. "
            "Expected: %s\nReceived: %s" % (expected_intervals,
                                            self.range_annot.intervals))

    def test_RangeAnnotation_invalid_attr(self):
        annot = RangeAnnotation()
        with self.assertRaises(ValueError):
            annot.bad_attr = 'some value'

    def test_TimeSeriesAnnotation_init(self):
        self.assertEqual(
            self.series_annot.data,
            [self.series],
            "Failed to initialize 'data' properly.")

    def test_TimeSeriesAnnotation_serialization(self):
        """Verify XAnnotation can be deserialized without a class wrapper."""
        annot2 = _loads(_dumps(self.series_annot))
        self.assertEqual(
            self.series_annot,
            annot2,
            "Failed to properly recreate the object."
            "Expected: %s\nReceived: %s" % (self.series_annot, annot2))

    def test_TimeSeriesAnnotation_factory(self):
        """Verify persistence of objects created via the factory method."""
        series = self.series_annot.create_datapoint()
        series.value = range(5)
        self.assertEqual(
            self.series_annot.data[-1].value,
            range(5),
            "Failed to maintain a handle of the factory-created datapoint. "
            "Expected: %s\nReceived: %s" % (range(5),
                                            self.series_annot.data[-1].value))

    def test_TimeSeriesAnnotation_datatype_validation(self):
        """Annotations should fail if the data types are not TimeSeries."""
        self.assertRaises(
            TypeError,
            TimeSeriesAnnotation,
            [Observation(1.0)])

        self.assertRaises(
            TypeError,
            TimeSeriesAnnotation,
            [Event(Observation(1.0))])

        self.assertRaises(
            TypeError,
            TimeSeriesAnnotation,
            [Range(Observation(1.0))])

    def test_TimeSeriesAnnotation_invalid_attr(self):
        annot = TimeSeriesAnnotation()
        with self.assertRaises(ValueError):
            annot.bad_attr = 'some value'

    def test_JAMS_invalid_attr(self):
        jam = JAMS()
        with self.assertRaises(ValueError):
            jam.bad_attr = 'some value'


if __name__ == "__main__":
    unittest.main()
