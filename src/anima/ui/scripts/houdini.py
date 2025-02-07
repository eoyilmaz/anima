# -*- coding: utf-8 -*-

import logging

import hou

from stalker import log

from anima.dcc import houdini as houdini_dcc
from anima.dcc.houdini.utils import Executor
from anima.log import logger
from anima.utils import do_db_setup


def show_version_dialog(mode=2):
    """Show version_dialog UI for Houdini.

    Args:
        mode (int): 0: Create, 1: Update, 2: Create or Update.
    """
    # connect to db
    do_db_setup()

    log.logging_level = logging.WARNING

    from anima.ui.dialogs import version_dialog

    h = houdini_dcc.Houdini()
    logger.setLevel(logging.WARNING)

    if hou.applicationVersion()[0] <= 13:
        version_dialog.UI(dcc=h, mode=mode)
    else:
        version_dialog.UI(dcc=h, executor=Executor(), mode=mode)
