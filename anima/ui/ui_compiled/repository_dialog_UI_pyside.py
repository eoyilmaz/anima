# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_files\repository_dialog.ui'
#
# Created: Tue May 09 09:41:16 2017
#      by: pyside-uic 0.2.14 running on PySide 1.1.1
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(502, 220)
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
        self.windows_path_label = QtGui.QLabel(Dialog)
        self.windows_path_label.setObjectName("windows_path_label")
        self.formLayout.setWidget(1, QtGui.QFormLayout.LabelRole, self.windows_path_label)
        self.windows_path_lineEdit = QtGui.QLineEdit(Dialog)
        self.windows_path_lineEdit.setObjectName("windows_path_lineEdit")
        self.formLayout.setWidget(1, QtGui.QFormLayout.FieldRole, self.windows_path_lineEdit)
        self.linux_label = QtGui.QLabel(Dialog)
        self.linux_label.setObjectName("linux_label")
        self.formLayout.setWidget(2, QtGui.QFormLayout.LabelRole, self.linux_label)
        self.linux_path_lineEdit = QtGui.QLineEdit(Dialog)
        self.linux_path_lineEdit.setObjectName("linux_path_lineEdit")
        self.formLayout.setWidget(2, QtGui.QFormLayout.FieldRole, self.linux_path_lineEdit)
        self.osx_path_label = QtGui.QLabel(Dialog)
        self.osx_path_label.setObjectName("osx_path_label")
        self.formLayout.setWidget(3, QtGui.QFormLayout.LabelRole, self.osx_path_label)
        self.osx_path_lineEdit = QtGui.QLineEdit(Dialog)
        self.osx_path_lineEdit.setObjectName("osx_path_lineEdit")
        self.formLayout.setWidget(3, QtGui.QFormLayout.FieldRole, self.osx_path_lineEdit)
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
        self.dialog_label.setText(QtGui.QApplication.translate("Dialog", "Create Repository", None, QtGui.QApplication.UnicodeUTF8))
        self.name_label.setText(QtGui.QApplication.translate("Dialog", "Name", None, QtGui.QApplication.UnicodeUTF8))
        self.name_validator_label.setText(QtGui.QApplication.translate("Dialog", "Validator Message", None, QtGui.QApplication.UnicodeUTF8))
        self.windows_path_label.setText(QtGui.QApplication.translate("Dialog", "Windows Path", None, QtGui.QApplication.UnicodeUTF8))
        self.linux_label.setText(QtGui.QApplication.translate("Dialog", "Linux Path", None, QtGui.QApplication.UnicodeUTF8))
        self.osx_path_label.setText(QtGui.QApplication.translate("Dialog", "OSX Path", None, QtGui.QApplication.UnicodeUTF8))

