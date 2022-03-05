# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_files\version_updater.ui'
#
# Created: Thu Nov 10 15:32:30 2016
#      by: pyside2-uic  running on PySide2 2.0.0~alpha0
#
# WARNING! All changes made in this file will be lost!

from PySide2 import QtCore, QtGui, QtWidgets


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.setWindowModality(QtCore.Qt.ApplicationModal)
        Dialog.resize(1304, 753)
        self.verticalLayout = QtWidgets.QVBoxLayout(Dialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.label = QtWidgets.QLabel(Dialog)
        self.label.setObjectName("label")
        self.verticalLayout.addWidget(self.label)
        self.versions_treeView = QtWidgets.QTreeView(Dialog)
        self.versions_treeView.setObjectName("versions_treeView")
        self.verticalLayout.addWidget(self.versions_treeView)
        self.horizontalWidget = QtWidgets.QWidget(Dialog)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.horizontalWidget.sizePolicy().hasHeightForWidth()
        )
        self.horizontalWidget.setSizePolicy(sizePolicy)
        self.horizontalWidget.setObjectName("horizontalWidget")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.horizontalWidget)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        spacerItem = QtWidgets.QSpacerItem(
            40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum
        )
        self.horizontalLayout.addItem(spacerItem)
        self.selectNone_pushButton = QtWidgets.QPushButton(self.horizontalWidget)
        self.selectNone_pushButton.setObjectName("selectNone_pushButton")
        self.horizontalLayout.addWidget(self.selectNone_pushButton)
        self.selectAll_pushButton = QtWidgets.QPushButton(self.horizontalWidget)
        self.selectAll_pushButton.setObjectName("selectAll_pushButton")
        self.horizontalLayout.addWidget(self.selectAll_pushButton)
        self.update_pushButton = QtWidgets.QPushButton(self.horizontalWidget)
        self.update_pushButton.setObjectName("update_pushButton")
        self.horizontalLayout.addWidget(self.update_pushButton)
        self.cancel_pushButton = QtWidgets.QPushButton(self.horizontalWidget)
        self.cancel_pushButton.setObjectName("cancel_pushButton")
        self.horizontalLayout.addWidget(self.cancel_pushButton)
        self.verticalLayout.addWidget(self.horizontalWidget)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(
            QtWidgets.QApplication.translate("Dialog", "Version Updater", None, -1)
        )
        self.label.setText(
            QtWidgets.QApplication.translate(
                "Dialog",
                '<html><head/><body><p><span style=" color:#c00000;">Red Versions need update,</span><span style=" color:#00c000;">Greens are OK</span>, check the Versions that you want to trigger an update.</p></body></html>',
                None,
                -1,
            )
        )
        self.selectNone_pushButton.setText(
            QtWidgets.QApplication.translate("Dialog", "Select None", None, -1)
        )
        self.selectAll_pushButton.setText(
            QtWidgets.QApplication.translate("Dialog", "Select All", None, -1)
        )
        self.update_pushButton.setText(
            QtWidgets.QApplication.translate("Dialog", "Update", None, -1)
        )
        self.cancel_pushButton.setText(
            QtWidgets.QApplication.translate("Dialog", "Cancel", None, -1)
        )
