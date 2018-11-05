# -*- coding: utf-8 -*-
# Copyright (c) 2012-2018, Anima Istanbul
#
# This module is part of anima-tools and is released under the BSD 2
# License: http://www.opensource.org/licenses/BSD-2-Clause
import logging

from anima import logger

# version_creator_dialog = None
# version_updater_dialog = None


def set_qt_lib():
    """sets the Qt lib according to the maya version
    """
    import pymel
    try:
        from anima import ui
        if pymel.versions.current() > 201650:
            ui.SET_PYSIDE2()
        else:
            ui.SET_PYSIDE()
    except AttributeError:
        pass


def version_creator(logging_level=logging.WARNING):
    """Helper function for version_creator UI for Maya
    """
    # connect to db
    from anima.utils import do_db_setup
    do_db_setup()

    # use PySide for Maya 2014
    # and PySide2 for Maya 2017
    set_qt_lib()

    from anima.ui import version_creator
    from anima.env import mayaEnv
    m = mayaEnv.Maya()

    import pymel
    m.name = "Maya%s" % str(pymel.versions.current())[0:4]

    logger.setLevel(logging_level)

    # global version_creator_dialog
    # if version_creator_dialog is None:
    #     version_creator_dialog = version_creator.UI(environment=m)
    # else:
    #     version_creator_dialog.show()

    # set the parent object to the maya main window
    version_creator.UI(environment=m, parent=mayaEnv.get_maya_main_window())


def version_updater(logging_level=logging.WARNING):
    """helper function for version_updater UI for Maya
    """
    # connect to db
    from anima.utils import do_db_setup
    do_db_setup()

    # set Qt lib
    set_qt_lib()

    from anima.ui import version_updater
    from anima.env import mayaEnv
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
    version_updater.UI(environment=m, parent=mayaEnv.get_maya_main_window())


def version_mover():
    """
    """
    # connect to db
    from anima.utils import do_db_setup
    do_db_setup()

    from anima.ui import version_mover as vm
    vm.UI()
