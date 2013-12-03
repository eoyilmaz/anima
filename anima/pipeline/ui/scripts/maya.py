# -*- coding: utf-8 -*-
# Copyright (c) 2012-2013, Anima Istanbul
#
# This module is part of anima-tools and is released under the BSD 2
# License: http://www.opensource.org/licenses/BSD-2-Clause


def version_creator():
    """helper class that has all the methods to display the UI
    """
    from stalker import db
    from stalker.db import DBSession
    DBSession.remove()
    db.setup()

    # use PySide for Maya 2014
    import pymel
    try:
        if pymel.versions.current() >= pymel.versions.v2014:
            from anima.pipeline import ui
            ui.SET_PYSIDE()
    except AttributeError:
        pass

    from anima.pipeline.ui import version_creator
    from anima.pipeline.env import mayaEnv
    reload(version_creator)
    mEnv = mayaEnv.Maya()
    mEnv.name = "Maya%s" % str(pymel.versions.current()[0:4])

    import logging
    logger = logging.getLogger('anima.pipeline.ui.version_creator')
    logger.setLevel(logging.WARNING)

    version_creator.UI()
