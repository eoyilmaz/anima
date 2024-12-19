# -*- coding: utf-8 -*-


from anima.ui.lib import QtWidgets


class SceneComboBox(QtWidgets.QComboBox):
    """A QComboBox variant for Stalker Scene instances"""

    def __init__(self, parent, sequence=None, *args, **kwargs):
        kwargs["parent"] = parent
        super(SceneComboBox, self).__init__(*args, **kwargs)
        self._sequence = None
        self.sequence = sequence
        self.fill_ui()

    def fill_ui(self):
        """fills the ui with sequence instances"""
        self.clear()
        if self.sequence is None:
            return

        for child in sorted(self.sequence.children, key=lambda x: x.name):
            if child.name.startswith("Scn"):
                scene = child
                self.addItem(scene.name, scene)

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
        from stalker import Sequence

        if sequence and not isinstance(sequence, Sequence):
            raise TypeError(
                "%s.sequence should be a Stalker Sequence instance, not %s"
                % (self.__class__.__name__, sequence.__class__.__name__)
            )

        self._sequence = sequence
        self.fill_ui()

    def get_current_scene(self):
        """returns the current scene instance"""
        return self.itemData(self.currentIndex())
