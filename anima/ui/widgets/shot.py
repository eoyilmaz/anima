# -*- coding: utf-8 -*-


from anima.ui.lib import QtWidgets


class ShotComboBox(QtWidgets.QComboBox):
    """A QComboBox variant for Stalker Shot instances"""

    def __init__(self, parent, sequence=None, *args, **kwargs):
        kwargs["parent"] = parent
        super(ShotComboBox, self).__init__(*args, **kwargs)
        self._sequence = None
        self.sequence = sequence
        self.fill_ui()

    def fill_ui(self):
        """fills the ui with sequence instances"""
        self.clear()
        if self.sequence is None:
            return

        from stalker import Shot

        for shot in (
            Shot.query.filter(Shot.sequence == self.sequence)
            .order_by(Shot.name)
            .all()
        ):
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
        from stalker import Sequence

        if sequence and not isinstance(sequence, Sequence):
            raise TypeError(
                "%s.sequence should be a Stalker Sequence instance, not %s"
                % (self.__class__.__name__, sequence.__class__.__name__)
            )

        self._sequence = sequence
        self.fill_ui()

    def get_current_shot(self):
        """returns the current shot instance"""
        return self.itemData(self.currentIndex())
