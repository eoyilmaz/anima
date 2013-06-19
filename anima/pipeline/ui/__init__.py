# -*- coding: utf-8 -*-
# Copyright (c) 2012-2013, Anima Istanbul
#
# This module is part of anima-tools and is released under the BSD 2
# License: http://www.opensource.org/licenses/BSD-2-Clause

import os
import logging

# Choose between PyQt4 or PySide
PYSIDE = 'PySide'
PYQT4 = 'PyQt4'

# set the default
qt_lib_key = "QT_LIB"
qt_lib = PYQT4

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

if os.environ.has_key(qt_lib_key):
    qt_lib = os.environ[qt_lib_key]

def IS_PYSIDE():
    return qt_lib == PYSIDE

def IS_PYQT4():
    return qt_lib == PYQT4

def SET_PYSIDE():
    logger.debug('setting environment to PySide')
    global qt_lib
    qt_lib = PYSIDE

def SET_PYQT4():
    logger.debug('setting environment to PyQt4')
    global qt_lib
    qt_lib = PYQT4
