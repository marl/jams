"""
JAMS Mongo API
==============

This library provides an interface for interfacing with a JAMS Mongo
instance.

"""

from .core import AnnotationArray

import pymongo
from copy import deepcopy


def convert_annotation_list(annotations_array, audio_id):
    """Take a "Jams-document" style annotations array,
    and convert it into a mongo-able annotationsl list.

    Parameters
    ----------
    annotations_list : jams.AnnotationArray

    audio_id : ObjectId
        Pointer to an audio document.

    Returns
    -------
    converted_annotations : list of Annotation
    """
    anns = AnnotationArray()

    for _ann in annotations_array:
        ann = deepcopy(_ann)
        ann.audio_id = audio_id
        anns.append(anns)

    return anns


class JamsMongo(object):
    """Model class for interfacing with JAMS Mongo Collection."""
    _collections = ["audio", "annotations"]

    def __init__(self, connection_str=None,
                 client=None,
                 database_name="jams"):
        """
        Pass the parameters necessary to create a MongoClient connection to
        mongodb.

        If no parameters are provided, just tries to connect to your
        local mongod.

        Parameters
        ----------
        connection_str : str or None
            Mongo connection string.

        client : pymongo.mongo_client.MongoClient
            A MongoClient reference. Use this if you want to pass the client
            instead of having JamsMongo create the client for you from the
            connection_str.

            (This is useful for unit tests / mongomock.)

        database_name : str
            The name of the database to use on your client.
        """
        self.connection_str = connection_str
        self.client = client
        self.database_name = database_name
        self._db = None

    def __enter__(self):
        """Set up your mongo collection, and return the object to access it."""
        self._connect_to_mongo()
        return self

    def __exit__(self, type, value, traceback):
        pass

    @property
    def db(self):
        return self._db

    def __getitem__(self, key):
        """Get a collection object from the db, if it is an allowable
        collection specified."""
        if key in self._collections:
            return self._db[key]
        else:
            raise KeyError("Invalid collection: {}".format(key))

    def _connect_to_mongo(self):
        """Connect to mongo database using the connection string
        provided in the constructor.

        Sets self._db for access in future
        """
        if self.client is None:
            self.client = pymongo.MongoClient(self.connection_str)

        self._db = self.client[self.database_name]

    def import_jams(self, jams_object):
        """Import a JAMS object into mongo.

        Puts JAMS metadata into the "Audio" collection,
        and puts the Annotations into the "Annotations" collection.

        Parameters
        ----------
        jams_object : jams.JAMS
        """
        # Extract the JAMS metadata & insert it into the Audio collection
        audio_id = self.insert_jams_metadata(
            jams_object.file_metadata.__json__)

        # Extract the JAMS Annotations and prepare them for mongification.
        annotation_list = convert_annotation_list(
            jams_object.annotations, audio_id=audio_id)

        # insert them into the Annotations collection.
        annotation_ids = self.insert_annotations(annotation_list)

        # [Optionally] Build the pivot table
        self.build_pivot_map(audio_id, annotation_ids)

    def insert_jams_metadata(self, jams_metadata):
        """Insert a JAMS file_metadata into the "Audio" collection,
        and return the ObjectId for the item inserted.

        Parameters
        ----------
        jams_metadata : dict

        Returns
        -------
        audio_id : ObjectId
            The ID for the object inserted into 'Audio'.
        """
        result = self['audio'].insert_one(jams_metadata)
        return result.inserted_id

    def insert_annotations(self, mongified_annotations_array):
        """Take an already mongo-prepared annotations array and insert all of
        the documents into 'annotations'.

        Parameters
        ----------
        mongified_annotations_array : list of Annotations
            List of Annoation documents ready for mongo.

        Returns
        -------
        annotation_ids : list of ObjectId
            List of IDs pointing to the new Annotation documents.
        """
        result = self['annotations'].insert_many(mongified_annotations_array)
        return result.inserted_ids

    def insert_annotation(self, annotation):
        """Insert a single annotation into the annotation collection.

        Parameters
        ----------
        annotation : JAMongo Annotation (TODO)

        Returns
        -------
        annotation_id : ObjectId
            The new id created on insertion.
        """
        result_ids = self.insert_annotation([annotation])
        return result_ids[0]

    def build_pivot_map(self, audio_id, annotation_ids):
        """Build a pivot table of audio_id -> annotation_ids

        Parameters
        ----------
        audio_id : ObjectId
            ID pointing to a document in the 'audio' collection.

        annotation_ids : list of ObjectId
            IDs pointing to documents in the 'annotations' collection.

        Returns
        -------
        pivot_id : ObjectId
            Pointer to the new object in the pivot table.
        """
        pass

    def find_audio(self, query):
        """Query the audio collection for IDs.

        Parameters
        ----------
        query : dict
            Mongo query dict.

        Returns
        -------
        audio_ids : list of ObjectIds
            A list of ObjectIds pointing to the items
            returned by the query.
        """
        cursor = self['audio'].find(query,
                                    projection={'_id': True})
        return [x['_id'] for x in cursor]

    def find_annotations(self, query):
        """Query the annotations for IDs.

        Parameters
        ----------
        query : dict
            Mongo query dict.

        Returns
        -------
        annotation_ids : list of ObjectIds
            A list of ObjectIds pointing to the items
            returned by the query.
        """
        cursor = self['annotations'].find(
            query, projection={'_id': True})
        return [x['_id'] for x in cursor]

    def get_annotations_by_audio_id(self, audio_id):
        annotations = self['annotations'].find(
            query={"audio_id": {"$in": audio_id}})
        return annotations
