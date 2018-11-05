# -*- coding: utf-8 -*-
# Copyright (c) 2012-2018, Anima Istanbul
#
# This module is part of anima-tools and is released under the BSD 2
# License: http://www.opensource.org/licenses/BSD-2-Clause
import re

from anima.ui.base import AnimaDialogBase, ui_caller
from anima.ui import IS_PYSIDE, IS_PYSIDE2, IS_PYQT4
from anima.ui.lib import QtCore, QtWidgets, QtGui


def UI(app_in=None, executor=None, **kwargs):
    """
    :param app_in: A Qt Application instance, which you can pass to let the UI
      be attached to the given applications event process.

    :param executor: Instead of calling app.exec_ the UI will call this given
      function. It also passes the created app instance to this executor.

    """
    return ui_caller(app_in, executor, MainDialog, **kwargs)


class MainDialog(QtWidgets.QDialog, AnimaDialogBase):
    """The FilenameTemplate Dialog
    """

    def __init__(self, parent=None, filename_template=None):
        super(MainDialog, self).__init__(parent=parent)

        self.filename_template = filename_template
        self.mode = 'Create'
        if self.filename_template:
            self.mode = 'Update'

        self._setup_ui()
        if self.filename_template:
            self._fill_ui_with_filename_template(self.filename_template)

    def _setup_ui(self):
        """setup the ui elements
        """
        self.resize(750, 180)
        self.vertical_layout = QtWidgets.QVBoxLayout(self)

        # Dialog Label
        self.dialog_label = QtWidgets.QLabel(self)
        self.dialog_label.setText('%s Filename Template' % self.mode)
        self.dialog_label.setStyleSheet("color: rgb(71, 143, 202);font: 18pt;")
        self.vertical_layout.addWidget(self.dialog_label)

        # Title Line
        line = QtWidgets.QFrame(self)
        line.setFrameShape(QtWidgets.QFrame.HLine)
        line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.vertical_layout.addWidget(line)

        # Form Layout
        self.form_layout = QtWidgets.QFormLayout()
        self.form_layout.setLabelAlignment(
            QtCore.Qt.AlignRight |
            QtCore.Qt.AlignTrailing |
            QtCore.Qt.AlignVCenter
        )
        self.vertical_layout.addLayout(self.form_layout)

        # ------------------------------------------------
        # Target Entity Type Field

        # label
        self.target_entity_type_label = \
            QtWidgets.QLabel('Target Entity Type', self)
        self.form_layout.setWidget(
            0, QtWidgets.QFormLayout.LabelRole, self.target_entity_type_label
        )

        # field
        self.target_entity_type_combo_box = QtWidgets.QComboBox(self)
        self.form_layout.setWidget(
            0, QtWidgets.QFormLayout.FieldRole,
            self.target_entity_type_combo_box
        )

        # ------------------------------------------------
        # Name Field
        self.name_label = QtWidgets.QLabel('Name', self)
        self.form_layout.setWidget(
            1, QtWidgets.QFormLayout.LabelRole, self.name_label
        )
        self.name_fields_vertical_layout = QtWidgets.QVBoxLayout()
        self.name_validator_label = QtWidgets.QLabel(self)
        self.name_validator_label.setStyleSheet('color: rgb(255, 0, 0);')

        from anima.ui.widgets import ValidatedLineEdit
        self.name_line_edit = ValidatedLineEdit(
            self,
            message_field=self.name_validator_label
        )

        self.name_fields_vertical_layout.addWidget(self.name_line_edit)
        self.name_fields_vertical_layout.addWidget(self.name_validator_label)
        self.form_layout.setLayout(
            1,
            QtWidgets.QFormLayout.FieldRole,
            self.name_fields_vertical_layout
        )

        # ------------------------------------------------
        # Path Code Field
        self.path_label = QtWidgets.QLabel('Path', self)
        self.form_layout.setWidget(
            2, QtWidgets.QFormLayout.LabelRole, self.path_label
        )

        self.path_line_edit = QtWidgets.QLineEdit(self)
        # set the default value to something useful
        self.form_layout.setWidget(
            2, QtWidgets.QFormLayout.FieldRole, self.path_line_edit
        )

        # ------------------------------------------------
        # Filename Code Field
        self.filename_label = QtWidgets.QLabel('Filename', self)
        self.form_layout.setWidget(
            3, QtWidgets.QFormLayout.LabelRole, self.filename_label
        )

        self.filename_line_edit = QtWidgets.QLineEdit(self)
        self.form_layout.setWidget(
            3, QtWidgets.QFormLayout.FieldRole, self.filename_line_edit
        )

        # ------------------------------------------------
        # Button Box
        self.button_box = QtWidgets.QDialogButtonBox(self)
        self.button_box.setOrientation(QtCore.Qt.Horizontal)
        self.button_box.setStandardButtons(
            QtWidgets.QDialogButtonBox.Cancel |
            QtWidgets.QDialogButtonBox.Ok
        )
        self.vertical_layout.addWidget(self.button_box)
        self.vertical_layout.setStretch(2, 1)

        # ------------------------------------------------
        # Default values
        self.target_entity_type_combo_box.addItems(
            ['Task', 'Asset', 'Shot', 'Sequence']
        )
        self.name_line_edit.set_invalid()  # Empty field is not valid
        self.path_line_edit.setText(
            '$REPO{{project.repository.id}}/{{project.code}}/'
            '{%- for parent_task in parent_tasks -%}{{parent_task.nice_name}}'
            '/{%- endfor -%}'
        )
        self.filename_line_edit.setText(
            '{{version.nice_name}}_v{{"%03d"|format(version.version_number)}}'
        )

        # ------------------------------------------------
        # Disable Fields
        if self.mode == 'Update':
            self.target_entity_type_combo_box.setEnabled(False)

        # ------------------------------------------------
        # Signals
        # Name
        QtCore.QObject.connect(
            self.name_line_edit,
            QtCore.SIGNAL('textChanged(QString)'),
            self.name_line_edit_changed
        )

        # Button box
        QtCore.QObject.connect(
            self.button_box, QtCore.SIGNAL("accepted()"), self.accept
        )
        QtCore.QObject.connect(
            self.button_box, QtCore.SIGNAL("rejected()"), self.reject
        )

    def name_line_edit_changed(self, text):
        """runs when the name_line_edit text has changed
        """
        if re.findall(r'[^a-zA-Z0-9\-_ ]+', text):
            self.name_line_edit.set_invalid('Invalid character')
        else:
            if text == '':
                self.name_line_edit.set_invalid('Enter a name')
            else:
                self.name_line_edit.set_valid()

    def _fill_ui_with_filename_template(self, filename_template):
        """Fills the UI with the given filename template

        :param filename_template: A Stalker FilenameTemplate instance
        :return:
        """
        if False:
            from stalker import FilenameTemplate
            assert isinstance(filename_template, FilenameTemplate)

        self.name_line_edit.setText(filename_template.name)
        self.path_line_edit.setText(filename_template.path)
        self.filename_line_edit.setText(filename_template.filename)

    def accept(self):
        """the overridden accept method
        """
        target_entity_type = self.target_entity_type_combo_box.currentText()

        if not self.name_line_edit.is_valid:
            QtWidgets.QMessageBox.critical(
                self,
                'Error',
                'Please fix <b>name</b> field!'
            )
            return
        name = self.name_line_edit.text()

        path = self.path_line_edit.text()
        if path == '':
            QtWidgets.QMessageBox.critical(
                self,
                'Error',
                'Please fix <b>path</b> field!'
            )
            return

        filename = self.filename_line_edit.text()
        if path == '':
            QtWidgets.QMessageBox.critical(
                self,
                'Error',
                'Please fix <b>filename</b> field!'
            )
            return

        logged_in_user = self.get_logged_in_user()
        from stalker.db.session import DBSession
        if self.mode == 'Create':
            try:
                from stalker import FilenameTemplate
                # create a new FilenameTemplate
                ft = FilenameTemplate(
                    name=name,
                    path=path,
                    filename=filename,
                    target_entity_type=target_entity_type,
                    created_by=logged_in_user
                )
                self.filename_template = ft
                DBSession.add(ft)
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
            try:
                self.filename_template.name = name
                self.filename_template.path = path
                self.filename_template.filename = filename
                self.filename_template.updated_by = logged_in_user
                DBSession.add(self.filename_template)
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
