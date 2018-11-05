# -*- coding: utf-8 -*-
# Copyright (c) 2012-2018, Anima Istanbul
#
# This module is part of anima-tools and is released under the BSD 2
# License: http://www.opensource.org/licenses/BSD-2-Clause


class Executor(object):
    """
    """

    def __init__(self):
        self.application = None
        # from anima.ui.lib import QtCore
        # self.event_loop = QtCore.QEventLoop()

    def exec_(self, app, dialog):
        self.application = app
        # add event loop callback to processEvents
        dialog.exec_()

    # def processEvents(self):
    #     self.event_loop.processEvents()
    #     self.application.sendPostedEvents(None, 0)


def version_creator():
    """Helper function for version_creator UI for Max
    """
    from anima.utils import do_db_setup
    do_db_setup()

    from anima import ui
    ui.SET_PYSIDE()

    from anima.ui import version_creator
    from anima.env import max as max_env

    m = max_env.Max()

    import MaxPlus
    max_window = MaxPlus.GetQMaxWindow()

    version_creator.UI(
        environment=m,
        executor=Executor(),
        parent=max_window
    )


def version_updater():
    """Helper function for version_updater UI for Max
    """
    from anima.utils import do_db_setup
    do_db_setup()

    from anima import ui
    ui.SET_PYSIDE()

    from anima.ui import version_updater
    from anima.env import max as max_env

    m = max_env.Max()

    import MaxPlus
    max_window = MaxPlus.GetQMaxWindow()

    version_updater.UI(
        environment=m,
        executor=Executor(),
        parent=max_window
    )
