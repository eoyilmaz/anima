# -*- coding: utf-8 -*-
from functools import partial

from anima.ui.lib import QtCore, QtGui, QtWidgets
from stalker import Project, Status, StatusList, Studio

if False:
    # this is for the IDE to pickup the code more easily
    from PySide2 import QtCore, QtGui, QtWidgets


class MainMenuBar(QtWidgets.QMenuBar):
    """Main application menu.

    Has similar options like Stalker Pyramid.
    """

    # signals
    list_clients_signal = QtCore.Signal()
    list_departments_signal = QtCore.Signal()
    list_groups_signal = QtCore.Signal()
    list_users_signal = QtCore.Signal()
    view_project_signal = QtCore.Signal(object)
    view_studio_signal = QtCore.Signal(object)
    view_user_signal = QtCore.Signal(object)

    def __init__(self, *args, **kwargs):
        super(MainMenuBar, self).__init__(*args, **kwargs)
        self.home_action = None
        self.studio_menu = None
        self.crew_menu = None
        self.users_action = None
        self.departments_action = None
        self.groups_action = None
        self.clients_action = None
        self.projects_menu = None
        self.setup()

    def setup(self):
        """Create the main application menu."""
        # Home Action
        self.home_action = self.addAction("Home")
        self.home_action.triggered.connect(partial(self.home_action_triggered))

        # Studio Menu
        self.studio_menu = self.addMenu("Studio")
        for studio in Studio.query.all():
            studio_action = self.studio_menu.addAction(studio.name)
            studio_action.triggered.connect(
                partial(self.view_studio_signal.emit, studio)
            )

        # Crew Menu
        self.crew_menu = self.addMenu("Crew")

        # Users
        self.users_action = self.crew_menu.addAction("Users")
        self.users_action.triggered.connect(self.list_users_signal.emit)

        # Departments
        self.departments_action = self.crew_menu.addAction("Departments")
        self.departments_action.triggered.connect(self.list_departments_signal.emit)

        # Groups
        self.groups_action = self.crew_menu.addAction("Groups")
        self.groups_action.triggered.connect(self.list_groups_signal.emit)

        # Clients
        self.clients_action = self.crew_menu.addAction("Clients")
        self.clients_action.triggered.connect(self.list_clients_signal.emit)

        # Projects Menu
        self.projects_menu = self.addMenu("Projects")
        # get all distinct project statuses
        project_status_list = StatusList.query.filter(
            StatusList.target_entity_type == "Project"
        ).first()
        for status in project_status_list.statuses:
            projects = (
                Project.query.filter(Project.status == status)
                .order_by(Project.name)
                .all()
            )
            if not projects:
                continue
            # create the status menu
            status_menu = self.projects_menu.addMenu(status.name)
            for project in projects:
                project_action = status_menu.addAction(project.name)
                assert isinstance(project_action, QtWidgets.QAction)
                project_action.triggered.connect(
                    partial(self.view_project_signal.emit, project)
                )

    def home_action_triggered(self):
        """Get the logged in user and emit a View User signal."""
        from stalker import LocalSession
        session = LocalSession()
        logged_in_user = session.logged_in_user
        self.view_user_signal.emit(logged_in_user)
