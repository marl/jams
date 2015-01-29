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
  >>> annot.append(time=0.33,
                   duration=0.0,
                   confidence=1.0,
                   value="1")


Then, we'll update the annotation's metadata by directly setting its fields:

  >>> annot.annotation_metadata.data_source = "Poorly paid students"
  >>> annot.annotation_metadata.curator.name = "My Name"
  >>> annot.annotation_metadata.curator.email = "somebody@aol.com"


And now a second time, cause this is our house (and we can do what we want):

  >>> annot.append(time=0.66,
                   duration=0.0,
                   confidence=1.0,
                   value="1")


Once you've added all your data, you can serialize the annotation to a file
with the built-in `json` library:

  >>> import json
  >>> with open("these_are_my.jams", 'w') as fp:
          json.dump(jam, fp, indent=2)

Or, less verbosely, using the built-in save function:

  >>> pyjams.save(jam, "these_are_still_my.jams")


2. Reading a Jams file
----------------------
Assuming you already have a JAMS file on-disk, say at 'these_are_also_my.jams',
you can easily read it back into memory:

  >>> another_jam = pyjams.load('these_are_also_my.jams')


And that's it!

  >>> print annot2
"""

import json
import numpy as np
import pandas as pd
import os

from . import util
from .version import version as __VERSION__

__OBJECT_TYPE__ = 'object_type'

# TODO: This is super fragile; migrate toward pkg_resources.
__SCHEMA__ = json.load(open(os.path.join(os.path.split(__file__)[0],
                                         '../schema/jams_schema.json')))


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
            setattr(self, name, value)

    @property
    def __schema__(self):
        # TODO(ejhumphrey): Disabled schema enforcement.
#         return
        return __SCHEMA__['definitions'].get(self.type, None)

    @property
    def __json__(self):
        """Return the object as a set of native datatypes for serialization.

        Note: Empty strings / lists / dicts, None, and attributes beginning
        with underscores are suppressed.
        """
        filtered_dict = dict()
        for k, v in self.__dict__.iteritems():
            if isinstance(v, pd.DataFrame):
                filtered_dict[k] = v
            elif v in [None, '', list(), dict()] or k.startswith('_'):
                continue
            else:
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

    def __setattr__(self, name, value):
        if self.__schema__ is not None:
            props = self.__schema__['properties']
            if name not in props:
                raise ValueError(
                    "Invalid attribute: %s\n"
                    "\t Should be one of %s." % (name, props.keys()))
        self.__dict__[name] = value

    def __len__(self):
        return len(self.keys())

    def __repr__(self):
        """Render the object alongside its attributes."""
        # data = ", ".join(["%s=%s" % (k, self[k]) for k in self.keys()])
        return '<%s: %s>' % (self.type, ", ".join(self.keys()))

    def __str__(self):
        return json.dumps(self, indent=2)

    def keys(self):
        """Return the fields of the object."""
        return self.__dict__.keys()

    def update(self, **kwargs):
        for name, value in kwargs.iteritems():
            setattr(self, name, value)

    @property
    def type(self):
        return self.__class__.__name__

    @classmethod
    def loads(cls, s):
        return cls.__json_init__(**json.loads(s))

    def dumps(self, *args, **kwargs):
        return json.dumps(self, *args, **kwargs)


class Sandbox(JObject):
    """Sandbox (unconstrained)

    Functionally identitical to JObjects, but the class hierarchy might be
    confusing if all objects inherit from Sandboxes."""
    pass


class JamsFrame(pd.DataFrame):
    '''A dataframe class for JAMS.

    This automates certain niceties, such as timestamp
    conversion and serializatoin.
    '''

    __dense = False

    @property
    def dense(self):
        '''Is this to be interpreted as a dense array, or sparse?'''
        return self.__dense

    @dense.setter
    def dense(self, value):
        '''Setter for dense'''
        self.__dense = value

    @classmethod
    def fields(cls):
        '''Fields of a JamsFrame'''
        return ['time', 'duration', 'value', 'confidence']

    @classmethod
    def from_dict(cls, *args, **kwargs):

        new_frame = super(JamsFrame, cls).from_dict(*args, **kwargs)

        # Encode time properly
        new_frame.time = pd.to_timedelta(new_frame.time,
                                         unit='s')

        new_frame.duration = pd.to_timedelta(new_frame.duration,
                                             unit='s')

        # Properly order the columns
        new_frame = new_frame[cls.fields()]

        # Clobber the class attribute
        new_frame.__class__ = cls
        return new_frame

    @classmethod
    def factory(cls):
        '''Construct a new, empty JamsFrame'''

        return cls.from_dict({x: [] for x in cls.fields()})

    @property
    def __json__(self):
        '''JSON encoding attribute'''

        def __recursive_simplify(D):
            '''A simplifier for nested dictionary structures'''
            if isinstance(D, list):
                return [__recursive_simplify(Di) for Di in D]

            dict_out = {}
            for key, value in D.iteritems():
                if isinstance(value, dict):
                    dict_out[key] = __recursive_simplify(value)
                else:
                    dict_out[key] = util.serialize_obj(value)
            return dict_out

        # By default, we'll output a record for each row
        # But, if the dense flag is set, we'll output the entire
        # table as one object

        orient = 'records'
        if self.dense:
            orient = 'list'

        return __recursive_simplify(self.to_dict(orient=orient))

    def add_observation(self, time=None, duration=None,
                        value=None, confidence=None):
        '''Add a single observation event to an existing frame'''

        n = len(self)
        self.loc[n] = {'time': pd.to_timedelta(time, unit='s'),
                       'duration': pd.to_timedelta(duration, unit='s'),
                       'value': value,
                       'confidence': confidence}

    def to_interval_values(self):
        '''Extract observation data in a mir_eval-friendly format.

        :returns:
            - intervals : np.ndarray [shape=(n, 2), dtype=float]
              Start- and end-times of all valued intervals

              intervals[i, :] = [time[i], time[i] + duration[i]]

            - labels : list
              List view of value field.
        '''

        times = util.timedelta_to_float(self.time.values)
        duration = util.timedelta_to_float(self.duration.values)

        return np.vstack([times, times + duration]).T, list(self.value)


class Annotation(JObject):
    """Annotation base class."""

    def __init__(self, data=None, annotation_metadata=None, namespace='',
                 sandbox=None):
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
        sandbox: Sandbox (dict), default=None
            Miscellaneous information; keep to native datatypes if possible.
        """

        JObject.__init__(self)

        if annotation_metadata is None:
            annotation_metadata = AnnotationMetadata()

        if sandbox is None:
            sandbox = Sandbox()

        self.annotation_metadata = AnnotationMetadata(**annotation_metadata)

        if data is None:
            self.data = JamsFrame.factory()
        else:
            self.data = JamsFrame.from_dict(data)

        self.sandbox = Sandbox(**sandbox)
        self.namespace = namespace

    def append(self, **kwargs):
        '''Append an observation to the data field'''

        self.data.add_observation(**kwargs)


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
        JObject.__init__(self)
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


class AnnotationArray(list):
    """AnnotationArray

    List subclass for managing collections of annotations, providing factory
    methods to create empty annotations.
    """
    def __init__(self, annotations):
        """Create an AnnotationArray.

        Parameters
        ----------
        annotations: list
            List of XAnnotations, or appropriately formated dicts, where X
            is consistent with AnnotationType.
        """
        if annotations is None:
            annotations = list()

        self.extend([Annotation(**obj) for obj in annotations])

    def create_annotation(self, *args, **kwargs):
        """Create an empty Annotation, returning a reference to
        the new annotation object.

        Returns
        -------
        obj: Annotation
            An annotation, initialized with the given arguments.
        """
        self.append(Annotation(*args, **kwargs))
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
        beat : list of Annotations
            Used for beat-tracking.
        chord : list of Annotations
            Used for chord estimation.
        genre : list of Annotations
            Used for genre tagging.
        key : list of Annotations
            Used for key estimation.
        mood : list of Annotations
            Used for mood estimation.
        melody : list of Annotations
            Used for continuous-f0 melody.
        note : list of Annotations
            Used for estimated note transcription.
        onset : list of Annotations
            Used for onset detection.
        pattern : list of Annotations
            Used for pattern discovery.
        pitch : list of Annotations
            Used for pitch estimation.
        segment : list of Annotations
            Used for music segmentation.
        source : list of Annotations
            Used for source activations.
        tag : list of Annotations
            Used for music tagging and semantic descriptors.
        file_metadata : FileMetadata (or dict), default=None
            Metadata corresponding to the audio file.
        sandbox : Sandbox (or dict), default=None
            Unconstrained global sandbox for additional information.
        """
        if file_metadata is None:
            file_metadata = FileMetadata()

        if sandbox is None:
            sandbox = Sandbox()

        self.beat = AnnotationArray([] if beat is None else beat)
        self.chord = AnnotationArray([] if chord is None else chord)
        self.genre = AnnotationArray([] if genre is None else genre)
        self.key = AnnotationArray([] if key is None else key)
        self.melody = AnnotationArray([] if melody is None else melody)
        self.mood = AnnotationArray([] if mood is None else mood)
        self.note = AnnotationArray([] if note is None else note)
        self.onset = AnnotationArray([] if onset is None else onset)
        self.pattern = AnnotationArray([] if pattern is None else pattern)
        self.pitch = AnnotationArray([] if pitch is None else pitch)
        self.segment = AnnotationArray([] if segment is None else segment)
        self.source = AnnotationArray([] if source is None else source)
        self.tag = AnnotationArray([] if tag is None else tag)
        self.file_metadata = FileMetadata(**file_metadata)
        self.sandbox = Sandbox(**sandbox)

    @property
    def __schema__(self):
        return None

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
        self.genre.extend(jam.pitch)
        self.key.extend(jam.key)
        self.melody.extend(jam.melody)
        self.mood.extend(jam.mood)
        self.note.extend(jam.note)
        self.onset.extend(jam.onset)
        self.pattern.extend(jam.pattern)
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
