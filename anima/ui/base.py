# -*- coding: utf-8 -*-
# Copyright (c) 2012-2017, Anima Istanbul
#
# This module is part of anima-tools and is released under the BSD 2
# License: http://www.opensource.org/licenses/BSD-2-Clause


import sys

from stalker import LocalSession
from anima.ui.utils import logger
from anima.ui.lib import QtCore, QtGui, QtWidgets


class AnimaDialogBase(object):
    """A simple class to hold basic common functions for dialogs
    """

    def center_window(self):
        """centers the window to the screen
        """
        desktop = QtWidgets.QApplication.desktop()
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
        from stalker.db.session import DBSession
        with DBSession.no_autoflush:
            logged_in_user = local_session.logged_in_user

        if not logged_in_user:
            from anima.ui import login_dialog
            dialog = login_dialog.MainDialog(parent=self)
            # dialog.deleteLater()
            dialog.exec_()
            result = dialog.result()

            try:
                # PySide
                accepted = QtWidgets.QDialog.DialogCode.Accepted
            except AttributeError:
                # PyQt4
                accepted = QtWidgets.QDialog.Accepted

            if result == accepted:
                local_session = LocalSession()
                logged_in_user = local_session.logged_in_user
            else:
                # close the ui
                # logged_in_user = self.get_logged_in_user()
                logger.debug("no logged in user")
                self.close()
        
        return logged_in_user


class MultiLineInputDialog(QtWidgets.QDialog):
    """A simple dialog with a QPlainTextEdit
    """
    pass


def ui_caller(app_in, executor, ui_class, **kwargs):
    global app
    global ui_instance
    self_quit = False
    app = QtWidgets.QApplication.instance()
    if app is None:
        if not app_in:
            try:
                app = QtWidgets.QApplication(sys.argv)
            except AttributeError:  # sys.argv gives argv.error
                app = QtWidgets.QApplication([])
        else:
            app = app_in
        self_quit = True

    ui_instance = ui_class(**kwargs)
    ui_instance.show()
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
        executor.exec_(app, ui_instance)
    return ui_instance
