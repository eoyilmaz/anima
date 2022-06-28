# -*- coding: utf-8 -*-

import re

from anima.ui.base import AnimaDialogBase, ui_caller
from anima.ui.lib import QtCore, QtWidgets


def UI(app_in=None, executor=None, **kwargs):
    """
    :param app_in: A Qt Application instance, which you can pass to let the UI
      be attached to the given applications event process.

    :param executor: Instead of calling app.exec_ the UI will call this given
      function. It also passes the created app instance to this executor.

    """
    return ui_caller(app_in, executor, MainDialog, **kwargs)


class MainDialog(QtWidgets.QDialog, AnimaDialogBase):
    """The structure Dialog"""

    def __init__(self, parent=None, structure=None):
        super(MainDialog, self).__init__(parent=parent)
        self.structure = structure
        self.mode = "Create"
        if self.structure:
            self.mode = "Update"

        self.name_validator_label = None
        self.name_line_edit = None
        self.filename_templates_double_list_widget = None
        self.custom_template_plain_text_edit = None
        self.button_box = None

        self.setup_ui()

        self._set_defaults()

        if self.structure:
            self.fill_ui_with_structure(self.structure)

    def setup_ui(self):
        """Create UI elements."""
        self.setWindowTitle("Structure Dialog")
        self.resize(754, 662)
        main_layout = QtWidgets.QVBoxLayout(self)

        # Dialog Label
        dialog_label = QtWidgets.QLabel(self)
        dialog_label.setText("%s Structure" % self.mode)
        dialog_label.setStyleSheet("color: rgb(71, 143, 202);\n" "font: 18pt;")
        main_layout.addWidget(dialog_label)

        line = QtWidgets.QFrame(self)
        line.setFrameShape(QtWidgets.QFrame.HLine)
        line.setFrameShadow(QtWidgets.QFrame.Sunken)
        main_layout.addWidget(line)

        # Form Layout
        form_layout = QtWidgets.QFormLayout()
        form_layout.setLabelAlignment(
            QtCore.Qt.AlignRight | QtCore.Qt.AlignTrailing | QtCore.Qt.AlignVCenter
        )
        label_role = QtWidgets.QFormLayout.LabelRole
        field_role = QtWidgets.QFormLayout.FieldRole

        # ========================================
        # Name Fields
        form_layout.setWidget(0, label_role, QtWidgets.QLabel("Name", self))
        name_fields_layout = QtWidgets.QVBoxLayout()

        # Validator
        from anima.ui.widgets import ValidatedLineEdit
        self.name_validator_label = QtWidgets.QLabel(self)
        self.name_validator_label.setStyleSheet("color: rgb(255, 0, 0);")

        # Field
        self.name_line_edit = ValidatedLineEdit(message_field=self.name_validator_label)
        self.name_line_edit.setPlaceholderText("Enter Name")
        self.name_line_edit.textChanged.connect(self.name_line_edit_changed)
        name_fields_layout.addWidget(self.name_line_edit)
        name_fields_layout.addWidget(self.name_validator_label)
        form_layout.setLayout(0, field_role, name_fields_layout)

        # ========================================
        # Filename Templates
        filename_templates_label = QtWidgets.QLabel(self)
        filename_templates_label.setText(
            '<html><head/><body><p align="right">Filename<br/>Templates</p></body></html>'
        )
        form_layout.setWidget(1, label_role, filename_templates_label)

        # Filename Template DoubleListWidget
        filename_template_fields_layout = QtWidgets.QVBoxLayout()
        from anima.ui.widgets import DoubleListWidget

        self.filename_templates_double_list_widget = DoubleListWidget(
            dialog=self,
            parent_layout=filename_template_fields_layout,
            primary_label_text="Templates From DB",
            secondary_label_text="Selected Templates",
        )
        # set the tooltip
        self.filename_templates_double_list_widget.primary_list_widget.setToolTip(
            "Right Click to Create/Update FilenameTemplates"
        )
        self.filename_templates_double_list_widget.secondary_list_widget.setToolTip(
            "Right Click to Create/Update FilenameTemplates"
        )
        # add context menu for primary items in DoubleListWidget
        widget = self.filename_templates_double_list_widget.primary_list_widget
        widget.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)

        widget = self.filename_templates_double_list_widget.primary_list_widget
        widget.customContextMenuRequested.connect(
            self.show_primary_filename_template_context_menu
        )

        # add context menu for secondary items in DoubleListWidget
        widget = self.filename_templates_double_list_widget.secondary_list_widget
        widget.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)

        widget = self.filename_templates_double_list_widget.secondary_list_widget
        widget.customContextMenuRequested.connect(
            self.show_secondary_filename_template_context_menu
        )
        form_layout.setLayout(1, field_role, filename_template_fields_layout,)

        # ========================================
        # Custom Template
        custom_template_label = QtWidgets.QLabel(self)
        custom_template_label.setText(
            '<html><head/><body><p align="right">Custom<br/>Template</p></body></html>'
        )
        form_layout.setWidget(
            2, label_role, custom_template_label
        )
        self.custom_template_plain_text_edit = QtWidgets.QPlainTextEdit(self)
        form_layout.setWidget(
            2, field_role, self.custom_template_plain_text_edit
        )
        main_layout.addLayout(form_layout)

        # ========================================
        # Button Box
        self.button_box = QtWidgets.QDialogButtonBox(self)
        self.button_box.setOrientation(QtCore.Qt.Horizontal)
        self.button_box.setStandardButtons(
            QtWidgets.QDialogButtonBox.Cancel | QtWidgets.QDialogButtonBox.Ok
        )
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        main_layout.addWidget(self.button_box)
        main_layout.setStretch(2, 1)

    def _set_defaults(self):
        """sets the default values"""
        # fill filename_templates_from_db_listWidget
        # add all the other filename templates from the database
        from stalker import FilenameTemplate

        fts = FilenameTemplate.query.all()

        self.filename_templates_double_list_widget.clear()
        self.filename_templates_double_list_widget.add_primary_items(
            list(
                map(lambda x: "%s (%s) (%s)" % (x.name, x.target_entity_type, x.id), fts)
            )
        )

    def name_line_edit_changed(self, text):
        """runs when the name_line_edit text has changed"""
        if re.findall(r"[^a-zA-Z0-9\-_ ]+", text):
            self.name_line_edit.set_invalid("Invalid character")
        else:
            if text == "":
                self.name_line_edit.set_invalid("Enter a name")
            else:
                self.name_line_edit.set_valid()

    def fill_ui_with_structure(self, structure):
        """fills the UI with the given structure

        :param structure: A Stalker ImageFormat instance
        :return:
        """
        self.structure = structure
        self.name_line_edit.setText(self.structure.name)
        self.name_line_edit.set_valid()

        self.custom_template_plain_text_edit.setPlainText(self.structure.custom_template)

        # add the structure templates to the secondary list of the double list
        self.filename_templates_double_list_widget.clear()
        self.filename_templates_double_list_widget.add_secondary_items(
            list(map(
                lambda x: "%s (%s) (%s)" % (x.name, x.target_entity_type, x.id),
                self.structure.templates,
            ))
        )

        # add all the other filename templates from the database
        from stalker import FilenameTemplate

        fts = FilenameTemplate.query.filter(
            ~FilenameTemplate.id.in_(map(lambda x: x.id, self.structure.templates))
        ).all()

        self.filename_templates_double_list_widget.add_primary_items(
            map(lambda x: "%s (%s) (%s)" % (x.name, x.target_entity_type, x.id), fts)
        )

    def show_primary_filename_template_context_menu(self, position):
        """shows the custom context menu for primary list widget

        :param position:
        :return:
        """
        self.show_filename_template_context_menu(
            self.filename_templates_double_list_widget.primary_list_widget, position
        )

    def show_secondary_filename_template_context_menu(self, position):
        """shows the custom context menu for secondary list widget

        :param position:
        :return:
        """
        self.show_filename_template_context_menu(
            self.filename_templates_double_list_widget.secondary_list_widget, position
        )

    def show_filename_template_context_menu(self, list_widget, position):
        """shows a context menu for the given list_widget

        :param list_widget: QListWidget instance
        :param position: the mouse click position
        :return:
        """
        item = list_widget.itemAt(position)

        menu = QtWidgets.QMenu()
        menu.addAction("Create FilenameTemplate...")
        if item:
            menu.addAction("Update FilenameTemplate...")

        global_position = list_widget.mapToGlobal(position)
        selected_item = menu.exec_(global_position)

        try:
            # PySide
            accepted = QtWidgets.QDialog.DialogCode.Accepted
        except AttributeError:
            # PyQt4
            accepted = QtWidgets.QDialog.Accepted

        if selected_item:
            choice = selected_item.text()
            if choice == "Create FilenameTemplate...":
                from anima.ui import filename_template_dialog

                create_filename_template_dialog = filename_template_dialog.MainDialog(
                    parent=self
                )
                create_filename_template_dialog.exec_()

                if create_filename_template_dialog.result() == accepted:
                    ft = create_filename_template_dialog.filename_template
                    list_widget.addItem(
                        "%s (%s) (%s)" % (ft.name, ft.target_entity_type, ft.id)
                    )
                create_filename_template_dialog.deleteLater()

            elif choice == "Update FilenameTemplate...":
                ft_id = int(item.text().split("(")[-1].split(")")[0])
                if not ft_id:
                    return

                from stalker import FilenameTemplate

                ft = FilenameTemplate.query.get(ft_id)

                from anima.ui import filename_template_dialog

                update_filename_template_dialog = filename_template_dialog.MainDialog(
                    parent=self, filename_template=ft
                )
                try:
                    update_filename_template_dialog.exec_()
                    if update_filename_template_dialog.result() == accepted:
                        # update the text of the item
                        ft = update_filename_template_dialog.filename_template
                        item.setText(
                            "%s (%s) (%s)" % (ft.name, ft.target_entity_type, ft.id)
                        )

                    update_filename_template_dialog.deleteLater()
                except Exception as e:
                    QtWidgets.QMessageBox.warning(self, "Error", str(e))
                    return

    def accept(self):
        """overridden accept method"""
        if not self.name_line_edit.is_valid:
            QtWidgets.QMessageBox.critical(
                self, "Error", "Please fix <b>name</b> field!"
            )
            return
        name = self.name_line_edit.text()

        custom_template = self.custom_template_plain_text_edit.toPlainText()

        filename_template_items = (
            self.filename_templates_double_list_widget.secondary_items()
        )
        filename_template_ids = []
        for item in filename_template_items:
            filename_template_id = int(item.text().split("(")[-1].split(")")[0])
            filename_template_ids.append(filename_template_id)

        from stalker import FilenameTemplate

        filename_templates = FilenameTemplate.query.filter(
            FilenameTemplate.id.in_(filename_template_ids)
        ).all()

        from stalker import Structure
        from stalker.db.session import DBSession

        logged_in_user = self.get_logged_in_user()
        if self.mode == "Create":
            # Create a new Structure
            try:
                structure = Structure(
                    name=name,
                    templates=filename_templates,
                    custom_template=custom_template,
                    created_by=logged_in_user,
                )
                self.structure = structure
                DBSession.add(structure)
                DBSession.commit()
            except Exception as e:
                DBSession.rollback()
                QtWidgets.QMessageBox.critical(self, "Error", str(e))
                return

        elif self.mode == "Update":
            # Update the structure
            try:
                self.structure.name = name
                self.structure.templates = filename_templates
                self.structure.custom_template = custom_template
                self.structure.updated_by = logged_in_user
                DBSession.add(self.structure)
                DBSession.commit()
            except Exception as e:
                DBSession.rollback()
                QtWidgets.QMessageBox.critical(self, "Error", str(e))
                return

        super(MainDialog, self).accept()
