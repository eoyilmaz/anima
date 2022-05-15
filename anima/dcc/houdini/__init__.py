# -*- coding: utf-8 -*-

import os
import hou
from anima.dcc.base import DCCBase


class Houdini(DCCBase):
    """the houdini DCC class"""

    name = "Houdini"
    extensions = {
        0: ".hiplc",
        hou.licenseCategoryType.Commercial: ".hip",
        hou.licenseCategoryType.Apprentice: ".hipnc",
        hou.licenseCategoryType.Indie: ".hiplc",
    }

    def __init__(self, name="", version=None):
        super(Houdini, self).__init__(name, version)

        from stalker import Repository

        # re initialize repo vars
        for repo in Repository.query.all():
            env_var_name = repo.env_var
            value = repo.path
            self.set_environment_variable(env_var_name, value)
            # TODO: remove the following line
            # export old env var
            self.set_environment_variable("REPO%s" % repo.id, value)

        self.name = "%s%s.%s" % (
            self.name,
            hou.applicationVersion()[0],
            hou.applicationVersion()[1],
        )

    def save_as(self, version, run_pre_publishers=True):
        """the save action for houdini DCC"""
        if not version:
            return

        from stalker import Version

        assert isinstance(version, Version)

        # get the current version,
        # and store it as the parent of the new version
        current_version = self.get_current_version()

        # initialize path variables by using update_paths()
        version.update_paths()

        # set the extension to hip
        version.extension = self.extensions[hou.licenseCategory()]

        # define that this version is created with Houdini
        version.created_with = self.name

        # create the folder if it doesn't exists
        try:
            os.makedirs(os.path.dirname(version.absolute_full_path))
        except OSError:
            # dirs exist
            pass

        # Go to the root take before doing anything
        if hou.takes.currentTake() != hou.takes.rootTake():
            root_take = hou.takes.rootTake()
            hou.takes.setCurrentTake(root_take)

        # houdini uses / instead of \ under windows
        # lets fix it

        # set the environment variables
        self.set_environment_variables(version)

        # update qLib Shot node
        self.update_shot_node(version)

        # set the render file name
        self.set_render_filename(version)

        # set the fps
        from stalker import Shot

        shot = version.task.parent
        if version and isinstance(shot, Shot):
            # set to shot.fps if this is a shot related scene
            self.set_fps(shot.fps)

            # also set frame range if this is the first version
            # if version.version_number == 1:
            self.set_frame_range(shot.cut_in, shot.cut_out)
        else:
            # set to project fps
            self.set_fps(version.task.project.fps)

        # update flipbook settings
        self.update_flipbook_settings()

        # houdini accepts only strings as file name, no unicode support as I
        # see
        hou.hipFile.save(file_name=str(version.absolute_full_path))

        # set the environment variables again
        self.set_environment_variables(version)

        # append it to the recent file list
        self.append_to_recent_files(version.absolute_full_path)

        # update the parent info
        if current_version:
            version.parent = current_version

            # update database with new version info
            from stalker.db.session import DBSession

            DBSession.commit()

        # create a local copy
        self.create_local_copy(version)

        return True

    def open(
        self,
        version,
        force=False,
        representation=None,
        reference_depth=0,
        skip_update_check=False,
    ):
        """the open action for houdini DCC"""
        if not version:
            return

        if hou.hipFile.hasUnsavedChanges() and not force:
            raise RuntimeError

        hou.hipFile.load(
            file_name=str(version.absolute_full_path), suppress_save_prompt=True
        )

        # set the environment variables
        self.set_environment_variables(version)

        # append it to the recent file list
        self.append_to_recent_files(version.absolute_full_path)

        # update flipbook settings
        self.update_flipbook_settings()

        from anima.dcc import empty_reference_resolution

        return empty_reference_resolution()

    def import_(self, version, use_namespace=True):
        """the import action for houdini DCC"""
        hou.hipFile.merge(str(version.absolute_full_path))
        return True

    def get_current_version(self):
        """Returns the currently opened Version instance"""
        version = None
        full_path = hou.hipFile.name()
        if full_path != "untitled.hip":
            version = self.get_version_from_full_path(full_path)
        return version

    def get_last_version(self):
        """gets the file name from houdini DCC"""
        version = self.get_current_version()

        if version is None:
            # read the recent file list
            version = self.get_version_from_recent_files()

        # if version is None:
        #    # get the latest possible version instance by using the project path

        return version

    def set_environment_variables(self, version):
        """sets the environment variables according to the given Version
        instance
        """
        if not version:
            return

        # set the $JOB variable to the parent of version.full_path
        from anima import logger

        logger.debug("version: %s" % version)
        logger.debug("version.path: %s" % version.absolute_path)
        logger.debug("version.filename: %s" % version.filename)
        logger.debug("version.full_path: %s" % version.absolute_full_path)
        logger.debug(
            "version.full_path (calculated): %s"
            % os.path.join(version.absolute_full_path, version.filename).replace(
                "\\", "/"
            )
        )
        job = str(version.absolute_path)
        hip = job
        hip_name = os.path.splitext(os.path.basename(str(version.absolute_full_path)))[
            0
        ]

        logger.debug("job     : %s" % job)
        logger.debug("hip     : %s" % hip)
        logger.debug("hipName : %s" % hip_name)

        self.set_environment_variable("JOB", job)
        self.set_environment_variable("HIP", hip)
        self.set_environment_variable("HIPNAME", hip_name)

    @classmethod
    def set_environment_variable(cls, var, value):
        """sets environment var

        :param str var: The name of the var
        :param value: The value of the variable
        """
        os.environ[var] = value
        try:
            hou.allowEnvironmentVariableToOverwriteVariable(var, True)
        except AttributeError:
            # should be Houdini 12
            hou.allowEnvironmentToOverwriteVariable(var, True)

        hscript_command = "set -g %s = '%s'" % (var, value)
        hou.hscript(str(hscript_command))

    @classmethod
    def update_flipbook_settings(cls):
        """updates the flipbook settings"""
        from anima.dcc.houdini import auxiliary

        scene_viewer = auxiliary.get_scene_viewer()
        if not scene_viewer:
            return

        fs = scene_viewer.flipbookSettings()
        flipbook_path = "$HIP/Outputs/playblast"
        fs.output("%s/$HIPNAME.$F4.jpg" % flipbook_path)

        # create the output folder
        import os

        try:
            os.makedirs(os.path.expandvars(flipbook_path))
        except OSError:
            # dir exists
            pass

    def get_recent_file_list(self):
        """returns the recent HIP files list from the houdini"""
        # use a FileHistory object
        file_history = FileHistory()

        # get the hip files list
        return file_history.get_recent_files("HIP")

    def get_frame_range(self):
        """returns the frame range of the"""
        # use the hscript commands to get the frame range
        time_info = hou.hscript("tset")[0].split("\n")

        pattern = r"[-0-9\.]+"

        import re

        start_frame = int(
            hou.timeToFrame(float(re.search(pattern, time_info[2]).group(0)))
        )
        duration = int(re.search(pattern, time_info[0]).group(0))
        end_frame = start_frame + duration - 1

        return start_frame, end_frame

    def set_frame_range(self, start_frame=1, end_frame=100, adjust_frame_range=False):
        """sets the frame range"""
        # --------------------------------------------
        # set the timeline
        current_frame = hou.frame()
        if current_frame < start_frame:
            hou.setFrame(start_frame)
        elif current_frame > end_frame:
            hou.setFrame(end_frame)

        # for now use hscript, the python version is not implemented yet
        hou.hscript(
            "tset `(" + str(start_frame) + "-1)/$FPS` `" + str(end_frame) + "/$FPS`"
        )

        # --------------------------------------------
        # Set the render nodes frame ranges if any
        # get the out nodes
        # output_nodes = self.get_output_nodes()
        #
        # for output_node in output_nodes:
        #     try:
        #         output_node.setParms(
        #             {'trange': 0, 'f1': start_frame, 'f2': end_frame, 'f3': 1}
        #         )
        #     except hou.OperationFailed:
        #         pass

    @classmethod
    def get_output_nodes(cls):
        """returns the rop nodes in the scene"""
        rop_context = hou.node("/out")

        # get the children
        out_nodes = rop_context.children()

        exclude_node_types = [
            hou.nodeType(hou.nodeTypeCategories()["Driver"], "wedge"),
            hou.nodeType(hou.nodeTypeCategories()["Driver"], "fetch"),
        ]

        # remove nodes in type in exclude_node_types list
        new_out_nodes = [
            node for node in out_nodes if node.type() not in exclude_node_types
        ]

        return new_out_nodes

    def get_fps(self):
        """returns the current fps"""
        return int(hou.fps())

    def get_shot_node(self):
        """returns or creates qLib shot node"""
        ql_shot_node_type = "qLib::shot_ql::1"
        obj_context = hou.node("/obj")
        for child in obj_context.children():
            if child.type().name() == ql_shot_node_type:
                return child

        # so we couldn't find the shot node
        # creat a new one
        try:
            shot_node = obj_context.createNode(ql_shot_node_type)
        except hou.OperationFailed:
            return
        else:
            return shot_node

    def update_shot_node(self, version):
        """sets the qLib shot node information

        :param version:
        :return:
        """
        task = version.task
        project = task.project
        shot_node = self.get_shot_node()
        if not shot_node:
            # qLib is not installed
            return

        shot_node.parm("proj").set(project.name)
        shot_node.parm("projs").set(project.code)

        from stalker import Shot

        image_format = project.image_format
        if task.parent and isinstance(task.parent, Shot):
            shot = task.parent
            shot_node.parm("frangex").set(shot.cut_in)
            shot_node.parm("frangey").set(shot.cut_out)
            image_format = shot.image_format

        shot_node.parm("shot").set(version.nice_name)
        # shot_node.parm("name_shot_node").pressButton()
        shot_node.setName("shotData")

        try:
            shot_node.parm("cam_resx").set(image_format.width)
        except hou.PermissionError:  # parameter is locked
            pass

        try:
            shot_node.parm("cam_resy").set(image_format.height)
        except hou.PermissionError:  # parameter is locked
            pass

    def set_render_filename(self, version):
        """sets the render file name"""
        # go to the Main take before doing anything
        # store the current take
        current_take = hou.takes.currentTake()
        hou.takes.setCurrentTake(hou.takes.rootTake())

        # HIPNAME is not working well with Afanasy
        # So use the scene base name again
        # output_filename = '$HIP/Outputs/renders/$OS/`$HIPNAME`_$OS.$F4.exr'
        import os

        output_filename = "$HIP/Outputs/renders/$OS/%s_$OS.$F4.exr" % (
            os.path.splitext(version.filename)[0]
        )

        shot_node = self.get_shot_node()
        output_nodes = self.get_output_nodes()
        for output_node in output_nodes:
            # get only the ifd nodes for now
            if output_node.type().name() == "ifd":
                # set the file name
                try:
                    output_node.setParms({"vm_picture": str(output_filename)})
                except hou.PermissionError:
                    # node is locked
                    pass

                # set the compression to zips (zip, single scanline)
                output_node.setParms({"vm_image_exr_compression": "zips"})

                # also create the folders
                output_file_full_path = output_node.evalParm("vm_picture")
                output_file_path = os.path.dirname(output_file_full_path)

                flat_output_file_path = output_file_path
                while "$" in flat_output_file_path:
                    flat_output_file_path = os.path.expandvars(flat_output_file_path)

                # do not create the folders
                # try:
                #     os.makedirs(flat_output_file_path)
                # except OSError:
                #     # dirs exists
                #     pass
            elif output_node.type().name() == "Redshift_ROP":
                # set the file name
                try:
                    output_node.setParms(
                        {"RS_outputFileNamePrefix": str(output_filename)}
                    )
                except hou.PermissionError:
                    # node is locked
                    pass

                try:
                    output_node.parm("RS_overrideCameraRes").set(True)
                except hou.PermissionError:  # parameter is locked
                    pass

                try:
                    output_node.parm("RS_overrideResScale").set(7)  # User specified
                except hou.PermissionError:  # parameter is locked
                    pass

                # try:
                #     output_node.parm("EnableOptiXRTOnSupportedGPUs").set(True)
                # except hou.PermissionError:  # parameter is locked
                #     pass

                # get the shot node and connect the resolution to it
                if shot_node:
                    # set the render camera
                    try:
                        output_node.parm("RS_renderCamera").setExpression(
                            'chsop("%s/shotcam")' % shot_node.path()
                        )
                    except hou.PermissionError:  # parameter is locked
                        pass

                    try:
                        output_node.parm("RS_overrideRes1").setExpression(
                            'ch("%s/cam_resx")' % shot_node.path()
                        )
                        output_node.parm("RS_overrideRes2").setExpression(
                            'ch("%s/cam_resy")' % shot_node.path()
                        )
                    except hou.PermissionError:  # parameter is locked
                        pass

                else:  # no shot node, no qlib
                    # so use the shot nodes resolution if this is a shot related node
                    # set the fps
                    from stalker import Shot

                    shot = version.task.parent
                    project = version.task.project
                    imf = project.image_format
                    if version and isinstance(shot, Shot):
                        imf = shot.image_format

                    try:
                        output_node.parm("RS_overrideRes1").set(imf.width)
                        output_node.parm("RS_overrideRes2").set(imf.height)
                    except hou.PermissionError:  # parameter is locked
                        pass

                # also set any AOVs to use the same output name prefixed with
                # the AOV name

                # get AOVs
                aov_count = output_node.evalParm("RS_aov")
                if aov_count:
                    for i in range(aov_count):
                        aov_index = i + 1
                        aov_custom_prefix_parm = "RS_aovCustomPrefix_%s" % aov_index
                        aov_custom_suffix_parm = "RS_aovSuffix_%s" % aov_index
                        try:
                            output_node.parm(aov_custom_prefix_parm).set(
                                '`strreplace(chs("RS_outputFileNamePrefix"), '
                                '".$F4.exr", "_" + chs("%s") + ".$F4.exr")`'
                                % aov_custom_suffix_parm
                            )
                        except hou.PermissionError:
                            # node is locked
                            pass

                # # set the compression to zips (zip, single scanline)
                # output_node.setParms({"vm_image_exr_compression": "zips"})

                # also create the folders
                output_file_full_path = output_node.evalParm("RS_outputFileNamePrefix")
                output_file_path = os.path.dirname(output_file_full_path)

                flat_output_file_path = output_file_path
                while "$" in flat_output_file_path:
                    flat_output_file_path = os.path.expandvars(flat_output_file_path)

                # enable skip rendered images
                output_node.parm("RS_outputSkipRendered").set(1)

                # create the folders if the node is not bypassed
                if not output_node.isBypassed():
                    try:
                        os.makedirs(flat_output_file_path)
                    except OSError:
                        # dirs exists
                        pass

        # restore the current take
        hou.takes.setCurrentTake(current_take)

    def set_fps(self, fps=25):
        """sets the time unit of the DCC"""
        if fps <= 0:
            return

        # keep the current start and end time of the time range
        start_frame, end_frame = self.get_frame_range()
        hou.setFps(fps)

        self.set_frame_range(start_frame, end_frame)

    def replace_paths(self):
        """replaces all the paths in all the path related nodes"""
        # get all the nodes and their childs and
        # try to get string and file path parameters
        # and replace them if they contain absolute paths
        pass

    @classmethod
    def get_aovs(cls, output_node):
        """Returns the AOVs from the the given RedShift ROP

        :param output_node: RedShift ROP node
        :return:
        """
        aovs = []
        return aovs


class FileHistory(object):
    """A Houdini recent file history parser

    Holds the data in a dictionary, where the keys are the file types and the
    values are string list of recent file paths of that type
    """

    def __init__(self):
        self._history_file_name = "file.history"
        self._history_file_path = ""

        # if os.name == 'nt':
        # under windows the HIH is useless
        # interpret the HIH from POSE environment variable
        self._history_file_path = os.path.dirname(os.getenv("POSE"))
        # else:
        #     self._history_file_path = os.getenv('HIH')

        self._history_file_full_path = os.path.join(
            self._history_file_path, self._history_file_name
        )

        self._buffer = []

        self._history = dict()

        self._read()
        self._parse()

    def _read(self):
        """reads the history file to a buffer"""
        try:
            history_file = open(self._history_file_full_path)
        except IOError:
            self._buffer = []
            return

        self._buffer = history_file.readlines()

        # strip all the lines
        self._buffer = [line.strip() for line in self._buffer]

        history_file.close()

    def _parse(self):
        """parses the data in self._buffer"""
        self._history = dict()
        buffer_list = self._buffer
        key_name = ""
        path_list = []
        len_buffer = len(buffer_list)

        for i in range(len_buffer):
            # try to find a '{'
            if buffer_list[i] == "{":
                # create a key with the previous line
                key_name = buffer_list[i - 1]
                path_list = []

                # starting from the next line
                for j in range(i + 1, len_buffer):

                    # add all the lines to the path_list until you find a '}'
                    current_element = buffer_list[j]
                    if current_element != "}":
                        path_list.append(current_element)
                    else:
                        # set i to j+1 and let it continue
                        i = j + 1
                        break
                    # append the key and data to the dictionary
                self._history[key_name] = path_list

    def get_recent_files(self, type_name=""):
        """returns the file list of the given file type"""
        if type_name == "" or type_name is None:
            return []
        else:
            return self._history.get(type_name, [])
