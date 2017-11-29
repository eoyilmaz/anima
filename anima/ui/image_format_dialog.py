# -*- coding: utf-8 -*-
# Copyright (c) 2012-2017, Anima Istanbul
#
# This module is part of anima-tools and is released under the BSD 2
# License: http://www.opensource.org/licenses/BSD-2-Clause
import re

from anima import logger
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
    """The ImageFormat Dialog
    """

    def __init__(self, parent=None, image_format=None):
        super(MainDialog, self).__init__(parent=parent)

        self.vertical_layout = None
        self.dialog_label = None
        self.line = None
        self.form_layout = None
        self.name_fields_vertical_layout = None
        self.name_validator_label = None
        self.width_height_label = None
        self.horizontal_layout = None
        self.width_spin_box = None
        self.label = None
        self.height_spin_box = None
        self.pixel_aspect_label = None
        self.pixel_aspect_double_spin_box = None
        self.name_label = None
        self.button_box = None

        self.setup_ui()

        self.image_format = image_format
        self.mode = 'Create'
        if self.image_format:
            self.mode = 'Update'

        self.dialog_label.setText('%s Image Format' % self.mode)

        # create name_lineEdit
        from anima.ui.widgets import ValidatedLineEdit
        self.name_line_edit = ValidatedLineEdit(
            message_field=self.name_validator_label
        )
        self.name_line_edit.setPlaceholderText('Enter Name')
        self.name_fields_vertical_layout.insertWidget(
            0, self.name_line_edit
        )

        self._setup_signals()

        self._set_defaults()

        if self.image_format:
            self.fill_ui_with_image_format(self.image_format)

    def setup_ui(self):
        self.resize(328, 184)
        self.vertical_layout = QtWidgets.QVBoxLayout(self)
        self.dialog_label = QtWidgets.QLabel(self)
        self.dialog_label.setStyleSheet("color: rgb(71, 143, 202);\n"
                                        "font: 18pt;")
        self.vertical_layout.addWidget(self.dialog_label)
        self.line = QtWidgets.QFrame(self)
        self.line.setFrameShape(QtWidgets.QFrame.HLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.vertical_layout.addWidget(self.line)
        self.form_layout = QtWidgets.QFormLayout()
        self.form_layout.setLabelAlignment(
            QtCore.Qt.AlignRight |
            QtCore.Qt.AlignTrailing |
            QtCore.Qt.AlignVCenter
        )
        self.name_fields_vertical_layout = QtWidgets.QVBoxLayout()
        self.name_validator_label = QtWidgets.QLabel(self)
        self.name_validator_label.setStyleSheet("color: rgb(255, 0, 0);")
        self.name_fields_vertical_layout.addWidget(
            self.name_validator_label)
        self.form_layout.setLayout(
            0,
            QtWidgets.QFormLayout.FieldRole,
            self.name_fields_vertical_layout
        )
        self.width_height_label = QtWidgets.QLabel(self)
        self.form_layout.setWidget(
            1,
            QtWidgets.QFormLayout.LabelRole,
            self.width_height_label
        )
        self.horizontal_layout = QtWidgets.QHBoxLayout()
        self.width_spin_box = QtWidgets.QSpinBox(self)
        self.width_spin_box.setMaximum(99999)
        self.horizontal_layout.addWidget(self.width_spin_box)
        self.label = QtWidgets.QLabel(self)
        self.horizontal_layout.addWidget(self.label)
        self.height_spin_box = QtWidgets.QSpinBox(self)
        self.height_spin_box.setMaximum(99999)
        self.horizontal_layout.addWidget(self.height_spin_box)
        self.horizontal_layout.setStretch(0, 1)
        self.horizontal_layout.setStretch(2, 1)
        self.form_layout.setLayout(
            1,
            QtWidgets.QFormLayout.FieldRole,
            self.horizontal_layout
        )
        self.pixel_aspect_label = QtWidgets.QLabel(self)
        self.form_layout.setWidget(
            2,
            QtWidgets.QFormLayout.LabelRole,
            self.pixel_aspect_label
        )
        self.pixel_aspect_double_spin_box = QtWidgets.QDoubleSpinBox(self)
        self.pixel_aspect_double_spin_box.setProperty("value", 1.0)
        self.form_layout.setWidget(
            2,
            QtWidgets.QFormLayout.FieldRole,
            self.pixel_aspect_double_spin_box
        )
        self.name_label = QtWidgets.QLabel(self)
        self.form_layout.setWidget(
            0,
            QtWidgets.QFormLayout.LabelRole,
            self.name_label
        )
        self.vertical_layout.addLayout(self.form_layout)
        self.button_box = QtWidgets.QDialogButtonBox(self)
        self.button_box.setOrientation(QtCore.Qt.Horizontal)
        self.button_box.setStandardButtons(
            QtWidgets.QDialogButtonBox.Cancel | QtWidgets.QDialogButtonBox.Ok)
        self.vertical_layout.addWidget(self.button_box)
        self.vertical_layout.setStretch(2, 1)

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
        QtCore.QMetaObject.connectSlotsByName(self)

        self.setWindowTitle("Image Format Dialog")
        self.dialog_label.setText("Create Image Format")
        self.name_validator_label.setText("Validator Message")
        self.width_height_label.setText("Width x Height")
        self.label.setText("x")
        self.pixel_aspect_label.setText("Pixel Aspect")
        self.name_label.setText("Name")

    def _setup_signals(self):
        """create the signals
        """
        # name_lineEdit is changed
        QtCore.QObject.connect(
            self.name_line_edit,
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
            self.name_line_edit.set_invalid('Invalid character')
        else:
            if text == '':
                self.name_line_edit.set_invalid('Enter a name')
            else:
                self.name_line_edit.set_valid()

    def fill_ui_with_image_format(self, image_format):
        """fills the UI with the given image_format

        :param image_format: A Stalker ImageFormat instance
        :return:
        """
        if False:
            from stalker import ImageFormat
            assert isinstance(image_format, ImageFormat)

        self.image_format = image_format
        self.name_line_edit.setText(self.image_format.name)
        self.name_line_edit.set_valid()

        self.width_spin_box.setValue(self.image_format.width)
        self.height_spin_box.setValue(self.image_format.height)
        self.pixel_aspect_double_spin_box.setValue(
            self.image_format.pixel_aspect
        )

    def accept(self):
        """overridden accept method
        """
        if not self.name_line_edit.is_valid:
            QtWidgets.QMessageBox.critical(
                self,
                'Error',
                'Please fix <b>name</b> field!'
            )
            return
        name = self.name_line_edit.text()

        width = self.width_spin_box.value()
        height = self.height_spin_box.value()
        pixel_aspect = self.pixel_aspect_double_spin_box.value()

        from stalker import ImageFormat
        from stalker.db.session import DBSession
        logged_in_user = self.get_logged_in_user()
        if self.mode == 'Create':
            # Create a new Image Format
            try:
                imf = ImageFormat(
                    name=name,
                    width=width,
                    height=height,
                    pixel_aspect=pixel_aspect,
                    created_by=logged_in_user
                )
                self.image_format = imf
                DBSession.add(imf)
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
            # Update the image format
            try:
                self.image_format.name = name
                self.image_format.width = width
                self.image_format.height = height
                self.image_format.pixel_aspect = pixel_aspect
                self.image_format.updated_by = logged_in_user
                DBSession.add(self.image_format)
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
