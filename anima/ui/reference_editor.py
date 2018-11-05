# -*- coding: utf-8 -*-
# Copyright (c) 2012-2018, Anima Istanbul
#
# This module is part of anima-tools and is released under the BSD 2
# License: http://www.opensource.org/licenses/BSD-2-Clause
from anima.ui import IS_PYSIDE, IS_PYSIDE2, IS_PYQT4
from anima.ui.base import ui_caller, QtWidgets


def UI(environment=None, app_in=None, executor=None):
    """
    """
    return ui_caller(app_in, executor, MainDialog, environment=environment)


if IS_PYSIDE():
    from anima.ui.ui_compiled import reference_editor_UI_pyside as reference_editor_UI
elif IS_PYSIDE2():
    from anima.ui.ui_compiled import reference_editor_UI_pyside2 as reference_editor_UI
elif IS_PYQT4():
    from anima.ui.ui_compiled import reference_editor_UI_pyqt4 as reference_editor_UI

class MainDialog(QtWidgets.QDialog, reference_editor_UI.Ui_Dialog):

    def __init__(self, environment=None, parent=None):
        super(MainDialog, self).__init__(parent)
        self.setupUi(self)

