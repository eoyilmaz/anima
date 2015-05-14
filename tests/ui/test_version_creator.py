# -*- coding: utf-8 -*-
# Copyright (c) 2012-2015, Anima Istanbul
#
# This module is part of anima-tools and is released under the BSD 2
# License: http://www.opensource.org/licenses/BSD-2-Clause
import sys
import shutil
import tempfile
import logging

import unittest
from anima.env.testing import TestEnvironment


logger = logging.getLogger('anima.ui.version_creator')
logger.setLevel(logging.DEBUG)

from stalker.models.auth import LocalSession
from anima.ui import IS_PYSIDE, IS_PYQT4, SET_PYSIDE, version_creator

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

from stalker import (db, defaults, User, Project, Repository, Structure,
                     Status, StatusList, Task, Group, Version)


class VersionCreatorTester(unittest.TestCase):
    """Tests the Version Creator instance
    """

    repo_path = ''

    @classmethod
    def setUpClass(cls):
        """setup once
        """
        # remove the transaction manager
        db.DBSession.remove()

        cls.repo_path = tempfile.mkdtemp()

        defaults.local_storage_path = tempfile.mktemp()

        db.setup({
            'sqlalchemy.url': 'sqlite:///:memory:',
            'sqlalchemy.echo': 'false'
        })
        db.init()

        # create Power Users Group
        cls.power_users_group = Group(name='Power Users')
        db.DBSession.add(cls.power_users_group)
        db.DBSession.commit()

        # create a LocalSession first
        cls.admin = User.query.all()[0]
        cls.lsession = LocalSession()
        cls.lsession.store_user(cls.admin)
        cls.lsession.save()

        # create a repository
        cls.test_repo1 = Repository(
            name='Test Repository',
            windows_path='T:/TestRepo/',
            linux_path='/mnt/T/TestRepo/',
            osx_path='/Volumes/T/TestRepo/'
        )

        cls.test_structure1 = Structure(
            name='Test Project Structure',
            templates=[],
            custom_template=''
        )

        cls.status_new = Status.query.filter_by(code='NEW').first()
        cls.status_wip = Status.query.filter_by(code='WIP').first()
        cls.status_cmpl = Status.query.filter_by(code='CMPL').first()

        cls.project_status_list = StatusList(
            name='Project Statuses',
            statuses=[cls.status_new, cls.status_wip, cls.status_cmpl],
            target_entity_type=Project
        )

        # create a couple of projects
        cls.test_project1 = Project(
            name='Project 1',
            code='P1',
            repository=cls.test_repo1,
            structure=cls.test_structure1,
            status_list=cls.project_status_list
        )

        cls.test_project2 = Project(
            name='Project 2',
            code='P2',
            repository=cls.test_repo1,
            structure=cls.test_structure1,
            status_list=cls.project_status_list
        )

        cls.test_project3 = Project(
            name='Project 3',
            code='P3',
            repository=cls.test_repo1,
            structure=cls.test_structure1,
            status_list=cls.project_status_list
        )

        cls.projects = [
            cls.test_project1,
            cls.test_project2,
            cls.test_project3
        ]

        cls.test_user1 = User(
            name='Test User',
            # groups=[self.power_users_group],
            login='tuser',
            email='tuser@tusers.com',
            password='secret'
        )
        db.DBSession.add(cls.test_user1)
        db.DBSession.commit()

        cls.admin.projects.append(cls.test_project1)
        cls.admin.projects.append(cls.test_project2)
        cls.admin.projects.append(cls.test_project3)
        cls.test_user1.projects.append(cls.test_project1)
        cls.test_user1.projects.append(cls.test_project2)
        cls.test_user1.projects.append(cls.test_project3)

        # project 1
        cls.test_task1 = Task(
            name='Test Task 1',
            project=cls.test_project1,
            resources=[cls.admin],
        )

        cls.test_task2 = Task(
            name='Test Task 2',
            project=cls.test_project1,
            resources=[cls.admin],
        )

        cls.test_task3 = Task(
            name='Test Task 2',
            project=cls.test_project1,
            resources=[cls.admin],
        )

        # project 2
        cls.test_task4 = Task(
            name='Test Task 4',
            project=cls.test_project2,
            resources=[cls.admin],
        )

        cls.test_task5 = Task(
            name='Test Task 5',
            project=cls.test_project2,
            resources=[cls.admin],
        )

        cls.test_task6 = Task(
            name='Test Task 6',
            parent=cls.test_task5,
            resources=[cls.admin],
        )

        cls.test_task7 = Task(
            name='Test Task 7',
            parent=cls.test_task5,
            resources=[],
        )

        cls.test_task8 = Task(
            name='Test Task 8',
            parent=cls.test_task5,
            resources=[],
        )

        cls.test_task9 = Task(
            name='Test Task 9',
            parent=cls.test_task5,
            resources=[],
        )

        # +-> Project 1
        # | |
        # | +-> Task1
        # | |
        # | +-> Task2
        # | |
        # | +-> Task3
        # |
        # +-> Project 2
        # | |
        # | +-> Task4
        # | |
        # | +-> Task5
        # |   |
        # |   +-> Task6
        # |   |
        # |   +-> Task7 (no resource)
        # |   |
        # |   +-> Task8 (no resource)
        # |   |
        # |   +-> Task9 (no resource)
        # |
        # +-> Project 3

        # record them all to the db
        db.DBSession.add_all([
            cls.admin, cls.test_project1, cls.test_project2, cls.test_project3,
            cls.test_task1, cls.test_task2, cls.test_task3, cls.test_task4,
            cls.test_task5, cls.test_task6, cls.test_task7, cls.test_task8,
            cls.test_task9
        ])
        db.DBSession.commit()

        cls.all_tasks = [
            cls.test_task1, cls.test_task2, cls.test_task3, cls.test_task4,
            cls.test_task5, cls.test_task6, cls.test_task7, cls.test_task8,
            cls.test_task9
        ]

        # create versions
        cls.test_version1 = Version(
            cls.test_task1,
            created_by=cls.admin,
            created_with='Test',
            description='Test Description'
        )
        db.DBSession.add(cls.test_version1)
        db.DBSession.commit()

        cls.test_version2 = Version(
            cls.test_task1,
            created_by=cls.admin,
            created_with='Test',
            description='Test Description'
        )
        db.DBSession.add(cls.test_version2)
        db.DBSession.commit()

        cls.test_version3 = Version(
            cls.test_task1,
            created_by=cls.admin,
            created_with='Test',
            description='Test Description'
        )
        cls.test_version3.is_published = True
        db.DBSession.add(cls.test_version3)
        db.DBSession.commit()

        cls.test_version4 = Version(
            cls.test_task1,
            take_name='Main@GPU',
            created_by=cls.admin,
            created_with='Test',
            description='Test Description'
        )
        cls.test_version4.is_published = True
        db.DBSession.add(cls.test_version4)
        db.DBSession.commit()

        if not QtGui.QApplication.instance():
            logger.debug('creating a new QApplication')
            cls.app = QtGui.QApplication(sys.argv)
        else:
            logger.debug('using the present QApplication: %s' % QtGui.qApp)
            # self.app = QtGui.qApp
            cls.app = QtGui.QApplication.instance()

        # cls.test_environment = TestEnvironment()
        cls.dialog = version_creator.MainDialog()
            # environment=cls.test_environment
        # )

    @classmethod
    def tearDownClass(cls):
        """teardown once
        """
        shutil.rmtree(
            defaults.local_storage_path,
            True
        )

        shutil.rmtree(cls.repo_path)

        # configure with transaction manager
        db.DBSession.remove()

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

    def test_close_button_closes_ui(self):
        """testing if the close button is closing the ui
        """
        self.dialog.show()

        self.assertEqual(self.dialog.isVisible(), True)

        # now run the UI
        QTest.mouseClick(self.dialog.close_pushButton, Qt.LeftButton)
        self.assertEqual(self.dialog.isVisible(), False)

    def test_login_dialog_is_shown_if_there_are_no_logged_in_user(self):
        """testing if the login dialog is shown if there is no logged in user
        """
        self.fail("Test is not implemented yet")

    def test_logged_in_user_field_is_updated_correctly(self):
        """testing if the logged_in_user field is updated correctly
        """
        # now expect to see the admin.name on the dialog.logged_in_user_label
        self.assertEqual(
            self.dialog.logged_in_user_label.text(),
            self.admin.name
        )

    def test_logout_button_shows_the_login_dialog(self):
        """logout dialog shows the login_dialog
        """
        self.fail('test is not implemented yet')

    def test_tasks_tree_view_is_filled_with_projects(self):
        """testing if the tasks_treeView is filled with projects as root
        level items
        """
        # now call the dialog and expect to see all these projects as root
        # level items in tasks_treeView

        self.assertEqual(
            len(self.admin.tasks),
            5
        )

        task_tree_model = self.dialog.tasks_treeView.model()
        row_count = task_tree_model.rowCount()
        self.assertEqual(3, row_count)

        index = task_tree_model.index(0, 0)
        p1_item = task_tree_model.itemFromIndex(index)
        self.assertEqual(p1_item.task, self.test_project1)

        index = task_tree_model.index(1, 0)
        p2_item = task_tree_model.itemFromIndex(index)
        self.assertEqual(p2_item.task, self.test_project2)

        index = task_tree_model.index(2, 0)
        p3_item = task_tree_model.itemFromIndex(index)
        self.assertEqual(p3_item.task, self.test_project3)

        # self.show_dialog(dialog)

    def test_tasks_tree_view_lists_all_tasks_properly(self):
        """testing if the tasks_treeView lists all the tasks properly
        """
        task_tree_model = self.dialog.tasks_treeView.model()
        row_count = task_tree_model.rowCount()
        self.assertEqual(3, row_count)

        # project1
        index = task_tree_model.index(0, 0)
        p1_item = task_tree_model.itemFromIndex(index)
        self.assertEqual(p1_item.task, self.test_project1)

        # project2
        index = task_tree_model.index(1, 0)
        p2_item = task_tree_model.itemFromIndex(index)
        self.assertEqual(p2_item.task, self.test_project2)

        # project3
        index = task_tree_model.index(2, 0)
        p3_item = task_tree_model.itemFromIndex(index)
        self.assertEqual(p3_item.task, self.test_project3)

        # self.show_dialog(self.dialog)

        # task1
        task1_item = p1_item.child(0, 0)
        self.assertEqual(task1_item.task, self.test_task1)

    def test_tasks_treeView_lists_only_my_tasks_if_checked(self):
        """testing if the tasks_treeView lists only my tasks if
        my_tasks_only_checkBox is checked
        """
        item_model = self.dialog.tasks_treeView.model()
        selection_model = self.dialog.tasks_treeView.selectionModel()

        # check show my tasks only check box
        self.dialog.my_tasks_only_checkBox.setChecked(True)

        # check if all my tasks are represented in the tree
        my_tasks = self.admin.tasks

        # generate a list of parent tasks
        all_my_parent_tasks = []
        for task in my_tasks:
            all_my_parent_tasks += task.parents

        all_my_parent_tasks = list(set(all_my_parent_tasks))

        for task in my_tasks:
            self.dialog.find_and_select_entity_item_in_treeView(
                task,
                self.dialog.tasks_treeView
            )
            # get the current selection
            self.assertEqual(
                task,
                self.dialog.get_task()
            )

        # check if non of the other tasks or their parents are visible
        for task in self.all_tasks:
            if task not in my_tasks and task not in all_my_parent_tasks:
                self.dialog.find_and_select_entity_item_in_treeView(
                    task,
                    self.dialog.tasks_treeView
                )
                # get the current selection
                self.assertTrue(self.dialog.get_task() is None)

        # now un check it and check if all tasks are shown
        self.dialog.my_tasks_only_checkBox.setChecked(False)
        # check if all the tasks are present in the tree
        for task in self.all_tasks:
            self.dialog.find_and_select_entity_item_in_treeView(
                task,
                self.dialog.tasks_treeView
            )
            # get the current selection
            self.assertEqual(self.dialog.get_task(), task)

    def test_takes_listWidget_lists_Main_by_default(self):
        """testing if the takes_listWidget lists "Main" by default
        """
        dialog = version_creator.MainDialog()
        self.assertEqual(
            defaults.version_take_name,
            dialog.takes_listWidget.currentItem().text()
        )

    def test_takes_listWidget_lists_Main_by_default_for_tasks_with_no_versions(self):
        """testing if the takes_listWidget lists "Main" by default for a task
        with no version
        """
        # now call the dialog and expect to see all these projects as root
        # level items in tasks_treeView

        dialog = version_creator.MainDialog()
        # self.show_dialog(dialog)

        self.assertEqual(
            defaults.version_take_name,
            dialog.takes_listWidget.currentItem().text()
        )

    def test_takes_listWidget_lists_Main_by_default_for_projects_with_no_tasks(self):
        """testing if the takes_listWidget lists "Main" by default for a
        project with no tasks
        """
        # now call the dialog and expect to see all these projects as root
        # level items in tasks_treeView

        dialog = version_creator.MainDialog()
        # self.show_dialog(dialog)

        self.assertEqual(
            defaults.version_take_name,
            dialog.takes_listWidget.currentItem().text()
        )

    def test_tasks_treeView_tasks_are_sorted(self):
        """testing if tasks in tasks_treeView are sorted according to their
        names
        """
        item_model = self.dialog.tasks_treeView.model()
        selection_model = self.dialog.tasks_treeView.selectionModel()

        index = item_model.index(0, 0)
        project1_item = item_model.itemFromIndex(index)
        self.dialog.tasks_treeView.expand(index)

        task1_item = project1_item.child(0, 0)
        self.assertEqual(task1_item.text(), self.test_task1.name)

        task2_item = project1_item.child(1, 0)
        self.assertEqual(task2_item.text(), self.test_task2.name)

    def test_tasks_treeView_do_not_cause_a_segfault(self):
        """there was a bug causing a segfault
        """
        dialog = version_creator.MainDialog()
        dialog = version_creator.MainDialog()
        dialog = version_creator.MainDialog()

    def test_previous_versions_tableWidget_is_filled_with_proper_info(self):
        """testing if the previous_versions_tableWidget is filled with proper
        information
        """
        # select the t1
        item_model = self.dialog.tasks_treeView.model()
        selection_model = self.dialog.tasks_treeView.selectionModel()

        index = item_model.index(0, 0)
        project1_item = item_model.itemFromIndex(index)
        # expand it
        self.dialog.tasks_treeView.expand(index)

        # get first child which is task1
        task1_item = project1_item.child(0, 0)

        # select task1
        selection_model.select(
            task1_item.index(),
            QtGui.QItemSelectionModel.Select
        )

        # select the first take
        self.dialog.takes_listWidget.setCurrentRow(0)

        # the row count should be 2
        self.assertEqual(
            self.dialog.previous_versions_tableWidget.rowCount(),
            3
        )

        # now check if the previous versions tableWidget has the info
        versions = [self.test_version1, self.test_version2, self.test_version3]
        for i in range(len(versions)):
            self.assertEqual(
                int(self.dialog.previous_versions_tableWidget.item(i, 0).text()),
                versions[i].version_number
            )

            self.assertEqual(
                self.dialog.previous_versions_tableWidget.item(i, 2).text(),
                versions[i].created_by.name
            )

            self.assertEqual(
                self.dialog.previous_versions_tableWidget.item(i, 6).text(),
                versions[i].description
            )

    def test_get_new_version_with_publish_check_box_is_checked_creates_published_version(self):
        """testing if checking publish_checkbox will create a published Version
        instance
        """
        # select the t1
        item_model = self.dialog.tasks_treeView.model()
        selection_model = self.dialog.tasks_treeView.selectionModel()

        index = item_model.index(0, 0)
        project1_item = item_model.itemFromIndex(index)
        # expand it
        self.dialog.tasks_treeView.expand(index)

        # get first child which is task1
        task1_item = project1_item.child(0, 0)

        # select task1
        selection_model.select(
            task1_item.index(),
            QtGui.QItemSelectionModel.Select
        )

        # first check if unpublished
        new_version = self.dialog.get_new_version()

        # is_published should be True
        self.assertFalse(new_version.is_published)

        # check task
        self.assertEqual(new_version.task, self.test_task1)

        # check the publish checkbox
        self.dialog.publish_checkBox.setChecked(True)

        new_version = self.dialog.get_new_version()

        # check task
        self.assertEqual(new_version.task, self.test_task1)

        # is_published should be True
        self.assertTrue(new_version.is_published)

    def test_users_can_change_the_publish_state_if_they_are_the_owner(self):
        """testing if the users are able to change the publish method if it is
        their versions
        """
        # select the t1
        item_model = self.dialog.tasks_treeView.model()
        selection_model = self.dialog.tasks_treeView.selectionModel()

        index = item_model.index(0, 0)
        project1_item = item_model.itemFromIndex(index)
        # expand it
        self.dialog.tasks_treeView.expand(index)

        # get first child which is task1
        task1_item = project1_item.child(0, 0)

        # select task1
        selection_model.select(
            task1_item.index(),
            QtGui.QItemSelectionModel.Select
        )

        # check if the menu item has a publish method for v8
        self.fail('test is not completed yet')

    def test_thumbnails_are_displayed_correctly(self):
        """testing if the thumbnails are displayed correctly
        """
        self.fail('test is not implemented yet')

    def test_representations_combo_box_lists_all_representations_of_current_env(self):
        """testing if representations_comboBox lists all the possible
        representations in current environment
        """
        test_environment = TestEnvironment()
        dialog = version_creator.MainDialog(
            environment=test_environment
        )
        for i in range(len(TestEnvironment.representations)):
            repr_name = TestEnvironment.representations[i]
            combo_box_text = dialog.representations_comboBox.itemText(i)
            self.assertEqual(repr_name, combo_box_text)

    def test_repr_as_separate_takes_check_box_is_unchecked_by_default(self):
        """testing if repr_as_separate_takes_checkBox is unchecked by default
        """
        self.assertFalse(
            self.dialog.repr_as_separate_takes_checkBox.isChecked()
        )

    def test_repr_as_separate_takes_check_box_is_working_properly(self):
        """testing if when the repr_as_separate_takes_checkBox is checked it
        will update the takes_listWidget to also show representation takes
        """
        # select project 1 -> task1
        item_model = self.dialog.tasks_treeView.model()
        selection_model = self.dialog.tasks_treeView.selectionModel()

        index = item_model.index(0, 0)
        project1_item = item_model.itemFromIndex(index)
        self.dialog.tasks_treeView.expand(index)

        task1_item = project1_item.child(0, 0)
        selection_model.select(
            task1_item.index(),
            QtGui.QItemSelectionModel.Select
        )

        # expect only one "Main" take listed in take_listWidget
        self.assertEqual(
            sorted(self.dialog.takes_listWidget.take_names),
            ['Main']
        )

        # check the repr_as_separate_takes_checkBox
        self.dialog.repr_as_separate_takes_checkBox.setChecked(True)

        # expect two takes of "Main" and "Main@GPU"
        self.assertEqual(
            sorted(self.dialog.takes_listWidget.take_names),
            ['Main', 'Main@GPU']
        )

        # self.show_dialog(self.dialog)

    def test_takes_with_representations_shows_in_blue(self):
        """testing if takes with representations will be displayed in blue
        """
        # select project 1 -> task1
        item_model = self.dialog.tasks_treeView.model()
        selection_model = self.dialog.tasks_treeView.selectionModel()

        index = item_model.index(0, 0)
        project1_item = item_model.itemFromIndex(index)
        self.dialog.tasks_treeView.expand(index)

        task1_item = project1_item.child(0, 0)
        selection_model.select(
            task1_item.index(),
            QtGui.QItemSelectionModel.Select
        )

        # expect only one "Main" take listed in take_listWidget
        main_item = self.dialog.takes_listWidget.item(0)
        item_foreground = main_item.foreground()
        color = item_foreground.color()
        self.assertEqual(
            color,
            QtGui.QColor(0, 0, 255)
        )
