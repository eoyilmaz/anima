# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'C:\Users\eoyilmaz\Documents\development\anima\anima\anima\ui\ui_files\repository_dialog.ui'
#
# Created: Sun May 07 20:38:08 2017
#      by: pyside2-uic  running on PySide2 2.0.0~alpha0
#
# WARNING! All changes made in this file will be lost!

from PySide2 import QtCore, QtGui, QtWidgets

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(348, 220)
        self.verticalLayout = QtWidgets.QVBoxLayout(Dialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.dialog_label = QtWidgets.QLabel(Dialog)
        self.dialog_label.setStyleSheet("color: rgb(71, 143, 202);\n"
"font: 18pt;")
        self.dialog_label.setObjectName("dialog_label")
        self.verticalLayout.addWidget(self.dialog_label)
        self.line = QtWidgets.QFrame(Dialog)
        self.line.setFrameShape(QtWidgets.QFrame.HLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setObjectName("line")
        self.verticalLayout.addWidget(self.line)
        self.formLayout = QtWidgets.QFormLayout()
        self.formLayout.setObjectName("formLayout")
        self.name_label = QtWidgets.QLabel(Dialog)
        self.name_label.setObjectName("name_label")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.name_label)
        self.name_fields_verticalLayout = QtWidgets.QVBoxLayout()
        self.name_fields_verticalLayout.setObjectName("name_fields_verticalLayout")
        self.name_validator_label = QtWidgets.QLabel(Dialog)
        self.name_validator_label.setStyleSheet("color: rgb(255, 0, 0);")
        self.name_validator_label.setObjectName("name_validator_label")
        self.name_fields_verticalLayout.addWidget(self.name_validator_label)
        self.formLayout.setLayout(0, QtWidgets.QFormLayout.FieldRole, self.name_fields_verticalLayout)
        self.windows_path_label = QtWidgets.QLabel(Dialog)
        self.windows_path_label.setObjectName("windows_path_label")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.windows_path_label)
        self.windows_path_lineEdit = QtWidgets.QLineEdit(Dialog)
        self.windows_path_lineEdit.setObjectName("windows_path_lineEdit")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.windows_path_lineEdit)
        self.linux_label = QtWidgets.QLabel(Dialog)
        self.linux_label.setObjectName("linux_label")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.linux_label)
        self.linux_path_lineEdit = QtWidgets.QLineEdit(Dialog)
        self.linux_path_lineEdit.setObjectName("linux_path_lineEdit")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.FieldRole, self.linux_path_lineEdit)
        self.osx_path_label = QtWidgets.QLabel(Dialog)
        self.osx_path_label.setObjectName("osx_path_label")
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.LabelRole, self.osx_path_label)
        self.osx_path_lineEdit = QtWidgets.QLineEdit(Dialog)
        self.osx_path_lineEdit.setObjectName("osx_path_lineEdit")
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.FieldRole, self.osx_path_lineEdit)
        self.verticalLayout.addLayout(self.formLayout)
        self.buttonBox = QtWidgets.QDialogButtonBox(Dialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)
        self.verticalLayout.setStretch(2, 1)

        self.retranslateUi(Dialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("accepted()"), Dialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("rejected()"), Dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QtWidgets.QApplication.translate("Dialog", "Dialog", None, -1))
        self.dialog_label.setText(QtWidgets.QApplication.translate("Dialog", "Create Repository", None, -1))
        self.name_label.setText(QtWidgets.QApplication.translate("Dialog", "Name", None, -1))
        self.name_validator_label.setText(QtWidgets.QApplication.translate("Dialog", "Validator Message", None, -1))
        self.windows_path_label.setText(QtWidgets.QApplication.translate("Dialog", "Windows Path", None, -1))
        self.linux_label.setText(QtWidgets.QApplication.translate("Dialog", "Linux Path", None, -1))
        self.osx_path_label.setText(QtWidgets.QApplication.translate("Dialog", "OSX Path", None, -1))

