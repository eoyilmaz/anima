# -*- coding: utf-8 -*-
# Copyright (c) 2012-2015, Anima Istanbul
#
# This module is part of anima-tools and is released under the BSD 2
# License: http://www.opensource.org/licenses/BSD-2-Clause

import tempfile
import os

import unittest

import anima
from anima.recent import RecentFileManager


class RecentFileManagerTestCase(unittest.TestCase):
    """tests the RecentFileManager class
    """

    def setUp(self):
        """setup the tests
        """
        anima.local_cache_folder = tempfile.gettempdir()

    def tearDown(self):
        """clean up test
        """
        os.remove(
            RecentFileManager.cache_file_full_path()
        )

    def test_add_method_is_working_properly(self):
        """testing if the add method will add a new file entry to the recent
        files list
        """
        rfm = RecentFileManager()
        test_values = [
            ('Photoshop', 'some path'),
            ('Maya', 'some other path'),
            ('Maya', 'some new other path'),
            ('Photoshop', 'some path 2')
        ]

        for test_value in test_values:
            env_name = test_value[0]
            path = test_value[1]
            rfm.add(env_name, path)

            self.assertEqual(
                rfm.recent_files[env_name][0],
                path
            )

    def test_add_method_with_a_new_environment_name(self):
        """testing if the add method is able to add files to a new environment
        """
        rfm = RecentFileManager()
        rfm.add('New Env', 'some path')
        self.assertEqual(
            rfm.recent_files['New Env'][0],
            'some path'
        )

    def test_add_method_also_calls_save(self):
        """testing if the add method also calls save method
        """
        rfm1 = RecentFileManager()
        rfm1.add('New Env', 'some path')
        rfm2 = RecentFileManager()
        self.assertEqual(
            rfm2['New Env'],
            ['some path']
        )

    def test_add_method_pops_previous_versions_and_inserts_them_to_0(self):
        """testing if an entry will be popped from the recent_files list if it
        is added to the list again
        """
        rfm1 = RecentFileManager()
        rfm1.add('Env1', 'path1')
        rfm1.add('Env1', 'path2')
        rfm1.add('Env1', 'path3')

        self.assertEqual(
            rfm1['Env1'],
            ['path3', 'path2', 'path1']
        )

        rfm1.add('Env1', 'path1')
        self.assertEqual(
            rfm1['Env1'],
            ['path1', 'path3', 'path2']
        )

    def test_recent_files_attribute_is_working_properly(self):
        """testing if the recent_files attribute is working properly
        """
        rfm1 = RecentFileManager()
        rfm1.add('New Env', 'some path')
        self.assertEqual(
            rfm1.recent_files,
            {'New Env': ['some path']}
        )

    def test_restore_limits_maximum_files_stored(self):
        """testing if restore limits the maximum files stored
        """
        rm = RecentFileManager()
        for i in range(anima.max_recent_files + 100):
            rm.add('Env1', 'some path %s' % i)

        rm2 = RecentFileManager()
        self.assertEqual(
            len(rm2['Env1']),
            anima.max_recent_files
        )

    def test_restore_is_working_properly(self):
        """testing if the restore method is working properly
        """
        rfm1 = RecentFileManager()
        rfm1.add('New Env', 'some path')
        rfm1.save()

        rfm2 = RecentFileManager()
        # clear the recent files
        rfm2.recent_files = []
        rfm2.restore()

        self.assertEqual(
            rfm2.recent_files['New Env'][0],
            'some path'
        )

    def test_RecentFileManager_is_indexable(self):
        """testing if the RecentFileManager instance is indexable with the
        environment name
        """
        rfm1 = RecentFileManager()
        rfm1.add('Env1', 'Path1')
        rfm1.add('Env1', 'Path2')
        rfm1.add('Env1', 'Path3')

        rfm1.add('Env2', 'Path4')
        rfm1.add('Env2', 'Path5')
        rfm1.add('Env2', 'Path6')

        self.assertEqual(
            rfm1['Env1'],
            ['Path3', 'Path2', 'Path1']
        )
        self.assertEqual(
            rfm1['Env2'],
            ['Path6', 'Path5', 'Path4']
        )

    def test_remove_method_removes_files_from_given_env(self):
        """testing if the given path will be removed from the given environment
        """
        rfm1 = RecentFileManager()
        rfm1.add('Env1', 'Path1')
        rfm1.add('Env1', 'Path2')
        rfm1.add('Env1', 'Path3')

        rfm1.add('Env2', 'Path4')
        rfm1.add('Env2', 'Path5')
        rfm1.add('Env2', 'Path6')

        self.assertEqual(
            rfm1['Env1'],
            ['Path3', 'Path2', 'Path1']
        )
        self.assertEqual(
            rfm1['Env2'],
            ['Path6', 'Path5', 'Path4']
        )

        rfm1.remove('Env1', 'Path1')
        self.assertEqual(
            rfm1['Env1'],
            ['Path3', 'Path2']
        )

        rfm1.remove('Env1', 'Path3')
        self.assertEqual(
            rfm1['Env1'],
            ['Path2']
        )

        rfm1.remove('Env2', 'Path5')
        self.assertEqual(
            rfm1['Env2'],
            ['Path6', 'Path4']
        )
