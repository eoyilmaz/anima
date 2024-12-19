# -*- coding: utf-8 -*-

import logging
import sys
import unittest

from anima.ui.dialogs import reference_editor

logger = logging.getLogger('anima.ui.reference_editor')


class ReferenceEditorTestCase(unittest.TestCase):

    def setUp(self):
        """set up the test environment
        """
        if not QtGui.QApplication.instance():
            logger.debug('creating a new QApplication')
            self.app = QtGui.QApplication(sys.argv)
        else:
            logger.debug('using the present QApplication: %s' % QtGui.qApp)
            # self.app = QtGui.qApp
            self.app = QtGui.QApplication.instance()

    def tearDown(self):
        """clean up the test environment
        """
        pass

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

    def test_close_button_closes_the_UI(self):
        """testing if the close button is closing the UI when clicked
        """
        dialog = reference_editor.MainDialog()
        self.show_dialog(dialog)
        #QTest.mouseClick(dialog.button_box.buttons()[0], Qt.LeftButton)
        self.assertFalse(dialog.isVisible())

    
