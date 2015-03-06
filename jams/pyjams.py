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


3. Function reference
---------------------
.. autosummary::
    :toctree: generated/

    load
    append
    import_lab

4. Object reference
-------------------
.. autosummary::
    :toctree: generated/

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
from jsonschema import ValidationError

import numpy as np
import pandas as pd
import os
import re
import six
import warnings
import sys

from pkg_resources import resource_filename

from .version import version as __VERSION__
from . import namespace as ns

__OBJECT_TYPE__ = 'object_type'


def __load_schema():
    '''Load the schema file from the package.'''

    schema_file = os.path.join('schema', 'jams_schema.json')

    schema = None
    with open(resource_filename(__name__, schema_file), mode='r') as fdesc:
        schema = json.load(fdesc)

    assert schema is not None

    return schema


__SCHEMA__ = __load_schema()


def load(filepath, strict=True):
    r"""Load a JAMS Annotation from a file.


    Parameters
    ----------
    filepath : str
        Path to the JAMS file to load

    strict : bool
        Enforce strict schema validation


    Returns
    -------
    jam : JAMS
        The loaded JAMS object


    Raises
    ------
    ValidationError
        if `strict==True` and validation files


    See also
    --------
    JAMS.validate
    JAMS.save
    """

    with open(filepath, 'r') as fdesc:
        jam = JAMS(**json.load(fdesc))

    jam.validate(strict=strict)

    return jam


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
    old_jam.save(new_filepath)


class JObject(object):
    r"""Dict-like object for JSON Serialization.

    This object behaves like a dictionary to allow init-level attribute names,
    seamless JSON-serialization, and double-star style unpacking (**obj).

    """
    def __init__(self, **kwargs):
        object.__init__(self)
        for name, value in six.iteritems(kwargs):
            setattr(self, name, value)

    @property
    def __schema__(self):
        return __SCHEMA__['definitions'].get(self.type, None)

    @property
    def __json__(self):
        r"""Return the object as a set of native datatypes for serialization.

        Note: Empty strings / lists / dicts, None, and attributes beginning
        with underscores are suppressed.
        """
        filtered_dict = dict()

        for k, item in six.iteritems(self.__dict__):
            if hasattr(item, '__json__'):
                filtered_dict[k] = item.__json__
            elif k.startswith('_') or not item:
                continue
            else:
                filtered_dict[k] = item

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
                    ("Invalid attribute: {:s}\n"
                     "\t Should be one of {:s}.").format(name, props.keys()))
        self.__dict__[name] = value

    def __len__(self):
        return len(self.keys())

    def __repr__(self):
        """Render the object alongside its attributes."""
        return '<{:s}: {:s}>'.format(self.type, ', '.join(self.keys()))

    def __str__(self):
        return json.dumps(self.__json__, indent=2)

    def keys(self):
        """Return the fields of the object."""
        return self.__dict__.keys()

    def update(self, **kwargs):
        '''Update the attributes of a JObject.'''
        for name, value in six.iteritems(kwargs):
            setattr(self, name, value)

    @property
    def type(self):
        '''Return the type of a derived JObject type'''
        return self.__class__.__name__

    @classmethod
    def loads(cls, string):
        return cls.__json_init__(**json.loads(string))

    def dumps(self, *args, **kwargs):
        return json.dumps(self, *args, **kwargs)

    def search(self, **kwargs):
        '''Query this object (and its descendants)'''

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
                match |= match_query(getattr(self, key),
                                       r_query[key])

        if not match:
            for attr in dir(self):
                obj = getattr(self, attr)

                if isinstance(obj, JObject):
                    match |= obj.search(**r_query)

        return match


class Sandbox(JObject):
    """Sandbox (unconstrained)

    Functionally identical to JObjects, but the class hierarchy might be
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
        '''Fields of a JamsFrame: (time, duration, value, confidence)'''
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
        '''Add a single observation event to an existing frame'''

        n = len(self)
        self.loc[n] = {'time': pd.to_timedelta(time, unit='s'),
                       'duration': pd.to_timedelta(duration, unit='s'),
                       'value': value,
                       'confidence': confidence}

    def to_interval_values(self):
        '''Extract observation data in a mir_eval-friendly format.

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

        if sandbox is None:
            sandbox = Sandbox()

        self.annotation_metadata = AnnotationMetadata(**annotation_metadata)

        if data is None:
            self.data = JamsFrame.factory()
        else:
            self.data = JamsFrame.from_dict(data)

        self.sandbox = Sandbox(**sandbox)
        self.namespace = namespace

        # Set the data export coding to match the namespace
        self.data.dense = ns.is_dense(self.namespace)

    @property
    def __schema__(self):
        return __SCHEMA__['definitions'].get(self.type, None)

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
    def __init__(self, title='', artist='', release='', duration=None,
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

        duration: number
            Time duration of the file, in seconds.

        identifiers : pyjams.Sandbox
            Sandbox of identifier keys (eg, musicbrainz ids)

        jams_version: str
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
    def __init__(self, annotations=None):
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
        ValidationError
            If `strict == True` and the JAMS object fails schema
            or namespace validation.

        See also
        --------
        validate
        """

        self.validate(strict=strict)

        with open(filepath, 'w') as fp:
            json.dump(self.__json__, fp, indent=2)

    def validate(self, strict=True):
        '''Validate a JAM object.

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
        ValidationError
            If `strict==True` and `jam` fails validation

        '''

        valid = True

        try:
            jsonschema.validate(self.__json__, __SCHEMA__)

        except ValidationError as invalid:
            if strict:
                six.reraise(*sys.exc_info())
            else:
                warnings.warn(str(invalid))

            valid = False

        for ann in self.annotations:
            valid &= ns.validate_annotation(ann, strict=strict)

        return valid


def import_lab(namespace, filename, jam=None, **parse_options):
    '''Load a .lab file into a JAMS object.

    .lab files are assumed to have the following format:

    TIME_START\\tTIME_END\\tANNOTATION

    Parameters
    ----------
    namespace : str
        The namespace for the new annotation

    filename : str
        Path to the .lab file

    jam : pyjams.JAMS (optional)
        An optional pre-existing JAMS object to append into.
        If `None`, a new, blank JAMS object is created.

    parse_options : additional keyword arguments
        See `pandas.DataFrame.read_csv`

    Returns
    -------
    jam : JAMS
        The modified or constructed JAMS object

    annotation : Annotation
        A handle to the newly constructed annotation object
    '''

    # Create a new annotation object
    annotation = Annotation(namespace)

    if jam is None:
        jam = JAMS()

    parse_options.setdefault('sep', r'\s+')
    parse_options.setdefault('engine', 'python')
    parse_options.setdefault('header', None)
    parse_options.setdefault('index_col', False)

    # This is a hack to handle potentially ragged .lab data
    parse_options.setdefault('names', range(20))

    data = pd.read_csv(filename, **parse_options)

    # Drop all-nan columns
    data = data.dropna(how='all', axis=1)

    # Do we need to add a duration column?
    # This only applies to event annotations
    if len(data.columns) == 2:
        # Insert a column of zeros after the timing
        data.insert(1, 'duration', 0)
    else:
        # Convert from time to duration
        data.loc[:, 1] -= data[0]

    for row in data.itertuples():
        time, duration = row[1:3]

        value = [x for x in row[3:] if x is not None][-1]

        annotation.data.add_observation(time=time,
                                        duration=duration,
                                        confidence=1.0,
                                        value=value)

    jam.annotations.append(annotation)

    return jam, annotation


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
    '''

    if six.callable(query):
        return query(string)

    elif isinstance(query, six.string_types):
        return re.match(query, string) is not None

    else:
        raise TypeError('Invalid query type: {}'.format(type(query)))

    return False


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