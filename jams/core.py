"""
Core functionality
------------------

This library provides an interface for reading JAMS into Python, or creating
them programatically.

.. currentmodule:: jams

Function reference
^^^^^^^^^^^^^^^^^^
.. autosummary::
    :toctree: generated/

    load

Object reference
^^^^^^^^^^^^^^^^
.. autosummary::
    :toctree: generated/
    :template: class.rst

    JAMS
    FileMetadata
    AnnotationArray
    AnnotationMetadata
    Curator
    Annotation
    Observation
    Sandbox
    JObject
    Observation
"""

import json
from collections import namedtuple

import os
import re
import warnings
import contextlib
import gzip
import six

import numpy as np
import pandas as pd
import jsonschema
from sortedcontainers import SortedKeyList
from decorator import decorator

from .version import version as __VERSION__
from . import schema
from .exceptions import JamsError, SchemaError, ParameterError


__all__ = ['load',
           'JObject', 'Sandbox',
           'Annotation', 'Curator', 'AnnotationMetadata',
           'FileMetadata', 'AnnotationArray', 'JAMS',
           'Observation']


def deprecated(version, version_removed):
    '''This is a decorator which can be used to mark functions
    as deprecated.

    It will result in a warning being emitted when the function is used.'''

    def __wrapper(func, *args, **kwargs):
        '''Warn the user, and then proceed.'''
        code = six.get_function_code(func)
        warnings.warn_explicit(
            "{:s}.{:s}\n\tDeprecated as of JAMS version {:s}."
            "\n\tIt will be removed in JAMS version {:s}."
            .format(func.__module__, func.__name__,
                    version, version_removed),
            category=DeprecationWarning,
            filename=code.co_filename,
            lineno=code.co_firstlineno + 1
        )
        return func(*args, **kwargs)

    return decorator(__wrapper)


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
            raise ParameterError('Unknown JAMS extension '
                                 'format: "{:s}"'.format(ext))

    else:
        # Don't know how to handle this. Raise a parameter error
        raise ParameterError('Invalid filename or '
                             'descriptor: {}'.format(name_or_fdesc))


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
        '''
        return schema.JAMS_SCHEMA['definitions'].get(self.type, None)

    @property
    def __json__(self):
        r"""Return the JObject as a set of native data types for serialization.

        Note: attributes beginning with underscores are suppressed.
        """
        filtered_dict = dict()

        for k, item in six.iteritems(self.__dict__):
            if k.startswith('_'):
                continue

            if hasattr(item, '__json__'):
                filtered_dict[k] = item.__json__
            else:
                filtered_dict[k] = serialize_obj(item)

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
        if self.__schema__ is not None:
            props = self.__schema__['properties']
            if name not in props:
                raise SchemaError("Attribute {} not in {}"
                                  .format(name, props.keys()))
        self.__dict__[name] = value

    def __contains__(self, key):
        return key in self.__dict__

    def __len__(self):
        return len(self.keys())

    def __repr__(self):
        """Render the object alongside its attributes."""
        indent = len(self.type) + 2
        jstr = ',\n' + ' ' * indent

        props = self._display_properties()

        params = jstr.join('{:}={:}'.format(p, summary(self[p],
                                                       indent=indent))
                           for (p, dp) in props)
        return '<{}({:})>'.format(self.type, params)

    def _display_properties(self):
        '''Returns a list of tuples (key, display_name)
        for properties of this object'''

        return sorted([(k, k) for k in self.__dict__])

    def _repr_html_(self):

        props = self._display_properties()

        if not props:
            return ''

        out = '<div class="panel-group">'
        for (prop, dprop) in props:
            content = summary_html(self[prop])

            prop_class = 'default'
            if not content:
                prop_class = 'danger'

            out += '<div class="panel panel-{}">'.format(prop_class)

            if (isinstance(self[prop], (JObject, AnnotationArray, dict))
               and content):
                # These classes should have collapses
                div_id = _get_divid(self[prop])

                out += r'''<div class="panel-heading" role="tab" id="heading-{0}">
                            <button
                                type="button"
                                data-toggle="collapse"
                                data-parent="#accordion"
                                href="#{0}"
                                aria-expanded="false"
                                class="collapsed btn btn-block btn-primary"
                                aria-controls="{0}">
                                {1:s}'''.format(div_id, dprop)

                if isinstance(self[prop], AnnotationArray):
                    out += r'''<span class="badge pull-right">
                                    {:d}
                               </span>'''.format(len(self[prop]))

                out += r''' </button></div>'''

                if content:
                    out += r'''<div class="panel-collapse collapse"
                                    id="{0}"
                                    role="tabpanel"
                                    aria-labelledby="hading{0}">
                                    <div class="panel-body">
                                        {1}
                                    </div>
                                </div>'''.format(div_id, content)
            else:
                out += r'''<div class="panel-heading">
                                {}&nbsp;
                                <span class="pull-right"><em>{}</em></span>
                           </div>'''.format(dprop, content)
            out += '</div>'
        out += '</div>'

        return out

    def __summary__(self):
        return '<{}(...)>'.format(self.type)

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

            `value` must be either an object (tested for equality), a
            string describing a search pattern (regular expression), or a
            lambda function which evaluates to `True` if the candidate
            object matches the search criteria and `False` otherwise.

        Returns
        -------
        match : bool
            `True` if any of the search keys match the specified value,
            `False` otherwise, or if the search keys do not exist
            within the object.

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
            schema.VALIDATOR.validate(self.__json__, self.__schema__)

        except jsonschema.ValidationError as invalid:
            if strict:
                raise SchemaError(str(invalid))
            else:
                warnings.warn(str(invalid))

            valid = False

        return valid


Observation = namedtuple('Observation',
                         ['time', 'duration', 'value', 'confidence'])
'''Core observation type: (time, duration, value, confidence).'''


class Sandbox(JObject):
    """Sandbox (unconstrained)

    Functionally identical to JObjects, but the class hierarchy might be
    confusing if all objects inherit from Sandboxes."""
    pass


class Annotation(JObject):
    """Annotation base class."""

    def __init__(self, namespace, data=None, annotation_metadata=None,
                 sandbox=None, time=0, duration=None):
        """Create an Annotation.

        Note that, if an argument is None, an empty Annotation is created in
        its place. Additionally, a dictionary matching the expected structure
        of the arguments will be parsed (i.e. instantiating from JSON).

        Parameters
        ----------
        namespace : str
            The namespace for this annotation

        data : dict of lists, list of dicts, or list of Observations
            Data for the new annotation

        annotation_metadata : AnnotationMetadata (or dict), default=None.
            Metadata corresponding to this Annotation.

        sandbox : Sandbox (dict), default=None
            Miscellaneous information; keep to native datatypes if possible.

        time : non-negative number
            The starting time for this annotation

        duration : non-negative number
            The duration of this annotation
        """

        super(Annotation, self).__init__()

        if annotation_metadata is None:
            annotation_metadata = AnnotationMetadata()

        self.annotation_metadata = AnnotationMetadata(**annotation_metadata)

        self.namespace = namespace

        self.data = SortedKeyList(key=self._key)

        if data is not None:
            if isinstance(data, dict):
                self.append_columns(data)
            else:
                self.append_records(data)

        if sandbox is None:
            sandbox = Sandbox()

        self.sandbox = Sandbox(**sandbox)

        self.time = time
        self.duration = duration

    def _display_properties(self):
        return [('namespace', 'Namespace'),
                ('time', 'Time'),
                ('duration', 'Duration'),
                ('annotation_metadata', 'Annotation metadata'),
                ('data', 'Data'),
                ('sandbox', 'Sandbox')]

    def append(self, time=None, duration=None, value=None, confidence=None):
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

        Examples
        --------
        >>> ann = jams.Annotation(namespace='chord')
        >>> ann.append(time=3, duration=2, value='E#')
        '''

        self.data.add(Observation(time=float(time),
                                  duration=float(duration),
                                  value=value,
                                  confidence=confidence))

    def append_records(self, records):
        '''Add observations from row-major storage.

        This is primarily useful for deserializing sparsely packed data.

        Parameters
        ----------
        records : iterable of dicts or Observations
            Each element of `records` corresponds to one observation.
        '''
        for obs in records:
            if isinstance(obs, Observation):
                self.append(**obs._asdict())
            else:
                self.append(**obs)

    def append_columns(self, columns):
        '''Add observations from column-major storage.

        This is primarily used for deserializing densely packed data.

        Parameters
        ----------
        columns : dict of lists
            Keys must be `time, duration, value, confidence`,
            and each much be a list of equal length.

        '''
        self.append_records([dict(time=t, duration=d, value=v, confidence=c)
                             for (t, d, v, c)
                             in six.moves.zip(columns['time'],
                                              columns['duration'],
                                              columns['value'],
                                              columns['confidence'])])

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
            `False` if the object fails to conform to schema,
            but `strict == False`.

        Raises
        ------
        SchemaError
            If `strict == True` and the object fails validation

        See Also
        --------
        JObject.validate
        '''

        # Get the schema for this annotation
        ann_schema = schema.namespace_array(self.namespace)

        valid = True

        try:
            schema.VALIDATOR.validate(self.__json_light__(data=False),
                                                schema.JAMS_SCHEMA)

            # validate each record in the frame
            data_ser = [serialize_obj(obs) for obs in self.data]
            schema.VALIDATOR.validate(data_ser, ann_schema)

        except jsonschema.ValidationError as invalid:
            if strict:
                raise SchemaError(str(invalid))
            else:
                warnings.warn(str(invalid))
            valid = False

        return valid

    def trim(self, start_time, end_time, strict=False):
        '''
        Trim the annotation and return as a new `Annotation` object.

        Trimming will result in the new annotation only containing observations
        that occur in the intersection of the time range spanned by the
        annotation and the time range specified by the user. The new annotation
        will span the time range ``[trim_start, trim_end]`` where
        ``trim_start = max(self.time, start_time)`` and ``trim_end =
        min(self.time + self.duration, end_time)``.

        If ``strict=False`` (default) observations that start before
        ``trim_start`` and end after it will be trimmed such that they start at
        ``trim_start``, and similarly observations that start before
        ``trim_end`` and end after it will be trimmed to end at ``trim_end``.
        If ``strict=True`` such borderline observations will be discarded.

        The new duration of the annotation will be ``trim_end - trim_start``.

        Note that if the range defined by ``[start_time, end_time]``
        doesn't intersect with the original time range spanned by the
        annotation the resulting annotation will contain no observations, will
        have the same start time as the original annotation and have duration
        0.

        This function also copies over all the annotation metadata from the
        original annotation and documents the trim operation by adding a list
        of tuples to the annotation's sandbox keyed by
        ``Annotation.sandbox.trim`` which documents each trim operation with a
        tuple ``(start_time, end_time, trim_start, trim_end)``.

        Parameters
        ----------
        start_time : float
            The desired start time for the trimmed annotation in seconds.
        end_time
            The desired end time for the trimmed annotation in seconds. Must be
            greater than ``start_time``.
        strict : bool
            When ``False`` (default) observations that lie at the boundaries of
            the trimming range (given by ``[trim_start, trim_end]`` as
            described above), i.e. observations that start before and end after
            either the trim start or end time, will have their time and/or
            duration adjusted such that only the part of the observation that
            lies within the trim range is kept. When ``True`` such observations
            are discarded and not included in the trimmed annotation.

        Returns
        -------
        ann_trimmed : Annotation
            The trimmed annotation, returned as a new jams.Annotation object.
            If the trim range specified by ``[start_time, end_time]`` does not
            intersect at all with the original time range of the annotation a
            warning will be issued and the returned annotation will be empty.

        Raises
        ------
        ParameterError
            If ``end_time`` is not greater than ``start_time``.

        Examples
        --------
        >>> ann = jams.Annotation(namespace='tag_open', time=2, duration=8)
        >>> ann.append(time=2, duration=2, value='one')
        >>> ann.append(time=4, duration=2, value='two')
        >>> ann.append(time=6, duration=2, value='three')
        >>> ann.append(time=7, duration=2, value='four')
        >>> ann.append(time=8, duration=2, value='five')
        >>> ann_trim = ann.trim(5, 8, strict=False)
        >>> print(ann_trim.time, ann_trim.duration)
        (5, 3)
        >>> ann_trim.to_dataframe()
           time  duration  value confidence
        0     5         1    two       None
        1     6         2  three       None
        2     7         1   four       None
        >>> ann_trim_strict = ann.trim(5, 8, strict=True)
        >>> print(ann_trim_strict.time, ann_trim_strict.duration)
        (5, 3)
        >>> ann_trim_strict.to_dataframe()
           time  duration  value confidence
        0     6         2  three       None
        '''
        # Check for basic start_time and end_time validity
        if end_time <= start_time:
            raise ParameterError(
                'end_time must be greater than start_time.')

        # If the annotation does not have a set duration value, we'll assume
        # trimming is possible (up to the user to ensure this is valid).
        if self.duration is None:
            orig_time = start_time
            orig_duration = end_time - start_time
            warnings.warn(
                "Annotation.duration is not defined, cannot check "
                "for temporal intersection, assuming the annotation "
                "is valid between start_time and end_time.")
        else:
            orig_time = self.time
            orig_duration = self.duration

        # Check whether there is intersection between the trim range and
        # annotation: if not raise a warning and set trim_start and trim_end
        # appropriately.
        if start_time > (orig_time + orig_duration) or (end_time < orig_time):
            warnings.warn(
                'Time range defined by [start_time,end_time] does not '
                'intersect with the time range spanned by this annotation, '
                'the trimmed annotation will be empty.')
            trim_start = self.time
            trim_end = trim_start
        else:
            # Determine new range
            trim_start = max(orig_time, start_time)
            trim_end = min(orig_time + orig_duration, end_time)

        # Create new annotation with same namespace/metadata
        ann_trimmed = Annotation(
            self.namespace,
            data=None,
            annotation_metadata=self.annotation_metadata,
            sandbox=self.sandbox,
            time=trim_start,
            duration=trim_end - trim_start)

        # Selectively add observations based on their start time / duration
        # We do this rather than copying and directly manipulating the
        # annotation' data frame (which might be faster) since this way trim is
        # independent of the internal data representation.
        for obs in self.data:

            obs_start = obs.time
            obs_end = obs_start + obs.duration

            # Special-case here handles duration=0 as a closed interval
            if obs_start < trim_end and (obs_end > trim_start or obs_start == obs_end >= trim_start):

                new_start = max(obs_start, trim_start)
                new_end = min(obs_end, trim_end)
                new_duration = new_end - new_start

                if ((not strict) or
                        (new_start == obs_start and new_end == obs_end)):
                    ann_trimmed.append(time=new_start,
                                       duration=new_duration,
                                       value=obs.value,
                                       confidence=obs.confidence)

        if 'trim' not in ann_trimmed.sandbox.keys():
            ann_trimmed.sandbox.update(
                trim=[{'start_time': start_time, 'end_time': end_time,
                       'trim_start': trim_start, 'trim_end': trim_end}])
        else:
            ann_trimmed.sandbox.trim.append(
                {'start_time': start_time, 'end_time': end_time,
                 'trim_start': trim_start, 'trim_end': trim_end})

        return ann_trimmed

    def slice(self, start_time, end_time, strict=False):
        '''
        Slice the annotation and return as a new `Annotation` object.

        Slicing has the same effect as trimming (see `Annotation.trim`) except
        that while trimming does not modify the start time of the annotation or
        the observations it contains, slicing will set the new annotation's
        start time to ``max(0, trimmed_annotation.time - start_time)`` and the
        start time of its observations will be set with respect to this new
        reference start time.

        This function documents the slice operation by adding a list of tuples
        to the annotation's sandbox keyed by ``Annotation.sandbox.slice`` which
        documents each slice operation with a tuple
        ``(start_time, end_time, slice_start, slice_end)``, where
        ``slice_start`` and ``slice_end`` are given by ``trim_start`` and
        ``trim_end`` (see `Annotation.trim`).

        Since slicing is implemented  using trimming, the trimming operation
        will also be documented in ``Annotation.sandbox.trim`` as described in
        `Annotation.trim`.

        This function is useful for example when trimming an audio file,
        allowing the user to trim the annotation while ensuring all time
        information matches the new trimmed audio file.

        Parameters
        ----------
        start_time : float
            The desired start time for slicing in seconds.
        end_time
            The desired end time for slicing in seconds. Must be greater than
            ``start_time``.
        strict : bool
            When ``False`` (default) observations that lie at the boundaries of
            the slice (see `Annotation.trim` for details) will have their time
            and/or duration adjusted such that only the part of the observation
            that lies within the slice range is kept. When ``True`` such
            observations are discarded and not included in the sliced
            annotation.

        Returns
        -------
        sliced_ann : Annotation
            The sliced annotation.

        See Also
        --------
        Annotation.trim

        Examples
        --------
        >>> ann = jams.Annotation(namespace='tag_open', time=2, duration=8)
        >>> ann.append(time=2, duration=2, value='one')
        >>> ann.append(time=4, duration=2, value='two')
        >>> ann.append(time=6, duration=2, value='three')
        >>> ann.append(time=7, duration=2, value='four')
        >>> ann.append(time=8, duration=2, value='five')
        >>> ann_slice = ann.slice(5, 8, strict=False)
        >>> print(ann_slice.time, ann_slice.duration)
        (0, 3)
        >>> ann_slice.to_dataframe()
           time  duration  value confidence
        0   0.0       1.0    two       None
        1   1.0       2.0  three       None
        2   2.0       1.0   four       None
        >>> ann_slice_strict = ann.slice(5, 8, strict=True)
        >>> print(ann_slice_strict.time, ann_slice_strict.duration)
        (0, 3)
        >>> ann_slice_strict.to_dataframe()
           time  duration  value confidence
        0   1.0       2.0  three       None
        '''
        # start by trimming the annotation
        sliced_ann = self.trim(start_time, end_time, strict=strict)
        raw_data = sliced_ann.pop_data()

        # now adjust the start time of the annotation and the observations it
        # contains.

        for obs in raw_data:
            new_time = max(0, obs.time - start_time)
            # if obs.time > start_time,
            #   duration doesn't change
            # if obs.time < start_time,
            #   duration shrinks by start_time - obs.time
            sliced_ann.append(time=new_time,
                              duration=obs.duration,
                              value=obs.value,
                              confidence=obs.confidence)

        ref_time = sliced_ann.time
        slice_start = ref_time
        slice_end = ref_time + sliced_ann.duration

        if 'slice' not in sliced_ann.sandbox.keys():
            sliced_ann.sandbox.update(
                slice=[{'start_time': start_time, 'end_time': end_time,
                        'slice_start': slice_start, 'slice_end': slice_end}])
        else:
            sliced_ann.sandbox.slice.append(
                {'start_time': start_time, 'end_time': end_time,
                 'slice_start': slice_start, 'slice_end': slice_end})

        # Update the timing for the sliced annotation
        sliced_ann.time = max(0, ref_time - start_time)

        return sliced_ann

    def pop_data(self):
        '''Replace this observation's data with a fresh container.

        Returns
        -------
        annotation_data : SortedKeyList
            The original annotation data container
        '''

        data = self.data
        self.data = SortedKeyList(key=self._key)
        return data

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

        ints, vals = [], []
        for obs in self.data:
            ints.append([obs.time, obs.time + obs.duration])
            vals.append(obs.value)

        if not ints:
            return np.empty(shape=(0, 2), dtype=float), []

        return np.array(ints), vals

    def to_event_values(self):
        '''Extract observation data in a `mir_eval`-friendly format.

        Returns
        -------
        times : np.ndarray [shape=(n,), dtype=float]
            Start-time of all observations

        labels : list
            List view of value field.
        '''
        ints, vals = [], []
        for obs in self.data:
            ints.append(obs.time)
            vals.append(obs.value)

        return np.array(ints), vals

    def to_dataframe(self):
        '''Convert this annotation to a pandas dataframe.

        Returns
        -------
        df : pd.DataFrame
            Columns are `time, duration, value, confidence`.
            Each row is an observation, and rows are sorted by
            ascending `time`.
        '''
        return pd.DataFrame.from_records(list(self.data),
                                         columns=['time', 'duration',
                                                  'value', 'confidence'])

    def to_samples(self, times, confidence=False):
        '''Sample the annotation at specified times.

        Parameters
        ----------
        times : np.ndarray, non-negative, ndim=1
            The times (in seconds) to sample the annotation

        confidence : bool
            If `True`, return both values and confidences.
            If `False` (default) only return values.

        Returns
        -------
        values : list
            `values[i]` is a list of observation values for intervals
            that cover `times[i]`.

        confidence : list (optional)
            `confidence` values corresponding to `values`
        '''
        times = np.asarray(times)
        if times.ndim != 1 or np.any(times < 0):
            raise ParameterError('times must be 1-dimensional and non-negative')

        idx = np.argsort(times)
        samples = times[idx]

        values = [list() for _ in samples]
        confidences = [list() for _ in samples]

        for obs in self.data:
            start = np.searchsorted(samples, obs.time)
            end = np.searchsorted(samples, obs.time + obs.duration, side='right')
            for i in range(start, end):
                values[idx[i]].append(obs.value)
                confidences[idx[i]].append(obs.confidence)

        if confidence:
            return values, confidences
        else:
            return values

    def __iter__(self):
        return iter(self.data)

    def to_html(self, max_rows=None):
        '''Render this annotation list in HTML

        Returns
        -------
        rendered : str
            An HTML table containing this annotation's data.
        '''
        n = len(self.data)

        div_id = _get_divid(self)

        out = r'''  <div class="panel panel-default">
                        <div class="panel-heading" role="tab" id="heading-{0}">
                            <button
                                type="button"
                                data-toggle="collapse"
                                data-parent="#accordion"
                                href="#{0}"
                                aria-expanded="false"
                                class="collapsed btn btn-info btn-block"
                                aria-controls="{0}">
                                {1:s}
                                <span class="badge pull-right">{2:d}</span>
                            </button>
                        </div>'''.format(div_id, self.namespace, n)

        out += r'''     <div id="{0}" class="panel-collapse collapse"
                             role="tabpanel" aria-labelledby="heading-{0}">
                            <div class="panel-body">'''.format(div_id)

        out += r'''<div class="pull-right">
                        {}
                    </div>'''.format(self.annotation_metadata._repr_html_())
        out += r'''<div class="pull-right clearfix">
                        {}
                    </div>'''.format(self.sandbox._repr_html_())

        # -- Annotation content starts here
        out += r'''<div><table border="1" class="dataframe">
                    <thead>
                        <tr style="text-align: right;">
                            <th></th>
                            <th>time</th>
                            <th>duration</th>
                            <th>value</th>
                            <th>confidence</th>
                        </tr>
                    </thead>'''.format(self.namespace, n)

        out += r'''<tbody>'''

        if max_rows is None or n <= max_rows:
            out += self._fmt_rows(0, n)
        else:
            out += self._fmt_rows(0, max_rows//2)
            out += r'''<tr>
                            <th>...</th>
                            <td>...</td>
                            <td>...</td>
                            <td>...</td>
                            <td>...</td>
                        </tr>'''
            out += self._fmt_rows(n-max_rows//2, n)

        out += r'''</tbody>'''

        out += r'''</table></div>'''

        out += r'''</div></div></div>'''
        return out

    def _fmt_rows(self, start, end):
        out = ''
        for i, obs in enumerate(self.data[start:end], start):
            out += r'''<tr>
                            <th>{:d}</th>
                            <td>{:0.3f}</td>
                            <td>{:0.3f}</td>
                            <td>{:}</td>
                            <td>{:}</td>
                        </tr>'''.format(i,
                                        obs.time,
                                        obs.duration,
                                        summary_html(obs.value),
                                        summary_html(obs.confidence))

        return out

    def _repr_html_(self, max_rows=25):
        '''Render annotation as HTML.  See also: `to_html()`'''
        return self.to_html(max_rows=max_rows)

    @property
    def __json__(self):
        return self.__json_light__(data=True)

    def __json_light__(self, data=True):
        r"""Return the JObject as a set of native data types for serialization.

        Note: attributes beginning with underscores are suppressed.
        """
        filtered_dict = dict()

        for k, item in six.iteritems(self.__dict__):
            if k.startswith('_'):
                continue
            elif k == 'data':
                if data:
                    filtered_dict[k] = self.__json_data__
                else:
                    filtered_dict[k] = []

            elif hasattr(item, '__json__'):
                filtered_dict[k] = item.__json__
            else:
                filtered_dict[k] = item

        return filtered_dict

    @property
    def __json_data__(self):
        r"""JSON-serialize the observation sequence."""
        if schema.is_dense(self.namespace):
            dense_records = dict()
            for field in Observation._fields:
                dense_records[field] = []

            for obs in self.data:
                for key, val in six.iteritems(obs._asdict()):
                    dense_records[key].append(serialize_obj(val))

            return dense_records

        else:
            return [serialize_obj(_) for _ in self.data]

    @classmethod
    def _key(cls, obs):
        '''Provides sorting index for Observation objects'''
        if not isinstance(obs, Observation):
            raise JamsError('{} must be of type jams.Observation'.format(obs))

        return obs.time


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

    def _display_properties(self):
        return [('name', 'Name'), ('email', 'Email')]


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

    def _display_properties(self):
        return [('annotator', 'Annotator'),
                ('version', 'Version'),
                ('corpus', 'Corpus'),
                ('curator', 'Curator'),
                ('annotation_tools', 'Annotation tools'),
                ('annotation_rules', 'Annotation rules'),
                ('data_source', 'Data source'),
                ('validation', 'Validation')]


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

    def _display_properties(self):
        return [('artist', 'Artist'),
                ('title', 'Title'),
                ('release', 'Release'),
                ('duration', 'Duration (s)'),
                ('jams_version', 'JAMS version'),
                ('identifiers', 'Identifiers')]


class AnnotationArray(list):
    """AnnotationArray

    This list subclass provides serialization and search/filtering
    for annotation collections.

    Fancy-indexing can be used to directly search for annotations
    belonging to a particular namespace.  Three types of indexing
    are supported:

    - integer or slice : acts just as in `list`, e.g., `arr[0]` or `arr[1:3]`
    - string : acts like a search, e.g.,
      `arr['beat'] == arr.search(namespace='beat')`
    - (string, integer or slice) acts like a search followed by index/slice

    Examples
    --------
    >>> # Retrieve the first annotation with simple indexing
    >>> ann = jam.annotations[0]

    >>> # Retrieve the first three annotations
    >>> anns = jam.annotations[:3]

    >>> # Retrieve a list of beat annotations
    >>> # equivalent to jam.search(namespace='beat')
    >>> beat_anns = jam.annotations['beat']

    >>> # Retrieve the second beat annotation
    >>> # equivalent to jam.search(namespace='beat')[1]
    >>> beat2 = jam.annotations['beat', 1]

    >>> # Retrieve everything after the second salami annotation
    >>> seg_anns = jam.annotations['segment_salami_.*', 2:]
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

    def __getitem__(self, idx):
        '''Overloaded getitem for syntactic search sugar'''

        # if we have only one argument, it can be an int, slice or query
        if isinstance(idx, (int, slice)):
            return list.__getitem__(self, idx)
        elif isinstance(idx, six.string_types) or six.callable(idx):
            return self.search(namespace=idx)
        elif isinstance(idx, tuple):
            return self.search(namespace=idx[0])[idx[1]]
        raise IndexError('Invalid index: {}'.format(idx))

    @property
    def __json__(self):
        return [item.__json__ for item in self]

    def trim(self, start_time, end_time, strict=False):
        '''
        Trim every annotation contained in the annotation array using
        `Annotation.trim` and return as a new `AnnotationArray`.

        See `Annotation.trim` for details about trimming. This function does
        not modify the annotations in the original annotation array.


        Parameters
        ----------
        start_time : float
            The desired start time for the trimmed annotations in seconds.
        end_time
            The desired end time for trimmed annotations in seconds. Must be
            greater than ``start_time``.
        strict : bool
            When ``False`` (default) observations that lie at the boundaries of
            the trimming range (see `Annotation.trim` for details) will have
            their time and/or duration adjusted such that only the part of the
            observation that lies within the trim range is kept. When ``True``
            such observations are discarded and not included in the trimmed
            annotation.

        Returns
        -------
        trimmed_array : AnnotationArray
            An annotation array where every annotation has been trimmed.
        '''
        trimmed_array = AnnotationArray()
        for ann in self:
            trimmed_array.append(ann.trim(start_time, end_time, strict=strict))

        return trimmed_array

    def slice(self, start_time, end_time, strict=False):
        '''
        Slice every annotation contained in the annotation array using
        `Annotation.slice`
        and return as a new AnnotationArray

        See `Annotation.slice` for details about slicing. This function does
        not modify the annotations in the original annotation array.

        Parameters
        ----------
        start_time : float
            The desired start time for slicing in seconds.
        end_time
            The desired end time for slicing in seconds. Must be greater than
            ``start_time``.
        strict : bool
            When ``False`` (default) observations that lie at the boundaries of
            the slicing range (see `Annotation.slice` for details) will have
            their time and/or duration adjusted such that only the part of the
            observation that lies within the trim range is kept. When ``True``
            such observations are discarded and not included in the sliced
            annotation.

        Returns
        -------
        sliced_array : AnnotationArray
            An annotation array where every annotation has been sliced.
        '''
        sliced_array = AnnotationArray()
        for ann in self:
            sliced_array.append(ann.slice(start_time, end_time, strict=strict))

        return sliced_array

    def __repr__(self):
        n = len(self)

        if n == 1:
            return '[1 annotation]'
        else:
            return '[{:d} annotations]'.format(n)

    def _repr_html_(self):
        out = ''
        for ann in self:
            out += '<div class="panel-group">{}</div>'.format(ann._repr_html_())
        return out


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

    def _display_properties(self):
        return [('file_metadata', 'File Metadata'),
                ('annotations', 'Annotations'),
                ('sandbox', 'Sandbox')]

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
        valid = True
        try:
            schema.VALIDATOR.validate(self.__json_light__, schema.JAMS_SCHEMA)

            for ann in self.annotations:
                if isinstance(ann, Annotation):
                    valid &= ann.validate(strict=strict)
                else:
                    msg = '{} is not a well-formed JAMS Annotation'.format(ann)
                    valid = False
                    if strict:
                        raise SchemaError(msg)
                    else:
                        warnings.warn(str(msg))

        except jsonschema.ValidationError as invalid:
            if strict:
                raise SchemaError(str(invalid))
            else:
                warnings.warn(str(invalid))

            valid = False

        return valid

    def trim(self, start_time, end_time, strict=False):
        '''
        Trim all the annotations inside the jam and return as a new `JAMS`
        object.

        See `Annotation.trim` for details about how the annotations
        are trimmed.

        This operation is also documented in the jam-level sandbox
        with a list keyed by ``JAMS.sandbox.trim`` containing a tuple for each
        jam-level trim of the form ``(start_time, end_time)``.

        This function also copies over all of the file metadata from the
        original jam.

        Note: trimming does not affect the duration of the jam, i.e. the value
        of ``JAMS.file_metadata.duration`` will be the same for the original
        and trimmed jams.

        Parameters
        ----------
        start_time : float
            The desired start time for the trimmed annotations in seconds.
        end_time
            The desired end time for trimmed annotations in seconds. Must be
            greater than ``start_time``.
        strict : bool
            When ``False`` (default) observations that lie at the boundaries of
            the trimming range (see `Annotation.trim` for details), will have
            their time and/or duration adjusted such that only the part of the
            observation that lies within the trim range is kept. When ``True``
            such observations are discarded and not included in the trimmed
            annotation.

        Returns
        -------
        jam_trimmed : JAMS
            The trimmed jam with trimmed annotations, returned as a new JAMS
            object.

        '''
        # Make sure duration is set in file metadata
        if self.file_metadata.duration is None:
            raise JamsError(
                'Duration must be set (jam.file_metadata.duration) before '
                'trimming can be performed.')

        # Make sure start and end times are within the file start/end times
        if not (0 <= start_time <= end_time <= float(
                self.file_metadata.duration)):
            raise ParameterError(
                'start_time and end_time must be within the original file '
                'duration ({:f}) and end_time cannot be smaller than '
                'start_time.'.format(float(self.file_metadata.duration)))

        # Create a new jams
        jam_trimmed = JAMS(annotations=None,
                           file_metadata=self.file_metadata,
                           sandbox=self.sandbox)

        # trim annotations
        jam_trimmed.annotations = self.annotations.trim(
            start_time, end_time, strict=strict)

        # Document jam-level trim in top level sandbox
        if 'trim' not in jam_trimmed.sandbox.keys():
            jam_trimmed.sandbox.update(
                trim=[{'start_time': start_time, 'end_time': end_time}])
        else:
            jam_trimmed.sandbox.trim.append(
                {'start_time': start_time, 'end_time': end_time})

        return jam_trimmed

    def slice(self, start_time, end_time, strict=False):
        '''
        Slice all the annotations inside the jam and return as a new `JAMS`
        object.

        See `Annotation.slice` for details about how the annotations
        are sliced.

        This operation is also documented in the jam-level sandbox
        with a list keyed by ``JAMS.sandbox.slice`` containing a tuple for each
        jam-level slice of the form ``(start_time, end_time)``.

        Since slicing is implemented using trimming, the operation will also be
        documented in ``JAMS.sandbox.trim`` as described in `JAMS.trim`.

        This function also copies over all of the file metadata from the
        original jam.

        Note: slicing will affect the duration of the jam, i.e. the new value
        of ``JAMS.file_metadata.duration`` will be ``end_time - start_time``.

        Parameters
        ----------
        start_time : float
            The desired start time for slicing in seconds.
        end_time
            The desired end time for slicing in seconds. Must be greater than
            ``start_time``.
        strict : bool
            When ``False`` (default) observations that lie at the boundaries of
            the slicing range (see `Annotation.slice` for details), will have
            their time and/or duration adjusted such that only the part of the
            observation that lies within the slice range is kept. When ``True``
            such observations are discarded and not included in the sliced
            annotation.

        Returns
        -------
        jam_sliced: JAMS
            The sliced jam with sliced annotations, returned as a new
            JAMS object.

        '''
        # Make sure duration is set in file metadata
        if self.file_metadata.duration is None:
            raise JamsError(
                'Duration must be set (jam.file_metadata.duration) before '
                'slicing can be performed.')

        # Make sure start and end times are within the file start/end times
        if (start_time < 0 or
                start_time > float(self.file_metadata.duration) or
                end_time < start_time or
                end_time > float(self.file_metadata.duration)):
            raise ParameterError(
                'start_time and end_time must be within the original file '
                'duration ({:f}) and end_time cannot be smaller than '
                'start_time.'.format(float(self.file_metadata.duration)))

        # Create a new jams
        jam_sliced = JAMS(annotations=None,
                          file_metadata=self.file_metadata,
                          sandbox=self.sandbox)

        # trim annotations
        jam_sliced.annotations = self.annotations.slice(
            start_time, end_time, strict=strict)

        # adjust dutation
        jam_sliced.file_metadata.duration = end_time - start_time

        # Document jam-level trim in top level sandbox
        if 'slice' not in jam_sliced.sandbox.keys():
            jam_sliced.sandbox.update(
                slice=[{'start_time': start_time, 'end_time': end_time}])
        else:
            jam_sliced.sandbox.slice.append(
                {'start_time': start_time, 'end_time': end_time})

        return jam_sliced

    @property
    def __json_light__(self):
        r"""Return the JObject as a set of native data types for serialization.

        Note: attributes beginning with underscores are suppressed.

        This also skips the `annotations` field, which will be validated separately.
        """
        filtered_dict = dict()

        for k, item in six.iteritems(self.__dict__):
            if k.startswith('_') or k == 'annotations':
                continue

            if hasattr(item, '__json__'):
                filtered_dict[k] = item.__json__
            else:
                filtered_dict[k] = serialize_obj(item)

        return filtered_dict


# -- Helper functions -- #
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

    elif (isinstance(query, six.string_types) and
          isinstance(string, six.string_types)):
        return re.match(query, string) is not None

    else:
        return query == string


def serialize_obj(obj):
    '''Custom serialization functionality for working with advanced data types.

    - numpy arrays are converted to lists
    - lists are recursively serialized element-wise

    '''

    if isinstance(obj, np.integer):
        return int(obj)

    elif isinstance(obj, np.floating):
        return float(obj)

    elif isinstance(obj, np.ndarray):
        return obj.tolist()

    elif isinstance(obj, list):
        return [serialize_obj(x) for x in obj]

    elif isinstance(obj, Observation):
        return {k: serialize_obj(v) for k, v in six.iteritems(obj._asdict())}

    return obj


def summary(obj, indent=0):
    '''Helper function to format repr strings for JObjects and friends.

    Parameters
    ----------
    obj
        The object to repr

    indent : int >= 0
        indent each new line by `indent` spaces

    Returns
    -------
    r : str
        If `obj` has a `__summary__` method, it is used.

        If `obj` is a `SortedKeyList`, then it returns a description
        of the length of the list.

        Otherwise, `repr(obj)`.
    '''
    if hasattr(obj, '__summary__'):
        rep = obj.__summary__()
    elif isinstance(obj, SortedKeyList):
        rep = '<{:d} observations>'.format(len(obj))
    else:
        rep = repr(obj)

    return rep.replace('\n', '\n' + ' ' * indent)


def summary_html(obj):

    if hasattr(obj, '_repr_html_'):
        return obj._repr_html_()
    elif isinstance(obj, dict):
        out = '<table class="table"><tbody>'
        for key in obj:
            out += r''' <tr>
                            <th scope="row">{0}</th>
                            <td>{1}</td>
                        </tr>'''.format(key, summary_html(obj[key]))
        out += '</tbody></table>'
        return out
    elif isinstance(obj, list):
        return ''.join([summary_html(x) for x in obj])
    else:
        return str(obj)


__DIVID_COUNT__ = 0


def _get_divid(obj):
    '''Static function to get a unique id for an object.
    This is used in HTML rendering to ensure unique div ids for each call
    to display an object'''

    global __DIVID_COUNT__
    __DIVID_COUNT__ += 1
    return '{}-{}'.format(id(obj), __DIVID_COUNT__)
