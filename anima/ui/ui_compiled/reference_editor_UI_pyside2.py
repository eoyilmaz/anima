# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_files\reference_editor.ui'
#
# Created: Thu Nov 10 15:32:30 2016
#      by: pyside2-uic  running on PySide2 2.0.0~alpha0
#
# WARNING! All changes made in this file will be lost!

from PySide2 import QtCore, QtGui, QtWidgets


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(853, 608)
        self.verticalLayout = QtWidgets.QVBoxLayout(Dialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout()
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.use_selection_checkBox = QtWidgets.QCheckBox(Dialog)
        self.use_selection_checkBox.setObjectName("use_selection_checkBox")
        self.verticalLayout_3.addWidget(self.use_selection_checkBox)
        self.tabWidget = QtWidgets.QTabWidget(Dialog)
        self.tabWidget.setObjectName("tabWidget")
        self.references_tab = QtWidgets.QWidget()
        self.references_tab.setObjectName("references_tab")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.references_tab)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.references_treeView = QtWidgets.QTreeView(self.references_tab)
        self.references_treeView.setObjectName("references_treeView")
        self.horizontalLayout.addWidget(self.references_treeView)
        self.frame = QtWidgets.QFrame(self.references_tab)
        self.frame.setFrameShape(QtWidgets.QFrame.Box)
        self.frame.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.frame.setObjectName("frame")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.frame)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.label = QtWidgets.QLabel(self.frame)
        self.label.setObjectName("label")
        self.verticalLayout_2.addWidget(self.label)
        self.textEdit = QtWidgets.QTextEdit(self.frame)
        self.textEdit.setObjectName("textEdit")
        self.verticalLayout_2.addWidget(self.textEdit)
        self.pushButton = QtWidgets.QPushButton(self.frame)
        self.pushButton.setObjectName("pushButton")
        self.verticalLayout_2.addWidget(self.pushButton)
        self.pushButton_2 = QtWidgets.QPushButton(self.frame)
        self.pushButton_2.setObjectName("pushButton_2")
        self.verticalLayout_2.addWidget(self.pushButton_2)
        self.pushButton_3 = QtWidgets.QPushButton(self.frame)
        self.pushButton_3.setObjectName("pushButton_3")
        self.verticalLayout_2.addWidget(self.pushButton_3)
        self.horizontalLayout.addWidget(self.frame)
        self.horizontalLayout.setStretch(0, 1)
        self.tabWidget.addTab(self.references_tab, "")
        self.textures_tab = QtWidgets.QWidget()
        self.textures_tab.setObjectName("textures_tab")
        self.tabWidget.addTab(self.textures_tab, "")
        self.animation_cache_tab = QtWidgets.QWidget()
        self.animation_cache_tab.setObjectName("animation_cache_tab")
        self.tabWidget.addTab(self.animation_cache_tab, "")
        self.verticalLayout_3.addWidget(self.tabWidget)
        self.verticalLayout.addLayout(self.verticalLayout_3)
        self.buttonBox = QtWidgets.QDialogButtonBox(Dialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(
            QtWidgets.QDialogButtonBox.Cancel | QtWidgets.QDialogButtonBox.Ok
        )
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(Dialog)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QObject.connect(
            self.buttonBox, QtCore.SIGNAL("accepted()"), Dialog.accept
        )
        QtCore.QObject.connect(
            self.buttonBox, QtCore.SIGNAL("rejected()"), Dialog.reject
        )
        QtCore.QMetaObject.connectSlotsByName(Dialog)
        Dialog.setTabOrder(self.use_selection_checkBox, self.tabWidget)
        Dialog.setTabOrder(self.tabWidget, self.buttonBox)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(
            QtWidgets.QApplication.translate("Dialog", "Reference Editor", None, -1)
        )
        self.use_selection_checkBox.setText(
            QtWidgets.QApplication.translate("Dialog", "Use Selection", None, -1)
        )
        self.label.setText(
            QtWidgets.QApplication.translate("Dialog", "Ref Info", None, -1)
        )
        self.pushButton.setText(
            QtWidgets.QApplication.translate("Dialog", "Create Ticket", None, -1)
        )
        self.pushButton_2.setText(
            QtWidgets.QApplication.translate(
                "Dialog", "Update To Latest Version", None, -1
            )
        )
        self.pushButton_3.setText(
            QtWidgets.QApplication.translate(
                "Dialog", "Save Edits as New Version", None, -1
            )
        )
        self.tabWidget.setTabText(
            self.tabWidget.indexOf(self.references_tab),
            QtWidgets.QApplication.translate("Dialog", "References", None, -1),
        )
        self.tabWidget.setTabText(
            self.tabWidget.indexOf(self.textures_tab),
            QtWidgets.QApplication.translate("Dialog", "Textures", None, -1),
        )
        self.tabWidget.setTabText(
            self.tabWidget.indexOf(self.animation_cache_tab),
            QtWidgets.QApplication.translate("Dialog", "Animation Caches", None, -1),
        )
