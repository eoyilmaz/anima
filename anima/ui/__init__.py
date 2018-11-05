# -*- coding: utf-8 -*-
# Copyright (c) 2012-2018, Anima Istanbul
#
# This module is part of anima-tools and is released under the BSD 2
# License: http://www.opensource.org/licenses/BSD-2-Clause

import os
from anima import logger

# Choose between PyQt4 or PySide
PYSIDE = 'PySide'
PYSIDE2 = 'PySide2'
PYQT4 = 'PyQt4'
QTPY = 'QtPy'  # support for https://www.gihub.com/motttoso/Qt.py

# set the default
qt_lib_key = "QT_LIB"
qt_lib = PYSIDE


if qt_lib_key in os.environ:
    qt_lib = os.environ[qt_lib_key]


def IS_PYSIDE():
    return qt_lib == PYSIDE


def IS_PYSIDE2():
    return qt_lib == PYSIDE2


def IS_PYQT4():
    return qt_lib == PYQT4


def IS_QTPY():
    return qt_lib == QTPY


def SET_PYSIDE():
    logger.debug('setting environment to PySide')
    global qt_lib
    qt_lib = PYSIDE


def SET_PYSIDE2():
    logger.debug('setting environment to PySide2')
    global qt_lib
    qt_lib = PYSIDE2


def SET_PYQT4():
    logger.debug('setting environment to PyQt4')
    global qt_lib
    qt_lib = PYQT4


def SET_QT():
    logger.debug('setting environment to Qt')
    global qt_lib
    qt_lib = PYQT4
