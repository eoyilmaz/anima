# -*- coding: utf-8 -*-

from anima.utils import do_db_setup


def version_dialog(lib="PySide"):
    """Helper function for version_dialog UI for Photoshop

    It uses with PySide by default you can opt to use PyQt4 instead by setting
    the ``lib`` argument to "PyQt4".

    :param str lib: choose a lib, one of ["PySide", "PyQt4"]
    :return: None
    """
    # connect to db
    do_db_setup()

    from anima.ui import SET_PYSIDE, SET_PYQT4

    if lib == "PySide":
        SET_PYSIDE()
    elif lib == "PyQt4":
        SET_PYQT4()

    from anima.dcc import photoshop

    reload(photoshop)
    p = photoshop.Photoshop()

    from anima.ui import version_dialog

    reload(version_dialog)
    # display only warning messages
    import logging

    logging.getLogger(version_dialog.__name__).setLevel(logging.WARNING)
    logging.getLogger("anima.ui").setLevel(logging.WARNING)
    logging.getLogger("anima.ui.models").setLevel(logging.WARNING)
    logging.getLogger("anima.dcc.photoshop").setLevel(logging.WARNING)
    logging.getLogger("stalker.db").setLevel(logging.WARNING)

    version_dialog.UI(environment=p)
