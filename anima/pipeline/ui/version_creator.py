# -*- coding: utf-8 -*-
# Copyright (c) 2012-2013, Anima Istanbul
#
# This module is part of anima-tools and is released under the BSD 2
# License: http://www.opensource.org/licenses/BSD-2-Clause

import logging
import datetime
import os
import re
from sqlalchemy import distinct
from stalker.db import DBSession
from stalker import (db, defaults, Version, StatusList, Project,
                     Task, LocalSession, EnvironmentBase)

import anima
from anima.pipeline import utils
from anima.pipeline.ui import utils as ui_utils
from anima.pipeline.ui import IS_PYSIDE, IS_PYQT4, login_dialog, version_updater
from anima.pipeline.ui.lib import QtGui, QtCore
from anima.pipeline.ui.utils import UICaller, AnimaDialogBase

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

if IS_PYSIDE():
    from anima.pipeline.ui.ui_compiled import version_creator_UI_pyside as version_creator_UI
elif IS_PYQT4():
    from anima.pipeline.ui.ui_compiled import version_creator_UI_pyqt4 as version_creator_UI


class TaskItem(QtGui.QStandardItem):
    """Implements the Task as a QStandardItem
    """
    def __init__(self, *args, **kwargs):
        QtGui.QStandardItem.__init__(self, *args, **kwargs)
        self.loaded = False
        self.task = None
        self.parent = None
        self.fetched_all = False
        self.setEditable(False)

    def clone(self):
        """returns a copy of this item
        """
        new_item = TaskItem()
        new_item.task = self.task
        new_item.parent = self.parent
        new_item.fetched_all = self.fetched_all
        return new_item

    def fetchMore(self):
        """
        """
        if self.task and not self.fetched_all:
            tasks = []
            if isinstance(self.task, Task):
                tasks = self.task.children
            elif isinstance(self.task, Project):
                tasks = self.task.root_tasks

            model = self.model()
            if model.user_tasks_only:
                user_tasks_and_parents = []
                # need to filter tasks which do not belong to user
                for task in tasks:
                    for user_task in model.user.tasks:
                        if task in user_task.parents or task is user_task:
                            user_tasks_and_parents.append(task)
                            break

                tasks = user_tasks_and_parents

            for task in tasks:
                task_item = TaskItem()
                task_item.parent = self
                task_item.task = task
                
                # set the font
                # task_item.setText(0, entity.name)
                # task_item.setText(1, entity.entity_type)
                task_item.setText(task.name)
                
                if task.is_container:
                    my_font = task_item.font()
                    my_font.setBold(True)
                    task_item.setFont(my_font)
                
                self.appendRow(task_item)

            self.fetched_all = True

    def hasChildren(self):
        if self.task:
            if isinstance(self.task, Task):
                return self.task.is_container
            elif isinstance(self.task, Project):
                return bool(len(self.task.root_tasks))
        else:
            return False


class TaskTreeModel(QtGui.QStandardItemModel):
    """Implements the model view for the task hierarchy
    """
    def __init__(self, *args, **kwargs):
        QtGui.QStandardItemModel.__init__(self, *args, **kwargs)
        self.user = None
        self.root = None
        self.user_tasks_only = False

    def populateTree(self):
        """populates tree with user projects
        """
        self.setColumnCount(3)
        self.setHorizontalHeaderLabels(
            ['Name', 'Type', 'Dependencies']
        )

        item_prototype = TaskItem()
        self.setItemPrototype(item_prototype)

        self.root = self.invisibleRootItem()
        self.root.fetched_all = False

    def canFetchMore(self, index):
        logger.debug('canFetchMore is running for index: %s' % index)
        if not index.isValid():
            logger.debug('index is not valid')
            if hasattr(self.root, 'fetched_all'):
                return not self.root.fetched_all
            else:
                return False
        else:
            item = self.itemFromIndex(index)
            return item.hasChildren()

    def fetchMore(self, index):
        """fetches more elements
        """
        logger.debug('fetchMore is running for index: %s' % index)
        if not index.isValid():
            # it is the root
            # return the projects
            projects = self.user.projects
            for project in projects:
                project_item = TaskItem()
                project_item.parent = self.root
                # project_item.setColumnCount(3)
                project_item.setText(project.name)

                project_item.task = project
                
                # set the font
                # project_item.setText(0, entity.name)
                # project_item.setText(1, entity.entity_type)
                project_item.setText(project.name)
                my_font = project_item.font()
                my_font.setBold(True)
                project_item.setFont(my_font)

                self.root.appendRow(project_item)
            self.root.fetched_all = True
        else:
            item = self.itemFromIndex(index)
            item.fetchMore()

    def hasChildren(self, index):
        """returns True or False depending on to the index and the item on the
        index
        """
        if not index.isValid():
            projects = self.user.projects
            return bool(len(projects) > 0)
        else:
            item = self.itemFromIndex(index)
            return (item.hasChildren())



def UI(environment=None, mode=0, app_in=None, executor=None):
    """
    :param environment: The
      :class:`~stalker.models.env.EnvironmentBase` can be None to let the UI to
      work in "environmentless" mode in which it only creates data in database
      and copies the resultant version file path to clipboard.
    
    :param mode: Runs the UI either in Read-Write (0) mode or in Read-Only (1)
      mode.

    :param app_in: A Qt Application instance, which you can pass to let the UI
      be attached to the given applications event process.
    
    :param executor: Instead of calling app.exec_ the UI will call this given
      function. It also passes the created app instance to this executor.
    
    """
    return UICaller(app_in, executor, MainDialog, environment=environment,
                    mode=mode)


class MainDialog(QtGui.QDialog, version_creator_UI.Ui_Dialog, AnimaDialogBase):
    """The main version creation dialog for the pipeline.

    This is the main interface that the users of the anima.pipeline will use
    to create a new :class:`~stalker.models.version.Version`\ s.

    It is possible to run the version_creator UI in read-only mode where the UI
    is created only for choosing previous versions. There will only be one
    button called "Choose" which returns the chosen Version instance.

    :param environment: It is an object which supplies **methods** like
      ``open``, ``save``, ``export``,  ``import`` or ``reference``. The most
      basic way to do this is to pass an instance of a class which is derived
      from the :class:`~stalker.models.env.EnvironmentBase` which has all this
      methods but produces ``NotImplementedError``\ s if the child class has
      not implemented these actions.

      The main duty of the Environment object is to introduce the host
      application (Maya, Houdini, Nuke, etc.) to the pipeline scripts and let
      it to open, save, export, import or reference a version file.

    **No Environment Interaction**

      The UI is able to handle the situation of not being bounded to an
      Environment. So if there is no Environment instance is given then the UI
      generates new Version instance and will allow the user to "copy" the full
      path of the newly generated Version. So environments which are not able
      to run Python code (Photoshop, ZBrush etc.) will also be able to
      contribute to projects.

    :param parent: The parent ``PySide.QtCore.QObject`` of this interface. It
      is mainly useful if this interface is going to be attached to a parent
      UI, like the Maya or Nuke.

    :param mode: Sets the UI in to Read-Write (mode=0) and Read-Only (mode=1)
      mode. Where in Read-Write there are all the buttons you would normally
      have (Export As, Save As, Open, Reference, Import), and in Read-Only mode
      it has only one button called "Choose" which lets you choose one Version.
    """

    def __init__(self, environment=None, parent=None, mode=0):
        logger.debug("initializing the interface")

        super(MainDialog, self).__init__(parent)
        self.setupUi(self)

        self.mode = mode
        self.chosen_version = None

        window_title = 'Version Creator | ' + \
                       'Anima Pipeline v' + anima.__version__

        if environment:
            window_title += " | " + environment.name
        else:
            window_title += " | No Environment"

        if self.mode:
            window_title += " | Read-Only Mode"
        else:
            window_title += " | Normal Mode"

        # change the window title
        self.setWindowTitle(window_title)

        # setup the database
        if DBSession is None:
            db.setup()

        self.environment = environment

        # create the project attribute in projects_comboBox
        self.current_dialog = None
        self.previous_versions_tableWidget.versions = []

        # set previous_versions_tableWidget.labels
        self.previous_versions_tableWidget.labels = [
            '#',
            'P',
            'User',
            'Size',
            'Date',
            'Description',
            #"Path"
        ]
        self.previous_versions_tableWidget.setColumnCount(
            len(self.previous_versions_tableWidget.labels)
        )

        # setup signals
        self._setup_signals()

        # setup defaults
        self._set_defaults()

        # center window
        self.center_window()

        logger.debug("finished initializing the interface")

    def show(self):
        """overridden show method
        """
        logged_in_user = self.get_logged_in_user()
        if not logged_in_user:
            self.close()
            return None
        else:
            return super(MainDialog, self).show()

    def _setup_signals(self):
        """sets up the signals
        """
        logger.debug("start setting up interface signals")

        # close button
        QtCore.QObject.connect(
            self.close_pushButton,
            QtCore.SIGNAL("clicked()"),
            self.close
        )

        #logout button
        QtCore.QObject.connect(
            self.logout_pushButton,
            QtCore.SIGNAL("clicked()"),
            self.logout
        )

        # my_tasks_only_checkBox
        QtCore.QObject.connect(
            self.my_tasks_only_checkBox,
            QtCore.SIGNAL("stateChanged(int)"),
            self.fill_tasks_treeView
        )

        # fit column 0 on expand/collapse
        QtCore.QObject.connect(
            self.tasks_treeView,
            QtCore.SIGNAL('expanded(QModelIndex)'),
            self.tasks_treeView_auto_fit_column
        )

        QtCore.QObject.connect(
            self.tasks_treeView,
            QtCore.SIGNAL('collapsed(QModelIndex)'),
            self.tasks_treeView_auto_fit_column
        )

        # takes_listWidget
        QtCore.QObject.connect(
            self.takes_listWidget,
            QtCore.SIGNAL("currentTextChanged(QString)"),
            self.takes_listWidget_changed
        )

        # takes_listWidget
        QtCore.QObject.connect(
            self.takes_listWidget,
            QtCore.SIGNAL("currentItemChanged(QListWidgetItem *, QListWidgetItem *)"),
            self.takes_listWidget_changed
        )

        # find_from_path_lineEdit
        QtCore.QObject.connect(
            self.find_from_path_pushButton,
            QtCore.SIGNAL('clicked()'),
            self.find_from_path_pushButton_clicked
        )

        # custom context menu for the tasks_treeView
        self.tasks_treeView.setContextMenuPolicy(
            QtCore.Qt.CustomContextMenu
        )

        QtCore.QObject.connect(
            self.tasks_treeView,
            QtCore.SIGNAL("customContextMenuRequested(const QPoint&)"),
            self._show_tasks_treeView_context_menu
        )

        # custom context menu for the previous_versions_tableWidget
        self.previous_versions_tableWidget.setContextMenuPolicy(
            QtCore.Qt.CustomContextMenu
        )

        QtCore.QObject.connect(
            self.previous_versions_tableWidget,
            QtCore.SIGNAL("customContextMenuRequested(const QPoint&)"),
            self._show_previous_versions_tableWidget_context_menu
        )

        # add_take_toolButton
        QtCore.QObject.connect(
            self.add_take_toolButton,
            QtCore.SIGNAL("clicked()"),
            self.add_take_toolButton_clicked
        )

        # export_as
        QtCore.QObject.connect(
            self.export_as_pushButton,
            QtCore.SIGNAL("clicked()"),
            self.export_as_pushButton_clicked
        )

        # save_as
        QtCore.QObject.connect(
            self.save_as_pushButton,
            QtCore.SIGNAL("clicked()"),
            self.save_as_pushButton_clicked
        )

        # open
        QtCore.QObject.connect(
            self.open_pushButton,
            QtCore.SIGNAL("clicked()"),
            self.open_pushButton_clicked
        )

        # chose
        QtCore.QObject.connect(
            self.chose_pushButton,
            QtCore.SIGNAL("cliched()"),
            self.chose_pushButton_clicked
        )

        if self.mode:
            # Read-Only mode, Choose the version
            # add double clicking to previous_versions_tableWidget
            QtCore.QObject.connect(
                self.previous_versions_tableWidget,
                QtCore.SIGNAL("cellDoubleClicked(int,int)"),
                self.chose_pushButton_clicked
            )
        else:
            # Read-Write mode, Open the version
            # add double clicking to previous_versions_tableWidget
            QtCore.QObject.connect(
                self.previous_versions_tableWidget,
                QtCore.SIGNAL("cellDoubleClicked(int,int)"),
                self.open_pushButton_clicked
            )

        # reference
        QtCore.QObject.connect(
            self.reference_pushButton,
            QtCore.SIGNAL("clicked()"),
            self.reference_pushButton_clicked
        )

        # import
        QtCore.QObject.connect(
            self.import_pushButton,
            QtCore.SIGNAL("clicked()"),
            self.import_pushButton_clicked
        )

        # show_only_published_checkBox
        QtCore.QObject.connect(
            self.show_published_only_checkBox,
            QtCore.SIGNAL("stateChanged(int)"),
            self.update_previous_versions_tableWidget
        )

        # show_only_published_checkBox
        QtCore.QObject.connect(
            self.version_count_spinBox,
            QtCore.SIGNAL("valueChanged(int)"),
            self.update_previous_versions_tableWidget
        )

        # upload_thumbnail_pushButton
        QtCore.QObject.connect(
            self.upload_thumbnail_pushButton,
            QtCore.SIGNAL("clicked()"),
            self.upload_thumbnail_pushButton_clicked
        )

        logger.debug("finished setting up interface signals")
    

    def get_logged_in_user(self):
        """returns the logged in user
        """
        local_session = LocalSession()
        logged_in_user = local_session.logged_in_user
        if not logged_in_user:
            dialog = login_dialog.MainDialog(parent=self)
            self.current_dialog = dialog
            dialog.exec_()
            logger.debug("dialog.DialogCode: %s" % dialog.DialogCode)
            if dialog.DialogCode == QtGui.QDialog.DialogCode.Accepted: #Accepted (1) or Rejected (0)
                local_session = LocalSession()
                logged_in_user = local_session.logged_in_user
                self.current_dialog = None
            else:
                # close the ui
                #logged_in_user = self.get_logged_in_user()
                logger.debug("no logged in user")
                self.close()

        return logged_in_user

    def fill_logged_in_user(self):
        """fills the logged in user label
        """
        logged_in_user = self.get_logged_in_user()
        if logged_in_user:
            self.logged_in_user_label.setText(logged_in_user.name)

    def logout(self):
        """log the current user out
        """
        lsession = LocalSession()
        lsession.delete()
        self.close()

    def _show_previous_versions_tableWidget_context_menu(self, position):
        """the custom context menu for the previous_versions_tableWidget
        """
        # convert the position to global screen position
        global_position = \
            self.previous_versions_tableWidget.mapToGlobal(position)

        item = self.previous_versions_tableWidget.itemAt(position)
        if not item:
            return

        index = item.row()
        version = self.previous_versions_tableWidget.versions[index]

        # create the menu
        menu = QtGui.QMenu()
        
        #change_status_menu = menu.addMenu('Change Status')
        #menu.addSeparator()

        logged_in_user = self.get_logged_in_user()
        
        if version.created_by == logged_in_user:
            if version.is_published:
                menu.addAction('Un-Publish')
            else:
                menu.addAction('Publish')
            menu.addSeparator()

        # add Browse Outputs
        menu.addAction("Browse Path...")
        menu.addAction("Copy Path")
        menu.addSeparator()

        if not self.mode:
            menu.addAction("Change Description...")
            menu.addSeparator()

        selected_item = menu.exec_(global_position)

        if selected_item:
            choice = selected_item.text()

            if version:
                if choice == "Publish":
                    # publish the selected version
                    # publish it
                    version.is_published = True
                    version.updated_by = logged_in_user
                    DBSession.add(version)
                    DBSession.commit()
                    # refresh the tableWidget
                    self.update_previous_versions_tableWidget()
                    return
                elif choice == "Un-Publish":
                    version.is_published = False
                    version.updated_by = logged_in_user
                    DBSession.add(version)
                    DBSession.commit()
                    # refresh the tableWidget
                    self.update_previous_versions_tableWidget()
                    return

            if choice == 'Browse Path...':
                path = os.path.expandvars(version.absolute_full_path)
                try:
                    utils.open_browser_in_location(path)
                except IOError:
                    QtGui.QMessageBox.critical(
                        self,
                        "Error",
                        "Path doesn't exists:\n" + path
                    )
            elif choice == 'Change Description...':
                if version:
                    # change the description
                    self.current_dialog = QtGui.QInputDialog(self)

                    new_description, ok = self.current_dialog.getText(
                        self,
                        "Enter the new description",
                        "Please enter the new description:",
                        QtGui.QLineEdit.Normal,
                        version.description
                    )

                    if ok:
                        # change the description of the version
                        version.description = new_description

                        DBSession.add(version)
                        DBSession.commit()

                        # update the previous_versions_tableWidget
                        self.update_previous_versions_tableWidget()
            elif choice == 'Copy Path':
                # just set the clipboard to the version.absolute_full_path
                clipboard = QtGui.QApplication.clipboard()
                clipboard.setText(os.path.normpath(version.absolute_full_path))

    def _show_tasks_treeView_context_menu(self, position):
        """the custom context menu for the tasks_treeView
        """
        # convert the position to global screen position
        global_position = \
            self.tasks_treeView.mapToGlobal(position)

        index = self.tasks_treeView.indexAt(position)
        model = self.tasks_treeView.model()
        item = model.itemFromIndex(index)
        logger.debug('itemAt(position) : %s' % item)

        if not item:
            return

        task = item.task

        # create the menu
        menu = QtGui.QMenu()

        # Add Depends To menu
        depends = task.depends
        if depends:
            depends_to_menu = menu.addMenu('Depends To')

            for dTask in depends:
                action = depends_to_menu.addAction(dTask.name)
                action.task = dTask

        # Add Dependent Of Menu
        dependent_of = task.dependent_of
        if dependent_of:
            dependent_of_menu = menu.addMenu('Dependent Of')

            for dTask in dependent_of:
                action = dependent_of_menu.addAction(dTask.name)
                action.task = dTask

        selected_item = menu.exec_(global_position)

        if selected_item:
            choice = selected_item.text()
            task = selected_item.task
            self.find_and_select_entity_item_in_treeView(
                task,
                self.tasks_treeView
            )

    def find_entity_item_in_tree_view(self, entity, treeView):
        """finds the item related to the stalker entity in the given
        QtTreeView
        """
        model = treeView.model()
        indexes = model.match(
            # 0, 0, entity.name, QtCore.Qt.MatchExactly, QtCore.Qt.MatchRecursive
            model.index(0, 0),
            0,
            entity.name,
            2,
            QtCore.Qt.MatchRecursive
        )

        logger.debug('items matching name : %s' % indexes)
        for index in indexes:
            item = model.itemFromIndex(index)
            if item:
                if item.task == entity:
                    return item

        return None

    def clear_tasks_treeView(self):
        """clears the tasks_treeView items and also removes the connection
        between Stalker entities and ui items
        """
        pass

    def fill_tasks_treeView(self):
        """sets up the tasks_treeView
        """
        logged_in_user = self.get_logged_in_user()

        task_tree_model = TaskTreeModel()
        task_tree_model.user_tasks_only = self.my_tasks_only_checkBox.isChecked()
        self.tasks_treeView.setModel(task_tree_model)

        task_tree_model.user = logged_in_user
        task_tree_model.populateTree()

        # tasks_treeView
        QtCore.QObject.connect(
            self.tasks_treeView.selectionModel(),
            QtCore.SIGNAL(
                'selectionChanged(const QItemSelection &, const QItemSelection &)'),
            self.tasks_treeView_changed
        )

    def tasks_treeView_auto_fit_column(self):
        """fits columns to content
        """
        self.tasks_treeView.resizeColumnToContents(0)

    def tasks_treeView_changed(self):
        """runs when the tasks_treeView item is changed
        """
        logger.debug('tasks_treeView_changed running')
        task = self.get_task()
        logger.debug('task : %s' % task)

        # update the thumbnail
        # TODO: do it in another thread
        self.clear_thumbnail()
        self.update_thumbnail()

        # get the versions of the entity
        takes = []

        if task:
            # clear the takes_listWidget and fill with new data
            logger.debug('clear takes widget')
            self.takes_listWidget.clear()

            if isinstance(task, Project):
                return

            takes = map(
                lambda x: x[0],
                DBSession.query(distinct(Version.take_name))
                .filter(Version.task == task)
                .all()
            )

        logger.debug("len(takes) from db: %s" % len(takes))
        
        if defaults.version_take_name not in takes:
            takes.append(defaults.version_take_name)

        if len(takes) == 0:
            # append the default take
            logger.debug("appending the default take name")
            self.takes_listWidget.addItem(defaults.version_take_name)
        else:
            logger.debug("adding the takes from db")
            self.takes_listWidget.addItems(takes)

        logger.debug("setting the first element selected")
        item = self.takes_listWidget.item(0)
        self.takes_listWidget.setCurrentItem(item)

    def project_changed(self):
        """updates the assets list_widget and sequences_comboBox for the 
        """
        logger.debug("project_comboBox has changed in the UI")

        project = self.get_current_project()
        if project:
            # update the client info
            self.client_name_label.setText(
                project.client.name if project.client else "N/A"
            )

        # call tabWidget_changed with the current index
        curr_tab_index = self.tabWidget.currentIndex()

        self.tabWidget_changed(curr_tab_index)


    def _set_defaults(self):
        """sets up the defaults for the interface
        """
        logger.debug("started setting up interface defaults")

        # before doing anything create a QSplitter for:
        #   tasks_groupBox
        #   new_version_groupBox
        #   previous_versions_groupBox
        # 
        # and add it under horizontalLayout_14

        splitter = QtGui.QSplitter()
        splitter.addWidget(self.tasks_groupBox)
        splitter.addWidget(self.new_version_groupBox)
        splitter.addWidget(self.previous_versions_groupBox)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 1)
        splitter.setStretchFactor(2, 2)
        self.horizontalLayout_14.addWidget(splitter)

        # disable update_paths_checkBox
        self.update_paths_checkBox.setVisible(False)

        # check login
        self.fill_logged_in_user()

        # clear the thumbnail area
        self.clear_thumbnail()

        # fill the tasks
        self.fill_tasks_treeView()
        self.tasks_treeView.setAutoExpandDelay(0)

        # add "Main" by default to the takes_listWidget
        self.takes_listWidget.addItem(defaults.version_take_name)
        # select it
        item = self.takes_listWidget.item(0)
        self.takes_listWidget.setCurrentItem(item)

        # run the project changed item for the first time
        # self.project_changed()

        if self.environment and isinstance(self.environment, EnvironmentBase):
            logger.debug("restoring the ui with the version from environment")

            # get the last version from the environment
            version_from_env = self.environment.get_last_version()

            logger.debug("version_from_env: %s" % version_from_env)

            self.restore_ui(version_from_env)
        else:
            # hide some buttons
            self.export_as_pushButton.setVisible(False)
            #self.open_pushButton.setVisible(False)
            self.reference_pushButton.setVisible(False)
            self.import_pushButton.setVisible(False)

        if self.mode:
            # run in read-only mode
            # hide buttons
            self.add_take_toolButton.setVisible(False)
            self.description_label.setVisible(False)
            self.description_textEdit.setVisible(False)
            self.publish_checkBox.setVisible(False)
            self.update_paths_checkBox.setVisible(False)
            self.export_as_pushButton.setVisible(False)
            self.save_as_pushButton.setVisible(False)
            self.open_pushButton.setVisible(False)
            self.reference_pushButton.setVisible(False)
            self.import_pushButton.setVisible(False)
            self.upload_thumbnail_pushButton.setVisible(False)
            self.user_label.setVisible(False)
            self.shot_info_update_pushButton.setVisible(False)
            self.frame_range_label.setVisible(False)
            self.handles_label.setVisible(False)
            self.start_frame_spinBox.setVisible(False)
            self.end_frame_spinBox.setVisible(False)
            self.handle_at_end_spinBox.setVisible(False)
            self.handle_at_start_spinBox.setVisible(False)
        else:
            self.chose_pushButton.setVisible(False)

        # update description field
        self.description_textEdit.setText('')

        logger.debug("finished setting up interface defaults")

    def restore_ui(self, version):
        """Restores the UI with the given Version instance
        
        :param version: :class:`~oyProjectManager.models.version.Version`
          instance
        """

        logger.debug("restoring ui with the given version: %s", version)

        # quit if version is None
        if version is None or not version.task.project.active:
            return

        # set the task
        task = version.task
        self.find_and_select_entity_item_in_treeView(task, self.tasks_treeView)

        # take_name
        take_name = version.take_name
        logger.debug('finding take with name: %s' % take_name)
        items = self.takes_listWidget.findItems(
            take_name,
            QtCore.Qt.MatchExactly
        )
        if not items:
            return

        self.takes_listWidget.setCurrentItem(items[0])

        # select the version in the previous version list
        index = -1
        for i, prev_version in enumerate(self.previous_versions_tableWidget.versions):
            prev_version = self.previous_versions_tableWidget.versions[i]
            if prev_version == version:
                index = i
                break

        logger.debug('current index: %s' % index)

        # select the row
        if index != -1:
            item = self.previous_versions_tableWidget.item(index, 0)
            logger.debug('item : %s' % item)
            self.previous_versions_tableWidget.setCurrentItem(item)

    def find_and_select_entity_item_in_treeView(self, task, treeView):
        """finds and selects the task in the given treeView item
        """
        item = self.find_entity_item_in_tree_view(task, treeView)
        # TODO: simplify this part
        if not item:
            # the item is not loaded to the UI yet
            # start loading its parents
            # start from the project
            item = self.find_entity_item_in_tree_view(task.project, treeView)

            if item:
                self.tasks_treeView.setExpanded(item.index(), True)

            if task.parents:
                # now starting from the most outer parent expand the tasks
                for parent in task.parents:
                    item = self.find_entity_item_in_tree_view(parent, treeView)

                    if item:
                        treeView.setExpanded(item.index(), True)

            # finally select the task
            item = self.find_entity_item_in_tree_view(task, treeView)

            if not item:
                # still no item
                return

        logger.debug('*******************************')
        logger.debug('item: %s' % item)

        self.tasks_treeView.selectionModel().select(
            item.index(), QtGui.QItemSelectionModel.ClearAndSelect
        )

    def takes_listWidget_changed(self, index):
        """runs when the takes_listWidget has changed
        """
        logger.debug('takes_listWidget_changed running')
        # update the previous_versions_tableWidget
        self.update_previous_versions_tableWidget()

    def clear_previous_versions_tableWidget(self):
        """clears the previous_versions_tableWidget properly
        """
        # clear the data
        self.previous_versions_tableWidget.clear()
        self.previous_versions_tableWidget.versions = []

        # reset the labels
        self.previous_versions_tableWidget.setHorizontalHeaderLabels(
            self.previous_versions_tableWidget.labels
        )

    def update_previous_versions_tableWidget(self):
        """updates the previous_versions_tableWidget
        """
        self.clear_previous_versions_tableWidget()

        task = self.get_task()
        if not task or not isinstance(task, Task):
            return

        # if version_type_name != '':
        #     logger.debug("version_type_name: %s" % version_type_name)
        #else:
        #    # delete the versions cache
        #    self.previous_versions_tableWidget.versions = []
        #    return

        # take name
        take_name = ""
        item = self.takes_listWidget.currentItem()
        if item:
            take_name = item.text()

        if take_name != '':
            logger.debug("take_name: %s" % take_name)
        else:
            return

        # query the Versions of this type and take
        query = Version.query \
            .filter(Version.task == task) \
            .filter(Version.take_name == take_name)

        # get the published only
        if self.show_published_only_checkBox.isChecked():
            query = query.filter(Version.is_published == True)

        # show how many
        count = self.version_count_spinBox.value()

        versions = query.order_by(Version.version_number.desc()) \
            .limit(count).all()

        versions.reverse()

        # set the versions cache by adding them to the widget
        self.previous_versions_tableWidget.versions = versions

        self.previous_versions_tableWidget.setRowCount(len(versions))

        def set_font(item):
            """sets the font for the given item

            :param item: the a QTableWidgetItem
            """
            my_font = item.font()
            my_font.setBold(True)

            item.setFont(my_font)

            foreground = item.foreground()
            foreground.setColor(QtGui.QColor(0, 192, 0))
            item.setForeground(foreground)

        # update the previous versions list
        for i, version in enumerate(versions):

            is_published = version.is_published
            
            c = 0

            # ------------------------------------
            # version_number
            item = QtGui.QTableWidgetItem(str(version.version_number))
            # align to center and vertical center
            item.setTextAlignment(0x0004 | 0x0080)

            if is_published:
                set_font(item)

            self.previous_versions_tableWidget.setItem(i, c, item)
            c += 1
            # ------------------------------------

            # ------------------------------------
            # created_with
            item = QtGui.QTableWidgetItem()
            if version.created_with:
                item.setIcon(ui_utils.getIcon(version.created_with.lower()))

            if is_published:
                set_font(item)
            self.previous_versions_tableWidget.setItem(i, c, item)
            c += 1
            # ------------------------------------

            # ------------------------------------
            # user.name
            created_by = ''
            if version.created_by:
                created_by = version.created_by.name
            item = QtGui.QTableWidgetItem(created_by)
            # align to left and vertical center
            item.setTextAlignment(0x0001 | 0x0080)

            if is_published:
                set_font(item)

            self.previous_versions_tableWidget.setItem(i, c, item)
            c += 1
            # ------------------------------------

            # ------------------------------------
            # filesize

            # get the file size
            #file_size_format = "%.2f MB"
            file_size = -1
            if os.path.exists(version.absolute_full_path):
                file_size = float(
                    os.path.getsize(version.absolute_full_path)) / 1024 / 1024

            item = QtGui.QTableWidgetItem(
                defaults.file_size_format % file_size)
            # align to left and vertical center
            item.setTextAlignment(0x0001 | 0x0080)

            if is_published:
                set_font(item)

            self.previous_versions_tableWidget.setItem(i, c, item)
            c += 1
            # ------------------------------------

            # ------------------------------------
            # date

            # get the file date
            file_date = datetime.datetime.today()
            if os.path.exists(version.absolute_full_path):
                file_date = datetime.datetime.fromtimestamp(
                    os.path.getmtime(version.absolute_full_path)
                )
            item = QtGui.QTableWidgetItem(
                file_date.strftime(defaults.date_time_format)
            )

            # align to left and vertical center
            item.setTextAlignment(0x0001 | 0x0080)

            if is_published:
                set_font(item)

            self.previous_versions_tableWidget.setItem(i, c, item)
            c += 1
            # ------------------------------------

            # ------------------------------------
            # description
            item = QtGui.QTableWidgetItem(version.description)
            # align to left and vertical center
            item.setTextAlignment(0x0001 | 0x0080)

            if is_published:
                set_font(item)

            self.previous_versions_tableWidget.setItem(i, c, item)
            c += 1
            # ------------------------------------

        # resize the first column
        self.previous_versions_tableWidget.resizeRowsToContents()
        self.previous_versions_tableWidget.resizeColumnsToContents()
        self.previous_versions_tableWidget.resizeRowsToContents()

    def get_task(self):
        """returns the task from the UI, it is an task, asset, shot, sequence
        or project
        """
        task = None
        indexes = self.tasks_treeView.selectionModel().selectedIndexes()
        if indexes:
            current_index = indexes[0]
            logger.debug('current_index : %s' % current_index)

            item_model = self.tasks_treeView.model()
            current_item = item_model.itemFromIndex(current_index)

            if current_item:
                task = current_item.task

        # logger.debug('task: %s' % task)
        return task

    def add_take_toolButton_clicked(self):
        """runs when the add_take_toolButton clicked
        """

        # open up a QInputDialog and ask for a take name
        # anything is acceptable
        # because the validation will occur in the Version instance

        self.current_dialog = QtGui.QInputDialog(self)

        current_take_name = self.takes_listWidget.currentItem().text()

        take_name, ok = self.current_dialog.getText(
            self,
            "Add Take Name",
            "New Take Name",
            QtGui.QLineEdit.Normal,
            current_take_name
        )

        if ok:
            # add the given text to the takes_listWidget
            # if it is not empty
            if take_name != "":
                # TODO: there are no tests for take_name conditioning
                # if the given take name is in the list don't add it
                take_name = take_name.title()
                # replace spaces with underscores
                take_name = re.sub(r'[\s\-]+', '_', take_name)
                take_name = re.sub(r'[^a-zA-Z0-9_]+', '', take_name)
                take_name = re.sub(r'[_]+', '_', take_name)
                take_name = re.sub(r'[_]+$', '', take_name)
                in_list = False
                for i in range(self.takes_listWidget.count()):
                    item = self.takes_listWidget.item(i)
                    if item.text() == take_name:
                        in_list = True
                if not in_list:
                    self.takes_listWidget.addItem(take_name)
                    # sort the list
                    self.takes_listWidget.sortItems()
                    items = self.takes_listWidget.findItems(
                        take_name,
                        QtCore.Qt.MatchExactly
                    )
                    if items:
                        item = items[0]
                        # set the take to the new one
                        self.takes_listWidget.setCurrentItem(item)

    def get_new_version(self):
        """returns a :class:`~oyProjectManager.models.version.Version` instance
        from the UI by looking at the input fields
        
        :returns: :class:`~oyProjectManager.models.version.Version` instance
        """
        # create a new version
        task = self.get_task()
        if not task or not isinstance(task, Task):
            return None

        take_name = self.takes_listWidget.currentItem().text()
        user = self.get_logged_in_user()
        if not user:
            self.close()

        description = self.description_textEdit.toPlainText()
        published = self.publish_checkBox.isChecked()
        
        # TODO: version statuses will be removed from Stalker, so later on delete this part
        # status_name = self.statuses_comboBox.currentText()
        versions_status_list = StatusList.query\
            .filter(StatusList.target_entity_type=='Version').first()
        status = versions_status_list.statuses[0]

        version = Version(
            task=task,
            created_by=user,
            take_name=take_name,
            description=description,
            status=status
        )
        version.is_published = published

        return version

    def get_previous_version(self):
        """returns the :class:`~oyProjectManager.models.version.Version`
        instance from the UI by looking at the previous_versions_tableWidget
        """
        index = self.previous_versions_tableWidget.currentRow()
        try:
            version = self.previous_versions_tableWidget.versions[index]
            return version
        except IndexError:
            return None

    def export_as_pushButton_clicked(self):
        """runs when the export_as_pushButton clicked
        """
        logger.debug("exporting the data as a new version")

        # get the new version
        new_version = self.get_new_version()

        # call the environments export_as method
        if self.environment is not None:
            self.environment.export_as(new_version)

            # inform the user about what happened
            if logger.level != logging.DEBUG:
                QtGui.QMessageBox.information(
                    self,
                    "Export",
                    new_version.filename + "\n\n has been exported correctly!",
                    QtGui.QMessageBox.Ok
                )

    def save_as_pushButton_clicked(self):
        """runs when the save_as_pushButton clicked
        """
        logger.debug("saving the data as a new version")

        # get the new version
        try:
            new_version = self.get_new_version()
        except (TypeError, ValueError) as e:
            # pop up an Message Dialog to give the error message
            QtGui.QMessageBox.critical(self, "Error", str(e))
            return None

        # call the environments save_as method
        if self.environment and isinstance(self.environment, EnvironmentBase):
            try:
                self.environment.save_as(new_version)
            except RuntimeError as e:
                QtGui.QMessageBox.critical(self, 'Error', str(e))
                return None
        else:
            logger.debug('No environment given, just generating paths')

            # just set the clipboard to the new_version.absolute_full_path
            clipboard = QtGui.QApplication.clipboard()
            new_version.update_paths()
            v_path = os.path.normpath(new_version.absolute_full_path)
            clipboard.setText(v_path)

            # create the path
            try:
                logger.debug('creating path for new version')
                os.makedirs(new_version.absolute_path)
            except OSError: # path already exists
                pass

            # create the output path
            #try:
            #    logger.debug('creating output_path for new version')
            #    os.makedirs(new_version.output_path)
            #except OSError: # path already exists
            #    pass

            # and warn the user about a new version is created and the
            # clipboard is set to the new version full path
            QtGui.QMessageBox.warning(
                self,
                "Path Generated",
                "A new Version is created at:\n\n" + v_path + "\n\n" +
                "And the path is copied to your clipboard!!!",
                QtGui.QMessageBox.Ok
            )

        # save the new version to the database
        DBSession().add(new_version)
        DBSession.commit()

        if self.environment:
            # close the UI
            self.close()
        else:
            # refresh the UI
            self.tasks_treeView_changed()

    def chose_pushButton_clicked(self):
        """runs when the chose_pushButton clicked
        """
        self.chosen_version = self.get_previous_version()
        if self.chosen_version:
            logger.debug(self.chosen_version)
            self.close()

    def open_pushButton_clicked(self):
        """runs when the open_pushButton clicked
        """
        # get the new version
        old_version = self.get_previous_version()

        logger.debug("opening version %s" % old_version)

        # call the environments open_ method
        if self.environment is not None:
            to_update_list = []
            # environment can throw RuntimeError for unsaved changes
            try:
                envStatus, to_update_list = \
                    self.environment.open_(old_version)
            except RuntimeError as e:
                # pop a dialog and ask if the user really wants to open the
                # file

                answer = QtGui.QMessageBox.question(
                    self,
                    'RuntimeError',
                    "There are <b>unsaved changes</b> in the current "
                    "scene<br><br>Do you really want to open the file?",
                    QtGui.QMessageBox.Yes,
                    QtGui.QMessageBox.No
                )

                envStatus = False

                if answer == QtGui.QMessageBox.Yes:
                    envStatus, to_update_list = \
                        self.environment.open_(old_version, True)
                else:
                    # no, just return
                    return

            # check the to_update_list to update old versions
            if len(to_update_list):
                # invoke the assetUpdater for this scene
                version_updater_mainDialog = \
                    version_updater.MainDialog(self.environment, self)

                version_updater_mainDialog.exec_()

            self.environment.post_open(old_version)

        # close the dialog
        self.close()

    def reference_pushButton_clicked(self):
        """runs when the reference_pushButton clicked
        """

        # get the new version
        previous_version = self.get_previous_version()

        # allow only published versions to be referenced
        if not previous_version.is_published:
            QtGui.QMessageBox.critical(
                self,
                "Critical Error",
                "Referencing <b>un-published versions</b> are not allowed!\n"
                "Please reference a published version of the same Asset/Shot",
                QtGui.QMessageBox.Ok
            )
            return

        logger.debug("referencing version %s" % previous_version)

        # call the environments reference method
        if self.environment is not None:
            self.environment.reference(previous_version)

            # inform the user about what happened
            if logger.level != logging.DEBUG:
                QtGui.QMessageBox.information(
                    self,
                    "Reference",
                    previous_version.filename + \
                    "\n\n has been referenced correctly!",
                    QtGui.QMessageBox.Ok
                )

    def import_pushButton_clicked(self):
        """runs when the import_pushButton clicked
        """

        # get the previous version
        previous_version = self.get_previous_version()

        logger.debug("importing version %s" % previous_version)

        # call the environments import_ method
        if self.environment is not None:
            self.environment.import_(previous_version)

            # inform the user about what happened
            if logger.level != logging.DEBUG:
                QtGui.QMessageBox.information(
                    self,
                    "Import",
                    previous_version.filename + \
                    "\n\n has been imported correctly!",
                    QtGui.QMessageBox.Ok
                )

    def clear_thumbnail(self):
        """clears the thumbnail_graphicsView
        """
        ui_utils.clear_thumbnail(self.thumbnail_graphicsView)

    def update_thumbnail(self):
        """updates the thumbnail for the selected task
        """
        # get the current task
        task = self.get_task()
        if task:
            ui_utils.update_gview_with_task_thumbnail(
                task,
                self.thumbnail_graphicsView
            )

    def upload_thumbnail_pushButton_clicked(self):
        """runs when the upload_thumbnail_pushButton is clicked
        """
        #thumbnail_full_path = ui_utils.choose_thumbnail(self)
        #
        ## if the thumbnail_full_path is empty do not do anything
        #if thumbnail_full_path == "":
        #    return
        #
        ## get the current task
        #task = self.get_task()
        #
        #ui_utils.upload_thumbnail(task, thumbnail_full_path)
        #
        ## update the thumbnail
        #self.update_thumbnail()
        # TODO: upload it to stalker server
        pass

    def find_from_path_pushButton_clicked(self):
        """runs when find_from_path_pushButton is clicked
        """
        full_path = self.find_from_path_lineEdit.text()
        env = EnvironmentBase()
        version = env.get_version_from_full_path(full_path)
        self.restore_ui(version)

    
