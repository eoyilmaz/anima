# -*- coding: utf-8 -*-
# Copyright (c) 2012-2015, Anima Istanbul
#
# This module is part of anima-tools and is released under the BSD 2
# License: http://www.opensource.org/licenses/BSD-2-Clause
from anima import logger
from anima.env import empty_reference_resolution
from anima.ui.base import AnimaDialogBase, ui_caller
from anima.ui.models import VersionTreeModel
from anima.ui.lib import QtGui, QtCore
from anima.ui import IS_PYSIDE, IS_PYQT4


if IS_PYSIDE():
    from anima.ui.ui_compiled import version_updater_UI_pyside as version_updater_UI
elif IS_PYQT4():
    from anima.ui.ui_compiled import version_updater_UI_pyqt4 as version_updater_UI


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
    return ui_caller(app_in, executor, MainDialog, **kwargs)


class MainDialog(QtGui.QDialog, version_updater_UI.Ui_Dialog, AnimaDialogBase):
    """The main dialog of the version updater system

    The version_tuple list consist of a Version instance and a reference
    object.

    For Maya environment the reference object is the PyMel Reference node,
    for other environments reference object type will be as native as it can be
    """

    def __init__(self, environment=None, parent=None,
                 reference_resolution=None):
        super(MainDialog, self).__init__(parent)
        self.setupUi(self)

        # change the window title
        self.setWindowTitle(self.windowTitle())

        # center to the window
        self.center_window()

        self.new_versions = []

        # setup the environment
        self.environment = self._validate_environment(environment)

        if reference_resolution is None:
            # generate from environment
            if self.environment:
                reference_resolution = \
                    self.environment.check_referenced_versions()
            else:
                # create an empty one
                reference_resolution = empty_reference_resolution()
        self.reference_resolution = reference_resolution

        self.setup_signals()

        self._fill_UI()

    def _validate_environment(self, environment):
        """validates the given environment value
        """
        if environment:
            current_version = environment.get_current_version()
            if not current_version:
                # there is no version so warn the user
                error_message = 'Please save the current scene with Version ' \
                                'Creator first!!!'
                QtGui.QMessageBox.critical(
                    self,
                    "Error",
                    error_message,
                    QtGui.QMessageBox.Ok
                )
                self.close()
                raise RuntimeError(error_message)

        return environment

    def setup_signals(self):
        """sets up the signals
        """
        # SIGNALS
        # cancel button
        QtCore.QObject.connect(
            self.cancel_pushButton,
            QtCore.SIGNAL("clicked()"),
            self.close
        )

        # select all button
        QtCore.QObject.connect(
            self.selectAll_pushButton,
            QtCore.SIGNAL("clicked()"),
            self._select_all_versions
        )

        # select none button
        QtCore.QObject.connect(
            self.selectNone_pushButton,
            QtCore.SIGNAL("clicked()"),
            self._select_no_version
        )

        # update button
        QtCore.QObject.connect(
            self.update_pushButton,
            QtCore.SIGNAL("clicked()"),
            self.update_versions
        )

        # fit column 0 on expand/collapse
        QtCore.QObject.connect(
            self.versions_treeView,
            QtCore.SIGNAL('expanded(QModelIndex)'),
            self.versions_treeView_auto_fit_column
        )

        QtCore.QObject.connect(
            self.versions_treeView,
            QtCore.SIGNAL('collapsed(QModelIndex)'),
            self.versions_treeView_auto_fit_column
        )

        # custom context menu for the version_treeView
        self.versions_treeView.setContextMenuPolicy(
            QtCore.Qt.CustomContextMenu
        )

        QtCore.QObject.connect(
            self.versions_treeView,
            QtCore.SIGNAL("customContextMenuRequested(const QPoint&)"),
            self._show_versions_treeView_context_menu
        )

    def versions_treeView_auto_fit_column(self):
        """fits columns to content
        """
        self.versions_treeView.resizeColumnToContents(0)
        self.versions_treeView.resizeColumnToContents(1)
        self.versions_treeView.resizeColumnToContents(2)
        self.versions_treeView.resizeColumnToContents(3)
        self.versions_treeView.resizeColumnToContents(4)
        self.versions_treeView.resizeColumnToContents(5)
        self.versions_treeView.resizeColumnToContents(6)

    def fill_versions_treeView(self):
        """sets up the versions_treeView
        """
        logger.debug('start filling versions_treeView')
        logger.debug('creating a new model')

        version_tree_model = VersionTreeModel()
        version_tree_model.reference_resolution = self.reference_resolution

        # populate with all update items
        version_tree_model.populateTree(self.reference_resolution['root'])

        self.versions_treeView.setModel(version_tree_model)

        logger.debug('setting up signals for versions_treeView_changed')
        # versions_treeView
        # QtCore.QObject.connect(
        #     self.versions_treeView.selectionModel(),
        #     QtCore.SIGNAL('selectionChanged(const QItemSelection &, '
        #                   'const QItemSelection &)'),
        #     self.versions_treeView_changed
        # )

        self.versions_treeView.is_updating = False
        self.versions_treeView_auto_fit_column()
        logger.debug('finished filling versions_treeView')

    def _fill_UI(self):
        """fills the UI with the asset data
        """
        # set the row count
        self.fill_versions_treeView()

    def _select_all_versions(self):
        """selects all the versions in the tableWidget
        """
        version_tree_model = self.versions_treeView.model()
        for i in range(version_tree_model.rowCount()):
            index = version_tree_model.index(i, 0)
            version_item = version_tree_model.itemFromIndex(index)
            version_item.setCheckState(QtCore.Qt.Checked)

    def _select_no_version(self):
        """deselects all versions in the tableWidget
        """
        version_tree_model = self.versions_treeView.model()
        for i in range(version_tree_model.rowCount()):
            index = version_tree_model.index(i, 0)
            version_item = version_tree_model.itemFromIndex(index)
            version_item.setCheckState(QtCore.Qt.Unchecked)

    def _show_versions_treeView_context_menu(self, position):
        """the custom context menu for the versions_treeView
        """
        # convert the position to global screen position
        global_position = \
            self.versions_treeView.mapToGlobal(position)

        index = self.versions_treeView.indexAt(position)
        model = self.versions_treeView.model()

        # get the column 0 item which holds the Version instance
        # index = self.versions_treeView.model().index(index.row(), 0)
        item = model.itemFromIndex(index)
        logger.debug('itemAt(position) : %s' % item)

        if not item:
            return

        if not hasattr(item, 'version'):
            return

        version = item.version
        latest_published_version = None
        if version:
            latest_published_version = version.latest_published_version

        item_action = item.action

        # if item_action != 'create':
        #    return

        from stalker import Version
        if not isinstance(version, Version):
            return

        # create the menu
        menu = QtGui.QMenu()

        # Add "Open..." action
        # Always open the latest published version
        absolute_full_path = version.absolute_full_path
        if absolute_full_path:
            action = menu.addAction('Open...')
            if latest_published_version:
                action.version = latest_published_version
            else:
                action.version = version

        selected_action = menu.exec_(global_position)

        if selected_action:
            choice = selected_action.text()
            if choice == 'Open...':
                self.open_version(selected_action.version)

    def open_version(self, version):
        """opens the given version in a new environment

        :param version: :class:`~stalker.model.version.Version` instance.
        """
        import subprocess
        import platform

        platform_name = platform.system().lower()

        # store the latest published version
        prev_lpv = version.latest_published_version

        process = subprocess.Popen(
            [self.environment.executable[platform_name],
             version.absolute_full_path],
            stderr=subprocess.PIPE
        )

        # wait until the process finishes
        process.wait()

        # check the latest published version again
        next_lpv = version.latest_published_version

        if prev_lpv != next_lpv:
            # a new version has been created so tell the environment to update
            # the references to this version
            self.reference_resolution = \
                self.environment.check_referenced_versions()

            # and then refresh the UI
            self._fill_UI()

    def update_versions(self):
        """updates the versions if it is checked in the UI
        """
        reference_resolution = self.generate_reference_resolution()

        # send them back to environment
        try:
            self.environment.update_versions(reference_resolution)
        except RuntimeError as e:
            # display as a Error message and return without doing anything
            message_box = QtGui.QMessageBox(self)
            message_box.critical(
                self,
                "Error",
                str(e),
                QtGui.QMessageBox.Ok
            )
            return

        # close the interface
        self.close()

    def generate_reference_resolution(self):
        """Generates a new reference_resolution dictionary from the UI

        :return: dictionary
        """
        generated_reference_resolution = empty_reference_resolution()

        # append anything that is checked

        version_tree_model = self.versions_treeView.model()
        for i in range(version_tree_model.rowCount()):
            index = version_tree_model.index(i, 0)
            version_item = version_tree_model.itemFromIndex(index)
            if version_item.checkState() == QtCore.Qt.Checked:
                version = version_item.version
                generated_reference_resolution['update'].append(version)

        return generated_reference_resolution

    def show(self):
        """overridden show method
        """
        logger.debug('MainDialog.show is started')
        logged_in_user = self.get_logged_in_user()
        if not logged_in_user:
            self.close()
            return_val = None
        else:
            return_val = super(MainDialog, self).show()

        logger.debug('MainDialog.show is finished')
        return return_val
