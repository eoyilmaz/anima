# -*- coding: utf-8 -*-
# Copyright (c) 2012-2014, Anima Istanbul
#
# This module is part of anima-tools and is released under the BSD 2
# License: http://www.opensource.org/licenses/BSD-2-Clause
from anima.ui import IS_PYSIDE, IS_PYQT4
from anima.ui.base import ui_caller


def UI(environment=None, app_in=None, executor=None):
    """
    """
    return ui_caller(app_in, executor, MainDialog, environment=environment)


if IS_PYSIDE(): \
elif IS_PYQT4():


class MainDialog(QtGui.QDialog, reference_editor_UI.Ui_Dialog):

    def __init__(self, environment=None, parent=None):
        super(MainDialog, self).__init__(parent)
        self.setupUi(self)

