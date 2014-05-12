# -*- coding: utf-8 -*-
# Copyright (c) 2012-2014, Anima Istanbul
#
# This module is part of anima-tools and is released under the BSD 2
# License: http://www.opensource.org/licenses/BSD-2-Clause
from anima.base import Singleton


class ProgressCaller(object):
    """A simple object to hold caller data for ProgressDialogManager
    """

    def __init__(self, max_iterations=0, title=''):
        self.max_iterations = max_iterations
        self.title = title
        self.current_step = 0
        self.manager = None

    def step(self, step_size=1, message=''):
        """A shortcut for the ProgressDialogManager.step() method
        :return:
        """
        self.manager.step(self, step=step_size, message=message)


class ProgressDialogManager(object):
    """A wrapper for the QtGui.QProgressDialog where it can be called from
    multiple other branches of the code.

    This is a wrapper for the QProgressDialog window. It is able to track more
    then one process. The current usage is as follows::

      pm = ProgressDialogManager()

      # register a new caller which will have 100 iterations
      caller = pm.register(100)

      for i in range(100):
          caller.step()

    So calling ``register`` will register a new caller for the progress window.
    The ProgressDialogManager will store the caller and will kill the
    QProgressDialog when all of the callers are completed.
    """

    __metaclass__ = Singleton

    def __init__(self):
        self.in_progress = False
        self.dialog = None
        self.callers = []

        self.title = ''
        self.max_iterations = 0
        self.current_step = 0

    def create_dialog(self):
        """creates the progressWindow
        """
        if self.dialog is None:
            print 'no dialog, creating one'
            from anima.ui.lib import QtGui
            self.dialog = QtGui.QProgressDialog()
            self.dialog.setRange(0, self.max_iterations)
            self.dialog.setLabelText(self.title)
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
        caller = ProgressCaller(max_iterations=max_iteration, title=title)
        caller.manager = self
        self.max_iterations += max_iteration

        if not self.in_progress:
            self.create_dialog()
        else:
            # update the maximum
            self.dialog.setRange(0, self.max_iterations)
            self.dialog.setValue(self.current_step)

        # also store this
        self.callers.append(caller)
        return caller

    def step(self, caller, step=1, message=''):
        """Increments the progress by the given mount

        :param caller: A :class:`.ProgressCaller` instance, generally returned
          by the :meth:`.register` method.
        :param step: The step size to increment, the default value is 1.
        """
        caller.current_step += step
        self.current_step += step
        self.dialog.setValue(self.current_step)
        self.dialog.setLabelText('%s : %s' % (caller.title, message))

        if caller.current_step == caller.max_iterations:
            # kill the caller
            self.end_progress(caller)

    def end_progress(self, caller):
        """Ends the progress for the given caller

        :param caller: A :class:`.ProgressCaller` instance
        :return: None
        """
        # remove the caller from the callers list
        self.callers.remove(caller)

        # check if there are still other callers
        if not len(self.callers):
            # remove the progress window
            self.close()