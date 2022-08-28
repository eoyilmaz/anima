# -*- coding: utf-8 -*-
import anima.utils
from anima import logger
from anima.ui.lib import QtCore, QtGui, QtWidgets
from anima.ui.models.task import TaskTreeModel


class DuplicateTaskHierarchyDialog(QtWidgets.QDialog):
    """custom dialog for duplicating task hierarchies"""

    def __init__(self, parent=None, duplicated_task_name="", *args, **kwargs):
        super(DuplicateTaskHierarchyDialog, self).__init__(
            parent=parent, *args, **kwargs
        )

        self.duplicated_task_name = duplicated_task_name

        # storage for widgets
        self.main_layout = None
        self.rename_new_task_checkbox = None
        self.label = None
        self.task_name_line_edit = None
        self.keep_resources_check_box = None
        self.number_of_copies_spin_box = None
        self.button_box = None

        # setup dialog
        self._setup_dialog()

    def _setup_dialog(self):
        """create the UI elements"""
        # set window title
        self.setWindowTitle("Duplicate Task Hierarchy")

        # set window size
        self.resize(420, 118)

        # create the main layout
        self.main_layout = QtWidgets.QVBoxLayout(self)
        self.setLayout(self.main_layout)

        # form layout
        form_layout = QtWidgets.QFormLayout()
        self.main_layout.addLayout(form_layout)

        label_role = QtWidgets.QFormLayout.LabelRole
        field_role = QtWidgets.QFormLayout.FieldRole

        i = 0
        # =======================
        # Rename Tasks
        i += 1
        form_layout.setWidget(i, label_role, QtWidgets.QLabel("Rename Tasks", self))

        self.rename_new_task_checkbox = QtWidgets.QCheckBox(self)
        self.rename_new_task_checkbox.setChecked(False)
        form_layout.setWidget(i, field_role, self.rename_new_task_checkbox)

        # ====================
        # Duplicated Task Name
        i += 1
        form_layout.setWidget(i, label_role, QtWidgets.QLabel("Duplicated Task Name", self))

        # the line edit
        self.task_name_line_edit = QtWidgets.QLineEdit(self)
        self.task_name_line_edit.setText(self.duplicated_task_name)
        self.task_name_line_edit.setEnabled(False)
        form_layout.setWidget(i, field_role, self.task_name_line_edit)

        # ===================
        # Number Of Copies
        i += 1
        form_layout.setWidget(i, label_role, QtWidgets.QLabel("Number Of Copies", self))

        self.number_of_copies_spin_box = QtWidgets.QSpinBox(self)
        self.number_of_copies_spin_box.setMinimum(1)
        self.number_of_copies_spin_box.setMaximum(1000)
        form_layout.setWidget(i, field_role, self.number_of_copies_spin_box)

        # ==============
        # Keep Resources
        i += 1
        form_layout.setWidget(i, label_role, QtWidgets.QLabel("Keep Resources", self))

        self.keep_resources_check_box = QtWidgets.QCheckBox(self)
        self.keep_resources_check_box.setChecked(True)
        form_layout.setWidget(i, field_role, self.keep_resources_check_box)

        # ===================
        # the button box
        self.button_box = QtWidgets.QDialogButtonBox(self)
        self.button_box.setOrientation(QtCore.Qt.Horizontal)
        self.button_box.setStandardButtons(
            QtWidgets.QDialogButtonBox.Cancel | QtWidgets.QDialogButtonBox.Ok
        )
        self.main_layout.addWidget(self.button_box)

        # setup signals
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        self.rename_new_task_checkbox.stateChanged.connect(
            self.rename_new_task_checkbox_state_changed
        )

    def rename_new_task_checkbox_state_changed(self, state):
        """Update the line edit

        :param state:
        :return:
        """
        self.task_name_line_edit.setEnabled(state)


class TaskTreeView(QtWidgets.QTreeView):
    """A custom tree view to display Tasks info"""

    def __init__(self, *args, **kwargs):
        # filter non Qt kwargs
        allow_multi_selection = False
        try:
            allow_multi_selection = kwargs.pop("allow_multi_selection")
        except KeyError:
            pass

        allow_drag = False
        try:
            allow_drag = kwargs.pop("allow_drag")
        except KeyError:
            pass

        self.project = kwargs.pop("project", None)
        self.show_completed_projects = False

        super(TaskTreeView, self).__init__(*args, **kwargs)

        self.is_updating = False

        # self.setAlternatingRowColors(True)
        self.setUniformRowHeights(True)
        self.header().setCascadingSectionResizes(True)

        # allow multiple selection
        if allow_multi_selection:
            self.setSelectionMode(self.ExtendedSelection)

        if allow_drag:
            self.setSelectionMode(self.ExtendedSelection)
            self.setDragDropMode(QtWidgets.QAbstractItemView.InternalMove)
            self.setDragEnabled(True)
            self.setAcceptDrops(True)
            self.setDropIndicatorShown(True)

        # delegate = TaskItemDelegate(self)
        # self.setItemDelegate(delegate)
        self.setup_signals()

    def setup_signals(self):
        """connects the signals to slots"""
        # fit column 0 on expand/collapse
        self.expanded.connect(self.expand_all_selected)
        self.collapsed.connect(self.collapse_all_selected)

        # custom context menu for the tasks_treeView
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)
        self.doubleClicked.connect(self.double_clicked_on_entity)

    def replace_with_other(self, layout, index, tree_view=None):
        """Replaces the given tree_view with itself

        :param layout: The QtGui.QLayout of the parent of the original
          QTreeView
        :param index: The item index.
        :param tree_view: The QtWidgets.QTreeView to replace with
        :return:
        """
        if tree_view:
            tree_view.deleteLater()
        layout.insertWidget(index, self)
        return self

    def auto_fit_column(self):
        """fits columns to content"""
        self.resizeColumnToContents(0)

    def fill(self):
        """fills the tree view with data"""
        logger.debug("start filling tasks_treeView")
        logger.debug("creating a new model")
        if not self.project:
            from sqlalchemy import alias
            from stalker import Task, Project
            from stalker.db.session import DBSession

            # projects = Project.query.order_by(Project.name).all()
            inner_tasks = alias(Task.__table__)
            subquery = DBSession.query(inner_tasks.c.id).filter(
                inner_tasks.c.project_id == Project.id
            )
            query = DBSession.query(
                Project.id,
                Project.name,
                Project.entity_type,
                Project.status_id,
                subquery.exists().label("has_children"),
            )
            if not self.show_completed_projects:
                from stalker import Status

                status_cmpl = Status.query.filter(Status.code == "CMPL").first()
                query = query.filter(Project.status != status_cmpl)

            query = query.order_by(Project.name)
            projects = query.all()
        else:
            self.project.has_children = bool(self.project.tasks)
            projects = [self.project]

        logger.debug("projects: %s" % projects)

        # delete the old model if any
        if self.model() is not None:
            self.model().deleteLater()

        task_tree_model = TaskTreeModel()
        task_tree_model.populateTree(projects)
        self.setModel(task_tree_model)
        self.is_updating = False

        self.auto_fit_column()

        logger.debug("finished filling tasks_treeView")

    def show_context_menu(self, position):
        """the custom context menu"""
        # convert the position to global screen position
        global_position = self.mapToGlobal(position)

        index = self.indexAt(position)
        model = self.model()
        item = model.itemFromIndex(index)
        logger.debug("itemAt(position) : %s" % item)
        task_id = None
        entity = None

        # if not item:
        #     return

        # if item and not hasattr(item, 'task'):
        #     return

        # from anima.ui.models.task import TaskItem
        # if not isinstance(item, TaskItem):
        #     return

        if item:
            try:
                if item.task:
                    task_id = item.task.id
            except AttributeError:
                return

        # if not task_id:
        #     return

        from anima import utils

        file_browser_name = utils.file_browser_name()

        # create the menu
        menu = QtWidgets.QMenu()  # Open in browser

        # -----------------------------------
        # actions created in different scopes
        create_time_log_action = None
        create_project_action = None
        update_task_action = None
        upload_thumbnail_action = None
        create_child_task_action = None
        duplicate_task_hierarchy_action = None
        delete_task_action = None
        export_to_json_action = None
        import_from_json_action = None
        no_deps_action = None
        create_project_structure_action = None
        update_project_action = None
        assign_users_action = None
        open_in_web_browser_action = None
        open_in_file_browser_action = None
        copy_url_action = None
        copy_id_to_clipboard = None
        fix_task_status_action = None
        change_status_menu_actions = []

        from anima import defaults
        from stalker import LocalSession

        local_session = LocalSession()
        logged_in_user = local_session.logged_in_user

        from stalker import SimpleEntity, Task, Project

        # TODO: Update this to use only task_id
        if task_id:
            entity = SimpleEntity.query.get(task_id)

        reload_action = menu.addAction("\uf0e8 Reload")

        # sub menus
        create_sub_menu = menu.addMenu("Create")
        update_sub_menu = menu.addMenu("Update")

        if defaults.is_power_user(logged_in_user):
            # create the Create Project menu item
            create_project_action = create_sub_menu.addAction(
                "\uf0e8 Create Project..."
            )

            if isinstance(entity, Project):
                # this is a project!
                if defaults.is_power_user(logged_in_user):
                    update_project_action = update_sub_menu.addAction(
                        "\uf044 Update Project..."
                    )
                    assign_users_action = menu.addAction("\uf0c0 Assign Users...")
                    create_project_structure_action = create_sub_menu.addAction(
                        "\uf115 Create Project Structure"
                    )
                    create_child_task_action = create_sub_menu.addAction(
                        "\uf0ae Create Child Task..."
                    )
                    # Export and Import JSON
                    create_sub_menu.addSeparator()
                    # export_to_json_action = create_sub_menu.addAction(u'\uf1f8 Export To JSON...')

                    import_from_json_action = create_sub_menu.addAction(
                        "\uf1f8 Import From JSON..."
                    )

        if entity:
            # separate the Project and Task related menu items
            menu.addSeparator()

            open_in_web_browser_action = menu.addAction("\uf14c Open In Web Browser...")
            open_in_file_browser_action = menu.addAction("\uf07c Browse Folders...")
            copy_url_action = menu.addAction("\uf0c5 Copy URL")
            copy_id_to_clipboard = menu.addAction("\uf0c5 Copy ID to clipboard")

            if isinstance(entity, Task):
                # this is a task
                create_project_structure_action = create_sub_menu.addAction(
                    "\uf115 Create Task Folder Structure"
                )

                task = entity
                from stalker import Status

                status_wfd = Status.query.filter(Status.code == "WFD").first()
                status_prev = Status.query.filter(Status.code == "PREV").first()
                status_cmpl = Status.query.filter(Status.code == "CMPL").first()
                if logged_in_user in task.resources and task.status not in [
                    status_wfd,
                    status_prev,
                    status_cmpl,
                ]:
                    create_sub_menu.addSeparator()
                    create_time_log_action = create_sub_menu.addAction(
                        "\uf073 Create TimeLog..."
                    )

                # Add Depends To menu
                menu.addSeparator()
                depends = task.depends
                if depends:
                    depends_to_menu = menu.addMenu("\uf090 Depends To")

                    for dTask in depends:
                        action = depends_to_menu.addAction(dTask.name)
                        action.task = dTask

                # Add Dependent Of Menu
                dependent_of = task.dependent_of
                if dependent_of:
                    dependent_of_menu = menu.addMenu("\uf08b Dependent Of")

                    for dTask in dependent_of:
                        action = dependent_of_menu.addAction(dTask.name)
                        action.task = dTask

                if not depends and not dependent_of:
                    no_deps_action = menu.addAction("\uf00d No Dependencies")
                    no_deps_action.setEnabled(False)

                # update task and create child task menu items
                menu.addSeparator()
                if defaults.is_power_user(logged_in_user):
                    create_sub_menu.addSeparator()
                    update_task_action = update_sub_menu.addAction(
                        "\uf044 Update Task..."
                    )

                    upload_thumbnail_action = update_sub_menu.addAction(
                        "\uf03e Upload Thumbnail..."
                    )

                    # Export and Import JSON
                    create_sub_menu.addSeparator()
                    export_to_json_action = create_sub_menu.addAction(
                        "\uf1f8 Export To JSON..."
                    )

                    import_from_json_action = create_sub_menu.addAction(
                        "\uf1f8 Import From JSON..."
                    )
                    create_sub_menu.addSeparator()

                    create_child_task_action = create_sub_menu.addAction(
                        "\uf0ae Create Child Task..."
                    )

                    duplicate_task_hierarchy_action = create_sub_menu.addAction(
                        "\uf0c5 Duplicate Task Hierarchy..."
                    )
                    delete_task_action = menu.addAction("\uf1f8 Delete Task...")

                    menu.addSeparator()

                # create the status_menu
                status_menu = update_sub_menu.addMenu("Status")

                fix_task_status_action = status_menu.addAction("\uf0e8 Fix Task Status")

                assert isinstance(status_menu, QtWidgets.QMenu)
                status_menu.addSeparator()

                # get all task statuses
                from anima import defaults

                menu_style_sheet = ""
                defaults_status_colors = defaults.status_colors

                change_status_menu_actions_enabled = False
                if defaults.is_power_user(logged_in_user):
                    change_status_menu_actions_enabled = True

                for status_code in defaults.status_colors:
                    change_status_menu_action = status_menu.addAction(status_code)
                    change_status_menu_action.setEnabled(
                        change_status_menu_actions_enabled
                    )

                    change_status_menu_action.setObjectName("status_%s" % status_code)

                    change_status_menu_actions.append(change_status_menu_action)

                    menu_style_sheet = "%s %s" % (
                        menu_style_sheet,
                        "QMenu#status_%s { background: %s %s %s}"
                        % (
                            status_code,
                            defaults_status_colors[status_code][0],
                            defaults_status_colors[status_code][1],
                            defaults_status_colors[status_code][2],
                        ),
                    )

                # change the BG Color of the status
                status_menu.setStyleSheet(menu_style_sheet)

        try:
            # PySide and PySide2
            accepted = QtWidgets.QDialog.DialogCode.Accepted
        except AttributeError:
            # PyQt4
            accepted = QtWidgets.QDialog.Accepted

        selected_action = menu.exec_(global_position)
        if selected_action:
            if selected_action is reload_action:
                if isinstance(entity, Project):
                    self.fill()
                    self.find_and_select_entity_item(item.task)
                else:
                    for item in self.get_selected_task_items():
                        item.reload()

            if create_project_action and selected_action is create_project_action:
                from anima.ui import project_dialog

                project_main_dialog = project_dialog.MainDialog(
                    parent=self, project=None
                )
                project_main_dialog.exec_()
                result = project_main_dialog.result()

                # refresh the task list
                if result == accepted:
                    self.fill()

                project_main_dialog.deleteLater()

            if entity:
                from anima import defaults

                url = "http://%s/%ss/%s/view" % (
                    defaults.stalker_server_internal_address,
                    entity.entity_type.lower(),
                    entity.id,
                )

                if selected_action is open_in_web_browser_action:
                    import webbrowser

                    webbrowser.open(url)
                elif selected_action is open_in_file_browser_action:
                    from anima import utils

                    try:
                        utils.open_browser_in_location(entity.absolute_path)
                    except IOError as e:
                        QtWidgets.QMessageBox.critical(
                            self, "Error", "%s" % e, QtWidgets.QMessageBox.Ok
                        )
                elif selected_action is copy_url_action:
                    clipboard = QtWidgets.QApplication.clipboard()
                    clipboard.setText(url)

                    # and warn the user about a new version is created and the
                    # clipboard is set to the new version full path
                    QtWidgets.QMessageBox.warning(
                        self,
                        "URL Copied To Clipboard",
                        "URL:<br><br>%s<br><br>is copied to clipboard!" % url,
                        QtWidgets.QMessageBox.Ok,
                    )
                elif selected_action is copy_id_to_clipboard:

                    clipboard = QtWidgets.QApplication.clipboard()
                    selected_entity_ids = ", ".join(
                        list(map(str, self.get_selected_task_ids()))
                    )
                    clipboard.setText(selected_entity_ids)

                    # and warn the user about a new version is created and the
                    # clipboard is set to the new version full path
                    QtWidgets.QMessageBox.warning(
                        self,
                        "ID Copied To Clipboard",
                        "IDs are copied to clipboard!<br>%s" % selected_entity_ids,
                        QtWidgets.QMessageBox.Ok,
                    )

                elif selected_action is create_time_log_action:
                    from anima.ui import time_log_dialog

                    time_log_dialog_main_dialog = time_log_dialog.MainDialog(
                        parent=self,
                        task=entity,
                    )
                    time_log_dialog_main_dialog.exec_()
                    result = time_log_dialog_main_dialog.result()
                    time_log_dialog_main_dialog.deleteLater()

                    if result == accepted:
                        # refresh the task list
                        if item.parent:
                            item.parent.reload()
                        else:
                            self.fill()

                        # reselect the same task
                        self.find_and_select_entity_item(entity)

                elif selected_action is update_task_action:
                    from anima.ui import task_dialog

                    task_main_dialog = task_dialog.MainDialog(
                        parent=self, tasks=self.get_selected_tasks()
                    )
                    task_main_dialog.exec_()
                    result = task_main_dialog.result()
                    task_main_dialog.deleteLater()

                    # refresh the task list
                    if result == accepted:
                        # just reload the same item
                        if item.parent:
                            item.parent.reload()
                        else:
                            # reload the entire
                            self.fill()
                        self.find_and_select_entity_item(entity)

                elif selected_action is upload_thumbnail_action:
                    from anima.ui import utils as ui_utils

                    thumbnail_full_path = ui_utils.choose_thumbnail(
                        self,
                        start_path=entity.absolute_path,
                        dialog_title="Choose Thumbnail For: %s" % entity.name,
                    )

                    # if the thumbnail_full_path is empty do not do anything
                    if thumbnail_full_path == "":
                        return

                    # get the current task
                    anima.utils.upload_thumbnail(entity, thumbnail_full_path)

                elif selected_action is create_child_task_action:
                    from anima.ui import task_dialog

                    task_main_dialog = task_dialog.MainDialog(
                        parent=self, parent_task=entity
                    )
                    task_main_dialog.exec_()
                    result = task_main_dialog.result()
                    tasks = task_main_dialog.tasks
                    task_main_dialog.deleteLater()

                    if result == accepted and tasks:
                        # reload the parent item
                        if item.parent:
                            item.parent.reload()
                        else:
                            self.fill()
                        self.find_and_select_entity_item(tasks[0])

                elif selected_action is duplicate_task_hierarchy_action:
                    dth_dialog = DuplicateTaskHierarchyDialog(
                        parent=self, duplicated_task_name=item.task.name
                    )
                    dth_dialog.exec_()

                    result = dth_dialog.result()
                    if result == accepted:
                        new_task_name = dth_dialog.task_name_line_edit.text()
                        rename_new_tasks = (
                            dth_dialog.rename_new_task_checkbox.isChecked()
                        )
                        keep_resources = (
                            dth_dialog.keep_resources_check_box.checkState()
                        )
                        number_of_copies = dth_dialog.number_of_copies_spin_box.value()

                        from anima import utils
                        from stalker import Task

                        new_tasks = []
                        parents_to_reload = set()
                        for item in self.get_selected_task_items():
                            task = Task.query.get(item.task.id)
                            new_tasks += utils.duplicate_task_hierarchy(
                                task,
                                None,
                                new_task_name if rename_new_tasks else None,
                                description="Duplicated from Task(%s)" % task.id,
                                user=logged_in_user,
                                keep_resources=keep_resources,
                                number_of_copies=number_of_copies
                            )

                            parents_to_reload.add(item.parent)

                        # reload all the parents
                        for parent in parents_to_reload:
                            parent.reload()

                        # now select new tasks
                        self.find_and_select_entity_item(new_tasks)

                elif selected_action is delete_task_action:
                    answer = QtWidgets.QMessageBox.question(
                        self,
                        "Delete Task?",
                        "Delete the task and children?<br><br>(NO UNDO!!!!)",
                        QtWidgets.QMessageBox.Yes,
                        QtWidgets.QMessageBox.No,
                    )
                    if answer == QtWidgets.QMessageBox.Yes:
                        from stalker.db.session import DBSession
                        from stalker import Task

                        tasks = self.get_selected_tasks()
                        logger.debug("tasks   : %s" % tasks)

                        task = Task.query.get(item.task.id)

                        # get the next sibling or the previous
                        # to select after deletion
                        select_task = item.parent.task
                        if task.parent:
                            all_siblings = list(
                                Task.query.filter(Task.parent == task.parent)
                                .order_by(Task.name)
                                .all()
                            )
                            if len(all_siblings) > 1:
                                sibling_index = all_siblings.index(task)
                                if sibling_index < len(all_siblings) - 1:
                                    # this is not the last task in the list
                                    # select next one
                                    select_task = all_siblings[sibling_index + 1]
                                elif sibling_index == len(all_siblings) - 1:
                                    # this is the last task
                                    # select previous task
                                    select_task = all_siblings[sibling_index - 1]

                        for task in tasks:
                            DBSession.delete(task)
                        DBSession.commit()
                        # reload the parent
                        unique_parent_items = []
                        for item in self.get_selected_task_items():
                            if item.parent and item.parent not in unique_parent_items:
                                unique_parent_items.append(item.parent)

                        if unique_parent_items:
                            for parent_item in unique_parent_items:
                                parent_item.reload()
                        else:
                            self.fill()
                        # either select the next or previous task or the parent
                        self.find_and_select_entity_item(select_task)

                elif selected_action is export_to_json_action:
                    # show a file browser
                    dialog = QtWidgets.QFileDialog(self, "Choose file")
                    dialog.setNameFilter("JSON Files (*.json)")
                    dialog.setFileMode(QtWidgets.QFileDialog.AnyFile)
                    if dialog.exec_():
                        file_path = dialog.selectedFiles()[0]
                        if file_path:
                            import os
                            import json
                            from anima.utils import task_hierarchy_io

                            # check file extension
                            parts = os.path.splitext(file_path)

                            if not parts[1]:
                                file_path = "%s%s" % (parts[0], ".json")

                            data = json.dumps(
                                entity,
                                cls=task_hierarchy_io.StalkerEntityEncoder,
                                check_circular=False,
                                indent=4,
                            )
                            try:
                                with open(file_path, "w") as f:
                                    f.write(data)
                            except Exception as e:
                                pass
                            finally:
                                QtWidgets.QMessageBox.information(
                                    self,
                                    "Task data Export to JSON!",
                                    "Task data Export to JSON!",
                                )

                elif selected_action is import_from_json_action:
                    # show a file browser
                    dialog = QtWidgets.QFileDialog(self, "Choose file")
                    dialog.setNameFilter("JSON Files (*.json)")
                    dialog.setFileMode(QtWidgets.QFileDialog.ExistingFile)
                    if dialog.exec_():
                        file_path = dialog.selectedFiles()[0]
                        if file_path:
                            import json

                            with open(file_path) as f:
                                data = json.load(f)
                            from anima.utils import task_hierarchy_io

                            if isinstance(entity, Task):
                                project = entity.project
                            elif isinstance(entity, Project):
                                project = entity

                            parent = None
                            if isinstance(entity, Task):
                                parent = entity

                            decoder = task_hierarchy_io.StalkerEntityDecoder(
                                project=project
                            )
                            loaded_entity = decoder.loads(data, parent=parent)

                            try:
                                from stalker.db.session import DBSession

                                DBSession.add(loaded_entity)
                                DBSession.commit()
                            except Exception as e:
                                QtWidgets.QMessageBox.critical(
                                    self, "Error!", "%s" % e, QtWidgets.QMessageBox.Ok
                                )
                            else:
                                item.reload()
                                QtWidgets.QMessageBox.information(
                                    self,
                                    "New Tasks are created!",
                                    "New Tasks are created",
                                )

                elif selected_action is create_project_structure_action:
                    answer = QtWidgets.QMessageBox.question(
                        self,
                        "Create Project Folder Structure?",
                        "This will create project folders, OK?",
                        QtWidgets.QMessageBox.Yes,
                        QtWidgets.QMessageBox.No,
                    )
                    if answer == QtWidgets.QMessageBox.Yes:
                        from anima import utils

                        try:
                            for task in self.get_selected_tasks():
                                utils.create_structure(task)
                        except Exception as e:
                            QtWidgets.QMessageBox.critical(self, "Error", str(e))
                        finally:
                            QtWidgets.QMessageBox.information(
                                self,
                                "Project Folder Structure is created!",
                                "Project Folder Structure is created!",
                            )
                    else:
                        return

                elif selected_action is fix_task_status_action:
                    from stalker.db.session import DBSession
                    from stalker import SimpleEntity, Task
                    from anima import utils

                    for entity in self.get_selected_tasks():
                        if isinstance(entity, Task):
                            utils.fix_task_statuses(entity)
                            utils.fix_task_computed_time(entity)
                            DBSession.add(entity)
                    DBSession.commit()

                    unique_parent_items = []
                    for item in self.get_selected_task_items():
                        if item.parent and item.parent not in unique_parent_items:
                            unique_parent_items.append(item.parent)

                    for parent_item in unique_parent_items:
                        parent_item.reload()

                elif selected_action is update_project_action:
                    from anima.ui import project_dialog

                    project_main_dialog = project_dialog.MainDialog(
                        parent=self, project=entity
                    )
                    project_main_dialog.exec_()
                    result = project_main_dialog.result()

                    # refresh the task list
                    if result == accepted:
                        self.fill()

                        # reselect the same task
                        self.find_and_select_entity_item(entity)

                    project_main_dialog.deleteLater()

                elif selected_action is assign_users_action:
                    from anima.ui import project_users_dialog

                    project_users_main_dialog = project_users_dialog.MainDialog(
                        parent=self, project=entity
                    )
                    project_users_main_dialog.exec_()
                    result = project_users_main_dialog.result()

                    project_users_main_dialog.deleteLater()

                elif selected_action in change_status_menu_actions:
                    # get the status code
                    status_code = selected_action.text()

                    from sqlalchemy import func

                    status = Status.query.filter(
                        func.lower(Status.code) == func.lower(status_code)
                    ).first()

                    # change the status of the entity
                    # if it is a leaf task
                    # if it doesn't have any dependent_of
                    # assert isinstance(entity, Task)
                    for task in self.get_selected_tasks():
                        if task.is_leaf and not task.dependent_of:
                            # then we can update it
                            task.status = status

                            # # fix other task statuses
                            # from anima import utils
                            # utils.fix_task_statuses(entity)

                            # refresh the tree
                            from stalker.db.session import DBSession

                            DBSession.add(task)
                            DBSession.commit()

                            if item.parent:
                                item.parent.reload()
                                self.find_and_select_entity_item(entity)
                else:
                    try:
                        # go to the dependencies
                        dep_task = selected_action.task
                        self.find_and_select_entity_item(dep_task, self)
                    except AttributeError:
                        pass

    def double_clicked_on_entity(self, index):
        """runs when double clicked on an leaf entity

        :param index:
        :return:
        """
        model = self.model()
        item = model.itemFromIndex(index)
        if not item:
            return

        if item.hasChildren():
            return

        logger.debug("item : %s" % item)
        task_id = None
        entity = None

        try:
            if item.task:
                task_id = item.task.id
        except AttributeError:
            return

        from stalker import Task

        if item.task.entity_type == "Task":

            if task_id:
                from stalker import SimpleEntity

                entity = SimpleEntity.query.get(task_id)

            from anima.ui import task_dialog

            task_main_dialog = task_dialog.MainDialog(parent=self, tasks=[entity])
            task_main_dialog.exec_()
            result = task_main_dialog.result()
            task_main_dialog.deleteLater()

            try:
                # PySide and PySide2
                accepted = QtWidgets.QDialog.DialogCode.Accepted
            except AttributeError:
                # PyQt4
                accepted = QtWidgets.QDialog.Accepted

            # refresh the task list
            if result == accepted:
                # just reload the same item
                if item.parent:
                    item.parent.reload()
                else:
                    # reload the entire
                    self.fill()

                self.find_and_select_entity_item(entity)

    def find_and_select_entity_item(self, tasks, tree_view=None):
        """Find and select the task in the given tree_view item.

        :param tasks: A list of Stalker tasks. A single Task is also accepted.
        :param tree_view: QTreeView or derivative.
        """
        if not tasks:
            return

        selection_model = self.selectionModel()
        selection_model.clearSelection()
        selection_flag = QtCore.QItemSelectionModel.Select

        if not tree_view:
            tree_view = self

        if not isinstance(tasks, list):
            tasks = [tasks]

        items = []
        for task in tasks:
            item = self.load_task_item_hierarchy(task, tree_view)
            if item:
                selection_model.select(item.index(), selection_flag)
                items.append(item)

        # scroll to the first item
        if items:
            self.scrollTo(
                items[0].index(), QtWidgets.QAbstractItemView.PositionAtCenter
            )
        return items

    def load_task_item_hierarchy(self, task, tree_view):
        """loads the TaskItem related to the given task in the given tree_view

        :return: TaskItem instance
        """
        if not task:
            return

        self.is_updating = True
        item = self.find_entity_item(task)
        if not item:
            # the item is not loaded to the UI yet
            # start loading its parents
            # start from the project
            from stalker import Task

            if isinstance(task, Task):
                item = self.find_entity_item(task.project, tree_view)
            else:
                item = self.find_entity_item(task, tree_view)
            logger.debug("item for project: %s" % item)

            if item:
                tree_view.setExpanded(item.index(), True)

            if isinstance(task, Task) and task.parents:
                # now starting from the most outer parent expand the tasks
                for parent in task.parents:
                    item = self.find_entity_item(parent, tree_view)

                    if item:
                        tree_view.setExpanded(item.index(), True)

            # finally select the task
            item = self.find_entity_item(task, tree_view)

            if not item:
                # still no item
                logger.debug("can not find item")

        self.is_updating = False
        return item

    def find_entity_item(self, entity, tree_view=None):
        """finds the item related to the stalker entity in the given
        QtTreeView
        """
        if not entity:
            return None

        if tree_view is None:
            tree_view = self

        indexes = self.get_item_indices_containing_text(entity.name, tree_view)
        model = tree_view.model()
        logger.debug("items matching name : %s" % indexes)
        for index in indexes:
            item = model.itemFromIndex(index)
            if item:
                if item.task.id == entity.id:
                    return item
        return None

    @classmethod
    def get_item_indices_containing_text(cls, text, tree_view):
        """returns the indexes of the item indices containing the given text"""
        model = tree_view.model()
        logger.debug("searching for text : %s" % text)
        return model.match(model.index(0, 0), 0, text, -1, QtCore.Qt.MatchRecursive)

    def get_selected_task_items(self):
        """returns the selected TaskItems"""
        from anima.ui.models.task import TaskItem

        selection_model = self.selectionModel()
        logger.debug("selection_model: %s" % selection_model)
        indexes = selection_model.selectedIndexes()
        logger.debug("selected indexes : %s" % indexes)
        task_items = []
        if indexes:
            item_model = self.model()
            logger.debug("indexes: %s" % indexes)
            for index in indexes:
                current_item = item_model.itemFromIndex(index)
                if current_item and isinstance(current_item, TaskItem):
                    task_items.append(current_item)
        logger.debug("task_items: %s" % task_items)
        return task_items

    def get_selected_task_ids(self):
        """returns the task from the UI, it is an task, asset, shot, sequence
        or project
        """
        task_ids = []
        for item in self.get_selected_task_items():
            task_id = item.task.id
            task_ids.append(task_id)

        logger.debug("task_ids: %s" % task_ids)
        return task_ids

    def get_selected_tasks(self):
        """returns the selected tasks"""
        task_ids = self.get_selected_task_ids()
        from stalker import SimpleEntity

        return list(SimpleEntity.query.filter(SimpleEntity.id.in_(task_ids)).all())

    def expand_all_selected(self, index):
        """expands all the selected items

        :param index:
        :return:
        """
        for item in self.get_selected_task_items():
            self.setExpanded(item.index(), True)
        self.auto_fit_column()

    def collapse_all_selected(self, index):
        """collapse all the selected items

        :param index:
        :return:
        """
        for item in self.get_selected_task_items():
            self.setExpanded(item.index(), False)
        self.auto_fit_column()
