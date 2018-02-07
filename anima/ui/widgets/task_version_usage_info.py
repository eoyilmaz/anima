# -*- coding: utf-8 -*-
# Copyright (c) 2018, Erkan  Ozgur Yilmaz
#
# This module is part of anima-tools and is released under the BSD 2
# License: http://www.opensource.org/licenses/BSD-2-Clause


from anima.ui.lib import QtWidgets


class TaskVersionUsageInfoWidget(QtWidgets.QWidget):
    """A widget that displays task version usage information
    """

    def __init__(self, task=None, parent=None, **kwargs):
        self.task = task
        self.parent = parent

        super(TaskVersionUsageInfoWidget, self).__init__(parent=parent)

        # storage for UI stuff
        self.vertical_layout = None
        self.header_horizontal_layout = None
        self.versions_use_in_label = None
        self.add_resource_button = None
        self.responsible_grid_layout = None

        self.setup_ui()

    def setup_ui(self):
        """create the UI widgets
        """
        self.vertical_layout = QtWidgets.QVBoxLayout(self)

        self.header_horizontal_layout = QtWidgets.QHBoxLayout()

        self.versions_use_in_label = QtWidgets.QLabel(self)
        self.versions_use_in_label.setText('Versions are used in')
        self.versions_use_in_label.setStyleSheet("""
            background-color: gray;
            color: white;
            font-weight: bold;
            padding: 0.5em;
        """)

        self.header_horizontal_layout.addWidget(self.versions_use_in_label)
        self.vertical_layout.addLayout(self.header_horizontal_layout)
