# -*- coding: utf-8 -*-

import logging
from anima import logger


def version_dialog(logging_level=logging.WARNING):
    """Helper function for version_dialog UI for MotionBuilder"""
    # connect to db
    from anima.utils import do_db_setup

    do_db_setup()

    from anima.ui.dialogs import version_dialog
    from anima.dcc import motion_builder

    mb = motion_builder.MotionBuilder()

    logger.setLevel(logging_level)

    version_dialog.UI(environment=mb)
