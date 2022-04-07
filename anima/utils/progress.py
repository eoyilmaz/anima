# -*- coding: utf-8 -*-

from anima.base import Singleton


class ProgressDialogBase(object):
    """Base class for all the other ProgressDialog variants."""

    def __init__(self):
        self.title = ""
        self.current_step = 0
        self.min_range = 0
        self.max_range = 100

    def show(self):
        """Display the dialog."""
        return

    def set_current_step(self, step):
        """Set the current step.

        Args:
            step (int): The current step value.
        """
        self.current_step = step

    def set_range(self, min_range=0, max_range=100):
        """Set the minimum and maximum ranges.

        Args:
            min_range (int): The minimum step value, default is 0.
            max_range (int): The maximum step value, default is 100.
        """
        self.min_range = min_range
        self.max_range = max_range

    def set_title(self, title):
        """Set the title.

        Args:
            title (str): The title.
        """
        self.title = title

    def was_cancelled(self):
        """Check if cancelled.

        Returns:
            bool: True if cancelled, False otherwise.
        """
        return False

    def close(self):
        """Close the dialog."""
        return


class TerminalProgressPrinter(ProgressDialogBase):
    """Simple terminal progress printer."""

    def __init__(self, max_characters=30, progress_char="#"):
        super(TerminalProgressPrinter, self).__init__()
        self.max_characters = max_characters
        self.progress_char = progress_char

    def calculate_progress(self):
        """Calculate progress.

        Returns:
            str: The str representation of the progress.
        """
        denominator = float(self.max_range - self.min_range)
        nominator = float(self.current_step - self.min_range)
        rational_step = nominator / denominator
        progress_chars = (
            self.progress_char * int(rational_step * float(self.max_characters))
        ).ljust(self.max_characters)
        percent = rational_step * 100.0
        return "[{}]: {:>3.0f}%: {}  ".format(progress_chars, percent, self.title)

    def output_progress(self, end=""):
        """Print the progress."""
        print("{}\r".format(self.calculate_progress()), end=end)

    def show(self):
        """Display the dialog."""
        self.output_progress()

    def set_current_step(self, step):
        """Set the current step.

        Args:
            step (int): The current step value.
        """
        super(TerminalProgressPrinter, self).set_current_step(step)
        self.output_progress()

    def close(self):
        """Close the dialog."""
        self.output_progress(end="\n")


class ProgressCaller(object):
    """A simple object to hold caller data for ProgressManager."""

    def __init__(self, max_steps=0, title=""):
        self.max_steps = max_steps
        self.title = title
        self.current_step = 0
        self.manager = None

    def step(self, step_size=1, message=""):
        """Shortcut for the ``ProgressManager`` ``step`` method.

        Args:
            step_size (int): The step size.
            message (str): Message that appears on the progress dialog.
        """
        self.manager.step(self, step=step_size, message=message)

    def end_progress(self):
        """Shortcut for the ``ProgressManager`` ``end_progress`` method."""
        self.manager.end_progress(self)


class ProgressManager(object):
    """A Singleton class that manages progress.

    The main motivation of this class is to be able to manage the progress from
    different code paths, so it is able to track more than one process at the same time.
    The current usage is as follows::

      # create a ProgressDialogBase or derivative to display the progress
      pm = ProgressManager(dialog_class=ProgressDialog)

      # register a new caller which will have 100 steps
      caller = pm.register(100)

      for i in range(100):
          caller.step()

    So calling ``register`` will register a new caller for the progress window. The
    ProgressManager will store the caller and will kill the ProgressDialog when all the
    callers are completed.
    """

    __metaclass__ = Singleton

    def __init__(self, dialog_class=None):
        self.in_progress = False
        self._dialog = None
        if dialog_class is None:
            dialog_class = ProgressDialogBase
        self.dialog_class = dialog_class
        self.callers = []
        self.title = ""
        self.max_steps = 0
        self.current_step = 0

    @property
    def dialog(self):
        if not self._dialog:
            self.create_dialog()
        return self._dialog

    def create_dialog(self):
        """Create the progress dialog."""
        if self._dialog is None:
            self._dialog = self.dialog_class()

        self._dialog.set_range(0, self.max_steps)
        self._dialog.set_title(self.title)
        self._dialog.show()

        # also set the Manager to in progress
        self.in_progress = True

    def was_cancelled(self):
        """Check if cancelled.

        Returns:
            bool: True if cancelled or False otherwise.
        """
        if self.dialog:
            return self.dialog.was_cancelled()
        return False

    def register(self, max_iteration, title=""):
        """Register a new caller.

        Args:
            max_iteration (int): Maximum number of expected steps.
            title (str): Dialog title.

        Returns:
            anima.utils.progress.ProgressCaller: A ProgressCaller instance.
        """
        caller = ProgressCaller(max_steps=max_iteration, title=title)
        caller.manager = self
        self.max_steps += max_iteration

        # update the maximum
        if not self.dialog:
            self.create_dialog()

        self.dialog.set_range(0, self.max_steps)
        self.dialog.set_current_step(self.current_step)

        # also store this
        self.callers.append(caller)
        return caller

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
            self.dialog.set_current_step(self.current_step)
            self.dialog.set_title("{} : {}".format(caller.title, message))

        if caller.current_step >= caller.max_steps:
            # kill the caller
            self.end_progress(caller)

    def end_progress(self, caller=None):
        """End the progress for the given caller.

        Args:
            caller (ProgressCaller, None): A :class:`.ProgressCaller` instance.
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
            if self.dialog:
                self.dialog.close()
                self._dialog = None