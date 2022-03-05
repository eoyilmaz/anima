# -*- coding: utf-8 -*-


from anima import logger
from anima.ui import IS_PYSIDE, IS_PYSIDE2, IS_PYQT4, IS_QTPY

if IS_PYQT4():
    logger.debug("importing PyQt4")
    import sip

    sip.setapi("QString", 2)
    sip.setapi("QVariant", 2)
    from PyQt4 import QtGui, QtCore

    QtWidgets = QtGui
elif IS_PYSIDE():
    logger.debug("importing PySide")
    from PySide import QtGui, QtCore

    QtWidgets = QtGui
elif IS_PYSIDE2():
    logger.debug("importing PySide2")
    from PySide2 import QtGui, QtCore, QtWidgets
elif IS_QTPY():
    logger.debug("importing Qt.py")
    from Qt import QtGui, QtCore, QtWidgets
