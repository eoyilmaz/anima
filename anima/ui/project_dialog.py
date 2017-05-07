# -*- coding: utf-8 -*-
# Copyright (c) 2012-2015, Anima Istanbul
#
# This module is part of anima-tools and is released under the BSD 2
# License: http://www.opensource.org/licenses/BSD-2-Clause
import re

from anima import logger
from anima.ui.base import AnimaDialogBase, ui_caller
from anima.ui import IS_PYSIDE, IS_PYSIDE2, IS_PYQT4
from anima.ui.lib import QtCore, QtWidgets, QtGui


if IS_PYSIDE():
    from anima.ui.ui_compiled import project_dialog_UI_pyside as project_dialog_UI
elif IS_PYSIDE2():
    from anima.ui.ui_compiled import project_dialog_UI_pyside2 as project_dialog_UI
elif IS_PYQT4():
    from anima.ui.ui_compiled import project_dialog_UI_pyqt4 as project_dialog_UI


def UI(app_in=None, executor=None, **kwargs):
    """
    :param app_in: A Qt Application instance, which you can pass to let the UI
      be attached to the given applications event process.

    :param executor: Instead of calling app.exec_ the UI will call this given
      function. It also passes the created app instance to this executor.

    """
    return ui_caller(app_in, executor, MainDialog, **kwargs)


class MainDialog(QtWidgets.QDialog, project_dialog_UI.Ui_Dialog, AnimaDialogBase):
    """The Project Dialog
    """

    def __init__(self, parent=None, project=None):
        logger.debug("initializing the interface")
        super(MainDialog, self).__init__(parent)
        self.setupUi(self)

        # store the logged in user
        self.logged_in_user = None

        self.project = project

        self.mode = 'Create'
        if self.project:
            self.mode = 'Update'

        self.dialog_label.setText('%s Project' % self.mode)

        from anima.ui.models import ValidatedLineEdit
        # add name_lineEdit
        self.name_lineEdit = ValidatedLineEdit(
            message_field=self.name_validator_label
        )
        self.name_fields_verticalLayout.insertWidget(
            0, self.name_lineEdit
        )

        # add code_lineEdit
        self.code_lineEdit = ValidatedLineEdit(
            message_field=self.code_validator_label
        )
        self.code_fields_verticalLayout.insertWidget(
            0, self.code_lineEdit
        )

        self._setup_signals()

        self._set_defaults()

        if self.project:
            self.fill_ui_with_project(self.project)

    def show(self):
        """overridden show method
        """
        logger.debug('MainDialog.show is started')
        self.logged_in_user = self.get_logged_in_user()
        if not self.logged_in_user:
            self.reject()
            return_val = None
        else:
            return_val = super(MainDialog, self).show()

        logger.debug('MainDialog.show is finished')
        return return_val

    def _setup_signals(self):
        """creates the signals
        """
        # name_lineEdit is changed
        QtCore.QObject.connect(
            self.name_lineEdit,
            QtCore.SIGNAL('textChanged(QString)'),
            self.name_line_edit_changed
        )

        # code_lineEdit is changed
        QtCore.QObject.connect(
            self.code_lineEdit,
            QtCore.SIGNAL('textChanged(QString)'),
            self.code_line_edit_changed
        )

    def _set_defaults(self):
        """setup the default values
        """
        # set size policies
        # self.name_lineEdit

        self.type_comboBox.setSizePolicy(
            QtWidgets.QSizePolicy.Expanding,
            QtWidgets.QSizePolicy.Fixed
        )

        self.status_comboBox.setSizePolicy(
            QtWidgets.QSizePolicy.Expanding,
            QtWidgets.QSizePolicy.Fixed
        )

        self.client_comboBox.setSizePolicy(
            QtWidgets.QSizePolicy.Expanding,
            QtWidgets.QSizePolicy.Fixed
        )

        self.agency_comboBox.setSizePolicy(
            QtWidgets.QSizePolicy.Expanding,
            QtWidgets.QSizePolicy.Fixed
        )

        self.production_company_comboBox.setSizePolicy(
            QtWidgets.QSizePolicy.Expanding,
            QtWidgets.QSizePolicy.Fixed
        )

        # invalidate the name and code fields by default
        self.name_lineEdit.set_invalid('Enter a name')
        self.code_lineEdit.set_invalid('Enter a code')

        # update type field
        from stalker import db, Type
        project_types = \
            db.DBSession.query(Type.id, Type.name)\
                .filter(Type.target_entity_type == 'Project')\
                .order_by(Type.name)\
                .all()

        self.type_comboBox.clear()
        self.type_comboBox.addItem('', -1)
        for type_id, type_name in project_types:
            self.type_comboBox.addItem(type_name, type_id)

        # fill the image format field
        from stalker import ImageFormat
        all_image_formats = db.DBSession\
            .query(ImageFormat.id, ImageFormat.name, ImageFormat.width, ImageFormat.height)\
            .order_by(ImageFormat.name)\
            .all()

        self.image_format_comboBox.clear()
        for imf_id, imf_name, imf_width, imf_height in all_image_formats:
            imf_text = '%s (%s x %s)' % (imf_name, imf_width, imf_height)
            self.image_format_comboBox.addItem(imf_text, imf_id)

        # fill the repository field
        from stalker import Repository
        all_repos = db.DBSession\
            .query(Repository.id, Repository.name)\
            .order_by(Repository.name)\
            .all()
        for repo_id, repo_name in all_repos:
            self.repository_comboBox.addItem(repo_name, repo_id)

        # fill the structure field
        from stalker import Structure
        all_structures = db.DBSession\
            .query(Structure.id, Structure.name).order_by(Structure.name).all()

        for st_id, st_name in all_structures:
            self.structure_comboBox.addItem(st_name, st_id)

        # fill status field
        sql = """select
        "SimpleEntities".id,
        "SimpleEntities".name
    from "Statuses"
    join "SimpleEntities" on "Statuses".id = "SimpleEntities".id
    join "StatusList_Statuses" on "Statuses".id = "StatusList_Statuses".status_id
    join "StatusLists" on "StatusLists".id = "StatusList_Statuses".status_list_id
    where "StatusLists".target_entity_type = 'Project'"""

        all_project_statuses = \
            db.DBSession.connection().execute(sql).fetchall()

        for st_id, st_name in all_project_statuses:
            self.status_comboBox.addItem(st_name, st_id)

    def name_line_edit_changed(self, text):
        """runs when the name_lineEdit text has changed
        """
        if re.findall(r'[^a-zA-Z0-9\-_ ]+', text):
            self.name_lineEdit.set_invalid('Invalid character')
        else:
            if text == '':
                self.name_lineEdit.set_invalid('Enter a name')
            else:
                self.name_lineEdit.set_valid()

        # update code field also
        formatted_text = re.sub(r'[^A-Z0-9_]+', '', text)
        self.code_lineEdit.setText(formatted_text)

    def code_line_edit_changed(self, text):
        """runs when the code_lineEdit text has changed
        """
        if re.findall(r'[^a-zA-Z0-9_]+', text):
            self.code_lineEdit.set_invalid('Invalid character')
        else:
            if text == '':
                self.code_lineEdit.set_invalid('Enter a code')
            else:
                self.code_lineEdit.set_valid()

    def fill_ui_with_project(self, project):
        """fills the UI fields with the given project

        :param project: A Stalker Project instance
        :return:
        """
        if not project:
            return
        self.project = project

        self.name_lineEdit.setText(project.name)
        self.name_lineEdit.set_valid()
        self.code_lineEdit.setText(project.code)
        self.code_lineEdit.set_valid()

        if project.type:
            index = self.type_comboBox.findData(project.type.id)
            if index:
                self.type_comboBox.setCurrentIndex(index)

        if project.image_format:
            index = self.image_format_comboBox.findData(
                project.image_format.id
            )
            if index:
                self.image_format_comboBox.setCurrentIndex(index)

        self.fps_spinBox.setValue(project.fps)

        if project.repository:
            # TODO: allow multiple repositories
            index = self.repository_comboBox.findText(
                project.repository.name,
                QtCore.Qt.MatchExactly
            )
            if index:
                self.repository_comboBox.setCurrentIndex(index)

        if project.structure:
            index = self.structure_comboBox.findText(
                project.structure.name,
                QtCore.Qt.MatchExactly
            )
            if index:
                self.repository_comboBox.setCurrentIndex(index)

        if project.status:
            index = self.status_comboBox.findText(
                project.status.name,
                QtCore.Qt.MatchExactly
            )
            if index:
                self.status_comboBox.setCurrentIndex(index)

    def accept(self):
        """create/update the project
        """
        # Name
        if not self.name_lineEdit.is_valid:
            QtWidgets.QMessageBox.critical(
                self,
                'Error',
                'Please fix <b>name</b> field!'
            )
            return
        name = self.name_lineEdit.text()

        # Code
        if not self.code_lineEdit.is_valid:
            QtWidgets.QMessageBox.critical(
                self,
                'Error',
                'Please fix <b>code</b> field!'
            )
            return
        code = self.code_lineEdit.text()

        # Type
        from stalker import Type
        index = self.type_comboBox.currentIndex()
        type_id = self.type_comboBox.itemData(index)
        type = Type.query.get(type_id) # None type is ok

        # Image Format
        from stalker import ImageFormat
        index = self.image_format_comboBox.currentIndex()
        image_format_id = self.image_format_comboBox.itemData(index)
        image_format = ImageFormat.query.get(image_format_id)
        if not image_format:
            QtWidgets.QMessageBox.critical(
                self,
                'Error',
                'Please select an valid <b>Image Format</b>!'
            )
            return

        # FPS
        fps = self.fps_spinBox.value()

        # Repository
        from stalker import Repository
        index = self.repository_comboBox.currentIndex()
        repo_id = self.repository_comboBox.itemData(index)
        repo = Repository.query.get(repo_id)
        if not repo:
            QtWidgets.QMessageBox.critical(
                self,
                'Error',
                'Please select an valid <b>Repository</b>!'
            )
            return

        # Structure
        from stalker import Structure
        index = self.structure_comboBox.currentIndex()
        structure_id = self.structure_comboBox.itemData(index)
        structure = Structure.query.get(structure_id)
        if not structure:
            QtWidgets.QMessageBox.critical(
                self,
                'Error',
                'Please select an valid <b>Structure</b>!'
            )
            return

        # Status
        from stalker import Status
        index = self.status_comboBox.currentIndex()
        status_id = self.status_comboBox.itemData(index)
        status = Status.query.get(status_id)
        if not status:
            QtWidgets.QMessageBox.critical(
                self,
                'Error',
                'Please select an valid <b>Status</b>!'
            )
            return

        # TODO: Add Client Data fields (which I don't care for now)
        logged_in_user = self.get_logged_in_user()

        # create or update project
        from stalker import db
        if self.mode == 'Create':
            # create a new project
            from stalker import Project
            new_project = Project(
                name=name,
                code=code,
                repositories=[repo],
                structure=structure,
                image_format=image_format,
                fps=fps,
                created_by=logged_in_user
            )
            db.DBSession.add(new_project)
            try:
                db.DBSession.commit()
            except Exception as e:
                db.DBSession.rollback()
                QtWidgets.QMessageBox.critical(
                    self,
                    'Error',
                    str(e)
                )
                return

        else:
            # update the project
            self.project.updated_by = logged_in_user
            self.project.name = name
            self.project.code = code
            self.project.repositories = [repo]
            self.project.structure = structure
            self.project.image_format = image_format
            self.project.fps = fps
            db.DBSession.add(self.project)
            try:
                db.DBSession.commit()
            except Exception as e:
                db.DBSession.rollback()
                QtWidgets.QMessageBox.critical(
                    self,
                    'Error',
                    str(e)
                )
                return

        super(MainDialog, self).accept()
