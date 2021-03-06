import pytest

import sys, os, shutil, uuid
myPath = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, myPath + "/../../src/vatic_checker/") # move to the src directory

import cli
import model

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
session = UnifiedAlchemyMagicMock(data = [
    (
        [call.query(model.User),
         call.filter(model.User.username == "a_newuser")],
        [model.User(guid=uuid.UUID("87599456d52b48b78a6b1b5b0ded7be1"),
                    username="a_newuser",
                    completed_training=False)]
    ),
    ([call.query(model.Video),
      call.filter(model.Video.name == "video_already_in_server",
             model.Video.start == 100,
             model.Video.end == 400)],
     [model.Video(
         id = 1,
         path = "tests/frames/zero",
         name = "video_already_in_server",
         duration = 300,
         start = 100,
         end = 400,
         label = "all",
         video_path = "tests/to_delete/",
         num_frames = 9,
         width = 720,
         height = 405)]),
    ([call.query(model.Video),
      call.filter(model.Video.name == "video_already_in_server")],
     [model.Video(
         id = 1,
         path = "tests/frames/zero",
         name = "video_already_in_server",
         duration = 300,
         start = 100,
         end = 400,
         label = "all",
         video_path = "tests/to_delete/",
         num_frames = 9,
         width = 720,
         height = 405)]),
([call.query(model.Video),
       call.filter(model.Video.name.like("video_already_in_server%"))],
      [model.Video(
          id = 1,
          path = "tests/frames/zero",
          name = "video_already_in_server",
          duration = 300,
          start = 100,
          end = 400,
          label = "all",
          video_path = "tests/to_delete/",
          num_frames = 9,
          width = 720,
          height = 405),
       # fake additional results so we can test the _N naming scheme
       model.Video(id = 2),
       model.Video(id = 3),
       model.Video(id = 4),
       model.Video(id = 5),
       model.Video(id = 6),
       model.Video(id = 7),
       model.Video(id = 8),
       model.Video(id = 9),])
    ])

class TestCLI(TestCase):
    @patch('cli.session', new=session)
    @patch('argparse.ArgumentParser.parse_args',
                return_value=argparse.Namespace(
                    name="aslized/ben_jarashow_1745",
                    location="tests/frames/zero",
                    duration=376,
                    video_path="some/path.m4v",
                    start=28624,
                    end=29000,
                    label="yll",
                    width=720,
                    height=405,
                    fortraining=False,
                    symlinkpath="tests/to_delete/"
                ))
    def test_load(self, mock_args):
        session.reset_mock()

        test_dir = "./tests/to_delete"
        if not os.path.exists(test_dir):
            os.mkdir(test_dir)
        cli.load("f")

        # assert that an add and commit were called
        session.add.assert_called_once()
        session.commit.assert_called_once()

        # assert that Video was inserted into (and not TrainingVideo)
        video_added = session.mock_calls[0][1][0]
        assert isinstance(video_added, model.Video)
        assert video_added.path == os.path.join(cwd, "tests/frames/zero")
        assert video_added.name == "aslized_ben_jarashow_1745"

        # assert that the link was created.
        assert os.path.islink(os.path.join(test_dir, "aslized_ben_jarashow_1745"))
        shutil.rmtree("./tests/to_delete")

class TestCLI(TestCase):
    @patch('cli.session', new=session)
    @patch('argparse.ArgumentParser.parse_args',
                return_value=argparse.Namespace(
                    name="video_already_in_server",
                    location="tests/frames/zero",
                    duration=300,
                    video_path="some/path.m4v",
                    start=100,
                    end=400,
                    label="yll",
                    width=720,
                    height=405,
                    fortraining=False,
                    symlinkpath="tests/to_delete/"
                ))
    def test_load_same_video(self, mock_args):
        session.reset_mock()

        test_dir = "./tests/to_delete"
        if not os.path.exists(test_dir):
            os.mkdir(test_dir)

        with pytest.raises(ValueError) as e_info:
            cli.load("f")

        # assert that an add and commit were called
        session.add.assert_not_called()
        session.commit.assert_not_called()

class TestCLI(TestCase):
    @patch('cli.session', new=session)
    @patch('argparse.ArgumentParser.parse_args',
                return_value=argparse.Namespace(
                    name="video_already_in_server",
                    location="tests/frames/zero",
                    duration=300,
                    video_path="some/path.m4v",
                    start=400,
                    end=700,
                    label="yll",
                    width=720,
                    height=405,
                    fortraining=False,
                    symlinkpath="tests/to_delete/"
                ))
    def test_load_same_name_video(self, mock_args):
        session.reset_mock()

        test_dir = "./tests/to_delete"
        if not os.path.exists(test_dir):
            os.mkdir(test_dir)

        cli.load("f")

        # assert that an add and commit were called
        session.add.assert_called_once()
        session.commit.assert_called_once()

        # assert that Video was inserted into (and not TrainingVideo)
        video_added = session.mock_calls[9][1][0]
        assert isinstance(video_added, model.Video)
        assert video_added.path == os.path.join(cwd, "tests/frames/zero")
        assert video_added.name == "video_already_in_server_10"

        # assert that the link was created.
        assert os.path.islink(os.path.join(test_dir, "video_already_in_server_10"))
        shutil.rmtree("./tests/to_delete")

    @patch('cli.session', new=session)
    @patch('argparse.ArgumentParser.parse_args',
                return_value=argparse.Namespace(
                    name="aslized/ben_jarashow_1745",
                    location="tests/frames/zero",
                    duration=376,
                    video_path="some/path.m4v",
                    start=28624,
                    end=29000,
                    label="yll",
                    width=720,
                    height=405,
                    fortraining=True,
                    symlinkpath="tests/to_delete/"
                ))
    def test_load_training(self, mock_args):
        session.reset_mock()

        test_dir = "./tests/to_delete"
        if not os.path.exists(test_dir):
            os.mkdir(test_dir)
        cli.load("f")

        # assert that an add and commit were called
        session.add.assert_called_once()
        session.commit.assert_called_once()

        # assert that TrainingVideo was inserted into and gold_standard_label was filled
        video_added = session.mock_calls[6][1][0]
        assert isinstance(video_added, model.TrainingVideo)
        assert video_added.path == os.path.join(cwd, "tests/frames/zero")
        assert video_added.name == "aslized_ben_jarashow_1745"
        assert video_added.gold_standard_label == "yll"

        # assert that the link was created.
        assert os.path.islink(os.path.join(test_dir, "aslized_ben_jarashow_1745"))
        shutil.rmtree("./tests/to_delete")


    @patch('cli.session', new=session)
    @patch('argparse.ArgumentParser.parse_args',
                return_value=argparse.Namespace(
                    username="a_brand_newuser",
                    trained=False,
                    admin=False
                ))
    def test_newuser(self, mock_args):
        session.reset_mock()

        cli.newuser("f")

        # assert that an add and commit were called
        session.add.assert_called_once()
        session.commit.assert_called_once()


    @patch('cli.session', new=session)
    @patch('argparse.ArgumentParser.parse_args',
                return_value=argparse.Namespace(
                    username="a_newuser",
                    trained=False,
                    admin=False
                ))
    def test_newuser_already_exists(self, mock_args):
        session.reset_mock()

        cli.newuser("f")

        session.query.return_value.filter.assert_called_once_with(model.User.username == "a_newuser")

        session.add.assert_not_called()


    @patch('cli.session', new=session)
    @patch('argparse.ArgumentParser.parse_args',
                return_value=argparse.Namespace(
                    username="a_brand_admin",
                    trained=True,
                    admin=True
                ))
    def test_newuser_with_args(self, mock_args):
        session.reset_mock()

        cli.newuser("f")

        # assert that an add and commit were called
        session.add.assert_called_once()
        session.commit.assert_called_once()

        # assert the args are set
        new_user = session.mock_calls[3][1][0]
        self.assertEqual(new_user.username, "a_brand_admin")
        self.assertTrue(new_user.completed_training)
        self.assertTrue(new_user.can_see_status)
