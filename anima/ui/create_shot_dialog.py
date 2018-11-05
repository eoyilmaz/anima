# -*- coding: utf-8 -*-
# Copyright (c) 2012-2018, Anima Istanbul
#
# This module is part of anima-tools and is released under the BSD 2
# License: http://www.opensource.org/licenses/BSD-2-Clause
from anima.ui.base import ui_caller, AnimaDialogBase
from anima.ui.lib import QtWidgets, QtCore


def UI(app_in=None, executor=None, **kwargs):
    """
    :param app_in: A Qt Application instance, which you can pass to let the UI
      be attached to the given applications event process.

    :param executor: Instead of calling app.exec_ the UI will call this given
      function. It also passes the created app instance to this executor.

    """
    return ui_caller(app_in, executor, MainDialog, **kwargs)


class MainDialog(QtWidgets.QDialog, AnimaDialogBase):
    """A simple dialog for creating Shots in bulk.
    """

    # TODO: Make this configurable with config.py
    shot_child_task_defaults = {
        'Animation': {
            'schedule_timing': 1,
            'schedule_unit': 'd',
        },
        'Camera': {
            'schedule_timing': 10,
            'schedule_unit': 'min',
            'schedule_model': 'duration',
        },
        'Comp': {
            'schedule_timing': 1,
            'schedule_unit': 'h',
        },
        'Lighting': {
            'schedule_timing': 3,
            'schedule_unit': 'h',
        },
        'Mocap': {
            'schedule_timing': 1,
            'schedule_unit': 'h'
        },
        'Plate': {
            'schedule_timing': 10,
            'schedule_unit': 'min',
            'schedule_model': 'duration'
        },
        'Previs': {
            'schedule_timing': 10,
            'schedule_unit': 'min',
            'schedule_model': 'duration',
            'type_name': 'Shot Previs'
        },
        'Scene Assembly': {
            'schedule_timing': 1,
            'schedule_unit': 'h',
        },
    }

    def __init__(self, parent=None, project=None, parent_task=None):
        super(MainDialog, self).__init__(parent)

        self._setup()

    def _setup(self):
        """create UI elements
        """
        self.setWindowTitle("Create Shot Dialog")
        self.resize(550, 790)
        self.vertical_layout = QtWidgets.QVBoxLayout(self)

        # ----------------------------------------------
        # Dilog Label
        self.dialog_label = QtWidgets.QLabel(self)
        self.dialog_label.setText('Create Shot')
        self.dialog_label.setStyleSheet("color: rgb(71, 143, 202);font: 18pt;")
        self.vertical_layout.addWidget(self.dialog_label)

        # ----------------------------------------------
        # Title Line
        line = QtWidgets.QFrame(self)
        line.setFrameShape(QtWidgets.QFrame.HLine)
        line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.vertical_layout.addWidget(line)

        # ----------------------------------------------
        # Button Box
        self.buttonBox = QtWidgets.QDialogButtonBox(self)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(
            QtWidgets.QDialogButtonBox.Cancel | QtWidgets.QDialogButtonBox.Ok
        )
        self.vertical_layout.addWidget(self.buttonBox)

        # ----------------------------------------------
        # SIGNALS

        # button box
        QtCore.QObject.connect(
            self.buttonBox,
            QtCore.SIGNAL("accepted()"),
            self.accept
        )
        QtCore.QObject.connect(
            self.buttonBox,
            QtCore.SIGNAL("rejected()"),
            self.reject
        )
