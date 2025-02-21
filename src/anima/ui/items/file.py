# -*- coding: utf-8 -*-
"""File related items are situated here."""

from anima.ui.lib import QtCore, QtGui, QtWidgets


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


class FileThumbnailItem(QtGui.QStandardItem):
    """A custom QStandardItem to hold File.thumbnail related data."""

    def __init__(self, *args, **kwargs):
        super(FileThumbnailItem, self).__init__(*args, **kwargs)


class FileNameItem(QtGui.QStandardItem):
    """A custom QStandardItem to hold File.name related data."""

    def __init__(self, *args, **kwargs):
        super(FileNameItem, self).__init__(*args, **kwargs)


class FileTypeItem(QtGui.QStandardItem):
    """A custom QStandardItem to hold File.type related data."""

    def __init__(self, *args, **kwargs):
        super(FileTypeItem, self).__init__(*args, **kwargs)


class FileFullPathItem(QtGui.QStandardItem):
    """A custom QStandardItem to hold File.full_path related data."""

    def __init__(self, *args, **kwargs):
        super(FileFullPathItem, self).__init__(*args, **kwargs)


class FileCreatedWithItem(QtGui.QStandardItem):
    """A custom QStandardItem to hold File.created_with related data."""

    def __init__(self, *args, **kwargs):
        super(FileCreatedWithItem, self).__init__(*args, **kwargs)


class FileAuditItem(QtGui.QStandardItem):
    """A custom QStandardItem to hold File audit related data."""

    def __init__(self, *args, **kwargs):
        super(FileAuditItem, self).__init__(*args, **kwargs)


class FileDateCreatedItem(QtGui.QStandardItem):
    """A custom QStandardItem to hold File.date_created related data."""

    def __init__(self, *args, **kwargs):
        super(FileDateCreatedItem, self).__init__(*args, **kwargs)


class FileDateUpdatedItem(QtGui.QStandardItem):
    """A custom QStandardItem to hold File.date_updated related data."""

    def __init__(self, *args, **kwargs):
        super(FileDateUpdatedItem, self).__init__(*args, **kwargs)


class FileItem(QtGui.QStandardItem):
    """A custom QStandardItem to hold File related data."""

    def __init__(self, *args, **kwargs):
        super(FileItem, self).__init__(*args, **kwargs)

        self.thumbnail_item = None
        self.name_item = None
        self.type_item = None
        self.full_path_item = None
        self.created_with_item = None
        self.created_by_item = None
        self.updated_by_item = None
        self.date_created_item = None
        self.date_updated_item = None
