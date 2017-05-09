# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_files\image_format_dialog.ui'
#
# Created: Tue May 09 09:41:16 2017
#      by: pyside-uic 0.2.14 running on PySide 1.1.1
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(328, 184)
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
        self.name_fields_verticalLayout = QtGui.QVBoxLayout()
        self.name_fields_verticalLayout.setObjectName("name_fields_verticalLayout")
        self.name_validator_label = QtGui.QLabel(Dialog)
        self.name_validator_label.setStyleSheet("color: rgb(255, 0, 0);")
        self.name_validator_label.setObjectName("name_validator_label")
        self.name_fields_verticalLayout.addWidget(self.name_validator_label)
        self.formLayout.setLayout(0, QtGui.QFormLayout.FieldRole, self.name_fields_verticalLayout)
        self.width_height_Label = QtGui.QLabel(Dialog)
        self.width_height_Label.setObjectName("width_height_Label")
        self.formLayout.setWidget(1, QtGui.QFormLayout.LabelRole, self.width_height_Label)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.width_spinBox = QtGui.QSpinBox(Dialog)
        self.width_spinBox.setMaximum(99999)
        self.width_spinBox.setObjectName("width_spinBox")
        self.horizontalLayout.addWidget(self.width_spinBox)
        self.label = QtGui.QLabel(Dialog)
        self.label.setObjectName("label")
        self.horizontalLayout.addWidget(self.label)
        self.height_spinBox = QtGui.QSpinBox(Dialog)
        self.height_spinBox.setMaximum(99999)
        self.height_spinBox.setObjectName("height_spinBox")
        self.horizontalLayout.addWidget(self.height_spinBox)
        self.horizontalLayout.setStretch(0, 1)
        self.horizontalLayout.setStretch(2, 1)
        self.formLayout.setLayout(1, QtGui.QFormLayout.FieldRole, self.horizontalLayout)
        self.pixel_aspect_label = QtGui.QLabel(Dialog)
        self.pixel_aspect_label.setObjectName("pixel_aspect_label")
        self.formLayout.setWidget(2, QtGui.QFormLayout.LabelRole, self.pixel_aspect_label)
        self.pixel_aspect_doubleSpinBox = QtGui.QDoubleSpinBox(Dialog)
        self.pixel_aspect_doubleSpinBox.setProperty("value", 1.0)
        self.pixel_aspect_doubleSpinBox.setObjectName("pixel_aspect_doubleSpinBox")
        self.formLayout.setWidget(2, QtGui.QFormLayout.FieldRole, self.pixel_aspect_doubleSpinBox)
        self.name_label = QtGui.QLabel(Dialog)
        self.name_label.setObjectName("name_label")
        self.formLayout.setWidget(0, QtGui.QFormLayout.LabelRole, self.name_label)
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
        self.dialog_label.setText(QtGui.QApplication.translate("Dialog", "Create Image Format", None, QtGui.QApplication.UnicodeUTF8))
        self.name_validator_label.setText(QtGui.QApplication.translate("Dialog", "Validator Message", None, QtGui.QApplication.UnicodeUTF8))
        self.width_height_Label.setText(QtGui.QApplication.translate("Dialog", "Width x Height", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("Dialog", "x", None, QtGui.QApplication.UnicodeUTF8))
        self.pixel_aspect_label.setText(QtGui.QApplication.translate("Dialog", "Pixel Aspect", None, QtGui.QApplication.UnicodeUTF8))
        self.name_label.setText(QtGui.QApplication.translate("Dialog", "Name", None, QtGui.QApplication.UnicodeUTF8))

