# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_files/login_dialog.ui'
#
# Created: Tue Jul 16 00:55:37 2013
#      by: pyside-uic 0.2.14 running on PySide 1.1.2
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.setWindowModality(QtCore.Qt.ApplicationModal)
        Dialog.resize(364, 138)
        Dialog.setModal(True)
        self.verticalLayout = QtGui.QVBoxLayout(Dialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.formLayout = QtGui.QFormLayout()
        self.formLayout.setFieldGrowthPolicy(QtGui.QFormLayout.AllNonFixedFieldsGrow)
        self.formLayout.setContentsMargins(-1, 10, -1, -1)
        self.formLayout.setObjectName("formLayout")
        self.login_or_email_label = QtGui.QLabel(Dialog)
        self.login_or_email_label.setObjectName("login_or_email_label")
        self.formLayout.setWidget(0, QtGui.QFormLayout.LabelRole, self.login_or_email_label)
        self.login_or_email_lineEdit = QtGui.QLineEdit(Dialog)
        self.login_or_email_lineEdit.setInputMask("")
        self.login_or_email_lineEdit.setObjectName("login_or_email_lineEdit")
        self.formLayout.setWidget(0, QtGui.QFormLayout.FieldRole, self.login_or_email_lineEdit)
        self.password_label = QtGui.QLabel(Dialog)
        self.password_label.setObjectName("password_label")
        self.formLayout.setWidget(1, QtGui.QFormLayout.LabelRole, self.password_label)
        self.password_lineEdit = QtGui.QLineEdit(Dialog)
        self.password_lineEdit.setInputMask("")
        self.password_lineEdit.setText("")
        self.password_lineEdit.setEchoMode(QtGui.QLineEdit.Password)
        self.password_lineEdit.setObjectName("password_lineEdit")
        self.formLayout.setWidget(1, QtGui.QFormLayout.FieldRole, self.password_lineEdit)
        self.buttonBox = QtGui.QDialogButtonBox(Dialog)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.formLayout.setWidget(2, QtGui.QFormLayout.FieldRole, self.buttonBox)
        self.verticalLayout.addLayout(self.formLayout)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QtGui.QApplication.translate("Dialog", "Login to Stalker", None, QtGui.QApplication.UnicodeUTF8))
        self.login_or_email_label.setText(QtGui.QApplication.translate("Dialog", "Login or email", None, QtGui.QApplication.UnicodeUTF8))
        self.password_label.setText(QtGui.QApplication.translate("Dialog", "Password", None, QtGui.QApplication.UnicodeUTF8))

