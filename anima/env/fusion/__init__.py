# -*- coding: utf-8 -*-
# Copyright (c) 2012-2015, Anima Istanbul
#
# This module is part of anima-tools and is released under the BSD 2
# License: http://www.opensource.org/licenses/BSD-2-Clause

import os
import PeyeonScript
import uuid

from anima import logger
from anima.env import empty_reference_resolution
from anima.env.base import EnvironmentBase
from anima.recent import RecentFileManager


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

    def __init__(self, name='', version=None, extensions=None):
        """fusion specific init
        """
        super(Fusion, self).__init__(name=name, version=version,
                                     extensions=extensions)
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

        rfm = RecentFileManager()
        rfm.add(self.name, version.absolute_full_path)

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

    def open(self, version, force=False, representation=None,
             reference_depth=0, skip_update_check=False):
        """the open action for nuke environment
        """
        version_full_path = os.path.normpath(version.absolute_full_path)

        # delete all the comps and open new one
        #comps = self.fusion.GetCompList().values()
        #for comp_ in comps:
        #    comp_.Close()

        self.fusion.LoadComp(version_full_path.encode())

        rfm = RecentFileManager()
        rfm.add(self.name, version.absolute_full_path)

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
        return empty_reference_resolution()

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
        # full_path = self.fusion_prefs["LastCompFile"]
        # return self.get_version_from_full_path(full_path)

        version = None
        rfm = RecentFileManager()

        try:
            recent_files = rfm[self.name]
        except KeyError:
            logger.debug('no recent files')
            recent_files = None

        if recent_files is not None:
            for i in range(len(recent_files)):
                version = self.get_version_from_full_path(recent_files[i])
                if version is not None:
                    break

            logger.debug("version from recent files is: %s" % version)

        return version

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
        """Returns the main saver nodes in the scene or an empty list.
        :return: list
        """
        # list all the saver nodes in the current file
        all_saver_nodes = self.comp.GetToolList(False, 'Saver').values()

        saver_nodes = []
        for saver_node in all_saver_nodes:
            if saver_node.GetAttrs('TOOLS_Name').startswith(
               self._main_output_node_name):
                saver_nodes.append(saver_node)

        return saver_nodes

    def create_node_tree(self, node_tree):
        """Creates a node tree from the given node tree.

        The node_tree is a Python dictionary showing node types and attribute
        values. Also it can be a list of dictionaries to create more complex
        trees.

        Each node_tree can create only one shading network. The format of the
        dictionary should be as follows.

        node_tree: {
            'type': <- The fusion node type of the toppest shader
            'attr': {
                <- A dictionary that contains attribute names and values.
                'Input': {
                    'type': --- type name of the connected node
                    'attr': {
                        <- attribute values ->
                    }
                }
            },
        }

        :param [dict, list] node_tree: A dictionary showing the node tree
          attributes.

        :return:
        """
        # allow it to accept both a list or dict
        if isinstance(node_tree, list):
            created_root_nodes = []
            for item in node_tree:
                created_root_nodes.append(
                    self.create_node_tree(item)
                )
            return created_root_nodes

        node_type = node_tree['type']

        self.comp.Lock()
        node = self.comp.AddTool(node_type)
        self.comp.Unlock()

        # attributes
        if 'attr' in node_tree:
            attributes = node_tree['attr']
            for key in attributes:
                value = attributes[key]
                if isinstance(value, dict):
                    new_node = self.create_node_tree(value)
                    node.Input = new_node
                else:
                    node.SetAttrs({key: value})

        # input lists
        if 'input_list' in node_tree:
            input_list = node_tree['input_list']
            for key in input_list:
                node_input_list = node.GetInputList()
                for input_entry_key in node_input_list.keys():
                    input_entry = node_input_list[input_entry_key]
                    input_id = input_entry.GetAttrs()['INPS_ID']
                    if input_id == key:
                        value = input_list[key]
                        input_entry[0] = value
                        break

        # ref_id
        if 'ref_id' in node_tree:
            node.SetData('ref_id', node_tree['ref_id'])

        # connected to
        if 'connected_to' in node_tree:
            connected_to = node_tree['connected_to']
            if 'Input' in connected_to:
                input_node = self.create_node_tree(connected_to['Input'])
                node.Input = input_node
            elif 'ref_id' in node_tree['connected_to']:
                ref_id = node_tree['connected_to']['ref_id']
                print('ref_id: %s' % ref_id)
                # find a node with ref_id equals to ref_id that is given in the
                # node tree
                all_nodes = self.comp.GetToolList().values()
                for r_node in all_nodes:
                    node_ref_id = r_node.GetData('ref_id')
                    print('node_ref_id: %s' % node_ref_id)
                    if node_ref_id == ref_id:
                        node.Input = r_node
                        break

        return node

    def create_main_saver_node(self, version):
        """Creates the default saver node if there is no created before.

        Creates the default saver nodes if there isn't any existing outputs,
        and updates the ones that is already created
        """

        def output_path_generator(file_format):
            """helper function to generate the output path

            :param file_format:
            :return:
            """
            # generate the data needed
            # the output path
            file_name_buffer = []
            template_kwargs = {}

            # if this is a shot related task set it to shots resolution
            version_sig_name = self.get_significant_name(version)

            file_name_buffer.append(
                '%(version_sig_name)s.001.%(format)s'
            )
            template_kwargs.update({
                'version_sig_name': version_sig_name,
                'format': file_format
            })

            output_file_name = ''.join(file_name_buffer) % template_kwargs

            # check if it is a stereo comp
            # if it is enable separate view rendering
            output_file_full_path = os.path.join(
                version.absolute_path,
                'Outputs',
                version.take_name,
                'v%03d' % version.version_number,
                file_format,
                output_file_name
            ).replace('\\', '/')

            # set the output path
            return '%s' % os.path.normpath(
                output_file_full_path
            ).encode()

        def output_node_name_generator(file_format):
            return '%s_%s' % (self._main_output_node_name, file_format)

        random_ref_id = uuid.uuid4().hex

        output_format_data = [
            {
                'name': 'png',
                'node_tree': {
                    'type': 'Saver',
                    'attr': {
                        'TOOLS_Name': output_node_name_generator('png'),
                    },
                    'input_list': {
                        'Clip': output_path_generator('png'),
                        'ProcessRed': 1,
                        'ProcessGreen': 1,
                        'ProcessBlue': 1,
                        'ProcessAlpha': 0,
                        'OutputFormat': 'PNGFormat',
                        'PNGFormat.SaveAlpha': 0,
                        'PNGFormat.Depth': 1,
                        'PNGFormat.CompressionLevel': 9,
                        'PNGFormat.GammaMode': 0,
                    },
                    'connected_to': {
                        'Input': {
                            'type': 'ColorCurves',
                            'ref_id': random_ref_id,
                            'input_list': {
                                'EditAlpha': 0.0,
                            },
                            'connected_to': {
                                'Input': {
                                    'type': 'CineonLog',
                                    'input_list': {
                                        'Mode': 1,
                                        'RedBlackLevel': 0.0,
                                        'RedWhiteLevel': 1023.0,
                                        'RedFilmStockGamma': 1.0
                                    },
                                    'connected_to': {
                                        'Input': {
                                            'type': 'TimeSpeed',
                                            'attr': {
                                                'TOOLB_PassThrough': True,
                                            },
                                            'input_list': {
                                                'Speed': 12.0/25.0,
                                                'InterpolateBetweenFrames': 0
                                            },
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            },
            {
                'name': 'exr',
                'node_tree': {
                    'type': 'Saver',
                    'attr': {
                        'TOOLS_Name': output_node_name_generator('exr'),
                    },
                    'input_list': {
                        'Clip': output_path_generator('exr'),
                        'ProcessRed': 1,
                        'ProcessGreen': 1,
                        'ProcessBlue': 1,
                        'ProcessAlpha': 0,
                        'OutputFormat': 'OpenEXRFormat',
                        'OpenEXRFormat.Depth': 1,  # 16-bit float
                        'OpenEXRFormat.RedEnable': 1,
                        'OpenEXRFormat.GreenEnable': 1,
                        'OpenEXRFormat.BlueEnable': 1,
                        'OpenEXRFormat.AlphaEnable': 0,
                        'OpenEXRFormat.ZEnable': 0,
                        'OpenEXRFormat.CovEnable': 0,
                        'OpenEXRFormat.ObjIDEnable': 0,
                        'OpenEXRFormat.MatIDEnable': 0,
                        'OpenEXRFormat.UEnable': 0,
                        'OpenEXRFormat.VEnable': 0,
                        'OpenEXRFormat.XNormEnable': 0,
                        'OpenEXRFormat.YNormEnable': 0,
                        'OpenEXRFormat.ZNormEnable': 0,
                        'OpenEXRFormat.XVelEnable': 0,
                        'OpenEXRFormat.YVelEnable': 0,
                        'OpenEXRFormat.XRevVelEnable': 0,
                        'OpenEXRFormat.YRevVelEnable': 0,
                        'OpenEXRFormat.XPosEnable': 0,
                        'OpenEXRFormat.YPosEnable': 0,
                        'OpenEXRFormat.ZPosEnable': 0,
                        'OpenEXRFormat.XDispEnable': 0,
                        'OpenEXRFormat.YDispEnable': 0,
                    },
                    'connected_to': {
                        'ref_id': random_ref_id
                    }
                }
            }
        ]

        # selectively generate output format
        saver_nodes = self.get_main_saver_node()

        for data in output_format_data:
            format_name = data['name']
            node_tree = data['node_tree']

            # now check if a node with the same name exists
            format_node = None
            format_node_name = output_node_name_generator(format_name)
            for node in saver_nodes:
                node_name = node.GetAttrs('TOOLS_Name')
                if node_name.startswith(format_node_name):
                    format_node = node
                    break

            # create the saver node for this format if missing
            if not format_node:
                self.create_node_tree(node_tree)
            else:
                # just update the input_lists
                if 'input_list' in node_tree:
                    input_list = node_tree['input_list']
                    for key in input_list:
                        node_input_list = format_node.GetInputList()
                        for input_entry_key in node_input_list.keys():
                            input_entry = node_input_list[input_entry_key]
                            input_id = input_entry.GetAttrs()['INPS_ID']
                            if input_id == key:
                                value = input_list[key]
                                input_entry[0] = value
                                break

            try:
                os.makedirs(
                    os.path.dirname(
                        output_path_generator(format_name)
                    )
                )
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
            project_dir = maps.get('Project:', None)

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
