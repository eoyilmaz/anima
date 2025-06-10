"""External DCCs module."""
import os
import re

from stalker import File, Version

from anima.dcc.base import DCCBase
from anima.log import logger


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
    """An external DCC which doesn't support Python.

    A very simple object that handles external DCCs. For now it just returns
    the name of the DCC, conforms the given version to the DCC by setting its
    file extension etc.
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
            raise TypeError(
                "{}.extension should be a str, not None".format(self.__class__.__name__)
            )

        if not isinstance(extensions, list):
            raise TypeError(
                "{}.extension should be a list of str, not {}".format(
                    self.__class__.__name__, extensions.__class__.__name__
                )
            )

        for i, extension in enumerate(extensions):
            if not extension.startswith("."):
                extension = f".{extension}"
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
        if not isinstance(name, str):
            raise TypeError(
                f"{self.__class__.__name__}.name should be an instance of str, "
                f"not {name.__class__.__name__}"
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
                f"{self.__class__.__name__}.structure should be a list of "
                "strings, showing the folder structure, "
                f"not {structure.__class__.__name__}: '{structure}'"
            )

        for item in structure:
            if not isinstance(item, str):
                raise TypeError(
                    f"All items in {self.__class__.__name__}.structure should "
                    f"be a str, not {item.__class__.__name__}: '{item}'"
                )

        return structure

    @property
    def structure(self) -> str:
        """Return the structure attribute value.

        Returns:
            str: The structure attribute value.
        """
        return self._structure

    @structure.setter
    def structure(self, structure) -> None:
        """Set the structure attribute value.

        Args:
            structure (List[str]): A list of strings showing the desired
                folders on that DCC.
        """
        self._structure = self._validate_structure(structure)

    def conform(self, version):
        """Conform the version to this DCC by setting its extension."""
        logger.debug("conforming version")
        if not isinstance(version, Version):
            raise TypeError(
                "version argument should be a stalker.version.Version instance, "
                f"not {version.__class__.__name__}: '{version}'"
            )
        version.update_paths()
        version.extension = self.extensions[0]
        version.created_with = self.name
        logger.debug(f"version.absolute_full_path : {version.absolute_full_path}")
        logger.debug(f"finished conforming version extension to: {self.extensions[0]}")

    def initialize_structure(self, version):
        """Initializes the DCC folder structure

        :return:
        """
        # check version type
        if not isinstance(version, Version):
            raise TypeError(
                '"version" argument in '
                f"{self.__class__.__name__}.initialize_structure should be a "
                "stalker.version.Version instance, "
                f"not {version.__class__.__name__}: '{version}'"
            )

        # create the folder in version.absolute_path
        extension = version.extension
        version.update_paths()
        version.extension = extension
        for folder in self.structure:
            folder_path = os.path.join(version.absolute_path, folder)
            logger.debug(f"creating: {folder_path}")
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
        """Return the settings file path.

        Returns:
            str: The path to the settings file where the last version
                information is stored.
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
        if not isinstance(version, Version):
            raise TypeError(
                '"version" argument in '
                f"{self.__class__.__name__}.append_to_recent_files "
                "method should be an instance of "
                "stalker.models.version.Version, "
                f"not {version.__class__.__name__}: '{version}'"
            )
        last_version_file_full_path = self.get_settings_file_path()
        try:
            os.makedirs(os.path.dirname(last_version_file_full_path))
        except OSError:
            pass

        with open(last_version_file_full_path, "w") as f:
            f.write(str(version.id))

    def get_last_file(self) -> None | File:
        """Return the last opened File instance from the DCC.

        * It first looks at the current open file full path and tries to match
          it with a File instance.
        * Then searches for the recent files list.
        * Still not able to find any File instances, will return the File
          instance with the highest id which has the current workspace path in
          its path.
        * Still not able to find any File instances returns None

        Returns:
            File: The File or None.
        """
        last_file_full_path = self.get_settings_file_path()
        try:
            with open(last_file_full_path, "r") as f:
                lines = f.readlines()
                fid = lines[0]
            return File.query.filter(File.id == fid).first()
        except (IOError, IndexError):
            return None

    def get_last_version(self):
        """Return the current version."""
        last_file_full_path = self.get_settings_file_path()
        try:
            with open(last_file_full_path, "r") as f:
                lines = f.readlines()
                vid = lines[0]
            return Version.query.filter(Version.id == vid).first()
        except (IOError, IndexError):
            return None


class ExternalDCCFactory(object):
    """A factory for External DCCs.

    A Factory object for DCCs. Generates :class:`ExternalDCC` instances.
    """

    @classmethod
    def get_dcc_names(cls, name_format="{name}"):
        """Return a list of DCC names which it is possible to create one DCC.

        Args:
            name_format (str): A string showing the format of the output
                variables:
                    {name} : the name of the DCC
                    {extension} : the native extension of the DCCs
                        scene/project file

        Returns:
            List[str]: A list of str showing DCC names.
        """
        dcc_names = []
        for dcc_name in list(external_dccs.keys()):
            dcc_data = external_dccs[dcc_name]
            dcc_names.append(
                name_format.format(
                    name=dcc_data["name"],
                    extension=dcc_data["extensions"][0],
                )
            )
        return dcc_names

    @classmethod
    def get_dcc(cls, name, name_format="{name}"):
        """Create a DCC with the given name.

        Args:
            name (str): The name of the DCC, should be a value from
                anima.dcc.externalDCC.dcc_names list.
            name_format (str): The name format.

        Returns:
            ExternalDCC: ExternalDCC instance.
        """
        if not isinstance(name, str):
            raise TypeError(
                f'"name" argument in {cls.__name__}.get_dcc() should be an '
                f"instance of str, not {name.__class__.__name__}: '{name}'"
            )

        # filter the name
        # replace anything that doesn't start with '{' with [\s\(\)\-]+
        pattern = re.sub(r"[^{\w}]+", r"[\\s\\(\\)\\-]+", name_format)

        pattern = pattern.replace("{name}", r"(?P<name>[\w\s]+)").replace(
            "{extension}", r"(?P<extension>\.\w+)"
        )
        logger.debug("pattern : {}".format(pattern))
        print("pattern : {}".format(pattern))

        match = re.search(pattern, name)
        dcc_name = None
        if match:
            dcc_name = match.group("name").strip()

        if dcc_name not in external_dccs:
            raise ValueError(
                f"{name} is not in "
                "anima.dcc.externalDCC.dcc_names list, "
                f"please supply a value from {list(external_dccs.keys())}"
            )

        dcc = external_dccs[dcc_name]
        return ExternalDCC(**dcc)
