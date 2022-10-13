# -*- coding: utf-8 -*-
"""Task related views."""

from anima import logger
from anima.ui.lib import QtCore, QtWidgets
from anima.ui.menus import TaskDataContextMenuHandler
from anima.ui.models.task import TaskTreeModel

from sqlalchemy import alias

from stalker import Project, SimpleEntity, Status, Task
from stalker.db.session import DBSession


if False:
    from PySide2 import QtCore, QtWidgets


class TaskTreeView(QtWidgets.QTreeView):
    """A custom tree view to display Tasks info"""

    def __init__(self, *args, **kwargs):
        # filter non Qt kwargs
        allow_multi_selection = False
        try:
            allow_multi_selection = kwargs.pop("allow_multi_selection")
        except KeyError:
            pass

        allow_drag = False
        try:
            allow_drag = kwargs.pop("allow_drag")
        except KeyError:
            pass

        self.project = kwargs.pop("project", None)
        self.show_completed_projects = False

        context_menu_handler_class = kwargs.pop("context_menu_handler_class", None)
        if context_menu_handler_class is None:
            self.context_menu_handler = TaskDataContextMenuHandler(parent=self)
        else:
            self.context_menu_handler = context_menu_handler_class(parent=self)

        super(TaskTreeView, self).__init__(*args, **kwargs)

        self.is_updating = False

        # self.setAlternatingRowColors(True)
        self.setUniformRowHeights(True)
        self.header().setCascadingSectionResizes(True)

        # allow multiple selection
        if allow_multi_selection:
            self.setSelectionMode(self.ExtendedSelection)

        if allow_drag:
            self.setSelectionMode(self.ExtendedSelection)
            self.setDragDropMode(QtWidgets.QAbstractItemView.InternalMove)
            self.setDragEnabled(True)
            self.setAcceptDrops(True)
            self.setDropIndicatorShown(True)

        # delegate = TaskItemDelegate(self)
        # self.setItemDelegate(delegate)
        self.setup_signals()

    def setup_signals(self):
        """connects the signals to slots"""
        # fit column 0 on expand/collapse
        self.expanded.connect(self.expand_all_selected)
        self.collapsed.connect(self.collapse_all_selected)

        # custom context menu for the tasks_treeView
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)
        self.doubleClicked.connect(self.double_clicked_on_entity)

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
        """fits columns to content"""
        self.resizeColumnToContents(0)

    def fill(self):
        """fills the tree view with data"""
        logger.debug("start filling tasks_treeView")
        logger.debug("creating a new model")
        if not self.project:
            # projects = Project.query.order_by(Project.name).all()
            inner_tasks = alias(Task.__table__)
            subquery = DBSession.query(inner_tasks.c.id).filter(
                inner_tasks.c.project_id == Project.id
            )
            query = DBSession.query(
                Project.id,
                Project.name,
                Project.entity_type,
                Project.status_id,
                subquery.exists().label("has_children"),
            )
            if not self.show_completed_projects:
                status_cmpl = Status.query.filter(Status.code == "CMPL").first()
                query = query.filter(Project.status != status_cmpl)

            query = query.order_by(Project.name)
            projects = query.all()
        else:
            self.project.has_children = bool(self.project.tasks)
            projects = [self.project]

        logger.debug("projects: %s" % projects)

        # delete the old model if any
        if self.model() is not None:
            self.model().deleteLater()

        task_tree_model = TaskTreeModel()
        task_tree_model.populateTree(projects)
        self.setModel(task_tree_model)
        self.is_updating = False

        self.auto_fit_column()

        logger.debug("finished filling tasks_treeView")

    def show_context_menu(self, position):
        """Create and show the context menu.

        Args:
            position (QPoint): Menu position.
        """
        if self.context_menu_handler:
            self.context_menu_handler.show_context_menu(position)

    def double_clicked_on_entity(self, index):
        """runs when double clicked on an leaf entity

        :param index:
        :return:
        """
        model = self.model()
        item = model.itemFromIndex(index)
        if not item:
            return

        if item.hasChildren():
            return

        logger.debug("item : %s" % item)
        task_id = None
        entity = None

        try:
            if item.task:
                task_id = item.task.id
        except AttributeError:
            return

        if item.task.entity_type == "Task":

            if task_id:
                entity = SimpleEntity.query.get(task_id)

            from anima.ui.dialogs import task_dialog

            task_main_dialog = task_dialog.MainDialog(parent=self, tasks=[entity])
            task_main_dialog.exec_()
            result = task_main_dialog.result()
            task_main_dialog.deleteLater()

            try:
                # PySide and PySide2
                accepted = QtWidgets.QDialog.DialogCode.Accepted
            except AttributeError:
                # PyQt4
                accepted = QtWidgets.QDialog.Accepted

            # refresh the task list
            if result == accepted:
                # just reload the same item
                if item.parent:
                    item.parent.reload()
                else:
                    # reload the entire
                    self.fill()

                self.find_and_select_entity_item(entity)

    def find_and_select_entity_item(self, tasks, tree_view=None):
        """Find and select the task in the given tree_view item.

        :param tasks: A list of Stalker tasks. A single Task is also accepted.
        :param tree_view: QTreeView or derivative.
        """
        if not tasks:
            return

        selection_model = self.selectionModel()
        selection_model.clearSelection()
        selection_flag = QtCore.QItemSelectionModel.Select

        if not tree_view:
            tree_view = self

        if not isinstance(tasks, list):
            tasks = [tasks]

        items = []
        for task in tasks:
            item = self.load_task_item_hierarchy(task, tree_view)
            if item:
                selection_model.select(item.index(), selection_flag)
                items.append(item)

        # scroll to the first item
        if items:
            self.scrollTo(items[0].index())
        return items

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
            if isinstance(task, Task):
                item = self.find_entity_item(task.project, tree_view)
            else:
                item = self.find_entity_item(task, tree_view)
            logger.debug("item for project: %s" % item)

            if item:
                tree_view.setExpanded(item.index(), True)

            if isinstance(task, Task) and task.parents:
                # now starting from the most outer parent expand the tasks
                for parent in task.parents:
                    item = self.find_entity_item(parent, tree_view)

                    if item:
                        tree_view.setExpanded(item.index(), True)

            # finally select the task
            item = self.find_entity_item(task, tree_view)

            if not item:
                # still no item
                logger.debug("can not find item")

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
        logger.debug("items matching name : %s" % indexes)
        for index in indexes:
            item = model.itemFromIndex(index)
            if item:
                if item.task.id == entity.id:
                    return item
        return None

    @classmethod
    def get_item_indices_containing_text(cls, text, tree_view):
        """returns the indexes of the item indices containing the given text"""
        model = tree_view.model()
        logger.debug("searching for text : %s" % text)
        return model.match(model.index(0, 0), 0, text, -1, QtCore.Qt.MatchRecursive)

    def get_selected_task_items(self):
        """returns the selected TaskItems"""
        from anima.ui.models.task import TaskItem

        selection_model = self.selectionModel()
        logger.debug("selection_model: %s" % selection_model)
        indexes = selection_model.selectedIndexes()
        logger.debug("selected indexes : %s" % indexes)
        task_items = []
        if indexes:
            item_model = self.model()
            logger.debug("indexes: %s" % indexes)
            for index in indexes:
                current_item = item_model.itemFromIndex(index)
                if current_item and isinstance(current_item, TaskItem):
                    task_items.append(current_item)
        logger.debug("task_items: %s" % task_items)
        return task_items

    def get_selected_task_ids(self):
        """returns the task from the UI, it is an task, asset, shot, sequence
        or project
        """
        task_ids = []
        for item in self.get_selected_task_items():
            task_id = item.task.id
            task_ids.append(task_id)

        logger.debug("task_ids: %s" % task_ids)
        return task_ids

    def get_selected_tasks(self):
        """returns the selected tasks"""
        task_ids = self.get_selected_task_ids()
        return list(SimpleEntity.query.filter(SimpleEntity.id.in_(task_ids)).all())

    def expand_all_selected(self, index):
        """Expand all the selected items.

        Args:
            index (QModelIndex):
        """
        for item in self.get_selected_task_items():
            self.setExpanded(item.index(), True)
        self.auto_fit_column()

    def collapse_all_selected(self, index):
        """Collapse all the selected items.

        Args:
            index (QModelIndex): The model index.
        """
        for item in self.get_selected_task_items():
            self.setExpanded(item.index(), False)
        self.auto_fit_column()


class TaskTableView(QtWidgets.QTableView):
    """A QTableView variant that shows task related data."""

    def __init__(self, *args, **kwargs):
        super(TaskTableView, self).__init__(*args, **kwargs)
