# -*- coding: utf-8 -*-
# Copyright (c) 2012-2020, Erkan Ozgur Yilmaz
#
# This module is part of anima and is released under the MIT
# License: http://www.opensource.org/licenses/MIT
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


def version_dialog(logging_level=logging.WARNING):
    """Helper function for version_dialog UI for Maya
    """
    # connect to db
    from anima.utils import do_db_setup
    do_db_setup()

    # use PySide2
    from anima import ui
    ui.SET_PYSIDE2()

    from anima.ui import version_dialog
    from anima.env import blender as blender_env
    b = blender_env.Blender()

    logger.setLevel(logging_level)

    # set the parent object to the maya main window
    version_dialog.UI(environment=b, parent=None)
