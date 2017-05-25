# -*- coding: utf-8 -*-
# Copyright (c) 2012-2017, Anima Istanbul
#
# This module is part of anima-tools and is released under the BSD 2
# License: http://www.opensource.org/licenses/BSD-2-Clause
import re

from anima import logger
from anima.ui.base import AnimaDialogBase, ui_caller
from anima.ui import IS_PYSIDE, IS_PYSIDE2, IS_PYQT4
from anima.ui.lib import QtCore, QtWidgets, QtGui


if IS_PYSIDE():
    from anima.ui.ui_compiled import image_format_dialog_UI_pyside \
        as image_format_dialog_UI
elif IS_PYSIDE2():
    from anima.ui.ui_compiled import image_format_dialog_UI_pyside2 \
        as image_format_dialog_UI
elif IS_PYQT4():
    from anima.ui.ui_compiled import image_format_dialog_UI_pyqt4 \
        as image_format_dialog_UI


def UI(app_in=None, executor=None, **kwargs):
    """
    :param app_in: A Qt Application instance, which you can pass to let the UI
      be attached to the given applications event process.

    :param executor: Instead of calling app.exec_ the UI will call this given
      function. It also passes the created app instance to this executor.

    """
    return ui_caller(app_in, executor, MainDialog, **kwargs)


class MainDialog(QtWidgets.QDialog, image_format_dialog_UI.Ui_Dialog, AnimaDialogBase):
    """The ImageFormat Dialog
    """

    def __init__(self, parent=None, image_format=None):
        super(MainDialog, self).__init__(parent=parent)
        self.setupUi(self)

        self.image_format = image_format
        self.mode = 'Create'
        if self.image_format:
            self.mode = 'Update'

        self.dialog_label.setText('%s Image Format' % self.mode)

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

        if self.image_format:
            self.fill_ui_with_image_format(self.image_format)

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

    def fill_ui_with_image_format(self, image_format):
        """fills the UI with the given image_format

        :param image_format: A Stalker ImageFormat instance
        :return:
        """
        if False:
            from stalker import ImageFormat
            assert isinstance(image_format, ImageFormat)

        self.image_format = image_format
        self.name_lineEdit.setText(self.image_format.name)
        self.name_lineEdit.set_valid()

        self.width_spinBox.setValue(self.image_format.width)
        self.height_spinBox.setValue(self.image_format.height)
        self.pixel_aspect_doubleSpinBox.setValue(
            self.image_format.pixel_aspect
        )

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

        width = self.width_spinBox.value()
        height = self.height_spinBox.value()
        pixel_aspect = self.pixel_aspect_doubleSpinBox.value()

        from stalker import db, ImageFormat
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
                db.DBSession.add(imf)
                db.DBSession.commit()
            except Exception as e:
                db.DBSession.rollback()
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
                db.DBSession.add(self.image_format)
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
