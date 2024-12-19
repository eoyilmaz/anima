# -*- coding: utf-8 -*-

import os
from anima import logger

# Choose the Qt library
PYSIDE = "pyside"
PYSIDE2 = "pyside2"
PYSIDE6 = "pyside6"

PYQT4 = "pyqt4"
PYQT5 = "pyqt5"
PYQT6 = "pyqt6"

QTPY = "QtPy"  # support for https://www.gihub.com/motttoso/Qt.py

# set the default
qt_api_env_var_name = "QT_API"
qt_api = PYSIDE2

ICON_CACHE = {}
FONT_CACHE = {}


if qt_api_env_var_name in os.environ:
    qt_api = os.environ.get(qt_api_env_var_name, PYSIDE6)
    # also set the qt_api key for QtPy
    os.environ["QT_API"] = qt_api.lower()


def IS_PYSIDE():
    return qt_api.lower() == PYSIDE.lower()


def IS_PYSIDE2():
    return qt_api.lower() == PYSIDE2.lower()


def IS_PYSIDE6():
    return qt_api.lower() == PYSIDE6.lower()


def IS_PYQT4():
    return qt_api.lower() == PYQT4.lower()


def IS_PYQT5():
    return qt_api.lower() == PYQT5.lower()


def IS_PYQT6():
    return qt_api.lower() == PYQT6.lower()


def IS_QTPY():
    return qt_api.lower() == QTPY.lower()

