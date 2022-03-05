# -*- coding: utf-8 -*-

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
    """The Project Dialog"""

    max_project_name_length = 32

    def __init__(self, parent=None, project=None):
        logger.debug("initializing the interface")
        super(MainDialog, self).__init__(parent)

        # store the logged in user
        self.logged_in_user = None
        self.project = project
        self.mode = "Create"
        if self.project:
            self.mode = "Update"
        self.image_format = None

        self._setup_ui()
        self._setup_signals()
        self._set_defaults()

        if self.project:
            self.fill_ui_with_project(self.project)

    def _setup_ui(self):
        """create UI elements"""
        self.resize(517, 545)
        self.vertical_layout = QtWidgets.QVBoxLayout(self)

        self.setWindowTitle("Project Dialog")

        # ----------------------
        # Dialog Label
        self.dialog_label = QtWidgets.QLabel(self)
        self.dialog_label.setText("%s Project" % self.mode)
        self.dialog_label.setStyleSheet("color: rgb(71, 143, 202);\nfont: 18pt;")
        self.vertical_layout.addWidget(self.dialog_label)
        self.line = QtWidgets.QFrame(self)
        self.line.setFrameShape(QtWidgets.QFrame.HLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.vertical_layout.addWidget(self.line)

        self.project_info_form_layout = QtWidgets.QFormLayout()
        self.project_info_form_layout.setLabelAlignment(
            QtCore.Qt.AlignRight | QtCore.Qt.AlignTrailing | QtCore.Qt.AlignVCenter
        )

        # ----------------------
        # Name Fields
        self.name_label = QtWidgets.QLabel(self)
        self.name_label.setText("Name")
        self.project_info_form_layout.setWidget(
            0, QtWidgets.QFormLayout.LabelRole, self.name_label
        )

        self.name_fields_vertical_layout = QtWidgets.QVBoxLayout()
        self.name_validator_label = QtWidgets.QLabel(self)
        self.name_validator_label.setText("Validator Message")
        self.name_validator_label.setStyleSheet("color: rgb(255, 0, 0);")
        self.name_fields_vertical_layout.addWidget(self.name_validator_label)
        self.project_info_form_layout.setLayout(
            0, QtWidgets.QFormLayout.FieldRole, self.name_fields_vertical_layout
        )

        # add name_line_edit
        from anima.ui.widgets import ValidatedLineEdit

        self.name_line_edit = ValidatedLineEdit(message_field=self.name_validator_label)
        self.name_fields_vertical_layout.insertWidget(0, self.name_line_edit)

        # ----------------------
        # Code Fields
        self.code_label = QtWidgets.QLabel(self)
        self.code_label.setText("Code")
        self.project_info_form_layout.setWidget(
            1, QtWidgets.QFormLayout.LabelRole, self.code_label
        )
        self.code_fields_vertical_layout = QtWidgets.QVBoxLayout()
        self.code_validator_label = QtWidgets.QLabel(self)
        self.code_validator_label.setText("Validator Message")
        self.code_validator_label.setStyleSheet("color: rgb(255, 0, 0);")
        self.code_fields_vertical_layout.addWidget(self.code_validator_label)
        self.project_info_form_layout.setLayout(
            1, QtWidgets.QFormLayout.FieldRole, self.code_fields_vertical_layout
        )

        # add code_line_edit
        self.code_line_edit = ValidatedLineEdit(message_field=self.code_validator_label)
        self.code_fields_vertical_layout.insertWidget(0, self.code_line_edit)

        # ----------------------
        # Type Fields
        self.type_label = QtWidgets.QLabel(self)
        self.type_label.setText("Type")
        self.project_info_form_layout.setWidget(
            2, QtWidgets.QFormLayout.LabelRole, self.type_label
        )
        self.type_combo_box = QtWidgets.QComboBox(self)
        self.type_combo_box.setEditable(True)
        self.project_info_form_layout.setWidget(
            2, QtWidgets.QFormLayout.FieldRole, self.type_combo_box
        )

        # ----------------------
        # Date Fields
        self.date_label = QtWidgets.QLabel(self)
        self.date_label.setText("Date")
        self.project_info_form_layout.setWidget(
            3, QtWidgets.QFormLayout.LabelRole, self.date_label
        )
        self.date_date_edit = QtWidgets.QDateEdit(self)
        self.project_info_form_layout.setWidget(
            3, QtWidgets.QFormLayout.FieldRole, self.date_date_edit
        )

        # ----------------------
        # Image Format Fields
        from anima.ui.widgets.image_format import ImageFormatWidget

        self.image_format = ImageFormatWidget(
            parent=self,
            parent_form_layout=self.project_info_form_layout,
            parent_form_layout_index=4,
        )

        # ----------------------
        # FPS Fields
        self.fps_label = QtWidgets.QLabel(self)
        self.fps_label.setText("FPS")
        self.project_info_form_layout.setWidget(
            5, QtWidgets.QFormLayout.LabelRole, self.fps_label
        )
        self.fps_spin_box = QtWidgets.QSpinBox(self)
        self.fps_spin_box.setMinimum(1)
        self.fps_spin_box.setProperty("value", 25)
        self.project_info_form_layout.setWidget(
            5, QtWidgets.QFormLayout.FieldRole, self.fps_spin_box
        )

        # ----------------------
        # Repository Fields
        self.repository_label = QtWidgets.QLabel(self)
        self.repository_label.setText("Repository")
        self.project_info_form_layout.setWidget(
            6, QtWidgets.QFormLayout.LabelRole, self.repository_label
        )
        self.repository_horizontal_layout = QtWidgets.QHBoxLayout()
        self.repository_combo_box = QtWidgets.QComboBox(self)
        self.repository_horizontal_layout.addWidget(self.repository_combo_box)

        # Update Repository Push Button
        self.update_repository_push_button = QtWidgets.QPushButton(self)
        self.update_repository_push_button.setText("Update...")
        self.repository_horizontal_layout.addWidget(self.update_repository_push_button)

        # Create Repository Push Button
        self.create_repository_pushButton = QtWidgets.QPushButton(self)
        self.create_repository_pushButton.setText("New...")
        self.repository_horizontal_layout.addWidget(self.create_repository_pushButton)

        self.repository_horizontal_layout.setStretch(0, 1)
        self.project_info_form_layout.setLayout(
            6, QtWidgets.QFormLayout.FieldRole, self.repository_horizontal_layout
        )

        # ----------------------
        self.structure_label = QtWidgets.QLabel(self)
        self.structure_label.setText("Structure")

        self.project_info_form_layout.setWidget(
            7, QtWidgets.QFormLayout.LabelRole, self.structure_label
        )
        self.structure_horizontal_layout = QtWidgets.QHBoxLayout()
        self.structure_combo_box = QtWidgets.QComboBox(self)
        self.structure_horizontal_layout.addWidget(self.structure_combo_box)

        # Update Structure Push Button
        self.update_structure_push_button = QtWidgets.QPushButton(self)
        self.update_structure_push_button.setText("Update...")
        self.structure_horizontal_layout.addWidget(self.update_structure_push_button)

        # Create Structure Push Button
        self.create_structure_push_button = QtWidgets.QPushButton(self)
        self.create_structure_push_button.setText("New...")
        self.structure_horizontal_layout.addWidget(self.create_structure_push_button)

        self.structure_horizontal_layout.setStretch(0, 1)
        self.project_info_form_layout.setLayout(
            7, QtWidgets.QFormLayout.FieldRole, self.structure_horizontal_layout
        )

        # ----------------------
        # Status Fields
        self.status_label = QtWidgets.QLabel(self)
        self.status_label.setText("Status")
        self.project_info_form_layout.setWidget(
            8, QtWidgets.QFormLayout.LabelRole, self.status_label
        )
        self.status_combo_box = QtWidgets.QComboBox(self)
        self.project_info_form_layout.setWidget(
            8, QtWidgets.QFormLayout.FieldRole, self.status_combo_box
        )
        self.vertical_layout.addLayout(self.project_info_form_layout)

        # ----------------------
        # Client Fields
        self.client_info_label = QtWidgets.QLabel(self)
        self.client_info_label.setText("Client Info")
        self.client_info_label.setStyleSheet("color: rgb(71, 143, 202);\nfont: 18pt;")
        self.vertical_layout.addWidget(self.client_info_label)
        self.line_2 = QtWidgets.QFrame(self)
        self.line_2.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_2.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.vertical_layout.addWidget(self.line_2)
        self.client_info_formLayout = QtWidgets.QFormLayout()
        self.client_info_formLayout.setLabelAlignment(
            QtCore.Qt.AlignRight | QtCore.Qt.AlignTrailing | QtCore.Qt.AlignVCenter
        )

        # Client Fields
        self.client_label = QtWidgets.QLabel(self)
        self.client_label.setText("Client")
        self.client_info_formLayout.setWidget(
            0, QtWidgets.QFormLayout.LabelRole, self.client_label
        )
        self.client_combo_box = QtWidgets.QComboBox(self)
        self.client_combo_box.setEditable(True)
        self.client_info_formLayout.setWidget(
            0, QtWidgets.QFormLayout.FieldRole, self.client_combo_box
        )

        # Agency Fields
        self.agency_label = QtWidgets.QLabel(self)
        self.agency_label.setText("Agency")
        self.client_info_formLayout.setWidget(
            1, QtWidgets.QFormLayout.LabelRole, self.agency_label
        )
        self.agency_combo_box = QtWidgets.QComboBox(self)
        self.agency_combo_box.setEditable(True)
        self.client_info_formLayout.setWidget(
            1, QtWidgets.QFormLayout.FieldRole, self.agency_combo_box
        )

        # Production Company Fields
        self.production_company_label = QtWidgets.QLabel(self)
        self.production_company_label.setText(
            '<html><head/><body><p align="right">Production<br/>'
            "Company</p></body></html>"
        )

        self.client_info_formLayout.setWidget(
            2, QtWidgets.QFormLayout.LabelRole, self.production_company_label
        )
        self.production_company_combo_box = QtWidgets.QComboBox(self)
        self.production_company_combo_box.setEditable(True)
        self.client_info_formLayout.setWidget(
            2, QtWidgets.QFormLayout.FieldRole, self.production_company_combo_box
        )
        self.vertical_layout.addLayout(self.client_info_formLayout)
        self.button_box = QtWidgets.QDialogButtonBox(self)
        self.button_box.setOrientation(QtCore.Qt.Horizontal)
        self.button_box.setStandardButtons(
            QtWidgets.QDialogButtonBox.Cancel | QtWidgets.QDialogButtonBox.Ok
        )
        self.vertical_layout.addWidget(self.button_box)
        self.vertical_layout.setStretch(2, 2)
        self.vertical_layout.setStretch(5, 1)

    def _setup_signals(self):
        """creates the signals"""
        QtCore.QObject.connect(
            self.button_box, QtCore.SIGNAL("accepted()"), self.accept
        )
        QtCore.QObject.connect(
            self.button_box, QtCore.SIGNAL("rejected()"), self.reject
        )

        # name_line_edit is changed
        QtCore.QObject.connect(
            self.name_line_edit,
            QtCore.SIGNAL("textChanged(QString)"),
            self.name_line_edit_changed,
        )

        # code_line_edit is changed
        QtCore.QObject.connect(
            self.code_line_edit,
            QtCore.SIGNAL("textChanged(QString)"),
            self.code_line_edit_changed,
        )

        # create_repository_pushButton
        QtCore.QObject.connect(
            self.create_repository_pushButton,
            QtCore.SIGNAL("clicked()"),
            self.create_repository_push_button_clicked,
        )

        # update_repository_push_button
        QtCore.QObject.connect(
            self.update_repository_push_button,
            QtCore.SIGNAL("clicked()"),
            self.update_repository_push_button_clicked,
        )

        # create_structure_push_button
        QtCore.QObject.connect(
            self.create_structure_push_button,
            QtCore.SIGNAL("clicked()"),
            self.create_structure_push_button_clicked,
        )

        # update_structure_push_button
        QtCore.QObject.connect(
            self.update_structure_push_button,
            QtCore.SIGNAL("clicked()"),
            self.update_structure_push_button_clicked,
        )

    def _set_defaults(self):
        """setup the default values"""
        # set size policies
        # self.name_line_edit

        self.type_combo_box.setSizePolicy(
            QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed
        )

        self.status_combo_box.setSizePolicy(
            QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed
        )

        self.client_combo_box.setSizePolicy(
            QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed
        )

        self.agency_combo_box.setSizePolicy(
            QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed
        )

        self.production_company_combo_box.setSizePolicy(
            QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed
        )

        # invalidate the name and code fields by default
        self.name_line_edit.set_invalid("Enter a name")
        self.code_line_edit.set_invalid("Enter a code")

        # update type field
        from stalker import Type
        from stalker.db.session import DBSession

        project_types = (
            DBSession.query(Type.id, Type.name)
            .filter(Type.target_entity_type == "Project")
            .order_by(Type.name)
            .all()
        )

        self.type_combo_box.clear()
        self.type_combo_box.addItem("", -1)
        for type_id, type_name in project_types:
            self.type_combo_box.addItem(type_name, type_id)

        self.image_format.fill_combo_box()
        self.fill_repository_combo_box()
        self.fill_structure_combo_box()

        # fill status field
        sql = """select
        "SimpleEntities".id,
        "SimpleEntities".name
    from "Statuses"
    join "SimpleEntities" on "Statuses".id = "SimpleEntities".id
    join "StatusList_Statuses" on "Statuses".id = "StatusList_Statuses".status_id
    join "StatusLists" on "StatusLists".id = "StatusList_Statuses".status_list_id
    where "StatusLists".target_entity_type = 'Project'"""

        all_project_statuses = DBSession.connection().execute(sql).fetchall()

        for st_id, st_name in all_project_statuses:
            self.status_combo_box.addItem(st_name, st_id)

    def show(self):
        """overridden show method"""
        logger.debug("MainDialog.show is started")
        self.logged_in_user = self.get_logged_in_user()
        if not self.logged_in_user:
            self.reject()
            return_val = None
        else:
            return_val = super(MainDialog, self).show()

        logger.debug("MainDialog.show is finished")
        return return_val

    def fill_repository_combo_box(self):
        """fills the repository_combo_box with Repository instances"""
        # fill the repository field
        from stalker import Repository
        from stalker.db.session import DBSession

        all_repos = (
            DBSession.query(Repository.id, Repository.name)
            .order_by(Repository.name)
            .all()
        )
        self.repository_combo_box.clear()
        for repo_id, repo_name in all_repos:
            self.repository_combo_box.addItem(repo_name, repo_id)

    def fill_structure_combo_box(self):
        """fills the structure_combo_box with Structure instances"""
        # fill the structure field
        from stalker import Structure
        from stalker.db.session import DBSession

        all_structures = (
            DBSession.query(Structure.id, Structure.name).order_by(Structure.name).all()
        )
        self.structure_combo_box.clear()
        for st_id, st_name in all_structures:
            self.structure_combo_box.addItem(st_name, st_id)

    def name_line_edit_changed(self, text):
        """runs when the name_line_edit text has changed"""
        if re.findall(r"[^a-zA-Z0-9\-_ ]+", text):
            self.name_line_edit.set_invalid("Invalid character")
        else:
            if text == "":
                self.name_line_edit.set_invalid("Enter a name")
            else:
                self.name_line_edit.set_valid()

        # update code field also
        formatted_text = re.sub(r"[^A-Z0-9_]+", "", text)
        self.code_line_edit.setText(formatted_text)

    def code_line_edit_changed(self, text):
        """runs when the code_line_edit text has changed"""
        if re.findall(r"[^a-zA-Z0-9_]+", text):
            self.code_line_edit.set_invalid("Invalid character")
        else:
            if text == "":
                self.code_line_edit.set_invalid("Enter a code")
            else:
                if len(text) > self.max_project_name_length:
                    self.code_line_edit.set_invalid(
                        "Code is too long (>%s)" % self.max_project_name_length
                    )
                else:
                    self.code_line_edit.set_valid()

    def fill_ui_with_project(self, project):
        """fills the UI fields with the given project

        :param project: A Stalker Project instance
        :return:
        """
        if not project:
            return
        self.project = project

        self.name_line_edit.setText(project.name)
        self.name_line_edit.set_valid()
        self.code_line_edit.setText(project.code)
        self.code_line_edit.set_valid()

        if project.type:
            index = self.type_combo_box.findData(project.type.id)
            if index:
                self.type_combo_box.setCurrentIndex(index)

        if project.image_format:
            index = self.image_format.combo_box.findData(project.image_format.id)
            if index:
                self.image_format.combo_box.setCurrentIndex(index)

        self.fps_spin_box.setValue(project.fps)

        if project.repository:
            # TODO: allow multiple repositories
            index = self.repository_combo_box.findText(
                project.repository.name, QtCore.Qt.MatchExactly
            )
            if index:
                self.repository_combo_box.setCurrentIndex(index)

        if project.structure:
            index = self.structure_combo_box.findText(
                project.structure.name, QtCore.Qt.MatchExactly
            )
            if index:
                self.structure_combo_box.setCurrentIndex(index)

        if project.status:
            index = self.status_combo_box.findText(
                project.status.name, QtCore.Qt.MatchExactly
            )
            if index:
                self.status_combo_box.setCurrentIndex(index)

    def create_repository_push_button_clicked(self):
        """runs when create_repository_pushButton is clicked"""
        try:
            # PySide
            accepted = QtWidgets.QDialog.DialogCode.Accepted
        except AttributeError:
            # PyQt4
            accepted = QtWidgets.QDialog.Accepted

        from anima.ui import repository_dialog

        create_repository_dialog = repository_dialog.MainDialog(parent=self)
        create_repository_dialog.exec_()
        result = create_repository_dialog.result()

        if result == accepted:
            repository = create_repository_dialog.repository

            # select the created repository
            self.fill_repository_combo_box()
            index = self.repository_combo_box.findData(repository.id)
            if index:
                self.repository_combo_box.setCurrentIndex(index)

        create_repository_dialog.deleteLater()

    def update_repository_push_button_clicked(self):
        """runs when update_repository_push_button is clicked"""
        try:
            # PySide
            accepted = QtWidgets.QDialog.DialogCode.Accepted
        except AttributeError:
            # PyQt4
            accepted = QtWidgets.QDialog.Accepted

        repo = self.get_current_repository()
        if not repo:
            return

        from anima.ui import repository_dialog

        update_repository_dialog = repository_dialog.MainDialog(
            parent=self, repository=repo
        )
        update_repository_dialog.exec_()
        result = update_repository_dialog.result()

        if result == accepted:
            repository = update_repository_dialog.repository

            # select the created repository
            self.fill_repository_combo_box()
            index = self.repository_combo_box.findData(repository.id)
            if index:
                self.repository_combo_box.setCurrentIndex(index)

        update_repository_dialog.deleteLater()

    def create_structure_push_button_clicked(self):
        """runs when create_structure_push_button is clicked"""
        try:
            # PySide
            accepted = QtWidgets.QDialog.DialogCode.Accepted
        except AttributeError:
            # PyQt4
            accepted = QtWidgets.QDialog.Accepted

        from anima.ui import structure_dialog

        create_structure_dialog = structure_dialog.MainDialog(parent=self)
        create_structure_dialog.exec_()
        result = create_structure_dialog.result()

        if result == accepted:
            structure = create_structure_dialog.structure

            # select the created repository
            self.fill_structure_combo_box()
            index = self.structure_combo_box.findData(structure.id)
            if index:
                self.structure_combo_box.setCurrentIndex(index)

        create_structure_dialog.deleteLater()

    def update_structure_push_button_clicked(self):
        """runs when update_structure_push_button is clicked"""
        try:
            # PySide
            accepted = QtWidgets.QDialog.DialogCode.Accepted
        except AttributeError:
            # PyQt4
            accepted = QtWidgets.QDialog.Accepted

        structure = self.get_current_structure()
        if not structure:
            return

        from anima.ui import structure_dialog

        update_structure_dialog = structure_dialog.MainDialog(
            parent=self, structure=structure
        )
        update_structure_dialog.exec_()
        result = update_structure_dialog.result()

        if result == accepted:
            structure = update_structure_dialog.structure

            # select the created repository
            self.fill_structure_combo_box()
            index = self.structure_combo_box.findData(structure.id)
            if index:
                self.structure_combo_box.setCurrentIndex(index)

        update_structure_dialog.deleteLater()

    def get_current_repository(self):
        """returns the currently selected repository instance from the UI"""
        from stalker import Repository

        index = self.repository_combo_box.currentIndex()
        repo_id = self.repository_combo_box.itemData(index)
        repo = Repository.query.get(repo_id)
        return repo

    def get_current_structure(self):
        """returns the currently selected structure instance from the UI"""
        from stalker import Structure

        index = self.structure_combo_box.currentIndex()
        structure_id = self.structure_combo_box.itemData(index)
        structure = Structure.query.get(structure_id)
        return structure

    def accept(self):
        """create/update the project"""
        # Name
        if not self.name_line_edit.is_valid:
            QtWidgets.QMessageBox.critical(
                self, "Error", "Please fix <b>name</b> field!"
            )
            return
        name = self.name_line_edit.text()

        # Code
        if not self.code_line_edit.is_valid:
            QtWidgets.QMessageBox.critical(
                self, "Error", "Please fix <b>code</b> field!"
            )
            return
        code = self.code_line_edit.text()

        # Type
        from stalker import Type

        index = self.type_combo_box.currentIndex()
        type_id = self.type_combo_box.itemData(index)
        type_ = Type.query.get(type_id)  # None type is ok

        # Image Format
        image_format = self.image_format.get_current_image_format()
        if not image_format:
            QtWidgets.QMessageBox.critical(
                self, "Error", "Please select a valid <b>Image Format</b>!"
            )
            return

        # FPS
        fps = self.fps_spin_box.value()

        # Repository
        repo = self.get_current_repository()
        if not repo:
            QtWidgets.QMessageBox.critical(
                self, "Error", "Please select a valid <b>Repository</b>!"
            )
            return

        # Structure
        structure = self.get_current_structure()
        if not structure:
            QtWidgets.QMessageBox.critical(
                self, "Error", "Please select a valid <b>Structure</b>!"
            )
            return

        # Status
        from stalker import Status

        index = self.status_combo_box.currentIndex()
        status_id = self.status_combo_box.itemData(index)
        status = Status.query.get(status_id)
        if not status:
            QtWidgets.QMessageBox.critical(
                self, "Error", "Please select a valid <b>Status</b>!"
            )
            return

        # TODO: Add Client Data fields (which I don't care for now)
        logged_in_user = self.get_logged_in_user()

        # create or update project
        from stalker.db.session import DBSession

        if self.mode == "Create":
            # create a new project
            from stalker import Project

            new_project = Project(
                name=name,
                code=code,
                type=type_,
                repositories=[repo],
                structure=structure,
                image_format=image_format,
                fps=fps,
                created_by=logged_in_user,
                status=status,
            )
            DBSession.add(new_project)
            try:
                DBSession.commit()
            except Exception as e:
                DBSession.rollback()
                QtWidgets.QMessageBox.critical(self, "Error", str(e))
                return

        else:
            # update the project
            self.project.updated_by = logged_in_user
            self.project.name = name
            self.project.code = code
            self.project.type = type_
            self.project.repositories = [repo]
            self.project.structure = structure
            self.project.image_format = image_format
            self.project.fps = fps
            self.project.status = status
            DBSession.add(self.project)
            try:
                DBSession.commit()
            except Exception as e:
                DBSession.rollback()
                QtWidgets.QMessageBox.critical(self, "Error", str(e))
                return

        super(MainDialog, self).accept()
