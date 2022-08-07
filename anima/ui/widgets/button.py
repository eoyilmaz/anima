# -*- coding: utf:8 -*-

from anima.ui.lib import QtCore, QtGui, QtWidgets

if False:
    from PySide2 import QtCore, QtGui, QtWidgets


class DashboardButton(QtWidgets.QPushButton):
    """Dashboard button class."""

    def __init__(self, *args, **kwargs):
        super(DashboardButton, self).__init__(*args, **kwargs)
