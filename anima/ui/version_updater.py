# -*- coding: utf-8 -*-

from anima import logger
from anima.dcc import empty_reference_resolution
from anima.ui.base import AnimaDialogBase, ui_caller
from anima.ui.models.version import VersionTreeModel
from anima.ui.lib import QtCore, QtWidgets


def UI(app_in=None, executor=None, **kwargs):
    """
    :param environment: The
      :class:`~anima.dcc.base.DCCBase` can be None to let the UI to
      work in "environmentless" mode in which it only creates data in database
      and copies the resultant version file path to clipboard.

    :param app_in: A Qt Application instance, which you can pass to let the UI
      be attached to the given applications event process.

    :param executor: Instead of calling app.exec_ the UI will call this given
      function. It also passes the created app instance to this executor.
    """
    return ui_caller(app_in, executor, MainDialog, **kwargs)


class MainDialog(QtWidgets.QDialog, AnimaDialogBase):
    """The main dialog of the version updater system

    The version_tuple list consist of a Version instance and a reference
    object.

    For Maya DCC the reference object is the PyMel Reference node,
    for other environments reference object type will be as native as it can be
    """

    def __init__(self, environment=None, parent=None, reference_resolution=None):
        super(MainDialog, self).__init__(parent)
        self.new_versions = []
        self.versions_tree_view = None
        self.select_none_push_button = None
        self.select_all_push_button = None
        self.update_push_button = None
        self.cancel_push_button = None

        self.setup_ui()

        # center to the window
        self.center_window()

        # setup the environment
        self.environment = self._validate_environment(environment)

        if reference_resolution is None:
            # generate from environment
            if self.environment:
                reference_resolution = self.environment.check_referenced_versions()
            else:
                # create an empty one
                reference_resolution = empty_reference_resolution()
        self.reference_resolution = reference_resolution

        self.fill_ui()

    def setup_ui(self):
        """Create UI elements."""
        # change the window title
        self.setWindowTitle("Version Updater")

        self.setWindowModality(QtCore.Qt.ApplicationModal)
        self.resize(1304, 753)
        main_layout = QtWidgets.QVBoxLayout(self)

        # Description
        description_label = QtWidgets.QLabel(self)
        description_label.setText(
            "<html>"
            "   <head/>"
            "   <body>"
            "       <p>"
            '           <span style=" color:#c00000;">Red Versions need update,</span>'
            '           <span style=" color:#00c000;">Greens are OK</span>, '
            "           check the Versions that you want to trigger an update."
            "       </p>"
            "   </body>"
            "</html>",
        )
        main_layout.addWidget(description_label)

        # Versions Tree View
        self.versions_tree_view = QtWidgets.QTreeView(self)
        # fit column 0 on expand/collapse
        self.versions_tree_view.expanded.connect(
            self.versions_tree_view_auto_fit_column
        )
        self.versions_tree_view.collapsed.connect(
            self.versions_tree_view_auto_fit_column
        )

        # custom context menu for the version_treeView
        self.versions_tree_view.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.versions_tree_view.customContextMenuRequested.connect(
            self.show_versions_tree_view_context_menu
        )
        main_layout.addWidget(self.versions_tree_view)

        # Main Widget
        main_widget = QtWidgets.QWidget(self)
        size_policy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred
        )
        size_policy.setHorizontalStretch(0)
        size_policy.setVerticalStretch(0)
        size_policy.setHeightForWidth(main_widget.sizePolicy().hasHeightForWidth())
        main_widget.setSizePolicy(size_policy)
        layout = QtWidgets.QHBoxLayout(main_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addItem(
            QtWidgets.QSpacerItem(
                40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum
            )
        )

        # Select None
        self.select_none_push_button = QtWidgets.QPushButton(main_widget)
        self.select_none_push_button.setText("Select None")
        self.select_none_push_button.clicked.connect(self.select_no_version)
        layout.addWidget(self.select_none_push_button)

        # Select All
        self.select_all_push_button = QtWidgets.QPushButton(main_widget)
        self.select_all_push_button.setText("Select All")
        self.select_all_push_button.clicked.connect(self.select_all_versions)
        layout.addWidget(self.select_all_push_button)

        # Update
        self.update_push_button = QtWidgets.QPushButton(main_widget)
        self.update_push_button.setText("Update")
        self.update_push_button.clicked.connect(self.update_versions)
        layout.addWidget(self.update_push_button)

        # Cancel
        self.cancel_push_button = QtWidgets.QPushButton(main_widget)
        self.cancel_push_button.setText("Cancel")
        self.cancel_push_button.clicked.connect(self.close)
        layout.addWidget(self.cancel_push_button)
        main_layout.addWidget(main_widget)


    def _validate_environment(self, environment):
        """validates the given DCC value"""
        if environment:
            current_version = environment.get_current_version()
            if not current_version:
                # there is no version so warn the user
                error_message = (
                    "Please save the current scene with Version Creator first!!!"
                )
                QtWidgets.QMessageBox.critical(
                    self, "Error", error_message, QtWidgets.QMessageBox.Ok
                )
                self.close()
                raise RuntimeError(error_message)

        return environment

    def versions_tree_view_auto_fit_column(self):
        """fits columns to content"""
        self.versions_tree_view.resizeColumnToContents(0)
        self.versions_tree_view.resizeColumnToContents(1)
        self.versions_tree_view.resizeColumnToContents(2)
        self.versions_tree_view.resizeColumnToContents(3)
        self.versions_tree_view.resizeColumnToContents(4)
        self.versions_tree_view.resizeColumnToContents(5)
        self.versions_tree_view.resizeColumnToContents(6)

    def fill_versions_tree_view(self):
        """sets up the versions_treeView"""
        logger.debug("start filling versions_treeView")
        logger.debug("creating a new model")

        version_tree_model = VersionTreeModel()
        version_tree_model.reference_resolution = self.reference_resolution

        # populate with all update items
        version_tree_model.populateTree(self.reference_resolution["root"])

        self.versions_tree_view.setModel(version_tree_model)

        logger.debug("setting up signals for versions_treeView_changed")
        # versions_treeView
        # QtCore.QObject.connect(
        #     self.versions_treeView.selectionModel(),
        #     QtCore.SIGNAL('selectionChanged(const QItemSelection &, '
        #                   'const QItemSelection &)'),
        #     self.versions_treeView_changed
        # )

        self.versions_tree_view.is_updating = False
        self.versions_tree_view_auto_fit_column()
        logger.debug("finished filling versions_treeView")

    def fill_ui(self):
        """fills the UI with the asset data"""
        # set the row count
        self.fill_versions_tree_view()

    def select_all_versions(self):
        """selects all the versions in the tableWidget"""
        version_tree_model = self.versions_tree_view.model()
        for i in range(version_tree_model.rowCount()):
            index = version_tree_model.index(i, 0)
            version_item = version_tree_model.itemFromIndex(index)
            version_item.setCheckState(QtCore.Qt.Checked)

    def select_no_version(self):
        """deselects all versions in the tableWidget"""
        version_tree_model = self.versions_tree_view.model()
        for i in range(version_tree_model.rowCount()):
            index = version_tree_model.index(i, 0)
            version_item = version_tree_model.itemFromIndex(index)
            version_item.setCheckState(QtCore.Qt.Unchecked)

    def show_versions_tree_view_context_menu(self, position):
        """the custom context menu for the versions_treeView"""
        # convert the position to global screen position
        global_position = self.versions_tree_view.mapToGlobal(position)

        index = self.versions_tree_view.indexAt(position)
        model = self.versions_tree_view.model()

        # get the column 0 item which holds the Version instance
        # index = self.versions_treeView.model().index(index.row(), 0)
        item = model.itemFromIndex(index)
        logger.debug("itemAt(position) : %s" % item)

        if not item:
            return

        if not hasattr(item, "version"):
            return

        version = item.version
        latest_published_version = None
        if version:
            latest_published_version = version.latest_published_version

        from stalker import Version

        if not isinstance(version, Version):
            return

        # create the menu
        menu = QtWidgets.QMenu()

        # Add "Open..." action
        # Always open the latest published version
        absolute_full_path = version.absolute_full_path
        if absolute_full_path:
            action = menu.addAction("Open...")
            if latest_published_version:
                action.version = latest_published_version
            else:
                action.version = version

        selected_action = menu.exec_(global_position)

        if selected_action:
            choice = selected_action.text()
            if choice == "Open...":
                self.open_version(selected_action.version)

    def open_version(self, version):
        """opens the given version in a new DCC

        :param version: :class:`~stalker.model.version.Version` instance.
        """
        import subprocess
        import platform

        platform_name = platform.system().lower()

        # store the latest published version
        prev_lpv = version.latest_published_version

        process = subprocess.Popen(
            [self.environment.executable[platform_name], version.absolute_full_path],
            stderr=subprocess.PIPE,
        )

        # wait until the process finishes
        process.wait()

        # check the latest published version again
        next_lpv = version.latest_published_version

        if prev_lpv != next_lpv:
            # a new version has been created so tell the environment to update
            # the references to this version
            self.reference_resolution = self.environment.check_referenced_versions()

            # and then refresh the UI
            self.fill_ui()

    def update_versions(self):
        """updates the versions if it is checked in the UI"""
        reference_resolution = self.generate_reference_resolution()

        # send them back to environment
        try:
            self.environment.update_versions(reference_resolution)
        except RuntimeError as e:
            # display as a Error message and return without doing anything
            message_box = QtWidgets.QMessageBox(self)
            message_box.critical(self, "Error", str(e), QtWidgets.QMessageBox.Ok)
            return

        # close the interface
        self.close()

    def generate_reference_resolution(self):
        """Generates a new reference_resolution dictionary from the UI

        :return: dictionary
        """
        generated_reference_resolution = empty_reference_resolution()

        # append anything that is checked

        version_tree_model = self.versions_tree_view.model()
        for i in range(version_tree_model.rowCount()):
            index = version_tree_model.index(i, 0)
            version_item = version_tree_model.itemFromIndex(index)
            if version_item.checkState() == QtCore.Qt.Checked:
                version = version_item.version
                generated_reference_resolution["update"].append(version)

        return generated_reference_resolution

    def show(self):
        """overridden show method"""
        logger.debug("MainDialog.show is started")
        logged_in_user = self.get_logged_in_user()
        if not logged_in_user:
            self.close()
            return_val = None
        else:
            return_val = super(MainDialog, self).show()

        logger.debug("MainDialog.show is finished")
        return return_val
