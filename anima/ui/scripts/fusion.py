# -*- coding: utf-8 -*-

import logging

from anima import logger


def version_dialog(lib="PySide", logging_level=logging.WARNING, parent=None):
    """Helper function for version_dialog UI for Fusion

    It uses with PySide by default you can opt to use PyQt4 instead by setting
    the ``lib`` argument to "PyQt4".

    :param str lib: choose a lib, one of ["PySide", "PyQt4"]
    :param logging_level:
    :return: None
    """
    # connect to db
    from anima.utils import do_db_setup

    do_db_setup()

    from anima.dcc import fusion

    fusion_env = fusion.Fusion()
    fusion_env.name = "Fusion"

    from anima.ui.dialogs import version_dialog

    logger.setLevel(logging_level)
    version_dialog.UI(environment=fusion_env, parent=parent)
