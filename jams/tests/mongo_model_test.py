import mongomock
from nose.tools import raises, eq_

import jams
from jams.mongo_model import JamsMongo


def test_local_jamsmongo():
    """TODO: Bad idea?"""
    mongo = JamsMongo()
    assert mongo is not None


def test_mock_jamsmongo():
    mongo = JamsMongo(client=mongomock.MongoClient())
    assert mongo is not None


def test_context_manager():
    with JamsMongo(client=mongomock.MongoClient()) as mongo:
        assert mongo.db is not None

        assert isinstance(mongo.audio, mongomock.Collection)
        assert isinstance(mongo.annotations, mongomock.Collection)


def test_insert_jams_metadata():
    pass


def test_insert_annotations():
    pass


def test_build_pivot_map():
    pass


def test_import_jams():
    """Test the end-to-end"""
    pass
