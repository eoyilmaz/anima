# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file './ui_files/reference_editor.ui'
#
# Created: Fri Sep 27 16:46:41 2013
#      by: PyQt4 UI code generator 4.10.1
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
        Dialog.resize(853, 608)
        self.verticalLayout = QtGui.QVBoxLayout(Dialog)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.verticalLayout_3 = QtGui.QVBoxLayout()
        self.verticalLayout_3.setObjectName(_fromUtf8("verticalLayout_3"))
        self.use_selection_checkBox = QtGui.QCheckBox(Dialog)
        self.use_selection_checkBox.setObjectName(_fromUtf8("use_selection_checkBox"))
        self.verticalLayout_3.addWidget(self.use_selection_checkBox)
        self.tabWidget = QtGui.QTabWidget(Dialog)
        self.tabWidget.setObjectName(_fromUtf8("tabWidget"))
        self.references_tab = QtGui.QWidget()
        self.references_tab.setObjectName(_fromUtf8("references_tab"))
        self.horizontalLayout = QtGui.QHBoxLayout(self.references_tab)
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.references_treeView = QtGui.QTreeView(self.references_tab)
        self.references_treeView.setObjectName(_fromUtf8("references_treeView"))
        self.horizontalLayout.addWidget(self.references_treeView)
        self.frame = QtGui.QFrame(self.references_tab)
        self.frame.setFrameShape(QtGui.QFrame.Box)
        self.frame.setFrameShadow(QtGui.QFrame.Sunken)
        self.frame.setObjectName(_fromUtf8("frame"))
        self.verticalLayout_2 = QtGui.QVBoxLayout(self.frame)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.label = QtGui.QLabel(self.frame)
        self.label.setObjectName(_fromUtf8("label"))
        self.verticalLayout_2.addWidget(self.label)
        self.textEdit = QtGui.QTextEdit(self.frame)
        self.textEdit.setObjectName(_fromUtf8("textEdit"))
        self.verticalLayout_2.addWidget(self.textEdit)
        self.pushButton = QtGui.QPushButton(self.frame)
        self.pushButton.setObjectName(_fromUtf8("pushButton"))
        self.verticalLayout_2.addWidget(self.pushButton)
        self.pushButton_2 = QtGui.QPushButton(self.frame)
        self.pushButton_2.setObjectName(_fromUtf8("pushButton_2"))
        self.verticalLayout_2.addWidget(self.pushButton_2)
        self.pushButton_3 = QtGui.QPushButton(self.frame)
        self.pushButton_3.setObjectName(_fromUtf8("pushButton_3"))
        self.verticalLayout_2.addWidget(self.pushButton_3)
        self.horizontalLayout.addWidget(self.frame)
        self.horizontalLayout.setStretch(0, 1)
        self.tabWidget.addTab(self.references_tab, _fromUtf8(""))
        self.textures_tab = QtGui.QWidget()
        self.textures_tab.setObjectName(_fromUtf8("textures_tab"))
        self.tabWidget.addTab(self.textures_tab, _fromUtf8(""))
        self.animation_cache_tab = QtGui.QWidget()
        self.animation_cache_tab.setObjectName(_fromUtf8("animation_cache_tab"))
        self.tabWidget.addTab(self.animation_cache_tab, _fromUtf8(""))
        self.verticalLayout_3.addWidget(self.tabWidget)
        self.verticalLayout.addLayout(self.verticalLayout_3)
        self.buttonBox = QtGui.QDialogButtonBox(Dialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(Dialog)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), Dialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), Dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(Dialog)
        Dialog.setTabOrder(self.use_selection_checkBox, self.tabWidget)
        Dialog.setTabOrder(self.tabWidget, self.buttonBox)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(_translate("Dialog", "Reference Editor", None))
        self.use_selection_checkBox.setText(_translate("Dialog", "Use Selection", None))
        self.label.setText(_translate("Dialog", "Ref Info", None))
        self.pushButton.setText(_translate("Dialog", "Create Ticket", None))
        self.pushButton_2.setText(_translate("Dialog", "Update To Latest Version", None))
        self.pushButton_3.setText(_translate("Dialog", "Save Edits as New Version", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.references_tab), _translate("Dialog", "References", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.textures_tab), _translate("Dialog", "Textures", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.animation_cache_tab), _translate("Dialog", "Animation Caches", None))

