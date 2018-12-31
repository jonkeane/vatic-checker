import os.path, sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import json, re, datetime, uuid, cStringIO, logging, urllib, urllib2
from sqlalchemy import and_, func, distinct, desc
from sqlalchemy.orm import aliased
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound

# import from vatic_checker though this will make testing more difficult
from vatic_checker.handler import handler, application, Error500
from vatic_checker.database import session
import vatic_checker.model as model

import config

# setup handler
ch = logging.StreamHandler(sys.stdout)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)

# setup the vatic parent logger
logger_checker = logging.getLogger("checker-server")
logger_checker.setLevel(logging.ERROR)
logger_checker.addHandler(ch)

# instantiate the server logger
logger = logging.getLogger("checker-server")

# send test to the log to ensure which level is running.
logger.error("This is a 40 (error)")
logger.debug("This is a 10 (debug)")

@handler()
def get_next(userid):
    """
    Returns the next video to annotate for a user if the user has completed
    training. If they have not completed the training, return a training video
    instead.
    """
    status = {}

    # TODO: error gracefully if not a UUID?

    user = session.query(model.User)
    user = user.filter(model.User.guid == userid)

    # TODO: error gracefully if less than one or more than one returned
    user = user.one()

    # retrieve training status, defaults to false
    status["trained"] = user.completed_training

    # check if there are at least N training videos annotated
    if status["trained"] == False:
        training_check = check_training_completion(user, config.min_training)
        if training_check:
            # update the database so we don't have to check each time
            user.completed_training = training_check
            session.commit()
            status["trained"] = training_check

    if status["trained"]:
        status.update(getNextLeastAnnoedVideo(user))
    else:
        status.update(getNextTrainingVideo(user))

    return status


def getNextLeastAnnoedVideo(user):
    """
    Returns the next video to annotate for a given user. This video will be the
    least annotated video by the user or everyone else.
    """
    # get the user id
    user_guid = user.guid

    return_value = {}

    # make aliases for the joins later
    annotations_current_user = aliased(model.Annotation)
    annotations_all = aliased(model.Annotation)

    videos = session.query(model.Video)

    # add the number of annotations for the current user
    videos = videos.add_column(
        func.count(distinct(annotations_current_user.user_guid).label('annos_current_user'))).\
    outerjoin(annotations_current_user,
              and_(annotations_current_user.video_id == model.Video.id,
                   annotations_current_user.user_guid == user_guid)).\
    group_by(model.Video.id)

    # add the number of annotations for all users
    videos = videos.add_column(
        func.count(annotations_all.user_guid.label('total_annos'))).\
    outerjoin(annotations_all, annotations_all.video_id == model.Video.id).\
    group_by(model.Video.id)

    # order so that if the current user hasn't annotated, that is preferred, but
    # if there is a tie, then get the newt least annotated video.
    # count_1 = annos_current_user
    # count_2 = total_annos
    videos = videos.order_by('count_1', 'count_2', func.rand())

    try:
        video = videos.first()
    except NoResultFound, e:
        logger.error("Found no videos available for annotations for user: %s" % (user_guid))
        return None

    return_value["video_id"] =  video[0].id
    return_value["name"] =  video[0].name
    return_value["start"] = 0 # the start frame is always 0
    return_value["end"] =  video[0].num_frames - 1 # bc zero-indexing, need to subtract one
    return_value["width"] =  video[0].width
    return_value["height"] =  video[0].height

    return return_value

def getNextTrainingVideo(user):
    """
    Returns the next training video to annotate for a given user.
    """
    # get the user id
    user_guid = user.guid

    return_value = {}

    training_videos = session.query(model.TrainingVideo, model.Training)

    # add the number of annotations for the current user
    training_videos = training_videos.\
    outerjoin(model.Training,
              and_(model.Training.video_id == model.TrainingVideo.id,
                   model.Training.user_guid == user_guid)).\
    filter(model.Training.success == None)

    # randomize
    training_videos = training_videos.order_by(func.rand())

    try:
        training_videos = training_videos.first()
    except NoResultFound, e:
        # TODO: don't try to get the next training video if none are left?
        logger.error("Found no training videos available for annotations for user: %s" % (user_guid))
        return None

    return_value["video_id"] =  training_videos[0].id
    return_value["name"] =  training_videos[0].name
    return_value["start"] = 0 # the start frame is always 0
    return_value["end"] =  training_videos[0].num_frames - 1 # bc zero-indexing, need to subtract one
    return_value["width"] =  training_videos[0].width
    return_value["height"] =  training_videos[0].height

    return return_value

def parse_annotation(postdata):
    out = {}

    # TODO: add try/excepts throughout here
    # strip any charaters that are not in our annotation set
    # SQL alchemy should quote special characters, but this is a good defense as well.
    # This allows all letters, numbers, ?, *, [, ], :, #, !, -
    out["anno"] = re.sub("[^A-z0-9 \?\*\[\]\:\#\!\\-]", "", postdata.get('anno_value', ''))
    out["video_id"] = int(postdata.get('video_id', None))
    out["user_guid"] = uuid.UUID(postdata.get('user_guid', None))

    return out

def check_training_completion(user, n):
    """
    Check if a user has trained enough
    """

    # confirm that n is less than or equal to available training videos
    training_videos = session.query(model.TrainingVideo)
    if training_videos.count() < n:
        logger.error("There are fewer training videos than the setting min_training. Change the min_training value in the config file to fix this.")
        raise Error500("Server misconfiguration: There are fewer training videos than the setting min_training. Please try reconfiguring and trying again.")

    # get the user id
    user_guid = user.guid

    trainings = session.query(model.Training.success, model.Training.video_id).\
    filter(model.Training.user_guid == user_guid).\
    group_by(model.Training.video_id).\
    filter(model.Training.success == True)

    if trainings.count() >= n:
        print("setting training to true")
        user.trained = True
        session.commit()
        return True

    # return false otherwise
    return False

@handler(post = "json")
def save_annotation(video_id, postdata):
    """
    Saves annotation for a regular video
    """
    data = parse_annotation(postdata)

    logger.debug("Saving annotation: annotation {0}; video_id {1}; user id {2}".format(
    data["anno"], data["video_id"], data["user_guid"])
    )

    # TODO: try/catch in case there is an issue with guid or video_id
    new_anno = model.Annotation(
        text = data["anno"],
        user_guid = data["user_guid"],
        video_id = data["video_id"],
        timestamp = datetime.datetime.utcnow()
        )

    session.add(new_anno)
    session.commit()

    logger.debug("Saved")
    return True

@handler(post = "json")
def save_training(video_id, postdata):
    """
    Saves annotation for a training video
    """
    data = parse_annotation(postdata)

    # start off skeptical
    success = False

    # check if the label matches
    training_video = session.query(model.TrainingVideo).\
    filter(model.TrainingVideo.id == data["video_id"])

    # TODO: catch if the video doesn't match anything
    training_video = training_video.one()

    if data["anno"] == training_video.gold_standard_label:
        success = True

    if success:
        logger.debug(
        "Saving training: annotation {0}; video_id {1}; user id {2}".format(
        data["anno"], data["video_id"], data["user_guid"])
        )

        # TODO: try/catch in case there is an issue with guid or video_id
        new_anno = model.Training(
            text = data["anno"],
            user_guid = data["user_guid"],
            video_id = data["video_id"],
            timestamp = datetime.datetime.utcnow(),
            success = success
            )

        session.add(new_anno)
        session.commit()

        logger.debug("Saved")
        return "all good"
    else:
        return "borked"


@handler(post = "json")
def login(params, postdata):
    """
    Returns the guid of the user if they exist
    """
    out = {}
    print(postdata)
    # verify the recpatcha is correct
    recaptcha_url = "https://www.google.com/recaptcha/api/siteverify"
    data = {
        "secret": config.recaptcha_secret,
        "response": postdata.get('recaptcha', '')
        }
    request = urllib2.Request(recaptcha_url, data=urllib.urlencode(data))
    resp = urllib2.urlopen(request)
    resp = json.loads(resp.read())

    # if the captch wasn't verified return false.
    if resp['success'] is not True:
        logger.debug("The recaptcha has failed, returning an error.")
        out['success'] = False
        out['reason'] = "Could not login"
        return out

    # strip all non alphanumeric characters
    username = re.sub("[^A-z0-9]", "", postdata.get('username', ''))

    user = session.query(model.User)
    user = user.filter(model.User.username == username)

    # TODO: error gracefully if less than one or more than one returned
    try:
        user = user.one()
    except NoResultFound:
        out['success'] = False
        out['reason'] = "Incorrect username"
        return out
    except MultipleResultsFound:
        logger.error("There is more than one user with that username. You must delete one from the database.")
        raise Error500("More than one user with that name. Please contact the researcher.")

    out['success'] = True
    out['user_guid'] = str(user.guid)

    return out
