# -*- coding: utf-8 -*-
# Copyright (c) 2018, Erkan  Ozgur Yilmaz
#
# This module is part of anima-tools and is released under the BSD 2
# License: http://www.opensource.org/licenses/BSD-2-Clause

from anima.ui.lib import QtCore, QtWidgets


class TaskDashboardWidget(QtWidgets.QWidget):
    """A widget that displays task related information
    """

    def __init__(self, task=None, parent=None, **kwargs):
        self.task = task
        self.parent = parent

        super(TaskDashboardWidget, self).__init__(parent=parent)

        # storage for UI stuff
        self.vertical_layout = None
        self.widget_label = None
        self.task_thumbnail_widget = None
        self.schedule_info_form_layout = None
        self.task_detail_widget = None
        self.task_timing_widget = None
        self.description_label = None
        self.description_field = None
        self.responsible_info_widget = None
        self.resource_info_widget = None
        self.task_versions_usage_info_widget = None
        self.watch_task_button = None
        self.fix_task_status_button = None
        self.task_status_label = None
        self.task_progress = None
        self.task_notes_widget = None

        self.setup_ui()
        self.fill_ui()

    def setup_ui(self):
        """create the UI widgets
        """
        # we need a main layout
        # may be a vertical one
        # or a form layout
        self.vertical_layout = QtWidgets.QVBoxLayout(self)

        # -------------------------
        # Dialog Label and buttons
        horizontal_layout3 = QtWidgets.QHBoxLayout()
        self.vertical_layout.addLayout(horizontal_layout3)

        self.widget_label = QtWidgets.QLabel(self)
        self.widget_label.setText(
            self.task.name if self.task else 'Task Name'
        )
        self.widget_label.setStyleSheet(
            "color: rgb(71, 143, 202);\nfont: 18pt;"
        )
        horizontal_layout3.addWidget(self.widget_label)
        horizontal_layout3.addStretch(1)

        # Add Watch Task button
        self.watch_task_button = QtWidgets.QPushButton(self)
        self.watch_task_button.setMaximumWidth(24)
        self.watch_task_button.setMaximumHeight(24)
        self.watch_task_button.setText("W")
        self.watch_task_button.setToolTip("Watch Task")
        self.fix_task_status_button = QtWidgets.QPushButton(self)
        self.fix_task_status_button.setMaximumWidth(24)
        self.fix_task_status_button.setMaximumHeight(24)
        self.fix_task_status_button.setText("F")
        self.fix_task_status_button.setToolTip("Fix Task Status")
        horizontal_layout3.addWidget(self.watch_task_button)
        horizontal_layout3.addWidget(self.fix_task_status_button)

        # Add Status Label
        vertical_layout3 = QtWidgets.QVBoxLayout()
        from anima.ui.widgets.task_status_label import TaskStatusLabel
        self.task_status_label = TaskStatusLabel(task=self.task)
        self.task_status_label.setMaximumHeight(12)
        vertical_layout3.addWidget(self.task_status_label)

        # Add ProgressBar
        self.task_progress = QtWidgets.QProgressBar(self)
        self.task_progress.setMinimum(0)
        self.task_progress.setMaximum(100)
        self.task_progress.setValue(50)
        self.task_progress.setAlignment(QtCore.Qt.AlignCenter)
        self.task_progress.setMaximumHeight(12)
        self.task_progress.setStyleSheet("""
            QProgressBar::chunk {
                background-color: #3add36;
                width: 1px;
            }
        """)
        vertical_layout3.addWidget(self.task_progress)

        # set items closer to each other
        vertical_layout3.setSpacing(0)

        horizontal_layout3.addLayout(vertical_layout3)

        # Add divider
        line = QtWidgets.QFrame(self)
        line.setFrameShape(QtWidgets.QFrame.HLine)
        line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.vertical_layout.addWidget(line)

        horizontal_layout1 = QtWidgets.QHBoxLayout()
        self.vertical_layout.addLayout(horizontal_layout1)

        vertical_layout1 = QtWidgets.QVBoxLayout()
        vertical_layout2 = QtWidgets.QVBoxLayout()
        horizontal_layout1.addLayout(vertical_layout1)
        horizontal_layout1.addLayout(vertical_layout2)

        # --------------------------
        # Horizontal Layout for thumbnail and detail widgets
        horizontal_layout2 = QtWidgets.QHBoxLayout()
        vertical_layout1.addLayout(horizontal_layout2)

        # --------------------------
        # Task Thumbnail
        from anima.ui.widgets.entity_thumbnail import EntityThumbnailWidget
        self.task_thumbnail_widget = \
            EntityThumbnailWidget(task=self.task, parent=self)

        horizontal_layout2.addWidget(self.task_thumbnail_widget)

        # --------------------------
        # Task Detail Info
        from anima.ui.widgets.task_detail import TaskDetailWidget
        self.task_detail_widget = TaskDetailWidget(task=self.task, parent=self)

        horizontal_layout2.addWidget(self.task_detail_widget)

        # --------------------------
        # Task Timing Info
        from anima.ui.widgets.task_timing import TaskTimingWidget
        self.task_timing_widget = TaskTimingWidget(task=self.task, parent=self)

        horizontal_layout2.addWidget(self.task_timing_widget)

        # add stretcher
        # horizontal_layout2.addStretch(1)

        # --------------------------
        # Description field
        self.description_label = QtWidgets.QLabel(self)
        self.description_label.setStyleSheet("""
        background-color: gray;
        color: white;
        font-weight: bold;
        padding: 0.5em;
        """)
        self.description_label.setText("Description")
        self.description_field = QtWidgets.QTextEdit(self)
        self.description_field.setAcceptRichText(True)
        vertical_layout1.addWidget(self.description_label)
        vertical_layout1.addWidget(self.description_field)

        # add stretcher
        vertical_layout1.addStretch(1)

        # ---------------------------
        # Responsible Info
        from anima.ui.widgets.responsible_info import ResponsibleInfoWidget
        self.responsible_info_widget = ResponsibleInfoWidget(
            task=self.task, parent=self
        )
        vertical_layout2.addWidget(self.responsible_info_widget)

        # ---------------------------
        # Resource Info
        from anima.ui.widgets.resource_info import ResourceInfoWidget
        self.resource_info_widget = ResourceInfoWidget(
            task=self.task, parent=self
        )
        vertical_layout2.addWidget(self.resource_info_widget)

        # ---------------------------
        # Task Versions Usage Info
        from anima.ui.widgets.task_version_usage_info import \
            TaskVersionUsageInfoWidget
        self.task_versions_usage_info_widget = TaskVersionUsageInfoWidget(
            task=self.task, parent=self
        )
        vertical_layout2.addWidget(self.task_versions_usage_info_widget)

        vertical_layout2.addStretch(1)

        horizontal_layout1.setStretch(0, 2)
        horizontal_layout1.setStretch(1, 1)

        # ---------------------------
        # Task Notes
        from anima.ui.widgets.entity_notes import EntityNotesWidgets
        self.task_notes_widget = \
            EntityNotesWidgets(entity=self.task, parent=self)
        self.vertical_layout.addWidget(self.task_notes_widget)

    def fill_ui(self):
        """fills the ui
        """
        self.widget_label.setText(
            self.task.name if self.task else 'Task Name'
        )

        self.task_thumbnail_widget.task = self.task
        self.task_thumbnail_widget.fill_ui()

        self.task_detail_widget.task = self.task
        self.task_detail_widget.fill_ui()

        self.task_timing_widget.task = self.task
        self.task_timing_widget.fill_ui()

        # self.description_label = None
        # self.description_field = None
        # self.responsible_info_widget = None
        # self.resource_info_widget = None
        # self.task_versions_usage_info_widget = None
        # self.watch_task_button = None
        # self.fix_task_status_button = None
        # self.task_status_label = None
        # self.task_progress = None

        self.task_notes_widget.task = self.task
        self.task_notes_widget.fill_ui()

