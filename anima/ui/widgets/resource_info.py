# -*- coding: utf-8 -*-
# Copyright (c) 2018, Erkan  Ozgur Yilmaz
#
# This module is part of anima-tools and is released under the BSD 2
# License: http://www.opensource.org/licenses/BSD-2-Clause


from anima.ui.lib import QtWidgets


class ResourceInfoWidget(QtWidgets.QWidget):
    """A widget that displays task resource information
    """

    def __init__(self, task=None, parent=None, **kwargs):
        self.task = task
        self.parent = parent

        super(ResourceInfoWidget, self).__init__(parent=parent)

        # storage for UI stuff
        self.vertical_layout = None
        self.header_horizontal_layout = None
        self.responsible_label = None
        self.add_resource_button = None
        self.responsible_grid_layout = None

        self.setup_ui()

    def setup_ui(self):
        """create the UI widgets
        """
        self.vertical_layout = QtWidgets.QVBoxLayout(self)

        self.header_horizontal_layout = QtWidgets.QHBoxLayout()

        self.responsible_label = QtWidgets.QLabel(self)
        self.responsible_label.setText('Resource')
        self.responsible_label.setStyleSheet("""
            background-color: gray;
            font-weight: bold;
            color: white;
            padding: 0.5em;
        """)

        self.add_resource_button = QtWidgets.QPushButton(self)
        self.add_resource_button.setText('+')
        self.add_resource_button.setStyleSheet("""
            background-color: gray;
            color: white;
            padding: 0.5em;
        """)

        self.header_horizontal_layout.addWidget(self.responsible_label)
        self.header_horizontal_layout.addStretch(1)
        self.header_horizontal_layout.addWidget(self.add_resource_button)
        self.header_horizontal_layout.setStretch(0, 1)
        self.header_horizontal_layout.setStretch(1, 0)
        self.vertical_layout.addLayout(self.header_horizontal_layout)

        self.responsible_grid_layout = QtWidgets.QGridLayout()
        self.vertical_layout.addLayout(self.responsible_grid_layout)
