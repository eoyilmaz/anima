# -*- coding: utf-8 -*-

from anima.ui.lib import QtCore, QtGui, QtWidgets

if False:
    from PySide2 import QtCore, QtGui, QtWidgets


class NoteWidget(QtWidgets.QWidget):
    """A widget for an individual Note entity"""

    bg_colors = {
        "": {
            "bg": QtGui.QColor(0x000000),
            "fg": QtGui.QColor(0xffffff),
        },
        "Request Review": {
            "bg": QtGui.QColor(0xffc657),
            "fg": QtGui.QColor(133, 93, 16),
        },
        "Request Revision": {
            "bg": QtGui.QColor(0x6f3cc4),
            "fg": QtGui.QColor(0xffffff),
        },
        "Forced Status": {
            "bg": QtGui.QColor(0xe2755f),
            "fg": QtGui.QColor(0xffffff),
        }
    }

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
        self.vertical_layout.setMargin(0)
        self.vertical_layout.setSpacing(0)

        # Title
        title_layout = QtWidgets.QHBoxLayout()
        title_layout.setMargin(0)
        self.vertical_layout.addLayout(title_layout)

        self.title_label = QtWidgets.QLabel(self)
        self.title_label.setContentsMargins(10, 0, 10, 0)
        self.title_label.setFixedHeight(31)

        self.date_created_label = QtWidgets.QLabel(self)
        self.date_created_label.setContentsMargins(10, 0, 10, 0)
        self.date_created_label.setMargin(0)
        self.date_created_label.setFixedHeight(31)
        title_layout.addWidget(self.title_label)
        title_layout.addWidget(self.date_created_label)

        # Content
        self.text = QtWidgets.QTextEdit(self)
        self.vertical_layout.addWidget(self.text)

        self.vertical_layout.setStretch(0, 0)
        self.vertical_layout.setStretch(1, 1)

    def fill_ui(self):
        """fill the ui"""
        if self.note:
            note_type_name = self.note.type.name if self.note.type else ""

            # =================
            # Title Label
            self.title_label.setText(note_type_name)
            self.title_label.setAutoFillBackground(True)

            # Make it bold
            font = self.title_label.font()
            font.setBold(True)
            self.title_label.setFont(font)

            # colorize
            palette = self.title_label.palette()
            palette.setColor(
                self.title_label.backgroundRole(),
                self.bg_colors.get(note_type_name, self.bg_colors[""])["bg"]
            )
            palette.setColor(
                self.title_label.foregroundRole(),
                self.bg_colors.get(note_type_name, self.bg_colors[""])["fg"]
            )
            self.title_label.setPalette(palette)

            # =================
            # Date
            date = self.note.date_created
            self.date_created_label.setText(
                "{:04d}-{:02d}-{:02d} {:02d}:{:02d}".format(
                    date.year,
                    date.month,
                    date.day,
                    date.hour,
                    date.minute
                )
            )

            # Colorize
            palette = self.date_created_label.palette()
            palette.setColor(
                self.title_label.backgroundRole(),
                self.bg_colors.get(note_type_name, self.bg_colors[""])["bg"]
            )
            palette.setColor(
                self.title_label.foregroundRole(),
                self.bg_colors.get(note_type_name, self.bg_colors[""])["fg"]
            )
            self.date_created_label.setPalette(palette)
            self.date_created_label.setAutoFillBackground(True)

            # =================
            # Text
            self.text.setText(self.note.content)
