# -*- coding: utf-8 -*-
# Copyright (c) 2018, Erkan  Ozgur Yilmaz
#
# This module is part of anima-tools and is released under the BSD 2
# License: http://www.opensource.org/licenses/BSD-2-Clause

from anima.ui.lib import QtWidgets


class EntityThumbnailWidget(QtWidgets.QWidget):
    """A widget that displays entity thumbnails and allows user to update the
    thumbnail if the user clicks on it
    """

    default_thumbnail_size = 128

    def __init__(self, task=None, parent=None, **kwargs):
        self.task = task
        self.parent = parent

        super(EntityThumbnailWidget, self).__init__(parent=parent)

        # storage for UI elements
        self.vertical_layout = None
        self.thumbnail_graphics_view = None

        self.setup_ui()

    def setup_ui(self):
        """create the UI widgets
        """
        self.vertical_layout = QtWidgets.QVBoxLayout(self)

        from anima.ui.lib import QtCore, QtGui
        # the widget should consist of a QGraphic
        self.thumbnail_graphics_view = QtWidgets.QGraphicsView(self)

        # set size policy
        size_policy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Fixed,
            QtWidgets.QSizePolicy.Fixed
        )
        size_policy.setHorizontalStretch(0)
        size_policy.setVerticalStretch(0)
        size_policy.setHeightForWidth(
            self.thumbnail_graphics_view.sizePolicy().hasHeightForWidth())
        self.thumbnail_graphics_view.setSizePolicy(size_policy)

        # set size
        default_size = QtCore.QSize(
            self.default_thumbnail_size,
            self.default_thumbnail_size
        )

        self.thumbnail_graphics_view.setMinimumSize(default_size)
        self.thumbnail_graphics_view.setMaximumSize(default_size)

        self.thumbnail_graphics_view.setAutoFillBackground(False)
        self.thumbnail_graphics_view.setVerticalScrollBarPolicy(
            QtCore.Qt.ScrollBarAlwaysOff
        )
        self.thumbnail_graphics_view.setHorizontalScrollBarPolicy(
            QtCore.Qt.ScrollBarAlwaysOff
        )
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        self.thumbnail_graphics_view.setBackgroundBrush(brush)
        self.thumbnail_graphics_view.setInteractive(False)
        self.thumbnail_graphics_view.setRenderHints(
            QtGui.QPainter.Antialiasing |
            QtGui.QPainter.HighQualityAntialiasing |
            QtGui.QPainter.SmoothPixmapTransform |
            QtGui.QPainter.TextAntialiasing
        )
        self.vertical_layout.addWidget(self.thumbnail_graphics_view)

    def fill_ui(self):
        """fills the ui with the given task thumbnail
        """
        # clear the thumbnail first
        self.clear_thumbnail()

        from anima.ui import utils
        utils.update_gview_with_task_thumbnail(
            self.task,
            self.thumbnail_graphics_view
        )

    def clear_thumbnail(self):
        """clears the content of the thumbnail
        """
        from anima.ui import utils
        utils.clear_thumbnail(self.thumbnail_graphics_view)
