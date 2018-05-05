# -*- coding: utf-8 -*-
# Copyright (c) 2018, Erkan  Ozgur Yilmaz
#
# This module is part of anima-tools and is released under the BSD 2
# License: http://www.opensource.org/licenses/BSD-2-Clause

from anima.ui.lib import QtCore, QtWidgets


class EntityNotesWidgets(QtWidgets.QWidget):
    """A widget to display entity notes
    """

    def __init__(self, entity=None, parent=None, **kwargs):
        self.entity = entity
        super(EntityNotesWidgets, self).__init__(parent=parent, **kwargs)

        self.note_widgets = []

        # storage for UI stuff
        self.vertical_layout = None

        self.setup_ui()
        self.fill_ui()

    def setup_ui(self):
        """creates the UI widgets
        """
        # the main layout
        self.vertical_layout = QtWidgets.QVBoxLayout(self)

    def fill_ui(self):
        """fill ui with the entity data
        """
        self._add_note_widgets()

    def _add_note_widgets(self):
        """simply adds the note widgets

        :return:
        """
        # store the note widget
        if self.entity:
            from anima.ui.widgets.note import NoteWidget
            for note in self.entity.notes:
                note_widget = NoteWidget(note=note, parent=self)
                self.note_widgets.append(note_widget)

                # also append it to the layout
                self.vertical_layout.addWidet(note_widget)
