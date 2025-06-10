# -*- coding: utf-8 -*-
"""File related item models are situated here."""

from stalker import File
from anima.ui.lib import QtCore, QtGui, QtWidgets
from anima.ui.items.file import (
    FileAuditItem,
    FileCreatedWithItem,
    FileDateCreatedItem,
    FileDateUpdatedItem,
    FileFullPathItem,
    FileItem,
    FileNameItem,
    FileThumbnailItem,
    FileTypeItem,
)


class FileItemModel(QtGui.QStandardItemModel):
    """A custom QStandardItemModel to hold File related data."""

    def __init__(self, *args, **kwargs):
        super(FileItemModel, self).__init__(*args, **kwargs)

    def populate(self, file: File):
        """Populate the model with the given file data.

        Args:
            file (File): A file instance.
        """
        self.clear()

        # create items
        file_item = FileItem(0, 7, file=file)
        thumbnail_item = FileThumbnailItem(file=file)
        name_item = FileNameItem(file=file)
        type_item = FileTypeItem(file=file)
        full_path_item = FileFullPathItem(file=file)
        created_with_item = FileAuditItem(file=file)
        created_by_item = FileAuditItem(file=file)
        date_created_item = FileDateCreatedItem(file=file)
        date_updated_item = FileDateUpdatedItem(file=file)

        # set items
        self.setItem(0, 0, thumbnail_item)
        self.setItem(1, 0, name_item)
        self.setItem(2, 0, type_item)
        self.setItem(3, 0, full_path_item)
        self.setItem(4, 0, created_with_item)
        self.setItem(5, 0, created_by_item)
        self.setItem(6, 0, date_created_item)
        self.setItem(7, 0, date_updated_item)
