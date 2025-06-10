# -*- coding: utf-8 -*-

from typing import List, Optional

from anima.ui.items.version import generate_version_row, VersionItem
from anima.ui.items.file import FileItem
from anima.ui.models.version import VersionItemModel
from stalker import Version
from anima.ui.lib import QtGui, QtWidgets


DEFAULT_VERSION_LABELS = [
    "Name",
    "Created With",
    "Created By",
    "Date Created",
    "Date Updated",
    "Type",
    "Full Path",
]


class VersionListView(QtWidgets.QListView):
    """A custom list view to display Version info."""

    def __init__(self, *args, **kwargs):
        super(VersionListView, self).__init__(*args, **kwargs)

        # TODO: Implement this as a class with all its context menus etc.


class VersionTreeView(QtWidgets.QTreeView):
    """A custom tree view to display Version related data.

    Args:
        parent (QtWidgets.QWidget): The parent widget.
        versions (List[Version]): A list of Version instances.

    """

    def __init__(
        self,
        parent: Optional[QtWidgets.QWidget] = None,
        labels: Optional[List[str]] = None,
        *args,
        **kwargs,
    ):
        super().__init__(parent=parent, *args, **kwargs)
        self.labels = labels or DEFAULT_VERSION_LABELS

    def populate(self, versions: List[Version]) -> None:
        """Populate the view with Versions.

        Args:
            versions (Optional[Version]): The versions to populate the tree
                with. All should be stalker.Version instances.
        """
        model = VersionItemModel(
            flat_view=False,
            labels=self.labels,
            row_generator=generate_version_row,
        )
        self.setModel(model)
        model.populate(versions)
        self.auto_fit_columns()

    def auto_fit_columns(self):
        """Fit columns to the content."""
        header = self.header()
        header.setVisible(True)
        header.setSectionsMovable(False)
        if (number_of_sections := header.count()) > 0:
            header.setSectionResizeMode(0, QtWidgets.QHeaderView.Interactive)
            for i in range(1, number_of_sections):
                header.setSectionResizeMode(i, QtWidgets.QHeaderView.Interactive)
        header.setStretchLastSection(True)
        header.setCascadingSectionResizes(False)
        header.resizeSections(QtWidgets.QHeaderView.ResizeToContents)

    def get_selected_items(self) -> List[QtGui.QStandardItem]:
        """Get the selected items in the view.

        Returns:
            List[QtGui.QStandardItem]: The selected items.
        """
        selection_model = self.selectionModel()
        if not (indices := selection_model.selectedIndexes()):
            return []
        items = []
        item_model = self.model()
        for index in indices:
            item = item_model.itemFromIndex(index)
            if item and isinstance(item, (VersionItem, FileItem)):
                items.append(item)
        return items

    def get_selected_versions(self) -> List[Version]:
        """Get the selected versions in the view.

        Returns:
            List[Version]: The selected versions.
        """
        items = self.get_selected_items()
        return [item.version for item in items if isinstance(item, VersionItem)]

    def get_selected_files(self) -> List[FileItem]:
        """Get the selected files in the view.

        Returns:
            List[FileItem]: The selected files.
        """
        items = self.get_selected_items()
        return [item.file for item in items if isinstance(item, FileItem)]
