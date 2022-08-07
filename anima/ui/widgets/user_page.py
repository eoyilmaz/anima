# -*- coding: utf-8 -*-
from functools import partial

from stalker import User

from anima.ui.lib import QtCore, QtGui, QtWidgets

from anima.ui.utils import update_graphics_view_with_entity_thumbnail, get_cached_icon
from anima.ui.widgets.button import DashboardButton
from anima.ui.widgets.page import PageTitleWidget

if False:
    from PySide2 import QtCore, QtGui, QtWidgets


class UserPropertyMixin(object):

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
        """
        # validate the data first
        if not isinstance(user, User):
            raise TypeError(
                "{}.user should be a stalker.models.auth.User instance, not {}".format(
                    self.__class__.__name__, user.__class__.__name,
                )
            )
        self._user = user


class UserPageWidget(QtWidgets.QWidget, UserPropertyMixin):
    """User home page."""

    def __init__(self, *args, **kwargs):
        super(UserPageWidget, self).__init__(*args, **kwargs)
        UserPropertyMixin.__init__(self)
        self._setup()

    def _setup(self):
        self.main_layout = QtWidgets.QHBoxLayout()
        self.setLayout(self.main_layout)

        # Side Bar
        self.side_bar = UserSideBarWidget(parent=self)
        self.main_layout.addWidget(self.side_bar)

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
                self._user,
                self.thumbnail_graphics_view
            )

        # Update Name
        self.name_label.setText("\n".join(user.name.split(" ") + [user.login]))

    def emit_signal_and_user(self, *args):
        """Emit the given signal with the current user."""
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
        self.setLayout(self.main_layout)
        page_title = PageTitleWidget("Dashboard")
        self.main_layout.addWidget(page_title)


class UserTasksByStatus(QtWidgets.QWidget, UserPropertyMixin):
    """Display user tasks grouped by their statuses.

    This is a classic Stalker Pyramid widget implemented in Qt.
    Displays tasks in a TabWidget grouped by their statuses. Each Tab contains a
    TaskTable.
    """

    def __init__(self, *args, **kwargs):
        super(UserTasksByStatus, self).__init__(*args, **kwargs)
        UserPropertyMixin.__init__(self)
        self._setup()

    def _setup(self):
        self.main_layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.main_layout)


