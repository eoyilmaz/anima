# -*- coding: utf-8 -*-
# Copyright (c) 2012-2013, Anima Istanbul
#
# This module is part of anima-tools and is released under the BSD 2
# License: http://www.opensource.org/licenses/BSD-2-Clause

import logging
import datetime
import os
import re
import tempfile

from sqlalchemy import distinct

from stalker.db import DBSession
from stalker import (db, defaults, Version, Project, Task, LocalSession,
                     EnvironmentBase, Group)

import anima
from anima.pipeline import utils, power_users_group_names
from anima.pipeline.env.externalEnv import ExternalEnvFactory
from anima.pipeline.ui import utils as ui_utils
from anima.pipeline.ui import IS_PYSIDE, IS_PYQT4, login_dialog, version_updater
from anima.pipeline.ui.lib import QtGui, QtCore
from anima.pipeline.ui.utils import UICaller, AnimaDialogBase


logger = logging.getLogger(__name__)
fh = logging.FileHandler(
    os.path.join(tempfile.gettempdir(), 'version_creator.log')
)
logger.setLevel(logging.DEBUG)
logger.addHandler(fh)

if IS_PYSIDE():
    from anima.pipeline.ui.ui_compiled import version_creator_UI_pyside as version_creator_UI
elif IS_PYQT4():
    from anima.pipeline.ui.ui_compiled import version_creator_UI_pyqt4 as version_creator_UI


class TaskItem(QtGui.QStandardItem):
    """Implements the Task as a QStandardItem
    """

    def __init__(self, *args, **kwargs):
        QtGui.QStandardItem.__init__(self, *args, **kwargs)
        logger.debug(
            'TaskItem.__init__() is started for item: %s' % self.text())
        self.loaded = False
        self.task = None
        self.parent = None
        self.fetched_all = False
        self.setEditable(False)
        self.user = None
        self.user_tasks_only = False
        logger.debug(
            'TaskItem.__init__() is finished for item: %s' % self.text())

    def clone(self):
        """returns a copy of this item
        """
        logger.debug('TaskItem.clone() is started for item: %s' % self.text())
        new_item = TaskItem()
        new_item.task = self.task
        new_item.parent = self.parent
        new_item.fetched_all = self.fetched_all
        logger.debug('TaskItem.clone() is finished for item: %s' % self.text())
        return new_item

    def canFetchMore(self):
        logger.debug(
            'TaskItem.canFetchMore() is started for item: %s' % self.text())
        return_value = False
        if self.task and not self.fetched_all:
            if isinstance(self.task, Task):
                return_value = self.task.is_container
            elif isinstance(self.task, Project):
                return_value = len(self.task.root_tasks) > 0
        else:
            return_value = False
        logger.debug(
            'TaskItem.canFetchMore() is finished for item: %s' % self.text())
        return return_value

    def fetchMore(self):
        logger.debug(
            'TaskItem.fetchMore() is started for item: %s' % self.text())

        if self.canFetchMore():
            tasks = []
            if isinstance(self.task, Task):
                tasks = self.task.children
            elif isinstance(self.task, Project):
                tasks = self.task.root_tasks

            # model = self.model() # This will cause a SEGFAULT
            if self.user_tasks_only:
                user_tasks_and_parents = []
                # need to filter tasks which do not belong to user
                for task in tasks:
                    for user_task in self.user.tasks:
                        if task in user_task.parents or \
                                        task is user_task or \
                                        task in self.user.projects:
                            user_tasks_and_parents.append(task)
                            break

                tasks = user_tasks_and_parents
            tasks = sorted(tasks, key=lambda x: x.name)

            for task in tasks:
                task_item = TaskItem(0, 3)
                task_item.parent = self
                task_item.task = task
                task_item.user = self.user
                task_item.user_tasks_only = self.user_tasks_only

                # set the font
                # name_item = QtGui.QStandardItem(task.name)
                # entity_type_item = QtGui.QStandardItem(task.entity_type)
                # task_item.setItem(0, 0, name_item)
                # task_item.setItem(0, 1, entity_type_item)
                task_item.setText(task.name)

                make_bold = False
                if isinstance(task, Task):
                    if task.is_container:
                        make_bold = True
                elif isinstance(task, Project):
                    make_bold = True

                if make_bold:
                    my_font = task_item.font()
                    my_font.setBold(True)
                    task_item.setFont(my_font)

                self.appendRow(task_item)

            self.fetched_all = True
        logger.debug(
            'TaskItem.fetchMore() is finished for item: %s' % self.text())

    def hasChildren(self):
        logger.debug(
            'TaskItem.hasChildren() is started for item: %s' % self.text())
        if self.task:
            if isinstance(self.task, Task):
                return_value = self.task.is_container
            elif isinstance(self.task, Project):
                return_value = len(self.task.root_tasks) > 0
            else:
                return_value = False
        else:
            return_value = False
        logger.debug(
            'TaskItem.hasChildren() is finished for item: %s' % self.text())
        return return_value


class TaskTreeModel(QtGui.QStandardItemModel):
    """Implements the model view for the task hierarchy
    """

    def __init__(self, *args, **kwargs):
        QtGui.QStandardItemModel.__init__(self, *args, **kwargs)
        logger.debug('TaskTreeModel.__init__() is started')
        self.user = None
        self.root = None
        self.user_tasks_only = False
        logger.debug('TaskTreeModel.__init__() is finished')

    def populateTree(self, projects):
        """populates tree with user projects
        """
        logger.debug('TaskTreeModel.populateTree() is started')
        self.setColumnCount(3)
        self.setHorizontalHeaderLabels(
            ['Name', 'Type', 'Dependencies']
        )

        #item_prototype = TaskItem()
        #self.setItemPrototype(item_prototype)

        for project in projects:
            project_item = TaskItem(0, 3)
            project_item.parent = None
            project_item.setColumnCount(3)
            project_item.setText(project.name)
            project_item.task = project
            project_item.user = self.user
            project_item.user_tasks_only = self.user_tasks_only

            # set the font
            # project_item.setText(0, entity.name)
            # project_item.setText(1, entity.entity_type)
            # name_item = QtGui.QStandardItem()
            # name_item.setText(project.name)
            # entity_type_item = QtGui.QStandardItem()
            # entity_type_item.setText(project.entity_type)
            # project_item.appendColumn([name_item, entity_type_item])

            # Set Font
            # project_item.setText(project.name)
            my_font = project_item.font()
            my_font.setBold(True)
            project_item.setFont(my_font)

            self.appendRow(project_item)

        logger.debug('TaskTreeModel.populateTree() is finished')

    def canFetchMore(self, index):
        logger.debug(
            'TaskTreeModel.canFetchMore() is started for index: %s' % index)
        if not index.isValid():
            return_value = False
        else:
            item = self.itemFromIndex(index)
            return_value = item.canFetchMore()
        logger.debug(
            'TaskTreeModel.canFetchMore() is finished for index: %s' % index)
        return return_value

    def fetchMore(self, index):
        """fetches more elements
        """
        logger.debug(
            'TaskTreeModel.canFetchMore() is started for index: %s' % index)
        if index.isValid():
            item = self.itemFromIndex(index)
            item.fetchMore()
        logger.debug(
            'TaskTreeModel.canFetchMore() is finished for index: %s' % index)

    def hasChildren(self, index):
        """returns True or False depending on to the index and the item on the
        index
        """
        logger.debug(
            'TaskTreeModel.hasChildren() is started for index: %s' % index)
        if not index.isValid():
            projects = self.user.projects
            return_value = len(projects) > 0
        else:
            item = self.itemFromIndex(index)
            return_value = False
            if item:
                return_value = item.hasChildren()
        logger.debug(
            'TaskTreeModel.hasChildren() is finished for index: %s' % index)
        return return_value


class TaskNameCompleter(QtGui.QCompleter):
    def __init__(self, parent):
        QtGui.QCompleter.__init__(self, [], parent)

    def update(self, completion_prefix):
        tasks = Task.query \
            .filter(Task.name.ilike('%' + completion_prefix + '%')) \
            .all()
        logger.debug('completer tasks : %s' % tasks)
        task_names = [task.name for task in tasks]
        model = QtGui.QStringListModel(task_names)
        self.setModel(model)
        # self.setCompletionPrefix(completion_prefix)
        self.setCompletionPrefix('')

        # if completion_prefix.strip() != '':
        self.complete()


class TakesListWidget(QtGui.QListWidget):
    """A specialized QListWidget variant used in Take names.
    """

    def __init__(self, parent=None, *args, **kwargs):
        QtGui.QListWidget.__init__(self, parent, *args, **kwargs)
        self._take_names = []
        self.take_names = []

    @property
    def take_names(self):
        return self._take_names

    @take_names.setter
    def take_names(self, take_names_in):
        logger.debug('setting take names')
        self.clear()
        self._take_names = take_names_in
        main = defaults.version_take_name
        if main in self._take_names:
            logger.debug('removing default take name from list')
            index_of_main = self._take_names.index(main)
            self._take_names.pop(index_of_main)

        # insert the default take name to the start
        self._take_names.insert(0, main)

        # clear the list and new items
        logger.debug('adding supplied take names: %s' % self._take_names)
        self.addItems(self._take_names)

        # select the first item
        self.setCurrentItem(self.item(0))

    def add_take(self, take_name):
        """adds a new take to the takes list
        """
        # condition the input
        # TODO: there are no tests for take_name conditioning
        # if the given take name is in the list don't add it
        take_name = take_name[0].upper() + take_name[1:]
        # replace spaces with underscores
        take_name = re.sub(r'[\s\-]+', '_', take_name)
        take_name = re.sub(r'[^a-zA-Z0-9_]+', '', take_name)
        take_name = re.sub(r'[_]+', '_', take_name)
        take_name = re.sub(r'[_]+$', '', take_name)

        if take_name not in self._take_names:
            # add the item via property
            new_take_list = self._take_names
            new_take_list.append(take_name)
            new_take_list.sort()
            self.take_names = new_take_list

            # select the newly added take name
            items = self.findItems(take_name, QtCore.Qt.MatchExactly)
            if items:
                item = items[0]
                # set the take to the new one
                self.setCurrentItem(item)

    @property
    def current_take_name(self):
        """gets the current take name
        """
        take_name = ''
        item = self.currentItem()
        if item:
            take_name = item.text()
        return take_name

    @current_take_name.setter
    def current_take_name(self, take_name):
        """sets the current take name
        """
        logger.debug('finding take with name: %s' % take_name)
        items = self.findItems(
            take_name,
            QtCore.Qt.MatchExactly
        )
        if items:
            self.setCurrentItem(items[0])

    def clear(self):
        """overridden clear method
        """
        self._take_names = []
        # call the super
        QtGui.QListWidget.clear(self)


class VersionsTableWidget(QtGui.QTableWidget):
    """A QTableWidget derivative specialized to hold version data
    """

    def __init__(self, parent=None, *args, **kwargs):
        QtGui.QTableWidget.__init__(self, parent, *args, **kwargs)

        self.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
        self.setAlternatingRowColors(True)
        self.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
        self.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.setShowGrid(False)
        self.setColumnCount(5)
        self.setObjectName("previous_versions_tableWidget")
        self.setColumnCount(5)
        self.setRowCount(0)
        self.setHorizontalHeaderItem(0, QtGui.QTableWidgetItem())
        self.setHorizontalHeaderItem(1, QtGui.QTableWidgetItem())
        self.setHorizontalHeaderItem(2, QtGui.QTableWidgetItem())
        self.setHorizontalHeaderItem(3, QtGui.QTableWidgetItem())
        self.setHorizontalHeaderItem(4, QtGui.QTableWidgetItem())
        self.horizontalHeader().setStretchLastSection(True)
        self.verticalHeader().setStretchLastSection(False)

        self.setToolTip(
            QtGui.QApplication.translate(
                "Dialog",
                "<html><head/><body><p>Right click to:</p><ul style=\"margin-top: 0px; margin-bottom: 0px; margin-left: 0px; margin-right: 0px; -qt-list-indent: 1;\"><li><span style=\" font-weight:600;\">Copy Path</span></li><li><span style=\" font-weight:600;\">Browse Path</span></li><li><span style=\" font-weight:600;\">Change Description</span></li></ul><p>Double click to:</p><ul style=\"margin-top: 0px; margin-bottom: 0px; margin-left: 0px; margin-right: 0px; -qt-list-indent: 1;\"><li style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-weight:600;\">Open</span></li></ul></body></html>",
                None,
                QtGui.QApplication.UnicodeUTF8
            )
        )

        self.versions = []
        self.labels = [
            '#',
            'App',
            'User',
            'Size',
            'Date',
            'Description',
        ]
        self.setColumnCount(len(self.labels))

    def clear(self):
        """overridden clear method
        """
        QtGui.QTableWidget.clear(self)
        self.versions = []

        # reset the labels
        self.setHorizontalHeaderLabels(self.labels)

    def select_version(self, version):
        """selects the given version in the list
        """
        # select the version in the previous version list
        index = -1
        for i, prev_version in enumerate(self.versions):
            if self.versions[i] == version:
                index = i
                break

        logger.debug('current index: %s' % index)

        # select the row
        if index != -1:
            item = self.item(index, 0)
            logger.debug('item : %s' % item)
            self.setCurrentItem(item)

    @property
    def current_version(self):
        """returns the current selected version from the table
        """
        index = self.currentRow()
        try:
            version = self.versions[index]
            return version
        except IndexError:
            return None

    def update_content(self, versions):
        """updates the content with the given versions data
        """
        logger.debug('VersionsTableWidget.update_content() is started')

        self.clear()
        self.versions = versions
        self.setRowCount(len(versions))

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

            self.setItem(i, c, item)
            c += 1
            # ------------------------------------

            # ------------------------------------
            # created_with
            item = QtGui.QTableWidgetItem()
            if version.created_with:
                item.setIcon(ui_utils.getIcon(version.created_with.lower()))

            if is_published:
                set_font(item)
            self.setItem(i, c, item)
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

            self.setItem(i, c, item)
            c += 1
            # ------------------------------------

            # ------------------------------------
            # filesize

            # get the file size
            #file_size_format = "%.2f MB"
            file_size = -1
            if os.path.exists(version.absolute_full_path):
                file_size = float(
                    os.path.getsize(version.absolute_full_path)) / 1048576

            item = QtGui.QTableWidgetItem(
                defaults.file_size_format % file_size)
            # align to left and vertical center
            item.setTextAlignment(0x0001 | 0x0080)

            if is_published:
                set_font(item)

            self.setItem(i, c, item)
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

            self.setItem(i, c, item)
            c += 1
            # ------------------------------------

            # ------------------------------------
            # description
            item = QtGui.QTableWidgetItem(version.description)
            # align to left and vertical center
            item.setTextAlignment(0x0001 | 0x0080)

            if is_published:
                set_font(item)

            self.setItem(i, c, item)
            c += 1
            # ------------------------------------

        # resize the first column
        self.resizeRowsToContents()
        self.resizeColumnsToContents()
        self.resizeRowsToContents()
        logger.debug('VersionsTableWidget.update_content() is finished')


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
        self.environment_name_format = '%n (%e)'

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

        # setup signals
        self._setup_signals()

        # setup defaults
        self._set_defaults()

        # center window
        self.center_window()

        logger.debug("finished initializing the interface")

    def close(self):
        logger.debug('closing the ui')
        super(MainDialog, self).close()

    def show(self):
        """overridden show method
        """
        logger.debug('MainDialog.show is started')
        logged_in_user = self.get_logged_in_user()
        if not logged_in_user:
            self.close()
            return_val = None
        else:
            return_val = super(MainDialog, self).show()

        logger.debug('MainDialog.show is finished')
        return return_val

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

        # search for tasks
        # QtCore.QObject.connect(
        #     self.search_task_comboBox,
        #     QtCore.SIGNAL("editTextChanged(QString)"),
        #     self.search_task_comboBox_textChanged
        # )

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
            QtCore.SIGNAL(
                "currentItemChanged(QListWidgetItem *, QListWidgetItem *)"),
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

    def is_power_user(self, user):
        """A predicate that retuns if the user is a poweruser
        """
        power_users_groups = Group.query \
            .filter(Group.name.in_(power_users_group_names)) \
            .all()
        if power_users_groups:
            for group in power_users_groups:
                if group in user.groups:
                    return True
        return False

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

        if not hasattr(item, 'task'):
            return

        task = item.task
        if not isinstance(task, Task):
            return

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

        if not depends and not dependent_of:
            no_deps_action = menu.addAction('No Dependencies')
            no_deps_action.setEnabled(False)

        selected_item = menu.exec_(global_position)

        if selected_item:
            choice = selected_item.text()
            task = selected_item.task
            self.find_and_select_entity_item_in_treeView(
                task,
                self.tasks_treeView
            )

    def get_item_indices_containing_text(self, text, treeView):
        """returns the indexes of the item indices containing the given text
        """
        model = treeView.model()
        logger.debug('searching for text : %s' % text)
        return model.match(
            model.index(0, 0),
            0,
            text,
            -1,
            QtCore.Qt.MatchRecursive
        )

    def find_entity_item_in_tree_view(self, entity, treeView):
        """finds the item related to the stalker entity in the given
        QtTreeView
        """
        indexes = self.get_item_indices_containing_text(entity.name, treeView)
        model = treeView.model()
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
        logger.debug('start filling tasks_treeView')
        logged_in_user = self.get_logged_in_user()

        logger.debug('creating a new model')
        projects = Project.query.order_by(Project.name).all()

        task_tree_model = TaskTreeModel()
        task_tree_model.user = logged_in_user
        task_tree_model.user_tasks_only = self.my_tasks_only_checkBox.isChecked()
        task_tree_model.populateTree(projects)

        self.tasks_treeView.setModel(task_tree_model)

        logger.debug('setting up signals for tasks_treeView_changed')
        # tasks_treeView
        QtCore.QObject.connect(
            self.tasks_treeView.selectionModel(),
            QtCore.SIGNAL('selectionChanged(const QItemSelection &, '
                          'const QItemSelection &)'),
            self.tasks_treeView_changed
        )

        self.tasks_treeView.is_updating = False
        logger.debug('finished filling tasks_treeView')

    def tasks_treeView_auto_fit_column(self):
        """fits columns to content
        """
        self.tasks_treeView.resizeColumnToContents(0)

    def tasks_treeView_changed(self):
        """runs when the tasks_treeView item is changed
        """
        logger.debug('tasks_treeView_changed running')
        if self.tasks_treeView.is_updating:
            logger.debug('tasks_treeView is updating, so returning early')
            return

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
            takes.sort()

        logger.debug("len(takes) from db: %s" % len(takes))

        logger.debug("adding the takes from db")
        self.takes_listWidget.take_names = takes

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
        logger.debug('finished creating splitter')

        # set icon for search_task_toolButton
        # icon = QtGui.QApplication.style().standardIcon(QtGui.QStyle.SP_BrowserReload)
        # self.search_task_toolButton.setIcon(icon)

        # disable update_paths_checkBox
        self.update_paths_checkBox.setVisible(False)

        # check login
        self.fill_logged_in_user()

        # clear the thumbnail area
        self.clear_thumbnail()

        # fill the tasks
        self.fill_tasks_treeView()

        # *********************************************************************
        # use the new TakeListWidget
        self.takes_listWidget.deleteLater()
        self.takes_listWidget = TakesListWidget()
        self.takes_listWidget.setObjectName("takes_listWidget")
        self.horizontalLayout_6.insertWidget(1, self.takes_listWidget)

        # reconnect signals
        # takes_listWidget
        QtCore.QObject.connect(
            self.takes_listWidget,
            QtCore.SIGNAL("currentTextChanged(QString)"),
            self.takes_listWidget_changed
        )

        # takes_listWidget
        QtCore.QObject.connect(
            self.takes_listWidget,
            QtCore.SIGNAL(
                "currentItemChanged(QListWidgetItem *, QListWidgetItem *)"),
            self.takes_listWidget_changed
        )
        # *********************************************************************



        # *********************************************************************
        # previous_versions_tableWidget
        self.previous_versions_tableWidget.deleteLater()
        self.previous_versions_tableWidget = VersionsTableWidget(
            self.previous_versions_groupBox
        )
        self.verticalLayout_7.insertWidget(1, self.previous_versions_tableWidget)
        self.setTabOrder(self.save_as_pushButton,
                         self.previous_versions_tableWidget)
        self.setTabOrder(self.previous_versions_tableWidget,
                         self.open_pushButton)

        # custom context menu for the previous_versions_tableWidget
        self.previous_versions_tableWidget.setContextMenuPolicy(
            QtCore.Qt.CustomContextMenu
        )

        QtCore.QObject.connect(
            self.previous_versions_tableWidget,
            QtCore.SIGNAL("customContextMenuRequested(const QPoint&)"),
            self._show_previous_versions_tableWidget_context_menu
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
        # *********************************************************************

        # run the project changed item for the first time
        # self.project_changed()

        # set the completer for the search_task_lineEdit
        # completer = TaskNameCompleter(self)
        # completer.setCaseSensitivity(QtCore.Qt.CaseInsensitive)
        # self.search_task_lineEdit.setCompleter(completer)
        # self.search_task_lineEdit.textChanged.connect(completer.update)
        # 
        # completer.activated.connect(self.search_task_lineEdit.setText)
        # completer.setWidget(self.search_task_lineEdit)
        # # self.search_task_lineEdit.editingFinished.connect()
        self.search_task_lineEdit.setVisible(False)

        # fill programs list
        env_factory = ExternalEnvFactory()
        env_names = env_factory.get_env_names(
            name_format=self.environment_name_format
        )
        self.environment_comboBox.addItems(env_names)

        is_external_env = False
        env = self.environment
        if not self.environment:
            is_external_env = True
            # just get one random environment
            env = env_factory.get_env(env_names[0])

        logger.debug("restoring the ui with the version from environment")

        # get the last version from the environment
        version_from_env = env.get_last_version()

        logger.debug("version_from_env: %s" % version_from_env)
        self.restore_ui(version_from_env)

        if is_external_env:
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
        if not self.find_and_select_entity_item_in_treeView(
                task, self.tasks_treeView):
            return

        # take_name
        take_name = version.take_name
        self.takes_listWidget.current_take_name = take_name

        # select the version in the previous version list
        self.previous_versions_tableWidget.select_version(version)

        if not self.environment:
            # set the environment_comboBox
            env_factory = ExternalEnvFactory()
            try:
                env = env_factory.get_env(version.created_with)
            except ValueError:
                pass
            else:
                # find it in the comboBox
                index = self.environment_comboBox.findText(
                    env.name, QtCore.Qt.MatchContains)
                if index:
                    self.environment_comboBox.setCurrentIndex(index)

    def load_task_item_hierarchy(self, task, treeView):
        """loads the TaskItem related to the given task in the given treeView
        
        :return: TaskItem instance
        """
        self.tasks_treeView.is_updating = True
        item = self.find_entity_item_in_tree_view(task, treeView)
        if not item:
            # the item is not loaded to the UI yet
            # start loading its parents
            # start from the project
            item = self.find_entity_item_in_tree_view(task.project, treeView)
            logger.debug('item for project: %s' % item)

            if item:
                treeView.setExpanded(item.index(), True)

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
                logger.debug('can not find item')

        self.tasks_treeView.is_updating = False
        return item

    def find_and_select_entity_item_in_treeView(self, task, treeView):
        """finds and selects the task in the given treeView item
        """
        item = self.load_task_item_hierarchy(task, treeView)

        logger.debug('*******************************')
        logger.debug('item: %s' % item)

        self.tasks_treeView.selectionModel().select(
            item.index(), QtGui.QItemSelectionModel.ClearAndSelect
        )
        return item

    def takes_listWidget_changed(self, index):
        """runs when the takes_listWidget has changed
        """
        logger.debug('takes_listWidget_changed started')
        # update the previous_versions_tableWidget
        self.update_previous_versions_tableWidget()
        logger.debug('takes_listWidget_changed finished')

    def update_previous_versions_tableWidget(self):
        """updates the previous_versions_tableWidget
        """
        logger.debug('update_previous_versions_tableWidget is started')
        self.previous_versions_tableWidget.clear()

        task = self.get_task()
        if not task or not isinstance(task, Task):
            return

        # take name
        take_name = self.takes_listWidget.current_take_name

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

        self.previous_versions_tableWidget.update_content(versions)
        logger.debug('update_previous_versions_tableWidget is finished')

    def get_task(self):
        """returns the task from the UI, it is an task, asset, shot, sequence
        or project
        """
        task = None
        selection_model = self.tasks_treeView.selectionModel()
        logger.debug('selection_model: %s' % selection_model)
        indexes = selection_model.selectedIndexes()
        logger.debug('selected indexes : %s' % indexes)
        if indexes:
            current_index = indexes[0]
            logger.debug('current_index : %s' % current_index)

            item_model = self.tasks_treeView.model()
            current_item = item_model.itemFromIndex(current_index)

            if current_item:
                task = current_item.task

        logger.debug('task: %s' % task)
        return task

    def add_take_toolButton_clicked(self):
        """runs when the add_take_toolButton clicked
        """

        # open up a QInputDialog and ask for a take name
        # anything is acceptable
        # because the validation will occur in the Version instance

        self.current_dialog = QtGui.QInputDialog(self)

        current_take_name = self.takes_listWidget.current_take_name

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
                self.takes_listWidget.add_take(take_name)

    def get_new_version(self):
        """returns a :class:`~oyProjectManager.models.version.Version` instance
        from the UI by looking at the input fields
        
        :returns: :class:`~oyProjectManager.models.version.Version` instance
        """
        # create a new version
        task = self.get_task()
        if not task or not isinstance(task, Task):
            return None

        take_name = self.takes_listWidget.current_take_name
        user = self.get_logged_in_user()
        if not user:
            self.close()

        description = self.description_textEdit.toPlainText()
        published = self.publish_checkBox.isChecked()

        version = Version(
            task=task,
            created_by=user,
            take_name=take_name,
            description=description
        )
        version.is_published = published

        return version

    def export_as_pushButton_clicked(self):
        """runs when the export_as_pushButton clicked
        """
        logger.debug("exporting the data as a new version")

        # get the new version
        new_version = self.get_new_version()

        if not new_version:
            return

        # check if the task is a leaf task
        if not new_version.task.is_leaf:
            QtGui.QMessageBox.critical(
                self, 'Error', 'Please select a <strong>leaf</strong> task!'
            )
            return

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

        if not new_version:
            return

        # check if the task is a leaf task
        if not new_version.task.is_leaf:
            QtGui.QMessageBox.critical(
                self, 'Error', 'Please select a <strong>leaf</strong> task!'
            )
            return

        # call the environments save_as method
        is_external_env = False
        environment = self.environment
        if not environment:
            # get the environment
            env_name = self.environment_comboBox.currentText()
            env_factory = ExternalEnvFactory()
            environment = env_factory.get_env(env_name, self.environment_name_format)
            is_external_env = True
            if not environment:
                logger.debug('no env found with name: %s' % env_name)
                return
            logger.debug('env: %s' % environment.name)

        try:
            environment.save_as(new_version)
        except RuntimeError as e:
            QtGui.QMessageBox.critical(self, 'Error', str(e))
            return

        if is_external_env:
            # set the clipboard to the new_version.absolute_full_path
            clipboard = QtGui.QApplication.clipboard()

            logger.debug('new_version.absolute_full_path: %s' %
                         new_version.absolute_full_path)

            v_path = os.path.normpath(new_version.absolute_full_path)
            clipboard.setText(v_path)
    
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
        DBSession.add(new_version)
        DBSession.commit()

        if is_external_env:
            # refresh the UI
            self.tasks_treeView_changed()
        else:
            # close the UI
            self.close()

    def chose_pushButton_clicked(self):
        """runs when the chose_pushButton clicked
        """
        self.chosen_version = self.previous_versions_tableWidget.current_version
        if self.chosen_version:
            logger.debug(self.chosen_version)
            self.close()

    def open_pushButton_clicked(self):
        """runs when the open_pushButton clicked
        """
        # get the new version
        old_version = self.previous_versions_tableWidget.current_version

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
        previous_version = self.previous_versions_tableWidget.current_version

        # allow only published versions to be referenced
        if not previous_version.is_published:
            QtGui.QMessageBox.critical(
                self,
                "Critical Error",
                "Referencing <b>un-published versions</b> are only "
                "allowed for Power Users!\n"
                "Please reference a published version of the same Asset/Shot",
                QtGui.QMessageBox.Ok
            )
            return

        logger.debug("referencing version %s" % previous_version)

        # call the environments reference method
        if self.environment is not None:
            # get the use namespace state
            use_namespace = self.useNameSpace_checkBox.isChecked()

            self.environment.reference(previous_version, use_namespace)

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
        previous_version = self.previous_versions_tableWidget.current_version

        logger.debug("importing version %s" % previous_version)

        # call the environments import_ method
        if self.environment is not None:
            # get the use namespace state
            use_namespace = self.useNameSpace_checkBox.isChecked()

            self.environment.import_(previous_version, use_namespace)

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

        # def search_task_comboBox_textChanged(self, text):
        #     """runs when search_task_comboBox text changed
        #     """
        #     # text = self.search_task_lineEdit.text().strip()
        #     self.search_task_comboBox.clear()
        #     if not text:
        #         return
        #     tasks = Task.query.filter(Task.name.contains(text)).all()
        #     logger.debug('tasks with text: "%s" are : %s' % (text, tasks))
        #     # load all the tasks and their parents so we are going to be able to
        #     # find them later on
        #     # for task in tasks:
        #     #     self.load_task_item_hierarchy(task, self.tasks_treeView)
        #     # 
        #     # # now get the indices
        #     # indices = self.get_item_indices_containing_text(text,
        #     #                                                 self.tasks_treeView)
        #     # logger.debug('indices containing the given text are : %s' % indices)
        # 
        #     # self.search_task_comboBox.addItems(
        #     #     [
        #     #         (task.name + ' (%s)' % map(lambda x: '|'.join([parent.name for parent in x.parents]), task)) for task in tasks
        #     #     ]
        #     # )
        #     items = []
        #     for task in tasks:
        #         hierarchy_name = task.name + '(' + '|'.join(map(lambda x: x.name, task.parents)) + ')'
        #         items.append(hierarchy_name)
        #     self.search_task_comboBox.addItems(items)
        # 
