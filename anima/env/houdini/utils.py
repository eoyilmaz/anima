# -*- coding: utf-8 -*-
# Copyright (c) 2020, Erkan Ozgur Yilmaz
#
# This module is part of anima and is released under the MIT
# License: http://www.opensource.org/licenses/MIT
import hou


class Executor(object):
    """Executor that binds the UI element to Houdini event loop
    """

    def __init__(self):
        self.application = None
        from anima.ui.lib import QtCore
        self.event_loop = QtCore.QEventLoop()

    def exec_(self, app, dialog):
        self.application = app
        app_version = hou.applicationVersion()[0]
        if app_version <= 15:
            self.application.setStyle('CleanLooks')
        elif 15 < app_version <= 17:
            self.application.setStyle('Fusion')

        hou.ui.addEventLoopCallback(self.processEvents)
        dialog.exec_()

    def processEvents(self):
        self.event_loop.processEvents()
        self.application.sendPostedEvents(None, 0)