# -*- coding: utf-8 -*-
# Copyright (c) 2012-2014, Anima Istanbul
#
# This module is part of anima-tools and is released under the BSD 2
# License: http://www.opensource.org/licenses/BSD-2-Clause
import os
import tempfile
import logging
import re

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
scenes/refs
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
        current_workspace_path = pm.workspace.path

        # create a new Default Project
        tempdir = tempfile.gettempdir()

        default_project_path = cls.create_default_project(path=tempdir,
                                                          name=project_name)
        logger.debug(
            'creating new default project at: %s' % default_project_path
        )

        original_file_name = os.path.basename(path)
        logger.debug('original_file_name: %s' % original_file_name)

        # update the workspace
        # do it as early as possible to be able to set unresolved paths
        # correctly
        pm.workspace.open(default_project_path)

        # open the given maya scene
        # any references that uses relative paths will not work at this moment
        # but hopefully we are using absolute paths in Anima
        #
        # check if the scene is already open
        if pm.sceneName() != path:
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
                new_ref_unresolved_path = os.path.join(
                    'scenes/refs',
                    os.path.basename(ref_path)
                )
                new_ref_path = os.path.join(
                    default_project_path,
                    new_ref_unresolved_path
                )
                logger.debug('new_ref_path: %s' % new_ref_path)

                pm.saveAs(new_ref_path)

                # add it to the reference_resolution
                reference_resolution[ref_path] = new_ref_unresolved_path

            # re open the original file
            logger.debug('re-opening the original file at: %s' % path)
            pm.openFile(path, force=True)

            logger.debug(
                'reference_resolution: {0:s}'.format(reference_resolution)
            )

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

        # and save it to the scenes folder of the default project
        pm.saveAs(
            os.path.join(default_project_path, 'scenes', original_file_name),
            type='mayaAscii'
        )

        # renew the scene
        pm.newFile(force=True)

        # restore the current workspace
        pm.workspace.open(current_workspace_path)

        return default_project_path

    @classmethod
    def flatten_external(cls, path, project_name='DefaultProject'):
        """Flattens the given maya scene in to a new default project externally
        that is without opening it and returns the project path.

        It will also flatten all the referenced files, textures, image planes
        and Arnold Scene Source files.

        :param path: The path to the file which wanted to be flattened
        :return:
        """
        # create a new Default Project
        tempdir = tempfile.gettempdir()

        default_project_path = cls.create_default_project(path=tempdir,
                                                          name=project_name)
        logger.debug(
            'creating new default project at: %s' % default_project_path
        )

        ref_paths = cls._move_file_and_fix_references(path, default_project_path)
        while len(ref_paths):
            ref_path = ref_paths.pop(0)
            new_ref_paths = \
                cls._move_file_and_fix_references(
                    ref_path,
                    default_project_path,
                    scenes_folder='scenes/refs'
                )

            # extend ref_paths with new ones
            for new_ref_path in new_ref_paths:
                if new_ref_path not in ref_paths:
                    ref_paths.append(new_ref_path)

        return default_project_path

    @classmethod
    def _move_file_and_fix_references(cls, path, project_path,
                                      scenes_folder='scenes',
                                      refs_folder='scenes/refs'):
        """Moves the given maya file to the given project path and moves any
        references of it to

        :param str path: The path of the maya file
        :param str project_path: The project path
        :param str scenes_folder: The scenes folder to store the original maya
          scene.
        :param str refs_folder: The references folder to replace reference
          paths with.
        :return list: returns a list of paths
        """
        #reference_resolution = {}
        original_file_name = os.path.basename(path)
        logger.debug('original_file_name: %s' % original_file_name)

        # read the data of the original file
        with open(os.path.expandvars(path)) as f:
            data = f.read()

        ref_paths = cls._extract_references(data)
        print 'extracted reference paths: %s' % ref_paths
        # fix all reference paths
        for ref_path in ref_paths:
            data = data.replace(
                ref_path,
                '%s/%s' % (refs_folder, os.path.basename(ref_path))
            )

        # now write all the data back to a new temp scene
        temp_file_path = \
            os.path.join(project_path, scenes_folder, original_file_name)

        with open(temp_file_path, 'w+') as f:
            f.write(data)

        return ref_paths

    @classmethod
    def _extract_references(cls, data):
        """returns the list of references in the given maya file

        :param str data: The content of the maya scene file

        :return:
        """
        # path_regex = r'\$REPO[\w\./]+'
        split_regex = r'\s'

        # so we have all the data
        # extract references
        ref_paths = []
        lines = data.split(';\n')
        for line in lines:
            if line.startswith('file -r'):
                ref_path = re.split(split_regex, line)[-1].replace('"', '')
                # and store it
                ref_paths.append(ref_path)

        return ref_paths

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
        # open the given path
        # but do not load any references
        pm.openFile(path, force=True, loadReferenceDepth='none')

        from stalker import Version

        # list all references
        for ref in pm.listReferences():
            ref_file_name = os.path.basename(ref.unresolvedPath())

            # try to find a corresponding Stalker Version instance with it
            version = Version.query\
                .filter(Version.full_path.endswith(ref_file_name))\
                .first()
            if version:
                # replace it
                ref.replaceWith(version.absolute_full_path)
                # leave it to anima.env.mayaEnv to replace the external paths

        # finally replace absolute paths with repo relative paths
        from anima.env.mayaEnv import Maya
        m_env = Maya()
        m_env.replace_external_paths()

        # save the file over itself
        pm.saveFile(force=True)
