# Vatic checker

[![Build Status](https://travis-ci.org/jonkeane/vatic-checker.svg?branch=master)](https://travis-ci.org/jonkeane/vatic-checker)

A simple web application that displays videos and allows users to annotate them. It borrows heavily from [vatic](https://github.com/cvondrick/vatic) (especially the video interface), but does not connect to or use Amazon's Mechanical Turk at all.

`vatic-checker` allows for training clips that must be annotated exactly correctly before an annotator is allowed to continue on with annotating other clips. Once they have completed training, they will be presented with a video to annotate. The video they are given is determined using the following hierarchy: 1. has the current user annotated this video, 2. has any other user annotated this video, 3. random after that. In other words: videos that the current annotator and no other annotator has never annotated are preferred most highly, then there are videos that others have annotated but the current annotator has not are preferred, and then which videos that meet those criteria are randomized within each group. This will maximize coverage while still allowing annotators to contribute more annotations to overlap for consistency checking within and across annotators.

# Setup
To install, `pip` should install all of the dependencies (though you will need to install ffmpeg separately)

```
pip install ./vatic-checker
```

Once you have installed `vatic-checker` you will have access to the `checker` command line utility. This utility provides a number of features for adding users, videos, training, etc.

# Configuration
## Initialize a directory to serve `vatic-checker` from
You can use `checker init directory` to install a directory to serve from. Edit `directory/config.py appropriately` as appropriate. For these examples, let's say that we went to the `/var/www` directory and we initialized with `checker init vatic-checker`. This means the directory where we are serving from is `/var/www/vatic-checker`. Then edit and move `http.conf` to the correct directory for your system (e.g. `/etc/httpd/conf.d/`).

## Initialize the database
First, we need to create the database itself, which you can do with:
`mysql -u [your user with appropriate permissions] -e 'create database vaticChecker;'` Then, use the name `vaticChecker` (or whatever you change that to) at the end of `database = mysql://[your user with appropriate permissions]@localhost/vaticChecker` in the config.py file to specify the user and database to use.

Now, run `checker setup --database` from the directory you are serving `vatic-checker` from (here: `/var/www/vatic-checker`), which will install all the necessary tables.

# Add users
To add users, while you are in the directory you have configured (here: `/var/www/vatic-checker`) and you can use the command `checker newuser [username]`. This will create a new user if there isn't already a user with that username. The usernames must be unique, and should only contain letters and numbers.

You can see what users have been added by using the command `checker users` (again, as always, in the directory where you're serving from, here: `/var/www/vatic-checker`).

There is currently no way to delete a user other than removing their entry from the database directly.

# Add training clips
First, there is a configuration property in config.py called `min_training`, it is an integer which is the minimum number of training clips a user needs to get correct before they are allowed to start annotating real clips. This can be set to any amount that is at least the same number or less than the number of training clips that you setup.

There are two ways to load training clips, one by one or from a csv.

## One by one
You can use the `checker loadtraining` command followed by a number of arguments to add one training video at a time. To use this, you must already have turned the video into frames using the `checker extract` command on the small clip that includes only the fingerspelling. Any of the paths can be quoted in case they include spaces or other characters that might impact bash argument parsing

```
checker loadtraining [/path/to/where/the/frames/are] --name [a unique name for the video] --video_path [/path/to/where/the/video/is] --start [msecs into the clip that the fingerspelling starts] --end [msecs into the clip that the fingerspelling ends] --duration [msecs of the duration] --label [the correct label]
```

## With a csv
If you already have the videos you want to load in a csv format, you can use that which will be quicker (and will also extract the frames automatically).

`checker importcsv [/path/to/training.csv] --training`

This csv must have the following columns. The columns are case sensitive and it matters if you have even minor differences in whitespace:
* `Filename` – The name to be used in the system. This must be unique among all videos being annotated.
* `Video Path` – a path to the video file that will be used. This path must be accessible to the system and user you are running `checker` as for the video to be extracted.
* `Begin Time - msec` – the number of milliseconds into the larger clip that the fingerspelling started.
* `End Time - msec` – the number of milliseconds into the larger clip that the fingerspelling ended.
* `Label` – the label that must be matched for the training to be considered successful. 

# Add clips to annotate
You can use the `checker load` command followed by a number of arguments to add one video to be annotated at a time. To use this, you must already have turned the video into frames using the `checker extract` command on the small clip that includes only the fingerspelling. Any of the paths can be quoted in case they include spaces or other characters that might impact bash argument parsing


There are two ways to load clips to annotate, one by one or from a csv.

## One by one
```
checker load [/path/to/where/the/frames/are] --name [a unique name for the video] --video_path [/path/to/where/the/video/is] --start [msecs into the clip that the fingerspelling starts] --end [msecs into the clip that the fingerspelling ends] --duration [msecs of the duration] --label [the label from mturk annotators]
```

## With a csv
If you already have the videos you want to load in a csv format, you can use that which will be quicker (and will also extract the frames automatically).

`checker importcsv [/path/to/videos.csv]`

This csv must have the following columns. The columns are case sensitive and it matters if you have even minor differences in whitespace:
* `Filename` – The name to be used in the system. This must be unique among all videos being annotated.
* `Video Path` – a path to the video file that will be used. This path must be accessible to the system and user you are running `checker` as for the video to be extracted.
* `Begin Time - msec` – the number of milliseconds into the larger clip that the fingerspelling started.
* `End Time - msec` – the number of milliseconds into the larger clip that the fingerspelling ended.
* `Label` – the label associated with the video if there is one (if there is none, this must still exist, but can be left as "").

# Export data
To export the data you can generate a csv with all of the relevant video data, as well as the annotations from the annotators using `checker export file.csv`. This makes a csv where each row is an annotation from a specific user for a specific video. Videos may have more than one annotation if multiple annotators annotated for the same video (or possibly even have multiple annotations from the same annotator if they have annotated it multiple times).


# Development

To install for development or to run tests, `pip` should install all of the dependencies (though you will need to install ffmpeg separately)

```
pip install ./vatic-checker[testing]
```

Then you can run tests with `pytest .`