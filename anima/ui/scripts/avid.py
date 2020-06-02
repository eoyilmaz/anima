# -*- coding: utf-8 -*-
# Copyright (c) 2012-2020, Anima Istanbul
#
# This module is part of anima and is released under the MIT
# License: http://www.opensource.org/licenses/MIT


def edl_importer():
    """Helper script for AVID edl importer
    """
    from anima.ui import SET_PYSIDE
    SET_PYSIDE()

    from anima.ui import edl_importer
    reload(edl_importer)

    edl_importer.UI()
