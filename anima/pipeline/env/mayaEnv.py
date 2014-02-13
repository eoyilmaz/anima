# -*- coding: utf-8 -*-
# Copyright (c) 2012-2014, Anima Istanbul
#
# This module is part of anima-tools and is released under the BSD 2
# License: http://www.opensource.org/licenses/BSD-2-Clause
import os
import shutil
import logging

import pymel.core
import pymel.versions


from stalker import db, Version

from .. import utils
from base import EnvironmentBase

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)


class Maya(EnvironmentBase):
    """the maya environment class
    """

    name = "Maya"

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

    def save_as(self, version):
        """The save_as action for maya environment.

        It saves the given Version instance to the Version.absolute_full_path.
        """
        from stalker import Version
        assert isinstance(version, Version)

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

        # set the playblast file name
        self.set_playblast_file_name(version)

        # create the folder if it doesn't exists
        utils.createFolder(version.absolute_path)

        # delete the unknown nodes
        unknownNodes = pymel.core.ls(type='unknown')
        pymel.core.delete(unknownNodes)

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
        self.update_version_inputs()

        # append it to the recent file list
        self.append_to_recent_files(
            version.absolute_full_path
        )

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
        db.DBSession.add(version)
        db.DBSession.commit()

        return True

    def open(self, version, force=False):
        """The open action for Maya environment.

        Opens the given Version file, sets the workspace etc.

        It also updates the referenced Version on open.

        :returns: list of :class:`~stalker.models.version.Version`
          instances which are referenced in to the opened version and those
          need to be updated
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

        self.append_to_recent_files(version.absolute_full_path)

        # replace_external_paths
        self.replace_external_paths()

        # check the referenced versions for any possible updates
        resolution_dictionary = self.check_referenced_versions()

        self.update_version_inputs()

        return True, resolution_dictionary

    def post_open(self):
        """Runs after opening a file
        """
        #self.load_referenced_versions()
        self.update_version_inputs()

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
        """
        # use the file name without extension as the namespace
        namespace = os.path.basename(version.filename)
        namespace = namespace.replace('.', '_')

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
                defaultNamespace=True,
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
            db.DBSession.commit()

        # also update version.inputs for the referenced input
        self.update_version_inputs(ref)

        return True

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
            for i in range(len(recent_files)-1, -1, -1):
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
        dRG.setAttr('imageFormat', 7) # force the format to iff
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
    def get_significant_name(cls, version, include_version_number=True):
        """returns a significant name starting from the closest parent which is
        an Asset, Shot or Sequence and includes the Project.code

        :rtype : basestring
        """
        sig_name = '%s_%s' % (version.task.project.code, version.nice_name)

        if include_version_number:
           sig_name = '%s_v%03d' % (sig_name, version.version_number)

        return sig_name

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
        ).replace('\\','/')

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
            db.DBSession.commit()

    def update_versions(self, resolution):
        """update versions to the latest version
        """
        # list only first level references
        references = sorted(pymel.core.listReferences(), key=lambda x: x.path)

        # get direct references
        for reference in references:
            version = self.get_version_from_full_path(reference.path)
            if version in resolution['update']:
                latest_published_version = version.latest_published_version
                absolute_full_path = latest_published_version.absolute_full_path
                reference.replaceWith(absolute_full_path)

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
            source_reference, resursive=True
        )
#        logger.debug("subReferences count: %s" % len(subReferences))

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
                #refNode = subRefData[1]
                #newNS = \
                #  self.get_full_namespace_from_node_name(refNode.nodes()[0])

            # if the new namespace is different than the previous one
            # also change the edit targets
            if previous_namespace != new_namespace:
#                logger.debug("prevNS: %s" % previous_namespace)
#                logger.debug("newNS : %s" % newNS)

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
                        #    changeEditTarget=(nodeOldName, nodeNewName)
                        #)
                        #pymel.core.referenceEdit(
                        #     subRef,
                        #     orn=baseRefNode,
                        #     changeEditTarget=(nodeOldName, nodeNewName)
                        #)
                        #for aRefNode in pymel.core.ls(type='reference'):
                            #if len(aRefNode.attr('sharedReference').listConnections(s=0,d=1)) == 0: # not a shared reference
                                #pymel.core.referenceEdit(aRefNode, orn=baseRefNode, changeEditTarget=(nodeOldName, nodeNewName), scs=1, fld=1)
                                ##pymel.core.referenceEdit(aRefNode, applyFailedEdits=True)
                    #pymel.core.referenceEdit(subRef, applyFailedEdits=True)

                # apply all the failed edits again
                pymel.core.referenceEdit(base_reference_node, applyFailedEdits=True)

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
                            assert isinstance(ref, pymel.core.system.FileReference)
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
            logger.debug(full_path)
            try:
                os.makedirs(full_path)
            except OSError:
                # dir exists
                pass

    def deep_version_inputs_update(self):
        """updates the inputs of the references of the current scene
        """
        # first update the current scene
        self.update_version_inputs()

        # the go to the references
        references_list = pymel.core.listReferences()

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
            prev_ref_path = None

    def check_referenced_versions(self):
        """Deeply checks all the references in the scene and returns a
        dictionary which uses the ids of the Versions as key and the action as
        value.

        Uses the top level references to get a Stalker Version instance and
        then tracks all the changes from these Version instances.

        :return: list
        """
        # recreate version.inputs list from current scene
        self.deep_version_inputs_update()

        # reverse walk in DFS
        dfs_version_references = []
        # TODO: with Stalker v0.2.5 replace this with Version.walk_inputs()
        resolution_dictionary = {
            'leave': [],
            'update': [],
            'create': []
        }

        version = self.get_current_version()
        for v in utils.walk_version_hierarchy(version):
            dfs_version_references.append(v)

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
                if any(rev_v in resolution_dictionary['update'] or
                       rev_v in resolution_dictionary['create']
                       for rev_v in v.inputs):
                    action = 'create'

            # so append this v to the related action list
            resolution_dictionary[action].append(v)

        return resolution_dictionary

    def deep_reference_update(self, reference_resolution):
        """Updates maya versions given with the reference_resolution dictionary.

        The reference_resolution should be a dictionary in the following
        format::

          reference_resolution = {
              'leave': [versionL1, versionL2, ..., versionLN],
              'update': [versionU1, versionU2, ..., versionUN],
              'create': [versionC1, versionC2, ..., versionCN],
          }

        All the references in the 'create' key will be opened and then the all
        references will be updated to the latest version and then a new
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
        # first get the resolution list
        new_versions = []
        pymel.core.newFile(force=True)

        # loop through 'create' versions and update their references
        # and create a new version for each of them
        for version in reference_resolution['create']:
            success, local_reference_resolution = \
                self.open(version, force=True)

            # replace each 'update' reference in the
            # local_reference_resolution list
            self.update_versions(local_reference_resolution)

            # save as a new version
            new_version = Version(
                task=version.task,
                take_name=version.take_name,
                parent=version,
                description='Automatically created with '
                            'Deep Reference Update'
            )
            new_version.is_published = True
            self.save_as(new_version)
            new_versions.append(new_version)

        return new_versions
