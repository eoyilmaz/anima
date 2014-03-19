# -*- coding: utf-8 -*-
# Copyright (c) 2012-2013, Anima Istanbul
#
# This module is part of anima-tools and is released under the BSD 2
# License: http://www.opensource.org/licenses/BSD-2-Clause


def edl_importer():
    """Helper script for AVID edl importer
    """
    from anima.ui import SET_PYSIDE
    SET_PYSIDE()

    from anima.ui import edl_importer
    reload(edl_importer)

    edl_importer.UI()
