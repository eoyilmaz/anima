# -*- coding: utf-8 -*-

import os
from anima import logger

# Choose the Qt library
PYSIDE = "PySide"
PYSIDE2 = "PySide2"
PYSIDE6 = "PySide6"

PYQT4 = "PyQt4"
PYQT5 = "PyQt5"
PYQT6 = "PyQt6"

QTPY = "QtPy"  # support for https://www.gihub.com/motttoso/Qt.py

# set the default
qt_lib_key = "QT_LIB"
qt_lib = PYSIDE2

ICON_CACHE = {}
FONT_CACHE = {}


if qt_lib_key in os.environ:
    qt_lib = os.environ[qt_lib_key]
    # also set the qt_api key for QtPy
    os.environ["QT_API"] = qt_lib.lower()


def IS_PYSIDE():
    return qt_lib == PYSIDE


def IS_PYSIDE2():
    return qt_lib == PYSIDE2


def IS_PYSIDE6():
    return qt_lib == PYSIDE6


def IS_PYQT4():
    return qt_lib == PYQT4


def IS_PYQT5():
    return qt_lib == PYQT5


def IS_PYQT6():
    return qt_lib == PYQT6


def IS_QTPY():
    return qt_lib == QTPY


def SET_PYSIDE():
    logger.debug("setting environment to PySide")
    global qt_lib
    qt_lib = PYSIDE


def SET_PYSIDE2():
    logger.debug("setting environment to PySide2")
    global qt_lib
    qt_lib = PYSIDE2
    # also set the qt_api key for QtPy
    os.environ["QT_API"] = qt_lib.lower()


def SET_PYSIDE6():
    logger.debug("setting environment to PySide6")
    global qt_lib
    qt_lib = PYSIDE6
    # also set the qt_api key for QtPy
    os.environ["QT_API"] = qt_lib.lower()


def SET_PYQT4():
    logger.debug("setting environment to PyQt4")
    global qt_lib
    qt_lib = PYQT4


def SET_PYQT5():
    logger.debug("setting environment to PyQt5")
    global qt_lib
    qt_lib = PYQT5
    # also set the qt_api key for QtPy
    os.environ["QT_API"] = qt_lib.lower()


def SET_PYQT6():
    logger.debug("setting environment to PyQt6")
    global qt_lib
    qt_lib = PYQT6
    # also set the qt_api key for QtPy
    os.environ["QT_API"] = qt_lib.lower()


def SET_QT():
    logger.debug("setting environment to Qt")
    global qt_lib
    qt_lib = QTPY
