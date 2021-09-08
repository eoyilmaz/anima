# -*- coding: utf-8 -*-


from anima.ui.lib import QtWidgets


class ProjectComboBox(QtWidgets.QComboBox):
    """A QComboBox variant for Stalker Project instances
    """

    def __init__(self, *args, **kwargs):
        super(ProjectComboBox, self).__init__(*args, **kwargs)
        self._show_active_projects = False
        self.__fill_ui()

    def __fill_ui(self):
        """fills the ui with project instances
        """
        from stalker import Project
        self.clear()

        # add the default item
        self.addItem("Select Project...", None)
        if self.show_active_projects:
            from stalker import Status
            cmpl = Status.query.filter(Status.code == 'CMPL').first()
            projects = Project.query.filter(Project.status != cmpl).all()
        else:
            projects = Project.query.order_by(Project.name).all()

        for project in projects:
            self.addItem(project.name, project.id)

    @property
    def show_active_projects(self):
        """getter for the self._show_active_projects property
        """
        return self._show_active_projects

    @show_active_projects.setter
    def show_active_projects(self, active_projects):
        """setter for the self._show_active_projects property

        :param bool active_projects:
        :return:
        """
        self._show_active_projects = bool(active_projects)
        self.__fill_ui()

    def get_current_project(self):
        """returns the current project instance
        """
        project_id = self.itemData(self.currentIndex())

        if project_id is not None:
            from stalker import Project
            return Project.query.get(project_id)
        else:
            return None
