# -*- coding: utf-8 -*-
# Copyright (c) 2012-2017, Anima Istanbul
#
# This module is part of anima-tools and is released under the BSD 2
# License: http://www.opensource.org/licenses/BSD-2-Clause
import MaxPlus
from anima.env.base import EnvironmentBase


def get_max_version():
    """Encapsulates the very cumbersome 3ds Max version string retrieval
    process and returns a simple string that contains the current MAX
    version.

    :return:
    """
    versions_LUT = {
        17000: '2015',
        18000: '2016',
        19000: '2017'
    }

    c = MaxPlus.Core.EvalMAXScript('maxVersion()')
    l = c.GetIntList()
    return versions_LUT[l.GetItem(0)]


class Max(EnvironmentBase):
    """The 3dsmax environment class
    """

    name = "3dsMax%s" % get_max_version()

    def get_current_version(self):
        """Returns the current Stalker version from the open scene

        :return:
        """
        version = None

        # pm.env.sceneName() always uses "/"
        full_path = MaxPlus.FileManager.GetFileNameAndPath()
        # try to get it from the current open scene
        if full_path != '':
            version = self.get_version_from_full_path(full_path)

        return version

    def open(self, version, force=False, representation=None,
             reference_depth=0, skip_update_check=False):
        """Opens the given version file

        :param version: The Stalker version instance
        :param force: force open, so don't care if there are any unsaved
          changes in the current scene.
        :param representation: The desired representation for the XRef files
          (Not Implemented)
        :param reference_depth: (Not Implemented)
        :param skip_update_check: (Not Implemented)
        :return: Returns a reference resolution that shows what to update.
        """
        # set the project dir
        self.set_project(version)

        # then open the file
        MaxPlus.FileManager.Open(version.absolute_full_path, True)
        from anima.env import empty_reference_resolution
        return empty_reference_resolution()

    def save_as(self, version, run_pre_publishers=True):
        """Saves the current scene under the given version.

        :param version: The Stalker.Version instance
        :param run_pre_publishers: A bool flag that allows skipping the pre
          publishers.
        :return:
        """
        # get the current version, and store it as the parent of the new
        # version
        current_version = self.get_current_version()

        version.update_paths()
        version.extension = '.max'

        # define that this version is created with Maya
        version.created_with = self.name

        project = version.task.project

        # set the project dir
        self.set_project(version)

        # check if this is a shot related task
        is_shot_related_task = False
        shot = None
        from stalker import Shot
        for task in version.task.parents:
            if isinstance(task, Shot):
                is_shot_related_task = True
                shot = task
                break

        # set scene fps
        # even if this is not the first version set the fps
        #
        # or better try to get the parent versions and see if we can reach to
        # a v001 which will guarantee that this version is coming from a file
        # that has its fps set before.
        #
        # If we can't get a v001 file, than it means that the user created a
        # new scene and saved it as a new version for series of already
        # existing versions, (ex. save as v002 for the first time)
        #
        # Let's hope that it will not break animators scenes, where we have
        # 12 FPS set for the shot and the intended fps is 25 which we will
        # newer know.
        if is_shot_related_task:
            self.set_fps(shot.fps)

            # set render resolution
            self.set_resolution(shot.image_format.width,
                                shot.image_format.height,
                                shot.image_format.pixel_aspect)
            # set the render range if it is the first version
            if version.version_number == 1:
                self.set_frame_range(shot.cut_in, shot.cut_out)
        else:
            # set render resolution
            if version.version_number == 1:
                self.set_resolution(project.image_format.width,
                                    project.image_format.height,
                                    project.image_format.pixel_aspect)
            self.set_fps(project.fps)

        # set the render file name and version
        self.set_render_filename(version)

        # create the folders beforehand
        try:
            import os
            os.makedirs(version.absolute_path)
        except OSError:
            pass

        MaxPlus.FileManager.Save(version.absolute_full_path)

        # update the parent info
        if version != current_version:  # prevent CircularDependencyError
            version.parent = current_version

        from stalker.db.session import DBSession
        DBSession.add(version)

        # append it to the recent file list
        self.append_to_recent_files(
            version.absolute_full_path
        )

        DBSession.commit()

    @classmethod
    def set_resolution(cls, width, height, pixel_aspect=1.0):
        """Sets the render resolution of this scene

        :param int width: Width of the render in pixels.
        :param int height: Height of the render in pixels.
        :param float pixel_aspect: The pixel aspect ratio. Default is 1.0.
        :return:
        """
        rs = MaxPlus.RenderSettings
        rs.SetWidth(width)
        rs.SetHeight(height)
        rs.SetPixelAspectRatio(pixel_aspect)
        rs.UpdateDialogParameters()

    def set_render_filename(self, version):
        """sets the render file name
        """
        import os
        render_output_folder = os.path.join(
            version.absolute_path,
            'Outputs'
        ).replace("\\", "/")
        version_sig_name = self.get_significant_name(version)

        render_file_full_path = \
            '%(render_output_folder)s/masterLayer/%(version_sig_name)s_' \
            '<RenderLayer>_<RenderPass>.exr' % {
                'render_output_folder': render_output_folder,
                'version_sig_name': version_sig_name
            }

        rs = MaxPlus.RenderSettings
        # rs.SetTimeType(1)  # Active Time Segment
        rs.SetTimeType(2)  # Range

        rs.SetUseImageSequence(True)
        rs.SetSaveFile(True)
        rs.SetOutputFile(render_file_full_path)

        rs.UpdateDialogParameters()

    def set_frame_range(self, start_frame=0, end_frame=100,
                        adjust_frame_range=False):
        """sets the start and end frame range
        """
        # set the playback range
        anim = MaxPlus.Animation
        ticks_per_frame = anim.GetTicksPerFrame()
        anim.SetStartTime(start_frame * ticks_per_frame)
        anim.SetEndTime(end_frame * ticks_per_frame)

        # and set the render range
        rs = MaxPlus.RenderSettings
        rs.SetTimeType(2)  # Range
        rs.SetStart(start_frame)
        rs.SetEnd(end_frame)

    def get_fps(self):
        """returns the fps of this environment
        """
        anim = MaxPlus.Animation
        return anim.GetFrameRate()

    @classmethod
    def set_fps(cls, fps=25.0):
        """sets the fps of the environment
        """
        anim = MaxPlus.Animation
        anim.SetFrameRate(int(fps))

    def set_project(self, version):
        """Sets the project to the given Versions project.

        :param version: A :class:`~stalker.models.version.Version`.
        """
        project_dir = version.absolute_path
        pm = MaxPlus.PathManager
        pm.SetProjectFolderDir(project_dir)

        # Set all the auxiliary paths
        project_structure = {
            'Animation': 'Outputs/sceneassets/animations',
            'Archives': 'Outputs/archives',
            'Autoback': 'Outputs/autoback',
            'CFD': 'Outputs/sceneassets/CFD',
            'Download': 'Outputs/downloads',
            'Export': 'Outputs/export',
            'Expression': 'Outputs/express',
            'Image': 'Outputs/sceneassets/images',
            'Import': 'Outputs/import',
            'Matlib': 'Outputs/materiallibraries',
            'Photometric': 'Outputs/sceneassets/photometric',
            'Preview': 'Outputs/previews',
            'ProjectFolder': '',
            'Proxies': 'Outputs/proxies',
            'RenderAssets': 'Outputs/sceneassets/renderassets',
            'RenderOutput': 'Outputs/renderoutput',
            'RenderPresets': 'Outputs/renderpresets',
            'Scene': '',
            'Sound': 'Outputs/sceneassets/sounds',
            'UserStartupTemplates': 'Outputs/startuptemplates',
            'Vpost': 'Outputs/vpost',
        }
