# -*- coding: utf-8 -*-
# Copyright (c) 2012-2017, Anima Istanbul
#
# This module is part of anima-tools and is released under the BSD 2
# License: http://www.opensource.org/licenses/BSD-2-Clause

import os

from anima import logger
from anima.env.base import EnvironmentBase


external_environments = {
    'MudBox': {
        'name': 'MudBox',
        'icon': 'mudbox.png',
        'executable': {
            'linux': 'mudbox',
            'windows': 'mudbox.exe',
        },
        'extensions': ['.mud'],
        'structure': [
            'Outputs',
        ]
    },
    #'ZBrush Project' : {
    #    'name': 'ZBrush Project',
    #    'icon': 'zbrush.png',
    #    'extensions': ['.zpr'],
    #    'structure': [
    #        'Outputs',
    #    ]
    #},
    'ZBrush': {
        'name': 'ZBrush',
        'icon': 'zbrush.png',
        'executable': {
            'windows': 'zbrush.exe',
        },
        'extensions': ['.ztl'],
        'structure': [
            'Outputs',
        ]
    },
}


class ExternalEnv(EnvironmentBase):
    """An external environment which doesn't support Python

    A very simple object that handles external environments. For now it just
    returns the name of the environment, conforms the given version to the
    environment by setting its file extension etc.
    """

    def __init__(self, name, structure=None, **kwargs):
        """

        :param name: The name of this environment
        :param extensions: The extensions of this environment
        :param structure: The folder structure of this environment
        :return:
        """
        super(ExternalEnv, self).__init__(name=name)
        self._name = None
        self._structure = None

        self.name = self._validate_name(name)
        self.structure = self._validate_structure(structure)

    def _validate_name(self, name):
        """validates the given name value

        :param name: the desired name
        :return: str
        """
        if not isinstance(name, str):
            raise TypeError(
                '%s.name should be an instance of str, not %s' % (
                    self.__class__.__name__,
                    name.__class__.__name__
                )
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
            raise TypeError('%s.structure should be a list of strings, '
                            'showing the folder structure, not %s' % 
                            (self.__class__.__name__,
                             structure.__class__.__name__))

        for item in structure:
            if not isinstance(item, basestring):
                raise TypeError('All items in %s.structure should be an '
                                'instance of basestring, an not %s' % 
                                (self.__class__.__name__,
                                 item.__class__.__name__))

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

        :param list structure: A list of string showing the desired folders on
          that environment
        :return: None
        """
        self._structure = self._validate_structure(structure)

    def conform(self, version):
        """Conforms the version to this environment by setting its extension.
        """
        logger.debug('conforming version')
        from stalker import Version
        if not isinstance(version, Version):
            raise TypeError('version argument should be a '
                            'stalker.version.Version instance, not %s' %
                            version.__class__.__name__)
        version.update_paths()
        version.extension = self.extensions[0]
        version.created_with = self.name
        logger.debug('version.absolute_full_path : %s' %
                     version.absolute_full_path)
        logger.debug('finished conforming version extension to: %s' %
                     self.extensions[0])

    def initialize_structure(self, version):
        """Initializes the environment folder structure

        :return:
        """
        # check version type
        from stalker import Version
        if not isinstance(version, Version):
            raise TypeError(
                '"version" argument in %s.initialize_structureshould be a '
                'stalker.version.Version instance, not %s' % (
                    self.__class__.__name__,
                    version.__class__.__name__
                )
            )

        # create the folder in version.absolute_path
        extension = version.extension
        version.update_paths()
        version.extension = extension
        for folder in self.structure:
            folder_path = os.path.join(version.absolute_path, folder)
            logger.debug('creating: %s' % folder_path)
            try:
                os.makedirs(folder_path)
            except OSError:
                # dir exists
                pass

    def save_as(self, version, run_pre_publishers=True):
        """A compatibility method which will allow this environment to be used
        in place of stalker.model.env.EnvironmentBase derivatives.

        :param version: stalker.models.version.Version instance
        :param bool run_pre_publishers: Run pre publishers of this environment
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
        atrc_path = os.path.expanduser('~/.atrc/')
        last_version_filename = 'last_version'
        return os.path.join(atrc_path, last_version_filename)

    def append_to_recent_files(self, version):
        """Appends the given version info to the recent files list

        :param version: A :class:`~stalker.models.version.Version` instance.
        :return:
        """
        from stalker import Version
        if not isinstance(version, Version):
            raise TypeError('"version" argument in %s.append_to_recent_files '
                            'method should be an instance of '
                            'stalker.models.version.Version, not %s' %
                            (self.__class__.__name__,
                             version.__class__.__name__))
        last_version_file_full_path = self.get_settings_file_path()
        try:
            os.makedirs(os.path.dirname(last_version_file_full_path))
        except OSError:
            pass

        with open(last_version_file_full_path, 'w') as f:
            f.write(str(version.id))

    def get_last_version(self):
        """returns the current version
        """
        last_version_file_full_path = self.get_settings_file_path()
        try:
            with open(last_version_file_full_path, 'r') as f:
                lines = f.readlines()
                vid = lines[0]
            from stalker import Version
            return Version.query.filter(Version.id==vid).first()
        except (IOError, IndexError):
            return None


class ExternalEnvFactory(object):
    """A factory for External Environments.

    A Factory object for environments. Generates :class:`ExternalEnv`
    instances.
    """

    @classmethod
    def get_env_names(cls, name_format="%n"):
        """returns a list of environment names which it is possible to create
        one environment.

        :param str name_format: A string showing the format of the output
          variables:
            %n : the name of the Environment
            %e : the extension of the Environment

        :return list: list
        """
        env_names = []
        for env_name in external_environments.keys():
            env_data = external_environments[env_name]
            env_names.append(
                name_format
                .replace('%n', env_data['name'])
                .replace('%e', env_data['extensions'][0])
            )
        return env_names

    @classmethod
    def get_env(cls, name, name_format="%n"):
        """Creates an environment with the given name

        :param str name: The name of the environment, should be a value from
          anima.env.externalEnv.environment_names list

        :return ExternalEnv: ExternalEnv instance
        """
        if not isinstance(name, basestring):
            raise TypeError('"name" argument in %s.get_env() should be an '
                            'instance of basestring, not %s' %
                            (cls.__name__, name.__class__.__name__))

        # filter the name
        import re

        # replace anything that doesn't start with '%' with [\s\(\)\-]+
        pattern = re.sub(r'[^%\w]+', '[\s\(\)\-]+', name_format)

        pattern = pattern\
            .replace('%n', '(?P<name>[\w\s]+)')\
            .replace('%e', '(?P<extension>\.\w+)')
        logger.debug('pattern : %s' % pattern)

        match = re.search(pattern, name)
        env_name = None
        if match:
            env_name = match.group('name').strip()

        env_names = external_environments.keys()
        if env_name not in env_names:
            raise ValueError(
                '%s is not in '
                'anima.env.externalEnv.environment_names list, '
                'please supply a value from %s' % (name, env_names))

        env = external_environments[env_name]
        return ExternalEnv(**env)
