# -*- coding: utf-8 -*-
# Copyright (c) 2012-2017, Anima Istanbul
#
# This module is part of anima-tools and is released under the BSD 2
# License: http://www.opensource.org/licenses/BSD-2-Clause

from anima import logger
from anima.ui.lib import QtCore, QtGui, QtWidgets
from anima.ui.models.task import TaskTreeModel


class DuplicateTaskHierarchyDialog(QtWidgets.QDialog):
    """custom dialog for duplicating task hierarchies
    """

    def __init__(self, parent=None, duplicated_task_name='', *args, **kwargs):
        super(DuplicateTaskHierarchyDialog, self).__init__(
            parent=parent, *args, **kwargs
        )

        self.duplicated_task_name = duplicated_task_name

        # storage for widgets
        self.main_layout = None
        self.label = None
        self.line_edit = None
        self.check_box = None
        self.button_box = None

        # setup dialog
        self._setup_dialog()

    def _setup_dialog(self):
        """create the UI elements
        """
        # set window title
        self.setWindowTitle("Duplicate Task Hierarchy")

        # set window size
        self.resize(285, 118)

        # create the main layout
        self.main_layout = QtWidgets.QVBoxLayout(self)
        self.setLayout(self.main_layout)

        # the label
        self.label = QtWidgets.QLabel(self)
        self.label.setText('Duplicated Task Name:')
        self.main_layout.addWidget(self.label)

        # the line edit
        self.line_edit = QtWidgets.QLineEdit(self)
        self.line_edit.setText(self.duplicated_task_name)
        self.main_layout.addWidget(self.line_edit)

        # the check box
        self.check_box = QtWidgets.QCheckBox(self)
        self.check_box.setText('Keep resources')
        self.main_layout.addWidget(self.check_box)

        # the button box
        self.button_box = QtWidgets.QDialogButtonBox(self)
        self.button_box.setOrientation(QtCore.Qt.Horizontal)
        self.button_box.setStandardButtons(
            QtWidgets.QDialogButtonBox.Cancel |
            QtWidgets.QDialogButtonBox.Ok
        )
        self.main_layout.addWidget(self.button_box)

        # setup signals
        QtCore.QObject.connect(
            self.button_box,
            QtCore.SIGNAL("accepted()"),
            self.accept
        )
        QtCore.QObject.connect(
            self.button_box,
            QtCore.SIGNAL("rejected()"),
            self.reject
        )


class TaskTreeView(QtWidgets.QTreeView):
    """A custom tree view to display Tasks info
    """

    def __init__(self, *args, **kwargs):
        self.project = kwargs.pop('project', None)
        self.show_completed_projects = False

        super(TaskTreeView, self).__init__(*args, **kwargs)

        self.is_updating = False

        self.setAlternatingRowColors(True)
        self.setUniformRowHeights(True)
        self.header().setCascadingSectionResizes(True)

        # # allow multiple selection
        # self.setSelectionMode(self.MultiSelection)

        # delegate = TaskItemDelegate(self)
        # self.setItemDelegate(delegate)
        self.setup_signals()

    def setup_signals(self):
        """connects the signals to slots
        """
        # fit column 0 on expand/collapse
        QtCore.QObject.connect(
            self,
            QtCore.SIGNAL('expanded(QModelIndex)'),
            self.auto_fit_column
        )

        QtCore.QObject.connect(
            self,
            QtCore.SIGNAL('collapsed(QModelIndex)'),
            self.auto_fit_column
        )

        # custom context menu for the tasks_treeView
        self.setContextMenuPolicy(
            QtCore.Qt.CustomContextMenu
        )

        QtCore.QObject.connect(
            self,
            QtCore.SIGNAL("customContextMenuRequested(const QPoint&)"),
            self.show_context_menu
        )

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
        """fits columns to content
        """
        self.resizeColumnToContents(0)

    def fill(self):
        """fills the tree view with data
        """
        logger.debug('start filling tasks_treeView')
        logger.debug('creating a new model')
        if not self.project:
            from sqlalchemy import alias
            from stalker import Task, Project
            from stalker.db.session import DBSession
            # projects = Project.query.order_by(Project.name).all()
            inner_tasks = alias(Task.__table__)
            subquery = DBSession.query(inner_tasks.c.id).filter(
                inner_tasks.c.project_id == Project.id)
            query = DBSession\
                .query(
                    Project.id, Project.name, Project.entity_type,
                    Project.status_id,
                    subquery.exists().label('has_children')
                )
            if not self.show_completed_projects:
                from stalker import Status
                status_cmpl = \
                    Status.query.filter(Status.code == 'CMPL').first()
                query = query.filter(Project.status != status_cmpl)

            query = query.order_by(Project.name)
            projects = query.all()
        else:
            self.project.has_children = bool(self.project.tasks)
            projects = [self.project]

        logger.debug('projects: %s' % projects)

        # delete the old model if any
        if self.model() is not None:
            self.model().deleteLater()

        task_tree_model = TaskTreeModel()
        task_tree_model.populateTree(projects)
        self.setModel(task_tree_model)
        self.is_updating = False

        self.auto_fit_column()

        logger.debug('finished filling tasks_treeView')

    def show_context_menu(self, position):
        """the custom context menu
        """
        # convert the position to global screen position
        global_position = self.mapToGlobal(position)

        index = self.indexAt(position)
        model = self.model()
        item = model.itemFromIndex(index)
        logger.debug('itemAt(position) : %s' % item)
        task_id = None
        entity = None

        # if not item:
        #     return

        # if item and not hasattr(item, 'task'):
        #     return

        from anima.ui.models.task import TaskItem
        #if not isinstance(item, TaskItem):
        #    return

        if item and item.task:
            task_id = item.task.id

        # if not task_id:
        #     return

        from anima import utils
        file_browser_name = utils.file_browser_name()

        # create the menu
        menu = QtWidgets.QMenu()  # Open in browser

        # sub menus
        create_sub_menu = menu.addMenu('Create')
        update_sub_menu = menu.addMenu('Update')

        # -----------------------------------
        # actions created in different scopes
        create_time_log_action = None
        create_project_action = None
        update_task_action = None
        create_child_task_action = None
        duplicate_task_hierarchy_action = None
        delete_task_action = None
        no_deps_action = None
        create_project_structure_action = None
        create_task_structure_action = None
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

        if defaults.is_power_user(logged_in_user):
            # create the Create Project menu item
            create_project_action = \
                create_sub_menu.addAction(u'\uf0e8 Create Project...')

            if isinstance(entity, Project):
                # this is a project!
                if defaults.is_power_user(logged_in_user):
                    update_project_action = \
                        update_sub_menu.addAction(u'\uf044 Update Project...')
                    assign_users_action = \
                        menu.addAction(u'\uf0c0 Assign Users...')
                    create_project_structure_action = \
                        create_sub_menu.addAction(
                            u'\uf115 Create Project Structure'
                        )
                    create_child_task_action = \
                        create_sub_menu.addAction(
                            u'\uf0ae Create Child Task...'
                        )

        if entity:
            # separate the Project and Task related menu items
            menu.addSeparator()

            open_in_web_browser_action = \
                menu.addAction(u'\uf14c Open In Web Browser...')
            open_in_file_browser_action = \
                menu.addAction(u'\uf07c Browse Folders...')
            copy_url_action = menu.addAction(u'\uf0c5 Copy URL')
            copy_id_to_clipboard = \
                menu.addAction(u'\uf0c5 Copy ID to clipboard')

            if isinstance(entity, Task):
                # this is a task
                create_task_structure_action = \
                    create_sub_menu.addAction(
                        u'\uf115 Create Task Folder Structure'
                    )

                task = entity
                from stalker import Status
                status_wfd = Status.query.filter(Status.code == 'WFD').first()
                status_prev = \
                    Status.query.filter(Status.code == 'PREV').first()
                status_cmpl = \
                    Status.query.filter(Status.code == 'CMPL').first()
                if logged_in_user in task.resources \
                        and task.status not in [status_wfd, status_prev,
                                                status_cmpl]:
                    create_sub_menu.addSeparator()
                    create_time_log_action = \
                        create_sub_menu.addAction(u'\uf073 Create TimeLog...')

                # Add Depends To menu
                menu.addSeparator()
                depends = task.depends
                if depends:
                    depends_to_menu = menu.addMenu(u'\uf090 Depends To')

                    for dTask in depends:
                        action = depends_to_menu.addAction(dTask.name)
                        action.task = dTask

                # Add Dependent Of Menu
                dependent_of = task.dependent_of
                if dependent_of:
                    dependent_of_menu = menu.addMenu(u'\uf08b Dependent Of')

                    for dTask in dependent_of:
                        action = dependent_of_menu.addAction(dTask.name)
                        action.task = dTask

                if not depends and not dependent_of:
                    no_deps_action = menu.addAction(u'\uf00d No Dependencies')
                    no_deps_action.setEnabled(False)

                # update task and create child task menu items
                menu.addSeparator()
                if defaults.is_power_user(logged_in_user):
                    create_sub_menu.addSeparator()
                    update_task_action = \
                        update_sub_menu.addAction(u'\uf044 Update Task...')

                    create_child_task_action = \
                        create_sub_menu.addAction(
                            u'\uf0ae Create Child Task...'
                        )
                    duplicate_task_hierarchy_action = \
                        create_sub_menu.addAction(
                            u'\uf0c5 Duplicate Task Hierarchy...'
                        )
                    delete_task_action = \
                        menu.addAction(u'\uf1f8 Delete Task...')

                # create the status_menu
                status_menu = update_sub_menu.addMenu('Status')

                fix_task_status_action = \
                    status_menu.addAction(u'\uf0e8 Fix Task Status')

                assert isinstance(status_menu, QtWidgets.QMenu)
                status_menu.addSeparator()

                # get all task statuses
                from anima import defaults

                menu_style_sheet = ''
                defaults_status_colors = defaults.status_colors
                for status_code in defaults.status_colors:
                    change_status_menu_action = \
                        status_menu.addAction(status_code)

                    change_status_menu_action.setObjectName(
                        'status_%s' % status_code
                    )

                    change_status_menu_actions.append(
                        change_status_menu_action
                    )

                    menu_style_sheet = "%s %s" % (
                        menu_style_sheet,
                        "QMenu#status_%s { background: %s %s %s}" %
                        (
                            status_code,
                            defaults_status_colors[status_code][0],
                            defaults_status_colors[status_code][1],
                            defaults_status_colors[status_code][2],
                        )
                    )

                # change the BG Color of the status
                status_menu.setStyleSheet(menu_style_sheet)

        try:
            # PySide and PySide2
            accepted = QtWidgets.QDialog.DialogCode.Accepted
        except AttributeError:
            # PyQt4
            accepted = QtWidgets.QDialog.Accepted

        selected_item = menu.exec_(global_position)
        if selected_item:
            if create_project_action \
               and selected_item == create_project_action:
                from anima.ui import project_dialog
                project_main_dialog = project_dialog.MainDialog(
                    parent=self,
                    project=None
                )
                project_main_dialog.exec_()
                result = project_main_dialog.result()

                # refresh the task list
                if result == accepted:
                    self.fill()

                project_main_dialog.deleteLater()

            if entity:
                from anima import defaults
                url = 'http://%s/%ss/%s/view' % (
                    defaults.stalker_server_internal_address,
                    entity.entity_type.lower(),
                    entity.id
                )

                if selected_item is open_in_web_browser_action:
                    import webbrowser
                    webbrowser.open(url)
                elif selected_item is open_in_file_browser_action:
                    from anima import utils
                    try:
                        utils.open_browser_in_location(entity.absolute_path)
                    except IOError as e:
                        QtWidgets.QMessageBox.critical(
                            self,
                            "Error",
                            "%s" % e,
                            QtWidgets.QMessageBox.Ok
                        )
                elif selected_item is copy_url_action:
                    clipboard = QtWidgets.QApplication.clipboard()
                    clipboard.setText(url)

                    # and warn the user about a new version is created and the
                    # clipboard is set to the new version full path
                    QtWidgets.QMessageBox.warning(
                        self,
                        "URL Copied To Clipboard",
                        "URL:<br><br>%s<br><br>is copied to clipboard!" %
                        url,
                        QtWidgets.QMessageBox.Ok
                    )
                elif selected_item is copy_id_to_clipboard:
                    clipboard = QtWidgets.QApplication.clipboard()
                    clipboard.setText('%s' % entity.id)

                    # and warn the user about a new version is created and the
                    # clipboard is set to the new version full path
                    QtWidgets.QMessageBox.warning(
                        self,
                        "ID Copied To Clipboard",
                        "ID %s is copied to clipboard!" % entity.id,
                        QtWidgets.QMessageBox.Ok
                    )

                elif selected_item is create_time_log_action:
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

                elif selected_item is update_task_action:
                    from anima.ui import task_dialog
                    task_main_dialog = task_dialog.MainDialog(
                        parent=self,
                        task=entity
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

                elif selected_item == create_child_task_action:
                    from anima.ui import task_dialog
                    task_main_dialog = task_dialog.MainDialog(
                        parent=self,
                        parent_task=entity
                    )
                    task_main_dialog.exec_()
                    result = task_main_dialog.result()
                    task = task_main_dialog.task
                    task_main_dialog.deleteLater()

                    if result == accepted and task:
                        # reload the parent item
                        if item.parent:
                            item.parent.reload()
                        else:
                            self.fill()
                        self.find_and_select_entity_item(task)

                elif selected_item is duplicate_task_hierarchy_action:
                    duplicate_task_hierarchy_dialog = \
                        DuplicateTaskHierarchyDialog(
                            parent=self, duplicated_task_name=item.task.name
                        )
                    duplicate_task_hierarchy_dialog.exec_()

                    result = duplicate_task_hierarchy_dialog.result()
                    if result == accepted:
                        new_task_name = \
                            duplicate_task_hierarchy_dialog.line_edit.text()

                        keep_resources = \
                            duplicate_task_hierarchy_dialog\
                                .check_box.checkState()

                        from anima import utils
                        from stalker import Task
                        task = Task.query.get(item.task.id)
                        new_task = utils.duplicate_task_hierarchy(
                            task,
                            None,
                            new_task_name,
                            description='Duplicated from Task(%s)' % task.id,
                            user=logged_in_user,
                            keep_resources=keep_resources
                        )
                        if new_task:
                            from stalker.db.session import DBSession
                            DBSession.commit()
                            item.parent.reload()
                            self.find_and_select_entity_item(new_task)

                elif selected_item is delete_task_action:
                    answer = QtWidgets.QMessageBox.question(
                        self,
                        'Delete Task?',
                        "Delete the task and children?<br><br>(NO UNDO!!!!)",
                        QtWidgets.QMessageBox.Yes,
                        QtWidgets.QMessageBox.No
                    )
                    if answer == QtWidgets.QMessageBox.Yes:
                        from stalker.db.session import DBSession
                        from stalker import Task
                        task = Task.query.get(item.task.id)
                        DBSession.delete(task)
                        DBSession.commit()
                        # reload the parent
                        if item.parent:
                            item.parent.reload()
                        else:
                            self.fill()
                        self.find_and_select_entity_item(item.parent.task)

                elif selected_item == create_project_structure_action:
                    answer = QtWidgets.QMessageBox.question(
                        self,
                        'Create Project Folder Structure?',
                        "This will create project folders, OK?",
                        QtWidgets.QMessageBox.Yes,
                        QtWidgets.QMessageBox.No
                    )
                    if answer == QtWidgets.QMessageBox.Yes:
                        from anima import utils
                        try:
                            utils.create_project_structure(entity)
                        except Exception as e:
                            pass
                        finally:
                            QtWidgets.QMessageBox.information(
                                self,
                                'Project Folder Structure is created!',
                                'Project Folder Structure is created!',
                            )
                    else:
                        return

                elif selected_item == create_task_structure_action:
                    answer = QtWidgets.QMessageBox.question(
                        self,
                        'Create Folder Structure?',
                        "This will create task folders, OK?",
                        QtWidgets.QMessageBox.Yes,
                        QtWidgets.QMessageBox.No
                    )
                    if answer == QtWidgets.QMessageBox.Yes:
                        from anima import utils
                        try:
                            utils.create_task_structure(entity)
                        except Exception as e:
                            pass
                        finally:
                            QtWidgets.QMessageBox.information(
                                self,
                                'Folder Structure is created!',
                                'Folder Structure is created!',
                            )
                    else:
                        return

                elif selected_item == fix_task_status_action:
                    from stalker import Task
                    if isinstance(entity, Task):
                        from anima import utils
                        utils.fix_task_statuses(entity)

                        from stalker.db.session import DBSession
                        DBSession.add(entity)
                        DBSession.commit()

                        if item.parent:
                            item.parent.reload()

                elif selected_item == update_project_action:
                    from anima.ui import project_dialog
                    project_main_dialog = project_dialog.MainDialog(
                        parent=self,
                        project=entity
                    )
                    project_main_dialog.exec_()
                    result = project_main_dialog.result()

                    # refresh the task list
                    if result == accepted:
                        self.fill()

                        # reselect the same task
                        self.find_and_select_entity_item(entity)

                    project_main_dialog.deleteLater()

                elif selected_item == assign_users_action:
                    from anima.ui import project_users_dialog
                    project_users_main_dialog = \
                        project_users_dialog.MainDialog(
                            parent=self,
                            project=entity
                        )
                    project_users_main_dialog.exec_()
                    result = project_users_main_dialog.result()

                    project_users_main_dialog.deleteLater()

                elif selected_item in change_status_menu_actions:
                    # get the status code
                    status_code = selected_item.text()

                    from sqlalchemy import func
                    status = \
                        Status.query.filter(
                            func.lower(Status.code) == func.lower(status_code)
                        ).first()

                    # change the status of the entity
                    # if it is a leaf task
                    # if it doesn't have any dependent_of
                    # assert isinstance(entity, Task)
                    if isinstance(entity, Task):
                        if entity.is_leaf and not entity.dependent_of:
                            # then we can update it
                            entity.status = status

                            # # fix other task statuses
                            # from anima import utils
                            # utils.fix_task_statuses(entity)

                            # refresh the tree
                            from stalker.db.session import DBSession
                            DBSession.add(entity)
                            DBSession.commit()

                            if item.parent:
                                item.parent.reload()
                                self.find_and_select_entity_item(entity)
                else:
                    try:
                        # go to the dependencies
                        dep_task = selected_item.task
                        self.find_and_select_entity_item(
                            dep_task,
                            self
                        )
                    except AttributeError:
                        pass

    def find_and_select_entity_item(self, task, tree_view=None):
        """finds and selects the task in the given tree_view item
        """
        # import time
        # start = time.time()
        if not task:
            # print ('TaskTreeView.find_and_select_entity_item returned early '
            #        '(1) and took: %0.2f seconds' % (time.time() - start))
            return

        if not tree_view:
            tree_view = self

        item = self.load_task_item_hierarchy(task, tree_view)

        selection_model = self.selectionModel()
        if not item:
            selection_model.clearSelection()
            # print ('TaskTreeView.find_and_select_entity_item returned early '
            #        '(2) and took: %0.2f seconds' % (time.time() - start))
            return

        try:
            selection_model.select(
                item.index(),
                QtGui.QItemSelectionModel.ClearAndSelect
            )
        except AttributeError:  # Fix for Qt5
            selection_model.select(
                item.index(),
                QtCore.QItemSelectionModel.ClearAndSelect
            )

        self.setCurrentIndex(item.index())

        self.scrollTo(
            item.index(), QtWidgets.QAbstractItemView.PositionAtBottom
        )
        # print ('TaskTreeView.find_and_select_entity_item took: '
        #        '%0.2f seconds' % (time.time() - start))
        return item

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
            logger.debug('item for project: %s' % item)

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
                logger.debug('can not find item')

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
        logger.debug('items matching name : %s' % indexes)
        for index in indexes:
            item = model.itemFromIndex(index)
            if item:
                if item.task.id == entity.id:
                    return item
        return None

    @classmethod
    def get_item_indices_containing_text(cls, text, tree_view):
        """returns the indexes of the item indices containing the given text
        """
        model = tree_view.model()
        logger.debug('searching for text : %s' % text)
        return model.match(
            model.index(0, 0),
            0,
            text,
            -1,
            QtCore.Qt.MatchRecursive
        )

    def get_task_id(self):
        """returns the task from the UI, it is an task, asset, shot, sequence
        or project
        """
        task_id = None
        selection_model = self.selectionModel()
        logger.debug('selection_model: %s' % selection_model)

        indexes = selection_model.selectedIndexes()
        logger.debug('selected indexes : %s' % indexes)

        if indexes:
            current_index = indexes[0]
            logger.debug('current_index : %s' % current_index)

            item_model = self.model()
            current_item = item_model.itemFromIndex(current_index)

            if current_item:
                task_id = current_item.task.id

        logger.debug('task_id: %s' % task_id)
        return task_id
