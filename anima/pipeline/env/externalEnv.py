# -*- coding: utf-8 -*-
# Copyright (c) 2012-2013, Anima Istanbul
#
# This module is part of anima-tools and is released under the BSD 2
# License: http://www.opensource.org/licenses/BSD-2-Clause

import logging
import os

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

external_environments = [
    {
        'name': 'MudBox',
        'extension': '.mud',
        'structure': [
            'Outputs',
        ]
    },
    {
        'name': 'Photoshop',
        'extension': '.psd',
        'structure': [
            'Outputs',
        ]
    },
    {
        'name': 'ZBrush Project',
        'extension': '.zpr',
        'structure': [
            'Outputs',
        ]
    },
    {
        'name': 'ZBrush Tool',
        'extension': '.ztl',
        'structure': [
            'Outputs',
        ]
    },
]


class ExternalEnv(object):
    """An external environment which doesn't support Python

    A very simple object that handles external environments. For now it just
    returns the name of the environment, conforms the given version to the
    environment by setting its file extension etc.
    """

    def __init__(self, name, extension, structure=None):
        """

        :param name: The name of this environment
        :param extension: The extension of this environment
        :param structure: The folder structure of this environment
        :return:
        """
        self._name = None
        self._extension = None
        self._structure = None

        self.name = self._validate_name(name)
        self.extension = self._validate_extension(extension)
        self.structure = self._validate_structure(structure)

    def _validate_name(self, name):
        """validates the given name value

        :param name: the desired name
        :return: str
        """
        if not isinstance(name, basestring):
            raise TypeError('%s.name should be an instance of '
                            'basestring, not %s' % (
                self.__class__.__name__, name.__class__.__name__)
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

    def _validate_extension(self, extension):
        """validates the given extension value

        :param extension: the desired extension
        :return: str
        """
        if not isinstance(extension, basestring):
            raise TypeError('%s.extension should be an instance of '
                            'basestring, not %s' % (
                self.__class__.__name__, extension.__class__.__name__)
            )
        return extension

    @property
    def extension(self):
        """the extension property getter

        :return: str
        """
        return self._extension

    @extension.setter
    def extension(self, extension):
        """the extension property setter

        :param str extension: A string value for desired extension should
          contain a value which starts with "."
        :return: None
        """
        self._extension = self._validate_extension(extension)

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
        version.extension = self.extension
        logger.debug('finished conforming version extension to: %s' % 
                     self.extension)

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
        version.update_paths()
        for folder in self.structure:
            folder_path = os.path.join(version.absolute_path, folder)
            logger.debug('creating: %s' % folder_path)
            try:
                os.makedirs(folder_path)
            except OSError:
                # dir exists
                pass


class ExternalEnvFactory(object):
    """A factory for External Environments.

    A Factory object for environments. Generates :class:`ExternalEnv`
    instances.
    """

    def get_environment_names(self):
        """returns a list of environment names which it is possible to create
        one environment.

        :return list: list
        """
        pass

    def get_env(self, name):
        """Creates an environment with the given name

        :param name:
        :return:
        """
        pass
