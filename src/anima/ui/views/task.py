# -*- coding: utf-8 -*-
"""Task related views."""

from anima import logger
from anima.ui.lib import QtCore, QtWidgets
from anima.ui.menus import TaskDataContextMenuHandler
from anima.ui.models.task import TaskTreeModel

from stalker import SimpleEntity, Task


if False:
    from PySide6 import QtCore, QtWidgets


class TaskTreeView(QtWidgets.QTreeView):
    """A custom tree view to display Tasks info.

    Args:
        tasks (list): A list of :obj:`stalker.models.Task` instances or derivative.
        allow_multi_selection (bool): If set to True allows multiple selection. The
            default value is False.
        allow_editing (bool): If set to True, allows editing of items. The default value
            is False.
        horizontal_labels (list): A list of str for the horizontal labels. The default
            value is False.
        show_dependency_info (bool): If set to True, shows an extra layer of child for
            the tasks for the dependency information. Default is False.
        show_asset_and_shot_children (bool): If set to True it will show the step tasks
            for each Asset and Shot. The default value is True.
        show_takes (bool): If set to True, shows another level in the
            tree of takes information for the child task of an Asset.
        context_menu_handler_class (:obj:``ui.menus.BaseContextMenuHandler``):
            A :obj:``ui.menus.BaseContextMenuHandler`` variant to handle the
            context menus. This allows to show different context menus for different
            setups.
    """

    def __init__(
        self,
        parent=None,
        tasks=None,
        allow_multi_selection=False,
        allow_drag=False,
        allow_editing=False,
        context_menu_handler_class=None,
        horizontal_labels=None,
        show_asset_and_shot_children=True,
        show_takes=False,
        show_dependency_info=False,
    ):
        super(TaskTreeView, self).__init__(parent=parent)

        self._tasks = []

        self.horizontal_labels = horizontal_labels
        self.show_dependency_info = show_dependency_info
        self.show_asset_and_shot_children = show_asset_and_shot_children
        self.show_takes = show_takes

        if context_menu_handler_class is None:
            self.context_menu_handler = TaskDataContextMenuHandler(parent=self)
        else:
            self.context_menu_handler = context_menu_handler_class(parent=self)
        self.is_updating = False

        # self.setAlternatingRowColors(True)
        self.setUniformRowHeights(True)
        self.header().setCascadingSectionResizes(True)

        self._allow_multi_selection = False
        self.allow_multi_selection = allow_multi_selection
        self.allow_editing = allow_editing
        self._allow_drag = False
        self.allow_drag = allow_drag

        # delegate = TaskItemDelegate(self)
        # self.setItemDelegate(delegate)
        self.setup_signals()

        if tasks is None:
            tasks = []
        self.tasks = tasks

    @property
    def allow_drag(self):
        """Getter for the allow drag property.

        Returns:
            bool: The allow_drag state.
        """
        return self._allow_drag

    @allow_drag.setter
    def allow_drag(self, allow_drag):
        """Set allow_drag property.

        Args:
            allow_drag (bool): The allow_drag state.
        """
        self._allow_drag = allow_drag
        if allow_drag:
            self.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
            self.setDragDropMode(QtWidgets.QAbstractItemView.InternalMove)
            self.setDragEnabled(True)
            self.setAcceptDrops(True)
            self.setDropIndicatorShown(True)
        else:
            pass

    @property
    def allow_multi_selection(self):
        """Getter for the allow_multi_selection property.

        Returns:
            bool: True if multi selection is allowed.
        """
        return self._allow_multi_selection

    @allow_multi_selection.setter
    def allow_multi_selection(self, allow_multi_selection):
        """Setter for the allow_multi_selection property.

        Args:
            allow_multi_selection (bool): When set to True allows multiple selection in
                the tree.
        """
        # allow multiple selection
        self._allow_multi_selection = allow_multi_selection
        if self._allow_multi_selection:
            self.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        else:
            self.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)

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
        """Fit columns to content."""
        self.resizeColumnToContents(0)

    @property
    def tasks(self):
        """Getter for the ``tasks`` property.

        Returns:
            list: A list of TaskBase instances.
        """
        return self._tasks

    @tasks.setter
    def tasks(self, tasks):
        self._tasks = tasks
        self.fill_ui(self.horizontal_labels)

    def fill_ui(self, horizontal_labels=None):
        """Fill the tree view with data.

        Args:
            horizontal_labels (List[str]): List of labels.
        """
        logger.debug("start filling tasks_treeView")
        logger.debug("creating a new model")

        # delete the old model if any
        if self.model() is not None:
            self.model().deleteLater()

        # update the horizontal labels but don't delete them
        if horizontal_labels is not None:
            self.horizontal_labels = horizontal_labels

        task_tree_model = TaskTreeModel(
            parent=self,
            show_dependency_info=self.show_dependency_info,
            show_asset_and_shot_children=self.show_asset_and_shot_children,
            show_takes=self.show_takes,
            horizontal_labels=self.horizontal_labels,
            allow_editing=self.allow_editing,
        )

        task_tree_model.populateTree(self.tasks)
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
        """runs when double-clicked on an leaf entity

        :param index:
        :return:
        """
        model = self.model()
        item = model.itemFromIndex(index)
        if not item:
            return

        if item.hasChildren():
            return

        logger.debug("item : {}".format(item))
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
                    self.fill_ui()

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
        """Load the TaskItem related to the given task in the given tree_view.

        Returns:
            TaskItem: TaskItem instance.
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
        """Find the item related to the stalker entity in the given QTreeView.

        Args:
            entity (Entity): Entity instances.
            tree_view (QTreeView): QTreeView derivative.

        Returns:
            TaskItem: The TaskItem that is the related entity.
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

    def get_selected_items(self):
        """Return the selected TaskItems.

        Returns:
            List[TaskItem]: List of selected TaskItem instances.
        """
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
        return [task.id for task in self.get_selected_tasks()]

    def get_selected_tasks(self):
        """returns the selected tasks"""
        return Task.query.filter(
            Task.id.in_([item.task.id for item in self.get_selected_items()])
        ).all()

    def expand_all_selected(self, index):
        """Expand all the selected items.

        Args:
            index (QModelIndex):
        """
        for item in self.get_selected_items():
            self.setExpanded(item.index(), True)
        self.auto_fit_column()

    def collapse_all_selected(self, index):
        """Collapse all the selected items.

        Args:
            index (QModelIndex): The model index.
        """
        for item in self.get_selected_items():
            self.setExpanded(item.index(), False)
        self.auto_fit_column()


class TaskTableView(QtWidgets.QTableView):
    """A QTableView variant that shows task related data."""

    def __init__(self, *args, **kwargs):
        super(TaskTableView, self).__init__(*args, **kwargs)
