# -*- coding: utf-8 -*-
from anima.ui.lib import QtCore, QtWidgets
from anima.ui.base import AnimaDialogBase, ui_caller


def UI(app_in=None, executor=None, **kwargs):
    """
    :param app_in: A Qt Application instance, which you can pass to let the UI
      be attached to the given applications event process.

    :param executor: Instead of calling app.exec_ the UI will call this given
      function. It also passes the created app instance to this executor.

    """
    return ui_caller(app_in, executor, UserDialog, **kwargs)


class UserDialog(QtWidgets.QDialog):
    """The User Creation Dialog"""

    def __init__(self, parent=None):
        super(UserDialog, self).__init__(parent=parent)
        self.setWindowTitle("User Dialog")
        self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)
        self.create_widgets()
        self.create_layouts()
        self.create_connections()

    def create_widgets(self):
        """Creates widgets"""
        self.dialog_label = QtWidgets.QLabel()
        self.dialog_label.setStyleSheet("color: rgb(71, 143, 202);\nfont: 18pt;")
        self.dialog_label.setText("Create User")

        self.line = QtWidgets.QFrame()
        self.line.setFrameShape(QtWidgets.QFrame.HLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)

        self.name_line_edit = QtWidgets.QLineEdit()
        self.name_line_edit.setPlaceholderText("Enter Name")

        self.login_line_edit = QtWidgets.QLineEdit()
        self.login_line_edit.setPlaceholderText("stalker")

        self.email_line_edit = QtWidgets.QLineEdit()
        self.email_line_edit.setPlaceholderText("stalker@gmail.com")

        self.password_line_edit = QtWidgets.QLineEdit()
        self.password_line_edit.setPlaceholderText("******")

        self.ok_button = QtWidgets.QPushButton("OK")
        self.cancel_button = QtWidgets.QPushButton("Cancel")

    def create_layouts(self):
        """Creates layouts"""
        form_layout = QtWidgets.QFormLayout()
        form_layout.addRow("Name", self.name_line_edit)
        form_layout.addRow("Login", self.login_line_edit)
        form_layout.addRow("Email", self.email_line_edit)
        form_layout.addRow("Password", self.password_line_edit)

        button_layout = QtWidgets.QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(self.ok_button)
        button_layout.addWidget(self.cancel_button)

        label_layout = QtWidgets.QVBoxLayout()
        label_layout.addWidget(self.dialog_label)
        label_layout.addWidget(self.line)
        label_layout.addStretch()

        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.addLayout(label_layout)
        main_layout.addLayout(form_layout)
        main_layout.addLayout(button_layout)

        self.resize(328, 184)

    def create_connections(self):
        """Creates connections"""
        self.ok_button.clicked.connect(self.check_user_pass)
        self.cancel_button.clicked.connect(self.close)

    def check_user_pass(self):
        """Checks the information entered by the user"""
        self.user_name = self.name_line_edit.text()
        self.user_login = self.login_line_edit.text()
        self.user_email = self.email_line_edit.text()
        self.user_password = self.password_line_edit.text()

        # Sends a warning message if the entered user information is missing
        if len(self.user_name) < 2 or len(self.user_login) < 2 or len(self.user_email) < 2 or len(
                self.user_password) < 2:
            QtWidgets.QMessageBox.warning(
                self,
                "Warning",
                "Please, fill out user information completely!"
            )
        else:
            self.create_user()

    def create_user(self):
        """Creates new user"""
        from stalker.db.session import DBSession
        from stalker import User

        new_user = User(
            name="{0}".format(self.user_name),
            login="{0}".format(self.user_login),
            email="{0}".format(self.user_email),
            password="{0}".format(self.user_password)
        )

        # Checks if the user's name and e-mail address are registered in the database.
        # Sends a warning message to the user if registered.

        if not User.query.filter_by(email=self.user_email).scalar() is None:
            QtWidgets.QMessageBox.warning(
                self,
                "Warning",
                "The email address you entered already belongs to an existing user , "
                "Please re-enter your e-mail address!"
            )
        elif not User.query.filter_by(login=self.user_login).scalar() is None:
            QtWidgets.QMessageBox.warning(
                self,
                "Warning",
                "The user '{0}' already exists, Please enter new "
                "username!".format(self.user_login)
            )
        else:
            try:
                # Save the user to database
                DBSession.save(new_user)
            # Gets the string representation of an exception
            except BaseException as e:
                DBSession.rollback()
                QtWidgets.QMessageBox.critical(
                    self,
                    "Error",
                    str(e)
                )

            # now we can give the information message
            QtWidgets.QMessageBox.information(
                self,
                "Success",
                "User '{0}' successfully created!".format(self.user_login)
            )
            # then we can close this dialog
            self.close()
