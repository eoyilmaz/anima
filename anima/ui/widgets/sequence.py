# -*- coding: utf-8 -*-


from anima.ui.lib import QtWidgets


class SequenceComboBox(QtWidgets.QComboBox):
    """A QComboBox variant for Stalker Sequence instances
    """

    def __init__(self, parent, project=None, *args, **kwargs):
        kwargs['parent'] = parent
        super(SequenceComboBox, self).__init__(*args, **kwargs)
        self._project = None
        self.project = project
        self.__fill_ui()

    def __fill_ui(self):
        """fills the ui with project instances
        """
        if self.project is None:
            return

        from stalker import Sequence
        self.clear()
        for sequence in Sequence.query.filter(Sequence.project==self.project).order_by(Sequence.name).all():
            self.addItem(sequence.name, sequence.id)

    @property
    def project(self):
        """the getter for the project property
        """
        return self._project

    @project.setter
    def project(self, project):
        """setter for the project property

        :param project:
        :return:
        """
        from stalker import Project
        if project and not isinstance(project, Project):
            raise TypeError(
                "%s.project should be a Stalker Project instance, not %s" % (
                    self.__class__.__name__,
                    project.__class__.__name__
                )
            )

        self._project = project
        self.__fill_ui()

    def get_current_sequence(self):
        """returns the current sequence instance
        """
        sequence_id = self.itemData(self.currentIndex())
        from stalker import Sequence
        return Sequence.query.get(sequence_id)
