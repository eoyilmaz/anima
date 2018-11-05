# -*- coding: utf-8 -*-
# Copyright (c) 2012-2018, Anima Istanbul
#
# This module is part of anima-tools and is released under the BSD 2
# License: http://www.opensource.org/licenses/BSD-2-Clause
from anima.utils import do_db_setup


def version_creator(lib='PySide'):
    """Helper function for version_creator UI for Photoshop

    It uses with PySide by default you can opt to use PyQt4 instead by setting
    the ``lib`` argument to "PyQt4".

    :param str lib: choose a lib, one of ["PySide", "PyQt4"]
    :return: None
    """
    # connect to db
    do_db_setup()

    from anima.ui import SET_PYSIDE, SET_PYQT4
    if lib == 'PySide':
        SET_PYSIDE()
    elif lib == 'PyQt4':
        SET_PYQT4()

    from anima.env import photoshop
    reload(photoshop)
    p = photoshop.Photoshop()

    from anima.ui import version_creator
    reload(version_creator)
    # display only warning messages
    import logging
    logging.getLogger(version_creator.__name__).setLevel(logging.WARNING)
    logging.getLogger("anima.ui").setLevel(logging.WARNING)
    logging.getLogger("anima.ui.models").setLevel(logging.WARNING)
    logging.getLogger("anima.env.photoshop").setLevel(
        logging.WARNING)
    logging.getLogger("stalker.db").setLevel(logging.WARNING)

    version_creator.UI(environment=p)
