# -*- coding: utf-8 -*-
# Stalker a Production Asset Management System
# Copyright (C) 2009-2013 Erkan Ozgur Yilmaz
# 
# This file is part of Stalker.
# 
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation;
# version 2.1 of the License.
# 
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
# 
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301 USA

import os
import tempfile
import unittest2

from anima.pipeline.ui import uiCompiler


class UIFileTestCase(unittest2.TestCase):
    """tests the UICFile class
    """

    def setUp(self):
        """set up the test
        """
        self.test_uicFile_path = tempfile.mktemp(suffix='.uic')
        # fill test data to the file
        with open(self.test_uicFile_path, 'w+') as f:
            f.write('test')
        self.test_uicFile = uiCompiler.UICFile(self.test_uicFile_path)

    def tearDown(self):
        """clear test data
        """
        os.remove(self.test_uicFile_path)

    def test_full_path_argument_is_skipped(self):
        """testing if a TypeError will be raised when the full_path argument is
        skipped
        """
        self.fail('test is not implemented yet')

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

    def test_md5_attribute_is_calculated_correctly(self):
        """testing if the md5 of the uic file is correctly calculated
        """
        from anima.pipeline import utils
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
        """testing if the isNew() method is working properly
        """
        self.assertTrue(
            self.test_uicFile.isNew()
        )

        # but not new if the md5 file is stored in the md5 file
        self.test_uicFile.update_md5_file()
        self.assertFalse(
            self.test_uicFile.isNew()
        )
