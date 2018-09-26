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
        self.type_field_is_updating = False
        self.created_by_label = None
        self.created_by_field = None
        self.updated_by_label = None
        self.updated_by_field = None
        self.timing_label = None
        self.timing_field = None
        self.priority_label = None
        self.priority_field = None
        self.cut_in_label = None
        self.cut_in_field = None
        self.cut_out_label = None
        self.cut_out_field = None

        self.setup_ui()
        self.fill_ui()

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

        # -------------------------------------------------------------
        # Cut In
        i += 1
        self.cut_in_label = QtWidgets.QLabel(self)
        self.cut_in_label.setText("Cut In")
        self.cut_in_label.setProperty("labelField", True)

        self.cut_in_field = QtWidgets.QLabel(self)
        self.cut_in_field.setText('1')

        self.form_layout.setWidget(
            i,
            QtWidgets.QFormLayout.LabelRole,
            self.cut_in_label
        )
        self.form_layout.setWidget(
            i,
            QtWidgets.QFormLayout.FieldRole,
            self.cut_in_field
        )

        # -------------------------------------------------------------
        # Cut Out
        i += 1
        self.cut_out_label = QtWidgets.QLabel(self)
        self.cut_out_label.setText("Cut Out")
        self.cut_out_label.setProperty("labelField", True)

        self.cut_out_field = QtWidgets.QLabel(self)
        self.cut_out_field.setText('1')

        self.form_layout.setWidget(
            i,
            QtWidgets.QFormLayout.LabelRole,
            self.cut_out_label
        )
        self.form_layout.setWidget(
            i,
            QtWidgets.QFormLayout.FieldRole,
            self.cut_out_field
        )

        # Create signals
        QtCore.QObject.connect(
            self.type_field,
            QtCore.SIGNAL('currentIndexChanged(QString)'),
            self.type_field_changed
        )

    def fill_ui(self):
        """fill the ui with the data
        """
        if self.task:
            self.name_field.setText(self.task.name)

            self._fill_task_type_widget()

            if self.task.created_by:
                self.created_by_field.setText(self.task.created_by.name)

            if self.task.updated_by:
                self.updated_by_field.setText(self.task.updated_by.name)

            self.timing_field.setText(
                '%s - %s' % (
                    self.task.start.strftime('%d-%m-%Y %H:%M'),
                    self.task.end.strftime('%d-%m-%Y %H:%M')
                )
            )

            self.priority_field.setText('%s' % self.task.priority)

            from stalker import Shot
            if isinstance(self.task, Shot):
                self.cut_in_field.setText('%s' % self.task.cut_in)
                self.cut_out_field.setText('%s' % self.task.cut_out)
                self.cut_in_label.setVisible(True)
                self.cut_in_field.setVisible(True)
                self.cut_out_label.setVisible(True)
                self.cut_out_field.setVisible(True)
            else:
                self.cut_in_label.setVisible(False)
                self.cut_in_field.setVisible(False)
                self.cut_out_label.setVisible(False)
                self.cut_out_field.setVisible(False)

    def _fill_task_type_widget(self):
        """fills the task type widget
        """
        if self.task is None:
            return

        # get the types
        from stalker import Type
        from stalker.db.session import DBSession
        all_types = \
            DBSession.query(Type.id, Type.name)\
                .filter(Type.target_entity_type == self.task.entity_type)\
                .all()

        self.type_field_is_updating = True
        self.type_field.clear()
        self.type_field.addItem('-- No Type --', -1)
        for type_data in all_types:
            self.type_field.addItem(type_data.name, type_data.id)

        # and select the corresponding type
        if self.task.type:
            index = self.type_field.findData(self.task.type.id)
            if index != -1:
                self.type_field.setCurrentIndex(index)
        self.type_field_is_updating = False

    def type_field_changed(self):
        """runs when the type field has changed
        """
        if self.task is None:
            return

        if self.type_field_is_updating:
            return

        # get the type
        assert isinstance(self.type_field, QtWidgets.QComboBox)
        index = self.type_field.currentIndex()
        type_id = self.type_field.itemData(index)

        if type_id != -1:
            from stalker import Type
            type_ = Type.query.get(type_id)
            self.task.type = type_
            from stalker.db.session import DBSession
            DBSession.save(self.task)
