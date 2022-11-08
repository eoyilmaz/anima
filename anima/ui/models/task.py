# -*- coding: utf-8 -*-
"""Custom UI items and models are here."""

from anima import defaults, logger
from anima.ui.lib import QtCore, QtGui, QtWidgets
from anima.ui.utils import load_font, get_cached_icon

from sqlalchemy.dialects.postgresql import array_agg
from sqlalchemy.orm import aliased

from stalker import Project, SimpleEntity, Task, User
from stalker.db.session import DBSession
from stalker.models.task import Task_Resources


if False:
    from PySide2 import QtCore, QtGui, QtWidgets


class TaskNameCompleter(QtWidgets.QCompleter):
    """Task name completer.

    Currently this is not used anywhere. Needs more work.

    Args:
        parent: The parent QWidget.
    """

    def __init__(self, parent):
        QtWidgets.QCompleter.__init__(self, [], parent)

    def update(self, completion_prefix):
        """Update the completion.

        Args:
            completion_prefix (str): The completion prefix.
        """
        tasks = Task.query.filter(
            Task.name.ilike("%{}%".format(completion_prefix))
        ).all()
        logger.debug("completer tasks : %s" % tasks)
        task_names = [task.name for task in tasks]
        model = QtGui.QStringListModel(task_names)
        self.setModel(model)
        # self.setCompletionPrefix(completion_prefix)
        self.setCompletionPrefix("")

        # if completion_prefix.strip() != '':
        self.complete()


# class TaskItemDelegate(QtWidgets.QStyledItemDelegate):
#     """Draws task item icons
#     """
#
#     task_entity_type_icons = {
#         'Task': u'\uf0ae',
#         'Asset': u'\uf12e',
#         'Shot': u'\uf030',
#         'Sequence': u'\uf1de',
#         'Project': u'\uf0e8'
#     }
#
#     def __init__(self, *args, **kwargs):
#         super(self.__class__, self).__init__(*args, **kwargs)
#
#         self.loaded_font_families = load_font('FontAwesome.otf')
#
#         self.default_font = QtGui.QFont()
#         self.font = QtGui.QFont()
#
#         if self.loaded_font_families:
#             self.font.setFamily(self.loaded_font_families[0])
#         self.font.setPixelSize(14)
#
#     def sizeHint(self, option, index):
#         """custom sizeHint, this is implemented because we have a custom paint
#         method
#
#         :param QStyleOptionItem option: Sylte option
#         :param QModelIndex index: The model index
#         :return:
#         """
#         size = super(self.__class__, self).sizeHint(option, index)
#         return QtCore.QSize(size.width() + 20, size.height())
#
#     def paint(self, painter, option, index):
#         """overridden paint method
#
#         :param painter: QPainter instance
#         :param option: QStyleOptionViewItem instance
#         :param index: QModelIndex instance
#         :return:
#         """
#         super(self.__class__, self).paint(painter, option, index)
#         # icon = QtGui.QIcon(QtCore.QSize(20, 20))
#         # option.icon = icon
#         # option.decorationSize = QtCore.QSize(20, 20)
#         # super(self.__class__, self).paint(painter, option, index)
#
#         item = index.model().itemFromIndex(index)
#         # bgrole = item.data(QtCore.Qt.BackgroundRole)
#         # fgrole = item.data(QtCore.Qt.ForegroundRole)
#
#         rect = option.rect
#         rect_x = rect.x()
#         rect_y = rect.y()
#         rect_w = rect.width()
#         rect_h = rect.height()
#
#         # if bgrole:
#         #     painter.fillRect(rect_x, rect_y, rect_w, rect_h, bgrole)
#
#         if isinstance(item, TaskItem):
#             entity_type = item.task.entity_type
#
#             # painter.setBrush(fgrole)
#
#             painter.setFont(self.font)
#             painter.drawText(
#                 rect_x + 4, rect_y + 4, 16, 16, 0,
#                 self.task_entity_type_icons[entity_type]
#             )
#
#             # painter.setFont(self.default_font)
#             # painter.drawText(
#             #     rect_x + 20, rect_y, rect_w - 20, rect_h, 0, item.task.name
#             # )


class TaskItem(QtGui.QStandardItem):
    """Implement the Task as a QStandardItem.

    Args:
        task (Entity): An entity that has id, name, entity_type, status_id and
            has_children fields.
        display_full_path (bool): When set to True, it will display the full path of the
            entity (if this is a Task derivative). False by default.
    """

    task_entity_types = ["Task", "Asset", "Shot", "Sequence"]

    def __init__(self, *args, **kwargs):
        self.loaded = False
        self.fetched_all = False
        task = kwargs.pop("task", None)
        self.display_full_path = kwargs.pop("display_full_path", False)

        QtGui.QStandardItem.__init__(self, *args, **kwargs)

        # color with task status
        self.setData(
            QtGui.QColor(*defaults.status_colors_by_id.get(task.status_id)),
            QtCore.Qt.BackgroundRole,
        )

        # use black text
        self.setForeground(QtGui.QBrush(QtGui.QColor(0, 0, 0)))

        self.parent = None
        self.setEditable(False)

        self._task = None
        self.task = task

    @property
    def task(self):
        """Return Task.

        Returns:
            Task: The Stalker Task instance stored in this item.
        """
        return self._task

    @task.setter
    def task(self, task):
        """Set the task property.

        Args:
            task: A stalker Task instance
        """
        self._task = task
        if not self._task:
            return

        icon = get_cached_icon(self._task.entity_type.lower())
        self.setData(icon, QtCore.Qt.DecorationRole)

        task_name = self.task.name
        if self.display_full_path:
            task_name = "{} ({} | {})".format(
                task.name,
                task.project.code,
                " | ".join(list(map(lambda x: x.name, task.parents)))
            )

        self.setData(task_name, QtCore.Qt.DisplayRole)

    def clone(self):
        """Return a copy of this item.

        Returns:
            TaskItem: A copy of this item.
        """
        logger.debug("TaskItem.clone() is started for item: %s" % self.text())
        new_item = TaskItem(task=self.task)
        new_item.parent = self.parent
        new_item.fetched_all = self.fetched_all
        logger.debug("TaskItem.clone() is finished for item: %s" % self.text())
        return new_item

    def canFetchMore(self):
        """Check if this item have children.

        Returns:
            bool: True if the item has children, False otherwise.
        """
        logger.debug("TaskItem.canFetchMore() is started for item: %s" % self.text())
        # return_value = False
        if self.task and self.task.id and not self.fetched_all:
            return_value = self.task.has_children
        else:
            return_value = False
        logger.debug("TaskItem.canFetchMore() is finished for item: %s" % self.text())
        return return_value

    def fetchMore(self):
        """Fetch child items."""
        logger.debug("TaskItem.fetchMore() is started for item: %s" % self.text())

        if self.canFetchMore():
            inner_tasks = aliased(Task)
            subquery = DBSession.query(Task.id).filter(Task.id == inner_tasks.parent_id)

            query = (
                DBSession.query(
                    Task.id,
                    Task.name,
                    Task.entity_type,
                    Task.status_id,
                    subquery.exists().label("has_children"),
                    array_agg(User.name).label("resources"),
                )
                .outerjoin(
                    Task_Resources, Task.__table__.c.id == Task_Resources.c.task_id
                )
                .outerjoin(User, Task_Resources.c.resource_id == User.id)
                .group_by(
                    Task.id,
                    Task.name,
                    Task.entity_type,
                    Task.status_id,
                    subquery.exists().label("has_children"),
                )
            )

            if self.task.entity_type != "Project":
                # query child tasks
                query = query.filter(Task.parent_id == self.task.id)
            else:
                # query only root tasks
                query = query.filter(Task.project_id == self.task.id).filter(
                    Task.parent_id == None
                )

            tasks = query.order_by(Task.name).all()

            # model = self.model() # This will cause a SEGFAULT
            # TODO: update it later on

            # start = time.time()
            task_items = []
            for task in tasks:
                task_item = TaskItem(0, 4, task=task)
                task_item.parent = self

                # color with task status
                task_item.setData(
                    QtGui.QColor(*defaults.status_colors_by_id[task.status_id]),
                    QtCore.Qt.BackgroundRole,
                )

                # use black text
                task_item.setForeground(QtGui.QBrush(QtGui.QColor(0, 0, 0)))

                task_items.append(task_item)

            if task_items:
                # self.appendRows(task_items)
                for task_item in task_items:
                    # TODO: Create a custom QStandardItem for each data type in
                    #       different columns
                    entity_type_item = QtGui.QStandardItem()
                    entity_type_item.setData(
                        task_item.task.entity_type, QtCore.Qt.DisplayRole
                    )

                    resources_item = QtGui.QStandardItem()
                    if task_item.task.resources != [None]:
                        resources_item.setData(
                            ", ".join(map(str, task_item.task.resources)),
                            QtCore.Qt.DisplayRole,
                        )

                    self.appendRow([task_item, entity_type_item, resources_item])

            self.fetched_all = True

        logger.debug("TaskItem.fetchMore() is finished for item: %s" % self.text())

    def hasChildren(self):
        """Check if this TaskItem has children.

        Returns:
            bool: True if the Task related to this item has children, False otherwise.
        """
        logger.debug("TaskItem.hasChildren() is started for item: %s" % self.text())
        return_value = self.task.has_children

        logger.debug("TaskItem.hasChildren() is finished for item: %s" % self.text())
        return return_value

    def type(self, *args, **kwargs):
        """Generate a custom type to distinguish this item from a QStandardItem.

        Args:
            args (list): The given arguments.
            kwargs (dict): The given keyword arguments.

        Returns:
            int: The custom user type value.
        """
        return QtGui.QStandardItem.UserType + 1

    def reload(self):
        """Reload the data."""
        # delete all the children and fetch them again
        for _ in range(self.rowCount()):
            self.removeRow(0)
        self.fetched_all = False
        self.fetchMore()

    def __hash__(self):
        """Generate a hash value from the Task.id.

        Returns:
            int: The hash value which is the task id.
        """
        return self.task.id


class TaskTreeModel(QtGui.QStandardItemModel):
    """Implement the model view for the task hierarchy."""

    def __init__(self, *args, **kwargs):
        logger.debug("TaskTreeModel.__init__() is started")
        self.root = None

        self.horizontal_labels = kwargs.pop("horizontal_labels", None)
        if self.horizontal_labels is None:
            # use default
            self.horizontal_labels = ["Name", "Type", "Resources", "Dependencies"]
        self.show_dependency_info = kwargs.pop("show_dependency_info", False)
        self.show_asset_and_shot_children = kwargs.pop(
            "show_asset_and_shot_children", True
        )
        self.show_asset_child_task_takes = kwargs.pop(
            "show_asset_child_task_takes", False
        )
        self.allow_editing = kwargs.pop("allow_editing", False)
        parent = kwargs.pop("parent", None)
        super(TaskTreeModel, self).__init__(parent=parent)

        logger.debug("TaskTreeModel.__init__() is finished")

    def flags(self, model_index):
        """Return model flags.

        Args:
            model_index: The item models index.

        Returns:
            int: Combined enum data of model flags.
        """
        default_flags = QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsDropEnabled
        if model_index.isValid():
            default_flags |= QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsDragEnabled
            if self.allow_editing:
                default_flags |= QtCore.Qt.ItemIsEditable
        return default_flags

    def canDropMimeData(self, data, action, row, column, parent):
        """Return if the item in the index can drop mime data.

        Args:
            data: The data.
            action: The given action.
            row: The dropped row.
            column: The dropped column.
            parent: The dropped parent item's model index.

        Returns:
            bool: Returns True if the data and action were handled by the model,
                otherwise returns False.
        """
        return True

    def mimeTypes(self):
        """Return the supported mime types.

        Returns:
            list: A list of strings of supported mime types.
        """
        return ["application/vnd.treeviewdragdrop.list"]

    def mimeData(self, indexes):
        """Generate the mime data.

        Args:
            indexes (list): List of dragged items' model indexes.

        Returns:
            QtCore.QMimeData: The QMimeData that contains the dragged Tasks ids.
        """
        encoded_data = QtCore.QByteArray()
        stream = QtCore.QDataStream(encoded_data, QtCore.QIODevice.WriteOnly)
        for index in indexes:
            if index.isValid():
                item = self.itemFromIndex(index)
                if isinstance(item, TaskItem):
                    text = "{}".format(item.task.id)
                    stream << QtCore.QByteArray(text.encode("utf-8"))
        mime_data = QtCore.QMimeData()
        mime_data.setData("application/vnd.treeviewdragdrop.list", encoded_data)
        return mime_data

    def dropMimeData(self, data, action, row, column, parent):
        """Handle drop data.

        Args:
            data: The data.
            action: The given action.
            row: The dropped row.
            column: The dropped column.
            parent: The dropped parent item's model index.

        Returns:
            bool: Returns True if the data and action were handled by the model,
                otherwise returns False.
        """
        if action == QtCore.Qt.IgnoreAction:
            return True
        if not data.hasFormat("application/vnd.treeviewdragdrop.list"):
            return False

        parent_item = self.itemFromIndex(parent)
        if not isinstance(parent_item, TaskItem):
            return False
        parent_entity = SimpleEntity.query.filter(
            SimpleEntity.id == parent_item.task.id
        ).first()
        if not parent_entity:
            return False

        encoded_data = data.data("application/vnd.treeviewdragdrop.list")
        stream = QtCore.QDataStream(encoded_data, QtCore.QIODevice.ReadOnly)
        dropped_ids = []
        while not stream.atEnd():
            text = QtCore.QByteArray()
            stream >> text
            text = bytes(text).decode("utf-8")
            dropped_ids.append(text)
        for id_ in dropped_ids:
            dropped_task = Task.query.get(id_)
            if isinstance(parent_entity, Task):
                dropped_task.parent = parent_entity
            elif isinstance(parent_entity, Project):
                dropped_task.parent = None
        DBSession.commit()
        parent_item.reload()
        return True

    def supportedDropActions(self):
        """Return the supported drop actions.

        Returns:
            int: A combined int of enum data of QtCore.Qt.*Action of sort.
        """
        return QtCore.Qt.MoveAction

    def populateTree(self, tasks):
        """Populate tree with user projects.

        Args:
            tasks (list): A list of Stalker Tasks instances.
        """
        logger.debug("TaskTreeModel.populateTree() is started")
        self.setColumnCount(4)
        self.setHorizontalHeaderLabels(self.horizontal_labels)

        for task in tasks:
            task_item = TaskItem(0, 4, task=task)
            task_item.parent = None
            task_item.setColumnCount(4)

            self.appendRow(task_item)

        logger.debug("TaskTreeModel.populateTree() is finished")

    def canFetchMore(self, index):
        """Check if the item can fetch more items.

        Args:
            index: The model index.

        Returns:
            bool: True if the item with the given index can fetch more items.
        """
        logger.debug("TaskTreeModel.canFetchMore() is started for index: %s" % index)
        if not index.isValid():
            return_value = False
        else:
            item = self.itemFromIndex(index)
            return_value = item.canFetchMore()
        logger.debug("TaskTreeModel.canFetchMore() is finished for index: %s" % index)
        return return_value

    def fetchMore(self, index):
        """Fetch more elements.

        Args:
            index: The model index.
        """
        logger.debug("TaskTreeModel.canFetchMore() is started for index: %s" % index)
        if index.isValid():
            item = self.itemFromIndex(index)
            item.fetchMore()
        logger.debug("TaskTreeModel.canFetchMore() is finished for index: %s" % index)

    def hasChildren(self, index):
        """Return True or False depending on to the index and the item on the index.

        Args:
            index: The model index.

        Returns:
            bool: True if the item in the given index has children, False otherwise.
        """
        logger.debug("TaskTreeModel.hasChildren() is started for index: %s" % index)
        if not index.isValid():
            projects_count = DBSession.query(Project.id).count()
            return_value = projects_count > 0
        else:
            item = self.itemFromIndex(index)
            return_value = False
            if item:
                return_value = item.hasChildren()
        logger.debug("TaskTreeModel.hasChildren() is finished for index: %s" % index)
        return return_value

    def reload(self, index):
        """Reload the item at the given index.

        Args:
            index: The model index to reload.
        """
        if not index.isValid():
            # just return
            return
        else:
            item = self.itemFromIndex(index)
            item.reload()


class TaskTableModel(QtGui.QStandardItemModel):
    """Task model suitable for data tables."""

    def __init__(self, *args, **kwargs):
        super(TaskTableModel, self).__init__(*args, **kwargs)
        self.setColumnCount(7)
        self.setHorizontalHeaderLabels(
            ["", "Thumbnail", "Start", "End", "Name", "Bid", "Sched."]
        )

    def populate_table(self, tasks):
        """Populate table with data."""
        for task in tasks:
            assert isinstance(task, Task)

            # CheckBox item
            check_box_item = QtGui.QStandardItem()
            check_box_item.setCheckable(True)
            check_box_item.setCheckState(QtCore.Qt.CheckState.Unchecked)

            # Thumbnail
            thumbnail_item = QtGui.QStandardItem()

            # Start Date
            start_date_item = QtGui.QStandardItem(
                "{}-{}-{}".format(task.start.year, task.start.month, task.start.day)
            )

            # End Date
            end_date_item = QtGui.QStandardItem(
                "{}-{}-{}".format(task.end.year, task.end.month, task.end.day)
            )

            # Name
            name_item = TaskItem(task=task, display_full_path=True)

            # Bid
            bid_timing_item = QtGui.QStandardItem(
                "{} {}".format(int(task.bid_timing), task.bid_unit)
            )

            # Schedule Timing
            schedule_timing_item = QtGui.QStandardItem(
                "{} {}".format(int(task.schedule_timing), task.schedule_unit)
            )

            self.appendRow([
                check_box_item,
                thumbnail_item,
                start_date_item,
                end_date_item,
                name_item,
                bid_timing_item,
                schedule_timing_item,
            ])


# class TaskTableSortFilterProxyModel(QtCore.QSortFilterProxyModel):
#     """
#     """
