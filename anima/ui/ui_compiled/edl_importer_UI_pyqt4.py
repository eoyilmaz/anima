# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file './ui_files/edl_importer.ui'
#
# Created: Thu Mar 20 13:46:56 2014
#      by: PyQt4 UI code generator 4.10.2
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
        Dialog.resize(923, 542)
        self.verticalLayout = QtGui.QVBoxLayout(Dialog)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.formLayout = QtGui.QFormLayout()
        self.formLayout.setFieldGrowthPolicy(QtGui.QFormLayout.AllNonFixedFieldsGrow)
        self.formLayout.setObjectName(_fromUtf8("formLayout"))
        self.media_files_path_lineEdit = QtGui.QLineEdit(Dialog)
        self.media_files_path_lineEdit.setObjectName(_fromUtf8("media_files_path_lineEdit"))
        self.formLayout.setWidget(0, QtGui.QFormLayout.FieldRole, self.media_files_path_lineEdit)
        self.label = QtGui.QLabel(Dialog)
        self.label.setObjectName(_fromUtf8("label"))
        self.formLayout.setWidget(1, QtGui.QFormLayout.LabelRole, self.label)
        self.label_2 = QtGui.QLabel(Dialog)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.formLayout.setWidget(0, QtGui.QFormLayout.LabelRole, self.label_2)
        self.verticalLayout.addLayout(self.formLayout)
        self.edl_preview_plainTextEdit = QtGui.QPlainTextEdit(Dialog)
        self.edl_preview_plainTextEdit.setReadOnly(True)
        self.edl_preview_plainTextEdit.setObjectName(_fromUtf8("edl_preview_plainTextEdit"))
        self.verticalLayout.addWidget(self.edl_preview_plainTextEdit)
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        self.send_pushButton = QtGui.QPushButton(Dialog)
        self.send_pushButton.setObjectName(_fromUtf8("send_pushButton"))
        self.horizontalLayout_2.addWidget(self.send_pushButton)
        self.verticalLayout.addLayout(self.horizontalLayout_2)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)
        Dialog.setTabOrder(self.media_files_path_lineEdit, self.edl_preview_plainTextEdit)
        Dialog.setTabOrder(self.edl_preview_plainTextEdit, self.send_pushButton)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(_translate("Dialog", "EDL Importer", None))
        self.label.setText(_translate("Dialog", "EDL Path", None))
        self.label_2.setText(_translate("Dialog", "AVID Media Files Path", None))
        self.send_pushButton.setText(_translate("Dialog", "Send To AVID", None))

