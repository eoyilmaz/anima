# -*- coding: utf-8 -*-

from functools import lru_cache
import os
import shutil
from typing import Dict, List, Optional, Union

from stalker import File, Project, Repository, Shot, Version
from stalker.db.session import DBSession


from anima import (
    defaults,
    representation,  # keep this to extend Stalker classes
)
from anima.log import logger
from anima.recent import RecentFileManager
from anima.utils.progress import ProgressManagerFactory


def generate_empty_reference_resolution(
    root : Optional[List[File]] = None,
    leave : Optional[List[File]] = None,
    update : Optional[List[File]] = None,
    create : Optional[List[File]] = None
) -> Dict:
    """Generate an empty reference_resolution dictionary.

    Generate a ``Reference Resolution`` dictionary, where there are keys like
    'root', 'leave', 'update', 'create' showing:

        root: the versions referenced directly to the root,
        leave: Versions those doesn't have any new versions,
        update: Versions does have an updated version,
        create: Versions that should be updated by creating a new published version
            because its references has updated versions.

    Returns:
        Dict: The reference resolution dictionary.
    """
    return {
        "root": [] if root is None else root,
        "leave": [] if leave is None else leave,
        "update": [] if update is None else update,
        "create": [] if create is None else create,
    }


class DCCBase(object):
    """Connects the DCC to Anima Pipeline.

    In Anima Pipeline, a DCC is a host application like Maya, Nuke, Houdini etc.

    Generally a GUI for the end user is given a class instance which is derived
    from DCCBase which helps the UI to be able to open, save, import or export
    a File without knowing the details of the DCC.

    The DCC instance supplies **methods** like ``open``, ``save``,
    ``export``,  ``import`` or ``reference``. The main duty of the DCC
    object is to introduce the host application (Maya, Houdini, Nuke, etc.) to
    Stalker and let it to open, save, export, import or reference a file.

    It is the pipeline developers duty to create the DCC class implementation
    for the applications used in the studio by deriving a new class from
    DCCBase and overriding its methods as necessary.

    Here is a brief example for creating an DCC for a generic program::

        from anima.dcc.base import DCCBase

        class MyProgramEnv(DCCBase):
            '''This is a class which will be used by the UI'''

            def open(file : stalker.File):
                '''Use the Python API of the DCC to open a version.'''

                # do anything that needs to be done before opening the file
                my_programs_own_python_api.open(filepath=self.file.full_path)

            def save_as(file : File):
                '''Use the Python API of the DCC to save the current scene.'''
                # there should be a Version containing this File
                version = Version.query.filter(Version.files.contains(file)).first()

                if version is None:
                    raise RuntimeError(
                        "The given File instance is not related to a Version, "
                        "can't save the current scene!"
                    )

                # set the file path
                full_path = str(version.generate_path(extension=self.extensions[0]))
                absolute_full_path = os.path.expandvars(full_path)

                file.full_path = full_path

                # do anything that needs to be done before saving the file
                my_programs_own_python_api.save(filepath=absolute_full_path)

                # do anything that needs to be done after saving the file

    and that is it.

    The DCC class by default has a property called ``version``. Holding the
    current open Version. It is None for a new scene and a
    :class:`~stalker.models.version.Version` instance in any other case.
    """

    name = "DCCBase"
    representations = ["Base"]
    has_publishers = False
    allow_publish_on_export = False
    extensions = []

    project_structure = []

    def __init__(self, name="", version=None):
        self._name = name
        self._version = version

    def __str__(self):
        """Return the string representation."""
        return self._name

    @property
    def version(self):
        """Return the current Version instance which is open in the DCC."""
        return self.get_current_version()

    @property
    def name(self) -> str:
        """Return the DCC name.

        Returns:
            str: The DCC name.
        """
        return self._name

    @name.setter
    def name(self, name: str) -> None:
        """Set the DCC name.

        Args:
            name (str): The DCC name.
        """
        self._name = name

    def save_as(self, file: File, run_pre_publishers=True):
        """Save the current scene in this DCC as the given File.

        It should save the current scene or file to the given `file.full_path`.

        Args:
            file (File): The :class:`~stalker.models.file.File` instance to
                save the scene as.
            run_pre_publishers (bool): Run pre publishers of this DCC or not.
                Default value is True.
        """
        raise NotImplementedError("save_as is not implemented in this DCC!")

    def export_as(self, file: File):
        """Export the contents of the open document as the given file.

        Args:
            file (File): A :class:`~stalker.models.file.File` instance.
        """
        raise NotImplementedError("export_as() is not implemented in this DCC!")

    def open(
        self,
        file: File,
        force: bool = False,
        reference_depth: int = 0,
        skip_update_check: bool = False,
    ):
        """Open the given File instance.
        
        Args:
            file (File): The stalker.File instance to open.
            force (bool): Skip any errors and force open the given file.
            reference_depth (int): The reference depth to load. This is kind of
                specifically created for Maya, but might make sense in other
                DCCs too.
            skip_update_check (bool): If True, skip the update check.
        """
        raise NotImplementedError("open() is not implemented in this DCC!")

    def import_(self, file: File):
        """Import the given File.
        
        Args:
            file (File): The file to import to.
        """
        raise NotImplementedError("import_() is not implemented in this DCC!")

    def reference(self, file: File, use_namespace: bool = True):
        """Reference the given File.
        
        Args:
            file (File): The stalker.File instance to reference.
            use_namespace (True): Some DCCs (Maya) support namespaces, if True
                this should use a namespace for the reference.
        """
        raise NotImplementedError("reference is not implemented in this DCC!")

    def trim_repo_path(self, path: str) -> str:
        """Trim the repository path value from the given path.

        Args:
            path (str): The path that wanted to be trimmed.

        Returns:
            str: The trimmed path.
        """
        # get the repo first
        repo = self.find_repo(path)

        if not repo:
            return path

        # then try to trim the path
        if path.startswith(repo.path):
            return path[len(repo.path) :]
        elif path.startswith(repo.windows_path):
            return path[len(repo.windows_path) :]
        elif path.startswith(repo.linux_path):
            return path[len(repo.linux_path) :]
        elif path.startswith(repo.macos_path):
            return path[len(repo.macos_path) :]
        return path

    @classmethod
    def find_repo(cls, path: str) -> Union[None, Repository]:
        """Return the repository from the given path.

        Args:
            path (str): Path in a repository.

        Returns:
            stalker.models.repository.Repository: The 
        """
        # first find the repository
        return Repository.find_repo(path)

    def get_versions_from_path(self, path: str) -> List[Version]:
        """Find Version instances from the given path value.

        Find and return the :class:`~stalker.models.version.Version`
        instances from the given path value which should be the File paths that
        a Version might contain in their `Version.files` attribute.

        Return an empty list if it can't find any matching.

        This method is different than :meth:`~.get_version_from_full_path`
        because it returns a list of :class:`~stalker.Version` instances which
        are residing in that path. The list is ordered by the ``id`` values of
        the instances.

        Args:
            path (str): A path which has possible :class:`~stalker.File`
                instances that are related to the Version that is being looked
                for.

        Returns:
            List[Version]: A list of :class:`~stalker.models.version.Version`
                instances.
        """
        if not path:
            return []

        # convert '\\' to '/'
        path = os.path.normpath(path).replace("\\", "/")

        os_independent_path = Repository.to_os_independent_path(path)
        logger.debug("os_independent_path: {}".format(os_independent_path))

        # try to get all versions with that info
        versions = []
        with DBSession.no_autoflush:
            files = File.query.filter(File.full_path.startswith(os_independent_path)).all()
            for file in files:
                versions += Version.query.filter(Version.files.contains(file)).all()

        return versions

    @classmethod
    def get_file_from_full_path(cls, full_path: str) -> Union[None, File]:
        """Find the File instance from the given full_path value.

        Args:
            full_path (str): The full_path of the desired `File` instance.

        Returns:
            Union[None, File]: Return the `File` if found, else return None.
        """
        if full_path is None or full_path == "":
            return

        logger.debug("full_path: {}".format(full_path))
        # convert '\\' to '/'
        full_path = os.path.normpath(os.path.expandvars(full_path)).replace("\\", "/")

        # trim repo path
        os_independent_path = Repository.to_os_independent_path(full_path)

        # try to get a file with that info
        logger.debug(f"getting a file with path: {full_path}")

        with DBSession.no_autoflush:
            file = File.query.filter(File.full_path == os_independent_path).first()
        logger.debug(f"file: {file}")

        return file

    @classmethod
    def get_version_from_full_path(cls, full_path: str) -> Version:
        """Find the Version instance from the given full_path value.

        Find and return a :class:`~stalker.models.version.Version` instance
        from the given full_path value.

        Returns None if it can't find any matching.

        Args:
            full_path (str): The full_path of the desired `Version` instance.

        Returns:
            Union[None, Version]: Return the Version if it is found.
        """
        file = cls.get_file_from_full_path(full_path)

        # finding the file
        if file is None:
            return

        version = Version.query.filter(Version.files.contains(file)).first()

        logger.debug(f"version: {version}")
        return version

    def get_current_file(self) -> Union[None, File]:
        """Return the current File from the DCC.

        Returns:
            stalker.File: A File instance or None.
        """
        raise NotImplementedError(
            "get_current_file() is not implemented for this DCC!"
        )

    def get_current_version(self) -> Union[None, Version]:
        """Return the current Version instance from the DCC.

        Returns:
            Union[None, Version]: A :class:`~stalker.Version` instance or
                None.
        """
        current_file = self.get_current_file()
        # query the version that contains this file
        return  Version.query.filter(Version.files.contains(current_file)).first()

    def append_to_recent_files(self, path: str) -> None:
        """Append the given path to the recent files list.

        Args:
            path (str): The path to append to the recent files list to.
        """
        # add the file to the recent file list
        rfm = RecentFileManager()
        rfm.add(self.name, path)


    def get_file_from_recent_files(self) -> File:
        """Try to return a `File` instance from the recent files list.

        It will return None if it can not find one.

        Returns:
            Union[None, File]: The recent File if possible or None. 
        """
        file = None

        logger.debug("trying to get the File from recent file list!")
        # read the file name from recent files list
        # try to get the a valid asset file from starting the last recent file

        rfm = RecentFileManager()

        try:
            recent_files = rfm[self.name]
        except KeyError:
            logger.debug("no recent files!")
            recent_files = None

        if recent_files is None:
            return

        for recent_file in recent_files:
            file = self.get_file_from_full_path(recent_file)
            if file is not None:
                break

        logger.debug(f"file from recent files is: {file}")

        return file

    def get_version_from_recent_files(self) -> Version:
        """Try to return a `Version` instance from the recent files list.

        It will return None if it can not find one.

        Returns:
            Union[None, Version]: The recent Version if possible or None. 
        """
        version = None

        logger.debug("trying to get the version from recent file list")

        file = self.get_file_from_recent_files()
        if not file:
            return
        
        version = Version.query.filter(Version.files.contains(file)).first()

        logger.debug(f"version from recent files is: {version}")

        return version

    def get_last_version(self) -> Union[None, Version]:
        """Return the last opened Version instance from the DCC.

        * It first looks at the current open file full path and tries to match
          it with a Version instance.
        * Then searches for the recent files list.
        * Still not able to find any Version instances, will return the version
          instance with the highest id which has the current workspace path in
          its path
        * Still not able to find any Version instances returns None

        Returns:
            Version: The Version or None.
        """
        version = self.get_current_version()

        # read the recent file list
        if version is None:
            version = self.get_version_from_recent_files()

        return version

    def get_project(self) -> Project:
        """returns the current project from DCC"""
        raise NotImplementedError("get_project is not implemented")

    def set_project(self, version):
        """Sets the project to the given Versions project.

        Args:
            version (Version): A :class:`~stalker.Version` instance.
        """
        raise NotImplementedError("set_project is not implemented")

    def update_version_inputs(self, parent_ref=None):
        """Update the references list of the current file.

        Args:
            parent_ref: The parent ref, if given will override the current
                file and a File instance will be queried from the given
                parent_ref.path.
        """
        logger.debug(f"parent_ref: {parent_ref}")

        logger.debug("get a file")
        if not parent_ref:
            logger.debug("got no parent_ref")
            version = self.get_current_version()
        else:
            logger.debug("have a parent_ref")
            version = self.get_version_from_full_path(parent_ref.path)

        if version is None:
            return

        logger.debug(f"got a version: {version.absolute_full_path}")
        # use the base representation if it is not

        if version.variant_name and version.parent:
            version = version.parent
            logger.debug(
                f"this is a representation switching to its parent: {version}"
            )

        # update the reference list
        referenced_versions = self.get_referenced_files(parent_ref)
        version.inputs = referenced_versions

        # commit data to the database
        DBSession.add(version)
        DBSession.commit()

    def deep_references_update(self):
        """Update the File.references with the references of the current scene."""
        raise NotImplementedError("deep_references_update is not implemented")

    def check_references(self, pdm=None):
        """Deeply checks all the references in the scene and returns a
        dictionary which has three keys called 'leave', 'update' and 'create'.

        Each of these keys correspond to a value of a list of
        :class:`~stalker.model.version.Version` instances. Where the list in
        'leave' key shows the Versions referenced (or deeply referenced) to the
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
        if not pdm:
            pdm = ProgressManagerFactory.get_progress_manager()

        caller = pdm.register(
            3,
            f"{self.__class__.__name__}.check_references() prepare data",
        )

        # deeply get which file is referencing which other files
        self.deep_references_update()
        if caller:
            caller.step()

        reference_resolution = generate_empty_reference_resolution(
            root=self.get_referenced_files()
        )

        if caller:
            caller.step()

        # reverse walk in DFS
        dfs_version_references = []

        version = self.get_current_version()
        if not version:
            return reference_resolution

        for v in version.walk_inputs():
            dfs_version_references.append(v)

        if caller:
            caller.step()

        # pop the first element which is the current scene
        dfs_version_references.pop(0)

        caller.end_progress()

        # register a new caller
        caller = pdm.register(
            len(dfs_version_references),
            f"{self.__class__.__name__}.check_references()",
        )

        # iterate back in the list
        for v in reversed(dfs_version_references):
            # check inputs first
            to_be_updated_list = []
            for ref_v in v.inputs:
                if not ref_v.is_latest_published_version():
                    to_be_updated_list.append(ref_v)

            if to_be_updated_list:
                action = "create"
                # check if there is a new published version of this version
                # that is using all the updated versions of the references
                latest_published_version = v.latest_published_version
                if latest_published_version and not v.is_latest_published_version():
                    # so there is a new published version
                    # check if its children needs any update
                    # and the updated child versions are already
                    # referenced to the this published version
                    if all(
                        [
                            ref_v.latest_published_version
                            in latest_published_version.inputs
                            for ref_v in to_be_updated_list
                        ]
                    ):
                        # so all new versions are referenced to this published
                        # version, just update to this latest published version
                        action = "update"
                    else:
                        # not all references are in the inputs
                        # so we need to create a new version as usual
                        # and update the references to the latest versions
                        action = "create"
            else:
                # nothing needs to be updated,
                # so check if this version has a new version,
                # also there could be no reference under this referenced
                # version
                if v.is_latest_published_version():
                    # do nothing
                    action = "leave"
                else:
                    # update to latest published version
                    action = "update"

                # before setting the action check all the inputs in
                # resolution_dictionary, if any of them are update, or create
                # then set this one to 'create'
                if any(
                    rev_v in reference_resolution["update"]
                    or rev_v in reference_resolution["create"]
                    for rev_v in v.inputs
                ):
                    action = "create"

            # so append this v to the related action list
            reference_resolution[action].append(v)

            caller.step(message=v.nice_name)

        caller.end_progress()

        return reference_resolution

    def get_referenced_files(self, parent_ref=None) -> List[File]:
        """Return :class:`~stalker.File`s that are referenced to the current scene.

        Args:
            parent_ref (pymel.nt.Reference): The parent reference node.
        
        Returns:
            List[File]: Referenced Files.
        """
        raise NotImplementedError(
            "get_referenced_files() is not implemented in this DCC!"
        )

    def update_reference_versions_to_latest(self, reference_resolution: Dict):
        """Update the File references to their latest versions.

        Args:
            reference_resolution (Dict): A dictionary with keys 'leave',
                'update' and 'create' with a list of :class:`~stalker.File`
                instances in each of them. Only 'update' key is used and if the
                File instance is in the 'update' list the reference is updated
                to the latest version.
        """
        raise NotImplementedError(
            "update_reference_versions_to_latest() is not implemented in this DCC!"
        )

    def get_frame_range(self):
        """Returns the frame range from the DCC

        :returns: a tuple of integers containing the start and end frame
            numbers
        """
        raise NotImplementedError("get_frame_range() is not implemented in this DCC!")

    def set_frame_range(self, start_frame=0, end_frame=100, adjust_frame_range=False):
        """Sets the frame range in the DCC to the given start and end
        frames
        """
        raise NotImplementedError("set_frame_range is not implemented")

    def get_fps(self):
        """Returns the frame rate of this current DCC"""
        raise NotImplementedError("get_fps is not implemented")

    def set_fps(self, fps=25):
        """Sets the frame rate of the DCC. The default value is 25.

        :param float fps: The FPS of the current DCC. Defaults to 25.
        :return:
        """
        raise NotImplementedError("set_fps is not implemented")

    def has_extension(self, filename: str) -> bool:
        """Return True if the given file names extension is in the extensions
        list false otherwise.

        accepts:
        * a full path with extension or not
        * a file name with extension or not
        * an extension with a dot on the start or not

        Args
            filename (str): A string containing the filename

        Returns:
            bool: True if the given filename has the correct extension.
        """
        if filename is None:
            return False
        return filename.split(".")[-1].lower() in self.extensions

    def load_references(self):
        """Load all the references."""
        raise NotImplementedError(
            "load_references() is not implemented in this DCC!"
        )

    def replace_reference(self, source_file : File, target_file : File):
        """Replace the source_file with the target_file.

        Args:
            source_file (File): A :class:`~stalker.File` instance holding the
                reference to be replaced

            target_version (File): A :class:`~stalker.File` instance holding
                the new reference replacing the source one.
        """
        raise NotImplementedError(
            "replace_reference() is not implemented in this DCC!"
        )

    def replace_external_paths(self, mode=0):
        """Replace the external paths with a proper paths;.

        External paths which are not starting with the environment variable are
        considered. The mode controls if the resultant path should be absolute
        or relative to the project dir.

        Args
            mode (int): Controls the resultant path is absolute or relative.

                mode 0: absolute (a path which starts with $REPO)
                mode 1: relative (to project path)
        """
        raise NotImplementedError(
            "replace_external_paths() is not implemented in this DCC!"
        )

    def reference_filters(self, version, options):
        """Checks the given version against the given options.

        Args:
            options (Dict): A dictionary object showing the reference options
        """
        pass

    @classmethod
    def get_significant_name(
        cls,
        version,
        include_project_code : bool = True,
        include_version_number : bool = True,
    ) -> str:
        """Return the significant name. 
        
        The significant name starts from the closest parent which is an Asset,
        Shot or Sequence and includes the ``Project.code``.

        Args:
            version : The Stalker Version instance.
            include_project_code (bool): Include project code.
            include_version_number (bool): Include version number.

        Returns:
            str: The significant name.
        """
        if include_project_code:
            sig_name = "{}_{}".format(version.task.project.code, version.nice_name)
        else:
            sig_name = version.nice_name

        if include_version_number:
            sig_name = "{}_r{:02d}_v{:03d}".format(
                sig_name,
                version.revision_number,
                version.version_number,
            )

        return sig_name

    @classmethod
    def local_backup_path(cls):
        """Return the local backup path.

        Returns:
            str: The local backup path.
        """
        # use the user home directory .stalker_local_backup
        return os.path.normpath(
            os.path.expanduser(f"{defaults.local_cache_folder}/projects_backup")
        ).replace("\\", "/")

    def create_project_structure(self, version):
        """Create the project structure.

        Args:
            version (Version): Stalker version.
        """
        project_path = version.absolute_path
        for path in self.project_structure:
            # TODO: use exist_ok=True for Python 3.x
            try:
                os.makedirs(os.path.normpath(os.path.join(project_path, path)))
            except OSError:
                # exists_ok
                pass

    @classmethod
    def create_local_copy(cls, file):
        """Create a local copy of the given file.

        Args:
            file (stalker.File): A stalker File instance.
        """
        absolute_full_path = os.path.expandvars(file.full_path)
        output_path = os.path.join(
            cls.local_backup_path(), absolute_full_path.replace(":", "")
        ).replace("\\", "/")

        output_full_path = os.path.join(
            cls.local_backup_path(), absolute_full_path.replace(":", "")
        ).replace("\\", "/")

        # do nothing if the version and the copy is on the same drive
        # (ex: do not duplicate the file)
        if len(os.path.commonprefix([output_full_path, absolute_full_path])):
            logger.debug(
                f"Local copy file: {output_full_path} is on the same drive "
                f"with the source file: {absolute_full_path}"
            )
            logger.debug("Not duplicating it!")
            return

        # create intermediate folders
        try:
            os.makedirs(output_path)
        except OSError:
            # already exists
            pass

        try:
            shutil.copy(absolute_full_path, output_full_path)
        except IOError:
            # no space left
            pass

        logger.debug(f"created copy to: {output_full_path}")

    @classmethod
    @lru_cache(maxsize=None)
    def get_shot(cls, version: Version) -> Union[None, Shot]:
        """Find and return the related Shot.

        Args:
            version (Version): A stalker Version instance.

        Returns:
            Union[None, Shot]: The stalker Shot instance or None if this
                version is not related to a Shot.
        """
        for task in version.task.parents:
            if isinstance(task, Shot):
                return task

    @lru_cache(maxsize=None)
    def is_shot_related_version(self, version: Version) -> bool:
        """Return True if this is a shot related version.

        Args
            version (Version):

        Returns:
            bool: True if this is shot related.
        """
        return self.get_shot(version) is not None

    def set_render_resolution(
        self,
        width : int,
        height : int,
        pixel_aspect : float = 1.0
    ) -> None:
        """Set the render resolution for the current DCC.

        Args:
            width (int): The width of the resolution.
            height (int): The height of the resolution.
            pixel_aspect (float): The pixel aspect ratio, defaults to 1.0.
        """
        raise NotImplementedError("set_render_resolution is not implemented")


class Filter(object):
    """A filter class filters given options against the given versions related
    task type.

    Args:
        version (Version): A :class:`~stalker.Version` instance. The related
            :class:`~stalker.Task` instances :attr:`~stalker.Task.type`
            attribute is key here. It defines which filter to apply to.

        options (Dict): A dictionary with keys are the name of the option and
            the value is the value of that option.
    """

    def __init__(self):
        pass


class OpenFilter(Filter):
    """A filter for Open operations"""

    pass


class ReferenceFilter(Filter):
    """A filter for Reference operations"""

    pass


class ImportFilter(Filter):
    """A filter for Import operations"""

    pass


class ExportFilter(Filter):
    """A filter for Export operations"""

    pass


class SaveAsFilter(Filter):
    """A Filter for Save As operations"""

    pass
