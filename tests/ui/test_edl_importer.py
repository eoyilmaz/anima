# -*- coding: utf-8 -*-

import shutil
import sys
import logging
import tempfile
import unittest
import os
import anima

from anima.ui import IS_PYSIDE, IS_PYQT4, SET_PYSIDE
from anima.ui.testing import PatchedMessageBox


SET_PYSIDE()

if IS_PYSIDE():
    from PySide import QtCore, QtGui
    from PySide.QtTest import QTest
    from PySide.QtCore import Qt
elif IS_PYQT4():
    import sip
    sip.setapi('QString', 2)
    sip.setapi('QVariant', 2)
    from PyQt4 import QtCore, QtGui
    from PyQt4.QtTest import QTest
    from PyQt4.QtCore import Qt

from anima.ui.dialogs import edl_importer

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
        # patch anima.defaults.local_cache_folder
        from anima import defaults
        self.original_cache_folder = defaults.local_cache_folder
        defaults.local_cache_folder = tempfile.gettempdir()

        if not QtGui.QApplication.instance():
            logger.debug('creating a new QApplication')
            self.app = QtGui.QApplication(sys.argv)
        else:
            logger.debug('using the present QApplication: %s' % QtGui.qApp)
            # self.app = QtGui.qApp
            self.app = QtGui.QApplication.instance()

        self.dialog = edl_importer.MainDialog()

        self.remove_files = []

    def tearDown(self):
        """clean up test
        """
        PatchedMessageBox.tear_down()

        # restore anima.defaults.local_cache_folder
        from anima import defaults
        defaults.local_cache_folder = self.original_cache_folder

        # remove self.remove_files
        for f in self.remove_files:
            if os.path.isfile(f):
                os.remove(f)
            elif os.path.isdir(f):
                shutil.rmtree(f)

    def test_edl_path_lineEdit_change_will_update_edl_preview_textEdit(self):
        """testing if changing edl_path_lineEdit will update the
        edl_preview_textEdit with the given file content
        """
        # create an edl file content
        # and then write it to a temp file
        # set the temp file path to path_lineEdit
        # expect the content to be in edl_preview_textEdit
        edl_path = os.path.abspath('../previs/test_data/test_v001.edl')
        self.dialog.edl_path_lineEdit.setText(edl_path)

        with open(edl_path) as f:
            edl_content = f.read()

        self.assertEqual(
            self.dialog.edl_preview_plainTextEdit.toPlainText(),
            edl_content
        )

    def test_edl_path_lineEdit_will_clear_edl_preview_textEdit_if_path_invalid(self):
        """testing if changing edl_path_lineEdit will clear the
        edl_preview_textEdit if edl_path_lineEdit is invalid
        """
        self.dialog.edl_preview_plainTextEdit.setPlainText('Some text')

        self.assertEqual(
            self.dialog.edl_preview_plainTextEdit.toPlainText(),
            'Some text'
        )

        self.dialog.edl_path_lineEdit.setText('Some text')

        self.assertEqual(
            self.dialog.edl_preview_plainTextEdit.toPlainText(),
            ''
        )

    def test_send_pushButton_will_warn_the_user_to_set_the_media_files_path_if_it_is_not_set_before(self):
        """testing if send_pushButton will warn the user to set the media files
        path in preferences if it is not set before
        """
        # set a proper EDL file
        edl_path = os.path.abspath('../previs/test_data/test_v001.edl')
        self.dialog.edl_path_lineEdit.setText(edl_path)

        # patch QMessageBox.critical method
        original = QtGui.QMessageBox.critical
        QtGui.QMessageBox = PatchedMessageBox

        self.assertEqual(PatchedMessageBox.called_function, '')
        self.assertEqual(PatchedMessageBox.title, '')
        self.assertEqual(PatchedMessageBox.message, '')

        # now hit it
        QTest.mouseClick(self.dialog.send_pushButton, Qt.LeftButton)

        # restore QMessageBox.critical
        QtGui.QMessageBox.critical = original

        self.assertEqual(PatchedMessageBox.called_function, 'critical')
        self.assertEqual(PatchedMessageBox.title, 'Error')

        self.assertEqual(
            "Media path doesn't exists",
            PatchedMessageBox.message
        )

    def test_send_pushButton_will_copy_mxf_files_to_media_files_folder(self):
        """testing if send_pushButton will copy the mxf files to media files
        folder
        """
        # create a proper edl file with proper files in a temp location
        # there should be MXF files
        tempdir = tempfile.gettempdir()

        media_files_path = os.path.join(tempdir, 'avid_media_file_path')
        try:
            os.mkdir(media_files_path)
        except OSError:
            pass
        self.remove_files.append(media_files_path)

        mxf_file_names = [
            'SEQ001_HSNI_003_0010_v001.mxf',
            'SEQ001_HSNI_003_0020_v001.mxf',
            'SEQ001_HSNI_003_0030_v001.mxf'
        ]

        edl_path = os.path.abspath('../previs/test_data/test_v001.edl')

        for mxf_file_name in mxf_file_names:
            media_file_full_path = os.path.join(tempdir, mxf_file_name)
            with open(media_file_full_path, 'w') as f:
                f.write('')
            self.remove_files.append(media_file_full_path)

        # set the avid media files folder path
        self.dialog.media_files_path_lineEdit.setText(media_files_path)

        # set the edl path
        self.dialog.edl_path_lineEdit.setText(edl_path)

        # now check before the files are not there
        self.assertFalse(
            os.path.exists(os.path.join(media_files_path, mxf_file_names[0]))
        )
        self.assertFalse(
            os.path.exists(os.path.join(media_files_path, mxf_file_names[1]))
        )
        self.assertFalse(
            os.path.exists(os.path.join(media_files_path, mxf_file_names[2]))
        )

        # self.show_dialog(self.dialog)

        # now hit it
        QTest.mouseClick(self.dialog.send_pushButton, Qt.LeftButton)

        # now check if the files are there
        self.assertTrue(
            os.path.exists(os.path.join(media_files_path, mxf_file_names[0]))
        )
        self.assertTrue(
            os.path.exists(os.path.join(media_files_path, mxf_file_names[1]))
        )
        self.assertTrue(
            os.path.exists(os.path.join(media_files_path, mxf_file_names[2]))
        )

    # def test_send_pushButton_will_show_progress_dialog(self):
    #     """testing if send_pushButton will show progress dialog
    #     """
    #     # create a proper edl file with proper files in a temp location
    #     # there should be MXF files
    #     tempdir = tempfile.gettempdir()
    # 
    #     media_files_path = os.path.join(tempdir, 'avid_media_file_path')
    #     try:
    #         os.mkdir(media_files_path)
    #     except OSError:
    #         pass
    #     self.remove_files.append(media_files_path)
    # 
    #     mxf_file_names = [
    #         'SEQ001_HSNI_003_0010_v001.mxf',
    #         'SEQ001_HSNI_003_0020_v001.mxf',
    #         'SEQ001_HSNI_003_0030_v001.mxf'
    #     ]
    # 
    #     edl_path = os.path.abspath('../previs/test_data/test_v001.edl')
    # 
    #     for mxf_file_name in mxf_file_names:
    #         media_file_full_path = os.path.join(tempdir, mxf_file_name)
    #         with open(media_file_full_path, 'w') as f:
    #             f.write('')
    #         self.remove_files.append(media_file_full_path)
    # 
    #     # set the avid media files folder path
    #     self.dialog.media_files_path_lineEdit.setText(media_files_path)
    # 
    #     # set the edl path
    #     self.dialog.edl_path_lineEdit.setText(edl_path)
    # 
    #     # now check before the files are not there
    #     self.assertFalse(
    #         os.path.exists(os.path.join(media_files_path, mxf_file_names[0]))
    #     )
    #     self.assertFalse(
    #         os.path.exists(os.path.join(media_files_path, mxf_file_names[1]))
    #     )
    #     self.assertFalse(
    #         os.path.exists(os.path.join(media_files_path, mxf_file_names[2]))
    #     )
    # 
    #     # now hit it
    #     QTest.mouseClick(self.dialog.send_pushButton, Qt.LeftButton)
    # 
    #     # now check if the files are there
    #     self.assertTrue(
    #         os.path.exists(os.path.join(media_files_path, mxf_file_names[0]))
    #     )
    #     self.assertTrue(
    #         os.path.exists(os.path.join(media_files_path, mxf_file_names[1]))
    #     )
    #     self.assertTrue(
    #         os.path.exists(os.path.join(media_files_path, mxf_file_names[2]))
    #     )

    def test_send_pushButton_will_open_the_edl_with_avid_edl_manager(self):
        """testing if the send_pushButton will open the edl with AVID EDL
        Manager
        """
        # Test Setup Idea
        #
        # create a EDL_manager file in /tmp
        # let it be a Python executable
        # make it set a file content
        self.fail('we can not test this one, it is a windows only executable')

    def test_media_files_path_lineEdit_content_will_be_stored(self):
        """testing if the media_files_path_lineEdit content will be stored in
        local_cache_folder/avid_media_file_path_storage file
        """
        # patch anima.defaults.local_cache_folder
        from anima import defaults
        original_value = defaults.local_cache_folder
        anima.local_cache_folder = tempfile.gettempdir()

        media_file_path_storage_full_path = os.path.join(
            defaults.local_cache_folder,
            defaults.avid_media_file_path_storage
        )
        self.remove_files.append(media_file_path_storage_full_path)

        test_value = 'some path'
        self.dialog.media_files_path_lineEdit.setText(test_value)

        # restore anima.defaults.local_cache_folder before asserting
        defaults.local_cache_folder = original_value

        self.assertTrue(os.path.exists(media_file_path_storage_full_path))

        with open(media_file_path_storage_full_path) as f:
            content = f.read()

        self.assertEqual(content, test_value)

    def test_media_files_path_lineEdit_content_will_be_restored(self):
        """testing if the media_files_path_lineEdit content will be stored in
        local_cache_folder/avid_media_file_path_storage file
        """
        from anima import defaults
        media_file_path_storage_full_path = os.path.join(
            defaults.local_cache_folder,
            defaults.avid_media_file_path_storage
        )
        self.remove_files.append(media_file_path_storage_full_path)

        test_value = 'some path'
        self.dialog.media_files_path_lineEdit.setText(test_value)

        # close the dialog and re open another instance
        self.dialog.close()

        self.dialog = edl_importer.MainDialog()

        # get the lineEdit value
        test_value2 = self.dialog.media_files_path_lineEdit.text()

        self.assertEqual(test_value2, test_value)
