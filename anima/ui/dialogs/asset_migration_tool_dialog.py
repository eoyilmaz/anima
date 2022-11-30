# -*- coding: utf-8 -*-
from anima.ui.lib import QtCore, QtGui, QtWidgets
from anima.ui.base import ui_caller
from anima.ui.dialogs import task_picker_dialog
from anima.utils import get_task_hierarchy_name, get_unique_take_names

from stalker import Asset, Task, Version


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

    add_assets = QtCore.Signal(object)
    remove_asset = QtCore.Signal(object)

    def __init__(self, parent=None, asset=None):
        super(AssetWidget, self).__init__(parent=parent)
        self._asset = None
        self.main_layout = None
        self.remove_button = None
        self.pick_new_parent_button = None
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
                COLORS["asset"]["bg"],
                COLORS["asset"]["fg"]
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
            task_grp_box = TaskWidget(parent=self, task=child_task)
            task_grp_box.add_assets.connect(self.add_assets)
            self.tasks_layout.addWidget(task_grp_box)

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

    def add_assets(self, assets):
        """Add the given assets as a AssetWidget.

        Args:
            assets ([stalker.Asset]): List of stalker.Asset instances.
        """

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
                asset_widget.add_assets.connect(self.add_assets)

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

    add_references = QtCore.Signal(object)

    def __init__(self, parent=None, task=None, take=None):
        super(TakeWidget, self).__init__(parent=parent)
        self._task = None
        self._take = None
        self.main_layout = None
        self.enable_take_check_box = None
        self.take_new_name_line_edit = None
        self.versions_combo_box = None
        self.check_references_button = None
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
        self.take_new_name_line_edit = QtWidgets.QLineEdit(self)
        self.take_new_name_line_edit.setToolTip("New Take Name")
        self.take_new_name_line_edit.setFixedWidth(150)
        self.take_new_name_line_edit.editingFinished.connect(self.take_new_name_edited)
        self.main_layout.addWidget(self.take_new_name_line_edit)

        # Versions
        self.versions_combo_box = QtWidgets.QComboBox()
        self.versions_combo_box.setFixedWidth(100)
        self.versions_combo_box.currentIndexChanged.connect(self.versions_combo_box_changed)
        self.main_layout.addWidget(self.versions_combo_box)

        # Check References
        self.check_references_button = QtWidgets.QPushButton(self)
        self.check_references_button.setText("Check References...")
        self.check_references_button.setEnabled(False)
        self.check_references_button.setVisible(False)
        self.check_references_button.setToolTip(
            "Check all the selected child takes\n"
            "for references to other assets\n"
            "and add them to the list..."
        )
        self.check_references_button.clicked.connect(self.check_references)
        self.main_layout.addWidget(self.check_references_button)

        self.main_layout.addSpacerItem(
            QtWidgets.QSpacerItem(
                20, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum
            )
        )

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
        for version in versions:
            self.versions_combo_box.addItem(
                "v{:03d}".format(version.version_number),
                version
            )

    def take_new_name_edited(self):
        """Check the text."""
        text = self.take_new_name_line_edit.text()
        if text == "":
            self.take_new_name_line_edit.setText(self.take)

    def versions_combo_box_changed(self, index):
        """Check if newly selected version has inputs.

        Args:
            index (int): Current index
        """
        version = self.versions_combo_box.currentData()
        if not version:
            return
        if version.inputs:
            self.check_references_button.setEnabled(True)
            self.check_references_button.setVisible(True)
        else:
            self.check_references_button.setEnabled(False)
            self.check_references_button.setVisible(False)
            self.check_references_button.setToolTip(
                "No references in the currently selected Version"
            )

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


class TaskWidget(QtWidgets.QGroupBox):
    """A QGroupBox variant to hold stalker.Task related data."""

    add_assets = QtCore.Signal(object)

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
            take_grp_box = TakeWidget(parent=self, task=self._task, take=take)
            self.takes_layout.addWidget(take_grp_box)
            take_grp_box.add_references.connect(self.add_assets)
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

                project_widget.add_assets([asset])
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
        self.main_layout = QtWidgets.QVBoxLayout(self)

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
            default_flags |= QtCore.Qt.ItemIsSelectable
        return default_flags

    def add_asset(self, asset):
        # add this asset as it is not in the list
        found_item = None
        row_count = self.rowCount()
        for i in range(row_count):
            item = self.item(i, 0)
            if isinstance(item, AssetItem) and item.asset == asset:
                found_item = item
                break

        if not found_item:
            asset_item = AssetItem(asset=asset)
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

        self._asset = asset
        self.setData(
            get_task_hierarchy_name(asset),
            QtCore.Qt.ItemDataRole.DisplayRole
        )
