# -*- coding: utf-8 -*-
# Copyright (c) 2012-2015, Anima Istanbul
#
# This module is part of anima-tools and is released under the BSD 2
# License: http://www.opensource.org/licenses/BSD-2-Clause
import tempfile
import os

import platform
import unittest
import shutil
from anima.env import discover_env_vars


platform_name = "Linux"


class EnvironmentVariableSetupTestCase(unittest.TestCase):
    """tests the anima.env.discover_env_variables() function
    """

    orig_platform_system = None
    patched_platform_system = None

    @classmethod
    def setUpClass(cls):
        """set up once
        """
        # patch platform.system
        cls.orig_platform_system = platform.system

        def pathched():
            global platform_name
            return platform_name

        platform.system = pathched

    @classmethod
    def tearDownClass(cls):
        """clean up once
        """
        platform.system = cls.orig_platform_system

    def setUp(self):
        """set up the test each time
        """
        # create a temp env.json file and fill data in to it
        self.anima_path = tempfile.mkdtemp()
        os.environ['ANIMAPATH'] = self.anima_path

        self.env_json_file_path = os.path.join(
            self.anima_path, 'env.json'
        )

        self.env_json_file_content = """{
    "*": {
        "windows": {
            "ENV1": ["Z:/some/path1", "Z:/some/path2"]
        },
        "linux": {
            "ENV1": ["/mnt/Z/some/path1", "/mnt/Z/some/path2"]
        },
        "osx": {
            "ENV1": ["/Volumes/Z/some/path1", "/Volumes/Z/some/path2"]
        }
    },
    "test_env": {
        "windows": {
            "ENV1": ["Z:/some/other/path1", "Z:/some/other/path2"]
        },
        "linux": {
            "ENV1": ["/mnt/Z/some/other/path1", "/mnt/Z/some/other/path2"]
        },
        "osx": {
            "ENV1": ["/Volumes/Z/some/other/path1", "/Volumes/Z/some/other/path2"]
        }
    },
    "other_env": {
        "windows": {
            "ENV1": ["Z:/this/should/not/be/appended"],
            "ENV2": ["Z:/also/these/should/not/be/appended"]
        },
        "linux": {
            "ENV1": ["/mnt/Z/this/should/not/be/appended"],
            "ENV2": ["/mnt/Z/also/these/should/not/be/appended"]
        },
        "osx": {
            "ENV1": ["/Volumes/Z/this/should/not/be/appended"],
            "ENV2": ["/Volumes/Z/also/these/should/not/be/appended"]
        }
    }
}"""
        # write the content to the file
        with open(self.env_json_file_path, 'w') as f:
            f.writelines(self.env_json_file_content)

        global platform_name
        platform_name = 'Linux'

    def tearDown(self):
        """clear tests each time
        """
        try:
            shutil.rmtree(self.anima_path)
        except OSError:
            pass

        try:
            os.environ.pop('ANIMAPATH')
        except KeyError:
            pass

    def test_anima_path_env_variable_does_not_exists(self):
        """testing if a KeyError will be raised if ANIMAPATH env variable
        does not exist
        """
        try:
            os.environ.pop("ANIMAPATH")
        except KeyError:
            pass

        self.assertRaises(KeyError, discover_env_vars)

    def test_env_json_file_does_not_exist(self):
        """testing if a IOError will be raised when the env.json file does not
        exists in the path that ANIMATPATH is pointing to
        """
        shutil.rmtree(self.anima_path)
        self.assertRaises(IOError, discover_env_vars)

    def test_env_json_will_be_searched_in_anima_path(self):
        """testing if the env.json file will be searched in the path that
        ANIMAPATH is pointing too.
        """
        self.assertFalse('ENV1' in os.environ)
        discover_env_vars()
        self.assertTrue('ENV1' in os.environ)

    def test_env_variables_defined_in_system_will_not_be_overwritten(self):
        """testing if environment variables defined in system will not be
        overwritten
        """
        os.environ['ENV1'] = '/Test/Value'
        discover_env_vars()
        self.assertEqual(
            '/Test/Value:/mnt/Z/some/path1:/mnt/Z/some/path2',
            os.environ['ENV1']
        )

    def test_env_variables_defined_with_asterix_will_defined_unrelated_to_the_env_name_argument(self):
        """testing if environment variables defined with the "*" environment
        name will be defined no matter what is given for the env_name argument
        """
        os.environ['ENV1'] = '/Test/Value'
        discover_env_vars('some_env_name')
        self.assertEqual(
            '/Test/Value:/mnt/Z/some/path1:/mnt/Z/some/path2',
            os.environ['ENV1']
        )

    def test_env_variables_will_appended_to_the_ones_defined_in_asterix(self):
        """testing if environment variables defined with other env names will
        be append to the ones defined in "*"
        """
        global platform_name
        platform_name = 'Linux'

        os.environ['ENV1'] = '/Test/Value'
        discover_env_vars('test_env')
        self.assertEqual(
            '/Test/Value:/mnt/Z/some/path1:/mnt/Z/some/path2:'
            '/mnt/Z/some/other/path1:/mnt/Z/some/other/path2',
            os.environ['ENV1']
        )

    def test_env_variables_is_working_properly_in_linux(self):
        """testing if environment variables are properly defined by using the
        os name
        """
        global platform_name
        platform_name = "Linux"
        try:
            os.environ.pop('ENV1')
        except KeyError:
            pass

        os.environ['ENV1'] = '/Test/Value'
        discover_env_vars('test_env')
        self.assertEqual(
            '/Test/Value:/mnt/Z/some/path1:/mnt/Z/some/path2:'
            '/mnt/Z/some/other/path1:/mnt/Z/some/other/path2',
            os.environ['ENV1']
        )

    def test_env_variables_is_working_properly_in_windows(self):
        """testing if environment variables are properly defined by using the
        os name
        """
        global platform_name
        platform_name = "Windows"
        try:
            os.environ.pop('ENV1')
        except KeyError:
            pass

        os.environ['ENV1'] = 'Z:/Test/Value'
        discover_env_vars('test_env')
        self.assertEqual(
            'Z:/Test/Value:Z:/some/path1:Z:/some/path2:'
            'Z:/some/other/path1:Z:/some/other/path2',
            os.environ['ENV1']
        )

    def test_env_variables_is_working_properly_in_osx(self):
        """testing if environment variables are properly defined by using the
        os name
        """
        global platform_name
        platform_name = "Darwin"

        self.assertEqual(
            "Darwin",
            platform.system()
        )
        try:
            os.environ.pop('ENV1')
        except KeyError:
            pass

        os.environ['ENV1'] = '/Volumes/Z/Test/Value'
        discover_env_vars('test_env')
        self.assertEqual(
            '/Volumes/Z/Test/Value:/Volumes/Z/some/path1:/Volumes/Z/some/path2:'
            '/Volumes/Z/some/other/path1:/Volumes/Z/some/other/path2',
            os.environ['ENV1']
        )
        '/Volumes/Z/Test/Value:/Volumes/Z/some/path1:/Volumes/Z/some/path2:/Volumes/Z/some/other/path1:/Volumes/Z/some/other/path2'
        '/Volumes/Z/Test/Value:/mnt/Z/some/path1:/mnt/Z/some/path2:/mnt/Z/some/other/path1:/mnt/Z/some/other/path2'

