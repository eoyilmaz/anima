# -*- coding: utf-8 -*-
"""Shot related tools
"""

from anima.ui.lib import QtCore, QtWidgets


class Clip(object):
    """
    """
    pass


class PlateInjector(object):
    """injects/renders plates for the selected Sequence

    Generates render jobs that renders the VFX related clips in the current timeline to their respective shot folder.
    """

    def __init__(self):
        self.project = None
        self.sequence = None

    def inject(self, clip):
        """
        """
        pass


class PlateInjectorUI(QtWidgets.QDialog):
    """The UI for the PlateInjector
    """

    def __init__(self):
        self.setup_ui()

    def setup_ui(self):
        """sets the ui up
        """
        self.main_layout = QtWidgets.QVBoxLayout(self)
