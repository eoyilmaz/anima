# -*- coding: utf-8 -*-
# Copyright (c) 2012-2013, Anima Istanbul
#
# This module is part of anima-tools and is released under the BSD 2
# License: http://www.opensource.org/licenses/BSD-2-Clause
import os
import sys
import shutil
import tempfile
import unittest2
import logging

from stalker.models.auth import LocalSession


# from PyQt4 import QtCore, QtGui
# from PyQt4.QtCore import Qt
# from PyQt4.QtTest import QTest

from anima.pipeline.ui import login_dialog, IS_PYSIDE, IS_PYQT4

if IS_PYSIDE:
    from PySide import QtCore, QtGui
    from PySide.QtTest import QTest
    from PySide.QtCore import Qt
elif IS_PYQT4:
    import sip

    sip.setapi('QString', 2)
    sip.setapi('QVariant', 2)
    from PyQt4 import QtCore, QtGui
    from PyQt4.QtTest import QTest
    from PySide.QtCore import Qt

from stalker import db, defaults, User, Project, Repository, Structure, Status, StatusList, Task, Version
from stalker.db.session import DBSession
from stalker.models.env import EnvironmentBase

from anima.pipeline.ui import version_creator

logger = logging.getLogger("anima.pipeline.ui.version_creator")
logger.setLevel(logging.DEBUG)


# exceptions for test purposes
from zope.sqlalchemy import ZopeTransactionExtension


class ExportAs(Exception):
    pass


class TestEnvironment(EnvironmentBase):
    """A test environment which just raises errors to check if the correct
    method has been called
    """

    name = "TestEnv"

    test_data = {
        "export_as": {"call count": 0, "data": None},
        "save_as": {"call count": 0, "data": None},
        "open_": {"call count": 0, "data": None},
        "reference": {"call count": 0, "data": None},
        "import_": {"call count": 0, "data": None},
    }

    def export_as(self, version):
        self.test_data["export_as"]["call count"] += 1
        self.test_data["export_as"]["data"] = version

    def save_as(self, version):
        self.test_data["save_as"]["call count"] += 1
        self.test_data["save_as"]["data"] = version

    def open_(self, version, force=False):
        self.test_data["open_"]["call count"] += 1
        self.test_data["open_"]["data"] = version

    def reference(self, version):
        self.test_data["reference"]["call count"] += 1
        self.test_data["reference"]["data"] = version

    def import_(self, version):
        self.test_data["import_"]["call count"] += 1
        self.test_data["import_"]["data"] = version

    def get_last_version(self):
        """mock version of the original this returns None all the time
        """
        return None


class VersionCreatorTester(unittest2.TestCase):
    """Tests the Version Creator instance
    """

    @classmethod
    def setUpClass(cls):
        """setup once
        """
        # remove the transaction manager
        DBSession.remove()
        DBSession.configure(extension=None)

    @classmethod
    def tearDownClass(cls):
        """teardown once
        """
        # configure with transaction manager
        DBSession.remove()
        DBSession.configure(
            extension=ZopeTransactionExtension()
        )

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
        """setup the test
        """
        # -----------------------------------------------------------------
        # start of the setUp

        defaults.local_storage_path = tempfile.mktemp()

        db.setup({'sqlalchemy.url': 'sqlite:///:memory:',
                  'sqlalchemy.echo': 'false'})

        # create the environment variable and point it to a temp directory
        # self.temp_config_folder = tempfile.mkdtemp()
        # self.temp_projects_folder = tempfile.mkdtemp()

        # os.environ["STALKER_PATH"] = self.temp_config_folder

        # for PyQt4
        self.app = QtGui.QApplication(sys.argv)

    def tearDown(self):
        """cleans the test environment
        """
        shutil.rmtree(
            defaults.local_storage_path,
            True
        )

        # shutil.rmtree(
        #     self.temp_config_folder,
        #     self.temp_projects_folder
        # )

    def test_close_button_closes_ui(self):
        """testing if the close button is closing the ui
        """
        dialog = version_creator.MainDialog()
        dialog.show()

        self.assertEqual(dialog.isVisible(), True)

        # now run the UI
        QTest.mouseClick(dialog.close_pushButton, Qt.LeftButton)
        self.assertEqual(dialog.isVisible(), False)

    def test_no_projects_no_problem(self):
        """testing if there will be no problem to open the ui without a project
        instance
        """
        dialog = version_creator.MainDialog()

    def test_login_dialog_is_shown_if_there_are_no_logged_in_user(self):
        """testing if the login dialog is shown if there is no logged in user
        """
        # dialog = version_creator.MainDialog()
        #QtCore.QTimer.singleShot(0, dialog.current_dialog, QtCore.SLOT('accept()'))
        # self.show_dialog(dialog)
        # TODO: this part is still not clear in my mind
        self.fail('test is not implemented yet')

    def test_logged_in_user_field_is_updated_correctly(self):
        """testing if the logged_in_user field is updated correctly
        """
        # create a LocalSession first
        admin = User.query.all()[0]
        lsession = LocalSession()
        lsession.store_user(admin)
        lsession.save()

        dialog = version_creator.MainDialog()

        # now expect to see the admin.name on the dialog.logged_in_user_label
        self.assertEqual(
            dialog.logged_in_user_label.text(),
            admin.name
        )

    def test_logout_button_shows_the_login_dialog(self):
        """logout dialog shows the login_dialog
        """
        # create a LocalSession first
        admin = User.query.all()[0]
        lsession = LocalSession()
        lsession.store_user(admin)
        lsession.save()

        dialog = version_creator.MainDialog()
        # self.show_dialog(dialog)

        # clicker = QtCore.QThread()
        # 
        # # setup a thread to click to the logout button
        # def click_on_logout():
        #     """a helper function to click on the button
        #     """
        #     # now click the logout button
        #     QTest.mouseClick(
        #         dialog.logout_pushButton,
        #         QtCore.Qt.LeftButton
        #     )
        # 
        # 
        # QtCore.QObject.connect(
        #     clicker,
        #     QtCore.SIGNAL('started()'),
        #     click_on_logout
        # )
        # 
        # # QtCore.QObject.connect(
        # #     dialog.logout_pushButton,
        # #     QtCore.SIGNAL('clicked()'),
        # #     clicker.quit
        # # )
        # 
        # # start the thread
        # clicker.start()
        # 
        # # register a QTimer to quit the thread
        # QtCore.QTimer.singleShot(
        #     1000,
        #     clicker,
        #     'exit()'
        # )
        # 
        # # wait the thread to finish
        # clicker.wait()
        # 
        # dialog_is_shown = False
        # print dialog.current_dialog
        # # expect to have the login_dialog to be shown
        # if dialog.current_dialog:
        #     dialog_is_shown = True
        #     self.assertIsInstance(
        #         dialog.current_dialog,
        #         login_dialog.MainDialog
        #     )

    def test_tasks_treeWidget_is_filled_with_projects(self):
        """testing if the tasks_treeWidget is filled with projects as root
        level items
        """
        # create local session
        admin = User.query.all()[0]
        local_session = LocalSession()
        local_session.store_user(admin)
        local_session.save()

        # create a repository
        repo1 = Repository(
            name='Test Repository',
            windows_path='T;/TestRepo/',
            linux_path='/mnt/T/TestRepo/',
            osx_path='/Volumes/T/TestRepo/'
        )

        structure1 = Structure(
            name='Test Project Structure',
            templates=[],
            custom_template=''
        )

        status1 = Status(
            name='Waiting To Start',
            code='WTS'
        )

        status2 = Status(
            name='Work In Progress',
            code='WIP'
        )

        status3 = Status(
            name='Completed',
            code='CMPL'
        )

        project_status_list = StatusList(
            name='Project Statuses',
            statuses=[status1, status2, status3],
            target_entity_type=Project
        )

        # create a couple of projects
        p1 = Project(
            name='Project 1',
            code='P1',
            repository=repo1,
            structure=structure1,
            status_list=project_status_list
        )

        p2 = Project(
            name='Project 2',
            code='P2',
            repository=repo1,
            structure=structure1,
            status_list=project_status_list
        )

        p3 = Project(
            name='Project 3',
            code='P3',
            repository=repo1,
            structure=structure1,
            status_list=project_status_list
        )

        projects = [p1, p2, p3]

        # create tasks for admin user
        task_status_list = StatusList(
            name='Task Statuses',
            statuses=[status1, status2, status3],
            target_entity_type=Task
        )

        # project 1

        t1 = Task(
            name='Test Task 1',
            project=p1,
            resources=[admin],
            status_list=task_status_list
        )

        t2 = Task(
            name='Test Task 2',
            project=p1,
            resources=[admin],
            status_list=task_status_list
        )

        t3 = Task(
            name='Test Task 2',
            project=p1,
            resources=[admin],
            status_list=task_status_list
        )

        # project 2
        t4 = Task(
            name='Test Task 4',
            project=p2,
            resources=[admin],
            status_list=task_status_list
        )

        t5 = Task(
            name='Test Task 5',
            project=p2,
            resources=[admin],
            status_list=task_status_list
        )

        # no tasks for project 3

        # record them all to the db
        DBSession.add_all([admin, p1, p2, p3, t1, t2, t3, t4, t5])
        DBSession.commit()

        # now call the dialog and expect to see all these projects as root
        # level items in tasks_treeWidget

        dialog = version_creator.MainDialog()
        # self.show_dialog(dialog)

        self.assertEqual(
            len(admin.tasks),
            5
        )

        self.assertEqual(
            dialog.tasks_treeWidget.topLevelItemCount(),
            2
        )

        for i in range(dialog.tasks_treeWidget.topLevelItemCount()):
            item = dialog.tasks_treeWidget.topLevelItem(i)
            self.assertEqual(
                projects[i].name,
                item.text(0)
            )

            self.assertEqual(
                projects[i].entity_type,
                item.text(1)
            )

    def test_takes_listWidget_lists_Main_by_default(self):
        """testing if the takes_listWidget lists "Main" by default
        """
        # create local session
        admin = User.query.all()[0]
        local_session = LocalSession()
        local_session.store_user(admin)
        local_session.save()

        dialog = version_creator.MainDialog()
        self.assertEqual(
            defaults.version_take_name,
            dialog.takes_listWidget.currentItem().text()
        )

    def test_takes_listWidget_lists_Main_by_default_for_tasks_with_no_versions(self):
        """testing if the takes_listWidget lists "Main" by default for a task
        with no version
        """
        # create local session
        admin = User.query.all()[0]
        local_session = LocalSession()
        local_session.store_user(admin)
        local_session.save()

        # create a repository
        repo1 = Repository(
            name='Test Repository',
            windows_path='T;/TestRepo/',
            linux_path='/mnt/T/TestRepo/',
            osx_path='/Volumes/T/TestRepo/'
        )

        structure1 = Structure(
            name='Test Project Structure',
            templates=[],
            custom_template=''
        )

        status1 = Status(
            name='Waiting To Start',
            code='WTS'
        )

        status2 = Status(
            name='Work In Progress',
            code='WIP'
        )

        status3 = Status(
            name='Completed',
            code='CMPL'
        )

        project_status_list = StatusList(
            name='Project Statuses',
            statuses=[status1, status2, status3],
            target_entity_type=Project
        )

        # create a couple of projects
        p1 = Project(
            name='Project 1',
            code='P1',
            repository=repo1,
            structure=structure1,
            status_list=project_status_list
        )

        p2 = Project(
            name='Project 2',
            code='P2',
            repository=repo1,
            structure=structure1,
            status_list=project_status_list
        )

        p3 = Project(
            name='Project 3',
            code='P3',
            repository=repo1,
            structure=structure1,
            status_list=project_status_list
        )

        projects = [p1, p2, p3]

        # create tasks for admin user
        task_status_list = StatusList(
            name='Task Statuses',
            statuses=[status1, status2, status3],
            target_entity_type=Task
        )

        # project 1
        t1 = Task(
            name='Test Task 1',
            project=p1,
            resources=[admin],
            status_list=task_status_list
        )

        t2 = Task(
            name='Test Task 2',
            project=p1,
            resources=[admin],
            status_list=task_status_list
        )

        t3 = Task(
            name='Test Task 2',
            project=p1,
            resources=[admin],
            status_list=task_status_list
        )

        # project 2
        t4 = Task(
            name='Test Task 4',
            project=p2,
            resources=[admin],
            status_list=task_status_list
        )

        t5 = Task(
            name='Test Task 5',
            project=p2,
            resources=[admin],
            status_list=task_status_list
        )

        # no tasks for project 3

        # record them all to the db
        DBSession.add_all([admin, p1, p2, p3, t1, t2, t3, t4, t5])
        DBSession.commit()

        # now call the dialog and expect to see all these projects as root
        # level items in tasks_treeWidget

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
        # create local session
        admin = User.query.all()[0]
        local_session = LocalSession()
        local_session.store_user(admin)
        local_session.save()

        # create a repository
        repo1 = Repository(
            name='Test Repository',
            windows_path='T;/TestRepo/',
            linux_path='/mnt/T/TestRepo/',
            osx_path='/Volumes/T/TestRepo/'
        )

        structure1 = Structure(
            name='Test Project Structure',
            templates=[],
            custom_template=''
        )

        status1 = Status(
            name='Waiting To Start',
            code='WTS'
        )

        status2 = Status(
            name='Work In Progress',
            code='WIP'
        )

        status3 = Status(
            name='Completed',
            code='CMPL'
        )

        project_status_list = StatusList(
            name='Project Statuses',
            statuses=[status1, status2, status3],
            target_entity_type=Project
        )

        # create a couple of projects
        p1 = Project(
            name='Project 1',
            code='P1',
            repository=repo1,
            structure=structure1,
            status_list=project_status_list
        )

        p2 = Project(
            name='Project 2',
            code='P2',
            repository=repo1,
            structure=structure1,
            status_list=project_status_list
        )

        p3 = Project(
            name='Project 3',
            code='P3',
            repository=repo1,
            structure=structure1,
            status_list=project_status_list
        )

        projects = [p1, p2, p3]

        # create tasks for admin user
        task_status_list = StatusList(
            name='Task Statuses',
            statuses=[status1, status2, status3],
            target_entity_type=Task
        )

        # create no tasks

        # record them all to the db
        DBSession.add_all([admin, p1, p2, p3])
        DBSession.commit()

        # now call the dialog and expect to see all these projects as root
        # level items in tasks_treeWidget

        dialog = version_creator.MainDialog()
        # self.show_dialog(dialog)
        
        self.assertEqual(
            defaults.version_take_name,
            dialog.takes_listWidget.currentItem().text()
        )
    def test_takes_listWidget_lists_all_the_takes_of_the_current_task_versions(self):
        """testing if the takes_listWidget lists all the takes of the current
        task versions
        """
        # create local session
        admin = User.query.all()[0]
        local_session = LocalSession()
        local_session.store_user(admin)
        local_session.save()

        # create a repository
        repo1 = Repository(
            name='Test Repository',
            windows_path='T;/TestRepo/',
            linux_path='/mnt/T/TestRepo/',
            osx_path='/Volumes/T/TestRepo/'
        )

        structure1 = Structure(
            name='Test Project Structure',
            templates=[],
            custom_template=''
        )

        status1 = Status(
            name='Waiting To Start',
            code='WTS'
        )

        status2 = Status(
            name='Work In Progress',
            code='WIP'
        )

        status3 = Status(
            name='Completed',
            code='CMPL'
        )

        project_status_list = StatusList(
            name='Project Statuses',
            statuses=[status1, status2, status3],
            target_entity_type=Project
        )

        # create a couple of projects
        p1 = Project(
            name='Project 1',
            code='P1',
            repository=repo1,
            structure=structure1,
            status_list=project_status_list
        )

        p2 = Project(
            name='Project 2',
            code='P2',
            repository=repo1,
            structure=structure1,
            status_list=project_status_list
        )

        p3 = Project(
            name='Project 3',
            code='P3',
            repository=repo1,
            structure=structure1,
            status_list=project_status_list
        )

        projects = [p1, p2, p3]

        # create tasks for admin user
        task_status_list = StatusList(
            name='Task Statuses',
            statuses=[status1, status2, status3],
            target_entity_type=Task
        )

        # project 1
        t1 = Task(
            name='Test Task 1',
            project=p1,
            resources=[admin],
            status_list=task_status_list
        )

        t2 = Task(
            name='Test Task 2',
            project=p1,
            resources=[admin],
            status_list=task_status_list
        )

        t3 = Task(
            name='Test Task 3',
            project=p1,
            resources=[admin],
            status_list=task_status_list
        )

        # project 2
        t4 = Task(
            name='Test Task 4',
            project=p2,
            resources=[admin],
            status_list=task_status_list
        )

        t5 = Task(
            name='Test Task 5',
            project=p2,
            resources=[admin],
            status_list=task_status_list
        )

        # no tasks for project 3
        
        # versions
        version_status_list = StatusList(
            name='Verson Statuses',
            statuses=[status1, status2, status3],
            target_entity_type=Version
        )
        
        # record them all to the db
        DBSession.add_all([admin, p1, p2, p3, t1, t2, t3, t4, t5,
                           version_status_list])
        DBSession.commit()

        # task 1
        
        # default (Main)
        v1 = Version(version_of=t1, full_path='/some/path')
        DBSession.add(v1)
        DBSession.commit()
        
        v2 = Version(version_of=t1, full_path='/some/path')
        DBSession.add(v2)
        DBSession.commit()

        v3 = Version(version_of=t1, full_path='/some/path')
        DBSession.add(v3)
        DBSession.commit()

        # Take1
        v4 = Version(version_of=t1, take_name='Take1', full_path='/some/path')
        DBSession.add(v4)
        DBSession.commit()

        v5 = Version(version_of=t1, take_name='Take1', full_path='/some/path')
        DBSession.add(v5)
        DBSession.commit()

        v6 = Version(version_of=t1, take_name='Take1', full_path='/some/path')
        DBSession.add(v6)
        DBSession.commit()

        # Take2
        v7 = Version(version_of=t1, take_name='Take2', full_path='/some/path')
        DBSession.add(v7)
        DBSession.commit()

        v8 = Version(version_of=t1, take_name='Take2', full_path='/some/path')
        DBSession.add(v8)
        DBSession.commit()

        v9 = Version(version_of=t1, take_name='Take2', full_path='/some/path')
        DBSession.add(v9)
        DBSession.commit()

        # now call the dialog and expect to see all these projects as root
        # level items in tasks_treeWidget

        dialog = version_creator.MainDialog()
        # self.show_dialog(dialog)

        # set the current item to task1
        # get the corresponding item
        items = dialog.tasks_treeWidget.findItems(
            p1.name,
            QtCore.Qt.MatchExactly,
            0
        )
        self.assertGreater(len(items), 0)
        p1_item = items[0]
        self.assertIsNotNone(p1_item)
        
        # get task1
        t1_item = None
        for i in range(p1_item.childCount()):
            item = p1_item.child(i)
            if item.text(0) == t1.name:
                t1_item = item
                break
        self.assertIsNotNone(t1_item)
        
        dialog.tasks_treeWidget.setCurrentItem(item)
        
        # now check if the takes_listWidget lists all the takes of the
        # t1 versions
        takes = ['Main', 'Take1', 'Take2']
        self.assertEqual(
            dialog.takes_listWidget.count(),
            3
        )
        
        self.assertTrue(
            dialog.takes_listWidget.item(0).text(),
            'Main'
        )
        
        self.assertTrue(
            dialog.takes_listWidget.item(1).text(),
            'Take1'
        )
        
        self.assertTrue(
            dialog.takes_listWidget.item(2).text(),
            'Take2'
        )
