# -*- coding: utf-8 -*-

import logging
from anima import logger


def set_qt_lib():
    """sets the Qt lib according to the maya version"""
    import pymel

    try:
        from anima import ui

        if pymel.versions.current() > 201650:
            ui.SET_PYSIDE2()
        else:
            ui.SET_PYSIDE()
    except AttributeError:
        pass


def version_dialog(logging_level=logging.WARNING, mode=2):
    """Helper function for version_dialog UI for Maya"""
    # connect to db
    from anima.utils import do_db_setup

    do_db_setup()

    # use PySide for Maya 2014
    # and PySide2 for Maya 2017
    set_qt_lib()

    from anima.ui.dialogs import version_dialog as vd
    from anima.dcc import mayaEnv

    m = mayaEnv.Maya()

    import pymel

    m.name = "Maya%s" % str(pymel.versions.current())[0:4]

    logger.setLevel(logging_level)

    # set the parent object to the maya main window
    vd.UI(environment=m, parent=mayaEnv.get_maya_main_window(), mode=mode)


def version_updater(logging_level=logging.WARNING):
    """helper function for version_updater UI for Maya"""
    # connect to db
    from anima.utils import do_db_setup

    do_db_setup()

    # set Qt lib
    set_qt_lib()

    from anima.ui.dialogs import version_updater as vu
    from anima.dcc import mayaEnv

    m = mayaEnv.Maya()

    import pymel

    m.name = "Maya%s" % str(pymel.versions.current())[0:4]

    logger.setLevel(logging_level)

    # generate a reference_resolution
    # global version_updater_dialog
    # if version_updater_dialog is None:
    #     version_updater_dialog = version_updater.UI(environment=m)
    # else:
    #     version_updater_dialog.show()

    # set the parent object to the maya main window
    vu.UI(environment=m, parent=mayaEnv.get_maya_main_window())


def version_mover():
    """ """
    # connect to db
    from anima.utils import do_db_setup

    do_db_setup()

    from anima.ui.dialogs import version_mover as vm

    vm.UI()


def project_manager(logging_level=logging.WARNING):
    """Helper function for project_manager UI for Maya"""
    # connect to db
    from anima.utils import do_db_setup

    do_db_setup()

    # use PySide for Maya 2014
    # and PySide2 for Maya 2017
    set_qt_lib()

    from anima.ui.dialogs import project_manager as projman

    # set the parent object to the maya main window
    projman.ui_caller(None, None, project_manager.MainWindow)


def archiver_dialog(logging_level=logging.WARNING, mode=2):
    """Archiver dialog UI for Maya."""
    # connect to db
    from anima.utils import do_db_setup

    do_db_setup()

    # use PySide for Maya 2014
    # and PySide2 for Maya 2017
    set_qt_lib()

    from anima.dcc import mayaEnv
    from anima.dcc.mayaEnv import archive
    from anima.ui.base import ui_caller
    from anima.ui.dialogs import archiver_dialog
    import pymel

    m = mayaEnv.Maya()
    m.name = "Maya%s" % str(pymel.versions.current())[0:4]

    logger.setLevel(logging_level)

    # set the parent object to the maya main window
    ui_caller(
        None, None, archiver_dialog.MultiVersionSelectDialog,
        environment=m, parent=mayaEnv.get_maya_main_window(),
        archiver=archive.Archiver()
    )
