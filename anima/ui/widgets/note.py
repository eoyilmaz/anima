# -*- coding: utf-8 -*-

from anima.ui.lib import QtCore, QtGui, QtWidgets


class NoteWidget(QtWidgets.QWidget):
    """A widget for an individual Note entity"""

    def __init__(self, note=None, parent=None, **kwargs):
        self.note = note
        super(NoteWidget, self).__init__(parent=parent, **kwargs)

        # storage for UI stuff
        self.vertical_layout = None
        self.text = None

        self._setup_ui()
        self.fill_ui()

    def _setup_ui(self):
        """creates UI widgets"""
        self.vertical_layout = QtWidgets.QVBoxLayout(self)
        self.text = QtWidgets.QTextEdit(self)
        self.vertical_layout.addWidget(self.text)

    def fill_ui(self):
        """fill the ui"""
        if self.note:
            self.text.setText(self.note.content)
