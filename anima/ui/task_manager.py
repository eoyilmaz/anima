# -*- coding: utf-8 -*-
# Copyright (c) 2012-2018, Anima Istanbul
#
# This module is part of anima-tools and is released under the BSD 2
# License: http://www.opensource.org/licenses/BSD-2-Clause

from anima.ui.base import AnimaDialogBase, ui_caller
from anima.ui.lib import QtCore, QtWidgets, QtGui


def UI(app_in=None, executor=None, **kwargs):
    """
    :param app_in: A Qt Application instance, which you can pass to let the UI
      be attached to the given applications event process.

    :param executor: Instead of calling app.exec_ the UI will call this given
      function. It also passes the created app instance to this executor.

    """
    return ui_caller(app_in, executor, MainDialog, **kwargs)


class MainDialog(QtWidgets.QDialog, AnimaDialogBase):
    """Bulk Task Manager Dialog to manage tasks in bulk.

    This UI filters parent tasks and displays the child tasks in a
    QTableWidget.
    """

    def __init__(self, parent=None):
        super(MainDialog, self).__init__(parent=parent)

        self.generic_selection_text = '== ALL =='

        self._setup_ui()
        self._setup_signals()
        self._fill_ui()

    def _setup_ui(self):
        """create the ui elements
        """
        self.resize(1350, 950)
        self.vertical_layout = QtWidgets.QVBoxLayout(self)

        # Dialog Label
        self.dialog_label = QtWidgets.QLabel(self)
        self.dialog_label.setText('Task Manager')
        self.dialog_label.setStyleSheet("color: rgb(71, 143, 202);font: 18pt;")
        self.vertical_layout.addWidget(self.dialog_label)

        # Title Line
        line = QtWidgets.QFrame(self)
        line.setFrameShape(QtWidgets.QFrame.HLine)
        line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.vertical_layout.addWidget(line)

        # --------------------------------------------
        # Filter Fields
        label_role = QtWidgets.QFormLayout.LabelRole
        field_role = QtWidgets.QFormLayout.FieldRole

        expanding = QtWidgets.QSizePolicy.Expanding
        fixed = QtWidgets.QSizePolicy.Fixed
        minimum = QtWidgets.QSizePolicy.Minimum

        # Filters Form Layout
        self.filters_form_layout = QtWidgets.QFormLayout()
        self.filters_form_layout.setLabelAlignment(
            QtCore.Qt.AlignRight |
            QtCore.Qt.AlignTrailing |
            QtCore.Qt.AlignVCenter
        )
        self.vertical_layout.addLayout(self.filters_form_layout)

        # Filer By Label
        i = 0
        self.filter_by_label = QtWidgets.QLabel(self)
        self.filter_by_label.setText('Filter By')
        self.filters_form_layout.setWidget(
            i, field_role, self.filter_by_label
        )
        i += 1

        # Project
        #   Label
        self.filter_by_project_label = QtWidgets.QLabel(self)
        self.filter_by_project_label.setText('Project')

        self.filters_form_layout.setWidget(
            i, label_role, self.filter_by_project_label
        )

        #   Field
        self.filter_by_project_combo_box = QtWidgets.QComboBox(self)
        self.filter_by_project_combo_box.setSizePolicy(expanding, fixed)
        self.filter_by_project_combo_box.setEditable(True)

        self.filters_form_layout.setWidget(
            i, field_role, self.filter_by_project_combo_box
        )
        i += 1

        # Entity Type
        #   Label
        self.filter_by_entity_type_label = QtWidgets.QLabel(self)
        self.filter_by_entity_type_label.setText('Entity Type')
        self.filters_form_layout.setWidget(
            i, label_role, self.filter_by_entity_type_label
        )

        #   Field
        self.filter_by_entity_type_combo_box = QtWidgets.QComboBox(self)
        self.filter_by_entity_type_combo_box.setSizePolicy(expanding, fixed)
        self.filters_form_layout.setWidget(
            i, field_role, self.filter_by_entity_type_combo_box
        )
        i += 1

        # Task Type
        #   Label
        self.filter_by_task_type_label = QtWidgets.QLabel(self)
        self.filter_by_task_type_label.setText('Task Type')
        self.filters_form_layout.setWidget(
            i, label_role, self.filter_by_task_type_label
        )

        #   Field
        self.filter_by_task_type_combo_box = QtWidgets.QComboBox(self)
        self.filter_by_task_type_combo_box.setSizePolicy(expanding, fixed)
        self.filters_form_layout.setWidget(
            i, field_role, self.filter_by_task_type_combo_box
        )
        i += 1

        # Sequence
        #   Only visible when entity type is Shot
        #   Label
        self.filter_by_sequence_label = QtWidgets.QLabel(self)
        self.filter_by_sequence_label.setText('Sequence')
        self.filters_form_layout.setWidget(
            i, label_role, self.filter_by_sequence_label
        )

        #   Field
        self.filter_by_sequence_combo_box = QtWidgets.QComboBox(self)
        self.filter_by_sequence_combo_box.setSizePolicy(expanding, fixed)
        self.filters_form_layout.setWidget(
            i, field_role, self.filter_by_sequence_combo_box
        )
        i += 1

        # Resource
        #   Label
        self.filter_by_resource_label = QtWidgets.QLabel(self)
        self.filter_by_resource_label.setText('Resource')
        self.filters_form_layout.setWidget(
            i, label_role, self.filter_by_resource_label
        )

        #   Field
        self.filter_by_resource_combo_box = QtWidgets.QComboBox(self)
        self.filter_by_resource_combo_box.setSizePolicy(expanding, fixed)
        self.filters_form_layout.setWidget(
            i, field_role, self.filter_by_resource_combo_box
        )
        i += 1

        # ------------------------------------------------
        # Filter Button
        self.filter_button_horizontal_layout = QtWidgets.QHBoxLayout(self)
        self.filters_form_layout.setLayout(
            i, field_role, self.filter_button_horizontal_layout
        )

        self.filter_push_button = QtWidgets.QPushButton(self)
        self.filter_push_button.setText('-> Apply Filter <-')
        self.filter_button_horizontal_layout.addWidget(self.filter_push_button)

        # spacer
        spacer = QtWidgets.QSpacerItem(40, 20, expanding, minimum)
        self.filter_button_horizontal_layout.addItem(spacer)

        # ------------------------------------------------
        # The main table widget
        self.data_table_widget = QtWidgets.QTableWidget(self)
        self.data_table_widget.setAutoFillBackground(True)
        self.data_table_widget.setEditTriggers(
            QtWidgets.QAbstractItemView.NoEditTriggers
        )
        self.data_table_widget.setColumnCount(2)
        self.data_table_widget.setRowCount(0)
        item = QtWidgets.QTableWidgetItem()
        self.data_table_widget.setHorizontalHeaderItem(0, item)

        item = QtWidgets.QTableWidgetItem()
        self.data_table_widget.setHorizontalHeaderItem(1, item)

        self.data_table_widget.horizontalHeader().setStretchLastSection(True)
        self.vertical_layout.addWidget(self.data_table_widget)

    def _setup_signals(self):
        """setup signals
        """
        # Filter By Project ComboBox
        QtCore.QObject.connect(
            self.filter_by_project_combo_box,
            QtCore.SIGNAL('currentIndexChanged(QString)'),
            self.filter_by_project_combo_box_changed
        )

        QtCore.QObject.connect(
            self.filter_by_entity_type_combo_box,
            QtCore.SIGNAL('currentIndexChanged(QString)'),
            self.filter_by_entity_type_combo_box_changed
        )

        QtCore.QObject.connect(
            self.filter_push_button,
            QtCore.SIGNAL('clicked()'),
            self.filter_push_button_clicked
        )

    def _fill_ui(self):
        """fills the UI
        """
        from stalker import Project
        self.filter_by_project_combo_box.addItem(
            self.generic_selection_text,
            -1
        )
        for p in Project.query.order_by(Project.name).all():
            self.filter_by_project_combo_box.addItem(
                p.name, p.id
            )

        self.filter_by_entity_type_combo_box.addItems(
            # [self.generic_selection_text, 'Task', 'Asset', 'Shot', 'Sequence']
            [self.generic_selection_text, 'Asset', 'Shot', 'Sequence']
        )

        # disable the task type field by default
        self.filter_by_task_type_combo_box.setEnabled(False)
        self.filter_by_sequence_combo_box.setEnabled(False)

    def get_project_id(self):
        """returns the current project id
        """
        project_id = -1
        try:
            project_id = self.filter_by_project_combo_box.currentData()
        except AttributeError:
            index = self.filter_by_project_combo_box.currentIndex()
            project_id = self.filter_by_project_combo_box.itemData(index)
        return project_id

    def get_project(self):
        """returns the project from the filter combo box
        """
        project_id = self.get_project_id()
        from stalker import Project
        return Project.query.get(project_id)

    def filter_by_project_combo_box_changed(self, text):
        """runs when the selection in filter_by_project_combo_box has changed
        """
        # get project
        project_id = self.get_project_id()
        from stalker import db, User
        if project_id == -1:
            resources = db.DBSession.query(User.id, User.name).all()
        else:
            from stalker import ProjectUser
            resources = db.DBSession\
                .query(User.id, User.name)\
                .join(ProjectUser)\
                .filter(ProjectUser.project_id == project_id)\
                .order_by(User.name)\
                .all()

        self.filter_by_resource_combo_box.clear()
        self.filter_by_resource_combo_box.addItem(
            self.generic_selection_text,
            -1
        )
        for u in resources:
            self.filter_by_resource_combo_box.addItem(u.name, u.id)

        # sequence combo box
        self.filter_by_sequence_combo_box.clear()
        self.filter_by_sequence_combo_box.addItem(
            self.generic_selection_text,
            -1
        )
        if project_id != -1:
            from stalker import Sequence
            seqs = db.DBSession\
                .query(Sequence.id, Sequence.name)\
                .filter(Sequence.project_id == project_id)\
                .order_by(Sequence.name)\
                .all()
            for seq in seqs:
                self.filter_by_sequence_combo_box.addItem(seq.name, seq.id)

    def filter_by_entity_type_combo_box_changed(self):
        """runs when the selection in filter_by_entity_type_combo_box is has
        changed
        """
        # get the entity type
        entity_type = self.filter_by_entity_type_combo_box.currentText()

        if entity_type == self.generic_selection_text:
            # disable task type field
            self.filter_by_task_type_combo_box.clear()
            self.filter_by_task_type_combo_box.addItem(
                self.generic_selection_text,
                -1
            )
            self.filter_by_task_type_combo_box.setEnabled(False)
        else:
            # get all the unique types from the database for that entity type
            from stalker import Type
            all_types = Type.query\
                .filter(Type.target_entity_type == entity_type)\
                .all()
            self.filter_by_task_type_combo_box.clear()
            self.filter_by_task_type_combo_box.setEnabled(True)
            self.filter_by_task_type_combo_box.addItem(
                self.generic_selection_text,
                -1
            )
            for t in all_types:
                self.filter_by_task_type_combo_box.addItem(t.name, t.id)

            if entity_type == 'Shot':
                # enable the sequence field
                self.filter_by_sequence_combo_box.setEnabled(True)

    def get_sequence_id(self):
        """returns the current sequence_id
        """
        try:
            sequence_id = self.filter_by_sequence_combo_box.currentData()
        except AttributeError:
            index = self.filter_by_sequence_combo_box.currentIndex()
            sequence_id = self.filter_by_sequence_combo_box.itemData(index)
        return sequence_id

    def get_task_type_id(self):
        """returns the task_type_id
        """
        try:
            task_type_id = self.filter_by_task_type_combo_box.currentData()
        except AttributeError:
            index = self.filter_by_task_type_combo_box.currentIndex()
            task_type_id = self.filter_by_task_type_combo_box.itemData(index)
        return task_type_id

    def get_resource_id(self):
        """returns the resource_id
        """
        try:
            resource_id = self.filter_by_resource_combo_box.currentData()
        except AttributeError:
            index = self.filter_by_resource_combo_box.currentIndex()
            resource_id = self.filter_by_resource_combo_box.itemData(index)
        return resource_id

    def get_filtered_entities(self):
        """returns the filtered entities according to the filter selection
        """
        project_id = self.get_project_id()
        entity_type = self.filter_by_entity_type_combo_box.currentText()
        sequence_id = self.get_sequence_id()
        task_type_id = self.get_task_type_id()
        resource_id = self.get_resource_id()

        from stalker import db, Task
        from stalker.db.session import DBSession
        query = DBSession.query(Task.id, Task.name)

        if project_id != -1:
            query = query.filter(Task.project_id == project_id)

        if task_type_id != -1:
            query = query.filter(Task.type_id == task_type_id)

        if entity_type != self.generic_selection_text:
            query = query.filter(Task.entity_type == entity_type)

            # if entity_type == 'Shot':
            #     from stalker.models.shot import Shot_Sequences
            #     query = query.filter(Shot_Sequences)

        # query the child tasks
        query = query.order_by(Task.name)

        return query.all()

    def filter_push_button_clicked(self):
        """runs when the filter_push_button is clicked
        """
        self.fill_table_widget()

    def fill_table_widget(self):
        """fills the table widget with data
        """
        task_data = self.get_filtered_entities()
        self.data_table_widget.clear()
        self.data_table_widget.setRowCount(len(task_data))
        for i, t_data in enumerate(task_data):
            item = QtWidgets.QTableWidgetItem(t_data.name)
            self.data_table_widget.setItem(i, 0, item)

