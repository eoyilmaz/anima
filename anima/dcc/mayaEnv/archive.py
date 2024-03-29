# -*- coding: utf-8 -*-

import glob
import os
import re
import shutil

from anima import logger
from anima.utils.archive import ArchiverBase

from stalker import Project, Task, Version


class Archiver(ArchiverBase):
    """Archive a Maya scene for external use.

    This utility class can flatten a maya scene including all its references in
    to a default maya project folder structure and can retrieve and connect the
    references to the original ones when the original file is returned.
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

    def create_default_project(self, path, name="DefaultProject"):
        """Creates default maya project structure along with a suitable
        workspace.mel file.

        :param str path: The path that the default project structure will be
          created.
        :param str name: The name of the archived project.

        :return:
        """
        project_path = super(Archiver, self).create_default_project(path, name)

        # create the workspace.mel
        workspace_mel_path = os.path.join(project_path, "workspace.mel")
        with open(workspace_mel_path, "w+") as f:
            f.writelines(self.default_workspace_content)

        return project_path

    def _extract_references(self, data=None):
        """returns the list of references in the given scene

        :param str data: The content of the maya scene file

        :return:
        """
        path_regex = r"\$REPO[\w\d\/_\.@\<\>]+"
        # so we have all the data
        # extract references
        ref_paths = list(set(re.findall(path_regex, data)))

        # also check for any paths that is starting with any of the $REPO
        # variable value
        for k in os.environ.keys():
            if k.startswith("REPO"):
                # consider this as a repository path and find all of the paths
                # starting with this value
                repo_path = os.environ[k]
                path_regex = r"{}[\w\d\/_\.@\<\>]+".format(repo_path)
                temp_ref_paths = list(set(re.findall(path_regex, data)))
                ref_paths += temp_ref_paths

        return list(
            filter(
                lambda x: os.path.splitext(x)[-1] not in self.exclude_mask, ref_paths
            )
        )

    def _move_file_and_fix_references(
        self, path, project_path, scenes_folder="", refs_folder=""
    ):
        """Move the file to the project path and move any references of it too.

        :param str path: The path of the scene file
        :param str project_path: The project path
        :param str scenes_folder: The scenes folder to store the original maya scene.
        :param str refs_folder: The references folder to replace reference paths with.
        :return list: returns a list of paths
        """
        # fix any env vars
        logger.debug("========================")
        logger.debug("path: {}".format(path))
        path = os.path.expandvars(path)

        # skip directories
        if os.path.isdir(path):
            logger.debug("Skipping directory: {}".format(path))
            return []

        # skip the file if it doesn't exist (unless it is a UDIM texture)
        if "<udim>" not in path and not os.path.isfile(path):
            # return early
            logger.debug("File doesn't exist: {}".format(path))
            return []

        original_file_name = os.path.basename(path)

        new_file_path = os.path.join(project_path, scenes_folder, original_file_name)

        scenes_folder_lut = {
            ".ma": "scenes/refs",
            # alembic cache
            ".abc": "scenes/refs",
            ".obj": "scenes/refs",
            # image files
            ".jpg": "sourceimages",
            ".png": "sourceimages",
            ".tif": "sourceimages",
            ".tiff": "sourceimages",
            ".tga": "sourceimages",
            ".exr": "sourceimages",
            ".hdr": "sourceimages",
            # RSProxy and arnold proxies
            ".rs": "sourceimages",
            ".ass": "sourceimages",
            # Audio and video files
            ".wav": "sound",
        }

        ref_paths = []
        # only get new ref paths for '.ma' files
        if path.endswith(".ma"):
            # read the data of the original file
            with open(path) as f:
                data = f.read()

            ref_paths = self._extract_references(data)
            # fix all reference paths
            for ref_path in ref_paths:
                ref_ext = os.path.splitext(ref_path)[-1]
                data = data.replace(
                    ref_path,
                    "{}/{}".format(
                        scenes_folder_lut.get(ref_ext, refs_folder),
                        os.path.basename(ref_path),
                    )
                )

            # now write all the data back to a new temp scene
            logger.debug("new_file_path: {}".format(new_file_path))
            with open(new_file_path, "w+") as f:
                f.write(data)
        else:
            # fix for UDIM texture paths
            # if the path contains <udim> find the other textures

            # dirty patch
            # move image files in to the sourceimages folder
            # along with the RedshiftProxy files
            file_extension = os.path.splitext(path)[-1]

            new_file_path = os.path.join(
                project_path,
                scenes_folder_lut.get(file_extension, refs_folder),
                original_file_name,
            )

            texture_file_extensions = [
                ".jpg",
                ".png",
                ".tif",
                ".tiff",
                ".tga",
                ".exr",
                ".hdr",
            ]

            if file_extension in texture_file_extensions:
                # get the rest of the UDIMs
                new_file_paths = []
                if "<udim>" in new_file_path:
                    image_file_paths = glob.glob(
                        path.replace("<udim>", "*")
                        .replace("u1_v1", "u*_v*")
                        .replace("U1_V1", "U*_V*")
                    )
                    if image_file_paths:
                        logger.debug("found UDIM textures:")
                else:
                    # TODO: Update this to also catch frames that doesn't start from
                    #       1001.
                    image_file_paths = glob.glob(
                        path.replace(".1001.", ".*.")
                    )

                for image_file_path in image_file_paths:
                    logger.debug(image_file_path)
                    image_file_name = os.path.basename(image_file_path)
                    new_image_file_path = os.path.join(
                        project_path,
                        scenes_folder_lut.get(file_extension, refs_folder),
                        image_file_name,
                    )
                    new_file_paths.append((image_file_path, new_image_file_path))
            elif file_extension == ".rs":
                # # this could be a .rs cache file series
                # new_file_paths = []
                # rs_cache_files = glob.glob(
                #     path.
                # )
                # TODO: Implement this.
                new_file_paths = [(path, new_file_path)]
            else:
                new_file_paths = [(path, new_file_path)]

            # just copy the file
            for original_file_path, new_file_path in new_file_paths:
                logger.debug("new_file_path: {}".format(new_file_path))
                try:
                    shutil.copy(original_file_path, new_file_path)
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
        path_regex = r'(\-typ\s)([\w\"\s]*\s)(")(.*scenes/.*[\w\d\/_\.@]+)'
        # so we have all the data
        # extract references
        ref_paths = [r[3] for r in re.findall(path_regex, data)]

        return ref_paths

    @classmethod
    def bind_to_original(cls, path, project=None):
        """Binds all the references to the original Versions in the repository.

        Given a maya scene file, this method will find the originals of the
        references in the database and will replace them with the originals.

        :param str path: The path of the maya file.
        :param Project project: If given the path will be searched among the given
          project Versions.

        :return:
        """
        # TODO: This will not fix the sound or texture files, that is anything
        #       other than a maya scene file.
        # get all reference paths
        with open(path, "rb") as f:
            data = f.read()

        # replace any non utf-8 compatible characters
        char_lut = {
            # ANSI Turkish Characters read as utf-8
            b"\xe7": b"c",
            b"\xc7": b"C",
            b"\xf0": b"g",
            b"\xd0": b"G",
            b"\xfd": b"i",
            b"\xdd": b"I",
            b"\xf6": b"o",
            b"\xd6": b"O",
            b"\xfe": b"s",
            b"\xde": b"S",
            b"\xfc": b"u",
            b"\xdc": b"U",
        }
        for char in char_lut:
            data = data.replace(char, char_lut[char])

        # now encode the data to utf-8
        data = data.decode("utf-8")

        unknown_references = []
        ref_paths = cls._extract_local_references(data)
        for ref_path in ref_paths:
            ref_file_name = os.path.basename(ref_path)
            logger.debug(f"ref_file_name: {ref_file_name}")

            # try to find a corresponding Stalker Version instance with it
            versions = []
            if project is not None:
                # use the given project
                versions = (
                    Version.query.join(Task, Version.task_id == Task.id)
                    .filter(Task.project == project)
                    .filter(Version.full_path.endswith(ref_file_name))
                    .all()
                )

            if not versions:
                print("no version found in the same project, "
                      "looking in to other projects")
                # try to look in to all projects, order by Project.date_created
                versions = (
                    Version.query.join(Task, Version.task_id == Task.id)
                    .join(Project, Task.project_id == Project.id)
                    .filter(Version.full_path.endswith(ref_file_name))
                    .order_by(Project.date_created)
                    .all()
                )

            version = None
            for v in versions:
                # check the whole filename
                if v.filename == ref_file_name:
                    version = v
                    break

            if version:
                # replace it
                data = data.replace(ref_path, version.full_path)
            else:
                # update unknown references
                unknown_references.append(ref_path)

        if len(ref_paths):
            # save the file over itself
            with open(path, "w+") as f:
                f.write(data)

        return unknown_references
