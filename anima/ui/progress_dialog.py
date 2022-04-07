# -*- coding: utf-8 -*-

from anima.ui.lib import QtGui, QtWidgets
from anima.utils.progress import ProgressDialogBase


class ProgressDialog(ProgressDialogBase, QtWidgets.QProgressDialog):
    """A ProgressDialog variant that uses QProgressDialog to show the progress."""

    def __init__(self, *args, **kwargs):
        ProgressDialogBase.__init__(self)
        QtWidgets.QProgressDialog.__init__(self, *args, **kwargs)
        self.setup_ui()

    def setup_ui(self):
        """Set the ui up."""
        self.setWindowFlag(QtGui.Qt.WindowStaysOnTopHint)
        self.setCancelButton(None)
        self.setMinimumDuration(0)

    def set_current_step(self, step):
        """Set the current step.

        Args:
            step (int): The current step value.
        """
        self.setValue(step)
        try:
            qApp = QtWidgets.qApp
        except AttributeError:
            qApp = QtWidgets.QApplication

        if qApp:
            qApp.processEvents()

    def set_range(self, min_range=0, max_range=100):
        """Set the minimum and maximum ranges.

        Args:
            min_range (int): The minimum step value, default is 0.
            max_range (int): The maximum step value, default is 100.
        """
        self.setRange(min_range, max_range)

    def set_title(self, title):
        """Set the title.

        Args:
            title (str): The title.
        """
        self.setLabelText(title)

    def was_cancelled(self):
        """Check if cancelled.

        Returns:
            bool: True if cancelled, False otherwise.
        """
        return self.wasCanceled()

    def center_window(self):
        """Center the dialog window to the screen."""
        desktop = QtWidgets.QApplication.desktop()
        cursor_pos = QtGui.QCursor.pos()
        desktop_number = desktop.screenNumber(cursor_pos)
        desktop_rect = desktop.screenGeometry(desktop_number)

        size = self.geometry()

        if size:
            dr_width = desktop_rect.width()
            dr_left = desktop_rect.left()
            dr_height = desktop_rect.height()
            dr_top = desktop_rect.top()
            self.move(
                (dr_width - size.width()) * 0.5 + dr_left,
                (dr_height - size.height()) * 0.5 + dr_top,
            )

    def show(self):
        """Display the dialog."""
        super(ProgressDialog, self).show()
        self.center_window()

    def close(self):
        """Close the dialog."""
        QtWidgets.QProgressDialog.close(self)
        self.deleteLater()
