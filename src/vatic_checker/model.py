import database
from sqlalchemy import Column, Integer, Float, String, Boolean, Text, DateTime
from sqlalchemy import ForeignKey, Table, PickleType
from sqlalchemy.orm import relationship, backref
from sqlalchemy.types import TypeDecorator, CHAR
from sqlalchemy.dialects.postgresql import UUID
import uuid
import random
import logging

logger = logging.getLogger("model")

class GUID(TypeDecorator):
    """Platform-independent GUID type.

    Uses Postgresql's UUID type, otherwise uses
    CHAR(32), storing as stringified hex values.

    """
    impl = CHAR

    def load_dialect_impl(self, dialect):
        if dialect.name == 'postgresql':
            return dialect.type_descriptor(UUID())
        else:
            return dialect.type_descriptor(CHAR(32))

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        elif dialect.name == 'postgresql':
            return str(value)
        else:
            if not isinstance(value, uuid.UUID):
                return "%.32x" % uuid.UUID(value).int
            else:
                # hexstring
                return "%.32x" % value.int

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        else:
            return uuid.UUID(value)

class Video(database.Base):
    __tablename__   = "videos"

    id              = Column(Integer, primary_key = True)
    path            = Column(String(350))
    name            = Column(String(250), index = True) # maybe don't need the index?
    duration        = Column(Integer)
    start           = Column(Integer)
    end             = Column(Integer)
    label           = Column(String(250))
    video_path      = Column(String(350))
    num_frames      = Column(Integer)
    width           = Column(Integer)
    height          = Column(Integer)

    def __getitem__(self, frame):
        path = Video.getframepath(frame, self.location)
        return Image.open(path)

    @classmethod
    def getframepath(cls, frame, base = None):
        path = "{0}.jpg".format(frame)
        if base is not None:
            path = "{0}/{1}".format(base, path)
        return path

class TrainingVideo(database.Base):
    __tablename__   = "trainingVideos"

    id                    = Column(Integer, primary_key = True)
    path                  = Column(String(350))
    name                  = Column(String(250), index = True) # maybe don't need the index?
    duration              = Column(Integer)
    start                 = Column(Integer)
    end                   = Column(Integer)
    label                 = Column(String(250))
    video_path            = Column(String(350))
    num_frames            = Column(Integer)
    width                 = Column(Integer)
    height                = Column(Integer)
    gold_standard_label   = Column(String(250))

    def __getitem__(self, frame):
        path = Video.getframepath(frame, self.location)
        return Image.open(path)

    @classmethod
    def getframepath(cls, frame, base = None):
        path = "{0}.jpg".format(frame)
        if base is not None:
            path = "{0}/{1}".format(base, path)
        return path

class User(database.Base):
    __tablename__ = "users"

    guid                 = Column(GUID, primary_key = True)
    username             = Column(String(250), unique = True)
    completed_training   = Column(Boolean, default = False)

class Training(database.Base):
    __tablename__ = "trainings"

    id          = Column(Integer, primary_key = True)
    text        = Column(String(250))
    user_guid   = Column(GUID, ForeignKey(User.guid))
    video_id    = Column(Integer, ForeignKey(TrainingVideo.id))
    timestamp   = Column(DateTime)
    success     = Column(Boolean, default = False)

class Annotation(database.Base):
    __tablename__ = "annotations"

    id          = Column(Integer, primary_key = True)
    text        = Column(String(250))
    user_guid   = Column(GUID, ForeignKey(User.guid))
    video_id    = Column(Integer, ForeignKey(Video.id))
    timestamp   = Column(DateTime)
