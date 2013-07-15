# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_files/login_dialog.ui'
#
# Created: Tue Jul 16 00:55:38 2013
#      by: PyQt4 UI code generator 4.10.1
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName(_fromUtf8("Dialog"))
        Dialog.setWindowModality(QtCore.Qt.ApplicationModal)
        Dialog.resize(364, 138)
        Dialog.setModal(True)
        self.verticalLayout = QtGui.QVBoxLayout(Dialog)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.formLayout = QtGui.QFormLayout()
        self.formLayout.setFieldGrowthPolicy(QtGui.QFormLayout.AllNonFixedFieldsGrow)
        self.formLayout.setContentsMargins(-1, 10, -1, -1)
        self.formLayout.setObjectName(_fromUtf8("formLayout"))
        self.login_or_email_label = QtGui.QLabel(Dialog)
        self.login_or_email_label.setObjectName(_fromUtf8("login_or_email_label"))
        self.formLayout.setWidget(0, QtGui.QFormLayout.LabelRole, self.login_or_email_label)
        self.login_or_email_lineEdit = QtGui.QLineEdit(Dialog)
        self.login_or_email_lineEdit.setInputMask(_fromUtf8(""))
        self.login_or_email_lineEdit.setObjectName(_fromUtf8("login_or_email_lineEdit"))
        self.formLayout.setWidget(0, QtGui.QFormLayout.FieldRole, self.login_or_email_lineEdit)
        self.password_label = QtGui.QLabel(Dialog)
        self.password_label.setObjectName(_fromUtf8("password_label"))
        self.formLayout.setWidget(1, QtGui.QFormLayout.LabelRole, self.password_label)
        self.password_lineEdit = QtGui.QLineEdit(Dialog)
        self.password_lineEdit.setInputMask(_fromUtf8(""))
        self.password_lineEdit.setText(_fromUtf8(""))
        self.password_lineEdit.setEchoMode(QtGui.QLineEdit.Password)
        self.password_lineEdit.setObjectName(_fromUtf8("password_lineEdit"))
        self.formLayout.setWidget(1, QtGui.QFormLayout.FieldRole, self.password_lineEdit)
        self.buttonBox = QtGui.QDialogButtonBox(Dialog)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.formLayout.setWidget(2, QtGui.QFormLayout.FieldRole, self.buttonBox)
        self.verticalLayout.addLayout(self.formLayout)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(_translate("Dialog", "Login to Stalker", None))
        self.login_or_email_label.setText(_translate("Dialog", "Login or email", None))
        self.password_label.setText(_translate("Dialog", "Password", None))

