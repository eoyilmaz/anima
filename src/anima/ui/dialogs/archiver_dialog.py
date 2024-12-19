# -*- coding: utf-8 -*-
"""Archiver related UI."""
import os.path
import re
import tempfile

from stalker import Version

from anima.ui.lib import QtCore, QtGui, QtWidgets
from anima.ui.dialogs.version_dialog import MainDialog, OPEN_MODE, VersionNT
from anima.utils import get_task_hierarchy_name
from anima.utils.archive import archive_versions

if False:
    from PySide6 import QtCore, QtGui, QtWidgets


PROJECT_NAME_REGEX = re.compile("([A-Z])([a-zA-Z0-9_]+)")


class MultiVersionSelectDialog(MainDialog):
    """A dialog for archiving multiple scenes at once.

    This derives from the version dialog.
    """

    def __init__(self, environment=None, parent=None, archiver=None):
        self.add_version_push_button = None
        self.archive_button = None
        self.archiver = archiver
        super(MultiVersionSelectDialog, self).__init__(
            environment=environment, parent=parent, mode=OPEN_MODE
        )

    def _setup_ui(self):
        super(MultiVersionSelectDialog, self)._setup_ui()
        # disable buttons
        self.switch_mode_button.setVisible(False)
        self.switch_mode_button.setEnabled(False)
        self.repr_as_separate_takes_check_box.setVisible(False)
        self.repr_as_separate_takes_check_box.setEnabled(False)
        self.add_take_push_button.setVisible(False)
        self.add_take_push_button.setEnabled(False)
        self.thumbnail_group_box.setVisible(False)
        self.thumbnail_group_box.setEnabled(False)

        # secondary controls
        self.representations_label.setVisible(False)
        self.representations_label.setEnabled(False)
        self.representations_comboBox.setVisible(False)
        self.representations_comboBox.setEnabled(False)
        self.reference_depth_label.setVisible(False)
        self.reference_depth_label.setEnabled(False)
        self.ref_depth_combo_box.setVisible(False)
        self.ref_depth_combo_box.setEnabled(False)
        self.use_namespace_check_box.setVisible(False)
        self.use_namespace_check_box.setEnabled(False)
        self.choose_version_push_button.setVisible(False)
        self.choose_version_push_button.setEnabled(False)
        self.check_updates_check_box.setVisible(False)
        self.check_updates_check_box.setEnabled(False)

        for index in range(self.previous_version_secondary_controls_layout.count()):
            item = self.previous_version_secondary_controls_layout.itemAt(0)
            self.previous_version_secondary_controls_layout.removeItem(item)

        for index in range(self.open_buttons_layout.count()):
            item = self.open_buttons_layout.itemAt(0)
            self.open_buttons_layout.removeItem(item)
        self.open_buttons_layout.insertSpacerItem(
            0,
            QtWidgets.QSpacerItem(
                40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum
            ),
        )

        # create a new ListView for the selected versions
        self.versions_main_layout.insertWidget(2, QtWidgets.QLabel("Selected Versions"))
        self.selected_versions_list_view = SelectedVersionsListView(self)
        self.versions_main_layout.insertWidget(3, self.selected_versions_list_view)
        self.selected_versions_list_view.go_to_version.connect(
            lambda v: self.tasks_tree_view.find_and_select_entity_item(v.task)
        )

        # Add a Archive button
        self.archive_button = QtWidgets.QPushButton(self)
        self.archive_button.setText("Archive")
        self.archive_button.clicked.connect(self.archive_selected_versions)

        self.open_buttons_layout.addWidget(self.archive_button)

        # Add the close button to the layout again
        self.open_buttons_layout.addWidget(self.close1_push_button)

        # remove the other buttons
        self.open_push_button.setEnabled(False)
        self.open_push_button.setVisible(False)
        self.open_as_new_version_push_button.setEnabled(False)
        self.open_as_new_version_push_button.setVisible(False)
        self.reference_push_button.setEnabled(False)
        self.reference_push_button.setVisible(False)
        self.import_push_button.setEnabled(False)
        self.import_push_button.setVisible(False)

    def _set_defaults(self):
        super(MultiVersionSelectDialog, self)._set_defaults()
        # re-arrange signals
        # disconnect old ones
        self.previous_versions_table_widget.cellDoubleClicked.disconnect()
        self.previous_versions_table_widget.customContextMenuRequested.disconnect()
        # do new connections.
        self.previous_versions_table_widget.cellDoubleClicked.connect(
            self.add_version_selected_version
        )

    def set_mode(self, mode):
        # always use open mode
        super(MultiVersionSelectDialog, self).set_mode(OPEN_MODE)

    def update_window_title(self):
        super(MultiVersionSelectDialog, self).update_window_title()
        self.setWindowTitle("Archiver - Version Selection Dialog")

    def add_version_selected_version(self, *args, **kwargs):
        """Add the selected version to the list."""
        version = self.previous_versions_table_widget.current_version
        self.selected_versions_list_view.add_version(version)

    def archive_selected_versions(self):
        """Archive selected versions."""
        versions = self.selected_versions_list_view.get_selected_versions()
        if not versions:
            return
        self.close()
        dialog = ArchiverDialog(
            parent=self.parent(), versions=versions, archiver=self.archiver
        )
        dialog.exec_()


class SelectedVersionsListView(QtWidgets.QListView):
    """A ListView derivative to store selected items."""

    go_to_version = QtCore.Signal(object)

    def __init__(self, parent=None, versions=None):
        super(SelectedVersionsListView, self).__init__(parent=parent)
        self.setModel(SelectedVersionsModel())
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.custom_context_menu)

        if versions is None:
            versions = []
        else:
            self.add_versions(versions)

    def add_versions(self, versions):
        """Add versions.

        Args:
            versions (List[stalker.Version]): List of stalker.Version instances.
        """
        if not versions:
            return

        model = self.model()
        for version in versions:
            model.add_version(version)

    def add_version(self, version):
        """Add the given version."""
        model = self.model()
        model.add_version(version)

    def get_selected_versions(self):
        """Return selected versions.

        Returns:
            list: List of selected versions.
        """
        versions = []
        model = self.model()
        for i in range(model.rowCount()):
            index = model.index(i, 0)
            item = model.itemFromIndex(index)
            versions.append(item.version)

        return versions

    def custom_context_menu(self, position):
        """Custom context menu."""
        index = self.indexAt(position)
        model = self.model()
        item = model.itemFromIndex(index)
        if not isinstance(item, SelectedVersionItem):
            return

        menu = QtWidgets.QMenu()
        go_to_version_action = menu.addAction("Go To Version")
        remove_item_action = menu.addAction("Remove Version")
        global_position = self.mapToGlobal(position)
        selected_action = menu.exec_(global_position)
        if not selected_action:
            return

        if selected_action == remove_item_action:
            model.removeRow(index.row())
        elif selected_action == go_to_version_action:
            self.go_to_version.emit(item.version)


class SelectedVersionsModel(QtGui.QStandardItemModel):
    """Item model for selected versions list."""

    def __init__(self):
        super(SelectedVersionsModel, self).__init__()

    def add_version(self, version):
        """Add the given version."""
        exists = False
        for i in range(self.rowCount()):
            index = self.index(i, 0)
            item = self.itemFromIndex(index)
            if isinstance(item, SelectedVersionItem) and item.version.id == version.id:
                exists = True
                break

        if not exists:
            version_item = SelectedVersionItem(0, 1, version=version)
            self.appendRow(version_item)


class SelectedVersionItem(QtGui.QStandardItem):
    """Item for SelectedVersion."""

    def __init__(self, *args, **kwargs):
        version = kwargs.pop("version")
        super(SelectedVersionItem, self).__init__(*args, **kwargs)
        self._version = None
        self.version = version

    @property
    def version(self):
        """Getter for the version property."""
        return self._version

    @version.setter
    def version(self, version):
        """Setter for the version property."""
        if isinstance(version, VersionNT):
            # convert it to a real version
            version = Version.query.filter(Version.id == version.id).first()

        self._version = version
        v = version
        self.setData(
            "{} | {} | v{:03d}".format(
                get_task_hierarchy_name(v.task), v.variant_name, v.version_number
            ),
            QtCore.Qt.DisplayRole,
        )


class ArchiverDialog(QtWidgets.QDialog):
    """Archiver dialog."""

    def __init__(self, parent=None, versions=None, archiver=None):
        super(ArchiverDialog, self).__init__(parent=parent)
        self.archiver = archiver

        if versions is None:
            versions = []
        self.versions = versions
        self.main_layout = None
        self.form_layout = None
        self.project_name_line_edit = None
        self.output_path_widget = None
        self.select_output_path_button = None
        self.temp_path_widget = None
        self.select_temp_path_button = None
        self.versions_list_view = None
        self.zip_file_path_widget = None
        self.archive_button = None
        self.cancel_button = None
        self.setup_ui()

    def setup_ui(self):
        """set up the ui widgets."""
        self.setWindowTitle("Archiver Dialog - ZIP File Creation")
        self.resize(800, 300)
        self.main_layout = QtWidgets.QVBoxLayout(self)
        self.form_layout = QtWidgets.QFormLayout()
        self.main_layout.addLayout(self.form_layout)

        # store roles
        label_role = QtWidgets.QFormLayout.LabelRole
        field_role = QtWidgets.QFormLayout.FieldRole

        # Field index counter
        i = -1

        # Project Name
        i += 1
        self.project_name_line_edit = QtWidgets.QLineEdit(self)
        self.form_layout.setWidget(
            i, label_role, QtWidgets.QLabel("Project Name", self)
        )
        self.form_layout.setWidget(i, field_role, self.project_name_line_edit)

        # Output Path
        i += 1
        output_path_layout = QtWidgets.QHBoxLayout()
        self.output_path_widget = QtWidgets.QLabel(self)
        self.output_path_widget.setTextInteractionFlags(
            QtCore.Qt.TextInteractionFlag.TextSelectableByMouse
        )
        self.select_output_path_button = QtWidgets.QPushButton(self)
        self.select_output_path_button.setText("...")
        self.select_output_path_button.setFixedWidth(20)
        self.select_output_path_button.clicked.connect(self.select_output_path)
        output_path_layout.addWidget(self.output_path_widget)
        output_path_layout.addWidget(self.select_output_path_button)
        output_path_layout.setStretch(0, 1)
        output_path_layout.setStretch(1, 0)

        self.form_layout.setWidget(i, label_role, QtWidgets.QLabel("Output Path", self))
        self.form_layout.setLayout(i, field_role, output_path_layout)

        # Temp Path
        i += 1
        temp_path_layout = QtWidgets.QHBoxLayout()
        self.temp_path_widget = QtWidgets.QLabel(self)
        self.temp_path_widget.setText(tempfile.gettempdir())
        self.temp_path_widget.setTextInteractionFlags(
            QtCore.Qt.TextInteractionFlag.TextSelectableByMouse
        )
        self.select_temp_path_button = QtWidgets.QPushButton(self)
        self.select_temp_path_button.setText("...")
        self.select_temp_path_button.setFixedWidth(20)
        self.select_temp_path_button.clicked.connect(self.select_temp_path)
        temp_path_layout.addWidget(self.temp_path_widget)
        temp_path_layout.addWidget(self.select_temp_path_button)
        temp_path_layout.setStretch(0, 1)
        temp_path_layout.setStretch(1, 0)

        self.form_layout.setWidget(i, label_role, QtWidgets.QLabel("Temp Path", self))
        self.form_layout.setLayout(i, field_role, temp_path_layout)

        # Versions List View
        i += 1
        self.versions_list_view = SelectedVersionsListView(
            parent=self, versions=self.versions
        )
        self.form_layout.setWidget(i, label_role, QtWidgets.QLabel("Versions", self))
        self.form_layout.setWidget(i, field_role, self.versions_list_view)

        # ZIP File Path
        i += 1
        self.zip_file_path_widget = QtWidgets.QLabel(self)
        self.zip_file_path_widget.setTextInteractionFlags(
            QtCore.Qt.TextInteractionFlag.TextSelectableByMouse
        )
        self.form_layout.setWidget(
            i, label_role, QtWidgets.QLabel("ZIP File Path", self)
        )
        self.form_layout.setWidget(i, field_role, self.zip_file_path_widget)

        # Button Layout
        button_layout = QtWidgets.QHBoxLayout()
        button_layout.addSpacerItem(
            QtWidgets.QSpacerItem(
                20, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum
            )
        )

        # Archive Button
        self.archive_button = QtWidgets.QPushButton(self)
        self.archive_button.setText("Do Archive!")
        self.archive_button.clicked.connect(self.do_archive)
        button_layout.addWidget(self.archive_button)

        # Cancel Button
        self.cancel_button = QtWidgets.QPushButton(self)
        self.cancel_button.setText("Cancel")
        self.cancel_button.clicked.connect(self.close)
        button_layout.addWidget(self.cancel_button)

        self.main_layout.addLayout(button_layout)

    def select_output_path(self):
        """Select an output path."""
        output_path = QtWidgets.QFileDialog(
            self, "Choose Output Folder"
        ).getExistingDirectory()
        if not output_path:
            return
        self.output_path_widget.setText(output_path)

    def select_temp_path(self):
        """Select a temp path."""
        temp_path = QtWidgets.QFileDialog(self, "Temp Folder").getExistingDirectory()
        if not temp_path:
            return
        self.temp_path_widget.setText(temp_path)

    @classmethod
    def validate_project_name(cls, project_name):
        """Validate the given project name.

        Args:
            project_name (str): Project name to validate.
        """
        match = PROJECT_NAME_REGEX.match(project_name)
        if not match or "".join(match.groups()) != project_name:
            return False
        return True

    @classmethod
    def validate_output_path(cls, output_path):
        """Validate the given output_path.

        Args:
            output_path (str): The output folder path.
        """
        if not os.path.exists(output_path):
            return False
        return True

    @classmethod
    def validate_temp_path(cls, temp_path):
        """Validate the given temp_path.

        Args:
            temp_path (str): The temp folder path.
        """
        if not os.path.exists(temp_path):
            return False
        return True

    def do_archive(self):
        """Do archive."""
        if not self.versions:
            QtWidgets.QMessageBox.critical(self, "Error!", "No Version is given!")
            return

        project_name = self.project_name_line_edit.text()
        output_path = self.output_path_widget.text()
        temp_path = self.temp_path_widget.text()

        if not self.validate_project_name(project_name):
            QtWidgets.QMessageBox.critical(
                self, "Error!", "Please supply a valid project name!"
            )
            return

        if not self.validate_output_path(output_path):
            QtWidgets.QMessageBox.critical(
                self, "Error!", "Please supply a valid output_path!"
            )
            return

        if not self.validate_temp_path(temp_path):
            QtWidgets.QMessageBox.critical(
                self, "Error!", "Please supply a valid temp path!"
            )
            return

        archive_versions(
            versions=self.versions,
            archiver=self.archiver,
            project_name=project_name,
            output_path=output_path,
            tempdir=temp_path,
            prompt=False,
        )
