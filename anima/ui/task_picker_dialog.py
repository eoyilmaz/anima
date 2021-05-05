# -*- coding: utf-8 -*-

from anima.ui.base import AnimaDialogBase, ui_caller
from anima.ui.lib import QtGui, QtCore, QtWidgets


def UI(app_in=None, executor=None, **kwargs):
    """
    :param app_in: A Qt Application instance, which you can pass to let the UI
      be attached to the given applications event process.

    :param executor: Instead of calling app.exec_ the UI will call this given
      function. It also passes the created app instance to this executor.

    """
    return ui_caller(app_in, executor, MainDialog, **kwargs)


class MainDialog(QtWidgets.QDialog, AnimaDialogBase):
    """The task picker dialog for easy task selection.

    This dialog is created to help users easily pick tasks in a complex task
    hierarchy.

    :param parent: The Qt dialog that is the parent of this one, None by
      default.

    :param project: The pre-selected project to show the tasks of.
    """

    def __init__(self, parent=None, project=None):
        super(MainDialog, self).__init__(parent)
        self._setup_ui()

        # create the custom task tree view

        from anima.ui.views.task import TaskTreeView
        self.tasks_tree_view = TaskTreeView(project=project)

        self.tasks_tree_view.replace_with_other(
            self.verticalLayout,
            0
        )

        self.tasks_tree_view.fill()

        # setup the double click signal
        QtCore.QObject.connect(
            self.tasks_tree_view,
            QtCore.SIGNAL('doubleClicked(QModelIndex)'),
            self.tasks_tree_view_double_clicked
        )

    def _setup_ui(self):
        self.resize(629, 567)
        self.verticalLayout = QtWidgets.QVBoxLayout(self)
        self.buttonBox = QtWidgets.QDialogButtonBox(self)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel | QtWidgets.QDialogButtonBox.Ok)
        self.verticalLayout.addWidget(self.buttonBox)

        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("accepted()"), self.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("rejected()"), self.reject)
        QtCore.QMetaObject.connectSlotsByName(self)

    def tasks_tree_view_double_clicked(self, model_index):
        """runs when double clicked on to a task

        :param model_index: QModelIndex
        :return:
        """
        # get the task
        task_id = None
        task_ids = self.tasks_tree_view.get_selected_task_ids()
        if task_ids:
            task_id = task_ids[0]
        from stalker import Task
        task = Task.query.get(task_id)
        # if the task is a leaf task then return it
        if task and task.is_leaf:
            self.accept()
