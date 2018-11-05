# -*- coding: utf-8 -*-
# Copyright (c) 2012-2018, Anima Istanbul
#
# This module is part of anima-tools and is released under the BSD 2
# License: http://www.opensource.org/licenses/BSD-2-Clause

from anima.ui.lib import QtCore, QtWidgets


class ImageFormatWidget(object):
    """Helper class for ImageFormat fields
    """

    def __init__(self,
                 parent=None,
                 parent_form_layout=None,
                 parent_form_layout_index=None):
        self.parent = parent
        self.parent_form_layout = parent_form_layout
        self.parent_form_layout_index = parent_form_layout_index

        self.label = None
        self.horizontal_layout = None
        self.combo_box = None
        self.create_push_button = None
        self.update_push_button = None

        self._setup_ui()
        self._setup_signals()

    def _setup_ui(self):
        """creates the ui elements
        """
        self.label = QtWidgets.QLabel(self.parent)
        self.parent_form_layout.setWidget(
            self.parent_form_layout_index,
            QtWidgets.QFormLayout.LabelRole,
            self.label
        )
        self.horizontal_layout = QtWidgets.QHBoxLayout()
        self.combo_box = QtWidgets.QComboBox(self.parent)
        self.horizontal_layout.addWidget(self.combo_box)
        self.update_push_button = QtWidgets.QPushButton(self.parent)
        self.horizontal_layout.addWidget(self.update_push_button)
        self.create_push_button = QtWidgets.QPushButton(self.parent)
        self.horizontal_layout.addWidget(self.create_push_button)
        self.horizontal_layout.setStretch(0, 1)
        self.parent_form_layout.setLayout(
            self.parent_form_layout_index,
            QtWidgets.QFormLayout.FieldRole,
            self.horizontal_layout
        )
        self.label.setText("Image Format")
        self.update_push_button.setText("Update...")
        self.create_push_button.setText("New...")

    def _setup_signals(self):
        """creates the signals between ui elements
        """

        # create_image_format_pushButton
        QtCore.QObject.connect(
            self.create_push_button,
            QtCore.SIGNAL('clicked()'),
            self.create_push_button_clicked
        )

        # update_image_format_pushButton
        QtCore.QObject.connect(
            self.update_push_button,
            QtCore.SIGNAL('clicked()'),
            self.update_push_button_clicked
        )

    def fill_combo_box(self):
        """fills the image_format_comboBox
        """
        # fill the image format field
        from stalker import ImageFormat
        from stalker.db.session import DBSession
        all_image_formats = DBSession \
            .query(ImageFormat.id, ImageFormat.name, ImageFormat.width,
                   ImageFormat.height) \
            .order_by(ImageFormat.name) \
            .all()
        self.combo_box.clear()
        for imf_id, imf_name, imf_width, imf_height in all_image_formats:
            imf_text = '%s (%s x %s)' % (imf_name, imf_width, imf_height)
            self.combo_box.addItem(imf_text, imf_id)

    def create_push_button_clicked(self):
        """runs when create_image_format_pushButton is clicked
        """
        try:
            # PySide
            accepted = QtWidgets.QDialog.DialogCode.Accepted
        except AttributeError:
            # PyQt4
            accepted = QtWidgets.QDialog.Accepted

        from anima.ui import image_format_dialog
        create_image_format_dialog = \
            image_format_dialog.MainDialog(parent=self.parent)
        create_image_format_dialog.exec_()
        result = create_image_format_dialog.result()

        if result == accepted:
            image_format = create_image_format_dialog.image_format

            # select the created image format
            self.fill_combo_box()
            self.set_current_image_format(image_format.id)

        create_image_format_dialog.deleteLater()

    def update_push_button_clicked(self):
        """runs when update_image_format_pushButton is clicked
        """
        try:
            # PySide
            accepted = QtWidgets.QDialog.DialogCode.Accepted
        except AttributeError:
            # PyQt4
            accepted = QtWidgets.QDialog.Accepted

        image_format = self.get_current_image_format()
        if not image_format:
            return

        from anima.ui import image_format_dialog
        update_image_format_dialog = \
            image_format_dialog.MainDialog(parent=self.parent,
                                           image_format=image_format)
        update_image_format_dialog.exec_()
        result = update_image_format_dialog.result()

        if result == accepted:
            image_format = update_image_format_dialog.image_format

            # select the created image format
            self.fill_combo_box()
            self.set_current_image_format(image_format.id)

        update_image_format_dialog.deleteLater()

    def get_current_image_format(self):
        """returns the currently selected image format instance from the UI
        """
        from stalker import ImageFormat
        index = self.combo_box.currentIndex()
        image_format_id = self.combo_box.itemData(index)
        image_format = ImageFormat.query.get(image_format_id)
        return image_format

    def set_current_image_format(self, image_format):
        """Sets the current selected image format

        :param image_format: Either the id of the ImageFormat instance or the
          instance itself.
        :return:
        """
        image_format_id = image_format
        from stalker import ImageFormat
        if isinstance(image_format, ImageFormat):
            image_format_id = image_format.id

        index = self.combo_box.findData(image_format_id)
        if index:
            self.combo_box.setCurrentIndex(index)

    def set_visible(self, visible):
        """sets the visibility of this widget

        :param visible:
        :return:
        """
        self.label.setVisible(visible)
        self.combo_box.setVisible(visible)
        self.update_push_button.setVisible(visible)
        self.create_push_button.setVisible(visible)
