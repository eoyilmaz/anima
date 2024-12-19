# -*- coding: utf-8 -*-


def version_dialog(mode=2):
    """Helper function for version_dialog UI for Nuke"""
    # connect to db
    from anima.utils import do_db_setup

    do_db_setup()

    from anima.ui.dialogs import version_dialog
    from anima.dcc import nukeEnv
    import nuke

    n = nukeEnv.Nuke()
    n.name = "nuke%s.%s" % (nuke.NUKE_VERSION_MAJOR, nuke.NUKE_VERSION_MINOR)

    # display only warning messages
    import logging

    logging.getLogger(version_dialog.__name__).setLevel(logging.WARNING)
    logging.getLogger("anima.ui").setLevel(logging.WARNING)
    logging.getLogger("anima.ui.models").setLevel(logging.WARNING)
    logging.getLogger("anima.dcc.nuke").setLevel(logging.WARNING)
    logging.getLogger("stalker.db").setLevel(logging.WARNING)

    version_dialog.UI(environment=n, mode=mode)
