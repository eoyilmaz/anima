# -*- coding: utf-8 -*-
import re

import qtawesome

from anima.ui.lib import QtCore, QtGui, QtWidgets
from anima.ui.base import ui_caller
from anima.ui.dialogs import task_picker_dialog
from anima.ui.widgets import ValidatedLineEdit
from anima.utils import get_task_hierarchy_name, get_unique_take_names

from stalker import Asset, Task, Version


TAKE_NAME_VALIDATOR_REGEX = re.compile("([A-Z]{1})([a-zA-Z0-9]+)")


if False:
    from PySide6 import QtCore, QtGui, QtWidgets


COLORS = {
    "project": {
        "fg": "#000000",
        "bg": "#ffe5bf",
    },
    "asset": {
        "fg": "#000000",
        "bg": "#c3e6a1",
    },
    "invalid_asset": {
        "fg": "#000000",
        "bg": "#f24949",
    },
    "task": {
        "fg": "#000000",
        "bg": "#acd2e5",
    },
}


def get_related_asset(task):
    """Return related Asset to the given task."""
    for parent in reversed(task.parents):
        if isinstance(parent, Asset):
            return parent
    return None


def UI(app_in=None, executor=None, **kwargs):
    """
    :param app_in: A Qt Application instance, which you can pass to let the UI
      be attached to the given applications event process.

    :param executor: Instead of calling app.exec_ the UI will call this given
      function. It also passes the created app instance to this executor.

    """
    return ui_caller(app_in, executor, AssetMigrationToolDialog, **kwargs)


class AssetStorage(object):
    """Generic storage for assets.

    This is created as a central storage for the AssetMigrationDialog. So all
    the assets are going to be stored in this class and be consumed by the UI
    elements, so that all the UI elements no matter how deep they are will be
    able to reach the data.
    """

    storage = {}

    @classmethod
    def add_entity(cls, entity):
        """Add the given entity to the storage.

        Args:
            entity (stalker.Asset | stalker.Task | stalker.Version): A
                stalker.Asset or stalker.Task or stalker.Version instance.
        """
        asset = None
        task = None
        version = None

        if isinstance(entity, Version):
            version = entity
            task = version.task

        if not task and entity.entity_type == "Task":
            # we need to find the related asset
            task = entity

        if task:
            asset = get_related_asset(task)

        if not asset and entity.entity_type == "Asset":
            asset = entity

        if asset is not None and asset not in cls.storage:
            cls.storage[asset] = {}

        if task and task not in cls.storage[asset]:
            cls.storage[asset][task] = {}

        if version:
            cls.storage[asset][task][version.take_name] = version

    @classmethod
    def add_entities(cls, entities):
        """Add the given list of assets to the storage."""
        for entity in entities:
            cls.add_entity(entity)

    @classmethod
    def remove_entity(cls, entity):
        """Remove the given entity.

        Args:
            entity (stalker.Asset | stalker.Task | stalker.Version): A
                stalker.Asset or stalker.Task or stalker.Version instance.
        """
        if isinstance(entity, Asset):
            asset = entity
            if asset in cls.storage:
                cls.storage.pop(asset)
        elif isinstance(entity, Task):
            task = entity
            asset = get_related_asset(task)
            if asset and task:
                cls.storage[asset].pop(task)
        elif isinstance(entity, Version):
            version = entity
            task = version.task
            asset = get_related_asset(task)
            if asset and task and version and task in cls.storage[asset]:
                cls.storage[asset][task].pop(version.take_name)

    @classmethod
    def is_in_storage(cls, entity):
        """Check if the given entity is in the storage.

        Args:
            entity (stalker.Asset | stalker.Task | stalker.Version): A
                stalker.Asset or stalker.Task or stalker.Version instance.

        Returns:
            bool: True if the entity is in storage False otherwise.
        """
        if entity.entity_type == "Asset":
            asset = entity
            return asset in cls.storage
        elif entity.entity_type == "Task":
            task = entity
            asset = get_related_asset(task)
            return task in cls.storage[asset]
        elif entity.entity_type == "Version":
            version = entity
            task = version.task
            asset = get_related_asset(task)
            return (
                asset in cls.storage
                and task in cls.storage[asset]
                and version.take_name in cls.storage[asset][task]
                and cls.storage[asset][task][version.take_name] == version
            )
        return False

    @classmethod
    def reset_storage(cls):
        """Reset storage."""
        cls.storage = {}


class AssetWidget(QtWidgets.QGroupBox):
    """A QGroupBox variant to hold stalker.Asset related data."""

    add_assets = QtCore.Signal(object)
    remove_asset = QtCore.Signal(object)
    version_updated = QtCore.Signal()

    def __init__(self, parent=None, asset=None):
        super(AssetWidget, self).__init__(parent=parent)
        self._asset = None
        self.main_layout = None
        self.remove_button = None
        self.pick_new_parent_button = None
        self.tasks_layout = None
        self.task_widgets = []
        self._new_parent = None
        self.new_parent_label = None
        self.setup_ui()
        self.asset = asset

    def setup_ui(self):
        """Create UI widgets."""
        self.main_layout = QtWidgets.QVBoxLayout(self)

        # Buttons layout
        buttons_layout = QtWidgets.QHBoxLayout()
        self.main_layout.addLayout(buttons_layout)

        # Remove Asset
        self.remove_button = QtWidgets.QPushButton(self)
        self.remove_button.setText("Remove Asset")
        self.remove_button.setToolTip("Removes the asset from the list.")
        self.remove_button.clicked.connect(self.remove)
        buttons_layout.addWidget(self.remove_button)

        # Pick New Parent
        self.pick_new_parent_button = QtWidgets.QPushButton(self)
        self.pick_new_parent_button.setText("Pick New Parent...")
        self.pick_new_parent_button.setToolTip("Select the new parent...")
        self.pick_new_parent_button.clicked.connect(self.pick_new_parent)
        buttons_layout.addWidget(self.pick_new_parent_button)

        # New Parent Label
        self.new_parent_label = QtWidgets.QLabel(self)
        buttons_layout.addWidget(self.new_parent_label)

        # Spacer for buttons
        buttons_layout.addSpacerItem(
            QtWidgets.QSpacerItem(
                20, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed
            )
        )

        self.tasks_layout = QtWidgets.QVBoxLayout()
        self.main_layout.addLayout(self.tasks_layout)

        self.setStyleSheet(
            "QGroupBox {{ background-color: {}; color: {}}}".format(
                COLORS["asset"]["bg"], COLORS["asset"]["fg"]
            )
        )

    def remove(self):
        """Remove self from parent."""
        self.remove_asset.emit(self)

    def pick_new_parent(self):
        """Show a TaskPickerDialog to let the user select a new parent."""
        dialog = task_picker_dialog.MainDialog(
            parent=self, project=None, allow_multi_selection=False
        )
        if self.new_parent:
            # start with the currently selected new_parent
            dialog.tasks_tree_view.find_and_select_entity_item(self.new_parent)
        dialog.exec()

        try:
            # PySide and PySide2
            accepted = QtWidgets.QDialog.DialogCode.Accepted
        except AttributeError:
            # PyQt4
            accepted = QtWidgets.QDialog.Accepted
        if dialog.result() == accepted:
            selected_tasks = dialog.tasks_tree_view.get_selected_tasks()
            dialog.deleteLater()

            if not selected_tasks:
                return

            new_parent = selected_tasks[0]
            assert isinstance(new_parent, Task)

            # don't allow a child to be a parent
            if self.asset in new_parent.parents:
                QtWidgets.QMessageBox.critical(
                    self,
                    "Invalid Parent!",
                    "Selected parent is one of the child of the Asset!!!",
                )
                return

            # don't allow the same parent
            if new_parent == self.asset.parent:
                QtWidgets.QMessageBox.critical(
                    self,
                    "Invalid Parent!",
                    "Selected parent is already the current parent!!!",
                )
                return

            # selecting a Project to be the new parent is okay
            self.new_parent = new_parent
            self.validate()

    @property
    def new_parent(self):
        """Return the new_parent attribute value.

        Returns:
            stalker.Task: The new_parent value.
        """
        return self._new_parent

    @new_parent.setter
    def new_parent(self, new_parent):
        """Set new parent."""
        self._new_parent = new_parent
        self.update_new_parent_label()
        self.validate()

    def update_new_parent_label(self):
        """Update the new parent label."""
        new_parent_hierarchy_name = "-- No New Parent Selected --"
        if self.new_parent:
            new_parent_hierarchy_name = get_task_hierarchy_name(self.new_parent)
        self.new_parent_label.setText(
            "New Parent: {}".format(new_parent_hierarchy_name)
        )

    @property
    def asset(self):
        """Return the asset.

        Returns:
            stalker.Asset: The stalker.Asset stored in this widget.
        """
        return self._asset

    @asset.setter
    def asset(self, asset):
        """Set the asset property.

        Args:
            asset (stalker.Asset):
        """
        if asset is None:
            return
        self._asset = asset
        self.setTitle(get_task_hierarchy_name(asset))
        # add all the child tasks as TaskGroupBoxes
        for child_task in sorted(asset.children, key=lambda x: x.name):
            if len(child_task.children):
                # this task has other child tasks
                # don't append it
                continue
            task_widget = TaskWidget(parent=self, task=child_task)
            task_widget.add_assets.connect(self.add_assets)
            task_widget.version_updated.connect(self.version_updated)
            self.task_widgets.append(task_widget)
            self.tasks_layout.addWidget(task_widget)

    def validate(self):
        """Validate the data."""
        # Check if there is a new parent
        if not self.new_parent:
            self.setStyleSheet(
                "QGroupBox {{ background-color: {}; color: {}}}".format(
                    COLORS["invalid_asset"]["bg"],
                    COLORS["invalid_asset"]["fg"],
                )
            )
            return False
        else:
            self.setStyleSheet(
                "QGroupBox {{ background-color: {}; color:{}}}".format(
                    COLORS["asset"]["bg"],
                    COLORS["asset"]["fg"],
                )
            )
            return True

    def check_versions(self):
        """Trigger a version check in all the child tasks widgets."""
        for task_widget in self.task_widgets:
            task_widget.check_versions()


class ProjectWidget(QtWidgets.QGroupBox):
    """A QGroupBox variant to hold stalker.Project related data."""

    remove_project = QtCore.Signal(object)

    def __init__(self, parent=None, project=None):
        super(ProjectWidget, self).__init__(parent=parent)
        self._project = None
        self.main_layout = None
        self.assets_layout = None
        self.asset_widgets = []
        self.setup_ui()
        self.project = project

    def setup_ui(self):
        """Create UI widgets."""
        self.main_layout = QtWidgets.QVBoxLayout(self)
        self.assets_layout = QtWidgets.QVBoxLayout()
        self.main_layout.addLayout(self.assets_layout)
        self.setStyleSheet(
            "QGroupBox {{ background-color: {}; color: {}}}".format(
                COLORS["project"]["bg"],
                COLORS["project"]["fg"],
            )
        )

    @property
    def project(self):
        """Return the project.

        Returns:
            stalker.Project: The project stored in this widget.
        """
        return self._project

    @project.setter
    def project(self, project):
        """Set the project property.

        Args:
            project (stalker.Project): A stalker.Project instance.
        """
        if project is None:
            return
        self._project = project
        self.update_title()

    def update_title(self):
        """Update title with the known information"""
        # update UI items.
        self.setTitle(
            "{} ({} Assets)".format(self._project.name, len(self.asset_widgets))
        )

    def add_assets(self, assets, silent=True):
        """Add the given assets as a AssetWidget.

        Args:
            assets ([stalker.Asset]): List of stalker.Asset instances.
            silent (bool): Do not show info dialog when set to False.
        """
        assets_added = []
        assets_not_added = []
        for asset in assets:
            if not isinstance(asset, Asset):
                # skip non asset entities
                continue

            if asset not in [asset_widget.asset for asset_widget in self.asset_widgets]:
                asset_widget = AssetWidget(parent=self)
                self.asset_widgets.append(asset_widget)
                self.assets_layout.addWidget(asset_widget)
                asset_widget.asset = asset
                # connect signals
                asset_widget.remove_asset.connect(self.remove_asset)
                asset_widget.version_updated.connect(self.check_versions)
                asset_widget.add_assets.connect(
                    lambda x: self.add_assets(x, silent=False)
                )
                assets_added.append(asset)

                # also store the assets in the asset storage
                AssetStorage.add_entity(asset)
            else:
                assets_not_added.append(asset)
        self.update_title()

        if not silent:
            if assets_added:
                QtWidgets.QMessageBox.information(
                    self,
                    "{} Assets added!".format(len(assets_added)),
                    "The following Assets are added:\n\n{}".format(
                        "\n".join(
                            [get_task_hierarchy_name(asset) for asset in assets_added]
                        )
                    ),
                )
            else:
                QtWidgets.QMessageBox.critical(
                    self,
                    "{} Assets NOT added!".format(len(assets_not_added)),
                    "The following Assets are NOT added:\n\n{}".format(
                        "\n".join(
                            [
                                get_task_hierarchy_name(asset)
                                for asset in assets_not_added
                            ]
                        )
                    ),
                )

    def remove_asset(self, asset_widget):
        """Remove the given asset."""
        for i, a_widget in enumerate(self.asset_widgets):
            if a_widget == asset_widget:
                self.assets_layout.removeWidget(a_widget)
                self.asset_widgets.pop(i)
                a_widget.deleteLater()
                break

        # also remove the asset from the AssetStorage
        AssetStorage.remove_entity(a_widget.asset)

        # Update Title
        self.update_title()

        # if no widget left, emit remove_project signal
        if not self.asset_widgets:
            self.remove_project.emit(self)
        else:
            self.check_versions()

    def check_versions(self):
        """Trigger a version check in all the child asset."""
        for asset_widget in self.asset_widgets:
            asset_widget.check_versions()


class StatusIcon(QtWidgets.QLabel):
    """Status icon widget.

    Use ``set_status`` method to change the status of this widget.
    """

    icon_char_lut = {
        False: {
            "icon": chr(0xF057),
            "style": "QLabel {color: red;}",
        },
        True: {
            "icon": chr(0xF058),
            "style": "QLabel {color: green;}",
        },
    }

    def __init__(self, *args, **kwargs):
        super(StatusIcon, self).__init__(*args, **kwargs)
        self._status = False
        self.setFont(qtawesome.font("fa", 16))
        self.update_icon()

    def set_status(self, status):
        """Set the status.

        Args:
            status (bool): bool status.
        """
        self._status = status
        self.update_icon()

    def update_icon(self):
        """Update the icon."""
        self.setText(self.icon_char_lut[self._status]["icon"])
        self.setStyleSheet(self.icon_char_lut[self._status]["style"])


class TakeWidget(QtWidgets.QWidget):
    """A QWidget variant to hold stalker.Task related data."""

    add_references = QtCore.Signal(object)
    version_updated = QtCore.Signal()

    def __init__(self, parent=None, task=None, take=None):
        super(TakeWidget, self).__init__(parent=parent)
        self._task = None
        self._take = None
        self.main_layout = None
        self.enable_take_check_box = None
        self.take_new_name_line_edit = None
        self.versions_combo_box = None
        self.migrate_status_icon = None
        self.no_references_message_label = None
        self.references_are_not_final_label = None
        self.all_references_are_included_label = None
        self.check_references_button = None
        self.take_new_name_validation_message_field = None
        self.setup_ui()
        self.task = task
        self.take = take

    def setup_ui(self):
        """Create UI widgets."""
        self.main_layout = QtWidgets.QHBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)

        # Enable This take Checkbox
        self.enable_take_check_box = QtWidgets.QCheckBox(self)
        self.enable_take_check_box.setChecked(True)
        self.enable_take_check_box.setText("--Take Name--")
        self.enable_take_check_box.setFixedWidth(150)
        self.enable_take_check_box.stateChanged.connect(self.enable_take)
        self.main_layout.addWidget(self.enable_take_check_box)

        # New Take Name
        take_new_name_layout = QtWidgets.QVBoxLayout()
        take_new_name_layout.setContentsMargins(0, 0, 0, 0)
        self.take_new_name_validation_message_field = QtWidgets.QLabel(self)
        self.take_new_name_validation_message_field.setStyleSheet("color: red;")
        self.take_new_name_line_edit = ValidatedLineEdit(
            parent=self, message_field=self.take_new_name_validation_message_field
        )  # QtWidgets.QLineEdit(self)
        self.take_new_name_line_edit.setToolTip("New Take Name")
        self.take_new_name_line_edit.setFixedWidth(150)
        self.take_new_name_line_edit.editingFinished.connect(self.take_new_name_edited)
        take_new_name_layout.addWidget(self.take_new_name_line_edit)
        take_new_name_layout.addWidget(self.take_new_name_validation_message_field)

        # self.main_layout.addWidget(self.take_new_name_line_edit)
        self.main_layout.addLayout(take_new_name_layout)

        # Versions
        self.versions_combo_box = QtWidgets.QComboBox()
        self.versions_combo_box.setFixedWidth(100)
        self.versions_combo_box.currentIndexChanged.connect(
            self.versions_combo_box_changed
        )
        self.main_layout.addWidget(self.versions_combo_box)

        self.no_references_message_label = QtWidgets.QLabel(self)
        self.no_references_message_label.setText("No references")
        self.no_references_message_label.setVisible(True)
        self.main_layout.addWidget(self.no_references_message_label)

        self.references_are_not_final_label = QtWidgets.QLabel(self)
        self.references_are_not_final_label.setText("Refs are not final")
        self.references_are_not_final_label.setVisible(False)
        self.main_layout.addWidget(self.references_are_not_final_label)

        self.all_references_are_included_label = QtWidgets.QLabel(self)
        self.all_references_are_included_label.setText("All refs. are included")
        self.all_references_are_included_label.setVisible(False)
        self.main_layout.addWidget(self.all_references_are_included_label)

        # Check References
        self.check_references_button = QtWidgets.QPushButton(self)
        self.check_references_button.setText("Check References...")
        self.check_references_button.setEnabled(False)
        self.check_references_button.setVisible(False)
        self.check_references_button.setToolTip(
            "Check references to other assets\n"
            "in this version and add them to the list..."
        )
        self.check_references_button.clicked.connect(self.check_references)
        self.main_layout.addWidget(self.check_references_button)

        self.main_layout.addSpacerItem(
            QtWidgets.QSpacerItem(
                20, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum
            )
        )

        # Reference Status
        self.migrate_status_icon = StatusIcon(self)
        self.main_layout.addWidget(self.migrate_status_icon)

    @property
    def task(self):
        """Return the task.

        Returns:
            stalker.Task:
        """
        return self._task

    @task.setter
    def task(self, task):
        """Set the task.

        Args:
            task (stalker.Task): The stalker.Task instance.
        """
        self._task = task

    @property
    def take(self):
        """Return the take.

        Returns:
            str: The take name that is stored in this widget.
        """
        return self._take

    @take.setter
    def take(self, take):
        """Set the take property.

        Args:
            take (stalker.Asset):
        """
        if take is None:
            return
        self._take = take
        self.enable_take_check_box.setText(take)
        self.take_new_name_line_edit.setText(take)
        self.validate_take_new_name()

        # Update Versions list
        versions = (
            Version.query.filter(Version.task == self.task)
            .filter(Version.take_name == self.take)
            .order_by(Version.version_number.desc())
            .all()
        )
        self.versions_combo_box.clear()
        for version in versions:
            self.versions_combo_box.addItem(
                "v{:03d}{}".format(
                    version.version_number,
                    " (Published)" if version.is_published else "",
                ),
                version,
            )

    def take_new_name_edited(self):
        """Check the text."""
        self.validate_take_new_name()

    def validate_take_new_name(self):
        text = self.take_new_name_line_edit.text()
        match = TAKE_NAME_VALIDATOR_REGEX.match(text)
        if not match or "".join(match.groups()) != text:
            self.migrate_status_icon.set_status(False)
            self.take_new_name_line_edit.set_invalid(
                "Take name is not in correct format"
            )
        else:
            self.migrate_status_icon.set_status(True)
            self.take_new_name_line_edit.set_valid()

    def versions_combo_box_changed(self, index):
        """Check if newly selected version has inputs.

        Args:
            index (int): Current index
        """
        version = self.versions_combo_box.currentData()
        if not version:
            return

        if version.inputs:
            # There are references in this version
            self.no_references_message_label.setVisible(False)

            missing_assets = []
            missing_versions = []

            for other_v in version.inputs:
                other_asset = get_related_asset(other_v.task)
                # Filter all the assets that are already in the AssetStorage
                if not AssetStorage.is_in_storage(other_asset):
                    missing_assets.append(other_asset)
                    missing_versions.append(other_v)
                elif not AssetStorage.is_in_storage(other_v):
                    # The asset is moving but not this version
                    missing_versions.append(other_v)

            tooltip = "\n".join(
                [
                    "{} | v{:03d}".format(
                        get_task_hierarchy_name(v.task), v.version_number
                    )
                    for v in version.inputs
                ]
            )
            self.migrate_status_icon.setToolTip(tooltip)

            if missing_assets:
                self.check_references_button.setEnabled(True)
                self.check_references_button.setVisible(True)
                self.migrate_status_icon.set_status(False)
                self.all_references_are_included_label.setVisible(False)
                self.references_are_not_final_label.setVisible(False)

            if missing_versions:
                self.check_references_button.setEnabled(True)
                self.check_references_button.setVisible(True)
                self.migrate_status_icon.set_status(False)
                self.all_references_are_included_label.setVisible(False)
                self.references_are_not_final_label.setVisible(True)

            if not missing_assets and not missing_versions:
                self.check_references_button.setEnabled(False)
                self.check_references_button.setVisible(False)
                self.migrate_status_icon.set_status(True)
                self.all_references_are_included_label.setVisible(True)
                self.references_are_not_final_label.setVisible(False)
        else:
            # no references in this version
            self.no_references_message_label.setVisible(True)
            self.check_references_button.setVisible(False)
            self.migrate_status_icon.set_status(True)
            self.all_references_are_included_label.setVisible(False)

        # trigger a version update
        if not AssetStorage.is_in_storage(version):
            AssetStorage.add_entity(version)
            self.version_updated.emit()

    def check_references(self):
        """Check references of the selected takes.

        Add the referenced assets to the end of the list.
        """
        version = self.versions_combo_box.currentData()
        referenced_assets_dialog = ReferencedAssetTasksDialog(parent=self)
        tasks = set()
        for other_v in version.inputs:
            tasks.add(other_v.task)

        for task in tasks:
            referenced_assets_dialog.add_task(task)

        referenced_assets_dialog.exec()
        # and refresh the TaskTreeView
        try:
            # PySide and PySide2
            accepted = QtWidgets.QDialog.DialogCode.Accepted
        except AttributeError:
            # PyQt4
            accepted = QtWidgets.QDialog.Accepted

        if not referenced_assets_dialog.result() == accepted:
            return

        # get the selected assets
        assets = referenced_assets_dialog.get_selected_assets()
        if assets:
            self.add_references.emit(assets)

    def enable_take(self, state):
        """Enable or disable take.

        Args:
            state (bool): Enable or disable state.
        """
        self.take_new_name_line_edit.setEnabled(state)
        self.versions_combo_box.setEnabled(state)
        self.check_references_button.setEnabled(state)
        self.all_references_are_included_label.setEnabled(state)
        self.no_references_message_label.setEnabled(state)
        version = self.versions_combo_box.currentData()
        if not state:
            # this take has been disabled, we don't care about the validity of
            # the new take name field
            self.migrate_status_icon.setVisible(False)
            self.take_new_name_line_edit.set_valid()

            # remove the version from the AssetStorage
            AssetStorage.remove_entity(version)
        else:
            # this take is re-enabled, re-validate the new take name
            self.migrate_status_icon.setVisible(True)
            self.validate_take_new_name()

            # add the version to the AssetStorage
            AssetStorage.add_entity(version)

        # trigger an version check update
        self.version_updated.emit()


class TaskWidget(QtWidgets.QGroupBox):
    """A QGroupBox variant to hold stalker.Task related data."""

    add_assets = QtCore.Signal(object)
    version_updated = QtCore.Signal()

    def __init__(self, parent=None, task=None):
        super(TaskWidget, self).__init__(parent=parent)
        self._task = None
        self.main_layout = None
        self.no_versions_place_holder = None
        self.takes_layout = None
        self.take_widgets = []
        self.setup_ui()
        self.task = task

    def setup_ui(self):
        """Create UI widgets."""
        self.main_layout = QtWidgets.QVBoxLayout(self)
        self.main_layout.setContentsMargins(12, 0, 12, 0)
        self.takes_layout = QtWidgets.QVBoxLayout()
        self.takes_layout.setContentsMargins(12, 0, 12, 0)
        self.no_versions_place_holder = QtWidgets.QLabel(self)
        self.no_versions_place_holder.setText("--- No Versions ---")
        self.no_versions_place_holder.setDisabled(True)
        self.takes_layout.addWidget(self.no_versions_place_holder)
        self.main_layout.addLayout(self.takes_layout)
        self.setStyleSheet(
            "QGroupBox {{ background-color: {}; color: {}}}".format(
                COLORS["task"]["bg"],
                COLORS["task"]["fg"],
            )
        )

    @property
    def task(self):
        """Return the task.

        Returns:
            stalker.Asset: The stalker.Asset stored in this widget.
        """
        return self._task

    @task.setter
    def task(self, task):
        """Set the task property.

        Args:
            task (stalker.Asset):
        """
        if task is None:
            return
        self._task = task
        self.setTitle(task.name)
        # add all the takes of this task as a TakeWidget

        take_names = get_unique_take_names(self._task.id)
        for take in take_names:
            take_widget = TakeWidget(parent=self, task=self._task, take=take)
            self.takes_layout.addWidget(take_widget)
            take_widget.add_references.connect(self.add_assets)
            take_widget.version_updated.connect(self.version_updated)
            self.take_widgets.append(take_widget)
        if take_names:
            self.no_versions_place_holder.setVisible(False)

    def check_versions(self):
        """Trigger a version check in all the child takes."""
        for take_widget in self.take_widgets:
            take_widget.versions_combo_box_changed(-1)


class AssetMigrationToolDialog(QtWidgets.QDialog):
    """Asset Migration Tool Dialog.

    This is a UI to help migrating assets (and all the referenced files, including DCC
    scripts, texture and audio files etc.) to a new project.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.main_layout = None
        self.pick_assets_button = None
        self.projects_scroll_area = None
        self.projects_layout = None
        self.project_widgets = []
        self.migrate_button = None
        self.task_tree_view = None
        self.setup_ui()

    def setup_ui(self):
        """Create UI elements."""
        self.setWindowTitle("Asset Migration Tool")
        self.resize(900, 1000)
        self.main_layout = QtWidgets.QVBoxLayout(self)

        # Dialog Label
        dialog_label = QtWidgets.QLabel(self)
        dialog_label.setText("Asset Migration Tool")
        dialog_label.setStyleSheet("color: rgb(71, 143, 202);font: 18pt;")
        self.main_layout.addWidget(dialog_label)

        # Title Line
        line = QtWidgets.QFrame(self)
        line.setFrameShape(QtWidgets.QFrame.HLine)
        line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.main_layout.addWidget(line)

        # Pick Assets button
        self.pick_assets_button = QtWidgets.QPushButton(self)
        self.pick_assets_button.setText("Pick Assets...")
        self.pick_assets_button.clicked.connect(self.pick_assets)
        self.main_layout.addWidget(self.pick_assets_button)

        self.projects_scroll_area = QtWidgets.QScrollArea(self)
        self.projects_scroll_area.setWidgetResizable(True)
        projects_inner_widget = QtWidgets.QWidget(self)
        self.projects_scroll_area.setWidget(projects_inner_widget)
        self.main_layout.addWidget(self.projects_scroll_area)

        self.projects_layout = QtWidgets.QVBoxLayout()
        projects_inner_widget.setLayout(self.projects_layout)

        # A TaskTreeView can also be used
        # self.task_tree_view = TaskTreeView(parent=self, show_takes=True)
        # self.main_layout.addWidget(self.task_tree_view)

        self.migrate_button = QtWidgets.QPushButton(self)
        self.migrate_button.setText("Migrate")
        self.migrate_button.clicked.connect(self.migrate)
        self.main_layout.addWidget(self.migrate_button)

        self.projects_layout.addItem(
            QtWidgets.QSpacerItem(
                20, 20, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding
            )
        )

    def pick_assets(self):
        """Show a Task Picker Dialog."""
        dialog = task_picker_dialog.MainDialog(
            parent=self, project=None, allow_multi_selection=True
        )
        dialog.exec()
        try:
            # PySide and PySide2
            accepted = QtWidgets.QDialog.DialogCode.Accepted
        except AttributeError:
            # PyQt4
            accepted = QtWidgets.QDialog.Accepted

        if dialog.result() == accepted:
            assets_added = []
            assets = dialog.tasks_tree_view.get_selected_tasks()
            dialog.deleteLater()

            if not assets:
                return

            # create a group box for the project for each selected asset
            for asset in assets:
                if not isinstance(asset, Asset):
                    continue
                project_widget = None
                for p_widget in self.project_widgets:
                    if p_widget.project == asset.project:
                        project_widget = p_widget
                        break

                if not project_widget:
                    project_widget = ProjectWidget(parent=self)
                    self.project_widgets.append(project_widget)
                    self.projects_layout.insertWidget(
                        self.projects_layout.count() - 1, project_widget
                    )
                    project_widget.project = asset.project

                project_widget.add_assets([asset], silent=True)
                # If a TaskTreeView is used, use the following to add the tasks
                # self.task_tree_view.tasks += [asset]
                assets_added.append(asset)
                # also walk through child tasks of this asset and try to find
                # more assets
                child_tasks = [task for task in asset.children]
                while child_tasks:
                    child_task = child_tasks.pop(0)
                    if isinstance(child_task, Asset):
                        assets.append(child_task)
                    else:
                        child_tasks += [task for task in child_task.children]

                # connect the signal
                project_widget.remove_project.connect(self.remove_project)

            # Trigger a Version check on all the take widgets
            for project_widget in self.project_widgets:
                project_widget.check_versions()

            if not assets_added:
                QtWidgets.QMessageBox.critical(
                    self,
                    "No Assets Selected",
                    "No Assets selected!",
                )
                return

    def remove_project(self, project_widget):
        """Remove the given project from the list.

        Args:
            project_widget (ProjectWidget): A ProjectWidget instance.
        """
        for i, child_project_widget in enumerate(self.project_widgets):
            if child_project_widget == project_widget:
                child_project_widget.deleteLater()
                self.project_widgets.pop(i)
                break

    def migrate(self):
        """Migrate assets."""
        # Validate all assets first
        invalid_assets = []
        for project_widget in self.project_widgets:
            for asset_widget in project_widget.asset_widgets:
                if not asset_widget.validate():
                    invalid_assets.append(asset_widget)

        if invalid_assets:
            QtWidgets.QMessageBox.critical(
                self,
                "Invalid Assets!",
                "There are invalid assets (marked with red).\n\nPlease fix them!",
            )
            return

        # if all assets are valid, do the migration work


class ReferencedAssetTasksDialog(QtWidgets.QDialog):
    """Show a list of Tasks referenced to another scene."""

    def __init__(self, parent=None, *args, **kwargs):
        super(ReferencedAssetTasksDialog, self).__init__(parent=parent)
        self.main_layout = None
        self.assets_list_view = None
        self.add_selected_assets_button = None
        self.setup_ui()

    def setup_ui(self):
        self.resize(600, 500)
        self.main_layout = QtWidgets.QVBoxLayout(self)

        # Info Label
        info_label = QtWidgets.QLabel(self)
        info_label.setText(
            "Select Assets to add\nDisabled items are already in the list!!!"
        )
        self.main_layout.addWidget(info_label)

        # Assets List Widget
        self.assets_list_view = AssetsListView(parent=self)
        self.assets_list_view.setModel(AssetItemModel())
        self.main_layout.addWidget(self.assets_list_view)

        # Add Selected Asset button
        self.add_selected_assets_button = QtWidgets.QPushButton(self)
        self.add_selected_assets_button.setText("Add Selected Assets")
        self.add_selected_assets_button.clicked.connect(self.accept)
        self.main_layout.addWidget(self.add_selected_assets_button)

    def add_task(self, task):
        """Add the given task.

        Args:
            task (stalker.Task): A stalker Task instance.
        """
        # check if the task is contained by one of the items
        asset = None
        if isinstance(task, Task):
            # try to get the closes asset to this task
            for parent in reversed(task.parents):
                if isinstance(parent, Asset):
                    asset = parent
                    break
        elif isinstance(task, Asset):
            asset = task

        asset_item_model = self.assets_list_view.model()
        assert isinstance(asset_item_model, AssetItemModel)
        asset_item_model.add_asset(asset)

    def get_selected_assets(self):
        """Get selected assets."""
        return self.assets_list_view.get_selected_assets()


class AssetsListView(QtWidgets.QListView):
    """Asset specific list view derivative."""

    def __init__(self, parent=None, *args, **kwargs):
        super(AssetsListView, self).__init__(parent=parent, *args, *kwargs)
        self.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)

    def get_selected_items(self):
        """Return selected AssetItems.

        Returns:
            list: List of AssetItem instances.
        """
        selection_model = self.selectionModel()
        indexes = selection_model.selectedIndexes()
        asset_items = []
        if indexes:
            item_model = self.model()
            for index in indexes:
                current_item = item_model.itemFromIndex(index)
                if current_item and isinstance(current_item, AssetItem):
                    asset_items.append(current_item)
        return asset_items

    def get_selected_assets(self):
        """Return selected Assets.

        Returns:
            list: List of stalker.Asset instances.
        """
        assets = []
        for asset_item in self.get_selected_items():
            assets.append(asset_item.asset)
        return assets


class AssetItemModel(QtGui.QStandardItemModel):
    """Asset item model."""

    def __init__(self):
        super(AssetItemModel, self).__init__()

    def flags(self, model_index):
        """Return model flags.

        Args:
            model_index: The item models index.

        Returns:
            int: Combined enum data of model flags.
        """
        default_flags = QtCore.Qt.ItemIsEnabled
        if model_index.isValid():
            item = self.itemFromIndex(model_index)
            return item.flags()
        return default_flags

    def add_asset(self, asset):
        """Add the given asset.

        Args:
            asset (stalker.Asset): A stalker.Asset instance.
        """
        # add this asset as it is not in the list
        found_item = None
        for i in range(self.rowCount()):
            item = self.item(i, 0)
            if isinstance(item, AssetItem) and item.asset == asset:
                found_item = item
                break

        if not found_item:
            asset_item = AssetItem(asset=asset)
            # disable this item if this is already in the AssetStorage
            if AssetStorage.is_in_storage(asset):
                asset_item.setFlags(
                    asset_item.flags()
                    & ~QtCore.Qt.ItemIsSelectable
                    & ~QtCore.Qt.ItemIsEnabled
                )
            self.appendRow(asset_item)


class AssetItem(QtGui.QStandardItem):
    """Asset item."""

    def __init__(self, asset=None, *args, **kwargs):
        super(AssetItem, self).__init__(*args, **kwargs)
        self._asset = None
        self.asset = asset

    @property
    def asset(self):
        """Return the asset.

        Returns:
            stalker.Asset: The stalker.Asset instance stored in this item.
        """
        return self._asset

    @asset.setter
    def asset(self, asset):
        """Set the asset attribute.

        Args:
            asset (stalker.Asset): A stalker Asset instance.
        """
        if asset is None:
            # This is not an asset related task
            RuntimeError("Not an asset or asset related task given.")
        else:
            self._asset = asset
            self.setData(
                get_task_hierarchy_name(asset), QtCore.Qt.ItemDataRole.DisplayRole
            )
