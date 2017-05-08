# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'C:\Users\eoyilmaz\Documents\development\anima\anima\anima\ui\ui_files\structure_dialog.ui'
#
# Created: Mon May 08 18:49:47 2017
#      by: pyside2-uic  running on PySide2 2.0.0~alpha0
#
# WARNING! All changes made in this file will be lost!

from PySide2 import QtCore, QtGui, QtWidgets

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(754, 662)
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
        self.formLayout.setLabelAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
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
        self.filenmate_templates_label = QtWidgets.QLabel(Dialog)
        self.filenmate_templates_label.setObjectName("filenmate_templates_label")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.filenmate_templates_label)
        self.filename_template_fields_verticalLayout = QtWidgets.QVBoxLayout()
        self.filename_template_fields_verticalLayout.setObjectName("filename_template_fields_verticalLayout")
        self.formLayout.setLayout(1, QtWidgets.QFormLayout.FieldRole, self.filename_template_fields_verticalLayout)
        self.custom_template_label = QtWidgets.QLabel(Dialog)
        self.custom_template_label.setObjectName("custom_template_label")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.custom_template_label)
        self.custom_template_plainTextEdit = QtWidgets.QPlainTextEdit(Dialog)
        self.custom_template_plainTextEdit.setObjectName("custom_template_plainTextEdit")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.FieldRole, self.custom_template_plainTextEdit)
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
        self.dialog_label.setText(QtWidgets.QApplication.translate("Dialog", "Create Structure", None, -1))
        self.name_label.setText(QtWidgets.QApplication.translate("Dialog", "Name", None, -1))
        self.name_validator_label.setText(QtWidgets.QApplication.translate("Dialog", "Validator Message", None, -1))
        self.filenmate_templates_label.setText(QtWidgets.QApplication.translate("Dialog", "<html><head/><body><p align=\"right\">Filename<br/>Templates</p></body></html>", None, -1))
        self.custom_template_label.setText(QtWidgets.QApplication.translate("Dialog", "<html><head/><body><p align=\"right\">Custom<br/>Template</p></body></html>", None, -1))

