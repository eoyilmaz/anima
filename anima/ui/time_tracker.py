# -*- coding: utf-8 -*-


import sys
from anima.ui import SET_PYSIDE2
SET_PYSIDE2()


from anima.ui.lib import QtCore, QtGui, QtWidgets


class App(object):
    def __init__(self):
        # Create a Qt application
        self.dialog = None
        self.app = QtWidgets.QApplication(sys.argv)

        from anima.ui.utils import get_icon
        icon = get_icon("stalkerpyramid")
        menu = QtWidgets.QMenu()
        setting_action = menu.addAction("setting")
        setting_action.triggered.connect(self.setting)
        exit_action = menu.addAction("exit")
        exit_action.triggered.connect(sys.exit)

        self.tray = QtWidgets.QSystemTrayIcon()
        self.tray.setIcon(icon)
        self.tray.setContextMenu(menu)
        self.tray.show()
        self.tray.setToolTip("unko!")
        self.tray.showMessage("hoge", "moge")
        self.tray.showMessage("fuga", "moge")

    def run(self):
        # Enter Qt application main loop
        self.app.exec_()
        sys.exit()

    def setting(self):
        self.dialog = QtWidgets.QDialog()
        self.dialog.setWindowTitle("Setting Dialog")
        self.dialog.show()


if __name__ == "__main__":
    app = App()
    app.run()
