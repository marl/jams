"""
JAMS Python API
===============

This library provides an interface for reading JAMS into Python, or creating
them programatically.

.. currentmodule:: jams

Function reference
------------------
.. autosummary::
    :toctree: generated/

    load

Object reference
----------------
.. autosummary::
    :toctree: generated/
    :template: class.rst

    JAMS
    FileMetadata
    AnnotationArray
    AnnotationMetadata
    Curator
    Annotation
    JamsFrame
    Sandbox
    JObject

"""
from bson import ObjectId
import bson.json_util as bjson
import json
import jsonschema

import numpy as np
import pandas as pd
import os
import re
import six
import warnings
import contextlib
import gzip

from .version import version as __VERSION__
from . import schema
from .exceptions import JamsError, SchemaError, ParameterError


__all__ = ['load',
           'JObject', 'Sandbox', 'JamsFrame',
           'Annotation', 'Curator', 'AnnotationMetadata',
           'FileMetadata', 'AnnotationArray', 'JAMS']


@contextlib.contextmanager
def _open(name_or_fdesc, mode='r', fmt='auto'):
    '''An intelligent wrapper for ``open``.

    Parameters
    ----------
    name_or_fdesc : string-type or open file descriptor
        If a string type, refers to the path to a file on disk.

        If an open file descriptor, it is returned as-is.

    mode : string
        The mode with which to open the file.
        See ``open`` for details.

    fmt : string ['auto', 'jams', 'json', 'jamz']
        The encoding for the input/output stream.

        If `auto`, the format is inferred from the filename extension.

        Otherwise, use the specified coding.


    See Also
    --------
    open
    gzip.open
    '''

    open_map = {'jams': open,
                'json': open,
                'jamz': gzip.open,
                'gz': gzip.open}

    # If we've been given an open descriptor, do the right thing
    if hasattr(name_or_fdesc, 'read') or hasattr(name_or_fdesc, 'write'):
        yield name_or_fdesc

    elif isinstance(name_or_fdesc, six.string_types):
        # Infer the opener from the extension

        if fmt == 'auto':
            _, ext = os.path.splitext(name_or_fdesc)

            # Pull off the extension separator
            ext = ext[1:]
        else:
            ext = fmt

        try:
            ext = ext.lower()

            # Force text mode if we're using gzip
            if ext in ['jamz', 'gz'] and 't' not in mode:
                mode = '{:s}t'.format(mode)

            with open_map[ext](name_or_fdesc, mode=mode) as fdesc:
                yield fdesc

        except KeyError:
            raise ParameterError('Unknown JAMS extension format: "{:s}"'.format(ext))

    else:
        # Don't know how to handle this. Raise a parameter error
        raise ParameterError('Invalid filename or descriptor: {:r}'.format(name_or_fdesc))


def load(path_or_file, validate=True, strict=True, fmt='auto'):
    r"""Load a JAMS Annotation from a file.


    Parameters
    ----------
    path_or_file : str or file-like
        Path to the JAMS file to load
        OR
        An open file handle to load from.

    validate : bool
        Attempt to validate the JAMS object

    strict : bool
        if `validate == True`, enforce strict schema validation

    fmt : str ['auto', 'jams', 'jamz']
        The encoding format of the input

        If `auto`, encoding is inferred from the file name.

        If the input is an open file handle, `jams` encoding
        is used.


    Returns
    -------
    jam : JAMS
        The loaded JAMS object


    Raises
    ------
    SchemaError
        if `validate == True`, `strict==True`, and validation fails


    See also
    --------
    JAMS.validate
    JAMS.save


    Examples
    --------
    >>> # Load a jams object from a file name
    >>> J = jams.load('data.jams')
    >>> # Or from an open file descriptor
    >>> with open('data.jams', 'r') as fdesc:
    ...     J = jams.load(fdesc)
    >>> # Non-strict validation
    >>> J = jams.load('data.jams', strict=False)
    >>> # No validation at all
    >>> J = jams.load('data.jams', validate=False)
    """

    with _open(path_or_file, mode='r', fmt=fmt) as fdesc:
        jam = JAMS(**json.load(fdesc))

    if validate:
        jam.validate(strict=strict)

    return jam


class JObject(object):
    r"""Dict-like object for JSON Serialization.

    This object behaves like a dictionary to allow init-level attribute names,
    seamless JSON-serialization, and double-star style unpacking (** obj).

    By setting the `type` attribute to a defined schema entry, only the fields
    allowed by the schema are permitted as attributes.
    """
    def __init__(self, **kwargs):
        '''Construct a new JObject

        Parameters
        ----------
        kwargs
            Each keyword argument becomes an attribute with the specified value

        Examples
        --------
        >>> J = jams.JObject(foo=5)
        >>> J.foo
        5
        >>> dict(J)
        {'foo': 5}
        '''
        super(JObject, self).__init__()

        for name, value in six.iteritems(kwargs):
            setattr(self, name, value)

    @property
    def __schema__(self):
        '''The schema definition for this JObject, if it exists.

        Returns
        -------
        schema : dict or None
            If dict, must have k-v pair for 'properties'.
        '''
        return schema.definition_schema(self.type, raise_if_missing=False)

    @property
    def __json__(self):
        r"""Return the JObject as a set of native data types for serialization.

        Note: attributes beginning with underscores are suppressed.
        """
        filtered_dict = dict()

        for k, item in six.iteritems(self.__dict__):
            if k.startswith('_'):
                continue

            if isinstance(item, ObjectId):
                item = json.loads(bjson.dumps(item))
            elif hasattr(item, '__json__'):
                item = item.__json__

            filtered_dict[k] = item

        return filtered_dict

    @classmethod
    def __json_init__(cls, **kwargs):
        """Initialize the object from a dictionary of values"""
        return cls(**kwargs)

    def __eq__(self, other):
        return (isinstance(other, self.__class__) and
                (self.__dict__ == other.__dict__))

    def __nonzero__(self):
        return bool(self.__json__)

    def __getitem__(self, key):
        """Dict-style interface"""
        return self.__dict__[key]

    def __setattr__(self, name, value):
        if self.__schema__:
            props = self.__schema__['properties']
            if name not in props:
                raise SchemaError("Attribute {} not in {}"
                                  .format(name, props.keys()))
        self.__dict__[name] = value

    def __len__(self):
        return len(self.keys())

    def __repr__(self):
        """Render the object alongside its attributes."""
        return '<{}: {:s}>'.format(self.type, ', '.join(self.keys()))

    def __str__(self):
        return json.dumps(self.__json__, indent=2)

    def dumps(self, **kwargs):
        '''Serialize the JObject to a string.

        Parameters
        ----------
        kwargs
            Keyword arguments to json.dumps

        Returns
        -------
        object_str : str
            Serialized JObject

        See Also
        --------
        json.dumps
        loads

        Examples
        --------
        >>> J = jams.JObject(foo=5, bar='baz')
        >>> J.dumps()
        '{"foo": 5, "bar": "baz"}'

        '''
        return json.dumps(self.__json__, **kwargs)

    def keys(self):
        """Return a list of the attributes of the object.

        Returns
        -------
        keys : list
            The attributes of the object

        Examples
        --------
        >>> J = jams.JObject(foo=5, bar='baz')
        >>> J.keys()
        ['foo', 'bar']
        """
        return self.__dict__.keys()

    def update(self, **kwargs):
        '''Update the attributes of a JObject.

        Parameters
        ----------
        kwargs
            Keyword arguments of the form `attribute=new_value`

        Examples
        --------
        >>> J = jams.JObject(foo=5)
        >>> J.dumps()
        '{"foo": 5}'
        >>> J.update(bar='baz')
        >>> J.dumps()
        '{"foo": 5, "bar": "baz"}'
        '''
        for name, value in six.iteritems(kwargs):
            setattr(self, name, value)

    @property
    def type(self):
        '''The type (class name) of a derived JObject type'''
        return self.__class__.__name__

    @classmethod
    def loads(cls, string):
        '''De-serialize a JObject

        Parameters
        ----------
        string : str
            A serialized (JSON string) JObject

        Returns
        -------
        J : JObject
            The input string reconstructed as a JObject

        See Also
        --------
        json.loads
        dumps

        Examples
        --------
        >>> J = jams.JObject(foo=5, bar='baz')
        >>> J.dumps()
        '{"foo": 5, "bar": "baz"}'
        >>> jams.JObject.loads(J.dumps())
        <JObject foo, bar>
        '''
        return cls.__json_init__(**bjson.loads(string))

    def search(self, **kwargs):
        '''Query this object (and its descendants).

        Parameters
        ----------
        kwargs
            Each `(key, value)` pair encodes a search field in `key`
            and a target value in `value`.

            `key` must be a string, and should correspond to a property in
            the JAMS object hierarchy, e.g., 'Annotation.namespace` or `email`

            `value` must be either an object (tested for equality), a
            string describing a search pattern (regular expression), or a
            lambda function which evaluates to `True` if the candidate
            object matches the search criteria and `False` otherwise.

        Returns
        -------
        match : bool
            `True` if any of the search keys match the specified value,
            `False` otherwise, or if the search keys do not exist within the object.

        Examples
        --------
        >>> J = jams.JObject(foo=5, needle='quick brown fox')
        >>> J.search(needle='.*brown.*')
        True
        >>> J.search(needle='.*orange.*')
        False
        >>> J.search(badger='.*brown.*')
        False
        >>> J.search(foo=5)
        True
        >>> J.search(foo=10)
        False
        >>> J.search(foo=lambda x: x < 10)
        True
        >>> J.search(foo=lambda x: x > 10)
        False
        '''

        match = False

        r_query = {}
        myself = self.__class__.__name__

        # Pop this object name off the query
        for k, value in six.iteritems(kwargs):
            k_pop = query_pop(k, myself)

            if k_pop:
                r_query[k_pop] = value

        if not r_query:
            return False

        for key in r_query:
            if hasattr(self, key):
                match |= match_query(getattr(self, key), r_query[key])

        if not match:
            for attr in dir(self):
                obj = getattr(self, attr)

                if isinstance(obj, JObject):
                    match |= obj.search(**r_query)

        return match

    def validate(self, strict=True):
        '''Validate a JObject against its schema

        Parameters
        ----------
        strict : bool
            Enforce strict schema validation

        Returns
        -------
        valid : bool
            True if the jam validates
            False if not, and `strict==False`

        Raises
        ------
        SchemaError
            If `strict==True` and `jam` fails validation
        '''

        valid = True
        try:
            jsonschema.validate(self.__json__, self.__schema__)

        except (JamsError, jsonschema.ValidationError) as invalid:
            if strict:
                raise SchemaError(str(invalid))
            else:
                warnings.warn(str(invalid))

            valid = False

        return valid


class Sandbox(JObject):
    """Sandbox (unconstrained)

    Functionally identical to JObjects, but the class hierarchy might be
    confusing if all objects inherit from Sandboxes."""
    pass


class JamsFrame(pd.DataFrame):
    '''A data-frame class for JAMS.

    This automates certain niceties, such as timestamp
    conversion and serialization.
    '''

    __dense = False

    def __init__(self, data=None, index=None, columns=None, dtype=None):
        '''Construct a new JamsFrame object.

        Parameters
        ----------
        data
            Optional data for the new JamsFrame, in any format supported
            by `pandas.DataFrame.__init__`.

            Fields must be `['time', 'duration', 'value', 'confidence']`.

            `time` and `duration` fields must be floating point types,
            measured in seconds.

        index
            Optional index on `data`.

        columns
        dtype
            These parameters are ignored by JamsFrame, but are allowed
            for API compatibility with `pandas.DataFrame`.

        See Also
        --------
        from_dict
        from_dataframe
        pandas.DataFrame.__init__

        '''
        super(JamsFrame, self).__init__(data=data, index=index,
                                        columns=self.fields())

        self.time = pd.to_timedelta(self.time, unit='s')
        self.duration = pd.to_timedelta(self.duration, unit='s')

    @property
    def dense(self):
        '''Boolean to determine whether the encoding is dense or sparse.

        Returns
        -------
        dense : bool
            `True` if the data should be encoded densely
            `False` otherwise
        '''
        return self.__dense

    @dense.setter
    def dense(self, value):
        '''Setter for dense'''
        self.__dense = value

    @classmethod
    def fields(cls):
        '''Fields of a JamsFrame: (time, duration, value, confidence)

        Returns
        -------
        fields : list
            The only permissible fields for a JamsFrame:
            `time`, `duration`, `value`, and `confidence`
        '''
        return ['time', 'duration', 'value', 'confidence']

    @classmethod
    def from_dict(cls, *args, **kwargs):
        '''Construct a new JamsFrame from a dictionary or list of dictionaries.

        This is analogous to pd.DataFrame.from_dict, except the returned object
        has the type `JamsFrame`.

        See Also
        --------
        pandas.DataFrame.from_dict
        from_dataframe
        '''
        new_frame = super(JamsFrame, cls).from_dict(*args, **kwargs)

        return cls.from_dataframe(new_frame)

    @classmethod
    def from_dataframe(cls, frame):
        '''Convert a pandas DataFrame into a JamsFrame.

        Note: this operation is destructive, in that the input
        DataFrame will have its type and data altered.

        Parameters
        ----------
        frame : pandas.DataFrame
            The input DataFrame.  Must have the appropriate JamsFrame fields:
            'time', 'duration', 'value', and 'confidence'.

            'time' and 'duration' fields should be of type `float` and measured
            in seconds.

        Returns
        -------
        jams_frame : JamsFrame
            The input `frame` modified to form a JamsFrame.

        See Also
        --------
        from_dict
        '''
        # Encode time properly
        frame.time = pd.to_timedelta(frame.time, unit='s')
        frame.duration = pd.to_timedelta(frame.duration, unit='s')

        # Properly order the columns
        frame = frame[cls.fields()]

        # Clobber the class attribute
        frame.__class__ = cls
        return frame

    @property
    def __json__(self):
        '''JSON encoding attribute'''

        def __recursive_simplify(D):
            '''A simplifier for nested dictionary structures'''
            if isinstance(D, list):
                return [__recursive_simplify(Di) for Di in D]

            dict_out = {}
            for key, value in six.iteritems(D):
                if isinstance(value, dict):
                    dict_out[key] = __recursive_simplify(value)
                else:
                    dict_out[key] = serialize_obj(value)
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
        '''Add a single observation event to an existing frame.

        New observations are appended to the end of the frame.

        Parameters
        ----------
        time : float
            The time of the new observation, in seconds

        duration : float
            The duration of the new observation, in seconds

        value
        confidence
            The value and confidence fields of the new observation.
            This should conform to the corresponding `namespace` of the
            containing `Annotation` object.

        Examples
        --------
        >>> frame = jams.JamsFrame()
        >>> frame.add_observation(time=3, duration=1.5, value='C#')
        >>> frame.add_observation(time=5, duration=.5, value='C#:min', confidence=.8)
        >>> frame
              time        duration   value confidence
        0 00:00:03 00:00:01.500000      C#        NaN
        1 00:00:05 00:00:00.500000  C#:min        0.8
        '''

        if time is None or not (time >= 0.0):
            raise ParameterError('time={} must be a non-negative number'.format(time))

        if duration is None or not (duration >= 0.0):
            raise ParameterError('duration={} must be a non-negative number'.format(duration))

        n = len(self)
        self.loc[n] = {'time': pd.to_timedelta(time, unit='s'),
                       'duration': pd.to_timedelta(duration, unit='s'),
                       'value': value,
                       'confidence': confidence}

    def to_interval_values(self):
        '''Extract observation data in a `mir_eval`-friendly format.

        Returns
        -------
        intervals : np.ndarray [shape=(n, 2), dtype=float]
            Start- and end-times of all valued intervals

            `intervals[i, :] = [time[i], time[i] + duration[i]]`

        labels : list
            List view of value field.
        '''

        times = timedelta_to_float(self.time.values)
        duration = timedelta_to_float(self.duration.values)

        return np.vstack([times, times + duration]).T, list(self.value)


class Annotation(JObject):
    """Annotation base class."""

    def __init__(self, namespace, data=None, annotation_metadata=None,
                 sandbox=None, time=0, duration=None, audio_id=None,
                 doc_id=None):
        """Create an Annotation.

        Note that, if an argument is None, an empty Annotation is created in
        its place. Additionally, a dictionary matching the expected structure
        of the arguments will be parsed (i.e. instantiating from JSON).

        Parameters
        ----------
        namespace : str
            The namespace for this annotation

        data : dict or list-of-dict
            Data for the new annotation in a format supported by `JamsFrame.from_dict`

        annotation_metadata : AnnotationMetadata (or dict), default=None.
            Metadata corresponding to this Annotation.

        sandbox : Sandbox (dict), default=None
            Miscellaneous information; keep to native datatypes if possible.

        time : non-negative number
            The starting time for this annotation

        duration : non-negative number
            The duration of this annotation

        audio_id : ObjectId or None
            Identifier of the audio object to which this annotation corresponds.

        doc_id : ObjectId or None
            Identifier of this annotation document.
        """

        super(Annotation, self).__init__()

        if annotation_metadata is None:
            annotation_metadata = AnnotationMetadata()

        self.annotation_metadata = AnnotationMetadata(**annotation_metadata)

        if data is None:
            self.data = JamsFrame()
        else:
            self.data = JamsFrame.from_dict(data)

        if sandbox is None:
            sandbox = Sandbox()

        self.sandbox = Sandbox(**sandbox)

        self.namespace = namespace

        # Set the data export coding to match the namespace
        self.data.dense = schema.is_dense(self.namespace)

        self.time = time
        self.duration = duration
        self.doc_id = doc_id
        self.audio_id = audio_id

    def append(self, **kwargs):
        '''Append an observation to the data field

        Parameters
        ----------
        time : float >= 0
        duration : float >= 0
            The time and duration of the new observation, in seconds
        value
        confidence
            The value and confidence of the new observations.

            Types and values should conform to the namespace of the
            Annotation object.

        See Also
        --------
        JamsFrame.add_observation

        Examples
        --------
        >>> ann = jams.Annotation(namespace='chord')
        >>> ann.append(time=0, duration=3, value='C#')
        >>> ann.append(time=3, duration=2, value='E#')
        >>> ann
        <Annotation: namespace, annotation_metadata, data, sandbox>
        >>> ann.data
              time  duration value confidence
        0 00:00:00  00:00:03    C#       None
        1 00:00:03  00:00:02    E#       None
        '''

        self.data.add_observation(**kwargs)

    def __eq__(self, other):
        '''Override JObject equality to handle JamsFrames specially'''
        if not isinstance(other, self.__class__):
            return False

        for key in self.__dict__:
            value = True
            if key == 'data':
                value = self.__dict__[key].equals(other.__dict__[key])
            else:
                value = self.__dict__[key] == other.__dict__[key]

            if not value:
                return False

        return True

    def validate(self, strict=True):
        '''Validate this annotation object against the JAMS schema,
        and its data against the namespace schema.

        Parameters
        ----------
        strict : bool
            If `True`, then schema violations will cause an Exception.
            If `False`, then schema violations will issue a warning.

        Returns
        -------
        valid : bool
            `True` if the object conforms to schema.
            `False` if the object fails to conform to schema, but `strict == False`.

        Raises
        ------
        SchemaError
            If `strict == True` and the object fails validation

        See Also
        --------
        JObject.validate
        '''

        valid = super(Annotation, self).validate(strict=strict)

        # Get the schema for this annotation
        ann_schema = schema.namespace(self.namespace)

        try:
            records = self.data.__json__

            # If the data has a dense packing, reshape it for record-wise validation
            if self.data.dense:
                records = [dict(_)
                           for _ in zip(*[[(k, v) for v in value]
                                          for (k, value) in six.iteritems(records)])]

            # validate each record in the frame
            for rec in records:
                jsonschema.validate(rec, ann_schema)

        except jsonschema.ValidationError as invalid:
            if strict:
                raise SchemaError(str(invalid))
            else:
                warnings.warn(str(invalid))
            valid = False

        return valid


class Curator(JObject):
    """Curator

    Container object for curator metadata.
    """
    def __init__(self, name='', email=''):
        """Create a Curator.

        Parameters
        ----------
        name: str, default=''
            Common name of the curator.

        email: str, default=''
            An email address corresponding to the curator.
        """
        super(Curator, self).__init__()
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
        super(AnnotationMetadata, self).__init__()

        if curator is None:
            curator = Curator()

        if annotator is None:
            annotator = JObject()

        self.curator = Curator(**curator)
        self.annotator = JObject(**annotator)

        self.version = version
        self.corpus = corpus
        self.annotation_tools = annotation_tools
        self.annotation_rules = annotation_rules
        self.validation = validation
        self.data_source = data_source


class FileMetadata(JObject):
    """Metadata for a given audio file."""
    def __init__(self, title='', artist='', release='', duration=None,
                 identifiers=None, jams_version=None):
        """Create a file-level Metadata object.

        Parameters
        ----------
        title: str
            Name of the recording.

        artist: str
            Name of the artist / musician.

        release: str
            Name of the release

        duration: number >= 0
            Time duration of the file, in seconds.

        identifiers : jams.Sandbox
            Sandbox of identifier keys (eg, musicbrainz ids)

        jams_version: str
            Version of the JAMS Schema.
        """
        super(FileMetadata, self).__init__()

        if jams_version is None:
            jams_version = __VERSION__

        if identifiers is None:
            identifiers = Sandbox()

        self.title = title
        self.artist = artist
        self.release = release
        self.duration = duration
        self.identifiers = Sandbox(**identifiers)
        self.jams_version = jams_version


class AnnotationArray(list):
    """AnnotationArray

    This list subclass provides serialization and search/filtering
    for annotation collections.
    """
    def __init__(self, annotations=None):
        """Create an AnnotationArray.

        Parameters
        ----------
        annotations: list
            List of Annotations, or appropriately formated dicts
            is consistent with Annotation.
        """
        super(AnnotationArray, self).__init__()

        if annotations is None:
            annotations = list()

        self.extend([Annotation(**obj) for obj in annotations])

    def search(self, **kwargs):
        '''Filter the annotation array down to only those Annotation
        objects matching the query.


        Parameters
        ----------
        kwargs : search parameters
            See JObject.search

        Returns
        -------
        results : AnnotationArray
            An annotation array of the objects matching the query

        See Also
        --------
        JObject.search
        '''

        results = AnnotationArray()

        for annotation in self:
            if annotation.search(**kwargs):
                results.append(annotation)

        return results

    @property
    def __json__(self):
        return [item.__json__ for item in self]


class JAMS(JObject):
    """Top-level Jams Object"""

    def __init__(self, annotations=None, file_metadata=None, sandbox=None):
        """Create a Jams object.

        Parameters
        ----------
        annotations : list of Annotations
            Zero or more Annotation objects

        file_metadata : FileMetadata (or dict), default=None
            Metadata corresponding to the audio file.

        sandbox : Sandbox (or dict), default=None
            Unconstrained global sandbox for additional information.

        """
        super(JAMS, self).__init__()

        if file_metadata is None:
            file_metadata = FileMetadata()

        if sandbox is None:
            sandbox = Sandbox()

        self.annotations = AnnotationArray(annotations=annotations)

        self.file_metadata = FileMetadata(**file_metadata)

        self.sandbox = Sandbox(**sandbox)

    @property
    def __schema__(self):
        return schema.JAMS_SCHEMA

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

        Raises
        ------
        ParameterError
            if `on_conflict` is an unknown value

        JamsError
            If a conflict is detected and `on_conflict='fail'`
        """

        if on_conflict not in ['overwrite', 'fail', 'ignore']:
            raise ParameterError("on_conflict='{}' is not in ['fail', "
                                 "'overwrite', 'ignore'].".format(on_conflict))

        if not self.file_metadata == jam.file_metadata:
            if on_conflict == 'overwrite':
                self.file_metadata = jam.file_metadata
            elif on_conflict == 'fail':
                raise JamsError("Metadata conflict! "
                                "Resolve manually or force-overwrite it.")

        self.annotations.extend(jam.annotations)
        self.sandbox.update(**jam.sandbox)

    def search(self, **kwargs):
        '''Search a JAMS object for matching objects.

        Parameters
        ----------
        kwargs : keyword arguments
            Keyword query

        Returns
        -------
        AnnotationArray
            All annotation objects in this JAMS which match the query

        See Also
        --------
        JObject.search
        AnnotationArray.search


        Examples
        --------
        A simple query to get all beat annotations

        >>> beats = my_jams.search(namespace='beat')

        '''

        return self.annotations.search(**kwargs)

    def save(self, path_or_file, strict=True, fmt='auto'):
        """Serialize annotation as a JSON formatted stream to file.

        Parameters
        ----------
        path_or_file : str or file-like
            Path to save the JAMS object on disk
            OR
            An open file descriptor to write into

        strict : bool
            Force strict schema validation

        fmt : str ['auto', 'jams', 'jamz']
            The output encoding format.

            If `auto`, it is inferred from the file name.

            If the input is an open file handle, `jams` encoding
            is used.


        Raises
        ------
        SchemaError
            If `strict == True` and the JAMS object fails schema
            or namespace validation.

        See also
        --------
        validate
        """

        self.validate(strict=strict)

        with _open(path_or_file, mode='w', fmt=fmt) as fdesc:
            json.dump(self.__json__, fdesc, indent=2)

    def validate(self, strict=True):
        '''Validate a JAMS object against the schema.

        Parameters
        ----------
        strict : bool
            If `True`, an exception will be raised on validation failure.
            If `False`, a warning will be raised on validation failure.

        Returns
        -------
        valid : bool
            `True` if the object passes schema validation.
            `False` otherwise.

        Raises
        ------
        SchemaError
            If `strict==True` and the JAMS object does not match the schema

        See Also
        --------
        jsonschema.validate

        '''
        valid = super(JAMS, self).validate(strict=strict)

        for ann in self.annotations:
            valid &= ann.validate(strict=strict)

        return valid


# -- Helper functions -- #

def timedelta_to_float(t):
    '''Convert a timedelta64[ns] to floating point (seconds)'''

    return t.astype(np.float) * 1e-9


def query_pop(query, prefix, sep='.'):
    '''Pop a prefix from a query string.


    Parameters
    ----------
    query : str
        The query string

    prefix : str
        The prefix string to pop, if it exists

    sep : str
        The string to separate fields

    Returns
    -------
    popped : str
        `query` with a `prefix` removed from the front (if found)
        or `query` if the prefix was not found

    Examples
    --------
    >>> query_pop('Annotation.namespace', 'Annotation')
    'namespace'
    >>> query_pop('namespace', 'Annotation')
    'namespace'

    '''

    terms = query.split(sep)

    if terms[0] == prefix:
        terms = terms[1:]

    return sep.join(terms)


def match_query(string, query):
    '''Test if a string matches a query.

    Parameters
    ----------
    string : str
        The string to test

    query : string, callable, or object
        Either a regular expression, callable function, or object.

    Returns
    -------
    match : bool
        `True` if:
        - `query` is a callable and `query(string) == True`
        - `query` is a regular expression and `re.match(query, string)`
        - or `string == query` for any other query

        `False` otherwise

    '''

    if six.callable(query):
        return query(string)

    elif isinstance(query, six.string_types):
        return re.match(query, string) is not None

    else:
        return query == string


def serialize_obj(obj):
    '''Custom serialization functionality for working with advanced data types.

    - Timedelta objects are converted to floats (in seconds)
    - numpy arrays are converted to lists
    - lists are recursively serialized element-wise

    '''
    if isinstance(obj, pd.tslib.Timedelta):
        return obj.total_seconds()

    elif isinstance(obj, np.ndarray):
        return obj.tolist()

    elif isinstance(obj, list):
        return [serialize_obj(x) for x in obj]

    return obj
