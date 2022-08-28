# -*- coding: utf-8 -*-

import logging
from anima import logger


def version_dialog(logging_level=logging.WARNING, mode=2):
    """Helper function for version_dialog UI for Maya"""
    # connect to db
    from anima.utils import do_db_setup
    from anima import ui

    do_db_setup()
    ui.SET_PYSIDE2()

    from anima.ui.dialogs import version_dialog
    from anima.dcc import tde4

    tde4_dcc = tde4.TDE4()

    logger.setLevel(logging_level)

    # set the parent object to the maya main window
    version_dialog.UI(environment=tde4_dcc, parent=None, mode=mode)
