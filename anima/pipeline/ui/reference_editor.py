# -*- coding: utf-8 -*-
# Copyright (c) 2012-2014, Anima Istanbul
#
# This module is part of anima-tools and is released under the BSD 2
# License: http://www.opensource.org/licenses/BSD-2-Clause
from anima.pipeline.ui import IS_PYSIDE, IS_PYQT4

from anima.pipeline.ui.lib import QtCore, QtGui
from anima.pipeline.ui.utils import UICaller


def UI(environment=None, app_in=None, executor=None):
    """
    """
    return UICaller(app_in, executor, MainDialog, environment=environment)


if IS_PYSIDE():
    from anima.pipeline.ui.ui_compiled import reference_editor_UI_pyside as reference_editor_UI
elif IS_PYQT4():
    from anima.pipeline.ui.ui_compiled import reference_editor_UI_pyqt4 as reference_editor_UI


class MainDialog(QtGui.QDialog, reference_editor_UI.Ui_Dialog):

    def __init__(self, environment=None, parent=None):
        super(MainDialog, self).__init__(parent)
        self.setupUi(self)

