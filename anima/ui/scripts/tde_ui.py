# -*- coding: utf-8 -*-

import logging
from anima import logger


def version_dialog(logging_level=logging.WARNING, mode=2):
    """Helper function for version_dialog UI for Maya
    """
    # connect to db
    from anima.utils import do_db_setup
    do_db_setup()

    # use PySide2
    from anima import ui
    ui.SET_PYSIDE2()

    from anima.ui import version_dialog
    from anima.env import equalizer
    e = equalizer.Equalizer()
    e.name = tde4.get3DEVersion().split(" ")[0]

    logger.setLevel(logging_level)

    # set the parent object to the maya main window
    version_dialog.UI(environment=e, mode=mode)
