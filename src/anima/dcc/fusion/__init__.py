"""Fusion DCC module."""
from __future__ import annotations

import datetime
import os
import time
import uuid
from pathlib import Path

try:
    # for Fusion inside Resolve
    import BlackmagicFusion as bmf
except (ImportError, ModuleNotFoundError):
    # for stand-alone Fusion
    import fusionscript as bmf

from stalker import File, Shot, Studio, Version
from stalker.db.session import DBSession

from anima.dcc.base import generate_empty_reference_resolution
from anima.dcc.base import DCCBase
from anima.dcc.fusion.utils import NodeUtils
from anima.log import logger
from anima.recent import RecentFileManager


class Fusion(DCCBase):
    """the fusion DCC class"""

    name = "Fusion"
    extensions = [".comp"]

    def __init__(self, name="", version=None):
        super(Fusion, self).__init__(name=name, version=version)
        # and add you own modifications to __init__

        self.fusion = bmf.scriptapp("Fusion")
        self.fusion_prefs = self.fusion.GetPrefs()["Global"]

        # update name with version
        self.name = "Fusion{}".format(
            self.fusion.GetAttrs("FUSIONS_Version").split(".")[0]
        )

        self.comp = self.fusion.GetCurrentComp()
        self.comp_prefs = self.comp.GetPrefs()["Comp"]

        self._main_output_node_name = "Main_Output"

    def save_as(self, file: File, run_pre_publishers: bool = True) -> bool:
        """Save the current open scene as the given.

        Args:
            file (stalker.File): A `stalker.File` instance.
            run_pre_publishers (bool, optional): Run pre-publishers if True.
                Default value is True. Currently unused.
        """
        # set the extension to '.comp'
        # refresh the current comp
        self.comp = self.fusion.GetCurrentComp()

        # get the related Version
        version : Version = Version.query.filter(Version.files.contains(file)).first()

        # its a new version please update the paths
        full_path: Path = version.generate_path(extension=self.extensions[0])
        file.full_path = str(full_path)
        file.created_with = self.name

        # set project_directory
        if shot := self.get_shot(version):
            # project directory should be set to the shot directory.
            self.project_directory = shot.absolute_path
        elif asset := self.get_asset(version):
            # project directory should be set to the asset directory.
            self.project_directory = asset.absolute_path
        else:
            # set project directory to the file absolute path.
            self.project_directory = os.path.dirname(file.absolute_path)

        # set range from the shot
        self.set_range_from_shot(version)

        # create the main write node
        self.create_main_saver_node(file)

        # replace read and write node paths
        # self.replace_external_paths()

        # create the path before saving
        try:
            os.makedirs(version.absolute_path)
        except OSError:
            # path already exists OSError
            pass

        # instead of lock/unlock disable AutoClipBrowse temporarily
        auto_browse = NodeUtils.disable_auto_clip_browse()
        self.comp.Save(file.absolute_full_path)
        NodeUtils.set_auto_clip_browse(auto_browse)

        # create a local copy
        self.create_local_copy(file)

        rfm = RecentFileManager()
        rfm.add(self.name, file.absolute_full_path)

        return True

    def set_range_from_shot(self, version: Version) -> None:
        """Set the frame range from the Shot entity if this version is related to one.

        Args:
            version (stalker.Version): The `stalker.Version` instance.
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

    def set_shot_from_range(self, version: Version) -> None:
        """Set the Shot.cut_in and Shot.cut_out attributes from the current frame range.

        This only works if the current task is related to a Stalker Shot instance.

        Args:
            version (stalker.Version): A Stalker Version instance.
        """
        # check if this is a shot related task
        is_shot_related_task = False
        shot = None

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

            DBSession.add(shot)
            DBSession.commit()

    def export_as(self, file):
        """Export the current as the given file.

        Args:
            file (stalker.File): The `stalker.File` instance.
        """
        raise NotImplementedError("export_as() is not implemented yet for Fusion")
        # its a new version please update the paths
        version : Version = Version.query.filter(Version.files.contains(file)).first()
        if not version:
            return
        # set the extension to '.comp'
        full_path = version.generate_path(extension=self.extensions[0])
        file.created_with = self.name

    def open(
        self,
        file: File,
        force: bool = False,
        representation: None | str = None,
        reference_depth: int = 0,
        skip_update_check: bool = False,
    ) -> bool:
        """Open the given File.

        Args:
            file (File): The Stalker `File` instance to open.
            force (bool): Unused.
            representation (str): Unused.
            reference_depth (int): Unused.
            skip_update_check (bool): Unused.

        Returns:
            bool: True if everything went well, False otherwise.
        """
        file_full_path = file.absolute_full_path

        # # delete all the comps and open new one
        # comps = self.fusion.GetCompList().values()
        # for comp_ in comps:
        #     comp_.Close()

        self.fusion.LoadComp(file_full_path)

        # instead of lock/unlock disable AutoClipBrowse temporarily
        auto_browse = NodeUtils.disable_auto_clip_browse()

        # set the project_directory
        # get the current comp fist
        self.comp = self.fusion.GetCurrentComp()

        # set project_directory
        version = Version.query.filter(Version.files.contains(file)).first()
        if shot := self.get_shot(version):
            # project directory should be set to the shot directory.
            self.project_directory = shot.absolute_path
        elif asset := self.get_asset(version):
            # project directory should be set to the asset directory.
            self.project_directory = asset.absolute_path
        else:
            # set project directory to the file absolute path.
            self.project_directory = os.path.dirname(file.absolute_path)

        # update the savers
        self.create_main_saver_node(file)

        # file paths in different OS'es should be replaced with a path that is suitable
        # for the current one
        # update loaders
        self.fix_loader_paths()

        NodeUtils.set_auto_clip_browse(auto_browse)

        rfm = RecentFileManager()
        rfm.add(self.name, file.absolute_full_path)

        # return True to specify everything was ok and an empty list
        # for the versions those needs to be updated
        return generate_empty_reference_resolution()

    def import_(self, file):
        """Import the given file content to the current scene."""
        # nuke.nodePaste(version.absolute_full_path)
        return True

    def get_current_file(self):
        """Return the File instance from the current open file.

        If it can't find any then return None.

        Returns:
            :class:`~stalker.models.file.File`: The currently opened file instance.
        """
        # full_path = self._root.knob('name').value()
        full_path = os.path.normpath(self.comp.GetAttrs()["COMPS_FileName"]).replace(
            "\\", "/"
        )
        return self.get_file_from_full_path(full_path)

    def get_current_version(self):
        """Find the Version instance from the current open file.

        If it can't find any then return None.

        :return: :class:`~stalker.models.version.Version`
        """
        # full_path = self._root.knob('name').value()
        full_path = os.path.normpath(self.comp.GetAttrs()["COMPS_FileName"]).replace(
            "\\", "/"
        )
        return self.get_version_from_full_path(full_path)

    def get_file_from_project_dir(self):
        """Try to find a Version from the current project directory.

        Returns:
            :class:`~stalker.models.version.Version`
        """
        files = self.get_files_from_path(self.project_directory)
        if files and len(files):
            return files[0]
        return None

    def get_last_file(self):
        """Return the last opened File instance."""
        file = super().get_last_file()
        if file:
            return file

        return self.get_file_from_project_dir()

    def get_last_version(self) -> None | Version:
        """Return the Version from fusion.

        Returns:
            None | Version: The Version instance if found, None otherwise.
        """
        version = super().get_last_version()

        # get the latest possible Version instance by using the workspace path
        if version is None:
            if file := self.get_file_from_project_dir():
                version = Version.query.filter(Version.files.contains(file)).first()

        return version

    def get_frame_range(self) -> tuple[int, int]:
        """Return the current frame range.

        Returns:
            tuple[int, int]: The current frame range.
        """
        start_frame = self.comp.GetAttrs()["COMPN_RenderStart"]
        end_frame = self.comp.GetAttrs()["COMPN_RenderEnd"]
        return start_frame, end_frame

    def set_frame_range(
        self,
        start_frame: int = 1,
        end_frame: int = 100,
        adjust_frame_range: bool = False
    ) -> None:
        """Set the start and end frame range.

        Args:
            start_frame (int, optional): The start frame.
            end_frame (int, optional): The end frame.
            adjust_frame_range(bool, optional): Currently unused. False by default.
        """
        self.comp.SetAttrs(
            {
                "COMPN_GlobalStart": start_frame,
                "COMPN_RenderStart": start_frame,
                "COMPN_GlobalEnd": end_frame,
                "COMPN_RenderEnd": end_frame,
            }
        )

    def set_fps(self, fps: int | float = 25) -> None:
        """Set the current fps.

        Currently defunct.

        Args:
            fps (int | float): The frame rate.
        """

    def get_fps(self) -> None:
        """Return the current fps.

        Returns:
            None: Currently not returning anything other than None.
        """
        return None

    def fix_loader_paths(self) -> None:
        """Fix loader paths mainly from one OS to another."""
        # get all loaders
        for loader in self.comp.GetToolList(False, "Loader").values():
            path = self.get_node_input_entry_value_by_name(loader, "Clip")
            if os.path.sep not in path:
                # replace '\\' with os.path.sep
                path = path.replace("/", "\\").replace("\\", os.path.sep)
                # TODO: Also replace absolute paths with proper paths for the current OS
                self.set_node_input_entry_by_name(loader, "Clip", path)

    def get_node_input_entry_by_name(self, node, key: str) -> None | dict:
        """Return the Input List entry by input list entry name.

        Args:
            node: The node.
            key (key): The entry name

        Returns:
            None | dict: The Input List entry by input list entry name, if one
                can be found. None otherwise.
        """
        node_input_list = node.GetInputList()
        for input_entry_key in node_input_list.keys():
            input_entry = node_input_list[input_entry_key]
            input_id = input_entry.GetAttrs()["INPS_ID"]
            if input_id == key:
                return input_entry
        return None

    def get_node_input_entry_value_by_name(self, node, key: str):
        """Return the Input List entry by input list entry name.

        Args:
            node: The node.
            key (str): The entry name.

        Returns:
            object: ???
        """
        input_entry = self.get_node_input_entry_by_name(node, key)
        return input_entry[0]

    def set_node_input_entry_by_name(self, node, key, value) -> None:
        """Set the Input List entry value by Input ID.

        Args:
            node: The node.
            key (str): The INS_ID of the key.
            value (str | float): The value.
        """
        input_entry = self.get_node_input_entry_by_name(node, key)
        input_entry[0] = value

    def get_main_saver_node(self) -> list:
        """Return the main saver nodes in the scene or an empty list.

        Returns:
            list: List of nodes.
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

    def create_node_tree(self, node_tree: list | dict):
        """Create a node tree from the given node tree.

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

        Args:
            node_tree (list | dict): A dictionary showing the node tree
                attributes.

        Returns:
            node: The created node.
        """
        # allow it to accept both a list or dict
        if isinstance(node_tree, list):
            created_root_nodes = []
            for item in node_tree:
                created_root_nodes.append(self.create_node_tree(item))
            return created_root_nodes

        node_type = node_tree["type"]

        # instead of lock/unlock disable AutoClipBrowse temporarily
        auto_browse = NodeUtils.disable_auto_clip_browse()
        node = self.comp.AddTool(node_type)
        NodeUtils.set_auto_clip_browse(auto_browse)

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
                print(f"ref_id: {ref_id}")
                # find a node with ref_id equals to ref_id that is given in the
                # node tree
                all_nodes = self.comp.GetToolList().values()
                for r_node in all_nodes:
                    node_ref_id = r_node.GetData("ref_id")
                    print(f"node_ref_id: {node_ref_id}")
                    if node_ref_id == ref_id:
                        node.Input = r_node
                        break

        return node

    def generate_output_path(self, version: Version, file_format: str) -> str:
        """Generate the output path.

        Args:
            version (stalker.Version): Stalker Version instance.
            file_format (str): A string showing the file format. Ex: tga, exr
                etc.

        Returns:
            str: The generated output path.
        """
        # generate the data needed
        # the output path
        file_name_buffer = []
        template_kwargs = {}

        # if this is a shot related task set it to shots resolution
        version_sig_name = self.get_significant_name(
            version, include_project_code=False
        )

        file_name_buffer.append("{version_sig_name}.001.{format}")
        template_kwargs.update(
            {"version_sig_name": version_sig_name, "format": file_format}
        )

        output_file_name = "".join(file_name_buffer).format(**template_kwargs)

        # check if it is a stereo comp
        # if it is enable separate view rendering
        output_file_path = os.path.join(
            version.absolute_path,
            "Outputs",
            f"r{version.revision_number:02d}_v{version.version_number:03d}",
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
        output_file_full_path = "Project:{}".format(
            os.path.relpath(
                output_file_full_path,
                self.project_directory
            )
        )

        # set the output path
        return os.path.normpath(output_file_full_path)

    def output_node_name_generator(self, file_format: str) -> str:
        """Generate output node name.

        Args:
            file_format (str): The file format name.

        Returns:
            str: The output node name.
        """
        return "{}_{}".format(self._main_output_node_name, file_format)

    def create_slate_node(
        self,
        version: Version,
        submitting_for: str = "FINAL",
        submission_note: str = ""
    ):
        """Create the slate node.

        Args:
            version (Version): A Stalker Version instance.
            submitting_for (str, optional): Submitting for "FINAL" or "WIP".
                Default is "FINAL".
            submission_note (str, optional): Submission note.

        Return:
            node: The created slate node.
        """
        # if the channels are animated, set new keyframes
        # first try to find the slate tool
        slate_node = self.comp.FindTool("MainSlate")
        if not slate_node:
            # create one
            # instead of lock/unlock disable AutoClipBrowse temporarily
            auto_browse = NodeUtils.disable_auto_clip_browse()
            self.comp.DoAction("AddSetting", {"filename": "Macros:/AnimaSlate.setting"})
            slate_node = self.comp.FindTool("AnimaSlate1")
            NodeUtils.set_auto_clip_browse(auto_browse)
            slate_node.SetAttrs({"TOOLS_Name": "MainSlate", "TOOLB_Locked": False})

        # set slate attributes
        from anima.dcc.fusion import utils

        # Thumbnail
        shot = self.get_shot(version)
        imf = None
        if shot:
            if shot.thumbnail:
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
        slate_node.Input5 = (
            f"{version.nice_name}"
            f"_r{version.revision_number:02d}"
            f"_v{version.version_number:03d}"
        )

        # Submitting For
        slate_node.Input6 = submitting_for

        # Date

        today = datetime.datetime.today()
        date_time_format = "%Y-%m-%d"
        slate_node.Input7 = today.strftime(date_time_format)

        # Vendor

        studio = Studio.query.first()
        if studio:
            slate_node.Input13 = studio.name

        # Media Color
        slate_node.Input18 = ""

        # connect the output to MediaOut
        media_out_node = None
        i = 0
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

    def create_main_saver_node(self, file: File) -> None:
        """Create the default saver node if there is no created before.

        Create the default saver nodes if there isn't any existing outputs,
        and updates the ones that is already created

        Args:
            file (stalker.File): The `stalker.File` instance.
        """
        fps = 25
        version = None
        if file:
            version = Version.query.filter(Version.files.contains(file)).first()
            project = version.task.project
            fps = project.fps

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
                        "Clip": self.generate_output_path(version, "jpg"),
                        "CreateDir": 1,
                        "ProcessRed": 1,
                        "ProcessGreen": 1,
                        "ProcessBlue": 1,
                        "ProcessAlpha": 0,
                        "OutputFormat": "JPEGFormat",
                        "JpegFormat.Quality": 97,
                    },
                    "connected_to": {
                        "Input": {
                            "type": "OCIOColorSpace",
                            "ref_id": random_ref_id,
                            "input_list": {
                                "OCIOConfig": (
                                    ""
                                    if "OCIO" in os.environ
                                    else "LUTs:/OpenColorIO-Configs/aces_1.3/config.ocio"
                                ),
                                "SourceSpace": "ACES - ACES2065-1",
                                "OutputSpace": "Output - Rec.709",
                            },
                            "connected_to": {
                                "Input": {
                                    "type": "OCIOColorSpace",
                                    "input_list": {
                                        "OCIOConfig": (
                                            ""
                                            if "OCIO" in os.environ
                                            else "LUTs:/OpenColorIO-Configs/aces_1.3/config.ocio"
                                        ),
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
                        "Clip": self.generate_output_path(version, "tga"),
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
                        "Clip": self.generate_output_path(version, "exr"),
                        "CreateDir": 1,
                        "ProcessRed": 1,
                        "ProcessGreen": 1,
                        "ProcessBlue": 1,
                        "ProcessAlpha": 0,
                        "OutputFormat": "OpenEXRFormat",
                        "OpenEXRFormat.Depth": 1,  # 16-bit float
                        "OpenEXRFormat.Compression": 8,  # DWA (32 lines)
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
                        "Clip": self.generate_output_path(version, "mp4"),
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
                        "Clip": self.generate_output_path(version, "mov"),
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
                            "Clip": self.generate_output_path(version, "jpg"),
                            "CreateDir": 1,
                            "ProcessRed": 1,
                            "ProcessGreen": 1,
                            "ProcessBlue": 1,
                            "ProcessAlpha": 0,
                            "OutputFormat": "JPEGFormat",
                            "JpegFormat.Quality": 97,
                        },
                        "connected_to": {
                            "Input": {
                                "type": "OCIOColorSpace",
                                "input_list": {
                                    "OCIOConfig": (
                                        ""
                                        if "OCIO" in os.environ
                                        else "LUTs:/OpenColorIO-Configs/aces_1.3/config.ocio"
                                    ),
                                    "SourceSpace": "ACES - ACES2065-1",
                                    "OutputSpace": "Utility - sRGB - Texture",
                                },
                                "connected_to": {
                                    "Input": {
                                        "type": "OCIOColorSpace",
                                        "ref_id": random_ref_id,
                                        "input_list": {
                                            "OCIOConfig": (
                                                ""
                                                if "OCIO" in os.environ
                                                else "LUTs:/OpenColorIO-Configs/aces_1.3/config.ocio"
                                            ),
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
                            "Clip": self.generate_output_path(version, "exr"),
                            "CreateDir": 1,
                            "ProcessRed": 1,
                            "ProcessGreen": 1,
                            "ProcessBlue": 1,
                            "ProcessAlpha": 0,
                            "OutputFormat": "OpenEXRFormat",
                            "OpenEXRFormat.Depth": 1,  # 16-bit float
                            "OpenEXRFormat.Compression": 8,  # DWA (32 line)
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
                                    "OCIOConfig": (
                                        ""
                                        if "OCIO" in os.environ
                                        else "LUTs:/OpenColorIO-Configs/aces_1.3/config.ocio"
                                    ),
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
                            "Clip": self.generate_output_path(version, "mov"),
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
                                    "OCIOConfig": (
                                        ""
                                        if "OCIO" in os.environ
                                        else "LUTs:/OpenColorIO-Configs/aces_1.3/config.ocio"
                                    ),
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

        if file.type and file.type.name == "STMap":
            output_format_data = [
                {
                    "name": "exr",
                    "node_tree": {
                        "type": "Saver",
                        "attr": {
                            "TOOLS_Name": self.output_node_name_generator("exr"),
                        },
                        "input_list": {
                            "Clip": self.generate_output_path(version, "exr"),
                            "CreateDir": 1,
                            "ProcessRed": 1,
                            "ProcessGreen": 1,
                            "ProcessBlue": 1,
                            "ProcessAlpha": 0,
                            "OutputFormat": "OpenEXRFormat",
                            "OpenEXRFormat.Depth": 2,  # 32-bit float
                            "OpenEXRFormat.Compression": 8,  # DWA (32 line)
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
                os.makedirs(
                    os.path.dirname(self.generate_output_path(version, format_name))
                )
            except OSError:
                # path already exists
                pass

    @property
    def project_directory(self) -> str:
        """The project directory.

        Set it to the project root, and set all your paths relative to this
        directory.

        Returns:
            str: The project directory.
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
    def project_directory(self, project_directory_in: str) -> None:
        """Set project directory.

        Args:
            project_directory_in (str): The project directory.
        """
        project_directory_in = os.path.normpath(project_directory_in)
        print(f"setting project directory to: {project_directory_in}")

        # set a path map
        self.comp.SetPrefs({"Comp.Paths.Map": {"Project:": project_directory_in}})
