# -*- coding: utf-8 -*-
# Copyright (c) 2012-2015, Anima Istanbul
#
# This module is part of anima-tools and is released under the BSD 2
# License: http://www.opensource.org/licenses/BSD-2-Clause

from stalker import defaults, Task, Project

from anima import logger, status_colors
from anima.ui.lib import QtGui, QtCore


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
            'VersionItem.__init__() is started for item: %s' % self.text())
        self.loaded = False
        self.version = None
        self.parent = None
        self.pseudo_model = None
        self.fetched_all = False
        self.setEditable(False)
        logger.debug(
            'VersionItem.__init__() is finished for item: %s' % self.text())

    def clone(self):
        """returns a copy of this item
        """
        logger.debug('VersionItem.clone() is started for item: %s' % self.text())
        new_item = VersionItem()
        new_item.version = self.version
        new_item.parent = self.parent
        new_item.fetched_all = self.fetched_all
        logger.debug('VersionItem.clone() is finished for item: %s' % self.text())
        return new_item

    def canFetchMore(self):
        logger.debug(
            'VersionItem.canFetchMore() is started for item: %s' % self.text())
        if self.version and not self.fetched_all:
            return_value = bool(self.version.inputs)
        else:
            return_value = False
        logger.debug(
            'VersionItem.canFetchMore() is finished for item: %s' % self.text())
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
            'VersionItem.fetchMore() is started for item: %s' % self.text())

        if self.canFetchMore():
            # model = self.model() # This will cause a SEGFAULT
            versions = sorted(self.version.inputs, key=lambda x: x.full_path)

            for version in versions:
                self.appendRow(
                    self.generate_version_row(self, self.pseudo_model, version)
                )

            self.fetched_all = True
        logger.debug(
            'VersionItem.fetchMore() is finished for item: %s' % self.text())

    def hasChildren(self):
        logger.debug(
            'VersionItem.hasChildren() is started for item: %s' % self.text())
        if self.version:
            return_value = bool(self.version.inputs)
        else:
            return_value = False
        logger.debug(
            'VersionItem.hasChildren() is finished for item: %s' % self.text())
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
            'VersionTreeModel.canFetchMore() is started for index: %s' % index)
        if not index.isValid():
            return_value = False
        else:
            item = self.itemFromIndex(index)
            return_value = item.canFetchMore()
        logger.debug(
            'VersionTreeModel.canFetchMore() is finished for index: %s' % index)
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


class VersionTreeView(QtGui.QTreeView):
    """A custom tree view to display Version info
    """

    def __init__(self, *args, **kwargs):
        super(VersionTreeView, self).__init__(*args, **kwargs)

        # TODO: Implement this as a class with all its context menus etc.


class TaskTreeView(QtGui.QTreeView):
    """A custom tree view to display Tasks info
    """

    def __init__(self, *args, **kwargs):
        super(TaskTreeView, self).__init__(*args, **kwargs)


class TaskItem(QtGui.QStandardItem):
    """Implements the Task as a QStandardItem
    """

    def __init__(self, *args, **kwargs):
        QtGui.QStandardItem.__init__(self, *args, **kwargs)
        logger.debug(
            'TaskItem.__init__() is started for item: %s' % self.text()
        )
        self.loaded = False
        self.task = None
        self.parent = None
        self.fetched_all = False
        self.setEditable(False)
        self.user = None
        self.user_tasks_only = False
        logger.debug(
            'TaskItem.__init__() is finished for item: %s' % self.text()
        )

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
            'TaskItem.canFetchMore() is started for item: %s' % self.text()
        )
        return_value = False
        if self.task and not self.fetched_all:
            if isinstance(self.task, Task):
                return_value = self.task.is_container
            elif isinstance(self.task, Project):
                return_value = len(self.task.root_tasks) > 0
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

                # color with task status
                task_item.setData(
                    QtGui.QColor(
                        *status_colors[task_item.task.status.code.lower()]
                    ),
                    QtCore.Qt.BackgroundRole
                )

                # use black text
                task_item.setForeground(
                    QtGui.QBrush(QtGui.QColor(0, 0, 0))
                )

                self.appendRow(task_item)

            self.fetched_all = True
        logger.debug(
            'TaskItem.fetchMore() is finished for item: %s' % self.text()
        )

    def hasChildren(self):
        logger.debug(
            'TaskItem.hasChildren() is started for item: %s' % self.text()
        )

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
            # root_item.appendRow(project_item)

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
            if self.user_tasks_only:
                if self.user:
                    projects = self.user.projects
                else:
                    projects = []
            else:
                projects = Project.query.all()
            return_value = len(projects) > 0
        else:
            item = self.itemFromIndex(index)
            return_value = False
            if item:
                return_value = item.hasChildren()
        logger.debug(
            'TaskTreeModel.hasChildren() is finished for index: %s' % index)
        return return_value


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
        QtGui.QListWidget.clear(self)


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
