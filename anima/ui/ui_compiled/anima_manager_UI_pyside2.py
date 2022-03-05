# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'C:\Users\eoyilmaz\Documents\development\anima\anima\anima\ui\ui_files\anima_manager.ui'
#
# Created: Wed May 03 15:22:34 2017
#      by: pyside2-uic  running on PySide2 2.0.0~alpha0
#
# WARNING! All changes made in this file will be lost!

from PySide2 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1108, 769)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.centralwidget)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout()
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.horizontalLayout.addLayout(self.verticalLayout_2)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1108, 21))
        self.menubar.setObjectName("menubar")
        self.menuFile = QtWidgets.QMenu(self.menubar)
        self.menuFile.setObjectName("menuFile")
        self.menuEdit = QtWidgets.QMenu(self.menubar)
        self.menuEdit.setObjectName("menuEdit")
        self.menuHelp = QtWidgets.QMenu(self.menubar)
        self.menuHelp.setObjectName("menuHelp")
        self.menuView = QtWidgets.QMenu(self.menubar)
        self.menuView.setObjectName("menuView")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.dockWidget = QtWidgets.QDockWidget(MainWindow)
        self.dockWidget.setObjectName("dockWidget")
        self.dockWidgetContents = QtWidgets.QWidget()
        self.dockWidgetContents.setObjectName("dockWidgetContents")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.dockWidgetContents)
        self.verticalLayout.setObjectName("verticalLayout")
        self.pushButton_2 = QtWidgets.QPushButton(self.dockWidgetContents)
        self.pushButton_2.setObjectName("pushButton_2")
        self.verticalLayout.addWidget(self.pushButton_2)
        self.pushButton_3 = QtWidgets.QPushButton(self.dockWidgetContents)
        self.pushButton_3.setObjectName("pushButton_3")
        self.verticalLayout.addWidget(self.pushButton_3)
        self.pushButton = QtWidgets.QPushButton(self.dockWidgetContents)
        self.pushButton.setObjectName("pushButton")
        self.verticalLayout.addWidget(self.pushButton)
        spacerItem = QtWidgets.QSpacerItem(
            20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding
        )
        self.verticalLayout.addItem(spacerItem)
        self.dockWidget.setWidget(self.dockWidgetContents)
        MainWindow.addDockWidget(QtCore.Qt.DockWidgetArea(1), self.dockWidget)
        self.actionConnect_To_Server = QtWidgets.QAction(MainWindow)
        self.actionConnect_To_Server.setObjectName("actionConnect_To_Server")
        self.actionAbout_AnimaMan = QtWidgets.QAction(MainWindow)
        self.actionAbout_AnimaMan.setObjectName("actionAbout_AnimaMan")
        self.actionLogin = QtWidgets.QAction(MainWindow)
        self.actionLogin.setObjectName("actionLogin")
        self.actionLogout = QtWidgets.QAction(MainWindow)
        self.actionLogout.setObjectName("actionLogout")
        self.actionExit = QtWidgets.QAction(MainWindow)
        self.actionExit.setObjectName("actionExit")
        self.actionUndo = QtWidgets.QAction(MainWindow)
        self.actionUndo.setObjectName("actionUndo")
        self.actionRedo = QtWidgets.QAction(MainWindow)
        self.actionRedo.setObjectName("actionRedo")
        self.actionCopy = QtWidgets.QAction(MainWindow)
        self.actionCopy.setObjectName("actionCopy")
        self.actionPaste = QtWidgets.QAction(MainWindow)
        self.actionPaste.setObjectName("actionPaste")
        self.actionFind = QtWidgets.QAction(MainWindow)
        self.actionFind.setObjectName("actionFind")
        self.actionHelp = QtWidgets.QAction(MainWindow)
        self.actionHelp.setObjectName("actionHelp")
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
            QtWidgets.QApplication.translate("MainWindow", "Anima Manager", None, -1)
        )
        self.menuFile.setTitle(
            QtWidgets.QApplication.translate("MainWindow", "File", None, -1)
        )
        self.menuEdit.setTitle(
            QtWidgets.QApplication.translate("MainWindow", "Edit", None, -1)
        )
        self.menuHelp.setTitle(
            QtWidgets.QApplication.translate("MainWindow", "Help", None, -1)
        )
        self.menuView.setTitle(
            QtWidgets.QApplication.translate("MainWindow", "View", None, -1)
        )
        self.pushButton_2.setText(
            QtWidgets.QApplication.translate("MainWindow", "My Projects", None, -1)
        )
        self.pushButton_3.setText(
            QtWidgets.QApplication.translate("MainWindow", "My Tasks", None, -1)
        )
        self.pushButton.setText(
            QtWidgets.QApplication.translate("MainWindow", "My Vacations", None, -1)
        )
        self.actionConnect_To_Server.setText(
            QtWidgets.QApplication.translate(
                "MainWindow", "Connect To Server...", None, -1
            )
        )
        self.actionAbout_AnimaMan.setText(
            QtWidgets.QApplication.translate(
                "MainWindow", "About AnimaMan ...", None, -1
            )
        )
        self.actionLogin.setText(
            QtWidgets.QApplication.translate("MainWindow", "Login...", None, -1)
        )
        self.actionLogout.setText(
            QtWidgets.QApplication.translate("MainWindow", "Logout", None, -1)
        )
        self.actionExit.setText(
            QtWidgets.QApplication.translate("MainWindow", "Exit", None, -1)
        )
        self.actionUndo.setText(
            QtWidgets.QApplication.translate("MainWindow", "Undo", None, -1)
        )
        self.actionRedo.setText(
            QtWidgets.QApplication.translate("MainWindow", "Redo", None, -1)
        )
        self.actionCopy.setText(
            QtWidgets.QApplication.translate("MainWindow", "Copy", None, -1)
        )
        self.actionPaste.setText(
            QtWidgets.QApplication.translate("MainWindow", "Paste", None, -1)
        )
        self.actionFind.setText(
            QtWidgets.QApplication.translate("MainWindow", "Find...", None, -1)
        )
        self.actionHelp.setText(
            QtWidgets.QApplication.translate("MainWindow", "Help", None, -1)
        )
