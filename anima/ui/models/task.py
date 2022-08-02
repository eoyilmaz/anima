# -*- coding: utf-8 -*-

from anima import logger, defaults
from anima.ui.lib import QtCore, QtGui, QtWidgets
from anima.ui.utils import load_font

from sqlalchemy.dialects.postgresql import array_agg
from sqlalchemy.orm import aliased

from stalker import Task, Project, User, SimpleEntity
from stalker.db.session import DBSession
from stalker.models.task import Task_Resources


class TaskIcon(QtGui.QIcon):
    """A custom QIcon that creates icons from text"""

    task_entity_type_icons = {
        "Task": "\uf0ae",
        "Asset": "\uf12e",
        "Shot": "\uf030",
        "Sequence": "\uf1de",
        "Project": "\uf0e8",
    }

    def __init__(self, *args, **kwargs):
        self.entity_type = kwargs.pop("entity_type", None)

        pixmap = QtGui.QPixmap(20, 20)
        super(TaskIcon, self).__init__(pixmap)

        loaded_font_families = load_font("FontAwesome.otf")
        # default_font = QtGui.QFont()
        self.icon_font = QtGui.QFont()

        if loaded_font_families:
            self.icon_font.setFamily(loaded_font_families[0])
            self.icon_font.setPixelSize(14)

    def paint(self, *args, **kwargs):
        """Custom painter

        :param QPainter painter:
        :param QRect rect:
        :param Qt.Alignment alignment:
        :param mode:
        :param state:
        :return:
        """
        super(TaskIcon, self).paint(*args, **kwargs)

        # # set text and icon
        # pixmap = QtGui.QPixmap(20, 20)
        # painter.setFont(self.icon_font)
        # # painter.begin(pixmap)
        # painter.drawText(
        #     rect.x() + 4, rect.y() + 4, 16, 16, 0,
        #     self.task_entity_type_icons[self.entity_type]
        # )
        # # painter.end()
        # self.setPixmap(pixmap)


class TaskNameCompleter(QtWidgets.QCompleter):
    def __init__(self, parent):
        QtWidgets.QCompleter.__init__(self, [], parent)

    def update(self, completion_prefix):

        tasks = Task.query.filter(Task.name.ilike("%" + completion_prefix + "%")).all()
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
    """Implements the Task as a QStandardItem


    :param entity: An entity that has id, name, entity_type, status_id and
      has_children fields
    """

    task_entity_types = ["Task", "Asset", "Shot", "Sequence"]

    def __init__(self, *args, **kwargs):
        self.task = kwargs.pop("task", None)
        self.loaded = False
        self.fetched_all = False

        QtGui.QStandardItem.__init__(self, *args, **kwargs)
        logger.debug("TaskItem.__init__() is started for item: %s" % self.text())
        self.parent = None
        self.setEditable(False)
        logger.debug("TaskItem.__init__() is finished for item: %s" % self.text())

        icon = TaskIcon(self.task.entity_type)
        self.setData(icon, QtCore.Qt.DecorationRole)
        self.setData(self.task.name, QtCore.Qt.DisplayRole)

    def clone(self):
        """returns a copy of this item"""
        logger.debug("TaskItem.clone() is started for item: %s" % self.text())
        new_item = TaskItem(task=self.task)
        new_item.parent = self.parent
        new_item.fetched_all = self.fetched_all
        logger.debug("TaskItem.clone() is finished for item: %s" % self.text())
        return new_item

    def canFetchMore(self):
        logger.debug("TaskItem.canFetchMore() is started for item: %s" % self.text())
        # return_value = False
        if self.task and self.task.id and not self.fetched_all:
            return_value = self.task.has_children
        else:
            return_value = False
        logger.debug("TaskItem.canFetchMore() is finished for item: %s" % self.text())
        return return_value

    def fetchMore(self):
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

            # # model = self.model() # This will cause a SEGFAULT
            # # TODO: update it later on

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
                    # TODO: Create a custom QStandardItem for each data type in different columns
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
        logger.debug("TaskItem.hasChildren() is started for item: %s" % self.text())
        return_value = self.task.has_children

        logger.debug("TaskItem.hasChildren() is finished for item: %s" % self.text())
        return return_value

    def type(self, *args, **kwargs):
        """ """
        return QtGui.QStandardItem.UserType + 1

    def reload(self):
        """reloads the self data"""
        # delete all the children and fetch them again
        for i in range(self.rowCount()):
            self.removeRow(0)
        self.fetched_all = False
        self.fetchMore()

    def __hash__(self):
        return self.task.id


class TaskTreeModel(QtGui.QStandardItemModel):
    """Implements the model view for the task hierarchy"""

    def __init__(self, *args, **kwargs):
        QtGui.QStandardItemModel.__init__(self, *args, **kwargs)
        logger.debug("TaskTreeModel.__init__() is started")
        self.root = None
        logger.debug("TaskTreeModel.__init__() is finished")

    def flags(self, model_index):
        """Returns model flags

        :param model_index: The item models index
        :return:
        """
        if not model_index.isValid():
            return (
                QtCore.Qt.ItemIsEnabled
                | QtCore.Qt.ItemIsDropEnabled
                # | default_flags
            )

        return (
            QtCore.Qt.ItemIsEnabled
            | QtCore.Qt.ItemIsSelectable
            | QtCore.Qt.ItemIsDragEnabled
            | QtCore.Qt.ItemIsDropEnabled
            # | default_flags
        )

    def canDropMimeData(self, data, action, row, column, parent):
        return True

    def mimeTypes(self):
        return ["application/vnd.treeviewdragdrop.list"]

    def mimeData(self, indexes):
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
        """Handle drop data."""
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
        return QtCore.Qt.MoveAction

    def populateTree(self, projects):
        """populates tree with user projects"""
        logger.debug("TaskTreeModel.populateTree() is started")
        self.setColumnCount(4)
        self.setHorizontalHeaderLabels(["Name", "Type", "Resources", "Dependencies"])

        for project in projects:
            project_item = TaskItem(0, 4, task=project)
            project_item.parent = None
            project_item.setColumnCount(4)

            # Set Font
            my_font = project_item.font()
            my_font.setBold(True)
            project_item.setFont(my_font)

            # color with task status
            project_item.setData(
                QtGui.QColor(*defaults.status_colors_by_id.get(project.status_id)),
                QtCore.Qt.BackgroundRole,
            )

            # use black text
            project_item.setForeground(QtGui.QBrush(QtGui.QColor(0, 0, 0)))

            self.appendRow(project_item)

        logger.debug("TaskTreeModel.populateTree() is finished")

    def canFetchMore(self, index):
        logger.debug("TaskTreeModel.canFetchMore() is started for index: %s" % index)
        if not index.isValid():
            return_value = False
        else:
            item = self.itemFromIndex(index)
            return_value = item.canFetchMore()
        logger.debug("TaskTreeModel.canFetchMore() is finished for index: %s" % index)
        return return_value

    def fetchMore(self, index):
        """fetches more elements"""
        logger.debug("TaskTreeModel.canFetchMore() is started for index: %s" % index)
        if index.isValid():
            item = self.itemFromIndex(index)
            item.fetchMore()
        logger.debug("TaskTreeModel.canFetchMore() is finished for index: %s" % index)

    def hasChildren(self, index):
        """Return True or False depending on to the index and the item on the index.
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
        """Reload the item at the given index."""
        if not index.isValid():
            # just return
            return
        else:
            item = self.itemFromIndex(index)
            item.reload()
