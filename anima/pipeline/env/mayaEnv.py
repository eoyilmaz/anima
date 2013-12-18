# -*- coding: utf-8 -*-
# Copyright (c) 2012-2013, Anima Istanbul
#
# This module is part of anima-tools and is released under the BSD 2
# License: http://www.opensource.org/licenses/BSD-2-Clause


import os
import shutil
import logging

from pymel import core as pm

from stalker.db import DBSession

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

        current_workspace_path = pm.workspace.path

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
            self.replace_external_paths(mode=1)

        # create the workspace folders
        self.create_workspace_file(workspace_path)

        # this sets the project
        pm.workspace.open(workspace_path)

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
            self.set_resolution(project.image_format.width,
                                project.image_format.height,
                                project.image_format.pixel_aspect)

        # set the render file name and version
        self.set_render_fileName(version)

        # set the playblast file name
        self.set_playblast_file_name(version)

        # create the folder if it doesn't exists
        utils.createFolder(version.absolute_path)

        # delete the unknown nodes
        unknownNodes = pm.ls(type='unknown')
        pm.delete(unknownNodes)

        # set the file paths for external resources
        self.replace_external_paths(mode=1)

        # save the file
        pm.saveAs(
            version.absolute_full_path,
            type='mayaAscii'
        )

        # update the parent info
        version.parent = current_version

        # update the reference list
        self.update_references_list(version)

        # append it to the recent file list
        self.append_to_recent_files(
            version.absolute_full_path
        )

        DBSession.commit()

        return True

    def export_as(self, version):
        """the export action for maya environment
        """
        # check if there is something selected
        if len(pm.ls(sl=True)) < 1:
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
        pm.exportSelected(version.absolute_full_path, type='mayaAscii')

        # save the version to database
        DBSession.add(version)
        DBSession.commit()

        return True

    def open_(self, version, force=False):
        """The open action for Maya environment.

        Opens the given Version file, sets the workspace etc.

        It also updates the referenced Version on open.

        :returns: list of :class:`~stalker.models.version.Version`
          instances which are referenced in to the opened version and those
          need to be updated
        """
        # store current workspace path
        previous_workspace_path = pm.workspace.path

        # set the project
        # new_workspace = os.path.dirname(version.absolute_path)
        new_workspace = version.absolute_path

        pm.workspace.open(new_workspace)

        # check for unsaved changes
        logger.info("opening file: %s" % version.absolute_full_path)

        try:
            pm.openFile(
                version.absolute_full_path,
                f=force,
                #loadReferenceDepth='none'
            )
        except RuntimeError as e:
            # restore the previous workspace
            pm.workspace.open(previous_workspace_path)

            # raise the RuntimeError again
            # for the interface
            raise e

        # set the playblast folder
        self.set_playblast_file_name(version)

        self.append_to_recent_files(version.absolute_full_path)

        # replace_external_paths
        self.replace_external_paths(mode=1)

        # check the referenced assets for newer version
        to_update_list = self.check_referenced_versions()

        #for update_info in to_update_list:
        #    version = update_info[0]

        self.update_references_list(version)

        return True, to_update_list

    def post_open(self, version):
        """Runs after opening a file
        """
        #self.load_referenced_versions()
        self.update_references_list(version)

    def import_(self, version, use_namespace=True):
        """Imports the content of the given Version instance to the current
        scene.

        :param version: The desired
          :class:`~stalker.models.version.Version` to be imported
        """
        if use_namespace:
            namespace = os.path.basename(version.filename)
            pm.importFile(
                version.absolute_full_path,
                namespace=namespace
            )
        else:
            pm.importFile(
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

        workspace_path = pm.workspace.path

        new_version_full_path = version.absolute_full_path
        if new_version_full_path.startswith(workspace_path):
            new_version_full_path = utils.relpath(
                workspace_path,
                new_version_full_path.replace("\\", "/"), "/", ".."
            )

        # replace the path with environment variable
        #new_version_full_path = repo.relative_path(new_version_full_path)

        if use_namespace:
            ref = pm.createReference(
                new_version_full_path,
                gl=True,
                namespace=namespace,
                options='v=0'
            )
        else:
            ref = pm.createReference(
                new_version_full_path,
                gl=True,
                defaultNamespace=True,
                options='v=0'
            )

        # replace external paths
        self.replace_external_paths(1)

        # set the reference state to loaded
        if not ref.isLoaded():
            ref.load()

        # append the referenced version to the current versions references
        # attribute

        current_version = self.get_current_version()
        if current_version:
            current_version.inputs.append(version)
            DBSession.commit()

        return True

    def get_version_from_workspace(self):
        """Tries to find a version from the current workspace path
        """
        logger.debug("trying to get the version from workspace")

        # get the workspace path
        workspace_path = pm.workspace.path
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

        # pm.env.sceneName() always uses "/"
        full_path = pm.env.sceneName()
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
            recent_files = pm.optionVar['RecentFilesList']
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

    def set_render_fileName(self, version):
        """sets the render file name
        """
        # assert isinstance(version, Version)
        render_output_folder = os.path.join(
            version.absolute_path,
            'Outputs'
        ).replace("\\", "/")

        # image folder from the workspace.mel
        # {{project.full_path}}/Sequences/{{seqence.code}}/Shots/{{shot.code}}/.maya_files/rendered_images
        image_folder_from_ws = pm.workspace.fileRules['images']
        image_folder_from_ws_full_path = os.path.join(
            version.absolute_path,
            image_folder_from_ws
        ).replace("\\", "/")

        version_sig_name = self.get_significant_name(version)

        render_file_full_path = render_output_folder + '/<RenderLayer>/' + \
            version_sig_name + '_<RenderLayer>_<RenderPass>'

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
        dRG = pm.PyNode('defaultRenderGlobals')
        dRG.setAttr('imageFilePrefix', render_file_rel_path)
        dRG.setAttr('renderVersion', "v%03d" % version.version_number )
        dRG.setAttr('animation', 1)
        dRG.setAttr('outFormatControl', 0 )
        dRG.setAttr('extensionPadding', 4 )
        dRG.setAttr('imageFormat', 7 ) # force the format to iff
        dRG.setAttr('pff', 1)

        self.set_output_file_format()

    @classmethod
    def set_output_file_format(cls):
        """sets the output file format
        """
        dRG = pm.PyNode('defaultRenderGlobals')

        # check the current renderer
        current_renderer = dRG.currentRenderer.get()
        if current_renderer == 'mentalRay':
            # set the render output to OpenEXR with zip compression
            dRG.imageFormat.set(51)
            dRG.imfkey.set('exr')
            # check the maya version and set it if maya version is equal or
            # greater than 2012
            import pymel
            try:
                if pymel.versions.current() >= pymel.versions.v2012:
                    try:
                        mrG = pm.PyNode("mentalrayGlobals")
                    except pm.general.MayaNodeError:
                        # the renderer is set to mentalray but it is not loaded
                        # so there is no mentalrayGlobals
                        # create them

                        # dirty little maya tricks
                        pm.mel.miCreateDefaultNodes()

                        # get it again
                        mrG = pm.PyNode("mentalrayGlobals")

                    mrG.imageCompression.set(4)
            except AttributeError, pm.general.MayaNodeError:
                pass

            # if the renderer is not registered this causes a _objectError
            # and the frame buffer to 16bit half
            try:
                miDF = pm.PyNode('miDefaultFramebuffer')
                miDF.datatype.set(16)
            except TypeError, pm.general.MayaNodeError:
                # just don't do anything
                pass
        elif current_renderer == 'arnold':
            dRG.imageFormat.set(51)  # exr
            dAD = pm.PyNode('defaultArnoldDriver')
            dAD.exrCompression.set(2)  # zips
            dAD.halfPrecision.set(1)  # half
            dAD.tiled.set(0)  # not tiled
            dAD.autocrop.set(1)  # will enhance file load times in Nuke

        ## check all the render layers and try to get if any of them are using
        ## mayaSoftware as the renderer, and set the render output to iff if any
        #for renderLayer in pm.ls(type='renderLayer'):
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
        pm.optionVar['playblastFile'] = playblast_full_path

    @classmethod
    def set_resolution(cls, width, height, pixel_aspect=1.0):
        """Sets the resolution of the current scene

        :param width: The width of the output image
        :param height: The height of the output image
        :param pixel_aspect: The pixel aspect ratio
        """
        dRes = pm.PyNode("defaultResolution")
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
        pm.workspace.open(version.absolute_path)
        # set the current timeUnit to match with the environments
        cls.set_fps(version.task.project.fps)

    @classmethod
    def append_to_recent_files(cls, path):
        """appends the given path to the recent files list
        """
        # add the file to the recent file list
        try:
            recent_files = pm.optionVar['RecentFilesList']
        except KeyError:
            # there is no recent files list so create one
            # normally it is Maya's job
            # but somehow it is not working for new installations
            recent_files = pm.OptionVarList( [], 'RecentFilesList' )

        #assert(isinstance(recentFiles,pm.OptionVarList))
        recent_files.appendVar( path )

    def check_external_files(self, version):
        """checks for external files in the current scene and raises
        RuntimeError if there are local files in the current scene, used as:

            - File Textures
            - Mentalray Textures
            - ImagePlanes
            - IBL nodes
            - References
        """

        def is_in_repo(path):
            """checks if the given path is in repository
            :param path: the path which wanted to be checked
            :return: True or False
            """
            assert isinstance(path, (str, unicode))
            path = os.path.expandvars(path)
            repo = self.find_repo(path)
            return repo is not None

        def move_to_local(file_path, type_name):
            """moves the files to the local "external" path
            """
            local_path = version.absolute_path + '/external_files/' + type_name
            filename = os.path.basename(file_path)
            destination_full_path = os.path.join(local_path, filename)
            # create the dirs
            try:
                os.makedirs(local_path)
            except OSError: # dir exists
                pass

            if not os.path.exists(destination_full_path):
                # move the file
                logger.debug('moving to: %s' % destination_full_path)
                try:
                    shutil.copy(file_path, local_path)
                except IOError: # no write permission
                    return None
                return destination_full_path
            else: # file already exists do not overwrite
                logger.debug('file already exists, not moving')
                return None

        external_nodes = []

        # check for file textures
        for file_texture in pm.ls(type=pm.nt.File):
            path = file_texture.attr('fileTextureName').get()
            logger.debug('checking path: %s' % path)
            if path is not None \
               and os.path.isabs(path) \
               and not is_in_repo(path):
                logger.debug('is not in repo: %s' % path)
                new_path = move_to_local(path, 'Textures')
                if not new_path:
                    # it was not copied
                    external_nodes.append(file_texture)
                else:
                    # succesfully copied
                    # update the path
                    logger.debug('updating texture path to: %s' % new_path)
                    file_texture.attr('fileTextureName').set(new_path)

        # check for arnold textures
        for arnold_texture in pm.ls(type='aiImage'):
            path = arnold_texture.attr('filename').get()
            logger.debug('checking path: %s' % path)
            if path is not None \
               and os.path.isabs(path) \
               and not is_in_repo(path):
                logger.debug('is not in repo: %s' % path)
                new_path = move_to_local(path, 'Textures')
                if not new_path:
                    # it was not copied
                    external_nodes.append(arnold_texture)
                else:
                    # succesfully copied
                    # update the path
                    logger.debug('updating texture path to: %s' % new_path)
                    arnold_texture.attr('filename').set(new_path)

        # check for mentalray textures
        try:
            for mr_texture in pm.ls(type=pm.nt.MentalrayTexture):
                path = mr_texture.attr('fileTextureName').get()
                logger.debug("path of %s: %s" % (mr_texture, path))
                if path is not None \
                   and os.path.isabs(path) \
                   and not is_in_repo(path):
                    logger.debug('is not in repo: %s' % path)
                    new_path = move_to_local(path, 'Textures')
                    if not new_path:
                        # it was not copied
                        external_nodes.append(mr_texture)
                    else:
                        # succesfully copied
                        # update the path
                        logger.debug('updating texture path to: %s' % new_path)
                        mr_texture.attr('fileTextureName').set(new_path)
        except AttributeError:  # MentalRay not loaded
            pass

        # check for ImagePlanes
        for image_plane in pm.ls(type=pm.nt.ImagePlane):
            path = image_plane.attr('imageName').get()
            if path is not None \
               and os.path.isabs(path) \
               and not is_in_repo(path):
                logger.debug('is not in repo: %s' % path)
                new_path = move_to_local(path, 'ImagePlanes')
                if not new_path:
                    # it was not copied
                    external_nodes.append(image_plane)
                else:
                    # succesfully copied
                    # update the path
                    logger.debug('updating image plane path to: %s' % new_path)
                    image_plane.attr('imageName').set(new_path)

        # check for IBL nodes
        try:
            for ibl in pm.ls(type=pm.nt.MentalrayIblShape):
                path = ibl.attr('texture').get()
                if path is not None \
                   and os.path.isabs(path) \
                   and not is_in_repo(path):
                    logger.debug('is not in repo: %s' % path)
                    new_path = move_to_local(path, 'IBL')
                    if not new_path:
                        # it was not copied
                        external_nodes.append(ibl)
                    else:
                        # succesfully copied
                        # update the path
                        logger.debug('updating ibl path to: %s' % new_path)
                        ibl.attr('texture').set(new_path)
        except AttributeError: # mentalray not loaded
            pass

        if external_nodes:
            pm.select(external_nodes)
            raise RuntimeError(
                'There are external references in your scene!!!\n\n'
                'The problematic nodes are:\n\n' +
                ", ".join(map(lambda x: x.name(), external_nodes)) +
                '\n\nThese nodes are added in to your selection list,\n'
                'Please correct them!\n\n'
                'YOUR FILE IS NOT GOING TO BE SAVED!!!'
            )

    def check_referenced_versions(self):
        """checks the referenced assets versions

        returns a list of Version instances and maya Reference objects in a
        tuple
        """
        # get all the valid version references
        version_tuple_list = self.get_referenced_versions()

        to_be_updated_list = []

        for version_tuple in version_tuple_list:
            version = version_tuple[0]
            if not version.is_latest_published_version():
                # add version to the update list
                to_be_updated_list.append(version_tuple)

        # sort the list according to full_path
        return sorted(to_be_updated_list, key=lambda x: x[2])

    def get_referenced_versions(self):
        """Returns the versions those been referenced to the current scene

        Returns Version instances and the corresponding Reference instance as a
        tupple in a list, and a string showing the path of the Reference.
        Replaces all the relative paths to absolute paths.

        The returned tuple format is as follows:
        (Version, Reference, full_path)
        """
        valid_versions = []

        # get all the references
        references = pm.listReferences()

        refs_and_paths = []
        # iterate over them to find valid assets
        for reference in references:
            # it is a dictionary
            temp_version_full_path = reference.path

            temp_version_full_path = \
                os.path.expandvars(
                    os.path.expanduser(
                        os.path.normpath(
                            temp_version_full_path
                        )
                    )
                ).replace("\\", "/")

            refs_and_paths.append((reference, temp_version_full_path))

        # sort them according to path
        # to make same paths together

        refs_and_paths = sorted(refs_and_paths, None, lambda x: x[1])

        prev_version = None
        prev_full_path = ''

        for reference, full_path in refs_and_paths:
            if full_path == prev_full_path:
                # directly append the version to the list
                valid_versions.append(
                    (prev_version, reference, prev_full_path)
                )
            else:
                # try to get a version with the given path
                temp_version = self.get_version_from_full_path(full_path)

                if temp_version:
                    valid_versions.append((temp_version, reference, temp_version.absolute_full_path))

                    prev_version = temp_version
                    prev_full_path = full_path

        # return a sorted list
        return sorted(valid_versions, None, lambda x: x[2])

    def update_references_list(self, version=None):
        """updates the references list of the current version
        :param version: the version to be checked
        """
        if version is not None:
            # update the reference list
            reference_list = []
            reference_info = self.get_referenced_versions()
            for data in reference_info:
                if data[0] not in reference_list:
                    reference_list.append(data[0])

            version.inputs = reference_list
            DBSession.commit()

    def update_versions(self, version_tuple_list):
        """update versions to the latest version
        """
        previous_version_full_path = ''
        latest_version = None

        for version_tuple in version_tuple_list:
            version = version_tuple[0]
            reference = version_tuple[1]
            version_full_path =  version_tuple[2]

            if version_full_path != previous_version_full_path:
                latest_published_version = version.latest_published_version
                previous_version_full_path = latest_published_version.absolute_full_path

            reference.replaceWith(latest_published_version.absolute_full_path)

    def get_frame_range(self):
        """returns the current playback frame range
        """
        start_frame = int(pm.playbackOptions(q=True, ast=True))
        end_frame = int(pm.playbackOptions(q=True, aet=True))
        return start_frame, end_frame

    def set_frame_range(self, start_frame=1, end_frame=100,
                        adjust_frame_range=False):
        """sets the start and end frame range
        """
        # set it in the playback
        pm.playbackOptions(ast=start_frame, aet=end_frame)

        if adjust_frame_range:
            pm.playbackOptions( min=start_frame, max=end_frame )

        # set in the render range
        dRG = pm.PyNode('defaultRenderGlobals')
        dRG.setAttr('startFrame', start_frame )
        dRG.setAttr('endFrame', end_frame )

    def get_fps(self):
        """returns the fps of the environment
        """
        # return directly from maya, it uses the same format
        return self.time_to_fps[pm.currentUnit(q=1, t=1)]

    @classmethod
    def set_fps(cls, fps=25):
        """sets the fps of the environment
        """
        # get the current time, current playback min and max (because maya
        # changes them, try to restore the limits)
        current_time = pm.currentTime(q=1)
        pMin = pm.playbackOptions(q=1, min=1)
        pMax = pm.playbackOptions(q=1, max=1)
        pAst = pm.playbackOptions(q=1, ast=1)
        pAet = pm.playbackOptions(q=1, aet=1)

        # set the time unit, do not change the keyframe times
        # use the timeUnit as it is
        time_unit = u"pal"

        # try to find a timeUnit for the given fps
        # TODO: set it to the closest one
        for key in cls.time_to_fps:
            if cls.time_to_fps[key] == fps:
                time_unit = key
                break

        pm.currentUnit(t=time_unit, ua=0)
        # to be sure
        pm.optionVar['workingUnitTime'] = time_unit

        # update the playback ranges
        pm.currentTime(current_time)
        pm.playbackOptions(ast=pAst, aet=pAet)
        pm.playbackOptions(min=pMin, max=pMax)

    @classmethod
    def load_referenced_versions(cls):
        """loads all the references
        """
        # get all the references
        for reference in pm.listReferences():
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
        # replacing references )
        subReferences = cls.get_all_sub_references(source_reference)
#        logger.debug("subReferences count: %s" % len(subReferences))

        if len(subReferences) > 0:
            # for all subReferences get the editString and apply it to the
            # replaced file with new namespace
            allEdits = []
            for subRef in subReferences:
                allEdits += subRef.getReferenceEdits(orn= base_reference_node)

            # replace the reference
            source_reference.replaceWith(target_file)

            # try to find the new namespace
            subReferences = cls.get_all_sub_references(source_reference)
            newNS = cls.get_full_namespace_from_node_name(
                subReferences[0].nodes()[0]
            )  # possible bug here, fix it later

            # replace the old namespace with the new namespace in all the edits
            allEdits = [edit.replace(previous_namespace + ":", newNS + ":")
                        for edit in allEdits]

            # apply all the edits
            for edit in allEdits:
                try:
                    pm.mel.eval(edit)
                except pm.MelError:
                    pass
        else:
            # replace the reference
            source_reference.replaceWith(target_file)

            # try to find the new namespace
            subReferences = cls.get_all_sub_references(source_reference)
            newNS = cls.get_full_namespace_from_node_name(
                subReferences[0].nodes()[0]
            )  # possible bug here, fix it later

            #subReferences = source_reference.subReferences()
            #for subRefData in subReferences.iteritems():
                #refNode = subRefData[1]
                #newNS = self.get_full_namespace_from_node_name( refNode.nodes()[0] )

            # if the new namespace is different than the previous one
            # also change the edit targets
            if previous_namespace != newNS:
#                logger.debug("prevNS: %s" % previous_namespace)
#                logger.debug("newNS : %s" % newNS)

                # get the new sub references
                for subRef in cls.get_all_sub_references( source_reference ):
                    # for all the nodes in sub references
                    # change the edit targets with new namespace
                    for node in subRef.nodes():
                        # use the long name -- suggested by maya help
                        nodeNewName = node.longName()
                        nodeOldName = nodeNewName.replace(
                            newNS + ':', previous_namespace + ':'
                        )

                        pm.referenceEdit(
                            base_reference_node,
                            changeEditTarget=(nodeOldName, nodeNewName)
                        )
                        #pm.referenceEdit(
                        #    baseRefNode,
                        #    orn=baseRefNode,
                        #    changeEditTarget=(nodeOldName, nodeNewName)
                        #)
                        #pm.referenceEdit(
                        #     subRef,
                        #     orn=baseRefNode,
                        #     changeEditTarget=(nodeOldName, nodeNewName)
                        #)
                        #for aRefNode in pm.ls(type='reference'):
                            #if len(aRefNode.attr('sharedReference').listConnections(s=0,d=1)) == 0: # not a shared reference
                                #pm.referenceEdit( aRefNode, orn=baseRefNode, changeEditTarget=( nodeOldName, nodeNewName), scs=1, fld=1 )
                                ##pm.referenceEdit( aRefNode, applyFailedEdits=True )
                    #pm.referenceEdit( subRef, applyFailedEdits=True )

                # apply all the failed edits again
                pm.referenceEdit(base_reference_node, applyFailedEdits=True)

    @classmethod
    def get_all_sub_references(cls, ref):
        """returns the recursive sub references as a list of FileReference
        objects for the given file reference
        """
        allRefs = []
        subRefDict = ref.subReferences()

        if len(subRefDict) > 0:
            for subRefData in subRefDict.iteritems():
                # first convert the sub ref dictionary to a normal ref object
                subRef = subRefData[1]
                allRefs.append(subRef)
                allRefs += cls.get_all_sub_references(subRef)

        return allRefs

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
        if pm.pluginInfo('stereoCamera', q=True, l=True):
            return len(pm.ls(type='stereoRigTransform')) > 0
        else:
            # return False because it is impossible without stereoCamera plugin
            # to have a stereoCamera rig
            return False

    def replace_external_paths(self, mode=0):
        """Replaces all the external paths

        replaces:
          references: replaces Windows, Linux or OSX paths with native one
                      (the one that the current user has) in absolute mode and
                      with a workspace relative path in relative mode.
          files     : absolute path in absolute mode and a workspace relative
                      path in relative mode

        Absolute mode works best for now.

        .. note::

          The system doesn't care about the mentalrayTexture nodes because the
          lack of a good environment variable support from that node. Use
          regular maya file nodes with mib_texture_filter_lookup nodes to have
          the same sharp results.

        :param mode: Defines the process mode:
          if mode == 0 : replaces with relative paths
          if mode == 1 : replaces with absolute paths
        """
        # TODO: Also check for image planes and replace the path
        logger.debug("replacing paths with mode: %i" % mode)

        # create a repository
        workspace_path = pm.workspace.path

        # *********************************************************************
        # References
        # replace reference paths with absolute path
        for ref in pm.listReferences():
            unresolved_path = ref.unresolvedPath().replace("\\", "/")
            repo = self.find_repo(unresolved_path)

            if repo:
                # make it absolute
                if repo.is_in_repo(unresolved_path):
                    new_ref_path = ""

                    if mode:
                        # convert to absolute path
                        new_ref_path = repo.to_native_path(ref.path)
                    else:
                        # convert to relative path
                        new_ref_path = utils.relpath(
                            workspace_path,
                            ref.path
                        )

                    if new_ref_path != unresolved_path:
                        logger.info("replacing reference: %s" % ref.path)
                        logger.info("replacing with: %s" % new_ref_path)
                        ref.replaceWith(new_ref_path)

        # *********************************************************************
        # Texture Files
        # replace with absolute path
        for image_file in pm.ls(type="file"):
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

            new_path = ""
            repo = self.find_repo(file_texture_path)

            if repo:
                if mode:
                    # convert to absolute
                    new_path = repo.to_native_path(file_texture_path)
                else:
                    # convert to relative
                    new_path = utils.relpath(
                        workspace_path,
                        file_texture_path,
                        "/", ".."
                    )


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
        for key in pm.workspace.fileRules:
            rule_path = pm.workspace.fileRules[key]
            full_path = os.path.join(path, rule_path).replace('\\', '/')
            logger.debug(full_path)
            try:
                os.makedirs(full_path)
            except OSError:
                # dir exists
                pass
