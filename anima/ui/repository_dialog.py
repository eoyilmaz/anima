# -*- coding: utf-8 -*-

import re

from anima import logger
from anima.ui.base import AnimaDialogBase, ui_caller
from anima.ui import IS_PYSIDE, IS_PYSIDE2, IS_PYQT4
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
    """The Repository Dialog"""

    def __init__(self, parent=None, repository=None):
        super(MainDialog, self).__init__(parent=parent)
        self._setup_ui()

        self.repository = repository
        self.mode = "Create"

        if self.repository:
            self.mode = "Update"

        self.dialog_label.setText("%s Repository" % self.mode)

        self._setup_signals()

        self._set_defaults()

        if self.repository:
            self.fill_ui_with_repository(self.repository)

    def _setup_ui(self):
        self.setObjectName("Dialog")
        self.resize(502, 220)
        self.vertical_layout = QtWidgets.QVBoxLayout(self)
        self.vertical_layout.setObjectName("verticalLayout")
        self.dialog_label = QtWidgets.QLabel(self)
        self.dialog_label.setStyleSheet("color: rgb(71, 143, 202);\n" "font: 18pt;")
        self.dialog_label.setObjectName("dialog_label")
        self.dialog_label.setText("Create Repository")

        self.vertical_layout.addWidget(self.dialog_label)
        self.line = QtWidgets.QFrame(self)
        self.line.setFrameShape(QtWidgets.QFrame.HLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setObjectName("line")
        self.vertical_layout.addWidget(self.line)
        self.form_layout = QtWidgets.QFormLayout()
        self.form_layout.setLabelAlignment(
            QtCore.Qt.AlignRight | QtCore.Qt.AlignTrailing | QtCore.Qt.AlignVCenter
        )
        self.form_layout.setObjectName("form_layout")

        row_number = 0
        # -------------
        # Name
        # Label
        self.name_label = QtWidgets.QLabel(self)
        self.name_label.setObjectName("name_label")
        self.name_label.setText("Name")
        self.form_layout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.name_label)

        # Field
        self.name_fields_vertical_layout = QtWidgets.QVBoxLayout()
        self.name_fields_vertical_layout.setObjectName("name_fields_verticalLayout")
        self.name_validator_label = QtWidgets.QLabel(self)
        self.name_validator_label.setStyleSheet("color: rgb(255, 0, 0);")
        self.name_validator_label.setObjectName("name_validator_label")
        self.name_fields_vertical_layout.addWidget(self.name_validator_label)
        self.form_layout.setLayout(
            row_number,
            QtWidgets.QFormLayout.FieldRole,
            self.name_fields_vertical_layout,
        )
        self.name_validator_label.setText("Validator Message")

        # create name_line_edit
        from anima.ui.widgets import ValidatedLineEdit

        self.name_line_edit = ValidatedLineEdit(message_field=self.name_validator_label)
        self.name_line_edit.setPlaceholderText("Enter Name")
        self.name_fields_vertical_layout.insertWidget(0, self.name_line_edit)

        row_number += 1
        # -------------
        # Code
        # Label
        self.code_label = QtWidgets.QLabel(self)
        self.code_label.setText("Code")
        self.code_label.setObjectName("code_label")
        self.form_layout.setWidget(
            row_number, QtWidgets.QFormLayout.LabelRole, self.code_label
        )

        # Field
        self.code_fields_vertical_layout = QtWidgets.QVBoxLayout()
        self.code_fields_vertical_layout.setObjectName("code_fields_verticalLayout")
        self.code_validator_label = QtWidgets.QLabel(self)
        self.code_validator_label.setStyleSheet("color: rgb(255, 0, 0);")
        self.code_validator_label.setObjectName("code_validator_label")
        self.code_fields_vertical_layout.addWidget(self.code_validator_label)
        self.form_layout.setLayout(
            row_number,
            QtWidgets.QFormLayout.FieldRole,
            self.code_fields_vertical_layout,
        )

        # create code_line_edit
        from anima.ui.widgets import ValidatedLineEdit

        self.code_line_edit = ValidatedLineEdit(message_field=self.code_validator_label)
        self.code_line_edit.setPlaceholderText("Enter Code")
        self.code_fields_vertical_layout.insertWidget(0, self.code_line_edit)

        row_number += 1
        # -------------
        # Windows Path
        # Label
        self.windows_path_label = QtWidgets.QLabel(self)
        self.windows_path_label.setObjectName("windows_path_label")
        self.form_layout.setWidget(
            row_number, QtWidgets.QFormLayout.LabelRole, self.windows_path_label
        )
        self.windows_path_label.setText("Windows Path")

        # Field
        self.windows_path_line_edit = QtWidgets.QLineEdit(self)
        self.windows_path_line_edit.setObjectName("windows_path_lineEdit")
        self.form_layout.setWidget(
            row_number, QtWidgets.QFormLayout.FieldRole, self.windows_path_line_edit
        )

        row_number += 1
        # -------------
        # Linux Path
        # Label
        self.linux_label = QtWidgets.QLabel(self)
        self.linux_label.setObjectName("linux_label")
        self.linux_label.setText("Linux Path")
        self.form_layout.setWidget(
            row_number, QtWidgets.QFormLayout.LabelRole, self.linux_label
        )

        # Field
        self.linux_path_line_edit = QtWidgets.QLineEdit(self)
        self.linux_path_line_edit.setObjectName("linux_path_lineEdit")
        self.form_layout.setWidget(
            row_number, QtWidgets.QFormLayout.FieldRole, self.linux_path_line_edit
        )

        row_number += 1
        # -------------
        # OSX Path
        # Label
        self.osx_path_label = QtWidgets.QLabel(self)
        self.osx_path_label.setObjectName("osx_path_label")
        self.osx_path_label.setText("OSX Path")
        self.form_layout.setWidget(
            row_number, QtWidgets.QFormLayout.LabelRole, self.osx_path_label
        )

        # Field
        self.osx_path_line_edit = QtWidgets.QLineEdit(self)
        self.osx_path_line_edit.setObjectName("osx_path_lineEdit")
        self.form_layout.setWidget(
            row_number, QtWidgets.QFormLayout.FieldRole, self.osx_path_line_edit
        )
        self.vertical_layout.addLayout(self.form_layout)

        # Button Box
        self.button_box = QtWidgets.QDialogButtonBox(self)
        self.button_box.setOrientation(QtCore.Qt.Horizontal)
        self.button_box.setStandardButtons(
            QtWidgets.QDialogButtonBox.Cancel | QtWidgets.QDialogButtonBox.Ok
        )
        self.button_box.setObjectName("button_box")
        self.vertical_layout.addWidget(self.button_box)
        self.vertical_layout.setStretch(2, 1)

        QtCore.QObject.connect(
            self.button_box, QtCore.SIGNAL("accepted()"), self.accept
        )
        QtCore.QObject.connect(
            self.button_box, QtCore.SIGNAL("rejected()"), self.reject
        )
        QtCore.QMetaObject.connectSlotsByName(self)

    def _setup_signals(self):
        """create the signals"""
        # name_line_edit is changed
        QtCore.QObject.connect(
            self.name_line_edit,
            QtCore.SIGNAL("textChanged(QString)"),
            self.name_line_edit_changed,
        )

    def _set_defaults(self):
        """sets the default values"""
        pass

    def name_line_edit_changed(self, text):
        """runs when the name_line_edit text has changed"""
        if re.findall(r"[^a-zA-Z0-9\-_ ]+", text):
            self.name_line_edit.set_invalid("Invalid character")
        else:
            if text == "":
                self.name_line_edit.set_invalid("Enter a name")
            else:
                self.name_line_edit.set_valid()

    def fill_ui_with_repository(self, repository):
        """fills the UI with the given repository

        :param repository: A Stalker ImageFormat instance
        :return:
        """
        if False:
            from stalker import Repository

            assert isinstance(repository, Repository)

        self.repository = repository
        self.name_line_edit.setText(self.repository.name)
        self.name_line_edit.set_valid()

        self.code_line_edit.setText(self.repository.code)
        self.code_line_edit.set_valid()

        self.windows_path_line_edit.setText(self.repository.windows_path)
        self.linux_path_line_edit.setText(self.repository.linux_path)
        self.osx_path_line_edit.setText(self.repository.osx_path)

    def accept(self):
        """overridden accept method"""
        if not self.name_line_edit.is_valid:
            QtWidgets.QMessageBox.critical(
                self, "Error", "Please fix <b>name</b> field!"
            )
            return
        name = self.name_line_edit.text()
        code = self.code_line_edit.text()

        windows_path = self.windows_path_line_edit.text()
        linux_path = self.linux_path_line_edit.text()
        osx_path = self.osx_path_line_edit.text()

        from stalker import Repository
        from stalker.db.session import DBSession

        logged_in_user = self.get_logged_in_user()
        if self.mode == "Create":
            # Create a new Repository
            try:
                repo = Repository(
                    name=name,
                    code=code,
                    windows_path=windows_path,
                    linux_path=linux_path,
                    osx_path=osx_path,
                )
                self.repository = repo
                DBSession.add(repo)
                DBSession.commit()
            except Exception as e:
                DBSession.rollback()
                QtWidgets.QMessageBox.critical(self, "Error", str(e))
                return

        elif self.mode == "Update":
            # Update the repository
            try:
                self.repository.name = name
                self.repository.code = code
                self.repository.windows_path = windows_path
                self.repository.linux_path = linux_path
                self.repository.osx_path = osx_path
                self.repository.updated_by = logged_in_user
                DBSession.add(self.repository)
                DBSession.commit()
            except Exception as e:
                DBSession.rollback()
                QtWidgets.QMessageBox.critical(self, "Error", str(e))
                return

        super(MainDialog, self).accept()
