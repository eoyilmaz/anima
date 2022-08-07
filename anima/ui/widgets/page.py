# -*- coding: utf-8 -*-

from anima.ui.lib import QtCore, QtGui, QtWidgets

if False:
    from PySide2 import QtCore, QtGui, QtWidgets


class PageTitleWidget(QtWidgets.QLabel):
    """Stylized page title widget."""

    def __init__(self, *args, **kwargs):
        super(PageTitleWidget, self).__init__(self, *args, **kwargs)
        self.setStyleSheet("color: rgb(71, 143, 202);\nfont: 18pt;")
