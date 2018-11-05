# -*- coding: utf-8 -*-
# Copyright (c) 2012-2018, Anima Istanbul
#
# This module is part of anima-tools and is released under the BSD 2
# License: http://www.opensource.org/licenses/BSD-2-Clause

import pyfbsdk
from anima.env.base import EnvironmentBase


class ClipData(object):
    """Holds Story clip related data
    """

    def __init__(self, shot_name=None, fbx_path=None, movie_path=None,
                 cut_in=None, cut_out=None, fps=None):
        self.shot_name = shot_name
        self.fbx_path = fbx_path
        self.movie_path = movie_path
        self.cut_in = cut_in
        self.cut_out = cut_out
        self.fps = fps


class MotionBuilder(EnvironmentBase):
    """
    """

    name = "MotionBuilder"
    has_publishers = False
    extensions = ['.fbx']

    def __init__(self, **kwargs):
        super(MotionBuilder, self).__init__(**kwargs)
        self.app = pyfbsdk.FBApplication()

    def get_current_version(self):
        """returns the current version
        """
        full_path = self.app.FBXFileName
        version = None
        if full_path:
            version = self.get_version_from_full_path(full_path)
        return version

    def open(self, version, force=False, representation=None,
             reference_depth=0, skip_update_check=False):
        """The overridden open method

        :param version:
        :param force:
        :param representation:
        :param reference_depth:
        :param skip_update_check:
        :return:
        """
        self.app.FileOpen(
            str(version.absolute_full_path)
        )

        from anima.env import empty_reference_resolution
        return empty_reference_resolution()

    def save_as(self, version, run_pre_publishers=True):
        """The overridden save method

        :param version:
        :param run_pre_publishers:
        :return:
        """
        version.update_paths()
        version.extension = self.extensions[0]

        # create the dirs first
        import os
        try:
            os.makedirs(version.absolute_path)
        except OSError:
            # already exists
            pass

        self.app.FileSave(str(version.absolute_full_path))

    def create_story(self, clip_data=None):
        """Creates a video story video_track

        :param clip_data:
        :return:
        """
        import os

        if clip_data is None:
            clip_data = []

        # find the default Shot Track
        track_container = pyfbsdk.FBStory().RootEditFolder.Tracks
        shot_track = None
        character_track = None
        for track in track_container:
            if track.Label == "Shot Track":
                shot_track = track
            elif track.Label == "Character Track":
                character_track = track

        if not shot_track:
            # Create a Shot Track
            shot_track = pyfbsdk.FBStoryTrack(
                pyfbsdk.FBStoryTrackType.kFBStoryTrackShot
            )

        if not character_track:
            character_track = pyfbsdk.FBStoryTrack(
                pyfbsdk.FBStoryTrackType.kFBStoryTrackCharacter
            )

        # create clips
        for clip_info in clip_data:
            assert isinstance(clip_info, ClipData)
            # create a new camera
            clip_camera = pyfbsdk.FBCamera(
                'Camera_Shot_%s' % str(clip_info.shot_name)
            )

            # Create a Shot clip
            cut_in_fbtime = pyfbsdk.FBTime(0, 0, 0, clip_info.cut_in)
            cut_out_fbtime = pyfbsdk.FBTime(0, 0, 0, clip_info.cut_out)

            shot_clip = pyfbsdk.FBStoryClip(
                clip_camera,
                shot_track,
                cut_in_fbtime
            )
            shot_clip.Stop = cut_out_fbtime
            shot_clip.Offset = cut_in_fbtime

            shot_clip.SetTime(
                None,
                None,
                cut_in_fbtime,
                cut_out_fbtime,
                False
            )
            if clip_info.fps:
                shot_clip.UseSystemFrameRate = False
                shot_clip.FrameRate = clip_info.fps

            # shot_clip.ClipAnimationPath = str(clip_info.fbx_path)
            character_clip = pyfbsdk.FBStoryClip(
                str(clip_info.fbx_path),
                character_track,
                cut_in_fbtime
            )
            character_clip.Stop = cut_out_fbtime
            character_clip.Offset = cut_in_fbtime

            # set the camera back plate to the video
            back_plate = pyfbsdk.FBTexture(str(clip_info.movie_path))

            # set the back plate as the shot_clip back plate
            clip_camera.BackGroundTexture = back_plate

            # set the video offset
            back_plate.Video.TimeOffset = cut_in_fbtime
