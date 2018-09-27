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

        self.setup_db()

        # Authentication Storage
        self.login_action = None
        self.logout_action = None
        self.logged_in_user = self.login()

        self.project_dock_widget = None

        # import qdarkgraystyle
        # app = QtWidgets.QApplication.instance()
        #
        # from anima.ui.lib import IS_PYQT4, IS_PYSIDE, IS_PYSIDE2
        #
        # if IS_PYSIDE():
        #     app.setStyleSheet(qdarkgraystyle.load_stylesheet())
        # elif IS_PYQT4():
        #     app.setStyleSheet(qdarkgraystyle.load_stylesheet(pyside=False))
        # elif IS_PYSIDE2():
        #     app.setStyleSheet(qdarkgraystyle.load_stylesheet_pyqt5())

        # storage for UI stuff
        self.task_dashboard_widget = None
        self.tasks_tree_view = None

        self.setWindowFlags(QtCore.Qt.ApplicationAttribute)
        self.settings = QtCore.QSettings(
            self.__company_name__,
            self.__app_name__
        )
        self.setup_ui()

    @classmethod
    def setup_db(cls):
        """setup the db
        """
        from anima.utils import do_db_setup
        do_db_setup()

    def setup_ui(self):
        """creates the UI widgets
        """
        self.setWindowTitle("%s v%s" % (self.__app_name__, self.__version__))

        # set application icon
        from anima import ui
        import os
        print('ui.__path__: %s' % ui.__path__[0])

        app_icon_path = os.path.join(
            ui.__path__[0],
            'images',
            'app_icon.png'
        )
        self.setWindowIcon(QtWidgets.QIcon(app_icon_path))

        self.create_main_menu()
        self.create_toolbars()
        self.create_dock_widgets()

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

    def reset_window_state(self):
        """reset window states
        """
        self.project_dock_widget.setVisible(True)

    def create_main_menu(self):
        """creates the main application menu
        """
        file_menu = self.menuBar().addMenu(self.tr("&File"))

        # -------------------------
        # Authentication Actions
        self.login_action = file_menu.addAction("&Login...")
        self.logout_action = file_menu.addAction("&Logout...")

        if self.logged_in_user:
            # hide login_action
            self.login_action.setVisible(False)
        else:
            # hide logout_action
            self.login_action.setVisible(False)

        QtCore.QObject.connect(
            self.login_action,
            QtCore.SIGNAL('triggered()'),
            self.login
        )

        QtCore.QObject.connect(
            self.logout_action,
            QtCore.SIGNAL('triggered()'),
            self.logout
        )

        file_menu.addSeparator()

        # ---------------------------
        # Standard File menu actions

        new_project_action = file_menu.addAction('&New Project...')
        open_action = file_menu.addAction('&Open...')
        save_action = file_menu.addAction('&Save...')

        # run the new Project dialog
        QtCore.QObject.connect(
            new_project_action,
            QtCore.SIGNAL("triggered()"),
            self.new_project_action_clicked
        )

        file_menu.addSeparator()

        exit_action = file_menu.addAction('E&xit')
        QtCore.QObject.connect(
            exit_action,
            QtCore.SIGNAL('triggered()'),
            self.close
        )

        view_menu = self.menuBar().addMenu(self.tr("&View"))

        reset_action = view_menu.addAction("&Reset Window States")
        QtCore.QObject.connect(
            reset_action,
            QtCore.SIGNAL('triggered()'),
            self.reset_window_state
        )

        # QtWidgets.QAction.

    def new_project_action_clicked(self):
        """runs when new project menu action is clicked
        """
        # show the new project dialog
        from anima.ui import project_dialog
        dialog = project_dialog.MainDialog(parent=self)
        dialog.exec_()

        # and refresh the TaskTreeView
        try:
            # PySide and PySide2
            accepted = QtWidgets.QDialog.DialogCode.Accepted
        except AttributeError:
            # PyQt4
            accepted = QtWidgets.QDialog.Accepted

        # refresh the task list
        if dialog.result() == accepted:
            self.tasks_tree_view.fill()

        dialog.deleteLater()

    def login(self):
        """returns the logged in user
        """
        from stalker import LocalSession
        local_session = LocalSession()
        from stalker.db.session import DBSession
        with DBSession.no_autoflush:
            logged_in_user = local_session.logged_in_user

        if not logged_in_user:
            from anima.ui import login_dialog
            dialog = login_dialog.MainDialog(parent=self)
            # dialog.deleteLater()
            dialog.exec_()
            result = dialog.result()

            try:
                # PySide
                accepted = QtWidgets.QDialog.DialogCode.Accepted
            except AttributeError:
                # PyQt4
                accepted = QtWidgets.QDialog.Accepted

            if result == accepted:
                local_session = LocalSession()
                logged_in_user = local_session.logged_in_user
            else:
                # close the ui
                # logged_in_user = self.get_logged_in_user()
                self.close()

            dialog.deleteLater()

        return logged_in_user

    def logout(self):
        """log the current user out
        """
        from stalker import LocalSession
        session = LocalSession()
        session.delete()

        self.logged_in_user = None
        # update file menu actions
        # self.logout_action.setVisible(False)
        # self.login_action.setVisible(True)
        self.close()

    def create_toolbars(self):
        """creates the toolbars
        """
        file_toolbar = self.addToolBar(self.tr("File"))
        file_toolbar.setObjectName('file_toolbar')
        file_toolbar.addAction('Create Project')

    def create_dock_widgets(self):
        """creates the dock widgets
        """
        # ----------------------------------------
        # create the Project Dock Widget
        self.project_dock_widget = QtWidgets.QDockWidget('Projects', self)
        self.project_dock_widget.setObjectName('project_dock_widget')
        # create the TaskTreeView as the main widget
        from anima.ui.views.task import TaskTreeView
        self.tasks_tree_view = TaskTreeView(parent=self)
        self.tasks_tree_view.setEditTriggers(
            QtWidgets.QAbstractItemView.NoEditTriggers
        )

        self.tasks_tree_view.show_completed_projects = True
        self.tasks_tree_view.fill()

        # also setup the signal
        QtCore.QObject.connect(
            self.tasks_tree_view.selectionModel(),
            QtCore.SIGNAL('selectionChanged(const QItemSelection &, '
                          'const QItemSelection &)'),
            self.tasks_tree_view_changed
        )

        self.project_dock_widget.setWidget(self.tasks_tree_view)

        # and set the left dock widget
        self.addDockWidget(
            QtCore.Qt.LeftDockWidgetArea,
            self.project_dock_widget
        )

        # ----------------------------------------
        # create the Central Widget
        from anima.ui.widgets.task_dashboard import TaskDashboardWidget
        self.task_dashboard_widget = TaskDashboardWidget(parent=self)
        self.setCentralWidget(self.task_dashboard_widget)

    def tasks_tree_view_changed(self):
        """runs when the tasks tree view changed
        """
        # get the currently selected task
        task_id = self.tasks_tree_view.get_task_id()
        from stalker import Task
        task = Task.query.get(task_id)

        # update the task dashboard widget
        self.task_dashboard_widget.task = task
        self.task_dashboard_widget.fill_ui()

    def show_and_raise(self):
        """
        """
        self.show()
        self.raise_()

    def closeEvent(self, event):
        """The overridden close event
        """
        self.write_settings()
        event.accept()


if __name__ == "__main__":
    ui_caller(None, None, MainWindow)
