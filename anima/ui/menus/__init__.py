# -*- coding: utf-8 -*-
import json
import os
import webbrowser
from functools import partial

from anima import defaults, logger
from anima.ui.lib import QtCore, QtGui, QtWidgets
from anima.ui.utils import choose_thumbnail, get_cached_icon
from anima.utils import (
    create_structure,
    duplicate_task_hierarchy,
    fix_task_computed_time,
    fix_task_statuses,
    open_browser_in_location,
    task_hierarchy_io,
    upload_thumbnail,
)
from anima.utils.progress import ProgressManager

from sqlalchemy import func

from stalker import (
    LocalSession,
    Project,
    SimpleEntity,
    Status,
    StatusList,
    Studio,
    Task,
)
from stalker.db.session import DBSession


if False:
    # this is for the IDE to pickup the code more easily
    from PySide2 import QtCore, QtGui, QtWidgets


class MainMenuBar(QtWidgets.QMenuBar):
    """Main application menu.

    Has similar options like Stalker Pyramid.
    """

    # signals
    list_clients_signal = QtCore.Signal()
    list_departments_signal = QtCore.Signal()
    list_groups_signal = QtCore.Signal()
    list_users_signal = QtCore.Signal()
    view_project_signal = QtCore.Signal(object)
    view_studio_signal = QtCore.Signal(object)
    view_user_signal = QtCore.Signal(object)
    create_project_signal = QtCore.Signal()

    def __init__(self, *args, **kwargs):
        super(MainMenuBar, self).__init__(*args, **kwargs)
        self.home_action = None
        self.studio_menu = None
        self.crew_menu = None
        self.users_action = None
        self.departments_action = None
        self.groups_action = None
        self.clients_action = None
        self.projects_menu = None
        self.setup()

    def setup(self):
        """Create the main application menu."""
        # Home Action
        self.home_action = self.addAction("Home")
        self.home_action.triggered.connect(partial(self.home_action_triggered))

        # Studio Menu
        self.studio_menu = self.addMenu("Studio")
        for studio in Studio.query.all():
            studio_action = self.studio_menu.addAction(studio.name)
            studio_action.triggered.connect(
                partial(self.view_studio_signal.emit, studio)
            )

        # Crew Menu
        self.crew_menu = self.addMenu("Crew")

        # Users
        self.users_action = self.crew_menu.addAction("Users")
        self.users_action.triggered.connect(self.list_users_signal.emit)

        # Departments
        self.departments_action = self.crew_menu.addAction("Departments")
        self.departments_action.triggered.connect(self.list_departments_signal.emit)

        # Groups
        self.groups_action = self.crew_menu.addAction("Groups")
        self.groups_action.triggered.connect(self.list_groups_signal.emit)

        # Clients
        self.clients_action = self.crew_menu.addAction("Clients")
        self.clients_action.triggered.connect(self.list_clients_signal.emit)

        # Projects Menu
        self.projects_menu = self.addMenu("Projects")
        # get all distinct project statuses
        project_status_list = StatusList.query.filter(
            StatusList.target_entity_type == "Project"
        ).first()
        for status in project_status_list.statuses:
            projects = (
                Project.query.filter(Project.status == status)
                .order_by(Project.name)
                .all()
            )
            if not projects:
                continue
            # create the status menu
            status_menu = self.projects_menu.addMenu(status.name)
            for project in projects:
                project_action = status_menu.addAction(project.name)
                assert isinstance(project_action, QtWidgets.QAction)
                project_action.triggered.connect(
                    partial(self.view_project_signal.emit, project)
                )
        # also add the new project dialog
        self.projects_menu.addSeparator()
        plus_icon = get_cached_icon("new_entity")
        new_project_action = self.projects_menu.addAction("New Project")
        new_project_action.setIcon(plus_icon)
        new_project_action.triggered.connect(self.create_project_signal.emit)

    def home_action_triggered(self):
        """Get the logged in user and emit a View User signal."""
        from stalker import LocalSession

        session = LocalSession()
        logged_in_user = session.logged_in_user
        self.view_user_signal.emit(logged_in_user)


class ContextMenuHandlerBase(object):
    """Base context menu handler.

    Other context menus derives from this one.

    Args:
        parent (QWidget): The parent QWidget.
    """

    def __init__(self, parent=None):
        self.parent = parent

    def show_context_menu(self, position):
        """Shot the context menu.

        Args:
            position (QPoint): Menu position.
        """
        if not self.parent:
            return

        return QtWidgets.QMenu(self.parent)


class TaskDataContextMenuHandler(ContextMenuHandlerBase):
    """Context menu for Task related views."""

    def show_context_menu(self, position):
        """Shot custom context menu.

        Args:
            position (QPoint): The menu display position.
        """
        # convert the position to global screen position
        global_position = self.parent.mapToGlobal(position)

        index = self.parent.indexAt(position)
        model = self.parent.model()
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

        local_session = LocalSession()
        logged_in_user = local_session.logged_in_user

        # TODO: Update this to use only task_id
        if task_id:
            entity = SimpleEntity.query.get(task_id)

        reload_action = menu.addAction(get_cached_icon("reload"), "Reload")

        # sub menus
        create_sub_menu = menu.addMenu("Create")
        update_sub_menu = menu.addMenu("Update")

        if defaults.is_power_user(logged_in_user):
            # create the Create Project menu item
            create_project_action = create_sub_menu.addAction(
                get_cached_icon("create_project"), "Create Project..."
            )

            if isinstance(entity, Project):
                # this is a project!
                if defaults.is_power_user(logged_in_user):
                    update_project_action = update_sub_menu.addAction(
                        get_cached_icon("update_project"), "Update Project..."
                    )
                    assign_users_action = menu.addAction(
                        get_cached_icon("users"), "Assign Users..."
                    )
                    create_project_structure_action = create_sub_menu.addAction(
                        get_cached_icon("browse_folder"), "Create Project Structure"
                    )
                    create_child_task_action = create_sub_menu.addAction(
                        get_cached_icon("task"), "Create Child Task..."
                    )
                    # Export and Import JSON
                    create_sub_menu.addSeparator()
                    # export_to_json_action = create_sub_menu.addAction(
                    #     get_cached_icon("export"), "Export To JSON..."
                    # )

                    import_from_json_action = create_sub_menu.addAction(
                        get_cached_icon("import"), "Import From JSON..."
                    )

        if entity:
            # separate the Project and Task related menu items
            menu.addSeparator()

            open_in_web_browser_action = menu.addAction(
                get_cached_icon("open_external_link"), "Open In Web Browser..."
            )
            open_in_file_browser_action = menu.addAction(
                get_cached_icon("browse_folder"), "Browse Folders..."
            )
            copy_icon = get_cached_icon("copy")
            copy_url_action = menu.addAction(copy_icon, "Copy URL")
            copy_id_to_clipboard = menu.addAction(copy_icon, "Copy ID to clipboard")

            if isinstance(entity, Task):
                # this is a task
                create_project_structure_action = create_sub_menu.addAction(
                    get_cached_icon("browse_folder"), "Create Task Folder Structure"
                )

                task = entity

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
                        get_cached_icon("timelog"), "Create TimeLog..."
                    )

                # Add Depends To menu
                menu.addSeparator()
                depends = task.depends
                if depends:
                    depends_to_menu = menu.addMenu(
                        get_cached_icon("depends_to"), "Depends To"
                    )

                    for dTask in depends:
                        action = depends_to_menu.addAction(dTask.name)
                        action.task = dTask

                # Add Dependent Of Menu
                dependent_of = task.dependent_of
                if dependent_of:
                    dependent_of_menu = menu.addMenu(
                        get_cached_icon("dependent_of"), "Dependent Of"
                    )

                    for dTask in dependent_of:
                        action = dependent_of_menu.addAction(dTask.name)
                        action.task = dTask

                if not depends and not dependent_of:
                    no_deps_action = menu.addAction(
                        get_cached_icon("cross"), "No Dependencies"
                    )
                    no_deps_action.setEnabled(False)

                # update task and create child task menu items
                menu.addSeparator()
                if defaults.is_power_user(logged_in_user):
                    create_sub_menu.addSeparator()
                    update_task_action = update_sub_menu.addAction(
                        get_cached_icon("edit_entity"), "Update Task..."
                    )

                    upload_thumbnail_action = update_sub_menu.addAction(
                        get_cached_icon("image"), "Upload Thumbnail..."
                    )

                    # Export and Import JSON
                    create_sub_menu.addSeparator()
                    export_to_json_action = create_sub_menu.addAction(
                        get_cached_icon("export"), "Export To JSON..."
                    )

                    import_from_json_action = create_sub_menu.addAction(
                        get_cached_icon("import"), "Import From JSON..."
                    )
                    create_sub_menu.addSeparator()

                    create_child_task_action = create_sub_menu.addAction(
                        get_cached_icon("task"), "Create Child Task..."
                    )

                    duplicate_task_hierarchy_action = create_sub_menu.addAction(
                        get_cached_icon("copy"), "Duplicate Task Hierarchy..."
                    )
                    delete_task_action = menu.addAction(
                        get_cached_icon("delete"), "Delete Task..."
                    )

                    menu.addSeparator()

                # create the status_menu
                status_menu = update_sub_menu.addMenu("Status")

                fix_task_status_action = status_menu.addAction(
                    get_cached_icon("create_project"), "Fix Task Status"
                )

                assert isinstance(status_menu, QtWidgets.QMenu)
                status_menu.addSeparator()

                # get all task statuses
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
                    self.parent.fill()
                    self.parent.find_and_select_entity_item(item.task)
                else:
                    for item in self.parent.get_selected_task_items():
                        item.reload()

            if create_project_action and selected_action is create_project_action:
                from anima.ui.dialogs import project_dialog

                project_main_dialog = project_dialog.MainDialog(
                    parent=self.parent, project=None
                )
                project_main_dialog.exec_()
                result = project_main_dialog.result()

                # refresh the task list
                if result == accepted:
                    self.parent.fill()

                project_main_dialog.deleteLater()

            if entity:
                url = "http://%s/%ss/%s/view" % (
                    defaults.stalker_server_internal_address,
                    entity.entity_type.lower(),
                    entity.id,
                )

                if selected_action is open_in_web_browser_action:
                    webbrowser.open(url)
                elif selected_action is open_in_file_browser_action:
                    try:
                        open_browser_in_location(entity.absolute_path)
                    except IOError as e:
                        QtWidgets.QMessageBox.critical(
                            self.parent, "Error", "%s" % e, QtWidgets.QMessageBox.Ok
                        )
                elif selected_action is copy_url_action:
                    clipboard = QtWidgets.QApplication.clipboard()
                    clipboard.setText(url)

                    # and warn the user about a new version is created and the
                    # clipboard is set to the new version full path
                    QtWidgets.QMessageBox.warning(
                        self.parent,
                        "URL Copied To Clipboard",
                        "URL:<br><br>%s<br><br>is copied to clipboard!" % url,
                        QtWidgets.QMessageBox.Ok,
                    )
                elif selected_action is copy_id_to_clipboard:

                    clipboard = QtWidgets.QApplication.clipboard()
                    selected_entity_ids = ", ".join(
                        list(map(str, self.parent.get_selected_task_ids()))
                    )
                    clipboard.setText(selected_entity_ids)

                    # and warn the user about a new version is created and the
                    # clipboard is set to the new version full path
                    QtWidgets.QMessageBox.warning(
                        self.parent,
                        "ID Copied To Clipboard",
                        "IDs are copied to clipboard!<br>%s" % selected_entity_ids,
                        QtWidgets.QMessageBox.Ok,
                    )

                elif selected_action is create_time_log_action:
                    from anima.ui.dialogs import time_log_dialog

                    time_log_dialog_main_dialog = time_log_dialog.MainDialog(
                        parent=self.parent,
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
                            self.parent.fill()

                        # reselect the same task
                        self.parent.find_and_select_entity_item(entity)

                elif selected_action is update_task_action:
                    from anima.ui.dialogs import task_dialog

                    task_main_dialog = task_dialog.MainDialog(
                        parent=self.parent, tasks=self.parent.get_selected_tasks()
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
                            self.parent.fill()
                        self.parent.find_and_select_entity_item(entity)

                elif selected_action is upload_thumbnail_action:
                    thumbnail_full_path = choose_thumbnail(
                        self.parent,
                        start_path=entity.absolute_path,
                        dialog_title="Choose Thumbnail For: %s" % entity.name,
                    )

                    # if the thumbnail_full_path is empty do not do anything
                    if thumbnail_full_path == "":
                        return

                    # get the current task
                    upload_thumbnail(entity, thumbnail_full_path)

                elif selected_action is create_child_task_action:
                    from anima.ui.dialogs import task_dialog

                    task_main_dialog = task_dialog.MainDialog(
                        parent=self.parent, parent_task=entity
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
                            self.parent.fill()
                        self.parent.find_and_select_entity_item(tasks[0])

                elif selected_action is duplicate_task_hierarchy_action:
                    from anima.ui.dialogs.task_dialog import (
                        DuplicateTaskHierarchyDialog,
                    )

                    dth_dialog = DuplicateTaskHierarchyDialog(
                        parent=self.parent, duplicated_task_name=item.task.name
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

                        new_tasks = []
                        parents_to_reload = set()
                        for item in self.parent.get_selected_task_items():
                            task = Task.query.get(item.task.id)
                            new_tasks += duplicate_task_hierarchy(
                                task,
                                None,
                                new_task_name if rename_new_tasks else None,
                                description="Duplicated from Task(%s)" % task.id,
                                user=logged_in_user,
                                keep_resources=keep_resources,
                                number_of_copies=number_of_copies,
                            )

                            parents_to_reload.add(item.parent)

                        # reload all the parents
                        for parent in parents_to_reload:
                            parent.reload()

                        # now select new tasks
                        self.parent.find_and_select_entity_item(new_tasks)

                elif selected_action is delete_task_action:
                    answer = QtWidgets.QMessageBox.question(
                        self.parent,
                        "Delete Task?",
                        "Delete the task and children?<br><br>(NO UNDO!!!!)",
                        QtWidgets.QMessageBox.Yes,
                        QtWidgets.QMessageBox.No,
                    )
                    if answer == QtWidgets.QMessageBox.Yes:
                        tasks = self.parent.get_selected_tasks()
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
                        for item in self.parent.get_selected_task_items():
                            if item.parent and item.parent not in unique_parent_items:
                                unique_parent_items.append(item.parent)

                        if unique_parent_items:
                            for parent_item in unique_parent_items:
                                parent_item.reload()
                        else:
                            self.parent.fill()
                        # either select the next or previous task or the parent
                        self.parent.find_and_select_entity_item(select_task)

                elif selected_action is export_to_json_action:
                    # show a file browser
                    dialog = QtWidgets.QFileDialog(self.parent, "Choose file")
                    dialog.setNameFilter("JSON Files (*.json)")
                    dialog.setFileMode(QtWidgets.QFileDialog.AnyFile)
                    if dialog.exec_():
                        file_path = dialog.selectedFiles()[0]
                        if file_path:
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
                            except Exception:
                                pass
                            finally:
                                QtWidgets.QMessageBox.information(
                                    self.parent,
                                    "Task data Export to JSON!",
                                    "Task data Export to JSON!",
                                )

                elif selected_action is import_from_json_action:
                    # show a file browser
                    dialog = QtWidgets.QFileDialog(self.parent, "Choose file or files")
                    dialog.setNameFilter("JSON Files (*.json)")
                    dialog.setFileMode(QtWidgets.QFileDialog.ExistingFiles)
                    if dialog.exec_():
                        items_to_reload = set()
                        imported_json_file_names = []
                        selected_files = dialog.selectedFiles()
                        if not selected_files:
                            return

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
                        from anima.ui.dialogs.progress_dialog import ProgressDialog

                        pdm = ProgressManager(dialog_class=ProgressDialog)
                        progress_caller = pdm.register(
                            max_iteration=len(selected_files),
                            title="Importing JSON files...",
                        )
                        for file_path in selected_files:
                            imported_json_file_name = os.path.basename(file_path)
                            with open(file_path) as f:
                                data = json.load(f)
                            loaded_entity = decoder.loads(data, parent=parent)

                            try:
                                DBSession.add(loaded_entity)
                                DBSession.commit()
                            except Exception as e:
                                DBSession.rollback()
                                QtWidgets.QMessageBox.critical(
                                    self.parent,
                                    "Error!",
                                    "%s" % e,
                                    QtWidgets.QMessageBox.Ok,
                                )
                            else:
                                items_to_reload.add(item)
                                imported_json_file_names.append(imported_json_file_name)
                            progress_caller.step(message=imported_json_file_name)
                        progress_caller.end_progress()

                        for item in items_to_reload:
                            item.reload()
                        QtWidgets.QMessageBox.information(
                            self.parent,
                            "New Tasks are created!",
                            "New Tasks are imported from:<br><br>{}".format(
                                "<br>".join(imported_json_file_names[:40])
                            ),
                        )

                elif selected_action is create_project_structure_action:
                    answer = QtWidgets.QMessageBox.question(
                        self.parent,
                        "Create Project Folder Structure?",
                        "This will create project folders, OK?",
                        QtWidgets.QMessageBox.Yes,
                        QtWidgets.QMessageBox.No,
                    )
                    if answer == QtWidgets.QMessageBox.Yes:
                        try:
                            for task in self.parent.get_selected_tasks():
                                create_structure(task)
                        except Exception as e:
                            QtWidgets.QMessageBox.critical(self.parent, "Error", str(e))
                        finally:
                            QtWidgets.QMessageBox.information(
                                self.parent,
                                "Project Folder Structure is created!",
                                "Project Folder Structure is created!",
                            )
                    else:
                        return

                elif selected_action is fix_task_status_action:
                    for entity in self.parent.get_selected_tasks():
                        if isinstance(entity, Task):
                            fix_task_statuses(entity)
                            fix_task_computed_time(entity)
                            DBSession.add(entity)
                    DBSession.commit()

                    unique_parent_items = []
                    for item in self.parent.get_selected_task_items():
                        if item.parent and item.parent not in unique_parent_items:
                            unique_parent_items.append(item.parent)

                    for parent_item in unique_parent_items:
                        parent_item.reload()

                elif selected_action is update_project_action:
                    from anima.ui.dialogs import project_dialog

                    project_main_dialog = project_dialog.MainDialog(
                        parent=self.parent, project=entity
                    )
                    project_main_dialog.exec_()
                    result = project_main_dialog.result()

                    # refresh the task list
                    if result == accepted:
                        self.parent.fill()

                        # reselect the same task
                        self.parent.find_and_select_entity_item(entity)

                    project_main_dialog.deleteLater()

                elif selected_action is assign_users_action:
                    from anima.ui.dialogs import project_users_dialog

                    project_users_main_dialog = project_users_dialog.MainDialog(
                        parent=self.parent, project=entity
                    )
                    project_users_main_dialog.exec_()
                    result = project_users_main_dialog.result()

                    project_users_main_dialog.deleteLater()

                elif selected_action in change_status_menu_actions:
                    # get the status code
                    status_code = selected_action.text()
                    status = Status.query.filter(
                        func.lower(Status.code) == func.lower(status_code)
                    ).first()

                    status_cmpl = Status.query.filter(Status.code == "CMPL").first()

                    # change the status of the entity
                    # if it is a leaf task
                    # if it doesn't have any task that it depends on
                    # or all of the dependent tasks are completed
                    # assert isinstance(entity, Task)
                    for task in self.parent.get_selected_tasks():
                        if task.is_leaf and (
                            not task.depends
                            or all([t.status == status_cmpl for t in task.depends])
                        ):
                            # then we can update it
                            task.status = status

                            # # fix other task statuses
                            # fix_task_statuses(entity)

                            # refresh the tree
                            DBSession.add(task)
                            DBSession.commit()

                            if item.parent:
                                item.parent.reload()
                                self.parent.find_and_select_entity_item(entity)
                else:
                    try:
                        # go to the dependencies
                        dep_task = selected_action.task
                        self.parent.find_and_select_entity_item(dep_task, self)
                    except AttributeError:
                        pass
