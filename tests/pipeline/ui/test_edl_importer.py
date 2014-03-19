# -*- coding: utf-8 -*-
# Copyright (c) 2012-2014, Anima Istanbul
#
# This module is part of anima-tools and is released under the BSD 2
# License: http://www.opensource.org/licenses/BSD-2-Clause
import sys
import logging
import unittest

from anima.ui import IS_PYSIDE, IS_PYQT4, SET_PYSIDE


SET_PYSIDE()

if IS_PYSIDE():
    from PySide import QtCore, QtGui
elif IS_PYQT4():
    import sip
    sip.setapi('QString', 2)
    sip.setapi('QVariant', 2)
    from PyQt4 import QtCore, QtGui

from anima.ui import edl_importer

logger = logging.getLogger('anima.ui.version_updater')
logger.setLevel(logging.DEBUG)


class EDLImporterTestCase(unittest.TestCase):
    """Tests the EDLImporter UI
    """

    def show_dialog(self, dialog):
        """show the given dialog
        """
        dialog.show()
        self.app.exec_()
        self.app.connect(
            self.app,
            QtCore.SIGNAL("lastWindowClosed()"),
            self.app,
            QtCore.SLOT("quit()")
        )

    def setUp(self):
        """setup the tests
        """

        if not QtGui.QApplication.instance():
            logger.debug('creating a new QApplication')
            self.app = QtGui.QApplication(sys.argv)
        else:
            logger.debug('using the present QApplication: %s' % QtGui.qApp)
            # self.app = QtGui.qApp
            self.app = QtGui.QApplication.instance()

        self.dialog = edl_importer.MainWindow()

    
