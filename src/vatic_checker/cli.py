"""
A lightweight cli framework.

To use this module, decorate functions with the 'handler' decorator. Then, call
with 'checker [command] [arguments]' from the shell.
"""

from future.standard_library import install_aliases
install_aliases()

from urllib.parse import urlparse, urlencode
from urllib.request import urlopen, Request
from urllib.error import HTTPError

import sys, os, shutil, glob, argparse, uuid, csv, urllib
import database
import ffmpeg
import model
from database import session
from sqlalchemy import func, distinct
from PIL import Image

try:
    import cPickle as pickle
except ImportError:
    import pickle

handlers = {}

def handler(help = "", inname = None):
    """
    Decorator bind a function as a handler for a cli command.

    help    specifies the help message to display
    inname  specifies the name of the handler, otherwise infer
    """
    def decorator(func):
        if inname is None:
            name = func.__name__.replace("_", "-")
        else:
            name = inname
        handlers[name.lower()] = func, help
        return func
    return decorator

class Command(object):
    def __init__(self, args):
        parser = self.setup()
        parser.prog = "vatic checker {0}".format(sys.argv[1])
        self(parser.parse_args(args))

    def setup(self):
        return argparse.ArgumentParser()

    def __call__(self, args):
        raise NotImplementedError("__call__() must be defined")

def main(args = None):
    """
    Dispatches the cli command through a given handler.
    """
    if args is None:
        args = sys.argv[1:]
    try:
        args[0]
    except IndexError:
        help()
    else:
        try:
           handler = handlers[args[0]][0]
        except KeyError:
            print("Error: Unknown action {0}".format(args[0]))
        else:
            try:
                handler(args[1:])
            finally:
                if session:
                    session.remove()

def help(args = None):
    """
    Print the help information.
    """
    for action, (_, help) in sorted(handlers.items()):
        print("{0:>15}   {1:<50}".format(action, help))

@handler("Start a new instance of vatic_checker")
class init(Command):
    def setup(self):
        parser = argparse.ArgumentParser()
        parser.add_argument("name")
        return parser

    def __call__(self, args):
        vc_path = os.path.dirname(__file__)
        public = os.path.join(vc_path, "public")
        target = os.path.join(os.getcwd(), args.name)

        if os.path.exists(target):
            print("{0} already exists".format(target))
            return

        shutil.copytree(public, os.path.join(target, "public"))

        shutil.copyfile(os.path.join(vc_path, "server.py"),
                        os.path.join(target, "server.py"))
        shutil.copyfile(os.path.join(vc_path, "config.py"),
                        os.path.join(target, "config.py"))

        for file in glob.glob(target + "/*.pyc"):
            os.remove(file)

        print("Initialized new project: {0}".format(args.name))

# TODO: update status
@handler("See vatic_chcker status")
class status(Command):
    def __call__(self, args):
        print("Not implemented")

@handler("Setup the application")
class setup(Command):
    def setup(self):
        parser = argparse.ArgumentParser()
        parser.add_argument("--database", action="store_true")
        parser.add_argument("--reset", action="store_true")
        return parser

    def resetdatabase(self):
        database.reinstall()
        print("Database reset!")

    def database(self, args):
        import model

        if args.reset:
            if args.no_confirm:
                self.resetdatabase()
            else:
                resp = raw_input("Reset database? ").lower()
                if resp in ["yes", "y"]:
                    self.resetdatabase()
                else:
                    print("Aborted. No changes to database.")
        else:
            database.install()
            print("Installed new tables, if any.")

    def __call__(self, args):
        if args.database:
            self.database(args)


@handler("Decompresses an entire video into frames")
class extract(Command):
    def setup(self):
        parser = argparse.ArgumentParser()
        parser.add_argument("video")
        parser.add_argument("output")
        parser.add_argument("--width", default=720, type=int)
        parser.add_argument("--height", default=480, type=int)
        parser.add_argument("--no-resize",
            action="store_true", default = False)
        parser.add_argument("--no-cleanup",
            action="store_true", default=False)
        return parser

    def __call__(self, args):
        try:
            os.makedirs(args.output)
        except:
            pass

        sequence = ffmpeg.extract(args.video)
        try:
            for frame, image in enumerate(sequence):
                if frame % 100 == 0:
                    print("Decoding frames {0} to {1}"
                        .format(frame, frame + 100))
                if not args.no_resize:
                    image.thumbnail((args.width, args.height), Image.BILINEAR)
                path = model.Video.getframepath(frame, args.output)
                try:
                    image.save(path)
                except IOError:
                    os.makedirs(os.path.dirname(path))
                    image.save(path)
        except:
            if not args.no_cleanup:
                print("Aborted. Cleaning up...")
                shutil.rmtree(args.output)
            raise


@handler("Imports a set of video frames")
class load(object):
    def __init__(self, args):
        args = self.setup().parse_args(args)

        # replace any / with underscores so as not to clash with folder separator
        args.name = args.name.replace('/', '_')

        # if the video is for training, then it should be stored in model.TrainingVideo
        if args.fortraining:
            self.table = model.TrainingVideo
        else:
            self.table = model.Video

        self(args)

    def setup(self):
        parser = argparse.ArgumentParser(add_help=False)
        parser.add_argument("location")
        parser.add_argument("--name")
        parser.add_argument("--video_path")
        parser.add_argument("--start")
        parser.add_argument("--end")
        parser.add_argument("--duration")
        parser.add_argument("--label")
        parser.add_argument("--width", default=720, type=int)
        parser.add_argument("--height", default=480, type=int)
        parser.add_argument("--fortraining", default=False, action="store_true")
        parser.add_argument("--symlinkpath", default="public/frames/")
        return parser

    def __call__(self, args):
        print("Checking integrity...")

        # read first frame to get sizes
        path = self.table.getframepath(0, args.location)

        try:
            im = Image.open(path)
        except IOError:
            print("Cannot read {0}".format(path))
            raise
            return
        width, height = im.size

        print("Searching for last frame...")

        maxframes = max(int(os.path.splitext(x)[0])
            for x in os.listdir("{0}"
            .format(args.location)))

        print("Found {0} frames.".format(maxframes))

        args.length = maxframes + 1

        # can we read the last frame?
        path = self.table.getframepath(maxframes, args.location)
        try:
            im = Image.open(path)
        except IOError:
            print("Cannot read {0}".format(path))
            return

        # check last frame sizes
        if im.size[0] != width and im.size[1] != height:
            print("First frame dimensions differs from last frame")
            return

        # if name and start and end are the same, this probably is a duplicate
        videos = session.query(model.Video).\
            filter(model.Video.name == args.name,
                   model.Video.start == args.start,
                   model.Video.end == args.end)
        if videos.count():
            print("Video {0} at {1} already exists with the same start time, end time, and name.".format(args.name, os.path.realpath(args.location)))
            raise ValueError("Video {0} is already in the database with the same start time, end time, and name.".format(args.name))

        # if there is already a video with this name, add _N to the end
        videos = session.query(model.Video).\
            filter(model.Video.name == args.name)
        if videos.count():
            old_name = args.name
            # get the number of videos with the name already in the DB, and add that + 1 to ensure uniqueness
            sim_videos = session.query(model.Video).\
                filter(model.Video.name.like(args.name+"%"))
            args.name = old_name + "_" + str(sim_videos.count()+1)

            print("There's already a video named {0}, renaming this one to {1}".format(old_name, args.name))

        # create video
        video_args = {
            "path": os.path.realpath(args.location),
            "name": args.name,
            "duration": args.duration,
            "start": args.start,
            "end": args.end,
            "label": args.label,
            "video_path": args.video_path,
            "width": width,
            "height": height,
            "num_frames": maxframes
        }

        if args.fortraining:
            # TODO: add a gold_standard argument?
            video_args["gold_standard_label"] = args.label

        video = self.table(**video_args)
        session.add(video)

        print("Creating symbolic link...")
        symlink = os.path.join(args.symlinkpath, "{0}".format(video.name))
        try:
            os.remove(symlink)
        except:
            pass

        try:
            os.mkdir(args.symlinkpath)
        except OSError:
            # might already exist, so try anyway
            pass
        os.symlink(video.path, symlink)

        session.commit()

        print("Video loaded and ready for annotation.")

@handler("Imports a training video")
class loadtraining(load):
    """
    A helper function for loading training videos (relies on load above for
    most functionality)
    """
    def __init__(self, args):
        args = self.setup().parse_args(args)

        # replace any / with underscores so as not to clash with folder separator
        args.name = args.name.replace('/', '_')

        args.fortraining = True
        # if the video is for training, then it should be stored in model.TrainingVideo
        if args.fortraining:
            self.table = model.TrainingVideo
        else:
            self.table = model.Video

        self(args)

    def setup(self):
        parser = argparse.ArgumentParser(add_help=False)
        parser.add_argument("location")
        parser.add_argument("--name")
        parser.add_argument("--video_path")
        parser.add_argument("--start")
        parser.add_argument("--end")
        parser.add_argument("--duration")
        parser.add_argument("--label")
        parser.add_argument("--width", default=720, type=int)
        parser.add_argument("--height", default=480, type=int)
        parser.add_argument("--symlinkpath", default="public/frames/")
        return parser

@handler("Lists available users")
class users(object):
    def __init__(self, args):
        args = self.setup().parse_args(args)

        self(args)

    def setup(self):
        parser = argparse.ArgumentParser(add_help=False)
        return parser

    def __call__(self, args):
        users = session.query(model.User.guid, model.User.username, model.User.completed_training)

        user_data = users.all()

        username_lengths = [len(x[1]) for x in user_data]

        print("The following users are configured in the server:")
        cols = ["guid", "name", "trained?"]
        row_format = "{:>37}{:>" + str(max(username_lengths) + 2 ) + "}{:>10}"
        print(row_format.format(*cols))
        for row in user_data:
            print(row_format.format(*row))
        return

@handler("Adds a new user")
class newuser(object):
    def __init__(self, args):
        args = self.setup().parse_args(args)

        self(args)

    def setup(self):
        parser = argparse.ArgumentParser(add_help=False)
        parser.add_argument("username")
        parser.add_argument("--trained", default=False, action="store_true")
        parser.add_argument("--admin", default=False, action="store_true")
        return parser

    def __call__(self, args):
        print("Checking if the user already exists...")

        users = session.query(model.User).filter(model.User.username == args.username)

        if users.count() > 0:
            print("There's already a user named {0}".format(args.username))
            return

        # create user
        new_guid = uuid.uuid4()
        user = model.User(
            username=args.username,
            guid=new_guid,
            completed_training=args.trained,
            can_see_status=args.admin
            )

        session.add(user)

        session.commit()

        print("A new user has been created for {0}".format(user.username))

@handler("Removes a user")
class deleteuser(object):
    def __init__(self, args):
        args = self.setup().parse_args(args)

        self(args)

    def setup(self):
        parser = argparse.ArgumentParser(add_help=False)
        parser.add_argument("username")
        return parser

    def __call__(self, args):
        users = session.query(model.User).filter(model.User.username == args.username)

        if users.count() < 1:
            print("There is no user named {0}".format(args.username))
            return
        elif users.count() > 1:
            print("Cannot yet delete users that have the same username")
            return

        # delete the user
        users.delete()
        session.commit()

        print("The user {0} has been deleted".format(args.username))

@handler("Exports data")
class export(object):
    def __init__(self, args):
        args = self.setup().parse_args(args)

        self(args)

    def setup(self):
        parser = argparse.ArgumentParser(add_help=False)
        parser.add_argument("filename")
        parser.add_argument("--training", default=False, action="store_true")
        return parser

    def __call__(self, args):
        anno_table = model.Annotation
        if (args.training):
            anno_table = model.Training

        annotations = session.query(
            model.User.username,
            anno_table.id,
            anno_table.text,
            anno_table.timestamp,
            model.Video.id,
            model.Video.path,
            model.Video.name,
            model.Video.duration,
            model.Video.start,
            model.Video.end,
            model.Video.label,
            model.Video.video_path,
            model.Video.num_frames
            ).filter(anno_table.video_id == model.Video.id).filter(anno_table.user_guid == model.User.guid)

        annos = annotations.all()

        with open(args.filename,'wb') as out:
            csv_out=csv.writer(out)
            csv_out.writerow(['annotator_username',
                              'annotation_id',
                              'annotation_text',
                              'annotation_timestamp',
                              'video_id',
                              'video_path',
                              'video_name',
                              'video_duration',
                              'video_start',
                              'video_end',
                              'video_label',
                              'video_video_path',
                              'video_num_frames'
                              ])
            for row in annos:
                csv_out.writerow(row)

        print("Exported {0} annotations".format(annotations.count()))

@handler("Takes a csv of data clips the videos and then imports it")
class importcsv(object):
    def __init__(self, args):
        args = self.setup().parse_args(args)

        self(args)

    def setup(self):
        parser = argparse.ArgumentParser(add_help=False)
        parser.add_argument("filename")
        parser.add_argument("--training", default=False, action="store_true")
        return parser

    def __call__(self, args):
        video_csv = []
        input_file = csv.DictReader(open(args.filename))
        for row in input_file:
            video_csv.append(row)

        # check that the csv object has all of the necesary columns.
        for clip in video_csv:
            columns = ['Filename',
                       'Video Path',
                       'Begin Time - msec',
                       'End Time - msec',
                       'Label']
            has_columns = [x in video_csv[0].keys() for x in columns]
            if all(has_columns) != True:
                # If any of the rows don't have the correct columns, error and return
                print("The csv does not have all of the necesary columns. The needed columns are case-sensitive, must include the spaces, and are called:")
                print("Filename: The name of the file (this will be used to identify the clip)")
                print("Video Path: The path to the video file, from which the clip should be extracted")
                print("Begin Time - msec: The time that the fingerspelling starts (in milliseconds)")
                print("End Time - msec: The time that the fingerspelling ends (in milliseconds)")
                print("Label: The label that was annotated by MTurkers. If these videos will be used for training, this is also the gold-standard label an annotator must get to be considered trained.")
                return

        # ensure filenames do not have slashes in them.
        for i in range(len(video_csv)):
            video_csv[i]['Filename'] = video_csv[i]['Filename'].replace('/', '_')

        # ensure paths have their " quoted
        for i in range(len(video_csv)):
            video_csv[i]['Video Path'] = video_csv[i]['Video Path'].replace('"', '\"')

        # TODO: ensure that the names are unique (because they will all be
        # stored in the same frame location if not)

        # make a clips directory
        try:
            os.mkdir("./clips")
        except OSError:
            # might already exist, so try anyway
            pass

        for clip in video_csv:
            # check if the all of the files exists, error gracefully otherwise
            if os.path.isfile(clip['Video Path']) != True:
                print("The video for the following row couldn't be accessed:")
                print(clip['Video Path'])
                print("Please check and make sure this path exists and is reachable.")
                print(clip)
                return

        # first, we need to clip the videos
        for clip in video_csv:
            print("Clipping {0} into just the fingerspelled segments...".format(clip['Filename']))
            ffmpeg.clip(source_path = clip['Video Path'],
                        start = int(clip['Begin Time - msec']),
                        end = int(clip['End Time - msec']),
                        output_path = os.path.join("./clips", clip['Filename']))

            print("Extracting frames from the clip...")
            extract([os.path.join("./clips", clip['Filename'] + ".mp4"),
                     os.path.join("./frames", clip['Filename']),
            ])

            print("Loading the clip into vatic-checker...")
            duration = int(clip['End Time - msec']) - int(clip['Begin Time - msec'])
            # setup arguments for load
            load_args = [os.path.join('./frames', clip['Filename']),
                    "--name", clip['Filename'], # name
                    "--video_path", clip['Video Path'], # video_path
                    "--start", clip['Begin Time - msec'], # start
                    "--end", clip['End Time - msec'], # end
                    "--duration", str(duration), # duration
                    "--label", clip['Label'] # label
                    ]
            if (args.training):
                load_args.append("--fortraining")
            load(load_args)

        print("Completed loading from {0}".format(args.filename))


@handler("get annotation status by user")
class userannos(object):
    def __init__(self, args):
        args = self.setup().parse_args(args)

        self(args)

    def setup(self):
        parser = argparse.ArgumentParser(add_help=False)
        parser.add_argument("username")
        return parser

    def __call__(self, args):
        print("Checking if the {0} exists...".format(args.username))

        users = session.query(model.User).filter(model.User.username == args.username)

        if users.count() == 0:
            print("There's no user named {0}".format(args.username))
            return

        user = users.first()

        # grab the user's annotations
        current_annotations = session.query(model.Annotation).filter(model.Annotation.user_guid == user.guid)
        subq = session.query(model.Annotation).\
                filter(model.Annotation.user_guid == user.guid).\
                subquery('sub')
        videos_annoed = session.query(model.Video, subq.c.text).\
             outerjoin(subq, subq.c.video_id == model.Video.id)

        print("{0} has already annotated {1} videos.".format(user.username, videos_annoed.filter(subq.c.text != None).count()))
        print("{0} has {1} videos left to annotate.".format(user.username, videos_annoed.filter(subq.c.text == None).count()))


@handler("get annotation status")
class annotationstats(object):
    def __init__(self, args):
        args = self.setup().parse_args(args)

        self(args)

    def setup(self):
        parser = argparse.ArgumentParser(add_help=False)
        return parser

    def __call__(self, args):
        # grab the users' annotations
        videos = session.query(model.Video)
        total_videos = videos.count()

        # grab the users' annotations
        current_annotations = session.\
            query(model.User.username, model.User.completed_training).\
             outerjoin(model.Annotation, model.User.guid == model.Annotation.user_guid).\
            group_by(model.User.guid).\
            add_column(
                func.count(distinct(model.Annotation.video_id).label('annos_current_user')))


        results = session.execute(current_annotations)
        results_dict = [dict(zip(["username", "completed_training", "annotations_completed"], row)) for row in results]

        print(results_dict)

@handler("get annotation status")
class videostats(object):
    def __init__(self, args):
        args = self.setup().parse_args(args)

        self(args)

    def setup(self):
        parser = argparse.ArgumentParser(add_help=False)
        return parser

    def __call__(self, args):
        # grab the users' annotations
        users = session.query(model.User)
        total_users = users.count()

        # grab the videos' annotations
        current_annotations = session.\
            query(model.Video.name).\
             outerjoin(model.Annotation, model.Video.id == model.Annotation.video_id).\
            group_by(model.Video.name).\
            add_column(
                func.count(distinct(model.Annotation.id).label('annos_current_user')))


        results = session.execute(current_annotations)
        results_dict = [dict(zip(["video_name", "annotations_completed"], row)) for row in results]

        print(results_dict)
