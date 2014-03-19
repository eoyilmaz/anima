# -*- coding: utf-8 -*-
# Copyright (c) 2012-2014, Anima Istanbul
#
# This module is part of anima-tools and is released under the BSD 2
# License: http://www.opensource.org/licenses/BSD-2-Clause

import logging

from anima.ui import IS_PYSIDE, IS_PYQT4


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


if IS_PYSIDE():
    logger.debug('importing PySide')
    from PySide import QtGui, QtCore
elif IS_PYQT4():
    logger.debug('importing PyQt4')
    import sip
    sip.setapi('QString', 2)
    sip.setapi('QVariant', 2)
    from PyQt4 import QtGui, QtCore
