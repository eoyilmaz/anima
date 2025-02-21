# -*- coding: utf-8 -*-

import logging
import sys
import unittest

from anima.ui.lib import QtCore, QtGui
from anima.ui.dialogs import reference_editor

logger = logging.getLogger("anima.ui.reference_editor")


class ReferenceEditorTestCase(unittest.TestCase):
    def setUp(self):
        """Set up the test environment."""
        if not QtGui.QApplication.instance():
            logger.debug("creating a new QApplication")
            self.app = QtGui.QApplication(sys.argv)
        else:
            logger.debug("using the present QApplication: {}".format(QtGui.qApp))
            # self.app = QtGui.qApp
            self.app = QtGui.QApplication.instance()

    def tearDown(self):
        """Clean up the test environment."""
        pass

    def show_dialog(self, dialog):
        """Show the given dialog."""
        dialog.show()
        self.app.exec_()
        self.app.connect(
            self.app,
            QtCore.SIGNAL("lastWindowClosed()"),
            self.app,
            QtCore.SLOT("quit()"),
        )

    def test_close_button_closes_the_UI(self):
        """close button is closing the UI when clicked"""
        dialog = reference_editor.MainDialog()
        self.show_dialog(dialog)
        # QTest.mouseClick(dialog.button_box.buttons()[0], Qt.LeftButton)
        self.assertFalse(dialog.isVisible())
