# -*- coding: utf-8 -*-
"""This is the old version of the Project Manager.

Still useful.

Usage is as follows:

```python
    import os
    os.environ['STALKER_PATH'] = '/mnt/NAS/Users/eoyilmaz/Stalker_Projects'

    from anima.ui import SET_PYSIDE2
    SET_PYSIDE2()

    from anima.ui import project_manager
    project_manager.ui_caller(None, None, project_manager.MainWindow)
```
"""
import os

from anima import logger
from anima import ui
from anima.ui.base import ui_caller
from anima.ui.dialogs import login_dialog
from anima.ui.dialogs import project_dialog
from anima.ui.lib import QtCore, QtGui, QtWidgets
from anima.ui.utils import load_font, set_widget_style
from anima.ui.views.task import TaskTreeView
from anima.ui.widgets.task_dashboard import TaskDashboardWidget
from anima.utils import do_db_setup, partial_project_query

from stalker import LocalSession
from stalker import Task
from stalker.db.session import DBSession


class MainWindow(QtWidgets.QMainWindow):
    """The main application."""

    __company_name__ = "Erkan Ozgur Yilmaz"
    __app_name__ = "Project Manager Old"
    __version__ = "1.0.0"

    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)

        self.setup_db()

        # Authentication Storage
        self.login_action = None
        self.logout_action = None
        self.logged_in_user = self.login()
        self.dark_theme = True  # Dark Theme is default
        self.project_dock_widget = None

        app = QtWidgets.QApplication.instance()
        default_application_font = app.font()
        default_font_size = default_application_font.pixelSize()

        loaded_font_families = load_font("FontAwesome.otf")
        application_font = QtGui.QFont()
        if loaded_font_families:
            application_font.setFamily(loaded_font_families[0])
            # self.application_font.setStyleHint(QtGui.QFont.Normal)
            application_font.setPixelSize(default_font_size)
            app.setFont(application_font)

        # storage for UI stuff
        self.task_dashboard_widget = None
        self.tasks_tree_view = None

        # self.setWindowFlags(QtCore.Qt.ApplicationAttribute)
        self.settings = QtCore.QSettings(self.__company_name__, self.__app_name__)
        self._setup_ui()

    def set_ui_theme(self, dark_theme=False):
        """Set the UI theme.

        Args:
            dark_theme (bool): If set to True the dark_theme will be used.
        """
        self.dark_theme = dark_theme
        set_widget_style(self, dark_theme=dark_theme)

    @classmethod
    def setup_db(cls):
        """Set the the db up."""
        do_db_setup()

    def _setup_ui(self):
        """Create the UI widgets."""
        self.setWindowTitle("%s v%s" % (self.__app_name__, self.__version__))

        # set application icon
        logger.debug("ui.__path__: %s" % ui.__path__[0])

        app_icon_path = os.path.join(ui.__path__[0], "images", "app_icon.png")
        self.setWindowIcon(QtGui.QIcon(app_icon_path))

        self.create_main_menu()
        self.create_toolbars()
        self.create_dock_widgets()

        self.read_settings()

    def write_settings(self):
        """Store the settings to persistent storage."""
        self.settings.beginGroup("MainWindow")

        self.settings.setValue("size", self.size())
        self.settings.setValue("pos", self.pos())
        self.settings.setValue("windowState", self.saveState())
        self.settings.setValue("dark_theme", self.dark_theme)
        if self.task_dashboard_widget.task:
            self.settings.setValue(
                "last_viewed_task_id", self.task_dashboard_widget.task.id
            )

        self.settings.endGroup()

    def read_settings(self):
        """Read settings from persistent storage."""
        self.settings.beginGroup("MainWindow")

        self.resize(self.settings.value("size", QtCore.QSize(800, 600)))
        self.move(self.settings.value("pos", QtCore.QPoint(100, 100)))
        self.restoreState(self.settings.value("windowState"))
        bool_settings_value_lut = {
            "false": False,
            "true": True,
        }
        dark_theme = self.settings.value("dark_theme", "false")
        if not isinstance(dark_theme, bool):
            dark_theme = bool_settings_value_lut[dark_theme]
        self.set_ui_theme(dark_theme=dark_theme)

        task_id = self.settings.value("last_viewed_task_id")
        if task_id:
            task = Task.query.filter_by(id=task_id).first()
            self.tasks_tree_view.find_and_select_entity_item(task)

        self.settings.endGroup()

    def reset_window_state(self):
        """Reset window states."""
        self.project_dock_widget.setVisible(True)

    def create_main_menu(self):
        """Create the main application menu."""
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

        self.login_action.triggered.connect(self.login)
        self.logout_action.triggered.connect(self.logout)

        file_menu.addSeparator()

        # ---------------------------
        # Standard File menu actions

        create_project_action = file_menu.addAction("&Create Project...")
        # open_action = file_menu.addAction('&Open...')
        # save_action = file_menu.addAction('&Save...')

        # run the new Project dialog
        create_project_action.triggered.connect(self.create_project_action_clicked)

        file_menu.addSeparator()

        exit_action = file_menu.addAction("E&xit")
        exit_action.triggered.connect(self.close)

        view_menu = self.menuBar().addMenu("&View")
        switch_theme = view_menu.addAction("Switch Theme")

        def ui_theme_setter_wrapper():
            self.set_ui_theme(not self.dark_theme)

        switch_theme.triggered.connect(ui_theme_setter_wrapper)

        reset_action = view_menu.addAction("&Reset Window States")
        reset_action.triggered.connect(self.reset_window_state)

    def create_project_action_clicked(self):
        """Run when new project menu action is clicked."""
        # show the new project dialog
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
            self.tasks_tree_view.fill_ui()

        dialog.deleteLater()

    def login(self):
        """Return the logged in user.

        Returns:
            stalker.User: The logged in user.
        """
        local_session = LocalSession()
        with DBSession.no_autoflush:
            logged_in_user = local_session.logged_in_user

        if not logged_in_user:
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
        """Log the current user out."""
        session = LocalSession()
        session.delete()

        self.logged_in_user = None
        # update file menu actions
        # self.logout_action.setVisible(False)
        # self.login_action.setVisible(True)
        self.close()

    def create_toolbars(self):
        """Create the toolbars."""
        file_toolbar = self.addToolBar(self.tr("File"))
        file_toolbar.setObjectName("file_toolbar")
        create_project_action = file_toolbar.addAction("Create Project")

        # Create signals
        create_project_action.triggered.connect(self.create_project_action_clicked)

    def create_dock_widgets(self):
        """Create the dock widget."""
        # ----------------------------------------
        # create the Project Dock Widget
        self.project_dock_widget = QtWidgets.QDockWidget("Projects", self)
        self.project_dock_widget.setObjectName("project_dock_widget")
        # create the TaskTreeView as the main widget
        self.tasks_tree_view = TaskTreeView(
            parent=self, allow_multi_selection=True, allow_drag=True
        )
        self.tasks_tree_view.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.tasks_tree_view.tasks = partial_project_query()

        # also setup the signal
        self.tasks_tree_view.selectionModel().selectionChanged.connect(
            self.tasks_tree_view_changed
        )

        self.project_dock_widget.setWidget(self.tasks_tree_view)

        # and set the left dock widget
        self.addDockWidget(QtCore.Qt.LeftDockWidgetArea, self.project_dock_widget)

        # ----------------------------------------
        # create the Central Widget
        self.task_dashboard_widget = TaskDashboardWidget(parent=self)
        self.setCentralWidget(self.task_dashboard_widget)

    def tasks_tree_view_changed(self):
        """Run when the tasks tree view changed."""
        # get the currently selected task
        task_id = None
        task_ids = self.tasks_tree_view.get_selected_task_ids()
        if task_ids:
            task_id = task_ids[-1]
        task = Task.query.filter_by(id=task_id).first()

        # update the task dashboard widget
        self.task_dashboard_widget.task = task

    def show_and_raise(self):
        """Show and raise."""
        self.show()
        self.raise_()

    def closeEvent(self, event):
        """Override close event.

        Args:
            event (QtCore.QEvent): QEvent instance.
        """
        self.write_settings()
        event.accept()


if __name__ == "__main__":
    ui_caller(None, None, MainWindow)
