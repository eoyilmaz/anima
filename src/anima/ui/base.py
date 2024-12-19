# -*- coding: utf-8 -*-


import sys

from stalker import LocalSession
from anima.ui.utils import logger
from anima.ui.lib import QtCore, QtGui, QtWidgets


class AnimaDialogBase(object):
    """A simple class to hold basic common functions for dialogs"""

    def center_window(self):
        """centers the window to the main application window"""

        # if there is no main application then fall back to centering to the
        # screen that the mouse pointer is in
        parent = self.parent()
        if not parent:
            self.center_window_to_screen()
            return

        # get the main application size
        # center to that dimension
        parent_size = parent.geometry()
        size = self.geometry()

        left = (parent_size.width() - size.width()) * 0.5 + parent_size.left()
        top = (parent_size.height() - size.height()) * 0.5 + parent_size.top()

        left = max(0, left)
        top = max(0, top)

        self.move(left, top)

    def center_window_to_screen(self):
        """centers the window to the screen that the mouse pointer is in"""
        desktop = QtWidgets.QApplication.desktop()
        cursor_pos = QtGui.QCursor.pos()
        desktop_number = desktop.screenNumber(cursor_pos)
        desktop_rect = desktop.screenGeometry(desktop_number)

        size = self.geometry()

        self.move(
            (desktop_rect.width() - size.width()) * 0.5 + desktop_rect.left(),
            (desktop_rect.height() - size.height()) * 0.5 + desktop_rect.top(),
        )

    def get_logged_in_user(self):
        """returns the logged in user"""
        # Fix issues about this method being a part of a QLayout instead of a QDialog
        parent = None
        if isinstance(self, QtWidgets.QDialog):
            parent = self

        local_session = LocalSession()
        from stalker.db.session import DBSession

        with DBSession.no_autoflush:
            logged_in_user = local_session.logged_in_user

        if not logged_in_user:
            from anima.ui.dialogs import login_dialog

            dialog = login_dialog.MainDialog(parent=parent)
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
                if isinstance(self, QtWidgets.QDialog):
                    self.close()
                raise RuntimeError("no logged in user")

        return logged_in_user


class MultiLineInputDialog(QtWidgets.QDialog):
    """A simple dialog with a QPlainTextEdit"""

    pass


def ui_caller(app_in, executor, ui_class, **kwargs):
    global app
    global ui_instance
    self_quit = False
    app = app_in
    if not app:
        try:
            app = QtWidgets.QApplication.instance()
        except TypeError:
            app = None

        if app is None:
            try:
                app = QtWidgets.QApplication(sys.argv)
            except (TypeError, AttributeError):  # sys.argv gives argv.error or
                # Qt gives TypeError
                app = QtWidgets.QApplication([])
            self_quit = True

    ui_instance = ui_class(**kwargs)
    ui_instance.show()
    if executor is None:
        app.exec_()
        if self_quit:
            app.connect(
                app, QtCore.SIGNAL("lastWindowClosed()"), app, QtCore.SLOT("quit()")
            )
    else:
        executor.exec_(app, ui_instance)
    return ui_instance
