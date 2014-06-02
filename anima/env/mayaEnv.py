# -*- coding: utf-8 -*-
# Copyright (c) 2012-2014, Anima Istanbul
#
# This module is part of anima-tools and is released under the BSD 2
# License: http://www.opensource.org/licenses/BSD-2-Clause

import os
import re
import shutil
import logging

import pymel.core
import maya.cmds

from pymel.core.uitypes import CheckBox, TextField
from pymel.core.general import Attribute
from pymel.core.system import FileReference

from anima.extension import extends

from anima import utils
from anima.exc import PublishError
from anima.env import empty_reference_resolution
from anima.env.base import EnvironmentBase
from anima.ui.progress_dialog import ProgressDialogManager
from anima import publish

# empty publishers first
publish.publishers = {}

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)


MAX_NODE_DISPLAY = 80


class MayaExtension(object):
    """Extension to PyMel classes
    """

    @extends(Attribute)
    @property
    def next_available(self):
        """returns the next available attr in a multi attr

        :return: The available index as an attribute
        """
        try:
            indices = self.getArrayIndices()
        except TypeError:
            return self

        available_index = 0

        try:
            for i in xrange(max(indices) + 2):
                if not self[i].connections():
                    available_index = i
                    break
        except ValueError:
            available_index = 0

        return self[available_index]

    @extends(CheckBox)
    def value(self, value=None):
        """returns or set the check box value
        """
        from pymel.core import checkBox
        if value is not None:
            # set the value
            checkBox(self, e=1, v=value)
        else:
            # get the value
            return checkBox(self, q=1, v=1)

    @extends(TextField)
    def text(self, value=None):
        """returns or sets the text field value
        """
        from pymel.core import textField
        if value is not None:
            # set the value
            textField(self, e=1, tx=value)
        else:
            # get the value
            return textField(self, q=1, tx=1)


class ReferenceExtension(object):
    """Extensions to Maya Reference node.

    Manages the Referenced ASS files in the current scene.

    This class helps converting references to ASS files and vice versa.
    """

    @extends(FileReference)
    def has_ass(self):
        """Checks if the reference has a related ASS take

        :return: bool
        """
        # create a temp maya env
        mEnv = Maya()
        ver = mEnv.get_version_from_full_path(self.path)

        if ver is None:
            return

        from stalker import Version
        # try to get the version with {{take}}_ASS
        task = ver.task
        ass_take = '%s_ASS' % ver.take_name

        # do a quick query
        ass_version = Version.query\
            .filter(Version.task == task)\
            .filter(Version.take_name == ass_take).first()

        if ass_version is None:
            return False

        latest_ass_version = ass_version.latest_published_version
        if latest_ass_version is None:
            return False

        return True

    @extends(FileReference)
    def is_ass(self):
        """Checks if the reference is an ASS version

        :return: bool
        """
        # create a temp maya env
        mEnv = Maya()
        ver = mEnv.get_version_from_full_path(self.path)

        if ver is None:
            return

        # try to get the version with {{take}}_ASS
        if '_ASS' in ver.take_name:
            return True
        else:
            return False

    @extends(FileReference)
    def to_ass(self):
        """Loads the ass version.

        Finds the related Stalker version of this reference, and replaces the
        path of this reference with the latest ASS take of the same task and
        take.
        """
        # create a temp maya env
        mEnv = Maya()
        ver = mEnv.get_version_from_full_path(self.path)

        if ver is None:
            return

        from stalker import Version
        # try to get the version with {{take}}_ASS
        task = ver.task
        ass_take = '%s_ASS' % ver.take_name

        # do a quick query
        ass_version = Version.query\
            .filter(Version.task == task)\
            .filter(Version.take_name == ass_take).first()

        if ass_version is None:
            return

        latest_ass_version = ass_version.latest_published_version
        if latest_ass_version is None:
            return

        self.replaceWith(latest_ass_version.absolute_full_path)

    @extends(FileReference)
    def to_original(self):
        """Loads the original version
        """
        # create a temp maya env
        mEnv = Maya()
        ver = mEnv.get_version_from_full_path(self.path)

        if ver is None:
            return

        from stalker import Version
        # try to get the version with {{take}}_ASS
        task = ver.task
        if '_ASS' not in ver.take_name:
            return

        original_take = ver.take_name.replace('_ASS', '')

        # do a quick query
        original_version = Version.query\
            .filter(Version.task == task)\
            .filter(Version.take_name == original_take).first()

        if original_version is None:
            return

        latest_original_version = original_version.latest_published_version
        if latest_original_version is None:
            return

        self.replaceWith(latest_original_version.absolute_full_path)


class Maya(EnvironmentBase):
    """The maya environment class

    .. versionadded:: 0.1.7
       Shallow Reference Updates

       With version 0.1.7 all the scene references are updated *shallowly*,
       that is no new versions are going to be created as opposed to
       **Deep Reference Updates**. With **Shallow Reference Update**, all the
       references in current scene is updated in place. So if a new version of
       a Version is present, Maya will update it to that version in the current
       scene without creating new intermediate versions. This makes things much
       simple and easy to manage.

    .. deprecated::
       Deep Reference Updates

       Deep reference updates are deprecated. Use shallow reference updates.

    """

    name = "Maya%s" % str(pymel.versions.current())[0:4]

    time_to_fps = {
        u'sec': 1,
        u'2fps': 2,
        u'3fps': 3,
        u'4fps': 4,
        u'5fps': 5,
        u'6fps': 6,
        u'8fps': 8,
        u'10fps': 10,
        u'12fps': 12,
        u'game': 15,
        u'16fps': 16,
        u'20fps': 20,
        u'film': 24,
        u'pal': 25,
        u'ntsc': 30,
        u'40fps': 40,
        u'show': 48,
        u'palf': 50,
        u'ntscf': 60,
        u'75fps': 75,
        u'80fps': 80,
        u'100fps': 100,
        u'120fps': 120,
        u'125fps': 125,
        u'150fps': 150,
        u'200fps': 200,
        u'240fps': 240,
        u'250fps': 250,
        u'300fps': 300,
        u'375fps': 375,
        u'400fps': 400,
        u'500fps': 500,
        u'600fps': 600,
        u'750fps': 750,
        u'millisec': 1000,
        u'1200fps': 1200,
        u'1500fps': 1500,
        u'2000fps': 2000,
        u'3000fps': 3000,
        u'6000fps': 6000,
    }

    maya_workspace_file_content = """
workspace -fr "3dPaintTextures" ".mayaFiles/sourceimages/3dPaintTextures/";
workspace -fr "Adobe(R) Illustrator(R)" ".mayaFiles/data/";
workspace -fr "aliasWire" ".mayaFiles/data/";
workspace -fr "animImport" ".mayaFiles/data/";
workspace -fr "animExport" ".mayaFiles/data/";
workspace -fr "audio" ".mayaFiles/sound/";
workspace -fr "autoSave" ".mayaFiles/autosave/";
workspace -fr "clips" ".mayaFiles/clips/";
workspace -fr "DAE_FBX" ".mayaFiles/data/";
workspace -fr "DAE_FBX export" ".mayaFiles/data/";
workspace -fr "depth" ".mayaFiles/renderData/depth/";
workspace -fr "diskCache" ".mayaFiles/cache/";
workspace -fr "DXF" ".mayaFiles/data/";
workspace -fr "DXF export" ".mayaFiles/data/";
workspace -fr "DXF_FBX" ".mayaFiles/data/";
workspace -fr "DXF_FBX export" ".mayaFiles/data/";
workspace -fr "eps" ".mayaFiles/data/";
workspace -fr "EPS" ".mayaFiles/data/";
workspace -fr "FBX" ".mayaFiles/data/";
workspace -fr "FBX export" ".mayaFiles/data/";
workspace -fr "fluidCache" ".mayaFiles/cache/fluid/";
workspace -fr "furAttrMap" ".mayaFiles/renderData/fur/furAttrMap/";
workspace -fr "furEqualMap" ".mayaFiles/renderData/fur/furEqualMap/";
workspace -fr "furFiles" ".mayaFiles/renderData/fur/furFiles/";
workspace -fr "furImages" ".mayaFiles/renderData/fur/furImages/";
workspace -fr "furShadowMap" ".mayaFiles/renderData/fur/furShadowMap/";
workspace -fr "IGES" ".mayaFiles/data/";
workspace -fr "IGESexport" ".mayaFiles/data/";
workspace -fr "illustrator" ".mayaFiles/data/";
workspace -fr "image" ".mayaFiles/images/";
workspace -fr "images" ".mayaFiles/images/";
workspace -fr "iprImages" ".mayaFiles/renderData/iprImages/";
workspace -fr "lights" ".mayaFiles/renderData/shaders/";
workspace -fr "mayaAscii" ".mayaFiles/scenes/";
workspace -fr "mayaBinary" ".mayaFiles/scenes/";
workspace -fr "mel" ".mayaFiles/scripts/";
workspace -fr "mentalray" ".mayaFiles/renderData/mentalray/";
workspace -fr "mentalRay" ".mayaFiles/renderData/mentalray";
workspace -fr "move" ".mayaFiles/data/";
workspace -fr "movie" ".mayaFiles/movies/";
workspace -fr "OBJ" ".mayaFiles/data/";
workspace -fr "OBJexport" ".mayaFiles/data/";
workspace -fr "offlineEdit" ".mayaFiles/scenes/edits/";
workspace -fr "particles" ".mayaFiles/particles/";
workspace -fr "renderData" ".mayaFiles/renderData/";
workspace -fr "renderScenes" ".mayaFiles/scenes/";
workspace -fr "RIB" ".mayaFiles/data/";
workspace -fr "RIBexport" ".mayaFiles/data/";
workspace -fr "scene" ".mayaFiles/scenes/";
workspace -fr "scripts" ".mayaFiles/scripts/";
workspace -fr "shaders" ".mayaFiles/renderData/shaders/";
workspace -fr "sound" ".mayaFiles/sound/";
workspace -fr "sourceImages" ".mayaFiles/sourceimages/";
workspace -fr "templates" ".mayaFiles/assets/";
workspace -fr "textures" ".mayaFiles/images/";
workspace -fr "translatorData" ".mayaFiles/data/";
"""

    executable = {
        'windows': 'maya',
        'linux': 'maya',
        'osx': 'maya'
    }

    def __init__(self, extensions=None, version=None):
        #super(Maya, self).__init__(self.name, extensions, version)
        EnvironmentBase.__init__(self, self.name, extensions, version)

        self.use_progress_window = False
        if not pymel.core.general.about(batch=1):
            self.use_progress_window = True

    def save_as(self, version):
        """The save_as action for maya environment.

        It saves the given Version instance to the Version.absolute_full_path.
        """
        if version.is_published:
            # before doing anything run all publishers
            type_name = ''
            if version.task.type:
                type_name = version.task.type.name

            publish.run_publishers(type_name)

        # get the current version, and store it as the parent of the new
        # version
        current_version = self.get_current_version()

        version.update_paths()

        # set version extension to ma
        version.extension = '.ma'

        # do not save if there are local files
        self.check_external_files(version)

        # define that this version is created with Maya
        version.created_with = self.name

        project = version.task.project

        current_workspace_path = pymel.core.workspace.path

        # create a workspace file inside a folder called .maya_files
        # at the parent folder of the current version
        # workspace_path = os.path.dirname(version.absolute_path)
        workspace_path = version.absolute_path

        # if the new workspace path is not matching the with the previous one
        # update the external paths to absolute version
        logger.debug("current workspace: %s" % current_workspace_path)
        logger.debug("next workspace: %s" % workspace_path)

        if current_workspace_path != workspace_path:
            logger.warning("changing workspace detected!")
            logger.warning("converting paths to absolute, to be able to "
                           "preserve external paths")

            # replace external paths with absolute ones
            self.replace_external_paths()

        # create the workspace folders
        self.create_workspace_file(workspace_path)

        # this sets the project
        pymel.core.workspace.open(workspace_path)

        # create workspace folders
        self.create_workspace_folders(workspace_path)

        # set scene fps
        self.set_fps(project.fps)

        # set render resolution
        # if this is a shot related task set it to shots resolution
        is_shot_related_task = False
        shot = None
        from stalker import Shot

        for task in version.task.parents:
            if isinstance(task, Shot):
                is_shot_related_task = True
                shot = task
                break

        if is_shot_related_task:
            self.set_resolution(shot.image_format.width,
                                shot.image_format.height,
                                shot.image_format.pixel_aspect)
            # set the render range if it is the first version
            if version.version_number == 1:
                self.set_frame_range(shot.cut_in, shot.cut_out)
        else:
            if version.version_number == 1:
                self.set_resolution(project.image_format.width,
                                    project.image_format.height,
                                    project.image_format.pixel_aspect)

        # set the render file name and version
        self.set_render_filename(version)

        # set sequence manager related data
        self.set_sequence_manager_data(version)

        # set the playblast file name
        self.set_playblast_file_name(version)

        # create the folder if it doesn't exists
        utils.createFolder(version.absolute_path)

        # delete the unknown nodes
        unknown_nodes = pymel.core.ls(type='unknown')
        # unlock each possible locked unknown nodes
        for node in unknown_nodes:
            node.unlock()
        pymel.core.delete(unknown_nodes)

        # set the file paths for external resources
        self.replace_external_paths()

        # save the file
        pymel.core.saveAs(
            version.absolute_full_path,
            type='mayaAscii'
        )

        # update the parent info
        if version != current_version:  # prevent CircularDependencyError
            version.parent = current_version

        # update the reference list
        # IMPORTANT: without this, the update workflow is not able to do
        # updates correctly, so do not disable this
        self.update_version_inputs()

        # append it to the recent file list
        self.append_to_recent_files(
            version.absolute_full_path
        )

        from stalker import db
        db.DBSession.add(version)
        db.DBSession.commit()

        return True

    def export_as(self, version):
        """the export action for maya environment
        """
        # check if there is something selected
        if len(pymel.core.ls(sl=True)) < 1:
            raise RuntimeError("There is nothing selected to export")

        # do not save if there are local files
        self.check_external_files(version)

        # set the extension to ma by default
        version.update_paths()
        version.extension = '.ma'
        version.created_with = self.name

        # create the folder if it doesn't exists
        utils.createFolder(version.absolute_path)

        # workspace_path = os.path.dirname(version.absolute_path)
        workspace_path = version.absolute_path

        self.create_workspace_file(workspace_path)
        self.create_workspace_folders(workspace_path)

        # export the file
        pymel.core.exportSelected(version.absolute_full_path, type='mayaAscii')

        # save the version to database
        from stalker import db
        db.DBSession.add(version)
        db.DBSession.commit()

        return True

    def open(self, version, force=False):
        """The open action for Maya environment.

        Opens the given Version file, sets the workspace etc.

        Returns a tuple of Bool and a Dictionary. The Bool value shows if
        everything went alright and the scene is opened without any problem.
        The Dictionary is called the Reference Resolution Dictionary, and has
        three keys ['leave', 'update', 'create'] and each of the keys is
        related with a list of Version instances. These Version instances are
        gathered from all the references in the opened scene no matter how
        deeply they've been referenced. So passing this dictionary to
        :meth:`.update_verions` will update or create new versions as
        necessary. You can also modify this dictionary before passing it to
        :meth:`.update_verions`, so only desired version instances are updated
        or a new version is created for them.

        :returns: (Bool, Dictionary)
        """
        # store current workspace path
        previous_workspace_path = pymel.core.workspace.path

        # set the project
        # new_workspace = os.path.dirname(version.absolute_path)
        new_workspace = version.absolute_path

        pymel.core.workspace.open(new_workspace)

        # check for unsaved changes
        logger.info("opening file: %s" % version.absolute_full_path)

        try:
            pymel.core.openFile(
                version.absolute_full_path,
                f=force,
                #loadReferenceDepth='none'
            )
        except RuntimeError as e:
            # restore the previous workspace
            pymel.core.workspace.open(previous_workspace_path)

            # raise the RuntimeError again
            # for the interface
            raise e

        # set the playblast folder
        self.set_playblast_file_name(version)

        # set sequence manager related data
        self.set_sequence_manager_data(version)

        self.append_to_recent_files(version.absolute_full_path)

        # replace_external_paths
        self.replace_external_paths()

        # check the referenced versions for any possible updates
        return self.check_referenced_versions()

    def import_(self, version, use_namespace=True):
        """Imports the content of the given Version instance to the current
        scene.

        :param version: The desired
          :class:`~stalker.models.version.Version` to be imported
        """
        if use_namespace:
            namespace = os.path.basename(version.filename)
            pymel.core.importFile(
                version.absolute_full_path,
                namespace=namespace
            )
        else:
            pymel.core.importFile(
                version.absolute_full_path,
                defaultNamespace=True
            )
        return True

    def reference(self, version, use_namespace=True):
        """References the given Version instance to the current Maya scene.

        :param version: The desired
          :class:`~stalker.models.version.Version` instance to be
          referenced.
        :return: :class:`~pymel.core.system.FileReference`
        """
        # use the file name without extension as the namespace
        namespace = os.path.basename(version.nice_name)

        if use_namespace:
            ref = pymel.core.createReference(
                version.absolute_full_path,
                gl=True,
                namespace=namespace,
                options='v=0'
            )
        else:
            ref = pymel.core.createReference(
                version.absolute_full_path,
                gl=True,
                defaultNamespace=True,  # this is not "no namespace", but safe
                options='v=0'
            )

        # replace external paths
        self.replace_external_paths()

        # set the reference state to loaded
        if not ref.isLoaded():
            ref.load()

        # append the referenced version to the current versions references
        # attribute
        current_version = self.get_current_version()
        if current_version:
            current_version.inputs.append(version)
            from stalker import db
            db.DBSession.commit()

        # also update version.inputs for the referenced input
        self.update_version_inputs(ref)

        return ref

    def get_version_from_workspace(self):
        """Tries to find a version from the current workspace path
        """
        logger.debug("trying to get the version from workspace")

        # get the workspace path
        workspace_path = pymel.core.workspace.path
        logger.debug("workspace_path: %s" % workspace_path)

        versions = self.get_versions_from_path(workspace_path)
        version = None

        if len(versions):
            version = versions[0]

        logger.debug("version from workspace is: %s" % version)
        return version

    def get_current_version(self):
        """Finds the Version instance from the current Maya session.

        If it can't find any then returns None.

        :return: :class:`~stalker.models.version.Version`
        """
        version = None

        # pymel.core.env.sceneName() always uses "/"
        full_path = pymel.core.env.sceneName()
        logger.debug('full_path : %s' % full_path)
        # try to get it from the current open scene
        if full_path != '':
            logger.debug("trying to get the version from current file")
            version = self.get_version_from_full_path(full_path)
            logger.debug("version from current file: %s" % version)

        return version

    def get_version_from_recent_files(self):
        """It will try to create a
        :class:`~stalker.models.version.Version` instance by looking at
        the recent files list.

        It will return None if it can not find one.

        :return: :class:`~stalker.models.version.Version`
        """
        version = None

        logger.debug("trying to get the version from recent file list")
        # read the fileName from recent files list
        # try to get the a valid asset file from starting the last recent file

        try:
            recent_files = pymel.core.optionVar['RecentFilesList']
        except KeyError:
            logger.debug("no recent files")
            recent_files = None

        if recent_files is not None:
            for i in range(len(recent_files) - 1, -1, -1):
                version = self.get_version_from_full_path(recent_files[i])
                if version is not None:
                    break

            logger.debug("version from recent files is: %s" % version)

        return version

    def get_last_version(self):
        """Returns the last opened or the current Version instance from the
        environment.

        * It first looks at the current open file full path and tries to match
          it with a Version instance.
        * Then searches for the recent files list.
        * Still not able to find any Version instances, will return the version
          instance with the highest id which has the current workspace path in
          its path
        * Still not able to find any Version instances returns None

        :returns: :class:`~stalker.models.version.Version` instance or
            None
        """
        version = self.get_current_version()

        # read the recent file list
        if version is None:
            version = self.get_version_from_recent_files()

        # get the latest possible Version instance by using the workspace path
        if version is None:
            version = self.get_version_from_workspace()

        return version

    def set_sequence_manager_data(self, version):
        """sets the sequenceManager1 node attributes including the version
        number.

        :param version: :class:`~stalker.models.version.Version`
        """
        from anima import previs  # to extend sequenceManager
        sm = pymel.core.ls('sequenceManager1')[0]
        if sm is not None:
            sm.get_shot_name_template()
            sm.set_version('v%03d' % version.version_number)

            for seq in sm.sequences.get():
                seq.get_sequence_name()

    def set_render_filename(self, version):
        """sets the render file name
        """
        # assert isinstance(version, Version)
        render_output_folder = os.path.join(
            version.absolute_path,
            'Outputs'
        ).replace("\\", "/")

        # image folder from the workspace.mel
        image_folder_from_ws = pymel.core.workspace.fileRules['images']
        image_folder_from_ws_full_path = os.path.join(
            version.absolute_path,
            image_folder_from_ws
        ).replace("\\", "/")

        version_sig_name = self.get_significant_name(version)

        render_file_full_path = \
            '%(render_output_folder)s/<RenderLayer>/%(version_sig_name)s_' \
            '<RenderLayer>_<RenderPass>' % {
                'render_output_folder': render_output_folder,
                'version_sig_name': version_sig_name
            }

        # convert the render_file_full_path to a relative path to the
        # imageFolderFromWS_full_path
        render_file_rel_path = utils.relpath(
            image_folder_from_ws_full_path,
            render_file_full_path,
            sep="/"
        )

        if self.has_stereo_camera():
            # just add the <Camera> template variable to the file name
            render_file_rel_path += "_<Camera>"

        # SHOTS/ToonShading/TestTransition/incidence/ToonShading_TestTransition_incidence_MasterPass_v050.####.iff

        # defaultRenderGlobals
        dRG = pymel.core.PyNode('defaultRenderGlobals')
        dRG.setAttr('imageFilePrefix', render_file_rel_path)
        dRG.setAttr('renderVersion', "v%03d" % version.version_number)
        dRG.setAttr('animation', 1)
        dRG.setAttr('outFormatControl', 0)
        dRG.setAttr('extensionPadding', 4)
        dRG.setAttr('imageFormat', 7)  # force the format to iff
        dRG.setAttr('pff', 1)

        self.set_output_file_format()

    @classmethod
    def set_output_file_format(cls):
        """sets the output file format
        """
        dRG = pymel.core.PyNode('defaultRenderGlobals')

        # check the current renderer
        current_renderer = dRG.currentRenderer.get()
        if current_renderer == 'mentalRay':
            # set the render output to OpenEXR with zip compression
            dRG.imageFormat.set(51)
            dRG.imfkey.set('exr')
            # check the maya version and set it if maya version is equal or
            # greater than 2012
            try:
                if pymel.versions.current() >= pymel.versions.v2012:
                    try:
                        mrG = pymel.core.PyNode("mentalrayGlobals")
                    except pymel.core.general.MayaNodeError:
                        # the renderer is set to mentalray but it is not loaded
                        # so there is no mentalrayGlobals
                        # create them

                        # dirty little maya tricks
                        pymel.core.mel.miCreateDefaultNodes()

                        # get it again
                        mrG = pymel.core.PyNode("mentalrayGlobals")

                    mrG.imageCompression.set(4)
            except AttributeError, pymel.core.general.MayaNodeError:
                pass

            # if the renderer is not registered this causes a _objectError
            # and the frame buffer to 16bit half
            try:
                miDF = pymel.core.PyNode('miDefaultFramebuffer')
                miDF.datatype.set(16)
            except TypeError, pymel.core.general.MayaNodeError:
                # just don't do anything
                pass
        elif current_renderer == 'arnold':
            dRG.imageFormat.set(51)  # exr
            dAD = pymel.core.PyNode('defaultArnoldDriver')
            dAD.exrCompression.set(2)  # zips
            dAD.halfPrecision.set(1)  # half
            dAD.tiled.set(0)  # not tiled
            dAD.autocrop.set(1)  # will enhance file load times in Nuke

        ## check all the render layers and try to get if any of them are using
        ## mayaSoftware as the renderer, and set the render output to iff if any
        #for renderLayer in pymel.core.ls(type='renderLayer'):
            ## if the renderer is set to mayaSoftware (which is very rare)
            #if dRG.getAttr('currentRenderer') == 'mayaSoftware':

    @classmethod
    def set_playblast_file_name(cls, version):
        """sets the playblast file name
        """
        playblast_path = os.path.join(
            version.absolute_path,
            'Outputs', "Playblast"
        ).replace('\\', '/')

        # use project name and sequence name if available
        # playblast_filename = version.task.project.code + "_" + \
        #                      os.path.splitext(version.filename)[0]

        playblast_filename = cls.get_significant_name(version)

        playblast_full_path = os.path.join(
            playblast_path,
            playblast_filename
        ).replace('\\', '/')

        # create the folder
        utils.mkdir(playblast_path)
        pymel.core.optionVar['playblastFile'] = playblast_full_path

    @classmethod
    def set_resolution(cls, width, height, pixel_aspect=1.0):
        """Sets the resolution of the current scene

        :param width: The width of the output image
        :param height: The height of the output image
        :param pixel_aspect: The pixel aspect ratio
        """
        dRes = pymel.core.PyNode("defaultResolution")
        dRes.width.set(width)
        dRes.height.set(height)
        dRes.pixelAspect.set(pixel_aspect)
        # also set the device aspect
        dRes.deviceAspectRatio.set(float(width) / float(height))

    @classmethod
    def set_project(cls, version):
        """Sets the project to the given version.

        The Maya version uses :class:`~stalker.models.version.Version`
        instances to set the project. Because the Maya workspace is related to
        the the Asset or Shot which can be derived from the Version instance
        very easily.
        """
        pymel.core.workspace.open(version.absolute_path)
        # set the current timeUnit to match with the environments
        cls.set_fps(version.task.project.fps)

    @classmethod
    def append_to_recent_files(cls, path):
        """appends the given path to the recent files list
        """
        # add the file to the recent file list
        try:
            recent_files = pymel.core.optionVar['RecentFilesList']
        except KeyError:
            # there is no recent files list so create one
            # normally it is Maya's job
            # but somehow it is not working for new installations
            recent_files = pymel.core.OptionVarList([], 'RecentFilesList')

        #assert(isinstance(recentFiles,pymel.core.OptionVarList))
        recent_files.appendVar(path)

    @classmethod
    def is_in_repo(cls, path):
        """checks if the given path is in repository
        :param path: the path which wanted to be checked
        :return: True or False
        """
        assert isinstance(path, (str, unicode))
        path = os.path.expandvars(path)
        repo = cls.find_repo(path)
        return repo is not None

    @classmethod
    def move_to_local(cls, version, file_path, type_name):
        """moves the files to the local "external" path
        """
        local_path = version.absolute_path + '/external_files/' + type_name
        filename = os.path.basename(file_path)
        destination_full_path = os.path.join(local_path, filename)
        # create the dirs
        try:
            os.makedirs(local_path)
        except OSError:  # dir exists
            pass

        if not os.path.exists(destination_full_path):
            # move the file
            logger.debug('moving to: %s' % destination_full_path)
            try:
                shutil.copy(file_path, local_path)
            except IOError:  # no write permission
                return None
            return destination_full_path
        else:  # file already exists do not overwrite
            logger.debug('file already exists, not moving')
            return None

    def check_external_files(self, version):
        """checks for external files in the current scene and raises
        RuntimeError if there are local files in the current scene, used as:

            - File Textures
            - Mentalray Textures
            - ImagePlanes
            - IBL nodes
            - References
        """
        external_nodes = []

        # check for file textures
        for file_texture in pymel.core.ls(type=pymel.core.nt.File):
            path = file_texture.attr('fileTextureName').get()
            logger.debug('checking path: %s' % path)
            if path is not None \
               and os.path.isabs(path) \
               and not self.is_in_repo(path):
                logger.debug('is not in repo: %s' % path)
                new_path = self.move_to_local(version, path, 'Textures')
                if not new_path:
                    # it was not copied
                    external_nodes.append(file_texture)
                else:
                    # successfully copied
                    # update the path
                    logger.debug('updating texture path to: %s' % new_path)
                    file_texture.attr('fileTextureName').set(new_path)

        # check for arnold textures
        for arnold_texture in pymel.core.ls(type='aiImage'):
            path = arnold_texture.attr('filename').get()
            logger.debug('checking path: %s' % path)
            if path is not None \
               and os.path.isabs(path) \
               and not self.is_in_repo(path):
                logger.debug('is not in repo: %s' % path)
                new_path = self.move_to_local(version, path, 'Textures')
                if not new_path:
                    # it was not copied
                    external_nodes.append(arnold_texture)
                else:
                    # successfully copied
                    # update the path
                    logger.debug('updating texture path to: %s' % new_path)
                    arnold_texture.attr('filename').set(new_path)

        # check for mentalray textures
        try:
            for mr_texture in pymel.core.ls(type=pymel.core.nt.MentalrayTexture):
                path = mr_texture.attr('fileTextureName').get()
                logger.debug("path of %s: %s" % (mr_texture, path))
                if path is not None \
                   and os.path.isabs(path) \
                   and not self.is_in_repo(path):
                    logger.debug('is not in repo: %s' % path)
                    new_path = self.move_to_local(version, path, 'Textures')
                    if not new_path:
                        # it was not copied
                        external_nodes.append(mr_texture)
                    else:
                        # successfully copied
                        # update the path
                        logger.debug('updating texture path to: %s' % new_path)
                        mr_texture.attr('fileTextureName').set(new_path)
        except AttributeError:  # MentalRay not loaded
            pass

        # check for ImagePlanes
        for image_plane in pymel.core.ls(type=pymel.core.nt.ImagePlane):
            path = image_plane.attr('imageName').get()
            if path is not None \
               and os.path.isabs(path) \
               and not self.is_in_repo(path):
                logger.debug('is not in repo: %s' % path)
                new_path = self.move_to_local(version, path, 'ImagePlanes')
                if not new_path:
                    # it was not copied
                    external_nodes.append(image_plane)
                else:
                    # successfully copied
                    # update the path
                    logger.debug('updating image plane path to: %s' % new_path)
                    image_plane.attr('imageName').set(new_path)

        # check for IBL nodes
        try:
            for ibl in pymel.core.ls(type=pymel.core.nt.MentalrayIblShape):
                path = ibl.attr('texture').get()
                if path is not None \
                   and os.path.isabs(path) \
                   and not self.is_in_repo(path):
                    logger.debug('is not in repo: %s' % path)
                    new_path = self.move_to_local(version, path, 'IBL')
                    if not new_path:
                        # it was not copied
                        external_nodes.append(ibl)
                    else:
                        # successfully copied
                        # update the path
                        logger.debug('updating ibl path to: %s' % new_path)
                        ibl.attr('texture').set(new_path)
        except AttributeError:  # mentalray not loaded
            pass

        if external_nodes:
            pymel.core.select(external_nodes)
            raise RuntimeError(
                'There are external references in your scene!!!\n\n'
                'The problematic nodes are:\n\n' +
                ", ".join(map(lambda x: x.name(), external_nodes)) +
                '\n\nThese nodes are added in to your selection list,\n'
                'Please correct them!\n\n'
                'YOUR FILE IS NOT GOING TO BE SAVED!!!'
            )

    def get_referenced_versions(self, parent_ref=None):
        """Returns the versions those been referenced to the current scene.

        :param parent_ref: The parent ref to start from. So the final list will
          be gathered from the references that are sub references of this
          parent ref.

        :returns: A list of Version instances
        """

        # get all the references
        references = pymel.core.listReferences(parent_ref)

        # sort them according to path
        # to make same paths together
        refs = sorted(references, key=lambda x: x.path)

        # lets use a progress window
        caller = None
        if len(references):
            pm = ProgressDialogManager()
            caller = pm.register(len(references), 'Maya.get_referenced_versions()')

        prev_path = ''
        versions = []
        for ref in refs:
            path = ref.path
            if path != prev_path:
                # try to get a version with the given path
                version = self.get_version_from_full_path(path)
                if version:
                    versions.append(version)
                    prev_path = path
            if caller is not None:
                caller.step()

        return versions

    def update_version_inputs(self, parent_ref=None):
        """updates the references list of the current version

        :param parent_ref: the parent ref, if given will override the given
          version argument and a Version instance will be get from the given
          parent_ref.path.
        """
        if not parent_ref:
            version = self.get_current_version()
        else:
            version = self.get_version_from_full_path(parent_ref.path)

        if version:
            # update the reference list
            referenced_versions = self.get_referenced_versions(parent_ref)
            version.inputs = referenced_versions
            from stalker import db
            db.DBSession.commit()

    def update_first_level_versions(self, reference_resolution):
        """Updates the versions to the latest version.

        :param reference_resolution: A dictionary with keys 'leave', 'update'
          and 'create' with a list of :class:`~stalker.models.version.Version`
          instances in each of them. Only 'update' key is used and if the
          Version instance is in the 'update' list the reference is updated to
          the latest version.
        """
        # list only first level references
        references = sorted(pymel.core.listReferences(), key=lambda x: x.path)

        # optimize it:
        #   do only one search for each references to the same version
        previous_ref_path = None
        previous_full_path = None

        updated_references = False

        for reference in references:
            path = reference.path
            if path == previous_ref_path:
                full_path = previous_full_path
            else:
                version = self.get_version_from_full_path(path)
                if version in reference_resolution['update']:
                    latest_published_version = version.latest_published_version
                    full_path = latest_published_version.absolute_full_path
                else:
                    full_path = None

            if full_path:
                reference.replaceWith(full_path)
                updated_references = True

        return updated_references

    def get_frame_range(self):
        """returns the current playback frame range
        """
        start_frame = int(pymel.core.playbackOptions(q=True, ast=True))
        end_frame = int(pymel.core.playbackOptions(q=True, aet=True))
        return start_frame, end_frame

    def set_frame_range(self, start_frame=1, end_frame=100,
                        adjust_frame_range=False):
        """sets the start and end frame range
        """
        # set it in the playback
        pymel.core.playbackOptions(ast=start_frame, aet=end_frame)

        if adjust_frame_range:
            pymel.core.playbackOptions(min=start_frame, max=end_frame)

        # set in the render range
        dRG = pymel.core.PyNode('defaultRenderGlobals')
        dRG.setAttr('startFrame', start_frame)
        dRG.setAttr('endFrame', end_frame)

    def get_fps(self):
        """returns the fps of the environment
        """
        # return directly from maya, it uses the same format
        return self.time_to_fps[pymel.core.currentUnit(q=1, t=1)]

    @classmethod
    def set_fps(cls, fps=25):
        """sets the fps of the environment
        """
        # get the current time, current playback min and max (because maya
        # changes them, try to restore the limits)
        current_time = pymel.core.currentTime(q=1)
        pMin = pymel.core.playbackOptions(q=1, min=1)
        pMax = pymel.core.playbackOptions(q=1, max=1)
        pAst = pymel.core.playbackOptions(q=1, ast=1)
        pAet = pymel.core.playbackOptions(q=1, aet=1)

        # set the time unit, do not change the keyframe times
        # use the timeUnit as it is
        time_unit = u"pal"

        # try to find a timeUnit for the given fps
        # TODO: set it to the closest one
        for key in cls.time_to_fps:
            if cls.time_to_fps[key] == fps:
                time_unit = key
                break

        pymel.core.currentUnit(t=time_unit, ua=0)
        # to be sure
        pymel.core.optionVar['workingUnitTime'] = time_unit

        # update the playback ranges
        pymel.core.currentTime(current_time)
        pymel.core.playbackOptions(ast=pAst, aet=pAet)
        pymel.core.playbackOptions(min=pMin, max=pMax)

    @classmethod
    def load_referenced_versions(cls):
        """loads all the references
        """
        # get all the references
        for reference in pymel.core.listReferences():
            reference.load()

    @classmethod
    def replace_versions(cls, source_reference, target_file):
        """replaces the source reference with the target file

        the source_reference may should be in maya reference node
        """
        # get the reference node
        base_reference_node = source_reference.refNode

        # get the base namespace before replacing the reference
        previous_namespace = \
            cls.get_full_namespace_from_node_name(source_reference.nodes()[0])

        # if the source_reference has referenced files do a dirty edit
        # by applying all the edits to the referenced node (the old way of
        # replacing references)
        sub_references = pymel.core.listReferences(
            source_reference, recursive=True
        )
        # logger.debug("subReferences count: %s" % len(subReferences))

        if len(sub_references) > 0:
            # for all subReferences get the editString and apply it to the
            # replaced file with new namespace
            all_edits = []
            for subRef in sub_references:
                all_edits += subRef.getReferenceEdits(orn=base_reference_node)

            # replace the reference
            source_reference.replaceWith(target_file)

            # try to find the new namespace
            sub_references = pymel.core.listReferences(
                source_reference, recursive=True
            )
            new_namespace = cls.get_full_namespace_from_node_name(
                sub_references[0].nodes()[0]
            )  # possible bug here, fix it later

            # replace the old namespace with the new namespace in all the edits
            all_edits = [
                edit.replace(previous_namespace + ":", new_namespace + ":")
                for edit in all_edits
            ]

            # apply all the edits
            for edit in all_edits:
                try:
                    pymel.core.mel.eval(edit)
                except pymel.core.MelError:
                    pass
        else:
            # replace the reference
            source_reference.replaceWith(target_file)

            # try to find the new namespace
            sub_references = pymel.core.listReferences(
                source_reference, recursive=True
            )
            new_namespace = cls.get_full_namespace_from_node_name(
                sub_references[0].nodes()[0]
            )  # possible bug here, fix it later

            #subReferences = source_reference.subReferences()
            #for subRefData in subReferences.iteritems():
            #    refNode = subRefData[1]
            #    newNS = \
            #      self.get_full_namespace_from_node_name(refNode.nodes()[0])

            # if the new namespace is different than the previous one
            # also change the edit targets
            if previous_namespace != new_namespace:
                # logger.debug("prevNS: %s" % previous_namespace)
                # logger.debug("newNS : %s" % newNS)

                # get the new sub references
                for subRef in pymel.core.listReferences(source_reference):
                    # for all the nodes in sub references
                    # change the edit targets with new namespace
                    for node in subRef.nodes():
                        # use the long name -- suggested by maya help
                        node_new_name = node.longName()
                        node_old_name = node_new_name.replace(
                            new_namespace + ':', previous_namespace + ':'
                        )

                        pymel.core.referenceEdit(
                            base_reference_node,
                            changeEditTarget=(node_old_name, node_new_name)
                        )
                        #pymel.core.referenceEdit(
                        #    baseRefNode,
                        #    orn=baseRefNode,
                        #    changeEditTarget=(node_old_name, node_new_name)
                        #)
                        #pymel.core.referenceEdit(
                        #     subRef,
                        #     orn=baseRefNode,
                        #     changeEditTarget=(node_old_name, node_new_name)
                        #)
                        #for aRefNode in pymel.core.ls(type='reference'):
                            #if len(aRefNode.attr('sharedReference').listConnections(s=0,d=1)) == 0: # not a shared reference
                                #pymel.core.referenceEdit(aRefNode, orn=baseRefNode, changeEditTarget=(nodeOldName, nodeNewName), scs=1, fld=1)
                                ##pymel.core.referenceEdit(aRefNode, applyFailedEdits=True)
                    #pymel.core.referenceEdit(subRef, applyFailedEdits=True)

                # apply all the failed edits again
                pymel.core.referenceEdit(base_reference_node,
                                         applyFailedEdits=True)

    @classmethod
    def get_full_namespace_from_node_name(cls, node):
        """dirty way of getting the namespace from node name
        """
        return ':'.join((node.name().split(':'))[:-1])

    @classmethod
    def has_stereo_camera(cls):
        """checks if the scene has a stereo camera setup
        returns True if any
        """
        # check if the stereoCameraRig plugin is loaded
        if pymel.core.pluginInfo('stereoCamera', q=True, l=True):
            return len(pymel.core.ls(type='stereoRigTransform')) > 0
        else:
            # return False because it is impossible without stereoCamera plugin
            # to have a stereoCamera rig
            return False

    def replace_external_paths(self, mode=0):
        """Replaces all the external paths. Because absolute mode is the
        default and only mode, the 'mode' parameter is not used.

        replaces:
          references: replaces Windows, Linux or OSX paths with native one
                      (the one that the current user has).
          files     : converts to absolute mode

        Absolute mode works best for now.

        .. note::

          The system doesn't care about the mentalrayTexture nodes because the
          lack of a good environment variable support from that node. Use
          regular maya file nodes with mib_texture_filter_lookup nodes to have
          the same sharp results.
        """
        # TODO: Also check for image planes and replace the path
        # create a repository
        workspace_path = pymel.core.workspace.path

        # *********************************************************************
        # References
        # replace reference paths with absolute path
        from stalker import Repository

        for ref in pymel.core.listReferences():
            unresolved_path = ref.unresolvedPath().replace("\\", "/")
            # keep the load state
            # load_state = ref.isLoded()
            repo = self.find_repo(unresolved_path)
            if False:
                assert isinstance(repo, Repository)
            # TODO: Please request Repository.is_native(path) from Stalker
            # Windows paths doesn't seem to be absolute under linux and osx

            if repo:
                update_path = False
                if not os.path.isabs(unresolved_path):
                    # update anyway
                    # either the path is really relative, or it is a windows
                    # path and we are under linux or osx
                    # or it is a linux or osx path and we are under windows
                    # so update it
                    update_path = True
                else:
                    # it seems the path is absolute
                    # but double check if the file path and the os is matching
                    path = unresolved_path
                    if not (path == repo.to_native_path(path)):
                        # again the path was osx and the os is linux or
                        # the path was linux and the os is osx
                        # so update it
                        update_path = True

                if update_path:
                    if repo.is_in_repo(unresolved_path):
                        # convert to absolute path
                        new_ref_path = repo.to_native_path(ref.path)

                        if new_ref_path != unresolved_path:
                            logger.info("replacing reference: %s" % ref.path)
                            logger.info("replacing with: %s" % new_ref_path)
                            ref.replaceWith(new_ref_path)

        # *********************************************************************
        # Texture Files
        # replace with absolute path
        for image_file in pymel.core.ls(type="file"):
            orig_file_texture_path = image_file.getAttr("fileTextureName")
            orig_file_texture_path = orig_file_texture_path.replace("\\", "/")

            logger.info("replacing file texture: %s" % orig_file_texture_path)

            file_texture_path = os.path.normpath(
                os.path.expandvars(
                    orig_file_texture_path
                )
            )
            file_texture_path = file_texture_path.replace("\\", "/")

            # convert to absolute
            if not os.path.isabs(file_texture_path):
                file_texture_path = os.path.join(
                    workspace_path,
                    file_texture_path
                ).replace("\\", "/")

            repo = self.find_repo(file_texture_path)

            if repo:
                # convert to absolute
                new_path = repo.to_native_path(file_texture_path)

                if new_path != orig_file_texture_path:
                    logger.info("with: %s" % new_path)
                    image_file.setAttr("fileTextureName", new_path)

    def create_workspace_file(self, path):
        """creates the workspace.mel at the given path
        """
        content = self.maya_workspace_file_content

        # check if there is a workspace.mel at the given path
        full_path = os.path.join(path, "workspace.mel").replace('\\', '/')

        if not os.path.exists(full_path):
            try:
                os.makedirs(
                    os.path.dirname(full_path)
                )
            except OSError:
                # dir exists
                pass

            with open(full_path, "w") as workspace_file:
                workspace_file.write(content)

    @classmethod
    def create_workspace_folders(cls, path):
        """creates the workspace folders

        :param path: the root of the workspace
        """
        for key in pymel.core.workspace.fileRules:
            rule_path = pymel.core.workspace.fileRules[key]
            full_path = os.path.join(path, rule_path).replace('\\', '/')
            # logger.debug(full_path)
            try:
                os.makedirs(full_path)
            except OSError:
                # dir exists
                pass

    def deep_version_inputs_update(self):
        """updates the inputs of the references of the current scene
        """
        # first update with data from first level references
        self.update_version_inputs()

        # the go to the references
        references_list = pymel.core.listReferences()

        # pm = ProgressDialogManager()
        # caller = pm.register(len(references_list),
        #                      'Maya.deep_version_inputs_update()')

        prev_ref_path = None
        while len(references_list):
            current_ref = references_list.pop(0)
            self.update_version_inputs(current_ref)
            # optimize it by only appending one instance of the same referenced
            # file
            # sort the references according to their paths so, all the
            # references of the same file will be got together
            all_refs = sorted(
                pymel.core.listReferences(current_ref),
                key=lambda x: x.path
            )
            for ref in all_refs:
                if ref.path != prev_ref_path:
                    prev_ref_path = ref.path
                    references_list.append(ref)
            # caller.step(message=prev_ref_path)
            prev_ref_path = None

        # it probably will terminate before expected, so call end_progress for
        # this caller
        # caller.end_progress()

    def check_referenced_versions(self):
        """Deeply checks all the references in the scene and returns a
        dictionary which has three keys called 'leave', 'update' and 'create'.

        Each of these keys correspond to a value of a list of
        :class:`~stalker.model.version.Version`\ s. Where the list in 'leave'
        key shows the Versions referenced (or deeply referenced) to the
        current scene which doesn't need to be changed.

        The list in 'update' key holds Versions those need to be updated to a
        newer version which are already exist.

        The list in 'create' key holds Version instance which needs to have its
        references to be updated to the never versions thus need a new version
        for them self.

        All the Versions in the list are sorted from the deepest to shallowest
        reference, so processing the list from 0th element to nth will always
        guarantee up to date info for the currently processed Version instance.

        Uses the top level references to get a Stalker Version instance and
        then tracks all the changes from these Version instances.

        :return: dictionary
        """
        pm = ProgressDialogManager()
        caller = pm.register(3, 'Maya.check_referenced_versions() prepare data')

        # deeply get which maya file is referencing which other files
        self.deep_version_inputs_update()
        caller.step()

        reference_resolution = \
            empty_reference_resolution(root=self.get_referenced_versions())
        caller.step()

        # reverse walk in DFS
        dfs_version_references = []

        version = self.get_current_version()
        for v in version.walk_inputs():
            dfs_version_references.append(v)
        caller.step()

        # pop the first element which is the current scene
        dfs_version_references.pop(0)

        caller.end_progress()

        # register a new caller
        caller = pm.register(len(dfs_version_references),
                             'Maya.check_referenced_versions()')

        # iterate back in the list
        for v in reversed(dfs_version_references):
            # check inputs first
            to_be_updated_list = []
            for ref_v in v.inputs:
                if not ref_v.is_latest_published_version():
                    to_be_updated_list.append(ref_v)

            if to_be_updated_list:
                action = 'create'
                # check if there is a new published version of this version
                # that is using all the updated versions of the references
                latest_published_version = v.latest_published_version
                if latest_published_version and \
                   not v.is_latest_published_version():
                    # so there is a new published version
                    # check if its children needs any update
                    # and the updated child versions are already
                    # referenced to the this published version
                    if all([ref_v.latest_published_version
                            in latest_published_version.inputs
                            for ref_v in to_be_updated_list]):
                        # so all new versions are referenced to this published
                        # version, just update to this latest published version
                        action = 'update'
                    else:
                        # not all references are in the inputs
                        # so we need to create a new version as usual
                        # and update the references to the latest versions
                        action = 'create'
            else:
                # nothing needs to be updated,
                # so check if this version has a new version,
                # also there could be no reference under this referenced
                # version
                if v.is_latest_published_version():
                    # do nothing
                    action = 'leave'
                else:
                    # update to latest published version
                    action = 'update'

                # before setting the action check all the inputs in
                # resolution_dictionary, if any of them are update, or create
                # then set this one to 'create'
                if any(rev_v in reference_resolution['update'] or
                       rev_v in reference_resolution['create']
                       for rev_v in v.inputs):
                    action = 'create'

            # so append this v to the related action list
            reference_resolution[action].append(v)

            # from stalker import Version
            # assert isinstance(v, Version)
            caller.step(message=v.nice_name)

        caller.end_progress()

        return reference_resolution

    def update_versions(self, reference_resolution):
        """Updates maya versions with the given reference_resolution.

        The reference_resolution should be a dictionary in the following
        format::

          reference_resolution = {
              'root": [versionLM, versionUM, versionCM, ..., VersionXM],
              'leave': [versionL1, versionL2, ..., versionLN],
              'update': [versionU1, versionU2, ..., versionUN],
              'create': [versionC1, versionC2, ..., versionCN],
          }

        Previously this method was opening all the maya files by itself and do
        all the reference updates. But then we had crappy Maya scene files
        where the reference edits where ruined somehow. We tried to fix it by
        switching to a new update scheme (Shallow Reference Updates) but then
        we found that it is not working as expected. Finally, we have decided
        to update only 1st level references and inform the user about the
        deeper level references that needs to be updated and created UIs to let
        the artist quickly open the maya scene which needs to be updated. This
        way we hope that we still are going to have updated references and will
        prevent any bad maya scene file.

        All the references in the 'create' key need to be opened and then the
        all references need to be updated to the latest version and then a new
        :class:`~stalker.models.version.Version` instance will be created for
        each of them, and the newly created versions will be returned.

        The Version instances in 'leave' list will not be touched.

        The Version instances in 'update' list are there because the Version
        instances in 'create' list needs them to be updated. So practically
        these are Versions with already new versions so they will also not be
        touched.

        :param reference_resolution: A dictionary with keys 'leave', 'update'
          or 'create' and values of list of
          :class:`~stalker.models.version.Version` instances.
        :return list: A list of :class:`~stalker.models.version.Version`
          instances if created any.
        """
        logger.debug(
            'updating to new versions with: %s' % reference_resolution
        )

        # just create a list from  first level references
        # and only update those references
        references_list = pymel.core.listReferences()

        # order to the path
        references_list = sorted(references_list, key=lambda x: x.path)

        prev_path = ''
        prev_vers = None

        # use a progress window for that
        pm = ProgressDialogManager()
        caller = pm.register(len(references_list), 'Maya.update_versions()')

        # while len(references_list):
        for ref in references_list:
            #current_ref = references_list.pop(0)
            current_ref = ref

            current_ref_path = current_ref.path

            if current_ref_path != prev_path:
                # get current version
                current_version = \
                    self.get_version_from_full_path(current_ref_path)
                prev_vers = current_version
            else:
                current_version = prev_vers

            # update to a new version if present
            if current_version in reference_resolution['update']:
                if not current_version.is_latest_published_version():
                    latest_published_version = \
                        current_version.latest_published_version

                    # replace the current reference with this one
                    current_ref.replaceWith(
                        latest_published_version.absolute_full_path
                    )

            # get any reference under it and append to the list
            # references_list.extend(
            #     sorted(
            #         pymel.core.listReferences(current_ref),
            #         key=lambda x: x.path
            #     )
            # )
            caller.step(message=ref.namespace)

        return []  # no new version will be created with the current version

    def update_reference_edits(self, version):
        """Updates the reference edits for the given file

        :param version: The stalker.models.version.Version instance.
        :return: True or False depending on if a new namespace is created.
        """
        # This will be used to determine if we need to create a new
        # version for this version
        updated_namespaces = False
        # referenceQuery = pymel.core.referenceQuery
        # use maya.cmds it is safer to use when there are Unicode edits
        import maya.cmds
        referenceQuery = maya.cmds.referenceQuery

        regex = r'(?P<nice_name>[\w_0-9]+)' \
                r'(?P<version>_v[0-9]+_ma[0-9]*)'

        # re open original scene
        reference_resolution = self.open(version, force=True)

        # check reference namespaces
        for ref in pymel.core.listReferences(recursive=True):
            namespace = ref.namespace
            match = re.match(regex, namespace)
            if match:
                updated_namespaces = True

        if not updated_namespaces:
            # do updates
            return self.update_first_level_versions(reference_resolution)

        # check references
        refs = pymel.core.listReferences(recursive=True)

        edits_dictionary = {}
        for i, ref in enumerate(reversed(refs)):
            # re apply any live edits
            try:
                # all_edits = referenceQuery(ref, es=1)
                all_edits = referenceQuery(
                    ref.refNode.name(),
                    es=True
                )
                if all_edits is None:
                    all_edits = []
            except UnicodeError:
                logger.debug('edits has improper character, skipping!!!')
                all_edits = []

            logger.debug('all_edits: %s' % all_edits)

            edits_dictionary[i] = {
                'namespace': ref.fullNamespace,
                'edits': all_edits
            }
            if all_edits:
                ref.removeReferenceEdits(force=1)
                ref.load()

        # do updates
        if self.update_first_level_versions(reference_resolution):
            updated_namespaces = True

        # replace first level reference namespaces
        for ref in pymel.core.listReferences():
            # replace any possible old namespace with current one
            ref_version = self.get_version_from_full_path(ref.path)
            old_namespace = ref.namespace
            try:
                new_namespace = ref_version.nice_name

                # changing to the same namespace will change the namespace
                # to "namespace" to "namespace1"
                # prevent this by checking if the desired namespace is really
                # not the old_namespace
                if old_namespace != new_namespace:
                    ref.namespace = ref_version.nice_name
                    updated_namespaces = True

            except RuntimeError:
                # Apparently There is no namespace, so do not change the
                # namespace
                pass

        refs = pymel.core.listReferences(recursive=True)
        for i, ref in enumerate(reversed(refs)):
            try:
                all_edits = edits_dictionary[i]['edits']
            except KeyError:
                # there is a problem with this file skip this edit
                continue
            logger.debug('re-all_edits: %s' % all_edits)

            old_namespace = edits_dictionary[i]['namespace']
            new_namespace = ref.fullNamespace

            logger.debug('old_namespace : %s' % old_namespace)
            logger.debug('new_namespace : %s' % new_namespace)

            # external edits, edits that are done in another scene
            external_edits = referenceQuery(ref, es=1, scs=1)

            for edit in all_edits:
                updated_edit = edit.replace(
                    old_namespace,
                    new_namespace
                ).replace('|:', '|')  # the last one is a weird bug

                # do not apply edits if they are coming from other scenes
                if updated_edit in external_edits:
                    continue

                logger.debug('updated_edit: %s' % updated_edit)
                # so this is an edit done in current scene
                try:
                    pymel.core.mel.eval(updated_edit)
                except RuntimeError:
                    logger.debug('There is a RuntimeError in : %s' %
                                 updated_edit)
                    pass

        return updated_namespaces

    def fix_reference_namespaces(self):
        """Fixes the reference namespaces in current scene.

        This is a utility method to help fix the reference namespaces without
        loosing reference edits.

        The previous reference namespace template was including the version
        number and the file extension, and in a later version the Maya
        environment started to use the ``version.nice_name`` as the namespace
        to let maya not to loose edits when new versions introduced.

        So basically this method finds the references with old namespaces no
        matter how deeply they are referenced and then creates new versions for
        the referencing version that uses the correct namespaces and then
        reapplies all the edits with tne new namespace.

        The returned list of versions `created_by` and `updated_by` attributes
        nee to be updated.

        :return: A list of newly created Versions
        """
        regex = r'(?P<nice_name>[\w_0-9]+)' \
                r'(?P<version>_v[0-9]+_ma[0-9]*)'

        started_from_version = self.get_current_version()
        created_versions = []

        # get inverted reference nodes
        refs = reversed(pymel.core.listReferences(recursive=1))

        to_update_list = []

        for ref in refs:
            # list every child ref of this ref
            update_this = False
            for child_ref in pymel.core.listReferences(ref):
                # check the namespace
                namespace = child_ref.namespace
                match = re.match(regex, namespace)
                if match:
                    update_this = True
            if update_this:
                to_update_list.append(ref)

        # sort to_update_list according to ref.path
        #to_update_list = sorted(to_update_list, key=lambda x: x.path)

        to_update_paths = []

        for ref in to_update_list:
            path = ref.path
            if path not in to_update_paths:
                to_update_paths.append(path)
                # also add parents
                parent_ref = ref.parent()
                while parent_ref:
                    current_ref = parent_ref
                    path = current_ref.path
                    if path not in to_update_paths:
                        to_update_paths.append(path)
                    parent_ref = current_ref.parent()

        # print "to_update_paths: %s" % to_update_paths

        if to_update_paths:
            # so, we need to update things

            # we need to :
            # 1- open up these versions,
            # 2- fix the namespace
            # 3- and create a new version
            # 4- open the original scene
            # 5- store all the edits
            # 6- change namespace
            # 7- fix edits with new namespace
            # 8- apply them

            caller = None
            if self.use_progress_window and len(to_update_paths):
                pm = ProgressDialogManager()
                caller = pm.register(len(to_update_paths),
                                     'Maya.fix_reference_namespaces()')

            from stalker import Version
            for path in to_update_paths:
                vers = self.get_version_from_full_path(path)

                logger.debug('vers: %s' % vers)
                if not vers:
                    continue

                # use the latest published version instead of the referenced
                # one, so we also do updates on the other hand
                vers = vers.latest_published_version
                logger.debug('vers.latest_published_version: %s' % vers)

                updated_namespaces = self.update_reference_edits(vers)

                logger.debug('updated_namespaces : %s' % updated_namespaces)
                if updated_namespaces:
                    # if we have changed the namespace we should create a new
                    # version
                    new_version = Version(
                        task=vers.task,
                        take_name=vers.take_name,
                        parent=vers,
                        description='Automatically created with Fix Reference '
                                    'Namespace'
                    )
                    new_version.is_published = True
                    created_versions.append(new_version)
                    logger.debug('new_version : %s' % new_version)
                    self.save_as(new_version)
                    # pymel.core.saveFile()

                if caller is not None:
                    caller.step(message=path)

            self.update_reference_edits(started_from_version)

        return created_versions

#************#
# PUBLISHERS #
#************#


#*********#
# GENERIC #
#*********#
@publish.publisher
def check_old_object_smoothing():
    """checking if there are objects with
    """
    meshes_with_smooth_mesh_preview = []
    for node in pymel.core.ls(type='mesh'):
        if node.displaySmoothMesh.get() != 0:
            meshes_with_smooth_mesh_preview.append(node)

    if len(meshes_with_smooth_mesh_preview) > 0:
        raise PublishError(
            'Please do not use <b>Smooth Mesh</b> on following nodes:<br><br>'
            '%s' %
            '<br>'.join(
                map(lambda x: x.name(),
                    meshes_with_smooth_mesh_preview[:MAX_NODE_DISPLAY])
            )
        )


#*******#
# MODEL #
#*******#
@publish.publisher('model')
def check_history():
    """there should be no history on the objects
    """
    excluded_types = ['mesh', 'shadingEngine', 'groupId']
    nodes_with_history = []

    # get all shapes
    all_shapes = pymel.core.ls(type='mesh')
    for node in all_shapes:
        history_nodes = []
        for h_node in node.listHistory(pdo=1, lv=1):
            if h_node.type() not in excluded_types:
                history_nodes.append(h_node)

        if len(history_nodes) > 1:
            nodes_with_history.append(node)

    if len(nodes_with_history):
        # there is history
        raise PublishError(
            'There is history on:\n\n'
            '%s'
            '\n\n'
            'there should be no '
            'history in Model versions' %
            '\n'.join(
                map(lambda x: x.name(),
                    nodes_with_history[:MAX_NODE_DISPLAY])
            )
        )


@publish.publisher('model')
def check_if_default_shader():
    """check if only default shader is assigned
    """
    if len(pymel.core.ls(mat=1)) > 2:
        raise PublishError(
            'Use only lambert1 as the shader!'
        )


@publish.publisher('model')
def check_if_root_nodes_have_no_transformation():
    """checks if transform nodes directly under world have 0 transformations
    """
    root_transform_nodes = []
    for node in pymel.core.ls(dag=1, transforms=1):
        shape = node.getShape()
        if shape:
            if node.getParent() is None and shape.type() not in ['camera']:
                root_transform_nodes.append(node)

    non_freezed_root_nodes = []
    for node in root_transform_nodes:
        t = node.t.get()
        r = node.r.get()
        s = node.s.get()
        if t.x != 0 or t.y != 0 or t.z != 0 \
           or r.x != 0 or r.y != 0 or r.z != 0 \
           or s.x != 1 or s.y != 1 or s.z != 1:
            non_freezed_root_nodes.append(node)

    if len(non_freezed_root_nodes):
        raise PublishError(
            'Please freeze the following node transformations:\n\n%s' %
            '\n'.join(
                map(lambda x: x.name(),
                    non_freezed_root_nodes[:MAX_NODE_DISPLAY])
            )
        )


@publish.publisher('model')
def check_if_leaf_mesh_nodes_have_no_transformation():
    """checks if all the Mesh transforms have 0 transformation, but it is
    allowed to move the mesh nodes in space with a parent group node.
    """
    mesh_nodes_with_transform_children = []
    for node in pymel.core.ls(dag=1, type='mesh'):
        parent = node.getParent()
        tra_under_shape = pymel.core.ls(
            parent.listRelatives(),
            type='transform'
        )
        if len(tra_under_shape):
            mesh_nodes_with_transform_children.append(parent)

    if len(mesh_nodes_with_transform_children):
        raise PublishError(
            'The following meshes have other objects parented to them:'
            '\n\n%s'
            '\n\nPlease remove any object under them!' %
            '\n'.join(
                map(lambda x: x.name(),
                    mesh_nodes_with_transform_children[:MAX_NODE_DISPLAY])
            )
        )


@publish.publisher('model')
def check_model_quality():
    """checks the quality of the model
    """
    pymel.core.select(None)
    pymel.core.mel.eval(
        'polyCleanupArgList 3 { "1","2","0","0","1","0","0","0","0","1e-005",'
        '"0","0","0","0","0","2","1" };'
    )

    if len(pymel.core.ls(sl=1)) > 0:
        raise RuntimeError(
            """There are issues in your model please run:<br><br>
            <b>PolygonMesh -> Mesh -> Cleanup...</b><br><br>
            <ul>Check:
            <li>Faces with more than 4 sides</li>
            <li>Faces with holes</li>
            <li>Lamina Faces</li>
            <li>Non-manifold Geometry</li>
            </ul>"""
        )


@publish.publisher('model')
def check_uvs():
    """checks uvs with no uv area
    """
    def area(p):
        return 0.5 * abs(sum(x0 * y1 - x1 * y0
                             for ((x0, y0), (x1, y1)) in segments(p)))

    def segments(p):
        return zip(p, p[1:] + [p[0]])

    all_meshes = pymel.core.ls(type='mesh')
    mesh_count = len(all_meshes)

    caller = None
    if not pymel.core.general.about(batch=1) and mesh_count:
        pm = ProgressDialogManager()
        caller = pm.register(mesh_count, 'check_uvs()')

    meshes_with_zero_uv_area = []
    for node in pymel.core.ls(type='mesh'):
        all_uvs = node.getUVs()
        try:
            for i in range(node.numFaces()):
                uvs = []
                for j in range(node.numPolygonVertices(i)):
                    #uvs.append(node.getPolygonUV(i, j))
                    uv_id = node.getPolygonUVid(i, j)
                    uvs.append((all_uvs[0][uv_id], all_uvs[1][uv_id]))
                if area(uvs) == 0.0:
                    meshes_with_zero_uv_area.append(node)
                    break
        except RuntimeError:
            meshes_with_zero_uv_area.append(node)
            break

        if caller is not None:
            caller.step()

    if len(meshes_with_zero_uv_area):
        pymel.core.select(meshes_with_zero_uv_area)
        raise RuntimeError(
            """There are models with no uvs or faces with zero uv area:<br><br>
            %s""" %
            '<br>'.join(
                map(lambda x: x.name(),
                    meshes_with_zero_uv_area[:MAX_NODE_DISPLAY])
            )
        )


@publish.publisher('model')
def check_anim_layers():
    """check if there are animation layers on the scene
    """
    if len(pymel.core.ls(type='animLayer')) > 0:
        raise PublishError(
            'There should be no <b>Animation Layers</b> in the scene!!!'
        )


@publish.publisher('model')
def check_display_layer():
    """check if there are display layers
    """
    if len(pymel.core.ls(type='displayLayer')) > 1:
        raise PublishError(
            'There should be no <b>Display Layers</b> in the scene!!!'
        )


@publish.publisher('model')
def check_extra_cameras():
    """checking if there are extra cameras
    """
    if len(pymel.core.ls(type='camera')) > 4:
        raise PublishError('There should be no extra cameras in your scene!')


@publish.publisher('model')
def check_empty_groups():
    """check if there are empty groups
    """
    empty_groups = []
    for node in pymel.core.ls(type='transform'):
        if len(node.listRelatives(children=1)) == 0:
            empty_groups.append(node)

    if len(empty_groups):
        raise PublishError(
            'There are <b>empty groups</b> in your scene, '
            'please remove them!!!'
        )


#******************#
# LOOK DEVELOPMENT #
#******************#
look_dev_types = ['LookDev', 'Look Dev', 'LookDevelopment', 'Look Development']


@publish.publisher(look_dev_types)
def check_all_tx_textures():
    """checks if tx textures are created for all of the texture nodes in the
    current scene
    """
    texture_file_paths = []
    workspace_path = pymel.core.workspace.path

    def add_path(path):
        if path != '':
            if not os.path.isabs(path):
                path = \
                    os.path.normpath(os.path.join(workspace_path, path))
            texture_file_paths.append(path)

    for node in pymel.core.ls(type='file'):
        add_path(node.fileTextureName.get())

    for node in pymel.core.ls(type='aiImage'):
        add_path(node.filename.get())

    textures_with_no_tx = []
    for path in texture_file_paths:
        tx_path = '%s.tx' % os.path.splitext(path)[0]
        if not os.path.exists(tx_path):
            textures_with_no_tx.append(path)

    if len(textures_with_no_tx):
        raise PublishError('There are textures with no <b>TX</b> file!!!')


@publish.publisher(look_dev_types)
def check_lights():
    """checks if there are lights in the scene
    """
    all_lights = pymel.core.ls(type='light')
    if len(all_lights):
        raise PublishError(
            'There are <b>Lights</b> in the current scene:<br><br>%s<br><br>'
            'Please delete them!!!' %
            '<br>'.join(map(lambda x: x.name(), all_lights))
        )


@publish.publisher(look_dev_types)
def check_unused_nodes():
    """selects unused shading nodes
    """
    num_of_items_deleted = pymel.core.mel.eval('MLdeleteUnused')
    if num_of_items_deleted:
        # do not raise any error just warn the user
        pymel.core.warning('Deleted unused nodes during Publish operation!!')


@publish.publisher(look_dev_types)
def check_only_arnold_materials_are_used():
    """check if only arnold materials are used
    """
    # TODO: this should be depending on to the project some projects still can
    #       use mental ray
    arnold_materials = [
        u'aiAmbientOcclusion',
        u'aiHair',
        u'aiRaySwitch',
        u'aiShadowCatcher',
        u'aiSkin',
        u'aiSkinSss',
        u'aiStandard',
        u'aiUtility',
        u'aiWireframe'
    ]

    non_arnold_materials = []

    for material in pymel.core.ls(mat=1):
        if material.name() not in ['lambert1', 'particleCloud1']:
            if material.type() not in arnold_materials:
                non_arnold_materials.append(material)

    if len(non_arnold_materials):
        raise PublishError(
            'There are non-Arnold materials in the scene:<br><br>%s<br><br>'
            'Please remove them!!!' %
            '<br>'.join(map(lambda x: x.name(), non_arnold_materials))
        )


@publish.publisher(look_dev_types)
def check_objects_still_using_default_shader():
    """check if there are objects still using the default shader
    """
    objects_with_default_material = pymel.core.sets('initialShadingGroup', q=1)
    if len(objects_with_default_material):
        raise PublishError(
            'There are objects still using <b>initialShadingGroup</b><br><br>'
            '%s<br><br>Please assign a proper material to them' %
            '<br>'.join(
                map(lambda x: x.name(), objects_with_default_material)
            )[:MAX_NODE_DISPLAY]
        )


@publish.publisher(look_dev_types + ['layout'])
def check_component_edits_on_references():
    """check if there are component edits on references
    """
    import maya.cmds
    reference_query = maya.cmds.referenceQuery

    references_with_component_edits = []

    for ref in pymel.core.listReferences(recursive=True):
        all_edits = reference_query(ref.refNode.name(), es=True)
        joined_edits = '\n'.join(all_edits)
        if '.pt[' in joined_edits or '.pnts[' in joined_edits:
            references_with_component_edits.append(ref)
            continue

    if len(references_with_component_edits):
        raise PublishError(
            'There are <b>component edits</b> on the following References:'
            '<br><br>%s<br><br>Please remove them!!!' %
            '<br>'.join(
                map(lambda x: x.refNode.name(),
                    references_with_component_edits)
            )[:MAX_NODE_DISPLAY]
        )


@publish.publisher(look_dev_types)
def check_if_previous_version_references():
    """check if a previous version of the same task is referenced to the scene
    """
    m = Maya()
    ver = m.get_current_version()
    same_version_references = []
    for ref in pymel.core.listReferences():  # check only 1st level references
        ref_version = m.get_version_from_full_path(ref.path)
        if ref_version:
            if ref_version.task == ver.task \
               and ref_version.take_name == ver.take_name:
                same_version_references.append(ref)

    if len(same_version_references):
        print 'The following nodes are references to an older version of ' \
              'this scene'
        print '\n'.join(
            map(lambda x: x.refNode.name(), same_version_references)
        )
        raise PublishError(
            'The current scene contains a <b>reference</b> to a<br>'
            '<b>previous version</b> of itself.<br><br>'
            'Please remove it!!!'
        )


@publish.publisher(look_dev_types)
def check_material_names():
    """check if the name of materials are not starting with the material type
    name
    """
    material_with_simple_names = []
    for mat in pymel.core.ls(mat=1):
        mat_name = mat.name()
        if mat_name not in ['lambert1', 'particleCloud1'] \
           and mat.name().startswith(mat.type()):
            material_with_simple_names.append(mat_name)

    if len(material_with_simple_names):
        print 'Use a more **descriptive** name for the following materials:'
        print '\n'.join(material_with_simple_names)
        raise PublishError(
            'Please use a more <b>descriptive</b> name<br>'
            'for the following materials:<br><br>%s' %
            '<br>'.join(material_with_simple_names)
        )
