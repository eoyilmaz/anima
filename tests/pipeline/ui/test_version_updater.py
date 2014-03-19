# -*- coding: utf-8 -*-
# Copyright (c) 2012-2014, Anima Istanbul
#
# This module is part of anima-tools and is released under the BSD 2
# License: http://www.opensource.org/licenses/BSD-2-Clause
import sys
import shutil
import tempfile
import os
import logging

import unittest2

from anima.utils import walk_version_hierarchy
from anima.env.testing import TestEnvironment


logger = logging.getLogger('anima.pipeline.ui.version_updater')
logger.setLevel(logging.DEBUG)

from anima.ui import IS_PYSIDE, IS_PYQT4, SET_PYSIDE, version_updater

SET_PYSIDE()

if IS_PYSIDE():
    logger.debug('environment is set to pyside, importing pyside')
    from PySide import QtCore, QtGui
    from PySide.QtTest import QTest
    from PySide.QtCore import Qt
elif IS_PYQT4():
    logger.debug('environment is set to pyqt4, importing pyqt4')
    import sip
    sip.setapi('QString', 2)
    sip.setapi('QVariant', 2)
    from PyQt4 import QtCore, QtGui
    from PyQt4.QtTest import QTest
    from PyQt4.QtCore import Qt

from stalker import (db, User, Project, Repository, Structure, Status,
                     StatusList, Task, Version, FilenameTemplate,
                     ImageFormat, Type, Asset, Sequence, Shot)


# exceptions for test purposes
class ExportAs(Exception):
    pass


class VersionUpdaterTester(unittest2.TestCase):
    """Tests the Version Updater UI instance
    """

    def show_dialog(self, dialog):
        """show the given dialog
        """
        dialog.show()
        self.app.exec_()
        self.app.connect(
            self.app,
            QtCore.SIGNAL("lastWindowClosed()"),
            self.app,
            QtCore.SLOT("quit()")
        )

    def setUp(self):
        """setup the tests
        """
        # -----------------------------------------------------------------
        # start of the setUp
        # create the environment variable and point it to a temp directory
        db.setup()
        db.init()

        self.temp_repo_path = tempfile.mkdtemp()

        self.user1 = User(
            name='User 1',
            login='user1',
            email='user1@users.com',
            password='12345'
        )
        db.DBSession.add(self.user1)
        db.DBSession.commit()

        # login as self.user1
        from stalker import LocalSession
        local_session = LocalSession()
        local_session.store_user(self.user1)
        local_session.save()

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
            name='SH001',
            code='SH001',
            project=self.project
        )

        # create a child Shot (child of a Sequence)
        self.shot2 = Shot(
            name='SH002',
            code='SH002',
            parent=self.sequence1
        )

        # create a child Shot (child of a child Sequence)
        self.shot3 = Shot(
            name='SH003',
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
            self.task_template, self.asset_template, self.shot_template,
            self.sequence_template
        ])
        db.DBSession.commit()

        # now create versions
        def create_version(task, take_name):
            """Creates a new version
            :param task: the task
            :param take_name: the take_name name
            :return: the version
            """
            # just renew the scene
            #pymel.core.newFile(force=True)

            v = Version(task=task, take_name=take_name)
            db.DBSession.add(v)
            db.DBSession.commit()
            #self.maya_env.save_as(v)
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
        # |  |     |  +- version2 (P)
        # |  |     |  +- version3 (P)
        # |  |     +- Take1
        # |  |        +- version4 (P)
        # |  |        +- version5
        # |  |        +- version6 (P)
        # |  |
        # |  +- task5
        # |  |  +- Main
        # |  |  |  +- version7
        # |  |  |  +- version8
        # |  |  |  +- version9
        # |  |  +- Take1
        # |  |     +- version10
        # |  |     +- version11
        # |  |     +- version12 (P)
        # |  |
        # |  +- task6
        # |     +- Main
        # |     |  +- version13
        # |     |  +- version14
        # |     |  +- version15
        # |     +- Take1
        # |        +- version16 (P)
        # |        +- version17
        # |        +- version18 (P)
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


        # Start Condition:
        #
        # version15
        #   version12
        #     version5
        #       version2 -> has new published version (version3)
        #     version5 -> Referenced a second time
        #       version2 -> has new published version (version3)
        #   version12 -> Referenced a second time
        #     version5
        #       version2 -> has new published version (version3)
        #     version5
        #       version2 -> has new published version (version3)
        #   version45 -> no change
        #     version48 -> no change
        #
        # Expected Final Result
        # version15A -> Derived from version15
        #   version12A -> Derived from version12
        #     version5A -> Derived from version5
        #       version3 -> has new published version (version3)
        #     version5A -> Derived from version5
        #       version3 -> has new published version (version3)
        #   version12A -> Derived from version12 - The second reference
        #     version5A -> Derived from version5
        #       version3 -> has new published version (version3)
        #     version5A -> Derived from version5
        #       version3 -> has new published version (version3)
        #   version45 -> no change
        #     version48 -> no change

        # create a deep relation
        self.version2.is_published = True
        self.version3.is_published = True

        # new scene
        # version5 references version2
        self.version5.inputs.append(self.version2)
        self.version5.is_published = True

        # version12 references version5
        self.version12.inputs.append(self.version5)
        self.version12.is_published = True

        # version45 references version48
        self.version45.is_published = True
        self.version48.is_published = True
        self.version45.inputs.append(self.version48)

        # version15 references version12 and version48
        self.version15.inputs.append(self.version12)
        self.version15.inputs.append(self.version45)

        # reference_resolution
        self.reference_resolution = {
            'root': [self.version12, self.version45],
            'leave': [self.version48, self.version45],
            'update': [self.version2],
            'create': [self.version5, self.version12]
        }

        # create a buffer for extra created files, which are to be removed
        self.remove_these_files_buffer = []

        self.test_environment = TestEnvironment(name='Test Environment')
        self.test_environment._version = self.version15

        if not QtGui.QApplication.instance():
            logger.debug('creating a new QApplication')
            self.app = QtGui.QApplication(sys.argv)
        else:
            logger.debug('using the present QApplication: %s' % QtGui.qApp)
            # self.app = QtGui.qApp
            self.app = QtGui.QApplication.instance()

        self.dialog = version_updater.MainDialog(
            environment=self.test_environment,
            reference_resolution=self.reference_resolution
        )

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

    def test_test_setup(self):
        """testing if the test setup is correct
        """
        print "version2  : %s" % self.version2
        print "version5  : %s" % self.version5
        print "version12 : %s" % self.version12
        print "version15 : %s" % self.version15

        # check the setup
        visited_versions = []
        for v in walk_version_hierarchy(self.version15):
            visited_versions.append(v)
        expected_visited_versions = \
            [self.version15, self.version12, self.version5, self.version2,
             self.version45, self.version48]

        print expected_visited_versions
        print visited_versions

        self.assertEqual(
            expected_visited_versions,
            visited_versions
        )

    def test_versions_treeView_displays_the_root_versions_correctly(self):
        """testing if versions_treeView is displaying the root versions
        correctly
        """
        # self.show_dialog(self.dialog)

        # check root rows
        version_tree_model = self.dialog.versions_treeView.model()
        row_count = version_tree_model.rowCount()
        self.assertEqual(2, row_count)

        # check if we have all items
        index = version_tree_model.index(0, 0)
        version12_item = version_tree_model.itemFromIndex(index)
        self.assertEqual(version12_item.version, self.version12)

        index = version_tree_model.index(1, 0)
        version45_item = version_tree_model.itemFromIndex(index)
        self.assertEqual(version45_item.version, self.version45)

    def test_versions_treeView_displays_the_version_hierarchy_correctly(self):
        """testing if versions_treeView is displaying the root versions
        correctly
        """
        # check root rows
        version_tree_model = self.dialog.versions_treeView.model()

        # check if we have all items
        index = version_tree_model.index(0, 0)
        version12_item = version_tree_model.itemFromIndex(index)

        index = version_tree_model.index(1, 0)
        version45_item = version_tree_model.itemFromIndex(index)

        # check deeper
        self.dialog.versions_treeView.expand(version12_item.index())
        version5_item = version12_item.child(0, 0)
        self.assertEqual(version5_item.version, self.version5)

        self.dialog.versions_treeView.expand(version5_item.index())
        version2_item = version5_item.child(0, 0)
        self.assertEqual(version2_item.version, self.version2)

        self.dialog.versions_treeView.expand(version45_item.index())
        version48_item = version45_item.child(0, 0)
        self.assertEqual(version48_item.version, self.version48)

    def test_versions_treeView_displays_the_version_hierarchy_colors_correctly(self):
        """testing if versions_treeView is displaying the versions in correct
        colors
        """
        # check root rows
        version_tree_model = self.dialog.versions_treeView.model()

        # check if we have all items
        index = version_tree_model.index(0, 0)
        version12_item = version_tree_model.itemFromIndex(index)

        index = version_tree_model.index(1, 0)
        version45_item = version_tree_model.itemFromIndex(index)

        # check deeper
        self.dialog.versions_treeView.expand(version12_item.index())
        version5_item = version12_item.child(0, 0)

        self.dialog.versions_treeView.expand(version5_item.index())
        version2_item = version5_item.child(0, 0)

        self.dialog.versions_treeView.expand(version45_item.index())
        version48_item = version45_item.child(0, 0)

        # version12
        fg = version12_item.foreground()
        color = fg.color()
        self.assertEqual(color, QtGui.QColor(192, 0, 0))

        # version5
        fg = version5_item.foreground()
        color = fg.color()
        self.assertEqual(color, QtGui.QColor(192, 0, 0))

        # version2
        fg = version2_item.foreground()
        color = fg.color()
        self.assertEqual(color, QtGui.QColor(192, 0, 0))

        # version45
        fg = version45_item.foreground()
        color = fg.color()
        self.assertEqual(color, QtGui.QColor(0, 192, 0))

        # version48
        fg = version48_item.foreground()
        color = fg.color()
        self.assertEqual(color, QtGui.QColor(0, 192, 0))

    def test_versions_treeView_displays_the_version_hierarchy_labels_correctly(self):
        """testing if versions_treeView is displaying the versions hierarchy
        with correct labels
        """
        # check root rows
        version_tree_model = self.dialog.versions_treeView.model()

        # check if we have all items
        index = version_tree_model.index(0, 0)
        version12_item = version_tree_model.itemFromIndex(index)

        index = version_tree_model.index(1, 0)
        version45_item = version_tree_model.itemFromIndex(index)

        # check deeper
        self.dialog.versions_treeView.expand(version12_item.index())
        version5_item = version12_item.child(0, 0)

        self.dialog.versions_treeView.expand(version5_item.index())
        version2_item = version5_item.child(0, 0)

        self.dialog.versions_treeView.expand(version45_item.index())
        version48_item = version45_item.child(0, 0)

        # version12 columns
        nice_name_item = \
            version_tree_model.itemFromIndex(version_tree_model.index(0, 2))
        take_column_item = \
            version_tree_model.itemFromIndex(version_tree_model.index(0, 3))
        current_version_column_item = \
            version_tree_model.itemFromIndex(version_tree_model.index(0, 4))
        latest_version_column_item = \
            version_tree_model.itemFromIndex(version_tree_model.index(0, 5))
        action_column_item = \
            version_tree_model.itemFromIndex(version_tree_model.index(0, 6))

        self.assertEqual(nice_name_item.text(),
                         'TP_Test_Task_1_Test_Task_5_Take1_v003')
        self.assertEqual(take_column_item.text(), 'Take1')
        self.assertEqual(current_version_column_item.text(), '3')
        self.assertEqual(latest_version_column_item.text(), '3')
        self.assertEqual(action_column_item.text(), 'create')

        # version5 columns
        nice_name_item = version12_item.child(0, 2)
        take_column_item = version12_item.child(0, 3)
        current_version_column_item = version12_item.child(0, 4)
        latest_version_column_item = version12_item.child(0, 5)
        action_column_item = version12_item.child(0, 6)

        self.assertEqual(nice_name_item.text(), 'TP_Asset_2_Take1_v002')
        self.assertEqual(take_column_item.text(), 'Take1')
        self.assertEqual(current_version_column_item.text(), '2')
        self.assertEqual(latest_version_column_item.text(), '2')
        self.assertEqual(action_column_item.text(), 'create')

        # version2 columns
        nice_name_item = version5_item.child(0, 2)
        take_column_item = version5_item.child(0, 3)
        current_version_column_item = version5_item.child(0, 4)
        latest_version_column_item = version5_item.child(0, 5)
        action_column_item = version5_item.child(0, 6)

        self.assertEqual(nice_name_item.text(), 'TP_Asset_2_Main_v002')
        self.assertEqual(take_column_item.text(), 'Main')
        self.assertEqual(current_version_column_item.text(), '2')
        self.assertEqual(latest_version_column_item.text(), '3')
        self.assertEqual(action_column_item.text(), 'update')

        # version45 columns
        nice_name_item = \
            version_tree_model.itemFromIndex(version_tree_model.index(1, 2))
        take_column_item = \
            version_tree_model.itemFromIndex(version_tree_model.index(1, 3))
        current_version_column_item = \
            version_tree_model.itemFromIndex(version_tree_model.index(1, 4))
        latest_version_column_item = \
            version_tree_model.itemFromIndex(version_tree_model.index(1, 5))
        action_column_item = \
            version_tree_model.itemFromIndex(version_tree_model.index(1, 6))

        self.assertEqual(nice_name_item.text(), 'TP_SH001_Main_v003')
        self.assertEqual(take_column_item.text(), 'Main')
        self.assertEqual(current_version_column_item.text(), '3')
        self.assertEqual(latest_version_column_item.text(), '3')
        self.assertEqual(action_column_item.text(), '')

        # version48
        nice_name_item = version45_item.child(0, 2)
        take_column_item = version45_item.child(0, 3)
        current_version_column_item = version45_item.child(0, 4)
        latest_version_column_item = version45_item.child(0, 5)
        action_column_item = version45_item.child(0, 6)

        self.assertEqual(nice_name_item.text(), 'TP_SH001_Take1_v003')
        self.assertEqual(take_column_item.text(), 'Take1')
        self.assertEqual(current_version_column_item.text(), '3')
        self.assertEqual(latest_version_column_item.text(), '3')
        self.assertEqual(action_column_item.text(), '')

    def test_all_the_root_version_items_check_state_is_True_by_default(self):
        """testing if all the check boxes for all the root items are already
        checked when the UI first appear
        """
        # check root rows
        version_tree_model = self.dialog.versions_treeView.model()

        # check if we have all items
        index = version_tree_model.index(0, 0)
        version12_item = version_tree_model.itemFromIndex(index)

        index = version_tree_model.index(1, 0)
        version45_item = version_tree_model.itemFromIndex(index)

        self.assertEqual(
            QtCore.Qt.CheckState.Checked,
            version12_item.checkState()
        )
        self.assertEqual(
            QtCore.Qt.CheckState.Checked,
            version45_item.checkState()
        )

    def test_generate_reference_resolution_generate_a_new_reference_resolution_correctly(self):
        """testing if version_updater.generate_reference_resolution() method
        will return a new reference_resolution according to the checked
        versions
        """
        reference_resolution = self.dialog.generate_reference_resolution()
        self.assertEqual(
            self.reference_resolution,
            reference_resolution
        )

        # now disable first version12_item
        # check root rows
        version_tree_model = self.dialog.versions_treeView.model()

        # check if we have all items
        index = version_tree_model.index(0, 0)
        version12_item = version_tree_model.itemFromIndex(index)

        version12_item.setCheckState(QtCore.Qt.CheckState.Unchecked)
        reference_resolution = self.dialog.generate_reference_resolution()
        self.assertEqual(
            {
                'root': [self.version12, self.version45],
                'leave': [self.version48, self.version45],
                'update': [],
                'create': []
            },
            reference_resolution
        )

    def test_update_versions_method_will_store_the_newly_created_Version_instances(self):
        """testing if the update_versions method will store the newly created
        versions in new_versions attribute
        """
        self.assertEqual(self.dialog.new_versions, [])
        self.dialog.update_versions()
        self.assertEqual(len(self.dialog.new_versions), 2)
        for v in self.dialog.new_versions:
            self.assertIsInstance(v, Version)

    def test_update_verions_method_will_update_new_versions_created_by_attribute(self):
        """testing if the update_versions method will update the created_by
        attributes of the newly created versions
        """
        self.assertEqual(self.dialog.new_versions, [])
        self.dialog.update_versions()
        self.assertEqual(len(self.dialog.new_versions), 2)
        for v in self.dialog.new_versions:
            self.assertEqual(v.created_by, self.user1)

    def test_update_pushButton_will_call_environment_update_versions_method(self):
        """testing if update_pushButton will call
        Test_Environment.update_versions method
        """
        self.assertRaises(
            KeyError,
            self.test_environment.test_data.__getitem__, 'update_versions'
        )
        # self.show_dialog(self.dialog)

        QTest.mouseClick(self.dialog.update_pushButton, Qt.LeftButton)
        print self.test_environment.test_data

        self.assertEqual(
            1,
            self.test_environment.test_data['update_versions']['call_count']
        )

    def test_select_none_pushButton_will_deselect_all_check_boxes_when_clicked(self):
        """testing if select none pushButton will deselect all the check boxes
        when clicked
        """
        # check if all are selected
        version_tree_model = self.dialog.versions_treeView.model()

        # check if we have all items
        index = version_tree_model.index(0, 0)
        version_item1 = version_tree_model.itemFromIndex(index)
        version_item1.setCheckState(QtCore.Qt.CheckState.Checked)

        index = version_tree_model.index(1, 0)
        version_item2 = version_tree_model.itemFromIndex(index)
        version_item2.setCheckState(QtCore.Qt.CheckState.Checked)

        QTest.mouseClick(self.dialog.selectNone_pushButton, Qt.LeftButton)

        self.assertEqual(version_item1.checkState(), QtCore.Qt.Unchecked)
        self.assertEqual(version_item2.checkState(), QtCore.Qt.Unchecked)

    def test_select_all_pushButton_will_select_all_check_boxes_when_clicked(self):
        """testing if select all pushButton will select all the check boxes
        when clicked
        """
        # check if all are selected
        version_tree_model = self.dialog.versions_treeView.model()

        # check if we have all items
        index = version_tree_model.index(0, 0)
        version_item1 = version_tree_model.itemFromIndex(index)
        version_item1.setCheckState(QtCore.Qt.CheckState.Unchecked)

        index = version_tree_model.index(1, 0)
        version_item2 = version_tree_model.itemFromIndex(index)
        version_item2.setCheckState(QtCore.Qt.CheckState.Unchecked)

        QTest.mouseClick(self.dialog.selectAll_pushButton, Qt.LeftButton)

        self.assertEqual(version_item1.checkState(), QtCore.Qt.Checked)
        self.assertEqual(version_item2.checkState(), QtCore.Qt.Checked)

    def test_init_will_fill_reference_resolution_if_it_is_empty_and_there_is_an_environment(self):
        """testing if the reference_resolution attribute will be filled by the
        environment if the reference_resolution argument is None or skipped and
        there is an environment
        """
        self.version1.inputs.append(self.version2)
        self.version1.inputs.append(self.version3)
        db.DBSession.commit()

        self.test_environment._version = self.version1

        new_dialog = version_updater.MainDialog(
            environment=self.test_environment
        )
        self.assertEqual(
            new_dialog.reference_resolution,
            self.test_environment.check_referenced_versions()
        )

    def test_init_will_raise_a_RuntimeError_if_the_current_version_is_None(self):
        """testing if a RuntimeError will be raised if the current_version of
        the environment is None
        """
        self.test_environment._version = None

        def patched(*args, **kwargs):
            pass

        # patch QMessageBox.critical method
        original = QtGui.QMessageBox.critical
        QtGui.QMessageBox.critical = patched

        self.assertRaises(RuntimeError, version_updater.MainDialog,
                          environment=self.test_environment)

        # restore QMessageBox.critical
        QtGui.QMessageBox.critical = original
