# -*- coding: utf-8 -*-
# Copyright (c) 2012-2015, Anima Istanbul
#
# This module is part of anima-tools and is released under the BSD 2
# License: http://www.opensource.org/licenses/BSD-2-Clause
import os
import shutil
from sqlalchemy import distinct
from stalker import db, Project, Task, Version

from anima.ui.lib import QtCore, QtGui
from anima.ui.base import AnimaDialogBase, ui_caller
from anima.ui.models import TaskTreeView, TaskTreeModel



def UI(app_in=None, executor=None, **kwargs):
    """
    :param environment: The
      :class:`~stalker.models.env.EnvironmentBase` can be None to let the UI to
      work in "environmentless" mode in which it only creates data in database
      and copies the resultant version file path to clipboard.

    :param app_in: A Qt Application instance, which you can pass to let the UI
      be attached to the given applications event process.

    :param executor: Instead of calling app.exec_ the UI will call this given
      function. It also passes the created app instance to this executor.
    """
    return ui_caller(app_in, executor, VersionMover, **kwargs)


class VersionMover(QtGui.QDialog, AnimaDialogBase):
    """Moves versions from one task to other.

    It is capable of moving the files or just copying and creating a new
    version instance.
    """

    def __init__(self, parent=None):
        super(VersionMover, self).__init__(parent)

        self.vertical_layout = None
        self.horizontal_layout = None
        self.horizontal_layout_2 = None
        self.from_task_tree_view = None
        self.to_task_tree_view = None
        self.copy_push_button = None

        self.setup_ui(self)

    def setup_ui(self, dialog):
        """Sets up the dialog

        :param dialog: QtGui.QDialog instance
        :return:
        """
        dialog.setObjectName("Dialog")
        dialog.setWindowModality(QtCore.Qt.ApplicationModal)
        dialog.resize(1200, 800)
        # layout vertical first
        self.vertical_layout = QtGui.QVBoxLayout(dialog)
        self.vertical_layout.setObjectName('verticalLayout1')

        self.horizontal_layout = QtGui.QHBoxLayout()

        self.from_task_tree_view = QtGui.QTreeView(dialog)
        self.from_task_tree_view.setObjectName("from_tasks_treeView")

        self.copy_push_button = QtGui.QPushButton(dialog)
        self.copy_push_button.setObjectName("copy_push_button")
        self.copy_push_button.setText('>')

        self.to_task_tree_view = TaskTreeView(dialog)
        self.to_task_tree_view.setObjectName("to_tasks_treeView")

        # self.horizontal_layout1.addWidget(self.from_task_tree_view)
        self.horizontal_layout.addWidget(self.from_task_tree_view)
        self.horizontal_layout.addWidget(self.copy_push_button)
        self.horizontal_layout.addWidget(self.to_task_tree_view)

        self.vertical_layout.addLayout(self.horizontal_layout)

        self.horizontal_layout_2 = QtGui.QHBoxLayout()
        self.horizontal_layout_2.setContentsMargins(-1, 10, -1, -1)
        self.horizontal_layout_2.setObjectName("horizontal_layout_2")

        self.vertical_layout.addLayout(self.horizontal_layout_2)

        QtCore.QMetaObject.connectSlotsByName(dialog)

        # initialize elements

        logged_in_user = self.get_logged_in_user()
        projects = Project.query.order_by(Project.name).all()

        task_tree_model = TaskTreeModel()
        task_tree_model.user = logged_in_user
        task_tree_model.populateTree(projects)

        # fit to elements
        self.from_tasks_tree_view_auto_fit_column()
        self.to_tasks_tree_view_auto_fit_column()

        self.from_task_tree_view.setModel(task_tree_model)
        self.to_task_tree_view.setModel(task_tree_model)

        # setup signals
        # tasks_treeView
        QtCore.QObject.connect(
            self.from_task_tree_view.selectionModel(),
            QtCore.SIGNAL('selectionChanged(const QItemSelection &, '
                          'const QItemSelection &)'),
            self.from_task_tree_view_changed
        )

        QtCore.QObject.connect(
            self.to_task_tree_view.selectionModel(),
            QtCore.SIGNAL('selectionChanged(const QItemSelection &, '
                          'const QItemSelection &)'),
            self.to_task_tree_view_changed
        )

        # fit column 0 on expand/collapse
        QtCore.QObject.connect(
            self.from_task_tree_view,
            QtCore.SIGNAL('expanded(QModelIndex)'),
            self.from_tasks_tree_view_auto_fit_column
        )

        QtCore.QObject.connect(
            self.to_task_tree_view,
            QtCore.SIGNAL('expanded(QModelIndex)'),
            self.to_tasks_tree_view_auto_fit_column
        )

        # copy_push_button
        QtCore.QObject.connect(
            self.copy_push_button,
            QtCore.SIGNAL("clicked()"),
            self.copy_versions
        )

    def from_tasks_tree_view_auto_fit_column(self):
        """fits columns to content
        """
        self.from_task_tree_view.resizeColumnToContents(0)

    def to_tasks_tree_view_auto_fit_column(self):
        """fits columns to content
        """
        self.to_task_tree_view.resizeColumnToContents(0)

    def from_task_tree_view_changed(self):
        """
        """
        pass

    def to_task_tree_view_changed(self):
        """
        """
        pass

    def get_task_from_tree_view(self, tree_view):
        """returns the task object from the given QTreeView
        """
        task = None
        selection_model = tree_view.selectionModel()

        indexes = selection_model.selectedIndexes()

        if indexes:
            current_index = indexes[0]

            item_model = tree_view.model()
            current_item = item_model.itemFromIndex(current_index)

            if current_item:
                try:
                    task = current_item.task
                except AttributeError:
                    pass

        return task

    def copy_versions(self):
        """copies versions from one task to another
        """
        # get from task
        from_task = self.get_task_from_tree_view(self.from_task_tree_view)

        # get logged in user
        logged_in_user = self.get_logged_in_user()

        if not from_task:
            QtGui.QMessageBox.critical(
                self,
                'Error',
                'Please select a task from <b>From Task</b> list'
            )
            return

        # get to task
        to_task = self.get_task_from_tree_view(self.to_task_tree_view)

        if not to_task:
            QtGui.QMessageBox.critical(
                self,
                'Error',
                'Please select a task from <b>To Task</b> list'
            )
            return

        # check if tasks are the same
        if from_task == to_task:
            QtGui.QMessageBox.critical(
                self,
                'Error',
                'Please select two different tasks'
            )
            return

        # get take names and related versions
        # get distinct take names
        from_take_names = map(
            lambda x: x[0],
            db.DBSession.query(distinct(Version.take_name))
            .filter(Version.task == from_task)
            .order_by(Version.take_name)
            .all()
        )

        # create versions for each take
        answer = QtGui.QMessageBox.question(
            self,
            'Info',
            "Will copy %s versions from take names:<br><br>"
            "%s"
            "<br><br>"
            "Is that Ok?" % (
                len(from_take_names),
                '<br>'.join(from_take_names)
            ),
            QtGui.QMessageBox.Yes,
            QtGui.QMessageBox.No
        )

        if answer == QtGui.QMessageBox.Yes:
            for take_name in from_take_names:
                latest_version = Version.query\
                    .filter_by(task=from_task)\
                    .filter_by(take_name=take_name)\
                    .order_by(Version.version_number.desc())\
                    .first()

                # create a new version
                new_version = Version(
                    task=to_task,
                    take_name=take_name
                )
                new_version.created_by = logged_in_user
                new_version.extension = latest_version.extension
                new_version.description = \
                    'Moved from another task (id=%s) with Version Mover' % \
                    latest_version.task.id
                new_version.created_with = latest_version.created_with
                db.DBSession.add(new_version)
                db.DBSession.commit()

                # update path
                new_version.update_paths()
                db.DBSession.add(new_version)
                db.DBSession.commit()

                # now copy the last_version file to the new_version path
                try:
                    os.makedirs(new_version.absolute_path)
                except OSError:  # path exists
                    pass

                # move the file there
                shutil.copyfile(
                    latest_version.absolute_full_path,
                    new_version.absolute_full_path
                )

            # inform the user
            QtGui.QMessageBox.information(
                self,
                'Success',
                'Successfully copied %s versions' % len(from_take_names)
            )


