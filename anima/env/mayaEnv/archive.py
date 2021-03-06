# -*- coding: utf-8 -*-
# Copyright (c) 2012-2020, Anima Istanbul
#
# This module is part of anima and is released under the MIT
# License: http://www.opensource.org/licenses/MIT
import os
import re

from anima import logger
from anima.utils.archive import ArchiverBase


class Archiver(ArchiverBase):
    """Archives a Maya scene for external use.

    This utility class can flatten a maya scene including all its references in
    to a default maya project folder structure and can retrieve and connect the
    references to the original ones when the original file is returned back.
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

    def create_default_project(self, path, name='DefaultProject'):
        """Creates default maya project structure along with a suitable
        workspace.mel file.

        :param str path: The path that the default project structure will be
          created.
        :param str name: The name of the archived project.

        :return:
        """
        project_path = super(Archiver, self).create_default_project(path, name)

        # create the workspace.mel
        workspace_mel_path = os.path.join(project_path, 'workspace.mel')
        with open(workspace_mel_path, 'w+') as f:
            f.writelines(self.default_workspace_content)

        return project_path

    def _extract_references(self, data=None):
        """returns the list of references in the given scene

        :param str data: The content of the maya scene file

        :return:
        """
        import os
        import re

        path_regex = r'\$REPO[\w\d\/_\.@]+'
        # so we have all the data
        # extract references
        ref_paths = re.findall(path_regex, data)

        # also check for any paths that is starting with any of the $REPO
        # variable value
        for k in os.environ.keys():
            if k.startswith('REPO'):
                # consider this as a repository path and find all of the paths
                # starting with this value
                repo_path = os.environ[k]
                path_regex = r'\%s[\w\d\/_\.@]+' % repo_path
                temp_ref_paths = re.findall(path_regex, data)
                ref_paths += temp_ref_paths

        return filter(lambda x: os.path.splitext(x)[1] not in self.exclude_mask, ref_paths)

    def _move_file_and_fix_references(self, path, project_path, scenes_folder='', refs_folder=''):
        """Moves the given file to the given project path and moves any references of it too

        :param str path: The path of the scene file
        :param str project_path: The project path
        :param str scenes_folder: The scenes folder to store the original maya scene.
        :param str refs_folder: The references folder to replace reference paths with.
        :return list: returns a list of paths
        """
        import os
        import shutil

        # fix any env vars
        path = os.path.expandvars(path)

        original_file_name = os.path.basename(path)
        logger.debug("original_file_name: %s" % original_file_name)

        new_file_path = os.path.join(project_path, scenes_folder, original_file_name)
        logger.debug("new_file_path: %s" % new_file_path)

        scenes_folder_lut = {
            '.ma': 'scenes/refs',

            # alembic cache
            '.abc': 'scenes/refs',

            # image files
            '.jpg': 'sourceimages',
            '.png': 'sourceimages',
            '.tif': 'sourceimages',
            '.tiff': 'sourceimages',
            '.tga': 'sourceimages',
            '.exr': 'sourceimages',
            '.hdr': 'sourceimages',

            # RSProxy and arnold proxies
            '.rs': 'sourceimages',
            '.ass': 'sourceimages',
        }

        ref_paths = []
        # skip the file if it doesn't exist
        if not os.path.exists(path):
            # return early
            return ref_paths

        # only get new ref paths for '.ma' files
        if path.endswith('.ma'):
            # read the data of the original file
            with open(path) as f:
                data = f.read()

            ref_paths = self._extract_references(data)
            # fix all reference paths
            for ref_path in ref_paths:
                ref_ext = os.path.splitext(ref_path)[-1]
                data = data.replace(
                    ref_path,
                    '%s/%s' % (
                        scenes_folder_lut.get(ref_ext, refs_folder),
                        os.path.basename(ref_path)
                    )
                )

            # now write all the data back to a new temp scene
            with open(new_file_path, 'w+') as f:
                f.write(data)
        else:
            # fix for UDIM texture paths
            # if the path contains 1001 or u1_v1 than find the other
            # textures

            # dirty patch
            # move image files in to the sourceimages folder
            # along with the RedshiftProxy files
            file_extension = os.path.splitext(path)[1]

            new_file_path = \
                os.path.join(
                    project_path,
                    scenes_folder_lut.get(
                        file_extension,
                        refs_folder
                    ),
                    original_file_name
                )

            import glob
            new_file_paths = [new_file_path]
            if '1001' in new_file_path or 'u1_v1' in new_file_path.lower():
                # get the rest of the textures
                new_file_paths = glob.glob(
                    new_file_path
                    .replace('1001', '*')
                    .replace('u1_v1', 'u*_v*')
                    .replace('U1_V1', 'U*_V*')
                )
                if new_file_paths:
                    logger.debug("found UDIM textures:")

                for p in new_file_paths:
                    logger.debug(p)

            # just copy the file
            for new_file_path in new_file_paths:
                logger.debug("%s -> %s" % (path, new_file_path))
                try:
                    shutil.copy(path, new_file_path)
                except IOError:
                    pass

        return ref_paths

    @classmethod
    def _extract_local_references(cls, data):
        """returns the list of local references (references that are referenced
        from scenes/refs folder) in the given maya file

        :param str data: The content of the maya scene file

        :return:
        """
        path_regex = r'scenes/refs/[\w\d\/_\.@]+'
        # so we have all the data
        # extract references
        ref_paths = re.findall(path_regex, data)

        return ref_paths

    @classmethod
    def bind_to_original(cls, path):
        """Binds all the references to the original Versions in the repository.

        Given a maya scene file, this method will find the originals of the
        references in the database and will replace them with the originals.

        :param str path: The path of the maya file.

        :return:
        """
        # TODO: This will not fix the sound or texture files, that is anything
        #       other than a maya scene file.
        # get all reference paths
        with open(path) as f:
            data = f.read()

        ref_paths = cls._extract_local_references(data)
        for ref_path in ref_paths:
            ref_file_name = os.path.basename(ref_path)

            # try to find a corresponding Stalker Version instance with it
            from stalker import Version
            version = Version.query\
                .filter(Version.full_path.endswith(ref_file_name))\
                .first()

            if version:
                # replace it
                data = data.replace(
                    ref_path,
                    version.full_path
                )

        if len(ref_paths):
            # save the file over itself
            with open(path, 'w+') as f:
                f.write(data)
