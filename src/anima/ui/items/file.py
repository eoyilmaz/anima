# -*- coding: utf-8 -*-
"""File related items are situated here."""

from typing import Any, Dict, List, Union

from stalker import File

from anima.ui.lib import QtCore, QtGui, QtWidgets
from anima.log import logger

#
# File.thumbnail
# File.name
# File.type
# File.full_path
# File.created_with
# File.created_by
# File.date_created
# File.date_updated
#


class FileItemBase(QtGui.QStandardItem):
    """A custom QStandardItem to hold File related data."""

    def __init__(self, *args, **kwargs):
        file = kwargs.pop("file", None)
        super().__init__(*args, **kwargs)
        self.fetched_all = False
        self._file = None
        self.file = file

    def _auto_set_text(self):
        """Automatically set the text of the item based on the file."""
        if self.file:
            self.setText(self.file.name)
        else:
            self.setText("No File Set")

    @property
    def file(self) -> Union[None, File]:
        return self._file

    @file.setter
    def file(self, file: File) -> None:
        """Set the file and update the item text.

        Args:
            file (File): The file to set.

        Raises:
            TypeError: If the given file is not an instance of stalker.File.
        """
        if not isinstance(file, File):
            raise TypeError(
                "file should be an instance of stalker.File, "
                f"not {file.__class__.__name__}: '{file}'"
            )
        self._file = file
        self._auto_set_text()

    def canFetchMore(self) -> bool:
        """Return if the file has fetched all its references.

        Returns:
            bool: If the file has fetched all its references.
        """
        return False

    def fetchMore(self) -> None:
        """Fetch more references of the file."""
        pass

    def hasChildren(self):
        """Return if the file has any references."""
        return False

    def type(self, *args: List[Any], **kwargs: Dict) -> int:
        """Generate a custom type to distinguish this item from a QStandardItem.

        Args:
            args (List[Any]): The given arguments.
            kwargs (dict): The given keyword arguments.

        Returns:
            int: The custom user type value.
        """
        return QtGui.QStandardItem.UserType + 1


class FileThumbnailItem(FileItemBase):
    """A custom QStandardItem to hold File.thumbnail related data."""


class FileNameItem(FileItemBase):
    """A custom QStandardItem to hold File.name related data."""


class FileTypeItem(FileItemBase):
    """A custom QStandardItem to hold File.type related data."""

    def _auto_set_text(self):
        """Automatically set the text of the item based on the file."""
        if self.file:
            self.setText(self.file.type.name if self.file.type else "")
        else:
            self.setText("No File Set")


class FileFullPathItem(FileItemBase):
    """A custom QStandardItem to hold File.full_path related data."""

    def _auto_set_text(self):
        """Automatically set the text of the item based on the file."""
        if self.file:
            self.setText(self.file.absolute_full_path)
        else:
            self.setText("No File Set")


class FileCreatedWithItem(FileItemBase):
    """A custom QStandardItem to hold File.created_with related data."""

    def _auto_set_text(self):
        """Automatically set the text of the item based on the file."""
        if self.file:
            self.setText(self.file.created_with)
        else:
            self.setText("No File Set")


class FileAuditItem(FileItemBase):
    """A custom QStandardItem to hold File audit related data."""

    def _auto_set_text(self):
        """Automatically set the text of the item based on the file."""
        if self.file:
            self.setText(self.file.created_by.name if self.file.created_by else "")
        else:
            self.setText("No File Set")


class FileDateCreatedItem(FileItemBase):
    """A custom QStandardItem to hold File.date_created related data."""

    def _auto_set_text(self):
        """Automatically set the text of the item based on the file."""
        if self.file:
            self.setText(self.file.date_created.strftime("%Y-%m-%d %H:%M:%S"))
        else:
            self.setText("No File Set")


class FileDateUpdatedItem(FileItemBase):
    """A custom QStandardItem to hold File.date_updated related data."""

    def _auto_set_text(self):
        """Automatically set the text of the item based on the file."""
        if self.file:
            self.setText(self.file.date_updated.strftime("%Y-%m-%d %H:%M:%S"))
        else:
            self.setText("No File Set")


class FileItem(FileItemBase):
    """A custom QStandardItem to hold File related data."""

    def _auto_set_text(self):
        """Automatically set the text of the item based on the file."""
        if self.file:
            self.setText(self.file.name)
        else:
            self.setText("No File Set")

    def canFetchMore(self) -> bool:
        """Return if the file has fetched all its references.

        Returns:
            bool: If the file has fetched all its references.
        """
        if not self.file:
            return False
        return not self.fetched_all

    def fetchMore(self) -> None:
        """Fetch more references of the file."""
        if not self.file:
            logger.debug("FileItem.fetchMore() is called without a file")
            return
        if self.fetched_all:
            logger.debug("FileItem.fetchMore() is already fetched all")
            return

        for file in self.file.references:
            file_item = FileItem(file=file)
            created_with_item = FileCreatedWithItem(file=file)

            self.appendRow([file_item, created_with_item])

        self.fetched_all = True

    def hasChildren(self):
        """Return if the file has any references."""
        if not self.file:
            return False
        return len(self.file.references) > 0
