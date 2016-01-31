from bson.objectid import ObjectId
import mongomock
from nose.tools import raises, eq_

import jams
from jams.jamongo import JamsMongo, convert_annotation_list


def test_local_jamsmongo():
    """TODO: Is this a bad idea?
    Maybe you don't want to have these tests rely on
    a local mongo instance."""
    mongo = JamsMongo()
    assert mongo is not None


def test_remote_jamsmongo():
    """TODO: Is this test useful? Don't know
    what you would actually connect to, but it would
    be nice to make sure you can do it."""
    connection_str = "mongodb://foo.bar.com:27017"
    mongo = JamsMongo(connection_str)
    assert mongo.connection_str == connection_str


def test_mock_jamsmongo():
    mongo = JamsMongo(client=mongomock.MongoClient())
    assert mongo is not None


def test_context_manager():
    with JamsMongo(client=mongomock.MongoClient()) as mongo:
        assert mongo.db is not None

        assert isinstance(mongo['audio'], mongomock.Collection)
        assert isinstance(mongo['annotations'], mongomock.Collection)

        yield raises(KeyError)(mongo.__getitem__), "fred"


def test_insert_jams_metadata():
    def __test(collection, new_id, expected):
        result = collection.find_one(new_id,
                                     projection={'_id': False})

        eq_(result, expected)

    # Load an example jam
    fn = 'fixtures/valid.jams'
    jam = jams.load(fn)
    expected = jam.file_metadata
    with JamsMongo(client=mongomock.MongoClient()) as mongo:
        new_id = mongo.insert_jams_metadata(expected.__json__)

        yield __test, mongo['audio'], new_id, expected.__json__


def test_convert_annotation_list():
    def __test(input_annotations, results, audio_id):

        assert isinstance(input_annotations, jams.AnnotationArray)

        for ref_ann, res_ann in zip(input_annotations, results):
            eq_(res_ann.audio_id, audio_id)

            ref = ref_ann.__json__
            out = res_ann.__json__

            # Clobber the audio_id for the rest of the equivalence test
            ref['audio_id'] = None
            out['audio_id'] = None
            eq_(jams.Annotation(**ref), jams.Annotation(**out))

    fn = 'fixtures/valid.jams'
    jam = jams.load(fn)

    garbage_id = ObjectId()
    result = convert_annotation_list(jam.annotations, garbage_id)

    yield __test, jam.annotations, result, garbage_id


def test_insert_annotations():
    def __test(collection, input_list, ids):
        cursor = collection.find({
            "_id": {"$in": ids}},
            projection={"_id": False})

        assert cursor.count() == len(input_list)

    garbage_annotations = [
        dict(garbage="in"),
        dict(garbage="out")
    ]

    with JamsMongo(client=mongomock.MongoClient()) as mongo:
        new_ids = mongo.insert_annotations(garbage_annotations)

        yield __test, mongo['annotations'], garbage_annotations, new_ids


def test_build_pivot_map():
    pass


def test_find_audio():
    def __test(created_ids, queried_ids):
        for aid in queried_ids:
            assert aid in created_ids

    dummy_audio_docs = [
        dict(title="Cannon in D", composer="Pachabel"),
        dict(title="Stairway to Heaven", artist="Led Zeppelin")
    ]

    input_ids = []
    with JamsMongo(client=mongomock.MongoClient()) as mongo:
        input_ids += [mongo.insert_jams_metadata(dummy_audio_docs[0])]
        input_ids += [mongo.insert_jams_metadata(dummy_audio_docs[1])]
        query_ids = mongo.find_audio({"artist": "Led Zeppelin"})
        yield __test, input_ids, query_ids


def test_query_annotations():
    def __test(created_ids, queried_ids):
        for aid in queried_ids:
            assert aid in created_ids

    # Todo... maybe real-er test exapmles...
    dummy_annotation_docs = [
        dict(foo="fred", bar="frank"),
        dict(foo="what", bar="happened")
    ]

    with JamsMongo(client=mongomock.MongoClient()) as mongo:
        input_ids = mongo.insert_annotations(dummy_annotation_docs)
        query_ids = mongo.find_annotations({"foo": "frank"})
        yield __test, input_ids, query_ids


def test_import_jams():
    """Test the end-to-end"""
    pass
