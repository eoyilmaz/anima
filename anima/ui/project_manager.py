# -*- coding: utf-8 -*-
# Copyright (c) 2018, Erkan  Ozgur Yilmaz
#
# This module is part of anima-tools and is released under the BSD 2
# License: http://www.opensource.org/licenses/BSD-2-Clause
from anima.ui.base import ui_caller
from anima.ui.lib import QtCore, QtWidgets


class MainWindow(QtWidgets.QMainWindow):
    """The main application
    """

    __company_name__ = 'Erkan Ozgur Yilmaz'
    __app_name__ = 'Project Manager'
    __version__ = '0.0.1'

    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)

        import qdarkgraystyle
        app = QtWidgets.QApplication.instance()

        from anima.ui.lib import IS_PYQT4, IS_PYSIDE, IS_PYSIDE2

        if IS_PYSIDE():
            app.setStyleSheet(qdarkgraystyle.load_stylesheet())
        elif IS_PYQT4():
            app.setStyleSheet(qdarkgraystyle.load_stylesheet(pyside=False))
        elif IS_PYSIDE2():
            app.setStyleSheet(qdarkgraystyle.load_stylesheet_pyqt5())

        self.setWindowFlags(QtCore.Qt.ApplicationAttribute)
        self.settings = QtCore.QSettings(
            self.__company_name__,
            self.__app_name__
        )
        self.setup_ui()

    def setup_ui(self):
        """creates the UI widgets
        """
        self.setWindowTitle("%s v%s" % (self.__app_name__, self.__version__))

        self.create_main_menu()
        self.create_toolbars()

        self.read_settings()

    def write_settings(self):
        """stores the settings to persistent storage
        """
        self.settings.beginGroup("MainWindow")

        self.settings.setValue("size", self.size())
        self.settings.setValue("pos", self.pos())
        self.settings.setValue("windowState", self.saveState())

        self.settings.endGroup()

    def read_settings(self):
        """read settings from persistent storage
        """
        self.settings.beginGroup('MainWindow')

        self.resize(self.settings.value('size', QtCore.QSize(800, 600)))
        self.move(self.settings.value('pos', QtCore.QPoint(100, 100)))
        self.restoreState(self.settings.value('windowState'))

        self.settings.endGroup()

    def create_main_menu(self):
        """creates the main application menu
        """
        file_menu = self.menuBar().addMenu(self.tr("&File"))

        new_action = file_menu.addAction('&New...')
        open_action = file_menu.addAction('&Open...')
        save_action = file_menu.addAction('&Save...')

        file_menu.addSeparator()

        exit_action = file_menu.addAction('E&xit')
        QtCore.QObject.connect(
            exit_action,
            QtCore.SIGNAL('triggered()'),
            self.close
        )

        # QtWidgets.QAction.

    def create_toolbars(self):
        """creates the toolbars
        """
        file_toolbar = self.addToolBar(self.tr("File"))
        file_toolbar.setObjectName('file_toolbar')
        file_toolbar.addAction('Create Project')

    def show_and_raise(self):
        """
        """
        self.show()
        self.raise_()

    def closeEvent(self, event):
        """The overridden close event
        """
        result = QtWidgets.QMessageBox.question(
            self, self.__app_name__,
            self.tr("Are you sure?\n"),
            QtWidgets.QMessageBox.Cancel | QtWidgets.QMessageBox.No | QtWidgets.QMessageBox.Yes,
            QtWidgets.QMessageBox.Yes
        )

        if result != QtWidgets.QMessageBox.Yes:
            event.ignore()
        else:
            self.write_settings()
            event.accept()


if __name__ == "__main__":
    app = ui_caller(None, None, MainWindow)
