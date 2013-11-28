# -*- coding: utf-8 -*-
# Copyright (c) 2012-2013, Anima Istanbul
#
# This module is part of anima-tools and is released under the BSD 2
# License: http://www.opensource.org/licenses/BSD-2-Clause
import shutil
import tempfile
import os
from stalker import Version, Task, Project, Structure, StatusList, Repository, Status, FilenameTemplate

import unittest2
from anima.pipeline.env.externalEnv import ExternalEnv, ExternalEnvFactory


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
        self.task_filename_template = FilenameTemplate(
            name='Task Filename Template',
            target_entity_type='Task',
            path='{{project.code}}/{%- for parent_task in parent_tasks -%}'
                 '{{parent_task.nice_name}}/{%- endfor -%}',
            filename='{{task.nice_name}}_{{version.take_name}}'
                     '_v{{"%03d"|format(version.version_number)}}{{extension}}'
        )
        self.project_structure = Structure(
            name='Project Structure',
            templates=[self.task_filename_template]
        )
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
        self.assertEqual(test_value, external_env.name)

    def test_name_attribute_is_working_properly(self):
        """testing if the name attribute value is correctly set
        """
        test_value = 'ZBrush'
        self.external_env.name = test_value
        self.assertEqual(test_value, self.external_env.name)

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
        test_value = '.ztl'
        self.kwargs['extension'] = test_value
        external_env = ExternalEnv(**self.kwargs)
        self.assertEqual(test_value, external_env.extension)

    def test_extension_attribute_is_working_properly(self):
        """testing if the extension attribute value is correctly set
        """
        test_value = '.ztl'
        self.external_env.extension = test_value
        self.assertEqual(test_value, self.external_env.extension)

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
        """testing if the conform method will set the version extension to the
        environment extension correctly
        """
        self.assertNotEqual(self.version.extension, '.ztl')
        external_env = ExternalEnv(name='ZBrush', extension='.ztl')

        external_env.conform(self.version)
        self.assertEqual(self.version.extension, '.ztl')

    def test_conform_method_will_set_the_version_created_with(self):
        """testing if the conform method will set the version extension to the
        environment name
        """
        self.assertNotEqual(self.version.extension, '.ztl')
        external_env = ExternalEnv(name='ZBrush', extension='.ztl')

        external_env.conform(self.version)
        self.assertEqual(self.version.created_with, 'ZBrush')

    def test_initialize_structure_version_argument_accepts_Version_instances_only(self):
        """testing if a TypeError will be raised when the version argument in
        initialize_structure method is not a Version instance
        """
        self.assertRaises(TypeError, self.external_env.initialize_structure,
                          version='not a version instance')

    def test_initialize_structure_will_create_the_folders_of_the_environment(self):
        """testing if the initialize_structure method will create the folders
        at the given Version instance path
        """
        self.external_env.initialize_structure(self.version)
        for folder in self.external_env.structure:
            self.assertTrue(
                os.path.exists(
                    os.path.join(self.version.absolute_path, folder)
                )
            )

    def test_initialize_structure_will_handle_OSErrors(self):
        """testing if the initialize_structure method will handle OSErrors when
        creating folders which are already there
        """
        # call it multiple times
        self.external_env.initialize_structure(self.version)
        self.external_env.initialize_structure(self.version)
        self.external_env.initialize_structure(self.version)


class ExternalEnvFactoryTestCase(unittest2.TestCase):
    """tests ExternalEnvFactory class
    """

    def test_get_env_names_method_will_return_all_environment_names_properly(self):
        """testing if ExternalEnvFactory.get_env_names() method will
        return all the environment names as a list of strings
        """
        from anima.pipeline.env.externalEnv import external_environments
        expected_result = external_environments.keys()
        ext_env_factory = ExternalEnvFactory()
        result = ext_env_factory.get_env_names()
        self.assertEqual(expected_result, result)

    def test_get_env_names_method_will_return_complex_environment_names_properly(self):
        """testing if ExternalEnvFactory.get_env_names() method will
        return all the environment names as a list of strings in desired format
        when environment_name_format is set
        """
        name_format = '%e - %n'
        expected_result = [
            '.zpr - ZBrush Project',
            '.ztl - ZBrush Tool',
            '.mud - MudBox',
            '.psd - Photoshop'
        ]
        ext_env_factory = ExternalEnvFactory()
        result = ext_env_factory.get_env_names(name_format=name_format)
        self.assertItemsEqual(expected_result, result)

    def test_get_env_method_name_argument_is_not_a_string(self):
        """testing if a TypeError will be raised when the name argument is not
        a string in ExternalEnvironmentFactory.get_env() method
        """
        ext_env_factory = ExternalEnvFactory()
        self.assertRaises(TypeError, ext_env_factory.get_env, 234)

    def test_get_env_method_name_is_not_in_list(self):
        """testing if a ValueError will be raised when the name argument value
        is not in the anima.pipeline.env.external_environments list
        """
        ext_env_factory = ExternalEnvFactory()
        self.assertRaises(ValueError, ext_env_factory.get_env, 'Modo')

    def test_get_env_method_will_return_desired_environment(self):
        """testing if ExternalEnvFactory.get_env() will return desired
        ExternalEnvironment instance
        """
        ext_env_factory = ExternalEnvFactory()

        photoshop = ext_env_factory.get_env('Photoshop')
        self.assertIsInstance(photoshop, ExternalEnv)
        self.assertEqual(photoshop.name, 'Photoshop')
        self.assertEqual(photoshop.extension, '.psd')
        self.assertEqual(photoshop.structure, ['Outputs'])

        zbrush_project = ext_env_factory.get_env('ZBrush Project')
        self.assertIsInstance(zbrush_project, ExternalEnv)
        self.assertEqual(zbrush_project.name, 'ZBrush Project')
        self.assertEqual(zbrush_project.extension, '.zpr')
        self.assertEqual(zbrush_project.structure, ['Outputs'])

        zbrush_tool = ext_env_factory.get_env('ZBrush Tool')
        self.assertIsInstance(zbrush_tool, ExternalEnv)
        self.assertEqual(zbrush_tool.name, 'ZBrush Tool')
        self.assertEqual(zbrush_tool.extension, '.ztl')
        self.assertEqual(zbrush_tool.structure, ['Outputs'])

        mudbox = ext_env_factory.get_env('MudBox')
        self.assertIsInstance(mudbox, ExternalEnv)
        self.assertEqual(mudbox.name, 'MudBox')
        self.assertEqual(mudbox.extension, '.mud')
        self.assertEqual(mudbox.structure, ['Outputs'])

    def test_get_env_method_will_return_desired_environment_even_with_complex_formats(self):
        """testing if ExternalEnvFactory.get_env() will return desired
        ExternalEnvironment instance even with names like "MudBox (.mud)"
        """
        ext_env_factory = ExternalEnvFactory()

        photoshop = ext_env_factory.get_env('Photoshop (.psd)',
                                            name_format='%n (%e)')
        self.assertIsInstance(photoshop, ExternalEnv)
        self.assertEqual(photoshop.name, 'Photoshop')
        self.assertEqual(photoshop.extension, '.psd')
        self.assertEqual(photoshop.structure, ['Outputs'])

        zbrush_project = ext_env_factory.get_env('ZBrush Project (.zpr)',
                                                 name_format='%n (%e)')
        self.assertIsInstance(zbrush_project, ExternalEnv)
        self.assertEqual(zbrush_project.name, 'ZBrush Project')
        self.assertEqual(zbrush_project.extension, '.zpr')
        self.assertEqual(zbrush_project.structure, ['Outputs'])

        zbrush_tool = ext_env_factory.get_env('ZBrush Tool (.ztl)',
                                              name_format='%n (%e)')
        self.assertIsInstance(zbrush_tool, ExternalEnv)
        self.assertEqual(zbrush_tool.name, 'ZBrush Tool')
        self.assertEqual(zbrush_tool.extension, '.ztl')
        self.assertEqual(zbrush_tool.structure, ['Outputs'])

        mudbox = ext_env_factory.get_env('MudBox (.mud)',
                                         name_format='%n (%e)')
        self.assertIsInstance(mudbox, ExternalEnv)
        self.assertEqual(mudbox.name, 'MudBox')
        self.assertEqual(mudbox.extension, '.mud')
        self.assertEqual(mudbox.structure, ['Outputs'])

    def test_get_env_method_will_return_desired_environment_even_with_custom_formats(self):
        """testing if ExternalEnvFactory.get_env() will return desired
        ExternalEnvironment instance even with names like "MudBox (.mud)"
        """
        ext_env_factory = ExternalEnvFactory()

        name_format = '(%e) - %n'

        photoshop = ext_env_factory.get_env('(.psd) - Photoshop',
                                            name_format=name_format)
        self.assertIsInstance(photoshop, ExternalEnv)
        self.assertEqual(photoshop.name, 'Photoshop')
        self.assertEqual(photoshop.extension, '.psd')
        self.assertEqual(photoshop.structure, ['Outputs'])

        zbrush_project = ext_env_factory.get_env('(.zpr) ZBrush Project',
                                                 name_format=name_format)
        self.assertIsInstance(zbrush_project, ExternalEnv)
        self.assertEqual(zbrush_project.name, 'ZBrush Project')
        self.assertEqual(zbrush_project.extension, '.zpr')
        self.assertEqual(zbrush_project.structure, ['Outputs'])

        zbrush_tool = ext_env_factory.get_env('(.ztl) ZBrush Tool',
                                              name_format=name_format)
        self.assertIsInstance(zbrush_tool, ExternalEnv)
        self.assertEqual(zbrush_tool.name, 'ZBrush Tool')
        self.assertEqual(zbrush_tool.extension, '.ztl')
        self.assertEqual(zbrush_tool.structure, ['Outputs'])

        mudbox = ext_env_factory.get_env('(.mud) MudBox',
                                         name_format=name_format)
        self.assertIsInstance(mudbox, ExternalEnv)
        self.assertEqual(mudbox.name, 'MudBox')
        self.assertEqual(mudbox.extension, '.mud')
        self.assertEqual(mudbox.structure, ['Outputs'])



