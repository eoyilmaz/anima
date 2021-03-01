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

        if not skip_update_check:
            return self.check_referenced_versions()
        else:
            from anima.env import empty_reference_resolution
            return empty_reference_resolution

    def reference(self, version, use_namespace=True):
        """References/Links another Blend file

        :param version:
        :param use_namespace:
        :return:
        """
        if not version:
            return

        files = {
            'Collection': [],
            'Image': [],
            'Mesh': [],
            'Material': [],
            'Object': [],
            'Scene': [],
            'Texture': [],
        }
        with bpy.data.libraries.load(version.absolute_full_path) as (data_from, data_to):
            # Collection
            for name in data_from.collections:
                files['Collection'].append({'name': name})

            # # Image
            # for name in data_from.images:
            #     files['Image'].append({'name': name})

            # # Mesh
            # for name in data_from.meshes:
            #     files['Mesh'].append({'name': name})

            # # Materials
            # for name in data_from.materials:
            #     files['Material'].append({'name': name})

            # # Objects
            # for name in data_from.objects:
            #     files['Object'].append({'name': name})

            # # Scenes
            # for name in data_from.scenes:
            #     files['Scene'].append({'name': name})

            # # Textures
            # for name in data_from.textures:
            #     files['Texture'].append({'name': name})

        for key in files:
            if files[key]:
                bpy.ops.wm.link(
                    directory="%s/%s/" % (version.absolute_full_path, key),
                    files=files[key]
                )

    def get_referenced_versions(self, parent_ref=None):
        """Returns the referenced versions

        :param parent_ref:
        :return:
        """
        import os
        versions = []
        for lib_name in bpy.data.libraries.keys():
            lib = bpy.data.libraries[lib_name]
            file_path = lib.filepath
            if file_path.startswith('//'):  # This is a relative path
                curr_blend_file_dir = os.path.dirname(bpy.data.filepath)
                file_full_path = os.path.normpath("%s%s" % (curr_blend_file_dir, file_path))
            else:
                file_full_path = os.path.normpath(file_path)
            version = self.get_version_from_full_path(file_full_path)
            if version and version not in versions:
                versions.append(version)

        return versions

    def update_versions(self, reference_resolution):
        """Updates the linked libraries according to the given reference_resolution.

        :param reference_resolution:
        :return:
        """
        import os
        for lib_name in bpy.data.libraries.keys():
            lib = bpy.data.libraries[lib_name]
            file_path = lib.filepath
            if file_path.startswith('//'):  # This is a relative path
                curr_blend_file_dir = os.path.dirname(bpy.data.filepath)
                file_full_path = os.path.normpath("%s%s" % (curr_blend_file_dir, file_path))
            else:
                file_full_path = os.path.normpath(file_path)
            version = self.get_version_from_full_path(file_full_path)
            if version in reference_resolution['update']:
                if not version.is_latest_published_version():
                    latest_published_version = version.latest_published_version

                    lib.filepath = latest_published_version.absolute_full_path
                    lib.reload()

        return []  # need to return an empty list

    def deep_version_inputs_update(self):
        """updates the inputs of the references of the current scene
        """
        # just use the first level references for now
        self.update_version_inputs()

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
        version_sig_name = self.get_significant_name(
            version,
            include_project_code=False
        )
        output_filename_template = '//Outputs/renders/beauty/%(version_sig_name)s_beauty.#'
        render_file_full_path = output_filename_template % {'version_sig_name': version_sig_name}

        bpy.context.scene.render.filepath = render_file_full_path

        bpy.context.scene.render.image_settings.file_format = 'OPEN_EXR'
        bpy.context.scene.render.image_settings.color_depth = '16'
        bpy.context.scene.render.image_settings.exr_codec = 'ZIP'
        bpy.context.scene.render.image_settings.color_mode = 'RGBA'
        bpy.context.scene.render.film_transparent = True

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

    def viewport_render_animation(self, context=None):
        """creates a playblast/flipbook

        :param context: The current context that this script is running at
        """
        import os
        version = self.get_current_version()

        # store the current render settings
        render_settings = {
            'filepath': bpy.context.scene.render.filepath,
            'file_format': bpy.context.scene.render.image_settings.file_format,
            'color_depth': bpy.context.scene.render.image_settings.color_depth,
            'exr_codec': bpy.context.scene.render.image_settings.exr_codec,
            'color_mode': bpy.context.scene.render.image_settings.color_mode,
        }

        # disable viewport overlay
        if not context:
            context = bpy.context
        current_overlay_state = context.space_data.overlay.show_overlays
        context.space_data.overlay.show_overlays = False

        # set output settings
        bpy.context.scene.render.image_settings.file_format = 'FFMPEG'
        bpy.context.scene.render.image_settings.color_mode = 'RGB'
        bpy.context.scene.render.ffmpeg.format = 'MPEG4'
        bpy.context.scene.render.ffmpeg.constant_rate_factor = 'HIGH'
        bpy.context.scene.render.ffmpeg.ffmpeg_preset = 'GOOD'
        bpy.context.scene.render.ffmpeg.gopsize = 12
        bpy.context.scene.render.filepath = "//"

        # set output filename
        if version:
            version_sig_name = self.get_significant_name(version, include_project_code=False)
        else:
            if bpy.data.filepath:
                version_sig_name = os.path.splitext(os.path.basename(bpy.data.filepath))[0]
            else:
                version_sig_name = 'playblast'

        output_filename_template = '//Outputs/playblast/%(version_sig_name)s.#'
        rendered_output_filename = output_filename_template % {'version_sig_name': version_sig_name}

        bpy.context.scene.render.filepath = rendered_output_filename

        # do the playblast
        try:
            bpy.ops.render.opengl(animation=True)
        finally:
            # enable viewport overlay
            context.space_data.overlay.show_overlays = current_overlay_state

            # restore the render settings
            bpy.context.scene.render.filepath = render_settings['filepath']
            bpy.context.scene.render.image_settings.file_format = render_settings['file_format']
            bpy.context.scene.render.image_settings.color_depth = render_settings['color_depth']
            bpy.context.scene.render.image_settings.exr_codec = render_settings['exr_codec']
            bpy.context.scene.render.image_settings.color_mode = render_settings['color_mode']

            # and open the file path
            from anima.utils import open_browser_in_location
            movie_file_rel_path = rendered_output_filename.replace(
                '#', '%s-%s' % (
                    bpy.context.scene.frame_start,
                    bpy.context.scene.frame_end
                )
            )[2:]  # removes the '//' at the beginning of the file path
            playblast_full_path = os.path.join(
                os.path.dirname(bpy.data.filepath),
                movie_file_rel_path
            )
            open_browser_in_location(playblast_full_path)
