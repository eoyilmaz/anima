# -*- coding: utf-8 -*-
# Copyright (c) 2012-2017, Anima Istanbul
#
# This module is part of anima-tools and is released under the BSD 2
# License: http://www.opensource.org/licenses/BSD-2-Clause


def version_creator():
    """Helper function for version_creator UI for Max
    """
    from anima.utils import do_db_setup
    do_db_setup()

    from anima import ui
    ui.SET_PYSIDE()

    from anima.ui import version_creator
    from anima.env import max

    m = max.Max()

    version_creator.UI(environment=m)

