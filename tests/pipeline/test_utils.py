# -*- coding: utf-8 -*-
# Copyright (c) 2012-2014, Anima Istanbul
#
# This module is part of anima-tools and is released under the BSD 2
# License: http://www.opensource.org/licenses/BSD-2-Clause
import shutil
import os

from stalker import (db, Project, Repository, Structure,
                     FilenameTemplate, User, Status, StatusList, ImageFormat,
                     Type, Task, Asset, Sequence, Shot, Version)
import tempfile

import unittest2
from anima.pipeline import utils
from anima.pipeline.utils import walk_version_hierarchy


class WaslkVersionHierarchyTestCase(unittest2.TestCase):
    """tests utils.walk_version_hierarchy() function
    """

    def setUp(self):
        """setup the tests
        """
        # -----------------------------------------------------------------
        # start of the setUp
        # create the environment variable and point it to a temp directory
        database_url = "sqlite:///:memory:"
        db.setup({'sqlalchemy.url': database_url})
        db.init()

        self.temp_repo_path = tempfile.mkdtemp()

        self.user1 = User(
            name='User 1',
            login='user1',
            email='user1@users.com',
            password='12345'
        )

        self.repo1 = Repository(
            name='Test Project Repository',
            linux_path=self.temp_repo_path,
            windows_path=self.temp_repo_path,
            osx_path=self.temp_repo_path
        )

        self.status_new = Status.query.filter_by(code='NEW').first()
        self.status_wip = Status.query.filter_by(code='WIP').first()
        self.status_comp = Status.query.filter_by(code='CMPL').first()

        self.task_template = FilenameTemplate(
            name='Task Template',
            target_entity_type='Task',
            path='{{project.code}}/'
                 '{%- for parent_task in version.task.parents -%}'
                 '{{parent_task.nice_name}}/'
                 '{%- endfor -%}',
            filename='{{version.nice_name}}'
                     '_v{{"%03d"|format(version.version_number)}}',
        )

        self.asset_template = FilenameTemplate(
            name='Asset Template',
            target_entity_type='Asset',
            path='{{project.code}}/'
                 '{%- for parent_task in version.task.parents -%}'
                 '{{parent_task.nice_name}}/'
                 '{%- endfor -%}',
            filename='{{version.nice_name}}'
                     '_v{{"%03d"|format(version.version_number)}}',
        )

        self.structure = Structure(
            name='Project Struture',
            templates=[self.task_template, self.asset_template]
        )

        self.project_status_list = StatusList(
            name='Project Statuses',
            target_entity_type='Project',
            statuses=[self.status_new, self.status_wip, self.status_comp]
        )

        self.image_format = ImageFormat(
            name='HD 1080',
            width=1920,
            height=1080,
            pixel_aspect=1.0
        )

        # create a test project
        self.project = Project(
            name='Test Project',
            code='TP',
            repository=self.repo1,
            status_list=self.project_status_list,
            structure=self.structure,
            image_format=self.image_format
        )

        self.task_status_list =\
            StatusList.query.filter_by(target_entity_type='Task').first()
        self.asset_status_list =\
            StatusList.query.filter_by(target_entity_type='Asset').first()
        self.shot_status_list =\
            StatusList.query.filter_by(target_entity_type='Shot').first()
        self.sequence_status_list =\
            StatusList.query.filter_by(target_entity_type='Sequence').first()

        self.character_type = Type(
            name='Character',
            code='CHAR',
            target_entity_type='Asset'
        )

        # create a test series of root task
        self.task1 = Task(
            name='Test Task 1',
            project=self.project
        )
        self.task2 = Task(
            name='Test Task 2',
            project=self.project
        )
        self.task3 = Task(
            name='Test Task 3',
            project=self.project
        )

        # then a couple of child tasks
        self.task4 = Task(
            name='Test Task 4',
            parent=self.task1
        )
        self.task5 = Task(
            name='Test Task 5',
            parent=self.task1
        )
        self.task6 = Task(
            name='Test Task 6',
            parent=self.task1
        )

        # create a root asset
        self.asset1 = Asset(
            name='Asset 1',
            code='asset1',
            type=self.character_type,
            project=self.project
        )

        # create a child asset
        self.asset2 = Asset(
            name='Asset 2',
            code='asset2',
            type=self.character_type,
            parent=self.task4
        )

        # create a root Sequence
        self.sequence1 = Sequence(
            name='Sequence1',
            code='SEQ1',
            project=self.project
        )

        # create a child Sequence
        self.sequence2 = Sequence(
            name='Sequence2',
            code='SEQ2',
            parent=self.task2
        )

        # create a root Shot
        self.shot1 = Shot(
            code='SH001',
            project=self.project
        )

        # create a child Shot (child of a Sequence)
        self.shot2 = Shot(
            code='SH002',
            parent=self.sequence1
        )

        # create a child Shot (child of a child Sequence)
        self.shot3 = Shot(
            code='SH003',
            parent=self.sequence2
        )

        # commit everything
        db.DBSession.add_all([
            self.repo1, self.status_new, self.status_wip, self.status_comp,
            self.project_status_list, self.project, self.task_status_list,
            self.asset_status_list, self.shot_status_list,
            self.sequence_status_list, self.task1, self.task2, self.task3,
            self.task4, self.task5, self.task6, self.asset1, self.asset2,
            self.shot1, self.shot2, self.shot3, self.sequence1, self.sequence2,
            self.task_template
        ])
        db.DBSession.commit()

        # now create versions
        def create_version(task, take_name):
            """Creates a new version
            :param task: the task
            :param take_name: the take_name name
            :return: the version
            """
            v = Version(task=task, take_name=take_name)
            db.DBSession.add(v)
            db.DBSession.commit()
            return v

        # asset2
        self.version1 = create_version(self.asset2, 'Main')
        self.version2 = create_version(self.asset2, 'Main')
        self.version3 = create_version(self.asset2, 'Main')

        self.version4 = create_version(self.asset2, 'Take1')
        self.version5 = create_version(self.asset2, 'Take1')
        self.version6 = create_version(self.asset2, 'Take1')

        # task5
        self.version7 = create_version(self.task5, 'Main')
        self.version8 = create_version(self.task5, 'Main')
        self.version9 = create_version(self.task5, 'Main')

        self.version10 = create_version(self.task5, 'Take1')
        self.version11 = create_version(self.task5, 'Take1')
        self.version12 = create_version(self.task5, 'Take1')

        # task6
        self.version13 = create_version(self.task6, 'Main')
        self.version14 = create_version(self.task6, 'Main')
        self.version15 = create_version(self.task6, 'Main')

        self.version16 = create_version(self.task6, 'Take1')
        self.version17 = create_version(self.task6, 'Take1')
        self.version18 = create_version(self.task6, 'Take1')

        # shot3
        self.version19 = create_version(self.shot3, 'Main')
        self.version20 = create_version(self.shot3, 'Main')
        self.version21 = create_version(self.shot3, 'Main')

        self.version22 = create_version(self.shot3, 'Take1')
        self.version23 = create_version(self.shot3, 'Take1')
        self.version24 = create_version(self.shot3, 'Take1')

        # task3
        self.version25 = create_version(self.task3, 'Main')
        self.version26 = create_version(self.task3, 'Main')
        self.version27 = create_version(self.task3, 'Main')

        self.version28 = create_version(self.task3, 'Take1')
        self.version29 = create_version(self.task3, 'Take1')
        self.version30 = create_version(self.task3, 'Take1')

        # asset1
        self.version31 = create_version(self.asset1, 'Main')
        self.version32 = create_version(self.asset1, 'Main')
        self.version33 = create_version(self.asset1, 'Main')

        self.version34 = create_version(self.asset1, 'Take1')
        self.version35 = create_version(self.asset1, 'Take1')
        self.version36 = create_version(self.asset1, 'Take1')

        # shot2
        self.version37 = create_version(self.shot2, 'Main')
        self.version38 = create_version(self.shot2, 'Main')
        self.version39 = create_version(self.shot2, 'Main')

        self.version40 = create_version(self.shot2, 'Take1')
        self.version41 = create_version(self.shot2, 'Take1')
        self.version42 = create_version(self.shot2, 'Take1')

        # shot1
        self.version43 = create_version(self.shot1, 'Main')
        self.version44 = create_version(self.shot1, 'Main')
        self.version45 = create_version(self.shot1, 'Main')

        self.version46 = create_version(self.shot1, 'Take1')
        self.version47 = create_version(self.shot1, 'Take1')
        self.version48 = create_version(self.shot1, 'Take1')

        # +- task1
        # |  |
        # |  +- task4
        # |  |  |
        # |  |  +- asset2
        # |  |     +- Main
        # |  |     |  +- version1
        # |  |     |  +- version2
        # |  |     |  +- version3
        # |  |     +- Take1
        # |  |        +- version4
        # |  |        +- version5
        # |  |        +- version6
        # |  |
        # |  +- task5
        # |  |  +- Main
        # |  |  |  +- version7
        # |  |  |  +- version8
        # |  |  |  +- version9
        # |  |  +- Take1
        # |  |     +- version10
        # |  |     +- version11
        # |  |     +- version12
        # |  |
        # |  +- task6
        # |     +- Main
        # |     |  +- version13
        # |     |  +- version14
        # |     |  +- version15
        # |     +- Take1
        # |        +- version16
        # |        +- version17
        # |        +- version18
        # |
        # +- task2
        # |  |
        # |  +- sequence2
        # |     |
        # |     +- shot3
        # |        +- Main
        # |        |  +- version19
        # |        |  +- version20
        # |        |  +- version21
        # |        +- Take1
        # |           +- version22
        # |           +- version23
        # |           +- version24
        # |
        # +- task3
        # |  +- Main
        # |  |  +- version25
        # |  |  +- version26
        # |  |  +- version27
        # |  +- Take1
        # |     +- version28
        # |     +- version29
        # |     +- version30
        # |
        # +- asset1
        # |  +- Main
        # |  |  +- version31
        # |  |  +- version32
        # |  |  +- version33
        # |  +- Take1
        # |     +- version34
        # |     +- version35
        # |     +- version36
        # |
        # +- sequence1
        # |  |
        # |  +- shot2
        # |     +- Main
        # |     |  +- version37
        # |     |  +- version38
        # |     |  +- version39
        # |     +- Take1
        # |        +- version40
        # |        +- version41
        # |        +- version42
        # |
        # +- shot1
        #    +- Main
        #    |  +- version43
        #    |  +- version44
        #    |  +- version45
        #    +- Take1
        #       +- version46
        #       +- version47
        #       +- version48

        # create a buffer for extra created files, which are to be removed
        self.remove_these_files_buffer = []

    def tearDown(self):
        """cleanup the test
        """
        # set the db.session to None
        db.DBSession.remove()

        # delete the temp folder
        shutil.rmtree(self.temp_repo_path, ignore_errors=True)

        for f in self.remove_these_files_buffer:
            if os.path.isfile(f):
                os.remove(f)
            elif os.path.isdir(f):
                shutil.rmtree(f, True)

    def test_walk_version_hierarchy_DFS_is_working_properly(self):
        """testing if walk_version_hierarchy is working properly in DFS mode
        """
        # create a hierarchy of versions
        self.version3.inputs.append(self.version6)
        self.version8.inputs.append(self.version3)

        self.version9.inputs.append(self.version3)
        self.version9.inputs.append(self.version8)
        self.version9.inputs.append(self.version12)

        self.version15.inputs.append(self.version9)
        self.version15.inputs.append(self.version18)

        self.version21.inputs.append(self.version24)

        self.version24.inputs.append(self.version6)

        self.version25.inputs.append(self.version33)

        self.version33.inputs.append(self.version24)

        self.version39.inputs.append(self.version42)

        self.version45.inputs.append(self.version48)

        self.version48.inputs.append(self.version33)

        # now test with different tasks
        visited_versions = []
        for v in walk_version_hierarchy(self.version3):
            visited_versions.append(v)
        expected_visited_versions = [self.version3, self.version6]
        self.assertEqual(
            expected_visited_versions,
            visited_versions
        )

        # now test with different tasks
        visited_versions = []
        for v in walk_version_hierarchy(self.version8):
            visited_versions.append(v)
        expected_visited_versions = \
            [self.version8, self.version3, self.version6]
        self.assertEqual(
            expected_visited_versions,
            visited_versions
        )

        # now test with different tasks
        visited_versions = []
        for v in walk_version_hierarchy(self.version9):
            visited_versions.append(v)
        expected_visited_versions = \
            [self.version9, self.version3, self.version6, self.version8,
             self.version3, self.version6, self.version12]
        self.assertEqual(
            expected_visited_versions,
            visited_versions
        )

        # now test with different tasks
        visited_versions = []
        for v in walk_version_hierarchy(self.version15):
            visited_versions.append(v)
        expected_visited_versions = \
            [self.version15, self.version9, self.version3, self.version6,
             self.version8, self.version3, self.version6, self.version12,
             self.version18]
        self.assertEqual(
            expected_visited_versions,
            visited_versions
        )

        # now test with different tasks
        visited_versions = []
        for v in walk_version_hierarchy(self.version21):
            visited_versions.append(v)
        expected_visited_versions = \
            [self.version21, self.version24, self.version6]
        self.assertEqual(
            expected_visited_versions,
            visited_versions
        )

        # now test with different tasks
        visited_versions = []
        for v in walk_version_hierarchy(self.version24):
            visited_versions.append(v)
        expected_visited_versions = \
            [self.version24, self.version6]
        self.assertEqual(
            expected_visited_versions,
            visited_versions
        )

        # now test with different tasks
        visited_versions = []
        for v in walk_version_hierarchy(self.version25):
            visited_versions.append(v)
        expected_visited_versions = \
            [self.version25, self.version33, self.version24, self.version6]
        self.assertEqual(
            expected_visited_versions,
            visited_versions
        )

        # now test with different tasks
        visited_versions = []
        for v in walk_version_hierarchy(self.version33):
            visited_versions.append(v)
        expected_visited_versions = \
            [self.version33, self.version24, self.version6]
        self.assertEqual(
            expected_visited_versions,
            visited_versions
        )

        # now test with different tasks
        visited_versions = []
        for v in walk_version_hierarchy(self.version39):
            visited_versions.append(v)
        expected_visited_versions = \
            [self.version39, self.version42]
        self.assertEqual(
            expected_visited_versions,
            visited_versions
        )

        # now test with different tasks
        visited_versions = []
        for v in walk_version_hierarchy(self.version45):
            visited_versions.append(v)
        expected_visited_versions = \
            [self.version45, self.version48, self.version33, self.version24,
             self.version6]
        self.assertEqual(
            expected_visited_versions,
            visited_versions
        )

        # now test with different tasks
        visited_versions = []
        for v in walk_version_hierarchy(self.version48):
            visited_versions.append(v)
        expected_visited_versions = \
            [self.version48, self.version33, self.version24,
             self.version6]
        self.assertEqual(
            expected_visited_versions,
            visited_versions
        )

    def test_walk_version_hierarchy_BFS_is_working_properly(self):
        """testing if walk_version_hierarchy is working properly in BFS mode
        """
        # create a hierarchy of versions
        self.version3.inputs.append(self.version6)
        self.version8.inputs.append(self.version3)

        self.version9.inputs.append(self.version3)
        self.version9.inputs.append(self.version8)
        self.version9.inputs.append(self.version12)

        self.version15.inputs.append(self.version9)
        self.version15.inputs.append(self.version18)

        self.version21.inputs.append(self.version24)

        self.version24.inputs.append(self.version6)

        self.version25.inputs.append(self.version33)

        self.version33.inputs.append(self.version24)

        self.version39.inputs.append(self.version42)

        self.version45.inputs.append(self.version48)

        self.version48.inputs.append(self.version33)

        # now test with different tasks
        visited_versions = []
        for v in walk_version_hierarchy(self.version3, 1):
            visited_versions.append(v)
        expected_visited_versions = [self.version3, self.version6]
        self.assertEqual(
            expected_visited_versions,
            visited_versions
        )

        # now test with different tasks
        visited_versions = []
        for v in walk_version_hierarchy(self.version8, 1):
            visited_versions.append(v)
        expected_visited_versions = \
            [self.version8, self.version3, self.version6]
        self.assertEqual(
            expected_visited_versions,
            visited_versions
        )

        # now test with different tasks
        visited_versions = []
        for v in walk_version_hierarchy(self.version9, 1):
            visited_versions.append(v)
        expected_visited_versions = \
            [self.version9, self.version3, self.version8, self.version12,
             self.version6, self.version3, self.version6]
        self.assertEqual(
            expected_visited_versions,
            visited_versions
        )

        # now test with different tasks
        visited_versions = []
        for v in walk_version_hierarchy(self.version15, 1):
            visited_versions.append(v)
        expected_visited_versions = \
            [self.version15, self.version9, self.version18, self.version3,
             self.version8, self.version12, self.version6, self.version3,
             self.version6]
        self.assertEqual(
            expected_visited_versions,
            visited_versions
        )

        # now test with different tasks
        visited_versions = []
        for v in walk_version_hierarchy(self.version21, 1):
            visited_versions.append(v)
        expected_visited_versions = \
            [self.version21, self.version24, self.version6]
        self.assertEqual(
            expected_visited_versions,
            visited_versions
        )

        # now test with different tasks
        visited_versions = []
        for v in walk_version_hierarchy(self.version24, 1):
            visited_versions.append(v)
        expected_visited_versions = \
            [self.version24, self.version6]
        self.assertEqual(
            expected_visited_versions,
            visited_versions
        )

        # now test with different tasks
        visited_versions = []
        for v in walk_version_hierarchy(self.version25, 1):
            visited_versions.append(v)
        expected_visited_versions = \
            [self.version25, self.version33, self.version24, self.version6]
        self.assertEqual(
            expected_visited_versions,
            visited_versions
        )

        # now test with different tasks
        visited_versions = []
        for v in walk_version_hierarchy(self.version33, 1):
            visited_versions.append(v)
        expected_visited_versions = \
            [self.version33, self.version24, self.version6]
        self.assertEqual(
            expected_visited_versions,
            visited_versions
        )

        # now test with different tasks
        visited_versions = []
        for v in walk_version_hierarchy(self.version39, 1):
            visited_versions.append(v)
        expected_visited_versions = \
            [self.version39, self.version42]
        self.assertEqual(
            expected_visited_versions,
            visited_versions
        )

        # now test with different tasks
        visited_versions = []
        for v in walk_version_hierarchy(self.version45, 1):
            visited_versions.append(v)
        expected_visited_versions = \
            [self.version45, self.version48, self.version33, self.version24,
             self.version6]
        self.assertEqual(
            expected_visited_versions,
            visited_versions
        )

        # now test with different tasks
        visited_versions = []
        for v in walk_version_hierarchy(self.version48, 1):
            visited_versions.append(v)
        expected_visited_versions = \
            [self.version48, self.version33, self.version24,
             self.version6]
        self.assertEqual(
            expected_visited_versions,
            visited_versions
        )

