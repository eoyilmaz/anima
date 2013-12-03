# -*- coding: utf-8 -*-
# Copyright (c) 2012-2013, Anima Istanbul
#
# This module is part of anima-tools and is released under the BSD 2
# License: http://www.opensource.org/licenses/BSD-2-Clause


import os
#import jinja2

import PeyeonScript
from .. import utils
from base import EnvironmentBase


class Fusion(EnvironmentBase):
    """the fusion environment class
    """

    name = "Fusion"
    extensions = ['.comp']

    fusion_formats = {
        "Multimedia": {
            "id": 0,
            "Width": 320,
            "Height": 240,
            "AspectX": 1.0,
            "AspectY": 1.0,
            "Rate": 15.0
        },
        "NTSC (D1)": {
            "id": 1,
            "Width": 720,
            "Height": 486,
            "AspectX": 0.9,
            "AspectY": 1.0,
            "Rate": 29.97
        },
        "NTSC (DV)": {
            "id": 2,
            "Width": 720,
            "Height": 480,
            "AspectX": 0.9,
            "AspectY": 1.0,
            "Rate": 29.97
        },
        "NTSC (Perception)": {
            "id": 3,
            "Width": 720,
            "Height": 480,
            "AspectX": 0.9,
            "AspectY": 1.0,
            "Rate": 29.97
        },
        "NTSC (Square Pixel)": {
            "id": 4,
            "Width": 640,
            "Height": 480,
            "AspectX": 1.0,
            "AspectY": 1.0,
            "Rate": 29.97
        },
        "NTSC 16:9": {
            "id": 5,
            "Width": 720,
            "Height": 486,
            "AspectX": 1.2,
            "AspectY": 1.0,
            "Rate": 29.97
        },
        "PAL / SECAM (D1)": {
            "id": 6,
            "Width": 720,
            "Height": 576,
            "AspectX": 1.0,
            "AspectY": 0.9375,
            "Rate": 25
        },
        "PAL / SECAM (Square Pixel)": {
            "id": 7,
            "Width": 768,
            "Height": 576,
            "AspectX": 1.0,
            "AspectY": 1.0,
            "Rate": 25
        },
        "PALplus 16:9": {
            "id": 8,
            "Width": 720,
            "Height": 576,
            "AspectX": 1.0,
            "AspectY": 0.703125,
            "Rate": 25
        },
        "HDTV 720": {
            "id": 9,
            "Width": 1280,
            "Height": 720,
            "AspectX": 1.0,
            "AspectY": 1.0,
            "Rate": 30
        },
        "HDTV 1080": {
            "id": 10,
            "Width": 1920,
            "Height": 1080,
            "AspectX": 1.0,
            "AspectY": 1.0,
            "Rate": 30
        },
        "D16": {
            "id": 11,
            "Width": 2880,
            "Height": 2304,
            "AspectX": 1.0,
            "AspectY": 1.0,
            "Rate": 24
        },
        "2K Full Aperture (Super 35)": {
            "id": 12,
            "Width": 2048,
            "Height": 1556,
            "AspectX": 1.0,
            "AspectY": 1.0,
            "Rate": 24
        },
        "4K Full Aperture (Super 35)": {
            "id": 13,
            "Width": 4096,
            "Height": 3112,
            "AspectX": 1.0,
            "AspectY": 1.0,
            "Rate": 24
        },
        "2K Academy (Regular 35)": {
            "id": 14,
            "Width": 1828,
            "Height": 1332,
            "AspectX": 1.0,
            "AspectY": 1.0,
            "Rate": 24
        },
        "4K Academy (Regular 35)": {
            "id": 15,
            "Width": 3656,
            "Height": 2664,
            "AspectX": 1.0,
            "AspectY": 1.0,
            "Rate": 24
        },
        "2K Academy in Full Aperture": {
            "id": 16,
            "Width": 2048,
            "Height": 1556,
            "AspectX": 1.0,
            "AspectY": 1.0,
            "Rate": 24
        },
        "4K Academy in Full Aperture": {
            "id": 17,
            "Width": 4096,
            "Height": 3112,
            "AspectX": 1.0,
            "AspectY": 1.0,
            "Rate": 24
        },
        "2K Anamorphic (CinemaScope)": {
            "id": 18,
            "Width": 1828,
            "Height": 1556,
            "AspectX": 2.0,
            "AspectY": 1.0,
            "Rate": 24
        },
        "4K Anamorphic (CinemaScope)": {
            "id": 19,
            "Width": 3656,
            "Height": 3112,
            "AspectX": 2.0,
            "AspectY": 1.0,
            "Rate": 24
        },
        "2K 1.85": {
            "id": 20,
            "Width": 1828,
            "Height": 988,
            "AspectX": 1.0,
            "AspectY": 1.0,
            "Rate": 24
        },
        "4K 1.85": {
            "id": 21,
            "Width": 3656,
            "Height": 1976,
            "AspectX": 1.0,
            "AspectY": 1.0,
            "Rate": 24
        },
        "3K VistaVision": {
            "id": 22,
            "Width": 3072,
            "Height": 2048,
            "AspectX": 1.0,
            "AspectY": 1.0,
            "Rate": 24
        },
        "6K VistaVision": {
            "id": 23,
            "Width": 6144,
            "Height": 4096,
            "AspectX": 1.0,
            "AspectY": 1.0,
            "Rate": 24
        },
        "5K IMAX 70mm": {
            "id": 24,
            "Width": 5464,
            "Height": 4096,
            "AspectX": 1.0,
            "AspectY": 1.0,
            "Rate": 24
        },
    }

    def __init__(self, version=None, name='', extensions=None):
        """fusion specific init
        """
        # and add you own modifications to __init__
        self.fusion = PeyeonScript.scriptapp("Fusion")
        self.fusion_prefs = self.fusion.GetPrefs()['Global']

        self.comp = self.fusion.GetCurrentComp()
        self.comp_prefs = self.comp.GetPrefs()['Comp']

        self._main_output_node_name = "Main_Output"

    def save_as(self, version):
        """"the save action for fusion environment

        uses Fusions own python binding
        """
        # set the extension to '.comp'
        from stalker import Version
        assert isinstance(version, Version)
        # its a new version please update the paths
        version.update_paths()
        version.extension = '.comp'
        version.created_with = self.name

        # set project_directory
        self.project_directory = os.path.dirname(version.absolute_path)

        # create the main write node
        self.create_main_saver_node(version)

        # replace read and write node paths
        #self.replace_external_paths()

        # create the path before saving
        try:
            os.makedirs(version.absolute_path)
        except OSError:
            # path already exists OSError
            pass

        version_full_path = os.path.normpath(version.absolute_full_path)

        self.comp.Lock()
        self.comp.Save(version_full_path.encode())
        self.comp.Unlock()

        return True

    def export_as(self, version):
        """the export action for nuke environment
        """
        # its a new version please update the paths
        version.update_paths()
        # set the extension to '.comp'
        version.extension = '.comp'
        version.created_with = self.name
        #        nuke.nodeCopy(version.fullPath)
        raise NotImplementedError(
            'export_as() is not implemented yet for Fusion'
        )

    def open_(self, version, force=False):
        """the open action for nuke environment
        """
        version_full_path = os.path.normpath(version.absolute_full_path)

        # delete all the comps and open new one
        #comps = self.fusion.GetCompList().values()
        #for comp_ in comps:
        #    comp_.Close()

        self.fusion.LoadComp(version_full_path.encode())

        # set the project_directory
        #self.project_directory = os.path.dirname(version.absolute_path)

        # TODO: file paths in different OS'es should be replaced with the current one
        # Check if the file paths are starting with a string matching one of
        # the OS'es project_directory path and replace them with a relative one
        # matching the current OS

        # replace paths
        #self.replace_external_paths()

        # return True to specify everything was ok and an empty list
        # for the versions those needs to be updated
        return True, []

    def post_open(self, version):
        """the post open action for the nuke environment
        """
        pass

    def import_(self, version):
        """the import action for nuke environment
        """
        #nuke.nodePaste(version.absolute_full_path)
        return True

    def get_current_version(self):
        """Finds the Version instance from the current open file.

        If it can't find any then returns None.

        :return: :class:`~oyProjectManager.models.version.Version`
        """
        #full_path = self._root.knob('name').value()
        full_path = os.path.normpath(
            self.comp.GetAttrs()['COMPS_FileName']
        ).replace('\\', '/')
        return self.get_version_from_full_path(full_path)

    def get_version_from_recent_files(self):
        """It will try to create a
        :class:`~oyProjectManager.models.version.Version` instance by looking
        at the recent files list.

        It will return None if it can not find one.

        :return: :class:`~oyProjectManager.models.version.Version`
        """
        full_path = self.fusion_prefs["LastCompFile"]
        return self.get_version_from_full_path(full_path)

    def get_version_from_project_dir(self):
        """Tries to find a Version from the current project directory

        :return: :class:`~oyProjectManager.models.version.Version`
        """
        versions = self.get_versions_from_path(self.project_directory)
        version = None

        if versions and len(versions):
            version = versions[0]

        return version

    def get_last_version(self):
        """gets the file name from nuke
        """
        version = self.get_current_version()

        # read the recent file list
        if version is None:
            version = self.get_version_from_recent_files()

        # get the latest possible Version instance by using the workspace path
        if version is None:
            version = self.get_version_from_project_dir()

        return version

    def get_frame_range(self):
        """returns the current frame range
        """
        #self._root = self.get_root_node()
        #startFrame = int(self._root.knob('first_frame').value())
        #endFrame = int(self._root.knob('last_frame').value())
        start_frame = self.comp.GetAttrs()['COMPN_GlobalStart']
        end_frame = self.comp.GetAttrs()['COMPN_GlobalEnd']
        return start_frame, end_frame

    def set_frame_range(self, start_frame=1, end_frame=100,
                        adjust_frame_range=False):
        """sets the start and end frame range
        """
        #self._root.knob('first_frame').setValue(start_frame)
        #self._root.knob('last_frame').setValue(end_frame)
        self.comp.SetAttrs(
            {
                "COMPN_GlobalStart": start_frame,
                "COMPN_GlobalEnd": end_frame
            }
        )

    def set_fps(self, fps=25):
        """sets the current fps
        """
        #        self._root.knob('fps').setValue(fps)
        pass

    def get_fps(self):
        """returns the current fps
        """
        #return int(self._root.knob('fps').getValue())
        return None

    def get_main_saver_node(self):
        """Returns the main saver node in the scene or None.
        """

        # list all the saver nodes in the current file
        all_saver_nodes = self.comp.GetToolList(False, 'Saver').values()

        for saver_node in all_saver_nodes:
            if saver_node.GetAttrs('TOOLS_Name').startswith(
                    self._main_output_node_name
            ):
                main_saver_node = saver_node
                return main_saver_node

        return None

    def create_main_saver_node(self, version):
        """creates the default saver node if there is no one created before.
        """
        from stalker import Version
        assert isinstance(version, Version)

        # list all the save nodes in the current file
        main_saver_node = self.get_main_saver_node()

        if main_saver_node is None:
            # create one with correct output path

            # lock the comp to prevent the file dialog
            self.comp.Lock()

            main_saver_node = self.comp.Saver

            # unlock the comp
            self.comp.Unlock()

        # set the output path
        output_file_name = ""

        task = version.task
        project = task.project
        output_file_name = '%s_%s_%s_Output_v%03d.001.exr' % (
            task.entity_type, task.id, version.take_name,
            version.version_number
        )

        # check if it is a stereo comp
        # if it is enable separate view rendering
        output_file_full_path = os.path.join(
            version.absolute_path,
            'Outputs',
            'v%03d' % version.version_number,
            'exr',
            output_file_name
        ).replace('\\', '/')

        # set the path
        main_saver_node.Clip[0] = 'Comp:' + os.path.normpath(
            utils.relpath(
                os.path.dirname(version.absolute_full_path),
                output_file_full_path,
                "/",
                ".."
            )
        ).encode()

        # set the main_saver_node name
        main_saver_node.SetAttrs({'TOOLS_Name': self._main_output_node_name})

        # create the path
        try:
            os.makedirs(os.path.dirname(output_file_full_path))
        except OSError:
            # path already exists
            pass

    @property
    def project_directory(self):
        """The project directory.

        Set it to the project root, and set all your paths relative to this
        directory.
        """

        # try to figure it out from the maps
        # search for Project path

        project_dir = None
        maps = self.comp_prefs['Paths'].get('Map', None)
        if maps:
            project_dir = maps.get('Project', None)

        #if not project_dir:
        #    # set the map for the project dir
        #    if self.version:
        #        project_dir = os.path.dirname(self.version.absolute_path)
        #        self.project_directory = project_dir

        return project_dir

    @project_directory.setter
    def project_directory(self, project_directory_in):

        project_directory_in = os.path.normpath(project_directory_in)

        # set a path map
        self.comp.SetPrefs(
            {
                'Comp.Paths.Map': {
                    'Project:': project_directory_in.encode()
                }
            }
        )
