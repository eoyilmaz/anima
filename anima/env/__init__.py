# -*- coding: utf-8 -*-
# Copyright (c) 2012-2018, Anima Istanbul
#
# This module is part of anima-tools and is released under the BSD 2
# License: http://www.opensource.org/licenses/BSD-2-Clause

import os
import json
import platform


def empty_reference_resolution(root=None, leave=None, update=None, create=None):
    """Generates an empty reference_resolution dictionary.

    Generates a ``Reference Resolution`` dictionary, where there are keys like
    'root', 'leave', 'update', 'create' showing:

    root: the versions referenced directly to the root,
    leave: Versions those doesn't have any new versions,
    update: Versions does have an updated version,
    create: Versions that should be updated by creating a new published version
      because its references has updated versions.

    :return: dict
    """
    return {
        'root': [] if root is None else root,
        'leave': [] if leave is None else leave,
        'update': [] if update is None else update,
        'create': [] if create is None else create
    }


def discover_env_vars(env_name=''):
    """Looks for an ``env.json`` file in the path shown with the $ANIMAPATH
    environment variable then creates the environment variables.

    If the ``env_name`` argument is given it will initialize the environment
    variables registered under that environment name.

    The ``env.json`` file format is as follows::

      {
        "env_name": {
          "os_name": {
            "var_name": ['values']
          }
        }
      }

    If "*" is given as the "env_name" (in the env.json file), all the variables
    will be registered regardless of what the ``env_name`` argument is given.

    A typical setup can be something as follows::

    {
      "*": {
        "windows": {
          "PYTHONPATH": []
        },
        "linux": {
          "PYTHONPATH": []
        },
        "osx": {
          "PYTHONATPATH": []
        }
      },
      "python2.6": {
        "windows": {
          "PYTHONPATH": []
        },
        "linux": {},
        "osx": {}
      },
      "python2.7": {
        "windows": {},
        "linux": {},
        "osx": {}
      },
      "python3": {
        "windows": {},
        "linux": {},
        "osx": {}
      },
      "maya": {
        "windows": {
          "MAYA_SCRIPTS_PATH": []
        },
        "linux": {},
        "osx": {}
      },
      "houdini": {
        "windows": {},
        "linux": {},
        "osx": {}
      },
      "nuke": {
        "windows": {},
        "linux": {},
        "osx": {}
      },
      "fusion": {
        "windows": {},
        "linux": {},
        "osx": {}
      },
      "photoshop": {
        "windows": {},
        "linux": {},
        "osx": {}
      },
      "blender": {
        "windows": {},
        "linux": {},
        "osx": {}
      },
    }

    The environment variables defined in "*" will be defined first and then
    the others will run. So defining some environment variables in "*" first
    and the let say under "blender" will not overwrite the variable values
    those are defined at "*".

    None of the definitions will overwrite system variables. So if you defined
    PYTHONPATH in your system environment then the variables defined in
    env.json will be appended to them.
    """
    from anima import defaults
    env_path = os.environ[defaults.anima_env_var]

    env_json_path = os.path.join(env_path, defaults.env_var_file_name)

    # parse the file as a json file
    with open(env_json_path) as f:
        data = json.load(f)

    # get the current os
    os_name = platform.system().lower()

    # replace darwin with osx
    if os_name == 'darwin':
        os_name = 'osx'

    # get the keys
    # first get *
    def append_data_from(env_name_i):
        if env_name_i in data:
            if os_name in data[env_name_i]:
                for env_var in data[env_name_i][os_name]:
                    values = data[env_name_i][os_name][env_var]
                    if env_var in os.environ:
                        values.insert(0, os.environ[env_var])

                    os.environ[env_var] = os.pathsep.join(values)

    append_data_from('*')
    append_data_from(env_name)
