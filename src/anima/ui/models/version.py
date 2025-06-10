# -*- coding: utf-8 -*-


from typing import List

from stalker import Version
from anima.log import logger
from anima.ui.items.version import VersionItem, generate_reference_version_row
from anima.ui.lib import QtCore, QtGui


class VersionItemModel(QtGui.QStandardItemModel):
    """Implements the model view for the version hierarchy."""

    def __init__(
        self,
        flat_view=False,
        labels=None,
        row_generator=None,
        allow_editing=False,
        *args,
        **kwargs,
    ):
        QtGui.QStandardItemModel.__init__(self, *args, **kwargs)
        logger.debug("VersionTreeModel.__init__() is started")
        self.root = None
        self.root_versions = []
        self.reference_resolution = None
        self.flat_view = flat_view
        self.allow_editing = allow_editing
        if not labels:
            labels = []
        self.labels = labels

        if not row_generator:
            row_generator = generate_reference_version_row
        self.row_generator = row_generator

        logger.debug("VersionTreeModel.__init__() is finished")

    def flags(self, model_index: QtCore.QModelIndex) -> int:
        """Return model flags.

        Args:
            model_index (QtCore.QModelIndex): The item model index.

        Returns:
            int: Combined enum data of model flags.
        """
        default_flags = QtCore.Qt.ItemIsEnabled
        if model_index.isValid():
            default_flags |= QtCore.Qt.ItemIsSelectable
            if self.allow_editing:
                default_flags |= QtCore.Qt.ItemIsEditable
        else:
            default_flags |= QtCore.ItemIsDropEnabled
        return default_flags

    def populate(self, versions: List[Version]) -> None:
        """Populate tree with root versions.

        Args:
            versions (List[Version]): A list of Stalker version instances.
        """
        logger.debug("VersionTreeModel.populate() is started")
        self.setColumnCount(len(self.labels))
        self.setHorizontalHeaderLabels(self.labels)

        self.root_versions = versions
        for version in versions:
            # self.appendRow(self.row_generator(parent=None, model=self, version=version))
            self.appendRow(VersionItem(version=version))

        logger.debug("VersionTreeModel.populate() is finished")

    def canFetchMore(self, index) -> bool:
        """Return true if the item can fetch more children.

        Args:
            index (QtCore.QModelIndex): The index to check if it can fetch more
                children.

        Returns:
            bool: True if the item can fetch more children.
        """
        logger.debug(f"VersionTreeModel.canFetchMore() is started for index: {index}")
        if not index.isValid():
            return False

        item = self.itemFromIndex(index)
        if not item:
            return False

        return_value = item.canFetchMore()
        logger.debug(f"VersionTreeModel.canFetchMore() is finished for index: {index}")
        return return_value

    def fetchMore(self, index) -> None:
        """Fetch more elements.

        Args:
            index (QtCore.QModelIndex): The index to fetch more elements.
        """
        logger.debug(f"VersionTreeModel.canFetchMore() is started for index: {index}")
        if not index.isValid():
            return

        item = self.itemFromIndex(index)
        item.fetchMore()

        logger.debug(f"VersionTreeModel.canFetchMore() is finished for index: {index}")

    def hasChildren(self, index) -> bool:
        """Return True if the item on the given index has children.

        Args:
            index (QtCore.QModelIndex): The index to check if it has children.

        Returns:
            bool: True if the item on the given index has
        """
        logger.debug(f"VersionTreeModel.hasChildren() is started for index: {index}")
        if not index.isValid():
            return len(self.root_versions) > 0

        if self.flat_view:
            return False

        item = self.itemFromIndex(index)
        return_value = False
        if item:
            return_value = item.hasChildren()

        logger.debug(f"VersionTreeModel.hasChildren() is finished for index: {index}")
        return return_value
