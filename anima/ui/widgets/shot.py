# -*- coding: utf-8 -*-


from anima.ui.lib import QtWidgets

from stalker import Task, Sequence, Shot



class ShotComboBox(QtWidgets.QComboBox):
    """A QComboBox variant for Stalker Shot instances"""

    def __init__(self, parent, sequence=None, scene=None, *args, **kwargs):
        kwargs["parent"] = parent
        super(ShotComboBox, self).__init__(*args, **kwargs)
        self._sequence = None
        self.sequence = sequence
        self._scene = None
        self.scene = scene
        self.fill_ui()

    def fill_ui(self):
        """fills the ui with sequence instances"""
        self.clear()
        if self.sequence is None:
            return

        if self.scene is None:
            shots = (
                Shot.query.filter(Shot.sequences.contains(self.sequence))
                .order_by(Shot.name)
                .all()
            )
        else:
            shots_task = (
                Task.query
                .filter(Task.parent == self.scene)
                .filter(Task.name == "Shots")
                .first()
            )
            shots = list(
                Shot.query.filter(Shot.parent == shots_task).order_by(Shot.name).all()
            )

        for shot in shots:
            self.addItem(shot.name, shot)

    @property
    def sequence(self):
        """the getter for the sequence property"""
        return self._sequence

    @sequence.setter
    def sequence(self, sequence):
        """setter for the sequence property

        :param sequence:
        :return:
        """
        if sequence and not isinstance(sequence, Sequence):
            raise TypeError(
                "%s.sequence should be a Stalker Sequence instance, not %s"
                % (self.__class__.__name__, sequence.__class__.__name__)
            )

        self._sequence = sequence
        self.fill_ui()

    @property
    def scene(self):
        """the getter for the scene property"""
        return self._scene

    @scene.setter
    def scene(self, scene):
        """setter for the scene property

        :param scene:
        :return:
        """
        if scene and not isinstance(scene, Task):
            raise TypeError(
                "%s.scene should be a Stalker Task instance, not %s"
                % (self.__class__.__name__, scene.__class__.__name__)
            )

        self._scene = scene
        self.fill_ui()

    def get_current_shot(self):
        """returns the current shot instance"""
        return self.itemData(self.currentIndex())
