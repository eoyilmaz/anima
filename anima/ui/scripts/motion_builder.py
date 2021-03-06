# -*- coding: utf-8 -*-
# Copyright (c) 2012-2020, Anima Istanbul
#
# This module is part of anima and is released under the MIT
# License: http://www.opensource.org/licenses/MIT
import logging
from anima import logger


def set_qt_lib():
    """sets the Qt lib according to the motion builder version
    """
    from anima import ui
    ui.SET_PYSIDE()


def version_dialog(logging_level=logging.WARNING):
    """Helper function for version_dialog UI for MotionBuilder
    """
    # connect to db
    from anima.utils import do_db_setup
    do_db_setup()

    # set Qt library
    set_qt_lib()

    from anima.ui import version_dialog
    from anima.env import motion_builder
    mb = motion_builder.MotionBuilder()

    logger.setLevel(logging_level)

    version_dialog.UI(environment=mb)
