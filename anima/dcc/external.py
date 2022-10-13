# -*- coding: utf-8 -*-

import os

from anima import logger
from anima.dcc.base import DCCBase


external_dccs = {
    "MudBox": {
        "name": "MudBox",
        "icon": "mudbox.png",
        "executable": {
            "linux": "mudbox",
            "windows": "mudbox.exe",
        },
        "extensions": [".mud"],
        "structure": [
            "Outputs",
        ],
    },
    #'ZBrush Project' : {
    #    'name': 'ZBrush Project',
    #    'icon': 'zbrush.png',
    #    'extensions': ['.zpr'],
    #    'structure': [
    #        'Outputs',
    #    ]
    # },
    "ZBrush": {
        "name": "ZBrush",
        "icon": "zbrush.png",
        "executable": {
            "windows": "zbrush.exe",
        },
        "extensions": [".ztl"],
        "structure": [
            "Outputs",
        ],
    },
}


class ExternalDCC(DCCBase):
    """An external DCC which doesn't support Python

    A very simple object that handles external environments. For now it just
    returns the name of the DCC, conforms the given version to the
    DCC by setting its file extension etc.
    """

    def __init__(self, name, structure=None, extensions=None, **kwargs):
        """

        :param name: The name of this DCC
        :param extensions: The extensions of this DCC
        :param structure: The folder structure of this DCC
        :return:
        """
        super(ExternalDCC, self).__init__(name=name)
        self._name = None
        self._structure = None
        self._extensions = None

        self.name = self._validate_name(name)
        self.structure = self._validate_structure(structure)
        self.extensions = self._validate_extensions(extensions)

    def _validate_extensions(self, extensions):
        if not extensions:
            raise TypeError("%s.extension can not be None" % self.__class__.__name__)

        for i, extension in enumerate(extensions):
            if not extension.startswith("."):
                extension = ".%s" % extension
                extensions[i] = extension

        return extensions

    @property
    def extensions(self):
        return self._extensions

    @extensions.setter
    def extensions(self, extensions):
        self._extensions = self._validate_extensions(extensions)

    def _validate_name(self, name):
        """validates the given name value

        :param name: the desired name
        :return: str
        """
        from anima import string_types

        if not isinstance(name, string_types):
            raise TypeError(
                "%s.name should be an instance of str, not %s"
                % (self.__class__.__name__, name.__class__.__name__)
            )
        return name

    @property
    def name(self):
        """the name property getter

        :return: str
        """
        return self._name

    @name.setter
    def name(self, name):
        """the name property setter

        :param str name: A string value for desired name should
          contain a value which starts with "."
        :return: None
        """
        self._name = self._validate_name(name)

    def _validate_structure(self, structure):
        """validates the given structure value

        :param str structure:
        :return: str
        """
        if structure is None:
            structure = []

        if not isinstance(structure, list):
            raise TypeError(
                "%s.structure should be a list of strings, "
                "showing the folder structure, not %s"
                % (self.__class__.__name__, structure.__class__.__name__)
            )

        for item in structure:
            if not isinstance(item, str):
                raise TypeError(
                    "All items in %s.structure should be an "
                    "instance of str, an not %s"
                    % (self.__class__.__name__, item.__class__.__name__)
                )

        return structure

    @property
    def structure(self):
        """the structure property getter

        :return: str
        """
        return self._structure

    @structure.setter
    def structure(self, structure):
        """the structure property setter

        :param list structure: A list of string showing the desired folders on that DCC
        :return: None
        """
        self._structure = self._validate_structure(structure)

    def conform(self, version):
        """Conforms the version to this DCC by setting its extension."""
        logger.debug("conforming version")
        from stalker import Version

        if not isinstance(version, Version):
            raise TypeError(
                "version argument should be a "
                "stalker.version.Version instance, not %s" % version.__class__.__name__
            )
        version.update_paths()
        version.extension = self.extensions[0]
        version.created_with = self.name
        logger.debug("version.absolute_full_path : %s" % version.absolute_full_path)
        logger.debug(
            "finished conforming version extension to: %s" % self.extensions[0]
        )

    def initialize_structure(self, version):
        """Initializes the DCC folder structure

        :return:
        """
        # check version type
        from stalker import Version

        if not isinstance(version, Version):
            raise TypeError(
                '"version" argument in %s.initialize_structureshould be a '
                "stalker.version.Version instance, not %s"
                % (self.__class__.__name__, version.__class__.__name__)
            )

        # create the folder in version.absolute_path
        extension = version.extension
        version.update_paths()
        version.extension = extension
        for folder in self.structure:
            folder_path = os.path.join(version.absolute_path, folder)
            logger.debug("creating: %s" % folder_path)
            try:
                os.makedirs(folder_path)
            except OSError:
                # dir exists
                pass

    def save_as(self, version, run_pre_publishers=True):
        """A compatibility method which will allow this DCC to be used
        in place of anima.dcc.base.DCCBase derivatives.

        :param version: stalker.models.version.Version instance
        :param bool run_pre_publishers: Run pre publishers of this DCC
          or not. Default value is True
        :return:
        """
        # just conform the version and initialize_structure
        self.conform(version)
        self.initialize_structure(version)
        self.append_to_recent_files(version)

    @classmethod
    def get_settings_file_path(cls):
        """returns the settings file path
        :return:
        """
        # append to .atrc file
        atrc_path = os.path.expanduser("~/.atrc/")
        last_version_filename = "last_version"
        return os.path.join(atrc_path, last_version_filename)

    def append_to_recent_files(self, version):
        """Appends the given version info to the recent files list

        :param version: A :class:`~stalker.models.version.Version` instance.
        :return:
        """
        from stalker import Version

        if not isinstance(version, Version):
            raise TypeError(
                '"version" argument in %s.append_to_recent_files '
                "method should be an instance of "
                "stalker.models.version.Version, not %s"
                % (self.__class__.__name__, version.__class__.__name__)
            )
        last_version_file_full_path = self.get_settings_file_path()
        try:
            os.makedirs(os.path.dirname(last_version_file_full_path))
        except OSError:
            pass

        with open(last_version_file_full_path, "w") as f:
            f.write(str(version.id))

    def get_last_version(self):
        """returns the current version"""
        last_version_file_full_path = self.get_settings_file_path()
        try:
            with open(last_version_file_full_path, "r") as f:
                lines = f.readlines()
                vid = lines[0]
            from stalker import Version

            return Version.query.filter(Version.id == vid).first()
        except (IOError, IndexError):
            return None


class ExternalDCCFactory(object):
    """A factory for External DCCs.

    A Factory object for DCCs. Generates :class:`ExternalDCC` instances.
    """

    @classmethod
    def get_env_names(cls, name_format="%n"):
        """returns a list of DCC names which it is possible to create one DCC.

        :param str name_format: A string showing the format of the output
          variables:
            %n : the name of the Environment
            %e : the extension of the Environment

        :return list: list
        """
        env_names = []
        for env_name in external_dccs.keys():
            env_data = external_dccs[env_name]
            env_names.append(
                name_format.replace("%n", env_data["name"]).replace(
                    "%e", env_data["extensions"][0]
                )
            )
        return env_names

    @classmethod
    def get_env(cls, name, name_format="%n"):
        """Creates a DCC with the given name

        :param str name: The name of the DCC, should be a value from
          anima.dcc.externalEnv.environment_names list

        :return ExternalDCC: ExternalDCC instance
        """
        if not isinstance(name, str):
            raise TypeError(
                '"name" argument in %s.get_env() should be an '
                "instance of str, not %s" % (cls.__name__, name.__class__.__name__)
            )

        # filter the name
        import re

        # replace anything that doesn't start with '%' with [\s\(\)\-]+
        pattern = re.sub(r"[^%\w]+", "[\s\(\)\-]+", name_format)

        pattern = pattern.replace("%n", "(?P<name>[\w\s]+)").replace(
            "%e", "(?P<extension>\.\w+)"
        )
        logger.debug("pattern : %s" % pattern)

        match = re.search(pattern, name)
        dcc_name = None
        if match:
            dcc_name = match.group("name").strip()

        dcc_names = external_dccs.keys()
        if dcc_name not in dcc_names:
            raise ValueError(
                "%s is not in "
                "anima.dcc.externalEnv.environment_names list, "
                "please supply a value from %s" % (name, dcc_names)
            )

        dcc = external_dccs[dcc_name]
        return ExternalDCC(**dcc)
