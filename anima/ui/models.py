# -*- coding: utf-8 -*-
# Copyright (c) 2012-2015, Anima Istanbul
#
# This module is part of anima-tools and is released under the BSD 2
# License: http://www.opensource.org/licenses/BSD-2-Clause

from anima import logger
from anima.ui.lib import QtGui, QtCore, QtWidgets


def set_item_color(item, color):
    """sets the item color

    :param item: the item
    """
    foreground = item.foreground()
    foreground.setColor(color)
    item.setForeground(foreground)


class VersionItem(QtGui.QStandardItem):
    """Implements the Version as a QStandardItem
    """

    def __init__(self, *args, **kwargs):
        QtGui.QStandardItem.__init__(self, *args, **kwargs)
        logger.debug(
            'VersionItem.__init__() is started for item: %s' % self.text()
        )
        self.loaded = False
        self.version = None
        self.parent = None
        self.pseudo_model = None
        self.fetched_all = False
        self.setEditable(False)
        logger.debug(
            'VersionItem.__init__() is finished for item: %s' % self.text()
        )

    def clone(self):
        """returns a copy of this item
        """
        logger.debug(
            'VersionItem.clone() is started for item: %s' % self.text()
        )
        new_item = VersionItem()
        new_item.version = self.version
        new_item.parent = self.parent
        new_item.fetched_all = self.fetched_all
        logger.debug(
            'VersionItem.clone() is finished for item: %s' % self.text()
        )
        return new_item

    def canFetchMore(self):
        logger.debug(
            'VersionItem.canFetchMore() is started for item: %s' % self.text()
        )
        if self.version and not self.fetched_all:
            return_value = bool(self.version.inputs)
        else:
            return_value = False
        logger.debug(
            'VersionItem.canFetchMore() is finished for item: %s' % self.text()
        )
        return return_value

    @classmethod
    def generate_version_row(cls, parent, pseudo_model, version):
        """Generates a new version row

        :return:
        """
        # column 0
        version_item = VersionItem(0, 0)
        version_item.parent = parent
        version_item.pseudo_model = pseudo_model

        version_item.version = version
        version_item.setEditable(False)
        reference_resolution = pseudo_model.reference_resolution

        if version in reference_resolution['update']:
            action = 'update'
            font_color = QtGui.QColor(192, 128, 0)
            if version in reference_resolution['root']:
                version_item.setCheckable(True)
                version_item.setCheckState(QtCore.Qt.Checked)
        elif version in reference_resolution['create']:
            action = 'create'
            font_color = QtGui.QColor(192, 0, 0)
            if version in reference_resolution['root']:
                version_item.setCheckable(True)
                version_item.setCheckState(QtCore.Qt.Checked)
        else:
            font_color = QtGui.QColor(0, 192, 0)
            action = ''

        version_item.action = action

        set_item_color(version_item, font_color)

        # thumbnail
        thumbnail_item = QtGui.QStandardItem()
        thumbnail_item.setEditable(False)
        # thumbnail_item.setText('no thumbnail')
        thumbnail_item.version = version
        thumbnail_item.action = action
        set_item_color(thumbnail_item, font_color)

        # Nice Name
        nice_name_item = QtGui.QStandardItem()
        nice_name_item.toolTip()
        nice_name_item.setText(
            '%s_v%s' % (
                version.nice_name,
                ('%s' % version.version_number).zfill(3)
            )
        )
        nice_name_item.setEditable(False)
        nice_name_item.version = version
        nice_name_item.action = action
        set_item_color(nice_name_item, font_color)

        # Take
        take_item = QtGui.QStandardItem()
        take_item.setEditable(False)
        take_item.setText(version.take_name)
        take_item.version = version
        take_item.action = action
        set_item_color(take_item, font_color)

        # Current
        current_version_item = QtGui.QStandardItem()
        current_version_item.setText('%s' % version.version_number)
        current_version_item.setEditable(False)
        current_version_item.version = version
        current_version_item.action = action
        set_item_color(current_version_item, font_color)

        # Latest
        latest_published_version = version.latest_published_version

        latest_published_version_item = QtGui.QStandardItem()
        latest_published_version_item.version = version
        latest_published_version_item.action = action
        latest_published_version_item.setEditable(False)

        latest_published_version_text = 'No Published Version'
        if latest_published_version:
            latest_published_version_text = '%s' % \
                latest_published_version.version_number
        latest_published_version_item.setText(
            latest_published_version_text
        )
        set_item_color(latest_published_version_item, font_color)

        # Action
        action_item = QtGui.QStandardItem()
        action_item.setEditable(False)
        action_item.setText(action)
        action_item.version = version
        action_item.action = action
        set_item_color(action_item, font_color)

        # Updated By
        updated_by_item = QtGui.QStandardItem()
        updated_by_item.setEditable(False)
        updated_by_text = ''
        if latest_published_version.updated_by:
            updated_by_text = latest_published_version.updated_by.name
        updated_by_item.setText(updated_by_text)
        updated_by_item.version = version
        updated_by_item.action = action
        set_item_color(updated_by_item, font_color)

        # Description
        description_item = QtGui.QStandardItem()
        if latest_published_version:
            description_item.setText(latest_published_version.description)
        description_item.setEditable(False)
        description_item.version = version
        description_item.action = action
        set_item_color(description_item, font_color)

        # # Path
        # path_item = QtGui.QStandardItem()
        # if latest_published_version:
        #     path_item.setText(version.absolute_full_path)
        # path_item.setEditable(True)
        # set_item_color(path_item, font_color)

        return [version_item, thumbnail_item, nice_name_item, take_item,
                current_version_item, latest_published_version_item,
                action_item, updated_by_item, description_item]

    def fetchMore(self):
        logger.debug(
            'VersionItem.fetchMore() is started for item: %s' % self.text()
        )

        if self.canFetchMore():
            # model = self.model() # This will cause a SEGFAULT
            versions = sorted(self.version.inputs, key=lambda x: x.full_path)

            for version in versions:
                self.appendRow(
                    self.generate_version_row(self, self.pseudo_model, version)
                )

            self.fetched_all = True
        logger.debug(
            'VersionItem.fetchMore() is finished for item: %s' % self.text()
        )

    def hasChildren(self):
        logger.debug(
            'VersionItem.hasChildren() is started for item: %s' % self.text()
        )
        if self.version:
            return_value = bool(self.version.inputs)
        else:
            return_value = False
        logger.debug(
            'VersionItem.hasChildren() is finished for item: %s' % self.text()
        )
        return return_value

    def type(self, *args, **kwargs):
        """
        """
        return QtGui.QStandardItem.UserType + 2


class VersionTreeModel(QtGui.QStandardItemModel):
    """Implements the model view for the version hierarchy
    """

    def __init__(self, flat_view=False, *args, **kwargs):
        QtGui.QStandardItemModel.__init__(self, *args, **kwargs)
        logger.debug('VersionTreeModel.__init__() is started')
        self.root = None
        self.root_versions = []
        self.reference_resolution = None
        self.flat_view = flat_view
        logger.debug('VersionTreeModel.__init__() is finished')

    def populateTree(self, versions):
        """populates tree with root versions
        """
        logger.debug('VersionTreeModel.populateTree() is started')
        self.setColumnCount(7)
        self.setHorizontalHeaderLabels(
            ['Do Update?', 'Thumbnail', 'Task', 'Take', 'Current', 'Latest',
             'Action', 'Updated By', 'Notes']
        )

        self.root_versions = versions
        for version in versions:
            self.appendRow(
                VersionItem.generate_version_row(None, self, version)
            )

        logger.debug('VersionTreeModel.populateTree() is finished')

    def canFetchMore(self, index):
        logger.debug(
            'VersionTreeModel.canFetchMore() is started for index: %s' % index
        )
        if not index.isValid():
            return_value = False
        else:
            item = self.itemFromIndex(index)
            return_value = item.canFetchMore()
        logger.debug(
            'VersionTreeModel.canFetchMore() is finished for index: %s' % index
        )
        return return_value

    def fetchMore(self, index):
        """fetches more elements
        """
        logger.debug(
            'VersionTreeModel.canFetchMore() is started for index: %s' % index
        )
        if index.isValid():
            item = self.itemFromIndex(index)
            item.fetchMore()
        logger.debug(
            'VersionTreeModel.canFetchMore() is finished for index: %s' % index
        )

    def hasChildren(self, index):
        """returns True or False depending on to the index and the item on the
        index
        """
        logger.debug(
            'VersionTreeModel.hasChildren() is started for index: %s' % index
        )
        if not index.isValid():
            return_value = len(self.root_versions) > 0
        else:
            if self.flat_view:
                return False
            else:
                item = self.itemFromIndex(index)
                return_value = False
                if item:
                    return_value = item.hasChildren()
        logger.debug(
            'VersionTreeModel.hasChildren() is finished for index: %s' % index
        )
        return return_value


class VersionTreeView(QtWidgets.QTreeView):
    """A custom tree view to display Version info
    """

    def __init__(self, *args, **kwargs):
        super(VersionTreeView, self).__init__(*args, **kwargs)

        # TODO: Implement this as a class with all its context menus etc.


class TaskTreeView(QtWidgets.QTreeView):
    """A custom tree view to display Tasks info
    """

    def __init__(self, *args, **kwargs):
        self.project = kwargs.pop('project', None)

        super(TaskTreeView, self).__init__(*args, **kwargs)
        self.is_updating = False
        self.user = None
        self.user_tasks_only = False

        self.setup_signals()

    def setup_signals(self):
        """connects the signals to slots
        """
        # fit column 0 on expand/collapse
        QtCore.QObject.connect(
            self,
            QtCore.SIGNAL('expanded(QModelIndex)'),
            self.auto_fit_column
        )

        QtCore.QObject.connect(
            self,
            QtCore.SIGNAL('collapsed(QModelIndex)'),
            self.auto_fit_column
        )

        # custom context menu for the tasks_treeView
        self.setContextMenuPolicy(
            QtCore.Qt.CustomContextMenu
        )

        QtCore.QObject.connect(
            self,
            QtCore.SIGNAL("customContextMenuRequested(const QPoint&)"),
            self.show_context_menu
        )

    def replace_with_other(self, layout, index, tree_view=None):
        """Replaces the given tree_view with itself

        :param layout: The QtGui.QLayout of the parent of the original
          QTreeView
        :param index: The item index.
        :param tree_view: The QtWidgets.QTreeView to replace with
        :return:
        """
        if tree_view:
            tree_view.deleteLater()
        layout.insertWidget(index, self)
        return self

    def auto_fit_column(self):
        """fits columns to content
        """
        self.resizeColumnToContents(0)

    def fill(self, user=None):
        """fills the tree view with data
        """
        logger.debug('start filling tasks_treeView')

        logger.debug('creating a new model')
        if not self.project:
            from stalker import Project
            projects = Project.query.order_by(Project.name).all()
        else:
            projects = [self.project]

        logger.debug('projects: %s' % projects)

        task_tree_model = TaskTreeModel()
        self.user = user
        task_tree_model.user = user
        task_tree_model.user_tasks_only = self.user_tasks_only
        task_tree_model.populateTree(projects)
        self.setModel(task_tree_model)

        # self.setModel(task_tree_model)
        self.is_updating = False
        logger.debug('finished filling tasks_treeView')

    def show_context_menu(self, position):
        """the custom context menu
        """
        # convert the position to global screen position
        global_position = self.mapToGlobal(position)

        index = self.indexAt(position)
        model = self.model()
        item = model.itemFromIndex(index)
        logger.debug('itemAt(position) : %s' % item)

        if not item:
            return

        if not hasattr(item, 'task_id'):
            return

        task_id = item.task_id
        if not task_id:
            return

        from stalker import SimpleEntity, Task, Project
        # TODO: Update this to use only task_id
        entity = SimpleEntity.query.get(task_id)
        if not entity:
            return

        # create the menu
        menu = QtWidgets.QMenu()  # Open in browser
        menu.addAction('Open In Web Browser...')
        menu.addAction('Copy URL')
        menu.addAction('Copy ID to clipboard')

        from anima import is_power_user
        # logged_in_user = self.get_logged_in_user()
        logged_in_user = model.user
        if isinstance(entity, Task):
            # this is a task
            task = entity
            from stalker import Status
            status_wfd = Status.query.filter(Status.code == 'WFD').first()
            status_prev = Status.query.filter(Status.code == 'PREV').first()
            status_cmpl = Status.query.filter(Status.code == 'CMPL').first()
            if logged_in_user in task.resources \
               and task.status not in [status_wfd, status_prev, status_cmpl]:
                menu.addSeparator()
                menu.addAction('Create TimeLog...')

            # update task and create child task menu items
            if is_power_user(logged_in_user):
                menu.addSeparator()
                menu.addAction('Update Task...')
                menu.addAction('Create Child Task...')
                menu.addAction('Duplicate Task Hierarchy...')
                menu.addAction('Delete Task...')

            menu.addSeparator()

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

        elif isinstance(entity, Project):
            # this is a project!
            project = entity
            if is_power_user(logged_in_user):
                menu.addSeparator()
                menu.addAction('Update Project...')
                menu.addSeparator()
                menu.addAction('Create Child Task...')

        try:
            # PySide and PySide2
            accepted = QtWidgets.QDialog.DialogCode.Accepted
        except AttributeError:
            # PyQt4
            accepted = QtWidgets.QDialog.Accepted

        selected_item = menu.exec_(global_position)
        if selected_item:
            choice = selected_item.text()
            import anima
            url = 'http://%s/%ss/%s/view' % (
                anima.stalker_server_internal_address,
                entity.entity_type.lower(),
                entity.id
            )
            if choice == 'Open In Web Browser...':
                import webbrowser
                webbrowser.open(url)
            elif choice == 'Copy URL':
                clipboard = QtWidgets.QApplication.clipboard()
                clipboard.setText(url)

                # and warn the user about a new version is created and the
                # clipboard is set to the new version full path
                QtWidgets.QMessageBox.warning(
                    self,
                    "URL Copied To Clipboard",
                    "URL:<br><br>%s<br><br>is copied to clipboard!" %
                    url,
                    QtWidgets.QMessageBox.Ok
                )
            elif choice == 'Copy ID to clipboard':
                clipboard = QtWidgets.QApplication.clipboard()
                clipboard.setText('%s' % entity.id)

                # and warn the user about a new version is created and the
                # clipboard is set to the new version full path
                QtWidgets.QMessageBox.warning(
                    self,
                    "ID Copied To Clipboard",
                    "ID %s is copied to clipboard!" % entity.id,
                    QtWidgets.QMessageBox.Ok
                )

            elif choice == 'Create TimeLog...':
                from anima.ui import time_log_dialog
                time_log_dialog_main_dialog = time_log_dialog.MainDialog(
                    parent=self,
                    task=entity,
                )
                time_log_dialog_main_dialog.exec_()
                result = time_log_dialog_main_dialog.result()
                time_log_dialog_main_dialog.deleteLater()

                if result == accepted:
                    # refresh the task list
                    self.fill(self.user)

                    # reselect the same task
                    self.find_and_select_entity_item(entity)

            elif choice == 'Update Task...':
                from anima.ui import task_dialog
                task_main_dialog = task_dialog.MainDialog(
                    parent=self,
                    task=entity
                )
                task_main_dialog.exec_()
                result = task_main_dialog.result()
                task_main_dialog.deleteLater()

                # refresh the task list
                if result == accepted:
                    self.fill(self.user)

                    # reselect the same task
                    self.find_and_select_entity_item(entity)

            elif choice == 'Create Child Task...':
                from anima.ui import task_dialog
                task_main_dialog = task_dialog.MainDialog(
                    parent=self,
                    parent_task=entity
                )
                task_main_dialog.exec_()
                result = task_main_dialog.result()
                task = task_main_dialog.task
                task_main_dialog.deleteLater()

                if result == accepted and task:
                    # refresh the task list
                    self.fill(self.user)

                    # reselect the same task
                    self.find_and_select_entity_item(task)

            elif choice == 'Duplicate Task Hierarchy...':
                QtWidgets.QMessageBox.warning(
                    self,
                    "Not Implemented!",
                    "Not implemented yet!"
                )
            elif choice == 'Delete Task...':
                QtWidgets.QMessageBox.warning(
                    self,
                    "Not Implemented!",
                    "Not implemented yet!"
                )
            elif choice == 'Update Project...':
                from anima.ui import project_dialog
                project_main_dialog = project_dialog.MainDialog(
                    parent=self,
                    project=entity
                )
                project_main_dialog.exec_()
                result = project_main_dialog.result()

                # refresh the task list
                if result == accepted:
                    self.fill(self.user)

                    # reselect the same task
                    self.find_and_select_entity_item(entity)

                project_main_dialog.deleteLater()

            else:
                # go to the dependencies
                dep_task = selected_item.task
                self.find_and_select_entity_item(
                    dep_task,
                    self
                )

    def find_and_select_entity_item(self, task, tree_view=None):
        """finds and selects the task in the given tree_view item
        """
        if not task:
            return

        if not tree_view:
            tree_view = self

        item = self.load_task_item_hierarchy(task, tree_view)

        selection_model = self.selectionModel()
        if not item:
            selection_model.clearSelection()
            return

        try:
            selection_model.select(
                item.index(),
                QtGui.QItemSelectionModel.ClearAndSelect
            )
        except AttributeError:  # Fix for Qt5
            selection_model.select(
                item.index(),
                QtCore.QItemSelectionModel.ClearAndSelect
            )

        self.setCurrentIndex(item.index())

        self.scrollTo(
            item.index(), QtWidgets.QAbstractItemView.PositionAtBottom
        )
        return item

    def load_task_item_hierarchy(self, task, tree_view):
        """loads the TaskItem related to the given task in the given tree_view

        :return: TaskItem instance
        """
        if not task:
            return

        self.is_updating = True
        item = self.find_entity_item(task)
        if not item:
            # the item is not loaded to the UI yet
            # start loading its parents
            # start from the project
            item = self.find_entity_item(task.project, tree_view)
            logger.debug('item for project: %s' % item)

            if item:
                tree_view.setExpanded(item.index(), True)

            if task.parents:
                # now starting from the most outer parent expand the tasks
                for parent in task.parents:
                    item = self.find_entity_item(parent, tree_view)

                    if item:
                        tree_view.setExpanded(item.index(), True)

            # finally select the task
            item = self.find_entity_item(task, tree_view)

            if not item:
                # still no item
                logger.debug('can not find item')

        self.is_updating = False
        return item

    def find_entity_item(self, entity, tree_view=None):
        """finds the item related to the stalker entity in the given
        QtTreeView
        """
        if not entity:
            return None

        if tree_view is None:
            tree_view = self

        indexes = self.get_item_indices_containing_text(entity.name, tree_view)
        model = tree_view.model()
        logger.debug('items matching name : %s' % indexes)
        for index in indexes:
            item = model.itemFromIndex(index)
            if item:
                if item.task_id == entity.id:
                    return item
        return None

    @classmethod
    def get_item_indices_containing_text(cls, text, tree_view):
        """returns the indexes of the item indices containing the given text
        """
        model = tree_view.model()
        logger.debug('searching for text : %s' % text)
        return model.match(
            model.index(0, 0),
            0,
            text,
            -1,
            QtCore.Qt.MatchRecursive
        )

    def get_task_id(self):
        """returns the task from the UI, it is an task, asset, shot, sequence
        or project
        """
        task_id = None
        selection_model = self.selectionModel()
        logger.debug('selection_model: %s' % selection_model)

        indexes = selection_model.selectedIndexes()
        logger.debug('selected indexes : %s' % indexes)

        if indexes:
            current_index = indexes[0]
            logger.debug('current_index : %s' % current_index)

            item_model = self.model()
            current_item = item_model.itemFromIndex(current_index)

            if current_item:
                task_id = current_item.task_id
                # if task_id:
                #     from stalker import db, Task
                #     task = Task.query.get(task_id)

        logger.debug('task_id: %s' % task_id)
        return task_id


class TaskItem(QtGui.QStandardItem):
    """Implements the Task as a QStandardItem
    """

    task_entity_types = ['Task', 'Asset', 'Shot', 'Sequence']

    def __init__(self, *args, **kwargs):
        QtGui.QStandardItem.__init__(self, *args, **kwargs)
        logger.debug(
            'TaskItem.__init__() is started for item: %s' % self.text()
        )
        self.loaded = False

        self.task_id = None
        self.task_name = None
        self.task_entity_type = None
        self.task_has_children = None
        self.task_children_data = None

        self.parent = None
        self.fetched_all = False
        self.setEditable(False)
        self.user_id = None
        self.user_name = None
        self.user_tasks_only = False
        logger.debug(
            'TaskItem.__init__() is finished for item: %s' % self.text()
        )

    def clone(self):
        """returns a copy of this item
        """
        logger.debug('TaskItem.clone() is started for item: %s' % self.text())
        new_item = TaskItem()
        new_item.task_id = self.task_id
        new_item.parent = self.parent
        new_item.fetched_all = self.fetched_all
        logger.debug('TaskItem.clone() is finished for item: %s' % self.text())
        return new_item

    def canFetchMore(self):
        logger.debug(
            'TaskItem.canFetchMore() is started for item: %s' % self.text()
        )
        return_value = False
        if self.task_id and not self.fetched_all:
            from stalker import db, SimpleEntity, Task
            if self.task_name is None:
                self.task_name, self.task_entity_type = \
                    db.DBSession.query(
                        SimpleEntity.name,
                        SimpleEntity.entity_type
                    )\
                    .filter(SimpleEntity.id == self.task_id)\
                    .first()

            if self.task_entity_type in self.task_entity_types:
                if self.task_has_children is None:
                    self.task_has_children = \
                        Task.query\
                            .filter(Task.parent_id == self.task_id)\
                            .count() > 0
                return_value = self.task_has_children
            elif self.task_entity_type == 'Project':
                if self.task_has_children is None:
                    self.task_has_children = \
                        Task.query\
                            .filter(Task.project_id == self.task_id)\
                            .filter(Task.parent_id == None)\
                            .count() > 0
                return_value = self.task_has_children
        else:
            return_value = False
        logger.debug(
            'TaskItem.canFetchMore() is finished for item: %s' % self.text()
        )
        return return_value

    def fetchMore(self):
        logger.debug(
            'TaskItem.fetchMore() is started for item: %s' % self.text()
        )

        if self.canFetchMore():
            tasks = []
            from stalker import db, SimpleEntity, Task

            if self.task_name is None:
                self.task_name, self.task_entity_type = \
                    db.DBSession \
                    .query(SimpleEntity.name, SimpleEntity.entity_type) \
                    .filter(SimpleEntity.id == self.task_id) \
                    .first()

            if self.task_children_data is None:
                if self.task_entity_type in self.task_entity_types:
                    self.task_children_data = db.DBSession \
                        .query(
                            Task.id,
                            Task.name,
                            Task.entity_type,
                            Task.status_id
                        ) \
                        .filter(Task.parent_id == self.task_id) \
                        .order_by(Task.name) \
                        .all()

                elif self.task_entity_type == 'Project':
                    self.task_children_data = db.DBSession\
                        .query(
                            Task.id,
                            Task.name,
                            Task.entity_type,
                            Task.status_id
                        ) \
                        .filter(Task.parent_id == None) \
                        .filter(Task.project_id == self.task_id) \
                        .order_by(Task.name) \
                        .all()

                tasks = self.task_children_data

            # # model = self.model() # This will cause a SEGFAULT
            # # TODO: update it later on

            # start = time.time()
            from anima import status_colors_by_id
            task_items = []
            for task in tasks:
                task_item = TaskItem(0, 3)
                task_item.parent = self
                task_item.task_id = task[0]
                task_item.user_id = self.user_id
                task_item.user_tasks_only = self.user_tasks_only

                # set the font
                task_item.setText(task[1])

                # color with task status
                task_item.setData(
                    QtGui.QColor(
                        *status_colors_by_id[task[3]]
                    ),
                    QtCore.Qt.BackgroundRole
                )

                # use black text
                task_item.setForeground(
                    QtGui.QBrush(QtGui.QColor(0, 0, 0))
                )

                task_items.append(task_item)

            if task_items:
                self.appendRows(task_items)

            self.fetched_all = True

        logger.debug(
            'TaskItem.fetchMore() is finished for item: %s' % self.text()
        )

    def hasChildren(self):
        logger.debug(
            'TaskItem.hasChildren() is started for item: %s' % self.text()
        )

        if self.task_id:
            from stalker import db, SimpleEntity, Task
            if self.task_name is None:
                self.task_name, self.task_entity_type = \
                    db.DBSession \
                    .query(SimpleEntity.name, SimpleEntity.entity_type) \
                    .filter(SimpleEntity.id == self.task_id) \
                    .first()
            if self.task_entity_type in self.task_entity_types:
                if self.task_has_children is None:
                    self.task_has_children = db.DBSession.query(Task.id)\
                        .filter(Task.parent_id == self.task_id)\
                        .count() > 0
                return_value = self.task_has_children
            elif self.task_entity_type == 'Project':
                if self.task_has_children is None:
                    self.task_has_children = \
                        db.DBSession.query(Task.id)\
                            .filter(Task.project_id == self.task_id)\
                            .filter(Task.parent_id == None)\
                            .count() > 0
                return_value = self.task_has_children

            else:
                return_value = False
        else:
            return_value = False

        logger.debug(
            'TaskItem.hasChildren() is finished for item: %s' % self.text()
        )
        return return_value

    def type(self, *args, **kwargs):
        """
        """
        return QtGui.QStandardItem.UserType + 1


class TaskTreeModel(QtGui.QStandardItemModel):
    """Implements the model view for the task hierarchy
    """

    def __init__(self, *args, **kwargs):
        QtGui.QStandardItemModel.__init__(self, *args, **kwargs)
        logger.debug('TaskTreeModel.__init__() is started')
        self.user_id = None
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

        # item_prototype = TaskItem()
        # self.setItemPrototype(item_prototype)
        # root_item = TaskItem(0, 3)
        # root_item.setColumnCount(3)
        # self.appendRow(root_item)

        for project in projects:
            project_item = TaskItem(0, 3)
            project_item.parent = None
            project_item.setColumnCount(3)
            project_item.setText(project.name)
            project_item.task_id = project.id
            project_item.user_id = self.user.id if self.user else -1
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
            # root_item.appendRow(project_item)

        logger.debug('TaskTreeModel.populateTree() is finished')

    def canFetchMore(self, index):
        logger.debug(
            'TaskTreeModel.canFetchMore() is started for index: %s' % index
        )
        if not index.isValid():
            return_value = False
        else:
            item = self.itemFromIndex(index)
            return_value = item.canFetchMore()
        logger.debug(
            'TaskTreeModel.canFetchMore() is finished for index: %s' % index
        )
        return return_value

    def fetchMore(self, index):
        """fetches more elements
        """
        logger.debug(
            'TaskTreeModel.canFetchMore() is started for index: %s' % index
        )
        if index.isValid():
            item = self.itemFromIndex(index)
            item.fetchMore()
        logger.debug(
            'TaskTreeModel.canFetchMore() is finished for index: %s' % index
        )

    def hasChildren(self, index):
        """returns True or False depending on to the index and the item on the
        index
        """
        logger.debug(
            'TaskTreeModel.hasChildren() is started for index: %s' % index
        )
        if not index.isValid():
            from stalker import db, Project, ProjectUser
            if self.user_tasks_only:
                if self.user_id:
                    projects_count = db.DBSession.query(ProjectUser.id)\
                        .filter(ProjectUser.user_id == self.user_id)\
                        .count()
                else:
                    projects_count = 0
            else:
                projects_count = db.DBSession.query(Project.id).count()
            return_value = projects_count > 0
        else:
            item = self.itemFromIndex(index)
            return_value = False
            if item:
                return_value = item.hasChildren()
        logger.debug(
            'TaskTreeModel.hasChildren() is finished for index: %s' % index
        )
        return return_value


class TakesListWidget(QtWidgets.QListWidget):
    """A specialized QListWidget variant used in Take names.
    """

    def __init__(self, parent=None, *args, **kwargs):
        QtWidgets.QListWidget.__init__(self, parent, *args, **kwargs)
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
        from stalker import defaults
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
        from stalker import Version
        take_name = Version._format_take_name(take_name)

        # if the given take name is in the list don't add it
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
        QtWidgets.QListWidget.clear(self)


class TaskNameCompleter(QtWidgets.QCompleter):
    def __init__(self, parent):
        QtWidgets.QCompleter.__init__(self, [], parent)

    def update(self, completion_prefix):
        from stalker import Task
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


class TimeEdit(QtWidgets.QTimeEdit):
    """Customized time edit widget
    """

    def __init__(self, *args, **kwargs):
        self.resolution = None
        if 'resolution' in kwargs:
            self.resolution = kwargs['resolution']
            kwargs.pop('resolution')

        super(TimeEdit, self).__init__(*args, **kwargs)

    def stepBy(self, step):
        """Custom stepBy function

        :param step:
        :return:
        """
        if self.currentSectionIndex() == 1:
            if step < 0:
                # auto update the hour section to the next hour
                minute = self.time().minute()
                if minute == 0:
                    # increment the hour section by one
                    self.setTime(
                        QtCore.QTime(
                            self.time().hour() - 1,
                            60 - self.resolution
                        )
                    )
                else:
                    self.setTime(
                        QtCore.QTime(
                            self.time().hour(),
                            minute - self.resolution
                        )
                    )

            else:
                # auto update the hour section to the next hour
                minute = self.time().minute()
                if minute == (60 - self.resolution):
                    # increment the hour section by one
                    self.setTime(
                        QtCore.QTime(
                            self.time().hour()+1,
                            0
                        )
                    )
                else:
                    self.setTime(
                        QtCore.QTime(
                            self.time().hour(),
                            minute + self.resolution
                        )
                    )
        else:
            if step < 0:
                if self.time().hour() != 0:
                    super(TimeEdit, self).stepBy(step)
            else:
                if self.time().hour() != 23:
                    super(TimeEdit, self).stepBy(step)


class TaskComboBox(QtWidgets.QComboBox):
    """A customized combobox that holds Tasks
    """

    def __init__(self, *args, **kwargs):
        super(TaskComboBox, self).__init__(*args, **kwargs)

    def showPopup(self, *args, **kwargs):
        self.view().setMinimumWidth(self.view().sizeHintForColumn(0))
        super(TaskComboBox, self).showPopup(*args, **kwargs)

    @classmethod
    def generate_task_name(cls, task):
        """Generates task names
        :param task:
        :return:
        """
        if task:
            return '%s (%s)' % (
                task.name,
                '%s | %s' % (
                    task.project.name,
                    ' | '.join(map(lambda x: x.name, task.parents))
                )
            )
        else:
            return ''

    def addTasks(self, tasks):
        """Overridden addItems method

        :param tasks: A list of Tasks
        :return:
        """
        # prepare task labels
        task_labels = []
        for task in tasks:
            # this is dirty
            task_label = self.generate_task_name(task)
            self.addItem(task_label, task)

    def currentTask(self):
        """returns the current task
        """
        return self.itemData(self.currentIndex())

    def setCurrentTask(self, task):
        """sets the current task to the given task
        """
        for i in range(self.count()):
            t = self.itemData(i)
            if t.id == task.id:
                self.setCurrentIndex(i)
                return

        raise IndexError('Task not found!')


class RecentFilesComboBox(QtWidgets.QComboBox):
    """A Fixed with popup box comboBox alternative
    """

    def showPopup(self, *args, **kwargs):
        view = self.view()
        column_size_hint = view.sizeHintForColumn(0)
        view.setMinimumWidth(column_size_hint + 20)
        super(RecentFilesComboBox, self).showPopup(*args, **kwargs)


class VersionsTableWidget(QtWidgets.QTableWidget):
    """A QTableWidget derivative specialized to hold version data
    """

    def __init__(self, parent=None, *args, **kwargs):
        QtWidgets.QTableWidget.__init__(self, parent, *args, **kwargs)

        self.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.setAlternatingRowColors(True)
        self.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.setShowGrid(False)
        self.setColumnCount(5)
        self.setObjectName("previous_versions_tableWidget")
        self.setColumnCount(5)
        self.setRowCount(0)
        self.setHorizontalHeaderItem(0, QtWidgets.QTableWidgetItem())
        self.setHorizontalHeaderItem(1, QtWidgets.QTableWidgetItem())
        self.setHorizontalHeaderItem(2, QtWidgets.QTableWidgetItem())
        self.setHorizontalHeaderItem(3, QtWidgets.QTableWidgetItem())
        self.setHorizontalHeaderItem(4, QtWidgets.QTableWidgetItem())
        self.horizontalHeader().setStretchLastSection(True)
        self.verticalHeader().setStretchLastSection(False)

        tool_tip_html = \
            "<html><head/><body><p>Right click to:</p><ul style=\"" \
            "margin-top: 0px; margin-bottom: 0px; margin-left: 0px; " \
            "margin-right: 0px; -qt-list-indent: 1;\"><li><span style=\" " \
            "font-weight:600;\">Copy Path</span></li><li><span style=\" " \
            "font-weight:600;\">Browse Path</span></li><li><span style=\" " \
            "font-weight:600;\">Change Description</span></li></ul>" \
            "<p>Double click to:</p><ul style=\"margin-top: 0px; " \
            "margin-bottom: 0px; margin-left: 0px; margin-right: 0px; " \
            "-qt-list-indent: 1;\"><li style=\" margin-top:12px; " \
            "margin-bottom:12px; margin-left:0px; margin-right:0px; " \
            "-qt-block-indent:0; text-indent:0px;\"><span style=\" " \
            "font-weight:600;\">Open</span></li></ul></body></html>"

        try:
            self.setToolTip(
                QtWidgets.QApplication.translate(
                    "Dialog",
                    tool_tip_html,
                    None,
                    QtWidgets.QApplication.UnicodeUTF8
                )
            )
        except AttributeError:
            self.setToolTip(
                QtWidgets.QApplication.translate(
                    "Dialog",
                    tool_tip_html,
                    None
                )
            )

        self.versions = []
        self.labels = [
            '#',
            'App',
            'Created By',
            'Updated By',
            'Size',
            'Date',
            'Description',
        ]
        self.setColumnCount(len(self.labels))

    def clear(self):
        """overridden clear method
        """
        QtWidgets.QTableWidget.clear(self)
        self.versions = []

        # reset the labels
        self.setHorizontalHeaderLabels(self.labels)

    def select_version(self, version):
        """selects the given version in the list
        """
        # select the version in the previous version list
        index = -1
        for i, prev_version in enumerate(self.versions):
            if self.versions[i].id == version.id:
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
        import os
        import datetime

        logger.debug('VersionsTableWidget.update_content() is started')

        self.clear()
        self.versions = versions
        self.setRowCount(len(versions))

        def set_published_font(item):
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
        from anima import user_names_lut
        for i, version in enumerate(versions):
            is_published = version.is_published
            absolute_full_path = os.path.normpath(
                os.path.expandvars(version.full_path)
            ).replace('\\', '/')
            version_file_exists = os.path.exists(absolute_full_path)

            c = 0

            # ------------------------------------
            # version_number
            item = QtWidgets.QTableWidgetItem(str(version.version_number))
            # align to center and vertical center
            item.setTextAlignment(0x0004 | 0x0080)

            if is_published:
                set_published_font(item)

            if not version_file_exists:
                item.setBackground(QtGui.QColor(64, 0, 0))

            self.setItem(i, c, item)
            c += 1
            # ------------------------------------

            # ------------------------------------
            # created_with
            item = QtWidgets.QTableWidgetItem()
            if version.created_with:
                from anima.ui import utils as ui_utils
                item.setIcon(ui_utils.get_icon(version.created_with.lower()))

            if is_published:
                set_published_font(item)

            if not version_file_exists:
                item.setBackground(QtGui.QColor(64, 0, 0))

            self.setItem(i, c, item)
            c += 1
            # ------------------------------------

            # ------------------------------------
            # user.name
            created_by = ''
            if version.created_by_id:
                created_by = user_names_lut[version.created_by_id]
            item = QtWidgets.QTableWidgetItem(created_by)
            # align to left and vertical center
            item.setTextAlignment(0x0001 | 0x0080)

            if is_published:
                set_published_font(item)

            if not version_file_exists:
                item.setBackground(QtGui.QColor(64, 0, 0))

            self.setItem(i, c, item)
            c += 1
            # ------------------------------------

            # ------------------------------------
            # user.name
            updated_by = ''
            if version.updated_by_id:
                updated_by = user_names_lut[version.updated_by_id]
            item = QtWidgets.QTableWidgetItem(updated_by)
            # align to left and vertical center
            item.setTextAlignment(0x0001 | 0x0080)

            if is_published:
                set_published_font(item)

            if not version_file_exists:
                item.setBackground(QtGui.QColor(64, 0, 0))

            self.setItem(i, c, item)
            c += 1
            # ------------------------------------

            # ------------------------------------
            # file size

            # get the file size
            #file_size_format = "%.2f MB"
            file_size = -1
            if version_file_exists:
                file_size = float(
                    os.path.getsize(absolute_full_path)) / 1048576

            from stalker import defaults
            item = QtWidgets.QTableWidgetItem(
                defaults.file_size_format % file_size
            )
            # align to left and vertical center
            item.setTextAlignment(0x0001 | 0x0080)

            if is_published:
                set_published_font(item)

            if not version_file_exists:
                item.setBackground(QtGui.QColor(64, 0, 0))

            self.setItem(i, c, item)
            c += 1
            # ------------------------------------

            # ------------------------------------
            # date

            # get the file date
            file_date = datetime.datetime.today()
            if version_file_exists:
                file_date = datetime.datetime.fromtimestamp(
                    os.path.getmtime(absolute_full_path)
                )
            item = QtWidgets.QTableWidgetItem(
                file_date.strftime(defaults.date_time_format)
            )

            # align to left and vertical center
            item.setTextAlignment(0x0001 | 0x0080)

            if is_published:
                set_published_font(item)

            if not version_file_exists:
                item.setBackground(QtGui.QColor(64, 0, 0))

            self.setItem(i, c, item)
            c += 1
            # ------------------------------------

            # ------------------------------------
            # description
            item = QtWidgets.QTableWidgetItem(version.description)
            # align to left and vertical center
            item.setTextAlignment(0x0001 | 0x0080)

            if is_published:
                set_published_font(item)

            if not version_file_exists:
                item.setBackground(QtGui.QColor(64, 0, 0))

            self.setItem(i, c, item)
            c += 1
            # ------------------------------------

        # resize the first column
        self.resizeRowsToContents()
        self.resizeColumnsToContents()
        self.resizeRowsToContents()
        logger.debug('VersionsTableWidget.update_content() is finished')


class ValidatedLineEdit(QtWidgets.QLineEdit):
    """A custom line edit that can display an icon
    """

    def __init__(self, *args, **kwargs):
        self.message_field = kwargs.pop('message_field', None)
        super(ValidatedLineEdit, self).__init__(*args, **kwargs)
        self.message_field.setVisible(False)
        self.icon = None
        self.is_valid = True
        self.message = ''

    def set_valid(self):
        """sets the field valid
        """
        self.set_icon(None)
        self.is_valid = True
        self.message = ''

        if self.message_field:
            self.message_field.setVisible(False)

    def set_invalid(self, message=''):
        """sets the field invalid
        """
        self.icon = self.style()\
            .standardIcon(QtWidgets.QStyle.SP_MessageBoxCritical)
        self.set_icon(self.icon)

        self.is_valid = False

        if self.message_field:
            self.message_field.setText(message)
            if self.isVisible():
                self.message_field.setVisible(True)

    def set_icon(self, icon=None):
        """Sets the icon

        :param icon: QIcon instance
        :return:
        """
        self.icon = icon
        if icon is None:
            self.setTextMargins(1, 1, 1, 1)
        else:
            self.setTextMargins(1, 1, 20, 1)

    def paintEvent(self, event):
        """Overridden paint event

        :param event: QPaintEvent instance
        :return:
        """
        super(ValidatedLineEdit, self).paintEvent(event)
        if self.icon is not None:
            painter = QtGui.QPainter(self)
            pixmap = self.icon.pixmap(self.height() - 6, self.height() - 6)

            x = self.width() - self.height() + 4

            painter.drawPixmap(x, 3, pixmap)
            painter.setPen(QtGui.QColor("lightgrey"))
            painter.drawLine(x - 2, 3, x - 2, self.height() - 4)


class DoubleListWidget(object):
    """This is a Widget that has two QListWidgets.
    """

    def __init__(self, dialog=None, parent_layout=None, primary_label_text='',
                 secondary_label_text=''):
        """
        :param dialog: QDialog instance that this is the child of.
        :param parent_layout: The QLayout instance to add this widgets to
        :param str primary_label_text: The label of the primary list
        :param str secondary_label_text: The label of the secondary list
        """
        self.dialog = dialog
        self.parent_layout = parent_layout

        # Layouts
        self.main_layout = None
        self.button_layout = None
        self.primary_widgets_layout = None
        self.secondary_widgets_layout = None

        # Widgets
        self.primary_list_widget = None
        self.secondary_list_widget = None
        self.primary_to_secondary_push_button = None
        self.secondary_to_primary_push_button = None

        self.primary_label = None
        self.secondary_label = None

        # Data
        self.primary_label_text = primary_label_text
        self.secondary_label_text = secondary_label_text

        self.__init__ui()

    def __init__ui(self):
        """creates the Widgets
        """
        # create a horizontal layout to hold the widgets
        self.main_layout = QtWidgets.QHBoxLayout()

        # ----------------------------------
        # Primary Widgets Layout
        self.primary_widgets_layout = QtWidgets.QVBoxLayout()

        # label
        self.primary_label = QtWidgets.QLabel(self.dialog)
        self.primary_label.setText(self.primary_label_text)
        self.primary_label.setAlignment(QtCore.Qt.AlignCenter)
        self.primary_widgets_layout.addWidget(self.primary_label)

        # list widget
        self.primary_list_widget = QtWidgets.QListWidget(self.dialog)
        self.primary_widgets_layout.addWidget(self.primary_list_widget)
        self.main_layout.addLayout(self.primary_widgets_layout)

        # ----------------------------------
        # Button Layout
        self.button_layout = QtWidgets.QVBoxLayout()
        self.button_layout.insertStretch(0, 0)
        self.primary_to_secondary_push_button = \
            QtWidgets.QPushButton('>>', parent=self.dialog)
        self.secondary_to_primary_push_button = \
            QtWidgets.QPushButton('<<', parent=self.dialog)

        self.primary_to_secondary_push_button.setMaximumSize(25, 16777215)
        self.secondary_to_primary_push_button.setMaximumSize(25, 16777215)

        self.button_layout.addWidget(self.primary_to_secondary_push_button)
        self.button_layout.addWidget(self.secondary_to_primary_push_button)

        self.button_layout.insertStretch(3, 0)
        self.main_layout.addLayout(self.button_layout)

        # ----------------------------------
        # Secondary Widgets Layout
        self.secondary_widgets_layout = QtWidgets.QVBoxLayout()

        # label
        self.secondary_label = QtWidgets.QLabel(self.dialog)
        self.secondary_label.setText(self.secondary_label_text)
        self.secondary_label.setAlignment(QtCore.Qt.AlignCenter)

        # list widget
        self.secondary_widgets_layout.addWidget(self.secondary_label)

        self.secondary_list_widget = QtWidgets.QListWidget(self.dialog)
        self.secondary_widgets_layout.addWidget(self.secondary_list_widget)
        self.main_layout.addLayout(self.secondary_widgets_layout)

        self.main_layout.setStretch(0, 1)
        self.main_layout.setStretch(1, 0)
        self.main_layout.setStretch(2, 1)

        self.parent_layout.addLayout(self.main_layout)

        # Create signals
        QtCore.QObject.connect(
            self.primary_to_secondary_push_button,
            QtCore.SIGNAL('clicked()'),
            self.primary_to_secondary_push_button_clicked
        )

        QtCore.QObject.connect(
            self.secondary_to_primary_push_button,
            QtCore.SIGNAL('clicked()'),
            self.secondary_to_primary_push_button_clicked
        )

    def add_primary_items(self, items):
        """Adds the given items to the primary list

        :param items:
        :return:
        """
        self.primary_list_widget.addItems(items)

    def add_secondary_items(self, items):
        """Adds the given items to the secondary list

        :param items:
        :return:
        """
        self.secondary_list_widget.addItems(items)

    def clear(self):
        """clears both of the lists
        """
        self.primary_list_widget.clear()
        self.secondary_list_widget.clear()

    def primary_to_secondary_push_button_clicked(self):
        """runs when the primary_to_secondary_push_button is clicked
        """
        # get the current item selected in primary list
        index = self.primary_list_widget.currentRow()
        item = self.primary_list_widget.takeItem(index)
        self.secondary_list_widget.addItem(item)

    def secondary_to_primary_push_button_clicked(self):
        """runs when the secondary_to_primary_push_button is clicked
        """
        index = self.secondary_list_widget.currentRow()
        item = self.secondary_list_widget.takeItem(index)
        self.primary_list_widget.addItem(item)

    def primary_items(self):
        """returns the items in primary_list_widget
        """
        items = []
        for i in range(self.primary_list_widget.count()):
            items.append(self.primary_list_widget.item(i))
        return items

    def secondary_items(self):
        """returns the items in secondary_list_widget
        """
        items = []
        for i in range(self.secondary_list_widget.count()):
            items.append(self.secondary_list_widget.item(i))
        return items
