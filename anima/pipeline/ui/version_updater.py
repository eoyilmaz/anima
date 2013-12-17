# -*- coding: utf-8 -*-
# Copyright (c) 2009-2012, Erkan Ozgur Yilmaz
# 
# This module is part of oyProjectManager and is released under the BSD 2
# License: http://www.opensource.org/licenses/BSD-2-Clause

from anima.pipeline.ui.utils import UICaller, AnimaDialogBase
from anima.pipeline.ui.lib import QtGui, QtCore
from anima.pipeline.ui import IS_PYSIDE, IS_PYQT4

if IS_PYSIDE():
    from anima.pipeline.ui.ui_compiled import version_updater_UI_pyside as version_updater_UI
elif IS_PYQT4():
    from anima.pipeline.ui.ui_compiled import version_updater_UI_pyqt4 as version_updater_UI


def UI(environment=None, app_in=None, executor=None):
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
    return UICaller(app_in, executor, MainDialog, environment=environment)


class MainDialog(QtGui.QDialog, version_updater_UI.Ui_Dialog, AnimaDialogBase):
    """The main dialog of the version updater system

    The version_tuple list consist of a Version instance and a reference
    object.

    For Maya environment the reference object is the PyMel Reference node,
    for other environments reference object type will be as native as it can be
    """

    def __init__(self, environment=None, parent=None):
        super(MainDialog, self).__init__(parent)
        self.setupUi(self)

        # change the window title
        self.setWindowTitle(self.windowTitle())

        # center to the window
        self.center_window()

        self._horizontalLabels = [
            'Parents',
            'Task',
            'Type',
            'Take',
            'Current',
            'Latest Published',
            'Do Update?'
        ]

        self.versions_tableWidget.setHorizontalHeaderLabels(
            self._horizontalLabels
        )
        self.versions_tableWidget.versions = []

        self.setup_signals()

        self._version_tuple_list = []
        self._num_of_versions = 0

        # setup the environment
        self.environment = environment

        self._do_env_read()
        self._fill_UI()

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

    def get_version_tuple_from_environment(self):
        """gets the references from environment

        returns a tuple consist of an asset and the environments representation
        of the asset
        """
        return self.environment.check_referenced_versions()

    @property
    def version_tuple_list(self):
        """returns the asset tuple list
        """
        return self._version_tuple_list

    @version_tuple_list.setter
    def version_tuple_list(self, version_tuple_list):
        """sets the asset tuple list
        """
        self._version_tuple_list = version_tuple_list
        self._num_of_versions = len(self._version_tuple_list)

    def _fill_UI(self):
        """fills the UI with the asset data
        """
        # set the row count
        self.versions_tableWidget.setRowCount(self._num_of_versions)
        self.versions_tableWidget.versions = []

        unpublished_versions = []

        for i, version_info in enumerate(self._version_tuple_list):
            version = version_info[0]
            # from stalker import Version
            # assert isinstance(version, Version)

            # TODO: there is a problem about unpublished versions
            latest_published_version = version.latest_published_version
            if latest_published_version is None:
                # just skip this one or at least warn the user
                unpublished_versions.append(version)
                continue

            # ------------------------------------
            # the parent names
            item = QtGui.QTableWidgetItem(version.nice_name)
            # align to left and vertical center
            item.setTextAlignment(
                QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter
            )
            self.versions_tableWidget.setItem(i, 0, item)

            # ------------------------------------
            # the task name
            item = QtGui.QTableWidgetItem(version.task.name)
            # align to left and vertical center
            item.setTextAlignment(
                QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter
            )
            self.versions_tableWidget.setItem(i, 0, item)

            #-------------------------------------
            # task entity type name
            item = QtGui.QTableWidgetItem(version.task.entity_type)
            # align to horizontal and vertical center
            item.setTextAlignment(
                QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter
            )
            self.versions_tableWidget.setItem(i, 1, item)

            #-------------------------------------
            # take name
            item = QtGui.QTableWidgetItem(version.take_name)
            # align to horizontal and vertical center
            item.setTextAlignment(
                QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter
            )
            self.versions_tableWidget.setItem(i, 2, item)

            # ------------------------------------
            # current version
            current_version_number = str(version.version_number)
            item = QtGui.QTableWidgetItem(current_version_number)
            # align to horizontal and vertical center
            item.setTextAlignment(
                QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter
            )
            self.versions_tableWidget.setItem(i, 3, item)

            # ------------------------------------
            # latest version
            latest_published_version_number = \
                str(version.latest_published_version.version_number)
            item = \
                QtGui.QTableWidgetItem(latest_published_version_number)
            # align to horizontal and vertical center
            item.setTextAlignment(
                QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter
            )
            self.versions_tableWidget.setItem(i, 4, item)
            # ------------------------------------

            # ------------------------------------
            # do update ?
            item = QtGui.QTableWidgetItem('')
            item.setTextAlignment(
                QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter
            )
            try:
                # for PyQt
                item.setCheckState(QtCore.Qt.Unchecked)
            except AttributeError:
                # for PyCharm
                item.setCheckState(0)
            self.versions_tableWidget.setItem(i, 5, item)
            # ------------------------------------

            self.versions_tableWidget.versions.append(version)

        if len(unpublished_versions):
            QtGui.QMessageBox.warning(
                self,
                "Warning",
                "The following references have no published versions:\n\n" +
                "\n".join([vers.filename for vers in unpublished_versions]) +
                "\n\nPlease publish them and re-open the current file.",
                QtGui.QMessageBox.Ok
            )

    def _do_env_read(self):
        """gets the asset tuple from env
        """
        self._version_tuple_list = self.get_version_tuple_from_environment()
        self._num_of_versions = len(self._version_tuple_list)

    def _select_all_versions(self):
        """selects all the versions in the tableWidget
        """
        for i in range(self.versions_tableWidget.rowCount()):
            item = self.versions_tableWidget.item(i, 5)
            item.setCheckState(QtCore.Qt.Checked)

    def _select_no_version(self):
        """deselects all versions in the tableWidget
        """
        for i in range(self.versions_tableWidget.rowCount()):
            item = self.versions_tableWidget.item(i, 5)
            item.setCheckState(QtCore.Qt.Unchecked)

    def update_versions(self):
        """updates the versions if it is checked in the UI
        """
        # get the marked versions from UI first
        marked_versions = self.get_marked_versions()

        # send them back to environment
        self.environment.update_versions(marked_versions)

        # close the interface
        self.close()

    def get_marked_versions(self):
        """returns the assets as tuple again, if it is checked in the interface
        """
        marked_version_list = []

        # find the marked versions
        for i in range(self._num_of_versions):
            checkBox_tableItem = self.versions_tableWidget.item(i, 5)

            if checkBox_tableItem.checkState() == QtCore.Qt.Checked:
                # get the ith number of the asset
                marked_version_list.append(self._version_tuple_list[i])

        return marked_version_list
