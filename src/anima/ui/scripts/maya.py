# -*- coding: utf-8 -*-

import logging

import pymel

from anima.dcc.mayaDCC.common import get_maya_main_window, Maya
from anima.dcc.mayaDCC import archive
from anima.log import logger
from anima.utils import do_db_setup


def show_version_dialog(logging_level=logging.WARNING, mode=2):
    """Show version_dialog UI for Maya."""
    # connect to db
    do_db_setup()

    from anima.ui.dialogs import version_dialog as vd

    maya_dcc = Maya()
    maya_dcc.name = "Maya{}".format(str(pymel.versions.current())[0:4])

    logger.setLevel(logging_level)

    # set the parent object to the maya main window
    vd.UI(dcc=maya_dcc, parent=get_maya_main_window(), mode=mode)


def show_version_updater(logging_level=logging.WARNING):
    """Show version_updater UI for Maya."""
    # connect to db
    do_db_setup()

    from anima.ui.dialogs import version_updater as vu

    maya_dcc = Maya()
    maya_dcc.name = "Maya{}".format(str(pymel.versions.current())[0:4])

    logger.setLevel(logging_level)

    # generate a reference_resolution
    # global version_updater_dialog
    # if version_updater_dialog is None:
    #     version_updater_dialog = version_updater.UI(dcc=m)
    # else:
    #     version_updater_dialog.show()

    # set the parent object to the maya main window
    vu.UI(dcc=maya_dcc, parent=get_maya_main_window())


def show_version_mover():
    """Show version_mover UI for Maya."""
    # connect to db
    do_db_setup()

    from anima.ui.dialogs import version_mover as vm

    vm.UI()


def show_project_manager(logging_level=logging.WARNING):
    """Show project_manager UI for Maya."""
    # connect to db
    do_db_setup()

    from anima.ui.dialogs import project_manager as projman

    # set the parent object to the maya main window
    projman.ui_caller(None, None, show_project_manager.MainWindow)


def show_archiver_dialog(logging_level=logging.WARNING, mode=2):
    """Show archiver dialog UI for Maya."""
    # connect to db
    do_db_setup()

    from anima.ui.base import ui_caller
    from anima.ui.dialogs import archiver_dialog
    import pymel

    maya_dcc = Maya()
    maya_dcc.name = "Maya{}".format(str(pymel.versions.current())[0:4])

    logger.setLevel(logging_level)

    # set the parent object to the maya main window
    ui_caller(
        None,
        None,
        archiver_dialog.MultiVersionSelectDialog,
        dcc=maya_dcc,
        parent=get_maya_main_window(),
        archiver=archive.Archiver(),
    )
