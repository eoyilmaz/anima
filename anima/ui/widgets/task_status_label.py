# -*- coding: utf-8 -*-
# Copyright (c) 2018, Erkan  Ozgur Yilmaz
#
# This module is part of anima-tools and is released under the BSD 2
# License: http://www.opensource.org/licenses/BSD-2-Clause

from anima.ui.lib import QtWidgets


class TaskStatusLabel(QtWidgets.QLabel):
    """A label for showing task statuses with color codes
    """

    status_colors = {
        'WFD': 'grey',
        'RTS': 'red',
        'WIP': 'orange',
        'HREV': 'purple',
        'DREV': 'dodgerblue',
        'STP': 'red',
        'OH': 'red',
        'CMPL': 'green',
    }

    def __init__(self, task=None, **kwargs):
        self.task = task
        super(TaskStatusLabel, self).__init__(**kwargs)

        self.setup_ui()

    def setup_ui(self):
        """setup the UI
        """
        # self.setMaximumWidth(75)
        # self.setMinimumWidth(75)
        self.setMaximumHeight(16)

        from anima.ui.lib import QtCore
        self.setAlignment(QtCore.Qt.AlignCenter)
        if self.task:
            status_color = self.status_colors[self.task.status.code]
            self.setStyleSheet(
                """
                    background-color: %s;
                    color: white;
                    text-align: center;
                    padding-left: 0.5em;
                    padding-right: 0.5em;
                """ % status_color
            )
            self.setText(self.task.status.name)
        else:
            self.setText('No Task')
            self.setStyleSheet(
                """
                    background-color: grey;
                    color: white;
                    text-align: center;
                    padding-left: 0.5em;
                    padding-right: 0.5em;
                """
            )
