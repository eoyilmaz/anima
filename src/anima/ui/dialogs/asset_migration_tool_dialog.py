# -*- coding: utf-8 -*-
import copy
import pprint
import re

import qtawesome

from anima.ui.base import ui_caller
from anima.ui.dialogs import task_picker_dialog
from anima.ui.lib import QtCore, QtGui, QtWidgets
from anima.ui.widgets import ValidatedLineEdit
from anima.utils import get_task_hierarchy_name, get_unique_variant_names

from stalker import Asset, Task, Version, Shot, Sequence

variant_name_VALIDATOR_REGEX = re.compile("([A-Z])([a-zA-Z0-9]+)")


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
    "task": {
        "fg": "#000000",
        "bg": "#acd2e5",
    },
    "invalid": {
        "fg": "#000000",
        "bg": "#d492f2",
    },
}


def get_related_asset(task):
    """Return related Asset to the given task.

    Args:
        task (stalker.Task): stalker.Task instance.

    Returns:
        Union[None, stalker.Asset]: The related Asset or None.
    """
    for parent in reversed(task.parents):
        if isinstance(parent, Asset):
            return parent
    return None


def get_intermediate_tasks(task1, task2):
    """Calculate the intermediate tasks between the given tasks.

    Args:
        task1 (stalker.Task): parent task.
        task2 (stalker.Task): child task.

    Returns:
        List[stalker.Task]: The intermediate tasks, also contains the second task,
          if the tasks are not hierarchically connected an empty list will be returned.
    """
    # create a list of tasks hierarchically in between the two tasks
    # A
    #  B
    #   C
    #    D
    # get_intermediate_tasks(A, D) --> [B, C, D]
    intermediate_tasks = []
    found_orig_task = False
    for parent in reversed(task2.parents + [task2]):
        if parent != task1:
            intermediate_tasks.append(parent)
        else:
            found_orig_task = True
            break
    if found_orig_task:
        return list(reversed(intermediate_tasks))
    else:
        return []


def UI(app_in=None, executor=None, **kwargs):
    """
    :param app_in: A Qt Application instance, which you can pass to let the UI
      be attached to the given applications event process.

    :param executor: Instead of calling app.exec_ the UI will call this given
      function. It also passes the created app instance to this executor.

    """
    return ui_caller(app_in, executor, AssetMigrationToolDialog, **kwargs)


class EntityStorage(object):
    """Generic storage for tasks.

    This is created as a central storage for the AssetMigrationDialog. So all
    the tasks are going to be stored in this class and be consumed by the UI
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
            cls.storage[asset][task][version.variant_name] = version

    @classmethod
    def add_entities(cls, entities):
        """Add the given list of tasks to the storage."""
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
            if (
                asset
                and task
                and version
                and task in cls.storage[asset]
                and version.variant_name in cls.storage[asset][task]
            ):
                cls.storage[asset][task].pop(version.variant_name)

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
            return asset in cls.storage and task in cls.storage[asset]
        elif entity.entity_type == "Version":
            version = entity
            task = version.task
            asset = get_related_asset(task)
            return (
                asset in cls.storage
                and task in cls.storage[asset]
                and version.variant_name in cls.storage[asset][task]
                and cls.storage[asset][task][version.variant_name] == version
            )
        return False

    @classmethod
    def reset_storage(cls):
        """Reset storage."""
        cls.storage = {}


class ProjectWidget(QtWidgets.QGroupBox):
    """A QGroupBox variant to hold stalker.Project related data."""

    remove_project = QtCore.Signal(object)

    def __init__(self, parent=None, project=None):
        super(ProjectWidget, self).__init__(parent=parent)
        self._project = None
        self.main_layout = None
        self.tasks_layout = None
        self.task_widgets = []
        self.setup_ui()
        self.project = project

    def setup_ui(self):
        """Create UI widgets."""
        self.main_layout = QtWidgets.QVBoxLayout(self)
        self.tasks_layout = QtWidgets.QVBoxLayout()
        self.main_layout.addLayout(self.tasks_layout)
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
            # "{} ({} Assets)".format(self._project.name, len(self.task_widgets))
            "{}".format(self._project.name)
        )

    def add_assets(self, assets, silent=True):
        """Add the given assets as a TaskWidget.

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

            if asset not in [task_widget.task for task_widget in self.task_widgets]:
                task_widget = TaskWidget(parent=self)
                self.task_widgets.append(task_widget)
                self.tasks_layout.addWidget(task_widget)
                task_widget.task = asset
                # connect signals
                task_widget.remove_task.connect(self.remove_task)
                task_widget.version_updated.connect(self.check_versions)
                task_widget.add_task.connect(self.add_tasks)
                assets_added.append(asset)

                # store the tasks in the task storage
                EntityStorage.add_entity(asset)

                # add all the immediate child tasks that has a version to the list
                task_widget.add_child_tasks(
                    [child_task for child_task in asset.children if child_task.versions]
                )

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

    def add_tasks(self, tasks):
        """Add the given tasks as a TaskWidget.

        Args:
            tasks ([stalker.Task]): List of stalker.Task instances.
        """
        # this is a Project widget
        # now, for each task
        for task in tasks:
            found_task_widget = None
            rest_of_the_tasks = None
            all_parents = copy.copy(task.parents) + [task]
            # iterate over parents,
            for i, parent in enumerate(all_parents):
                # try to find a child widget,
                # that has one of the parents of that particular task
                for task_widget in self.task_widgets:
                    if parent == task_widget.task:
                        # okay, we found a child widget that has one of the parents
                        # give the rest of the tasks to that widget,
                        # so that it can add them as child widgets.
                        rest_of_the_tasks = all_parents[i + 1:]
                        found_task_widget = task_widget
                        break
                if found_task_widget and rest_of_the_tasks:
                    break
            if found_task_widget and rest_of_the_tasks:
                # if we found a widget,
                # give the rest of the tasks to that widget, so that it
                # adds them appropriately
                assert isinstance(found_task_widget, TaskWidget)
                found_task_widget.add_child_tasks(rest_of_the_tasks)
            else:
                # If we couldn't find a proper task widget that has any of the parents,
                # get list of parents related to the asset,
                # and add all immediate children tasks as a new TaskWidget.

                # okay we couldn't find an appropriate TaskWidget
                # add this as an asset
                asset = get_related_asset(task)
                self.add_assets([asset])
        # trigger a version check
        self.check_versions()

    def remove_task(self, task_widget):
        """Remove the given asset."""
        # also remove the asset from the EntityStorage
        EntityStorage.remove_entity(task_widget.task)

        # Remove from the self
        for i, t_widget in enumerate(self.task_widgets):
            if t_widget == task_widget:
                self.tasks_layout.removeWidget(t_widget)
                self.task_widgets.pop(i)
                break
        task_widget.deleteLater()

        # Update Title
        self.update_title()

        # if no widget left, emit remove_project signal
        if not self.task_widgets:
            self.remove_project.emit(self)
        else:
            self.check_versions()

    def check_versions(self):
        """Trigger a version check in all the child tasks."""
        for task_widget in self.task_widgets:
            task_widget.check_versions()

    def validate(self):
        """Validate the Tasks.

        Returns:
            bool: True for valid, False otherwise.
        """
        return all([task_widget.validate() for task_widget in self.task_widgets])

    def to_dict(self, dict_in=None):
        """Return a dictionary representing the migration data.

        Returns:
            dict: The migration data.
        """
        dict_out = dict_in if dict_in is not None else {}
        for task_widget in self.task_widgets:
            assert isinstance(task_widget, TaskWidget)
            task_widget.to_dict(dict_in=dict_out)
        return dict_out


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

    @property
    def status(self):
        """Getter for the status attribute.

        Returns:
            bool: The status.
        """
        return self._status

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
        )
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
            "Check references to other tasks\n"
            "in this version and add them to the list..."
        )
        self.check_references_button.clicked.connect(self.pick_references)
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
            take (str):
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
            .filter(Version.variant_name == self.take)
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

    def validate(self):
        """Validate the general status of this take.

        Returns:
            bool: True for valid, False otherwise.
        """
        if not self.enable_take_check_box.isChecked():
            # doesn't matter return this is valid.
            is_valid = True
        else:
            is_valid = self.validate_take_new_name() and self.validate_versions()
        self.migrate_status_icon.set_status(is_valid)
        return is_valid

    def validate_take_new_name(self):
        """Validate take new name.

        Returns:
            bool: True for valid, False otherwise.
        """
        text = self.get_new_variant_name()
        match = variant_name_VALIDATOR_REGEX.match(text)
        if not match or "".join(match.groups()) != text:
            self.take_new_name_line_edit.set_invalid(
                "Take name is not in correct format"
            )
            return False
        else:
            self.take_new_name_line_edit.set_valid()
            return True

    def get_new_variant_name(self):
        """Return the new take name."""
        return self.take_new_name_line_edit.text()

    def versions_combo_box_changed(self, index):
        """Check if newly selected version has inputs.

        Args:
            index (int): Current index
        """
        self.enable_take(self.enable_take_check_box.isChecked())

    def get_current_version(self):
        """Return the currently selected version.

        Returns:
            stalker.Version: Currently selected version in the UI.
        """
        return self.versions_combo_box.currentData()

    def validate_versions(self):
        """Validate referenced versions of the currently selected version.

        Returns:
            bool: True if all referenced versions are valid, False otherwise.
        """
        version = self.get_current_version()
        if version is None:
            return False

        validation_status = True
        if version.inputs:
            # There are references in this version
            self.no_references_message_label.setVisible(False)
            missing_assets = []
            missing_versions = []
            for other_v in version.inputs:
                other_asset = get_related_asset(other_v.task)
                # Filter all the tasks that are already in the EntityStorage
                if not EntityStorage.is_in_storage(other_asset):
                    missing_assets.append(other_asset)
                    missing_versions.append(other_v)
                elif not EntityStorage.is_in_storage(other_v):
                    # The asset is moving but not this version
                    missing_versions.append(other_v)

            tooltip = "\n".join(
                [
                    "{} | {} | v{:03d}".format(
                        get_task_hierarchy_name(v.task), v.variant_name, v.version_number
                    )
                    for v in version.inputs
                ]
            )
            self.migrate_status_icon.setToolTip(tooltip)
            if missing_assets:
                self.check_references_button.setEnabled(True)
                self.check_references_button.setVisible(True)
                self.all_references_are_included_label.setVisible(False)
                self.references_are_not_final_label.setVisible(False)
                validation_status = False

            if missing_versions:
                self.check_references_button.setEnabled(True)
                self.check_references_button.setVisible(True)
                self.all_references_are_included_label.setVisible(False)
                self.references_are_not_final_label.setVisible(True)
                validation_status = False

            if not missing_assets and not missing_versions:
                self.check_references_button.setEnabled(False)
                self.check_references_button.setVisible(False)
                self.all_references_are_included_label.setVisible(True)
                self.references_are_not_final_label.setVisible(False)
                validation_status = True
        else:
            # no references in this version
            self.no_references_message_label.setVisible(True)
            self.check_references_button.setVisible(False)
            self.all_references_are_included_label.setVisible(False)
            validation_status = True
        return validation_status

    def pick_references(self):
        """Pick references of the selected takes.

        Add the referenced tasks to the end of the list.
        """
        version = self.get_current_version()
        referenced_tasks_dialog = ReferencedEntityDialog(parent=self)
        versions = version.inputs

        for version in versions:
            referenced_tasks_dialog.add_entity(version)

        referenced_tasks_dialog.exec()
        # and refresh the TaskTreeView
        try:
            # PySide and PySide2
            accepted = QtWidgets.QDialog.DialogCode.Accepted
        except AttributeError:
            # PyQt4
            accepted = QtWidgets.QDialog.Accepted

        if not referenced_tasks_dialog.result() == accepted:
            return

        # get the selected tasks
        tasks = referenced_tasks_dialog.get_selected_tasks()
        if tasks:
            self.add_references.emit(tasks)

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
        version = self.get_current_version()
        if not state:
            # this take has been disabled, we don't care about the validity of
            # the new take name field
            self.migrate_status_icon.setVisible(False)
            self.take_new_name_line_edit.set_valid()
            self.validate()

            # remove the version from the EntityStorage
            EntityStorage.remove_entity(version)
        else:
            # this take is re-enabled, re-validate the new take name
            self.migrate_status_icon.setVisible(True)
            self.validate()

            # add the version to the EntityStorage
            EntityStorage.add_entity(version)

        # trigger an version check update
        self.version_updated.emit()

    def is_enabled(self):
        """Return True if this take is enabled.

        Returns:
            bool: Return True if this take is enabled.
        """
        return self.enable_take_check_box.isChecked()

    def to_dict(self):
        """Return a dictionary representing the migration data.

        Returns:
            dict: The migration data.
        """
        return {
            "new_name": self.get_new_variant_name(),
            "versions": [self.get_current_version().version_number],
        }

    def remove(self):
        """Remove self."""
        # Remove Version from the EntityStorage
        EntityStorage.remove_entity(self.get_current_version())

        # Remove self widget
        self.deleteLater()

        # Inform others
        self.version_updated.emit()


class TaskWidget(QtWidgets.QGroupBox):
    """A QGroupBox variant to hold stalker.Task related data."""

    add_task = QtCore.Signal(object)
    remove_task = QtCore.Signal(object)
    version_updated = QtCore.Signal()

    def __init__(self, parent=None, task=None):
        super(TaskWidget, self).__init__(parent=parent)
        self._task = None
        self.main_layout = None
        self.no_versions_place_holder = None
        self.remove_button = None
        self.pick_new_parent_button = None
        self.asset_new_name_label = None
        self.asset_new_name_line_edit = None
        self.asset_new_name_validation_message_field = None
        self.asset_new_code_label = None
        self.asset_new_code_line_edit = None
        self.asset_new_code_validation_message_field = None
        self.child_widgets_layout = None
        self.take_widgets = []
        self.task_widgets = []
        self._new_parent = None
        self.new_parent_label = None
        self.setup_ui()
        self.task = task

    def setup_ui(self):
        """Create UI widgets."""
        self.main_layout = QtWidgets.QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)

        # Buttons layout
        buttons_layout = QtWidgets.QHBoxLayout()
        buttons_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.addLayout(buttons_layout)

        # Remove Task
        self.remove_button = QtWidgets.QPushButton(self)
        self.remove_button.setText("Remove Asset")
        self.remove_button.setToolTip("Removes the asset from the list.")
        self.remove_button.clicked.connect(self.remove_wrapper)
        buttons_layout.addWidget(self.remove_button)

        # Pick New Parent
        self.pick_new_parent_button = QtWidgets.QPushButton(self)
        self.pick_new_parent_button.setText("Pick New Parent...")
        self.pick_new_parent_button.setToolTip("Select the new parent...")
        self.pick_new_parent_button.clicked.connect(self.pick_new_parent)
        buttons_layout.addWidget(self.pick_new_parent_button)
        if isinstance(self.parent(), TaskWidget) and self.new_parent:
            self.pick_new_parent_button.setVisible(False)

        # New Parent Label
        self.new_parent_label = QtWidgets.QLabel(self)
        buttons_layout.addWidget(self.new_parent_label)

        # Spacer for buttons
        buttons_layout.addSpacerItem(
            QtWidgets.QSpacerItem(
                20, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed
            )
        )

        # New Asset Name
        asset_new_name_and_code_layout = QtWidgets.QHBoxLayout()
        asset_new_name_and_code_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.addLayout(asset_new_name_and_code_layout)

        validation_hint = (
            "First Letter : A-Z\n"
            "Other Letters: a-z A-Z 0-9\n"
            "No empty spaces!\n"
            "No underscore, no dash etc.\n"
        )

        self.asset_new_name_label = QtWidgets.QLabel(self)
        self.asset_new_name_label.setText("Asset New Name")
        asset_new_name_and_code_layout.addWidget(self.asset_new_name_label)

        asset_new_name_layout = QtWidgets.QVBoxLayout()
        asset_new_name_layout.setContentsMargins(0, 0, 0, 0)
        self.asset_new_name_validation_message_field = QtWidgets.QLabel(self)
        self.asset_new_name_validation_message_field.setStyleSheet("color: red;")
        self.asset_new_name_line_edit = ValidatedLineEdit(
            parent=self, message_field=self.asset_new_name_validation_message_field
        )
        self.asset_new_name_line_edit.setToolTip(
            "New Asset Name\n\n{}".format(validation_hint)
        )
        self.asset_new_name_line_edit.setFixedWidth(150)
        self.asset_new_name_line_edit.editingFinished.connect(
            self.validate_asset_new_name
        )
        asset_new_name_layout.addWidget(self.asset_new_name_line_edit)
        asset_new_name_layout.addWidget(self.asset_new_name_validation_message_field)

        asset_new_name_and_code_layout.addLayout(asset_new_name_layout)

        # New Asset Code
        self.asset_new_code_label = QtWidgets.QLabel(self)
        self.asset_new_code_label.setText("Asset New Code")
        asset_new_name_and_code_layout.addWidget(self.asset_new_code_label)

        asset_new_code_layout = QtWidgets.QVBoxLayout()
        asset_new_code_layout.setContentsMargins(0, 0, 0, 0)
        self.asset_new_code_validation_message_field = QtWidgets.QLabel(self)
        self.asset_new_code_validation_message_field.setStyleSheet("color: red;")
        self.asset_new_code_line_edit = ValidatedLineEdit(
            parent=self, message_field=self.asset_new_code_validation_message_field
        )
        self.asset_new_code_line_edit.setToolTip(
            "New Asset Code\n\n{}".format(validation_hint)
        )
        self.asset_new_code_line_edit.setFixedWidth(150)
        self.asset_new_code_line_edit.editingFinished.connect(
            self.validate_asset_new_code
        )
        asset_new_code_layout.addWidget(self.asset_new_code_line_edit)
        asset_new_code_layout.addWidget(self.asset_new_code_validation_message_field)

        asset_new_name_and_code_layout.addLayout(asset_new_code_layout)

        # Spacer for buttons
        asset_new_name_and_code_layout.addSpacerItem(
            QtWidgets.QSpacerItem(
                20, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed
            )
        )

        self.child_widgets_layout = QtWidgets.QVBoxLayout()
        self.child_widgets_layout.setContentsMargins(12, 0, 12, 0)
        self.no_versions_place_holder = QtWidgets.QLabel(self)
        self.no_versions_place_holder.setText("--- No Versions ---")
        self.no_versions_place_holder.setVisible(False)
        self.child_widgets_layout.addWidget(self.no_versions_place_holder)
        self.main_layout.addLayout(self.child_widgets_layout)

    def remove_wrapper(self):
        """Wrap remove task for UI purposes."""
        result = QtWidgets.QMessageBox.critical(
            self,
            "Remove Task!",
            "Remove this {}?".format(self.task.entity_type),
            QtWidgets.QMessageBox.StandardButton.Yes
            | QtWidgets.QMessageBox.StandardButton.No,
        )
        if result == QtWidgets.QMessageBox.StandardButton.Yes:
            self.remove()
            self.version_updated.emit()

    def remove(self):
        """Remove self from."""
        # Remove all child task widgets
        task_widgets = copy.copy(self.task_widgets)
        for child_task_widget in task_widgets:
            child_task_widget.remove()

        # Remove any take widgets
        take_widgets = copy.copy(self.take_widgets)
        for child_take_widget in take_widgets:
            child_take_widget.remove()

        # Remove self.task from EntityStorage
        EntityStorage.remove_entity(self.task)

        # Delete the widget
        self.deleteLater()

        # Inform parents
        self.remove_task.emit(self)

    def remove_child_task(self, task_widget):
        """Remove the given child task_widget"""
        # Remove from the self
        for i, t_widget in enumerate(self.task_widgets):
            if t_widget == task_widget:
                self.child_widgets_layout.removeWidget(t_widget)
                self.task_widgets.pop(i)
                break

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
            # don't allow a child to be a parent
            if self.task in new_parent.parents:
                QtWidgets.QMessageBox.critical(
                    self,
                    "Invalid Parent!",
                    "Selected parent is one of the child of the Asset!!!",
                )
                return

            # don't allow the same parent
            if new_parent == self.task.parent:
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
        if isinstance(self.parent(), TaskWidget) and self._new_parent:
            self.pick_new_parent_button.setVisible(False)
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

    def validate_asset_new_name(self):
        """Validate asset new name.

        Returns:
            bool: True for valid, False otherwise.
        """
        # Only validate for Assets
        if not isinstance(self.task, Asset):
            self.asset_new_name_line_edit.set_valid()
            return True

        text = self.asset_new_name_line_edit.text()
        match = variant_name_VALIDATOR_REGEX.match(text)
        if not match or "".join(match.groups()) != text:
            self.asset_new_name_line_edit.set_invalid(
                "Asset name is not in correct format"
            )
            return False
        else:
            self.asset_new_name_line_edit.set_valid()
            return True

    def validate_asset_new_code(self):
        """Validate asset new code.

        Returns:
            bool: True for valid, False otherwise.
        """
        # Only validate for Assets
        if not isinstance(self.task, (Asset, Shot, Sequence)):
            self.asset_new_code_line_edit.set_valid()
            return True

        text = self.asset_new_code_line_edit.text()
        match = variant_name_VALIDATOR_REGEX.match(text)
        if not match or "".join(match.groups()) != text:
            self.asset_new_code_line_edit.set_invalid(
                "Asset code is not in correct format"
            )
            return False
        else:
            self.asset_new_code_line_edit.set_valid()
            return True

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
        self.setTitle(get_task_hierarchy_name(task))
        EntityStorage.add_entity(self._task)

        if isinstance(task, (Asset, Shot, Sequence)):
            self.asset_new_name_line_edit.setText(task.name)
            self.asset_new_code_line_edit.setText(task.code)
            # self.validate_asset_new_name()
            # self.validate_asset_new_code()
        else:
            # just hide the new name fields
            self.asset_new_name_label.setVisible(False)
            self.asset_new_name_line_edit.setVisible(False)

            # just hide the new code fields
            self.asset_new_code_validation_message_field.setVisible(False)
            self.asset_new_code_label.setVisible(False)
            self.asset_new_code_line_edit.setVisible(False)
            self.asset_new_code_validation_message_field.setVisible(False)

        # Update Remove Button text
        self.remove_button.setText("Remove {}".format(self._task.entity_type))

        self.setStyleSheet(
            "QGroupBox {{ background-color: {}; color: {}}}".format(
                COLORS[self._task.entity_type.lower()]["bg"],
                COLORS[self._task.entity_type.lower()]["fg"],
            )
        )
        # add all the takes of this task as a TakeWidget
        variant_names = get_unique_variant_names(self._task.id)
        for take in variant_names:
            take_widget = TakeWidget(parent=self, task=self._task, take=take)
            self.child_widgets_layout.addWidget(take_widget)
            take_widget.add_references.connect(self.add_task)
            take_widget.version_updated.connect(self.version_updated)
            self.take_widgets.append(take_widget)
        if variant_names:
            self.no_versions_place_holder.setVisible(False)

        if task.children:
            self.no_versions_place_holder.setVisible(False)

    def add_child_tasks(self, child_tasks):
        """Add the given task as a new widget if it is a child of the current task.

        Args:
            child_tasks (List[stalker.Task]): A stalker.Task instance (or derivative).
        """
        tasks_added = []
        for child_task in child_tasks:
            # starting from the given child_task,
            # traverse up to the parents
            # and add the parent task (which will add the original child task already)
            # as a child widget,
            # otherwise this will go up to the ProjectWidget
            # and will be added to the end of the list as a separate entity
            # this way, we can prevent that
            intermediate_tasks = get_intermediate_tasks(self.task, child_task)
            child_task_widget_tasks = [
                child_task_widget.task for child_task_widget in self.task_widgets
            ]
            for i, task in enumerate(intermediate_tasks):
                if task in self.task.children:
                    if task not in child_task_widget_tasks:
                        # we should add a new widget
                        task_widget = TaskWidget(parent=self, task=task)
                        task_widget.remove_task.connect(self.remove_child_task)
                        task_widget.version_updated.connect(self.version_updated.emit)
                        task_widget.add_task.connect(self.add_task)
                        task_widget.new_parent = self.task
                        self.task_widgets.append(task_widget)
                        self.child_widgets_layout.addWidget(task_widget)
                        tasks_added.append(task)
                        task_added = task

                        # give the rest of the tasks to this widget
                        task_widget.add_child_tasks(intermediate_tasks[i + 1:])
                        break
                    else:
                        # oh okay so this task is already in a task_widget
                        for task_widget in self.task_widgets:
                            if task_widget.task == task:
                                # give the rest of the tasks to that task widget
                                task_widget.add_child_tasks(intermediate_tasks[i + 1:])
                                break

        if tasks_added:
            # some tasks are added
            # trigger version_update
            self.version_updated.emit()

    def check_versions(self):
        """Trigger a version check in all the child takes and task widgets."""
        for take_widget in self.take_widgets:
            take_widget.validate()

        for task_widget in self.task_widgets:
            task_widget.check_versions()

    def is_enabled(self):
        """Return True if all takes are enabled.

        Returns:
            bool: If all take widgets are enabled.
        """
        return any(take_widget.is_enabled() for take_widget in self.take_widgets)

    def validate(self):
        """Validate the current task widget.

        Returns:
            bool: True if all TaskWidgets are valid, False otherwise.
        """
        is_valid = (
            self.new_parent
            and all([take_widget.validate() for take_widget in self.take_widgets])
            and all([task_widget.validate() for task_widget in self.task_widgets])
            and self.validate_asset_new_name()
            and self.validate_asset_new_code()
        )

        if is_valid:
            self.setStyleSheet(
                "QGroupBox {{ background-color: {}; color:{}}}".format(
                    COLORS[self._task.entity_type.lower()]["bg"],
                    COLORS[self._task.entity_type.lower()]["fg"],
                )
            )
        else:
            self.setStyleSheet(
                "QGroupBox {{ background-color: {}; color: {}}}".format(
                    COLORS["invalid"]["bg"],
                    COLORS["invalid"]["fg"],
                )
            )

        return is_valid

    def to_dict(self, dict_in=None):
        """Return a dictionary representing the migration data.

        Returns:
            dict: The migration data.
        """
        dict_out = dict_in if dict_in is not None else dict()
        # New Parent ID
        dict_out[self.task.id] = {}
        if self.new_parent:
            dict_out[self.task.id]["new_parent_id"] = self.new_parent.id

        if isinstance(self.task, (Asset, Shot, Sequence)):
            new_name = self.asset_new_name_line_edit.text()
            if new_name != self.task.name:
                dict_out[self.task.id]["new_name"] = new_name
            new_code = self.asset_new_code_line_edit.text()
            if new_code != self.task.code:
                dict_out[self.task.id]["new_code"] = new_code

        # Takes
        if self.take_widgets and all(
            [take_widget.is_enabled for take_widget in self.take_widgets]
        ):
            dict_out[self.task.id]["takes"] = dict(
                (take_widget.take, take_widget.to_dict())
                for take_widget in self.take_widgets
                if take_widget.is_enabled()
            )

        # child tasks
        for task_widget in self.task_widgets:
            task_widget.to_dict(dict_in=dict_out)
        return dict_out


class AssetMigrationToolDialog(QtWidgets.QDialog):
    """Asset Migration Tool Dialog.

    This is a UI to help migrating tasks (and all the referenced files, including DCC
    scripts, texture and audio files etc.) to a new project.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.main_layout = None
        self.pick_assets_button = None
        self.projects_scroll_area = None
        self.projects_layout = None
        self.project_widgets = []
        self.validate_button = None
        self.migrate_button = None
        self.task_tree_view = None
        self.setup_ui()

    def setup_ui(self):
        """Create UI elements."""
        self.setWindowTitle("Asset Migration Tool")
        self.resize(1280, 1000)
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

        # Legend Labels
        legend_layout = QtWidgets.QHBoxLayout()
        legend_layout.addSpacerItem(
            QtWidgets.QSpacerItem(
                20, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum
            )
        )
        self.main_layout.addLayout(legend_layout)

        for entity in COLORS:
            legend_box = QtWidgets.QLabel(self)
            legend_box.setStyleSheet(
                "background-color: {};".format(COLORS[entity.lower()]["bg"])
            )
            legend_box.setFixedSize(20, 20)
            legend_layout.addWidget(legend_box)

            legend_text = QtWidgets.QLabel(self)
            legend_text.setText(entity.title())
            legend_layout.addWidget(legend_text)

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

        button_layout = QtWidgets.QHBoxLayout()
        self.main_layout.addLayout(button_layout)

        button_layout.addItem(
            QtWidgets.QSpacerItem(
                20, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum
            )
        )

        self.validate_button = QtWidgets.QPushButton(self)
        self.validate_button.setText("Validate")
        self.validate_button.clicked.connect(self.validate_wrapper)
        button_layout.addWidget(self.validate_button)

        self.migrate_button = QtWidgets.QPushButton(self)
        self.migrate_button.setText("Migrate")
        self.migrate_button.clicked.connect(self.migrate)
        button_layout.addWidget(self.migrate_button)

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

    def validate(self):
        """Validates the selected tasks and versions.

        Returns:
            bool: A bool result showing True for valid, False for invalid result.
        """
        return all(
            [project_widget.validate() for project_widget in self.project_widgets]
        )

    def validate_wrapper(self):
        """Wrap validate functionality to display appropriate messages."""
        # validate tasks
        validation_result = self.validate()
        if not validation_result:
            QtWidgets.QMessageBox.critical(
                self,
                "Invalid Assets!",
                "There are invalid tasks (marked with purple).\n\nPlease fix them!",
            )
        else:
            QtWidgets.QMessageBox.information(
                self,
                "All Assets Okay!",
                "All Assets and Tasks are valid 👍",
            )
        return validation_result

    def to_dict(self):
        """Return a dictionary representing the migration data.

        Returns:
            dict: The migration data.
        """
        empty_dict = {}
        for project_widget in self.project_widgets:
            project_widget.to_dict(dict_in=empty_dict)
        return empty_dict

    def migrate(self):
        """Migrate tasks."""
        validation_result = self.validate_wrapper()
        if not validation_result:
            return

        # print the pprint output
        migration_recipe = self.to_dict()
        pprint.pprint(migration_recipe, indent=4)

        # create the AssetMigrationTool
        from anima.dcc.mayaEnv import asset_migration_tool

        amt = asset_migration_tool.AssetMigrationTool()
        amt.migration_recipe = migration_recipe

        try:
            amt.migrate()
        except Exception as e:
            QtWidgets.QMessageBox.critical(
                self,
                "Error",
                "Error during migration:\n\n{}".format(e)
            )
            print(e)
        else:
            QtWidgets.QMessageBox.information(
                self,
                "Success",
                "Successfully migrated assets!\n\nClose the UI now."
            )
            # disable the migrate button
            self.migrate_button.setDisabled(True)


class ReferencedEntityDialog(QtWidgets.QDialog):
    """Show a list of Entities (Tasks, Versions etc.) referenced to another scene."""

    def __init__(self, parent=None, *args, **kwargs):
        super(ReferencedEntityDialog, self).__init__(parent=parent)
        self.main_layout = None
        self.entity_list_view = None
        self.add_selected_tasks_button = None
        self.setup_ui()

    def setup_ui(self):
        self.resize(600, 500)
        self.main_layout = QtWidgets.QVBoxLayout(self)

        # Info Label
        info_label = QtWidgets.QLabel(self)
        info_label.setText(
            "Select Tasks to add\nDisabled items are already in the list!!!"
        )
        self.main_layout.addWidget(info_label)

        # Entity List Widget
        self.entity_list_view = VersionsListView(parent=self)
        self.entity_list_view.setModel(VersionItemModel())
        self.main_layout.addWidget(self.entity_list_view)

        # Add Selected Asset button
        self.add_selected_tasks_button = QtWidgets.QPushButton(self)
        self.add_selected_tasks_button.setText("Add Selected Entities")
        self.add_selected_tasks_button.clicked.connect(self.accept)
        self.main_layout.addWidget(self.add_selected_tasks_button)

    def add_entity(self, version):
        """Add the given version.

        Args:
            version (stalker.Version): A stalker.Version instance.
        """
        version_item_model = self.entity_list_view.model()
        version_item_model.add_version(version)

    def get_selected_tasks(self):
        """Get selected tasks."""
        return self.entity_list_view.get_selected_tasks()


class TasksListView(QtWidgets.QListView):
    """Task specific list view derivative."""

    def __init__(self, parent=None, *args, **kwargs):
        super(TasksListView, self).__init__(parent=parent, *args, *kwargs)
        self.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)

    def get_selected_items(self):
        """Return selected TaskItems.

        Returns:
            list: List of TaskItem instances.
        """
        selection_model = self.selectionModel()
        indexes = selection_model.selectedIndexes()
        task_items = []
        if indexes:
            item_model = self.model()
            for index in indexes:
                current_item = item_model.itemFromIndex(index)
                if current_item and isinstance(current_item, TaskItem):
                    task_items.append(current_item)
        return task_items

    def get_selected_tasks(self):
        """Return selected Tasks.

        Returns:
            list: List of stalker.Asset instances.
        """
        tasks = []
        for task_item in self.get_selected_items():
            tasks.append(task_item.task)
        return tasks


class VersionsListView(QtWidgets.QListView):
    """Version specific list view derivative."""

    def __init__(self, parent=None, *args, **kwargs):
        super(VersionsListView, self).__init__(parent=parent, *args, *kwargs)
        self.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)

    def get_selected_items(self):
        """Return selected VersionItems.

        Returns:
            list: List of VersionItem instances.
        """
        selection_model = self.selectionModel()
        indexes = selection_model.selectedIndexes()
        version_items = []
        if indexes:
            item_model = self.model()
            for index in indexes:
                current_item = item_model.itemFromIndex(index)
                if current_item and isinstance(current_item, VersionItem):
                    version_items.append(current_item)
        return version_items

    def get_selected_tasks(self):
        """Return selected Tasks.

        Returns:
            list: List of stalker.Task instances.
        """
        tasks = []
        for version_item in self.get_selected_items():
            tasks.append(version_item.version.task)
        return tasks

    def get_selected_versions(self):
        """Return selected Versions.

        Returns:
            list: List of stalker.Version instances.
        """
        versions = []
        for version_item in self.get_selected_items():
            versions.append(version_item.version)
        return versions


class TaskItemModel(QtGui.QStandardItemModel):
    """Task item model."""

    def __init__(self):
        super(TaskItemModel, self).__init__()

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

    def add_task(self, task):
        """Add the given task.

        Args:
            task (stalker.Task): A stalker.Task instance.
        """
        # add this task as it is not in the list
        found_item = None
        for i in range(self.rowCount()):
            item = self.item(i, 0)
            if isinstance(item, TaskItem) and item.task == task:
                found_item = item
                break

        if not found_item:
            task_item = TaskItem(task=task)
            # disable this item if this is already in the EntityStorage
            if EntityStorage.is_in_storage(task):
                task_item.setFlags(
                    task_item.flags()
                    & ~QtCore.Qt.ItemIsSelectable
                    & ~QtCore.Qt.ItemIsEnabled
                )
            self.appendRow(task_item)


class VersionItemModel(QtGui.QStandardItemModel):
    """Version item model."""

    def __init__(self):
        super(VersionItemModel, self).__init__()

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

    def add_version(self, version):
        """Add the given version.

        Args:
            version (stalker.Version): A stalker.Version instance.
        """
        # add this version as it is not in the list
        found_item = None
        for i in range(self.rowCount()):
            item = self.item(i, 0)
            if isinstance(item, VersionItem) and item.version == version:
                found_item = item
                break

        if not found_item:
            version_item = VersionItem(version=version)
            # disable this item if this is already in the EntityStorage
            if EntityStorage.is_in_storage(version):
                version_item.setFlags(
                    version_item.flags()
                    & ~QtCore.Qt.ItemIsSelectable
                    & ~QtCore.Qt.ItemIsEnabled
                )
            self.appendRow(version_item)


class TaskItem(QtGui.QStandardItem):
    """Task item."""

    def __init__(self, task=None, *args, **kwargs):
        super(TaskItem, self).__init__(*args, **kwargs)
        self._task = None
        self.task = task

    @property
    def task(self):
        """Return the task.

        Returns:
            stalker.Task: The stalker.Task instance stored in this item.
        """
        return self._task

    @task.setter
    def task(self, task):
        """Set the task attribute.

        Args:
            task (stalker.Task): A stalker Task instance.
        """
        if task is None:
            # This is not an asset related task
            RuntimeError("Not a task given.")
        else:
            self._task = task
            self.setData(
                get_task_hierarchy_name(task), QtCore.Qt.ItemDataRole.DisplayRole
            )


class VersionItem(QtGui.QStandardItem):
    """Version item."""

    def __init__(self, version=None, *args, **kwargs):
        super(VersionItem, self).__init__(*args, **kwargs)
        self._version = None
        self.version = version

    @property
    def version(self):
        """Return the version.

        Returns:
            stalker.Version: The stalker.Version instance stored in this item.
        """
        return self._version

    @version.setter
    def version(self, version):
        """Set the version attribute.

        Args:
            version (stalker.Version): A stalker Version instance.
        """
        if version is None:
            # This is not an asset related version
            RuntimeError("Not a Version is given.")
        else:
            self._version = version
            self.setData(
                "{} --- {}_v{:03d}".format(
                    get_task_hierarchy_name(version.task),
                    version.nice_name,
                    version.version_number,
                ),
                QtCore.Qt.ItemDataRole.DisplayRole,
            )
