# -*- coding: utf-8 -*-
"""User page related widgets are here."""

from functools import partial

from anima.ui.lib import QtCore, QtGui, QtWidgets
from anima.ui.models.task import TaskTableModel
from anima.ui.utils import get_cached_icon, update_graphics_view_with_entity_thumbnail
from anima.ui.views.task import TaskTableView
from anima.ui.widgets.button import DashboardButton
from anima.ui.widgets.page import PageTitleWidget
from anima.ui.widgets.project import ProjectComboBox

from sqlalchemy import distinct
from sqlalchemy.sql.functions import count

from stalker import Project, Status, Task, User
from stalker.db.session import DBSession


if False:
    from PySide2 import QtCore, QtGui, QtWidgets


class UserPropertyMixin(object):
    """User property mixin."""

    def __init__(self):
        self._user = None

    @property
    def user(self):
        """Return the user.

        Returns:
            :obj:`stalker.User`: The user stored in this page.
        """
        return self._user

    @user.setter
    def user(self, user):
        """Set the user.

        Args:
            user (:obj:`stalker.user`): The user for this widget to show the details of.

        Raises:
            TypeError: When the given user argument value is not None and not a Stalker
                User instance.
        """
        # validate the data first
        if user is not None and not isinstance(user, User):
            raise TypeError(
                "{}.user should be a stalker.models.auth.User instance, not {}".format(
                    self.__class__.__name__,
                    user.__class__.__name,
                )
            )
        self._user = user


class ProjectPropertyMixin(object):
    """Project property mixin."""

    def __init__(self):
        self._project = None

    @property
    def project(self):
        """Return the project.

        Returns:
            :obj:`stalker.Project`: The project stored in this page.
        """
        return self._project

    @project.setter
    def project(self, project):
        """Set the project.

        Args:
            project (:obj:`stalker.project`): The project for this widget to show the
                details of.

        Raises:
            TypeError: When the given project argument value is not None and not a
                Project instance.
        """
        # validate the data first
        if project is not None and not isinstance(project, Project):
            raise TypeError(
                "{}.project should be a stalker.models.auth.Project instance, "
                "not {}".format(
                    self.__class__.__name__,
                    project.__class__.__name,
                )
            )
        self._project = project


class UserPageWidget(QtWidgets.QWidget, UserPropertyMixin):
    """User home page."""

    pages = {}

    def __init__(self, *args, **kwargs):
        super(UserPageWidget, self).__init__(*args, **kwargs)
        UserPropertyMixin.__init__(self)
        self._setup()

    def _setup(self):
        self.main_layout = QtWidgets.QHBoxLayout()
        self.main_layout.setMargin(0)
        self.setLayout(self.main_layout)

        # -------------------------
        # Side Bar
        self.side_bar = UserSideBarWidget(parent=self)
        self.main_layout.addWidget(self.side_bar)
        # Signals
        self.side_bar.view_user_dashboard.connect(self.view_dashboard)

        # -------------------------
        # Main Stacked Widget
        self.main_stacked_widget = QtWidgets.QStackedWidget(self)
        self.main_layout.addWidget(self.main_stacked_widget)
        self.main_layout.setStretch(0, 0)  # side_bar

    @UserPropertyMixin.user.setter
    def user(self, user):
        """Set the user.

        Args:
            user (:obj:`stalker.user`): The user for this widget to show the details of.
        """
        UserPropertyMixin.user.fset(self, user)
        self.side_bar.user = user
        self.view_dashboard(self.user)

    def view_dashboard(self, user):
        """Show User page.

        Args:
            user (:class:``stalker.User``): A Stalker User instance.
        """
        # find the User Page in the Main Stacked Widget
        # and get the main widget on the User Page
        # if there is no widget just create a new UserPage widget
        # set the user
        user_dashboard_widget = self.pages.get("UserDashboard")
        if not user_dashboard_widget:
            user_dashboard_widget = UserDashboardWidget(parent=self)
            self.pages["UserDashboard"] = user_dashboard_widget
        index = self.main_stacked_widget.indexOf(user_dashboard_widget)
        if index == -1:
            index = self.main_stacked_widget.addWidget(user_dashboard_widget)
        user_dashboard_widget.user = user
        self.main_stacked_widget.setCurrentIndex(index)


class UserSideBarWidget(QtWidgets.QWidget, UserPropertyMixin):
    """User side bar widget."""

    view_user_dashboard = QtCore.Signal(object)
    view_user_reports = QtCore.Signal(object)
    view_user_results = QtCore.Signal(object)
    list_user_authlogs = QtCore.Signal(object)
    list_user_departments = QtCore.Signal(object)
    list_user_groups = QtCore.Signal(object)
    list_user_projects = QtCore.Signal(object)
    list_user_reviews = QtCore.Signal(object)
    list_user_tasks = QtCore.Signal(object, object)  # action and user entity
    list_user_tickets = QtCore.Signal(object)
    list_user_timelogs = QtCore.Signal(object)
    list_user_vacations = QtCore.Signal(object)
    list_user_versions = QtCore.Signal(object)

    def __init__(self, *args, **kwargs):
        super(UserSideBarWidget, self).__init__(*args, **kwargs)
        UserPropertyMixin.__init__(self)
        self._setup()

    def _setup(self):
        self.setMaximumWidth(200)
        self.main_layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.main_layout)

        # ------------------
        # Thumbnail and Name
        self.thumbnail_and_name_layout = QtWidgets.QHBoxLayout()
        self.main_layout.addLayout(self.thumbnail_and_name_layout)

        # Thumbnail
        self.thumbnail_graphics_view = QtWidgets.QGraphicsView(self)
        self.thumbnail_graphics_view.setMaximumSize(100, 100)
        self.thumbnail_and_name_layout.addWidget(self.thumbnail_graphics_view)

        self.name_label = QtWidgets.QLabel(self)
        self.thumbnail_and_name_layout.addWidget(self.name_label)

        # -----------------------
        # Menu Buttons
        self.buttons_layout = QtWidgets.QVBoxLayout()
        self.main_layout.addLayout(self.buttons_layout)

        # Dashboard
        self.dashboard_button = DashboardButton(
            get_cached_icon("dashboard"), "Dashboard", parent=self
        )
        self.buttons_layout.addWidget(self.dashboard_button)
        self.dashboard_button.clicked.connect(
            partial(self.emit_signal_and_user, self.view_user_dashboard)
        )

        # My Tasks
        self.my_tasks_button = DashboardButton(
            get_cached_icon("task"), "My Tasks", parent=self
        )
        self.buttons_layout.addWidget(self.my_tasks_button)
        self.my_tasks_button.clicked.connect(
            partial(self.emit_signal_and_user, self.list_user_tasks, None)
        )

        # Responsible Of
        self.responsible_of_tasks_button = DashboardButton(
            get_cached_icon("task"), "Responsible Of", parent=self
        )
        self.buttons_layout.addWidget(self.responsible_of_tasks_button)
        self.responsible_of_tasks_button.clicked.connect(
            partial(self.emit_signal_and_user, self.list_user_tasks, "responsible")
        )

        # Watch List
        self.watch_list_button = DashboardButton(
            get_cached_icon("task"), "Watch List", parent=self
        )
        self.buttons_layout.addWidget(self.watch_list_button)
        self.responsible_of_tasks_button.clicked.connect(
            partial(self.emit_signal_and_user, self.list_user_tasks, "watching")
        )

        # Tickets
        self.tickets_button = DashboardButton(
            get_cached_icon("ticket"), "Tickets", parent=self
        )
        self.buttons_layout.addWidget(self.tickets_button)
        self.tickets_button.clicked.connect(
            partial(self.emit_signal_and_user, self.list_user_tickets)
        )

        # TimeLogs
        self.timelogs_button = DashboardButton(
            get_cached_icon("timelog"), "TimeLogs", parent=self
        )
        self.buttons_layout.addWidget(self.timelogs_button)
        self.timelogs_button.clicked.connect(
            partial(self.emit_signal_and_user, self.list_user_timelogs)
        )

        # Reviews
        self.reviews_button = DashboardButton(
            get_cached_icon("review"), "Reviews", parent=self
        )
        self.buttons_layout.addWidget(self.reviews_button)
        self.reviews_button.clicked.connect(
            partial(self.emit_signal_and_user, self.list_user_reviews)
        )

        # Reports
        self.reports_button = DashboardButton(
            get_cached_icon("report"), "Reports", parent=self
        )
        self.buttons_layout.addWidget(self.reports_button)
        self.reports_button.clicked.connect(
            partial(self.emit_signal_and_user, self.view_user_reports)
        )

        # Results
        self.results_button = DashboardButton(
            get_cached_icon("result"), "Results", parent=self
        )
        self.buttons_layout.addWidget(self.results_button)
        self.results_button.clicked.connect(
            partial(self.emit_signal_and_user, self.view_user_results)
        )

        # AuthLogs
        self.authlogs_button = DashboardButton(
            get_cached_icon("authlog"), "Authlogs", parent=self
        )
        self.buttons_layout.addWidget(self.authlogs_button)
        self.authlogs_button.clicked.connect(
            partial(self.emit_signal_and_user, self.view_user_results)
        )

        # Vacations
        self.vacations_button = DashboardButton(
            get_cached_icon("vacation"), "Vacations", parent=self
        )
        self.buttons_layout.addWidget(self.vacations_button)
        self.vacations_button.clicked.connect(
            partial(self.emit_signal_and_user, self.list_user_vacations)
        )

        # Efficiency
        # ------------- SKIP FOR NOW -----------------

        # Versions
        self.versions_button = DashboardButton(
            get_cached_icon("version"), "Versions", parent=self
        )
        self.buttons_layout.addWidget(self.versions_button)
        self.versions_button.clicked.connect(
            partial(self.emit_signal_and_user, self.list_user_versions)
        )

        # Departments
        # Groups
        # Projects

        # -----------------------
        # Spacer Item
        self.buttons_layout.addSpacerItem(
            QtWidgets.QSpacerItem(
                -1, -1, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding
            )
        )

        # style_sheet = self.styleSheet()
        # style_sheet += """.QPushButton {
        #     text-align: left;
        #     padding-left: 10px;
        #     height: 32px;
        # }"""

        # self.setStyleSheet(style_sheet)

    @UserPropertyMixin.user.setter
    def user(self, user):
        """Set the user.

        Args:
            user (:obj:`stalker.user`): The user for this widget to show the details of.
        """
        UserPropertyMixin.user.fset(self, user)
        # update the thumbnail
        if self._user.thumbnail:
            update_graphics_view_with_entity_thumbnail(
                self._user, self.thumbnail_graphics_view
            )

        # Update Name
        self.name_label.setText("\n".join(user.name.split(" ") + [user.login]))

    def emit_signal_and_user(self, *args):
        """Emit the given signal with the current user.

        Args:
            args: All the arguments.
        """
        # This is a little hacky,
        # but it should work with signals demanding any number of arguments
        signal = args[0]  # this is always the signal
        # this could be written as args[0] = self.user
        # but this is much more cleaner
        new_args = [self.user] + list(args[1:])
        # now we can emit the signal with arguments
        signal.emit(*new_args)


class UserDashboardWidget(QtWidgets.QWidget, UserPropertyMixin):
    """User Dashboard widget."""

    def __init__(self, *args, **kwargs):
        super(UserDashboardWidget, self).__init__(*args, **kwargs)
        UserPropertyMixin.__init__(self)
        self._setup()

    def _setup(self):
        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.setMargin(0)
        self.setLayout(self.main_layout)
        page_title = PageTitleWidget("Dashboard")
        self.main_layout.addWidget(page_title)

        self.content_layout = QtWidgets.QHBoxLayout()
        self.content_layout.setMargin(0)
        self.main_layout.addLayout(self.content_layout)

        # ---------------------------------
        # User Tasks By Status Widget
        self.user_tasks_by_status_widget = UserTasksByStatusWidget(self)
        # self.user_tasks_by_status_widget.user = self.user
        self.content_layout.addWidget(self.user_tasks_by_status_widget)

        # ---------------------------------
        # User Calendar
        pass

        # ---------------------------------
        # User Recent messages
        pass

    @UserPropertyMixin.user.setter
    def user(self, user):
        """Set the user.

        Args:
            user (:obj:`stalker.user`): The user for this widget to show the details of.
        """
        UserPropertyMixin.user.fset(self, user)
        # update the widgets
        self.user_tasks_by_status_widget.user = user


class UserTasksByStatusWidget(
    QtWidgets.QWidget, UserPropertyMixin, ProjectPropertyMixin
):
    """Display user tasks grouped by their statuses.

    This is a classic Stalker Pyramid widget implemented in Qt.
    Displays tasks in a TabWidget grouped by their statuses. Each Tab contains a
    TaskTable.
    """

    status_order = ["WFD", "RTS", "WIP", "PREV", "HREV", "DREV", "CMPL", "OH", "STOP"]

    def __init__(self, *args, **kwargs):
        super(UserTasksByStatusWidget, self).__init__(*args, **kwargs)
        UserPropertyMixin.__init__(self)
        ProjectPropertyMixin.__init__(self)
        self.tabs = []
        self._setup()

    def _setup(self):
        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.setMargin(0)
        self.setLayout(self.main_layout)

        # Project Combo Box
        project_combo_box_layout = QtWidgets.QHBoxLayout()
        project_combo_box_layout.setMargin(0)
        self.main_layout.addLayout(project_combo_box_layout)

        self.project_combo_box = ProjectComboBox(self)
        self.project_combo_box.show_active_projects = True
        self.project_combo_box.currentIndexChanged.connect(
            partial(self.project_combo_box_changed)
        )
        project_combo_box_layout.addWidget(self.project_combo_box)
        project_combo_box_layout.addSpacerItem(
            QtWidgets.QSpacerItem(
                -1, -1, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum
            )
        )

        # the tabWidget
        self.main_tab_widget = QtWidgets.QTabWidget(self)
        self.main_layout.addWidget(self.main_tab_widget)

    def project_combo_box_changed(self, index):
        """Update the project from the combo box.

        Args:
            index (int): The current index.
        """
        self.project = self.project_combo_box.get_current_project()

    @UserPropertyMixin.user.setter
    def user(self, user):
        """Set the user.

        Args:
            user (:obj:`stalker.user`): The user for this widget to show the details of.
        """
        UserPropertyMixin.user.fset(self, user)
        self.update()

    @ProjectPropertyMixin.project.setter
    def project(self, project):
        """Set the project.

        Args:
            project (:obj:`stalker.Project`): The project for this widget to show the
                details of.
        """
        ProjectPropertyMixin.project.fset(self, project)
        self.update()

    def update(self):
        """Update the data in the tabs."""
        # clear all the tabs
        self.main_tab_widget.clear()

        if not self.user or not self.project:
            return

        # get all the distinct Statuses for the user for the specific project
        status_codes_and_counts = (
            DBSession.query(distinct(Status.code), count(Status.code))
            .join(Task.status)
            .filter(Task.resources.contains(self.user))
            .filter(Task.project == self.project)
            .group_by(Status.code)
            .all()
        )
        # convert it to a dictionary,
        # where the status code is the key and count is the value
        status_codes_and_counts = dict(status_codes_and_counts)

        # Orchestrate the order of the statuses
        for status_code in self.status_order:
            if status_code in status_codes_and_counts:
                # create one tab for each status
                status = Status.query.filter(Status.code == status_code).first()
                status_tab = QtWidgets.QWidget(self)
                self.main_tab_widget.addTab(
                    status_tab,
                    get_cached_icon(status_code),
                    "{} ({})".format(status_code, status_codes_and_counts[status_code]),
                )
                # add a layout to this widget
                status_tab_layout = QtWidgets.QVBoxLayout()
                status_tab.setLayout(status_tab_layout)

                # add a TaskTableView to this status_tab
                task_table = TaskTableView(self)
                task_table_model = TaskTableModel(self)
                task_table.setModel(task_table_model)
                status_tab_layout.addWidget(task_table)

                tasks = (
                    Task.query
                    .filter(Task.project==self.project)
                    .filter(Task.resources.contains(self.user))
                    .filter(Task.status == status)
                    .all()
                )
                task_table_model.populate_table(tasks)
                task_table.resizeColumnsToContents()
