# -*- coding: utf-8 -*-
# Copyright (c) 2012-2013, Anima Istanbul
#
# This module is part of anima-tools and is released under the BSD 2
# License: http://www.opensource.org/licenses/BSD-2-Clause
import logging

from anima import logger
from anima.utils import do_db_setup


def version_creator(lib='PySide', logging_level=logging.WARNING):
    """Helper function for version_creator UI for Fusion

    It uses with PySide by default you can opt to use PyQt4 instead by setting
    the ``lib`` argument to "PyQt4".

    :param str lib: choose a lib, one of ["PySide", "PyQt4"]
    :param logging_level:
    :return: None
    """
    # connect to db
    do_db_setup()

    from anima.ui import SET_PYSIDE, SET_PYQT4
    if lib == 'PySide':
        SET_PYSIDE()
    elif lib == 'PyQt4':
        SET_PYQT4()

    from anima.env import fusion
    reload(fusion)
    fusion_env = fusion.Fusion()
    fusion_env.name = 'Fusion'

    from anima.ui import version_creator
    logger.setLevel(logging_level)
    version_creator.UI(environment=fusion_env)
