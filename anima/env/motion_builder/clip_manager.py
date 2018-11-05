# -*- coding: utf-8 -*-
# Copyright (c) 2012-2018, Anima Istanbul
#
# This module is part of anima-tools and is released under the BSD 2
# License: http://www.opensource.org/licenses/BSD-2-Clause


from anima.ui.base import AnimaDialogBase, ui_caller
from anima.ui.lib import QtCore, QtGui, QtWidgets


def UI(app_in=None, executor=None, **kwargs):
    """
    :param app_in: A Qt Application instance, which you can pass to let the UI
      be attached to the given applications event process.

    :param executor: Instead of calling app.exec_ the UI will call this given
      function. It also passes the created app instance to this executor.

    """
    return ui_caller(app_in, executor, MainDialog, **kwargs)


class ClipFieldGrp(object):
    """A class to organize clip fields
    """

    def __init__(self):
        self.parent = None
        self.layout = None

        self.shot_name_field = None

        self.fbx_file_field = None
        self.fbx_choose_button = None

        self.video_file_field = None
        self.video_choose_button = None

        self.cut_in_field = None
        self.cut_out_field = None

        self.delete_push_button = None

        self._delete_callback = None

        self._previous_field = None
        self._next_field = None

        self.fps_field = None

    def create(self, parent=None):
        """Creates the fields under the given layout
        :param parent:
        :return:
        """
        self.parent = parent

        # Main Layout
        self.layout = QtWidgets.QHBoxLayout(parent)
        layout_widget = self.layout.widget()

        # Shot Name Field
        self.shot_name_field = QtWidgets.QLineEdit(layout_widget)
        self.layout.addWidget(self.shot_name_field)

        # FBX file field
        self.fbx_file_field = QtWidgets.QLineEdit(layout_widget)
        self.fbx_file_field.setPlaceholderText("Choose FBX File")
        self.layout.addWidget(self.fbx_file_field)

        # FBX Button
        self.fbx_choose_button = QtWidgets.QPushButton(layout_widget)
        self.fbx_choose_button.setText("...")
        self.layout.addWidget(self.fbx_choose_button)

        # Video file field
        self.video_file_field = QtWidgets.QLineEdit(layout_widget)
        self.video_file_field.setPlaceholderText("Choose Video File")
        self.layout.addWidget(self.video_file_field)

        # FBX Button
        self.video_choose_button = QtWidgets.QPushButton(layout_widget)
        self.video_choose_button.setText("...")
        self.layout.addWidget(self.video_choose_button)

        # Cut in Field
        self.cut_in_field = QtWidgets.QSpinBox()
        self.cut_in_field.setMinimum(0)
        self.cut_in_field.setMaximum(9999999)
        self.layout.addWidget(self.cut_in_field)

        # Cut out Field
        self.cut_out_field = QtWidgets.QSpinBox()
        self.cut_out_field.setMinimum(0)
        self.cut_out_field.setMaximum(9999999)
        self.layout.addWidget(self.cut_out_field)

        # FPS Field
        self.fps_field = QtWidgets.QDoubleSpinBox()
        self.fps_field.setMinimum(0)
        self.fps_field.setMaximum(9999999)
        self.fps_field.setDecimals(2)
        self.layout.addWidget(self.fps_field)

        # Delete Button
        self.delete_push_button = QtWidgets.QPushButton(layout_widget)
        self.delete_push_button.setText("Delete")
        self.layout.addWidget(self.delete_push_button)

        # Signals
        import functools

        # Choose FBX Push Button
        QtCore.QObject.connect(
            self.fbx_choose_button,
            QtCore.SIGNAL("clicked()"),
            functools.partial(self.fbx_choose_button_clicked)
        )

        # Choose Video Push Button
        QtCore.QObject.connect(
            self.video_choose_button,
            QtCore.SIGNAL("clicked()"),
            functools.partial(self.video_choose_button_clicked)
        )

        QtCore.QObject.connect(
            self.delete_push_button,
            QtCore.SIGNAL("clicked()"),
            functools.partial(self.delete)
        )

        QtCore.QObject.connect(
            self.video_file_field,
            QtCore.SIGNAL("editingFinished()"),
            functools.partial(self.video_file_field_changed)
        )

    def fbx_choose_button_clicked(self):
        """runs when the FBX push button is clicked
        """
        dialog = QtWidgets.QFileDialog(self.parent, "Choose FBX File")
        result = dialog.getOpenFileName()
        file_path = result[0]
        if file_path:
            self.fbx_file_field.setText(file_path)

    def video_choose_button_clicked(self):
        """runs when the Video push button is clicked
        """
        dialog = QtWidgets.QFileDialog(self.parent, "Choose Video File")
        result = dialog.getOpenFileName()
        file_path = result[0]
        if file_path:
            self.video_file_field.setText(file_path)

    def video_file_field_changed(self):
        """Runs when the video file field has changed

        :param text: The video path
        :return:
        """
        file_path = self.video_file_field.text()
        import os
        if not os.path.exists(file_path):
            return

        # read video in out
        # use MediaManager
        from anima.utils import MediaManager
        mm = MediaManager()
        video_info = mm.get_video_info(file_path)
        number_of_frames = int(
            video_info['stream_info'][0].get('nb_frames', 0)
        )

        # get the fps
        fps_str = video_info['stream_info'][0].get('avg_frame_rate', 25)
        if '/' in fps_str:
            fps_data = fps_str.split('/')
            fps = float(fps_data[0]) / float(fps_data[1])
        else:
            fps = float(fps_str)
        self.fps_field.setValue(fps)

        # update the cut_out to be cut_in + number_of_frames
        self.cut_out_field.setValue(
            self.cut_in_field.value() + number_of_frames
        )
        # and trigger an update
        self.update_cut_in_out_from_neighbours()

    def delete(self):
        """delete self
        """
        # join previous and next video fields
        if self.previous_field:
            self.previous_field.next_field = self.next_field

        if self.next_field:
            self.next_field.previous_field = self.previous_field

        self.delete_push_button.deleteLater()
        self.video_choose_button.deleteLater()
        self.video_file_field.deleteLater()
        self.fbx_choose_button.deleteLater()
        self.fbx_file_field.deleteLater()
        self.cut_in_field.deleteLater()
        self.cut_out_field.deleteLater()
        self.shot_name_field.deleteLater()
        self.layout.deleteLater()

        if self._delete_callback:
            self._delete_callback(self)

    @property
    def previous_field(self):
        """return the previous field
        """
        return self._previous_field

    @previous_field.setter
    def previous_field(self, field):
        """Update the previous field info

        :param ClipFieldGrp field:
        :return:
        """
        # update the cut_in and cut_out to previous fields info
        self._previous_field = field
        self.update_cut_in_out_from_neighbours()

    @property
    def next_field(self):
        """returns the next field
        """
        return self._next_field

    @next_field.setter
    def next_field(self, field):
        """Update the next field info

        :param ClipFieldGrp field:
        :return:
        """
        self._next_field = field
        if self.next_field:
            self.next_field.update_cut_in_out_from_neighbours()

    def update_cut_in_out_from_neighbours(self):
        """updates the cut_in and cut_out info with neighbour fields
        """
        duration = self.cut_out_field.value() - self.cut_in_field.value() + 1
        if self.previous_field:
            self.cut_in_field.setValue(
                self.previous_field.cut_out_field.value()
            )

        self.cut_out_field.setValue(
            self.cut_in_field.value() + duration - 1
        )

        # also trigger an update for the next fields
        if self.next_field:
            self.next_field.update_cut_in_out_from_neighbours()


class MainDialog(QtWidgets.QDialog, AnimaDialogBase):
    """Bulk Task Manager Dialog to manage tasks in bulk.

    This UI filters parent tasks and displays the child tasks in a
    QTableWidget.
    """

    def __init__(self, parent=None):
        super(MainDialog, self).__init__(parent=parent)

        self.clip_fields = []
        self._setup_ui()

    def _setup_ui(self):
        """create the UI elements
        """
        # Create the main layout
        self.resize(850, 650)

        # Main Layout
        self.main_layout = QtWidgets.QVBoxLayout(self)

        # Dialog Label
        self.dialog_label = QtWidgets.QLabel(self)

        self.dialog_label.setText("Clip Manager")
        self.dialog_label.setStyleSheet("color: rgb(71, 143, 202);font: 18pt;")

        self.main_layout.addWidget(self.dialog_label)

        # Title Line
        line = QtWidgets.QFrame(self)
        line.setFrameShape(QtWidgets.QFrame.HLine)
        line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.main_layout.addWidget(line)

        # Add Clip Field Button
        self.add_clip_field_push_button = QtWidgets.QPushButton(self)
        self.add_clip_field_push_button.setText("Add Clip")
        self.main_layout.addWidget(self.add_clip_field_push_button)

        # Clip Fields Layout
        self.scroll_area_widget = QtWidgets.QWidget(self)
        self.clip_vertical_layout = QtWidgets.QVBoxLayout(self)
        self.scroll_area_widget.setLayout(self.clip_vertical_layout)

        self.scroll_area = QtWidgets.QScrollArea(self)
        self.scroll_area.setVerticalScrollBarPolicy(
            QtCore.Qt.ScrollBarAsNeeded
        )
        self.scroll_area.setHorizontalScrollBarPolicy(
            QtCore.Qt.ScrollBarAsNeeded
        )
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setWidget(self.scroll_area_widget)

        self.main_layout.addWidget(self.scroll_area)

        # Create Shots Push Button
        self.create_shots_push_button = QtWidgets.QPushButton(self)
        self.create_shots_push_button.setText("Create")
        self.main_layout.addWidget(self.create_shots_push_button)

        # setup signals
        # Add Clip Push Button
        QtCore.QObject.connect(
            self.add_clip_field_push_button,
            QtCore.SIGNAL("clicked()"),
            self.add_clip_field
        )

        # Create Push Button
        QtCore.QObject.connect(
            self.create_shots_push_button,
            QtCore.SIGNAL("clicked()"),
            self.create_shots
        )

    def add_clip_field(self):
        """Adds a new clip field
        """
        new_clip_field = ClipFieldGrp()
        new_clip_field.create(self)
        self.clip_vertical_layout.addLayout(new_clip_field.layout)

        # also set previous and next fields
        previous_field = None
        if len(self.clip_fields):
            previous_field = self.clip_fields[-1]
            assert isinstance(previous_field, ClipFieldGrp)

        self.clip_fields.append(new_clip_field)
        new_clip_field._delete_callback = self._delete_child_callback

        if previous_field:
            new_clip_field.previous_field = previous_field
            previous_field.next_field = new_clip_field

        new_clip_field.shot_name_field.setText(
            str(len(self.clip_fields) * 10).zfill(4)
        )

    def create_shots(self):
        """creates shots
        """
        clip_data = []
        from anima.env.motion_builder import ClipData
        for clip_field in self.clip_fields:
            assert isinstance(clip_field, ClipFieldGrp)

            shot_name = clip_field.shot_name_field.text()
            fbx_path = clip_field.fbx_file_field.text()
            video_path = clip_field.video_file_field.text()
            cut_in = clip_field.cut_in_field.value()
            cut_out = clip_field.cut_out_field.value()
            fps = clip_field.fps_field.value()

            clip_data.append(
                ClipData(shot_name, fbx_path, video_path, cut_in, cut_out, fps)
            )

        from anima.env import motion_builder
        mb = motion_builder.MotionBuilder()
        mb.create_story(clip_data)

    def _delete_child_callback(self, child):
        """deletes ClipFieldGrp instances from the self.clip_fields

        :param child:
        :return:
        """
        self.clip_fields.remove(child)
