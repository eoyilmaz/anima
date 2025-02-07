# -*- coding: utf-8 -*-

import logging

from anima.dcc import motion_builder as motion_builder_dcc
from anima.log import logger
from anima.utils import do_db_setup


def show_version_dialog(logging_level : int = logging.WARNING) -> None:
    """Show version_dialog UI for MotionBuilder."""
    # connect to db
    do_db_setup()

    from anima.ui.dialogs import version_dialog

    mb_dcc = motion_builder_dcc.MotionBuilder()
    logger.setLevel(logging_level)
    version_dialog.UI(dcc=mb_dcc)
