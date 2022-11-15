# -*- coding: utf-8 -*-
from anima.ui.lib import QtCore, QtGui, QtWidgets
from anima.ui.base import ui_caller
from anima.ui.dialogs import task_picker_dialog
from anima.utils import get_task_hierarchy_name, get_unique_take_names

from stalker import Asset, Task, Version


if False:
    from PySide2 import QtCore, QtGui, QtWidgets


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
        self.tasks_layout = None
        self.setup_ui()
        self.asset = asset

    def setup_ui(self):
        """Create UI widgets."""
        self.main_layout = QtWidgets.QVBoxLayout(self)
        self.remove_button = QtWidgets.QPushButton(self)
        self.remove_button.setText("Remove Asset")
        self.remove_button.clicked.connect(self.remove)
        self.main_layout.addWidget(self.remove_button)
        self.tasks_layout = QtWidgets.QVBoxLayout()
        self.main_layout.addLayout(self.tasks_layout)

    def remove(self):
        """Remove self from parent."""
        self.remove_asset.emit(self)

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


class TakesWidget(QtWidgets.QWidget):
    """A QWidget variant to hold stalker.Task related data."""

    def __init__(self, parent=None, task=None, take=None):
        super(TakesWidget, self).__init__(parent=parent)
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
        # add all the takes of this task as a TakesWidget

        take_names = get_unique_take_names(self._task.id)
        for take in take_names:
            take_grp_box = TakesWidget(parent=self, task=self._task, take=take)
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
        self.projects_scroll_area = None
        self.projects_layout = None
        self.pick_assets_button = None
        self.project_widgets = []
        self.task_tree_view = None

        self.setup_ui()

    def setup_ui(self):
        """Create UI elements."""
        self.setWindowTitle("Asset Migration Tool")
        self.resize(1000, 600)
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

        # self.main_layout.addItem(
        #     QtWidgets.QSpacerItem(
        #         20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding
        #     )
        # )

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

        assets_added = []
        if dialog.result() == accepted:
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
                    self.projects_layout.addWidget(project_widget)
                    project_widget.project = asset.project

                project_widget.add_asset(asset)
                assets_added.append(asset)
                # connect the signal
                project_widget.remove_project.connect(self.remove_project)

        if not assets_added:
            QtWidgets.QMessageBox()
            QtWidgets.QMessageBox.critical(
                self,
                "No Assets Selected",
                "No Assets selected, please try again!",
            )
            self.pick_assets_button_clicked()

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
