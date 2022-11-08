# -*- coding: utf-8 -*-
"""
import os
os.environ['STALKER_PATH'] = '/mnt/NAS/Users/eoyilmaz/Stalker_Projects'

from anima.ui import SET_PYSIDE2
SET_PYSIDE2()

from anima.ui import project_manager
project_manager.ui_caller(None, None, project_manager.MainWindow)
"""
import os

from anima import ui, logger
from anima.ui.base import ui_caller
from anima.ui.lib import QtCore, QtGui, QtWidgets
from anima.ui.utils import set_widget_style
from anima.ui.menus import MainMenuBar

from stalker import Client, Department, Group, User

from anima.ui.widgets.user_page import UserPageWidget

if False:
    from PySide2 import QtCore, QtGui, QtWidgets


class MainWindow(QtWidgets.QMainWindow):
    """The main application"""

    __company_name__ = "Erkan Ozgur Yilmaz"
    __app_name__ = "Project Manager"
    __version__ = "1.0.0"

    pages = {}

    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)

        self.setup_db()

        # Authentication Storage
        self.login_action = None
        self.logout_action = None
        self.logged_in_user = self.login()
        self.dark_theme = True  # Dark Theme is default
        self.project_dock_widget = None

        # storage for UI stuff
        self.task_dashboard_widget = None
        self.tasks_tree_view = None

        # self.setWindowFlags(QtCore.Qt.ApplicationAttribute)
        self.settings = QtCore.QSettings(self.__company_name__, self.__app_name__)
        self._setup()

        # set the default page to logged in users home page
        self.view_user(self.logged_in_user)

    def set_ui_theme(self, dark_theme=False):
        """Set the UI theme.

        Args:
            dark_theme (bool): If set to True the dark_theme will be used.
        """
        self.dark_theme = dark_theme
        set_widget_style(self, dark_theme=dark_theme)

    @classmethod
    def setup_db(cls):
        """setup the db"""
        from anima.utils import do_db_setup

        do_db_setup()

    def _setup(self):
        """creates the UI widgets"""
        self.setWindowTitle("%s v%s" % (self.__app_name__, self.__version__))

        # set application icon
        logger.debug("ui.__path__: %s" % ui.__path__[0])

        app_icon_path = os.path.join(ui.__path__[0], "../images", "app_icon.png")
        self.setWindowIcon(QtGui.QIcon(app_icon_path))

        menu_bar = MainMenuBar()
        self.setMenuBar(menu_bar)
        menu_bar.view_project_signal.connect(self.view_project)
        menu_bar.view_user_signal.connect(self.view_user)
        menu_bar.view_studio_signal.connect(self.view_studio)
        menu_bar.list_clients_signal.connect(self.list_clients)
        menu_bar.list_departments_signal.connect(self.list_departments)
        menu_bar.list_groups_signal.connect(self.list_groups)
        menu_bar.list_users_signal.connect(self.list_users)
        menu_bar.create_project_signal.connect(self.create_project)

        self.create_toolbars()
        self.create_dock_widgets()

        self.read_settings()

    def list_clients(self):
        """Show List Clients page."""
        for client in Client.query.order_by(Client.name).all():
            print(client.name)

    def list_departments(self):
        """Show List Departments page."""
        for department in Department.query.order_by(Department.name).all():
            print(department.name)

    def list_groups(self):
        """Show List Groups page."""
        for group in Group.query.order_by(Group.name).all():
            print(group.name)

    def list_users(self):
        """Show List Users page."""
        for user in User.query.order_by(User.name).all():
            print(user.name)

    def view_project(self, project):
        """Show Project page."""
        print(project.name)

    def view_user(self, user):
        """Show User page."""
        # find the User Page in the Main Stacked Widget
        # and get the main widget on the User Page
        # if there is no widget just create a new UserPage widget
        # set the user
        user_page_widget = self.pages.get("UserPage")
        if not user_page_widget:
            user_page_widget = UserPageWidget(parent=self)
            self.pages["UserPage"] = user_page_widget
        index = self.main_stacked_widget.indexOf(user_page_widget)
        if index == -1:
            index = self.main_stacked_widget.addWidget(user_page_widget)
        user_page_widget.user = user
        self.main_stacked_widget.setCurrentIndex(index)

    def view_studio(self, studio):
        """Show Studio page."""
        print(studio.name)

    def write_settings(self):
        """stores the settings to persistent storage"""
        self.settings.beginGroup("MainWindow")

        self.settings.setValue("size", self.size())
        self.settings.setValue("pos", self.pos())
        self.settings.setValue("windowState", self.saveState())
        self.settings.setValue("dark_theme", self.dark_theme)
        # if self.task_dashboard_widget.task:
        #     self.settings.setValue(
        #         "last_viewed_task_id", self.task_dashboard_widget.task.id
        #     )

        self.settings.endGroup()

    def read_settings(self):
        """read settings from persistent storage"""
        self.settings.beginGroup("MainWindow")

        self.resize(self.settings.value("size", QtCore.QSize(800, 600)))
        self.move(self.settings.value("pos", QtCore.QPoint(100, 100)))
        self.restoreState(self.settings.value("windowState"))
        bool_settings_value_lut = {"false": False, "true": True}
        # self.set_ui_theme(
        #     dark_theme=bool_settings_value_lut[
        #         self.settings.value("dark_theme", "false")
        #     ]
        # )

        # from anima.ui.views.task import TaskTreeView
        #
        # assert isinstance(self.tasks_tree_view, TaskTreeView)
        #
        # task_id = self.settings.value("last_viewed_task_id")
        # if task_id:
        #     from stalker import Task
        #
        #     task = Task.query.get(task_id)
        #     self.tasks_tree_view.find_and_select_entity_item(task)

        self.settings.endGroup()

    def reset_window_state(self):
        """reset window states"""
        # self.project_dock_widget.setVisible(True)

    def create_project(self):
        """runs when new project menu action is clicked"""
        # show the new project dialog
        from anima.ui.dialogs import project_dialog

        dialog = project_dialog.MainDialog(parent=self)
        dialog.exec_()

        # and refresh the TaskTreeView
        try:
            # PySide and PySide2
            accepted = QtWidgets.QDialog.DialogCode.Accepted
        except AttributeError:
            # PyQt4
            accepted = QtWidgets.QDialog.Accepted

        # # refresh the task list
        # if dialog.result() == accepted:
        #     self.tasks_tree_view.fill_ui()

        dialog.deleteLater()

    def login(self):
        """returns the logged in user"""
        from stalker import LocalSession

        local_session = LocalSession()
        from stalker.db.session import DBSession

        with DBSession.no_autoflush:
            logged_in_user = local_session.logged_in_user

        if not logged_in_user:
            from anima.ui.dialogs import login_dialog

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
        """log the current user out"""
        from stalker import LocalSession

        session = LocalSession()
        session.delete()

        self.logged_in_user = None
        # update file menu actions
        # self.logout_action.setVisible(False)
        # self.login_action.setVisible(True)
        self.close()

    def create_toolbars(self):
        """creates the toolbars"""
        file_toolbar = self.addToolBar("File")
        file_toolbar.setObjectName("file_toolbar")
        create_project_action = file_toolbar.addAction("Create Project")

        # Create signals
        create_project_action.triggered.connect(self.create_project)

    def create_dock_widgets(self):
        """creates the dock widgets"""
        # # ----------------------------------------
        # # create the Project Dock Widget
        # self.project_dock_widget = QtWidgets.QDockWidget("Projects", self)
        # self.project_dock_widget.setObjectName("project_dock_widget")
        # # create the TaskTreeView as the main widget
        # from anima.ui.views.task import TaskTreeView
        #
        # self.tasks_tree_view = TaskTreeView(
        #     parent=self, allow_multi_selection=True, allow_drag=True
        # )
        # self.tasks_tree_view.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        #
        # self.tasks_tree_view.show_completed_projects = True
        # self.tasks_tree_view.fill_ui()
        #
        # # also setup the signal
        # self.tasks_tree_view.selectionModel().selectionChanged.connect(
        #     self.tasks_tree_view_changed
        # )
        #
        # self.project_dock_widget.setWidget(self.tasks_tree_view)
        #
        # # and set the left dock widget
        # self.addDockWidget(QtCore.Qt.LeftDockWidgetArea, self.project_dock_widget)
        #
        # # ----------------------------------------
        # # create the Central Widget
        # from anima.ui.widgets.task_dashboard import TaskDashboardWidget
        #
        # self.task_dashboard_widget = TaskDashboardWidget(parent=self)
        # self.setCentralWidget(self.task_dashboard_widget)
        self.main_stacked_widget = QtWidgets.QStackedWidget(self)
        self.setCentralWidget(self.main_stacked_widget)

    # def tasks_tree_view_changed(self):
    #     """runs when the tasks tree view changed"""
    #     # get the currently selected task
    #     task_id = None
    #     task_ids = self.tasks_tree_view.get_selected_task_ids()
    #     if task_ids:
    #         task_id = task_ids[-1]
    #
    #     from stalker import Task
    #
    #     task = Task.query.filter_by(id=task_id).first()
    #
    #     # update the task dashboard widget
    #     self.task_dashboard_widget.task = task

    def show_and_raise(self):
        """ """
        self.show()
        self.raise_()

    def closeEvent(self, event):
        """The overridden close event"""
        self.write_settings()
        event.accept()


if __name__ == "__main__":
    ui_caller(None, None, MainWindow)
