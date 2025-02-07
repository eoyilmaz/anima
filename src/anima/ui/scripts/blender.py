# -*- coding: utf-8 -*-
"""
Initialize Python Environment with the following code (will be automated later on):

import sys
import os
for path in os.environ["PYTHONPATH"].split(os.path.pathsep):
    sys.path.append(path)

from anima.ui.scripts import blender
blender.show_version_dialog()

"""
import logging

from anima.log import logger
from anima.utils import do_db_setup
from anima.ui.dialogs import version_dialog, version_updater
from anima.dcc import blender as blender_dcc


def show_version_dialog(logging_level=logging.WARNING, mode=2):
    """Show version_dialog UI for Blender."""
    # connect to db
    do_db_setup()
    b = blender_dcc.Blender()
    logger.setLevel(logging_level)
    # set the parent object to the maya main window
    version_dialog.UI(dcc=b, parent=None, mode=mode)


def show_version_updater(logging_level=logging.WARNING):
    """Show version_dialog UI for Blender."""
    # connect to db
    do_db_setup()
    b = blender_dcc.Blender()
    logger.setLevel(logging_level)
    # set the parent object to the blender main window
    version_updater.UI(dcc=b, parent=None)
