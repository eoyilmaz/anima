# -*- coding: utf-8 -*-
# Copyright (c) 2012-2015, Anima Istanbul
#
# This module is part of anima-tools and is released under the BSD 2
# License: http://www.opensource.org/licenses/BSD-2-Clause
import re

from anima import logger
from anima.ui.base import AnimaDialogBase, ui_caller
from anima.ui import IS_PYSIDE, IS_PYSIDE2, IS_PYQT4
from anima.ui.lib import QtCore, QtWidgets, QtGui


if IS_PYSIDE():
    from anima.ui.ui_compiled import task_dialog_UI_pyside as task_dialog_UI
elif IS_PYSIDE2():
    from anima.ui.ui_compiled import task_dialog_UI_pyside2 as task_dialog_UI
elif IS_PYQT4():
    from anima.ui.ui_compiled import task_dialog_UI_pyqt4 as task_dialog_UI


def UI(app_in=None, executor=None, **kwargs):
    """
    :param app_in: A Qt Application instance, which you can pass to let the UI
      be attached to the given applications event process.

    :param executor: Instead of calling app.exec_ the UI will call this given
      function. It also passes the created app instance to this executor.

    """
    return ui_caller(app_in, executor, MainDialog, **kwargs)


class MainDialog(QtWidgets.QDialog, task_dialog_UI.Ui_Dialog, AnimaDialogBase):
    """The Task Dialog
    """

    def __init__(self, parent=None, parent_task=None, task=None):
        logger.debug("initializing the interface")
        super(MainDialog, self).__init__(parent)
        self.setupUi(self)

        # store the logged in user
        self.logged_in_user = None

        self.parent_task = parent_task
        self.task = task
        self.mode = 'Create'
        if self.task:
            self.mode = 'Update'

        self.dialog_label.setText('%s Task' % self.mode)

        self.task_created = None

        self.updating_resources_combo_box = False
        self.updating_responsible_combo_box = False
        self.updating_name_lineEdit = False
        self.updating_code_lineEdit = False

        self.last_selected_dependent_task = None

        # add self.parent_task_lineEdit
        from anima.ui.models import ValidatedLineEdit

        self.parent_task_lineEdit = ValidatedLineEdit(
            message_field=self.parent_task_validator_label
        )
        self.parent_task_lineEdit.setEnabled(False)
        self.parent_task_fields_horizontalLayout.insertWidget(
            0, self.parent_task_lineEdit
        )

        # add name_lineEdit
        self.name_lineEdit = ValidatedLineEdit(
            message_field=self.name_validator_label
        )
        self.name_field_verticalLayout.insertWidget(
            0, self.name_lineEdit
        )

        # add code_lineEdit
        self.code_lineEdit = ValidatedLineEdit(
            message_field=self.code_validator_label
        )
        self.code_field_verticalLayout.insertWidget(
            0, self.code_lineEdit
        )

        # update the tab order
        self.setTabOrder(self.entity_type_comboBox, self.projects_comboBox)
        self.setTabOrder(self.projects_comboBox, self.parent_task_lineEdit)
        self.setTabOrder(
            self.parent_task_lineEdit, self.pick_parent_task_pushButton
        )
        self.setTabOrder(self.pick_parent_task_pushButton, self.name_lineEdit)
        self.setTabOrder(self.name_lineEdit, self.code_lineEdit)
        self.setTabOrder(self.code_lineEdit, self.task_type_comboBox)
        self.setTabOrder(self.task_type_comboBox, self.asset_type_comboBox)
        self.setTabOrder(self.asset_type_comboBox, self.sequence_comboBox)
        self.setTabOrder(self.sequence_comboBox, self.fps_spinBox)
        self.setTabOrder(self.fps_spinBox, self.cutIn_spinBox)
        self.setTabOrder(self.cutIn_spinBox, self.cutOut_spinBox)
        self.setTabOrder(self.cutOut_spinBox, self.depends_to_listWidget)
        self.setTabOrder(
            self.depends_to_listWidget, self.add_depending_task_pushButton
        )
        self.setTabOrder(
            self.add_depending_task_pushButton,
            self.remove_depending_task_pushButton
        )
        self.setTabOrder(
            self.remove_depending_task_pushButton, self.resources_comboBox
        )
        self.setTabOrder(self.resources_comboBox, self.resources_listWidget)
        self.setTabOrder(self.resources_listWidget, self.responsible_comboBox)
        self.setTabOrder(
            self.responsible_comboBox, self.responsible_listWidget
        )
        self.setTabOrder(
            self.responsible_listWidget, self.schedule_timing_spinBox
        )
        self.setTabOrder(
            self.schedule_timing_spinBox, self.schedule_unit_comboBox
        )
        self.setTabOrder(
            self.schedule_unit_comboBox, self.schedule_model_comboBox
        )
        self.setTabOrder(
            self.schedule_model_comboBox, self.update_bid_checkBox
        )
        self.setTabOrder(self.update_bid_checkBox, self.priority_spinBox)

        self._setup_signals()

        self._set_defaults()

        if self.task:
            self.fill_ui_with_task(self.task)

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
            self.entity_type_comboBox,
            QtCore.SIGNAL('currentIndexChanged(QString)'),
            self.entity_type_combo_box_changed
        )

        # project_comboBox changed
        QtCore.QObject.connect(
            self.projects_comboBox,
            QtCore.SIGNAL('currentIndexChanged(QString)'),
            self.projects_combo_box_changed
        )

        # name_lineEdit is changed
        QtCore.QObject.connect(
            self.name_lineEdit,
            QtCore.SIGNAL('textChanged(QString)'),
            self.name_line_edit_changed
        )

        # code_lineEdit is changed
        QtCore.QObject.connect(
            self.code_lineEdit,
            QtCore.SIGNAL('textChanged(QString)'),
            self.code_line_edit_changed
        )

        # pick_task_pushButton
        QtCore.QObject.connect(
            self.pick_parent_task_pushButton,
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

        # resources_comboBox changed
        QtCore.QObject.connect(
            self.resources_comboBox,
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

    def _set_defaults(self):
        """sets the defaults fro the ui
        """
        # hide validators
        self.parent_task_validator_label.setVisible(False)

        # hide code area
        self.code_label.setVisible(False)
        self.code_lineEdit.setVisible(False)

        # hide asset type area
        self.asset_type_label.setVisible(False)
        self.asset_type_comboBox.setVisible(False)

        # hide shot fields
        self.sequence_label.setVisible(False)
        self.sequence_comboBox.setVisible(False)
        self.fps_label.setVisible(False)
        self.fps_spinBox.setVisible(False)
        self.cutIn_cutOut_label.setVisible(False)
        self.cutIn_spinBox.setVisible(False)
        self.cutOut_spinBox.setVisible(False)

        # hide update bid fields
        self.update_bid_label.setVisible(False)
        self.update_bid_checkBox.setVisible(False)

        # fill projects list
        self.projects_comboBox.clear()
        from stalker import Project, Task
        self.projects_comboBox.addItems(
            sorted([p.name for p in Project.query.all()])
        )

        # select the project if a parent_task or task given
        project = None
        if self.parent_task:
            if isinstance(self.parent_task, Task):
                project = self.parent_task.project
            elif isinstance(self.parent_task, Project):
                project = self.parent_task
                self.parent_task = None
        self.set_project(project)

        # if a parent is given set it to the parent_task_lineEdit
        self.set_parent_task(self.parent_task)

        # task types
        from stalker import db, Type
        all_task_type_names = db.DBSession.query(Type.name)\
            .filter(Type.target_entity_type == 'Task')\
            .order_by(Type.name.asc())\
            .all()
        self.task_type_comboBox.clear()
        self.task_type_comboBox.addItems(
            [''] + map(lambda x: x[0], all_task_type_names)
        )

        # asset types
        from stalker import Type
        all_asset_type_names = db.DBSession.query(Type.name)\
            .filter(Type.target_entity_type == 'Asset')\
            .order_by(Type.name.asc())\
            .all()
        self.asset_type_comboBox.clear()
        self.asset_type_comboBox.addItems(
            [''] + map(lambda x: x[0], all_asset_type_names)
        )

        # sequences
        from stalker import Sequence
        all_sequence_names = db.DBSession\
            .query(Sequence.name)\
            .filter(Sequence.project == project)\
            .all()
        self.sequence_comboBox.clear()
        self.sequence_comboBox.addItems(
            [''] + map(lambda x: x[0], all_sequence_names)
        )

        self.fps_spinBox.setValue(25)
        self.cutIn_spinBox.setValue(0)
        self.cutOut_spinBox.setValue(0)

        # schedule info defaults
        # schedule timing
        from stalker import defaults
        self.schedule_timing_spinBox.setValue(10)

        # schedule unit
        self.schedule_unit_comboBox.addItems(defaults.datetime_units)
        self.schedule_unit_comboBox.setCurrentIndex(0)

        # schedule model
        self.schedule_model_comboBox.addItems(defaults.task_schedule_models)

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
        self.entity_type_comboBox.setEnabled(False)
        self.projects_comboBox.setEnabled(False)

        from stalker import Asset, Shot, Sequence

        self.set_project(task.project)
        self.set_parent_task(task.parent)

        # entity_type
        index = self.entity_type_comboBox.findText(self.task.entity_type)
        if index and index != self.entity_type_comboBox.currentIndex():
            self.entity_type_comboBox.setCurrentIndex(index)
        else:
            # because the comboBox will not trigger it automatically do it
            # manually and just allow it to hide or show fields
            self.entity_type_combo_box_changed(self.task.entity_type)

        match_exactly = QtCore.Qt.MatchExactly
        # task or asset type
        if self.task.type:
            combo_box = None
            if self.task.entity_type == 'Task':
                combo_box = self.task_type_comboBox
            elif self.task.entity_type == 'Asset':
                combo_box = self.asset_type_comboBox

            if combo_box:
                index = combo_box.findText(self.task.type.name, match_exactly)
                if index:
                    combo_box.setCurrentIndex(index)

        self.name_lineEdit.setText(self.task.name)

        if isinstance(self.task, (Asset, Shot, Sequence)):
            # set the code
            self.code_lineEdit.setText(self.task.code)

        # shot info
        # set the fps to project by default, later update it to the shot.fps
        self.fps_spinBox.setValue(self.task.project.fps)

        # sequences
        from stalker import db, Sequence
        all_sequence_names = db.DBSession \
            .query(Sequence.name) \
            .filter(Sequence.project == task.project) \
            .order_by(Sequence.name.asc()) \
            .all()
        self.sequence_comboBox.clear()
        self.sequence_comboBox.addItems(
            [''] + map(lambda x: x[0], all_sequence_names)
        )

        if isinstance(self.task, Shot):
            # select the correct sequence
            if self.task.sequences:
                seq = self.task.sequences[0]
                index = self.sequence_comboBox.findText(
                    seq.name,
                    match_exactly
                )
                if index:
                    self.sequence_comboBox.setCurrentIndex(index)

            self.fps_spinBox.setValue(self.task.fps)
            self.cutIn_spinBox.setValue(self.task.cut_in)
            self.cutOut_spinBox.setValue(self.task.cut_out)

        for dep_task in self.task.depends:
            self.add_dependent_task(dep_task)

        # add resources
        for user in self.task.resources:
            self.resources_combo_box_changed(user.name)

        # responsible
        for user in self.task.responsible:
            self.responsible_combo_box_changed(user.name)

        # schedule info
        self.schedule_timing_spinBox.setValue(self.task.schedule_timing)

        index = self.schedule_unit_comboBox.findText(
            self.task.schedule_unit, QtCore.Qt.MatchExactly
        )
        if index:
            self.schedule_unit_comboBox.setCurrentIndex(index)

        index = self.schedule_model_comboBox.findText(
            self.task.schedule_model, QtCore.Qt.MatchExactly
        )
        if index:
            self.schedule_model_comboBox.setCurrentIndex(index)

    def entity_type_combo_box_changed(self, entity_type):
        """runs when the entity_type_comboBox has changed

        :param str entity_type:
        :return:
        """
        if entity_type == 'Task':
            # code fields
            self.code_label.setVisible(False)
            self.code_lineEdit.setVisible(False)

            # task type fields
            self.task_type_label.setVisible(True)
            self.task_type_comboBox.setVisible(True)

            # asset type fields
            self.asset_type_label.setVisible(False)
            self.asset_type_comboBox.setVisible(False)

            # shot fields
            self.sequence_label.setVisible(False)
            self.sequence_comboBox.setVisible(False)
            self.fps_label.setVisible(False)
            self.fps_spinBox.setVisible(False)
            self.cutIn_cutOut_label.setVisible(False)
            self.cutIn_spinBox.setVisible(False)
            self.cutOut_spinBox.setVisible(False)

            # resources field
            self.resources_label.setVisible(True)
            self.resources_comboBox.setVisible(True)
            self.resources_listWidget.setVisible(True)

            # depends to fields
            self.depends_to_label.setVisible(True)
            self.depends_to_listWidget.setVisible(True)
            self.add_depending_task_pushButton.setVisible(True)
            self.remove_depending_task_pushButton.setVisible(True)

            # schedule fields
            self.schedule_timing_label.setVisible(True)
            self.schedule_timing_spinBox.setVisible(True)
            self.schedule_unit_comboBox.setVisible(True)
            self.schedule_model_comboBox.setVisible(True)
            if self.mode == 'Update':
                self.update_bid_label.setVisible(True)
                self.update_bid_checkBox.setVisible(True)
            else:
                self.update_bid_label.setVisible(False)
                self.update_bid_checkBox.setVisible(False)

        elif entity_type == 'Asset':
            # code fields
            self.code_label.setVisible(True)
            self.code_lineEdit.setVisible(True)

            # task type fields
            self.task_type_label.setVisible(False)
            self.task_type_comboBox.setVisible(False)

            # asset type fields
            self.asset_type_label.setVisible(True)
            self.asset_type_comboBox.setVisible(True)

            # shot fields
            self.sequence_label.setVisible(False)
            self.sequence_comboBox.setVisible(False)
            self.fps_label.setVisible(False)
            self.fps_spinBox.setVisible(False)
            self.cutIn_cutOut_label.setVisible(False)
            self.cutIn_spinBox.setVisible(False)
            self.cutOut_spinBox.setVisible(False)

            # resources field
            self.resources_label.setVisible(False)
            self.resources_comboBox.setVisible(False)
            self.resources_listWidget.setVisible(False)

            # depends to fields
            self.depends_to_label.setVisible(False)
            self.depends_to_listWidget.setVisible(False)
            self.add_depending_task_pushButton.setVisible(False)
            self.remove_depending_task_pushButton.setVisible(False)

            # schedule fields
            self.schedule_timing_label.setVisible(False)
            self.schedule_timing_spinBox.setVisible(False)
            self.schedule_unit_comboBox.setVisible(False)
            self.schedule_model_comboBox.setVisible(False)
            self.update_bid_label.setVisible(False)
            self.update_bid_checkBox.setVisible(False)

        elif entity_type == 'Shot':
            # code fields
            self.code_label.setVisible(True)
            self.code_lineEdit.setVisible(True)

            # task type fields
            self.task_type_label.setVisible(False)
            self.task_type_comboBox.setVisible(False)

            # asset type fields
            self.asset_type_label.setVisible(False)
            self.asset_type_comboBox.setVisible(False)

            # shot fields
            self.sequence_label.setVisible(True)
            self.sequence_comboBox.setVisible(True)
            self.fps_label.setVisible(True)
            self.fps_spinBox.setVisible(True)
            self.cutIn_cutOut_label.setVisible(True)
            self.cutIn_spinBox.setVisible(True)
            self.cutOut_spinBox.setVisible(True)

            # resources field
            self.resources_label.setVisible(False)
            self.resources_comboBox.setVisible(False)
            self.resources_listWidget.setVisible(False)

            # depends to fields
            self.depends_to_label.setVisible(False)
            self.depends_to_listWidget.setVisible(False)
            self.add_depending_task_pushButton.setVisible(False)
            self.remove_depending_task_pushButton.setVisible(False)

            # schedule fields
            self.schedule_timing_label.setVisible(False)
            self.schedule_timing_spinBox.setVisible(False)
            self.schedule_unit_comboBox.setVisible(False)
            self.schedule_model_comboBox.setVisible(False)
            self.update_bid_label.setVisible(False)
            self.update_bid_checkBox.setVisible(False)

        elif entity_type == 'Sequence':
            # code fields
            self.code_label.setVisible(True)
            self.code_lineEdit.setVisible(True)

            # task type fields
            self.task_type_label.setVisible(False)
            self.task_type_comboBox.setVisible(False)

            # asset type fields
            self.asset_type_label.setVisible(False)
            self.asset_type_comboBox.setVisible(False)

            # shot fields
            self.sequence_label.setVisible(False)
            self.sequence_comboBox.setVisible(False)
            self.fps_label.setVisible(False)
            self.fps_spinBox.setVisible(False)
            self.cutIn_cutOut_label.setVisible(False)
            self.cutIn_spinBox.setVisible(False)
            self.cutOut_spinBox.setVisible(False)

            # resources field
            self.resources_label.setVisible(False)
            self.resources_comboBox.setVisible(False)
            self.resources_listWidget.setVisible(False)

            # depends to fields
            self.depends_to_label.setVisible(False)
            self.depends_to_listWidget.setVisible(False)
            self.add_depending_task_pushButton.setVisible(False)
            self.remove_depending_task_pushButton.setVisible(False)

            # schedule fields
            self.schedule_timing_label.setVisible(False)
            self.schedule_timing_spinBox.setVisible(False)
            self.schedule_unit_comboBox.setVisible(False)
            self.schedule_model_comboBox.setVisible(False)
            self.update_bid_label.setVisible(False)
            self.update_bid_checkBox.setVisible(False)

    def get_project(self):
        """returns the current selected project

        :return:
        """
        project_name = self.projects_comboBox.currentText()
        from stalker import Project
        return Project.query.filter(Project.name == project_name).first()

    def set_project(self, project):
        """sets the project

        :param project: A Stalker Project
        :return:
        """
        if project and project != self.get_project():
            index = self.projects_comboBox.findText(
                project.name,
                QtCore.Qt.MatchExactly
            )
            if index:
                self.projects_comboBox.setCurrentIndex(index)

    def get_parent_task(self):
        """returns the currently selected parent task

        :return:
        """
        parent_task_text = self.parent_task_lineEdit.text()
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
        """sets the parent_task_lineEdit

        :param task: A Stalker task
        :return:
        """
        if task:
            self.set_project(task.project)
            self.parent_task = task
            self.parent_task_lineEdit.setText(
                self.get_task_hierarchy_name(task)
            )

    def pick_parent_task_push_button_clicked(self):
        """runs when pick_parent_task_pushButton is clicked
        """
        from anima.ui import task_picker_dialog
        task_picker_main_dialog = task_picker_dialog.MainDialog(
            parent=self,
            project=self.get_project()
        )
        if self.mode == 'Update':
            # also inform the task_picker_dialog that we want to select for
            # parent

            task_picker_main_dialog.pick_task_for = self.task
            task_picker_main_dialog.pick_as_parent = True

            # scroll to the current task
            task_picker_main_dialog.tasks_treeView\
                .find_and_select_entity_item(self.task)

        task_picker_main_dialog.deleteLater()
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
            if self.task and self.mode == 'Update':
                # check if the picked parent task is suitable for the updated
                # task
                if self.task in parent_task.parents \
                   or self.task == parent_task:
                    # warn the user by invalidating the field
                    self.parent_task_lineEdit.set_invalid(
                        'New parent is not valid!'
                    )
                else:
                    self.parent_task_lineEdit.set_valid()

    def projects_combo_box_changed(self, project_name):
        """runs when the project_comboBox is changed
        """
        # reset the parent task
        self.parent_task_lineEdit.setText('')

        # reset resources
        # add resources
        from anima import user_names_lut
        from stalker import db, Project, User, ProjectUser
        all_project_user_ids = db.DBSession.query(User.id)\
            .join(ProjectUser)\
            .join(Project)\
            .filter(Project.name == project_name)\
            .all()

        all_user_names = \
            map(lambda x: user_names_lut[x[0]], all_project_user_ids)

        # clear depends_to_listWidget
        self.depends_to_listWidget.clear()

        # clear resources_listWidget
        self.resources_listWidget.clear()

        # get resources from the project
        self.updating_resources_combo_box = True
        self.resources_comboBox.clear()
        self.resources_comboBox.addItems([''] + all_user_names)
        self.updating_resources_combo_box = False

        # get resources from the project
        self.updating_responsible_combo_box = True
        self.responsible_comboBox.clear()
        self.responsible_comboBox.addItems([''] + all_user_names)
        self.updating_responsible_combo_box = False

    def name_line_edit_changed(self, text):
        """runs when the name_lineEdit text has changed
        """
        # if any([True for c in text if ord(c) >= 128]):
        #     self.name_lineEdit.set_invalid('Turkce karakter kullanma!!!!')
        # else:
        #     self.name_lineEdit.set_valid()

        if re.findall(r'[^a-zA-Z0-9_ ]+', text):
            self.name_lineEdit.set_invalid('Invalid character')
        else:
            self.name_lineEdit.set_valid()

        # just update the code field
        formatted_text = text.strip().replace(' ', '_').replace('-', '_')

        # remove multiple under scores
        formatted_text = re.sub('[_]+', '_', formatted_text)

        self.code_lineEdit.setText(formatted_text)

    def code_line_edit_changed(self, text):
        """runs when the code_lineEdit text has changed
        """
        if self.updating_code_lineEdit:
            return

        self.updating_code_lineEdit = True

        if re.findall(r'[^a-zA-Z0-9_ ]+', text):
            self.code_lineEdit.set_invalid('Invalid character')
        else:
            self.code_lineEdit.set_valid()

        # just update the code field
        formatted_text = text.strip().replace(' ', '_').replace('-', '_')

        # remove multiple under scores
        formatted_text = re.sub('[_]+', '_', formatted_text)

        self.code_lineEdit.setText(formatted_text)
        self.updating_code_lineEdit = False

    def add_depending_task_push_button_clicked(self):
        """runs when add depending task push button clicked
        """
        from anima.ui import task_picker_dialog
        task_picker_main_dialog = task_picker_dialog.MainDialog(
            parent=self,
            project=self.get_project()
        )
        if self.last_selected_dependent_task:
            task_picker_main_dialog.tasks_treeView.find_and_select_entity_item(
                self.last_selected_dependent_task
            )
        task_picker_main_dialog.exec_()

        task_id = task_picker_main_dialog.tasks_treeView.get_task_id()
        if task_id is None:
            return

        from stalker import Task
        task = Task.query.get(task_id)

        if task is None:
            return

        if task.project != self.get_project():
            QtWidgets.QMessageBox.critical(
                self,
                'Error',
                'Please select a task from the same project!'
            )
            return

        self.add_dependent_task(task)

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
        """runs when resources_comboBox item changed

        :param str item_text: Currently selected item text
        :return:
        """
        if item_text == '':
            return

        if self.updating_resources_combo_box:
            return

        self.updating_resources_combo_box = True

        index = \
            self.resources_comboBox.findText(item_text, QtCore.Qt.MatchExactly)
        if index:
            # remove the item from the comboBox
            self.resources_comboBox.removeItem(index)
            # select the first index which is ''
            self.resources_comboBox.setCurrentIndex(0)

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
        # remove the item and add it to the resources_comboBox
        self.updating_resources_combo_box = True
        self.resources_listWidget.takeItem(
            self.resources_listWidget.row(item)
        )

        # return it to the resources_comboBox
        self.resources_comboBox.addItem(item_text)
        self.updating_resources_combo_box = False

    def depends_to_list_widget_item_double_clicked(self, item):
        """runs when an item is double clicked in depends_to_listWidget

        :param item: A Qt.QListWidgetItem
        :return:
        """
        # remove the item and add it to the resources_comboBox
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
        entity_type = self.entity_type_comboBox.currentText()
        project = self.get_project()

        if not self.parent_task_lineEdit.is_valid:
            QtWidgets.QMessageBox.critical(
                self,
                'Error',
                'Some fields are not valid!'
            )
            return
        parent_task = self.get_parent_task()

        if not self.name_lineEdit.is_valid:
            QtWidgets.QMessageBox.critical(
                self,
                'Error',
                'Some fields are not valid!'
            )
            return
        name = self.name_lineEdit.text()

        if not self.code_lineEdit.is_valid:
            QtWidgets.QMessageBox.critical(
                self,
                'Error',
                'Some fields are not valid!'
            )
            return
        code = self.code_lineEdit.text()

        task_type_name = self.task_type_comboBox.currentText()

        from stalker import db, Type
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
                db.DBSession.add(task_type)

        asset_type_name = self.asset_type_comboBox.currentText()
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
                db.DBSession.add(asset_type)

        from stalker import Sequence
        sequence_name = self.sequence_comboBox.currentText()
        sequence = Sequence.query\
            .filter(Sequence.project == project)\
            .filter(Sequence.name == sequence_name)\
            .first()

        fps = self.fps_spinBox.value()
        cut_in = self.cutIn_spinBox.value()
        cut_out = self.cutOut_spinBox.value()

        depends = self.get_tasks_from_list_widget(self.depends_to_listWidget)
        resources = self.get_users_from_list_widget(self.resources_listWidget)
        responsible = \
            self.get_users_from_list_widget(self.responsible_listWidget)

        schedule_timing = self.schedule_timing_spinBox.value()
        schedule_unit = self.schedule_unit_comboBox.currentText()
        schedule_model = self.schedule_model_comboBox.currentText()

        priority = self.priority_spinBox.value()

        created_by = self.get_logged_in_user()

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
            'created_by': created_by
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
        elif entity_type == 'Sequence':
            entity_class = Sequence
        else:
            entity_class = Task
            kwargs['type'] = task_type

        if self.mode == 'Create':
            # Create
            try:
                task = entity_class(**kwargs)
                db.DBSession.add(task)
                db.DBSession.commit()
            except Exception as e:
                db.DBSession.rollback()
                QtWidgets.QMessageBox.critical(
                    self,
                    'Error',
                    str(e)
                )
            else:
                self.task_created = task
                self.reject()
        else:
            # Update
            self.task.name = name
            if isinstance(self.task, (Asset, Shot, Sequence)):
                self.task.code = code

            if isinstance(self.task, Shot):
                self.task.fps = fps
                self.task.sequences = [sequence]
                self.task.cut_in = cut_in
                self.task.cut_out = cut_out

            from stalker.exceptions import CircularDependencyError
            try:
                self.task.parent = parent_task
            except CircularDependencyError as e:
                db.DBSession.rollback()
                QtWidgets.QMessageBox.critical(
                    self,
                    'Error',
                    str(e)
                )
                # revert the parent field
                if self.task.parent:
                    self.parent_task_lineEdit.setText(
                        self.get_task_hierarchy_name(self.task.parent)
                    )
                else:
                    self.parent_task_lineEdit.setText('')
                self.parent_task_lineEdit.set_valid()
                return

            try:
                self.task.depends = depends
            except CircularDependencyError as e:
                db.DBSession.rollback()
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

            if self.update_bid_checkBox.isChecked():
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
                db.DBSession.add(self.task)
                db.DBSession.commit()
            except Exception as e:
                db.DBSession.rollback()
                QtWidgets.QMessageBox.critical(
                    self,
                    'Error',
                    str(e)
                )
            finally:
                super(MainDialog, self).accept()
