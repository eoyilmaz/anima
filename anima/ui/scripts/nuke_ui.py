# -*- coding: utf-8 -*-

def set_qt_lib():
    import nuke
    if nuke.NUKE_VERSION_MAJOR > 10:
        from anima.ui import SET_PYSIDE2
        SET_PYSIDE2()
    else:
        from anima.ui import SET_PYSIDE
        SET_PYSIDE()


def version_dialog(mode=2):
    """Helper function for version_dialog UI for Nuke
    """
    # connect to db
    from anima.utils import do_db_setup
    do_db_setup()

    # set PySide or PySide2
    set_qt_lib()

    from anima.ui import version_dialog
    from anima.dcc import nukeEnv
    import nuke
    n = nukeEnv.Nuke()
    n.name = "nuke%s.%s" % (nuke.NUKE_VERSION_MAJOR, nuke.NUKE_VERSION_MINOR)

    # display only warning messages
    import logging
    logging.getLogger(version_dialog.__name__).setLevel(logging.WARNING)
    logging.getLogger("anima.ui").setLevel(logging.WARNING)
    logging.getLogger("anima.ui.models").setLevel(logging.WARNING)
    logging.getLogger("anima.dcc.nuke").setLevel(logging.WARNING)
    logging.getLogger("stalker.db").setLevel(logging.WARNING)

    version_dialog.UI(environment=n, mode=mode)
