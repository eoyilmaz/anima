# -*- coding: utf-8 -*-
"""Archiver utilities."""
import os
import shutil
import tempfile
import zipfile

import anima
from anima import logger
from anima.utils import open_browser_in_location

from stalker import Repository


class ArchiverBase(object):
    """The base class for Archivers."""

    default_project_structure = ""

    def __init__(self, exclude_mask=None, recursive_search=False):
        if exclude_mask is None:
            exclude_mask = []
        self.exclude_mask = exclude_mask
        self.recursive_search = recursive_search

    @classmethod
    def create_default_project(cls, path, name="DefaultProject"):
        """Create default project structure.

        Args:
            path (str): The path that the default project structure will be created.
            name (str): The name of the archived project.

        Returns:
            str: New project path.
        """
        project_path = os.path.join(path, name)

        # let's create the structure
        for dir_name in cls.default_project_structure.split("\n"):
            dir_path = os.path.join(project_path, dir_name.strip())
            try:
                os.makedirs(dir_path)
            except OSError:
                pass

        return project_path

    def flatten(self, paths, project_name="DefaultProject", tempdir=None):
        """Flatten the given scene in to a new default project.

        It will also flatten all the referenced files, textures, image planes,
        Redshift Proxy files.

        Args:
            paths (List[str]): A list of paths to the filed which wanted to be
                flattened.
            project_name (str): The new project name.
            tempdir (str): The temporary dir to flatten the project to, the default is
                ``tempfile.gettempdir()``.

        Returns:
            str: The project paths.
        """
        # create a new Default Project
        if not tempdir:
            tempdir = tempfile.gettempdir()

        all_repos = Repository.query.all()

        default_project_path = self.create_default_project(
            path=tempdir, name=project_name
        )

        logger.debug("creating new default project at: %s" % default_project_path)

        ref_paths = []
        for path in paths:
            ref_paths += self._move_file_and_fix_references(
                path, default_project_path, scenes_folder="scenes"
            )
        ref_paths = list(set(ref_paths))

        while len(ref_paths):
            ref_path = ref_paths.pop(0)

            if (
                self.exclude_mask
                and os.path.splitext(ref_path)[-1] in self.exclude_mask
            ):
                logger.debug("skipping: %s" % ref_path)
                continue

            # fix different OS paths
            for repo in all_repos:
                if repo.is_in_repo(ref_path):
                    ref_path = repo.to_native_path(ref_path)

            new_ref_paths = self._move_file_and_fix_references(
                ref_path, default_project_path, scenes_folder="scenes/refs"
            )

            # extend ref_paths with new ones
            for new_ref_path in new_ref_paths:
                if new_ref_path not in ref_paths:
                    ref_paths.append(new_ref_path)

        return default_project_path

    def _move_file_and_fix_references(
        self, path, project_path, scenes_folder="", refs_folder=""
    ):
        """Move the file to the project path and moves any references of it too.

        Args:
            path (str): The path of the scene file.
            project_path (str): The project path.
            scenes_folder (str): The scenes folder to store the original maya scene.
            refs_folder (str): The references folder to replace reference paths with.

        Raises:
            NotImplementedError: This needs to be implemented in the derived class.
        """
        # This needs to be implemented by the environment
        raise NotImplementedError(
            "This method needs to be implemented by the derived class"
        )

    def _extract_references(self):
        """Return the list of references in the given scene.

        Raises:
            NotImplementedError: This needs to be implemented in the derived class.
        """
        raise NotImplementedError(
            "This method needs to be implemented by the derived class"
        )

    @classmethod
    def archive(cls, path, tempdir=None):
        """Create a zip file containing the given directory.

        Args:
            path (str): Path to the archived directory.
            tempdir (str): The temporary dir to use for ZIP creation, the default value
                is ``tempfile.gettempdir()``.

        Returns:
            str: ZIP file path.
        """
        if not tempdir:
            tempdir = tempfile.gettempdir()

        dir_name = os.path.basename(path)
        zip_path = os.path.join(tempdir, "%s.zip" % dir_name)

        parent_path = os.path.dirname(path) + "/"

        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED, allowZip64=True) as z:
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


def archive_current_scene(version, archiver):
    """Archive current scene.

    Args:
        version (stalker.Version): A ``stalker.models.version.Version`` instance to get
            information about the project etc.
        archiver (ArchiverBase): The ``anima.utils.archive.ArchiverBase`` derivative
            properly implemented for the current DCC.
    """
    from anima.ui.lib import QtWidgets

    # before doing anything ask it to the user
    answer = QtWidgets.QMessageBox.question(
        None,
        "Do Archive?",
        "This will create a ZIP file containing"
        "<br>the current scene and all its references"
        "<br>"
        "Is that OK?",
        QtWidgets.QMessageBox.Yes,
        QtWidgets.QMessageBox.No,
    )
    if answer == QtWidgets.QMessageBox.No:
        return

    input_dialog = QtWidgets.QInputDialog(None)
    tempdir, ok = input_dialog.getText(
        None,
        "Temporary dir to use?",
        "Please choose a temporary directory:",
        QtWidgets.QLineEdit.Normal,
        tempfile.gettempdir(),
    )

    if version:
        path = version.absolute_full_path
        task = version.task
        # project_name = version.nice_name
        project_name = os.path.splitext(os.path.basename(version.absolute_full_path))[0]
        project_path = archiver.flatten(
            [path], project_name=project_name, tempdir=tempdir
        )

        # append link file
        stalker_link_file_path = os.path.join(project_path, "scenes/stalker_links.txt")
        version_upload_link = "%s/tasks/%s/versions/list" % (
            anima.defaults.stalker_server_external_address,
            task.id,
        )
        request_review_link = "%s/tasks/%s/view" % (
            anima.defaults.stalker_server_external_address,
            task.id,
        )
        with open(stalker_link_file_path, "w+") as f:
            f.write(
                "Version Upload Link: %s\n"
                "Request Review Link: %s\n" % (version_upload_link, request_review_link)
            )
        zip_path = archiver.archive(project_path, tempdir=tempdir)
        new_zip_path = os.path.join(version.absolute_path, os.path.basename(zip_path))

        # move the zip right beside the original version file
        shutil.move(zip_path, new_zip_path)

        # open the zip file in browser
        open_browser_in_location(new_zip_path)
