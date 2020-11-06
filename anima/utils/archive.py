# -*- coding: utf-8 -*-
# Copyright (c) 2012-2020, Erkan Ozgur Yilmaz
#
# This module is part of anima and is released under the MIT
# License: http://www.opensource.org/licenses/MIT
from anima import logger


class ArchiverBase(object):
    """The base class for Archivers
    """
    default_project_structure = ""

    def __init__(self, exclude_mask=None, recursive_search=False):
        if exclude_mask is None:
            exclude_mask = []
        self.exclude_mask = exclude_mask
        self.recursive_search = recursive_search

    @classmethod
    def create_default_project(cls, path, name='DefaultProject'):
        """Creates default maya project structure along with a suitable
        workspace.mel file.

        :param str path: The path that the default project structure will be
          created.
        :param str name: The name of the archived project.

        :return:
        """
        import os
        project_path = os.path.join(path, name)

        # lets create the structure
        for dir_name in cls.default_project_structure.split('\n'):
            dir_path = os.path.join(project_path, dir_name.strip())
            try:
                os.makedirs(dir_path)
            except OSError:
                pass

        return project_path

    def flatten(self, path, project_name='DefaultProject'):
        """Flattens the given scene in to a new default project.

        It will also flatten all the referenced files, textures, image planes,
        Redshift Proxy files.

        :param path: The path to the file which wanted to be flattened.
        :param project_name: The new project name.
        :return:
        """
        # create a new Default Project
        import tempfile
        import os

        tempdir = tempfile.gettempdir()
        from stalker import Repository
        all_repos = Repository.query.all()

        default_project_path = \
            self.create_default_project(path=tempdir, name=project_name)

        logger.debug(
            'creating new default project at: %s' % default_project_path
        )

        ref_paths = \
            self._move_file_and_fix_references(path, default_project_path, scenes_folder='scenes')

        while len(ref_paths):
            ref_path = ref_paths.pop(0)

            if self.exclude_mask \
                    and os.path.splitext(ref_path)[1] in self.exclude_mask:
                logger.debug('skipping: %s' % ref_path)
                continue

            # fix different OS paths
            for repo in all_repos:
                if repo.is_in_repo(ref_path):
                    ref_path = repo.to_native_path(ref_path)

            new_ref_paths = \
                self._move_file_and_fix_references(ref_path, default_project_path, scenes_folder='scenes/refs')

            # extend ref_paths with new ones
            for new_ref_path in new_ref_paths:
                if new_ref_path not in ref_paths:
                    ref_paths.append(new_ref_path)

        return default_project_path

    def _move_file_and_fix_references(self, path, project_path, scenes_folder='', refs_folder=''):
        """Moves the given file to the given project path and moves any
        references of it too

        :param str path: The path of the scene file
        :param str project_path: The project path
        :param str scenes_folder: The scenes folder to store the original maya scene.
        :param str refs_folder: The references folder to replace reference paths with.
        :return list: returns a list of paths
        """
        # This needs to be implemented by the environment
        raise NotImplementedError("This method needs to be implemented by the environment")

    def _extract_references(self, data):
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

        new_ref_paths = []
        for ref_path in ref_paths:
            if os.path.splitext(ref_path)[1] not in self.exclude_mask:
                new_ref_paths.append(ref_path)
        ref_paths = new_ref_paths

        return ref_paths

    @classmethod
    def archive(cls, path):
        """Creates a zip file containing the given directory.

        :param path: Path to the archived directory.
        :return:
        """
        import zipfile
        import os
        import tempfile
        dir_name = os.path.basename(path)
        zip_path = os.path.join(tempfile.gettempdir(), '%s.zip' % dir_name)

        parent_path = os.path.dirname(path) + '/'

        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED, allowZip64=True) as z:
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
    """Helper function for archiver

    :param version: A ``stalker.models.version.Version`` instance to get information about the project and etc.
    :param archiver: The ``anima.utils.archive.ArchiverBase`` derivative properly implemented for the current environment.
    """
    import os
    import shutil
    import anima
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
        QtWidgets.QMessageBox.No
    )
    if answer == QtWidgets.QMessageBox.No:
        return

    if version:
        path = version.absolute_full_path
        task = version.task
        if False:
            from stalker import Version, Task
            assert (isinstance(version, Version))
            assert (isinstance(task, Task))
        # project_name = version.nice_name
        project_name = os.path.splitext(
            os.path.basename(
                version.absolute_full_path
            )
        )[0]
        project_path = archiver.flatten(path, project_name=project_name)

        # append link file
        stalker_link_file_path = \
            os.path.join(project_path, 'scenes/stalker_links.txt')
        version_upload_link = '%s/tasks/%s/versions/list' % (
            anima.defaults.stalker_server_external_address,
            task.id
        )
        request_review_link = '%s/tasks/%s/view' % (
            anima.defaults.stalker_server_external_address,
            task.id
        )
        with open(stalker_link_file_path, 'w+') as f:
            f.write(
                "Version Upload Link: %s\n"
                "Request Review Link: %s\n" % (version_upload_link, request_review_link)
            )
        zip_path = archiver.archive(project_path)
        new_zip_path = os.path.join(
            version.absolute_path,
            os.path.basename(zip_path)
        )

        # move the zip right beside the original version file
        shutil.move(zip_path, new_zip_path)

        # open the zip file in browser
        from anima.utils import open_browser_in_location
        open_browser_in_location(new_zip_path)
