# -*- coding: utf-8 -*-
"""
Initialize Python Environment with the following code (will be automated later on):

import sys
import os
for path in os.environ["PYTHONPATH"].split(os.path.pathsep):
    sys.path.append(path)

from anima.ui.scripts import blender
blender.version_dialog()

"""


import logging

from anima import logger


def version_dialog(logging_level=logging.WARNING, mode=2):
    """Helper function for version_dialog UI for Blender"""
    # connect to db
    from anima.utils import do_db_setup

    do_db_setup()

    # use PySide2
    from anima import ui

    ui.SET_PYSIDE2()

    from anima.ui.dialogs import version_dialog
    from anima.dcc import blender as blender_dcc

    b = blender_dcc.Blender()

    logger.setLevel(logging_level)

    # set the parent object to the maya main window
    version_dialog.UI(environment=b, parent=None, mode=mode)


def version_updater(logging_level=logging.WARNING):
    """Helper function for version_dialog UI for Blender"""
    # connect to db
    from anima.utils import do_db_setup

    do_db_setup()

    # use PySide2
    from anima import ui

    ui.SET_PYSIDE2()

    from anima.ui.dialogs import version_updater
    from anima.dcc import blender

    b = blender.Blender()

    logger.setLevel(logging_level)

    # set the parent object to the blender main window
    version_updater.UI(environment=b, parent=None)
