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

from anima import extension  # extend Stalker classes
from anima import log  # initialize logging
from anima.config import Config
from anima.version import __version__


ALEMBIC = "Alembic"
USD = "USD"
CACHE_FORMAT_DATA = {
    ALEMBIC: {"output_dir": "alembic", "file_extension": ".abc"},
    USD: {"output_dir": "usd", "file_extension": ".usd"},
}
TIMING_RESOLUTION = 10  # in minutes

defaults = Config()
