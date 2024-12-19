# -*- coding: utf-8 -*-


import hou

from anima import logger
from anima.dcc.houdini.utils import Executor
from anima.utils import do_db_setup


def version_dialog(mode=2):
    """Helper function for version_dialog UI for Houdini"""
    # connect to db
    do_db_setup()

    import logging
    from stalker import log

    log.logging_level = logging.WARNING

    from anima.ui.dialogs import version_dialog
    from anima.dcc import houdini

    h = houdini.Houdini()
    logger.setLevel(logging.WARNING)

    if hou.applicationVersion()[0] <= 13:
        version_dialog.UI(environment=h, mode=mode)
    else:
        version_dialog.UI(environment=h, executor=Executor(), mode=mode)
