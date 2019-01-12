import pytest

import sys, os, shutil, uuid
myPath = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, myPath + "/../../src/vatic_checker/") # move to the src directory

import cli
import model

from alchemy_mock.mocking import UnifiedAlchemyMagicMock, AlchemyMagicMock
import argparse
try:
    from unittest import mock  # python 3.3+
except ImportError:
    import mock  # python 2.6-3.2

# current working directory
cwd = os.getcwd()


# mock the session object from cli so that the database isn't harmed.
session = UnifiedAlchemyMagicMock(data = [
    (
        [mock.call.query(model.User),
         mock.call.filter(model.User.username == "a_newuser")],
        [model.User(guid=uuid.UUID("87599456d52b48b78a6b1b5b0ded7be1"),
                    username="a_newuser",
                    completed_training=False)]
    )
])
@mock.patch('cli.session', new=session)
@mock.patch('argparse.ArgumentParser.parse_args',
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
def test_load(mock_args):
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

@mock.patch('cli.session', new=session)
@mock.patch('argparse.ArgumentParser.parse_args',
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
def test_load_training(mock_args):
    session.reset_mock()

    test_dir = "./tests/to_delete"
    if not os.path.exists(test_dir):
        os.mkdir(test_dir)
    cli.load("f")

    # assert that an add and commit were called
    session.add.assert_called_once()
    session.commit.assert_called_once()

    # assert that TrainingVideo was inserted into and gold_standard_label was filled
    video_added = session.mock_calls[0][1][0]
    assert isinstance(video_added, model.TrainingVideo)
    assert video_added.path == os.path.join(cwd, "tests/frames/zero")
    assert video_added.name == "aslized_ben_jarashow_1745"
    assert video_added.gold_standard_label == "yll"

    # assert that the link was created.
    assert os.path.islink(os.path.join(test_dir, "aslized_ben_jarashow_1745"))
    shutil.rmtree("./tests/to_delete")


@mock.patch('cli.session', new=session)
@mock.patch('argparse.ArgumentParser.parse_args',
            return_value=argparse.Namespace(
                username="a_brand_newuser",
                trained=False
            ))
def test_newuser(mock_args):
    session.reset_mock()

    cli.newuser("f")

    # assert that an add and commit were called
    session.add.assert_called_once()
    session.commit.assert_called_once()


@mock.patch('cli.session', new=session)
@mock.patch('argparse.ArgumentParser.parse_args',
            return_value=argparse.Namespace(
                username="a_newuser",
                trained=False
            ))
def test_newuser_already_exists(mock_args):
    session.reset_mock()

    cli.newuser("f")

    session.query.return_value.filter.assert_called_once_with(model.User.username == "a_newuser")

    session.add.assert_not_called()
