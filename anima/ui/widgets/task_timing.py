# -*- coding: utf-8 -*-


from anima.ui.lib import QtCore, QtWidgets


class TaskTimingInfoWidget(QtWidgets.QWidget):
    """Displays task timing details"""

    def __init__(self, task=None, parent=None, **kwargs):
        self._task = None
        self.parent = parent
        super(TaskTimingInfoWidget, self).__init__(parent=parent)

        # storage for UI stuff
        self.vertical_layout = None
        self.title_label = None
        self.form_layout = None
        self.bid_label = None
        self.bid_field = None
        self.schedule_timing_label = None
        self.schedule_timing_field = None
        self.total_time_logs_label = None
        self.total_time_logs_field = None
        self.time_to_complete_label = None
        self.time_to_complete_field = None
        self.schedule_model_label = None
        self.schedule_model_field = None

        self._setup_ui()
        self.task = task

    def _setup_ui(self):
        """creates the UI widgets"""
        self.setStyleSheet(
            """
            QLabel{
                background-color: #d9edf7;
                color: #3a87ad;
                padding-top: 2px;
                padding-bottom: 2px;
            }
            QLabel[labelField="true"] {
                font-weight: bold;
            }
        """
        )

        # the main layout
        self.vertical_layout = QtWidgets.QVBoxLayout(self)

        # -------------------------------------------------------------
        # Title Label
        self.title_label = QtWidgets.QLabel(self)
        self.title_label.setText("Timing (0 TimeLogs)")
        self.title_label.setAlignment(QtCore.Qt.AlignCenter)
        self.title_label.setStyleSheet(
            """
            font-weight: bold;
            background-color: white;
            color: #7c9fca;
        """
        )
        self.vertical_layout.addWidget(self.title_label)

        # the form layout
        self.form_layout = QtWidgets.QFormLayout()
        self.form_layout.setLabelAlignment(
            QtCore.Qt.AlignRight | QtCore.Qt.AlignTrailing | QtCore.Qt.AlignVCenter
        )
        self.form_layout.setSpacing(2)
        self.vertical_layout.addLayout(self.form_layout)

        i = -1
        label_width = 120
        field_width = 60
        label_align = QtCore.Qt.AlignRight
        # -------------------------------------------------------------
        # Bid Field
        i += 1
        self.bid_label = QtWidgets.QLabel(self)
        self.bid_label.setText("Bid")
        self.bid_label.setProperty("labelField", True)
        self.bid_label.setMinimumWidth(label_width)
        self.bid_label.setAlignment(label_align)

        self.bid_field = QtWidgets.QLabel(self)
        self.bid_field.setMinimumWidth(field_width)

        self.form_layout.setWidget(i, QtWidgets.QFormLayout.LabelRole, self.bid_label)
        self.form_layout.setWidget(i, QtWidgets.QFormLayout.FieldRole, self.bid_field)

        # -------------------------------------------------------------
        # Schedule Timing Field
        i += 1
        self.schedule_timing_label = QtWidgets.QLabel(self)
        self.schedule_timing_label.setText("Schedule Timing")
        self.schedule_timing_label.setProperty("labelField", True)
        self.schedule_timing_label.setMinimumWidth(label_width)
        self.schedule_timing_label.setAlignment(label_align)

        self.schedule_timing_field = QtWidgets.QLabel(self)
        self.schedule_timing_field.setMinimumWidth(field_width)

        self.form_layout.setWidget(
            i, QtWidgets.QFormLayout.LabelRole, self.schedule_timing_label
        )
        self.form_layout.setWidget(
            i, QtWidgets.QFormLayout.FieldRole, self.schedule_timing_field
        )

        # -------------------------------------------------------------
        # Total TimeLogs Field
        i += 1
        self.total_time_logs_label = QtWidgets.QLabel(self)
        self.total_time_logs_label.setText("Total Time Logs")
        self.total_time_logs_label.setProperty("labelField", True)
        self.total_time_logs_label.setMinimumWidth(label_width)
        self.total_time_logs_label.setAlignment(label_align)

        self.total_time_logs_field = QtWidgets.QLabel(self)
        self.total_time_logs_field.setMinimumWidth(field_width)

        self.form_layout.setWidget(
            i, QtWidgets.QFormLayout.LabelRole, self.total_time_logs_label
        )
        self.form_layout.setWidget(
            i, QtWidgets.QFormLayout.FieldRole, self.total_time_logs_field
        )

        # -------------------------------------------------------------
        # Time To Complete Field
        i += 1
        self.time_to_complete_label = QtWidgets.QLabel(self)
        self.time_to_complete_label.setText("Time To Complete")
        self.time_to_complete_label.setProperty("labelField", True)
        self.time_to_complete_label.setMinimumWidth(label_width)
        self.time_to_complete_label.setAlignment(label_align)

        self.time_to_complete_field = QtWidgets.QLabel(self)
        self.time_to_complete_field.setMinimumWidth(field_width)

        self.form_layout.setWidget(
            i, QtWidgets.QFormLayout.LabelRole, self.time_to_complete_label
        )
        self.form_layout.setWidget(
            i, QtWidgets.QFormLayout.FieldRole, self.time_to_complete_field
        )

        # -------------------------------------------------------------
        # Schedule Model Field
        i += 1
        self.schedule_model_label = QtWidgets.QLabel(self)
        self.schedule_model_label.setText("Schedule Model")
        self.schedule_model_label.setProperty("labelField", True)
        self.schedule_model_label.setMinimumWidth(label_width)
        self.schedule_model_label.setAlignment(label_align)

        self.schedule_model_field = QtWidgets.QLabel(self)
        self.schedule_model_field.setMinimumWidth(field_width)

        self.form_layout.setWidget(
            i, QtWidgets.QFormLayout.LabelRole, self.schedule_model_label
        )
        self.form_layout.setWidget(
            i, QtWidgets.QFormLayout.FieldRole, self.schedule_model_field
        )

    @property
    def task(self):
        """the getter for the _task attribute"""
        return self._task

    @task.setter
    def task(self, task):
        """setter for the task property

        :param task: A Stalker Task instance
        :return:
        """
        from stalker import Task

        if isinstance(task, Task):
            self._task = task

            self.bid_field.setText("%s %s" % (task.bid_timing, task.bid_unit))
            self.schedule_timing_field.setText(
                "%s %s" % (task.schedule_timing, task.schedule_unit)
            )
            self.total_time_logs_field.setText(
                "%s %s" % task.least_meaningful_time_unit(task.total_logged_seconds)
            )
            self.time_to_complete_field.setText(
                "%s %s"
                % task.least_meaningful_time_unit(
                    task.total_seconds - task.total_logged_seconds
                )
            )

            self.schedule_model_field.setText(task.schedule_model)
        else:
            field_value = "No Task"
            self.bid_field.setText(field_value)
            self.schedule_timing_field.setText(field_value)
            self.total_time_logs_field.setText(field_value)
            self.time_to_complete_field.setText(field_value)
            self._task = None
