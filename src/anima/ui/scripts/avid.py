# -*- coding: utf-8 -*-


def edl_importer():
    """Helper script for AVID edl importer."""
    from anima.ui.dialogs import edl_importer

    reload(edl_importer)

    edl_importer.UI()
