# -*- coding: utf-8 -*-
# Copyright (c) 2012-2014, Anima Istanbul
#
# This module is part of anima-tools and is released under the BSD 2
# License: http://www.opensource.org/licenses/BSD-2-Clause
from anima.env import houdini
from anima.ui import version_creator
from anima.ui.scripts import do_db_setup


def version_creator():
    """Helper function for version_creator UI for Houdini
    """
    # connect to db
    do_db_setup()

    h = houdini.Houdini()

    import logging
    logger = logging.getLogger('anima.ui.version_creator')
    logger.setLevel(logging.WARNING)
    logger = logging.getLogger('anima.ui.models')
    logger.setLevel(logging.WARNING)

    version_creator.UI(environment=h)
