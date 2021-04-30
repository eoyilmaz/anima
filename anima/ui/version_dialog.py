# -*- coding: utf-8 -*-

# License: http://www.opensource.org/licenses/MIT

import sys
import os
import logging
from collections import namedtuple

import anima.utils
from anima import logger
from anima.ui.base import AnimaDialogBase, ui_caller
from anima.ui.lib import QtCore, QtGui, QtWidgets

from anima.ui.views.task import TaskTreeView
from anima.ui.widgets import TakesListWidget, RecentFilesComboBox
from anima.ui.widgets.version import VersionsTableWidget

if sys.version_info.major > 2:
    exceptionMessageGenerator = lambda e: str(e)
else:
    exceptionMessageGenerator = lambda e: e.message

ref_depth_res = [
    "As Saved",
    "All",
    "Top Level Only",
    "None"
]

VersionNT = namedtuple(
    # A named tuple for fast Version look-up
    "VersionNT",
    [
        "id",
        "version_number",
        "is_published",
        "created_with",
        "created_by_id",
        "updated_by_id",
        "full_path",
        "description"
    ]
)

# Mode is now defining the UI mode as which functionality it gives
# Mode 0: Save As
# Mode 1: Open
# Mode 2: Both Save As and Open. This is the default and this is the
#         legacy mode now, which will be deprecated in later versions.
SAVE_AS_MODE = 0
OPEN_MODE = 1
SAVE_AS_AND_OPEN_MODE = 2


# class RepresentationMessageBox(QtGui.QDialog, AnimaDialogBase):
#     """A message box variant
#     """
#
#     def __init__(self, parent=None):
#         super(RepresentationMessageBox, self).__init__(parent)
#         self.desired_repr = "Base"
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

    It is possible to run the version_dialog UI in read-only mode where the UI
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

    :param mode: The mode parameter has changed meaning. It is now to define if
      the UI is in **Save/Create** mode or in **Open/Read** mode. It will
      discern the Open and Save functionality, which was previously both exist
      at the same time and still can be by setting the mode to 2, which is the
      default value for now, but it will deprecate in later versions.

      The previous functionality of defining if the UI is in **Read-Write** or
      **Read-Only** mode has been automized. So the UI can decide to be in
      **Read-Only** mode if the given Environment doesn't have ``save_as``
      ability. When the UI is in Read-Write mode there will be all the buttons
      you would normally have (Export As, Save As, Open, Reference, Import),
      and in Read-Only mode it will have only one button called "Choose" which
      lets you choose one Version.
    """

    def __init__(self, environment=None, parent=None, mode=SAVE_AS_AND_OPEN_MODE):
        logger.debug("initializing the interface")
        super(MainDialog, self).__init__(parent)
        self.environment = environment

        self.mode = None
        self.window_title = ""
        self.chosen_version = None
        self.environment_name_format = "%n (%e)"
        # create the project attribute in projects_combo_box
        self.current_dialog = None

        # setup UI
        self._setup_ui()

        # setup signals
        self._setup_signals()

        # setup defaults
        self._set_defaults()

        # set mode
        self.set_mode(mode)

        # center window
        self.center_window()

        logger.debug("finished initializing the interface")

    def _setup_ui(self):
        """sets the UI up
        """
        self.update_window_title()

        self.resize(1500, 850)

        style_sheet = """
            QGroupBox::title {
                color: rgb(71, 143, 202);
                font-size: 108pt;
                font-weight: bold;
            }
        """

        # TODO: This is a very dirty fix, do it properly
        if self.environment.name.lower().startswith("houdini"):
            style_sheet += """QGroupBox{
                margin: 0px;
            }
            """

        self.setStyleSheet(style_sheet)

        # self.setStyle(QtWidgets.QStyleFactory.create("Fusion"))

        # Dialog itself
        self.setWindowModality(QtCore.Qt.ApplicationModal)
        self.setSizeGripEnabled(True)
        self.setModal(True)

        # Layouts
        # Main Layout
        self.main_layout = QtWidgets.QVBoxLayout(self)

        self.main_widget = QtWidgets.QWidget(self)
        size_policy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Preferred,
            QtWidgets.QSizePolicy.Preferred
        )
        size_policy.setHorizontalStretch(1)
        size_policy.setVerticalStretch(1)
        size_policy.setHeightForWidth(
            self.main_widget.sizePolicy().hasHeightForWidth()
        )
        self.main_widget.setSizePolicy(size_policy)

        self.vertical_layout_1 = QtWidgets.QVBoxLayout(self.main_widget)
        self.vertical_layout_1.setSizeConstraint(QtWidgets.QLayout.SetMaximumSize)
        self.vertical_layout_1.setContentsMargins(0, 0, 0, 0)

        # ------------------------------------------------
        # Switch Mode Button
        self.horizontal_layout_11 = QtWidgets.QHBoxLayout()
        self.switch_mode_button = QtWidgets.QPushButton(self.main_widget)
        self.horizontal_layout_11.addWidget(self.switch_mode_button)

        # ------------------------------------------------
        # Login Information
        self.horizontal_layout_11.setContentsMargins(0, 0, 0, 0)
        spacer_item = QtWidgets.QSpacerItem(
            40, 20,
            QtWidgets.QSizePolicy.Expanding,
            QtWidgets.QSizePolicy.Minimum
        )
        self.horizontal_layout_11.addItem(spacer_item)

        # Logged in As Label
        self.logged_in_as_label = QtWidgets.QLabel(self.main_widget)
        self.logged_in_as_label.setText("<b>Logged In As:</b>")
        self.logged_in_as_label.setTextFormat(QtCore.Qt.AutoText)
        self.horizontal_layout_11.addWidget(self.logged_in_as_label)

        # Logged in User Label
        self.logged_in_user_label = QtWidgets.QLabel(self.main_widget)
        self.horizontal_layout_11.addWidget(self.logged_in_user_label)

        # Logout Push Button
        self.logout_push_button = QtWidgets.QPushButton(self.main_widget)
        self.logout_push_button.setText("Logout")

        self.horizontal_layout_11.addWidget(self.logout_push_button)
        self.vertical_layout_1.addLayout(self.horizontal_layout_11)

        # Add a line
        line = QtWidgets.QFrame(self.main_widget)
        line.setFrameShape(QtWidgets.QFrame.HLine)
        line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.vertical_layout_1.addWidget(line)

        # ------------------------------------------------
        # The Task Tree, New Version and Previous Versions Layouts
        self.horizontal_layout_12 = QtWidgets.QHBoxLayout()

        # Tasks GroupBox
        self.tasks_group_box = QtWidgets.QGroupBox(self)
        self.tasks_group_box.setTitle("Tasks")

        self.vertical_layout_7 = QtWidgets.QVBoxLayout()
        self.vertical_layout_7.addWidget(self.tasks_group_box)

        # self.horizontal_layout_12.addWidget(self.tasks_group_box)
        self.horizontal_layout_12.addLayout(self.vertical_layout_7)

        # splitter.addWidget(self.tasks_groupBox)

        self.vertical_layout_2 = QtWidgets.QVBoxLayout(self.tasks_group_box)
        # self.vertical_layout_2.setContentsMargins(-1, 9, -1, -1)

        # Show My Tasks Only CheckBox
        self.my_tasks_only_check_box = QtWidgets.QCheckBox(self)
        self.my_tasks_only_check_box.setText("Show my tasks only")
        self.my_tasks_only_check_box.setChecked(False)
        self.vertical_layout_2.addWidget(self.my_tasks_only_check_box)

        # Show Completed Projects
        self.show_completed_check_box = QtWidgets.QCheckBox(self)
        self.show_completed_check_box.setText("Show Completed Projects")
        self.show_completed_check_box.setChecked(False)
        self.vertical_layout_2.addWidget(self.show_completed_check_box)

        self.horizontal_layout_4 = QtWidgets.QHBoxLayout()
        self.search_task_line_edit = QtWidgets.QLineEdit(self)
        self.horizontal_layout_4.addWidget(self.search_task_line_edit)
        self.vertical_layout_2.addLayout(self.horizontal_layout_4)

        # ========================================
        # Recent Files Combo Box
        self.horizontal_layout_8 = QtWidgets.QHBoxLayout()
        self.recent_files_combo_box = RecentFilesComboBox(self)
        self.recent_files_combo_box.setToolTip("Recent Files")
        self.recent_files_combo_box.addItem("--- No Recent Files ---")
        self.horizontal_layout_8.addWidget(self.recent_files_combo_box)

        # Clear Recent Files Push Button
        self.clear_recent_files_push_button = QtWidgets.QPushButton(self)
        self.clear_recent_files_push_button.setText("Clear")
        self.horizontal_layout_8.addWidget(self.clear_recent_files_push_button)
        self.horizontal_layout_8.setStretch(0, 1)
        self.vertical_layout_2.addLayout(self.horizontal_layout_8)

        # ========================================
        self.horizontal_layout_3 = QtWidgets.QHBoxLayout()
        self.find_from_path_line_edit = QtWidgets.QLineEdit(self)
        self.find_from_path_line_edit.setPlaceholderText("Find From Path")

        self.horizontal_layout_3.addWidget(self.find_from_path_line_edit)
        self.find_from_path_push_button = QtWidgets.QPushButton(self)
        self.find_from_path_push_button.setText("Find")

        self.find_from_path_push_button.setDefault(True)
        self.horizontal_layout_3.addWidget(self.find_from_path_push_button)
        self.vertical_layout_2.addLayout(self.horizontal_layout_3)

        # ========================================
        # Tasks Tree View
        self.tasks_tree_view = TaskTreeView(self)
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
        self.tasks_tree_view.setEditTriggers(
            QtWidgets.QAbstractItemView.NoEditTriggers
        )
        # self.tasks_tree_view.setAlternatingRowColors(True)
        # self.tasks_tree_view.setUniformRowHeights(True)
        # self.tasks_tree_view.header().setCascadingSectionResizes(True)
        self.vertical_layout_2.addWidget(self.tasks_tree_view)

        # ------------------------------------------
        # New Version Fields
        self.new_version_controls_widget = QtWidgets.QWidget(self)
        self.new_version_main_layout = QtWidgets.QVBoxLayout(self.new_version_controls_widget)

        # ==================
        # Description Field
        self.description_label = QtWidgets.QLabel(self)
        self.description_label.setText("Description")
        self.description_label.setMinimumSize(QtCore.QSize(35, 0))
        self.new_version_main_layout.addWidget(self.description_label)
        self.description_text_edit = QtWidgets.QTextEdit(self)
        self.description_text_edit.setHtml(
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

        self.description_text_edit.setEnabled(True)
        self.description_text_edit.setTabChangesFocus(True)
        # self.description_text_edit.setMaximumHeight(130)
        self.new_version_main_layout.addWidget(self.description_text_edit)

        self.save_as_buttons_layout = QtWidgets.QHBoxLayout()
        self.environment_combo_box = QtWidgets.QComboBox(self)
        self.save_as_buttons_layout.addWidget(self.environment_combo_box)

        # ===================
        # Save As
        self.save_as_push_button = QtWidgets.QPushButton(self)
        self.save_as_push_button.setText("Save As")
        self.save_as_push_button.setDefault(False)
        self.save_as_buttons_layout.addWidget(self.save_as_push_button)

        # ===================
        # Export Push Button
        self.export_as_push_button = QtWidgets.QPushButton(self)
        self.export_as_push_button.setText("Export Selection As")
        self.save_as_buttons_layout.addWidget(self.export_as_push_button)

        # ===================
        # Publish Push Button
        self.publish_push_button = QtWidgets.QPushButton(self)
        self.publish_push_button.setText("Publish")
        if not self.environment.has_publishers:
            self.publish_push_button.setText("Publish")
        self.save_as_buttons_layout.addWidget(self.publish_push_button)

        # Close Push Button
        self.close2_push_button = QtWidgets.QPushButton(self)
        self.close2_push_button.setText("Close")
        self.save_as_buttons_layout.addWidget(self.close2_push_button)

        self.new_version_main_layout.addLayout(self.save_as_buttons_layout)

        self.new_version_main_layout.setStretch(0, 0)
        self.new_version_main_layout.setStretch(1, 10)
        self.new_version_main_layout.setStretch(2, 1)

        # ---------------------------------------------
        # Thumbnail Graphics View and Buttons
        self.thumbnail_group_box = QtWidgets.QGroupBox(self)
        self.thumbnail_group_box.setTitle("Task Thumbnail")

        self.vertical_layout_7.addWidget(self.thumbnail_group_box)

        self.thumbnail_layout = QtWidgets.QVBoxLayout(self.thumbnail_group_box)

        self.thumbnail_graphics_view = QtWidgets.QGraphicsView(self)
        size_policy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Fixed,
            QtWidgets.QSizePolicy.Fixed
        )
        size_policy.setHorizontalStretch(0)
        size_policy.setVerticalStretch(0)
        size_policy.setHeightForWidth(self.thumbnail_graphics_view.sizePolicy().hasHeightForWidth())
        self.thumbnail_graphics_view.setSizePolicy(size_policy)
        self.thumbnail_graphics_view.setMinimumSize(QtCore.QSize(320, 180))
        self.thumbnail_graphics_view.setMaximumSize(QtCore.QSize(320, 180))
        self.thumbnail_graphics_view.setAutoFillBackground(False)
        self.thumbnail_graphics_view.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.thumbnail_graphics_view.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        self.thumbnail_graphics_view.setBackgroundBrush(brush)
        self.thumbnail_graphics_view.setInteractive(False)
        self.thumbnail_graphics_view.setRenderHints(
            QtGui.QPainter.Antialiasing |
            QtGui.QPainter.HighQualityAntialiasing |
            QtGui.QPainter.SmoothPixmapTransform |
            QtGui.QPainter.TextAntialiasing
        )
        self.thumbnail_layout.addWidget(self.thumbnail_graphics_view)

        spacer_item1 = QtWidgets.QSpacerItem(
            0, 0,
            QtWidgets.QSizePolicy.Minimum,
            QtWidgets.QSizePolicy.Minimum
        )
        self.thumbnail_layout.addItem(spacer_item1)

        self.horizontal_layout_13 = QtWidgets.QHBoxLayout()
        # self.horizontal_layout_13.setContentsMargins(-1, -1, -1, 10)
        spacer_item1 = QtWidgets.QSpacerItem(
            5, 20,
            QtWidgets.QSizePolicy.Minimum,
            QtWidgets.QSizePolicy.Minimum
        )
        self.horizontal_layout_13.addItem(spacer_item1)
        self.upload_thumbnail_push_button = QtWidgets.QPushButton(self)
        self.upload_thumbnail_push_button.setText("Upload")
        self.horizontal_layout_13.addWidget(self.upload_thumbnail_push_button)
        self.clear_thumbnail_push_button = QtWidgets.QPushButton(self)
        self.clear_thumbnail_push_button.setText("Clear")
        self.horizontal_layout_13.addWidget(self.clear_thumbnail_push_button)

        self.thumbnail_layout.addLayout(self.horizontal_layout_13)

        # ------------------------------------------
        # Takes Goes its own groupbox
        self.takes_group_box = QtWidgets.QGroupBox()
        self.takes_group_box.setTitle("Takes")

        self.vertical_layout_8 = QtWidgets.QVBoxLayout(self.takes_group_box)

        # ===================
        # Show Representations
        self.repr_as_separate_takes_check_box = QtWidgets.QCheckBox()
        self.repr_as_separate_takes_check_box.setText("Show Repr.")
        self.repr_as_separate_takes_check_box.setToolTip(
            "<html><head/><body><p>Check this to show "
            "<span style=\" font-weight:600;\">Representations</span> as "
            "separate takes if available</p></body></html>"
        )
        self.vertical_layout_8.addWidget(self.repr_as_separate_takes_check_box)

        # # add a spacer
        # spacer_item = QtWidgets.QSpacerItem(
        #     40, 20,
        #     QtWidgets.QSizePolicy.Expanding,
        #     QtWidgets.QSizePolicy.Minimum
        # )
        # self.vertical_layout_8.addItem(spacer_item)

        # ===================
        # Add Take Push Button
        self.add_take_push_button = QtWidgets.QPushButton(self)
        self.add_take_push_button.setText("New Take")
        self.add_take_push_button.setMinimumWidth(120)
        self.vertical_layout_8.addWidget(self.add_take_push_button)

        # ====================
        # Takes Label
        self.takes_label = QtWidgets.QLabel()
        self.takes_label.setText("Take")
        self.takes_label.setMinimumSize(QtCore.QSize(35, 0))
        self.vertical_layout_8.addWidget(self.takes_label)

        # ===================
        # Takes ComboBox
        # self.takes_combo_box = TakesComboBox(self)
        self.takes_list_widget = TakesListWidget(self)
        self.vertical_layout_8.addWidget(self.takes_list_widget)

        # ------------------------------------------
        # Previous Versions Group Box

        self.versions_group_box = QtWidgets.QGroupBox(self)
        self.versions_group_box.setTitle("Versions")

        self.versions_main_layout = QtWidgets.QVBoxLayout(self.versions_group_box)
        self.horizontal_layout_10 = QtWidgets.QHBoxLayout()

        # Show Only # Items Label
        # self.show_only_label = QtWidgets.QLabel(self.previous_versions_group_box)
        # self.show_only_label.setText("Show Only")
        # self.horizontal_layout_10.addWidget(self.show_only_label)

        # Version Count
        # self.version_count_spin_box = QtWidgets.QSpinBox(self.previous_versions_group_box)
        # self.version_count_spin_box.setMaximum(999999)
        # self.version_count_spin_box.setProperty("value", 25)
        # self.horizontal_layout_10.addWidget(self.version_count_spin_box)

        # # Add a line
        # line = QtWidgets.QFrame(self.previous_versions_group_box)
        # line.setFrameShape(QtWidgets.QFrame.VLine)
        # line.setFrameShadow(QtWidgets.QFrame.Sunken)
        # self.horizontal_layout_10.addWidget(line)

        # ==============================
        # Show Published Only Check Box
        self.show_published_only_check_box = QtWidgets.QCheckBox(self)
        self.horizontal_layout_10.addWidget(self.show_published_only_check_box)
        self.show_published_only_check_box.setText("Show Published Only")

        spacer_item2 = QtWidgets.QSpacerItem(
            40, 20,
            QtWidgets.QSizePolicy.Expanding,
            QtWidgets.QSizePolicy.Minimum
        )
        self.horizontal_layout_10.addItem(spacer_item2)
        self.versions_main_layout.addLayout(self.horizontal_layout_10)

        # previous_versions_table_widget
        self.previous_versions_table_widget = VersionsTableWidget(self)

        self.previous_versions_table_widget.setToolTip(
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
        self.previous_versions_table_widget.horizontalHeaderItem(0).setText("Version")
        self.previous_versions_table_widget.horizontalHeaderItem(1).setText("User")
        self.previous_versions_table_widget.horizontalHeaderItem(2).setText("File Size")
        self.previous_versions_table_widget.horizontalHeaderItem(3).setText("Date")
        self.previous_versions_table_widget.horizontalHeaderItem(4).setText("Description")

        self.previous_versions_table_widget.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        # self.previous_versions_table_widget.setAlternatingRowColors(True)
        self.previous_versions_table_widget.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.previous_versions_table_widget.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.previous_versions_table_widget.setShowGrid(False)
        self.previous_versions_table_widget.setColumnCount(7)
        self.previous_versions_table_widget.setRowCount(0)

        for i in range(7):
            item = QtWidgets.QTableWidgetItem()
            self.previous_versions_table_widget.setHorizontalHeaderItem(i, item)

        self.previous_versions_table_widget.horizontalHeader().setStretchLastSection(True)
        self.previous_versions_table_widget.verticalHeader().setStretchLastSection(False)

        self.versions_main_layout.addWidget(self.previous_versions_table_widget)

        self.previous_version_secondary_controls_widget = QtWidgets.QWidget(self)
        self.previous_version_secondary_controls_layout = QtWidgets.QHBoxLayout(self.previous_version_secondary_controls_widget)


        self.representations_label = QtWidgets.QLabel(self)
        self.representations_label.setText("Repr.")
        self.previous_version_secondary_controls_layout.addWidget(self.representations_label)

        self.representations_comboBox = QtWidgets.QComboBox(self)
        self.representations_comboBox.setToolTip("Choose Representation (if supported by the environment)")

        self.previous_version_secondary_controls_layout.addWidget(self.representations_comboBox)
        self.reference_depth_label = QtWidgets.QLabel(self)
        self.reference_depth_label.setText("Refs")
        self.previous_version_secondary_controls_layout.addWidget(self.reference_depth_label)
        self.ref_depth_combo_box = QtWidgets.QComboBox(self)
        self.ref_depth_combo_box.setToolTip("Choose reference depth (if supported by environment)")
        self.previous_version_secondary_controls_layout.addWidget(self.ref_depth_combo_box)
        spacer_item3 = QtWidgets.QSpacerItem(
            40, 20,
            QtWidgets.QSizePolicy.Expanding,
            QtWidgets.QSizePolicy.Minimum
        )
        self.previous_version_secondary_controls_layout.addItem(spacer_item3)
        self.use_namespace_check_box = QtWidgets.QCheckBox(self)
        self.use_namespace_check_box.setText("Use Namespace")
        self.use_namespace_check_box.setToolTip(
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
        self.use_namespace_check_box.setChecked(True)
        self.previous_version_secondary_controls_layout.addWidget(self.use_namespace_check_box)

        # Choose Push Button
        self.choose_version_push_button = QtWidgets.QPushButton(self)
        self.choose_version_push_button.setText("Choose")
        self.previous_version_secondary_controls_layout.addWidget(self.choose_version_push_button)

        # Check Updates Check Box
        self.check_updates_check_box = QtWidgets.QCheckBox(self)
        self.check_updates_check_box.setToolTip("Disable update check (faster)")
        self.check_updates_check_box.setText("Check Updates")
        self.check_updates_check_box.setChecked(True)
        self.previous_version_secondary_controls_layout.addWidget(self.check_updates_check_box)

        self.previous_version_controls_widget = QtWidgets.QWidget(self)
        self.open_buttons_layout = QtWidgets.QHBoxLayout(self.previous_version_controls_widget)

        # Open Push Button
        self.open_push_button = QtWidgets.QPushButton(self)
        self.open_buttons_layout.addWidget(self.open_push_button)
        self.open_push_button.setText("Open")

        # Open As New Version Push Button
        self.open_as_new_version_push_button = QtWidgets.QPushButton(self)
        self.open_buttons_layout.addWidget(self.open_as_new_version_push_button)
        self.open_as_new_version_push_button.setText("Open As New Version")
        self.open_as_new_version_push_button.setToolTip(
            "Opens the selected version and immediately creates a new version."
        )

        # Reference Push Button
        self.reference_push_button = QtWidgets.QPushButton(self)
        self.reference_push_button.setText("Reference")
        self.open_buttons_layout.addWidget(self.reference_push_button)

        # Import Push Button
        self.import_push_button = QtWidgets.QPushButton(self)
        self.import_push_button.setText("Import")
        self.open_buttons_layout.addWidget(self.import_push_button)

        # Close Push Button
        self.close1_push_button = QtWidgets.QPushButton(self)
        self.close1_push_button.setText("Close")
        self.open_buttons_layout.addWidget(self.close1_push_button)

        self.versions_main_layout.addWidget(self.previous_version_secondary_controls_widget)
        self.versions_main_layout.addWidget(self.previous_version_controls_widget)
        self.versions_main_layout.addWidget(self.new_version_controls_widget)

        self.vertical_layout_6 = QtWidgets.QVBoxLayout()
        self.horizontal_layout_12.addWidget(self.takes_group_box)
        self.horizontal_layout_12.addLayout(self.vertical_layout_6)

        self.vertical_layout_6.addWidget(self.versions_group_box)
        # self.vertical_layout_6.addWidget(self)

        self.vertical_layout_6.setStretch(0, 10)
        self.vertical_layout_6.setStretch(1, 0)

        self.horizontal_layout_12.setStretch(0, 2)
        self.horizontal_layout_12.setStretch(1, 1)
        self.horizontal_layout_12.setStretch(2, 4)

        self.vertical_layout_1.addLayout(self.horizontal_layout_12)
        self.main_layout.addWidget(self.main_widget)

        QtCore.QMetaObject.connectSlotsByName(self)
        self.setTabOrder(self.description_text_edit, self.export_as_push_button)
        self.setTabOrder(self.export_as_push_button, self.save_as_push_button)
        self.setTabOrder(self.save_as_push_button, self.previous_versions_table_widget)
        self.setTabOrder(self.previous_versions_table_widget, self.open_push_button)
        self.setTabOrder(self.open_push_button, self.open_as_new_version_push_button)
        self.setTabOrder(self.open_as_new_version_push_button, self.reference_push_button)
        self.setTabOrder(self.reference_push_button, self.import_push_button)

    # def close(self):
    #     logger.debug("closing the ui")
    #     QtWidgets.QDialog.close(self)

    def update_window_title(self):
        """updates the window title depending on the environment and mode
        """
        import anima
        window_title = "Anima Pipeline v%s " % anima.__version__

        if self.environment:
            window_title = "%s | %s" % (window_title, self.environment.name)
        else:
            window_title = "%s | No Environment" % window_title

        if self.mode == SAVE_AS_MODE:
            window_title = "%s | Version: Save-As Mode" % window_title
        elif self.mode == OPEN_MODE:
            window_title = "%s | Version: Open Mode" % window_title
        elif self.mode == SAVE_AS_AND_OPEN_MODE:
            window_title = "%s | Version: Save As & Open Mode" % window_title

        # change the window title
        self.setWindowTitle(window_title)

    def set_mode(self, mode):
        """sets the UI mode

        :param mode:
        :return:
        """
        self.mode = mode
        self.update_window_title()
        if self.mode == SAVE_AS_MODE:  # Save As Mode
            self.previous_version_controls_widget.setVisible(False)
            self.previous_version_secondary_controls_widget.setVisible(False)
            self.new_version_controls_widget.setVisible(True)
            self.switch_mode_button.setText("Switch to Open Mode")
        elif self.mode == OPEN_MODE:  # Open Mode
            self.previous_version_controls_widget.setVisible(True)
            self.previous_version_secondary_controls_widget.setVisible(True)
            self.new_version_controls_widget.setVisible(False)
            self.switch_mode_button.setText("Switch to Save As Mode")
        elif self.mode == SAVE_AS_AND_OPEN_MODE:
            self.previous_version_controls_widget.setVisible(True)
            self.previous_version_secondary_controls_widget.setVisible(True)
            self.new_version_controls_widget.setVisible(True)

            # no mode switching in this mode
            self.switch_mode_button.setVisible(False)

    def switch_mode(self):
        """switches mode between Open and Save As
        """
        if self.mode == SAVE_AS_MODE:
            self.set_mode(OPEN_MODE)
        elif self.mode == OPEN_MODE:
            self.set_mode(SAVE_AS_MODE)

    def show(self):
        """overridden show method
        """
        logger.debug("MainDialog.show is started")
        logged_in_user = self.get_logged_in_user()
        if not logged_in_user:
            self.close()
            return_val = None
        else:
            return_val = super(MainDialog, self).show()
            self.center_window()

        logger.debug("MainDialog.show is finished")
        return return_val

    def _setup_signals(self):
        """sets up the signals
        """
        logger.debug("start setting up interface signals")

        # close button
        QtCore.QObject.connect(
            self.close1_push_button,
            QtCore.SIGNAL("clicked()"),
            self.close
        )

        QtCore.QObject.connect(
            self.close2_push_button,
            QtCore.SIGNAL("clicked()"),
            self.close
        )

        # switch mode button
        QtCore.QObject.connect(
            self.switch_mode_button,
            QtCore.SIGNAL("clicked()"),
            self.switch_mode
        )

        # logout button
        QtCore.QObject.connect(
            self.logout_push_button,
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

        # # takes_combo_box
        # QtCore.QObject.connect(
        #     self.takes_combo_box,
        #     QtCore.SIGNAL("currentTextChanged(QString)"),
        #     self.takes_combo_box_changed
        # )

        # repr_as_separate_takes_checkBox
        QtCore.QObject.connect(
            self.repr_as_separate_takes_check_box,
            QtCore.SIGNAL("stateChanged(int)"),
            self.tasks_tree_view_changed
        )

        # takes_combo_box
        QtCore.QObject.connect(
            self.takes_list_widget,
            QtCore.SIGNAL(
                "currentItemChanged(QListWidgetItem *, QListWidgetItem *)"
                # "currentIndexChanged(QString)"
            ),
            self.takes_list_widget_changed
        )

        # recent files comboBox
        QtCore.QObject.connect(
            self.recent_files_combo_box,
            QtCore.SIGNAL("currentIndexChanged(QString)"),
            self.recent_files_combo_box_index_changed
        )

        # find_from_path_lineEdit
        QtCore.QObject.connect(
            self.find_from_path_push_button,
            QtCore.SIGNAL("clicked()"),
            self.find_from_path_push_button_clicked
        )

        # add_take_toolButton
        QtCore.QObject.connect(
            self.add_take_push_button,
            QtCore.SIGNAL("clicked()"),
            self.add_take_push_button_clicked
        )

        # export_as
        QtCore.QObject.connect(
            self.export_as_push_button,
            QtCore.SIGNAL("clicked()"),
            self.export_as_push_button_clicked
        )

        # save_as
        QtCore.QObject.connect(
            self.save_as_push_button,
            QtCore.SIGNAL("clicked()"),
            self.save_as_push_button_clicked
        )

        # publish
        QtCore.QObject.connect(
            self.publish_push_button,
            QtCore.SIGNAL("clicked()"),
            self.publish_push_button_clicked
        )

        # open
        QtCore.QObject.connect(
            self.open_push_button,
            QtCore.SIGNAL("clicked()"),
            self.open_push_button_clicked
        )

        # open as
        QtCore.QObject.connect(
            self.open_as_new_version_push_button,
            QtCore.SIGNAL("clicked()"),
            self.open_as_new_version_push_button_clicked
        )

        # chose
        QtCore.QObject.connect(
            self.choose_version_push_button,
            QtCore.SIGNAL("cliched()"),
            self.choose_version_push_button_clicked
        )

        # reference
        QtCore.QObject.connect(
            self.reference_push_button,
            QtCore.SIGNAL("clicked()"),
            self.reference_push_button_clicked
        )

        # import
        QtCore.QObject.connect(
            self.import_push_button,
            QtCore.SIGNAL("clicked()"),
            self.import_push_button_clicked
        )

        # show_only_published_checkBox
        QtCore.QObject.connect(
            self.show_published_only_check_box,
            QtCore.SIGNAL("stateChanged(int)"),
            self.update_previous_versions_table_widget
        )

        # # version_count_spin_box
        # QtCore.QObject.connect(
        #     self.version_count_spin_box,
        #     QtCore.SIGNAL("valueChanged(int)"),
        #     self.update_previous_versions_table_widget
        # )

        # upload_thumbnail_push_button
        QtCore.QObject.connect(
            self.upload_thumbnail_push_button,
            QtCore.SIGNAL("clicked()"),
            self.upload_thumbnail_push_button_clicked
        )

        # upload_thumbnail_push_button
        QtCore.QObject.connect(
            self.clear_thumbnail_push_button,
            QtCore.SIGNAL("clicked()"),
            self.clear_thumbnail_push_button_clicked
        )

        # close button
        QtCore.QObject.connect(
            self.clear_recent_files_push_button,
            QtCore.SIGNAL("clicked()"),
            self.clear_recent_file_push_button_clicked
        )

        QtCore.QObject.connect(
            self.show_completed_check_box,
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
        """the custom context menu for the previous_versions_table_widget
        """
        # convert the position to global screen position
        global_position = \
            self.previous_versions_table_widget.mapToGlobal(position)

        item = self.previous_versions_table_widget.itemAt(position)
        # if not item:
        #     return

        index = None
        version = None
        if item:
            index = item.row()
            version = self.previous_versions_table_widget.versions[index]
            from stalker import Version
            version = Version.query.get(version.id)

        # create the menu
        menu = QtWidgets.QMenu()

        logged_in_user = self.get_logged_in_user()

        # add Browse Outputs
        browse_path_action = menu.addAction("Browse Path...")
        browse_outputs_action = menu.addAction("Browse Outputs...")
        upload_output_action = menu.addAction("Upload Output...")
        copy_path_action = menu.addAction("Copy Path")
        rerender_path_variables_action = \
            menu.addAction("Re-Render Path Variables")
        menu.addSeparator()
        change_description_action = menu.addAction("Change Description...")
        menu.addSeparator()

        if not item:
            browse_path_action.setEnabled(False)
            browse_outputs_action.setEnabled(False)
            upload_output_action.setEnabled(False)
            copy_path_action.setEnabled(False)
            rerender_path_variables_action.setEnabled(False)
            change_description_action.setEnabled(False)

        # Create power menu
        publish_action = menu.addAction("Publish")
        menu.addSeparator()
        create_version_action = menu.addAction("Create Dummy Version")
        delete_action = menu.addAction("Delete")

        if version:
            from anima import defaults
            if logged_in_user in version.task.responsible \
               or logged_in_user not in version.task.resources \
               or defaults.is_power_user(logged_in_user):

                if version.is_published:
                    publish_action.setText("Un-Publish")
            else:
                publish_action.setEnabled(False)
                delete_action.setEnabled(False)
        else:
            publish_action.setEnabled(False)
            delete_action.setEnabled(False)

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
                            "Error",
                            "This version is referenced by the following "
                            "tasks:<br><br>%s<br><br>"
                            "So, you can not un-publish it!" %
                            "<br>".join(
                                list(
                                    map(
                                        lambda x: x.name,
                                        related_tasks
                                    )
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
                elif choice == "Delete":
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
                            "Error",
                            "This version is referenced by the following "
                            "tasks:<br><br>%s<br><br>"
                            "So, you can not delete it!" %
                            "<br>".join(
                                list(
                                    map(
                                        lambda x: x.name,
                                        related_tasks
                                    )
                                )
                            )
                        )
                    else:
                        # Ask user if he/she is sure
                        answer = QtWidgets.QMessageBox.question(
                            self,
                            "Delete?",
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
                                    "Error",
                                    str(e)
                                )
                            finally:
                                # refresh the tableWidget
                                self.update_previous_versions_table_widget()
                        else:
                            return

            from anima import utils
            if choice == "Browse Path...":
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
            elif choice == "Browse Outputs...":
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
            elif choice == "Change Description...":
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

                        # update the previous_versions_table_widget
                        self.update_previous_versions_table_widget()
            elif choice == "Copy Path":
                # just set the clipboard to the version.absolute_full_path
                clipboard = QtWidgets.QApplication.clipboard()
                clipboard.setText(
                    os.path.normpath(
                        os.path.expandvars(
                            version.full_path
                        )
                    )
                )
            elif selected_item == create_version_action:
                # create a new version with the currently selected data
                version = self.get_new_version()

                # update version info
                # set to the base extension
                version.update_paths()
                version.extension = self.environment.extensions[0]
                version.created_with = self.environment.name

                from stalker.db.session import DBSession
                try:
                    DBSession.commit()
                except BaseException:
                    DBSession.rollback()

                # now reload the UI
                self.update_previous_versions_table_widget()
            elif selected_item == rerender_path_variables_action:
                if version:
                    # warn the user before doing anything
                    # answer = QtWidgets.QMessageBox.question(
                    #     self,
                    #     "Re-Render Path Variables?",
                    #     "This will recalculate the version path"
                    #     "<br>"
                    #     "<br>Files will not be deleted!",
                    #     QtWidgets.QMessageBox.Yes,
                    #     QtWidgets.QMessageBox.No
                    # )
                    # if answer == QtWidgets.QMessageBox.Yes:
                    from stalker import Version
                    assert isinstance(version, Version)
                    ext = version.extension
                    version.update_paths()
                    version.extension = ext
                    from stalker.db.session import DBSession
                    try:
                        DBSession.commit()
                    except BaseException:
                        DBSession.rollback()
                    # now reload the UI
                    self.update_previous_versions_table_widget()

    @classmethod
    def get_item_indices_containing_text(cls, text, tree_view):
        """returns the indexes of the item indices containing the given text
        """
        model = tree_view.model()
        logger.debug("searching for text : %s" % text)
        return model.match(
            model.index(0, 0),
            0,
            text,
            -1,
            QtCore.Qt.MatchRecursive
        )

    def find_entity_item_in_tree_view(self, entity, tree_view):
        """finds the item related to the stalker entity in the given
        QtTreeView
        """
        if not entity:
            return None

        indexes = self.get_item_indices_containing_text(entity.name, tree_view)
        model = tree_view.model()
        logger.debug("items matching name : %s" % indexes)
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
        # ask the user if he/she is sure about that
        answer = QtWidgets.QMessageBox.question(
            self,
            "Clear recent files list?",
            "Clear recent files list?",
            QtWidgets.QMessageBox.Yes,
            QtWidgets.QMessageBox.No
        )
        if answer == QtWidgets.QMessageBox.Yes:
            self.clear_recent_files()
            self.update_recent_files_combo_box()

    def update_recent_files_combo_box(self):
        """
        """
        self.recent_files_combo_box.setSizeAdjustPolicy(
            QtWidgets.QComboBox.AdjustToContentsOnFirstShow
        )
        self.recent_files_combo_box.setFixedWidth(250)

        self.recent_files_combo_box.clear()
        self.recent_files_combo_box.addItem("--- No Recent Files ---")

        # update recent files list
        if self.environment:
            from anima.recent import RecentFileManager
            rfm = RecentFileManager()
            try:
                recent_files = rfm[self.environment.name]

                if len(recent_files):
                    self.recent_files_combo_box.clear()
                    recent_files.insert(0, "--- Choose A Recent File ---")
                    # append them to the comboBox

                    for i, full_path in enumerate(recent_files[:50]):
                        parts = os.path.split(full_path)
                        filename = parts[-1]
                        self.recent_files_combo_box.addItem(
                            filename,
                            full_path,
                        )

                        self.recent_files_combo_box.setItemData(
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

                    self.recent_files_combo_box.setSizePolicy(
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
        """wrapper for the tasks_tree_view.fill() method
        """
        self.tasks_tree_view.show_completed_projects = show_completed_projects
        self.tasks_tree_view.fill()

        # also setup the signal
        logger.debug("setting up signals for tasks_tree_view_changed")
        QtCore.QObject.connect(
            self.tasks_tree_view.selectionModel(),
            QtCore.SIGNAL("selectionChanged(const QItemSelection &, "
                          "const QItemSelection &)"),
            self.tasks_tree_view_changed
        )

    def tasks_tree_view_changed(self):
        """runs when the tasks_tree_view item is changed
        """
        logger.debug("tasks_tree_view_changed running")
        if self.tasks_tree_view.is_updating:
            logger.debug("tasks_tree_view is updating, so returning early")
            return

        task_id = self.tasks_tree_view.get_task_id()
        logger.debug("task_id : %s" % task_id)

        # update the thumbnail
        # TODO: do it in another thread
        self.clear_thumbnail()
        self.update_thumbnail()

        # get the versions of the entity
        takes = []

        if task_id:
            # clear the takes_combo_box and fill with new data
            logger.debug("clear takes widget")
            self.takes_list_widget.clear()

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

                takes = list(map(lambda x: x[0], result))

                if not self.repr_as_separate_takes_check_box.isChecked():
                    # filter representations
                    from anima.representation import Representation
                    takes = [take for take in takes
                             if Representation.repr_separator not in take]
                takes = sorted(takes, key=lambda x: x.lower())

            logger.debug("len(takes) from db: %s" % len(takes))

            logger.debug("adding the takes from db")
            self.takes_list_widget.take_names = takes
            self.takes_label.setText("Takes (%s)" % len(takes))

    def _set_defaults(self):
        """sets up the defaults for the interface
        """
        logger.debug("started setting up interface defaults")
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
            self.show_completed_check_box.isChecked()
        )

        # reconnect signals
        # takes_combo_box
        # QtCore.QObject.connect(
        #     self.takes_list_widget,
        #     QtCore.SIGNAL("currentTextChanged(QString)"),
        #     self.takes_list_widget_changed
        # )

        # takes_combo_box
        QtCore.QObject.connect(
            self.takes_list_widget,
            QtCore.SIGNAL(
                "currentItemChanged(QListWidgetItem *, QListWidgetItem *)"),
            self.takes_list_widget_changed
        )
        # *********************************************************************

        # custom context menu for the previous_versions_table_widget
        self.previous_versions_table_widget.setContextMenuPolicy(
            QtCore.Qt.CustomContextMenu
        )

        QtCore.QObject.connect(
            self.previous_versions_table_widget,
            QtCore.SIGNAL("customContextMenuRequested(const QPoint&)"),
            self._show_previous_versions_tableWidget_context_menu
        )

        # Open the version
        # add double clicking to previous_versions_table_widget
        QtCore.QObject.connect(
            self.previous_versions_table_widget,
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
        self.search_task_line_edit.setVisible(False)

        # fill programs list
        from anima.env.external import ExternalEnvFactory
        env_factory = ExternalEnvFactory()
        env_names = env_factory.get_env_names(
            name_format=self.environment_name_format
        )
        self.environment_combo_box.addItems(env_names)

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
            self.ref_depth_combo_box.addItem(r)

        logger.debug("restoring the ui with the version from environment")

        # get the last version from the environment
        version_from_env = env.get_last_version()

        logger.debug("version_from_env: %s" % version_from_env)
        self.restore_ui(version_from_env)

        if is_external_env:
            # hide some buttons
            self.export_as_push_button.setVisible(False)
            self.reference_push_button.setVisible(False)
            self.import_push_button.setVisible(False)
        else:
            self.environment_combo_box.setVisible(False)

        # update description field
        self.description_text_edit.setText("")

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
        self.takes_list_widget.current_take_name = take_name

        # select the version in the previous version list
        self.previous_versions_table_widget.select_version(version)

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
                    self.environment_combo_box.findText(
                        env.name,
                        QtCore.Qt.MatchContains
                    )
                if index:
                    self.environment_combo_box.setCurrentIndex(index)

    def takes_list_widget_changed(self, index):
        """runs when the takes_listWidget has changed
        """
        logger.debug("takes_list_widget_changed started")
        # count = self.takes_list_widget.count()
        # if index == count - 1:
        #     # call New Take
        #     pass
        # else:
        #     # update the previous_versions_table_widget
        #     self.update_previous_versions_table_widget()
        self.update_previous_versions_table_widget()

        logger.debug("takes_combo_box_changed finished")

    def update_previous_versions_table_widget(self):
        """updates the previous_versions_table_widget
        """
        logger.debug("update_previous_versions_table_widget is started")
        self.previous_versions_table_widget.clear()

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
            self.previous_versions_table_widget.clear()
            return

        # take name
        take_name = self.takes_list_widget.current_take_name

        if take_name != "":
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
        if self.show_published_only_check_box.isChecked():
            query = query.filter(Version.is_published == True)

        # show how many
        # count = self.version_count_spin_box.value()

        data_from_db = \
            query.order_by(Version.version_number.desc()).all()
        versions = list(map(lambda x: VersionNT(*x), data_from_db))
        versions.reverse()

        self.previous_versions_table_widget.update_content(versions)
        logger.debug("update_previous_versions_table_widget is finished")

    def add_take_push_button_clicked(self):
        """runs when the add_take_toolButton clicked
        """
        # open up a QInputDialog and ask for a take name
        # anything is acceptable
        # because the validation will occur in the Version instance

        self.current_dialog = QtWidgets.QInputDialog(self)

        current_take_name = self.takes_list_widget.current_take_name

        take_name, ok = self.current_dialog.getText(
            self,
            "Add Take Name",
            "New Take Name",
            QtWidgets.QLineEdit.Normal,
            current_take_name
        )

        if ok:
            # add the given text to the takes_combo_box
            # if it is not empty
            if take_name != "":
                self.takes_list_widget.add_take(take_name)

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
                "Error",
                "Please select a <strong>leaf</strong> task!"
            )
            return None

        take_name = self.takes_list_widget.current_take_name
        user = self.get_logged_in_user()
        if not user:
            self.close()

        description = self.description_text_edit.toPlainText()
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
                error_message = "%s" % e
            except UnicodeEncodeError:
                if sys.version_info[0] >= 3:
                    error_message = str(e)
                else:
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
                error_message = "%s" % e
                print(error_message)
                QtWidgets.QMessageBox.critical(
                    self,
                    "Error",
                    error_message
                )
                from stalker.db.session import DBSession
                DBSession.rollback()
                return
            finally:
                self.update_previous_versions_table_widget()

                # inform the user about what has happened
                if logger.level != logging.DEBUG:
                    QtWidgets.QMessageBox.information(
                        self,
                        "Export",
                        "%s\n\n has been exported correctly!" %
                        new_version.filename
                    )

    def save_as_push_button_clicked(self):
        """runs when the save_as_push_button clicked
        """
        logger.debug("saving the data as a new version")
        new_version = self.get_new_version()
        self.save_as_wrapper(new_version)

    def publisher_rejected(self, version=None):
        """runs when the publisher is rejected
        """
        from stalker import Version
        from stalker.db.session import DBSession
        if version and isinstance(version, Version):
            if version:
                DBSession.delete(version)
                DBSession.commit()
            DBSession.rollback()

    def publish_push_button_clicked(self):
        """runs when the publish_push_button clicked
        """
        logger.debug("saving the data as a new published version")
        answer = QtWidgets.QMessageBox.question(
            self,
            "Publish?",
            "Publish?",
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
                    version=new_version,
                    parent=self.parent()
                )

                # connect the rejected signal to delete the new version
                QtCore.QObject.connect(
                    dialog,
                    QtCore.SIGNAL("rejected()"),
                    functools.partial(self.publisher_rejected, version=new_version)
                )

                dialog.show()
                if dialog.check_all_publishers():
                    # auto run the publish button if all publishers are passing
                    dialog.publish_push_button_clicked()
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
            logger.debug("no new_version, returning back!")
            return

        # call the environments save_as method
        from stalker.db.session import DBSession
        is_external_env = False
        environment = self.environment
        if not environment:
            # get the environment
            env_name = self.environment_combo_box.currentText()
            from anima.env.external import ExternalEnvFactory
            env_factory = ExternalEnvFactory()
            environment = env_factory.get_env(
                env_name,
                self.environment_name_format
            )
            is_external_env = True
            if not environment:
                logger.debug("no env found with name: %s" % env_name)
                DBSession.rollback()
                return
            logger.debug("env: %s" % environment.name)
        else:
            # check if the version the user is trying to create and the version
            # that is currently open in the current environment belongs to the
            # same task
            current_version = environment.get_current_version()
            if current_version and current_version.task != new_version.task:
                # ask to the user if he/she is sure about that
                answer = QtWidgets.QMessageBox.question(
                    self,
                    "Possible Mistake?",
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

        if version.is_published:
            # check if this is the first version
            logger.debug("version.version_number: %s" % version.version_number)
            if version.version_number == 1:
                # it is not allowed to publish the first version
                QtWidgets.QMessageBox.critical(
                    self,
                    "Error",
                    "Can not publish the FIRST version!!!"
                    "<br><br>"
                    "Save it normally first."
                )

                DBSession.rollback()
                return

        from anima.exc import PublishError
        try:
            environment.save_as(new_version, **kwargs)
        except (RuntimeError, PublishError) as e:
            try:
                error_message = "%s" % e
            except UnicodeEncodeError:
                if sys.version_info[0] >= 3:
                    error_message = str(e)
                else:
                    error_message = unicode(e)

            print(error_message)
            QtWidgets.QMessageBox.critical(
                self,
                "Error",
                error_message
            )

            DBSession.rollback()
            return

        if is_external_env:
            # set the clipboard to the new_version.absolute_full_path
            clipboard = QtWidgets.QApplication.clipboard()

            logger.debug(
                "new_version.absolute_full_path: %s" %
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
                "Error",
                "Something went wrong with %s\n"
                "and the file is not created!\n\n"
                "Please save again!" % environment.name
            )
            DBSession.rollback()
        DBSession.commit()

        if is_external_env:
            # refresh the UI
            self.tasks_tree_view_changed()
        else:
            # close the UI
            self.close()

    def choose_version_push_button_clicked(self):
        """runs when the choose_pushButton clicked
        """
        version = self.previous_versions_table_widget.current_version
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
        if self.mode == SAVE_AS_MODE:
            return

        # get the new version
        old_version = self.previous_versions_table_widget.current_version
        skip_update_check = not self.check_updates_check_box.isChecked()

        from stalker import Version
        old_version = Version.query.get(old_version.id)

        if not self.check_version_file_exists(old_version):
            return

        # close the dialog
        # TODO: Please, please, please fix the following code!
        is_blender = False
        if self.environment and self.environment.name.lower().startswith('blender'):
            is_blender = True

        if not is_blender:
            self.close()

        # call the environments open method
        if self.environment is not None:
            repr_name = self.representations_comboBox.currentText()
            ref_depth = ref_depth_res.index(self.ref_depth_combo_box.currentText())

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
                    "RuntimeError",
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
            if reference_resolution["create"] or reference_resolution["update"]:
                # invoke the version_updater for this scene
                from anima.ui import version_updater
                version_updater_main_dialog = \
                    version_updater.MainDialog(
                        environment=self.environment,
                        parent=self,
                        reference_resolution=reference_resolution
                    )

                version_updater_main_dialog.exec_()

                # delete the dialog when it is done
                version_updater_main_dialog.deleteLater()

        if is_blender:
            self.close()

    def open_as_new_version_push_button_clicked(self):
        """Opens the selected version and immediately saves it as a new version
        """
        new_version = self.get_new_version()
        self.open_push_button_clicked()
        logger.debug("opening the data as a new version")
        self.save_as_wrapper(new_version)

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
        previous_version = self.previous_versions_table_widget.current_version

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
            use_namespace = self.use_namespace_check_box.isChecked()

            # check if it has any representations
            # .filter(Version.parent == previous_version)\
            all_repr_count = Version.query\
                .filter(Version.task == previous_version.task)\
                .filter(Version.take_name.ilike(previous_version.take_name + "@%"))\
                .count()

            if all_repr_count > 0:
                # ask which one to reference
                repr_message_box = QtWidgets.QMessageBox()
                repr_message_box.setText("Which Repr.?")
                from anima.representation import Representation
                base_button = \
                    repr_message_box.addButton(
                        Representation.base_repr_name,
                        QtWidgets.QMessageBox.ActionRole
                    )
                setattr(base_button, "repr_version", previous_version)

                for repr_name in self.environment.representations:
                    repr_str = "%{take}{repr_separator}{repr_name}%".format(
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
                        setattr(repr_button, "repr_version", repr_version)

                # add a cancel button
                cancel_button = repr_message_box.addButton(
                    "Cancel",
                    QtWidgets.QMessageBox.RejectRole
                )

                repr_message_box.exec_()
                clicked_button = repr_message_box.clickedButton()
                if clicked_button.text() != "Cancel":
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
                    exceptionMessageGenerator(e)
                )

    def import_push_button_clicked(self):
        """runs when the import_pushButton clicked
        """
        # get the previous version
        previous_version_id = \
            self.previous_versions_table_widget.current_version.id

        from stalker import Version
        previous_version = Version.query.get(previous_version_id)

        if not self.check_version_file_exists(previous_version):
            return

        # logger.debug("importing version %s" % previous_version)

        # call the environments import_ method
        if self.environment is not None:
            # get the use namespace state
            use_namespace = self.use_namespace_check_box.isChecked()

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
        ui_utils.clear_thumbnail(self.thumbnail_graphics_view)

    def update_thumbnail(self):
        """updates the thumbnail for the selected task
        """
        # get the current task
        self.clear_thumbnail_push_button.setEnabled(False)
        task_id = self.tasks_tree_view.get_task_id()
        if task_id:
            from anima.ui import utils as ui_utils
            from stalker import Task
            task = Task.query.get(task_id)
            if task and task.thumbnail:
                self.clear_thumbnail_push_button.setEnabled(True)
            ui_utils.update_graphics_view_with_task_thumbnail(
                task, self.thumbnail_graphics_view
            )

    def upload_thumbnail_push_button_clicked(self):
        """runs when the upload_thumbnail_pushButton is clicked
        """
        # get the current task
        task_id = self.tasks_tree_view.get_task_id()

        if not task_id:
            return

        from stalker import Task
        task = Task.query.get(task_id)

        if not task:
            return

        from anima.ui import utils as ui_utils
        thumbnail_full_path = ui_utils.choose_thumbnail(
            self,
            start_path=task.absolute_path,
            dialog_title="Choose Thumbnail for: %s" % task.name
        )

        # if the thumbnail_full_path is empty do not do anything
        if thumbnail_full_path == "":
            return

        anima.utils.upload_thumbnail(task, thumbnail_full_path)

        # update the thumbnail
        self.update_thumbnail()

    def clear_thumbnail_push_button_clicked(self):
        """clears the thumbnail of the current task if it has one
        """
        # check the thumbnail view first
        scene = self.thumbnail_graphics_view.scene()
        if not scene.items():
            print("returned by thumbnail_graphics_view")
            return
        print("not returned by thumbnail_graphics_view")

        task_id = self.tasks_tree_view.get_task_id()

        if not task_id:
            return

        from stalker import SimpleEntity
        from stalker.db.session import DBSession
        result = DBSession \
            .query(SimpleEntity.thumbnail_id) \
            .filter(SimpleEntity.id == task_id) \
            .first()
        thumb_id = result[0]

        if not thumb_id:
            return

        answer = QtWidgets.QMessageBox.question(
            self,
            "Delete Thumbnail?",
            "Delete Thumbnail?",
            QtWidgets.QMessageBox.Yes,
            QtWidgets.QMessageBox.No
        )

        if answer == QtWidgets.QMessageBox.Yes:
            # remove the thumbnail and its thumbnail and its thumbnail
            from stalker import Task, Link
            t = Link.query.filter(Link.id == thumb_id).first()
            task = Task.query.get(task_id)
            task.thumbnail = None
            if t.thumbnail:
                if t.thumbnail.thumbnail:
                    DBSession.delete(t.thumbnail.thumbnail)
                    t.thumbnail = None
                DBSession.delete(t.thumbnail)
            # leave the files there
            DBSession.delete(t)
            DBSession.commit()

            # update the thumbnail
            self.clear_thumbnail()

    def find_from_path(self, path):
        """Finds versions from the given path

        :param path:
        :return:
        """
        from anima.env.base import EnvironmentBase
        env = EnvironmentBase()
        if path:
            version = env.get_version_from_full_path(path)
            self.restore_ui(version)

    def find_from_path_push_button_clicked(self):
        """runs when find_from_path_pushButton is clicked
        """
        self.find_from_path(self.find_from_path_line_edit.text())

    # def search_task_comboBox_textChanged(self, text):
    #     """runs when search_task_comboBox text changed
    #     """
    #     # text = self.search_task_lineEdit.text().strip()
    #     self.search_task_comboBox.clear()
    #     if not text:
    #         return
    #     tasks = Task.query.filter(Task.name.contains(text)).all()
    #     logger.debug("tasks with text: "%s" are : %s" % (text, tasks))
    #     # load all the tasks and their parents so we are going to be able to
    #     # find them later on
    #     # for task in tasks:
    #     #     self.load_task_item_hierarchy(task, self.tasks_tree_view)
    #     #
    #     # # now get the indices
    #     # indices = self.get_item_indices_containing_text(text,
    #     #                                                 self.tasks_tree_view)
    #     # logger.debug("indices containing the given text are : %s" % indices)
    #
    #     # self.search_task_comboBox.addItems(
    #     #     [
    #     #         (task.name + " (%s)" % map(lambda x: "|".join([parent.name for parent in x.parents]), task)) for task in tasks
    #     #     ]
    #     # )
    #     items = []
    #     for task in tasks:
    #         hierarchy_name = task.name + "(" + "|".join(map(lambda x: x.name, task.parents)) + ")"
    #         items.append(hierarchy_name)
    #     self.search_task_comboBox.addItems(items)
    #

    def recent_files_combo_box_index_changed(self, path):
        """runs when the recent files combo box index has changed

        :param path: 
        :return:
        """
        current_index = self.recent_files_combo_box.currentIndex()
        if current_index != 0:  # This would be the placeholder
            path = self.recent_files_combo_box.itemData(current_index)
            self.find_from_path(path)
