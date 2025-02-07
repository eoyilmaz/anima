# -*- coding: utf-8 -*-

import logging

from anima.log import logger
from anima.utils import do_db_setup


def show_version_dialog(logging_level=logging.WARNING, mode=2):
    """Show version_dialog UI for 3DE4."""
    # connect to db

    do_db_setup()

    from anima.ui.dialogs import version_dialog
    from anima.dcc import tde4

    tde4_dcc = tde4.TDE4()

    logger.setLevel(logging_level)

    # set the parent object to the maya main window
    version_dialog.UI(dcc=tde4_dcc, parent=None, mode=mode)
