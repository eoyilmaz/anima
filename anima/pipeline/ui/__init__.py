# -*- coding: utf-8 -*-
# Copyright (c) 2012-2013, Anima Istanbul
#
# This module is part of anima-tools and is released under the BSD 2
# License: http://www.opensource.org/licenses/BSD-2-Clause

import sys
import os

# Choose between PyQt4 or PySide
PYSIDE = 'PySide'
PYQT4 = 'PyQt4'

# set the default
qt_lib_key = "QT_LIB"
qt_lib = PYQT4

if os.environ.has_key(qt_lib_key):
    qt_lib = os.environ[qt_lib_key]


def is_pyside():
    return qt_lib == PYSIDE


def is_pyqt4():
    return qt_lib == PYQT4


if is_pyside():
    from PySide import QtGui, QtCore
elif is_pyqt4():
    import sip

    sip.setapi('QString', 2)
    sip.setapi('QVariant', 2)
    from PyQt4 import QtGui, QtCore


def UICaller(app_in, executor, DialogClass, **kwargs):
    global app
    global mainDialog
    self_quit = False
    if QtGui.QApplication.instance() is None:
        if not app_in:
            try:
                app = QtGui.QApplication(sys.argv)
            except AttributeError: # sys.argv gives argv.error
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


class AnimaDialogBase(object):
    """A simple class to hold basic common functions for dialogs
    """

    def _center_window(self):
        """centers the window to the screen
        """
        screen = QtGui.QDesktopWidget().screenGeometry()
        size = self.geometry()
        self.move(
            (screen.width() - size.width()) * 0.5,
            (screen.height() - size.height()) * 0.5
        )
