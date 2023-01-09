# -*- coding: utf-8 -*-

import calendar
import copy
import datetime
import fractions
import hashlib
import math
import os
import platform
import pprint
import re
import shutil
import subprocess
import sys
import tempfile
import uuid

from anima import defaults, logger

import exifread

import pytz

from sqlalchemy import and_, exists, or_
from sqlalchemy.exc import UnboundExecutionError
from sqlalchemy.orm import aliased
from sqlalchemy.pool import NullPool
from sqlalchemy.sql.functions import array_agg

from stalker import (
    Asset,
    Link,
    Project,
    Repository,
    Sequence,
    Shot,
    Status,
    Task,
    TimeLog,
    User,
    Version,
    db,
)
from stalker.db.session import DBSession
from stalker.models.auth import AuthenticationLog, LOGIN, LocalSession
from stalker.models.task import Task_Resources


def all_equal(elements):
    """Return True if all the elements are equal, otherwise False.

    Args:
        elements (list): List of elements.

    Returns:
        bool: True if all elements are equal, False otherwise.
    """
    first_element = elements[0]
    for other_element in elements[1:]:
        if other_element != first_element:
            return False
    return True


def common_prefix(*sequences):
    """Return a list of common elements at the start of all sequences.

    Then a list of lists that are the unique tails of each sequence.

    Args:
        sequences: Arg list.

    Returns:
        list, list: The first list contains the common parts, the second list contains
            uncommon elements.
    """
    # if there are no sequences at all, we're done
    if not sequences:
        return [], []
    # loop in parallel on the sequences
    common = []
    for elements in zip(*sequences):
        # unless all elements are equal, bail out of the loop
        if not all_equal(elements):
            break

        # got one more common element, append it and keep looping
        common.append(elements[0])

    # return the common prefix and unique tails
    return common, [sequence[len(common) :] for sequence in sequences]


def relpath(p1, p2, sep=None, pardir=None):
    """Return a relative path from p1 equivalent to path p2.

    In particular:

        the empty string, if p1 == p2;
        p2, if p1 and p2 have no common prefix.

    Args:
        p1 (str): The path that wanted to be converted to a relative path to p2.
        p2 (str): The other path to base the p1 to.
        sep (str, Optional): Path separator.
        pardir (str, Optional): Parent dir operator. ".." most commonly.

    Returns:
        str: The processed relative path.
    """
    if sep is None:
        sep = os.path.sep

    if pardir is None:
        pardir = os.path.pardir

    # replace any trailing slashes at the end
    p1 = re.sub(r"[/]+$", "", p1)
    p1 = re.sub(r"[\\]+$", "", p1)

    common, (u1, u2) = common_prefix(p1.split(sep), p2.split(sep))
    if not common:
        return p2  # leave path absolute if nothing at all in common

    return sep.join([pardir] * len(u1) + u2)


def open_browser_in_location(path):
    """Open the os native browser at the given path.

    Args:
        path (str): The path that the browser should be opened at.

    Raises:
        IOError: When the given path doesn't exist
    """
    command = []
    path = os.path.normpath(os.path.expandvars(path))

    if not os.path.exists(path):
        path = os.path.dirname(path)

    if sys.platform.startswith("linux"):
        command = "xdg-open {}".format(path)
    elif sys.platform.startswith("win"):
        if os.path.isdir(path):
            command = "explorer {}".format(path.replace("/", "\\"))
        elif os.path.isfile(path):
            command = "explorer /select,{}".format(path.replace("/", "\\"))
    elif sys.platform == "darwin":
        # TODO: finder can not open files for now, fix it later
        if not os.path.isdir(path):
            path = os.path.dirname(path)
        command = "open -a /System/Library/CoreServices/Finder.app {}".format(path)

    if os.path.exists(path):
        subprocess.Popen(command, shell=True)
    else:
        raise IOError("%s doesn't exists!" % path)


def md5_checksum(path):
    """Generate md5 of a file with the given path.

    Args:
        path (str): absolute path to  the file.

    Returns:
        str: The mde5 checksum.
    """
    m = hashlib.md5()
    with open(path) as f:
        chunk = f.read(8192)
        while chunk:
            m.update(chunk)
            chunk = f.read(8192)
    return m.digest()


class StalkerThumbnailCache(object):
    """A simple file cache system."""

    @classmethod
    def get(cls, thumbnail_full_path, login=None, password=None):
        """Return the file either from cache or from stalker server.

        Args:
            thumbnail_full_path (str): The thumbnail full path.
            login (str): The user name.
            password (str): The user password.

        Returns:
            str: The thumbnail path.
        """
        # look up in the cache first
        filename = os.path.basename(thumbnail_full_path)
        logger.debug("filename : %s" % filename)

        cache_path = os.path.expanduser(defaults.local_cache_folder)
        cached_file_full_path = os.path.join(cache_path, filename)

        url = "%s/%s" % (defaults.stalker_server_internal_address, thumbnail_full_path)
        login_url = "%s/login" % defaults.stalker_server_internal_address

        logger.debug("cache_path            : %s" % cache_path)
        logger.debug("cached_file_full_path : %s" % cached_file_full_path)
        logger.debug("url                   : %s" % url)

        if not os.path.exists(cached_file_full_path) and login and password:
            # download the file and put it on to the cache
            if sys.version_info[0] >= 3:
                # Python 3
                from http.cookiejar import CookieJar
                from urllib.request import build_opener
                from urllib.parse import urlencode
                from urllib.request import HTTPCookieProcessor
            else:
                # Python 2
                from cookielib import CookieJar
                from urllib import urlencode
                from urllib2 import build_opener, HTTPCookieProcessor

            cj = CookieJar()
            opener = build_opener(HTTPCookieProcessor(cj))
            login_data = urlencode(
                {"login": login, "password": password, "submit": True}
            )
            opener.open(login_url, login_data)

            resp = opener.open(url)
            data = resp.read()

            # put it in to a file
            # TODO: from header decide ascii or binary mode
            if not os.path.exists(cache_path):
                os.makedirs(cache_path)

            with open(cached_file_full_path, "wb") as f:
                f.write(data)

        return cached_file_full_path


def do_db_setup():
    """Set up the database."""
    try:
        DBSession.connection()
        logger.debug("already connected, not creating any new connections")
    except UnboundExecutionError:
        # DBSession.remove()
        # DBSession.close()
        # no connection do setup
        logger.debug("doing a new connection with NullPool")

        settings = defaults.database_engine_settings
        settings["sqlalchemy.poolclass"] = NullPool
        db.setup(settings)


def utc_to_local(utc_dt):
    """Convert utc time to local time.

    based on the answer of J.F. Sebastian at
    http://stackoverflow.com/questions/4563272/how-to-convert-a-python-utc-datetime-to-a-local-datetime-using-only-python-stand/13287083#13287083

    Args:
        utc_dt (datetime.datetime): The UTC datetime instance.

    Returns:
        datetime.datetime: The localised version of the given UTC datetime.datetime
            instance.
    """
    # get integer timestamp to avoid precision lost
    timestamp = calendar.timegm(utc_dt.timetuple())
    local_dt = datetime.datetime.fromtimestamp(timestamp)
    return local_dt.replace(microsecond=utc_dt.microsecond)


def local_to_utc(local_dt):
    """Convert local datetime to utc datetime.

    based on the answer of J.F. Sebastian at
    http://stackoverflow.com/questions/4563272/how-to-convert-a-python-utc-datetime-to-a-local-datetime-using-only-python-stand/13287083#13287083

    Args:
        local_dt (datetime.datetime): The local datetime instance.

    Returns:
        datetime.datetime: The UTC version of the given local datetime.datetime
            instance.
    """
    # get the utc_dt as if the local_dt is utc and calculate the timezone
    # difference and add it to the local dt object
    return local_dt - (utc_to_local(local_dt) - local_dt)


class MediaManager(object):
    """Manages media files.

    MediaManager is the media hub of Stalker Pyramid. It is responsible of the
    uploads/downloads of media files and all kind of conversions.

    It can convert image, video and audio files. The default format for image
    files is PNG and the default format for video os WebM (VP8), and mp3
    (stereo, 96 kBit/s) is the default format for audio files.

    It can filter files from request parameters and upload them to the server,
    also for image files it will generate thumbnails and versions to be viewed
    from web.

    It can handle image sequences, and will create only one Link object per
    image sequence. The thumbnail of an image sequence will be a gif image.

    It will generate a zip file to serve all the images in an image sequence.
    """

    def __init__(self):
        self.reference_path = "References/Stalker_Pyramid/"
        self.version_output_path = "Outputs/Stalker_Pyramid/"

        # accepted image formats
        self.image_formats = [
            ".gif",
            ".ico",
            ".iff",
            ".jpg",
            ".jpeg",
            ".png",
            ".tga",
            ".tif",
            ".tiff",
            ".bmp",
            ".exr",
        ]

        # accepted video formats
        self.video_formats = [
            ".3gp",
            ".a64",
            ".asf",
            ".avi",
            ".dnxhd",
            ".f4v",
            ".filmstrip",
            ".flv",
            ".h261",
            ".h263",
            ".h264",
            ".ipod",
            ".m4v",
            ".matroska",
            ".mjpeg",
            ".mkv",
            ".mov",
            ".mp4",
            ".mpeg",
            ".mpg",
            ".mpeg1video",
            ".mpeg2video",
            ".mv",
            ".mxf",
            ".ogg",
            ".rm",
            ".swf",
            ".vc1",
            ".vcd",
            ".vob",
            ".webm",
        ]

        # thumbnail format
        self.thumbnail_format = ".jpg"
        self.thumbnail_width = 512
        self.thumbnail_height = 512
        self.thumbnail_options = {"quality": 80}  # default options for thumbnails

        # images and videos for web
        self.web_image_format = ".jpg"
        self.web_image_width = 1920
        self.web_image_height = 1080

        self.web_video_format = ".webm"
        self.web_video_width = 960
        self.web_video_height = 540
        self.web_video_bitrate = 4096  # in kBits/sec

        # commands
        self.ffmpeg_command_path = defaults.ffmpeg_command_path
        self.ffprobe_command_path = defaults.ffprobe_command_path

    @classmethod
    def reorient_image(cls, img):
        """Re-orient rotated images by looking at EXIF data.

        Args:
            img (PIL.Image): A PIL.Image instance.

        Returns:
            PIL.Image: A PIL.Image instance.
        """
        # get the image rotation from EXIF information
        file_full_path = img.filename

        with open(file_full_path) as f:
            tags = exifread.process_file(f)

        orientation_string = tags.get("Image Orientation")

        from PIL import Image

        if orientation_string:
            orientation = orientation_string.values[0]
            if orientation == 1:
                # do nothing
                pass
            elif orientation == 2:  # flipped in X
                img = img.transpose(Image.FLIP_LEFT_RIGHT)
            elif orientation == 3:  # rotated 180 degree
                img = img.transpose(Image.ROTATE_180)
            elif orientation == 4:  # flipped in Y
                img = img.transpose(Image.FLIP_TOP_BOTTOM)
            elif orientation == 5:  #
                img = img.transpose(Image.ROTATE_270)
                img = img.transpose(Image.FLIP_LEFT_RIGHT)
            elif orientation == 6:
                img = img.transpose(Image.FLIP_LEFT_RIGHT)
            elif orientation == 7:
                img = img.transpose(Image.ROTATE_90)
                img = img.transpose(Image.FLIP_LEFT_RIGHT)
            elif orientation == 8:
                img = img.transpose(Image.ROTATE_90)

        return img

    def generate_image_thumbnail(self, file_full_path):
        """Generate a thumbnail for the given image file.

        Args:
            file_full_path (str): Generates a thumbnail for the given file in the given
                path.

        Returns:
            str: The thumbnail path.
        """
        # generate thumbnail for the image and save it to a tmp folder
        suffix = self.thumbnail_format

        from PIL import Image

        img = Image.open(file_full_path)
        # do a double scale
        img.thumbnail((2 * self.thumbnail_width, 2 * self.thumbnail_height))
        img.thumbnail((self.thumbnail_width, self.thumbnail_height), Image.ANTIALIAS)

        # re-orient images
        img = self.reorient_image(img)

        if img.format == "GIF":
            suffix = ".gif"  # force save in gif format
        else:
            # check if the image is in RGB mode
            if img.mode != "RGB":
                img = img.convert("RGB")
        thumbnail_path = tempfile.mktemp(suffix=suffix)

        img.save(thumbnail_path, **self.thumbnail_options)
        return thumbnail_path

    def generate_image_for_web(self, file_full_path):
        """Generate a version suitable to be viewed from a web browser.

        Args:
            file_full_path (str): Generates a thumbnail for the given file in the given
                path.

        Returns:
            str: The thumbnail path.
        """
        # generate thumbnail for the image and save it to a tmp folder
        suffix = self.thumbnail_format

        from PIL import Image

        img = Image.open(file_full_path)
        if img.size[0] > self.web_image_width or img.size[1] > self.web_image_height:
            # do a double scale
            img.thumbnail((2 * self.web_image_width, 2 * self.web_image_height))
            img.thumbnail(
                (self.web_image_width, self.web_image_height), Image.ANTIALIAS
            )

        # re-orient images
        img = self.reorient_image(img)

        if img.format == "GIF":
            suffix = ".gif"  # force save in gif format
        else:
            # check if the image is in RGB mode
            if img.mode != "RGB":
                img = img.convert("RGB")

        thumbnail_path = tempfile.mktemp(suffix=suffix)

        img.save(thumbnail_path)
        return thumbnail_path

    def generate_video_thumbnail(self, file_full_path):
        """Generate a thumbnail for the given video link.

        Args:
            file_full_path (str): A string showing the full path of the video file.

        Returns:
            str: The thumbnail file path.
        """
        # TODO: split this in to two different methods, one generating
        #       thumbnails from the video and another one accepting three
        #       images
        media_info = self.get_video_info(file_full_path)
        video_info = media_info["video_info"]

        # get the correct stream
        video_stream = None
        for stream in media_info["stream_info"]:
            if stream["codec_type"] == "video":
                video_stream = stream

        nb_frames = video_stream.get("nb_frames")
        if nb_frames is None or nb_frames == "N/A":
            # no nb_frames
            # first try to use "r_frame_rate" and "duration"
            frame_rate = video_stream.get("r_frame_rate")

            if frame_rate is None:  # still no frame rate
                # try to use the video_info and duration
                # and try to get frame rate
                frame_rate = float(video_info.get("TAG:framerate", 23.976))
            else:
                # check if it is in Number/Number format
                if "/" in frame_rate:
                    nominator, denominator = frame_rate.split("/")
                    frame_rate = float(nominator) / float(denominator)

            # get duration
            duration = video_stream.get("duration")
            if duration == "N/A":  # no duration
                duration = float(video_info.get("duration", 1))
            else:
                duration = float(duration)

            # at this stage we should have enough info, may not be correct but
            # we should have something
            # calculate nb_frames
            logger.debug("duration  : %s" % duration)
            logger.debug("frame_rate: %s" % frame_rate)
            nb_frames = int(duration * frame_rate)
        nb_frames = int(nb_frames)

        start_thumb_path = tempfile.mktemp(suffix=self.thumbnail_format)
        mid_thumb_path = tempfile.mktemp(suffix=self.thumbnail_format)
        end_thumb_path = tempfile.mktemp(suffix=self.thumbnail_format)

        thumbnail_path = tempfile.mktemp(suffix=self.thumbnail_format)

        # generate three thumbnails from the start, middle and end of the file
        start_frame = int(nb_frames * 0.10)
        mid_frame = int(nb_frames * 0.5)
        end_frame = int(nb_frames * 0.90) - 1

        # start_frame
        self.ffmpeg(
            **{
                "i": file_full_path,
                "vf": "select='eq(n,0)'",
                "vframes": start_frame,
                "o": start_thumb_path,
            }
        )
        # mid_frame
        self.ffmpeg(
            **{
                "i": file_full_path,
                "vf": "select='eq(n,%s)'" % mid_frame,
                "vframes": 1,
                "o": mid_thumb_path,
            }
        )
        # end_frame
        self.ffmpeg(
            **{
                "i": file_full_path,
                "vf": "select='eq(n,%s)'" % end_frame,
                "vframes": 1,
                "o": end_thumb_path,
            }
        )

        # check if all of the thumbnails are present
        if not os.path.exists(start_thumb_path):
            if os.path.exists(mid_thumb_path):
                start_thumb_path = mid_thumb_path
            elif os.path.exists(end_thumb_path):
                start_thumb_path = end_thumb_path
                mid_thumb_path = end_thumb_path

        if not os.path.exists(mid_thumb_path):
            if os.path.exists(start_thumb_path):
                mid_thumb_path = start_thumb_path
            else:
                start_thumb_path = end_thumb_path
                mid_thumb_path = end_thumb_path

        if not os.path.exists(end_thumb_path):
            # use the mid frame if available or the start frame
            if os.path.exists(mid_thumb_path):
                end_thumb_path = mid_thumb_path
            else:
                mid_thumb_path = start_thumb_path
                end_thumb_path = start_thumb_path

        # now merge them
        self.ffmpeg(
            **{
                "i": [start_thumb_path, mid_thumb_path, end_thumb_path],
                "filter_complex": "[0:0]scale=3*%(tw)s/4:-1,pad=%(tw)s:%(th)s[s];"
                "[1:0]scale=3*%(tw)s/4:-1,fade=out:300:30:alpha=1[m];"
                "[2:0]scale=3*%(tw)s/4:-1,fade=out:300:30:alpha=1[e];"
                "[s][e]overlay=%(tw)s/4:%(th)s-h[x];"
                "[x][m]overlay=%(tw)s/8:%(th)s/2-h/2"
                % {"tw": self.thumbnail_width, "th": self.thumbnail_height},
                "o": thumbnail_path,
            }
        )

        # remove the intermediate data
        try:
            os.remove(start_thumb_path)
        except OSError:
            pass

        try:
            os.remove(mid_thumb_path)
        except OSError:
            pass

        try:
            os.remove(end_thumb_path)
        except OSError:
            pass

        return thumbnail_path

    def generate_video_for_web(self, file_full_path):
        """Generate a web friendly version for the given video.

        Args:
            file_full_path (str): A string showing the full path of the video file.

        Returns:
            str: The web version full path.
        """
        web_version_full_path = tempfile.mktemp(suffix=self.web_video_format)
        self.convert_to_webm(file_full_path, web_version_full_path)
        return web_version_full_path

    def generate_thumbnail(self, file_full_path):
        """Generate a thumbnail for the given link.

        Args:
            file_full_path (str): Generates a thumbnail for the given file in the given
                path.

        Raises:
            RuntimeError: If the given file path is not a video or image file path.

        Returns:
            str: The thumbnail path.
        """
        extension = os.path.splitext(file_full_path)[-1].lower()
        # check if it is an image or video or non of them
        if extension in self.image_formats:
            # generate a thumbnail from image
            return self.generate_image_thumbnail(file_full_path)
        elif extension in self.video_formats:
            return self.generate_video_thumbnail(file_full_path)

        # not an image nor a video so no thumbnail, raise RuntimeError
        raise RuntimeError(
            "%s is not an image nor a video file, can not "
            "generate a thumbnail for it!" % file_full_path
        )

    def generate_media_for_web(self, file_full_path):
        """Generate a media suitable for web browsers.

        It will generate PNG for images, and a WebM for video files.

        Args:
            file_full_path (str): Generates a web suitable version for the given file in
                the given path.

        Raises:
            RuntimeError: If the given file path is not a video or image file path.

        Returns:
            str: Returns the media file path.
        """
        extension = os.path.splitext(file_full_path)[-1].lower()
        # check if it is an image or video or non of them
        if extension in self.image_formats:
            # generate a thumbnail from image
            return self.generate_image_for_web(file_full_path)
        elif extension in self.video_formats:
            return self.generate_video_for_web(file_full_path)

        # not an image nor a video so no thumbnail, raise RuntimeError
        raise RuntimeError("%s is not an image nor a video file!" % file_full_path)

    @classmethod
    def generate_local_file_path(cls, extension=""):
        """Generate  file paths in server side storage.

        Args:
            extension (str): Desired file extension.

        Returns:
            str: The local file path.
        """
        # upload it to the stalker server side storage path
        new_filename = uuid.uuid4().hex + extension
        first_folder = new_filename[:2]
        second_folder = new_filename[2:4]
        file_path = os.path.join(
            defaults.server_side_storage_path, first_folder, second_folder
        )

        file_full_path = os.path.join(file_path, new_filename)

        return file_full_path

    def get_video_info(self, full_path):
        """Return the video info like the duration in seconds and fps.

        Uses ffmpeg to extract information about the video file.

        Args:
            full_path (str): The full path of the video file

        Returns:
            list: A list containing the video info.
        """
        output_buffer = self.ffprobe(
            **{
                "show_streams": full_path,
            }
        )

        media_info = {"video_info": None, "stream_info": []}
        video_info = {}
        stream_info = {}

        # get STREAM info
        line = output_buffer.pop(0).strip()
        while line is not None:
            if line == "[STREAM]":
                # pop until you find [/STREAM]
                while line != "[/STREAM]":
                    if "=" in line:
                        flag, value = line.split("=")
                        stream_info[flag] = value
                    line = output_buffer.pop(0).strip()

                copy_stream = copy.deepcopy(stream_info)
                media_info["stream_info"].append(copy_stream)
                stream_info = {}
            try:
                line = output_buffer.pop(0).strip()
            except IndexError:
                line = None

        # also get FORMAT info
        output_buffer = self.ffprobe(
            **{
                "show_format": full_path,
            }
        )

        line = output_buffer.pop(0).strip()
        while line is not None:
            if line == "[FORMAT]":
                # pop until you find [/FORMAT]
                while line != "[/FORMAT]":
                    if "=" in line:
                        flag, value = line.split("=")
                        video_info[flag] = value
                    line = output_buffer.pop(0).strip()

                media_info["video_info"] = video_info
            try:
                line = output_buffer.pop(0).strip()
            except IndexError:
                line = None

        return media_info

    def ffmpeg(self, **kwargs):
        """``ffmpeg`` command wrapper.

        Args:
            kwargs: Keyword arguments to pass to the ffmpeg command.

        Returns:
            str: The command output buffer.
        """
        # there is only one special keyword called 'o'

        # this will raise KeyError if there is no 'o' key which is good to
        # prevent the rest to execute
        output = kwargs.get("o")
        try:
            kwargs.pop("o")
        except KeyError:  # no output
            pass

        # generate args
        args = [self.ffmpeg_command_path]

        # first process the -start_number flag
        if "start_number" in kwargs:
            key = "start_number"
            flag = "-%s" % key
            # use pop to remove the key
            value = kwargs.pop(key)
            # append the flag
            args.append(flag)
            # append the value
            args.append(str(value))

        # process framerate option
        # if this is included later it causes the video duration to be
        # interpretted in a wrong manner
        if "framerate" in kwargs:
            key = "framerate"
            flag = "-%s" % key
            # use pop to remove the key
            value = kwargs.pop(key)
            # append the flag
            args.append(flag)
            # append the value
            args.append(str(value))

        # first process the -i flag
        if "i" in kwargs:
            ss_key = "ss"
            ss_flag = "-%s" % ss_key
            ss_value = None
            to_key = "to"
            to_flag = "-%s" % to_key
            to_value = None
            if ss_key in kwargs:
                # seek for each input
                # use pop to remove the key
                ss_value = kwargs.pop(ss_key)
            if to_key in kwargs:
                # seek for each input
                # use pop to remove the key
                to_value = kwargs.pop(to_key)

            key = "i"
            flag = "-%s" % key
            # use pop to remove the key
            value = kwargs.pop(key)
            if not isinstance(value, list):
                if ss_value:
                    # put ss before i
                    args.append(ss_flag)
                    args.append(ss_value)
                if to_value:
                    # put to after ss and before i
                    args.append(to_flag)
                    args.append(to_value)

                # append the flag
                args.append(flag)
                # append the value
                args.append(str(value))
            else:
                # it is a multi flag
                # so append the flag every time you append the key
                for i, v in enumerate(value):
                    if ss_value and ss_value[i]:
                        # put ss before i
                        args.append(ss_flag)
                        args.append(ss_value[i])
                    if to_value and to_value[i]:
                        # put to after ss and before i
                        args.append(to_flag)
                        args.append(to_value[i])
                    args.append(flag)
                    args.append(str(v))

        # then include the other flags
        for key in kwargs:
            flag = "-" + key
            value = kwargs[key]
            if not isinstance(value, list):
                # append the flag
                args.append(flag)
                # append the value
                args.append(str(value))
            else:
                # it is a multi flag
                # so append the flag every time you append the key
                for v in value:
                    args.append(flag)
                    args.append(str(v))

        # if output format is not a jpg or png
        # if output.split(".")[-1] not in ["jpg", "jpeg", "png", "tga"]:
        #     # use all cpus
        #     import multiprocessing

        #     num_of_threads = multiprocessing.cpu_count()
        #     args.append("-threads")
        #     args.append("%s" % num_of_threads)

        # overwrite any file
        args.append("-y")

        # append the output
        if output != "" and output is not None:  # for info only
            args.append(output)

        logger.debug("calling ffmpeg with args: %s" % args)

        startupinfo = None
        if os.name == "nt":
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

        print("ffmpeg command: %s" % " ".join(args))

        process = subprocess.Popen(
            args, stderr=subprocess.PIPE, startupinfo=startupinfo
        )

        # loop until process finishes and capture stderr output
        stderr_buffer = []
        while True:
            stderr = process.stderr.readline()
            if not isinstance(stderr, str):
                stderr = stderr.decode("utf-8", "replace")

            if stderr == "" and process.poll() is not None:
                break

            if stderr != "":
                stderr_buffer.append(stderr)

        # if process.returncode:
        #     # there is an error
        #     raise RuntimeError(stderr_buffer)

        logger.debug(stderr_buffer)
        logger.debug("process completed!")
        return stderr_buffer

    def ffprobe(self, **kwargs):
        """`ffprobe`` command wrapper.

        Args:
            kwargs: Keyword arguments to pass to the ffprobe command.

        Returns:
            str: The command output buffer.
        """
        # generate args
        args = [self.ffprobe_command_path]
        for key in kwargs:
            flag = "-" + key
            value = kwargs[key]
            if not isinstance(value, list):
                # append the flag
                args.append(flag)
                # append the value
                args.append(str(value))
            else:
                # it is a multi flag
                # so append the flag every time you append the key
                for v in value:
                    args.append(flag)
                    args.append(str(v))

        logger.debug("calling ffprobe with args: %s" % args)

        startupinfo = None
        if os.name == "nt":
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

        process = subprocess.Popen(
            args, stdout=subprocess.PIPE, startupinfo=startupinfo
        )

        # loop until process finishes and capture stderr output
        stdout_buffer = []
        while True:
            stdout = process.stdout.readline()
            if not isinstance(stdout, str):
                stdout = stdout.decode("utf-8", "replace")

            if stdout == "" and process.poll() is not None:
                break

            if stdout != "":
                stdout_buffer.append(stdout)

        # if process.returncode:
        #     # there is an error
        #     raise RuntimeError(stderr_buffer)

        logger.debug(stdout_buffer)
        logger.debug("process completed!")
        return stdout_buffer

    def convert_to_h264(self, input_path, output_path, options=None):
        """Convert the given input to h264.

        Args:
            input_path (str): A string of path, can have wild card characters.
            output_path (str): The output path.
            options (dict): Extra options to pass to the ffmpeg command.

        Returns:
            str: The h264 file path.
        """
        if options is None:
            options = {}

        # change the extension to mp4
        output_path = "%s%s" % (os.path.splitext(output_path)[0], ".mp4")

        conversion_options = {
            "i": input_path,
            "vcodec": "libx264",
            "vf": "format=yuv420p",  # to support whatsapp
            # 'profile:v': 'main',
            "g": 1,  # key frame every 1 frame
            "b:v": "20480k",
            "o": output_path,
        }
        conversion_options.update(options)
        pprint.pprint(conversion_options)
        self.ffmpeg(**conversion_options)
        return output_path

    def convert_to_webm(self, input_path, output_path, options=None):
        """Convert the given input to webm format.

        Args:
            input_path (str): A string of path, can have wild card characters.
            output_path (str): The output path.
            options (dict): Extra options to pass to the ffmpeg command.

        Returns:
            str: The webm file path.
        """
        if options is None:
            options = {}

        # change the extension to webm
        output_path = "%s%s" % (os.path.splitext(output_path)[0], ".webm")

        conversion_options = {
            "i": input_path,
            "vcodec": "libvpx",
            "b:v": "%sk" % self.web_video_bitrate,
            "o": output_path,
        }
        conversion_options.update(options)

        self.ffmpeg(**conversion_options)

        return output_path

    def convert_to_prores(self, input_path, output_path, options=None):
        """Convert the given input to Apple Prores 422 format.

        Args:
            input_path (str): A string of path, can have wild card characters.
            output_path (str): The output path.
            options (dict): Extra options to pass to the ffmpeg command.

        Returns:
            str: The prores file path.
        """
        if options is None:
            options = {}

        # change the extension to webm
        output_path = "%s%s" % (os.path.splitext(output_path)[0], ".mov")

        conversion_options = {
            "i": input_path,
            "probesize": 5000000,
            "f": "image2",
            "profile:v": 3,
            "qscale:v": 13,  # use between 9 - 13
            "vcodec": "prores_ks",
            "vendor": "ap10",
            "vf": "format=yuv422p10le",
            "o": output_path,
        }
        conversion_options.update(options)

        self.ffmpeg(**conversion_options)

        return output_path

    def convert_to_mjpeg(self, input_path, output_path, options=None):
        """Convert the given input to Apple Motion Jpeg format.

        Args:
            input_path (str): A string of path, can have wild card characters.
            output_path (str): The output path.
            options (dict): Extra options to pass to the ffmpeg command.

        Returns:
            str: The mjpg file path.
        """
        if options is None:
            options = {}

        # change the extension to webm
        output_path = "%s%s" % (os.path.splitext(output_path)[0], ".mov")

        # ffmpeg -y
        # -probesize 5000000
        # -f image2
        # -r 48
        # -force_fps
        # -i ${DPX_HERO}
        # -c:v mjpeg
        # -qscale:v 1
        # -vendor ap10
        # -vf format=yuvj422p
        # -s 2048x1152
        # -r 48 output.mov
        conversion_options = {
            "i": input_path,
            "probesize": 5000000,
            "f": "image2",
            "qscale:v": 1,
            "vcodec": "mjpeg",
            "vendor": "ap10",
            "vf": "format=yuv422p",
            "o": output_path,
        }
        conversion_options.update(options)

        self.ffmpeg(**conversion_options)

        return output_path

    @classmethod
    def convert_to_animated_gif(cls, input_path, output_path, options=None):
        """Convert the given input to animated gif.

        Args:
            input_path (str): A string of path, can have wild card characters.
            output_path (str): The output path.
            options (dict): Extra options to pass to the ffmpeg command.

        Returns:
            str: The gif path.
        """
        if options is None:
            options = {}

        # change the extension to gif
        output_path = "%s%s" % (os.path.splitext(output_path)[0], ".gif")

        conversion_options = {"i": input_path, "o": output_path}
        conversion_options.update(options)

        cls.ffmpeg(**conversion_options)

        return output_path

    def upload_with_request_params(self, file_params):
        """Upload objects with request params.

        Args:
            file_params: An object with two attributes, first a ``filename`` attribute
                and a ``file`` which is a file like object.

        Returns:
            list: A list containing the uploaded file info.
        """
        uploaded_file_info = []
        # get the file names
        for file_param in file_params:
            filename = file_param.filename
            file_object = file_param.file

            # upload to a temp path
            uploaded_file_full_path = self.upload_file(
                file_object, tempfile.mkdtemp(), filename
            )

            # return the file information
            file_info = {
                "full_path": uploaded_file_full_path,
                "original_filename": filename,
            }

            uploaded_file_info.append(file_info)

        return uploaded_file_info

    @classmethod
    def randomize_file_name(cls, full_path):
        """Randomize the file name by adding the first 4 characters of a UUID4 sequence.

        Args:
            full_path (str): The filename to be randomized.

        Returns:
            str: The randomized filename.
        """
        # get the filename
        path = os.path.dirname(full_path)
        filename = os.path.basename(full_path)

        # get the base name
        basename, extension = os.path.splitext(filename)

        # generate uuid4 sequence until there is no file with that name
        def generate():
            random_part = "_%s" % uuid.uuid4().hex[:4]
            return os.path.join(path, "%s%s%s" % (basename, random_part, extension))

        random_file_full_path = generate()
        # generate until we have something unique
        # it will be the first one 99.9% of time
        while os.path.exists(random_file_full_path):
            random_file_full_path = generate()

        return random_file_full_path

    @classmethod
    def format_filename(cls, filename):
        """Format the filename to comply with file naming rules of Stalker Pyramid.

        Args:
            filename (str): The filename to format.

        Returns:
            str: The formatted filename.
        """
        if isinstance(filename, str):
            filename = filename.decode("utf-8")

        # replace Turkish characters
        bad_character_map = {
            "\xc3\xa7": "c",
            "\xc4\x9f": "g",
            "\xc4\xb1": "i",
            "\xc3\xb6": "o",
            "\xc5\x9f": "s",
            "\xc3\xbc": "u",
            "\xc3\x87": "C",
            "\xc4\x9e": "G",
            "\xc4\xb0": "I",
            "\xc5\x9e": "S",
            "\xc3\x96": "O",
            "\xc3\x9c": "U",
            "\xe7": "c",
            "\u011f": "g",
            "\u0131": "i",
            "\xf6": "o",
            "\u015f": "s",
            "\xfc": "u",
            "\xc7": "C",
            "\u011e": "G",
            "\u0130": "I",
            "\u015e": "S",
            "\xd6": "O",
            "\xdc": "U",
        }
        filename_buffer = []
        for char in filename:
            if char in bad_character_map:
                filename_buffer.append(bad_character_map[char])
            else:
                filename_buffer.append(char)
        filename = "".join(filename_buffer)

        # replace ' ' with '_'
        basename, extension = os.path.splitext(filename)
        filename = "%s%s" % (
            re.sub(r'[\s\.\\/:\*\?"<>|=,+]+', "_", basename),
            extension,
        )

        return filename

    def upload_file(self, file_object, file_path=None, filename=None):
        """Upload files to the given path.

        The data of the files uploaded from a Web application is hold in a file
        like object. This method dumps the content of this file like object to
        the given path.

        Args:
            file_object (file): File like object holding the data.
            file_path (str): The path of the file to output the data to. If it is
                skipped the data will be written to a temp folder.
            filename (str): The desired file name for the uploaded file. If it is
                skipped a unique temp filename will be generated.

        Returns:
            str: The uploaded file full path.
        """
        if file_path is None:
            file_path = tempfile.gettempdir()

        if filename is None:
            filename = tempfile.mktemp(dir=file_path)
        else:
            filename = self.format_filename(filename)

        file_full_path = os.path.join(file_path, filename)
        if os.path.exists(file_full_path):
            file_full_path = self.randomize_file_name(file_full_path)

        # write down to a temp file first
        temp_file_full_path = "%s~" % file_full_path

        # create folders
        try:
            os.makedirs(file_path)
        except OSError:  # Path exist
            pass

        with open(temp_file_full_path, "wb") as output_file:
            file_object.seek(0)
            while True:
                data = file_object.read(2 << 16)
                if not data:
                    break
                output_file.write(data)

        # data is written completely, rename temp file to original file
        os.rename(temp_file_full_path, file_full_path)

        return file_full_path

    def upload_reference(self, task, file_object, filename):
        """Upload a reference for the given task.

        Upload to the Task.path/References/Stalker_Pyramid/ folder and create a Link
        object to there. Again the Link object will have a Repository root relative
        path.

        It will also create a thumbnail under
        {{Task.absolute_path}}/References/Stalker_Pyramid/Thumbs folder and a
        web friendly version (PNG for images, WebM for video files) under
        {{Task.absolute_path}}/References/Stalker_Pyramid/ForWeb folder.

        Args:
            task (stalker.Task): The task that a reference is uploaded to. Should be an
                instance of :class:`.Task` class.
            file_object (file): The file like object holding the content of the uploaded
                file.
            filename (str): The original filename.

        Returns:
            stalker.Link: A :class:`stalker.Link` instance.
        """
        ############################################################
        # ORIGINAL
        ############################################################
        file_path = os.path.join(os.path.join(task.absolute_path), self.reference_path)

        # upload it
        reference_file_full_path = self.upload_file(file_object, file_path, filename)

        reference_file_file_name = os.path.basename(reference_file_full_path)
        reference_file_base_name = os.path.splitext(reference_file_file_name)[0]

        # create a Link instance and return it.
        # use a Repository relative path
        repo = task.project.repository
        relative_full_path = repo.make_relative(reference_file_full_path)

        link = Link(full_path=relative_full_path, original_filename=filename)

        # create a thumbnail for the given reference
        # don't forget that the first thumbnail is the Web viewable version
        # and the second thumbnail is the thumbnail

        ############################################################
        # WEB VERSION
        ############################################################
        web_version_temp_full_path = self.generate_media_for_web(
            reference_file_full_path
        )
        web_version_extension = os.path.splitext(web_version_temp_full_path)[-1]

        web_version_file_name = "%s%s" % (
            reference_file_base_name,
            web_version_extension,
        )
        web_version_full_path = os.path.join(
            os.path.dirname(reference_file_full_path), "ForWeb", web_version_file_name
        )
        web_version_repo_relative_full_path = repo.make_relative(web_version_full_path)
        web_version_link = Link(
            full_path=web_version_repo_relative_full_path,
            original_filename=web_version_file_name,
        )

        # move it to repository
        try:
            os.makedirs(os.path.dirname(web_version_full_path))
        except OSError:  # path exists
            pass
        shutil.move(web_version_temp_full_path, web_version_full_path)

        ############################################################
        # THUMBNAIL
        ############################################################
        # finally generate a Thumbnail
        thumbnail_temp_full_path = self.generate_thumbnail(reference_file_full_path)
        thumbnail_extension = os.path.splitext(thumbnail_temp_full_path)[-1]
        thumbnail_file_name = "%s%s" % (reference_file_base_name, thumbnail_extension)

        thumbnail_full_path = os.path.join(
            os.path.dirname(reference_file_full_path), "Thumbnail", thumbnail_file_name
        )
        thumbnail_repo_relative_full_path = repo.make_relative(thumbnail_full_path)
        thumbnail_link = Link(
            full_path=thumbnail_repo_relative_full_path,
            original_filename=thumbnail_file_name,
        )

        # move it to repository
        try:
            os.makedirs(os.path.dirname(thumbnail_full_path))
        except OSError:  # path exists
            pass
        shutil.move(thumbnail_temp_full_path, thumbnail_full_path)

        ############################################################
        # LINK Objects
        ############################################################
        # link them
        # assign it as a reference to the given task
        task.references.append(link)
        link.thumbnail = web_version_link
        web_version_link.thumbnail = thumbnail_link

        return link

    def upload_version(self, task, file_object, take_name=None, extension=""):
        """Upload versions to the Task.path folder and create a Version object.

        Again the Version object will have a Repository root relative path.

        The filename of the version will be automatically generated by Stalker.

        Args:
            task (stalker.Task): The task that a version is uploaded to. Should be an
                instance of :class:`.Task` class.
            file_object (file): A file like object holding the content of the version.
            take_name (str): A string showing the the take name of the Version.
                If skipped defaults.version_take_name will be used.
            extension (str): The file extension of the version.

        Returns:
            stalker.Version: A :class:`stalker.Version` instance.
        """
        if take_name is None:
            take_name = defaults.version_take_name

        v = Version(task=task, take_name=take_name, created_with="Stalker Pyramid")
        v.update_paths()
        v.extension = extension

        # upload it
        self.upload_file(file_object, v.absolute_path, v.filename)

        return v

    def upload_version_output(self, version, file_object, filename):
        """Upload a file as an output for the given :class:`.Version` instance.

        Will store the file in {{Version.absolute_path}}/Outputs/Stalker_Pyramid/
        folder.

        It will also generate a thumbnail in
        {{Version.absolute_path}}/Outputs/Stalker_Pyramid/Thumbs folder and a
        web friendly version (PNG for images, WebM for video files) under
        {{Version.absolute_path}}/Outputs/Stalker_Pyramid/ForWeb folder.

        Args:
            version (stalker.Version): A :class:`.Version` instance that the output is
                uploaded for.
            file_object (file): The file like object holding the content of the
                uploaded file.
            filename (str): The original filename.

        Returns:
            stalker.Link: stalker.Link instance.
        """
        ############################################################
        # ORIGINAL
        ############################################################
        file_path = os.path.join(
            os.path.join(version.absolute_path), self.version_output_path
        )

        # upload it
        version_output_file_full_path = self.upload_file(
            file_object, file_path, filename
        )

        version_output_file_name = os.path.basename(version_output_file_full_path)
        version_output_base_name = os.path.splitext(version_output_file_name)[0]

        # create a Link instance and return it.
        # use a Repository relative path
        repo = version.task.project.repository

        full_path = str(version_output_file_full_path)

        link = Link(
            full_path=repo.to_os_independent_path(full_path),
            original_filename=str(filename),
        )

        # create a thumbnail for the given version output
        # don't forget that the first thumbnail is the Web viewable version
        # and the second thumbnail is the thumbnail

        ############################################################
        # WEB VERSION
        ############################################################
        web_version_link = None
        try:
            web_version_temp_full_path = self.generate_media_for_web(
                version_output_file_full_path
            )
            web_version_extension = os.path.splitext(web_version_temp_full_path)[-1]
            web_version_full_path = os.path.join(
                os.path.dirname(version_output_file_full_path),
                "ForWeb",
                version_output_base_name + web_version_extension,
            )

            web_version_link = Link(
                full_path=repo.to_os_independent_path(web_version_full_path),
                original_filename=filename,
            )

            # move it to repository
            try:
                os.makedirs(os.path.dirname(web_version_full_path))
            except OSError:  # path exists
                pass
            shutil.move(web_version_temp_full_path, web_version_full_path)
        except RuntimeError:
            # not an image or video so skip it
            pass

        ############################################################
        # THUMBNAIL
        ############################################################
        # finally generate a Thumbnail
        thumbnail_link = None
        try:
            thumbnail_temp_full_path = self.generate_thumbnail(
                version_output_file_full_path
            )
            thumbnail_extension = os.path.splitext(thumbnail_temp_full_path)[-1]

            thumbnail_full_path = os.path.join(
                os.path.dirname(version_output_file_full_path),
                "Thumbnail",
                version_output_base_name + thumbnail_extension,
            )

            thumbnail_link = Link(
                full_path=repo.to_os_independent_path(thumbnail_full_path),
                original_filename=filename,
            )

            # move it to repository
            try:
                os.makedirs(os.path.dirname(thumbnail_full_path))
            except OSError:  # path exists
                pass
            shutil.move(thumbnail_temp_full_path, thumbnail_full_path)
        except RuntimeError:
            # not an image or video so skip it
            pass

        ############################################################
        # LINK Objects
        ############################################################
        # link them
        # assign it as an output to the given version
        version.outputs.append(link)
        if web_version_link:
            link.thumbnail = web_version_link
            if thumbnail_link:
                web_version_link.thumbnail = thumbnail_link

        return link


class Exposure(object):
    """A class for photo exposure calculation.

    Args:
        shutter (float | Fraction): The shutter in seconds. 1/125 for 1/125 seconds.
        f_stop (float): The F-Stop number. 8 for f/8.
        iso (float): The ISO number. 100 for ISO 100.
    """

    def __init__(self, shutter=None, f_stop=None, iso=None):
        self._shutter = None
        self.shutter = shutter
        self.f_stop = f_stop
        self.iso = iso

    @property
    def shutter(self):
        """Getter for the shutter property.

        Returns:
            float: The shutter value.
        """
        return self._shutter

    @shutter.setter
    def shutter(self, shutter):
        """Setter for the shutter property.

        Args:
            shutter (float): Shutter value.
        """
        if not isinstance(shutter, fractions.Fraction):
            self._shutter = fractions.Fraction(shutter)
        else:
            self._shutter = shutter

    def to(self, other_exp):
        """Calculate the exposure to equalize this exposure to the the given exposure.

        Args:
            other_exp (Exposure): The other Exposure instance

        Returns:
            float: The exposure difference.
        """
        # convert every thing to fractions
        shutter = math.log(
            float(other_exp.shutter.numerator)
            * float(self.shutter.denominator)
            / (float(other_exp.shutter.denominator) * float(self.shutter.numerator)),
            2,
        )

        f_stop = math.log(
            (float(self.f_stop) * float(self.f_stop))
            / (float(other_exp.f_stop) * float(other_exp.f_stop)),
            2,
        )
        iso = math.log(float(other_exp.iso) / float(self.iso), 2)
        return shutter + f_stop + iso

    def from_(self, other_exp):
        """Calculate the exposure to equalize the other exposure to this exposure.

        Args:
            other_exp (Exposure): The other Exposure instance.

        Returns:
            float: The exposure difference.
        """
        return -self.to(other_exp)


def create_structure(entity):
    """Create the directory structure of the given project or task.

    Also consider custom template structure.

    Args:
        entity (stalker.Project | stalker.Task): A Stalker Project or Task instance
    """
    custom_template = None
    project = None
    task = None
    tasks = []

    if isinstance(entity, Project):
        project = entity
        task = None
        custom_template = project.structure.custom_template
        tasks = project.tasks

    elif isinstance(entity, Task):
        task = entity
        tasks = [entity]
        custom_template = task.project.structure.custom_template

    # Task Folders
    for t in tasks:
        try:
            os.makedirs(t.absolute_path)
        except OSError:
            # path already exist
            pass

    # Custom Template
    if custom_template:
        import jinja2

        template = jinja2.Template(custom_template, extensions=["jinja2.ext.do"])
        paths = template.render(project=project, entity=task).split("\n")
        for path in paths:
            path = path.strip()
            if path != "":
                try:
                    os.makedirs(path)
                except OSError:
                    # path already exist
                    pass


def file_browser_name():
    """Return the file browser name of the current OS.

    Returns:
        str: The file browser name.
    """
    file_browsers = {
        "windows": "Explorer",  # All windows versions
        "darwin": "Finder",  # OSX
        "linux": "File Browser",  # Gnome: Files, Ubuntu: Nautilus
    }
    return file_browsers[platform.system().lower()]


def generate_unique_shot_name(project, base_name, shot_name_increment=10):
    """Generate a unique shot name and code based of the base_name.

    Args:
        project (stalker.Project): Search unique shot in this project.
        base_name (str): The base shot name
        shot_name_increment (int): The increment amount

    Raises:
        RuntimeError: If it is not possible to generate a unique name.

    Returns:
        str: The unique shot name.
    """
    logger.debug("generating unique shot number based on: {}".format(base_name))
    logger.debug("shot_name_increment is: {}".format(shot_name_increment))

    regex = re.compile("[0-9]+")

    # base_name: Ep001_001_0010
    name_parts = base_name.split("_")

    # find the shot number
    try:
        shot_number_as_string = regex.findall(name_parts[-1])[-1]
    except IndexError:
        # no number in name
        name_parts = [name_parts[0], "000"]
        shot_number_as_string = "000"

    padding = len(shot_number_as_string)
    shot_number = int(shot_number_as_string)

    # initialize from the given shot_number
    i = shot_number

    logger.debug("start shot_number: {}".format(shot_number))

    while True and i < 100000:
        name_parts[-1] = str(i).zfill(padding)
        shot_name = "_".join(name_parts)
        if is_unique_shot_name(project, shot_name):
            logger.debug("generated unique shot name: %s" % shot_name)
            return shot_name
        i += shot_name_increment

    raise RuntimeError("Can not generate a unique shot name!!!")


def is_unique_shot_name(project, shot_name):
    """Check if the given shot name is unique for the given project.

    Args:
        project (Project): A stalker.Project instance.
        shot_name (str): The Shot name to check against being unique.

    Returns:
        bool: True if this is a unique shot name.
    """
    with DBSession.no_autoflush:
        unique_shot_name = not DBSession.query(
            exists().where(and_(Shot.project == project, Shot.name == shot_name))
        ).scalar()
    return unique_shot_name


def duplicate_task(task, user, keep_resources=False):
    """Duplicate the given task without children.

    Args:
        task (stalker.Task): A stalker.Task instance to duplicate.
        user (stalker.User): A stalker.User instance which will be recorded as the
            creator of the new entities.
        keep_resources (bool): Set this True if you want to keep the resources.

    Returns:
        stalker.Task: The newly created (duplicate) stalker.Task instance.
    """
    # create a new task and change its attributes
    class_ = Task
    extra_kwargs = {}
    if task.entity_type == "Asset":
        class_ = Asset
        extra_kwargs = {"code": task.code}
    elif task.entity_type == "Shot":
        class_ = Shot

        # generate a unique shot name based on task.name
        logger.debug("generating unique shot name!")
        shot_name = generate_unique_shot_name(task.project, task.name)
        extra_kwargs = {
            "name": shot_name,
            "code": shot_name,
            "cut_in": defaults.cut_in,  # use the default values for cut in and cut out
            "cut_out": defaults.cut_out,
        }
    elif task.entity_type == "Sequence":
        class_ = Sequence
        extra_kwargs = {"code": task.code}

    # all duplicated tasks are new tasks
    with DBSession.no_autoflush:
        wfd = Status.query.filter(Status.code == "WFD").first()

    utc_now = datetime.datetime.now(pytz.utc)

    kwargs = {
        "name": task.name,
        "project": task.project,
        "bid_timing": task.bid_timing,
        "bid_unit": task.bid_unit,
        "computed_end": task.computed_end,
        "computed_start": task.computed_start,
        "created_by": user,
        "description": task.description,
        "is_milestone": task.is_milestone,
        "priority": task.priority,
        "schedule_constraint": task.schedule_constraint,
        "schedule_model": task.schedule_model,
        "schedule_timing": task.schedule_timing,
        "schedule_unit": task.schedule_unit,
        "status": wfd,
        "status_list": task.status_list,
        "tags": task.tags,
        "responsible": task.responsible,
        "start": task.start,
        "end": task.end,
        "type": task.type,
        "watchers": task.watchers,
        "date_created": utc_now,
    }

    if keep_resources:
        kwargs["resources"] = task.resources

    kwargs.update(extra_kwargs)

    dup_task = class_(**kwargs)
    dup_task.generic_data = task.generic_data

    return dup_task


def walk_and_duplicate_task_hierarchy(task, user, keep_resources=False):
    """Walk through task hierarchy and create duplicates of all the tasks found.

    Args:
        task (stalker.Task): A stalker.Task instance to start the traversal from.
        user (stalker.User): A stalker.models.auth.User instance that does this action.
        keep_resources (bool): Set this True to keep the resources

    Returns:
        stalker.Task: The newly created (duplicate) stalker.Task instance.
    """
    # start from the given task
    logger.debug("duplicating task : %s" % task)
    logger.debug("task.children    : %s" % task.children)
    dup_task = duplicate_task(task, user, keep_resources=keep_resources)
    task.duplicate = dup_task
    for child in task.children:
        logger.debug("duplicating child : %s" % child)
        duplicated_child = walk_and_duplicate_task_hierarchy(
            child, user, keep_resources=keep_resources
        )
        duplicated_child.parent = dup_task
    return dup_task


def update_dependencies_in_duplicated_hierarchy(task):
    """Update the dependencies in the given task.

    Uses the task.duplicate attribute to find the duplicate

    Args:
        task (stalker.Task): The top most task of the hierarchy
    """
    try:
        duplicated_task = task.duplicate
    except AttributeError:
        # not a duplicated task
        logger.debug("task has no duplicate: %s" % task)
        return

    for dependent_task in task.depends:
        if hasattr(dependent_task, "duplicate"):
            logger.debug("there is a duplicate!")
            logger.debug("dependent_task.duplicate : %s" % dependent_task.duplicate)
            duplicated_task.depends.append(dependent_task.duplicate)
        else:
            logger.debug("there is no duplicate!")
            duplicated_task.depends.append(dependent_task)

    for child in task.children:
        # check child dependencies
        # loop through children
        update_dependencies_in_duplicated_hierarchy(child)


def cleanup_duplicate_residuals(task):
    """Clean the duplicate attributes in the hierarchy.

    Args:
        task (stalker.Task): The top task in the hierarchy
    """
    try:
        delattr(task, "duplicate")
    except AttributeError:
        pass

    for child in task.children:
        cleanup_duplicate_residuals(child)


def duplicate_task_hierarchy(
    task, parent, name, description, user, keep_resources=False, number_of_copies=1
):
    """Duplicate the given task hierarchy.

    Walks through the hierarchy of the given task and duplicates every
    instance it finds in a new task.

    Args:
        task (stalker.Task): The task that wanted to be duplicated.
        parent (stalker.Task): The parent task to move the newly created tasks under.
        name (str): The new task name.
        description (str): The new task description
        user (stalker.User): The new task resource
        keep_resources (bool): If True, the task resources will be kept on newly
            created tasks. Default is False.
        number_of_copies (int): The number of copies, default is 1.

    Returns:
        list: A list of stalker.models.task.Task instances.
    """
    if not name:
        name = task.name

    dup_tasks = []
    for _ in range(number_of_copies):
        if isinstance(task, Shot):
            # generate a new unique name
            if not is_unique_shot_name(task.project, name):
                name = generate_unique_shot_name(task.project, name)

        dup_task = walk_and_duplicate_task_hierarchy(
            task, user, keep_resources=keep_resources
        )
        update_dependencies_in_duplicated_hierarchy(task)

        cleanup_duplicate_residuals(task)
        # update the parent
        if parent is None and task.parent is not None:
            parent = task.parent

        dup_task.parent = parent
        # just rename the dup_task

        # check if this is a Shot before setting the name
        if isinstance(task, Shot):
            # set the other data
            dup_task.sequences = task.sequences
            dup_task.cut_in = task.cut_in
            dup_task.cut_out = task.cut_out

        dup_task.name = name
        dup_task.code = name
        dup_task.description = description

        dup_tasks.append(dup_task)
        DBSession.add(dup_task)
        DBSession.commit()

    return dup_tasks


def fix_task_statuses(task):
    """Fix task statuses.

    Args:
        task (stalker.Task): A stalker.Task instance.
    """
    if task:
        task.update_status_with_dependent_statuses()
        task.update_status_with_children_statuses()
        task.update_schedule_info()

        check_task_status_by_schedule_model(task)
        fix_task_computed_time(task)


def check_task_status_by_schedule_model(task):
    """Check task status by schedule model.

    Run this after scheduling project checks the task statuses.

    Args:
        task (stalker.Task): A stalker.Task instance.
    """
    logger.debug("check_task_status_by_schedule_model starts")

    utc_now = datetime.datetime.now(pytz.utc)

    status_cmpl = Status.query.filter(Status.code == "CMPL").first()
    status_wip = Status.query.filter(Status.code == "WIP").first()

    if task.is_leaf and task.schedule_model == "duration":
        depends_tasks_cmpl = True
        for dependent_task in task.depends:
            if dependent_task.status is not status_cmpl:
                depends_tasks_cmpl = False
                break

        if depends_tasks_cmpl:
            task.status = status_cmpl

            if task.computed_start is None:
                task.computed_start = task.start

            if task.computed_end is None:
                task.computed_end = task.end

            if task.computed_end < utc_now:
                task.status = status_cmpl
            elif task.computed_start < utc_now < task.computed_end:
                task.status = status_wip


def get_actual_start_time(task):
    """Return the start time of the earliest time logs of the given task.

    If the task doesn't have any time logs this function will return the task
    start_time.

    Args:
        task (stalker.Task): The stalker task instance that the time log will be
            investigated.

    Raises:
        TypeError: If the given task is not a stalker.Task instance.

    Returns:
        datetime.datetime: The actual start time based on the TimeLogs.
    """
    if not isinstance(task, Task):
        raise TypeError(
            "task should be an instance of stalker.models.task.Task, not %s"
            % task.__class__.__name__
        )

    first_time_log = (
        TimeLog.query.filter(TimeLog.task == task).order_by(TimeLog.start.asc()).first()
    )

    if first_time_log:
        return first_time_log.start
    else:
        if task.schedule_model == "duration":
            start_time = task.project.start
            for tdep in task.depends:
                if tdep.computed_end > start_time:
                    start_time = tdep.computed_end
            return start_time

    return task.computed_start


def get_actual_end_time(task):
    """Return the end time of the latest time logs of the given task.

    If the task doesn't have any time logs this function will return the task end_time.

    Args:
        task (stalker.Task): The stalker Task instance that the time log will be
            investigated.

    Raises:
        TypeError: If the given task is not a stalker.Task instance.

    Returns:
        datetime.datetime: The actual end time based on the TimeLogs.
    """
    if not isinstance(task, Task):
        raise TypeError(
            "task should be an instance of stalker.models.task.Task, not %s"
            % task.__class__.__name__
        )

    end_time_log = (
        TimeLog.query.filter(TimeLog.task == task).order_by(TimeLog.end.desc()).first()
    )

    if end_time_log:
        return end_time_log.end
    else:
        if task.schedule_model == "duration":
            end_time = task.project.start
            for tdep in task.depends:
                if tdep.computed_end > end_time:
                    duration = datetime.timedelta(minutes=0)
                    if task.schedule_unit == "min":
                        duration = datetime.timedelta(minutes=task.schedule_timing)
                    elif task.schedule_unit == "h":
                        duration = datetime.timedelta(hours=task.schedule_timing)
                    elif task.schedule_unit == "d":
                        duration = datetime.timedelta(days=task.schedule_timing)
                    elif task.schedule_unit == "w":
                        duration = datetime.timedelta(weeks=task.schedule_timing)
                    elif task.schedule_unit == "m":
                        duration = datetime.timedelta(weeks=4 * task.schedule_timing)
                    end_time = tdep.computed_end + duration
            return end_time

    return task.computed_end


def fix_task_computed_time(task):
    """Fix task's computed_start and computed_end time based on timelogs of the task.

    Args:
        task (stalker.Task): The stalker.Task instance that the time log will be
            investigated.
    """
    if task.status.code not in ["CMPL", "STOP", "OH"]:
        return

    else:
        start_time = get_actual_start_time(task)
        end_time = get_actual_end_time(task)

        task.computed_start = start_time
        task.computed_end = end_time

        logger.debug("Task computed time is fixed!")


def smooth_array(data, iteration=1):
    """Smooths the given list of data.

    Derived from Maya MEL script: modifySelectedCurves.mel

    Args:
        data (list): A list of objects that can be multiplied of added to each other
            like simple numbers to Vectors.
        iteration (int): Number of iterations. Defaults to 1.

    Returns:
        list: The smoothed result.
    """
    # keep te first and last position
    for _ in range(iteration):
        prev = data[0]
        current = data[1]
        for i in range(1, len(data) - 1):
            next = data[i + 1]
            new_pos = current * 0.4 + (next + prev) * 0.3

            data[i] = new_pos

            prev = current
            current = next

    return data


def authenticate(login, password):
    """Authenticate the given login and password information.

    If the ``defaults.enable_ldap_authentication`` is False, the system will
    only use Stalker to authenticate.

    ``defaults.enable_ldap_authentication`` is True then the system will use
    the given LDAP server for authentication and then will create or update the
    data in Stalker DB.

    Args:
        login (str): The login.
        password (str): The plain password.

    Returns:
        bool: True/False based on the success of the operation.
    """
    if not defaults.enable_ldap_authentication:
        # No LDAP authentication
        # try authenticating with stalker
        success = stalker_authenticate(login, password)
    else:
        # defaults.enable_ldap_authentication is True
        # so always authenticate with LDAP
        success = ldap_authenticate(login, password)

        # if success:
        #     # update Stalker with the given information
        #     # by either creating a new user or updating the user password
        #     pass

    if success:
        # create the local session
        user = User.query.filter(or_(User.login == login, User.email == login)).first()

        session = LocalSession()
        session.store_user(user)
        session.save()

        # also store a AuthenticationLog in the database
        al = AuthenticationLog(
            user=user, date=datetime.datetime.now(pytz.utc), action=LOGIN
        )

        DBSession.add(al)
        DBSession.commit()

    return success


def stalker_authenticate(login, password):
    """Authenticate with data from Stalker.

    Args:
        login (str): The user login name.
        password (str): The raw password.

    Returns:
        bool: True/False depending on the success of the operation.
    """
    # check the given user password
    from stalker import User

    # check with the login or email attribute
    from sqlalchemy import or_

    user = User.query.filter(or_(User.login == login, User.email == login)).first()

    success = False
    if user:
        success = user.check_password(password)

    return success


def ldap_authenticate(login, password, ldap_server_address=None, ldap_base_dn=None):
    """Authenticate with data from Stalker and creates a proper local session.

    Args:
        login (str): The login name.
        password (str): The password.
        ldap_server_address (str): The LDAP server address.
        ldap_base_dn (str): The LDAP base domain.

    Returns:
        bool: True/False based on the success of the operation.
    """
    # check the LDAP server for login information
    success = False
    from anima import defaults

    if not ldap_server_address:
        ldap_server_address = defaults.ldap_server_address

    if not ldap_base_dn:
        ldap_base_dn = defaults.ldap_base_dn

    from ldap3 import Server, Connection

    if ldap_server_address and ldap_base_dn:
        ldap_server = Server(ldap_server_address)
        ldap_connection = Connection(server=ldap_server, user=login, password=password)
        success = ldap_connection.bind()
        logger.debug("ldap_connection.bind(): %s" % success)
        logger.debug(
            "ldap_connection.extend.standard.who_am_i(): %s"
            % ldap_connection.extend.standard.who_am_i()
        )

        if success:
            result = ldap_connection.extend.standard.who_am_i()

            if result:
                create_user_with_ldap_info(
                    ldap_connection, ldap_base_dn, login, password
                )

        ldap_connection.unbind()

    return success


def create_user_with_ldap_info(ldap_connection, ldap_base_dn, login, password):
    """Create/Update the user in Stalker with data coming from LDAP server.

    If the user exists in the Stalker DB it updates the password and group information
    of the user.

    Args:
        ldap_connection (ldap3.Connection): The LDAP connection.
        ldap_base_dn (str): Domain name.
        login (str): The login.
        password (str): The clear text password.

    Returns:
        stalker.User: The stalker.User that has been created or updated.
    """
    # so there is a user in the LDAP server
    # also create it here in StalkerDB
    # get user details like name, login, email, password
    name = get_user_name_from_ldap(ldap_connection, ldap_base_dn, login)
    # login = login
    # generate a dummy email for now
    # TODO: Get a proper email address from the LDAP server
    email = "%s@%s" % (
        login,
        ".".join([DC.split("=")[1] for DC in ldap_base_dn.split(",")]),
    )
    # password = password
    from stalker import User, Group
    from stalker.db.session import DBSession

    # the user may exist in Stalker DB
    # In this case just update the password
    new_user = User.query.filter(User.login == login).first()
    if new_user:  # Just update the password
        new_user.password = password
    else:  # The user doesn't exist in the database create a new one
        new_user = User(name=name, login=login, email=email, password=password)

    DBSession.add(new_user)
    DBSession.commit()

    # get user group names from the server
    ldap_group_names = get_user_groups_from_ldap(ldap_connection, ldap_base_dn, login)

    # get a mapped group_names of local Stalker groups
    from anima import defaults

    updated_group_info = False
    for lda_group_name in ldap_group_names:
        stalker_group_name = defaults.ldap_user_group_map.get(lda_group_name)
        if stalker_group_name:
            stalker_group = Group.query.filter(Group.name == stalker_group_name).first()
            if stalker_group:
                new_user.groups.append(stalker_group)
                updated_group_info = True

    if updated_group_info:
        DBSession.commit()

    return new_user


def get_user_attributes_from_ldap(ldap_connection, ldap_base_dn, login, attribute):
    """Return the user group names.

    No permissions for now

    Args:
        ldap_connection (ldap3.Connection): The ldap_client as ldap3.Connection instance
        ldap_base_dn (str): The domain name in LDAP format (all this CN, DN stuff)
        login (str): The login
        attribute (str): The attribute to query

    Returns:
        list: A list of user attributes.
    """
    result = []
    if ldap_connection:
        ldap_filter = "(sAMAccountName=%s)" % login

        result = ldap_connection.search(
            ldap_base_dn,
            ldap_filter,
            attributes=attribute,
        )
        if result:
            data = ldap_connection.response
            return data[0]["attributes"][attribute]

    return None


def get_user_name_from_ldap(ldap_connection, ldap_base_dn, login):
    """Return the real user name from LDAP server.

    Args:
        ldap_connection (ldap3.Connection): The ldap_connection as ldap3.Connection
            instance.
        ldap_base_dn (str): The domain name in LDAP format (all this CN, DN stuff)
        login (str): the login to query the name of.

    Returns:
        str: The user name.
    """
    return get_user_attributes_from_ldap(
        ldap_connection, ldap_base_dn, login, "displayName"
    )[0]


def get_user_groups_from_ldap(ldap_connection, ldap_base_dn, login):
    """Return the user group names.

    No permissions for now.

    Args:
        ldap_connection (ldap3.Connection): The ldap_connection as ldap3.Connection
            instance.
        ldap_base_dn (str): The domain name in LDAP format (all this CN, DN stuff).
        login (str): the login to query the name of.

    Returns:
        list: List of group names.
    """
    data = get_user_attributes_from_ldap(
        ldap_connection, ldap_base_dn, login, "memberOf"
    )
    return [d.split(",")[0].split("=")[1] for d in data]


def milliseconds_to_tc(milliseconds):
    """Convert the given milliseconds to FFMpeg compatible timecode.

    Args:
        milliseconds (int, flot): The milliseconds value.

    Returns:
        str: The FFMpeg compatible timecode.
    """
    hours = int(milliseconds / 3600000)
    residual_minutes = milliseconds - hours * 3600000
    minutes = int(residual_minutes / 60000)
    residual_seconds = residual_minutes - minutes * 60000
    seconds = int(residual_seconds / 1000)
    residual_milliseoncds = residual_seconds - seconds * 1000
    milliseconds = int(residual_milliseoncds)

    return "%02i:%02i:%02i.%03i" % (hours, minutes, seconds, milliseconds)


def upload_thumbnail(task, thumbnail_full_path):
    """Upload the given thumbnail for the given entity.

    Args:
        task: An instance of stalker.models.entity.SimpleEntity or a derivative.
        thumbnail_full_path (str): A string which is showing the path of the thumbnail
            image.

    Returns:
        bool: That shows the result.
    """
    extension = os.path.splitext(thumbnail_full_path)[-1]

    # move the file to the task thumbnail folder
    # and mimic StalkerPyramids output format
    thumbnail_original_file_name = "thumbnail%s" % extension
    thumbnail_final_full_path = os.path.join(
        task.absolute_path, "Thumbnail", thumbnail_original_file_name
    )

    try:
        os.makedirs(os.path.dirname(thumbnail_final_full_path))
    except OSError:
        pass

    # # convert the thumbnail to jpg if it is a format that is not supported by
    # # browsers
    # ext_not_supported_by_browsers = ['.bmp', '.tga', '.tif', '.tiff', '.exr']
    # if extension in ext_not_supported_by_browsers:
    #     # use MediaManager to convert them
    #     from anima.utils import MediaManager
    #     mm = MediaManager()
    #     thumbnail_full_path = mm.generate_image_thumbnail(thumbnail_full_path)
    try:
        shutil.copy(thumbnail_full_path, thumbnail_final_full_path)
    except shutil.SameFileError:
        pass

    thumbnail_os_independent_path = Repository.to_os_independent_path(
        thumbnail_final_full_path
    )
    l_thumb = Link.query.filter(Link.full_path == thumbnail_os_independent_path).first()

    if not l_thumb:
        l_thumb = Link(
            full_path=thumbnail_os_independent_path,
            original_filename=thumbnail_original_file_name,
        )

    task.thumbnail = l_thumb

    # get a version of this Task

    v = Version.query.filter(Version.task == task).first()
    if v:
        for naming_parent in v.naming_parents:
            if not naming_parent.thumbnail:
                naming_parent.thumbnail = l_thumb
                DBSession.add(naming_parent)

    DBSession.add(l_thumb)
    DBSession.commit()

    return True


def text_splitter(input_text, max_line_length=32):
    """Split the text from white spaces.

    Splits will be joined word by word but in groups of max_characters length.

    Args:
        input_text (str): The text
        max_line_length (int): The max line length. Default 32.

    Returns:
        str: The splitted and joined text.
    """
    lines = []
    words = input_text.split(" ")
    temp_line = ""
    while words:
        word = words.pop(0)
        current_line_length = len(temp_line)
        if current_line_length + len(word) <= max_line_length:
            temp_line = "%s %s" % (temp_line, word)
        else:
            lines.append(temp_line)
            temp_line = word
    else:
        lines.append(temp_line)

    return lines


def to_unit(seconds, unit, model):
    """Convert the ``seconds`` value to the given ``unit``.

    Depending on to the ``schedule_model`` the value will differ. So if the
    ``schedule_model`` is 'effort' or 'length' then the ``seconds`` and
    ``schedule_unit`` values are interpreted as work time, if the
    ``schedule_model`` is 'duration' then the ``seconds`` and
    ``schedule_unit`` values are considered as calendar time.

    Args:
        seconds (int): The seconds to convert
        unit (str): The unit value, one of 'min', 'h', 'd', 'w', 'm', 'y'
        model (str): The schedule model, one of 'effort', 'length' or 'duration'

    Returns:
        None, float: The resultant value of the converted unit.

    # TODO: This is temporarily ported from Stalker 0.2.27
    """
    if not unit:
        return None

    lut = {"min": 60, "h": 3600, "d": 86400, "w": 604800, "m": 2419200, "y": 31536000}

    if model in ["effort", "length"]:
        from stalker import defaults

        day_wt = defaults.daily_working_hours * 3600
        week_wt = defaults.weekly_working_days * day_wt
        month_wt = 4 * week_wt
        year_wt = int(defaults.yearly_working_days) * day_wt

        lut = {
            "min": 60,
            "h": 3600,
            "d": day_wt,
            "w": week_wt,
            "m": month_wt,
            "y": year_wt,
        }

    return seconds / lut[unit]


def convert_to_partial_task(task=None):
    """Convert the given task to a partial representation.

    Args:
        task (stalker.Task): A stalker.Task instance.

    Returns:
        sqlalchemy.engine.row.Row: This can be used like a dictionary.
    """
    inner_tasks = aliased(Task)
    subquery = DBSession.query(Task.id).filter(Task.id == inner_tasks.parent_id)
    return (
        DBSession.query(
            Task.id,
            Task.name,
            Task.entity_type,
            Task.status_id,
            subquery.exists().label("has_children"),
            array_agg(User.name).label("resources"),
        )
        .outerjoin(Task_Resources, Task.__table__.c.id == Task_Resources.c.task_id)
        .outerjoin(User, Task_Resources.c.resource_id == User.id)
        .group_by(
            Task.id,
            Task.name,
            Task.entity_type,
            Task.status_id,
            subquery.exists().label("has_children"),
        )
        .filter(Task.id == task.id)
        .first()
    )


def convert_to_partial_project(project=None):
    """Convert the given project to a partial representation.

    Args:
        project (stalker.Project): A stalker.Project instance.

    Returns:
        sqlalchemy.engine.row.Row: This can be used like a dictionary.
    """
    inner_tasks = aliased(Task.__table__)
    subquery = DBSession.query(inner_tasks.c.id).filter(
        inner_tasks.c.project_id == Project.id
    )
    return DBSession.query(
        Project.id,
        Project.name,
        Project.entity_type,
        Project.status_id,
        subquery.exists().label("has_children"),
    ).filter(Project.id==project.id).first()


def partial_task_query(parent_task=None):
    """Do a partial Task query.

    Using this query is super fast compared to using real stalker Task, Asset, Shot,
    Sequence, Project instances and it is generally enough to use the output of this
    function for UI purposes.

    Args:
        parent_task (stalker.Task): This can be another result proxy object.

    Returns:
        list[sqlalchemy.engine.row.Row]: Returns a list of sqlalchemy.engine.row.Row
            instances which can be used like dictionaries.
    """
    inner_tasks = aliased(Task)
    subquery = DBSession.query(Task.id).filter(Task.id == inner_tasks.parent_id)
    query = (
        DBSession.query(
            Task.id,
            Task.name,
            Task.entity_type,
            Task.status_id,
            subquery.exists().label("has_children"),
            array_agg(User.name).label("resources"),
        )
        .outerjoin(Task_Resources, Task.__table__.c.id == Task_Resources.c.task_id)
        .outerjoin(User, Task_Resources.c.resource_id == User.id)
        .group_by(
            Task.id,
            Task.name,
            Task.entity_type,
            Task.status_id,
            subquery.exists().label("has_children"),
        )
    )
    if parent_task.entity_type != "Project":
        # query child tasks
        query = query.filter(Task.parent_id == parent_task.id)
    else:
        # query only root tasks
        query = query.filter(Task.project_id == parent_task.id).filter(
            Task.parent_id == None  # noqa: E711
        )
    return query.order_by(Task.name).all()


def partial_project_query():
    """Return all the projects in the database.

    Returns:
        list[sqlalchemy.engine.row.Row]: Returns a list of sqlalchemy.engine.row.Row
            instances which can be used like dictionaries.
    """
    inner_tasks = aliased(Task.__table__)
    subquery = DBSession.query(inner_tasks.c.id).filter(
        inner_tasks.c.project_id == Project.id
    )
    query = DBSession.query(
        Project.id,
        Project.name,
        Project.entity_type,
        Project.status_id,
        subquery.exists().label("has_children"),
    )
    query = query.order_by(Project.name)
    return query.all()


def get_task_hierarchy_name(task):
    """Generate the task hierarchy name that includes the full path.

    Args:
        task (stalker.Task): A stalker.Task instance.

    Returns:
        str: Task hierarchy name.
    """
    if task.parents:
        path = "%s | %s" % (
            task.project.code,
            " | ".join(map(lambda x: x.name, task.parents)),
        )
    else:
        path = task.project.code

    return "%s (%s) (%s)" % (task.name, path, task.id)


def get_unique_take_names(task_id, include_reprs=False):
    """Return the unique take names for the given task.

    Args:
        task_id (int): The task id.
        include_reprs (bool): Including representations (takes with "@" in their name).
            By default this is False.

    Returns:
        list: A list of strings of unique take names.
    """
    query = (
        DBSession.query(Version.take_name)
        .filter(Version.task_id == task_id)
    )
    if not include_reprs:
        from anima.representation import Representation
        query = query.filter(~Version.take_name.contains(Representation.repr_separator))

    return [t[0] for t in query.distinct().order_by(Version.take_name).all()]


def get_project_from_path(path):
    """Find project from path.

    Given a path this helper function will try to find the project from the given path.

    Args:
        path (str): A path.

    Returns:
        Union[Project, None]: If found, the stalker.Project instance, or None.
    """
    from stalker import Repository
    path = Repository.to_os_independent_path(path)
    project_code = path.split("/")[1]
    # This is only true for the default configuration
    # but this is 99.99% of the times okay
    from stalker import Project
    return Project.query.filter(Project.code == project_code).first()
