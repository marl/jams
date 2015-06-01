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

import json
import jsonschema

import numpy as np
import pandas as pd
import os
import re
import six
import warnings

from pkg_resources import resource_filename

from .version import version as __VERSION__
from . import ns
from .exceptions import JamsError, SchemaError, ParameterError


__all__ = ['load',
           'JObject', 'Sandbox', 'JamsFrame',
           'Annotation', 'Curator', 'AnnotationMetadata',
           'FileMetadata', 'AnnotationArray', 'JAMS']


__OBJECT_TYPE__ = 'object_type'


def __load_schema():
    '''Load the schema file from the package.'''

    schema_file = os.path.join('schema', 'jams_schema.json')

    schema = None
    with open(resource_filename(__name__, schema_file), mode='r') as fdesc:
        schema = json.load(fdesc)

    if schema is None:
        raise JamsError('Unable to load JAMS schema')

    return schema


__SCHEMA__ = __load_schema()


def load(filepath, validate=True, strict=True):
    r"""Load a JAMS Annotation from a file.


    Parameters
    ----------
    filepath : str
        Path to the JAMS file to load

    validate : bool
        Attempt to validate the JAMS object

    strict : bool
        if `validate == True`, enforce strict schema validation


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
    """

    with open(filepath, 'r') as fdesc:
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
        '''
        return __SCHEMA__['definitions'].get(self.type, None)

    @property
    def __json__(self):
        r"""Return the JObject as a set of native datatypes for serialization.

        Note: attributes beginning with underscores are suppressed.
        """
        filtered_dict = dict()

        for k, item in six.iteritems(self.__dict__):
            if k.startswith('_'):
                continue

            if hasattr(item, '__json__'):
                filtered_dict[k] = item.__json__
            else:
                filtered_dict[k] = item

        return filtered_dict

    @classmethod
    def __json_init__(cls, **kwargs):
        """TODO(ejhumphrey@nyu.edu): writeme."""
        return cls(**kwargs)

    def __eq__(self, other):
        return (isinstance(other, self.__class__) and
                (self.__dict__ == other.__dict__))

    def __nonzero__(self):
        return bool(self.__json__)

    def __getitem__(self, key):
        """TODO(ejhumphrey@nyu.edu): writeme."""
        return self.__dict__[key]

    def __setattr__(self, name, value):
        if self.__schema__ is not None:
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
        '''Deserialize a JObject

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
        return cls.__json_init__(**json.loads(string))

    def search(self, **kwargs):
        '''Query this object (and its descendants).

        Parameters
        ----------
        kwargs
            Each `(key, value)` pair encodes a search field in `key`
            and a target value in `value`.

            `key` must be a string, and should correspond to a property in
            the JAMS object hierarchy, e.g., 'Annotation.namespace` or `email`

            `value` must be either a string describing a search pattern (regular
            expression) or a lambda function which evaluates to `True` if the candidate
            object matches the search criteria and `False` otherwise.

        Returns
        -------
        match : bool
            `True` if any of the search keys match the specified value,
            `False` otherwise, or if the search keys do not exist within the object.

        Raises
        ------
        ParameterError
            If a search value is not a string or callable

        Examples
        --------
        >>> J = jams.JObject(foo=5, needle='quick brown fox')
        >>> J.search(needle='.*brown.*')
        True
        >>> J.search(needle='.*orange.*')
        False
        >>> J.search(badger='.*brown.*')
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
            jsonschema.validate(self.__json__, __SCHEMA__)

        except jsonschema.ValidationError as invalid:
            if strict:
                six.raise_from(SchemaError, invalid)
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
    '''A dataframe class for JAMS.

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
                 sandbox=None):
        """Create an Annotation.

        Note that, if an argument is None, an empty Annotation is created in
        its place. Additionally, a dictionary matching the expected structure
        of the arguments will be parsed (i.e. instantiating from JSON).

        Parameters
        ----------
        namespace : str
            The namespace for this annotation

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
        self.data.dense = ns.is_dense(self.namespace)

    def append(self, **kwargs):
        '''Append an observation to the data field'''

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

        valid = super(Annotation, self).validate(strict=strict)

        # Get the schema for this annotation
        schema = ns.schema(self.namespace,
                           default=__SCHEMA__['definitions']['SparseObservation'])

        try:
            # validate each record in the frame
            for rec in self.data.__json__:
                jsonschema.validate(rec, schema)

        except jsonschema.ValidationError as invalid:
            if strict:
                six.raise_from(SchemaError, invalid)
            else:
                warnings.warn(str(invalid))
            valid = False

        return valid


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
        super(AnnotationMetadata, self).__init__()

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

        duration: number
            Time duration of the file, in seconds.

        identifiers : pyjams.Sandbox
            Sandbox of identifier keys (eg, musicbrainz ids)

        jams_version: str
            Version of the JAMS Schema.
        """
        super(FileMetadata, self).__init__()

        jams_version = __VERSION__ if jams_version is None else jams_version
        identifiers = Sandbox() if identifiers is None else identifiers

        self.title = title
        self.artist = artist
        self.release = release
        self.duration = duration
        self.identifiers = Sandbox(**identifiers)
        self.jams_version = jams_version


class AnnotationArray(list):
    """AnnotationArray

    List subclass for managing collections of annotations, providing factory
    methods to create empty annotations.
    """
    def __init__(self, annotations=None):
        """Create an AnnotationArray.

        Parameters
        ----------
        annotations: list
            List of XAnnotations, or appropriately formated dicts, where X
            is consistent with AnnotationType.
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
            Zero or more Annotation objcets

        file_metadata : FileMetadata (or dict), default=None
            Metadata corresponding to the audio file.

        sandbox : Sandbox (or dict), default=None
            Unconstrained global sandbox for additional information.

        """
        JObject.__init__(self)

        if file_metadata is None:
            file_metadata = FileMetadata()

        if sandbox is None:
            sandbox = Sandbox()

        self.annotations = AnnotationArray(annotations=annotations)

        self.file_metadata = FileMetadata(**file_metadata)

        self.sandbox = Sandbox(**sandbox)

    @property
    def __schema__(self):
        return __SCHEMA__

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


        Examples
        --------
        A simple query to get all beat annotations

        >>> beats = my_jams.search(namespace='beat')

        '''

        return self.annotations.search(**kwargs)

    def save(self, filepath, strict=True):
        """Serialize annotation as a JSON formatted stream to file.

        Parameters
        ----------
        filepath : str
            Path to save the JAMS object on disk

        strict : bool
            Force strict schema validation

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

        with open(filepath, 'w') as fdesc:
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
    '''Test if a string matches a functional query.

    Parameters
    ----------
    string : str
        The string to test

    query : string or callable
        Either a regular expression or a callable function

    Returns
    -------
    match : bool
        `True` if `query` is a callable and `query(string) == True`
        or if `query` is a regexp and `re.match(query, regexp)`

        `False` otherwise

    Raises
    ------
    ParameterError
        if `query` is not a string or callable
    '''

    if six.callable(query):
        return query(string)

    elif isinstance(query, six.string_types):
        return re.match(query, string) is not None

    raise ParameterError('Invalid query type: {}'.format(type(query)))


def serialize_obj(obj):
    '''Custom serialization functionality for working with advanced data types.

    - Timedelta objects are convered to floats (in seconds)
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
