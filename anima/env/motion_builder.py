# -*- coding: utf-8 -*-
# Copyright (c) 2012-2017, Anima Istanbul
#
# This module is part of anima-tools and is released under the BSD 2
# License: http://www.opensource.org/licenses/BSD-2-Clause


from anima.env.base import EnvironmentBase
import pyfbsdk


class MotionBuilder(EnvironmentBase):
    """
    """

    name = "MotionBuilder"
    has_publishers = False

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
        version.extension = '.fbx'

        # create the dirs first
        import os
        try:
            os.makedirs(version.absolute_path)
        except OSError:
            # already exists
            pass

        self.app.FileSave(str(version.absolute_full_path))

