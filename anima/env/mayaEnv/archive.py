# -*- coding: utf-8 -*-
# Copyright (c) 2012-2014, Anima Istanbul
#
# This module is part of anima-tools and is released under the BSD 2
# License: http://www.opensource.org/licenses/BSD-2-Clause
import os
import tempfile
import logging


import pymel.core as pm

logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)


class Archiver(object):
    """Archives a Maya scene for external use.

    This utility class can flatten a maya scene including all its references in
    to a default maya project folder structure and can retrieve and connect the
    references to the original ones when the files is returned back.
    """

    default_workspace_content = """// Anima Archiver Default Project Definition

workspace -fr "translatorData" "data";
workspace -fr "offlineEdit" "scenes/edits";
workspace -fr "renderData" "renderData";
workspace -fr "scene" "scenes";
workspace -fr "3dPaintTextures" "sourceimages/3dPaintTextures";
workspace -fr "eps" "data";
workspace -fr "OBJexport" "data";
workspace -fr "mel" "scripts";
workspace -fr "furShadowMap" "renderData/fur/furShadowMap";
workspace -fr "particles" "cache/particles";
workspace -fr "audio" "sound";
workspace -fr "scripts" "scripts";
workspace -fr "sound" "sound";
workspace -fr "DXF_FBX export" "data";
workspace -fr "furFiles" "renderData/fur/furFiles";
workspace -fr "depth" "renderData/depth";
workspace -fr "autoSave" "autosave";
workspace -fr "furAttrMap" "renderData/fur/furAttrMap";
workspace -fr "diskCache" "data";
workspace -fr "fileCache" "cache/nCache";
workspace -fr "ASS Export" "data";
workspace -fr "FBX export" "data";
workspace -fr "sourceImages" "sourceimages";
workspace -fr "FBX" "data";
workspace -fr "DAE_FBX export" "data";
workspace -fr "movie" "movies";
workspace -fr "Alembic" "data";
workspace -fr "DAE_FBX" "data";
workspace -fr "iprImages" "renderData/iprImages";
workspace -fr "mayaAscii" "scenes";
workspace -fr "furImages" "renderData/fur/furImages";
workspace -fr "furEqualMap" "renderData/fur/furEqualMap";
workspace -fr "illustrator" "data";
workspace -fr "DXF_FBX" "data";
workspace -fr "mayaBinary" "scenes";
workspace -fr "move" "data";
workspace -fr "images" "images";
workspace -fr "fluidCache" "cache/nCache/fluid";
workspace -fr "clips" "clips";
workspace -fr "ASS" "data";
workspace -fr "OBJ" "data";
workspace -fr "templates" "assets";
workspace -fr "shaders" "renderData/shaders";
"""

    default_project_structure = """assets
autosave
cache
cache/nCache
cache/nCache/fluid
cache/particles
clips
data
images
movies
renderData
renderData/depth
renderData/fur
renderData/fur/furAttrMap
renderData/fur/furEqualMap
renderData/fur/furFiles
renderData/fur/furImages
renderData/fur/furShadowMap
renderData/iprImages
renderData/shaders
scenes
scenes/edits
scripts
sound
sourceimages
sourceimages/3dPaintTextures"""

    @classmethod
    def create_default_project(cls, path, name='DefaultProject'):
        """Creates default maya project structure along with a suitable
        workspace.mel file.

        :param str path: The path that the default project structure will be
          created.

        :return:
        """
        project_path = os.path.join(path, name)

        # lets create the structure
        for dir_name in cls.default_project_structure.split('\n'):
            dir_path = os.path.join(project_path, dir_name)
            try:
                os.makedirs(dir_path)
            except OSError:
                pass

        # create the workspace.mel
        workspace_mel_path = os.path.join(project_path, 'workspace.mel')
        with open(workspace_mel_path, 'w+') as f:
            f.writelines(cls.default_workspace_content)

        return project_path

    @classmethod
    def flatten(cls, path, project_name='DefaultProject'):
        """Flattens the given maya scene in to a new default project and
        returns the project path.

        It will also flatten all the referenced files, textures, image planes
        and Arnold Scene Source files.

        :param path: The path to the file which wanted to be flattened
        :return:
        """
        current_workspace_path = pm.workspace.getcwd()

        # create a new Default Project
        tempdir = tempfile.gettempdir()

        default_project_path = cls.create_default_project(path=tempdir,
                                                          name=project_name)
        logger.debug(
            'creating new default project at: %s' % default_project_path
        )

        original_file_name = os.path.basename(path)
        logger.debug('original_file_name: %s' % original_file_name)

        # open the given maya scene
        pm.openFile(path, force=True, loadReferenceDepth='all')

        all_refs = pm.listReferences(recursive=True)
        if len(all_refs):
            # There are references
            # so copy them all starting from the deepest one
            logger.debug('There are references in the original file!')

            # create a reference resolution
            logger.debug('Creating reference resolution')
            reference_resolution = {}

            all_ref_paths = [ref.path for ref in all_refs]

            for ref_path in reversed(all_ref_paths):
                # if this reference is already resolved skip it
                if ref_path in reference_resolution:
                    continue

                pm.openFile(ref_path, force=True, loadReferenceDepth='all')
                # check their first level references
                # they should be on the reference resolution list
                for c_ref in pm.listReferences():
                    if c_ref.path in reference_resolution:
                        c_ref.replaceWith(reference_resolution[c_ref.path])

                # save it to the DefaultProject/scenes
                new_ref_path = os.path.join(
                    default_project_path,
                    'scenes',
                    os.path.basename(ref_path)
                )
                logger.debug('new_ref_path: %s' % new_ref_path)

                pm.saveAs(new_ref_path)

                # add it to the reference_resolution
                reference_resolution[ref_path] = new_ref_path

            # re open the original file
            logger.debug('re-opening the original file at: %s' % path)
            pm.openFile(path, force=True)

            # replace all first level references
            logger.debug('replacing references!')
            for c_ref in pm.listReferences():
                original_ref_path = c_ref.path
                if original_ref_path in reference_resolution:
                    resolved_ref_path = reference_resolution[c_ref.path]
                    logger.debug(
                        'found reference: %s -> %s' %
                        (original_ref_path, resolved_ref_path)
                    )
                    c_ref.replaceWith(resolved_ref_path)
                else:
                    logger.devug(
                        'no reference resolution for: %s' % original_ref_path
                    )

        # update the workspace
        pm.workspace.chdir(default_project_path)

        # and save it to the scenes folder of the default project
        pm.saveAs(
            os.path.join(default_project_path, 'scenes', original_file_name),
            type='mayaAscii'
        )

        # renew the scene
        pm.newFile(force=True)

        # restore the current workspace
        try:
            pm.workspace.chdir(current_workspace_path)
        except RuntimeError:
            # the current_workspace_path is invalid
            # no problem
            pass

        return default_project_path

    @classmethod
    def archive(cls, path):
        """Creates a zip file containing the given directory.

        :param path: Path to the archived directory.
        :return:
        """
        import zipfile
        dir_name = os.path.basename(path)
        zip_path = os.path.join(tempfile.gettempdir(), '%s.zip' % dir_name)

        parent_path = os.path.dirname(path) + '/'

        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as z:
            for current_dir_path, dir_names, file_names in os.walk(path):
                for dir_name in dir_names:
                    dir_path = os.path.join(current_dir_path, dir_name)
                    arch_path = dir_path[len(parent_path):]
                    z.write(dir_path, arch_path)

                for file_name in file_names:
                    file_path = os.path.join(current_dir_path, file_name)
                    arch_path = file_path[len(parent_path):]
                    z.write(file_path, arch_path)

        return zip_path

    @classmethod
    def bind_to_original(cls, path):
        """Binds all the references to the original Versions in the repository.

        Given a maya scene file, this method will find the originals of the
        references in the database and will replace them with the originals.

        :param str path: The path of the maya file.

        :return:
        """
        pass
