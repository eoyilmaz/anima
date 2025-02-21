# -*- coding: utf-8 -*-

import logging
from typing import TYPE_CHECKING, Optional

from anima.dcc.resolve import toolbox
from anima.log import logger
from anima.utils import do_db_setup


if TYPE_CHECKING:
    from anima.ui.lib.QtWidgets import QWidget


def show_toolbox(
    logging_level: int = logging.WARNING, parent: Optional["QWidget"] = None
) -> None:
    """Show toolbox for Resolve.

    It uses with PySide by default you can opt to use PyQt4 instead by setting
    the ``lib`` argument to "PyQt4".

    Args:
        logging_level (int): Set the logging level. Default is logging.WARNING.
        parent (QWidget): The parent widget. Default is None.
    """
    do_db_setup()

    dialog = toolbox.UI()
    return dialog
