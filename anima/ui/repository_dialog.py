# -*- coding: utf-8 -*-
# Copyright (c) 2012-2018, Anima Istanbul
#
# This module is part of anima-tools and is released under the BSD 2
# License: http://www.opensource.org/licenses/BSD-2-Clause
import re

from anima import logger
from anima.ui.base import AnimaDialogBase, ui_caller
from anima.ui import IS_PYSIDE, IS_PYSIDE2, IS_PYQT4
from anima.ui.lib import QtCore, QtWidgets, QtGui


if IS_PYSIDE():
    from anima.ui.ui_compiled import repository_dialog_UI_pyside \
        as repository_dialog_UI
elif IS_PYSIDE2():
    from anima.ui.ui_compiled import repository_dialog_UI_pyside2 \
        as repository_dialog_UI
elif IS_PYQT4():
    from anima.ui.ui_compiled import repository_dialog_UI_pyqt4 \
        as repository_dialog_UI


def UI(app_in=None, executor=None, **kwargs):
    """
    :param app_in: A Qt Application instance, which you can pass to let the UI
      be attached to the given applications event process.

    :param executor: Instead of calling app.exec_ the UI will call this given
      function. It also passes the created app instance to this executor.

    """
    return ui_caller(app_in, executor, MainDialog, **kwargs)


class MainDialog(QtWidgets.QDialog, repository_dialog_UI.Ui_Dialog, AnimaDialogBase):
    """The Repository Dialog
    """

    def __init__(self, parent=None, repository=None):
        super(MainDialog, self).__init__(parent=parent)
        self.setupUi(self)

        self.repository = repository
        self.mode = 'Create'

        if self.repository:
            self.mode = 'Update'

        self.dialog_label.setText('%s Repository' % self.mode)

        # create name_lineEdit
        from anima.ui.widgets import ValidatedLineEdit
        self.name_lineEdit = ValidatedLineEdit(
            message_field=self.name_validator_label
        )
        self.name_lineEdit.setPlaceholderText('Enter Name')
        self.name_fields_verticalLayout.insertWidget(
            0, self.name_lineEdit
        )

        self._setup_signals()

        self._set_defaults()

        if self.repository:
            self.fill_ui_with_repository(self.repository)

    def _setup_signals(self):
        """create the signals
        """
        # name_lineEdit is changed
        QtCore.QObject.connect(
            self.name_lineEdit,
            QtCore.SIGNAL('textChanged(QString)'),
            self.name_line_edit_changed
        )

    def _set_defaults(self):
        """sets the default values
        """
        pass

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

    def fill_ui_with_repository(self, repository):
        """fills the UI with the given repository

        :param repository: A Stalker ImageFormat instance
        :return:
        """
        if False:
            from stalker import Repository
            assert isinstance(repository, Repository)

        self.repository = repository
        self.name_lineEdit.setText(self.repository.name)
        self.name_lineEdit.set_valid()

        self.windows_path_lineEdit.setText(self.repository.windows_path)
        self.linux_path_lineEdit.setText(self.repository.linux_path)
        self.osx_path_lineEdit.setText(self.repository.osx_path)

    def accept(self):
        """overridden accept method
        """
        if not self.name_lineEdit.is_valid:
            QtWidgets.QMessageBox.critical(
                self,
                'Error',
                'Please fix <b>name</b> field!'
            )
            return
        name = self.name_lineEdit.text()

        windows_path = self.windows_path_lineEdit.text()
        linux_path = self.linux_path_lineEdit.text()
        osx_path = self.osx_path_lineEdit.text()

        from stalker import Repository
        from stalker.db.session import DBSession
        logged_in_user = self.get_logged_in_user()
        if self.mode == 'Create':
            # Create a new Repository
            try:
                repo = Repository(
                    name=name,
                    windows_path=windows_path,
                    linux_path=linux_path,
                    osx_path=osx_path
                )
                self.repository = repo
                DBSession.add(repo)
                DBSession.commit()
            except Exception as e:
                DBSession.rollback()
                QtWidgets.QMessageBox.critical(
                    self,
                    'Error',
                    str(e)
                )
                return

        elif self.mode == 'Update':
            # Update the repository
            try:
                self.repository.name = name
                self.repository.windows_path = windows_path
                self.repository.linux_path = linux_path
                self.repository.osx_path = osx_path
                self.repository.updated_by = logged_in_user
                DBSession.add(self.repository)
                DBSession.commit()
            except Exception as e:
                DBSession.rollback()
                QtWidgets.QMessageBox.critical(
                    self,
                    'Error',
                    str(e)
                )
                return

        super(MainDialog, self).accept()
