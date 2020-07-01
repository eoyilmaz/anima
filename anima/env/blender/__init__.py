# -*- coding: utf-8 -*-
# Copyright (c) 2012-2020, Erkan Ozgur Yilmaz
#
# This module is part of anima and is released under the MIT
# License: http://www.opensource.org/licenses/MIT


import bpy

from anima.env.base import EnvironmentBase


class Blender(EnvironmentBase):
    """The Blender environment wrapper
    """

    name = "Blender%s.%s" % (bpy.app.version[0:2])
    representations = ['Base']

    has_publishers = True

    extensions = ['.blend']

    def __init__(self,version=None):
        EnvironmentBase.__init__(self, self.name, version)

    def save_as(self, version, run_pre_publishers=True):
        """Save as action for Blender

        :param version:
        :param run_pre_publishers:
        :return:
        """
        version.update_paths()
        # set version extension to .blend
        version.extension = self.extensions[0]

        # store what this file is created with
        version.created_with = self.name

        project = version.task.project

        shot = self.get_shot(version)

        fps = None
        imf = None
        if shot and version.version_number == 1:
            self.set_frame_range(shot.cut_in, shot.cut_out)

        fps = shot.fps if shot else project.fps
        imf = shot.image_format if shot else project.image_format

        self.set_render_resolution(imf.width, imf.height, imf.pixel_aspect)
        self.set_fps(fps)

        self.set_render_filename(version)

        # create the folder if it doesn't exists
        try:
            import os
            os.makedirs(version.absolute_path)
        except OSError:
            # already exists
            pass

        # finally save the file
        bpy.ops.wm.save_as_mainfile(filepath=version.absolute_full_path)

        from stalker.db.session import DBSession
        DBSession.add(version)

        # append it to the recent file list
        self.append_to_recent_files(version.absolute_full_path)
        DBSession.commit()

        # create a local copy
        self.create_local_copy(version)

        # run post publishers here
        if version.is_published:
            # before doing anything run all publishers
            type_name = ''
            if version.task.type:
                type_name = version.task.type.name

            # before running use the staging area to store the current version
            from anima.publish import staging, run_publishers, POST_PUBLISHER_TYPE
            from anima.exc import PublishError
            staging['version'] = version
            try:
                run_publishers(type_name, publisher_type=POST_PUBLISHER_TYPE)
            except PublishError as e:
                # do not forget to clean up the staging area
                staging.clear()
                raise e

        return True

    def open(self, version, force=False, representation=None,
             reference_depth=0, skip_update_check=False):

        # leave it simple for now
        bpy.ops.wm.open_mainfile(filepath=version.absolute_full_path)

    def set_fps(self, fps=25.0):
        """

        :param fps:
        :return:
        """
        bpy.context.scene.render.fps = fps

    def set_frame_range(self, start_frame=1001, end_frame=1100, adjust_frame_range=False):
        """Sets the frame range
        :param int start_frame: The start frame.
        :param int  end_frame: The end frame.
        :param bool adjust_frame_range: Obsolete for now.
        :return:
        """
        bpy.context.scene.frame_start = start_frame
        bpy.context.scene.frame_end = end_frame

    def set_render_resolution(self, width, height, pixel_aspect=1.0):
        """Sets the render resolution for the current environment

        :param int width: The width of the resolution
        :param int height: The height of the resolution
        :param float pixel_aspect: The pixel aspect ratio, defaults to 1.0.
        :return:
        """
        bpy.context.scene.render.resolution_x = width
        bpy.context.scene.render.resolution_y = height
        bpy.context.scene.render.pixel_aspect_x = pixel_aspect
        bpy.context.scene.render.pixel_aspect_y = 1

    def set_render_filename(self, version):
        """Sets the render filename

        :param version: The Stalker Version instance
        :return:
        """
        import os
        version_sig_name = self.get_significant_name(
            version,
            include_project_code=False
        )
        output_filename_template = \
            '//Outputs/renders/beauty/' \
            '%(version_sig_name)s_beauty.#'

        render_file_full_path = \
            output_filename_template % {
                'version_sig_name': version_sig_name
            }

        bpy.context.scene.render.filepath = render_file_full_path

        bpy.context.scene.render.image_settings.file_format = 'OPEN_EXR'
        bpy.context.scene.render.image_settings.color_depth = '16'
        bpy.context.scene.render.image_settings.exr_codec = 'ZIP'

        bpy.context.scene.render.use_overwrite = False
        bpy.context.scene.render.use_placeholder = True

    def get_current_version(self):
        """returns the current open version
        """
        version = None
        full_path = bpy.data.filepath
        if full_path != '':
            version = self.get_version_from_full_path(full_path)
        return version
