# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_files\edl_importer.ui'
#
# Created: Thu Nov 10 15:32:30 2016
#      by: pyside2-uic  running on PySide2 2.0.0~alpha0
#
# WARNING! All changes made in this file will be lost!

from PySide2 import QtCore, QtGui, QtWidgets


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(923, 542)
        self.verticalLayout = QtWidgets.QVBoxLayout(Dialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.formLayout = QtWidgets.QFormLayout()
        self.formLayout.setFieldGrowthPolicy(
            QtWidgets.QFormLayout.AllNonFixedFieldsGrow
        )
        self.formLayout.setObjectName("formLayout")
        self.media_files_path_lineEdit = QtWidgets.QLineEdit(Dialog)
        self.media_files_path_lineEdit.setObjectName("media_files_path_lineEdit")
        self.formLayout.setWidget(
            0, QtWidgets.QFormLayout.FieldRole, self.media_files_path_lineEdit
        )
        self.label = QtWidgets.QLabel(Dialog)
        self.label.setObjectName("label")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.label)
        self.label_2 = QtWidgets.QLabel(Dialog)
        self.label_2.setObjectName("label_2")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.label_2)
        self.verticalLayout.addLayout(self.formLayout)
        self.edl_preview_plainTextEdit = QtWidgets.QPlainTextEdit(Dialog)
        self.edl_preview_plainTextEdit.setReadOnly(True)
        self.edl_preview_plainTextEdit.setObjectName("edl_preview_plainTextEdit")
        self.verticalLayout.addWidget(self.edl_preview_plainTextEdit)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.send_pushButton = QtWidgets.QPushButton(Dialog)
        self.send_pushButton.setObjectName("send_pushButton")
        self.horizontalLayout_2.addWidget(self.send_pushButton)
        self.verticalLayout.addLayout(self.horizontalLayout_2)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)
        Dialog.setTabOrder(
            self.media_files_path_lineEdit, self.edl_preview_plainTextEdit
        )
        Dialog.setTabOrder(self.edl_preview_plainTextEdit, self.send_pushButton)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(
            QtWidgets.QApplication.translate("Dialog", "EDL Importer", None, -1)
        )
        self.label.setText(
            QtWidgets.QApplication.translate("Dialog", "EDL Path", None, -1)
        )
        self.label_2.setText(
            QtWidgets.QApplication.translate(
                "Dialog", "AVID Media Files Path", None, -1
            )
        )
        self.send_pushButton.setText(
            QtWidgets.QApplication.translate("Dialog", "Send To AVID", None, -1)
        )
