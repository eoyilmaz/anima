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

import sys
import os
import stat
import tempfile
import logging
from anima.config import Config
from stalker import SimpleEntity, Project

__version__ = "0.8.0"

string_types = []
if sys.version_info[0] >= 3:  # Python 3
    string_types = tuple([str])
else:  # Python 2
    string_types = tuple([str, unicode])


ALEMBIC = "Alembic"
USD = "USD"
CACHE_FORMAT_DATA = {
    ALEMBIC: {"output_dir": "alembic", "file_extension": ".abc"},
    USD: {"output_dir": "usd", "file_extension": ".usd"},
}


def get_generic_text_attr(self, attr):
    """patch Simple entity to add new functionality"""
    import json

    attr_value = None
    if self.generic_text:
        data = json.loads(self.generic_text)
        attr_value = data.get(attr)
    return attr_value


def set_generic_text_attr(self, attr, value):
    """patch Simple entity to add new functionality"""
    import json

    data = {}
    if self.generic_text:
        data = json.loads(self.generic_text)
    data[attr] = value
    self.generic_text = json.dumps(data)


SimpleEntity.get_generic_text_attr = get_generic_text_attr
SimpleEntity.set_generic_text_attr = set_generic_text_attr


# Patch Stalker.Project
@property
def is_managed(self):
    """Return True if this is a managed project."""
    project_repo = self.repository
    return not os.path.exists(
        os.path.join(
            project_repo.path, self.code, "unmanaged_project"
        )
    )


@property
def cache_format(self):
    """Return the project cache format.

    By default it is Alembic.
    """
    project_repo = self.repository

    if os.path.exists(
        os.path.join(
            project_repo.path, self.code, "use_usd"
        )
    ):
        return USD
    else:
        return ALEMBIC


Project.is_managed = is_managed
Project.cache_format = cache_format


# create logger
# logging.basicConfig()
logger = logging.getLogger(__name__)
logging_level = logging.ERROR
logger.setLevel(logging_level)

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

# set stalker to use the same logger

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

TIMING_RESOLUTION = 10  # in minutes

defaults = Config()
