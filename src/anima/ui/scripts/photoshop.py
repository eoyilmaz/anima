# -*- coding: utf-8 -*-

import logging


from anima.utils import do_db_setup
from anima.dcc import photoshop
from anima.ui.dialogs import version_dialog


def version_dialog(lib="PySide"):
    """Helper function for version_dialog UI for Photoshop

    It uses with PySide by default you can opt to use PyQt4 instead by setting
    the ``lib`` argument to "PyQt4".

    :param str lib: choose a lib, one of ["PySide", "PyQt4"]
    :return: None
    """
    # connect to db
    do_db_setup()

    p = photoshop.Photoshop()
    # display only warning messages

    logging.getLogger(version_dialog.__name__).setLevel(logging.WARNING)
    logging.getLogger("anima.ui").setLevel(logging.WARNING)
    logging.getLogger("anima.ui.models").setLevel(logging.WARNING)
    logging.getLogger("anima.dcc.photoshop").setLevel(logging.WARNING)
    logging.getLogger("stalker.db").setLevel(logging.WARNING)

    version_dialog.UI(environment=p)
