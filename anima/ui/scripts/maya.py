# -*- coding: utf-8 -*-
# Copyright (c) 2012-2015, Anima Istanbul
#
# This module is part of anima-tools and is released under the BSD 2
# License: http://www.opensource.org/licenses/BSD-2-Clause
import logging

from anima import logger
from anima.env.mayaEnv import Maya
from anima.utils import do_db_setup

def set_qt_lib():
    """sets the Qt lib according to the maya version
    """
    import pymel
    try:
        from anima import ui
        if pymel.versions.current() > 201500:
            ui.SET_PYSIDE2()
        else:
            ui.SET_PYSIDE()
    except AttributeError:
        pass


def version_creator(logging_level=logging.WARNING):
    """Helper function for version_creator UI for Maya
    """
    # connect to db
    do_db_setup()

    # use PySide for Maya 2014
    set_qt_lib()

    from anima.ui import version_creator, models
    from anima.env import mayaEnv
    reload(version_creator)
    reload(models)
    reload(mayaEnv)
    m = Maya()

    import pymel
    m.name = "Maya%s" % str(pymel.versions.current())[0:4]

    logger.setLevel(logging_level)

    version_creator.UI(environment=m)


def version_updater(logging_level=logging.WARNING):
    """helper function for version_updater UI for Maya
    """
    # connect to db
    do_db_setup()

    # set Qt lib
    set_qt_lib()

    from anima.ui import version_updater, models
    from anima.env import mayaEnv
    reload(mayaEnv)
    reload(version_updater)
    reload(models)
    m = Maya()
    import pymel
    m.name = "Maya" + str(pymel.versions.current())[0:4]

    logger.setLevel(logging_level)

    # generate a reference_resolution
    version_updater.UI(environment=m)


def version_mover():
    """
    """
    # connect to db
    do_db_setup()

    from anima.ui import version_mover as vm
    vm.UI()
