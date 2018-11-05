# -*- coding: utf-8 -*-
# Copyright (c) 2012-2018, Anima Istanbul
#
# This module is part of anima-tools and is released under the BSD 2
# License: http://www.opensource.org/licenses/BSD-2-Clause
import os

from anima import logger, log_file_handler
from anima.recent import RecentFileManager


class EnvironmentBase(object):
    """Connects the environment (the host program) to Stalker.

    In Stalker, an Environment is a host application like Maya, Nuke, Houdini
    etc.

    Generally a GUI for the end user is given an environment which helps the
    QtGui to be able to open, save, import or export a Version without
    knowing the details of the environment.

    The environment object supplies **methods** like ``open``, ``save``,
    ``export``,  ``import`` or ``reference``. The main duty of the Environment
    object is to introduce the host application (Maya, Houdini, Nuke, etc.) to
    Stalker and let it to open, save, export, import or reference a file.

    It is the pipeline developers duty to create the environment classes for
    the programs used in the studio by instantiating this class and overriding
    the methods as necessary. You can find good examples in `Anima Tools`_
    which is a Python package developed in `Anima Istanbul`_.

    .. _Anima Tools: https://pypi.python.org/pypi/anima
    .. _Anima Istanbul: http;//www.animaistanbul.com

    Here is a brief example for creating an environment for a generic program::

        from Stalker import EnvironmentBase

        class MyProgramEnv(EnvironmentBase):
            \"""This is a class which will be used by the UI
            \"""

            def open():
                \"""uses the programs own Python API to open a version of an
                asset
                \"""

                # do anything that needs to be done before opening the file
                my_programs_own_python_api.open(filepath=self.version.full_path)

            def save():
                \"""uses the programs own Python API to save the current file
                as a new version.
                \"""

                # do anything that needs to be done before saving the file
                my_programs_own_python_api.save(filepath=self.version.full_path)

                # do anything that needs to be done after saving the file

    and that is it.

    The environment class by default has a property called ``version``. Holding
    the current open Version. It is None for a new scene and a
    :class:`~stalker.models.version.Version` instance in any other case.
    """

    name = "EnvironmentBase"
    representations = ['Base']
    has_publishers = False
    allow_publish_on_export = False
    extensions = []

    def __init__(self, name="", version=None):
        self._name = name
        self._version = version

    def __str__(self):
        """the string representation of the environment
        """
        return self._name

    @property
    def version(self):
        """returns the current Version instance which is open in the
        environment
        """
        return self.get_current_version()

    @property
    def name(self):
        """returns the environment name
        """
        return self._name

    @name.setter
    def name(self, name):
        """sets the environment name
        """
        self._name = name

    def save_as(self, version, run_pre_publishers=True):
        """The save as action of this environment. It should save the current
        scene or file to the given version.full_path

        :param version: stalker.models.version.Version instance.
        :param bool run_pre_publishers: Run pre publishers of this environment
          or not. Default value is True
        """
        raise NotImplementedError

    def export_as(self, version):
        """Exports the contents of the open document as the given version.

        :param version: A :class:`~stalker.models.version.Version` instance
          holding the desired version.
        """
        raise NotImplementedError

    def open(self, version, force=False, representation=None,
             reference_depth=0, skip_update_check=False):
        """the open action
        """
        raise NotImplementedError

    def import_(self, version):
        """the import action
        """
        raise NotImplementedError

    def reference(self, version, use_namespace=True):
        """the reference action
        """
        raise NotImplementedError

    def trim_repo_path(self, path):
        """Trims the repository path value from the given path

        :param path: The path that wanted to be trimmed
        :return: str
        """
        # get the repo first
        repo = self.find_repo(path)

        if not repo:
            return path

        # then try to trim the path
        if path.startswith(repo.path):
            return path[len(repo.path):]
        elif path.startswith(repo.windows_path):
            return path[len(repo.windows_path):]
        elif path.startswith(repo.linux_path):
            return path[len(repo.linux_path):]
        elif path.startswith(repo.osx_path):
            return path[len(repo.osx_path):]
        return path

    @classmethod
    def find_repo(cls, path):
        """returns the repository from the given path

        :param str path: path in a repository
        :return: stalker.models.repository.Repository
        """
        # path could be using environment variables so expand them
        # path = os.path.expandvars(path)

        # first find the repository
        from stalker import Repository

        repos = Repository.query.all()
        found_repo = None
        for repo in repos:
            if path.startswith(repo.path) \
               or path.startswith(repo.windows_path) \
               or path.startswith(repo.linux_path) \
               or path.startswith(repo.osx_path):
                found_repo = repo
                break
        return found_repo

    def get_versions_from_path(self, path):
        """Finds Version instances from the given path value.

        Finds and returns the :class:`~stalker.models.version.Version`
        instances from the given path value.

        Returns an empty list if it can't find any matching.

        This method is different than
        :meth:`~stalker.env.EnvironmentBase.get_version_from_full_path`
        because it returns a list of
        :class:`~stalker.models.version.Version` instances which are
        residing in that path. The list is ordered by the ``id``\ s of the
        instances.

        :param path: A path which has possible
            :class:`~stalker.models.version.Version` instances.

        :return: A list of :class:`~stalker.models.version.Version` instances.
        """
        if not path:
            return []

        # convert '\\' to '/'
        path = os.path.normpath(path).replace('\\', '/')
        from stalker import Repository
        os_independent_path = Repository.to_os_independent_path(path)
        logger.debug('os_independent_path: %s' % os_independent_path)

        from stalker import Version
        from stalker.db.session import DBSession

        # try to get all versions with that info
        with DBSession.no_autoflush:
            versions = Version.query.\
                filter(Version.full_path.startswith(os_independent_path)).all()

        return versions

    @classmethod
    def get_version_from_full_path(cls, full_path):
        """Finds the Version instance from the given full_path value.

        Finds and returns a :class:`~stalker.models.version.Version` instance
        from the given full_path value.

        Returns None if it can't find any matching.

        :param full_path: The full_path of the desired
            :class:`~stalker.models.version.Version` instance.

        :return: :class:`~stalker.models.version.Version`
        """
        logger.debug('full_path: %s' % full_path)
        # convert '\\' to '/'
        full_path = os.path.normpath(
            os.path.expandvars(full_path)
        ).replace('\\', '/')

        # trim repo path
        from stalker import Repository, Version
        os_independent_path = Repository.to_os_independent_path(full_path)

        # try to get a version with that info
        logger.debug('getting a version with path: %s' % full_path)

        version = Version.query\
            .filter(Version.full_path == os_independent_path).first()
        logger.debug('version: %s' % version)
        return version

    def get_current_version(self):
        """Returns the current Version instance from the environment.

        :returns: :class:`~stalker.models.version.Version` instance or None
        """
        raise NotImplementedError

    def append_to_recent_files(self, path):
        """appends the given path to the recent files list
        """
        # add the file to the recent file list
        rfm = RecentFileManager()
        rfm.add(self.name, path)

    def get_version_from_recent_files(self):
        """This will try to create a :class:`.Version` instance by looking at
        the recent files list.

        It will return None if it can not find one.

        :return: :class:`.Version`
        """
        version = None

        logger.debug("trying to get the version from recent file list")
        # read the fileName from recent files list
        # try to get the a valid asset file from starting the last recent file

        rfm = RecentFileManager()

        try:
            recent_files = rfm[self.name]
        except KeyError:
            logger.debug('no recent files')
            recent_files = None

        if recent_files is not None:
            for recent_file in recent_files:
                version = self.get_version_from_full_path(recent_file)
                if version is not None:
                    break

            logger.debug("version from recent files is: %s" % version)

        return version

    def get_last_version(self):
        """Returns the last opened Version instance from the environment.

        * It first looks at the current open file full path and tries to match
          it with a Version instance.
        * Then searches for the recent files list.
        * Still not able to find any Version instances, will return the version
          instance with the highest id which has the current workspace path in
          its path
        * Still not able to find any Version instances returns None

        :returns: :class:`~stalker.models.version.Version` instance or None.
        """
        version = self.get_current_version()

        # read the recent file list
        if version is None:
            version = self.get_version_from_recent_files()

        return version

    def get_project(self):
        """returns the current project from environment
        """
        raise NotImplementedError

    def set_project(self, version):
        """Sets the project to the given Versions project.

        :param version: A :class:`~stalker.models.version.Version`.
        """
        raise NotImplementedError

    def update_version_inputs(self, parent_ref=None):
        """updates the references list of the current version

        :param parent_ref: the parent ref, if given will override the given
          version argument and a Version instance will be get from the given
          parent_ref.path.
        """
        logger.debug('parent_ref: %s' % parent_ref)

        logger.debug('get a version')
        if not parent_ref:
            logger.debug('got no parent_ref')
            version = self.get_current_version()
        else:
            logger.debug('have a parent_ref')
            version = self.get_version_from_full_path(parent_ref.path)

        if version:
            logger.debug('got a version: %s' % version.absolute_full_path)
            # use the original version if it is a Repr version
            from anima.representation import Representation
            if Representation.repr_separator in version.take_name \
               and version.parent:
                version = version.parent
                logger.debug(
                    'this is a representation switching to its parent: %s' %
                    version
                )

            # update the reference list
            referenced_versions = self.get_referenced_versions(parent_ref)
            version.inputs = referenced_versions

            # commit data to the database
            from stalker.db.session import DBSession
            DBSession.add(version)
            DBSession.commit()

    def deep_version_inputs_update(self):
        """Updates the inputs of the references of the current scene
        """
        raise NotImplementedError

    def check_referenced_versions(self, pdm=None):
        """Deeply checks all the references in the scene and returns a
        dictionary which has three keys called 'leave', 'update' and 'create'.

        Each of these keys correspond to a value of a list of
        :class:`~stalker.model.version.Version`\ s. Where the list in 'leave'
        key shows the Versions referenced (or deeply referenced) to the
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
            from anima.ui.progress_dialog import ProgressDialogManager
            pdm = ProgressDialogManager()

        caller = \
            pdm.register(
                3,
                '%s.check_referenced_versions() prepare data' %
                self.__class__.__name__
            )

        # deeply get which file is referencing which other files
        self.deep_version_inputs_update()
        if caller:
            caller.step()

        from anima.env import empty_reference_resolution
        reference_resolution = \
            empty_reference_resolution(root=self.get_referenced_versions())

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
            '%s.check_referenced_versions()' % self.__class__.__name__
        )

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
                if any(rev_v in reference_resolution['update'] or
                       rev_v in reference_resolution['create']
                       for rev_v in v.inputs):
                    action = 'create'

            # so append this v to the related action list
            reference_resolution[action].append(v)

            # from stalker import Version
            # assert isinstance(v, Version)
            caller.step(message=v.nice_name)

        caller.end_progress()

        return reference_resolution

    def get_referenced_versions(self, parent_ref=None):
        """Returns the :class:`~stalker.models.version.Version` instances which
        are referenced in to the current scene

        :param parent_ref: The parent reference node.
        :returns: list of :class:`~stalker.models.version.Version` instances.
        """
        raise NotImplementedError

    def update_versions(self, reference_resolution):
        """Updates the versions to the latest ones.

        :param reference_resolution: A dictionary with keys 'leave', 'update'
          and 'create' with a list of :class:`~stalker.models.version.Version`
          instances in each of them. Only 'update' key is used and if the
          Version instance is in the 'update' list the reference is updated to
          the latest version.
        """
        raise NotImplementedError

    def get_frame_range(self):
        """Returns the frame range from the environment

        :returns: a tuple of integers containing the start and end frame
            numbers
        """
        raise NotImplementedError

    def set_frame_range(self, start_frame=0, end_frame=100,
                        adjust_frame_range=False):
        """Sets the frame range in the environment to the given start and end
        frames
        """
        raise NotImplementedError

    def get_fps(self):
        """Returns the frame rate of this current environment
        """
        raise NotImplementedError

    def set_fps(self, fps=25):
        """Sets the frame rate of the environment. The default value is 25.
        """
        raise NotImplementedError

    def has_extension(self, filename):
        """Returns True if the given file names extension is in the extensions
        list false otherwise.

        accepts:
        * a full path with extension or not
        * a file name with extension or not
        * an extension with a dot on the start or not

        :param filename: A string containing the filename
        """
        if filename is None:
            return False
        return filename.split('.')[-1].lower() in self.extensions

    def load_referenced_versions(self):
        """loads all the references
        """
        raise NotImplementedError

    def replace_version(self, source_version, target_version):
        """Replaces the source_version with the target_version

        :param source_version: A
          :class:`~stalker.models.version.Version` instance holding the version
          to be replaced

        :param target_version: A
          :class:`~stalker.models.version.Version` instance holding the new
          version replacing the source one.
        """
        raise NotImplementedError

    def replace_external_paths(self, mode=0):
        """Replaces the external paths (which are not starting with the
        environment variable) with a proper path. The mode controls if the
        resultant path should be absolute or relative to the project dir.

        :param mode: Controls the resultant path is absolute or relative.

          mode 0: absolute (a path which starts with $REPO)
          mode 1: relative (to project path)

        :return:
        """
        raise NotImplementedError

    def reference_filters(self, version, options):
        """Checks the given version against the given options

        :param options: a dictionary object showing the reference options
        :return:
        """
        pass

    @classmethod
    def get_significant_name(cls, version, include_project_code=True,
                             include_version_number=True):
        """returns a significant name starting from the closest parent which is
        an Asset, Shot or Sequence and includes the Project.code

        :param version: The Stalker Version instance.
        :param bool include_project_code: Include project code.
        :param bool include_version_number: Include version number

        :rtype : basestring
        """
        if include_project_code:
            sig_name = '%s_%s' % (version.task.project.code, version.nice_name)
        else:
            sig_name = version.nice_name

        if include_version_number:
            sig_name = '%s_v%03d' % (sig_name, version.version_number)

        return sig_name

    @classmethod
    def local_backup_path(cls):
        """returns the local backup path

        :return:
        """
        # use the user home directory .stalker_local_backup
        from anima import defaults
        return os.path.normpath(
            os.path.expanduser(
                '%s/projects_backup' % defaults.local_cache_folder
            )
        ).replace('\\', '/')

    @classmethod
    def create_local_copy(cls, version):
        """Creates a local copy of the given version

        :param version:
        :return:
        """
        output_path = os.path.join(
            cls.local_backup_path(),
            version.absolute_path.replace(':', '')
        ).replace('\\', '/')

        output_full_path = os.path.join(
            cls.local_backup_path(),
            version.absolute_full_path.replace(':', '')
        ).replace('\\', '/')

        # do nothing if the version and the copy is on the same drive
        # (ex: do not duplicate the file)
        if len(os.path.commonprefix([output_full_path,
                                     version.absolute_full_path])):
            logger.debug(
                'Local copy file: %s is on the same drive with the source '
                'file: %s' % (output_full_path, version.absolute_full_path)
            )
            logger.debug('Not duplicating it!')
            return

        # create intermediate folders
        try:
            os.makedirs(output_path)
        except OSError:
            # already exists
            pass

        import shutil

        try:
            shutil.copy(
                version.absolute_full_path,
                output_full_path
            )
        except IOError:
            # no space left
            pass

        logger.debug('created copy to: %s' % output_full_path)


class Filter(object):
    """A filter class filters given options against the given versions related
    task type.

    :param version: :class:`~stalker.models.version.Version` instance. The
      related :class:`~stalker.models.task.Task`\ s
      :attr:`~stalker.models.task.Task.type` attribute is key here. It defines
      which filter to apply to.

    :param options: A dictionary with keys are the name of the option and the
      value is the value of that option.
    """

    def __init__(self):
        pass


class OpenFilter(Filter):
    """A filter for Open operations
    """
    pass


class ReferenceFilter(Filter):
    """A filter for Reference operations
    """
    pass


class ImportFilter(Filter):
    """A filter for Import operations
    """
    pass


class ExportFilter(Filter):
    """A filter for Export operations
    """
    pass


class SaveAsFilter(Filter):
    """A Filter for Save As operations
    """
    pass
