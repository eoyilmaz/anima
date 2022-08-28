# -*- coding: utf-8 -*-

from anima.ui.lib import QtCore, QtGui, QtWidgets

if False:
    from PySide2 import QtCore, QtGui, QtWidgets


class DarkStyle(QtWidgets.QProxyStyle):
    """Custom Proxy Style."""

    def __init__(self, *args, **kwargs):
        super(DarkStyle, self).__init__(*args, **kwargs)

    def standardPalette(self):
        palette = super(DarkStyle, self).standardPalette()
        print("DarkStyle.standardPalette is working 1")
        # palette = QtGui.QPalette()
        # Now use a palette to switch to dark colors:
        palette.setColor(QtGui.QPalette.Window, QtGui.QColor(53, 53, 53))
        palette.setColor(QtGui.QPalette.WindowText, QtCore.Qt.white)
        palette.setColor(QtGui.QPalette.Base, QtGui.QColor(25, 25, 25))
        palette.setColor(QtGui.QPalette.AlternateBase, QtGui.QColor(53, 53, 53))
        palette.setColor(QtGui.QPalette.ToolTipBase, QtCore.Qt.white)
        palette.setColor(QtGui.QPalette.ToolTipText, QtCore.Qt.white)
        palette.setColor(QtGui.QPalette.Text, QtCore.Qt.white)
        palette.setColor(
            QtGui.QPalette.Disabled,
            QtGui.QPalette.Text,
            QtGui.QColor(QtCore.Qt.darkGray),
        )
        palette.setColor(QtGui.QPalette.Button, QtGui.QColor(53, 53, 53))
        palette.setColor(QtGui.QPalette.ButtonText, QtCore.Qt.white)
        palette.setColor(
            QtGui.QPalette.Disabled,
            QtGui.QPalette.ButtonText,
            QtGui.QColor(QtCore.Qt.darkGray),
        )
        palette.setColor(QtGui.QPalette.BrightText, QtCore.Qt.red)
        palette.setColor(
            QtGui.QPalette.Disabled,
            QtGui.QPalette.BrightText,
            QtGui.QColor(255, 128, 128),
        )
        palette.setColor(QtGui.QPalette.Link, QtGui.QColor(42, 130, 218))
        palette.setColor(QtGui.QPalette.Highlight, QtGui.QColor(42, 130, 218))
        palette.setColor(QtGui.QPalette.HighlightedText, QtCore.Qt.black)

        return palette
