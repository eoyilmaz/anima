# -*- coding: utf-8 -*-
# Copyright (c) 2012-2013, Anima Istanbul
#
# This module is part of anima-tools and is released under the BSD 2
# License: http://www.opensource.org/licenses/BSD-2-Clause
import shutil
import tempfile
import os
from stalker import Version, Task, Project, Structure, StatusList, Repository, Status

import unittest2
from anima.pipeline.env.externalEnv import ExternalEnv


class ExternalEnvTestCase(unittest2.TestCase):
    """tests ExternalEnv class
    """

    def setUp(self):
        """set up the test
        """
        self.temp_path = tempfile.mkdtemp()
        self.repo = Repository(
            name='Test Repository',
            linux_path=self.temp_path,
            windows_path=self.temp_path,
            osx_path=self.temp_path
        )
        self.status_new = Status(name='New', code='NEW')
        self.status_wip = Status(name='Work In Progress', code='WIP')
        self.status_cmpl = Status(name='Complete', code='CMPL')
        self.project_status_list = StatusList(
            target_entity_type='Project',
            name='Project Statuses',
            statuses=[self.status_new, self.status_wip, self.status_cmpl]
        )
        self.project_structure = Structure(name='Project Structure')
        self.project = Project(
            name='Test Project',
            code='TP',
            status_list=self.project_status_list,
            repository=self.repo,
            structure=self.project_structure
        )
        self.task_status_list = StatusList(
            target_entity_type='Task',
            name='Task Statuses',
            statuses=[self.status_new, self.status_wip, self.status_cmpl]
        )
        self.task = Task(
            name='Test Task',
            project=self.project,
            status_list=self.task_status_list
        )
        self.version = Version(
            task=self.task
        )
        
        self.kwargs = {
            'name': 'Photoshop',
            'extension': 'psd',
            'structure': [
                'Outputs'
            ]
        }

        self.external_env = ExternalEnv(**self.kwargs)

    def tearDown(self):
        """clean up the test
        """
        shutil.rmtree(self.temp_path)

    def test_name_argument_cannot_be_skipped(self):
        """testing if a TypeError will raised when the name argument is skipped
        """
        self.kwargs.pop('name')
        self.assertRaises(TypeError, ExternalEnv, **self.kwargs)

    def test_name_argument_cannot_be_None(self):
        """testing if a TypeError will be raised when the name argument is None
        """
        self.kwargs['name'] = None
        self.assertRaises(TypeError, ExternalEnv, **self.kwargs)

    def test_name_attribute_cannot_be_set_to_None(self):
        """testing if a TypeError will be raised when the name attribute is set
        to None
        """
        self.assertRaises(TypeError, setattr, self.external_env, 'name', None)

    def test_name_argument_should_be_a_string(self):
        """testing if a TypeError will be raised when the name argument is not
        a string
        """
        self.kwargs['name'] = 32
        self.assertRaises(TypeError, **self.kwargs)

    def test_name_attribute_should_be_set_to_a_string(self):
        """testing if a TypeError will be raised when the name attribute is set
        to a value other than a string
        """
        self.assertRaises(TypeError, setattr, self.external_env, 'name', 23)

    def test_name_argument_is_working_properly(self):
        """testing if the name argument value is correctly passed to the name
        attribute
        """
        test_value = 'ZBrush'
        self.kwargs['name'] = test_value
        external_env = ExternalEnv(**self.kwargs)
        self.assertEqual(test_value, external_env)

    def test_name_attribute_is_working_properly(self):
        """testing if the name attribute value is correctly set
        """
        test_value = 'ZBrush'
        self.external_env = test_value
        self.assertEqual(test_value, self.external_env)

    def test_extension_argument_cannot_be_skipped(self):
        """testing if a TypeError will raised when the extension argument is
        skipped
        """
        self.kwargs.pop('extension')
        self.assertRaises(TypeError, ExternalEnv, **self.kwargs)

    def test_extension_argument_cannot_be_None(self):
        """testing if a TypeError will be raised when the extension argument is
        None
        """
        self.kwargs['extension'] = None
        self.assertRaises(TypeError, ExternalEnv, **self.kwargs)

    def test_extension_attribute_cannot_be_set_to_None(self):
        """testing if a TypeError will be raised when the extension attribute
        is set to None
        """
        self.assertRaises(TypeError, setattr, self.external_env, 'extension', None)

    def test_extension_argument_should_be_a_string(self):
        """testing if a TypeError will be raised when the extension argument is
        not a string
        """
        self.kwargs['extension'] = 32
        self.assertRaises(TypeError, **self.kwargs)

    def test_extension_attribute_should_be_set_to_a_string(self):
        """testing if a TypeError will be raised when the extension attribute
        is set to a value other than a string
        """
        self.assertRaises(TypeError, setattr, self.external_env, 'extension', 23)

    def test_extension_argument_is_working_properly(self):
        """testing if the extension argument value is correctly passed to the
        extension attribute
        """
        test_value = 'ztl'
        self.kwargs['extension'] = test_value
        external_env = ExternalEnv(**self.kwargs)
        self.assertEqual(test_value, external_env)

    def test_extension_attribute_is_working_properly(self):
        """testing if the extension attribute value is correctly set
        """
        test_value = 'ztl'
        self.external_env.extension = test_value
        self.assertEqual(test_value, self.external_env)

    def test_structure_argument_can_be_skipped(self):
        """testing if the structure argument can be skipped
        """
        self.kwargs.pop('structure')
        ExternalEnv(**self.kwargs)

    def test_structure_attribute_value_when_structure_argument_is_skipped(self):
        """testing if the structure argument attribute will be an empty list
        when the structure argument is skipped
        """
        self.kwargs.pop('structure')
        external_env = ExternalEnv(**self.kwargs)
        self.assertEqual(external_env.structure, [])

    def test_structure_argument_can_be_set_to_None(self):
        """testing if the structure argument can be set to None
        """
        self.kwargs['structure'] = None
        ExternalEnv(**self.kwargs)

    def test_structure_attribute_value_when_structure_argument_is_None(self):
        """testing if the structure argument attribute will be an empty list
        when the structure argument value is None
        """
        self.kwargs['structure'] = None
        external_env = ExternalEnv(**self.kwargs)
        self.assertEqual(external_env.structure, [])

    def test_structure_attribute_can_be_set_to_None(self):
        """testing if the structure attribute value will be an empty list when
        the structure attribute is set to None
        """
        self.external_env.structure = None

    def test_structure_argument_is_not_a_list(self):
        """testing if a TypeError will be raised when the structure argument
        is not None or a list
        """
        self.kwargs['structure'] = 'this is not a list'
        self.assertRaises(TypeError, ExternalEnv, **self.kwargs)

    def test_structure_attribute_is_not_a_list(self):
        """testing if a TypeError will be raised when the structure attribute
        is not a set to None or a list
        """
        self.assertRaises(TypeError, self.external_env, 'structure',
                          'this is not a list')

    def test_structure_argument_is_not_a_list_of_strings(self):
        """testing if a TypeError will be raised when not all the the elements
        are strings in structure argument
        """
        self.kwargs['structure'] = ['not', 1, 'list of', 'strings']
        self.assertRaises(TypeError, ExternalEnv, **self.kwargs)

    def test_structure_attribute_is_not_a_list_of_strings(self):
        """testing if a TypeError will be raised when not all the the elements
        are strings in structure attribute value
        """
        test_value = ['not', 1, 'list of', 'strings']
        self.assertRaises(TypeError, setattr, self.external_env, 'structure',
                          test_value)

    def test_structure_argument_is_working_properly(self):
        """testing if the structure argument value is correctly passed to the
        structure attribute
        """
        test_value = ['Outputs', 'Inputs', 'cache']
        self.kwargs['structure'] = test_value
        external_env = ExternalEnv(**self.kwargs)
        self.assertItemsEqual(test_value, external_env.structure)

    def test_structure_attribute_is_working_properly(self):
        """testing if the structure attribute value can be correctly updated
        """
        test_value = ['Outputs', 'Inputs', 'cache']
        self.external_env.structure = test_value
        self.assertItemsEqual(test_value, self.external_env.structure)

    def test_conform_version_argument_accepts_Version_instances_only(self):
        """testing if a TypeError will be raised when the version argument in
        conform method is not a Version instance
        """
        self.assertRaises(TypeError, self.external_env.conform,
                          version='not a version instance')

    def test_conform_method_will_set_the_version_extension(self):
        """testing if the conform method will set the method extension to the
        environment extension correctly
        """
        self.assertNotEqual(self.version.extension, '.ztl')
        external_env = ExternalEnv(name='ZBrush', extension='.ztl')

        external_env.conform(self.version)
        self.assertEqual(self.version.extension, '.ztl')

    def test_initialize_structure_version_argument_accepts_Version_instances_only(self):
        """testing if a TypeError will be raised when the version argument in
        initialize_structure method is not a Version instance
        """
        self.assertRaises(TypeError, self.external_env.conform,
                          version='not a version instance')

    def test_initialize_structure_will_create_the_folders_of_the_environemnt(self):
        """testing if the initialize_structure method will create the folders
        at the given Version instance path
        """
        self.external_env.conform(self.version)
        for folder in self.external_env.structure:
            self.assertTrue(
                os.path.exists(
                    os.path.join(self.version.absolute_path, folder)
                )
            )


class ExternalEnvFactoryTestCase(unittest2.TestCase):
    """tests ExternalEnvFactory class
    """

    pass


