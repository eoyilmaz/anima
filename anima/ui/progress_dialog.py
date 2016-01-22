# -*- coding: utf-8 -*-
# Copyright (c) 2012-2015, Anima Istanbul
#
# This module is part of anima-tools and is released under the BSD 2
# License: http://www.opensource.org/licenses/BSD-2-Clause
from anima.base import Singleton
from anima.ui.lib import QtCore, QtGui


class ProgressCaller(object):
    """A simple object to hold caller data for ProgressDialogManager
    """

    def __init__(self, max_steps=0, title=''):
        self.max_steps = max_steps
        self.title = title
        self.current_step = 0
        self.manager = None

    def step(self, step_size=1, message=''):
        """A shortcut for the ProgressDialogManager.step() method
        """
        self.manager.step(self, step=step_size, message=message)

    def end_progress(self):
        """A shortcut fro the ProgressDialogManager.end_progress() method
        """
        self.manager.end_progress(self)


class ProgressDialogManager(object):
    """A wrapper for the QtGui.QProgressDialog where it can be called from
    multiple other branches of the code.

    This is a wrapper for the QProgressDialog window. It is able to track more
    then one process. The current usage is as follows::

      pm = ProgressDialogManager()

      # register a new caller which will have 100 steps
      caller = pm.register(100)

      for i in range(100):
          caller.step()

    So calling ``register`` will register a new caller for the progress window.
    The ProgressDialogManager will store the caller and will kill the
    QProgressDialog when all of the callers are completed.
    """

    __metaclass__ = Singleton

    def __init__(self, parent=None):
        self.in_progress = False
        self.dialog = None
        self.callers = []

        if not hasattr(self, 'use_ui'):
            # prevent resetting the use_ui to True
            self.use_ui = True

        self.parent = parent

        self.title = ''
        self.max_steps = 0
        self.current_step = 0

    def create_dialog(self):
        """creates the progressWindow
        """
        if self.use_ui:
            if self.dialog is None:
                self.dialog = \
                    QtGui.QProgressDialog(self.parent)
                    # QtGui.QProgressDialog(None, QtCore.Qt.WindowStaysOnTopHint)
                # self.dialog.setMinimumDuration(2000)
                self.dialog.setRange(0, self.max_steps)
                self.dialog.setLabelText(self.title)
                # self.dialog.setAutoClose(True)
                # self.dialog.setAutoReset(True)
                self.center_window()
                self.dialog.show()

        # also set the Manager to in progress
        self.in_progress = True

    def close(self):
        """kills the progressWindow
        """
        if self.dialog is not None:
            self.dialog.close()

        # re initialize self
        self.__init__()

    def register(self, max_iteration, title=''):
        """registers a new caller

        :return: ProgressCaller instance
        """
        caller = ProgressCaller(max_steps=max_iteration, title=title)
        caller.manager = self
        self.max_steps += max_iteration

        if self.use_ui:
            if not self.in_progress:
                self.create_dialog()
            else:
                # update the maximum
                self.dialog.setRange(0, self.max_steps)
                self.dialog.setValue(self.current_step)
            # self. center_window()

        # also store this
        self.callers.append(caller)
        return caller

    def center_window(self):
        """recenters the dialog window to the screen
        """
        if self.dialog is not None:
            desktop = QtGui.QApplication.desktop()
            cursor_pos = QtGui.QCursor.pos()
            desktop_number = desktop.screenNumber(cursor_pos)
            desktop_rect = desktop.screenGeometry(desktop_number)

            size = self.dialog.geometry()

            self.dialog.move(
                (desktop_rect.width() - size.width()) * 0.5 + desktop_rect.left(),
                (desktop_rect.height() - size.height()) * 0.5 + desktop_rect.top()
            )

    def step(self, caller, step=1, message=''):
        """Increments the progress by the given mount

        :param caller: A :class:`.ProgressCaller` instance, generally returned
          by the :meth:`.register` method.
        :param step: The step size to increment, the default value is 1.
        """
        caller.current_step += step
        self.current_step += step
        if self.dialog:
            self.dialog.setValue(self.current_step)
            self.dialog.setLabelText('%s : %s' % (caller.title, message))
            # self.center_window()

        if caller.current_step >= caller.max_steps:
            # kill the caller
            self.end_progress(caller)

        QtGui.qApp.processEvents()

    def end_progress(self, caller):
        """Ends the progress for the given caller

        :param caller: A :class:`.ProgressCaller` instance
        :return: None
        """
        # remove the caller from the callers list
        if caller in self.callers:
            self.callers.remove(caller)
            # also reduce the max_steps counter
            # in case of an early kill
            steps_left = caller.max_steps - caller.current_step
            if steps_left > 0:
                self.max_steps -= steps_left

        if len(self.callers) == 0:
            self.close()
