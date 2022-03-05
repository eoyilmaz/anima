# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_files\login_dialog.ui'
#
# Created: Thu Nov 10 15:32:30 2016
#      by: pyside2-uic  running on PySide2 2.0.0~alpha0
#
# WARNING! All changes made in this file will be lost!

from PySide2 import QtCore, QtGui, QtWidgets


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.setWindowModality(QtCore.Qt.ApplicationModal)
        Dialog.resize(364, 138)
        Dialog.setModal(True)
        self.verticalLayout = QtWidgets.QVBoxLayout(Dialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.formLayout = QtWidgets.QFormLayout()
        self.formLayout.setFieldGrowthPolicy(
            QtWidgets.QFormLayout.AllNonFixedFieldsGrow
        )
        self.formLayout.setContentsMargins(-1, 10, -1, -1)
        self.formLayout.setObjectName("formLayout")
        self.login_or_email_label = QtWidgets.QLabel(Dialog)
        self.login_or_email_label.setObjectName("login_or_email_label")
        self.formLayout.setWidget(
            0, QtWidgets.QFormLayout.LabelRole, self.login_or_email_label
        )
        self.login_or_email_lineEdit = QtWidgets.QLineEdit(Dialog)
        self.login_or_email_lineEdit.setInputMask("")
        self.login_or_email_lineEdit.setObjectName("login_or_email_lineEdit")
        self.formLayout.setWidget(
            0, QtWidgets.QFormLayout.FieldRole, self.login_or_email_lineEdit
        )
        self.password_label = QtWidgets.QLabel(Dialog)
        self.password_label.setObjectName("password_label")
        self.formLayout.setWidget(
            1, QtWidgets.QFormLayout.LabelRole, self.password_label
        )
        self.password_lineEdit = QtWidgets.QLineEdit(Dialog)
        self.password_lineEdit.setInputMask("")
        self.password_lineEdit.setText("")
        self.password_lineEdit.setEchoMode(QtWidgets.QLineEdit.Password)
        self.password_lineEdit.setObjectName("password_lineEdit")
        self.formLayout.setWidget(
            1, QtWidgets.QFormLayout.FieldRole, self.password_lineEdit
        )
        self.buttonBox = QtWidgets.QDialogButtonBox(Dialog)
        self.buttonBox.setStandardButtons(
            QtWidgets.QDialogButtonBox.Cancel | QtWidgets.QDialogButtonBox.Ok
        )
        self.buttonBox.setObjectName("buttonBox")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.FieldRole, self.buttonBox)
        self.verticalLayout.addLayout(self.formLayout)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(
            QtWidgets.QApplication.translate("Dialog", "Login to Stalker", None, -1)
        )
        self.login_or_email_label.setText(
            QtWidgets.QApplication.translate("Dialog", "Login or email", None, -1)
        )
        self.password_label.setText(
            QtWidgets.QApplication.translate("Dialog", "Password", None, -1)
        )
