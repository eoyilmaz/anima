# -*- coding: utf-8 -*-
# Copyright (c) 2012-2013, Anima Istanbul
#
# This module is part of anima-tools and is released under the BSD 2
# License: http://www.opensource.org/licenses/BSD-2-Clause

import logging
from PySide import __all__

import re

from stalker import Task, Project, defaults
from anima.pipeline.ui.lib import QtGui, QtCore
from anima.pipeline.ui.version_creator import logger

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


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
