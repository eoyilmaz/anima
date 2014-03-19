# -*- coding: utf-8 -*-
# Copyright (c) 2012-2013, Anima Istanbul
#
# This module is part of anima-tools and is released under the BSD 2
# License: http://www.opensource.org/licenses/BSD-2-Clause
from anima.ui.scripts import do_db_setup


def version_creator():
    """Helper function for version_creator UI for Nuke
    """
    # connect to db
    do_db_setup()

    # use PySide
    from anima import ui
    ui.SET_PYSIDE()

    from anima.ui import version_creator
    from anima.env import nukeEnv
    n = nukeEnv.Nuke()
    n.name = "Nuke"

    # display only warning messages
    import logging
    logging.getLogger(version_creator.__name__).setLevel(logging.WARNING)
    logging.getLogger("anima.ui").setLevel(logging.WARNING)
    logging.getLogger("anima.ui.models").setLevel(logging.WARNING)
    logging.getLogger("anima.env.nuke").setLevel(logging.WARNING)
    logging.getLogger("stalker.db").setLevel(logging.WARNING)

    version_creator.UI(environment=n)
