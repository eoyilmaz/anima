# -*- coding: utf-8 -*-
# Copyright (c) 2012-2019, Anima Istanbul
#
# This module is part of anima-tools and is released under the MIT
# License: http://www.opensource.org/licenses/MIT

import tempfile
import unittest

import pymel.core as pm

from stalker import (db, User, Repository, Status, FilenameTemplate, Structure,
                     StatusList, ImageFormat, Project, Task, Sequence, Shot,
                     Type, Version)

from anima.env.mayaEnv import previs, Maya


class ShotSplitterTestCase(unittest.TestCase):
    """tests the anima.env.maya.previs.ShotSplitter class
    """

    def setUp(self):
        """create test data
        """
        database_url = 'sqlite:///:memory:'
        db.setup({'sqlalchemy.url': database_url})
        db.init()

        self.temp_repo_path = tempfile.mkdtemp()

        self.user1 = User(
            name='User 1',
            login='User 1',
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
                 '{%- for parent_task in parent_tasks -%}'
                 '{{parent_task.nice_name}}/'
                 '{%- endfor -%}',
            filename='{{version.nice_name}}'
                     '_v{{"%03d"|format(version.version_number)}}',
        )

        self.asset_template = FilenameTemplate(
            name='Asset Template',
            target_entity_type='Asset',
            path='{{project.code}}/'
                 '{%- for parent_task in parent_tasks -%}'
                 '{{parent_task.nice_name}}/'
                 '{%- endfor -%}',
            filename='{{version.nice_name}}'
                     '_v{{"%03d"|format(version.version_number)}}',
        )

        self.shot_template = FilenameTemplate(
            name='Shot Template',
            target_entity_type='Shot',
            path='{{project.code}}/'
                 '{%- for parent_task in parent_tasks -%}'
                 '{{parent_task.nice_name}}/'
                 '{%- endfor -%}',
            filename='{{version.nice_name}}'
                     '_v{{"%03d"|format(version.version_number)}}',
        )

        self.sequence_template = FilenameTemplate(
            name='Sequence Template',
            target_entity_type='Sequence',
            path='{{project.code}}/'
                 '{%- for parent_task in parent_tasks -%}'
                 '{{parent_task.nice_name}}/'
                 '{%- endfor -%}',
            filename='{{version.nice_name}}'
                     '_v{{"%03d"|format(version.version_number)}}',
        )

        self.structure = Structure(
            name='Project Struture',
            templates=[self.task_template, self.asset_template,
                       self.shot_template, self.sequence_template]
        )

        self.project_status_list = \
            StatusList.query.filter_by(target_entity_type='Project').first()

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

        # create task hierarchy
        #
        # ASSETS
        #
        self.assets = Task(
            name='Assets',
            project=self.project,
            responsible=[self.user1]
        )

        #
        # SEQUENCES
        #
        self.sequences = Task(
            name='Sequences',
            project=self.project,
            responsible=[self.user1]
        )

        self.seq001 = Sequence(
            name='Seq001',
            code='Seq001',
            parent=self.sequences
        )

        self.scene_task = Task(
            name='001_IST',
            parent=self.seq001
        )

        self.scene_previs_type = Type(
            name='Scene Previs',
            code='Scene Previs',
            target_entity_type='Task'
        )

        self.scene_previs = Task(
            name='Scene Previs',
            parent=self.scene_task,
            type=self.scene_previs_type
        )

        self.shots = Task(
            name='Shots',
            parent=self.scene_task
        )

        self.shot1 = Shot(
            name='Seq001_001_IST_0010',
            code='Seq001_001_IST_0010',
            parent=self.shots
        )

        # create shot tasks
        self.previs = Task(
            name='Previs',
            parent=self.shot1
        )

        self.camera = Task(
            name='Camera',
            parent=self.shot1
        )

        self.animation = Task(
            name='Animation',
            parent=self.shot1
        )

        self.scene_assembly = Task(
            name='SceneAssembly',
            parent=self.shot1
        )

        self.lighting = Task(
            name='Lighting',
            parent=self.shot1
        )

        self.comp = Task(
            name='Comp',
            parent=self.shot1
        )

        # create maya files
        self.maya_env = Maya()
        pm.newFile(force=True)

        sm = pm.PyNode('sequenceManager1')

        seq1 = sm.create_sequence('001_IST')

        # create 3 shots
        shot1 = seq1.create_shot('shot1')
        shot2 = seq1.create_shot('shot2')
        shot3 = seq1.create_shot('shot3')

        # set shot ranges
        shot1.startFrame.set(1)
        shot1.endFrame.set(100)

        shot2.startFrame.set(101)
        shot2.endFrame.set(200)
        shot2.sequenceStartFrame.set(101)

        shot3.startFrame.set(201)
        shot3.endFrame.set(300)
        shot3.sequenceStartFrame.set(201)

        # save the file under scene previs
        v = Version(task=self.scene_previs)

        self.maya_env.save_as(v)
        pm.newFile(force=1)
        print(v.absolute_full_path)

    def test_test_setup(self):
        """to test test setup
        """
        pass
