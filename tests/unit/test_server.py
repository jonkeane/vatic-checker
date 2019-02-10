import pytest

import sys, os, shutil, uuid
myPath = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, myPath + "/../../src/vatic_checker/") # move to the src directory

import server
import vatic_checker.model as model
from vatic_checker.handler import Error500

from sqlalchemy import and_, func, distinct, desc
from sqlalchemy.orm import aliased

from alchemy_mock.mocking import UnifiedAlchemyMagicMock, AlchemyMagicMock
import argparse
from unittest import TestCase

try:
    from unittest.mock import patch, call  # python 3.3+
except ImportError:
    from mock import patch, call # python 2.6-3.2

# current working directory
cwd = os.getcwd()

# mock the session object from cli so that the database isn't harmed.
untrained_user = model.User(
    guid=uuid.UUID("87599456d52b48b78a6b1b5b0ded7be1"),
    username="untrained",
    completed_training=False)

trained_user = model.User(
    guid=uuid.UUID("ea3f15f611084c3ba84b8068f5234928"),
    username="trained",
    completed_training=True)

finished_user = model.User(
    guid=uuid.UUID("465db3c5171a4ddc82ee35de3d31ab40"),
    username="finished",
    completed_training=True)

annotations_current_user = aliased(model.Annotation)
annotations_all = aliased(model.Annotation)

session = UnifiedAlchemyMagicMock(data = [
    (
        [call.query(model.TrainingVideo)],
        [model.TrainingVideo(id = 1),model.TrainingVideo(id = 2)]
    ),
    (
        [call.query(model.Video)],
        [model.Video(id = 1),model.Video(id = 2)]
    ),
    (
        [call.query(model.User), call.filter(model.User.guid == untrained_user.guid)],
        [untrained_user]
    ),
    (
        [call.query(model.User), call.filter(model.User.guid == trained_user.guid)],
        [trained_user]
    ),
    # for test_enough_annoed_videos
    (
        [call.query(model.Training.success, model.Training.video_id),
        call.group_by(model.Training.video_id),
        call.filter(model.Training.success == True, model.Training.user_guid == untrained_user.guid)],
        [model.TrainingVideo(id = 1)]
    ),
    (
        [call.query(model.Annotation),
         call.filter(model.Annotation.user_guid == trained_user.guid),
         call.subquery('sub')],
        [model.Annotation(video_id = 1)]
    ),
])

class TestHandler(TestCase):
    @patch('server.session', new=session)
    def test_training_warns_if_not_enough_training_videos(self):
        session.reset_mock()
        with pytest.raises(Error500) as e_info:
            status = server.check_training_completion(untrained_user, 100)

    @patch('server.session', new=session)
    def test_not_enough_annoed_videos(self):
        session.reset_mock()
        status = server.check_training_completion(untrained_user, 2)
        self.assertFalse(status)

    @patch('server.session', new=session)
    def test_enough_annoed_videos(self):
        session.reset_mock()
        status = server.check_training_completion(untrained_user, 1)
        self.assertTrue(status)

        # and there's a commit that is updating the user
        session.commit.assert_called_once()

    # this needs to be tested with get_next() not with check_training_completion
    # @patch('server.session', new=session)
    # def test_already_verified(self):
    #     session.reset_mock()
    #     status = server.check_training_completion(trained_user, 2)
    #     self.assertTrue(status)


    def test_parse_anno_sql_cleansing(self):
        new_guid = uuid.uuid4()
        postdata = {'anno_value': "foo;bar", "video_id": 1, "user_guid": str(new_guid)}
        out = server.parse_annotation(postdata)
        self.assertEqual(out['anno'], "foobar")
        self.assertEqual(out['video_id'], 1)
        self.assertEqual(out['user_guid'], new_guid)

    def test_parse_anno_ok_with_diacritics(self):
        new_guid = uuid.uuid4()
        postdata = {'anno_value': "foo?bar", "video_id": 1, "user_guid": str(new_guid)}
        out = server.parse_annotation(postdata)
        self.assertEqual(out['anno'], "foo?bar")
        self.assertEqual(out['video_id'], 1)
        self.assertEqual(out['user_guid'], new_guid)
