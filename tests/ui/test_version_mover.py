# -*- coding: utf-8 -*-
# Copyright (c) 2012-2015, Anima Istanbul
#
# This module is part of anima-tools and is released under the BSD 2
# License: http://www.opensource.org/licenses/BSD-2-Clause
import os
import sys
import tempfile
import unittest
import logging
from sqlalchemy import distinct

from anima.ui import SET_PYSIDE, IS_PYSIDE, IS_PYQT4

from anima.ui.version_mover import VersionMover
from anima.ui.testing import PatchedMessageBox

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

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


#from anima.ui.lib import QtCore, QtGui

from stalker import db, Task, Version, Project, Repository, Structure, \
    FilenameTemplate, StatusList, Status


class VersionMoverTestCase(unittest.TestCase):
    """tests the VersionMover class
    """

    original_message_box = None

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

    def create_version(self, task, take_name):
        """A helper method for creating a new version

        :param task: the task
        :param take_name: the take_name name
        :return: the Version instance
        """
        # just renew the scene
        v = Version(task=task, take_name=take_name)
        v.update_paths()

        db.DBSession.add(v)
        db.DBSession.commit()

        # create a file
        try:
            os.makedirs(os.path.dirname(v.absolute_full_path))
        except OSError:  # dir exists
            pass

        with open(v.absolute_full_path, 'w+'):
            pass

        return v

    @classmethod
    def setUpClass(cls):
        """set up once
        """
        # patch QMessageBox
        cls.original_message_box = QtGui.QMessageBox
        QtGui.QMessageBox = PatchedMessageBox

    @classmethod
    def tearDownClass(cls):
        """clean up once
        """
        QtGui.QMessageBox = cls.original_message_box

    def setUp(self):
        """sets up the test
        """
        db.setup()
        db.init()

        self.test_repo_path = tempfile.mkdtemp()

        # create test data
        self.test_repo = Repository(
            name='Test Repository',
            linux_path=self.test_repo_path,
            windows_path=self.test_repo_path,
            osx_path=self.test_repo_path
        )

        self.test_task_template = FilenameTemplate(
            name='Task Template',
            target_entity_type='Task',
            path='{{project.code}}/{%- for parent_task in parent_tasks -%}'
                 '{{parent_task.nice_name}}/{%- endfor -%}',
            filename='{{version.nice_name}}'
                     '_v{{"%03d"|format(version.version_number)}}',
        )

        self.test_structure = Structure(
            name='Test Project Structure',
            templates=[self.test_task_template]
        )

        self.status_new = Status.query.filter_by(code='NEW').first()
        self.status_wip = Status.query.filter_by(code='WIP').first()
        self.status_cmpl = Status.query.filter_by(code='CMPL').first()

        self.test_project_status_list = StatusList(
            name='Project Statuses',
            statuses=[self.status_new, self.status_wip, self.status_cmpl],
            target_entity_type='Project'
        )

        self.test_project1 = Project(
            name='Test Project 1',
            code='TP1',
            repository=self.test_repo,
            structure=self.test_structure,
            status_list=self.test_project_status_list
        )
        db.DBSession.add(self.test_project1)
        db.DBSession.commit()

        # now create tasks

        # root tasks
        self.test_task1 = Task(
            name='Task1',
            project=self.test_project1
        )

        self.test_task2 = Task(
            name='Task2',
            project=self.test_project1
        )

        self.test_task3 = Task(
            name='Task3',
            project=self.test_project1
        )

        # child of Task1
        self.test_task4 = Task(
            name='Task4',
            parent=self.test_task1
        )

        self.test_task5 = Task(
            name='Task5',
            parent=self.test_task1
        )

        self.test_task6 = Task(
            name='Task6',
            parent=self.test_task1
        )

        # child of Task2
        self.test_task7 = Task(
            name='Task7',
            parent=self.test_task2
        )

        self.test_task8 = Task(
            name='Task8',
            parent=self.test_task2
        )

        self.test_task9 = Task(
            name='Task9',
            parent=self.test_task2
        )

        # child of Task10
        self.test_task10 = Task(
            name='Task10',
            parent=self.test_task3
        )

        self.test_task11 = Task(
            name='Task11',
            parent=self.test_task3
        )

        self.test_task12 = Task(
            name='Task12',
            parent=self.test_task3
        )

        db.DBSession.add_all([
            self.test_task1, self.test_task2, self.test_task3, self.test_task4,
            self.test_task5, self.test_task6, self.test_task7, self.test_task8,
            self.test_task9, self.test_task10, self.test_task11,
            self.test_task12
        ])

        # now create versions for each of leaf tasks

        # Task4
        # Main
        self.test_version1 = self.create_version(self.test_task4,
                                                 take_name='Main')
        self.test_version2 = self.create_version(self.test_task4,
                                                 take_name='Main')
        self.test_version3 = self.create_version(self.test_task4,
                                                 take_name='Main')

        # Take1
        self.test_version4 = self.create_version(self.test_task4,
                                                 take_name='Take1')
        self.test_version5 = self.create_version(self.test_task4,
                                                 take_name='Take1')
        self.test_version6 = self.create_version(self.test_task4,
                                                 take_name='Take1')

        # Take2
        self.test_version7 = self.create_version(self.test_task4,
                                                 take_name='Take2')
        self.test_version8 = self.create_version(self.test_task4,
                                                 take_name='Take2')
        self.test_version9 = self.create_version(self.test_task4,
                                                 take_name='Take2')

        # Task5
        # Main
        self.test_version10 = self.create_version(self.test_task5,
                                                  take_name='Main')
        self.test_version11 = self.create_version(self.test_task5,
                                                  take_name='Main')
        self.test_version12 = self.create_version(self.test_task5,
                                                  take_name='Main')

        # Take1
        self.test_version13 = self.create_version(self.test_task5,
                                                  take_name='Take1')
        self.test_version14 = self.create_version(self.test_task5,
                                                  take_name='Take1')
        self.test_version15 = self.create_version(self.test_task5,
                                                  take_name='Take1')

        # Take2
        self.test_version16 = self.create_version(self.test_task5,
                                                  take_name='Take2')
        self.test_version17 = self.create_version(self.test_task5,
                                                  take_name='Take2')
        self.test_version18 = self.create_version(self.test_task5,
                                                  take_name='Take2')

        # Task6
        # Main
        self.test_version19 = self.create_version(self.test_task6,
                                                  take_name='Main')
        self.test_version20 = self.create_version(self.test_task6,
                                                  take_name='Main')
        self.test_version21 = self.create_version(self.test_task6,
                                                  take_name='Main')

        # Take1
        self.test_version22 = self.create_version(self.test_task6,
                                                  take_name='Take1')
        self.test_version23 = self.create_version(self.test_task6,
                                                  take_name='Take1')
        self.test_version24 = self.create_version(self.test_task6,
                                                  take_name='Take1')

        # Take2
        self.test_version25 = self.create_version(self.test_task6,
                                                  take_name='Take2')
        self.test_version26 = self.create_version(self.test_task6,
                                                  take_name='Take2')
        self.test_version27 = self.create_version(self.test_task6,
                                                  take_name='Take2')

        # Task7
        # Main
        self.test_version28 = self.create_version(self.test_task7,
                                                  take_name='Main')
        self.test_version29 = self.create_version(self.test_task7,
                                                  take_name='Main')
        self.test_version30 = self.create_version(self.test_task7,
                                                  take_name='Main')

        # Take1
        self.test_version31 = self.create_version(self.test_task7,
                                                  take_name='Take1')
        self.test_version32 = self.create_version(self.test_task7,
                                                  take_name='Take1')
        self.test_version33 = self.create_version(self.test_task7,
                                                  take_name='Take1')

        # Take2
        self.test_version34 = self.create_version(self.test_task7,
                                                  take_name='Take2')
        self.test_version35 = self.create_version(self.test_task7,
                                                  take_name='Take2')
        self.test_version36 = self.create_version(self.test_task7,
                                                  take_name='Take2')

        # Task8 - will have no versions

        # Task9 - it is a destination task with versions
        # Main
        self.test_version37 = self.create_version(self.test_task9,
                                                  take_name='Main')
        self.test_version38 = self.create_version(self.test_task9,
                                                  take_name='Main')
        self.test_version39 = self.create_version(self.test_task9,
                                                  take_name='Main')

        # Take1 - an existing take
        self.test_version40 = self.create_version(self.test_task9,
                                                  take_name='Take1')
        self.test_version41 = self.create_version(self.test_task9,
                                                  take_name='Take1')
        self.test_version42 = self.create_version(self.test_task9,
                                                  take_name='Take1')

        # Take3 - a non existing take
        self.test_version43 = self.create_version(self.test_task9,
                                                  take_name='Take1')
        self.test_version44 = self.create_version(self.test_task9,
                                                  take_name='Take1')
        self.test_version45 = self.create_version(self.test_task9,
                                                  take_name='Take1')

        if not QtGui.QApplication.instance():
            self.app = QtGui.QApplication(sys.argv)
        else:
            # self.app = QtGui.qApp
            self.app = QtGui.QApplication.instance()

        self.dialog = VersionMover()

    def tearDown(self):
        """clean up every time
        """
        PatchedMessageBox.tear_down()

    def test_copy_button_clicked_with_no_selection_on_from_task_tree_view(self):
        """testing if a QMessageDialog will be displayed when the copy button
        selected and no selection is made in from_task_tree_view
        """
        self.assertEqual(PatchedMessageBox.called_function, '')

        # now try to copy it
        QTest.mouseClick(self.dialog.copy_push_button, Qt.LeftButton)

        self.assertEqual(PatchedMessageBox.called_function, 'critical')
        self.assertEqual(PatchedMessageBox.title, 'Error')
        self.assertEqual(PatchedMessageBox.message,
                         'Please select a task from <b>From Task</b> list')

    def test_copy_button_clicked_with_no_selection_on_to_task_tree_view(self):
        """testing if a QMessageDialog will be displayed when the copy button
        selected and no selection is made in to_task_tree_vie
        """
        # select one task in from_task_tree_view

        # Select Task4 in from_task_tree_view
        selection_model = self.dialog.from_task_tree_view.selectionModel()
        model = self.dialog.from_task_tree_view.model()

        project1_item = model.item(0, 0)
        self.dialog.from_task_tree_view.expand(project1_item.index())

        task1_item = project1_item.child(0, 0)
        self.dialog.from_task_tree_view.expand(task1_item.index())

        task4_item = task1_item.child(0, 0)

        selection_model.select(
            task4_item.index(),
            QtGui.QItemSelectionModel.Select
        )

        self.assertEqual(PatchedMessageBox.called_function, '')

        # now try to copy it
        QTest.mouseClick(self.dialog.copy_push_button, Qt.LeftButton)

        self.assertEqual(PatchedMessageBox.called_function, 'critical')
        self.assertEqual(PatchedMessageBox.title, 'Error')
        self.assertEqual(PatchedMessageBox.message,
                         'Please select a task from <b>To Task</b> list')

    def test_copy_button_clicked_with_same_task_is_selected_in_both_sides(self):
        """testing if a QMessageDialog will warn the user about he/she selected
        the same task in both tree views
        """
        # select one task in from_task_tree_view

        # Select Task4 in from_task_tree_view
        selection_model = self.dialog.from_task_tree_view.selectionModel()
        model = self.dialog.from_task_tree_view.model()

        project1_item = model.item(0, 0)
        self.dialog.from_task_tree_view.expand(project1_item.index())

        task1_item = project1_item.child(0, 0)
        self.dialog.from_task_tree_view.expand(task1_item.index())

        task4_item = task1_item.child(0, 0)

        selection_model.select(
            task4_item.index(),
            QtGui.QItemSelectionModel.Select
        )

        # Select Task4 in to_task_tree_view
        selection_model = self.dialog.to_task_tree_view.selectionModel()
        model = self.dialog.to_task_tree_view.model()

        project1_item = model.item(0, 0)
        self.dialog.to_task_tree_view.expand(project1_item.index())

        task1_item = project1_item.child(0, 0)
        self.dialog.to_task_tree_view.expand(task1_item.index())

        task4_item = task1_item.child(0, 0)

        selection_model.select(
            task4_item.index(),
            QtGui.QItemSelectionModel.Select
        )

        self.assertEqual(PatchedMessageBox.called_function, '')

        # now try to copy it
        QTest.mouseClick(self.dialog.copy_push_button, Qt.LeftButton)

        self.assertEqual(PatchedMessageBox.called_function, 'critical')
        self.assertEqual(PatchedMessageBox.title, 'Error')
        self.assertEqual(PatchedMessageBox.message,
                         'Please select two different tasks')

    def test_copy_button_is_working_properly(self):
        """testing if the copy button is working properly
        """
        # Select Task4 in from_task_tree_view
        selection_model = self.dialog.from_task_tree_view.selectionModel()
        model = self.dialog.from_task_tree_view.model()

        project1_item = model.item(0, 0)
        self.dialog.from_task_tree_view.expand(project1_item.index())

        task1_item = project1_item.child(0, 0)
        self.dialog.from_task_tree_view.expand(task1_item.index())

        task4_item = task1_item.child(0, 0)

        selection_model.select(
            task4_item.index(),
            QtGui.QItemSelectionModel.Select
        )

        # Select Task8 in to_task_tree_view
        selection_model = self.dialog.to_task_tree_view.selectionModel()
        model = self.dialog.to_task_tree_view.model()

        project1_item = model.item(0, 0)
        self.dialog.to_task_tree_view.expand(project1_item.index())

        task2_item = project1_item.child(1, 0)
        self.dialog.to_task_tree_view.expand(task2_item.index())

        task8_item = task2_item.child(1, 0)

        selection_model.select(
            task8_item.index(),
            QtGui.QItemSelectionModel.Select
        )

        # before copying anything
        # check if there are no versions under Task8
        self.assertTrue(self.test_task8.versions == [])
        self.assertEqual(len(self.test_task4.versions), 9)

        take_name_count = db.DBSession\
            .query(distinct(Version.take_name))\
            .filter(Version.task == self.test_task4)\
            .count()
        self.assertEqual(take_name_count, 3)

        # for testing purposes set question result to QtGui.QMessageBox.Yes
        PatchedMessageBox.Yes = self.original_message_box.Yes
        PatchedMessageBox.No = self.original_message_box.No
        PatchedMessageBox.question_return_value = self.original_message_box.Yes

        # copy it
        QTest.mouseClick(self.dialog.copy_push_button, Qt.LeftButton)

        # and expect as many versions under task8 as the task4 take_names
        # check if it still has 9 versions
        self.assertEqual(len(self.test_task4.versions), 9)
        self.assertEqual(
            len(self.test_task8.versions),
            take_name_count
        )

        # check if files are copied there
        for version in self.test_task8.versions:
            self.assertTrue(os.path.exists(version.absolute_full_path))

    # def test_destination_task_has_versions_already(self):
    #     """testing if the there will be no problem when the destination task
    #     already has versions
    #     """
    #     self.fail('test is not implemented yet')

    # def test_move_button_clicked_with_no_selection_on_from_task_tree_view(self):
    #     """testing if a QMessageDialog will be displayed when the move button
    #     selected and no selection is made in from_task_tree_view
    #     """
    #     self.fail('test is not implemented yet')
    # 
    # def test_move_button_clicked_with_no_selection_on_to_task_tree_view(self):
    #     """testing if a QMessageDialog will be displayed when the move button
    #     selected and no selection is made in to_task_tree_vie
    #     """
    #     self.fail('test is not implemented yet')
    # 
    # def test_move_button_clicked_with_same_task_is_selected_in_both_sides(self):
    #     """testing if a QMessageDialog will warn the user about he/she selected
    #     the same task in both tree views
    #     """
    #     self.fail('test is not implemented yet')
    # 
    # def test_move_button_is_working_properly(self):
    #     """testing if the move button is working properly
    #     """
    #     self.fail('test is not implemented yet')

