# -*- coding: utf-8 -*-
# Copyright (c) 2012-2014, Anima Istanbul
#
# This module is part of anima-tools and is released under the BSD 2
# License: http://www.opensource.org/licenses/BSD-2-Clause
import os

import unittest

from stalker import db, Repository
from anima import repo_env_template
from anima.env import create_repo_vars, to_os_independent_path


class RepoVarsTestCase(unittest.TestCase):
    """tests the anima.env.create_repo_vars() function
    """

    @classmethod
    def setUpClass(cls):
        """setup once
        """
        # create a test database
        db.setup()
        db.init()

        # create test repositories
        cls.repo1 = Repository(
            name='Test Repo 1',
            linux_path='/test/repo/1/linux/path',
            windows_path='T:/test/repo/1/windows/path',
            osx_path='/test/repo/1/osx/path',
        )

        cls.repo2 = Repository(
            name='Test Repo 2',
            linux_path='/test/repo/2/linux/path',
            windows_path='T:/test/repo/2/windows/path',
            osx_path='/test/repo/2/osx/path',
        )

        cls.repo3 = Repository(
            name='Test Repo 3',
            linux_path='/test/repo/3/linux/path',
            windows_path='T:/test/repo/3/windows/path',
            osx_path='/test/repo/3/osx/path',
        )

        cls.repo4 = Repository(
            name='Test Repo 4',
            linux_path='/test/repo/4/linux/path',
            windows_path='T:/test/repo/4/windows/path',
            osx_path='/test/repo/4/osx/path',
        )

        cls.repo5 = Repository(
            name='Test Repo 5',
            linux_path='/test/repo/5/linux/path',
            windows_path='T:/test/repo/5/windows/path',
            osx_path='/test/repo/5/osx/path',
        )

        cls.all_repos = [cls.repo1, cls.repo2, cls.repo3, cls.repo4, cls.repo5]

        db.DBSession.add_all(cls.all_repos)
        db.DBSession.commit()

    def test_all_environ_vars_are_created(self):
        """testing if all environment vars for all the repositories are created
        upon call to create_repo_vars function
        """
        for repo in self.all_repos:
            self.assertFalse(repo_env_template % {'id': repo.id} in os.environ)

        create_repo_vars()

        for repo in self.all_repos:
            self.assertTrue(repo_env_template % {'id': repo.id} in os.environ)

    def test_environment_var_values_are_correct(self):
        """testing if all environment var values are correct
        """
        create_repo_vars()
        for repo in self.all_repos:
            self.assertEqual(
                os.environ[repo_env_template % {'id': repo.id}],
                repo.path
            )

    def test_to_os_independent_path_is_working_properly(self):
        """testing if anima.env.to_os_independent_path() is working properly
        """
        # repo4
        linux_path = '/test/repo/4/linux/path/PRJ1/Assets/test.ma'
        windows_path = 'T:/test/repo/4/windows/path/PRJ1/Assets/test.ma'
        osx_path = '/test/repo/4/osx/path/PRJ1/Assets/test.ma'

        os_independent_path = '$REPO%s/PRJ1/Assets/test.ma' % self.repo4.id

        self.assertEqual(
            to_os_independent_path(linux_path),
            os_independent_path
        )

        self.assertEqual(
            to_os_independent_path(windows_path),
            os_independent_path
        )

        self.assertEqual(
            to_os_independent_path(osx_path),
            os_independent_path
        )

        # repo5
        linux_path = '/test/repo/5/linux/path/PRJ1/Assets/test.ma'
        windows_path = 'T:/test/repo/5/windows/path/PRJ1/Assets/test.ma'
        osx_path = '/test/repo/5/osx/path/PRJ1/Assets/test.ma'

        os_independent_path = '$REPO%s/PRJ1/Assets/test.ma' % self.repo5.id

        self.assertEqual(
            to_os_independent_path(linux_path),
            os_independent_path
        )

        self.assertEqual(
            to_os_independent_path(windows_path),
            os_independent_path
        )

        self.assertEqual(
            to_os_independent_path(osx_path),
            os_independent_path
        )

