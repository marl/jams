"""
JAMS Mongo API
==============

This library provides an interface for interfacing with a JAMS Mongo
instance.

"""

import pymongo


class JamsMongo(object):
    """Model class for interfacing with JAMS Mongo Collection."""

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

    @property
    def audio(self):
        """Return a pointer to the audio collection."""
        return self._db['audio']

    @property
    def annotations(self):
        """Return a pointer to the annotations collection."""
        return self._annotations['annotations']

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
        audio_id = self.insert_jams_metadata(jams_object.file_metadata)

        # Extract the JAMS Annotations and prepare them for mongification.
        annotation_list = self.convert_annotation_list(jams_object.annotations)

        # insert them into the Annotations collection.
        annotation_ids = self.insert_annotations(annotation_list, audio_id)

        # Optionally build the pivot table?
        self.build_pivot_map(audio_id, annotation_ids)

    def insert_jams_metadata(self, jams_metadata):
        """Insert a JAMS file_metadata into the "Audio" collection,
        and return the ObjectId for the item inserted.

        Parameters
        ----------
        jams_metadata : jams.FileMetadata

        Returns
        -------
        audio_id : ObjectId
            The ID for the object inserted into 'Audio'.
        """
        pass

    def convert_annotation_list(annotations_array):
        """Take a "Jams-document" style annotations array,
        and convert it into a mongo-able annotationsl list.

        Parameters
        ----------
        annotations_list : jams.AnnotationArray

        Returns
        -------
        converted_annotations : list
        """
        return []

    def insert_annotations(self, mongified_annotations_array, audio_id):
        """Take an already mongo-prepared annotations array and insert all of
        the documents into 'annotations'.

        Parameters
        ----------
        mongified_annotations_array : list of Annotations
            List of Annoation documents ready for mongo.

        audio_id : ObjectId
            ID pointing to the source metadata.

        Returns
        -------
        annotation_ids : list of ObjectId
            List of IDs pointing to the new Annotation documents.
        """
        pass

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
