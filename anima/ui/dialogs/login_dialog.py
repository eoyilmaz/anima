# -*- coding: utf-8 -*-

import anima
from anima import logger
from anima.ui.base import AnimaDialogBase, ui_caller
from anima.ui.lib import QtCore, QtGui, QtWidgets


def UI(app_in=None, executor=None):
    """the UI to call the dialog by itself

    :param app_in: A Qt Application instance, which you can pass to let the UI
      be attached to the given applications event process.

    :param executor: Instead of calling app.exec_ the UI will call this given
      function. It also passes the created app instance to this executor.
    """
    return ui_caller(app_in, executor, MainDialog)


class MainDialog(QtWidgets.QDialog, AnimaDialogBase):
    """This is a simple login dialog which connects to Stalker to authenticate
    the username/password couple.
    """

    def __init__(self, parent=None):
        logger.debug("initializing the interface")
        super(MainDialog, self).__init__(parent)
        self.success = False
        self.login_or_email_label = None
        self.login_or_email_line_edit = None
        self.password_line_edit = None
        self.button_box = None
        self.setup_ui()
        self.center_window()
        logger.debug("finished initializing the interface")

    def setup_ui(self):
        """Create UI elements."""
        # change the window title
        self.setWindowTitle("Login Dialog | Anima v{}".format(anima.__version__))

        self.setObjectName("Dialog")
        self.setWindowModality(QtCore.Qt.ApplicationModal)
        self.resize(364, 138)
        self.setModal(True)
        main_layout = QtWidgets.QVBoxLayout()
        self.setLayout(main_layout)
        form_layout = QtWidgets.QFormLayout()
        form_layout.setFieldGrowthPolicy(QtWidgets.QFormLayout.AllNonFixedFieldsGrow)
        form_layout.setContentsMargins(-1, 10, -1, -1)

        label_role = QtWidgets.QFormLayout.LabelRole
        field_role = QtWidgets.QFormLayout.FieldRole

        self.login_or_email_label = QtWidgets.QLabel(self)
        self.login_or_email_label.setText("Login or email")
        form_layout.setWidget(0, label_role, self.login_or_email_label)
        self.login_or_email_line_edit = QtWidgets.QLineEdit(self)
        self.login_or_email_line_edit.setInputMask("")
        form_layout.setWidget(0, field_role, self.login_or_email_line_edit)

        # Password
        form_layout.setWidget(1, label_role, QtWidgets.QLabel("Password", self))
        self.password_line_edit = QtWidgets.QLineEdit(self)
        self.password_line_edit.setInputMask("")
        self.password_line_edit.setText("")
        self.password_line_edit.setEchoMode(QtWidgets.QLineEdit.Password)
        form_layout.setWidget(1, field_role, self.password_line_edit)

        # Button Box
        self.button_box = QtWidgets.QDialogButtonBox(self)
        self.button_box.setStandardButtons(
            QtWidgets.QDialogButtonBox.Cancel | QtWidgets.QDialogButtonBox.Ok
        )
        form_layout.setWidget(2, field_role, self.button_box)
        main_layout.addLayout(form_layout)

        # setup signals
        # cancel button
        self.button_box.rejected.connect(self.close)

        # Ok button
        self.button_box.accepted.connect(self.login)

        logger.debug("finished setting up interface signals")

    def login(self):
        """does the nasty details for user to login"""
        from anima.utils import authenticate

        # get the user first
        login = self.login_or_email_line_edit.text()
        password = self.password_line_edit.text()

        if authenticate(login, password):
            self.accept()
        else:
            QtWidgets.QMessageBox.critical(
                self, "Error", "login or password is incorrect"
            )
