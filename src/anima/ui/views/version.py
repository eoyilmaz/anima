from typing import List, Optional

from anima.ui.items.version import generate_version_row, VersionItem
from anima.ui.items.file import FileItem
from anima.ui.models.version import VersionItemModel
from stalker import File, Version
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

    def select_version(self, version: Version) -> None:
        """Select a specific version in the view.

        Args:
            version (Version): The version to select.

        Returns:
            None | VersionItem: The selected VersionItem if found, otherwise None.
        """
        model = self.model()
        if not model:
            return
        for row in range(model.rowCount()):
            item = model.item(row)
            if isinstance(item, VersionItem) and item.version == version:
                index = model.indexFromItem(item)
                self.setCurrentIndex(index)
                self.setExpanded(index, True)
                self.scrollTo(index)
                return item

        return None

    def select_file(self, file: File) -> None:
        """Select a specific file in the view.

        Args:
            file (File): The file to select.

        Returns:
            None | FileItem: The selected FileItem if found, otherwise None.
        """
        if (
            not (model := self.model())
            or not (
                version := Version.query.filter(Version.files.contains(file)).first()
            )
            or (version_item := self.select_version(version)) is None
            or not version_item.hasChildren()
        ):
            return

        for row in range(version_item.rowCount()):
            item = version_item.child(row)
            if isinstance(item, FileItem) and item.file == file:
                index = model.indexFromItem(item)
                self.setCurrentIndex(index)
                self.scrollTo(index)
                return item

        return None
