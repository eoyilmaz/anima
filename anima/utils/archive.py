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

from anima.utils.progress import ProgressManagerFactory


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
        pm = ProgressManagerFactory.get_progress_manager()
        progress_caller = pm.register(max_iteration=len(paths), title="Flatten Paths")

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
            progress_caller.step(message=os.path.basename(path))

        ref_paths = list(set(ref_paths))
        progress_caller = pm.register(
            max_iteration=len(ref_paths), title="Scan References"
        )

        while len(ref_paths):
            ref_path = ref_paths.pop(0)
            # report progress upfront
            progress_caller.step(message=os.path.basename(ref_path))

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
                    # update progress caller step size
                    progress_caller.max_steps += 1

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

        max_iteration = 0
        for current_dir_path, dir_names, file_names in os.walk(path):
            max_iteration += len(dir_names)
            max_iteration += len(file_names)

        pm = ProgressManagerFactory.get_progress_manager()
        progress_caller = pm.register(
            max_iteration=max_iteration, title="Create ZIP File"
        )

        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED, allowZip64=True) as z:
            for current_dir_path, dir_names, file_names in os.walk(path):
                for dir_name in dir_names:
                    dir_path = os.path.join(current_dir_path, dir_name)
                    arch_path = dir_path[len(parent_path) :]
                    z.write(dir_path, arch_path)
                    progress_caller.step(message=dir_name)

                for file_name in file_names:
                    file_path = os.path.join(current_dir_path, file_name)
                    arch_path = file_path[len(parent_path) :]
                    z.write(file_path, arch_path)
                    progress_caller.step(message=file_name)

        return zip_path


def archive_versions(
    versions,
    archiver,
    project_name=None,
    output_path=None,
    tempdir=None,
    prompt=True,
):
    """Archive the given versions.

    Args:
        versions (List[stalker.Version]): A ``stalker.models.version.Version`` instance
            to get information about the project etc.
        archiver (ArchiverBase): The ``anima.utils.archive.ArchiverBase`` derivative
            properly implemented for the current DCC.
        project_name (Union[None, str]): The project name, if skipped a project name
            will be generated from the first version in the versions list.
        output_path (Union[None, str]): The output folder path, if skipped an output
            path will be generated from the first version in the versions list.
        tempdir (Union[None, str]): The tempdir to use. If not given a path is going to
            be asked to the user.
        prompt (bool): If True, a final confirmation will be asked to the user.
        progress_caller (ProgressCaller): A ProgessCaller instance to report the
            progress. If given archive_version will report the progress through that
            instance.

    Returns:
        str: The ZIP file path.
    """

    from anima.ui.lib import QtWidgets

    if False:
        from PySide6 import QtWidgets

    if not versions:
        QtWidgets.QMessageBox.critical(None, "Error!", "No version is given!")
        return

    # before doing anything ask it to the user
    if prompt:
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

    if not tempdir or not isinstance(tempdir, str) or tempdir == "":
        input_dialog = QtWidgets.QInputDialog(None)
        tempdir, ok = input_dialog.getText(
            None,
            "Temporary dir to use?",
            "Please choose a temporary directory:",
            QtWidgets.QLineEdit.Normal,
            tempfile.gettempdir(),
        )

    # use the first version to determine the ZIP file path
    if not project_name or not isinstance(project_name, str):
        project_name = os.path.splitext(
            os.path.basename(versions[0].absolute_full_path)
        )[0]

    if not output_path or not isinstance(output_path, str):
        output_path = versions[0].absolute_path

    paths = []
    data_links = []
    for version in versions:
        task = version.task
        paths.append(version.absolute_full_path)
        version_upload_link = "%s/tasks/%s/versions/list" % (
            anima.defaults.stalker_server_external_address,
            task.id,
        )
        request_review_link = "%s/tasks/%s/view" % (
            anima.defaults.stalker_server_external_address,
            task.id,
        )
        data_link = (
            "--------------------\n"
            "Version Upload Link: {}\n"
            "Request Review Link: {}\n".format(version_upload_link, request_review_link)
        )
        data_links.append(data_link)

    project_path = archiver.flatten(
        paths,
        project_name=project_name,
        tempdir=tempdir,
    )

    # append link file
    stalker_link_file_path = os.path.join(project_path, "scenes/stalker_links.txt")

    with open(stalker_link_file_path, "w+") as f:
        f.write("\n".join(data_links))

    zip_path = archiver.archive(project_path, tempdir=tempdir)
    new_zip_path = os.path.join(output_path, os.path.basename(zip_path))

    # move the zip right beside the original version file
    shutil.move(zip_path, new_zip_path)

    # remote the temp project_path
    shutil.rmtree(project_path, ignore_errors=True)

    # open the zip file in browser
    open_browser_in_location(new_zip_path)

    return new_zip_path
