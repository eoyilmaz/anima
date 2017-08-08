# -*- coding: utf-8 -*-
# Copyright (c) 2012-2015, Anima Istanbul
#
# This module is part of anima-tools and is released under the BSD 2
# License: http://www.opensource.org/licenses/BSD-2-Clause

import os
import tempfile

import unittest

from anima import utils

from anima.ui import uiCompiler


class UIFileTestCase(unittest.TestCase):
    """tests the UIFile class
    """

    def setUp(self):
        """set up the test
        """
        self.test_uicFile_path = tempfile.mktemp(suffix='.uic')
        # fill test data to the file
        with open(self.test_uicFile_path, 'w+') as f:
            f.write('test')
        self.test_uicFile = uiCompiler.UIFile(self.test_uicFile_path)

    def tearDown(self):
        """clear test data
        """
        os.remove(self.test_uicFile_path)

    def test_full_path_argument_is_skipped(self):
        """testing if a TypeError will be raised when the full_path argument is
        skipped
        """
        self.assertRaises(TypeError, uiCompiler.UIFile)

    def test_filename_attribute_initialized_correctly(self):
        """testing if the filename attribute is initialized correctly
        """
        expected_value = os.path.basename(self.test_uicFile_path[:-4]) + '.uic'
        self.assertEqual(expected_value, self.test_uicFile.filename)

    def test_path_attribute_initialized_correctly(self):
        """testing if the path attribute is initialized correctly
        """
        expected_value = '/'.join(self.test_uicFile_path.split('/')[:-1])
        self.assertEqual(expected_value, self.test_uicFile.path)

    def test_md5_filename_attribute_initialized_correctly(self):
        """testing if the md5_filename is initialized correctly
        """
        expected_value = os.path.basename(self.test_uicFile_path)[:-4] + '.md5'
        self.assertEqual(expected_value, self.test_uicFile.md5_filename)

    def test_md5_file_full_path_attribute_initialized_correctly(self):
        """testing if the md5 file is initialized correctly
        """
        expected_value = os.path.join(
            self.test_uicFile.path,
            os.path.basename(self.test_uicFile_path)[:-4] + '.md5'
        )
        self.assertEqual(expected_value, self.test_uicFile.md5_file_full_path)

    def test_pyqt4_filename_attribute_initialized_correctly(self):
        """testing if the pyqt4_filename attribute is initialized correctly
        """
        expected_value = "%s_UI_pyqt4.py" % \
            os.path.basename(self.test_uicFile_path)[:-4]
        self.assertEqual(expected_value, self.test_uicFile.pyqt4_filename)

    def test_pyqt4_full_path_attribute_initialized_correctly(self):
        """testing if the pyqt4_full_path attribute is initialized correctly
        """
        expected_value = os.path.normpath(os.path.join(
            self.test_uicFile.path, '../ui_compiled',
            os.path.basename(self.test_uicFile_path)[:-4] + '_UI_pyqt4.py'))
        self.assertEqual(expected_value, self.test_uicFile.pyqt4_full_path)

    def test_pyside_filename_attribute_initialized_correctly(self):
        """testing if the pyside_filename attribute is initialized correctly
        """
        expected_value = '%s_UI_pyside.py' % \
                         os.path.basename(self.test_uicFile_path)[:-4]
        self.assertEqual(expected_value, self.test_uicFile.pyside_filename)

    def test_pyside_full_path_attribute_initialized_correctly(self):
        """testing if the pyside_full_path attribute is initialized correctly
        """
        expected_value = os.path.normpath(
            os.path.join(self.test_uicFile.path, '../ui_compiled',
            os.path.basename(self.test_uicFile_path)[:-4] + '_UI_pyside.py')
        )
        self.assertEqual(expected_value, self.test_uicFile.pyside_full_path)

    def test_md5_attribute_is_calculated_correctly(self):
        """testing if the md5 of the uic file is correctly calculated
        """
        expected_value = utils.md5_checksum(self.test_uicFile_path)
        self.assertEqual(expected_value, self.test_uicFile.md5)

    def test_update_md5_correctly_saves_the_md5_checksum_to_file(self):
        """testing if the update_md5() correctly saves the md5 data in to the
        md5 file
        """
        self.test_uicFile.update_md5_file()
        # now read the md5 file and check if it has the md5 checksum
        with open(self.test_uicFile.md5_file_full_path) as f:
            md5 = f.read()
        self.assertEqual(md5, self.test_uicFile.md5)
        # remove the md5 file
        os.remove(self.test_uicFile.md5_file_full_path)

    def test_isNew_method_is_working_correctly(self):
        """testing if the is_new() method is working properly
        """
        self.assertTrue(
            self.test_uicFile.is_new()
        )

        # but not new if the md5 file is stored in the md5 file
        self.test_uicFile.update_md5_file()
        self.assertFalse(
            self.test_uicFile.is_new()
        )
