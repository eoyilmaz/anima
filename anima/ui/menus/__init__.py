# -*- coding: utf-8 -*-

from anima.ui.lib import QtCore, QtGui, QtWidgets
from stalker import Project, Status, StatusList, Studio

if False:
    # this is for the IDE to pickup the code more easily
    from PySide2 import QtCore, QtGui, QtWidgets


class MainMenuBar(QtWidgets.QMenuBar):
    """Main application menu.

    Has similar options like Stalker Pyramid.
    """

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
        self.home_action = self.addAction("Home")
        self.studio_menu = self.addMenu("Studio")
        for studio in Studio.query.all():
            self.studio_menu.addAction(studio.name)

        self.crew_menu = self.addMenu("Crew")
        self.users_action = self.crew_menu.addAction("Users")
        self.departments_action = self.crew_menu.addAction("Departments")
        self.groups_action = self.crew_menu.addAction("Groups")
        self.clients_action = self.crew_menu.addAction("Clients")

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
                # project_action.emit(b"ViewProject()", project)
