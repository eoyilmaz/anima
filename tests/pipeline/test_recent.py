# -*- coding: utf-8 -*-
# Copyright (c) 2012-2013, Anima Istanbul
#
# This module is part of anima-tools and is released under the BSD 2
# License: http://www.opensource.org/licenses/BSD-2-Clause

import tempfile
import os

import unittest2
from anima.pipeline.recent import RecentFileManager
from anima import pipeline


class RecentFileManagerTestCase(unittest2.TestCase):
    """tests the RecentFileManager class
    """

    def setUp(self):
        """setup the tests
        """
        pipeline.local_cache_folder = tempfile.gettempdir()

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

    def test_recent_files_attribute_is_working_properly(self):
        """testing if the recent_files attribute is working properly
        """
        rfm1 = RecentFileManager()
        rfm1.add('New Env', 'some path')
        self.assertEqual(
            rfm1.recent_files,
            {'New Env': ['some path']}
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
