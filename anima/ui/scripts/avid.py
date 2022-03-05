# -*- coding: utf-8 -*-


def edl_importer():
    """Helper script for AVID edl importer"""
    from anima.ui import SET_PYSIDE

    SET_PYSIDE()

    from anima.ui import edl_importer

    reload(edl_importer)

    edl_importer.UI()
