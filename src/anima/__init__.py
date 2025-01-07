# -*- coding: utf-8 -*-
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

import logging
import os
import stat
import tempfile


from anima import extension  # extend Stalker classes
from anima.config import Config
from anima.version import __version__

from stalker.log import get_logger, set_level


ALEMBIC = "Alembic"
USD = "USD"
CACHE_FORMAT_DATA = {
    ALEMBIC: {"output_dir": "alembic", "file_extension": ".abc"},
    USD: {"output_dir": "usd", "file_extension": ".usd"},
}
TIMING_RESOLUTION = 10  # in minutes


# create logger
# logging.basicConfig()
logger = get_logger(__name__)
logging_level = logging.ERROR
set_level(logging_level)

# create formatter
logging_formatter = logging.Formatter(
    "%(module)s: %(funcName)s: %(levelname)s: %(message)s"
)

# create file handler
log_file_path = os.path.join(tempfile.gettempdir(), "anima.log")
log_file_handler = logging.FileHandler(log_file_path)
log_file_handler.setFormatter(logging_formatter)

# add file handler
logger.addHandler(log_file_handler)

# fix file mod for log file
os.chmod(
    log_file_path,
    stat.S_IRWXU
    + stat.S_IRWXG
    + stat.S_IRWXO
    - stat.S_IXUSR
    - stat.S_IXGRP
    - stat.S_IXOTH,
)

defaults = Config()
