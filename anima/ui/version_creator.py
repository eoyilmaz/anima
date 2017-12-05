# -*- coding: utf-8 -*-
# Copyright (c) 2012-2017, Anima Istanbul
#
# This module is part of anima-tools and is released under the BSD 2
# License: http://www.opensource.org/licenses/BSD-2-Clause

import logging
import os
from collections import namedtuple

import anima
from anima import logger
from anima.ui.base import AnimaDialogBase, ui_caller
from anima.ui.lib import QtCore, QtGui, QtWidgets

from anima.ui.views.task import TaskTreeView
from anima.ui.widgets import TakesListWidget, RecentFilesComboBox
from anima.ui.widgets.version import VersionsTableWidget


ref_depth_res = [
    'As Saved',
    'All',
    'Top Level Only',
    'None'
]

VersionNT = namedtuple(
    # A named tuple for fast Version look-up
    'VersionNT',
    [
        'id',
        'version_number',
        'is_published',
        'created_with',
        'created_by_id',
        'updated_by_id',
        'full_path',
        'description'
    ]
)


# class RepresentationMessageBox(QtGui.QDialog, AnimaDialogBase):
#     """A message box variant
#     """
#
#     def __init__(self, parent=None):
#         super(RepresentationMessageBox, self).__init__(parent)
#         self.desired_repr = 'Base'
#
#     def _setup_ui_(self):
#         """generates default buttons
#         """
#         verticalLayout = QtGui.QVBoxLayout(self)
#         question_label =


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


class MainDialog(QtWidgets.QDialog, AnimaDialogBase):
    """The main version creation dialog for the pipeline.

    This is the main interface that the users of the ``anima`` will use to
    create a new :class:`~stalker.models.version.Version`\ s.

    It is possible to run the version_creator UI in read-only mode where the UI
    is created only for choosing previous versions. There will only be one
    button called "Choose" which returns the chosen Version instance.

    :param environment: It is an object which supplies **methods** like
      ``open``, ``save``, ``export``,  ``import`` or ``reference``. The most
      basic way to do this is to pass an instance of a class which is derived
      from the :class:`~stalker.models.env.EnvironmentBase` which has all this
      methods but produces ``NotImplementedError``\ s if the child class has
      not implemented these actions.

      The main duty of the Environment object is to introduce the host
      application (Maya, Houdini, Nuke, etc.) to the pipeline scripts and let
      it to open, save, export, import or reference a version file.

    **No Environment Interaction**

      The UI is able to handle the situation of not being bounded to an
      Environment. So if there is no Environment instance is given then the UI
      generates new Version instance and will allow the user to "copy" the full
      path of the newly generated Version. So environments which are not able
      to run Python code (Photoshop, ZBrush etc.) will also be able to
      contribute to projects.

    :param parent: The parent ``PySide.QtCore.QObject`` of this interface. It
      is mainly useful if this interface is going to be attached to a parent
      UI, like the Maya or Nuke.

    :param mode: Sets the UI in to Read-Write (mode=0) and Read-Only (mode=1)
      mode. Where in Read-Write there are all the buttons you would normally
      have (Export As, Save As, Open, Reference, Import), and in Read-Only mode
      it has only one button called "Choose" which lets you choose one Version.
    """

    def __init__(self, environment=None, parent=None, mode=0):
        logger.debug("initializing the interface")

        super(MainDialog, self).__init__(parent)
        self._setup_ui()

        self.mode = mode
        self.chosen_version = None
        self.environment_name_format = '%n (%e)'

        window_title = 'Version Creator | Anima v' + anima.__version__

        if environment:
            window_title = "%s | %s" % (window_title, environment.name)
        else:
            window_title = "%s | No Environment" % window_title

        if self.mode:
            window_title = "%s | Read-Only Mode" % window_title
        else:
            window_title = "%s | Normal Mode" % window_title

        # change the window title
        self.setWindowTitle(window_title)

        self.environment = environment
        if not self.environment.has_publishers:
            self.publish_pushButton.setText('Publish')

        # create the project attribute in projects_comboBox
        self.current_dialog = None

        # setup signals
        self._setup_signals()

        # setup defaults
        self._set_defaults()

        # center window
        self.center_window()

        logger.debug("finished initializing the interface")

    def _setup_ui(self):
        self.setWindowModality(QtCore.Qt.ApplicationModal)
        self.resize(1753, 769)
        size_policy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred,
                                           QtWidgets.QSizePolicy.Preferred)
        size_policy.setHorizontalStretch(1)
        size_policy.setVerticalStretch(1)
        size_policy.setHeightForWidth(
            self.sizePolicy().hasHeightForWidth())
        self.setSizePolicy(size_policy)
        self.setSizeGripEnabled(True)
        self.setModal(True)
        self.horizontalLayout = QtWidgets.QHBoxLayout(self)
        self.verticalWidget = QtWidgets.QWidget(self)
        size_policy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred,
                                           QtWidgets.QSizePolicy.Preferred)
        size_policy.setHorizontalStretch(1)
        size_policy.setVerticalStretch(1)
        size_policy.setHeightForWidth(
            self.verticalWidget.sizePolicy().hasHeightForWidth())
        self.verticalWidget.setSizePolicy(size_policy)
        self.verticalLayout = QtWidgets.QVBoxLayout(self.verticalWidget)
        self.verticalLayout.setSizeConstraint(
            QtWidgets.QLayout.SetMaximumSize)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_11 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_11.setContentsMargins(0, 0, 0, 0)
        spacerItem = QtWidgets.QSpacerItem(40, 20,
                                           QtWidgets.QSizePolicy.Expanding,
                                           QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_11.addItem(spacerItem)

        # Logged in As Label
        self.logged_in_as_label = QtWidgets.QLabel(self.verticalWidget)
        self.logged_in_as_label.setText("<b>Logged In As:</b>")
        self.logged_in_as_label.setTextFormat(QtCore.Qt.AutoText)
        self.horizontalLayout_11.addWidget(self.logged_in_as_label)

        # Logged in User Label
        self.logged_in_user_label = QtWidgets.QLabel(self.verticalWidget)
        self.horizontalLayout_11.addWidget(self.logged_in_user_label)

        self.logout_pushButton = QtWidgets.QPushButton(self.verticalWidget)
        self.horizontalLayout_11.addWidget(self.logout_pushButton)
        self.verticalLayout.addLayout(self.horizontalLayout_11)
        self.line_3 = QtWidgets.QFrame(self.verticalWidget)
        self.line_3.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_3.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.verticalLayout.addWidget(self.line_3)
        self.horizontalLayout_14 = QtWidgets.QHBoxLayout()
        self.tasks_groupBox = QtWidgets.QGroupBox(self.verticalWidget)
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.tasks_groupBox)
        self.verticalLayout_2.setContentsMargins(-1, 9, -1, -1)

        # Show My Tasks Only CheckBox
        self.my_tasks_only_checkBox =\
            QtWidgets.QCheckBox(self.tasks_groupBox)
        self.my_tasks_only_checkBox.setChecked(False)
        self.verticalLayout_2.addWidget(self.my_tasks_only_checkBox)

        # Show Completed Projects
        self.show_completed_checkBox =\
            QtWidgets.QCheckBox(self.tasks_groupBox)
        self.show_completed_checkBox.setText('Show Completed Projects')
        self.show_completed_checkBox.setChecked(False)
        self.verticalLayout_2.addWidget(self.show_completed_checkBox)


        self.horizontalLayout_4 = QtWidgets.QHBoxLayout()
        self.search_task_lineEdit = QtWidgets.QLineEdit(
            self.tasks_groupBox)
        self.horizontalLayout_4.addWidget(self.search_task_lineEdit)
        self.verticalLayout_2.addLayout(self.horizontalLayout_4)

        # self.tasks_tree_view = QtWidgets.QTreeView()
        self.tasks_tree_view = TaskTreeView(self.tasks_groupBox)
        self.tasks_tree_view.setEditTriggers(
            QtWidgets.QAbstractItemView.NoEditTriggers)
        self.tasks_tree_view.setAlternatingRowColors(True)
        self.tasks_tree_view.setUniformRowHeights(True)
        self.tasks_tree_view.header().setCascadingSectionResizes(True)
        self.verticalLayout_2.addWidget(self.tasks_tree_view)

        self.horizontalLayout_8 = QtWidgets.QHBoxLayout()

        self.recent_files_comboBox = RecentFilesComboBox(self.tasks_groupBox)
        self.horizontalLayout_8.addWidget(self.recent_files_comboBox)

        self.clear_recent_files_pushButton = QtWidgets.QPushButton(
            self.tasks_groupBox)
        self.horizontalLayout_8.addWidget(
            self.clear_recent_files_pushButton)
        self.horizontalLayout_8.setStretch(0, 1)
        self.verticalLayout_2.addLayout(self.horizontalLayout_8)
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.find_from_path_lineEdit = QtWidgets.QLineEdit(
            self.tasks_groupBox)
        self.horizontalLayout_3.addWidget(self.find_from_path_lineEdit)
        self.find_from_path_pushButton = QtWidgets.QPushButton(
            self.tasks_groupBox)
        self.find_from_path_pushButton.setDefault(True)
        self.horizontalLayout_3.addWidget(self.find_from_path_pushButton)
        self.verticalLayout_2.addLayout(self.horizontalLayout_3)
        self.thumbnail_graphicsView = QtWidgets.QGraphicsView(
            self.tasks_groupBox)
        size_policy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Fixed,
            QtWidgets.QSizePolicy.Fixed
        )
        size_policy.setHorizontalStretch(0)
        size_policy.setVerticalStretch(0)
        size_policy.setHeightForWidth(
            self.thumbnail_graphicsView.sizePolicy().hasHeightForWidth())
        self.thumbnail_graphicsView.setSizePolicy(size_policy)
        self.thumbnail_graphicsView.setMinimumSize(QtCore.QSize(320, 180))
        self.thumbnail_graphicsView.setMaximumSize(QtCore.QSize(320, 180))
        self.thumbnail_graphicsView.setAutoFillBackground(False)
        self.thumbnail_graphicsView.setVerticalScrollBarPolicy(
            QtCore.Qt.ScrollBarAlwaysOff)
        self.thumbnail_graphicsView.setHorizontalScrollBarPolicy(
            QtCore.Qt.ScrollBarAlwaysOff)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        self.thumbnail_graphicsView.setBackgroundBrush(brush)
        self.thumbnail_graphicsView.setInteractive(False)
        self.thumbnail_graphicsView.setRenderHints(
            QtGui.QPainter.Antialiasing |
            QtGui.QPainter.HighQualityAntialiasing |
            QtGui.QPainter.SmoothPixmapTransform |
            QtGui.QPainter.TextAntialiasing
        )
        self.verticalLayout_2.addWidget(self.thumbnail_graphicsView)
        self.horizontalLayout_16 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_16.setContentsMargins(-1, -1, -1, 10)
        spacer_item1 = QtWidgets.QSpacerItem(40, 20,
                                            QtWidgets.QSizePolicy.Expanding,
                                            QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_16.addItem(spacer_item1)
        self.upload_thumbnail_pushButton = QtWidgets.QPushButton(
            self.tasks_groupBox)
        self.horizontalLayout_16.addWidget(self.upload_thumbnail_pushButton)
        self.clear_thumbnail_pushButton = \
            QtWidgets.QPushButton(self.tasks_groupBox)
        self.horizontalLayout_16.addWidget(self.clear_thumbnail_pushButton)
        self.verticalLayout_2.addLayout(self.horizontalLayout_16)
        self.horizontalLayout_14.addWidget(self.tasks_groupBox)
        self.new_version_groupBox = QtWidgets.QGroupBox(self.verticalWidget)
        font = QtGui.QFont()
        font.setWeight(50)
        font.setBold(False)
        self.new_version_groupBox.setFont(font)
        self.verticalLayout_6 = \
            QtWidgets.QVBoxLayout(self.new_version_groupBox)
        self.verticalLayout_3 = QtWidgets.QVBoxLayout()
        self.horizontalLayout_9 = QtWidgets.QHBoxLayout()
        self.takes_label = QtWidgets.QLabel(self.new_version_groupBox)
        self.takes_label.setMinimumSize(QtCore.QSize(35, 0))
        font = QtGui.QFont()
        font.setWeight(50)
        font.setBold(False)
        self.takes_label.setFont(font)
        self.horizontalLayout_9.addWidget(self.takes_label)
        self.repr_as_separate_takes_checkBox = QtWidgets.QCheckBox(
            self.new_version_groupBox)
        self.horizontalLayout_9.addWidget(
            self.repr_as_separate_takes_checkBox)
        self.add_take_pushButton = QtWidgets.QPushButton(
            self.new_version_groupBox)
        self.horizontalLayout_9.addWidget(self.add_take_pushButton)
        self.horizontalLayout_9.setStretch(1, 1)
        self.verticalLayout_3.addLayout(self.horizontalLayout_9)
        self.horizontalLayout_6 = QtWidgets.QHBoxLayout()

        # =================
        # Takes List Widget
        self.takes_listWidget = TakesListWidget(self.new_version_groupBox)
        self.horizontalLayout_6.addWidget(self.takes_listWidget)

        self.verticalLayout_3.addLayout(self.horizontalLayout_6)
        self.description_label = QtWidgets.QLabel(self.new_version_groupBox)
        self.description_label.setMinimumSize(QtCore.QSize(35, 0))
        self.verticalLayout_3.addWidget(self.description_label)
        self.description_textEdit = QtWidgets.QTextEdit(
            self.new_version_groupBox
        )
        self.description_textEdit.setEnabled(True)
        self.description_textEdit.setTabChangesFocus(True)
        self.verticalLayout_3.addWidget(self.description_textEdit)
        self.verticalLayout_3.setStretch(1, 10)
        self.verticalLayout_3.setStretch(3, 3)
        self.verticalLayout_6.addLayout(self.verticalLayout_3)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.environment_comboBox = QtWidgets.QComboBox(
            self.new_version_groupBox
        )
        self.horizontalLayout_2.addWidget(self.environment_comboBox)
        self.export_as_pushButton = QtWidgets.QPushButton(
            self.new_version_groupBox
        )
        self.horizontalLayout_2.addWidget(self.export_as_pushButton)
        self.publish_pushButton = QtWidgets.QPushButton(
            self.new_version_groupBox
        )
        self.horizontalLayout_2.addWidget(self.publish_pushButton)
        self.save_as_pushButton = QtWidgets.QPushButton(
            self.new_version_groupBox
        )
        self.save_as_pushButton.setDefault(False)
        self.horizontalLayout_2.addWidget(self.save_as_pushButton)
        self.verticalLayout_6.addLayout(self.horizontalLayout_2)
        self.horizontalLayout_14.addWidget(self.new_version_groupBox)
        self.previous_versions_groupBox = QtWidgets.QGroupBox(
            self.verticalWidget)
        self.verticalLayout_7 = \
            QtWidgets.QVBoxLayout(self.previous_versions_groupBox)
        self.horizontalLayout_10 = QtWidgets.QHBoxLayout()
        self.show_only_label = \
            QtWidgets.QLabel(self.previous_versions_groupBox)
        self.horizontalLayout_10.addWidget(self.show_only_label)
        self.version_count_spinBox = \
            QtWidgets.QSpinBox(self.previous_versions_groupBox)
        self.version_count_spinBox.setMaximum(999999)
        self.version_count_spinBox.setProperty("value", 25)
        self.horizontalLayout_10.addWidget(self.version_count_spinBox)
        self.line = QtWidgets.QFrame(self.previous_versions_groupBox)
        self.line.setFrameShape(QtWidgets.QFrame.VLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.horizontalLayout_10.addWidget(self.line)
        self.show_published_only_checkBox = \
            QtWidgets.QCheckBox(self.previous_versions_groupBox)
        self.horizontalLayout_10.addWidget(self.show_published_only_checkBox)
        spacerItem2 = QtWidgets.QSpacerItem(40, 20,
                                            QtWidgets.QSizePolicy.Expanding,
                                            QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_10.addItem(spacerItem2)
        self.verticalLayout_7.addLayout(self.horizontalLayout_10)

        # previous_versions_tableWidget
        self.previous_versions_tableWidget = VersionsTableWidget(
            self.previous_versions_groupBox
        )

        self.previous_versions_tableWidget.setEditTriggers(
            QtWidgets.QAbstractItemView.NoEditTriggers)
        self.previous_versions_tableWidget.setAlternatingRowColors(True)
        self.previous_versions_tableWidget.setSelectionMode(
            QtWidgets.QAbstractItemView.SingleSelection)
        self.previous_versions_tableWidget.setSelectionBehavior(
            QtWidgets.QAbstractItemView.SelectRows)
        self.previous_versions_tableWidget.setShowGrid(False)
        self.previous_versions_tableWidget.setColumnCount(7)
        self.previous_versions_tableWidget.setRowCount(0)
        item = QtWidgets.QTableWidgetItem()
        self.previous_versions_tableWidget.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.previous_versions_tableWidget.setHorizontalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        self.previous_versions_tableWidget.setHorizontalHeaderItem(2, item)
        item = QtWidgets.QTableWidgetItem()
        self.previous_versions_tableWidget.setHorizontalHeaderItem(3, item)
        item = QtWidgets.QTableWidgetItem()
        self.previous_versions_tableWidget.setHorizontalHeaderItem(4, item)
        item = QtWidgets.QTableWidgetItem()
        self.previous_versions_tableWidget.setHorizontalHeaderItem(5, item)
        item = QtWidgets.QTableWidgetItem()
        self.previous_versions_tableWidget.setHorizontalHeaderItem(6, item)
        self.previous_versions_tableWidget\
            .horizontalHeader()\
            .setStretchLastSection(True)
        self.previous_versions_tableWidget\
            .verticalHeader()\
            .setStretchLastSection(False)
        self.verticalLayout_7.addWidget(self.previous_versions_tableWidget)
        self.horizontalLayout_5 = QtWidgets.QHBoxLayout()
        self.label = QtWidgets.QLabel(self.previous_versions_groupBox)
        self.horizontalLayout_5.addWidget(self.label)
        self.representations_comboBox = \
            QtWidgets.QComboBox(self.previous_versions_groupBox)
        self.horizontalLayout_5.addWidget(self.representations_comboBox)
        self.label_2 = QtWidgets.QLabel(self.previous_versions_groupBox)
        self.horizontalLayout_5.addWidget(self.label_2)
        self.ref_depth_comboBox = \
            QtWidgets.QComboBox(self.previous_versions_groupBox)
        self.horizontalLayout_5.addWidget(self.ref_depth_comboBox)
        spacerItem3 = QtWidgets.QSpacerItem(40, 20,
                                            QtWidgets.QSizePolicy.Expanding,
                                            QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_5.addItem(spacerItem3)
        self.useNameSpace_checkBox = \
            QtWidgets.QCheckBox(self.previous_versions_groupBox)
        self.useNameSpace_checkBox.setChecked(True)
        self.horizontalLayout_5.addWidget(self.useNameSpace_checkBox)
        self.chose_pushButton = \
            QtWidgets.QPushButton(self.previous_versions_groupBox)
        self.horizontalLayout_5.addWidget(self.chose_pushButton)
        self.checkUpdates_checkBox = \
            QtWidgets.QCheckBox(self.previous_versions_groupBox)
        self.checkUpdates_checkBox.setChecked(True)
        self.horizontalLayout_5.addWidget(self.checkUpdates_checkBox)
        self.open_pushButton = \
            QtWidgets.QPushButton(self.previous_versions_groupBox)
        self.horizontalLayout_5.addWidget(self.open_pushButton)
        self.reference_pushButton = \
            QtWidgets.QPushButton(self.previous_versions_groupBox)
        self.horizontalLayout_5.addWidget(self.reference_pushButton)
        self.import_pushButton = \
            QtWidgets.QPushButton(self.previous_versions_groupBox)
        self.horizontalLayout_5.addWidget(self.import_pushButton)
        self.close_pushButton = \
            QtWidgets.QPushButton(self.previous_versions_groupBox)
        self.close_pushButton.setStyleSheet("")
        self.horizontalLayout_5.addWidget(self.close_pushButton)
        self.verticalLayout_7.addLayout(self.horizontalLayout_5)
        self.horizontalLayout_14.addWidget(self.previous_versions_groupBox)
        self.horizontalLayout_14.setStretch(2, 1)
        self.verticalLayout.addLayout(self.horizontalLayout_14)
        self.horizontalLayout.addWidget(self.verticalWidget)

        self.setWindowTitle("Version Creator - Stalker")
        self.logout_pushButton.setText("Logout")
        self.tasks_groupBox.setTitle("Tasks")
        self.my_tasks_only_checkBox.setText("Show my tasks only")
        self.tasks_tree_view.setToolTip(
            "<html><head/><body><p>Right Click:</p><ul style=\""
            "margin-top: 0px; margin-bottom: 0px; margin-left: 0px; "
            "margin-right: 0px; -qt-list-indent: 1; "
            "\"><li style=\" margin-top:12px; margin-bottom:0px; "
            "margin-left:0px; margin-right:0px; -qt-block-indent:0; "
            "text-indent:0px;\">"
            "To go to the <span style=\" font-weight:600;\">"
            "Dependent Tasks</span></li><li style=\" margin-top:0px; "
            "margin-bottom:12px; margin-left:0px; margin-right:0px; "
            "-qt-block-indent:0; text-indent:0px;\">"
            "To go to the <span style=\" font-weight:600;\">"
            "Dependee Tasks</span></li></ul><p><br/></p></body></html>"
        )
        self.recent_files_comboBox.setToolTip("Recent Files")
        self.clear_recent_files_pushButton.setText("Clear")
        self.find_from_path_lineEdit.setPlaceholderText("Find From Path")
        self.find_from_path_pushButton.setText("Find")
        self.upload_thumbnail_pushButton.setText("Upload")
        self.clear_thumbnail_pushButton.setText("Clear")
        self.new_version_groupBox.setTitle("New Version")
        self.takes_label.setText("Take")
        self.repr_as_separate_takes_checkBox.setToolTip(
            "<html><head/><body><p>Check this to show "
            "<span style=\" font-weight:600;\">Representations</span> as "
            "separate takes if available</p></body></html>"
        )
        self.repr_as_separate_takes_checkBox.setText("Show Repr.")
        self.add_take_pushButton.setText("New Take")
        self.description_label.setText("Desc.")
        self.description_textEdit.setHtml(
            "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \""
            "http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
            "<html><head><meta name=\"qrichtext\" content=\"1\" />"
            "<style type=\"text/css\">\n"
            "p, li { white-space: pre-wrap; }\n"
            "</style></head><body style=\" font-family:\'MS Shell Dlg 2\'; "
            "font-size:8.25pt; font-weight:400; font-style:normal;\">\n"
            "<p style=\"-qt-paragraph-type:empty; margin-top:0px; "
            "margin-bottom:0px; margin-left:0px; margin-right:0px; "
            "-qt-block-indent:0; text-indent:0px; font-family:\'Sans Serif\'; "
            "font-size:9pt;\"><br /></p></body></html>",
        )
        self.export_as_pushButton.setText("Export Selection As")
        self.save_as_pushButton.setText("Save As")
        self.publish_pushButton.setText("Publish Checker")
        self.previous_versions_groupBox.setTitle("Previous Versions")
        self.show_only_label.setText("Show Only")
        self.show_published_only_checkBox.setText("Show Published Only")
        self.previous_versions_tableWidget.setToolTip(
            """
            <html>
            <head/>
            <body>
                <p>Right click to:</p>
                <ul style="margin-top: 0px;
                           margin-bottom: 0px;
                           margin-left: 0px;
                           margin-right: 0px;
                           -qt-list-indent: 1;">
                    <li>
                        <span style="font-weight:600;">Copy Path</span>
                    </li>

                    <li>
                        <span style="font-weight:600;">Browse Path</span>
                    </li>

                    <li>
                        <span style="font-weight:600;">Change Description</span>
                    </li>
                </ul>
                <p>Double click to:</p>
                <ul style="margin-top: 0px;
                           margin-bottom: 0px;
                           margin-left: 0px;
                           margin-right: 0px;
                           -qt-list-indent: 1;">
                    <li style="margin-top:12px;
                               margin-bottom:12px;
                               margin-left:0px;
                               margin-right:0px;
                               -qt-block-indent:0;
                               text-indent:0px;">
                        <span style=" font-weight:600;">Open</span>
                    </li>
                </ul>
            </body>
            </html>
            """
        )
        self.previous_versions_tableWidget.horizontalHeaderItem(0).setText(
            "Version"
        )
        self.previous_versions_tableWidget.horizontalHeaderItem(1).setText(
            "User"
        )
        self.previous_versions_tableWidget.horizontalHeaderItem(2).setText(
            "File Size"
        )
        self.previous_versions_tableWidget.horizontalHeaderItem(3).setText(
            "Date"
        )
        self.previous_versions_tableWidget.horizontalHeaderItem(4).setText(
            "Description"
        )
        self.label.setText("Repr")
        self.representations_comboBox.setToolTip(
            "Choose Representation (if supported by the environment)"
        )
        self.label_2.setText("Refs")
        self.ref_depth_comboBox.setToolTip(
            "Choose reference depth (if supported by environment)"
        )
        self.useNameSpace_checkBox.setToolTip(
            """
            <html>
                <head/>
                <body>
                    <p>Uncheck it if you are going to use 
                        <span style="font-weight:600;">Alembic Cache</span>.
                    </p>
                </body>
            </html>
            """
        )
        self.useNameSpace_checkBox.setText("Use Namespace")
        self.chose_pushButton.setText("Choose")
        self.checkUpdates_checkBox.setToolTip("Disable update check (faster)")
        self.checkUpdates_checkBox.setText("Check Updates")
        self.open_pushButton.setText("Open")
        self.reference_pushButton.setText("Reference")
        self.import_pushButton.setText("Import")
        self.close_pushButton.setText("Close")

        QtCore.QMetaObject.connectSlotsByName(self)
        self.setTabOrder(self.description_textEdit, self.export_as_pushButton)
        self.setTabOrder(self.export_as_pushButton, self.save_as_pushButton)
        self.setTabOrder(self.save_as_pushButton,
                         self.previous_versions_tableWidget)
        self.setTabOrder(self.previous_versions_tableWidget,
                         self.open_pushButton)
        self.setTabOrder(self.open_pushButton, self.reference_pushButton)
        self.setTabOrder(self.reference_pushButton, self.import_pushButton)

    # def close(self):
    #     logger.debug('closing the ui')
    #     QtWidgets.QDialog.close(self)

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

    def _setup_signals(self):
        """sets up the signals
        """
        logger.debug("start setting up interface signals")

        # close button
        QtCore.QObject.connect(
            self.close_pushButton,
            QtCore.SIGNAL("clicked()"),
            self.close
        )

        # logout button
        QtCore.QObject.connect(
            self.logout_pushButton,
            QtCore.SIGNAL("clicked()"),
            self.logout
        )

        # # my_tasks_only_checkBox
        # QtCore.QObject.connect(
        #     self.my_tasks_only_checkBox,
        #     QtCore.SIGNAL("stateChanged(int)"),
        #     self.my_tasks_only_check_box_changed
        # )

        # search for tasks
        # QtCore.QObject.connect(
        #     self.search_task_comboBox,
        #     QtCore.SIGNAL("editTextChanged(QString)"),
        #     self.search_task_comboBox_textChanged
        # )

        # # takes_listWidget
        # QtCore.QObject.connect(
        #     self.takes_listWidget,
        #     QtCore.SIGNAL("currentTextChanged(QString)"),
        #     self.takes_listWidget_changed
        # )

        # repr_as_separate_takes_checkBox
        QtCore.QObject.connect(
            self.repr_as_separate_takes_checkBox,
            QtCore.SIGNAL("stateChanged(int)"),
            self.tasks_tree_view_changed
        )

        # takes_listWidget
        QtCore.QObject.connect(
            self.takes_listWidget,
            QtCore.SIGNAL(
                "currentItemChanged(QListWidgetItem *, QListWidgetItem *)"),
            self.takes_listWidget_changed
        )

        # recent files comboBox
        QtCore.QObject.connect(
            self.recent_files_comboBox,
            QtCore.SIGNAL('currentIndexChanged(QString)'),
            self.recent_files_combo_box_index_changed
        )

        # find_from_path_lineEdit
        QtCore.QObject.connect(
            self.find_from_path_pushButton,
            QtCore.SIGNAL('clicked()'),
            self.find_from_path_push_button_clicked
        )

        # add_take_toolButton
        QtCore.QObject.connect(
            self.add_take_pushButton,
            QtCore.SIGNAL("clicked()"),
            self.add_take_push_button_clicked
        )

        # export_as
        QtCore.QObject.connect(
            self.export_as_pushButton,
            QtCore.SIGNAL("clicked()"),
            self.export_as_push_button_clicked
        )

        # save_as
        QtCore.QObject.connect(
            self.save_as_pushButton,
            QtCore.SIGNAL("clicked()"),
            self.save_as_push_button_clicked
        )

        # publish
        QtCore.QObject.connect(
            self.publish_pushButton,
            QtCore.SIGNAL("clicked()"),
            self.publish_push_button_clicked
        )

        # open
        QtCore.QObject.connect(
            self.open_pushButton,
            QtCore.SIGNAL("clicked()"),
            self.open_push_button_clicked
        )

        # chose
        QtCore.QObject.connect(
            self.chose_pushButton,
            QtCore.SIGNAL("cliched()"),
            self.chose_push_button_clicked
        )

        # reference
        QtCore.QObject.connect(
            self.reference_pushButton,
            QtCore.SIGNAL("clicked()"),
            self.reference_push_button_clicked
        )

        # import
        QtCore.QObject.connect(
            self.import_pushButton,
            QtCore.SIGNAL("clicked()"),
            self.import_pushButton_clicked
        )

        # show_only_published_checkBox
        QtCore.QObject.connect(
            self.show_published_only_checkBox,
            QtCore.SIGNAL("stateChanged(int)"),
            self.update_previous_versions_table_widget
        )

        # show_only_published_checkBox
        QtCore.QObject.connect(
            self.version_count_spinBox,
            QtCore.SIGNAL("valueChanged(int)"),
            self.update_previous_versions_table_widget
        )

        # upload_thumbnail_pushButton
        QtCore.QObject.connect(
            self.upload_thumbnail_pushButton,
            QtCore.SIGNAL("clicked()"),
            self.upload_thumbnail_push_button_clicked
        )

        # upload_thumbnail_pushButton
        QtCore.QObject.connect(
            self.clear_thumbnail_pushButton,
            QtCore.SIGNAL("clicked()"),
            self.clear_thumbnail_push_button_clicked
        )

        # close button
        QtCore.QObject.connect(
            self.clear_recent_files_pushButton,
            QtCore.SIGNAL("clicked()"),
            self.clear_recent_file_push_button_clicked
        )

        QtCore.QObject.connect(
            self.show_completed_checkBox,
            QtCore.SIGNAL("stateChanged(int)"),
            self.fill_tasks_tree_view
        )

        logger.debug("finished setting up interface signals")

    def fill_logged_in_user(self):
        """fills the logged in user label
        """
        logged_in_user = self.get_logged_in_user()
        if logged_in_user:
            self.logged_in_user_label.setText(logged_in_user.name)

    def logout(self):
        """log the current user out
        """
        from stalker import LocalSession
        lsession = LocalSession()
        lsession.delete()
        self.close()

    def _show_previous_versions_tableWidget_context_menu(self, position):
        """the custom context menu for the previous_versions_tableWidget
        """
        # convert the position to global screen position
        global_position = \
            self.previous_versions_tableWidget.mapToGlobal(position)

        item = self.previous_versions_tableWidget.itemAt(position)
        if not item:
            return

        index = item.row()
        version = self.previous_versions_tableWidget.versions[index]
        from stalker import Version
        version = Version.query.get(version.id)

        # create the menu
        menu = QtWidgets.QMenu()

        logged_in_user = self.get_logged_in_user()

        # add Browse Outputs
        menu.addAction("Browse Path...")
        menu.addAction("Browse Outputs...")
        menu.addAction("Upload Output...")
        menu.addAction("Copy Path")
        menu.addSeparator()

        if not self.mode:
            menu.addAction("Change Description...")
            menu.addSeparator()

        # Create power menu
        from anima import defaults
        if logged_in_user in version.task.responsible \
           or logged_in_user not in version.task.resources \
           or defaults.is_power_user(logged_in_user):
            if version.is_published:
                menu.addAction('Un-Publish')
            else:
                menu.addAction('Publish')
            menu.addSeparator()
            menu.addAction('Delete')

        selected_item = menu.exec_(global_position)

        if selected_item:
            choice = selected_item.text()
            if version:
                if choice == "Publish":
                    # publish it
                    version.is_published = True
                    version.updated_by = logged_in_user
                    from stalker.db.session import DBSession
                    DBSession.add(version)
                    DBSession.commit()
                    # refresh the tableWidget
                    self.update_previous_versions_table_widget()
                    return
                elif choice == "Un-Publish":
                    # allow the user un-publish this version if it is not used
                    # by any other versions
                    from stalker import Version
                    versions_using_this_versions = \
                        Version.query\
                               .filter(Version.inputs.contains(version))\
                               .all()

                    if len(versions_using_this_versions):
                        related_tasks = []
                        for v in versions_using_this_versions:
                            if v.task not in related_tasks:
                                related_tasks.append(v.task)

                        QtWidgets.QMessageBox.critical(
                            self,
                            'Error',
                            'This version is referenced by the following '
                            'tasks:<br><br>%s<br><br>'
                            'So, you can not un-publish it!' %
                            '<br>'.join(
                                map(
                                    lambda x: x.name,
                                    related_tasks
                                )
                            )
                        )
                    else:
                        version.is_published = False
                        version.updated_by = logged_in_user
                        from stalker.db.session import DBSession
                        DBSession.add(version)
                        DBSession.commit()
                        # refresh the tableWidget
                        self.update_previous_versions_table_widget()
                elif choice == 'Delete':
                    versions_using_this_versions = \
                        Version.query\
                               .filter(Version.inputs.contains(version))\
                               .all()
                    # if there are other versions using this version
                    # don't allow it to be deleted
                    if len(versions_using_this_versions):
                        related_tasks = []
                        for v in versions_using_this_versions:
                            if v.task not in related_tasks:
                                related_tasks.append(v.task)

                        QtWidgets.QMessageBox.critical(
                            self,
                            'Error',
                            'This version is referenced by the following '
                            'tasks:<br><br>%s<br><br>'
                            'So, you can not delete it!' %
                            '<br>'.join(
                                map(
                                    lambda x: x.name,
                                    related_tasks
                                )
                            )
                        )
                    else:
                        # Ask user if he/she is sure
                        answer = QtWidgets.QMessageBox.question(
                            self,
                            'Delete?',
                            "Delete the version?"
                            "<br>"
                            "<br>Files will not be deleted!",
                            QtWidgets.QMessageBox.Yes,
                            QtWidgets.QMessageBox.No
                        )
                        if answer == QtWidgets.QMessageBox.Yes:
                            from stalker.db.session import DBSession
                            # remove any parent data

                            try:
                                DBSession.delete(version)
                                DBSession.commit()
                            except Exception as e:
                                DBSession.rollback()
                                QtWidgets.QMessageBox.critical(
                                    self,
                                    'Error',
                                    str(e)
                                )
                            finally:
                                # refresh the tableWidget
                                self.update_previous_versions_table_widget()
                        else:
                            return

            from anima import utils
            if choice == 'Browse Path...':
                path = os.path.expandvars(
                    os.path.expandvars(
                        version.full_path
                    )
                )
                try:
                    utils.open_browser_in_location(path)
                except IOError:
                    QtWidgets.QMessageBox.critical(
                        self,
                        "Error",
                        "Path doesn't exists:\n%s" % path
                    )
            if choice == 'Browse Outputs...':
                path = os.path.join(
                    os.path.dirname(
                        os.path.expandvars(
                            version.full_path
                        )
                    ),
                    "Outputs"
                )
                try:
                    utils.open_browser_in_location(path)
                except IOError:
                    QtWidgets.QMessageBox.critical(
                        self,
                        "Error",
                        "Path doesn't exists:\n%s" % path
                    )
            elif choice == "Upload Output...":
                # upload output to the given version
                # show a file browser
                dialog = QtWidgets.QFileDialog(self, "Choose file")
                result = dialog.getOpenFileName()
                file_path = result[0]
                if file_path:
                    from anima.utils import MediaManager
                    with open(file_path) as f:
                        MediaManager.upload_version_output(
                            version, f, os.path.basename(file_path)
                        )
            elif choice == 'Change Description...':
                if version:
                    # change the description
                    self.current_dialog = QtWidgets.QInputDialog(parent=self)

                    new_description, ok = self.current_dialog.getText(
                        self,
                        "Enter the new description",
                        "Please enter the new description:",
                        QtWidgets.QLineEdit.Normal,
                        version.description
                    )

                    if ok:
                        # change the description of the version
                        version.description = new_description

                        from stalker.db.session import DBSession
                        DBSession.add(version)
                        DBSession.commit()

                        # update the previous_versions_tableWidget
                        self.update_previous_versions_table_widget()
            elif choice == 'Copy Path':
                # just set the clipboard to the version.absolute_full_path
                clipboard = QtWidgets.QApplication.clipboard()
                clipboard.setText(
                    os.path.normpath(
                        os.path.expandvars(
                            version.full_path
                        )
                    )
                )


    def get_item_indices_containing_text(self, text, treeView):
        """returns the indexes of the item indices containing the given text
        """
        model = treeView.model()
        logger.debug('searching for text : %s' % text)
        return model.match(
            model.index(0, 0),
            0,
            text,
            -1,
            QtCore.Qt.MatchRecursive
        )

    def find_entity_item_in_tree_view(self, entity, treeView):
        """finds the item related to the stalker entity in the given
        QtTreeView
        """
        if not entity:
            return None

        indexes = self.get_item_indices_containing_text(entity.name, treeView)
        model = treeView.model()
        logger.debug('items matching name : %s' % indexes)
        for index in indexes:
            item = model.itemFromIndex(index)
            if item:
                if item.task_id == entity.id:
                    return item
        return None

    def clear_recent_files(self):
        """clears the recent files
        """
        if self.environment:
            from anima.recent import RecentFileManager
            rfm = RecentFileManager()
            rfm[self.environment.name] = []
            rfm.save()

    def clear_recent_file_push_button_clicked(self):
        """clear the recent files
        """
        self.clear_recent_files()
        self.update_recent_files_combo_box()

    def update_recent_files_combo_box(self):
        """
        """
        self.recent_files_comboBox.setSizeAdjustPolicy(
            QtWidgets.QComboBox.AdjustToContentsOnFirstShow
        )
        self.recent_files_comboBox.setFixedWidth(250)

        self.recent_files_comboBox.clear()
        # update recent files list
        if self.environment:
            from anima.recent import RecentFileManager
            rfm = RecentFileManager()
            try:
                recent_files = rfm[self.environment.name]
                recent_files.insert(0, '')
                # append them to the comboBox

                for i, full_path in enumerate(recent_files[:50]):
                    parts = os.path.split(full_path)
                    filename = parts[-1]
                    self.recent_files_comboBox.addItem(
                        filename,
                        full_path,
                    )

                    self.recent_files_comboBox.setItemData(
                        i,
                        full_path,
                        QtCore.Qt.ToolTipRole
                    )

                # try:
                #     self.recent_files_comboBox.setStyleSheet(
                #         "qproperty-textElideMode: ElideNone"
                #     )
                # except:
                #     pass

                self.recent_files_comboBox.setSizePolicy(
                    QtWidgets.QSizePolicy.MinimumExpanding,
                    QtWidgets.QSizePolicy.Minimum
                )
            except KeyError:
                pass

    # def my_tasks_only_check_box_changed(self, state):
    #     """Runs when the my_tasks_only_checkBox state changed
    #
    #     :param state:
    #     :return:
    #     """
    #     # self.tasks_tree_view.user_tasks_only = bool(state)
    #     # self.fill_tasks_tree_view()

    def fill_tasks_tree_view(self, show_completed_projects=False):
        """wrapper for the tasks_treeView.fill() method
        """
        self.tasks_tree_view.fill(
            show_completed_projects=show_completed_projects
        )

        # also setup the signal
        logger.debug('setting up signals for tasks_treeView_changed')
        QtCore.QObject.connect(
            self.tasks_tree_view.selectionModel(),
            QtCore.SIGNAL('selectionChanged(const QItemSelection &, '
                          'const QItemSelection &)'),
            self.tasks_tree_view_changed
        )

    def tasks_tree_view_changed(self):
        """runs when the tasks_treeView item is changed
        """
        logger.debug('tasks_tree_view_changed running')
        if self.tasks_tree_view.is_updating:
            logger.debug('tasks_treeView is updating, so returning early')
            return

        task_id = self.tasks_tree_view.get_task_id()
        logger.debug('task_id : %s' % task_id)

        # update the thumbnail
        # TODO: do it in another thread
        self.clear_thumbnail()
        self.update_thumbnail()

        # get the versions of the entity
        takes = []

        if task_id:
            # clear the takes_listWidget and fill with new data
            logger.debug('clear takes widget')
            self.takes_listWidget.clear()

            from stalker import SimpleEntity
            from stalker.db.session import DBSession
            entity_type = DBSession\
                .query(SimpleEntity.entity_type)\
                .filter(SimpleEntity.id == task_id)\
                .first()

            if entity_type == "Project":
                return

            from stalker import Task
            from stalker.db.session import DBSession
            children_count = DBSession.query(Task.id)\
                .filter(Task.parent_id == task_id)\
                .count()

            if children_count == 0:
                from sqlalchemy import text
                sql = """SELECT
                    DISTINCT "Versions".take_name
                FROM "Versions"
                WHERE "Versions".task_id = :task_id
                """
                result = DBSession\
                    .connection()\
                    .execute(text(sql), task_id=task_id)\
                    .fetchall()

                takes = map(lambda x: x[0], result)

                if not self.repr_as_separate_takes_checkBox.isChecked():
                    # filter representations
                    from anima.repr import Representation
                    takes = [take for take in takes
                             if Representation.repr_separator not in take]
                takes = sorted(takes, key=lambda x: x.lower())

            logger.debug("len(takes) from db: %s" % len(takes))

            logger.debug("adding the takes from db")
            self.takes_listWidget.take_names = takes

    def _set_defaults(self):
        """sets up the defaults for the interface
        """
        logger.debug("started setting up interface defaults")

        # before doing anything create a QSplitter for:
        #   tasks_groupBox
        #   new_version_groupBox
        #   previous_versions_groupBox
        #
        # and add it under horizontalLayout_14

        splitter = QtWidgets.QSplitter()
        splitter.addWidget(self.tasks_groupBox)
        splitter.addWidget(self.new_version_groupBox)
        splitter.addWidget(self.previous_versions_groupBox)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 1)
        splitter.setStretchFactor(2, 2)
        self.horizontalLayout_14.addWidget(splitter)
        logger.debug('finished creating splitter')

        # set icon for search_task_toolButton
        # icon = QtGui.QApplication.style().standardIcon(QtWidgets.QStyle.SP_BrowserReload)
        # self.search_task_toolButton.setIcon(icon)

        # disable update_paths_checkBox
        # self.update_paths_checkBox.setVisible(False)

        # check login
        self.fill_logged_in_user()

        # clear the thumbnail area
        self.clear_thumbnail()

        # fill the tasks and show completed projects if check box is checked
        self.fill_tasks_tree_view(
            self.show_completed_checkBox.isChecked()
        )

        # reconnect signals
        # takes_listWidget
        QtCore.QObject.connect(
            self.takes_listWidget,
            QtCore.SIGNAL("currentTextChanged(QString)"),
            self.takes_listWidget_changed
        )

        # takes_listWidget
        QtCore.QObject.connect(
            self.takes_listWidget,
            QtCore.SIGNAL(
                "currentItemChanged(QListWidgetItem *, QListWidgetItem *)"),
            self.takes_listWidget_changed
        )
        # *********************************************************************

        # custom context menu for the previous_versions_tableWidget
        self.previous_versions_tableWidget.setContextMenuPolicy(
            QtCore.Qt.CustomContextMenu
        )

        QtCore.QObject.connect(
            self.previous_versions_tableWidget,
            QtCore.SIGNAL("customContextMenuRequested(const QPoint&)"),
            self._show_previous_versions_tableWidget_context_menu
        )

        if self.mode:
            # Read-Only mode, Choose the version
            # add double clicking to previous_versions_tableWidget
            QtCore.QObject.connect(
                self.previous_versions_tableWidget,
                QtCore.SIGNAL("cellDoubleClicked(int,int)"),
                self.chose_push_button_clicked
            )
        else:
            # Read-Write mode, Open the version
            # add double clicking to previous_versions_tableWidget
            QtCore.QObject.connect(
                self.previous_versions_tableWidget,
                QtCore.SIGNAL("cellDoubleClicked(int,int)"),
                self.open_push_button_clicked
            )
        # *********************************************************************
        # set the completer for the search_task_lineEdit
        # completer = TaskNameCompleter(self)
        # completer.setCaseSensitivity(QtCore.Qt.CaseInsensitive)
        # self.search_task_lineEdit.setCompleter(completer)
        # self.search_task_lineEdit.textChanged.connect(completer.update)
        #
        # completer.activated.connect(self.search_task_lineEdit.setText)
        # completer.setWidget(self.search_task_lineEdit)
        # # self.search_task_lineEdit.editingFinished.connect()
        self.search_task_lineEdit.setVisible(False)

        # fill programs list
        from anima.env.external import ExternalEnvFactory
        env_factory = ExternalEnvFactory()
        env_names = env_factory.get_env_names(
            name_format=self.environment_name_format
        )
        self.environment_comboBox.addItems(env_names)

        is_external_env = False
        env = self.environment
        if not self.environment:
            is_external_env = True
            # just get one random environment
            env = env_factory.get_env(env_names[0])

        # get all the representations available for this environment
        reprs = env.representations
        # add them to the representations comboBox
        for r in reprs:
            self.representations_comboBox.addItem(r)

        # add reference depth
        for r in ref_depth_res:
            self.ref_depth_comboBox.addItem(r)

        logger.debug("restoring the ui with the version from environment")

        # get the last version from the environment
        version_from_env = env.get_last_version()

        logger.debug("version_from_env: %s" % version_from_env)
        self.restore_ui(version_from_env)

        if is_external_env:
            # hide some buttons
            self.export_as_pushButton.setVisible(False)
            self.reference_pushButton.setVisible(False)
            self.import_pushButton.setVisible(False)
        else:
            self.environment_comboBox.setVisible(False)

        if self.mode:
            # run in read-only mode
            # hide buttons
            self.add_take_pushButton.setVisible(False)
            self.description_label.setVisible(False)
            self.description_textEdit.setVisible(False)
            self.export_as_pushButton.setVisible(False)
            self.save_as_pushButton.setVisible(False)
            self.publish_pushButton.setVisible(False)
            self.open_pushButton.setVisible(False)
            self.reference_pushButton.setVisible(False)
            self.import_pushButton.setVisible(False)
            self.upload_thumbnail_pushButton.setVisible(False)
            self.user_label.setVisible(False)
            self.shot_info_update_pushButton.setVisible(False)
            self.frame_range_label.setVisible(False)
            self.handles_label.setVisible(False)
            self.start_frame_spinBox.setVisible(False)
            self.end_frame_spinBox.setVisible(False)
            self.handle_at_end_spinBox.setVisible(False)
            self.handle_at_start_spinBox.setVisible(False)
        else:
            self.chose_pushButton.setVisible(False)

        # update description field
        self.description_textEdit.setText('')

        self.update_recent_files_combo_box()

        logger.debug("finished setting up interface defaults")

    def restore_ui(self, version):
        """Restores the UI with the given Version instance

        :param version: :class:`~oyProjectManager.models.version.Version`
          instance
        """
        logger.debug("restoring ui with the given version: %s", version)

        # quit if version is None
        if version is None or not version.task.project.active:
            return

        # set the task
        task = version.task

        found_task_item = self.tasks_tree_view.find_and_select_entity_item(task)
        if not found_task_item:
            return

        # take_name
        take_name = version.take_name
        self.takes_listWidget.current_take_name = take_name

        # select the version in the previous version list
        self.previous_versions_tableWidget.select_version(version)

        if not self.environment:
            # set the environment_comboBox
            from anima.env.external import ExternalEnvFactory
            env_factory = ExternalEnvFactory()
            try:
                env = env_factory.get_env(version.created_with)
            except ValueError:
                pass
            else:
                # find it in the comboBox
                index = \
                    self.environment_comboBox.findText(
                        env.name,
                        QtCore.Qt.MatchContains
                    )
                if index:
                    self.environment_comboBox.setCurrentIndex(index)

    def takes_listWidget_changed(self, index):
        """runs when the takes_listWidget has changed
        """
        logger.debug('takes_listWidget_changed started')
        # update the previous_versions_tableWidget
        self.update_previous_versions_table_widget()
        logger.debug('takes_listWidget_changed finished')

    def update_previous_versions_table_widget(self):
        """updates the previous_versions_tableWidget
        """
        logger.debug('update_previous_versions_table_widget is started')
        self.previous_versions_tableWidget.clear()

        from stalker import Task
        task_id = self.tasks_tree_view.get_task_id()
        if not task_id:  # or not isinstance(task, Task):
            return

        # do not display any version for a container task
        from stalker.db.session import DBSession
        children_count = DBSession\
            .query(Task.id)\
            .filter(Task.parent_id == task_id)\
            .count()
        if children_count > 0:
            # clear the versions list
            self.previous_versions_tableWidget.clear()
            return

        # take name
        take_name = self.takes_listWidget.current_take_name

        if take_name != '':
            logger.debug("take_name: %s" % take_name)
        else:
            return

        # query the Versions of this type and take
        from stalker import Version
        query = DBSession.query(
            # use only the necessary fields
            Version.id, Version.version_number,
            Version.is_published, Version.created_with,
            Version.created_by_id, Version.updated_by_id,
            Version.full_path,  # convert to absolute full path
            Version.description,
        )\
            .filter(Version.task_id == task_id) \
            .filter(Version.take_name == take_name)

        # get the published only
        if self.show_published_only_checkBox.isChecked():
            query = query.filter(Version.is_published == True)

        # show how many
        count = self.version_count_spinBox.value()

        data_from_db = \
            query.order_by(Version.version_number.desc()).limit(count).all()
        versions = map(lambda x: VersionNT(*x), data_from_db)
        versions.reverse()

        self.previous_versions_tableWidget.update_content(versions)
        logger.debug('update_previous_versions_table_widget is finished')

    def add_take_push_button_clicked(self):
        """runs when the add_take_toolButton clicked
        """
        # open up a QInputDialog and ask for a take name
        # anything is acceptable
        # because the validation will occur in the Version instance

        self.current_dialog = QtWidgets.QInputDialog(self)

        current_take_name = self.takes_listWidget.current_take_name

        take_name, ok = self.current_dialog.getText(
            self,
            "Add Take Name",
            "New Take Name",
            QtWidgets.QLineEdit.Normal,
            current_take_name
        )

        if ok:
            # add the given text to the takes_listWidget
            # if it is not empty
            if take_name != "":
                self.takes_listWidget.add_take(take_name)

    def get_new_version(self, publish=False):
        """returns a :class:`~oyProjectManager.models.version.Version` instance
        from the UI by looking at the input fields

        :returns: :class:`~oyProjectManager.models.version.Version` instance
        """
        # create a new version
        from stalker import Task
        task_id = self.tasks_tree_view.get_task_id()

        if not task_id:
            return None

        from stalker.db.session import DBSession
        with DBSession.no_autoflush:
            task = Task.query.get(task_id)

        # check if the task is a leaf task
        if not task.is_leaf:
            QtWidgets.QMessageBox.critical(
                self,
                'Error',
                'Please select a <strong>leaf</strong> task!'
            )
            return None

        take_name = self.takes_listWidget.current_take_name
        user = self.get_logged_in_user()
        if not user:
            self.close()

        description = self.description_textEdit.toPlainText()
        # published = self.publish_checkBox.isChecked()

        from stalker.db.session import DBSession
        from stalker import Version
        try:
            version = Version(
                task=task,
                created_by=user,
                take_name=take_name,
                description=description
            )
            version.is_published = publish
            DBSession.add(version)
        except (TypeError, ValueError) as e:
            # pop up an Message Dialog to give the error message
            try:
                error_message = '%s' % e
            except UnicodeEncodeError:
                error_message = unicode(e)
            QtWidgets.QMessageBox.critical(self, "Error", error_message)

            DBSession.rollback()
            return None

        # if everything went well return the new version
        return version

    def export_as_push_button_clicked(self):
        """runs when the export_as_pushButton clicked
        """
        logger.debug("exporting the data as a new version")

        # get the new version
        # exporting a published version is not allowed anymore
        new_version = self.get_new_version()

        if not new_version:
            return

        # call the environments export_as method
        if self.environment is not None:
            try:
                self.environment.export_as(new_version)
            except RuntimeError as e:
                error_message = '%s' % e
                print(error_message)
                QtWidgets.QMessageBox.critical(
                    self,
                    'Error',
                    error_message
                )
                from stalker.db.session import DBSession
                DBSession.rollback()
                return

            # inform the user about what has happened
            if logger.level != logging.DEBUG:
                QtWidgets.QMessageBox.information(
                    self,
                    "Export",
                    "%s\n\n has been exported correctly!" %
                    new_version.filename
                )

    def save_as_push_button_clicked(self):
        """runs when the save_as_pushButton clicked
        """
        logger.debug("saving the data as a new version")
        new_version = self.get_new_version()
        self.save_as_wrapper(new_version)

    def publish_push_button_clicked(self):
        """runs when the publish_pushButton clicked
        """
        logger.debug("saving the data as a new published version")
        answer = QtWidgets.QMessageBox.question(
            self,
            'Publish?',
            'Publish?',
            QtWidgets.QMessageBox.Yes,
            QtWidgets.QMessageBox.No
        )
        if answer == QtWidgets.QMessageBox.Yes:
            new_version = self.get_new_version(publish=True)
            if self.environment and self.environment.has_publishers:
                import functools
                callback = functools.partial(
                    self.save_as_wrapper,
                    version=new_version,
                    run_pre_publishers=False
                )
                # create the publish window
                from anima.ui import publish_checker
                self.close()
                dialog = publish_checker.UI(
                    environment=self.environment,
                    publish_callback=callback,
                    version=new_version
                )
                dialog.show()
                dialog.check_all_publishers()
            else:
                self.save_as_wrapper(new_version)
        else:
            return

    def save_as_wrapper(self, version, **kwargs):
        """The wrapper function that runs when save_as or publish push buttons
        are clicked

        :param version: A Stalker Version instance.
        :return:
        """
        # get the new version
        new_version = version

        # if we still don't have a version just return without doing anything
        if not new_version:
            return

        # call the environments save_as method
        from stalker.db.session import DBSession
        is_external_env = False
        environment = self.environment
        if not environment:
            # get the environment
            env_name = self.environment_comboBox.currentText()
            from anima.env.external import ExternalEnvFactory
            env_factory = ExternalEnvFactory()
            environment = env_factory.get_env(
                env_name,
                self.environment_name_format
            )
            is_external_env = True
            if not environment:
                logger.debug('no env found with name: %s' % env_name)
                DBSession.rollback()
                return
            logger.debug('env: %s' % environment.name)
        else:
            # check if the version the user is trying to create and the version
            # that is currently open in the current environment belongs to the
            # same task
            current_version = environment.get_current_version()
            if current_version and current_version.task != new_version.task:
            # ask to the user if he/she is sure about that
                answer = QtWidgets.QMessageBox.question(
                    self,
                    'Possible Mistake?',
                    "Saving under different Task<br>"
                    "<br>"
                    "current version: <b>%s</b><br>"
                    "new version    : <b>%s</b><br>"
                    "<br>"
                    "Are you sure?" % (
                        current_version.nice_name,
                        new_version.nice_name
                    ),
                    QtWidgets.QMessageBox.Yes,
                    QtWidgets.QMessageBox.No
                )

                if answer == QtWidgets.QMessageBox.No:
                    # no, just return
                    DBSession.rollback()
                    return

        from anima.exc import PublishError
        try:
            environment.save_as(new_version, **kwargs)
        except (RuntimeError, PublishError) as e:
            try:
                error_message = '%s' % e
            except UnicodeEncodeError:
                error_message = unicode(e)

            print(error_message)
            QtWidgets.QMessageBox.critical(
                self,
                'Error',
                error_message
            )

            DBSession.rollback()
            return

        if is_external_env:
            # set the clipboard to the new_version.absolute_full_path
            clipboard = QtWidgets.QApplication.clipboard()

            logger.debug(
                'new_version.absolute_full_path: %s' %
                new_version.absolute_full_path)

            v_path = os.path.normpath(new_version.absolute_full_path)
            clipboard.setText(v_path)

            # and warn the user about a new version is created and the
            # clipboard is set to the new version full path
            QtWidgets.QMessageBox.warning(
                self,
                "Path Generated",
                "A new Version is created at:\n\n%s\n\n"
                "And the path is copied to your clipboard!!!" % v_path,
                QtWidgets.QMessageBox.Ok
            )

        # check if the new version is pointing to a valid file
        # save the new version to the database
        from stalker import Version
        new_version = Version.query.get(new_version.id)
        if not os.path.exists(new_version.absolute_full_path):
            # raise an error
            QtWidgets.QMessageBox.critical(
                self,
                'Error',
                'Something went wrong with %s\n'
                'and the file is not created!\n\n'
                'Please save again!' % environment.name
            )
            DBSession.rollback()
        DBSession.commit()

        if is_external_env:
            # refresh the UI
            self.tasks_tree_view_changed()
        else:
            # close the UI
            self.close()

    def chose_push_button_clicked(self):
        """runs when the chose_pushButton clicked
        """
        version = self.previous_versions_tableWidget.current_version
        if not version:
            return

        version_id = version.id
        if not version_id:
            return

        from stalker import Version
        self.chosen_version = Version.query.get(version_id)

        if self.chosen_version:
            logger.debug(self.chosen_version.id)
            self.close()

    def open_push_button_clicked(self):
        """runs when the open_pushButton clicked
        """
        # get the new version
        old_version = self.previous_versions_tableWidget.current_version
        skip_update_check = not self.checkUpdates_checkBox.isChecked()

        from stalker import Version
        old_version = Version.query.get(old_version.id)

        if not self.check_version_file_exists(old_version):
            return

        # call the environments open method
        if self.environment is not None:
            repr_name = self.representations_comboBox.currentText()
            ref_depth = ref_depth_res.index(
                self.ref_depth_comboBox.currentText()
            )

            # environment can throw RuntimeError for unsaved changes
            try:
                reference_resolution = \
                    self.environment.open(
                        old_version,
                        representation=repr_name,
                        reference_depth=ref_depth,
                        skip_update_check=skip_update_check
                    )
            except RuntimeError as e:
                # pop a dialog and ask if the user really wants to open the
                # file

                answer = QtWidgets.QMessageBox.question(
                    self,
                    'RuntimeError',
                    "There are <b>unsaved changes</b> in the current "
                    "scene<br><br>Do you really want to open the file?",
                    QtWidgets.QMessageBox.Yes,
                    QtWidgets.QMessageBox.No
                )

                if answer == QtWidgets.QMessageBox.Yes:
                    reference_resolution =\
                        self.environment.open(
                            old_version,
                            True,
                            representation=repr_name,
                            reference_depth=ref_depth,
                            skip_update_check=skip_update_check
                        )
                else:
                    # no, just return
                    return

            # check the reference_resolution to update old versions
            if reference_resolution['create'] \
               or reference_resolution['update']:
                # invoke the version_updater for this scene
                from anima.ui import version_updater
                version_updater_main_dialog = \
                    version_updater.MainDialog(
                        environment=self.environment,
                        parent=self,
                        reference_resolution=reference_resolution
                    )

                version_updater_main_dialog.exec_()

        # close the dialog
        self.close()

    def check_version_file_exists(self, version):
        """Checks if the version file exists in the file system

        :param version: A Stalker Version instance
        :return:
        """
        if not os.path.exists(version.absolute_full_path):
            # the file doesn't exist
            # warn the user
            QtWidgets.QMessageBox.critical(
                self,
                "File Doesn't Exist!",
                "File doesn't exist!:<br><br>%s" %
                version.absolute_full_path
            )
            return False
        return True

    def reference_push_button_clicked(self):
        """runs when the reference_pushButton clicked
        """
        # get the new version
        previous_version = self.previous_versions_tableWidget.current_version

        # allow only published versions to be referenced
        if not previous_version.is_published:
            QtWidgets.QMessageBox.critical(
                self,
                "Critical Error",
                "Referencing <b>un-published versions</b> are only "
                "allowed for Power Users!\n"
                "Please reference a published version of the same Asset/Shot",
                QtWidgets.QMessageBox.Ok
            )
            return

        from stalker import Version
        previous_version = Version.query.get(previous_version.id)

        if not self.check_version_file_exists(previous_version):
            return

        logger.debug("referencing version with id: %s" % previous_version.id)
        # call the environments reference method
        if self.environment is not None:
            # get the use namespace state
            use_namespace = self.useNameSpace_checkBox.isChecked()

            # check if it has any representations
            # .filter(Version.parent == previous_version)\
            all_repr_count = Version.query\
                .filter(Version.task == previous_version.task)\
                .filter(Version.take_name.ilike(previous_version.take_name + '@%'))\
                .count()

            if all_repr_count > 0:
                # ask which one to reference
                repr_message_box = QtWidgets.QMessageBox()
                repr_message_box.setText('Which Repr.?')
                from anima.repr import Representation
                base_button = \
                    repr_message_box.addButton(
                        Representation.base_repr_name,
                        QtWidgets.QMessageBox.ActionRole
                    )
                setattr(base_button, 'repr_version', previous_version)

                for repr_name in self.environment.representations:
                    repr_str = '%{take}{repr_separator}{repr_name}%'.format(
                        take=previous_version.take_name,
                        repr_name=repr_name,
                        repr_separator=Representation.repr_separator
                    )
                    repr_version = Version.query\
                        .filter(Version.task == previous_version.task)\
                        .filter(Version.take_name.ilike(repr_str))\
                        .order_by(Version.version_number.desc())\
                        .first()

                    if repr_version:
                        repr_button = repr_message_box.addButton(
                            repr_name,
                            QtWidgets.QMessageBox.ActionRole
                        )
                        setattr(repr_button, 'repr_version', repr_version)

                # add a cancel button
                cancel_button = repr_message_box.addButton(
                    'Cancel',
                    QtWidgets.QMessageBox.RejectRole
                )

                repr_message_box.exec_()
                clicked_button = repr_message_box.clickedButton()
                if clicked_button.text() != 'Cancel':
                    if clicked_button.repr_version:
                        previous_version = clicked_button.repr_version
                else:
                    return

            try:
                self.environment.reference(previous_version, use_namespace)

                # inform the user about what happened
                if logger.level != logging.DEBUG:
                    QtWidgets.QMessageBox.information(
                        self,
                        "Reference",
                        "%s\n\n has been referenced correctly!" %
                        previous_version.filename,
                        QtWidgets.QMessageBox.Ok
                    )
            except RuntimeError as e:
                QtWidgets.QMessageBox.critical(
                    self,
                    "Error",
                    e.message
                )

    def import_pushButton_clicked(self):
        """runs when the import_pushButton clicked
        """
        # get the previous version
        previous_version_id = \
            self.previous_versions_tableWidget.current_version.id

        from stalker import Version
        previous_version = Version.query.get(previous_version_id)

        if not self.check_version_file_exists(previous_version):
            return

        # logger.debug("importing version %s" % previous_version)

        # call the environments import_ method
        if self.environment is not None:
            # get the use namespace state
            use_namespace = self.useNameSpace_checkBox.isChecked()

            self.environment.import_(previous_version, use_namespace)

            # inform the user about what happened
            if logger.level != logging.DEBUG:
                QtWidgets.QMessageBox.information(
                    self,
                    "Import",
                    "%s\n\n has been imported correctly!" %
                    previous_version.filename,
                    QtWidgets.QMessageBox.Ok
                )

    def clear_thumbnail(self):
        """clears the thumbnail_graphicsView
        """
        from anima.ui import utils as ui_utils
        ui_utils.clear_thumbnail(self.thumbnail_graphicsView)

    def update_thumbnail(self):
        """updates the thumbnail for the selected task
        """
        # get the current task
        task_id = self.tasks_tree_view.get_task_id()
        if task_id:
            from anima.ui import utils as ui_utils
            # TODO: Update this too
            from stalker import Task
            task = Task.query.get(task_id)
            ui_utils.update_gview_with_task_thumbnail(
                task,
                self.thumbnail_graphicsView
            )

    def upload_thumbnail_push_button_clicked(self):
        """runs when the upload_thumbnail_pushButton is clicked
        """
        from anima.ui import utils as ui_utils
        thumbnail_full_path = ui_utils.choose_thumbnail(self)

        # if the thumbnail_full_path is empty do not do anything
        if thumbnail_full_path == "":
            return

        # get the current task
        task_id = self.tasks_tree_view.get_task_id()

        if task_id:
            # TODO: Update this too
            from stalker import Task
            task = Task.query.get(task_id)
            ui_utils.upload_thumbnail(task, thumbnail_full_path)

            # update the thumbnail
            self.update_thumbnail()

    def clear_thumbnail_push_button_clicked(self):
        """clears the thumbnail of the current task if it has one
        """
        task_id = self.tasks_tree_view.get_task_id()

        if not task_id:
            return

        from stalker import SimpleEntity
        from stalker.db.session import DBSession
        thumb_id = DBSession\
            .query(SimpleEntity.thumbnail_id)\
            .filter(SimpleEntity.id == task_id)\
            .first()

        # thumb_id = task.thumbnail
        if not thumb_id:
            return

        answer = QtWidgets.QMessageBox.question(
            self,
            'Delete Thumbnail?',
            'Delete Thumbnail?',
            QtWidgets.QMessageBox.Yes,
            QtWidgets.QMessageBox.No
        )

        if answer == QtWidgets.QMessageBox.Yes:
            # remove the thumbnail and its thumbnail and its thumbnail
            from stalker import Link
            t = Link.query.filter(Link.id == thumb_id).first()
            DBSession.delete(t)
            if t.thumbnail:
                DBSession.delete(t.thumbnail)
                if t.thumbnail.thumbnail:
                    DBSession.delete(t.thumbnail.thumbnail)
            # leave the files there
            DBSession.commit()

            # update the thumbnail
            self.clear_thumbnail()

    def find_from_path_push_button_clicked(self):
        """runs when find_from_path_pushButton is clicked
        """
        full_path = self.find_from_path_lineEdit.text()
        from anima.env.base import EnvironmentBase
        env = EnvironmentBase()
        version = env.get_version_from_full_path(full_path)
        self.restore_ui(version)

    # def search_task_comboBox_textChanged(self, text):
    #     """runs when search_task_comboBox text changed
    #     """
    #     # text = self.search_task_lineEdit.text().strip()
    #     self.search_task_comboBox.clear()
    #     if not text:
    #         return
    #     tasks = Task.query.filter(Task.name.contains(text)).all()
    #     logger.debug('tasks with text: "%s" are : %s' % (text, tasks))
    #     # load all the tasks and their parents so we are going to be able to
    #     # find them later on
    #     # for task in tasks:
    #     #     self.load_task_item_hierarchy(task, self.tasks_tree_view)
    #     #
    #     # # now get the indices
    #     # indices = self.get_item_indices_containing_text(text,
    #     #                                                 self.tasks_tree_view)
    #     # logger.debug('indices containing the given text are : %s' % indices)
    #
    #     # self.search_task_comboBox.addItems(
    #     #     [
    #     #         (task.name + ' (%s)' % map(lambda x: '|'.join([parent.name for parent in x.parents]), task)) for task in tasks
    #     #     ]
    #     # )
    #     items = []
    #     for task in tasks:
    #         hierarchy_name = task.name + '(' + '|'.join(map(lambda x: x.name, task.parents)) + ')'
    #         items.append(hierarchy_name)
    #     self.search_task_comboBox.addItems(items)
    #

    def recent_files_combo_box_index_changed(self, path):
        """runs when the recent files combo box index has changed

        :param path: 
        :return:
        """
        current_index = self.recent_files_comboBox.currentIndex()
        path = self.recent_files_comboBox.itemData(current_index)
        self.find_from_path_lineEdit.setText(path)
        self.find_from_path_push_button_clicked()
