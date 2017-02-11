# -*- coding: utf-8 -*-
# Copyright (c) 2012-2015, Anima Istanbul
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

import os
import stat
import datetime
import tempfile
import platform
import logging

# create logger
#logging.basicConfig()
logger = logging.getLogger(__name__)
logging_level = logging.DEBUG
logger.setLevel(logging_level)

# create formatter
logging_formatter = \
    logging.Formatter('%(module)s: %(funcName)s: %(levelname)s: %(message)s')

# create file handler
log_file_path = os.path.join(
    tempfile.gettempdir(),
    'anima.log'
)
log_file_handler = logging.FileHandler(log_file_path)
log_file_handler.setFormatter(logging_formatter)

# add file handler
logger.addHandler(log_file_handler)

# set stalker to use the same logger

# create initial log
#logger.debug('***************************************************************')
#logger.debug('started new anima instance on %s' % datetime.datetime.now())
#logger.debug('***************************************************************')

# fix file mod for log file
os.chmod(
    log_file_path,
    stat.S_IRWXU + stat.S_IRWXG + stat.S_IRWXO -
    stat.S_IXUSR - stat.S_IXGRP - stat.S_IXOTH
)

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

# some media
ffmpeg_command_path = 'ffmpeg'
ffprobe_command_path = 'ffprobe'

max_recent_files = 50

status_colors = {
    'wfd': [171, 186, 195],
    'rts': [209, 91, 71],
    'wip': [255, 198, 87],
    'prev': [111, 179, 224],
    'hrev': [126, 110, 176],
    'drev': [126, 110, 176],
    'cmpl': [130, 175, 111],
    'oh': [213, 63, 64],
    'stop': [78, 89, 98],
}

status_colors_by_id = {}


def fill_status_colors_by_id():
    """fills the status_colors_by_id dictionary
    """
    if not status_colors_by_id:
        from stalker import StatusList
        task_status_list = \
            StatusList.query\
                .filter(StatusList.target_entity_type == 'Task')\
                .first()

        for status in task_status_list.statuses:
            status_colors_by_id[status.id] = status_colors[status.code.lower()]

fill_status_colors_by_id()
