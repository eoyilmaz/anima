# -*- coding: utf-8 -*-

import logging
from typing import TYPE_CHECKING

from anima.dcc import fusion as fusion_dcc
from anima.log import logger
from anima.utils import do_db_setup


if TYPE_CHECKING:
    from qtpy.QtWidgets import QWidget


def show_version_dialog(
    lib: str = "PySide", logging_level: int = logging.WARNING, parent: "QWidget" = None
):
    """Show version_dialog UI for Fusion.

    It uses with PySide by default you can opt to use PyQt4 instead by setting
    the ``lib`` argument to "PyQt4".

    Args:
        lib (str): Choose a lib, one of ["PySide", "PyQt4"]
        logging_level (int): The logging level.
    """
    # connect to db
    do_db_setup()

    fusion_env = fusion_dcc.Fusion()
    fusion_env.name = "Fusion"

    from anima.ui.dialogs import version_dialog

    logger.setLevel(logging_level)
    version_dialog.UI(dcc=fusion_env, parent=parent)
