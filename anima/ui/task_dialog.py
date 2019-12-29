# -*- coding: utf-8 -*-
# Copyright (c) 2012-2019, Anima Istanbul
#
# This module is part of anima and is released under the MIT
# License: http://www.opensource.org/licenses/MIT
import re

from anima import logger
from anima.ui.base import AnimaDialogBase, ui_caller
from anima.ui.lib import QtCore, QtWidgets


def UI(app_in=None, executor=None, **kwargs):
    """
    :param app_in: A Qt Application instance, which you can pass to let the UI
      be attached to the given applications event process.

    :param executor: Instead of calling app.exec_ the UI will call this given
      function. It also passes the created app instance to this executor.

    """
    return ui_caller(app_in, executor, MainDialog, **kwargs)


class MainDialog(QtWidgets.QDialog, AnimaDialogBase):
    """The Task Dialog
    """
    CREATE_MODE = 'Create'
    UPDATE_MODE = 'Update'

    def __init__(self, parent=None, parent_task=None, task=None):
        logger.debug("initializing the interface")
        super(MainDialog, self).__init__(parent)

        # store the logged in user
        self.logged_in_user = None

        self.parent_task = parent_task
        self.task = task
        self.mode = self.CREATE_MODE
        if self.task:
            self.mode = self.UPDATE_MODE

        self._setup()

        self.updating_resources_combo_box = False
        self.updating_responsible_combo_box = False
        self.updating_name_lineEdit = False
        self.updating_code_lineEdit = False

        self.last_selected_dependent_task = None

        self._setup_signals()
        self._set_defaults()

        if self.task:
            self.fill_ui_with_task(self.task)

    def _setup(self):
        """setup the ui elements
        """
        self.setWindowTitle("Task Dialog")
        self.resize(550, 790)
        self.vertical_layout = QtWidgets.QVBoxLayout(self)

        # Dialog Label
        self.dialog_label = QtWidgets.QLabel(self)
        self.dialog_label.setText('%s Task' % self.mode)
        self.dialog_label.setStyleSheet("color: rgb(71, 143, 202);font: 18pt;")
        self.vertical_layout.addWidget(self.dialog_label)

        # Title Line
        line = QtWidgets.QFrame(self)
        line.setFrameShape(QtWidgets.QFrame.HLine)
        line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.vertical_layout.addWidget(line)

        # Form Layout
        self.form_layout = QtWidgets.QFormLayout()
        self.form_layout.setFieldGrowthPolicy(
            QtWidgets.QFormLayout.AllNonFixedFieldsGrow
        )
        self.form_layout.setLabelAlignment(
            QtCore.Qt.AlignRight |
            QtCore.Qt.AlignTrailing |
            QtCore.Qt.AlignVCenter
        )

        form_field_index = 0

        # ----------------------------------------------
        # Project Field
        self.project_label = QtWidgets.QLabel("Project", self)
        self.form_layout.setWidget(
            form_field_index,
            QtWidgets.QFormLayout.LabelRole,
            self.project_label
        )
        self.projects_combo_box = QtWidgets.QComboBox(self)
        self.form_layout.setWidget(
            form_field_index,
            QtWidgets.QFormLayout.FieldRole,
            self.projects_combo_box
        )
        form_field_index += 1

        # ----------------------------------------------
        # Entity Type Field

        # label
        self.entity_type_label = QtWidgets.QLabel("Entity Type", self)
        self.form_layout.setWidget(
            form_field_index,
            QtWidgets.QFormLayout.LabelRole,
            self.entity_type_label
        )

        # field
        self.entity_type_combo_box = QtWidgets.QComboBox(self)

        self.entity_type_combo_box.addItem("Task")
        self.entity_type_combo_box.addItem("Asset")
        self.entity_type_combo_box.addItem("Shot")
        self.entity_type_combo_box.addItem("Sequence")

        self.form_layout.setWidget(
            form_field_index,
            QtWidgets.QFormLayout.FieldRole,
            self.entity_type_combo_box
        )
        form_field_index += 1

        # ----------------------------------------------
        # Parent Task Field
        self.parent_label = QtWidgets.QLabel("Parent", self)
        self.parent_label.setObjectName("parent_label")
        self.form_layout.setWidget(
            form_field_index,
            QtWidgets.QFormLayout.LabelRole,
            self.parent_label
        )
        self.parent_task_fields_vertical_layout = QtWidgets.QVBoxLayout()
        self.parent_task_fields_vertical_layout.setObjectName(
            "parent_task_fields_vertical_layout")
        self.parent_task_fields_horizontal_layout = QtWidgets.QHBoxLayout()
        self.parent_task_fields_horizontal_layout.setObjectName(
            "parent_task_fields_horizontal_layout")

        # Validator
        self.parent_task_validator_label = \
            QtWidgets.QLabel("Validator Message", self)
        self.parent_task_validator_label.setStyleSheet(
            "color: rgb(255, 0, 0);"
        )

        # Line Edit
        from anima.ui.widgets import ValidatedLineEdit
        self.parent_task_line_edit = ValidatedLineEdit(
            message_field=self.parent_task_validator_label
        )
        self.parent_task_line_edit.setEnabled(False)
        self.parent_task_fields_horizontal_layout.addWidget(
            self.parent_task_line_edit
        )

        self.pick_parent_task_push_button = QtWidgets.QPushButton(self)
        self.pick_parent_task_push_button.setToolTip("Pick parent task")
        self.pick_parent_task_push_button.setText("...")

        self.parent_task_fields_horizontal_layout.addWidget(
            self.pick_parent_task_push_button
        )
        self.parent_task_fields_vertical_layout.addLayout(
            self.parent_task_fields_horizontal_layout
        )
        self.parent_task_fields_vertical_layout.addWidget(
            self.parent_task_validator_label
        )
        self.form_layout.setLayout(
            form_field_index,
            QtWidgets.QFormLayout.FieldRole,
            self.parent_task_fields_vertical_layout
        )
        form_field_index += 1

        # ----------------------------------------------
        # Name Fields
        self.name_label = QtWidgets.QLabel("Name", self)
        self.form_layout.setWidget(
            form_field_index,
            QtWidgets.QFormLayout.LabelRole,
            self.name_label
        )
        self.name_field_vertical_layout = QtWidgets.QVBoxLayout()
        self.name_validator_label = QtWidgets.QLabel("Validator Message", self)
        self.name_validator_label.setStyleSheet("color: rgb(255, 0, 0);")

        self.name_line_edit = ValidatedLineEdit(
            message_field=self.name_validator_label
        )
        self.name_field_vertical_layout.addWidget(self.name_line_edit)
        self.name_field_vertical_layout.addWidget(self.name_validator_label)

        self.form_layout.setLayout(
            form_field_index,
            QtWidgets.QFormLayout.FieldRole,
            self.name_field_vertical_layout
        )
        form_field_index += 1

        # ----------------------------------------------
        # Code Fields
        self.code_label = QtWidgets.QLabel("Code", self)
        self.form_layout.setWidget(
            form_field_index,
            QtWidgets.QFormLayout.LabelRole,
            self.code_label
        )
        self.code_field_vertical_layout = QtWidgets.QVBoxLayout()

        # Validator Label
        self.code_validator_label = QtWidgets.QLabel("Validator Message", self)
        self.code_validator_label.setStyleSheet("color: rgb(255, 0, 0);")

        # Validated Line Edit
        self.code_line_edit = ValidatedLineEdit(
            message_field=self.code_validator_label
        )
        self.code_field_vertical_layout.addWidget(self.code_line_edit)
        self.code_field_vertical_layout.addWidget(self.code_validator_label)

        self.form_layout.setLayout(
            form_field_index,
            QtWidgets.QFormLayout.FieldRole,
            self.code_field_vertical_layout
        )
        form_field_index += 1

        # ----------------------------------------------
        # Task Type Fields
        self.task_type_label = QtWidgets.QLabel("Task Type", self)
        self.form_layout.setWidget(
            form_field_index,
            QtWidgets.QFormLayout.LabelRole,
            self.task_type_label
        )

        self.task_type_combo_box = QtWidgets.QComboBox(self)
        self.task_type_combo_box.setEditable(True)
        self.form_layout.setWidget(
            form_field_index,
            QtWidgets.QFormLayout.FieldRole,
            self.task_type_combo_box
        )
        form_field_index += 1

        # ----------------------------------------------
        # Asset Type Fields
        self.asset_type_label = QtWidgets.QLabel("Asset Type", self)
        self.form_layout.setWidget(
            form_field_index,
            QtWidgets.QFormLayout.LabelRole,
            self.asset_type_label
        )

        self.asset_type_combo_box = QtWidgets.QComboBox(self)
        self.asset_type_combo_box.setEditable(True)
        self.form_layout.setWidget(
            form_field_index,
            QtWidgets.QFormLayout.FieldRole,
            self.asset_type_combo_box
        )
        form_field_index += 1

        # ----------------------------------------------
        # Sequence Fields
        self.sequence_label = QtWidgets.QLabel("Sequence", self)
        self.form_layout.setWidget(
            form_field_index,
            QtWidgets.QFormLayout.LabelRole,
            self.sequence_label
        )
        self.sequence_combo_box = QtWidgets.QComboBox(self)
        self.form_layout.setWidget(
            form_field_index,
            QtWidgets.QFormLayout.FieldRole,
            self.sequence_combo_box
        )
        form_field_index += 1

        # ----------------------------------------------
        # FPS Fields
        self.fps_label = QtWidgets.QLabel("FPS", self)
        self.form_layout.setWidget(
            form_field_index,
            QtWidgets.QFormLayout.LabelRole,
            self.fps_label
        )
        self.fps_spin_box = QtWidgets.QSpinBox(self)
        self.fps_spin_box.setMinimum(1)
        self.form_layout.setWidget(
            form_field_index,
            QtWidgets.QFormLayout.FieldRole,
            self.fps_spin_box
        )
        form_field_index += 1

        # ----------------------------------------------
        # CutIn & CutOut Fields
        self.cut_in_cut_out_label = QtWidgets.QLabel("Cut In & Out", self)
        self.form_layout.setWidget(
            form_field_index,
            QtWidgets.QFormLayout.LabelRole,
            self.cut_in_cut_out_label
        )
        self.horizontal_layout_4 = QtWidgets.QHBoxLayout()
        self.cut_in_spin_box = QtWidgets.QSpinBox(self)
        self.cut_in_spin_box.setMaximum(999999)
        self.horizontal_layout_4.addWidget(self.cut_in_spin_box)
        self.cut_out_spin_box = QtWidgets.QSpinBox(self)
        self.cut_out_spin_box.setMaximum(999999)

        self.horizontal_layout_4.addWidget(self.cut_out_spin_box)
        self.form_layout.setLayout(
            form_field_index,
            QtWidgets.QFormLayout.FieldRole,
            self.horizontal_layout_4
        )
        form_field_index += 1

        # ----------------------------------------------
        # Image Format Fields
        from anima.ui.widgets.image_format import ImageFormatWidget
        self.image_format = ImageFormatWidget(
            parent=self,
            parent_form_layout=self.form_layout,
            parent_form_layout_index=form_field_index
        )
        form_field_index += 1

        # ----------------------------------------------
        # DependsTo Fields
        self.depends_to_label = QtWidgets.QLabel("Depends To", self)
        self.form_layout.setWidget(
            form_field_index,
            QtWidgets.QFormLayout.LabelRole,
            self.depends_to_label
        )
        self.horizontal_layout_3 = QtWidgets.QHBoxLayout()
        self.depends_to_listWidget = QtWidgets.QListWidget(self)
        self.depends_to_listWidget.setSelectionMode(
            QtWidgets.QAbstractItemView.MultiSelection
        )
        self.horizontal_layout_3.addWidget(self.depends_to_listWidget)
        self.vertical_layout_3 = QtWidgets.QVBoxLayout()
        self.add_depending_task_pushButton = QtWidgets.QPushButton("+", self)
        self.add_depending_task_pushButton.setToolTip("Add depending task...")
        self.add_depending_task_pushButton.setMaximumSize(
            QtCore.QSize(25, 16777215))
        self.vertical_layout_3.addWidget(self.add_depending_task_pushButton)
        self.remove_depending_task_pushButton =\
            QtWidgets.QPushButton("-", self)
        self.remove_depending_task_pushButton.setToolTip(
            "Remove depending task..."
        )
        self.remove_depending_task_pushButton.setMaximumSize(
            QtCore.QSize(25, 16777215))
        self.vertical_layout_3.addWidget(
            self.remove_depending_task_pushButton)
        spacer_item = QtWidgets.QSpacerItem(
            20, 40,
            QtWidgets.QSizePolicy.Minimum,
            QtWidgets.QSizePolicy.Expanding
        )
        self.vertical_layout_3.addItem(spacer_item)
        self.horizontal_layout_3.addLayout(self.vertical_layout_3)
        self.form_layout.setLayout(
            form_field_index,
            QtWidgets.QFormLayout.FieldRole,
            self.horizontal_layout_3
        )
        form_field_index += 1

        # ----------------------------------------------
        # Resources Fields
        self.resources_label = QtWidgets.QLabel("Resources", self)
        self.form_layout.setWidget(
            form_field_index,
            QtWidgets.QFormLayout.LabelRole,
            self.resources_label
        )
        self.vertical_layout_2 = QtWidgets.QVBoxLayout()
        self.resources_combo_box = QtWidgets.QComboBox(self)
        self.resources_combo_box.setEditable(True)

        self.vertical_layout_2.addWidget(self.resources_combo_box)
        self.resources_listWidget = QtWidgets.QListWidget(self)
        self.resources_listWidget.setToolTip("Double click to remove")
        self.vertical_layout_2.addWidget(self.resources_listWidget)
        self.form_layout.setLayout(
            form_field_index,
            QtWidgets.QFormLayout.FieldRole,
            self.vertical_layout_2
        )
        form_field_index += 1

        # ----------------------------------------------
        # Responsible Fields
        self.responsible_label = QtWidgets.QLabel("Responsible", self)
        self.form_layout.setWidget(
            form_field_index,
            QtWidgets.QFormLayout.LabelRole,
            self.responsible_label
        )
        self.vertical_layout_4 = QtWidgets.QVBoxLayout()
        self.responsible_comboBox = QtWidgets.QComboBox(self)
        self.responsible_comboBox.setEditable(True)
        self.vertical_layout_4.addWidget(self.responsible_comboBox)
        self.responsible_listWidget = QtWidgets.QListWidget(self)
        self.vertical_layout_4.addWidget(self.responsible_listWidget)
        self.form_layout.setLayout(
            form_field_index,
            QtWidgets.QFormLayout.FieldRole,
            self.vertical_layout_4
        )
        form_field_index += 1

        # ----------------------------------------------
        # Schedule Timing Fields
        self.schedule_timing_label = QtWidgets.QLabel("Schedule Timing", self)
        self.form_layout.setWidget(
            form_field_index,
            QtWidgets.QFormLayout.LabelRole,
            self.schedule_timing_label
        )
        self.horizontal_layout_2 = QtWidgets.QHBoxLayout()
        self.schedule_timing_spin_box = QtWidgets.QSpinBox(self)
        self.schedule_timing_spin_box.setMaximum(9999)
        self.horizontal_layout_2.addWidget(self.schedule_timing_spin_box)
        self.schedule_unit_combo_box = QtWidgets.QComboBox(self)
        self.horizontal_layout_2.addWidget(self.schedule_unit_combo_box)
        self.schedule_model_combo_box = QtWidgets.QComboBox(self)
        self.horizontal_layout_2.addWidget(self.schedule_model_combo_box)
        self.form_layout.setLayout(
            form_field_index,
            QtWidgets.QFormLayout.FieldRole,
            self.horizontal_layout_2
        )
        form_field_index += 1

        # ----------------------------------------------
        # Update Bid Fields
        self.update_bid_label = QtWidgets.QLabel("Update Bid", self)
        self.form_layout.setWidget(
            form_field_index,
            QtWidgets.QFormLayout.LabelRole,
            self.update_bid_label
        )
        self.update_bid_check_box = QtWidgets.QCheckBox(self)
        self.update_bid_check_box.setText("")
        self.form_layout.setWidget(
            form_field_index,
            QtWidgets.QFormLayout.FieldRole,
            self.update_bid_check_box
        )
        form_field_index += 1

        # ----------------------------------------------
        # Priority Fields
        self.priority_label = QtWidgets.QLabel("Priority", self)
        self.form_layout.setWidget(
            form_field_index,
            QtWidgets.QFormLayout.LabelRole,
            self.priority_label
        )
        self.priority_spin_box = QtWidgets.QSpinBox(self)
        self.priority_spin_box.setMaximum(1000)
        self.priority_spin_box.setProperty("value", 500)
        self.form_layout.setWidget(
            form_field_index,
            QtWidgets.QFormLayout.FieldRole,
            self.priority_spin_box
        )

        self.vertical_layout.addLayout(self.form_layout)
        form_field_index += 1

        # ----------------------------------------------
        # Button Box
        self.button_box = QtWidgets.QDialogButtonBox(self)
        self.button_box.setOrientation(QtCore.Qt.Horizontal)
        self.button_box.setStandardButtons(
            QtWidgets.QDialogButtonBox.Cancel | QtWidgets.QDialogButtonBox.Ok
        )
        self.vertical_layout.addWidget(self.button_box)

        # ----------------------------------------------
        # Set Tab Order
        self.setTabOrder(self.projects_combo_box, self.entity_type_combo_box)
        self.setTabOrder(
            self.entity_type_combo_box, self.pick_parent_task_push_button
        )
        self.setTabOrder(
            self.pick_parent_task_push_button, self.name_line_edit
        )
        self.setTabOrder(
            self.name_line_edit, self.code_line_edit
        )
        self.setTabOrder(
            self.code_line_edit, self.task_type_combo_box
        )

        self.setTabOrder(self.task_type_combo_box, self.asset_type_combo_box)
        self.setTabOrder(self.asset_type_combo_box, self.sequence_combo_box)
        self.setTabOrder(self.sequence_combo_box, self.fps_spin_box)
        self.setTabOrder(self.fps_spin_box, self.cut_in_spin_box)
        self.setTabOrder(self.cut_in_spin_box, self.cut_out_spin_box)
        self.setTabOrder(self.cut_out_spin_box, self.depends_to_listWidget)
        self.setTabOrder(
            self.depends_to_listWidget, self.add_depending_task_pushButton
        )
        self.setTabOrder(
            self.add_depending_task_pushButton,
            self.remove_depending_task_pushButton
        )
        self.setTabOrder(
            self.remove_depending_task_pushButton, self.resources_combo_box
        )
        self.setTabOrder(self.resources_combo_box, self.resources_listWidget)
        self.setTabOrder(self.resources_listWidget, self.responsible_comboBox)
        self.setTabOrder(
            self.responsible_comboBox, self.responsible_listWidget
        )
        self.setTabOrder(
            self.responsible_listWidget, self.schedule_timing_spin_box
        )
        self.setTabOrder(
            self.schedule_timing_spin_box, self.schedule_unit_combo_box
        )
        self.setTabOrder(
            self.schedule_unit_combo_box, self.schedule_model_combo_box
        )
        self.setTabOrder(
            self.schedule_model_combo_box, self.update_bid_check_box
        )
        self.setTabOrder(self.update_bid_check_box, self.priority_spin_box)

    def show(self):
        """overridden show method
        """
        logger.debug('MainDialog.show is started')
        self.logged_in_user = self.get_logged_in_user()
        if not self.logged_in_user:
            self.reject()
            return_val = None
        else:
            return_val = super(MainDialog, self).show()

        logger.debug('MainDialog.show is finished')
        return return_val

    def _setup_signals(self):
        """set the signals
        """
        # Entity type changed
        QtCore.QObject.connect(
            self.entity_type_combo_box,
            QtCore.SIGNAL('currentIndexChanged(QString)'),
            self.entity_type_combo_box_changed
        )

        # project_comboBox changed
        QtCore.QObject.connect(
            self.projects_combo_box,
            QtCore.SIGNAL('currentIndexChanged(QString)'),
            self.projects_combo_box_changed
        )

        # name_line_edit is changed
        QtCore.QObject.connect(
            self.name_line_edit,
            QtCore.SIGNAL('textChanged(QString)'),
            self.name_line_edit_changed
        )

        # code_line_edit is changed
        QtCore.QObject.connect(
            self.code_line_edit,
            QtCore.SIGNAL('textChanged(QString)'),
            self.code_line_edit_changed
        )

        # pick_task_pushButton
        QtCore.QObject.connect(
            self.pick_parent_task_push_button,
            QtCore.SIGNAL("clicked()"),
            self.pick_parent_task_push_button_clicked
        )

        # add_depending_task_pushButton
        QtCore.QObject.connect(
            self.add_depending_task_pushButton,
            QtCore.SIGNAL('clicked()'),
            self.add_depending_task_push_button_clicked
        )

        # remove_depending_task_pushButton
        QtCore.QObject.connect(
            self.remove_depending_task_pushButton,
            QtCore.SIGNAL('clicked()'),
            self.remove_depending_task_push_button_clicked
        )

        # depends_to_listWidget doubleClicked
        QtCore.QObject.connect(
            self.depends_to_listWidget,
            QtCore.SIGNAL("itemDoubleClicked(QListWidgetItem*)"),
            self.depends_to_list_widget_item_double_clicked
        )

        # resources_combo_box changed
        QtCore.QObject.connect(
            self.resources_combo_box,
            QtCore.SIGNAL('currentIndexChanged(QString)'),
            self.resources_combo_box_changed
        )

        # resources_listWidget doubleClicked
        QtCore.QObject.connect(
            self.resources_listWidget,
            QtCore.SIGNAL("itemDoubleClicked(QListWidgetItem*)"),
            self.resources_list_widget_item_double_clicked
        )

        # responsible_comboBox changed
        QtCore.QObject.connect(
            self.responsible_comboBox,
            QtCore.SIGNAL('currentIndexChanged(QString)'),
            self.responsible_combo_box_changed
        )

        # responsible_listWidget doubleClicked
        QtCore.QObject.connect(
            self.responsible_listWidget,
            QtCore.SIGNAL("itemDoubleClicked(QListWidgetItem*)"),
            self.responsible_list_widget_item_double_clicked
        )

        # button box
        QtCore.QObject.connect(
            self.button_box,
            QtCore.SIGNAL("accepted()"),
            self.accept
        )
        QtCore.QObject.connect(
            self.button_box,
            QtCore.SIGNAL("rejected()"),
            self.reject
        )

    def _set_defaults(self):
        """sets the defaults fro the ui
        """
        # hide validators
        self.parent_task_validator_label.setVisible(False)

        # invalidate the name field by default
        self.name_line_edit.set_invalid('Please enter a name!')

        # hide code area
        self.code_label.setVisible(False)
        self.code_line_edit.setVisible(False)

        # invalidate the code by default
        self.code_line_edit.set_invalid('Please enter a code!')

        # hide asset type area
        self.asset_type_label.setVisible(False)
        self.asset_type_combo_box.setVisible(False)

        # hide shot fields
        self.sequence_label.setVisible(False)
        self.sequence_combo_box.setVisible(False)
        self.fps_label.setVisible(False)
        self.fps_spin_box.setVisible(False)
        self.cut_in_cut_out_label.setVisible(False)
        self.cut_in_spin_box.setVisible(False)
        self.cut_out_spin_box.setVisible(False)
        self.image_format.set_visible(False)

        # hide update bid fields
        self.update_bid_label.setVisible(False)
        self.update_bid_check_box.setVisible(False)

        # fill projects list
        self.projects_combo_box.clear()
        from stalker import Project, Task
        self.projects_combo_box.addItems(
            sorted([p.name for p in Project.query.all()])
        )

        # fill image_format combo_box
        self.image_format.fill_combo_box()

        self.fps_spin_box.setValue(25)

        # select the project if a parent_task or task given
        project = None
        if self.parent_task:
            if isinstance(self.parent_task, Task):
                project = Project.query.get(self.parent_task.project_id)
            elif isinstance(self.parent_task, Project):
                project = self.parent_task
                self.parent_task = None
            if project:
                # set the default value of the fps
                self.fps_spin_box.setValue(project.fps)

        # if there is a parent task also set the responsible to the parent
        # responsible
        if self.parent_task:
            for responsible in self.parent_task.responsible:
                self.responsible_combo_box_changed(responsible.name)

        self.set_project(project)

        # if a parent is given set it to the parent_task_line_edit
        self.set_parent_task(self.parent_task)

        # task types
        from stalker import Type
        from stalker.db.session import DBSession
        all_task_type_names = DBSession.query(Type.name)\
            .filter(Type.target_entity_type == 'Task')\
            .order_by(Type.name.asc())\
            .all()
        self.task_type_combo_box.clear()
        self.task_type_combo_box.addItems(
            [''] + map(lambda x: x[0], all_task_type_names)
        )

        # asset types
        from stalker import Type
        all_asset_type_names = DBSession.query(Type.name)\
            .filter(Type.target_entity_type == 'Asset')\
            .order_by(Type.name.asc())\
            .all()
        self.asset_type_combo_box.clear()
        self.asset_type_combo_box.addItems(
            [''] + map(lambda x: x[0], all_asset_type_names)
        )

        # sequences
        from stalker import Sequence
        all_sequence_names = DBSession\
            .query(Sequence.name)\
            .filter(Sequence.project == project)\
            .all()
        self.sequence_combo_box.clear()
        self.sequence_combo_box.addItems(
            [''] + map(lambda x: x[0], all_sequence_names)
        )

        self.cut_in_spin_box.setValue(1001)
        self.cut_out_spin_box.setValue(1100)

        # schedule info defaults
        # schedule timing
        from anima import defaults
        self.schedule_timing_spin_box.setValue(10)

        # schedule unit
        self.schedule_unit_combo_box.addItems(defaults.datetime_units)
        self.schedule_unit_combo_box.setCurrentIndex(0)

        # schedule model
        self.schedule_model_combo_box.addItems(defaults.task_schedule_models)

    def fill_ui_with_task(self, task):
        """Fills the ui with the given task info

        :param task: A Stalker Task instance
        :return:
        """
        self.task = task
        if not self.task:
            return

        # Updating a task
        # so disable the entity_type and project fields
        self.entity_type_combo_box.setEnabled(False)
        self.projects_combo_box.setEnabled(False)

        from stalker import Asset, Shot, Sequence

        self.set_project(task.project)
        self.set_parent_task(task.parent)

        # entity_type
        index = self.entity_type_combo_box.findText(self.task.entity_type)
        if index and index != self.entity_type_combo_box.currentIndex():
            self.entity_type_combo_box.setCurrentIndex(index)
        else:
            # because the comboBox will not trigger it automatically do it
            # manually and just allow it to hide or show fields
            self.entity_type_combo_box_changed(self.task.entity_type)

        match_exactly = QtCore.Qt.MatchExactly
        # task or asset type
        if self.task.type:
            combo_box = None
            if self.task.entity_type == 'Task':
                combo_box = self.task_type_combo_box
            elif self.task.entity_type == 'Asset':
                combo_box = self.asset_type_combo_box

            if combo_box:
                index = combo_box.findText(self.task.type.name, match_exactly)
                if index:
                    combo_box.setCurrentIndex(index)

        self.name_line_edit.setText(self.task.name)

        if isinstance(self.task, (Asset, Shot, Sequence)):
            # set the code
            self.code_line_edit.setText(self.task.code)

        # shot info
        # set the fps to project by default, later update it to the shot.fps
        self.fps_spin_box.setValue(self.task.project.fps)

        # sequences
        from stalker import Sequence
        from stalker.db.session import DBSession
        all_sequence_names = DBSession \
            .query(Sequence.name) \
            .filter(Sequence.project == task.project) \
            .order_by(Sequence.name.asc()) \
            .all()
        self.sequence_combo_box.clear()
        self.sequence_combo_box.addItems(
            [''] + map(lambda x: x[0], all_sequence_names)
        )

        if isinstance(self.task, Shot):
            # select the correct sequence
            if self.task.sequences:
                seq = self.task.sequences[0]
                index = self.sequence_combo_box.findText(
                    seq.name,
                    match_exactly
                )
                if index:
                    self.sequence_combo_box.setCurrentIndex(index)

            self.fps_spin_box.setValue(self.task.fps)
            self.cut_in_spin_box.setValue(self.task.cut_in)
            self.cut_out_spin_box.setValue(self.task.cut_out)

            # select correct image format
            self.image_format.set_current_image_format(
                self.task.image_format.id
            )

        for dep_task in self.task.depends:
            self.add_dependent_task(dep_task)

        # add resources
        for user in self.task.resources:
            self.resources_combo_box_changed(user.name)

        # responsible
        for user in self.task.responsible:
            self.responsible_combo_box_changed(user.name)

        # schedule info
        self.schedule_timing_spin_box.setValue(self.task.schedule_timing)

        index = self.schedule_unit_combo_box.findText(
            self.task.schedule_unit, QtCore.Qt.MatchExactly
        )
        if index:
            self.schedule_unit_combo_box.setCurrentIndex(index)

        index = self.schedule_model_combo_box.findText(
            self.task.schedule_model, QtCore.Qt.MatchExactly
        )
        if index:
            self.schedule_model_combo_box.setCurrentIndex(index)

    def entity_type_combo_box_changed(self, entity_type):
        """runs when the entity_type_combo_box has changed

        :param str entity_type:
        :return:
        """
        if entity_type == 'Task':
            # code fields
            self.code_label.setVisible(False)
            self.code_line_edit.setVisible(False)

            # task type fields
            self.task_type_label.setVisible(True)
            self.task_type_combo_box.setVisible(True)

            # asset type fields
            self.asset_type_label.setVisible(False)
            self.asset_type_combo_box.setVisible(False)

            # shot fields
            self.sequence_label.setVisible(False)
            self.sequence_combo_box.setVisible(False)
            self.fps_label.setVisible(False)
            self.fps_spin_box.setVisible(False)
            self.cut_in_cut_out_label.setVisible(False)
            self.cut_in_spin_box.setVisible(False)
            self.cut_out_spin_box.setVisible(False)
            self.image_format.set_visible(False)

            # resources field
            self.resources_label.setVisible(True)
            self.resources_combo_box.setVisible(True)
            self.resources_listWidget.setVisible(True)

            # depends to fields
            self.depends_to_label.setVisible(True)
            self.depends_to_listWidget.setVisible(True)
            self.add_depending_task_pushButton.setVisible(True)
            self.remove_depending_task_pushButton.setVisible(True)

            # schedule fields
            self.schedule_timing_label.setVisible(True)
            self.schedule_timing_spin_box.setVisible(True)
            self.schedule_unit_combo_box.setVisible(True)
            self.schedule_model_combo_box.setVisible(True)
            if self.mode == self.UPDATE_MODE:
                # if this is a parent task
                # do not show resource and timing related fields
                from stalker import Task
                assert isinstance(self.task, Task)

                if self.task.is_container:
                    self.resources_label.setVisible(False)
                    self.resources_combo_box.setVisible(False)
                    self.resources_listWidget.setVisible(False)
                    self.schedule_timing_label.setVisible(False)
                    self.schedule_timing_spin_box.setVisible(False)
                    self.schedule_unit_combo_box.setVisible(False)
                    self.schedule_model_combo_box.setVisible(False)

                    self.update_bid_label.setVisible(False)
                    self.update_bid_check_box.setVisible(False)
                else:
                    self.update_bid_label.setVisible(True)
                    self.update_bid_check_box.setVisible(True)

            else:
                self.update_bid_label.setVisible(False)
                self.update_bid_check_box.setVisible(False)

        elif entity_type == 'Asset':
            # code fields
            self.code_label.setVisible(True)
            self.code_line_edit.setVisible(True)

            # task type fields
            self.task_type_label.setVisible(False)
            self.task_type_combo_box.setVisible(False)

            # asset type fields
            self.asset_type_label.setVisible(True)
            self.asset_type_combo_box.setVisible(True)

            # shot fields
            self.sequence_label.setVisible(False)
            self.sequence_combo_box.setVisible(False)
            self.fps_label.setVisible(False)
            self.fps_spin_box.setVisible(False)
            self.cut_in_cut_out_label.setVisible(False)
            self.cut_in_spin_box.setVisible(False)
            self.cut_out_spin_box.setVisible(False)
            self.image_format.set_visible(False)

            # resources field
            self.resources_label.setVisible(False)
            self.resources_combo_box.setVisible(False)
            self.resources_listWidget.setVisible(False)

            # depends to fields
            self.depends_to_label.setVisible(False)
            self.depends_to_listWidget.setVisible(False)
            self.add_depending_task_pushButton.setVisible(False)
            self.remove_depending_task_pushButton.setVisible(False)

            # schedule fields
            self.schedule_timing_label.setVisible(False)
            self.schedule_timing_spin_box.setVisible(False)
            self.schedule_unit_combo_box.setVisible(False)
            self.schedule_model_combo_box.setVisible(False)
            self.update_bid_label.setVisible(False)
            self.update_bid_check_box.setVisible(False)

        elif entity_type == 'Shot':
            # code fields
            self.code_label.setVisible(True)
            self.code_line_edit.setVisible(True)

            # task type fields
            self.task_type_label.setVisible(False)
            self.task_type_combo_box.setVisible(False)

            # asset type fields
            self.asset_type_label.setVisible(False)
            self.asset_type_combo_box.setVisible(False)

            # shot fields
            self.sequence_label.setVisible(True)
            self.sequence_combo_box.setVisible(True)
            self.fps_label.setVisible(True)
            self.fps_spin_box.setVisible(True)
            self.cut_in_cut_out_label.setVisible(True)
            self.cut_in_spin_box.setVisible(True)
            self.cut_out_spin_box.setVisible(True)
            self.image_format.set_visible(True)

            # resources field
            self.resources_label.setVisible(False)
            self.resources_combo_box.setVisible(False)
            self.resources_listWidget.setVisible(False)

            # depends to fields
            self.depends_to_label.setVisible(False)
            self.depends_to_listWidget.setVisible(False)
            self.add_depending_task_pushButton.setVisible(False)
            self.remove_depending_task_pushButton.setVisible(False)

            # schedule fields
            self.schedule_timing_label.setVisible(False)
            self.schedule_timing_spin_box.setVisible(False)
            self.schedule_unit_combo_box.setVisible(False)
            self.schedule_model_combo_box.setVisible(False)
            self.update_bid_label.setVisible(False)
            self.update_bid_check_box.setVisible(False)

        elif entity_type == 'Sequence':
            # code fields
            self.code_label.setVisible(True)
            self.code_line_edit.setVisible(True)

            # task type fields
            self.task_type_label.setVisible(False)
            self.task_type_combo_box.setVisible(False)

            # asset type fields
            self.asset_type_label.setVisible(False)
            self.asset_type_combo_box.setVisible(False)

            # shot fields
            self.sequence_label.setVisible(False)
            self.sequence_combo_box.setVisible(False)
            self.fps_label.setVisible(False)
            self.fps_spin_box.setVisible(False)
            self.cut_in_cut_out_label.setVisible(False)
            self.cut_in_spin_box.setVisible(False)
            self.cut_out_spin_box.setVisible(False)
            self.image_format.set_visible(False)

            # resources field
            self.resources_label.setVisible(False)
            self.resources_combo_box.setVisible(False)
            self.resources_listWidget.setVisible(False)

            # depends to fields
            self.depends_to_label.setVisible(False)
            self.depends_to_listWidget.setVisible(False)
            self.add_depending_task_pushButton.setVisible(False)
            self.remove_depending_task_pushButton.setVisible(False)

            # schedule fields
            self.schedule_timing_label.setVisible(False)
            self.schedule_timing_spin_box.setVisible(False)
            self.schedule_unit_combo_box.setVisible(False)
            self.schedule_model_combo_box.setVisible(False)
            self.update_bid_label.setVisible(False)
            self.update_bid_check_box.setVisible(False)

    def get_project(self):
        """returns the current selected project

        :return:
        """
        project_name = self.projects_combo_box.currentText()
        from stalker import Project
        return Project.query.filter(Project.name == project_name).first()

    def set_project(self, project):
        """sets the project

        :param project: A Stalker Project
        :return:
        """
        if project and project != self.get_project():
            index = self.projects_combo_box.findText(
                project.name,
                QtCore.Qt.MatchExactly
            )
            if index:
                self.projects_combo_box.setCurrentIndex(index)

            if self.mode == self.CREATE_MODE:
                # also update the image format field
                self.image_format.set_current_image_format(
                    project.image_format
                )

    def get_parent_task(self):
        """returns the currently selected parent task

        :return:
        """
        parent_task_text = self.parent_task_line_edit.text()
        if parent_task_text != '':
            return self.get_task_from_ui_text(parent_task_text)
        else:
            return

    def get_task_hierarchy_name(self, task):
        """returns the task hierarchy name which includes the path

        :return str: Task hierarchy name
        """
        if task.parents:
            path = '%s | %s' % (
                task.project.code,
                ' | '.join(map(lambda x: x.name, task.parents))
            )
        else:
            path = task.project.code

        return '%s (%s) (%s)' % (task.name, path, task.id)

    def set_parent_task(self, task):
        """sets the parent_task_line_edit

        :param task: A Stalker task
        :return:
        """
        if task:
            self.set_project(task.project)
            self.parent_task = task
            self.parent_task_line_edit.setText(
                self.get_task_hierarchy_name(task)
            )

    def pick_parent_task_push_button_clicked(self):
        """runs when pick_parent_task_push_button is clicked
        """
        from anima.ui import task_picker_dialog

        task_picker_main_dialog = task_picker_dialog.MainDialog(
            parent=self,
            project=self.get_project()
        )
        # scroll to the current task
        parent_task = self.get_parent_task()
        task_picker_main_dialog.tasks_treeView\
            .find_and_select_entity_item(parent_task)
        task_picker_main_dialog.exec_()

        try:
            # PySide and PySide2
            accepted = QtWidgets.QDialog.DialogCode.Accepted
        except AttributeError:
            # PyQt4
            accepted = QtWidgets.QDialog.Accepted

        if task_picker_main_dialog.result() == accepted:
            parent_task_id = \
                task_picker_main_dialog.tasks_treeView.get_task_id()

            if parent_task_id is None:
                return

            from stalker import Task
            parent_task = Task.query.get(parent_task_id)

            if parent_task is None:
                return

            self.set_parent_task(parent_task)

            # also validate if this parent task is ok
            if self.task and self.mode == self.UPDATE_MODE:
                # check if the picked parent task is suitable for the updated
                # task
                if self.task in parent_task.parents \
                   or self.task == parent_task:
                    # warn the user by invalidating the field
                    self.parent_task_line_edit.set_invalid(
                        'New parent is not valid!'
                    )
                else:
                    self.parent_task_line_edit.set_valid()

        # delete the dialog
        task_picker_main_dialog.deleteLater()

    def projects_combo_box_changed(self, project_name):
        """runs when the project_comboBox is changed
        """
        # reset the parent task
        self.parent_task_line_edit.setText('')

        # reset resources
        # add resources
        from anima import defaults
        from stalker import Project, User, ProjectUser
        from stalker.db.session import DBSession
        all_project_user_ids = DBSession.query(User.id)\
            .join(ProjectUser)\
            .join(Project)\
            .filter(Project.name == project_name)\
            .all()

        all_user_names = \
            sorted(
                map(
                    lambda x: defaults.user_names_lut[x[0]],
                    all_project_user_ids
                )
            )

        # clear depends_to_listWidget
        self.depends_to_listWidget.clear()

        # clear resources_listWidget
        self.resources_listWidget.clear()

        # get resources from the project
        self.updating_resources_combo_box = True
        self.resources_combo_box.clear()
        self.resources_combo_box.addItems([''] + all_user_names)
        self.updating_resources_combo_box = False

        # get resources from the project
        self.updating_responsible_combo_box = True
        self.responsible_comboBox.clear()
        self.responsible_comboBox.addItems([''] + all_user_names)
        self.updating_responsible_combo_box = False

    def name_line_edit_changed(self, text):
        """runs when the name_line_edit text has changed
        """
        # if any([True for c in text if ord(c) >= 128]):
        #     self.name_line_edit.set_invalid('Turkce karakter kullanma!!!!')
        # else:
        #     self.name_line_edit.set_valid()

        if re.findall(r'[^a-zA-Z0-9_ ]+', text):
            self.name_line_edit.set_invalid('Invalid character')
        else:
            self.name_line_edit.set_valid()

        if text == '':
            self.name_line_edit.set_invalid('Please enter a name!')

        # just update the code field
        formatted_text = text.strip().replace(' ', '_').replace('-', '_')

        # remove multiple under scores
        formatted_text = re.sub('[_]+', '_', formatted_text)

        self.code_line_edit.setText(formatted_text)

    def code_line_edit_changed(self, text):
        """runs when the code_line_edit text has changed
        """
        if self.updating_code_lineEdit:
            return

        self.updating_code_lineEdit = True

        if re.findall(r'[^a-zA-Z0-9_ ]+', text):
            self.code_line_edit.set_invalid('Invalid character')
        else:
            if text == '':
                self.code_line_edit.set_invalid('Please enter a code!')
            else:
                if len(text) > 24:
                    self.code_line_edit.set_invalid('Code is too long (>24)')
                else:
                    self.code_line_edit.set_valid()

        # just update the code field
        formatted_text = text.strip().replace(' ', '_').replace('-', '_')

        # remove multiple under scores
        formatted_text = re.sub('[_]+', '_', formatted_text)

        self.code_line_edit.setText(formatted_text)
        self.updating_code_lineEdit = False

    def add_depending_task_push_button_clicked(self):
        """runs when add depending task push button clicked
        """
        try:
            # PySide and PySide2
            accepted = QtWidgets.QDialog.DialogCode.Accepted
        except AttributeError:
            # PyQt4
            accepted = QtWidgets.QDialog.Accepted

        from anima.ui import task_picker_dialog
        task_picker_main_dialog = task_picker_dialog.MainDialog(
            parent=self,
            project=self.get_project()
        )

        if self.last_selected_dependent_task:
            task_picker_main_dialog.tasks_treeView.find_and_select_entity_item(
                self.last_selected_dependent_task
            )
        else:
            # then select the parent at least
            task_picker_main_dialog.tasks_treeView.find_and_select_entity_item(
                self.get_parent_task()
            )

        task_picker_main_dialog.exec_()

        if task_picker_main_dialog.result() == accepted:
            task_id = task_picker_main_dialog.tasks_treeView.get_task_id()
            from stalker import Task
            task = Task.query.get(task_id)

            if task is not None:
                if task.project != self.get_project():
                    QtWidgets.QMessageBox.critical(
                        self,
                        'Error',
                        'Please select a task from the same project!'
                    )
                else:
                    self.add_dependent_task(task)

        # Delete the dialog
        # TODO: Try to immediately delete the dialog don't wait until here
        task_picker_main_dialog.deleteLater()

    def add_dependent_task(self, task):
        """Adds a task to the dependent task listWidget

        :param task:
        :return:
        """
        task_path = self.get_task_hierarchy_name(task)
        # don't add if the task already exists
        tasks_exists = self.depends_to_listWidget.findItems(
            task_path,
            QtCore.Qt.MatchExactly
        )
        if not tasks_exists:
            # add the item to the depends to task list
            item = QtWidgets.QListWidgetItem(task_path)
            self.depends_to_listWidget.insertItem(0, item)
            self.depends_to_listWidget.sortItems()
        
            self.last_selected_dependent_task = task

    def remove_depending_task_push_button_clicked(self):
        """runs whn remove_depending_task_pushButton is clicked
        """
        # just remove the current selected item
        for item in self.depends_to_listWidget.selectedItems():
            self.depends_to_listWidget.takeItem(
                self.depends_to_listWidget.row(
                    item
                )
            )

    def resources_combo_box_changed(self, item_text):
        """runs when resources_combo_box item changed

        :param str item_text: Currently selected item text
        :return:
        """
        if item_text == '':
            return

        if self.updating_resources_combo_box:
            return

        self.updating_resources_combo_box = True

        index = \
            self.resources_combo_box.findText(item_text, QtCore.Qt.MatchExactly)
        if index:
            # remove the item from the comboBox
            self.resources_combo_box.removeItem(index)
            # select the first index which is ''
            self.resources_combo_box.setCurrentIndex(0)

            # add the item to the resources list
            item = QtWidgets.QListWidgetItem(item_text)
            self.resources_listWidget.insertItem(0, item)
            self.resources_listWidget.sortItems()

        self.updating_resources_combo_box = False

    def responsible_combo_box_changed(self, item_text):
        """runs when responsible_comboBox item changed

        :param str item_text: Currently selected item text
        :return:
        """
        if item_text == '':
            return

        if self.updating_responsible_combo_box:
            return

        self.updating_responsible_combo_box = True

        index = self.responsible_comboBox.findText(
            item_text, QtCore.Qt.MatchExactly
        )
        if index:
            # remove the item from the comboBox
            self.responsible_comboBox.removeItem(index)
            # select the first index which is ''
            self.responsible_comboBox.setCurrentIndex(0)

            # add the item to the resources list
            item = QtWidgets.QListWidgetItem(item_text)
            self.responsible_listWidget.insertItem(0, item)
            self.responsible_listWidget.sortItems()

        self.updating_responsible_combo_box = False

    def resources_list_widget_item_double_clicked(self, item):
        """runs when an item is double clicked in resources_listWidget

        :param item: A Qt.QListWidgetItem
        :return:
        """
        item_text = item.text()
        # remove the item and add it to the resources_combo_box
        self.updating_resources_combo_box = True
        self.resources_listWidget.takeItem(
            self.resources_listWidget.row(item)
        )

        # return it to the resources_combo_box
        self.resources_combo_box.addItem(item_text)
        self.updating_resources_combo_box = False

    def depends_to_list_widget_item_double_clicked(self, item):
        """runs when an item is double clicked in depends_to_listWidget

        :param item: A Qt.QListWidgetItem
        :return:
        """
        # remove the item and add it to the resources_combo_box
        self.depends_to_listWidget.takeItem(
            self.depends_to_listWidget.row(item)
        )

    def responsible_list_widget_item_double_clicked(self, item):
        """runs when an item is double clicked in responsible_listWidget

        :param item: A Qt.QListWidgetItem
        :return:
        """
        item_text = item.text()
        # remove the item and add it to the responsible_comboBox
        self.updating_responsible_combo_box = True
        self.responsible_listWidget.takeItem(
            self.responsible_listWidget.row(item)
        )

        # return it to the responsible_comboBox
        self.responsible_comboBox.addItem(item_text)
        self.updating_responsible_combo_box = False

    @classmethod
    def get_tasks_from_list_widget(cls, list_widget):
        """returns the tasks from a listWidget

        :param list_widget: QListWidget
        :return:
        """
        tasks = []
        for i in range(list_widget.count()):
            task_item = list_widget.item(i)
            task = cls.get_task_from_ui_text(task_item.text())
            if task:
                tasks.append(task)
        return tasks

    @classmethod
    def get_task_from_ui_text(cls, text):
        """returns a Task instance from the given UI text
        """
        from stalker import Task
        task_id = int(text.split('(')[-1].replace(')', ''))
        return Task.query.get(task_id)

    @classmethod
    def get_users_from_list_widget(cls, list_widget):
        """returns users from the given list_widget

        :param list_widget:
        :return:
        """
        from stalker import User
        users = []
        for i in range(list_widget.count()):
            user_item = list_widget.item(i)
            user = User.query.filter(User.name == user_item.text()).first()
            if user:
                users.append(user)
        return users

    def accept(self):
        """create/update the task
        """
        # start with creating the task
        entity_type = self.entity_type_combo_box.currentText()
        project = self.get_project()

        if not self.parent_task_line_edit.is_valid:
            QtWidgets.QMessageBox.critical(
                self,
                'Error',
                'Some fields are not valid!'
            )
            return
        parent_task = self.get_parent_task()

        if not self.name_line_edit.is_valid:
            QtWidgets.QMessageBox.critical(
                self,
                'Error',
                'Some fields are not valid!'
            )
            return
        name = self.name_line_edit.text()

        if not self.code_line_edit.is_valid:
            QtWidgets.QMessageBox.critical(
                self,
                'Error',
                'Some fields are not valid!'
            )
            return
        code = self.code_line_edit.text()

        # Task Type
        from stalker import Type
        from stalker.db.session import DBSession
        task_type_name = self.task_type_combo_box.currentText()
        task_type = None
        if task_type_name:
            task_type = Type.query\
                .filter(Type.target_entity_type == 'Task')\
                .filter(Type.name == task_type_name)\
                .first()
            if not task_type:
                # create a new Task Type
                task_type = Type(
                    name=task_type_name,
                    code=task_type_name,
                    target_entity_type='Task'
                )
                DBSession.add(task_type)

        # Asset Type
        asset_type_name = self.asset_type_combo_box.currentText()
        asset_type = None
        if asset_type_name:
            asset_type = Type.query\
                .filter(Type.target_entity_type == 'Asset')\
                .filter(Type.name == asset_type_name)\
                .first()
            if not asset_type:
                # create a new Asset Type
                asset_type = Type(
                    name=asset_type_name,
                    code=asset_type_name,
                    target_entity_type='Asset'
                )
                DBSession.add(asset_type)

        # Sequence
        from stalker import Sequence
        sequence_name = self.sequence_combo_box.currentText()
        sequence = Sequence.query\
            .filter(Sequence.project == project)\
            .filter(Sequence.name == sequence_name)\
            .first()

        fps = self.fps_spin_box.value()
        cut_in = self.cut_in_spin_box.value()
        cut_out = self.cut_out_spin_box.value()
        image_format = self.image_format.get_current_image_format()

        depends = self.get_tasks_from_list_widget(self.depends_to_listWidget)
        resources = self.get_users_from_list_widget(self.resources_listWidget)
        responsible = \
            self.get_users_from_list_widget(self.responsible_listWidget)

        schedule_timing = self.schedule_timing_spin_box.value()
        schedule_unit = self.schedule_unit_combo_box.currentText()
        schedule_model = self.schedule_model_combo_box.currentText()

        priority = self.priority_spin_box.value()

        created_by = self.get_logged_in_user()

        import datetime
        from anima.utils import local_to_utc
        utc_now = local_to_utc(datetime.datetime.now())
        import stalker
        from distutils.version import LooseVersion
        if LooseVersion(stalker.__version__) >= LooseVersion('0.2.18'):
            # inject timezone info
            import pytz
            utc_now = utc_now.replace(tzinfo=pytz.utc)

        kwargs = {
            'name': name,
            'code': code,
            'project': project,
            'parent': parent_task,
            'depends': depends,
            'resources': resources,
            'responsible': responsible,
            'schedule_timing': schedule_timing,
            'schedule_unit': schedule_unit,
            'schedule_model': schedule_model,
            'priority': priority,
            'created_by': created_by,
            'date_created': utc_now
        }
        from stalker import Task, Asset, Shot, Sequence
        if entity_type == 'Asset':
            entity_class = Asset
            kwargs['type'] = asset_type
        elif entity_type == 'Shot':
            entity_class = Shot
            kwargs['sequences'] = [sequence]
            kwargs['fps'] = fps
            kwargs['cut_in'] = cut_in
            kwargs['cut_out'] = cut_out

            # only set the image format if it is different than the one used
            # for the Project
            if project.image_format != image_format:
                kwargs['image_format'] = image_format

        elif entity_type == 'Sequence':
            entity_class = Sequence
        else:
            entity_class = Task
            kwargs['type'] = task_type

        if self.mode == self.CREATE_MODE:
            # Create
            try:
                task = entity_class(**kwargs)
                DBSession.add(task)
                DBSession.commit()
            except Exception as e:
                DBSession.rollback()
                QtWidgets.QMessageBox.critical(
                    self,
                    'Error',
                    str(e)
                )
            else:
                self.task = task
        else:
            # Update
            self.task.name = name
            if isinstance(self.task, (Asset, Shot, Sequence)):
                self.task.code = code
                if isinstance(self.task, Asset):
                    self.task.type = asset_type

            if isinstance(self.task, Shot):
                self.task.fps = fps
                self.task.sequences = [sequence]
                self.task.cut_in = cut_in
                self.task.cut_out = cut_out

                # only set the image format if it is different than the one
                # used for the Project
                if self.task.project.image_format != image_format:
                    self.task.image_format = image_format
                else:
                    # or check if the shot is updated to use the Project image
                    # format so set the shot.image_format to None
                    self.task.image_format = None

            from stalker.exceptions import CircularDependencyError
            try:
                self.task.parent = parent_task
            except CircularDependencyError as e:
                DBSession.rollback()
                QtWidgets.QMessageBox.critical(
                    self,
                    'Error',
                    str(e)
                )
                # revert the parent field
                if self.task.parent:
                    self.parent_task_line_edit.setText(
                        self.get_task_hierarchy_name(self.task.parent)
                    )
                else:
                    self.parent_task_line_edit.setText('')
                self.parent_task_line_edit.set_valid()
                return

            try:
                from stalker.exceptions import StatusError
                try:
                    if self.task.depends != depends:
                        self.task.depends = depends
                except StatusError as e:
                    DBSession.rollback()
                    QtWidgets.QMessageBox.critical(
                        self,
                        'Error',
                        str(e)
                    )
                    return
            except CircularDependencyError as e:
                DBSession.rollback()
                QtWidgets.QMessageBox.critical(
                    self,
                    'Error',
                    str(e)
                )
                return

            self.task.resources = resources
            self.task.responsible = responsible
            self.task.schedule_timing = schedule_timing
            self.task.schedule_unit = schedule_unit
            self.task.schedule_model = schedule_model

            if self.update_bid_check_box.isChecked():
                self.task.bid_timing = schedule_timing
                self.task.bid_unit = schedule_unit

            self.task.priority = priority
            self.task.updated_by = self.get_logged_in_user()

            import datetime
            from anima.utils import local_to_utc
            utc_now = local_to_utc(datetime.datetime.now())
            import stalker
            from distutils.version import LooseVersion
            if LooseVersion(stalker.__version__) >= LooseVersion('0.2.18'):
                # inject timezone info
                import pytz
                utc_now = utc_now.replace(tzinfo=pytz.utc)

            self.task.date_updated = utc_now
            try:
                DBSession.add(self.task)
                DBSession.commit()
            except Exception as e:
                DBSession.rollback()
                QtWidgets.QMessageBox.critical(
                    self,
                    'Error',
                    str(e)
                )

        super(MainDialog, self).accept()
