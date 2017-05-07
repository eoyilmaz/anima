# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'C:\Users\eoyilmaz\Documents\development\anima\anima\anima\ui\ui_files\image_format_dialog.ui'
#
# Created: Sun May 07 12:39:28 2017
#      by: pyside2-uic  running on PySide2 2.0.0~alpha0
#
# WARNING! All changes made in this file will be lost!

from PySide2 import QtCore, QtGui, QtWidgets

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(328, 175)
        self.verticalLayout = QtWidgets.QVBoxLayout(Dialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.dialog_label = QtWidgets.QLabel(Dialog)
        self.dialog_label.setStyleSheet("color: rgb(71, 143, 202);\n"
"font: 18pt;")
        self.dialog_label.setObjectName("dialog_label")
        self.verticalLayout.addWidget(self.dialog_label)
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
        self.width_height_Label = QtWidgets.QLabel(Dialog)
        self.width_height_Label.setObjectName("width_height_Label")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.width_height_Label)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.width_spinBox = QtWidgets.QSpinBox(Dialog)
        self.width_spinBox.setMaximum(99999)
        self.width_spinBox.setObjectName("width_spinBox")
        self.horizontalLayout.addWidget(self.width_spinBox)
        self.label = QtWidgets.QLabel(Dialog)
        self.label.setObjectName("label")
        self.horizontalLayout.addWidget(self.label)
        self.height_spinBox = QtWidgets.QSpinBox(Dialog)
        self.height_spinBox.setMaximum(99999)
        self.height_spinBox.setObjectName("height_spinBox")
        self.horizontalLayout.addWidget(self.height_spinBox)
        self.horizontalLayout.setStretch(0, 1)
        self.horizontalLayout.setStretch(2, 1)
        self.formLayout.setLayout(1, QtWidgets.QFormLayout.FieldRole, self.horizontalLayout)
        self.pixel_aspect_label = QtWidgets.QLabel(Dialog)
        self.pixel_aspect_label.setObjectName("pixel_aspect_label")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.pixel_aspect_label)
        self.pixel_aspect_doubleSpinBox = QtWidgets.QDoubleSpinBox(Dialog)
        self.pixel_aspect_doubleSpinBox.setProperty("value", 1.0)
        self.pixel_aspect_doubleSpinBox.setObjectName("pixel_aspect_doubleSpinBox")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.FieldRole, self.pixel_aspect_doubleSpinBox)
        self.verticalLayout.addLayout(self.formLayout)
        self.buttonBox = QtWidgets.QDialogButtonBox(Dialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)
        self.verticalLayout.setStretch(1, 1)

        self.retranslateUi(Dialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("accepted()"), Dialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("rejected()"), Dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QtWidgets.QApplication.translate("Dialog", "Dialog", None, -1))
        self.dialog_label.setText(QtWidgets.QApplication.translate("Dialog", "Create Image Format", None, -1))
        self.name_label.setText(QtWidgets.QApplication.translate("Dialog", "Name", None, -1))
        self.name_validator_label.setText(QtWidgets.QApplication.translate("Dialog", "Validator Message", None, -1))
        self.width_height_Label.setText(QtWidgets.QApplication.translate("Dialog", "Width x Height", None, -1))
        self.label.setText(QtWidgets.QApplication.translate("Dialog", "x", None, -1))
        self.pixel_aspect_label.setText(QtWidgets.QApplication.translate("Dialog", "Pixel Aspect", None, -1))

