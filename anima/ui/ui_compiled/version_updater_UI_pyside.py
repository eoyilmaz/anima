# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file './ui_files/version_updater.ui'
#
# Created: Tue May  6 17:38:32 2014
#      by: pyside-uic 0.2.13 running on PySide 1.1.0
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.setWindowModality(QtCore.Qt.ApplicationModal)
        Dialog.resize(1304, 753)
        self.verticalLayout = QtGui.QVBoxLayout(Dialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.label = QtGui.QLabel(Dialog)
        self.label.setObjectName("label")
        self.verticalLayout.addWidget(self.label)
        self.versions_treeView = QtGui.QTreeView(Dialog)
        self.versions_treeView.setObjectName("versions_treeView")
        self.verticalLayout.addWidget(self.versions_treeView)
        self.horizontalWidget = QtGui.QWidget(Dialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.horizontalWidget.sizePolicy().hasHeightForWidth())
        self.horizontalWidget.setSizePolicy(sizePolicy)
        self.horizontalWidget.setObjectName("horizontalWidget")
        self.horizontalLayout = QtGui.QHBoxLayout(self.horizontalWidget)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.selectNone_pushButton = QtGui.QPushButton(self.horizontalWidget)
        self.selectNone_pushButton.setObjectName("selectNone_pushButton")
        self.horizontalLayout.addWidget(self.selectNone_pushButton)
        self.selectAll_pushButton = QtGui.QPushButton(self.horizontalWidget)
        self.selectAll_pushButton.setObjectName("selectAll_pushButton")
        self.horizontalLayout.addWidget(self.selectAll_pushButton)
        self.update_pushButton = QtGui.QPushButton(self.horizontalWidget)
        self.update_pushButton.setObjectName("update_pushButton")
        self.horizontalLayout.addWidget(self.update_pushButton)
        self.cancel_pushButton = QtGui.QPushButton(self.horizontalWidget)
        self.cancel_pushButton.setObjectName("cancel_pushButton")
        self.horizontalLayout.addWidget(self.cancel_pushButton)
        self.verticalLayout.addWidget(self.horizontalWidget)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QtGui.QApplication.translate("Dialog", "Version Updater", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("Dialog", "<html><head/><body><p><span style=\" color:#c00000;\">Red Versions need update,</span><span style=\" color:#00c000;\">Greens are OK</span>, check the Versions that you want to trigger an update.</p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
        self.selectNone_pushButton.setText(QtGui.QApplication.translate("Dialog", "Select None", None, QtGui.QApplication.UnicodeUTF8))
        self.selectAll_pushButton.setText(QtGui.QApplication.translate("Dialog", "Select All", None, QtGui.QApplication.UnicodeUTF8))
        self.update_pushButton.setText(QtGui.QApplication.translate("Dialog", "Update", None, QtGui.QApplication.UnicodeUTF8))
        self.cancel_pushButton.setText(QtGui.QApplication.translate("Dialog", "Cancel", None, QtGui.QApplication.UnicodeUTF8))

