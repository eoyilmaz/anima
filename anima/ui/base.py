# -*- coding: utf-8 -*-
# Copyright (c) 2012-2015, Anima Istanbul
#
# This module is part of anima-tools and is released under the BSD 2
# License: http://www.opensource.org/licenses/BSD-2-Clause


import sys

from stalker import LocalSession
from anima.ui.utils import logger
from anima.ui.lib import QtCore, QtGui


class AnimaDialogBase(object):
    """A simple class to hold basic common functions for dialogs
    """

    def center_window(self):
        """centers the window to the screen
        """
        desktop = QtGui.QApplication.desktop()
        cursor_pos = QtGui.QCursor.pos()
        desktop_number = desktop.screenNumber(cursor_pos)
        desktop_rect = desktop.screenGeometry(desktop_number)

        size = self.geometry()

        self.move(
            (desktop_rect.width() - size.width()) * 0.5 + desktop_rect.left(),
            (desktop_rect.height() - size.height()) * 0.5 + desktop_rect.top()
        )

    def get_logged_in_user(self):
        """returns the logged in user
        """
        local_session = LocalSession()
        logged_in_user = local_session.logged_in_user
        if not logged_in_user:
            from anima.ui import login_dialog
            dialog = login_dialog.MainDialog(parent=self)
            dialog.exec_()
            logger.debug("dialog.DialogCode: %s" % dialog.DialogCode)

            try:
                # PySide
                accepted = QtGui.QDialog.DialogCode.Accepted
            except AttributeError:
                # PyQt4
                accepted = QtGui.QDialog.Accepted

            if dialog.DialogCode == accepted:
                local_session = LocalSession()
                logged_in_user = local_session.logged_in_user
            else:
                # close the ui
                # logged_in_user = self.get_logged_in_user()
                logger.debug("no logged in user")
                self.close()

        return logged_in_user


class MultiLineInputDialog(QtGui.QDialog):
    """A simple dialog with a QPlainTextEdit
    """
    pass


def ui_caller(app_in, executor, DialogClass, **kwargs):
    global app
    global mainDialog
    self_quit = False
    if QtGui.QApplication.instance() is None:
        if not app_in:
            try:
                app = QtGui.QApplication(sys.argv)
            except AttributeError:  # sys.argv gives argv.error
                app = QtGui.QApplication([])
        else:
            app = app_in
        self_quit = True
    else:
        app = QtGui.QApplication.instance()

    mainDialog = DialogClass(**kwargs)
    mainDialog.show()
    if executor is None:
        app.exec_()
        if self_quit:
            app.connect(
                app,
                QtCore.SIGNAL("lastWindowClosed()"),
                app,
                QtCore.SLOT("quit()")
            )
    else:
        executor.exec_(app, mainDialog)
    return mainDialog
