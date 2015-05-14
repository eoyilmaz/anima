# -*- coding: utf-8 -*-
# Copyright (c) 2012-2015, Anima Istanbul
#
# This module is part of anima-tools and is released under the BSD 2
# License: http://www.opensource.org/licenses/BSD-2-Clause

from anima import logger
from anima.ui import SET_PYQT4
from anima.utils import do_db_setup

SET_PYQT4()

import logging


def version_creator():
    """Helper function for version_creator UI for Houdini
    """
    # connect to db
    do_db_setup()

    from stalker import log
    log.logging_level = logging.WARNING

    from anima.ui import version_creator
    from anima.env import houdini
    reload(houdini)
    reload(version_creator)

    h = houdini.Houdini()

    logger.setLevel(logging.WARNING)

    version_creator.UI(environment=h)
