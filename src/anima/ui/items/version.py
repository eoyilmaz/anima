# -*- coding: utf-8 -*-

from typing import Union
from stalker import Version
from anima.log import logger
from anima.ui.items.file import (
    FileAuditItem,
    FileCreatedWithItem,
    FileDateCreatedItem,
    FileDateUpdatedItem,
    FileFullPathItem,
    FileItem,
    FileTypeItem,
)
from anima.ui.lib import QtCore, QtGui


def set_item_color(item, color):
    """sets the item color

    :param item: the item
    :param color: the color
    """
    foreground = item.foreground()
    foreground.setColor(color)
    item.setForeground(foreground)


def generate_reference_version_row(parent, model, version):
    """Generate a new referenced version row.

    Args:
        parent (QtGui.QStandardItem): The parent item.
        model (QtGui.QStandardItemModel): The item model.
        version (Version): The version instance.

    Returns:
        List[QtGui.QStandardItem]: The generated row.
    """
    # column 0
    version_item = VersionItem(0, 0)
    version_item.parent = parent

    version_item.version = version
    version_item.setEditable(False)
    reference_resolution = model.reference_resolution

    if reference_resolution:
        if version in reference_resolution["update"]:
            action = "update"
            font_color = QtGui.QColor(192, 128, 0)
            if version in reference_resolution["root"]:
                version_item.setCheckable(True)
                version_item.setCheckState(QtCore.Qt.Checked)
        elif version in reference_resolution["create"]:
            action = "create"
            font_color = QtGui.QColor(192, 0, 0)
            if version in reference_resolution["root"]:
                version_item.setCheckable(True)
                version_item.setCheckState(QtCore.Qt.Checked)
    else:
        font_color = QtGui.QColor(0, 192, 0)
        action = ""

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
    nice_name_item.setText(f"{version.nice_name}_v{version.version_number:03d}")
    nice_name_item.setEditable(False)
    nice_name_item.version = version
    nice_name_item.action = action
    set_item_color(nice_name_item, font_color)

    # # Variant
    # variant_item = QtGui.QStandardItem()
    # variant_item.setEditable(False)
    # variant_item.setText(version.variant_name)
    # variant_item.version = version
    # variant_item.action = action
    # set_item_color(variant_item, font_color)

    # Version
    current_version_item = QtGui.QStandardItem()
    current_version_item.setText(f"{version.version_number}")
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

    latest_published_version_text = "No Published Version"
    if latest_published_version:
        latest_published_version_text = f"{latest_published_version.version_number}"
    latest_published_version_item.setText(latest_published_version_text)
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
    updated_by_text = ""
    if latest_published_version and latest_published_version.updated_by:
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

    return [
        version_item,
        thumbnail_item,
        nice_name_item,
        # variant_item,
        current_version_item,
        latest_published_version_item,
        action_item,
        updated_by_item,
        description_item,
    ]


def generate_version_row(parent, model, version):
    """Generate a new version row.

    Args:
        parent (QtGui.QStandardItem): The parent item.
        model (QtGui.QStandardItemModel): The item model.
        version (Version): The version instance.

    Returns:
        List[QtGui.QStandardItem]: The generated row.
    """
    # column 0
    version_item = VersionItem(0, 0)
    version_item.parent = parent

    version_item.version = version
    version_item.setEditable(False)

    font_color = version_item.foreground().color()
    if version.is_published:
        font_color = QtGui.QColor(0, 192, 0)
    set_item_color(version_item, font_color)

    return [
        version_item,
    ]


def generate_file_row(parent, model, file):
    """Generate a new file row.

    Args:
        parent (QtGui.QStandardItem): The parent item.
        model (QtGui.QStandardItemModel): The item model.
        file (File): The file instance.

    Returns:
        List[QtGui.QStandardItem]: The generated row.
    """
    # column 0
    file_item = FileItem(file=file)
    file_item.parent = parent

    return [
        file_item,
        FileCreatedWithItem(file=file),
        FileAuditItem(file=file),
        FileDateCreatedItem(file=file),
        FileDateUpdatedItem(file=file),
        FileTypeItem(file=file),
        FileFullPathItem(file=file),
    ]


class VersionItem(QtGui.QStandardItem):
    """Implement Version as a QStandardItem."""

    def __init__(self, *args, **kwargs):
        version = kwargs.pop("version", None)
        super().__init__(*args, **kwargs)
        self.loaded = False
        self._version = None
        self.version = version
        self.parent = None
        self.fetched_all = False
        self.setEditable(False)

    @property
    def version(self) -> Version:
        """Return the version.

        Returns:
            Version: The version.
        """
        return self._version

    @version.setter
    def version(self, version: Union[None, Version]) -> None:
        """Set the version and update the item text.

        Args:
            version (Union[None, Version]): The version to set. Can be set to
                None.

        Raises:
            TypeError: If the given version is not an instance of Version.
        """
        if version is not None and not isinstance(version, (Version)):
            raise TypeError(
                "version should be an instance of stalker.Version, "
                f"not {version.__class__.__name__}: '{version}'"
            )

        self._version = version
        if version:
            self.setText(
                "r{:02d}_v{:03d}".format(
                    version.revision_number, version.version_number
                )
            )
        else:
            self.setText("-- None --")

    def clone(self) -> "VersionItem":
        """Return a copy of this item.

        Returns:
            VersionItem: The copied item.
        """
        new_item = VersionItem()
        new_item.version = self.version
        new_item.parent = self.parent
        new_item.fetched_all = self.fetched_all
        return new_item

    def canFetchMore(self) -> bool:
        """Return True if the item can fetch more children.

        Returns:
            bool: True if the item can fetch more children.
        """
        # print(f"self.version.files: {self.version.files}")
        if self.version and not self.fetched_all:
            return len(self.version.files) > 0

        return False

    def fetchMore(self) -> None:
        """Fetch more children."""
        if not self.canFetchMore():
            return

        # model = self.model() # This will cause a SEGFAULT
        files = self.version.files

        for file in files:
            self.appendRow(
                generate_file_row(parent=self, model=self.model(), file=file)
            )

        self.fetched_all = True

    def hasChildren(self) -> bool:
        """Return True if the item has children.

        Returns:
            bool: True if the item has children.
        """
        # print(f"self.version.files: {self.version.files}")
        if self.version:
            return len(self.version.files) > 0

        return False

    def type(self, *args, **kwargs) -> int:
        """Return the item type.

        Returns:
            int: The item type.
        """
        return QtGui.QStandardItem.UserType + 2
