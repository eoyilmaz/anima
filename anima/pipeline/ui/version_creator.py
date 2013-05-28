# -*- coding: utf-8 -*-
# Copyright (c) 2012-2013, Anima Istanbul
#
# This module is part of anima-tools and is released under the BSD 2
# License: http://www.opensource.org/licenses/BSD-2-Clause

import logging
import os
from sqlalchemy import distinct
from stalker.db import DBSession
from stalker.models.auth import LocalSession
from stalker.models.env import EnvironmentBase

import anima
from anima.pipeline.ui import (UICaller, AnimaDialogBase, IS_PYQT4, IS_PYSIDE,
                               QtGui, QtCore, ui_utils, login_dialog)

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


from stalker import db, defaults, Version


if IS_PYSIDE:
    from anima.pipeline.ui.ui_compiled import version_creator_UI_pyside as version_creator_UI
elif IS_PYQT4:
    from anima.pipeline.ui.ui_compiled import version_creator_UI_pyqt4 as version_creator_UI


def UI(environment=None, mode=0, app_in=None, executor=None):
    """
    :param environment: The
      :class:`~stalker.models.env.EnvironmentBase` can be None to let the UI to
      work in "environmentless" mode in which it only creates data in database
      and copies the resultant version file path to clipboard.
    
    :param mode: Runs the UI either in Read-Write (0) mode or in Read-Only (1)
      mode.

    :param app_in: A Qt Application instance, which you can pass to let the UI
      be attached to the given applications event process.
    
    :param executor: Instead of calling app.exec_ the UI will call this given
      function. It also passes the created app instance to this executor.
    
    """
    return UICaller(app_in, executor, MainDialog, environment=environment,
                    mode=mode)


class MainDialog(QtGui.QDialog, version_creator_UI.Ui_Dialog, AnimaDialogBase):
    """The main version creation dialog for the pipeline.
    
    This is the main interface that the users of the anima.pipeline will use
    to create a new :class:`~stalker.models.version.Version`\ s.
    
    It is possible to run the version_creator UI in read-only mode where the UI
    is created only for choosing previous versions. There will only be one
    button called "Choose" which returns the chosen Version instance.
    
    :param environment: It is an object which supplies **methods** like
      ``open``, ``save``, ``export``,  ``import`` or ``reference``. The most
      basic way to do this is to pass an instance of a class which is derived
      from the :class:`~stalker.models.env.EnvironmentBase` which has all this
      methods but produces ``NotImplementedError``\ s if the child class has
      not implemented these actions.
      
      The main duty of the Environment object is to introduce the host
      application (Maya, Houdini, Nuke, etc.) to the pipeline scripts and let
      it to open, save, export, import or reference a file.
      
    No Environment Interaction
    
      From and after version 0.2.5 the UI is now able to handle the situation
      of not being bounded to an Environment. So if there is no Environment
      instance is given then the UI generates new Version instance and will
      allow the user to "copy" the full path of the newly generated Version.
      So environments which are not able to run Python code (Photoshop etc.)
      will also be able to contribute to projects.
    
    :param parent: The parent ``PySide.QtCore.QObject`` of this interface. It
      is mainly useful if this interface is going to be attached to a parent
      UI, like the Maya or Nuke.
    
    :param mode: Sets the UI in to Read-Write (mode=0) and Read-Only (mode=1)
      mode. Where in Read-Write there are all the buttons you would normally
      have (Export As, Save As, Open, Reference, Import), and in Read-Only mode
      it has only one button called "Choose" which lets you choose one Version.
    """

    def __init__(self, environment=None, parent=None, mode=0):
        logger.debug("initializing the interface")

        super(MainDialog, self).__init__(parent)
        self.setupUi(self)

        self.mode = mode
        self.chosen_version = None

        window_title = 'Version Creator | ' + \
                       'Anima Pipeline v' + anima.__version__

        if environment:
            window_title += " | " + environment.name
        else:
            window_title += " | No Environment"

        if self.mode:
            window_title += " | Read-Only Mode"
        else:
            window_title += " | Normal Mode"

        # change the window title
        self.setWindowTitle(window_title)

        # setup the database
        if DBSession is None:
            db.setup()

        self.environment = environment

        # create the project attribute in projects_comboBox
        self.current_dialog = None
        self.previous_versions_tableWidget.versions = []

        # set previous_versions_tableWidget.labels
        self.previous_versions_tableWidget.labels = [
            "Version",
            "User",
            "Status",
            "File Size",
            "Date",
            "Note",
            #"Path"
        ]

        # setup signals
        self._setup_signals()

        # setup defaults
        self._set_defaults()

        # center window
        self.center_window()
        
        logger.debug("finished initializing the interface")

    def show(self):
        """overridden show method
        """
        logged_in_user = self.get_logged_in_user()
        return super(MainDialog, self).show()

    def _setup_signals(self):
        """sets up the signals
        """

        logger.debug("start setting up interface signals")

        # close button
        QtCore.QObject.connect(
            self.close_pushButton,
            QtCore.SIGNAL("clicked()"),
            self.close
        )

        #logout button
        QtCore.QObject.connect(
            self.logout_pushButton,
            QtCore.SIGNAL("clicked()"),
            self.logout
        )

        # projects_comboBox
        # QtCore.QObject.connect(
        #     self.projects_comboBox,
        #     QtCore.SIGNAL("currentIndexChanged(int)"),
        #     self.project_changed
        # )

        # tabWidget
        # QtCore.QObject.connect(
        #     self.tabWidget,
        #     QtCore.SIGNAL("currentChanged(int)"),
        #     self.tabWidget_changed
        # )

        # sequences_comboBox
        # QtCore.QObject.connect(
        #     self.sequences_comboBox,
        #     QtCore.SIGNAL("currentIndexChanged(int)"),
        #     self.sequences_comboBox_changed
        # )

        # assets_tableWidget
        # QtCore.QObject.connect(
        #     self.assets_tableWidget,
        #     QtCore.SIGNAL(
        #         'currentItemChanged(QTableWidgetItem*,QTableWidgetItem*)'
        #     ),
        #     self.asset_changed
        # )

        # shots_listWidget
        # QtCore.QObject.connect(
        #     self.shots_listWidget,
        #     QtCore.SIGNAL("currentTextChanged(QString)"),
        #     self.shot_changed
        # )

        #        # asset_description_edit_pushButton
        #        QtCore.QObject.connect(
        #            self.asset_description_edit_pushButton,
        #            QtCore.SIGNAL("clicked()"),
        #            self.asset_description_edit_pushButton_clicked
        #        )
        #        
        #        # shot_description_edit_pushButton
        #        QtCore.QObject.connect(
        #            self.shot_description_edit_pushButton,
        #            QtCore.SIGNAL("clicked()"),
        #            self.shot_description_edit_pushButton_clicked
        #        )

        # types_comboBox
        # QtCore.QObject.connect(
        #     self.version_types_listWidget,
        #     QtCore.SIGNAL("currentTextChanged(QString)"),
        #     self.version_types_listWidget_changed
        # )
        
        # tasks_listWidget
        QtCore.QObject.connect(
            self.tasks_treeWidget,
            QtCore.SIGNAL('currentItemChanged(QTreeWidgetItem *, QTreeWidgetItem *)'),
            self.tasks_treeWidget_changed
        )

        # take_comboBox
        QtCore.QObject.connect(
            self.takes_listWidget,
            QtCore.SIGNAL("currentTextChanged(QString)"),
            self.takes_listWidget_changed
        )

        # add_type_toolButton
        # QtCore.QObject.connect(
        #     self.add_type_toolButton,
        #     QtCore.SIGNAL("clicked()"),
        #     self.add_type_toolButton_clicked
        # )

        # custom context menu for the assets_tableWidget
        # self.assets_tableWidget.setContextMenuPolicy(
        #     QtCore.Qt.CustomContextMenu
        # )

        # QtCore.QObject.connect(
        #     self.assets_tableWidget,
        #     QtCore.SIGNAL("customContextMenuRequested(const QPoint&)"),
        #     self._show_assets_tableWidget_context_menu
        # )

        # custom context menu for the previous_versions_tableWidget
        self.previous_versions_tableWidget.setContextMenuPolicy(
            QtCore.Qt.CustomContextMenu
        )

        QtCore.QObject.connect(
            self.previous_versions_tableWidget,
            QtCore.SIGNAL("customContextMenuRequested(const QPoint&)"),
            self._show_previous_versions_tableWidget_context_menu
        )

        # create_asset_pushButton
        # QtCore.QObject.connect(
        #     self.create_asset_pushButton,
        #     QtCore.SIGNAL("clicked()"),
        #     self.create_asset_pushButton_clicked
        # )

        # add_take_toolButton
        QtCore.QObject.connect(
            self.add_take_toolButton,
            QtCore.SIGNAL("clicked()"),
            self.add_take_toolButton_clicked
        )

        # export_as
        QtCore.QObject.connect(
            self.export_as_pushButton,
            QtCore.SIGNAL("clicked()"),
            self.export_as_pushButton_clicked
        )

        # save_as
        QtCore.QObject.connect(
            self.save_as_pushButton,
            QtCore.SIGNAL("clicked()"),
            self.save_as_pushButton_clicked
        )

        # open
        QtCore.QObject.connect(
            self.open_pushButton,
            QtCore.SIGNAL("clicked()"),
            self.open_pushButton_clicked
        )

        # chose
        QtCore.QObject.connect(
            self.chose_pushButton,
            QtCore.SIGNAL("cliched()"),
            self.chose_pushButton_clicked
        )

        if self.mode:
            # Read-Only mode, Choose the version
            # add double clicking to previous_versions_tableWidget
            QtCore.QObject.connect(
                self.previous_versions_tableWidget,
                QtCore.SIGNAL("cellDoubleClicked(int,int)"),
                self.chose_pushButton_clicked
            )
        else:
            # Read-Write mode, Open the version
            # add double clicking to previous_versions_tableWidget
            QtCore.QObject.connect(
                self.previous_versions_tableWidget,
                QtCore.SIGNAL("cellDoubleClicked(int,int)"),
                self.open_pushButton_clicked
            )

        # reference
        QtCore.QObject.connect(
            self.reference_pushButton,
            QtCore.SIGNAL("clicked()"),
            self.reference_pushButton_clicked
        )

        # import
        QtCore.QObject.connect(
            self.import_pushButton,
            QtCore.SIGNAL("clicked()"),
            self.import_pushButton_clicked
        )

        # show_only_published_checkBox
        QtCore.QObject.connect(
            self.show_published_only_checkBox,
            QtCore.SIGNAL("stateChanged(int)"),
            self.update_previous_versions_tableWidget
        )

        # show_only_published_checkBox
        QtCore.QObject.connect(
            self.version_count_spinBox,
            QtCore.SIGNAL("valueChanged(int)"),
            self.update_previous_versions_tableWidget
        )

        # shot_info_update_pushButton 
        # QtCore.QObject.connect(
        #     self.shot_info_update_pushButton,
        #     QtCore.SIGNAL("clicked()"),
        #     self.shot_info_update_pushButton_clicked
        # )

        # upload_thumbnail_pushButton
        QtCore.QObject.connect(
            self.upload_thumbnail_pushButton,
            QtCore.SIGNAL("clicked()"),
            self.upload_thumbnail_pushButton_clicked
        )

        logger.debug("finished setting up interface signals")


    def get_logged_in_user(self):
        """returns the logged in user
        """
        local_session = LocalSession()
        logged_in_user = local_session.logged_in_user
        if not logged_in_user:
            dialog = login_dialog.MainDialog(parent=self)
            self.current_dialog = dialog
            dialog.exec_()
            if dialog.DialogCode: #Accepted (1) or Rejected (0)
                local_session = LocalSession()
                logged_in_user = local_session.logged_in_user
                self.current_dialog = None
            else:
                # recurse
                logged_in_user = self.get_logged_in_user()

        return logged_in_user

    def fill_logged_in_user(self):
        """fills the logged in user label
        """
        logged_in_user = self.get_logged_in_user()
        self.logged_in_user_label.setText(logged_in_user.name)

    def logout(self):
        """logouts the current user
        """
        lsession = LocalSession()
        lsession.delete()
        logged_in_user = self.get_logged_in_user()
        self.fill_logged_in_user()

    # def _show_assets_tableWidget_context_menu(self, position):
    #     """the custom context menu for the assets_tableWidget
    #     """
    # 
    #     if self.mode:
    #         # do not show in Read-Only mode
    #         return
    # 
    #     # convert the position to global screen position
    #     global_position = self.assets_tableWidget.mapToGlobal(position)
    # 
    #     # create the menu
    #     menu = QtGui.QMenu()
    #     menu.addAction("Rename Asset")
    # 
    #     selected_item = menu.exec_(global_position)
    # 
    #     if selected_item:
    #         # something is chosen
    #         if selected_item.text() == "Rename Asset":
    # 
    #             asset = self.get_task()
    # 
    #             # show a dialog
    #             self.current_dialog = QtGui.QInputDialog(self)
    #             new_asset_name, ok = self.current_dialog.getText(
    #                 self,
    #                 "Rename Asset",
    #                 "New Asset Name",
    #                 QtGui.QLineEdit.Normal,
    #                 asset.name
    #             )
    # 
    #             if ok:
    #                 # if it is not empty
    #                 if new_asset_name != "":
    #                     # get the asset from the list
    #                     asset.name = new_asset_name
    #                     asset.code = new_asset_name
    #                     asset.save()
    # 
    #                     # update assets_tableWidget
    #                     self.tabWidget_changed(0)

    def _show_previous_versions_tableWidget_context_menu(self, position):
        """the custom context menu for the pervious_versions_tableWidget
        """
        # convert the position to global screen position
        global_position = \
            self.previous_versions_tableWidget.mapToGlobal(position)

        item = self.previous_versions_tableWidget.itemAt(position)
        if not item:
            return

        index = item.row()
        version = self.previous_versions_tableWidget.versions[index]

        # create the menu
        menu = QtGui.QMenu()

        #if not version.is_published:
        #    previous_versions_tableWidget_menu.addAction("Publish")

        #previous_versions_tableWidget_menu.addSeparator()

        if not self.mode:
            # add statuses
            for status in conf.status_list_long_names:
                action = QtGui.QAction(status, menu)
                action.setCheckable(True)
                # set it checked if the status of the version is the current status
                if version.status == status:
                    action.setChecked(True)

                menu.addAction(action)

            # add separator
            menu.addSeparator()

        # add Browse Outputs
        menu.addAction("Browse Output Path...")
        menu.addSeparator()

        if not self.mode:
            menu.addAction("Change Note...")
            menu.addSeparator()

        menu.addAction("Copy Path")
        menu.addAction("Copy Output Path")

        selected_item = menu.exec_(global_position)

        if selected_item:
            #if selected_item.text() == "Publish":
            #    # publish the selected version
            #    if version:
            #        # publish it
            #        if not version.is_published:
            #            version.is_published = True
            #            version.save()
            #            # refresh the tableWidget
            #            self.update_previous_versions_tableWidget()
            #            return

            choice = selected_item.text()

            if choice in conf.status_list_long_names:
                # change the status of the version
                if version:
                    version.status = selected_item.text()
                    version.save()
                    # refresh the tableWidget
                    self.update_previous_versions_tableWidget()
                    return
            elif choice == 'Browse Output Path...':
                path = os.path.expandvars(version.output_path)
                try:
                    utils.open_browser_in_location(path)
                except IOError:
                    QtGui.QMessageBox.critical(
                        self,
                        "Error",
                        "Path doesn't exists:\n" + path
                    )
            elif choice == 'Change Note...':
                if version:
                    # change the note
                    self.current_dialog = QtGui.QInputDialog(self)

                    new_note, ok = self.current_dialog.getText(
                        self,
                        "Enter the new note",
                        "Please enter the new note:",
                        QtGui.QLineEdit.Normal,
                        version.note
                    )

                    if ok:
                        # change the note of the version
                        version.note = new_note
                        version.save()
                        # update the previous_versions_tableWidget
                        self.update_previous_versions_tableWidget()
            elif choice == 'Copy Path':
                # just set the clipboard to the version.full_path
                clipboard = QtGui.QApplication.clipboard()
                clipboard.setText(os.path.normpath(version.full_path))
            elif choice == 'Copy Output Path':
                # just set the clipboard to the version.output_path
                clipboard = QtGui.QApplication.clipboard()
                clipboard.setText(os.path.normpath(version.output_path))

    def rename_asset(self, asset, new_name):
        """Renames the asset with the given new name
        
        :param asset: The :class:`~oyProjectManager.models.asset.Asset` instance
          to be renamed.
        
        :param new_name: The desired new name for the asset.
        """
        pass

    def fill_tasks_treeWidget(self):
        """fills the tasks_treeWidget
        """
        # first clear it
        self.tasks_treeWidget.clear()
        
        # create column headers
        self.tasks_treeWidget.setColumnCount(2)
        self.tasks_treeWidget.setHeaderLabels(
            ['Name', 'Type']
        )
        
        # now get the tasks of the current user
        logged_in_user = self.get_logged_in_user()
        
        tasks = logged_in_user.tasks
        
        logger.setLevel(logging.DEBUG)
        logger.debug(tasks)
        
        # now first fill the projects
        projects = []
        for task in tasks:
            if task.project not in projects:
                projects.append(task.project)
        
        # add the projects
        root_items = []
        for project in projects:
            item = QtGui.QTreeWidgetItem(self.tasks_treeWidget)
            item.setText(0, project.name)
            item.setText(1, project.__class__.__name__)
            item.stalker_entity = project
            root_items.append(item)
        
        # now add the tasks
        for task in tasks:
            # create the item
            item = QtGui.QTreeWidgetItem()
            item.setText(0, task.name)
            item.setText(1, task.__class__.__name__)
            item.stalker_entity = task
            
            # now append it to the related project
            for project_item in root_items:
                if project_item.stalker_entity is task.project:
                    # append the item to that project
                    project_item.addChild(item)
                    break
        
        # congratulate your self
        logger.debug('all items are successfully added to tasks_treeWidget')
    
    def tasks_treeWidget_changed(self, from_item, to_item):
        """runs when the tasks_treeWidget item is changed
        """
        entity = from_item.stalker_entity
        # get the versions of the entity
        takes = []
        if entity:
            # clear the takes_listWidget and fill with new data
            self.takes_listWidget.clear()
            
            takes = map(
                lambda x: x[0],
                 DBSession.query(distinct(Version.take_name))
                    .filter(Version.version_of==entity)
                    .all()
            )
            
        logger.debug("len(takes) from db: %s" % len(takes))
        
        if len(takes) == 0:
            # append the default take
            logger.debug("appending the default take name")
            self.takes_listWidget.addItem(defaults.version_take_name)
        else:
            logger.debug("adding the takes from db")
            self.takes_listWidget.addItems(takes)
        
        logger.debug("setting the first element selected")
        item = self.takes_listWidget.item(0)
        self.takes_listWidget.setCurrentItem(item)


    def _set_defaults(self):
        """sets up the defaults for the interface
        """
        logger.debug("started setting up interface defaults")
        
        # check login
        self.fill_logged_in_user()

        # clear the thumbnail area
        self.clear_thumbnail()

        # fill the statuses_comboBox
        self.statuses_comboBox.clear()
        # self.statuses_comboBox.addItems(conf.status_list_long_names)

        # fill the tasks
        self.fill_tasks_treeWidget()

        # add "Main" by default to the takes_listWidget
        self.takes_listWidget.addItem(defaults.version_take_name)
        # select it
        item = self.takes_listWidget.item(0)
        self.takes_listWidget.setCurrentItem(item)

        # run the project changed item for the first time
        # self.project_changed()

        if self.environment and isinstance(self.environment, EnvironmentBase):
            logger.debug("restoring the ui with the version from environment")

            # get the last version from the environment
            version_from_env = self.environment.get_last_version()

            logger.debug("version_from_env: %s" % version_from_env)

            self.restore_ui(version_from_env)
        else:
            # hide some buttons
            self.export_as_pushButton.setVisible(False)
            #self.open_pushButton.setVisible(False)
            self.reference_pushButton.setVisible(False)
            self.import_pushButton.setVisible(False)

        if self.mode:
            # run in read-only mode
            # hide buttons
            # self.create_asset_pushButton.setVisible(False)
            # self.add_type_toolButton.setVisible(False)
            self.add_take_toolButton.setVisible(False)
            self.note_label.setVisible(False)
            self.note_textEdit.setVisible(False)
            self.status_label.setVisible(False)
            self.statuses_comboBox.setVisible(False)
            self.publish_checkBox.setVisible(False)
            self.update_paths_checkBox.setVisible(False)
            self.export_as_pushButton.setVisible(False)
            self.save_as_pushButton.setVisible(False)
            self.open_pushButton.setVisible(False)
            self.reference_pushButton.setVisible(False)
            self.import_pushButton.setVisible(False)
            self.upload_thumbnail_pushButton.setVisible(False)
            self.user_label.setVisible(False)
            # self.users_comboBox.setVisible(False)
            self.shot_info_update_pushButton.setVisible(False)
            self.frame_range_label.setVisible(False)
            self.handles_label.setVisible(False)
            self.start_frame_spinBox.setVisible(False)
            self.end_frame_spinBox.setVisible(False)
            self.handle_at_end_spinBox.setVisible(False)
            self.handle_at_start_spinBox.setVisible(False)
        else:
            self.chose_pushButton.setVisible(False)

        # update note field
        self.note_textEdit.setText('')

        logger.debug("finished setting up interface defaults")

    def restore_ui(self, version):
        """Restores the UI with the given Version instance
        
        :param version: :class:`~oyProjectManager.models.version.Version`
          instance
        """

        logger.debug("restoring ui with the given version: %s", version)

        # quit if version is None
        if version is None or not version.project.active:
            return

        # set the project
        index = self.projects_comboBox.findText(version.project.name)

        if index != -1:
            self.projects_comboBox.setCurrentIndex(index)
        else:
            return

        # set the versionable
        versionable = version.version_of

        # set the tab
        if isinstance(versionable, Asset):
            self.tabWidget.setCurrentIndex(0)

            # set the asset name
            items = self.assets_tableWidget.findItems(
                versionable.name,
                QtCore.Qt.MatchExactly
            )
            item = None
            if items:
                item = items[0]
            else:
                return

            logger.debug('*******************************')
            logger.debug('item: %s' % item)

            self.assets_tableWidget.setCurrentItem(item)

        else:
            self.tabWidget.setCurrentIndex(1)

            #the sequence
            index = self.sequences_comboBox.findText(versionable.sequence.name)

            if index != -1:
                self.sequences_comboBox.setCurrentIndex(index)
            else:
                return

            # the shot code
            items = self.shots_listWidget.findItems(
                versionable.code,
                QtCore.Qt.MatchExactly
            )
            item = None
            if items:
                item = items[0]
            else:
                return
            self.shots_listWidget.setCurrentItem(item)

        # version_type name
        type_name = version.type.name
        logger.debug('finding type with name: %s' % type_name)
        items = self.version_types_listWidget.findItems(
            type_name,
            QtCore.Qt.MatchExactly
        )

        if not items:
            logger.debug('no items found with: %s' % type_name)
            return

        self.version_types_listWidget.setCurrentItem(items[0])

        # take_name
        take_name = version.take_name
        logger.debug('finding take with name: %s' % take_name)
        items = self.takes_listWidget.findItems(
            take_name,
            QtCore.Qt.MatchExactly
        )
        self.takes_listWidget.setCurrentItem(items[0])

    def project_changed(self):
        """updates the assets list_widget and sequences_comboBox for the 
        """
        logger.debug("project_comboBox has changed in the UI")

        project = self.get_current_project()
        if project:
            # update the client info
            self.client_name_label.setText(
                project.client.name if project.client else "N/A"
            )

        # call tabWidget_changed with the current index
        curr_tab_index = self.tabWidget.currentIndex()

        self.tabWidget_changed(curr_tab_index)

    def tabWidget_changed(self, index):
        """called when the tab widget is changed
        """

        proj = self.get_current_project()

        # clear the thumbnail area
        self.clear_thumbnail()

        # clear previous_versions_tableWidget
        self.clear_previous_versions_tableWidget()

        # if assets is the current tab
        if index == 0:
            logger.debug("tabWidget index changed to asset")

            # TODO: don't update if the project is the same with the cached one

            # get all the assets of the project
            assets = Asset.query() \
                .filter(Asset.project == proj) \
                .order_by(Asset.type) \
                .order_by(Asset.name) \
                .all()

            # add the assets to the assets list
            self.assets_tableWidget.assets = assets

            # add their names to the list
            self.assets_tableWidget.clear()
            self.assets_tableWidget.setRowCount(len(assets))
            self.assets_tableWidget.setHorizontalHeaderLabels(
                self.assets_tableWidget.labels
            )

            for i, asset in enumerate(assets):
                # type
                item = QtGui.QTableWidgetItem(asset.type)
                # align to left and vertical center
                item.setTextAlignment(0x0001 | 0x0080)

                self.assets_tableWidget.setItem(i, 0, item)

                # name
                item = QtGui.QTableWidgetItem(asset.name)
                item.setTextAlignment(0x0001 | 0x0080)

                self.assets_tableWidget.setItem(i, 1, item)

            self.assets_tableWidget.resizeColumnsToContents()

            # set the list to the first asset
            table_item = self.assets_tableWidget.item(0, 0)

            if table_item is not None:
                self.assets_tableWidget.selectRow(0)

                # call asset update
                self.asset_changed()

            #                # enable the asset_description_edit_pushButton
            #                self.asset_description_edit_pushButton.setEnabled(True)
            else:
            #                # disable the asset_description_edit_pushButton
            #                self.asset_description_edit_pushButton.setEnabled(False)

                # clear the versions comboBox
                self.version_types_listWidget.clear()

                # set the take to default
                self.takes_listWidget.clear()
                self.takes_listWidget.addItem(conf.default_take_name)
                item = self.takes_listWidget.item(0)
                self.takes_listWidget.setCurrentItem(item)


        elif self.tabWidget.currentIndex() == 1:
            # TODO: don't update if the project is not changed from the last one

            logger.debug("tabWidget index changed to shots")

            # update the sequence comboBox
            seqs = Sequence.query().filter(Sequence.project == proj).all()

            self.sequences_comboBox.clear()
            self.sequences_comboBox.addItems([seq.name for seq in seqs])

            # attach the sequences to the sequences_comboBox
            self.sequences_comboBox.sequences = seqs

            if self.sequences_comboBox.count():
                self.sequences_comboBox.setCurrentIndex(0)
                self.sequences_comboBox_changed(0)
            else:
                # there is no sequence
                # clear the shots_listWidget
                self.shots_listWidget.clear()

                # clear the version comboBox
                self.version_types_listWidget.clear()

                # set the take to default
                self.takes_listWidget.clear()
                self.takes_listWidget.addItem(conf.default_take_name)
                item = self.takes_listWidget.item(0)
                self.takes_listWidget.setCurrentItem(item)

    def sequences_comboBox_changed(self, index):
        """called when the sequences_comboBox index has changed
        """
        logger.debug("sequences_comboBox changed")

        # get the cached sequence instance
        try:
            seq = self.sequences_comboBox.sequences[index]
        except IndexError:
            logger.debug("there is no sequences cached in sequence_comboBox")
            return

        # update the shots_listWidget
        shots = Shot.query().filter(Shot.sequence == seq).all()
        shots.sort(key=lambda x: utils.embedded_numbers(x.number))

        # add their names to the list
        self.shots_listWidget.clear()
        self.shots_listWidget.addItems([shot.code for shot in shots])

        # set the shots cache
        self.shots_listWidget.shots = shots

        # set the list to the first shot
        list_item = self.shots_listWidget.item(0)

        # clear the thumbnail area
        self.clear_thumbnail()

        if list_item is not None:
            self.shots_listWidget.setCurrentItem(list_item)

            # call shots update
        #            self.asset_changed(list_item.text())

        #            # enable the asset_description_edit_pushButton
        #            self.shot_description_edit_pushButton.setEnabled(True)
        #        else:
        #            self.shot_description_edit_pushButton.setEnabled(False)

    def asset_changed(self):
        """updates the asset related fields with the current asset information
        """

        proj = self.get_current_project()

        #asset = \
        #    Asset.query().\
        #    filter(Asset.project==proj).\
        #    filter_by(name=asset_name).\
        #    first()
        asset = self.get_task()

        if asset is None:
            return

        #        # set the description
        #        if asset.description is not None:
        #            self.asset_description_textEdit.setText(asset.description)
        #        else:
        #            self.asset_description_textEdit.setText("")

        # update the version data
        # Types
        # get all the types for this asset
        # available in this environment

        if self.environment is None:
            types = map(
                lambda x: x[0],
                db.query(distinct(VersionType.name))
                .join(Version)
                .filter(Version.version_of == asset)
                .all()
            )
        else:
            types = map(
                lambda x: x[0],
                db.query(distinct(VersionType.name))
                .join(VersionTypeEnvironments)
                .join(Version)
                .filter(
                    VersionTypeEnvironments.environment_name == self.environment.name)
                .filter(Version.version_of == asset)
                .all()
            )

        # add the types to the version types list
        self.version_types_listWidget.clear()
        self.version_types_listWidget.addItems(types)

        # select the first one
        item = self.version_types_listWidget.item(0)
        self.version_types_listWidget.setCurrentItem(item)

        # update thumbnail
        self.update_thumbnail()

    def get_current_shot(self):
        """returns the current selected shot in the interface
        """
        # get the shot from the index
        index = self.shots_listWidget.currentIndex().row()
        shot = self.shots_listWidget.shots[index]
        return shot

    def shot_changed(self, shot_name):
        """updates the shot related fields with the current shot information
        """

        proj = self.get_current_project()
        shot = self.get_current_shot()

        #        # set the description
        #        if shot.description is not None:
        #            self.shot_description_textEdit.setText(shot.description)
        #        else:
        #            self.shot_description_textEdit.setText("")

        # update the version data
        # frame info
        self.start_frame_spinBox.setValue(shot.start_frame)
        self.end_frame_spinBox.setValue(shot.end_frame)
        self.handle_at_start_spinBox.setValue(shot.handle_at_start)
        self.handle_at_end_spinBox.setValue(shot.handle_at_end)

        # Types
        # get all the types for this shot
        if self.environment is None:
            types = map(
                lambda x: x[0],
                db.query(distinct(VersionType.name)).
                join(Version).
                filter(Version.version_of == shot).
                all()
            )
        else:
            types = map(
                lambda x: x[0],
                db.query(distinct(VersionType.name))
                .join(VersionTypeEnvironments)
                .join(Version)
                .filter(
                    VersionTypeEnvironments.environment_name == self.environment.name)
                .filter(Version.version_of == shot)
                .all()
            )

        # clear previous versions tableWidget
        self.clear_previous_versions_tableWidget()

        # add the types to the version types list
        self.version_types_listWidget.clear()
        self.version_types_listWidget.addItems(types)

        # select the first one
        item = self.version_types_listWidget.item(0)
        self.version_types_listWidget.setCurrentItem(item)

        # update thumbnail
        self.update_thumbnail()

    def shot_info_update_pushButton_clicked(self):
        """runs when the shot_info_update_pushButton is clicked
        """

        shot = self.get_current_shot()

        # get the info
        start_frame = self.start_frame_spinBox.value()
        end_frame = self.end_frame_spinBox.value()
        handle_at_start = self.handle_at_start_spinBox.value()
        handle_at_end = self.handle_at_end_spinBox.value()

        # now update the shot
        shot.start_frame = start_frame
        shot.end_frame = end_frame
        shot.handle_at_start = handle_at_start
        shot.handle_at_end = handle_at_end

        shot.save()

    def version_types_listWidget_changed(self, index):
        """runs when the asset version types comboBox has changed
        """
        versionable = self.get_task()

        # version type name
        version_type_name = ""
        item = self.version_types_listWidget.currentItem()
        if item:
            version_type_name = item.text()

        self.takes_listWidget.clear()
        self.clear_previous_versions_tableWidget()

        if version_type_name != '':
            logger.debug("version_type_name: %s" % version_type_name)
        else:
            return

        # Takes
        # get all the takes of the current asset
        takes = map(
            lambda x: x[0],
            db.query(distinct(Version.take_name))
            .join(VersionType)
            .filter(VersionType.name == version_type_name)
            .filter(Version.version_of == versionable)
            .all()
        )

        logger.debug("len(takes) from db: %s" % len(takes))

        if len(takes) == 0:
            # append the default take
            logger.debug("appending the default take name")
            self.takes_listWidget.addItem(conf.default_take_name)
        else:
            logger.debug("adding the takes from db")
            self.takes_listWidget.addItems(takes)

        logger.debug("setting the first element selected")
        item = self.takes_listWidget.item(0)
        self.takes_listWidget.setCurrentItem(item)

    def takes_listWidget_changed(self, index):
        """runs when the takes_listWidget has changed
        """
        # update the previous_versions_tableWidget
        self.update_previous_versions_tableWidget()

        # update the statuses_comboBox
        task = self.get_task()

        # take name
        take_name = ""
        item = self.takes_listWidget.currentItem()
        if item:
            take_name = item.text()

        # query the Versions of this type and take
        query = Version.query\
            .filter(Version.version_of == task) \
            .filter(Version.take_name == take_name)

        version = query.order_by(Version.version_number.desc()).first()

        if version:
            self.set_status(version.status)

    def set_status(self, status):
        """sets the chosen status on statuses_comboBox
        """
        # TODO: add this part
        pass

    def clear_previous_versions_tableWidget(self):
        """clears the previous_versions_tableWidget properly
        """
        # clear the data
        self.previous_versions_tableWidget.clear()
        self.previous_versions_tableWidget.versions = []

        # reset the labels
        self.previous_versions_tableWidget.setHorizontalHeaderLabels(
            self.previous_versions_tableWidget.labels
        )

    def update_previous_versions_tableWidget(self):
        """updates the previous_versions_tableWidget
        """
        task = self.get_task()

        # version type name
        version_type_name = ''
        # item = self.version_types_listWidget.currentItem()
        # if item:
        #     version_type_name = item.text()

        self.clear_previous_versions_tableWidget()

        if version_type_name != '':
            logger.debug("version_type_name: %s" % version_type_name)
        else:
            # delete the versions cache
            self.previous_versions_tableWidget.versions = []
            return

        # take name
        take_name = ""
        item = self.takes_listWidget.currentItem()
        if item:
            take_name = item.text()

        if take_name != '':
            logger.debug("take_name: %s" % take_name)
        else:
            return

        # query the Versions of this type and take
        query = Version.query().join(VersionType) \
            .filter(VersionType.name == version_type_name) \
            .filter(Version.version_of == task) \
            .filter(Version.take_name == take_name)

        # get the published only
        if self.show_published_only_checkBox.isChecked():
            query = query.filter(Version.is_published == True)

        # show how many
        count = self.version_count_spinBox.value()

        versions = query.order_by(Version.version_number.desc()) \
            .limit(count).all()

        versions.reverse()

        # set the versions cache by adding them to the widget
        self.previous_versions_tableWidget.versions = versions

        self.previous_versions_tableWidget.setRowCount(len(versions))

        def set_font(item):
            """sets the font for the given item
            
            :param item: the a QTableWidgetItem
            """
            my_font = item.font()
            my_font.setBold(True)

            item.setFont(my_font)

            foreground = item.foreground()
            foreground.setColor(QtGui.QColor(0, 192, 0))
            item.setForeground(foreground)

        # update the previous versions list
        for i, vers in enumerate(versions):

            is_published = vers.is_published

            # ------------------------------------
            # version_number
            item = QtGui.QTableWidgetItem(str(vers.version_number))
            # align to center and vertical center
            item.setTextAlignment(0x0004 | 0x0080)

            if is_published:
                set_font(item)

            self.previous_versions_tableWidget.setItem(i, 0, item)
            # ------------------------------------

            # ------------------------------------
            # user.name
            item = QtGui.QTableWidgetItem(vers.created_by.name)
            # align to left and vertical center
            item.setTextAlignment(0x0001 | 0x0080)

            if is_published:
                set_font(item)

            self.previous_versions_tableWidget.setItem(i, 1, item)
            # ------------------------------------

            # ------------------------------------
            # status
            item = QtGui.QTableWidgetItem(vers.status)
            # align to left and vertical center
            item.setTextAlignment(0x0004 | 0x0080)

            #if is_published:
            #    set_font(item)

            # colorize the item
            index = conf.status_list.index(vers.status)
            bgcolor = conf.status_bg_colors[index]
            fgcolor = conf.status_fg_colors[index]

            bg = item.background()
            bg.setColor(QtGui.QColor(*bgcolor))
            item.setBackground(bg)

            fg = item.foreground()
            fg.setColor(QtGui.QColor(*fgcolor))

            try:
                item.setBackgroundColor(QtGui.QColor(*bgcolor))
            except AttributeError: # gives error with PySide
                pass

            self.previous_versions_tableWidget.setItem(i, 2, item)
            # ------------------------------------


            # ------------------------------------
            # filesize

            # get the file size
            #file_size_format = "%.2f MB"
            file_size = -1
            if os.path.exists(vers.full_path):
                file_size = float(
                    os.path.getsize(vers.full_path)) / 1024 / 1024

            item = QtGui.QTableWidgetItem(conf.file_size_format % file_size)
            # align to left and vertical center
            item.setTextAlignment(0x0001 | 0x0080)

            if is_published:
                set_font(item)

            self.previous_versions_tableWidget.setItem(i, 3, item)
            # ------------------------------------

            # ------------------------------------
            # date

            # get the file date
            file_date = datetime.datetime.today()
            if os.path.exists(vers.full_path):
                file_date = datetime.datetime.fromtimestamp(
                    os.path.getmtime(vers.full_path)
                )
            item = QtGui.QTableWidgetItem(
                file_date.strftime(conf.time_format)
            )

            # align to left and vertical center
            item.setTextAlignment(0x0001 | 0x0080)

            if is_published:
                set_font(item)

            self.previous_versions_tableWidget.setItem(i, 4, item)
            # ------------------------------------

            # ------------------------------------
            # note
            item = QtGui.QTableWidgetItem(vers.note)
            # align to left and vertical center
            item.setTextAlignment(0x0001 | 0x0080)

            if is_published:
                set_font(item)

            self.previous_versions_tableWidget.setItem(i, 5, item)
            # ------------------------------------

        # resize the first column
        self.previous_versions_tableWidget.resizeRowsToContents()
        self.previous_versions_tableWidget.resizeColumnsToContents()
        self.previous_versions_tableWidget.resizeRowsToContents()

    def create_asset_pushButton_clicked(self):
        """displays an input dialog and creates a new asset if everything is ok
        """

        dialog = create_asset_dialog.create_asset_dialog(parent=self)
        dialog.exec_()

        ok = dialog.ok
        asset_name = dialog.asset_name_lineEdit.text()
        asset_type_name = dialog.asset_types_comboBox.currentText()

        logger.debug('new asset_name: %s' % asset_name)
        logger.debug('new asset_type_name: %s' % asset_type_name)

        if not ok:
            return
        elif asset_name == "" or asset_type_name == "":
            error_message = "The given Asset.name or Asset.type is " \
                            "empty!!!\n\nNot creating any new asset!"

            QtGui.QMessageBox.critical(self, 'Error', error_message)
            return

        proj = self.get_current_project()

        try:
            new_asset = Asset(proj, asset_name, type=asset_type_name)
            new_asset.save()

            # recreate the project structure
            proj.create()

            # update the assets by calling project_changed
            self.project_changed()

        except (TypeError, ValueError, IntegrityError) as e:
            error_message = str(e)
            if isinstance(e, IntegrityError):
                # the transaction needs to be rollback
                db.session.rollback()
                error_message = "Asset.name or Asset.code is not unique"

            # pop up an Message Dialog to give the error message
            QtGui.QMessageBox.critical(self, "Error", error_message)

            return

    def get_task(self):
        """returns the task from the UI, it is an task, asset or a shot
        """
        task = None
        assert isinstance(self.tasks_treeWidget, QtGui.QTreeWidget)
        # self.tasks_treeWidget.

        logger.debug('task: %s' % task)
        return task

    def get_version_type(self):
        """returns the VersionType instance by looking at the UI elements. It
        will return the correct VersionType by looking at if it is an Asset or
        a Shot and picking the name of the VersionType from the comboBox
        
        :returns: :class:`~oyProjectManager.models.version.VersionType`
        """

        project = self.get_current_project()
        if project is None:
            return None

        # get the versionable type
        versionable = self.get_task()

        type_for = versionable.__class__.__name__

        # get the version type name
        version_type_name = ""
        item = self.version_types_listWidget.currentItem()
        if item:
            version_type_name = item.text()

        # get the version type instance
        return VersionType.query() \
            .filter(VersionType.type_for == type_for) \
            .filter(VersionType.name == version_type_name) \
            .first()

    # def get_current_project(self):
    #     """Returns the currently selected project instance in the
    #     projects_comboBox
    #     :return: :class:`~oyProjectManager.models.project.Project` instance
    #     """
    #     
    #     index = self.projects_comboBox.currentIndex()
    #     
    #     try:
    #         return self.projects_comboBox.projects[index]
    #     except IndexError:
    #         return None

    def add_type(self, version_type):
        """adds new types to the version_types_listWidget
        """

        if not isinstance(version_type, VersionType):
            raise TypeError(
                "please supply a oyProjectManager.models.version.VersionType "
                "for the type to be added to the version_types_listWidget"
            )

        # check if the given type is suitable for the current versionable
        versionable = self.get_task()

        if versionable.__class__.__name__ != version_type.type_for:
            raise TypeError("The given version_type is not suitable for %s"
                            % self.tabWidget.tabText(
                self.tabWidget.currentIndex()
            ))

        items = self.version_types_listWidget.findItems(
            version_type.name,
            QtCore.Qt.MatchExactly
        )

        if not len(items):
            self.version_types_listWidget.addItem(version_type.name)

            # select the last added type
            index = self.version_types_listWidget.count() - 1
            item = self.version_types_listWidget.item(index)
            self.version_types_listWidget.setCurrentItem(item)

    def add_type_toolButton_clicked(self):
        """adds a new type for the currently selected Asset or Shot
        """
        proj = self.get_current_project()

        # get the versionable
        versionable = self.get_task()

        # get all the version types which doesn't have any version defined

        # get all the current types from the interface
        current_types = []
        for index in range(self.version_types_listWidget.count()):
            current_types.append(
                self.version_types_listWidget.item(index).text()
            )

        # available types for Versionable in this environment
        # if there is an environment given
        if self.environment:
            available_types = map(
                lambda x: x[0],
                db.query(distinct(VersionType.name))
                .join(VersionTypeEnvironments)
                .filter(VersionType.type_for == versionable.__class__.__name__)
                .filter(
                    VersionTypeEnvironments.environment_name == self.environment.name)
                .filter(~ VersionType.name.in_(current_types))
                .all()
            )
        else:
            # there is no environment
            # just return all VersionType names
            # TODO: create test for that case
            available_types = map(
                lambda x: x[0],
                db.query(distinct(VersionType.name))
                .filter(VersionType.type_for == versionable.__class__.__name__)
                .filter(~ VersionType.name.in_(current_types))
                .all()
            )


        # create a QInputDialog with comboBox
        self.current_dialog = QtGui.QInputDialog(self)

        if self.environment:
            type_name, ok = self.current_dialog.getItem(
                self,
                "Choose a VersionType",
                "Available Version Types for %ss in %s" %
                (versionable.__class__.__name__, self.environment.name),
                available_types,
                0,
                False
            )
        else:
            type_name, ok = self.current_dialog.getItem(
                self,
                "Choose a VersionType",
                "Available Version Types for %ss" %
                versionable.__class__.__name__,
                available_types,
                0,
                False
            )

            # if ok add the type name to the end of the types_comboBox and make
            # it the current selection
        if ok:
            # get the type
            vers_type = VersionType.query().filter_by(name=type_name).first()

            try:
                self.add_type(vers_type)
            except TypeError:
                # the given type doesn't exists
                # just return without doing anything
                return

    def add_take_toolButton_clicked(self):
        """runs when the add_take_toolButton clicked
        """

        # open up a QInputDialog and ask for a take name
        # anything is acceptable
        # because the validation will occur in the Version instance

        self.current_dialog = QtGui.QInputDialog(self)

        current_take_name = self.takes_listWidget.currentItem().text()

        take_name, ok = self.current_dialog.getText(
            self,
            "Add Take Name",
            "New Take Name",
            QtGui.QLineEdit.Normal,
            current_take_name
        )

        if ok:
            # add the given text to the takes_listWidget
            # if it is not empty
            if take_name != "":
                # TODO: there are no tests for take_name conditioning
                # if the given take name is in the list don't add it
                take_name = take_name.title()
                # replace spaces with underscores
                take_name = re.sub(r'[\s\-]+', '_', take_name)
                take_name = re.sub(r'[^a-zA-Z0-9_]+', '', take_name)
                take_name = re.sub(r'[_]+', '_', take_name)
                take_name = re.sub(r'[_]+$', '', take_name)
                in_list = False
                for i in range(self.takes_listWidget.count()):
                    item = self.takes_listWidget.item(i)
                    if item.text() == take_name:
                        in_list = True
                if not in_list:
                    self.takes_listWidget.addItem(take_name)
                    # sort the list
                    self.takes_listWidget.sortItems()
                    items = self.takes_listWidget.findItems(
                        take_name,
                        QtCore.Qt.MatchExactly
                    )
                    if items:
                        item = items[0]
                        # set the take to the new one
                        self.takes_listWidget.setCurrentItem(item)

    def get_new_version(self):
        """returns a :class:`~oyProjectManager.models.version.Version` instance
        from the UI by looking at the input fields
        
        :returns: :class:`~oyProjectManager.models.version.Version` instance
        """

        # create a new version
        versionable = self.get_task()
        version_type = self.get_version_type()
        take_name = self.takes_listWidget.currentItem().text()
        user = self.get_user()

        note = self.note_textEdit.toPlainText()

        published = self.publish_checkBox.isChecked()

        status = self.statuses_comboBox.currentText()

        version = Version(
            versionable,
            versionable.code,
            version_type,
            user,
            take_name=take_name,
            note=note,
            is_published=published,
            status=status
        )

        return version

    def get_previous_version(self):
        """returns the :class:`~oyProjectManager.models.version.Version`
        instance from the UI by looking at the previous_versions_tableWidget
        """

        index = self.previous_versions_tableWidget.currentRow()

        try:
            version = self.previous_versions_tableWidget.versions[index]
            return version
        except IndexError:
            return None

    def get_user(self):
        """returns the current User instance from the interface by looking at
        the name of the user from the users comboBox
        
        :return: :class:`~oyProjectManager.models.auth.User` instance
        """

        index = self.users_comboBox.currentIndex()
        return self.users_comboBox.users[index]

    def export_as_pushButton_clicked(self):
        """runs when the export_as_pushButton clicked
        """

        logger.debug("exporting the data as a new version")

        # get the new version
        new_version = self.get_new_version()

        # call the environments export_as method
        if self.environment is not None:
            self.environment.export_as(new_version)

            # inform the user about what happened
            if logger.level != logging.DEBUG:
                QtGui.QMessageBox.information(
                    self,
                    "Export",
                    new_version.filename + "\n\n has been exported correctly!",
                    QtGui.QMessageBox.Ok
                )

    def save_as_pushButton_clicked(self):
        """runs when the save_as_pushButton clicked
        """

        logger.debug("saving the data as a new version")

        # get the new version
        try:
            new_version = self.get_new_version()
        except (TypeError, ValueError) as e:
            # pop up an Message Dialog to give the error message
            QtGui.QMessageBox.critical(self, "Error", e)
            return None

        # call the environments save_as method
        if self.environment and isinstance(self.environment, EnvironmentBase):
            try:
                self.environment.save_as(new_version)
            except RuntimeError as e:
                QtGui.QMessageBox.critical(self, 'Error', str(e))
                return None
        else:
            logger.debug('No environment given, just generating paths')

            # just set the clipboard to the new_version.full_path
            clipboard = QtGui.QApplication.clipboard()
            v_path = os.path.normpath(new_version.full_path)
            clipboard.setText(v_path)

            # create the path
            try:
                logger.debug('creating path for new version')
                os.makedirs(new_version.path)
            except OSError: # path already exists
                pass

            # create the output path
            try:
                logger.debug('creating output_path for new version')
                os.makedirs(new_version.output_path)
            except OSError: # path already exists
                pass

            # and warn the user about a new version is created and the
            # clipboard is set to the new version full path
            QtGui.QMessageBox.warning(
                self,
                "Path Generated",
                "A new Version is created at:\n\n" + v_path + "\n\n" +
                "And the path is copied to your clipboard!!!",
                QtGui.QMessageBox.Ok
            )

        # save the new version to the database
        db.session.add(new_version)
        db.session.commit()

        # save the last user
        conf.last_user_id = new_version.created_by.id

        if self.environment:
            # close the UI
            self.close()
        else:
            # refresh the UI
            self.project_changed()

    def chose_pushButton_clicked(self):
        """runs when the chose_pushButton clicked
        """
        self.chosen_version = self.get_previous_version()
        if self.chosen_version:
            logger.debug(self.chosen_version)
            self.close()

    def open_pushButton_clicked(self):
        """runs when the open_pushButton clicked
        """
        # get the new version
        old_version = self.get_previous_version()

        logger.debug("opening version %s" % old_version)

        # call the environments open_ method
        if self.environment is not None:
            to_update_list = []
            # environment can throw RuntimeError for unsaved changes
            try:
                envStatus, to_update_list = \
                    self.environment.open_(old_version)
            except RuntimeError as e:
                # pop a dialog and ask if the user really wants to open the
                # file

                answer = QtGui.QMessageBox.question(
                    self,
                    'RuntimeError',
                    "There are <b>unsaved changes</b> in the current "
                    "scene<br><br>Do you really want to open the file?",
                    QtGui.QMessageBox.Yes,
                    QtGui.QMessageBox.No
                )

                envStatus = False

                if answer == QtGui.QMessageBox.Yes:
                    envStatus, to_update_list = \
                        self.environment.open_(old_version, True)
                else:
                    # no, just return
                    return

            # check the to_update_list to update old versions
            if len(to_update_list):
                # invoke the assetUpdater for this scene
                version_updater_mainDialog = \
                    version_updater.MainDialog(self.environment, self)

                version_updater_mainDialog.exec_()

            self.environment.post_open(old_version)

        # close the dialog
        self.close()

    def reference_pushButton_clicked(self):
        """runs when the reference_pushButton clicked
        """

        # get the new version
        previous_version = self.get_previous_version()

        # allow only published versions to be referenced
        if not previous_version.is_published:
            QtGui.QMessageBox.critical(
                self,
                "Critical Error",
                "Referencing <b>un-published versions</b> are not allowed!\n"
                "Please reference a published version of the same Asset/Shot",
                QtGui.QMessageBox.Ok
            )
            return

        logger.debug("referencing version %s" % previous_version)

        # call the environments reference method
        if self.environment is not None:
            self.environment.reference(previous_version)

            # inform the user about what happened
            if logger.level != logging.DEBUG:
                QtGui.QMessageBox.information(
                    self,
                    "Reference",
                    previous_version.filename + \
                    "\n\n has been referenced correctly!",
                    QtGui.QMessageBox.Ok
                )

    def import_pushButton_clicked(self):
        """runs when the import_pushButton clicked
        """

        # get the previous version
        previous_version = self.get_previous_version()

        logger.debug("importing version %s" % previous_version)

        # call the environments import_ method
        if self.environment is not None:
            self.environment.import_(previous_version)

            # inform the user about what happened
            if logger.level != logging.DEBUG:
                QtGui.QMessageBox.information(
                    self,
                    "Import",
                    previous_version.filename + \
                    "\n\n has been imported correctly!",
                    QtGui.QMessageBox.Ok
                )

    def clear_thumbnail(self):
        """clears the thumbnail_graphicsView
        """
        ui_utils.clear_thumbnail(self.thumbnail_graphicsView)

    def update_thumbnail(self):
        """updates the thumbnail for the selected versionable
        """

        # get the current versionable
        versionable = self.get_task()
        ui_utils.update_gview_with_version_thumbnail(
            versionable,
            self.thumbnail_graphicsView
        )

    def upload_thumbnail_pushButton_clicked(self):
        """runs when the upload_thumbnail_pushButton is clicked
        """

        thumbnail_full_path = ui_utils.choose_thumbnail(self)

        # if the tumbnail_full_path is empty do not do anything
        if thumbnail_full_path == "":
            return

        # get the current versionable
        versionable = self.get_task()

        ui_utils.upload_thumbnail(versionable, thumbnail_full_path)

        # update the thumbnail
        self.update_thumbnail()
    
