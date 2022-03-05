# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_files\anima_manager.ui'
#
# Created: Thu May 04 11:01:53 2017
#      by: PyQt4 UI code generator 4.9.1
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName(_fromUtf8("MainWindow"))
        MainWindow.resize(1108, 769)
        self.centralwidget = QtGui.QWidget(MainWindow)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.horizontalLayout = QtGui.QHBoxLayout(self.centralwidget)
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.verticalLayout_2 = QtGui.QVBoxLayout()
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.horizontalLayout.addLayout(self.verticalLayout_2)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtGui.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1108, 21))
        self.menubar.setObjectName(_fromUtf8("menubar"))
        self.menuFile = QtGui.QMenu(self.menubar)
        self.menuFile.setObjectName(_fromUtf8("menuFile"))
        self.menuEdit = QtGui.QMenu(self.menubar)
        self.menuEdit.setObjectName(_fromUtf8("menuEdit"))
        self.menuHelp = QtGui.QMenu(self.menubar)
        self.menuHelp.setObjectName(_fromUtf8("menuHelp"))
        self.menuView = QtGui.QMenu(self.menubar)
        self.menuView.setObjectName(_fromUtf8("menuView"))
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtGui.QStatusBar(MainWindow)
        self.statusbar.setObjectName(_fromUtf8("statusbar"))
        MainWindow.setStatusBar(self.statusbar)
        self.dockWidget = QtGui.QDockWidget(MainWindow)
        self.dockWidget.setObjectName(_fromUtf8("dockWidget"))
        self.dockWidgetContents = QtGui.QWidget()
        self.dockWidgetContents.setObjectName(_fromUtf8("dockWidgetContents"))
        self.verticalLayout = QtGui.QVBoxLayout(self.dockWidgetContents)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.pushButton_2 = QtGui.QPushButton(self.dockWidgetContents)
        self.pushButton_2.setObjectName(_fromUtf8("pushButton_2"))
        self.verticalLayout.addWidget(self.pushButton_2)
        self.pushButton_3 = QtGui.QPushButton(self.dockWidgetContents)
        self.pushButton_3.setObjectName(_fromUtf8("pushButton_3"))
        self.verticalLayout.addWidget(self.pushButton_3)
        self.pushButton = QtGui.QPushButton(self.dockWidgetContents)
        self.pushButton.setObjectName(_fromUtf8("pushButton"))
        self.verticalLayout.addWidget(self.pushButton)
        spacerItem = QtGui.QSpacerItem(
            20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding
        )
        self.verticalLayout.addItem(spacerItem)
        self.dockWidget.setWidget(self.dockWidgetContents)
        MainWindow.addDockWidget(QtCore.Qt.DockWidgetArea(1), self.dockWidget)
        self.actionConnect_To_Server = QtGui.QAction(MainWindow)
        self.actionConnect_To_Server.setObjectName(_fromUtf8("actionConnect_To_Server"))
        self.actionAbout_AnimaMan = QtGui.QAction(MainWindow)
        self.actionAbout_AnimaMan.setObjectName(_fromUtf8("actionAbout_AnimaMan"))
        self.actionLogin = QtGui.QAction(MainWindow)
        self.actionLogin.setObjectName(_fromUtf8("actionLogin"))
        self.actionLogout = QtGui.QAction(MainWindow)
        self.actionLogout.setObjectName(_fromUtf8("actionLogout"))
        self.actionExit = QtGui.QAction(MainWindow)
        self.actionExit.setObjectName(_fromUtf8("actionExit"))
        self.actionUndo = QtGui.QAction(MainWindow)
        self.actionUndo.setObjectName(_fromUtf8("actionUndo"))
        self.actionRedo = QtGui.QAction(MainWindow)
        self.actionRedo.setObjectName(_fromUtf8("actionRedo"))
        self.actionCopy = QtGui.QAction(MainWindow)
        self.actionCopy.setObjectName(_fromUtf8("actionCopy"))
        self.actionPaste = QtGui.QAction(MainWindow)
        self.actionPaste.setObjectName(_fromUtf8("actionPaste"))
        self.actionFind = QtGui.QAction(MainWindow)
        self.actionFind.setObjectName(_fromUtf8("actionFind"))
        self.actionHelp = QtGui.QAction(MainWindow)
        self.actionHelp.setObjectName(_fromUtf8("actionHelp"))
        self.menuFile.addAction(self.actionConnect_To_Server)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionLogin)
        self.menuFile.addAction(self.actionLogout)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionExit)
        self.menuEdit.addAction(self.actionUndo)
        self.menuEdit.addAction(self.actionRedo)
        self.menuEdit.addSeparator()
        self.menuEdit.addAction(self.actionCopy)
        self.menuEdit.addAction(self.actionPaste)
        self.menuEdit.addSeparator()
        self.menuEdit.addAction(self.actionFind)
        self.menuHelp.addAction(self.actionHelp)
        self.menuHelp.addSeparator()
        self.menuHelp.addAction(self.actionAbout_AnimaMan)
        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuEdit.menuAction())
        self.menubar.addAction(self.menuView.menuAction())
        self.menubar.addAction(self.menuHelp.menuAction())

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(
            QtGui.QApplication.translate(
                "MainWindow", "Anima Manager", None, QtGui.QApplication.UnicodeUTF8
            )
        )
        self.menuFile.setTitle(
            QtGui.QApplication.translate(
                "MainWindow", "File", None, QtGui.QApplication.UnicodeUTF8
            )
        )
        self.menuEdit.setTitle(
            QtGui.QApplication.translate(
                "MainWindow", "Edit", None, QtGui.QApplication.UnicodeUTF8
            )
        )
        self.menuHelp.setTitle(
            QtGui.QApplication.translate(
                "MainWindow", "Help", None, QtGui.QApplication.UnicodeUTF8
            )
        )
        self.menuView.setTitle(
            QtGui.QApplication.translate(
                "MainWindow", "View", None, QtGui.QApplication.UnicodeUTF8
            )
        )
        self.pushButton_2.setText(
            QtGui.QApplication.translate(
                "MainWindow", "My Projects", None, QtGui.QApplication.UnicodeUTF8
            )
        )
        self.pushButton_3.setText(
            QtGui.QApplication.translate(
                "MainWindow", "My Tasks", None, QtGui.QApplication.UnicodeUTF8
            )
        )
        self.pushButton.setText(
            QtGui.QApplication.translate(
                "MainWindow", "My Vacations", None, QtGui.QApplication.UnicodeUTF8
            )
        )
        self.actionConnect_To_Server.setText(
            QtGui.QApplication.translate(
                "MainWindow",
                "Connect To Server...",
                None,
                QtGui.QApplication.UnicodeUTF8,
            )
        )
        self.actionAbout_AnimaMan.setText(
            QtGui.QApplication.translate(
                "MainWindow", "About AnimaMan ...", None, QtGui.QApplication.UnicodeUTF8
            )
        )
        self.actionLogin.setText(
            QtGui.QApplication.translate(
                "MainWindow", "Login...", None, QtGui.QApplication.UnicodeUTF8
            )
        )
        self.actionLogout.setText(
            QtGui.QApplication.translate(
                "MainWindow", "Logout", None, QtGui.QApplication.UnicodeUTF8
            )
        )
        self.actionExit.setText(
            QtGui.QApplication.translate(
                "MainWindow", "Exit", None, QtGui.QApplication.UnicodeUTF8
            )
        )
        self.actionUndo.setText(
            QtGui.QApplication.translate(
                "MainWindow", "Undo", None, QtGui.QApplication.UnicodeUTF8
            )
        )
        self.actionRedo.setText(
            QtGui.QApplication.translate(
                "MainWindow", "Redo", None, QtGui.QApplication.UnicodeUTF8
            )
        )
        self.actionCopy.setText(
            QtGui.QApplication.translate(
                "MainWindow", "Copy", None, QtGui.QApplication.UnicodeUTF8
            )
        )
        self.actionPaste.setText(
            QtGui.QApplication.translate(
                "MainWindow", "Paste", None, QtGui.QApplication.UnicodeUTF8
            )
        )
        self.actionFind.setText(
            QtGui.QApplication.translate(
                "MainWindow", "Find...", None, QtGui.QApplication.UnicodeUTF8
            )
        )
        self.actionHelp.setText(
            QtGui.QApplication.translate(
                "MainWindow", "Help", None, QtGui.QApplication.UnicodeUTF8
            )
        )
