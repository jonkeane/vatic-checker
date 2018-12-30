import pytest

import sys, os
myPath = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, myPath + "/../../src/vatic_checker/") # move to the src directory

import ffmpeg

def test_which():
    eless = ffmpeg.which("ls")
    assert eless.endswith("ls")
