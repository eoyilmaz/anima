# -*- coding: utf-8 -*-
# Copyright (c) 2012-2014, Anima Istanbul
#
# This module is part of anima-tools and is released under the BSD 2
# License: http://www.opensource.org/licenses/BSD-2-Clause
from anima.pipeline.ui.scripts import do_db_setup


def version_creator():
    """Helper function for version_creator UI for Maya
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

    version_creator.UI(environment=mEnv)


def version_updater():
    """helper function for version_updater UI for Maya
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

    from anima.pipeline.ui import version_updater, models
    from anima.pipeline.env import mayaEnv
    reload(version_updater)
    reload(models)
    maya_env = mayaEnv.Maya()
    maya_env.name = "Maya" + str(pymel.versions.current())[0:4]

    import logging
    logger = logging.getLogger('anima.pipeline.env.base')
    logger.setLevel(logging.WARNING)
    logger = logging.getLogger('anima.pipeline.ui.version_updater')
    logger.setLevel(logging.WARNING)
    logger = logging.getLogger('anima.pipeline.ui.models')
    logger.setLevel(logging.WARNING)

    # generate a reference_resolution
    reference_resolution = maya_env.check_referenced_versions()
    version_updater.UI(environment=maya_env,
                       reference_resolution=reference_resolution)
