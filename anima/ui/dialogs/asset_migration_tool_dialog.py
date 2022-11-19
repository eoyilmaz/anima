# -*- coding: utf-8 -*-
from anima.ui.lib import QtCore, QtGui, QtWidgets
from anima.ui.base import ui_caller
from anima.ui.dialogs import task_picker_dialog
from anima.ui.views.task import TaskTreeView
from anima.utils import get_task_hierarchy_name, get_unique_take_names

from stalker import Asset, Task, Version


if False:
    from PySide2 import QtCore, QtGui, QtWidgets


COLORS = {"project": "#ffe5bf", "asset": "#c3e6a1", "task": "#acd2e5"}


def UI(app_in=None, executor=None, **kwargs):
    """
    :param app_in: A Qt Application instance, which you can pass to let the UI
      be attached to the given applications event process.

    :param executor: Instead of calling app.exec_ the UI will call this given
      function. It also passes the created app instance to this executor.

    """
    return ui_caller(app_in, executor, AssetMigrationToolDialog, **kwargs)


class AssetWidget(QtWidgets.QGroupBox):
    """A QGroupBox variant to hold stalker.Asset related data."""

    remove_asset = QtCore.Signal(object)

    def __init__(self, parent=None, asset=None):
        super(AssetWidget, self).__init__(parent=parent)
        self._asset = None
        self.main_layout = None
        self.remove_button = None
        self.pick_new_parent_button = None
        self.check_references_button = None
        self.tasks_layout = None
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

        # Check References
        self.check_references_button = QtWidgets.QPushButton(self)
        self.check_references_button.setText("Check References...")
        self.check_references_button.setToolTip(
            "Check all the selected child takes\n"
            "for references to other assets\n"
            "and add them to the list..."
        )
        self.check_references_button.clicked.connect(self.check_references)
        buttons_layout.addWidget(self.check_references_button)

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
            "QGroupBox {{ background-color: {}; }}".format(COLORS["asset"])
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

    def update_new_parent_label(self):
        """Update the new parent label."""
        new_parent_hierarchy_name = "-- No New Parent Selected --"
        if self.new_parent:
            new_parent_hierarchy_name = get_task_hierarchy_name(self.new_parent)
        self.new_parent_label.setText(
            "New Parent: {}".format(new_parent_hierarchy_name)
        )

    def check_references(self):
        """Check references of the selected takes.

        Add the referenced assets to the end of the list.
        """
        QtWidgets.QMessageBox.critical(
            self,
            "Not Implemented Yet!",
            "This part is not implemented yet!",
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
            task_grp_box = TaskWidget(parent=self, task=child_task)
            self.tasks_layout.addWidget(task_grp_box)


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
            "QGroupBox {{ background-color: {}; }}".format(COLORS["project"])
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

    def add_asset(self, asset):
        """Add the given asset as a AssetWidget.

        Args:
            asset (stalker.Asset): A stalker.Asset instance.
        """
        if not isinstance(asset, Asset):
            # skip non asset entities
            return

        if asset not in [asset_widget.asset for asset_widget in self.asset_widgets]:
            asset_widget = AssetWidget(parent=self)
            self.asset_widgets.append(asset_widget)
            self.assets_layout.addWidget(asset_widget)
            asset_widget.asset = asset
            # connect signals
            asset_widget.remove_asset.connect(self.remove_asset)
            self.update_title()

    def remove_asset(self, asset_widget):
        """Remove the given asset."""
        for i, a_widget in enumerate(self.asset_widgets):
            if a_widget == asset_widget:
                self.assets_layout.removeWidget(a_widget)
                self.asset_widgets.pop(i)
                a_widget.deleteLater()
                break

        # Update Title
        self.update_title()

        # if no widget left, emit remove_project signal
        if not self.asset_widgets:
            self.remove_project.emit(self)


class TakeWidget(QtWidgets.QWidget):
    """A QWidget variant to hold stalker.Task related data."""

    def __init__(self, parent=None, task=None, take=None):
        super(TakeWidget, self).__init__(parent=parent)
        self._task = None
        self._take = None
        self.main_layout = None
        self.enable_take_check_box = None
        self.take_new_name_line_edit = None
        self.versions_combo_box = None
        self.setup_ui()
        self.task = task
        self.take = take

    def setup_ui(self):
        """Create UI widgets."""
        self.main_layout = QtWidgets.QHBoxLayout(self)
        self.main_layout.setMargin(0)

        # Enable This take Checkbox
        self.enable_take_check_box = QtWidgets.QCheckBox(self)
        self.enable_take_check_box.setChecked(True)
        self.enable_take_check_box.setText("--Take Name--")
        self.enable_take_check_box.setMinimumWidth(100)
        self.main_layout.addWidget(self.enable_take_check_box)

        # New Take Name
        self.take_new_name_line_edit = QtWidgets.QLineEdit(self)
        self.take_new_name_line_edit.setToolTip("New Take Name")
        self.take_new_name_line_edit.editingFinished.connect(self.take_new_name_edited)
        self.main_layout.addWidget(self.take_new_name_line_edit)

        # Versions
        self.versions_combo_box = QtWidgets.QComboBox()
        self.main_layout.addWidget(self.versions_combo_box)

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

        # Update Versions list
        versions = (
            Version.query.filter(Version.task == self.task)
            .filter(Version.take_name == self.take)
            .order_by(Version.version_number.desc())
            .all()
        )
        self.versions_combo_box.clear()
        self.versions_combo_box.addItems(
            ["v{:03d}".format(version.version_number) for version in versions]
        )

    def take_new_name_edited(self):
        """Check the text."""
        text = self.take_new_name_line_edit.text()
        if text == "":
            self.take_new_name_line_edit.setText(self.take)


class TaskWidget(QtWidgets.QGroupBox):
    """A QGroupBox variant to hold stalker.Task related data."""

    def __init__(self, parent=None, task=None):
        super(TaskWidget, self).__init__(parent=parent)
        self._task = None
        self.main_layout = None
        self.no_versions_place_holder = None
        self.takes_layout = None
        self.setup_ui()
        self.task = task

    def setup_ui(self):
        """Create UI widgets."""
        self.main_layout = QtWidgets.QVBoxLayout(self)
        self.takes_layout = QtWidgets.QVBoxLayout()
        self.no_versions_place_holder = QtWidgets.QLabel(self)
        self.no_versions_place_holder.setText("--- No Versions ---")
        self.no_versions_place_holder.setDisabled(True)
        self.takes_layout.addWidget(self.no_versions_place_holder)
        self.main_layout.addLayout(self.takes_layout)
        self.setStyleSheet(
            "QGroupBox {{ background-color: {}; }}".format(COLORS["task"])
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
            take_grp_box = TakeWidget(parent=self, task=self._task, take=take)
            self.takes_layout.addWidget(take_grp_box)
        if take_names:
            self.no_versions_place_holder.setVisible(False)


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
        self.resize(600, 1000)
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
        self.pick_assets_button.clicked.connect(self.pick_assets_button_clicked)
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
        self.main_layout.addWidget(self.migrate_button)

        self.projects_layout.addItem(
            QtWidgets.QSpacerItem(
                20, 20, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding
            )
        )

    def pick_assets_button_clicked(self):
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

                project_widget.add_asset(asset)
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
