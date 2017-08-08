# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_files\structure_dialog.ui'
#
# Created: Tue May 09 09:41:16 2017
#      by: pyside-uic 0.2.14 running on PySide 1.1.1
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(754, 662)
        self.verticalLayout = QtGui.QVBoxLayout(Dialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.dialog_label = QtGui.QLabel(Dialog)
        self.dialog_label.setStyleSheet("color: rgb(71, 143, 202);\n"
"font: 18pt;")
        self.dialog_label.setObjectName("dialog_label")
        self.verticalLayout.addWidget(self.dialog_label)
        self.line = QtGui.QFrame(Dialog)
        self.line.setFrameShape(QtGui.QFrame.HLine)
        self.line.setFrameShadow(QtGui.QFrame.Sunken)
        self.line.setObjectName("line")
        self.verticalLayout.addWidget(self.line)
        self.formLayout = QtGui.QFormLayout()
        self.formLayout.setLabelAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.formLayout.setObjectName("formLayout")
        self.name_label = QtGui.QLabel(Dialog)
        self.name_label.setObjectName("name_label")
        self.formLayout.setWidget(0, QtGui.QFormLayout.LabelRole, self.name_label)
        self.name_fields_verticalLayout = QtGui.QVBoxLayout()
        self.name_fields_verticalLayout.setObjectName("name_fields_verticalLayout")
        self.name_validator_label = QtGui.QLabel(Dialog)
        self.name_validator_label.setStyleSheet("color: rgb(255, 0, 0);")
        self.name_validator_label.setObjectName("name_validator_label")
        self.name_fields_verticalLayout.addWidget(self.name_validator_label)
        self.formLayout.setLayout(0, QtGui.QFormLayout.FieldRole, self.name_fields_verticalLayout)
        self.filenmate_templates_label = QtGui.QLabel(Dialog)
        self.filenmate_templates_label.setObjectName("filenmate_templates_label")
        self.formLayout.setWidget(1, QtGui.QFormLayout.LabelRole, self.filenmate_templates_label)
        self.filename_template_fields_verticalLayout = QtGui.QVBoxLayout()
        self.filename_template_fields_verticalLayout.setObjectName("filename_template_fields_verticalLayout")
        self.formLayout.setLayout(1, QtGui.QFormLayout.FieldRole, self.filename_template_fields_verticalLayout)
        self.custom_template_label = QtGui.QLabel(Dialog)
        self.custom_template_label.setObjectName("custom_template_label")
        self.formLayout.setWidget(2, QtGui.QFormLayout.LabelRole, self.custom_template_label)
        self.custom_template_plainTextEdit = QtGui.QPlainTextEdit(Dialog)
        self.custom_template_plainTextEdit.setObjectName("custom_template_plainTextEdit")
        self.formLayout.setWidget(2, QtGui.QFormLayout.FieldRole, self.custom_template_plainTextEdit)
        self.verticalLayout.addLayout(self.formLayout)
        self.buttonBox = QtGui.QDialogButtonBox(Dialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)
        self.verticalLayout.setStretch(2, 1)

        self.retranslateUi(Dialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("accepted()"), Dialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("rejected()"), Dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QtGui.QApplication.translate("Dialog", "Dialog", None, QtGui.QApplication.UnicodeUTF8))
        self.dialog_label.setText(QtGui.QApplication.translate("Dialog", "Create Structure", None, QtGui.QApplication.UnicodeUTF8))
        self.name_label.setText(QtGui.QApplication.translate("Dialog", "Name", None, QtGui.QApplication.UnicodeUTF8))
        self.name_validator_label.setText(QtGui.QApplication.translate("Dialog", "Validator Message", None, QtGui.QApplication.UnicodeUTF8))
        self.filenmate_templates_label.setText(QtGui.QApplication.translate("Dialog", "<html><head/><body><p align=\"right\">Filename<br/>Templates</p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
        self.custom_template_label.setText(QtGui.QApplication.translate("Dialog", "<html><head/><body><p align=\"right\">Custom<br/>Template</p></body></html>", None, QtGui.QApplication.UnicodeUTF8))

