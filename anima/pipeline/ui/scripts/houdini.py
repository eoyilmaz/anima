# -*- coding: utf-8 -*-
# Copyright (c) 2012-2013, Anima Istanbul
#
# This module is part of anima-tools and is released under the BSD 2
# License: http://www.opensource.org/licenses/BSD-2-Clause
from anima.pipeline.ui.scripts import do_db_setup


def version_creator():
    """helper function to display version_creator in houdini
    """
    # connect to db
    do_db_setup()

    from anima.pipeline.ui import version_creator
    from anima.pipeline.env import houdiniEnv
    hEnv = houdiniEnv.Houdini()

    import logging
    logger = logging.getLogger('anima.pipeline.ui.version_creator')
    logger.setLevel(logging.WARNING)
    logger = logging.getLogger('anima.pipeline.ui.models')
    logger.setLevel(logging.WARNING)

    version_creator.UI(hEnv)
