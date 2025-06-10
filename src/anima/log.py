"""Logging related functionalities are situated here."""

import logging
import os
import stat
import tempfile

# create logger
# logging.basicConfig()
from stalker.log import get_logger, set_level


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
