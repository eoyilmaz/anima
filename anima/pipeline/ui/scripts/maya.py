# -*- coding: utf-8 -*-
# Copyright (c) 2012-2013, Anima Istanbul
#
# This module is part of anima-tools and is released under the BSD 2
# License: http://www.opensource.org/licenses/BSD-2-Clause
from anima.pipeline.ui.scripts import do_db_setup


def version_creator():
    """helper class that has all the methods to display the UI
    """
    # connect to db
    do_db_setup()

    # use PySide for Maya 2014
    import pymel
    try:
        if pymel.versions.current() >= pymel.versions.v2014:
            from anima.pipeline import ui
            ui.SET_PYSIDE()
    except AttributeError:
        pass

    from anima.pipeline.ui import version_creator, models
    from anima.pipeline.env import mayaEnv
    reload(version_creator)
    reload(models)
    mEnv = mayaEnv.Maya()
    mEnv.name = "Maya%s" % str(pymel.versions.current())[0:4]

    import logging
    logger = logging.getLogger('anima.pipeline.ui.version_creator')
    logger.setLevel(logging.WARNING)
    logger = logging.getLogger('anima.pipeline.ui.models')
    logger.setLevel(logging.WARNING)

    version_creator.UI(mEnv)
