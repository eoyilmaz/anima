# -*- coding: utf-8 -*-
# Copyright (c) 2018, Erkan  Ozgur Yilmaz
#
# This module is part of anima-tools and is released under the BSD 2
# License: http://www.opensource.org/licenses/BSD-2-Clause


from anima.ui.lib import QtWidgets


class TaskDetailWidget(QtWidgets.QWidget):
    """Displays simple task details
    """

    def __init__(self, task=None, parent=None, **kwargs):
        self.task = task
        self.parent = parent
        super(TaskDetailWidget, self).__init__(parent=parent)

        # storage for UI stuff
        self.vertical_layout = None
        self.form_layout = None
        self.name_label = None
        self.name_field = None
        self.type_label = None
        self.type_field = None
        self.created_by_label = None
        self.created_by_field = None
        self.updated_by_label = None
        self.updated_by_field = None
        self.timing_label = None
        self.timing_field = None
        self.priority_label = None
        self.priority_field = None

        self.setup_ui()

    def setup_ui(self):
        """creates the UI widgets
        """
        self.setStyleSheet("""
        QLabel[labelField="true"] {
            font-weight: bold;
        }
        """)

        # the main layout
        self.vertical_layout = QtWidgets.QVBoxLayout(self)

        # the form layout
        from anima.ui.lib import QtCore
        self.form_layout = QtWidgets.QFormLayout()
        self.form_layout.setLabelAlignment(
            QtCore.Qt.AlignRight |
            QtCore.Qt.AlignTrailing |
            QtCore.Qt.AlignVCenter
        )
        self.vertical_layout.addLayout(self.form_layout)

        i = -1
        # -------------------------------------------------------------
        # Name Field
        i += 1
        self.name_label = QtWidgets.QLabel(self)
        self.name_label.setText("Name")
        self.name_label.setProperty("labelField", True)

        self.name_field = QtWidgets.QLineEdit(self)

        self.form_layout.setWidget(
            i,
            QtWidgets.QFormLayout.LabelRole,
            self.name_label
        )
        self.form_layout.setWidget(
            i,
            QtWidgets.QFormLayout.FieldRole,
            self.name_field
        )

        # -------------------------------------------------------------
        # Type Field
        i += 1
        self.type_label = QtWidgets.QLabel(self)
        self.type_label.setText("Type")
        self.type_label.setProperty("labelField", True)

        self.type_field = QtWidgets.QComboBox(self)

        self.form_layout.setWidget(
            i,
            QtWidgets.QFormLayout.LabelRole,
            self.type_label
        )
        self.form_layout.setWidget(
            i,
            QtWidgets.QFormLayout.FieldRole,
            self.type_field
        )

        # -------------------------------------------------------------
        # Created By Field
        i += 1
        self.created_by_label = QtWidgets.QLabel(self)
        self.created_by_label.setText("Created By")
        self.created_by_label.setProperty("labelField", True)

        self.created_by_field = QtWidgets.QLabel(self)

        self.form_layout.setWidget(
            i,
            QtWidgets.QFormLayout.LabelRole,
            self.created_by_label
        )
        self.form_layout.setWidget(
            i,
            QtWidgets.QFormLayout.FieldRole,
            self.created_by_field
        )

        # -------------------------------------------------------------
        # Updated By Field
        i += 1
        self.updated_by_label = QtWidgets.QLabel(self)
        self.updated_by_label.setText("Updated By")
        self.updated_by_label.setProperty("labelField", True)

        self.updated_by_field = QtWidgets.QLabel(self)

        self.form_layout.setWidget(
            i,
            QtWidgets.QFormLayout.LabelRole,
            self.updated_by_label
        )
        self.form_layout.setWidget(
            i,
            QtWidgets.QFormLayout.FieldRole,
            self.updated_by_field
        )

        # -------------------------------------------------------------
        # Timing Field
        i += 1
        self.timing_label = QtWidgets.QLabel(self)
        self.timing_label.setText("Timing")
        self.timing_label.setProperty("labelField", True)

        self.timing_field = QtWidgets.QLabel(self)
        self.timing_field.setText('23 Hours ago -> an Hour ago!')

        self.form_layout.setWidget(
            i,
            QtWidgets.QFormLayout.LabelRole,
            self.timing_label
        )
        self.form_layout.setWidget(
            i,
            QtWidgets.QFormLayout.FieldRole,
            self.timing_field
        )

        # -------------------------------------------------------------
        # Priority
        i += 1
        self.priority_label = QtWidgets.QLabel(self)
        self.priority_label.setText("Priority")
        self.priority_label.setProperty("labelField", True)

        self.priority_field = QtWidgets.QLabel(self)
        self.priority_field.setText('950')

        self.form_layout.setWidget(
            i,
            QtWidgets.QFormLayout.LabelRole,
            self.priority_label
        )
        self.form_layout.setWidget(
            i,
            QtWidgets.QFormLayout.FieldRole,
            self.priority_field
        )
