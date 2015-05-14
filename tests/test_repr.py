# -*- coding: utf-8 -*-
# Copyright (c) 2012-2015, Anima Istanbul
#
# This module is part of anima-tools and is released under the BSD 2
# License: http://www.opensource.org/licenses/BSD-2-Clause
import shutil
import tempfile

import unittest
import os
from stalker import (db, User, Repository, Status, FilenameTemplate, Structure,
                     StatusList, ImageFormat, Project, Type, Task, Version)
from anima.repr import Representation


class RepresentationTestCase(unittest.TestCase):
    """tests anima.repr.Representation class
    """
    temp_repo_path = ''
    remove_these_files_buffer = []

    @classmethod
    def create_version(cls, task, take_name):
        """A helper method for creating a new version

        :param task: the task
        :param take_name: the take_name name
        :return: the version
        """
        v = Version(task=task, take_name=take_name)
        db.DBSession.add(v)
        db.DBSession.commit()
        return v

    @classmethod
    def setUpClass(cls):
        """setup test
        """
        # -----------------------------------------------------------------
        # start of the setUp
        # create the environment variable and point it to a temp directory
        database_url = "sqlite:///:memory:"
        db.setup({'sqlalchemy.url': database_url})
        db.init()

        cls.temp_repo_path = tempfile.mkdtemp()

        cls.user1 = User(
            name='User 1',
            login='user1',
            email='user1@users.com',
            password='12345'
        )

        cls.repo1 = Repository(
            name='Test Project Repository',
            linux_path=cls.temp_repo_path,
            windows_path=cls.temp_repo_path,
            osx_path=cls.temp_repo_path
        )

        cls.status_new = Status.query.filter_by(code='NEW').first()
        cls.status_wip = Status.query.filter_by(code='WIP').first()
        cls.status_comp = Status.query.filter_by(code='CMPL').first()

        cls.task_template = FilenameTemplate(
            name='Task Template',
            target_entity_type='Task',
            path='{{project.code}}/'
                 '{%- for parent_task in parent_tasks -%}'
                 '{{parent_task.nice_name}}/'
                 '{%- endfor -%}',
            filename='{{version.nice_name}}'
                     '_v{{"%03d"|format(version.version_number)}}',
        )

        cls.structure = Structure(
            name='Project Struture',
            templates=[cls.task_template]
        )

        cls.project_status_list = StatusList(
            name='Project Statuses',
            target_entity_type='Project',
            statuses=[cls.status_new, cls.status_wip, cls.status_comp]
        )

        cls.image_format = ImageFormat(
            name='HD 1080',
            width=1920,
            height=1080,
            pixel_aspect=1.0
        )

        # create a test project
        cls.project = Project(
            name='Test Project',
            code='TP',
            repository=cls.repo1,
            status_list=cls.project_status_list,
            structure=cls.structure,
            image_format=cls.image_format
        )

        cls.task_status_list =\
            StatusList.query.filter_by(target_entity_type='Task').first()

        cls.character_type = Type(
            name='Character',
            code='CHAR',
            target_entity_type='Asset'
        )

        # create a test series of root task
        cls.task1 = Task(
            name='Test Task 1',
            project=cls.project
        )
        cls.task2 = Task(
            name='Test Task 2',
            project=cls.project
        )

        # commit everything
        db.DBSession.add_all([
            cls.repo1, cls.status_new, cls.status_wip, cls.status_comp,
            cls.project_status_list, cls.project, cls.task_status_list,
            cls.task1, cls.task2, cls.task_template
        ])
        db.DBSession.commit()

        cls.version1 = cls.create_version(cls.task1, 'Main')
        cls.version2 = cls.create_version(cls.task1, 'Main')
        cls.version3 = cls.create_version(cls.task1, 'Main')

        # create other reprs
        # BBOX
        cls.version4 = cls.create_version(cls.task1, 'Main@BBox')
        cls.version5 = cls.create_version(cls.task1, 'Main@BBox')
        cls.version5.is_published = True
        db.DBSession.commit()

        # ASS
        cls.version6 = cls.create_version(cls.task1, 'Main@ASS')
        cls.version7 = cls.create_version(cls.task1, 'Main@ASS')
        cls.version7.is_published = True
        db.DBSession.commit()

        # GPU
        cls.version8 = cls.create_version(cls.task1, 'Main@GPU')
        cls.version9 = cls.create_version(cls.task1, 'Main@GPU')

        # Non default take name
        cls.version10 = cls.create_version(cls.task1, 'alt1')
        cls.version11 = cls.create_version(cls.task1, 'alt1')

        # Hires
        cls.version12 = cls.create_version(cls.task1, 'alt1@Hires')
        cls.version13 = cls.create_version(cls.task1, 'alt1@Hires')

        # Midres
        cls.version14 = cls.create_version(cls.task1, 'alt1@Midres')
        cls.version15 = cls.create_version(cls.task1, 'alt1@Midres')

        # Lores
        cls.version16 = cls.create_version(cls.task1, 'alt1@Lores')
        cls.version17 = cls.create_version(cls.task1, 'alt1@Lores')
        cls.version17.is_published = True

        # No Repr
        cls.version18 = cls.create_version(cls.task1, 'NoRepr')
        cls.version19 = cls.create_version(cls.task1, 'NoRepr')
        db.DBSession.commit()

        # create a buffer for extra created files, which are to be removed
        cls.remove_these_files_buffer = []

    @classmethod
    def tearDownClass(cls):
        """cleanup the test
        """
        # set the db.session to None
        db.DBSession.remove()

        # delete the temp folder
        shutil.rmtree(cls.temp_repo_path, ignore_errors=True)

        for f in cls.remove_these_files_buffer:
            if os.path.isfile(f):
                os.remove(f)
            elif os.path.isdir(f):
                shutil.rmtree(f, True)

    def test_list_all_lists_all_representations(self):
        """testing if Representation.list_all() returns a list of strings
        showing the repr names.
        """
        expected_result = ['Base', 'BBox', 'ASS', 'GPU']
        rep = Representation(self.version1)
        result = rep.list_all()
        self.assertEqual(sorted(expected_result), sorted(result))

    def test_list_all_lists_all_representations_from_non_base_version(self):
        """testing if Representation.list_all() returns a list of strings
        showing the repr names by using non base version.
        """
        expected_result = ['Base', 'Hires', 'Midres', 'Lores']
        rep = Representation(self.version10)
        result = rep.list_all()
        self.assertEqual(sorted(expected_result), sorted(result))

    def test_find_method_finds_the_given_representation(self):
        """testing if Representation.find() finds the latest version with the
        given representation.
        """
        rep = Representation(self.version1)
        result = rep.find('BBox')
        self.assertEqual(self.version5, result)

    def test_find_method_finds_the_given_repr_from_different_repr(self):
        """testing if Representation.find() finds the latest version with the
        given representation from a different representation than the base one.
        """
        rep = Representation(self.version4)
        result = rep.find('ASS')
        self.assertEqual(self.version7, result)

    def test_find_method_returns_none_for_invalid_repr_name(self):
        """testing if Representation.find() returns None for invalid or
        nonexistent repr name
        """
        rep = Representation(self.version4)
        self.assertTrue(rep.find('NonExists') is None)

    def test_has_any_repr_method_is_working_properly(self):
        """testing if Representation.has_any_repr() method is working properly
        """
        rep = Representation(self.version1)
        self.assertTrue(rep.has_any_repr())

        rep.version = self.version17
        self.assertTrue(rep.has_any_repr())

        rep.version = self.version19
        self.assertFalse(rep.has_any_repr())

    def test_has_repr_method_is_working_properly(self):
        """testing if Representation.has_repr() method is working properly
        """
        rep = Representation(self.version1)
        self.assertTrue(rep.has_repr('BBox'))

        rep.version = self.version17
        self.assertTrue(rep.has_repr('Lores'))

        rep.version = self.version19
        self.assertFalse(rep.has_repr('BBox'))

    def test_get_base_take_name_is_working_properly(self):
        """testing if the Representation.get_base_take_name() method is working
        properly
        """
        rep = Representation()
        self.assertEqual('Main', rep.get_base_take_name(self.version1))
        self.assertEqual('alt1', rep.get_base_take_name(self.version10))
        self.assertEqual('alt1', rep.get_base_take_name(self.version12))
        self.assertEqual('NoRepr', rep.get_base_take_name(self.version18))

    def test_version_argument_is_skipped(self):
        """testing if it is possible to skip the version argument
        """
        rep = Representation()
        self.assertTrue(rep.version is None)

    def test_version_argument_is_none(self):
        """testing if the version argument can be None
        """
        rep = Representation(None)
        self.assertTrue(rep.version is None)

    def test_version_attribute_is_set_to_none(self):
        """testing if setting the version attribute to None is possible
        """
        rep = Representation(self.version1)
        self.assertFalse(rep.version is None)
        rep.version = None
        self.assertTrue(rep.version is None)

    def test_version_argument_is_not_a_version_instance(self):
        """testing if a TypeError will be raised when the version argument is
        not a Version instance
        """
        with self.assertRaises(TypeError) as cm:
            Representation('not a version')

        self.assertEqual(
            'Representation.version should be a '
            'stalker.models.version.Version instance, not str',
            str(cm.exception)
        )

    def test_version_attribute_is_not_a_version_instance(self):
        """testing if a TypeError will be raised when the version attribute is
        set to a value other then None and a Version instance
        """
        rep = Representation()
        with self.assertRaises(TypeError) as cm:
            rep.version = 'not a version'

        self.assertEqual(
            'Representation.version should be a '
            'stalker.models.version.Version instance, not str',
            str(cm.exception)
        )

    def test_version_argument_is_working_properly(self):
        """testing if the version argument value is correctly passed to the
        version attribute
        """
        rep = Representation(self.version1)
        self.assertEqual(rep.version, self.version1)

    def test_version_attribute_is_working_properly(self):
        """testing if the version attribute is working properly
        """
        rep = Representation(self.version1)
        self.assertNotEqual(rep.version, self.version2)
        rep.version = self.version2
        self.assertEqual(rep.version, self.version2)

    def test_is_base_method_is_working_properly(self):
        """testing if Representation.is_base() method is working properly
        """
        rep = Representation(self.version1)
        self.assertTrue(rep.is_base())

        rep = Representation(self.version4)
        self.assertFalse(rep.is_base())

    def test_is_repr_method_is_working_properly(self):
        """testing if Representation.is_repr() method is working properly
        """
        rep = Representation(self.version1)
        self.assertTrue(rep.is_repr('Base'))

        rep = Representation(self.version4)
        self.assertFalse(rep.is_repr('Base'))

        rep = Representation(self.version4)
        self.assertTrue(rep.is_repr('BBox'))

    def test_repr_property_is_working_properly(self):
        """testing if Representation.repr property is working properly
        """
        rep = Representation(self.version1)
        self.assertEqual(rep.repr, 'Base')

        rep = Representation(self.version4)
        self.assertTrue(rep.repr, 'BBox')

