# -*- coding: utf-8 -*-
# Copyright (c) 2012-2014, Anima Istanbul
#
# This module is part of anima-tools and is released under the BSD 2
# License: http://www.opensource.org/licenses/BSD-2-Clause
from anima.pipeline.ui.scripts import do_db_setup


def version_creator(lib='PySide'):
    """Helper function for version_creator UI for Photoshop

    It uses with PySide by default you can opt to use PyQt4 instead by setting
    the ``lib`` argument to "PyQt4".

    :param str lib: choose a lib, one of ["PySide", "PyQt4"]
    :return: None
    """
    # connect to db
    do_db_setup()

    from anima.pipeline.ui import SET_PYSIDE, SET_PYQT4
    if lib == 'PySide':
        SET_PYSIDE()
    elif lib == 'PyQt4':
        SET_PYQT4()

    from anima.pipeline.env.photoshopEnv import Photoshop
    photoshop_env = Photoshop()

    from anima.pipeline.ui import version_creator
    # display only warning messages
    import logging
    logging.getLogger(version_creator.__name__).setLevel(logging.WARNING)
    logging.getLogger("anima.pipeline.ui").setLevel(logging.WARNING)
    logging.getLogger("anima.pipeline.ui.models").setLevel(logging.WARNING)
    logging.getLogger("anima.pipeline.env.photoshopEnv").setLevel(
        logging.WARNING)
    logging.getLogger("stalker.db").setLevel(logging.WARNING)

    version_creator.UI(environment=photoshop_env)
