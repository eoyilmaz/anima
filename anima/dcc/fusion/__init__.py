# -*- coding: utf-8 -*-

import sys

exceptions = None
if sys.version_info[0] >= 3:
    exceptions = (ImportError, ModuleNotFoundError)
else:
    exceptions = ImportError

try:
    # for Fusion 6 and 7
    import PeyeonScript as bmf
except exceptions:
    # for Fusion 8+
    try:
        # for Fusion inside Resolve
        import BlackmagicFusion as bmf
    except exceptions:
        from anima.dcc import blackmagic as bmd

        bmf = bmd.get_bmd()


from anima import logger
from anima.dcc import empty_reference_resolution
from anima.dcc.base import DCCBase
from anima.recent import RecentFileManager


class Fusion(DCCBase):
    """the fusion DCC class"""

    name = "Fusion"
    extensions = [".comp"]

    fusion_formats = {
        "Multimedia": {
            "id": 0,
            "Width": 320,
            "Height": 240,
            "AspectX": 1.0,
            "AspectY": 1.0,
            "Rate": 15.0,
        },
        "NTSC (D1)": {
            "id": 1,
            "Width": 720,
            "Height": 486,
            "AspectX": 0.9,
            "AspectY": 1.0,
            "Rate": 29.97,
        },
        "NTSC (DV)": {
            "id": 2,
            "Width": 720,
            "Height": 480,
            "AspectX": 0.9,
            "AspectY": 1.0,
            "Rate": 29.97,
        },
        "NTSC (Perception)": {
            "id": 3,
            "Width": 720,
            "Height": 480,
            "AspectX": 0.9,
            "AspectY": 1.0,
            "Rate": 29.97,
        },
        "NTSC (Square Pixel)": {
            "id": 4,
            "Width": 640,
            "Height": 480,
            "AspectX": 1.0,
            "AspectY": 1.0,
            "Rate": 29.97,
        },
        "NTSC 16:9": {
            "id": 5,
            "Width": 720,
            "Height": 486,
            "AspectX": 1.2,
            "AspectY": 1.0,
            "Rate": 29.97,
        },
        "PAL / SECAM (D1)": {
            "id": 6,
            "Width": 720,
            "Height": 576,
            "AspectX": 1.0,
            "AspectY": 0.9375,
            "Rate": 25,
        },
        "PAL / SECAM (Square Pixel)": {
            "id": 7,
            "Width": 768,
            "Height": 576,
            "AspectX": 1.0,
            "AspectY": 1.0,
            "Rate": 25,
        },
        "PALplus 16:9": {
            "id": 8,
            "Width": 720,
            "Height": 576,
            "AspectX": 1.0,
            "AspectY": 0.703125,
            "Rate": 25,
        },
        "HDTV 720": {
            "id": 9,
            "Width": 1280,
            "Height": 720,
            "AspectX": 1.0,
            "AspectY": 1.0,
            "Rate": 30,
        },
        "HDTV 1080": {
            "id": 10,
            "Width": 1920,
            "Height": 1080,
            "AspectX": 1.0,
            "AspectY": 1.0,
            "Rate": 30,
        },
        "D16": {
            "id": 11,
            "Width": 2880,
            "Height": 2304,
            "AspectX": 1.0,
            "AspectY": 1.0,
            "Rate": 24,
        },
        "2K Full Aperture (Super 35)": {
            "id": 12,
            "Width": 2048,
            "Height": 1556,
            "AspectX": 1.0,
            "AspectY": 1.0,
            "Rate": 24,
        },
        "4K Full Aperture (Super 35)": {
            "id": 13,
            "Width": 4096,
            "Height": 3112,
            "AspectX": 1.0,
            "AspectY": 1.0,
            "Rate": 24,
        },
        "2K Academy (Regular 35)": {
            "id": 14,
            "Width": 1828,
            "Height": 1332,
            "AspectX": 1.0,
            "AspectY": 1.0,
            "Rate": 24,
        },
        "4K Academy (Regular 35)": {
            "id": 15,
            "Width": 3656,
            "Height": 2664,
            "AspectX": 1.0,
            "AspectY": 1.0,
            "Rate": 24,
        },
        "2K Academy in Full Aperture": {
            "id": 16,
            "Width": 2048,
            "Height": 1556,
            "AspectX": 1.0,
            "AspectY": 1.0,
            "Rate": 24,
        },
        "4K Academy in Full Aperture": {
            "id": 17,
            "Width": 4096,
            "Height": 3112,
            "AspectX": 1.0,
            "AspectY": 1.0,
            "Rate": 24,
        },
        "2K Anamorphic (CinemaScope)": {
            "id": 18,
            "Width": 1828,
            "Height": 1556,
            "AspectX": 2.0,
            "AspectY": 1.0,
            "Rate": 24,
        },
        "4K Anamorphic (CinemaScope)": {
            "id": 19,
            "Width": 3656,
            "Height": 3112,
            "AspectX": 2.0,
            "AspectY": 1.0,
            "Rate": 24,
        },
        "2K 1.85": {
            "id": 20,
            "Width": 1828,
            "Height": 988,
            "AspectX": 1.0,
            "AspectY": 1.0,
            "Rate": 24,
        },
        "4K 1.85": {
            "id": 21,
            "Width": 3656,
            "Height": 1976,
            "AspectX": 1.0,
            "AspectY": 1.0,
            "Rate": 24,
        },
        "3K VistaVision": {
            "id": 22,
            "Width": 3072,
            "Height": 2048,
            "AspectX": 1.0,
            "AspectY": 1.0,
            "Rate": 24,
        },
        "6K VistaVision": {
            "id": 23,
            "Width": 6144,
            "Height": 4096,
            "AspectX": 1.0,
            "AspectY": 1.0,
            "Rate": 24,
        },
        "5K IMAX 70mm": {
            "id": 24,
            "Width": 5464,
            "Height": 4096,
            "AspectX": 1.0,
            "AspectY": 1.0,
            "Rate": 24,
        },
    }

    def __init__(self, name="", version=None):
        """fusion specific init"""
        super(Fusion, self).__init__(name=name, version=version)
        # and add you own modifications to __init__

        # self.fusion = bmd.scriptapp("Fusion")
        # self.fusion = bmd.get_fusion()

        self.fusion = bmf.scriptapp("Fusion")
        self.fusion_prefs = self.fusion.GetPrefs()["Global"]

        # update name with version
        self.name = "Fusion%s" % self.fusion.GetAttrs("FUSIONS_Version").split(".")[0]

        self.comp = self.fusion.GetCurrentComp()
        self.comp_prefs = self.comp.GetPrefs()["Comp"]

        self._main_output_node_name = "Main_Output"

    def save_as(self, version, run_pre_publishers=True):
        """the save action for fusion DCC

        uses Fusions own python binding
        """
        # set the extension to '.comp'
        # refresh the current comp
        self.comp = self.fusion.GetCurrentComp()
        from stalker import Version

        assert isinstance(version, Version)
        # its a new version please update the paths
        version.update_paths()
        version.extension = self.extensions[0]
        version.created_with = self.name

        # set project_directory
        import os

        self.project_directory = os.path.dirname(version.absolute_path)

        # set range from the shot
        self.set_range_from_shot(version)

        # create the main write node
        self.create_main_saver_node(version)

        # replace read and write node paths
        # self.replace_external_paths()

        # create the path before saving
        try:
            os.makedirs(version.absolute_path)
        except OSError:
            # path already exists OSError
            pass

        version_full_path = os.path.normpath(version.absolute_full_path)

        self.comp.Lock()
        self.comp.Save(
            version_full_path
            if sys.version_info[0] >= 3
            else version_full_path.encode()
        )
        self.comp.Unlock()

        # create a local copy
        self.create_local_copy(version)

        rfm = RecentFileManager()
        rfm.add(self.name, version.absolute_full_path)

        return True

    def set_range_from_shot(self, version):
        """sets the frame range from the Shot entity if this version is related
        to one.

        :param version:
        :return:
        """
        # check if this is a shot related task
        shot = self.get_shot(version)

        if shot:
            # use the shot image_format
            fps = shot.fps
            imf = shot.image_format

            # set frame ranges
            self.set_frame_range(
                start_frame=shot.cut_in,
                end_frame=shot.cut_out,
            )
        else:
            # use the Project image_format
            fps = version.task.project.fps
            imf = version.task.project.image_format

        # set comp resolution and fps
        if imf:
            self.comp.SetPrefs(
                {
                    # Image Format
                    "Comp.FrameFormat.Width": imf.width,
                    "Comp.FrameFormat.Height": imf.height,
                    "Comp.FrameFormat.AspectY": imf.pixel_aspect,
                    "Comp.FrameFormat.AspectX": imf.pixel_aspect,
                    # FPS
                    "Comp.FrameFormat.Rate": fps,
                    # set project frame format to 16bit
                    "Comp.FrameFormat.DepthFull": 2.0,
                    "Comp.FrameFormat.DepthLock": True,
                }
            )

    def set_shot_from_range(self, version):
        """sets the Shot.cut_in and Shot.cut_out attributes from the current frame range if the current task is related
        to a Stalker Shot instance.

        :param Stalker.Version version: A Stalker Version instance.
        :return:
        """
        # check if this is a shot related task
        is_shot_related_task = False
        shot = None
        from stalker import Shot

        for task in version.task.parents:
            if isinstance(task, Shot):
                is_shot_related_task = True
                shot = task
                break

        if is_shot_related_task and shot:
            # set frame ranges
            cut_in, cut_out = self.get_frame_range()
            shot.cut_in = int(cut_in)
            shot.cut_out = int(cut_out)
            from stalker.db.session import DBSession

            DBSession.add(shot)
            DBSession.commit()

    def export_as(self, version):
        """the export action for nuke DCC"""
        # its a new version please update the paths
        version.update_paths()
        # set the extension to '.comp'
        version.extension = self.extensions[0]
        version.created_with = self.name

        raise NotImplementedError("export_as() is not implemented yet for Fusion")

        # # create a local copy
        # self.create_local_copy(version)

    def open(
        self,
        version,
        force=False,
        representation=None,
        reference_depth=0,
        skip_update_check=False,
    ):
        """the open action for nuke DCC"""
        import os

        version_full_path = os.path.normpath(version.absolute_full_path)

        # # delete all the comps and open new one
        # comps = self.fusion.GetCompList().values()
        # for comp_ in comps:
        #     comp_.Close()

        self.fusion.LoadComp(
            version_full_path
            if sys.version_info[0] >= 3
            else version_full_path.encode()
        )

        self.comp.Lock()

        # set the project_directory
        # get the current comp fist
        self.comp = self.fusion.GetCurrentComp()
        self.project_directory = os.path.dirname(version.absolute_path)

        # update the savers
        self.create_main_saver_node(version)

        # file paths in different OS'es should be replaced with a path that is suitable for the current one
        # update loaders
        self.fix_loader_paths()

        self.comp.Unlock()

        rfm = RecentFileManager()
        rfm.add(self.name, version.absolute_full_path)

        # return True to specify everything was ok and an empty list
        # for the versions those needs to be updated
        return empty_reference_resolution()

    def import_(self, version):
        """the import action for nuke DCC"""
        # nuke.nodePaste(version.absolute_full_path)
        return True

    def get_current_version(self):
        """Finds the Version instance from the current open file.

        If it can't find any then returns None.

        :return: :class:`~oyProjectManager.models.version.Version`
        """
        # full_path = self._root.knob('name').value()
        import os

        full_path = os.path.normpath(self.comp.GetAttrs()["COMPS_FileName"]).replace(
            "\\", "/"
        )
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
            logger.debug("no recent files")
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
        """gets the file name from fusion"""
        version = self.get_current_version()

        # read the recent file list
        if version is None:
            version = self.get_version_from_recent_files()

        # get the latest possible Version instance by using the workspace path
        if version is None:
            version = self.get_version_from_project_dir()

        return version

    def get_frame_range(self):
        """returns the current frame range"""
        start_frame = self.comp.GetAttrs()["COMPN_RenderStart"]
        end_frame = self.comp.GetAttrs()["COMPN_RenderEnd"]
        return start_frame, end_frame

    def set_frame_range(self, start_frame=1, end_frame=100, adjust_frame_range=False):
        """sets the start and end frame range"""
        self.comp.SetAttrs(
            {
                "COMPN_GlobalStart": start_frame,
                "COMPN_RenderStart": start_frame,
                "COMPN_GlobalEnd": end_frame,
                "COMPN_RenderEnd": end_frame,
            }
        )

    def set_fps(self, fps=25):
        """sets the current fps"""
        pass

    def get_fps(self):
        """returns the current fps"""
        return None

    def fix_loader_paths(self):
        """fixes loader paths mainly from one OS to another"""
        import os

        # get all loaders
        for loader in self.comp.GetToolList(False, "Loader").values():
            path = self.get_node_input_entry_value_by_name(loader, "Clip")
            if os.path.sep not in path:
                # replace '\\' with os.path.sep
                path = path.replace("/", "\\").replace("\\", os.path.sep)
                # TODO: Also replace absolute paths with proper paths for the current OS
                self.set_node_input_entry_by_name(loader, "Clip", path)

    def get_node_input_entry_by_name(self, node, key):
        """returns the Input List entry by input list entry name

        :param node: The node
        :param string key: The entry name
        :return:
        """
        node_input_list = node.GetInputList()
        for input_entry_key in node_input_list.keys():
            input_entry = node_input_list[input_entry_key]
            input_id = input_entry.GetAttrs()["INPS_ID"]
            if input_id == key:
                return input_entry

    def get_node_input_entry_value_by_name(self, node, key):
        """returns the Input List entry by input list entry name

        :param node: The node
        :param string key: The entry name
        :return:
        """
        input_entry = self.get_node_input_entry_by_name(node, key)
        return input_entry[0]

    def set_node_input_entry_by_name(self, node, key, value):
        """sets the Input List entry value by Input ID

        :param node: The node
        :param string key: The INS_ID of the key
        :param value: The value
        :return:
        """
        input_entry = self.get_node_input_entry_by_name(node, key)
        input_entry[0] = value

    def get_main_saver_node(self):
        """Returns the main saver nodes in the scene or an empty list.
        :return: list
        """
        # list all the saver nodes in the current file
        all_saver_nodes = self.comp.GetToolList(False, "Saver").values()

        saver_nodes = []
        for saver_node in all_saver_nodes:
            if saver_node.GetAttrs("TOOLS_Name").startswith(
                self._main_output_node_name
            ):
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
                created_root_nodes.append(self.create_node_tree(item))
            return created_root_nodes

        node_type = node_tree["type"]

        self.comp.Lock()
        node = self.comp.AddTool(node_type)
        self.comp.Unlock()

        # attributes
        if "attr" in node_tree:
            attributes = node_tree["attr"]
            for key in attributes:
                value = attributes[key]
                if isinstance(value, dict):
                    new_node = self.create_node_tree(value)
                    node.Input = new_node
                else:
                    node.SetAttrs({key: value})

        # input lists
        if "input_list" in node_tree:
            input_list = node_tree["input_list"]
            for key in input_list:
                node_input_list = node.GetInputList()
                for input_entry_key in node_input_list.keys():
                    input_entry = node_input_list[input_entry_key]
                    input_id = input_entry.GetAttrs()["INPS_ID"]
                    if input_id == key:
                        value = input_list[key]
                        input_entry[0] = value
                        break

        # ref_id
        if "ref_id" in node_tree:
            node.SetData("ref_id", node_tree["ref_id"])

        # connected to
        if "connected_to" in node_tree:
            connected_to = node_tree["connected_to"]
            if "Input" in connected_to:
                input_node = self.create_node_tree(connected_to["Input"])
                node.Input = input_node
            elif "ref_id" in node_tree["connected_to"]:
                ref_id = node_tree["connected_to"]["ref_id"]
                print("ref_id: %s" % ref_id)
                # find a node with ref_id equals to ref_id that is given in the
                # node tree
                all_nodes = self.comp.GetToolList().values()
                for r_node in all_nodes:
                    node_ref_id = r_node.GetData("ref_id")
                    print("node_ref_id: %s" % node_ref_id)
                    if node_ref_id == ref_id:
                        node.Input = r_node
                        break

        return node

    def output_path_generator(self, version, file_format):
        """helper function to generate the output path

        :param version: Stalker Version instance
        :param str file_format: A string showing the file format. Ex: tga, exr
          etc.
        :return:
        """
        # generate the data needed
        # the output path
        file_name_buffer = []
        template_kwargs = {}

        # if this is a shot related task set it to shots resolution
        version_sig_name = self.get_significant_name(
            version, include_project_code=False
        )

        file_name_buffer.append("%(version_sig_name)s.001.%(format)s")
        template_kwargs.update(
            {"version_sig_name": version_sig_name, "format": file_format}
        )

        output_file_name = "".join(file_name_buffer) % template_kwargs

        # check if it is a stereo comp
        # if it is enable separate view rendering
        import os

        output_file_path = os.path.join(
            version.absolute_path,
            "Outputs",
            version.take_name,
            "v%03d" % version.version_number,
            file_format,
        )

        # create the dir
        try:
            os.makedirs(output_file_path)
        except OSError:
            # path exists
            pass

        output_file_full_path = os.path.join(
            output_file_path, output_file_name
        ).replace("\\", "/")

        # make the path Project: relative
        output_file_full_path = "Project:%s" % os.path.relpath(
            output_file_full_path, os.path.dirname(version.absolute_path)
        )

        # set the output path
        if sys.version_info[0] >= 3:
            return "%s" % os.path.normpath(output_file_full_path)
        else:
            return "%s" % os.path.normpath(output_file_full_path).encode()

    def output_node_name_generator(self, file_format):
        return "%s_%s" % (self._main_output_node_name, file_format)

    def create_slate_node(self, version, submitting_for="FINAL", submission_note=""):
        """Creates the slate node

        :param version: A Stalker Version instance
        :param str submitting_for: Submitting for "FINAL" or "WIP". Default is "FINAL".
        :param str submission_note: Submission note.
        :return:
        """
        # if the channels are animated, set new keyframes
        # first try to find the slate tool
        slate_node = self.comp.FindTool("MainSlate")
        if not slate_node:
            # create one
            self.comp.Lock()
            self.comp.DoAction("AddSetting", {"filename": "Macros:/AnimaSlate.setting"})
            slate_node = self.comp.FindTool("AnimaSlate1")
            self.comp.Unlock()
            slate_node.SetAttrs({"TOOLS_Name": "MainSlate", "TOOLB_Locked": False})

        # set slate attributes
        from anima.dcc.fusion import utils

        # Thumbnail
        shot = self.get_shot(version)
        imf = None
        if shot:
            if shot.thumbnail:
                import os

                thumbnail_full_path = os.path.expandvars(shot.thumbnail.full_path)
                slate_node.Input1 = thumbnail_full_path

            if shot:
                imf = shot.image_format
            else:
                imf = version.task.project.image_format

            # Shot Types
            # TODO: For now use Netflix format, extend it later on
            from anima.utils.report import NetflixReporter

            slate_node.Input8 = ", ".join(
                NetflixReporter.generate_shot_methodologies(shot)
            )

            # Shot Description
            from anima.utils import text_splitter

            split_description = text_splitter(shot.description, 40)
            slate_node.Input9 = "\n".join(split_description[0:3])
            slate_node.Input10 = "\n".join(split_description[0:3])

            # Submission Note
            slate_node.Input11 = submission_note

            # Shot Name
            slate_node.Input12 = shot.name

            # Episode and Sequence
            seq = None
            if shot.sequences:
                seq = shot.sequences[0]
                slate_node.Input14 = seq.name
                slate_node.Input15 = seq.name

            # Scene Name
            # Use shot name for now
            parts = shot.name.split("_")
            try:
                scene_name = parts[2]
            except IndexError:
                scene_name = ""
            slate_node.Input16 = scene_name

            # Frames
            slate_node.Input17 = shot.cut_out - shot.cut_in + 1
        else:
            # Frames
            slate_node.Input17 = ""

        # Show Name
        slate_node.Input4 = version.task.project.name

        # Version Name
        slate_node.Input5 = "%s_v%03d" % (version.nice_name, version.version_number)

        # Submitting For
        slate_node.Input6 = submitting_for

        # Date
        import datetime

        today = datetime.datetime.today()
        date_time_format = "%Y-%m-%d"
        slate_node.Input7 = today.strftime(date_time_format)

        # Vendor
        from stalker import Studio

        studio = Studio.query.first()
        if studio:
            slate_node.Input13 = studio.name

        # Media Color
        slate_node.Input18 = ""

        # connect the output to MediaOut
        media_out_node = None
        i = 0
        import time

        while not media_out_node and i < 2:
            media_out_node = self.comp.FindTool("MediaOut1")
            if not media_out_node:
                print("no MediaOut1 node, waiting for 1 sec!")
                time.sleep(1)
            else:
                print("found MediaOut1 node!")
                media_out_node.Input = slate_node
            i += 1

        return slate_node

    def create_main_saver_node(self, version):
        """Creates the default saver node if there is no created before.

        Creates the default saver nodes if there isn't any existing outputs,
        and updates the ones that is already created
        """
        fps = 25
        if version:
            project = version.task.project
            fps = project.fps

        import uuid

        random_ref_id = uuid.uuid4().hex

        output_format_data = [
            {
                "name": "jpg",
                "node_tree": {
                    "type": "Saver",
                    "attr": {
                        "TOOLS_Name": self.output_node_name_generator("jpg"),
                    },
                    "input_list": {
                        "Clip": self.output_path_generator(version, "jpg"),
                        "CreateDir": 1,
                        "ProcessRed": 1,
                        "ProcessGreen": 1,
                        "ProcessBlue": 1,
                        "ProcessAlpha": 0,
                        "OutputFormat": "JPEGFormat",
                        "JpegFormat.Quality": 85,
                    },
                    "connected_to": {
                        "Input": {
                            "type": "OCIOColorSpace",
                            "ref_id": random_ref_id,
                            "input_list": {
                                "OCIOConfig": "LUTs:/OpenColorIO-Configs/aces_1.2/config.ocio",
                                "SourceSpace": "ACES - ACES2065-1",
                                "OutputSpace": "Output - Rec.709",
                            },
                            "connected_to": {
                                "Input": {
                                    "type": "OCIOColorSpace",
                                    "input_list": {
                                        "OCIOConfig": "LUTs:/OpenColorIO-Configs/aces_1.2/config.ocio",
                                        "SourceSpace": "Utility - Linear - sRGB",
                                        "OutputSpace": "ACES - ACES2065-1",
                                    },
                                }
                            },
                        }
                    },
                },
            },
            {
                "name": "tga",
                "node_tree": {
                    "type": "Saver",
                    "attr": {
                        "TOOLS_Name": self.output_node_name_generator("tga"),
                    },
                    "input_list": {
                        "Clip": self.output_path_generator(version, "tga"),
                        "CreateDir": 1,
                        "ProcessRed": 1,
                        "ProcessGreen": 1,
                        "ProcessBlue": 1,
                        "ProcessAlpha": 0,
                        "OutputFormat": "TGAFormat",
                    },
                    "connected_to": {"ref_id": random_ref_id},
                },
            },
            {
                "name": "exr",
                "node_tree": {
                    "type": "Saver",
                    "attr": {
                        "TOOLS_Name": self.output_node_name_generator("exr"),
                    },
                    "input_list": {
                        "Clip": self.output_path_generator(version, "exr"),
                        "CreateDir": 1,
                        "ProcessRed": 1,
                        "ProcessGreen": 1,
                        "ProcessBlue": 1,
                        "ProcessAlpha": 0,
                        "OutputFormat": "OpenEXRFormat",
                        "OpenEXRFormat.Depth": 1,  # 16-bit float
                        "OpenEXRFormat.RedEnable": 1,
                        "OpenEXRFormat.GreenEnable": 1,
                        "OpenEXRFormat.BlueEnable": 1,
                        "OpenEXRFormat.AlphaEnable": 0,
                        "OpenEXRFormat.ZEnable": 0,
                        "OpenEXRFormat.CovEnable": 0,
                        "OpenEXRFormat.ObjIDEnable": 0,
                        "OpenEXRFormat.MatIDEnable": 0,
                        "OpenEXRFormat.UEnable": 0,
                        "OpenEXRFormat.VEnable": 0,
                        "OpenEXRFormat.XNormEnable": 0,
                        "OpenEXRFormat.YNormEnable": 0,
                        "OpenEXRFormat.ZNormEnable": 0,
                        "OpenEXRFormat.XVelEnable": 0,
                        "OpenEXRFormat.YVelEnable": 0,
                        "OpenEXRFormat.XRevVelEnable": 0,
                        "OpenEXRFormat.YRevVelEnable": 0,
                        "OpenEXRFormat.XPosEnable": 0,
                        "OpenEXRFormat.YPosEnable": 0,
                        "OpenEXRFormat.ZPosEnable": 0,
                        "OpenEXRFormat.XDispEnable": 0,
                        "OpenEXRFormat.YDispEnable": 0,
                    },
                    "connected_to": {"ref_id": random_ref_id},
                },
            },
            {
                "name": "mp4",
                "node_tree": {
                    "type": "Saver",
                    "attr": {
                        "TOOLS_Name": self.output_node_name_generator("mp4"),
                    },
                    "input_list": {
                        "Clip": self.output_path_generator(version, "mp4"),
                        "CreateDir": 1,
                        "ProcessRed": 1,
                        "ProcessGreen": 1,
                        "ProcessBlue": 1,
                        "ProcessAlpha": 0,
                        "OutputFormat": "QuickTimeMovies",
                        "ProcessMode": "Auto",
                        "SaveFrames": "Full",
                        "QuickTimeMovies.Compression": "H.264_avc1",
                        "QuickTimeMovies.Quality": 95.0,
                        "QuickTimeMovies.FrameRateFps": fps,
                        "QuickTimeMovies.KeyFrames": 5,
                        "StartRenderScript": 'frames_at_once = comp:GetPrefs("Comp.Memory.FramesAtOnce")\ncomp:SetPrefs("Comp.Memory.FramesAtOnce", 1)',
                        "EndRenderScript": 'comp:SetPrefs("Comp.Memory.FramesAtOnce", frames_at_once)',
                    },
                    "connected_to": {"ref_id": random_ref_id},
                },
            },
            {
                "name": "mov",
                "node_tree": {
                    "type": "Saver",
                    "attr": {
                        "TOOLS_Name": self.output_node_name_generator("mov"),
                    },
                    "input_list": {
                        "Clip": self.output_path_generator(version, "mov"),
                        "CreateDir": 1,
                        "ProcessRed": 1,
                        "ProcessGreen": 1,
                        "ProcessBlue": 1,
                        "ProcessAlpha": 0,
                        "OutputFormat": "QuickTimeMovies",
                        "ProcessMode": "Auto",
                        "SaveFrames": "Full",
                        "QuickTimeMovies.Compression": "Apple ProRes 422 HQ_apch",
                        "QuickTimeMovies.Quality": 95.0,
                        "QuickTimeMovies.FrameRateFps": fps,
                        "QuickTimeMovies.KeyFrames": 5,
                        "QuickTimeMovies.LimitDataRate": 0.0,
                        "QuickTimeMovies.DataRateK": 1000.0,
                        "QuickTimeMovies.Advanced": 1.0,
                        "QuickTimeMovies.Primaries": 0.0,
                        "QuickTimeMovies.Transfer": 0.0,
                        "QuickTimeMovies.Matrix": 0.0,
                        "QuickTimeMovies.PixelAspectRatio": 0.0,
                        "QuickTimeMovies.ErrorDiffusion": 1.0,
                        "QuickTimeMovies.SaveAlphaChannel": 1.0,
                        "StartRenderScript": 'frames_at_once = comp:GetPrefs("Comp.Memory.FramesAtOnce")\ncomp:SetPrefs("Comp.Memory.FramesAtOnce", 1)',
                        "EndRenderScript": 'comp:SetPrefs("Comp.Memory.FramesAtOnce", frames_at_once)',
                    },
                    "connected_to": {"ref_id": random_ref_id},
                },
            },
        ]

        if version.task.type and version.task.type.name == "Plate":
            # create a different type of outputs
            output_format_data = [
                {
                    "name": "jpg",
                    "node_tree": {
                        "type": "Saver",
                        "attr": {
                            "TOOLS_Name": self.output_node_name_generator("jpg"),
                        },
                        "input_list": {
                            "Clip": self.output_path_generator(version, "jpg"),
                            "CreateDir": 1,
                            "ProcessRed": 1,
                            "ProcessGreen": 1,
                            "ProcessBlue": 1,
                            "ProcessAlpha": 0,
                            "OutputFormat": "JPEGFormat",
                            "JpegFormat.Quality": 85,
                        },
                        "connected_to": {
                            "Input": {
                                "type": "OCIOColorSpace",
                                "input_list": {
                                    "OCIOConfig": "LUTs:/OpenColorIO-Configs/aces_1.2/config.ocio",
                                    "SourceSpace": "ACES - ACES2065-1",
                                    "OutputSpace": "Output - sRGB",
                                },
                                "connected_to": {
                                    "Input": {
                                        "type": "OCIOColorSpace",
                                        "ref_id": random_ref_id,
                                        "input_list": {
                                            "OCIOConfig": "LUTs:/OpenColorIO-Configs/aces_1.2/config.ocio",
                                            "SourceSpace": "ACES - ACES2065-1",
                                            "OutputSpace": "ACES - ACES2065-1",
                                        },
                                    }
                                },
                            }
                        },
                    },
                },
                {
                    "name": "exr",
                    "node_tree": {
                        "type": "Saver",
                        "attr": {
                            "TOOLS_Name": self.output_node_name_generator("exr"),
                        },
                        "input_list": {
                            "Clip": self.output_path_generator(version, "exr"),
                            "CreateDir": 1,
                            "ProcessRed": 1,
                            "ProcessGreen": 1,
                            "ProcessBlue": 1,
                            "ProcessAlpha": 0,
                            "OutputFormat": "OpenEXRFormat",
                            "OpenEXRFormat.Depth": 1,  # 16-bit float
                            "OpenEXRFormat.RedEnable": 1,
                            "OpenEXRFormat.GreenEnable": 1,
                            "OpenEXRFormat.BlueEnable": 1,
                            "OpenEXRFormat.AlphaEnable": 0,
                            "OpenEXRFormat.ZEnable": 0,
                            "OpenEXRFormat.CovEnable": 0,
                            "OpenEXRFormat.ObjIDEnable": 0,
                            "OpenEXRFormat.MatIDEnable": 0,
                            "OpenEXRFormat.UEnable": 0,
                            "OpenEXRFormat.VEnable": 0,
                            "OpenEXRFormat.XNormEnable": 0,
                            "OpenEXRFormat.YNormEnable": 0,
                            "OpenEXRFormat.ZNormEnable": 0,
                            "OpenEXRFormat.XVelEnable": 0,
                            "OpenEXRFormat.YVelEnable": 0,
                            "OpenEXRFormat.XRevVelEnable": 0,
                            "OpenEXRFormat.YRevVelEnable": 0,
                            "OpenEXRFormat.XPosEnable": 0,
                            "OpenEXRFormat.YPosEnable": 0,
                            "OpenEXRFormat.ZPosEnable": 0,
                            "OpenEXRFormat.XDispEnable": 0,
                            "OpenEXRFormat.YDispEnable": 0,
                        },
                        "connected_to": {
                            "Input": {
                                "type": "OCIOColorSpace",
                                "input_list": {
                                    "OCIOConfig": "LUTs:/OpenColorIO-Configs/aces_1.2/config.ocio",
                                    "SourceSpace": "ACES - ACES2065-1",
                                    "OutputSpace": "ACES - ACES2065-1",
                                },
                                "connected_to": {
                                    "ref_id": random_ref_id,
                                },
                            }
                        },
                    },
                },
                {
                    "name": "mov",
                    "node_tree": {
                        "type": "Saver",
                        "attr": {
                            "TOOLS_Name": self.output_node_name_generator("mov"),
                        },
                        "input_list": {
                            "Clip": self.output_path_generator(version, "mov"),
                            "CreateDir": 1,
                            "ProcessRed": 1,
                            "ProcessGreen": 1,
                            "ProcessBlue": 1,
                            "ProcessAlpha": 0,
                            "OutputFormat": "QuickTimeMovies",
                            "ProcessMode": "Auto",
                            "SaveFrames": "Full",
                            "QuickTimeMovies.Compression": "Apple ProRes 422 HQ_apch",
                            "QuickTimeMovies.Quality": 95.0,
                            "QuickTimeMovies.FrameRateFps": fps,
                            "QuickTimeMovies.KeyFrames": 5,
                            "QuickTimeMovies.LimitDataRate": 0.0,
                            "QuickTimeMovies.DataRateK": 1000.0,
                            "QuickTimeMovies.Advanced": 1.0,
                            "QuickTimeMovies.Primaries": 0.0,
                            "QuickTimeMovies.Transfer": 0.0,
                            "QuickTimeMovies.Matrix": 0.0,
                            "QuickTimeMovies.PixelAspectRatio": 0.0,
                            "QuickTimeMovies.ErrorDiffusion": 1.0,
                            "QuickTimeMovies.SaveAlphaChannel": 1.0,
                            "StartRenderScript": 'frames_at_once = comp:GetPrefs("Comp.Memory.FramesAtOnce")\ncomp:SetPrefs("Comp.Memory.FramesAtOnce", 1)',
                            "EndRenderScript": 'comp:SetPrefs("Comp.Memory.FramesAtOnce", frames_at_once)',
                        },
                        "connected_to": {
                            "Input": {
                                "type": "OCIOColorSpace",
                                "input_list": {
                                    "OCIOConfig": "LUTs:/OpenColorIO-Configs/aces_1.2/config.ocio",
                                    "SourceSpace": "ACES - ACES2065-1",
                                    "OutputSpace": "Output - Rec.709",
                                },
                                "connected_to": {
                                    "ref_id": random_ref_id,
                                },
                            }
                        },
                    },
                },
            ]

        if version.take_name == "STMap":
            output_format_data = [
                {
                    "name": "exr",
                    "node_tree": {
                        "type": "Saver",
                        "attr": {
                            "TOOLS_Name": self.output_node_name_generator("exr"),
                        },
                        "input_list": {
                            "Clip": self.output_path_generator(version, "exr"),
                            "CreateDir": 1,
                            "ProcessRed": 1,
                            "ProcessGreen": 1,
                            "ProcessBlue": 1,
                            "ProcessAlpha": 0,
                            "OutputFormat": "OpenEXRFormat",
                            "OpenEXRFormat.Depth": 2,  # 32-bit float
                            "OpenEXRFormat.RedEnable": 1,
                            "OpenEXRFormat.GreenEnable": 1,
                            "OpenEXRFormat.BlueEnable": 1,
                            "OpenEXRFormat.AlphaEnable": 0,
                            "OpenEXRFormat.ZEnable": 0,
                            "OpenEXRFormat.CovEnable": 0,
                            "OpenEXRFormat.ObjIDEnable": 0,
                            "OpenEXRFormat.MatIDEnable": 0,
                            "OpenEXRFormat.UEnable": 0,
                            "OpenEXRFormat.VEnable": 0,
                            "OpenEXRFormat.XNormEnable": 0,
                            "OpenEXRFormat.YNormEnable": 0,
                            "OpenEXRFormat.ZNormEnable": 0,
                            "OpenEXRFormat.XVelEnable": 0,
                            "OpenEXRFormat.YVelEnable": 0,
                            "OpenEXRFormat.XRevVelEnable": 0,
                            "OpenEXRFormat.YRevVelEnable": 0,
                            "OpenEXRFormat.XPosEnable": 0,
                            "OpenEXRFormat.YPosEnable": 0,
                            "OpenEXRFormat.ZPosEnable": 0,
                            "OpenEXRFormat.XDispEnable": 0,
                            "OpenEXRFormat.YDispEnable": 0,
                        },
                        "connected_to": {"ref_id": random_ref_id},
                    },
                },
            ]
            self.comp.SetPrefs(
                {
                    # set project frame format to 32bit
                    "Comp.FrameFormat.DepthFull": 3.0,
                    "Comp.FrameFormat.DepthLock": True,
                }
            )

        # selectively generate output format
        saver_nodes = self.get_main_saver_node()

        for data in output_format_data:
            format_name = data["name"]
            node_tree = data["node_tree"]

            # now check if a node with the same name exists
            format_node = None
            format_node_name = self.output_node_name_generator(format_name)
            for node in saver_nodes:
                node_name = node.GetAttrs("TOOLS_Name")
                if node_name.startswith(format_node_name):
                    format_node = node
                    break

            # create the saver node for this format if missing
            if not format_node:
                self.create_node_tree(node_tree)
            else:
                # just update the input_lists
                if "input_list" in node_tree:
                    input_list = node_tree["input_list"]
                    for key in input_list:
                        node_input_list = format_node.GetInputList()
                        for input_entry_key in node_input_list.keys():
                            input_entry = node_input_list[input_entry_key]
                            input_id = input_entry.GetAttrs()["INPS_ID"]
                            if input_id == key:
                                value = input_list[key]
                                input_entry[0] = value
                                break

            try:
                import os

                os.makedirs(
                    os.path.dirname(self.output_path_generator(version, format_name))
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
        maps = self.comp_prefs["Paths"].get("Map", None)
        if maps:
            project_dir = maps.get("Project:", None)

        # if not project_dir:
        #     # set the map for the project dir
        #     if self.version:
        #         project_dir = os.path.dirname(self.version.absolute_path)
        #         self.project_directory = project_dir

        return project_dir

    @project_directory.setter
    def project_directory(self, project_directory_in):
        """Sets project directory

        :param str project_directory_in: the project directory
        :return:
        """
        import os

        project_directory_in = os.path.normpath(project_directory_in)
        print("setting project directory to: %s" % project_directory_in)

        # set a path map
        self.comp.SetPrefs(
            {
                "Comp.Paths.Map": {
                    "Project:": project_directory_in
                    if sys.version_info[0] >= 3
                    else project_directory_in.encode()
                }
            }
        )
