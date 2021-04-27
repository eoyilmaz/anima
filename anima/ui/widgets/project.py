# -*- coding: utf-8 -*-


from anima.ui.lib import QtWidgets


class ProjectComboBox(QtWidgets.QComboBox):
    """A QComboBox variant for Stalker Project instances
    """

    def __init__(self, *args, **kwargs):
        super(ProjectComboBox, self).__init__(*args, **kwargs)

        self.__fill_ui()

    def __fill_ui(self):
        """fills the ui with project instances
        """
        from stalker import Project
        self.clear()
        for project in Project.query.order_by(Project.name).all():
            self.addItem(project.name, project.id)

    def get_current_project(self):
        """returns the current project instance
        """
        project_id = self.currentData()
        from stalker import Project
        return Project.query.get(project_id)
