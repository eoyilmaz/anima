# -*- coding: utf-8 -*-
# Copyright (c) 2012-2017, Anima Istanbul
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

import os
import stat
import tempfile
import logging
from anima.config import Config

__version__ = "0.3.2"

# create logger
# logging.basicConfig()
logger = logging.getLogger(__name__)
logging_level = logging.ERROR
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

# fix file mod for log file
os.chmod(
    log_file_path,
    stat.S_IRWXU + stat.S_IRWXG + stat.S_IRWXO -
    stat.S_IXUSR - stat.S_IXGRP - stat.S_IXOTH
)

defaults = Config()
