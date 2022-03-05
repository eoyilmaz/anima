# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file './ui_files/reference_editor.ui'
#
# Created: Fri Sep 27 16:46:40 2013
#      by: pyside-uic 0.2.14 running on PySide 1.1.2
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(853, 608)
        self.verticalLayout = QtGui.QVBoxLayout(Dialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.verticalLayout_3 = QtGui.QVBoxLayout()
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.use_selection_checkBox = QtGui.QCheckBox(Dialog)
        self.use_selection_checkBox.setObjectName("use_selection_checkBox")
        self.verticalLayout_3.addWidget(self.use_selection_checkBox)
        self.tabWidget = QtGui.QTabWidget(Dialog)
        self.tabWidget.setObjectName("tabWidget")
        self.references_tab = QtGui.QWidget()
        self.references_tab.setObjectName("references_tab")
        self.horizontalLayout = QtGui.QHBoxLayout(self.references_tab)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.references_treeView = QtGui.QTreeView(self.references_tab)
        self.references_treeView.setObjectName("references_treeView")
        self.horizontalLayout.addWidget(self.references_treeView)
        self.frame = QtGui.QFrame(self.references_tab)
        self.frame.setFrameShape(QtGui.QFrame.Box)
        self.frame.setFrameShadow(QtGui.QFrame.Sunken)
        self.frame.setObjectName("frame")
        self.verticalLayout_2 = QtGui.QVBoxLayout(self.frame)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.label = QtGui.QLabel(self.frame)
        self.label.setObjectName("label")
        self.verticalLayout_2.addWidget(self.label)
        self.textEdit = QtGui.QTextEdit(self.frame)
        self.textEdit.setObjectName("textEdit")
        self.verticalLayout_2.addWidget(self.textEdit)
        self.pushButton = QtGui.QPushButton(self.frame)
        self.pushButton.setObjectName("pushButton")
        self.verticalLayout_2.addWidget(self.pushButton)
        self.pushButton_2 = QtGui.QPushButton(self.frame)
        self.pushButton_2.setObjectName("pushButton_2")
        self.verticalLayout_2.addWidget(self.pushButton_2)
        self.pushButton_3 = QtGui.QPushButton(self.frame)
        self.pushButton_3.setObjectName("pushButton_3")
        self.verticalLayout_2.addWidget(self.pushButton_3)
        self.horizontalLayout.addWidget(self.frame)
        self.horizontalLayout.setStretch(0, 1)
        self.tabWidget.addTab(self.references_tab, "")
        self.textures_tab = QtGui.QWidget()
        self.textures_tab.setObjectName("textures_tab")
        self.tabWidget.addTab(self.textures_tab, "")
        self.animation_cache_tab = QtGui.QWidget()
        self.animation_cache_tab.setObjectName("animation_cache_tab")
        self.tabWidget.addTab(self.animation_cache_tab, "")
        self.verticalLayout_3.addWidget(self.tabWidget)
        self.verticalLayout.addLayout(self.verticalLayout_3)
        self.buttonBox = QtGui.QDialogButtonBox(Dialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(
            QtGui.QDialogButtonBox.Cancel | QtGui.QDialogButtonBox.Ok
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
            QtGui.QApplication.translate(
                "Dialog", "Reference Editor", None, QtGui.QApplication.UnicodeUTF8
            )
        )
        self.use_selection_checkBox.setText(
            QtGui.QApplication.translate(
                "Dialog", "Use Selection", None, QtGui.QApplication.UnicodeUTF8
            )
        )
        self.label.setText(
            QtGui.QApplication.translate(
                "Dialog", "Ref Info", None, QtGui.QApplication.UnicodeUTF8
            )
        )
        self.pushButton.setText(
            QtGui.QApplication.translate(
                "Dialog", "Create Ticket", None, QtGui.QApplication.UnicodeUTF8
            )
        )
        self.pushButton_2.setText(
            QtGui.QApplication.translate(
                "Dialog",
                "Update To Latest Version",
                None,
                QtGui.QApplication.UnicodeUTF8,
            )
        )
        self.pushButton_3.setText(
            QtGui.QApplication.translate(
                "Dialog",
                "Save Edits as New Version",
                None,
                QtGui.QApplication.UnicodeUTF8,
            )
        )
        self.tabWidget.setTabText(
            self.tabWidget.indexOf(self.references_tab),
            QtGui.QApplication.translate(
                "Dialog", "References", None, QtGui.QApplication.UnicodeUTF8
            ),
        )
        self.tabWidget.setTabText(
            self.tabWidget.indexOf(self.textures_tab),
            QtGui.QApplication.translate(
                "Dialog", "Textures", None, QtGui.QApplication.UnicodeUTF8
            ),
        )
        self.tabWidget.setTabText(
            self.tabWidget.indexOf(self.animation_cache_tab),
            QtGui.QApplication.translate(
                "Dialog", "Animation Caches", None, QtGui.QApplication.UnicodeUTF8
            ),
        )
