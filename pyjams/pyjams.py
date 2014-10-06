"""JAMS Python API

This library provides an interface for reading JAMS into Python, or creating
them programatically.


1. Creating a JAMS data structure from scratch
----------------------------------------------
First, create the top-level JAMS container:

  >>> import pyjams
  >>> jam = pyjams.JAMS()

 Now we can create a beat annotation:

  >>> annot = jam.beat.create_annotation()
  >>> beat = annot.create_datapoint()
  >>> beat.time.value = 0.33
  >>> beat.time.confidence = 1.0
  >>> beat.label.value = "1"
  >>> beat.label.confidence = 0.75


Then, we'll update the annotation's metadata by directly setting its fields:

  >>> annot.annotation_metadata.data_source = "Poorly paid students"
  >>> annot.annotation_metadata.curator.name = "My Name"
  >>> annot.annotation_metadata.curator.email = "somebody@aol.com"


And now a second time, cause this is our house (and we can do what we want):

  >>> beat2 = annot.create_datapoint()
  >>> beat2.label.value = "second beat"


Once you've added all your data, you can serialize the annotation to a file
with the built-in `json` library:

  >>> import json
  >>> with open("these_are_my.jams", 'w') as fp:
          json.dump(annot, fp, indent=2)

Or, less verbosely, using the built-in save function:

  >>> pyjams.save(annot, "these_are_still_my.jams")


2. Reading a Jams file
----------------------
Assuming you already have a JAMS file on-disk, say at 'these_are_also_my.jams',
you can easily read it back into memory:

  >>> another_annot = pyjams.load('these_are_also_my.jams')


And that's it!

  >>> print annot2
"""

__VERSION__ = "0.0.1"
__OBJECT_TYPE__ = 'object_type'

import json


def load(filepath):
    """Load a JAMS Annotation from a file."""
    return JAMS(**json.load(open(filepath, 'r')))


def save(jam, filepath):
    """Serialize annotation as a JSON formatted stream to file."""
    with open(filepath, 'w') as fp:
        json.dump(jam, fp, indent=2)


def append(jam, filepath, new_filepath=None, on_conflict='fail'):
    """Append the contents of one JAMS file to another.

    Parameters
    ----------
    jam: JAMS object
        Annotation object to write.
    filepath: str
        Jams file the object should be added to.
    new_filepath: str
        Optional output file for non-destructive append operations.
    on_conflict: str, default='fail'
        Strategy for resolving metadata conflicts; one of:
                ['fail', 'overwrite', 'ignore'].
    """
    old_jam = load(filepath)
    old_jam.add(jam, on_conflict=on_conflict)
    if new_filepath is None:
        new_filepath = filepath
    save(old_jam, new_filepath)


class JObject(object):
    """Dict-like object for JSON Serialization.

    This object behaves like a dictionary to allow init-level attribute names,
    seamless JSON-serialization, and double-star style unpacking (**obj).
    """
    def __init__(self, **kwargs):
        object.__init__(self)
        for name, value in kwargs.iteritems():
            self.__dict__[name] = value

    @property
    def __json__(self):
        """TODO(ejhumphrey@nyu.edu): writeme."""
        filtered_dict = dict()
        for k, v in self.__dict__.iteritems():
            if v in [None, '', list(), dict()] or k.startswith('_'):
                continue
            filtered_dict[k] = v
        return filtered_dict

    @classmethod
    def __json_init__(cls, **kwargs):
        """TODO(ejhumphrey@nyu.edu): writeme."""
        return cls(**kwargs)

    def __eq__(self, y):
        """Test for equality between two objects.

        Uses the following logic:
        1. If the class types are equal, the serialized objects are compared;
        2. If the compared object is a dict, the serialized object is compared;
        3. False
        """
        if isinstance(y, dict):
            return self.__json__ == y
        elif isinstance(y, self.__class__):
            return self.__json__ == y.__json__
        return False

    def __nonzero__(self):
        return bool(self.__json__)

    def __getitem__(self, key):
        """TODO(ejhumphrey@nyu.edu): writeme."""
        return self.__dict__[key]

    def __len__(self):
        return len(self.keys())

    def __repr__(self):
        """Render the object alongside its attributes."""
        # data = ", ".join(["%s=%s" % (k, self[k]) for k in self.keys()])
        return '<%s: %s>' % (self.type, ", ".join(self.keys()))

    def __str__(self):
        return json.dumps(self, indent=2)

    def keys(self):
        """TODO(ejhumphrey@nyu.edu): writeme."""
        return self.__dict__.keys()

    def update(self, **kwargs):
        for name, value in kwargs.iteritems():
            self.__dict__[name] = value

    @property
    def type(self):
        return self.__class__.__name__


class Observation(JObject):
    """Observation

    Smallest observable concept (value) with a confidence interval. Used for
    almost anything, from observed times to semantic tags.
    """
    def __init__(self, value=None, confidence=None, secondary_value=None):
        """Create an Observation.

        Parameters
        ----------
        value: obj, default=None
            The conceptual value for this observation.
        confidence: float, default=None
            Degree of confidence for the value, in the range [0, 1].
        secondary_value: obj, default=None
        """
        self.value = value
        self.confidence = confidence
        self.secondary_value = secondary_value


class Event(Observation):
    """Event (Sparse)

    Instantaneous time event, consisting of two Observations (time and label).
    Used for such ideas like beats or onsets.
    """
    def __init__(self, time=None, label=None):
        """Create an Event.

        Note that, if an argument is None, an empty Observation is created in
        its place. Additionally, a dictionary matching the expected structure
        of the arguments will be parsed successfully (i.e. instantiating from
        JSON).

        Parameters
        ----------
        time: Observation (or dict), default=None
            A time Observation for this event.
        label: Observation (or dict), default=None
            A semantic concept for this event, as an Observation.
        """
        if time is None:
            time = Observation()
        if label is None:
            label = Observation()
        self.time = Observation(**time)
        self.label = Observation(**label)


class Range(Observation):
    """Range

    An observed time interval, composed of three Observations (start, end, and
    label). Used for such concepts as chords.
    """
    def __init__(self, start=None, end=None, label=None):
        """Create a Range.

        Note that, if an argument is None, an empty Observation is created in
        its place. Additionally, a dictionary matching the expected structure
        of the arguments will be parsed successfully (i.e. instantiating from
        JSON).

        Parameters
        ----------
        start: Observation (or dict)
            The observed start time of the range.
        end: Observation (or dict)
            The observed end time of the range.
        label: Observation (or dict)
            Label over this time interval.
        """
        # input checks
        start = Observation() if start is None else start
        end = Observation() if end is None else end
        label = Observation() if label is None else label

        self.start = Observation(**start)
        self.end = Observation(**end)
        self.label = Observation(**label)
        if not self.duration is None and self.duration < 0:
            raise ValueError(
                "end.value (%s) < start.value (%s)" % (self.end.value,
                                                       self.start.value))

    @property
    def duration(self):
        if None in (self.end.value, self.start.value):
            return None
        return self.end.value - self.start.value


class TimeSeries(Observation):
    """Sampled Time Series Observation

    This could be an array, and skip the value abstraction. However,
    some abstraction could help turn data into numpy arrays on the fly.

    However, np.ndarrays are not directly serializable. It might be necessary
    to subclass np.ndarray and change __repr__.
    """
    def __init__(self, value=None, time=None, confidence=None):
        """Create a TimeSeries.

        Note that, if an argument is None, empty lists are created in
        its place. Additionally, a dictionary matching the expected structure
        of the arguments will be parsed successfully (i.e. instantiating from
        JSON).

        Parameters
        ----------
        value: list or serializable array
            Values for this time-series.
        time: list or serializable 1D-array
            Times corresponding to the value series.
        confidence: list or serializable 1D-array
            Confidence values corresponding to the value series.
        """
        # input checks
        value = list() if value is None else value
        time = list() if time is None else time
        confidence = list() if confidence is None else confidence

        # Validation -- could possibly be a private method to call when fields
        #   change, but properties / setters break the JSON serialization.
        lengths = list()
        for x in (value, time, confidence):
            if x:
                lengths.append(len(x))
        if lengths and len(set(lengths)) > 1:
            raise ValueError("All initialized lists must be the same length.")

        self.value = value
        self.time = time
        self.confidence = confidence


class BaseAnnotation(JObject):
    """Annotation base class.

    Default Type: None

    Be aware that Annotations define a '_DefaultType' class variable,
    specifying the kind of objects contained in its 'data' attribute. Therefore
    any subclass will need to set this accordingly.
    """
    _DefaultType = None

    def __init__(self, data=None, annotation_metadata=None, sandbox=None):
        """Create an Annotation.

        Note that, if an argument is None, an empty Annotation is created in
        its place. Additionally, a dictionary matching the expected structure
        of the arguments will be parsed (i.e. instantiating from JSON).

        Parameters
        ----------
        data: list, or None
            Collection of Observations
        annotation_metadata: AnnotationMetadata (or dict), default=None.
            Metadata corresponding to this Annotation.
        sandbox: dict
            Miscellaneous information; keep to native datatypes if possible.
        """
        # TODO(ejhumphrey@nyu.edu): We may want to subclass list here to turn
        #   'data' into a special container with convenience methods to more
        #   easily unpack sparse events, among other things.
        if data is None:
            data = list()
        if annotation_metadata is None:
            annotation_metadata = AnnotationMetadata()
        if sandbox is None:
            sandbox = JObject()

        self.annotation_metadata = AnnotationMetadata(**annotation_metadata)
        self.data = self.__parse_data__(data)
        self.sandbox = JObject(**sandbox)

    def __parse_data__(self, data):
        """This method unpacks data as a specific type of objects, defined by
        the self._DefaultType, for the purposes of safely creating a list of
        properly initialized objects.

        Parameters
        ----------
        data: list
            Collection of dicts or _DefaultTypes.

        Returns
        -------
        objects: list
            Collection of _DefaultTypes.
        """
        return [self._DefaultType(**obj) for obj in data]

    def create_datapoint(self):
        """Factory method to create an empty Data object based on this type of
        Annotation, adding it to the data list and returning a reference.

        Returns
        -------
        obj: self._DefaultType
            An empty object, whose type is determined by the Annotation type.
        """
        self.data.append(self._DefaultType())
        return self.data[-1]


class ObservationAnnotation(BaseAnnotation):
    """Observation Annotation

    Default Type: Observation

    Be aware that Annotations define a '_DefaultType' class variable,
    specifying the kind of objects contained in its 'data' attribute. Therefore
    any subclass will need to set this accordingly."""
    _DefaultType = Observation


class EventAnnotation(BaseAnnotation):
    """Event Annotation

    Default Type: Event

    Be aware that Annotations define a '_DefaultType' class variable,
    specifying the kind of objects contained in its 'data' attribute. Therefore
    any subclass will need to set this accordingly."""
    _DefaultType = Event

    @property
    def labels(self):
        """All labels in the annotation, as a single object.

        Returns
        -------
        labels: JObject
            Object with the label fields (value, confidence, secondary_label)
            as lists, in order over the annotation.
        """
        kwargs = dict([(k, [obj.label[k] for obj in self.data])
                       for k in self._DefaultType().label.keys()])
        return Observation(**kwargs)

    @property
    def times(self):
        """All times in the annotation, as a single object.

        Returns
        -------
        times: JObject
            Object with the time fields (value, confidence, secondary_label)
            as lists, in order over the annotation.
        """
        kwargs = dict([(k, [obj.time[k] for obj in self.data])
                       for k in self._DefaultType().time.keys()])
        return Observation(**kwargs)


class TimeSeriesAnnotation(BaseAnnotation):
    """TimeSeries Annotation

    Default Type: TimeSeries

    Be aware that Annotations define a '_DefaultType' class variable,
    specifying the kind of objects contained in its 'data' attribute. Therefore
    any subclass will need to set this accordingly."""
    _DefaultType = TimeSeries


class RangeAnnotation(BaseAnnotation):
    """Range Annotation

    Default Type: Range

    Be aware that Annotations define a '_DefaultType' class variable,
    specifying the kind of objects contained in its 'data' attribute. Therefore
    any subclass will need to set this accordingly."""
    _DefaultType = Range

    @property
    def labels(self):
        """All labels in the annotation, as a single object.

        Returns
        -------
        labels: JObject
            Object with the label fields (value, confidence, secondary_label)
            as lists, in order over the annotation.
        """
        kwargs = dict([(k, [obj.label[k] for obj in self.data])
                       for k in self._DefaultType().label.keys()])
        return Observation(**kwargs)

    @property
    def starts(self):
        """All start times in the annotation, as a single object.

        Returns
        -------
        start_times: JObject
            Object with the start fields (value, confidence, secondary_label)
            as lists, in order over the annotation.
        """
        kwargs = dict([(k, [obj.start[k] for obj in self.data])
                       for k in self._DefaultType().start.keys()])
        return Observation(**kwargs)

    @property
    def ends(self):
        """All end times in the annotation, as a single Observation.

        Returns
        -------
        end_times: Observation
            Object with the end fields (value, confidence, secondary_label)
            as lists, in order over the annotation.
        """
        kwargs = dict([(k, [obj.end[k] for obj in self.data])
                      for k in self._DefaultType().end.keys()])
        return Observation(**kwargs)

    @property
    def intervals(self):
        """All start and end times in the annotation.

        Returns
        -------
        intervals: list of tuples
            Ordered collection of (start.value, end.value) pairs
        """
        return [(obj.start.value, obj.end.value) for obj in self.data]


class Curator(JObject):
    """Curator

    Container object for curator metadata.
    """
    def __init__(self, name='', email=''):
        """Create an Curator.

        Parameters
        ----------
        name: str, default=''
            Common name of the curator.
        email: str, default=''
            An email address corresponding to the curator.
        """
        self.name = name
        self.email = email


class AnnotationMetadata(JObject):
    """AnnotationMetadata

    Data structure for metadata corresponding to a specific annotation.
    """
    def __init__(self, curator=None, version='', corpus='', annotator=None,
                 annotation_tools='', annotation_rules='', validation='',
                 data_source=''):
        """Create an AnnotationMetadata object.

        Parameters
        ----------
        curator: Curator, default=None
            Object documenting a name and email address for the person of
            correspondence.
        version: string, default=''
            Version of this annotation.
        annotator: dict, default=None
            Sandbox for information about the specific annotator, such as
            musical experience, skill level, principal instrument, etc.
        corpus: str, default=''
            Collection assignment.
        annotation_tools: str, default=''
            Description of the tools used to create the annotation.
        annotation_rules: str, default=''
            Description of the rules provided to the annotator.
        validation: str, default=''
            Methods for validating the integrity of the data.
        data_source: str, default=''
            Description of where the data originated, e.g. 'Manual Annotation'.
        """
        curator = JObject() if curator is None else curator
        annotator = JObject() if annotator is None else annotator

        self.curator = Curator(**curator)
        self.version = version
        self.corpus = corpus
        self.annotator = JObject(**annotator)
        self.annotation_tools = annotation_tools
        self.annotation_rules = annotation_rules
        self.validation = validation
        self.data_source = data_source


class FileMetadata(JObject):
    """Metadata for a given audio file."""
    def __init__(self, title='', artist='', release='', duration='',
                 identifiers=None, jams_version=None):
        """Create a file-level Metadata object.

        Parameters
        ----------
        title: str
            Name of the recording.
        artist: str
            Name of the artist / musician.
        md5: str
            MD5 hash of the corresponding file.
        duration: str
            Time duration of the file, as HH:MM:SS.
        echonest_id: str
            Echonest ID for this track.
        mbid: str
            MusicBrainz ID for this track.
        version: str, or default=None
            Version of the JAMS Schema.
        """
        jams_version = __VERSION__ if jams_version is None else jams_version
        identifiers = JObject() if identifiers is None else identifiers

        self.title = title
        self.artist = artist
        self.release = release
        self.duration = duration
        self.identifiers = JObject(**identifiers)
        self.jams_version = jams_version


class AnnotationList(list):
    """AnnotationList

    List subclass for managing collections of annotations, providing factory
    methods to create empty annotations.
    """
    def __init__(self, annotations, AnnotationType):
        """Create an AnnotationList.

        Parameters
        ----------
        annotations: list
            List of XAnnotations, or appropriately formated dicts, where X
            is consistent with AnnotationType.
        AnnotationType: class
            XAnnotation to use as the default type, where X in
                [Observation, Event, Range, TimeSeries]
        """
        if annotations is None:
            annotations = list()

        self._DefaultType = AnnotationType
        self.extend([self._DefaultType(**obj) for obj in annotations])

    def create_annotation(self):
        """Create an empty XAnnotation based on the annotation type provided
        on init, adding it to the annotation list and returning a reference to
        the new annotation object.

        Returns
        -------
        obj: AnnotationType
            An empty annotation, whose type is determined by self._DefaultType.
        """
        self.append(self._DefaultType())
        return self[-1]


class JAMS(JObject):
    """Top-level Jams Object"""

    def __init__(self, beat=None, chord=None, genre=None, key=None, mood=None,
                 melody=None, note=None, onset=None, pattern=None, pitch=None,
                 segment=None, source=None, tag=None, file_metadata=None,
                 sandbox=None):
        """Create a Jams object.

        Parameters
        ----------
        beat: list of EventAnnotations
            Used for beat-tracking.
        chord: list of RangeAnnotations
            Used for chord recognition.
        melody: list of TimeSeriesAnnotations
            Used for continuous-f0 melody.
        segment: list of RangeAnnotations
            Used for music segmentation.
        tag: list of Annotations
            Used for music tagging and semantic descriptors.
        file_metadata: FileMetadata
            Metadata corresponding to the audio file.
        """

        if file_metadata is None:
            file_metadata = FileMetadata()

        if sandbox is None:
            sandbox = JObject()

        self.beat = AnnotationList(
            [] if beat is None else beat, EventAnnotation)
        self.chord = AnnotationList(
            [] if chord is None else chord, RangeAnnotation)
        self.genre = AnnotationList(
            [] if genre is None else genre, ObservationAnnotation)
        self.key = AnnotationList(
            [] if key is None else key, RangeAnnotation)
        self.melody = AnnotationList(
            [] if melody is None else melody, TimeSeriesAnnotation)
        self.mood = AnnotationList(
            [] if mood is None else mood, ObservationAnnotation)
        self.note = AnnotationList(
            [] if note is None else note, RangeAnnotation)
        self.onset = AnnotationList(
            [] if onset is None else onset, EventAnnotation)
        self.pattern = AnnotationList(
            [] if pattern is None else pattern, TimeSeriesAnnotation)
        self.pitch = AnnotationList(
            [] if pitch is None else pitch, TimeSeriesAnnotation)
        self.segment = AnnotationList(
            [] if segment is None else segment, RangeAnnotation)
        self.source = AnnotationList(
            [] if source is None else source, RangeAnnotation)
        self.tag = AnnotationList(
            [] if tag is None else tag, ObservationAnnotation)
        self.file_metadata = FileMetadata(**file_metadata)
        self.sandbox = JObject(**sandbox)

    def add(self, jam, on_conflict='fail'):
        """Add the contents of another jam to this object.

        Note that, by default, this method fails if file_metadata is not
        identical and raises a ValueError; either resolve this manually
        (because conflicts should almost never happen), force an 'overwrite',
        or tell the method to 'ignore' the metadata of the object being added.

        Parameters
        ----------
        jam: JAMS object
            Object to add to this jam
        on_conflict: str, default='fail'
            Strategy for resolving metadata conflicts; one of
                ['fail', 'overwrite', or 'ignore'].
        """
        equal_metadata = self.file_metadata == jam.file_metadata
        if on_conflict == 'overwrite':
            self.file_metadata = jam.file_metadata
        elif on_conflict == 'fail' and not equal_metadata:
            raise ValueError("Metadata conflict! "
                             "Resolve manually or force-overwrite it.")
        elif on_conflict == 'ignore':
            pass
        else:
            raise ValueError("on_conflict received '%s'. Must be one of "
                             "['fail', 'overwrite', 'ignore']." % on_conflict)

        self.beat.extend(jam.beat)
        self.chord.extend(jam.chord)
        self.key.extend(jam.key)
        self.melody.extend(jam.melody)
        self.note.extend(jam.note)
        self.pitch.extend(jam.pitch)
        self.segment.extend(jam.segment)
        self.source.extend(jam.source)
        self.tag.extend(jam.tag)
        self.sandbox.update(**jam.sandbox)


# Private functionality
# -- Used internally / for testing purposes --
def __jams_serialization__():
    """writeme."""
    def encode(self, jams_obj):
        """writeme."""
        return jams_obj.__json__

    def decode(obj):
        """writeme."""
        if __OBJECT_TYPE__ in obj:
            return eval(obj.pop(__OBJECT_TYPE__)).__json_init__(**obj)
        return obj

    json.JSONEncoder.default = encode
    json._default_decoder = json.JSONDecoder(object_hook=decode)


__jams_serialization__()


def _loads(*args, **kwargs):
    """Alias of json.loads()"""
    return json.loads(*args, **kwargs)


def _dumps(*args, **kwargs):
    """Alias of json.dumps()"""
    return json.dumps(*args, **kwargs)
