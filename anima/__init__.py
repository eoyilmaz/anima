# -*- coding: utf-8 -*-
# Copyright (c) 2012-2014, Anima Istanbul
#
# This module is part of anima-tools and is released under the BSD 2
# License: http://www.opensource.org/licenses/BSD-2-Clause
"""Anima Pipeline Library

Anima uses ``Stalker Configuration Framework``.

To be able to make it work set the STALKER_CONFIG environment variable to a
valid configuration folder (which has a config.py file inside, if there is no
config.py file create one).

Place the following variables in to the config.py file::

  database_engine_settings = {
      'sqlalchemy.url': 'dialect://user:password@a.b.c.d/stalker',
      'sqlalchemy.echo': False,
      'sqlalchemy.pool_size': 1,
      'sqlalchemy.max_overflow': 3
  }

  stalker_server_internal_address = 'http://a.b.c.d:xxxx'
  stalker_server_external_address = 'http://e.f.g.h:xxxx'
"""

__version__ = "0.1.13.dev"

from stalker import defaults

import logging
logging.basicConfig()
logging_level = logging.DEBUG


stalker_server_internal_address = ''
stalker_server_external_address = ''
try:
    stalker_server_internal_address = defaults.stalker_server_internal_address
    stalker_server_external_address = defaults.stalker_server_external_address
except KeyError:
    pass

stalker_dummy_user_login = 'anima'
stalker_dummy_user_pass = 'anima'
local_cache_folder = '~/.cache/anima/'
recent_file_name = 'recent_files'
avid_media_file_path_storage = 'avid_media_file_path'

normal_users_group_names = ['Normal Users']
power_users_group_names = ['Power Users', 'admins']

# environment variable template for repositories
repo_env_template = 'REPO%(id)s'

anima_env_var = 'ANIMAPATH'
env_var_file_name = 'env.json'
