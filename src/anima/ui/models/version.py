# -*- coding: utf-8 -*-


from anima.log import logger
from anima.ui.items.version import VersionItem
from anima.ui.lib import QtGui


def set_item_color(item, color):
    """sets the item color

    :param item: the item
    :param color: the color
    """
    foreground = item.foreground()
    foreground.setColor(color)
    item.setForeground(foreground)


class VersionItemModel(QtGui.QStandardItemModel):
    """Implements the model view for the version hierarchy."""

    def __init__(self, flat_view=False, *args, **kwargs):
        QtGui.QStandardItemModel.__init__(self, *args, **kwargs)
        logger.debug("VersionTreeModel.__init__() is started")
        self.root = None
        self.root_versions = []
        self.reference_resolution = None
        self.flat_view = flat_view
        logger.debug("VersionTreeModel.__init__() is finished")

    def populateTree(self, versions):
        """populates tree with root versions"""
        logger.debug("VersionTreeModel.populateTree() is started")
        self.setColumnCount(7)
        self.setHorizontalHeaderLabels(
            [
                "Do Update?",
                "Thumbnail",
                "Task",
                "Variant",
                "Current",
                "Latest",
                "Action",
                "Updated By",
                "Notes",
            ]
        )

        self.root_versions = versions
        for version in versions:
            self.appendRow(VersionItem.generate_version_row(None, self, version))

        logger.debug("VersionTreeModel.populateTree() is finished")

    def canFetchMore(self, index):
        logger.debug(f"VersionTreeModel.canFetchMore() is started for index: {index}")
        if not index.isValid():
            return_value = False
        else:
            item = self.itemFromIndex(index)
            return_value = item.canFetchMore()
        logger.debug(f"VersionTreeModel.canFetchMore() is finished for index: {index}")
        return return_value

    def fetchMore(self, index):
        """fetches more elements"""
        logger.debug(f"VersionTreeModel.canFetchMore() is started for index: {index}")
        if index.isValid():
            item = self.itemFromIndex(index)
            item.fetchMore()
        logger.debug(f"VersionTreeModel.canFetchMore() is finished for index: {index}")

    def hasChildren(self, index):
        """returns True or False depending on to the index and the item on the
        index
        """
        logger.debug(f"VersionTreeModel.hasChildren() is started for index: {index}")
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
        logger.debug(f"VersionTreeModel.hasChildren() is finished for index: {index}")
        return return_value
