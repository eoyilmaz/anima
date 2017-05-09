# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_files\image_format_dialog.ui'
#
# Created: Tue May 09 09:41:16 2017
#      by: PyQt4 UI code generator 4.9.1
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName(_fromUtf8("Dialog"))
        Dialog.resize(328, 184)
        self.verticalLayout = QtGui.QVBoxLayout(Dialog)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.dialog_label = QtGui.QLabel(Dialog)
        self.dialog_label.setStyleSheet(_fromUtf8("color: rgb(71, 143, 202);\n"
"font: 18pt;"))
        self.dialog_label.setObjectName(_fromUtf8("dialog_label"))
        self.verticalLayout.addWidget(self.dialog_label)
        self.line = QtGui.QFrame(Dialog)
        self.line.setFrameShape(QtGui.QFrame.HLine)
        self.line.setFrameShadow(QtGui.QFrame.Sunken)
        self.line.setObjectName(_fromUtf8("line"))
        self.verticalLayout.addWidget(self.line)
        self.formLayout = QtGui.QFormLayout()
        self.formLayout.setLabelAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.formLayout.setObjectName(_fromUtf8("formLayout"))
        self.name_fields_verticalLayout = QtGui.QVBoxLayout()
        self.name_fields_verticalLayout.setObjectName(_fromUtf8("name_fields_verticalLayout"))
        self.name_validator_label = QtGui.QLabel(Dialog)
        self.name_validator_label.setStyleSheet(_fromUtf8("color: rgb(255, 0, 0);"))
        self.name_validator_label.setObjectName(_fromUtf8("name_validator_label"))
        self.name_fields_verticalLayout.addWidget(self.name_validator_label)
        self.formLayout.setLayout(0, QtGui.QFormLayout.FieldRole, self.name_fields_verticalLayout)
        self.width_height_Label = QtGui.QLabel(Dialog)
        self.width_height_Label.setObjectName(_fromUtf8("width_height_Label"))
        self.formLayout.setWidget(1, QtGui.QFormLayout.LabelRole, self.width_height_Label)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.width_spinBox = QtGui.QSpinBox(Dialog)
        self.width_spinBox.setMaximum(99999)
        self.width_spinBox.setObjectName(_fromUtf8("width_spinBox"))
        self.horizontalLayout.addWidget(self.width_spinBox)
        self.label = QtGui.QLabel(Dialog)
        self.label.setObjectName(_fromUtf8("label"))
        self.horizontalLayout.addWidget(self.label)
        self.height_spinBox = QtGui.QSpinBox(Dialog)
        self.height_spinBox.setMaximum(99999)
        self.height_spinBox.setObjectName(_fromUtf8("height_spinBox"))
        self.horizontalLayout.addWidget(self.height_spinBox)
        self.horizontalLayout.setStretch(0, 1)
        self.horizontalLayout.setStretch(2, 1)
        self.formLayout.setLayout(1, QtGui.QFormLayout.FieldRole, self.horizontalLayout)
        self.pixel_aspect_label = QtGui.QLabel(Dialog)
        self.pixel_aspect_label.setObjectName(_fromUtf8("pixel_aspect_label"))
        self.formLayout.setWidget(2, QtGui.QFormLayout.LabelRole, self.pixel_aspect_label)
        self.pixel_aspect_doubleSpinBox = QtGui.QDoubleSpinBox(Dialog)
        self.pixel_aspect_doubleSpinBox.setProperty("value", 1.0)
        self.pixel_aspect_doubleSpinBox.setObjectName(_fromUtf8("pixel_aspect_doubleSpinBox"))
        self.formLayout.setWidget(2, QtGui.QFormLayout.FieldRole, self.pixel_aspect_doubleSpinBox)
        self.name_label = QtGui.QLabel(Dialog)
        self.name_label.setObjectName(_fromUtf8("name_label"))
        self.formLayout.setWidget(0, QtGui.QFormLayout.LabelRole, self.name_label)
        self.verticalLayout.addLayout(self.formLayout)
        self.buttonBox = QtGui.QDialogButtonBox(Dialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.verticalLayout.addWidget(self.buttonBox)
        self.verticalLayout.setStretch(2, 1)

        self.retranslateUi(Dialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), Dialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), Dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QtGui.QApplication.translate("Dialog", "Dialog", None, QtGui.QApplication.UnicodeUTF8))
        self.dialog_label.setText(QtGui.QApplication.translate("Dialog", "Create Image Format", None, QtGui.QApplication.UnicodeUTF8))
        self.name_validator_label.setText(QtGui.QApplication.translate("Dialog", "Validator Message", None, QtGui.QApplication.UnicodeUTF8))
        self.width_height_Label.setText(QtGui.QApplication.translate("Dialog", "Width x Height", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("Dialog", "x", None, QtGui.QApplication.UnicodeUTF8))
        self.pixel_aspect_label.setText(QtGui.QApplication.translate("Dialog", "Pixel Aspect", None, QtGui.QApplication.UnicodeUTF8))
        self.name_label.setText(QtGui.QApplication.translate("Dialog", "Name", None, QtGui.QApplication.UnicodeUTF8))

