# -*- coding: utf-8 -*-

from anima.base import Singleton


class ProgressCaller(object):
    """A simple object to hold caller data for ProgressDialogManager."""

    def __init__(self, max_steps=0, title=""):
        self.max_steps = max_steps
        self.title = title
        self.current_step = 0
        self.manager = None

    def step(self, step_size=1, message=""):
        """Shortcut for the ``ProgressDialogManager`` ``step`` method.

        Args:
            step_size (int): The step size.
            message (str): Message that appears on the progress dialog.
        """
        self.manager.step(self, step=step_size, message=message)

    def end_progress(self):
        """Shortcut for the ``ProgressDialogManager`` ``end_progress`` method."""
        self.manager.end_progress(self)


class ProgressDialogManager(object):
    """Wrapper for the QProgressDialog that can be called from multiple other code paths.

    This is a wrapper for the QProgressDialog window. It is able to track more than one
    process. The current usage is as follows::

      pm = ProgressDialogManager()

      # register a new caller which will have 100 steps
      caller = pm.register(100)

      for i in range(100):
          caller.step()

    So calling ``register`` will register a new caller for the progress window. The
    ProgressDialogManager will store the caller and will kill the QProgressDialog when
    all the callers are completed.
    """

    __metaclass__ = Singleton

    def __init__(self, parent=None, dialog=None):
        self.in_progress = False
        self.dialog = dialog
        self.callers = []

        if not hasattr(self, "use_ui"):
            # prevent resetting the use_ui to True
            self.use_ui = True

        self.parent = parent

        self.title = ""
        self.max_steps = 0
        self.current_step = 0

    def create_dialog(self):
        """Create the progress dialog."""
        if self.use_ui:
            if self.dialog is None:
                from anima.ui.lib import QtWidgets
                self.dialog = QtWidgets.QProgressDialog(self.parent)

            # QtGui.QProgressDialog(None, QtCore.Qt.WindowStaysOnTopHint)
            self.dialog.setRange(0, self.max_steps)
            self.dialog.setLabelText(self.title)
            self.dialog.setCancelButton(None)
            self.center_window()
            self.dialog.show()

        # also set the Manager to in progress
        self.in_progress = True

    def was_cancelled(self):
        """Check if cancelled.

        Returns:
            bool: True if cancelled or False otherwise.
        """
        if self.dialog:
            return self.dialog.wasCanceled()
        return False

    def close(self):
        """Kill the progress dialog."""
        if self.dialog is not None:
            self.dialog.close()
            self.dialog.deleteLater()

        # re initialize self
        self.__init__(parent=self.parent, dialog=self.dialog)

    def register(self, max_iteration, title=""):
        """Register a new caller.

        Args:
            max_iteration (int): Maximum number of expected steps.
            title (str): Dialog title.

        Returns:
            rbl_pipe_ui.blueprint.utils.ProgressCaller: A ProgressCaller instance.
        """
        caller = ProgressCaller(max_steps=max_iteration, title=title)
        caller.manager = self
        self.max_steps += max_iteration

        if self.use_ui:
            if not self.in_progress:
                self.create_dialog()
            else:
                # update the maximum
                if not self.dialog:
                    self.create_dialog()
                self.dialog.setRange(0, self.max_steps)
                self.dialog.setValue(self.current_step)

        # also store this
        self.callers.append(caller)
        return caller

    def center_window(self):
        """Center the dialog window to the screen."""
        if self.dialog is not None:
            from anima.ui.lib import QtGui, QtWidgets

            desktop = QtWidgets.QApplication.desktop()
            cursor_pos = QtGui.QCursor.pos()
            desktop_number = desktop.screenNumber(cursor_pos)
            desktop_rect = desktop.screenGeometry(desktop_number)

            size = self.dialog.geometry()

            if size:
                dr_width = desktop_rect.width()
                dr_left = desktop_rect.left()
                dr_height = desktop_rect.height()
                dr_top = desktop_rect.top()
                self.dialog.move(
                    (dr_width - size.width()) * 0.5 + dr_left,
                    (dr_height - size.height()) * 0.5 + dr_top,
                )

    def step(self, caller, step=1, message=""):
        """Increment the progress by the given amount.

        Args:
            caller (ProgressCaller): A :class:`.ProgressCaller` instance, generally
                returned by the :meth:`.register` method.
            step (int): The step size to increment, the default value is 1.
            message (str): The progress message as string.
        """
        caller.current_step += step
        self.current_step += step
        if self.dialog:
            self.dialog.setValue(self.current_step)
            self.dialog.setLabelText("{} : {}".format(caller.title, message))

        if caller.current_step >= caller.max_steps:
            # kill the caller
            self.end_progress(caller)

        if self.use_ui:
            from anima.ui.lib import QtWidgets

            try:
                qApp = QtWidgets.qApp
            except AttributeError:
                qApp = QtWidgets.QApplication

            if qApp:
                qApp.processEvents()

    def end_progress(self, caller):
        """End the progress for the given caller.

        Args:
            caller: A :class:`.ProgressCaller` instance.
        """
        # remove the caller from the callers list
        if caller in self.callers:
            self.callers.remove(caller)
            # also reduce the max_steps counter
            # in case of an early kill
            steps_left = caller.max_steps - caller.current_step
            if steps_left > 0:
                self.max_steps -= steps_left

        if not self.callers:
            self.close()
