# -*- coding: utf-8 -*-
from stalker import User

from anima.ui.lib import QtCore, QtGui, QtWidgets

from anima.ui.utils import update_graphics_view_with_entity_thumbnail, get_cached_icon

if False:
    from PySide2 import QtCore, QtGui, QtWidgets


class UserPage(QtWidgets.QWidget):
    """User home page."""

    def __init__(self, *args, **kwargs):
        super(UserPage, self).__init__(*args, **kwargs)
        self.main_layout = None
        self.side_bar = None
        self._user = None
        self.setup()

    def setup(self):
        self.main_layout = QtWidgets.QHBoxLayout()
        self.setLayout(self.main_layout)
        self.side_bar = UserSideBar(parent=self)
        self.main_layout.addWidget(self.side_bar)

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
        self._user = user
        self.side_bar.user = user


class UserSideBar(QtWidgets.QWidget):
    """User side bar widget."""

    def __init__(self, *args, **kwargs):
        super(UserSideBar, self).__init__(*args, **kwargs)
        self.main_layout = None
        self.thumbnail_and_name_layout = None
        self.thumbnail_graphics_view = None
        self.name_label = None
        self.buttons_layout = None
        self.dashboard_button = None
        self._user = None
        self.setup()

    def setup(self):
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
        self.dashboard_button = QtWidgets.QPushButton(
            get_cached_icon("dashboard"), "Dashboard", parent=self
        )
        self.buttons_layout.addWidget(self.dashboard_button)

        # My Tasks
        self.my_tasks_button = QtWidgets.QPushButton(
            get_cached_icon("task"), "My Tasks", parent=self
        )
        self.buttons_layout.addWidget(self.my_tasks_button)

        # Responsible Of
        self.responsible_of_tasks_button = QtWidgets.QPushButton(
            get_cached_icon("task"), "Responsible Of", parent=self
        )
        self.buttons_layout.addWidget(self.responsible_of_tasks_button)

        # Watch List
        self.watch_list_button = QtWidgets.QPushButton(
            get_cached_icon("task"), "Watch List", parent=self
        )
        self.buttons_layout.addWidget(self.watch_list_button)

        # Tickets
        self.tickets_button = QtWidgets.QPushButton(
            get_cached_icon("ticket"), "Tickets", parent=self
        )
        self.buttons_layout.addWidget(self.tickets_button)

        # Timelogs

        # Reviews
        # Reports
        # Results
        # AuthLogs
        # Vacations
        # Efficiency
        # Versions
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

        # update the thumbnail
        if self._user.thumbnail:
            update_graphics_view_with_entity_thumbnail(
                self._user,
                self.thumbnail_graphics_view
            )

        # Update Name
        self.name_label.setText("{} {}".format(user.name, user.login))
