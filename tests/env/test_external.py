# -*- coding: utf-8 -*-
# Copyright (c) 2012-2015, Anima Istanbul
#
# This module is part of anima-tools and is released under the BSD 2
# License: http://www.opensource.org/licenses/BSD-2-Clause
import shutil
import tempfile
import os

from stalker import (db, Version, Task, Project, Structure, StatusList,
                     Repository, Status, FilenameTemplate)
import unittest

from anima.env.external import ExternalEnv, ExternalEnvFactory


class ExternalEnvTestCase(unittest.TestCase):
    """tests ExternalEnv class
    """

    def setUp(self):
        """set up the test
        """
        db.setup()
        db.init()

        self.temp_path = tempfile.mkdtemp()
        self.repo = Repository(
            name='Test Repository',
            linux_path=self.temp_path,
            windows_path=self.temp_path,
            osx_path=self.temp_path
        )
        self.status_new = Status.query.filter_by(code='NEW').first()
        self.status_wip = Status.query.filter_by(code='WIP').first()
        self.status_cmpl = Status.query.filter_by(code='CMPL').first()

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
            filename='{{version.nice_name}}'
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

        self.task = Task(
            name='Test Task',
            project=self.project
        )
        self.version = Version(
            task=self.task
        )

        self.kwargs = {
            'name': 'Photoshop',
            'extensions': ['psd'],
            'structure': ['Outputs']
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
        self.kwargs.pop('extensions')
        self.assertRaises(TypeError, ExternalEnv, **self.kwargs)

    def test_extension_argument_cannot_be_None(self):
        """testing if a TypeError will be raised when the extension argument is
        None
        """
        self.kwargs['extensions'] = None
        self.assertRaises(TypeError, ExternalEnv, **self.kwargs)

    def test_extension_attribute_cannot_be_set_to_None(self):
        """testing if a TypeError will be raised when the extension attribute
        is set to None
        """
        self.assertRaises(TypeError, setattr, self.external_env, 'extensions', None)

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
        self.assertRaises(TypeError, setattr, self.external_env, 'extensions', 23)

    def test_extension_argument_with_no_dots_is_working(self):
        """testing if extension argument accepts strings without a dot at the
        beginning
        """
        self.kwargs['extensions'] = ['psd']
        external_env = ExternalEnv(**self.kwargs)
        self.assertEqual(['.psd'], external_env.extensions)

    def test_extension_attribute_with_no_dots_is_working(self):
        """testing if extension attribute accepts strings without a dot at the
        beginning
        """
        self.external_env.extensions = ['psd']
        self.assertEqual(['.psd'], self.external_env.extensions)

    def test_extension_argument_is_working_properly(self):
        """testing if the extension argument value is correctly passed to the
        extension attribute
        """
        test_value = ['.ztl']
        self.kwargs['extensions'] = test_value
        external_env = ExternalEnv(**self.kwargs)
        self.assertEqual(test_value, external_env.extensions)

    def test_extension_attribute_is_working_properly(self):
        """testing if the extension attribute value is correctly set
        """
        test_value = ['.ztl']
        self.external_env.extensions = test_value
        self.assertEqual(test_value, self.external_env.extensions)

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
        self.assertEqual(sorted(test_value), sorted(external_env.structure))

    def test_structure_attribute_is_working_properly(self):
        """testing if the structure attribute value can be correctly updated
        """
        test_value = ['Outputs', 'Inputs', 'cache']
        self.external_env.structure = test_value
        self.assertEqual(sorted(test_value),
                         sorted(self.external_env.structure))

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
        external_env = ExternalEnv(name='ZBrush', extensions=['.ztl'])

        external_env.conform(self.version)
        self.assertEqual(self.version.extension, '.ztl')

    def test_conform_method_will_set_the_version_created_with(self):
        """testing if the conform method will set the version extension to the
        environment name
        """
        self.assertNotEqual(self.version.extension, '.ztl')
        external_env = ExternalEnv(name='ZBrush', extensions=['.ztl'])

        external_env.conform(self.version)
        self.assertEqual(self.version.extension, '.ztl')
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

    def test_save_as_will_conform_and_initialize_structure(self):
        """testing if the save_as method will conform the given version and
        initialize the structure
        """
        self.external_env.save_as(self.version)
        self.assertEquals(self.external_env.extensions[0],
                          self.version.extension)
        for folder in self.external_env.structure:
            self.assertTrue(
                os.path.exists(
                    os.path.join(self.version.absolute_path, folder)
                )
            )

    def test_get_settings_file_path_returns_the_settings_path_correctly(self):
        """testing if the get_settings_path returns the settings path correctly
        """
        self.assertEqual(
            os.path.expanduser('~/.atrc/last_version'),
            ExternalEnv.get_settings_file_path()
        )

    def test_append_to_recent_files_version_argument_is_not_a_Version_instance(self):
        """testing if a TypeError will be raised when the version argument in
        append_to_recent_files() method is not a stalker.models.version.Version
        instance
        """
        self.assertRaises(TypeError, self.external_env.append_to_recent_files,
                          3121)

    def test_append_to_recent_files_working_properly(self):
        """testing if the append_to_recent_files() method is working properly
        """
        # set the id attribute of the test version to a random number
        self.version.id = 234
        self.external_env.append_to_recent_files(self.version)
        # check the settings file
        path = self.external_env.get_settings_file_path()
        with open(path, 'r') as f:
            vid = f.read()
        self.assertEqual(vid, str(234))

    def test_get_last_version_is_working_properly(self):
        """testing if hte get_last_version() method will return Version
        instance properly
        """
        # need a database for this test
        from stalker import db
        db.setup({'sqlalchemy.url': 'sqlite:///:memory:'})
        db.DBSession.add(self.version)
        db.DBSession.commit()
        self.assertTrue(self.version.id is not None)
        self.external_env.append_to_recent_files(self.version)
        last_version = self.external_env.get_last_version()
        self.assertEqual(last_version, self.version)


class ExternalEnvFactoryTestCase(unittest.TestCase):
    """tests ExternalEnvFactory class
    """

    @classmethod
    def setUpClass(cls):
        """set up once
        """
        db.setup()
        db.init()

    def test_get_env_names_method_will_return_all_environment_names_properly(self):
        """testing if ExternalEnvFactory.get_env_names() method will
        return all the environment names as a list of strings
        """
        from anima.env.external import external_environments
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
            '.ztl - ZBrush',
            '.mud - MudBox',
            #'.psd - Photoshop'
        ]
        ext_env_factory = ExternalEnvFactory()
        result = ext_env_factory.get_env_names(name_format=name_format)
        self.assertEqual(sorted(expected_result), sorted(result))

    def test_get_env_method_name_argument_is_not_a_string(self):
        """testing if a TypeError will be raised when the name argument is not
        a string in ExternalEnvironmentFactory.get_env() method
        """
        ext_env_factory = ExternalEnvFactory()
        self.assertRaises(TypeError, ext_env_factory.get_env, 234)

    def test_get_env_method_name_is_not_in_list(self):
        """testing if a ValueError will be raised when the name argument value
        is not in the anima.env.external_environments list
        """
        ext_env_factory = ExternalEnvFactory()
        self.assertRaises(ValueError, ext_env_factory.get_env, 'Modo')

    def test_get_env_method_will_return_desired_environment(self):
        """testing if ExternalEnvFactory.get_env() will return desired
        ExternalEnvironment instance
        """
        ext_env_factory = ExternalEnvFactory()

        #photoshop = ext_env_factory.get_env('Photoshop')
        #self.assertIsInstance(photoshop, ExternalEnv)
        #self.assertEqual(photoshop.name, 'Photoshop')
        #self.assertEqual(photoshop.extension, '.psd')
        #self.assertEqual(photoshop.structure, ['Outputs'])

        zbrush_tool = ext_env_factory.get_env('ZBrush')
        self.assertTrue(isinstance(zbrush_tool, ExternalEnv))
        self.assertEqual(zbrush_tool.name, 'ZBrush')
        self.assertEqual(zbrush_tool.extensions, ['.ztl'])
        self.assertEqual(zbrush_tool.structure, ['Outputs'])

        mudbox = ext_env_factory.get_env('MudBox')
        self.assertTrue(isinstance(mudbox, ExternalEnv))
        self.assertEqual(mudbox.name, 'MudBox')
        self.assertEqual(mudbox.extensions, ['.mud'])
        self.assertEqual(mudbox.structure, ['Outputs'])

    def test_get_env_method_will_return_desired_environment_even_with_complex_formats(self):
        """testing if ExternalEnvFactory.get_env() will return desired
        ExternalEnvironment instance even with names like "MudBox (.mud)"
        """
        ext_env_factory = ExternalEnvFactory()
        #
        #photoshop = ext_env_factory.get_env('Photoshop (.psd)',
        #                                    name_format='%n (%e)')
        #self.assertIsInstance(photoshop, ExternalEnv)
        #self.assertEqual(photoshop.name, 'Photoshop')
        #self.assertEqual(photoshop.extension, '.psd')
        #self.assertEqual(photoshop.structure, ['Outputs'])

        zbrush = ext_env_factory.get_env('ZBrush (.ztl)',
                                         name_format='%n (%e)')
        self.assertTrue(isinstance(zbrush, ExternalEnv))
        self.assertEqual(zbrush.name, 'ZBrush')
        self.assertEqual(zbrush.extensions, ['.ztl'])
        self.assertEqual(zbrush.structure, ['Outputs'])

        mudbox = ext_env_factory.get_env('MudBox (.mud)',
                                         name_format='%n (%e)')
        self.assertTrue(isinstance(mudbox, ExternalEnv))
        self.assertEqual(mudbox.name, 'MudBox')
        self.assertEqual(mudbox.extensions, ['.mud'])
        self.assertEqual(mudbox.structure, ['Outputs'])

    def test_get_env_method_will_return_desired_environment_even_with_custom_formats(self):
        """testing if ExternalEnvFactory.get_env() will return desired
        ExternalEnvironment instance even with names like "MudBox (.mud)"
        """
        ext_env_factory = ExternalEnvFactory()

        name_format = '(%e) - %n'

        #photoshop = ext_env_factory.get_env('(.psd) - Photoshop',
        #                                    name_format=name_format)
        #self.assertIsInstance(photoshop, ExternalEnv)
        #self.assertEqual(photoshop.name, 'Photoshop')
        #self.assertEqual(photoshop.extension, '.psd')
        #self.assertEqual(photoshop.structure, ['Outputs'])

        zbrush = ext_env_factory.get_env('(.ztl) ZBrush',
                                         name_format=name_format)
        self.assertTrue(isinstance(zbrush, ExternalEnv))
        self.assertEqual(zbrush.name, 'ZBrush')
        self.assertEqual(zbrush.extensions, ['.ztl'])
        self.assertEqual(zbrush.structure, ['Outputs'])

        mudbox = ext_env_factory.get_env('(.mud) MudBox',
                                         name_format=name_format)
        self.assertTrue(isinstance(mudbox, ExternalEnv))
        self.assertEqual(mudbox.name, 'MudBox')
        self.assertEqual(mudbox.extensions, ['.mud'])
        self.assertEqual(mudbox.structure, ['Outputs'])
