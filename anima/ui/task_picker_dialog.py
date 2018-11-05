# -*- coding: utf-8 -*-
# Copyright (c) 2012-2018, Anima Istanbul
#
# This module is part of anima-tools and is released under the BSD 2
# License: http://www.opensource.org/licenses/BSD-2-Clause

from anima.ui.base import AnimaDialogBase, ui_caller
from anima.ui import IS_PYSIDE, IS_PYSIDE2, IS_PYQT4
from anima.ui.lib import QtGui, QtCore, QtWidgets


if IS_PYSIDE():
    from anima.ui.ui_compiled import task_picker_dialog_UI_pyside as task_picker_dialog_UI
elif IS_PYSIDE2():
    from anima.ui.ui_compiled import task_picker_dialog_UI_pyside2 as task_picker_dialog_UI
elif IS_PYQT4():
    from anima.ui.ui_compiled import task_picker_dialog_UI_pyqt4 as task_picker_dialog_UI


def UI(app_in=None, executor=None, **kwargs):
    """
    :param environment: The
      :class:`~stalker.models.env.EnvironmentBase` can be None to let the UI to
      work in "environmentless" mode in which it only creates data in database
      and copies the resultant version file path to clipboard.

    :param mode: Runs the UI either in Read-Write (0) mode or in Read-Only (1)
      mode.

    :param app_in: A Qt Application instance, which you can pass to let the UI
      be attached to the given applications event process.

    :param executor: Instead of calling app.exec_ the UI will call this given
      function. It also passes the created app instance to this executor.

    """
    return ui_caller(app_in, executor, MainDialog, **kwargs)


class MainDialog(QtWidgets.QDialog, task_picker_dialog_UI.Ui_Dialog, AnimaDialogBase):
    """The task picker dialog for easy task selection.

    This dialog is created to help users easily pick tasks in a complex task
    hierarchy.

    :param parent: The Qt dialog that is the parent of this one, None by
      default.

    :param project: The pre-selected project to show the tasks of.
    """

    def __init__(self, parent=None, project=None):
        super(MainDialog, self).__init__(parent)
        self.setupUi(self)

        # create the custom task tree view

        from anima.ui.views.task import TaskTreeView
        self.tasks_treeView = TaskTreeView(project=project)

        self.tasks_treeView.replace_with_other(
            self.verticalLayout,
            0
        )

        self.tasks_treeView.fill()

        # setup the double click signal
        QtCore.QObject.connect(
            self.tasks_treeView,
            QtCore.SIGNAL('doubleClicked(QModelIndex)'),
            self.tasks_tree_view_double_clicked
        )

    def tasks_tree_view_double_clicked(self, model_index):
        """runs when double clicked on to a task

        :param model_index: QModelIndex
        :return:
        """
        # get the task
        task_id = self.tasks_treeView.get_task_id()
        from stalker import Task
        task = Task.query.get(task_id)
        # if the task is a leaf task then return it
        if task and task.is_leaf:
            self.accept()
