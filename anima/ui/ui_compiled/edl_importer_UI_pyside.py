# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file './ui_files/edl_importer.ui'
#
# Created: Thu Mar 20 13:46:56 2014
#      by: pyside-uic 0.2.13 running on PySide 1.1.0
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(923, 542)
        self.verticalLayout = QtGui.QVBoxLayout(Dialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.formLayout = QtGui.QFormLayout()
        self.formLayout.setFieldGrowthPolicy(QtGui.QFormLayout.AllNonFixedFieldsGrow)
        self.formLayout.setObjectName("formLayout")
        self.media_files_path_lineEdit = QtGui.QLineEdit(Dialog)
        self.media_files_path_lineEdit.setObjectName("media_files_path_lineEdit")
        self.formLayout.setWidget(0, QtGui.QFormLayout.FieldRole, self.media_files_path_lineEdit)
        self.label = QtGui.QLabel(Dialog)
        self.label.setObjectName("label")
        self.formLayout.setWidget(1, QtGui.QFormLayout.LabelRole, self.label)
        self.label_2 = QtGui.QLabel(Dialog)
        self.label_2.setObjectName("label_2")
        self.formLayout.setWidget(0, QtGui.QFormLayout.LabelRole, self.label_2)
        self.verticalLayout.addLayout(self.formLayout)
        self.edl_preview_plainTextEdit = QtGui.QPlainTextEdit(Dialog)
        self.edl_preview_plainTextEdit.setReadOnly(True)
        self.edl_preview_plainTextEdit.setObjectName("edl_preview_plainTextEdit")
        self.verticalLayout.addWidget(self.edl_preview_plainTextEdit)
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.send_pushButton = QtGui.QPushButton(Dialog)
        self.send_pushButton.setObjectName("send_pushButton")
        self.horizontalLayout_2.addWidget(self.send_pushButton)
        self.verticalLayout.addLayout(self.horizontalLayout_2)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)
        Dialog.setTabOrder(self.media_files_path_lineEdit, self.edl_preview_plainTextEdit)
        Dialog.setTabOrder(self.edl_preview_plainTextEdit, self.send_pushButton)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QtGui.QApplication.translate("Dialog", "EDL Importer", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("Dialog", "EDL Path", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("Dialog", "AVID Media Files Path", None, QtGui.QApplication.UnicodeUTF8))
        self.send_pushButton.setText(QtGui.QApplication.translate("Dialog", "Send To AVID", None, QtGui.QApplication.UnicodeUTF8))

