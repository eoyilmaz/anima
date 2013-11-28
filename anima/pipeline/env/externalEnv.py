# -*- coding: utf-8 -*-
# Copyright (c) 2012-2013, Anima Istanbul
#
# This module is part of anima-tools and is released under the BSD 2
# License: http://www.opensource.org/licenses/BSD-2-Clause


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
        pass

    def conform(self, version):
        """Conforms the version to this environment by setting its extension.
        """
        pass

    def initialize_structure(self, version):
        """Initializes the environment folder structure

        :return:
        """
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
