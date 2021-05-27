# -*- coding: utf-8 -*-


from anima.ui.lib import QtWidgets


class TaskStatusLabel(QtWidgets.QLabel):
    """A label for showing task statuses with color codes
    """

    status_colors = {
        'WFD': 'grey',
        'RTS': 'red',
        'WIP': 'orange',
        'HREV': 'purple',
        'DREV': 'dodgerblue',
        'STOP': 'red',
        'OH': 'red',
        'CMPL': 'green',
    }

    def __init__(self, task=None, **kwargs):
        super(TaskStatusLabel, self).__init__(**kwargs)
        self._task = None
        self.task = task

        self.setup_ui()

    def setup_ui(self):
        """setup the UI
        """
        # self.setMaximumWidth(75)
        # self.setMinimumWidth(75)
        self.setMaximumHeight(16)

        from anima.ui.lib import QtCore
        self.setAlignment(QtCore.Qt.AlignCenter)

    @property
    def task(self):
        return self._task

    @task.setter
    def task(self, task):
        """setter for the task property

        :param task: A Stalker Task instance
        :return:
        """
        from stalker import Task
        if isinstance(task, Task):
            self._task = task
            status_color = self.status_colors[self.task.status.code]
            self.setStyleSheet(
                """
                    background-color: %s;
                    color: white;
                    text-align: center;
                    padding-left: 0.5em;
                    padding-right: 0.5em;
                """ % status_color
            )
            self.setText(self.task.status.name)
        else:
            self._task = None
            self.setText('No Task')
            self.setStyleSheet(
                """
                    background-color: grey;
                    color: white;
                    text-align: center;
                    padding-left: 0.5em;
                    padding-right: 0.5em;
                """
            )
