# -*- coding: utf-8 -*-
# Copyright (c) 2021, Mehmet Erer
#
# This module is part of anima and is released under the MIT
# License: http://www.opensource.org/licenses/MIT

import os
import re
import glob
import tempfile
from stalker import Project, Sequence, Scene, Shot, Task

from anima.ui.base import AnimaDialogBase, ui_caller
from anima.ui.lib import QtCore, QtWidgets
from anima.env import blackmagic
from anima.utils import do_db_setup

do_db_setup()

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s


def UI(app_in=None, executor=None, **kwargs):
    """
    :param app_in: A Qt Application instance, which you can pass to let the UI
      be attached to the given applications event process.

    :param executor: Instead of calling app.exec_ the UI will call this given
      function. It also passes the created app instance to this executor.

    """
    return ui_caller(app_in, executor, MainDialog, **kwargs)


class MainDialog(QtWidgets.QDialog, AnimaDialogBase):
    """Conformer MainDialog
    """

    def __init__(self, *args, **kwargs):
        super(MainDialog, self).__init__(*args, **kwargs)

        self.resolve = blackmagic.get_resolve()
        self.project = self.resolve.GetProjectManager().GetCurrentProject()

        xml_path = tempfile.gettempdir()
        xml_file_name = 'conformer___temp__1.8_fcpxml.fcpxml'
        xml_file_path = os.path.join(xml_path, xml_file_name)
        self.xml_path = xml_file_path

        self._setup_ui()

        self._setup_signals()

        self._set_defaults()

    def _setup_ui(self):
        """setups UI
        """
        bmgc_project_name = self.project.GetName()
        bmgc_project_fps = self.project.GetSetting('timelineFrameRate')

        self.setWindowTitle('Conformer')
        self.resize(500, 100)

        self.vertical_layout = QtWidgets.QVBoxLayout(self)

        self.bmgc_project_label = QtWidgets.QLabel(self.vertical_layout.widget())
        self.bmgc_project_label.setText('%s - [%s fps] / Resolve' % (bmgc_project_name, bmgc_project_fps))
        self.bmgc_project_label.setStyleSheet(_fromUtf8("color: rgb(71, 143, 202);\n""font: 12pt;"))
        self.vertical_layout.addWidget(self.bmgc_project_label)

        line = QtWidgets.QFrame(self.vertical_layout.parent())
        line.setFrameShape(QtWidgets.QFrame.HLine)
        line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.vertical_layout.addWidget(line)

        self.h_layout1 = QtWidgets.QHBoxLayout(self.vertical_layout.widget())

        self.stalker_project_label = QtWidgets.QLabel(self.h_layout1.widget())
        self.stalker_project_label.setText('Stalker Project:')
        self.h_layout1.addWidget(self.stalker_project_label)

        size_policy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        self.project_combo_box = QtWidgets.QComboBox(self.h_layout1.widget())
        self.project_combo_box.setSizePolicy(size_policy)
        self.h_layout1.addWidget(self.project_combo_box)

        self.vertical_layout.addLayout(self.h_layout1)

        self.h_layout2 = QtWidgets.QHBoxLayout(self.vertical_layout.widget())

        self.stalker_seq_label = QtWidgets.QLabel(self.h_layout2.widget())
        self.stalker_seq_label.setText('Stalker Seq:      ')
        self.h_layout2.addWidget(self.stalker_seq_label)

        size_policy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        self.seq_combo_box = QtWidgets.QComboBox(self.h_layout2.widget())
        self.seq_combo_box.setSizePolicy(size_policy)
        self.h_layout2.addWidget(self.seq_combo_box)

        self.vertical_layout.addLayout(self.h_layout2)

        self.h_layout3 = QtWidgets.QHBoxLayout(self.vertical_layout.widget())

        self.stalker_scene_label = QtWidgets.QLabel(self.h_layout3.widget())
        self.stalker_scene_label.setText('Stalker Scene:  ')
        self.h_layout3.addWidget(self.stalker_scene_label)

        size_policy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        self.scene_combo_box = QtWidgets.QComboBox(self.h_layout3.widget())
        self.scene_combo_box.setSizePolicy(size_policy)
        self.h_layout3.addWidget(self.scene_combo_box)

        self.vertical_layout.addLayout(self.h_layout3)

        self.h_layout_shots = QtWidgets.QHBoxLayout(self.vertical_layout.widget())

        self.shot_in_label = QtWidgets.QLabel(self.h_layout_shots.widget())
        self.shot_in_label.setText('Shot In:')
        self.h_layout_shots.addWidget(self.shot_in_label)

        size_policy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        self.shot_in_combo_box = QtWidgets.QComboBox(self.h_layout_shots.widget())
        self.shot_in_combo_box.setSizePolicy(size_policy)
        self.h_layout_shots.addWidget(self.shot_in_combo_box)

        self.shot_out_label = QtWidgets.QLabel(self.h_layout_shots.widget())
        self.shot_out_label.setText('Shot Out:')
        self.h_layout_shots.addWidget(self.shot_out_label)

        size_policy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        self.shot_out_combo_box = QtWidgets.QComboBox(self.h_layout_shots.widget())
        self.shot_out_combo_box.setSizePolicy(size_policy)
        self.h_layout_shots.addWidget(self.shot_out_combo_box)

        self.vertical_layout.addLayout(self.h_layout_shots)

        self.h_layout4 = QtWidgets.QHBoxLayout(self.vertical_layout.widget())

        self.width_label = QtWidgets.QLabel(self.h_layout4.widget())
        self.width_label.setText('Width:')
        self.h_layout4.addWidget(self.width_label)

        self.width_line = QtWidgets.QLineEdit(self.h_layout4.widget())
        self.width_line.setText('-')
        self.width_line.setEnabled(0)
        self.h_layout4.addWidget(self.width_line)

        self.height_label = QtWidgets.QLabel(self.h_layout4.widget())
        self.height_label.setText('Height:')
        self.h_layout4.addWidget(self.height_label)

        self.height_line = QtWidgets.QLineEdit(self.h_layout4.widget())
        self.height_line.setText('-')
        self.height_line.setEnabled(0)
        self.h_layout4.addWidget(self.height_line)

        self.fps_label = QtWidgets.QLabel(self.h_layout4.widget())
        self.fps_label.setText('Fps:')
        self.h_layout4.addWidget(self.fps_label)

        self.fps_line = QtWidgets.QLineEdit(self.h_layout4.widget())
        self.fps_line.setText('-')
        self.fps_line.setEnabled(0)
        self.h_layout4.addWidget(self.fps_line)

        self.vertical_layout.addLayout(self.h_layout4)

        self.h_layout5 = QtWidgets.QHBoxLayout(self.vertical_layout.widget())

        self.task_name_label = QtWidgets.QLabel(self.h_layout5.widget())
        self.task_name_label.setText('Task Name:')
        self.h_layout5.addWidget(self.task_name_label)

        size_policy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        self.task_name_combo_box = QtWidgets.QComboBox(self.h_layout5.widget())
        self.task_name_combo_box.setSizePolicy(size_policy)
        self.h_layout5.addWidget(self.task_name_combo_box)

        self.ext_name_label = QtWidgets.QLabel(self.h_layout5.widget())
        self.ext_name_label.setText('Extension:')
        self.h_layout5.addWidget(self.ext_name_label)

        size_policy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        self.ext_name_combo_box = QtWidgets.QComboBox(self.h_layout5.widget())
        self.ext_name_combo_box.setSizePolicy(size_policy)
        self.h_layout5.addWidget(self.ext_name_combo_box)

        self.alpha_only_check_box = QtWidgets.QCheckBox(self.h_layout5.widget())
        self.alpha_only_check_box.setText('Alpha Only')
        self.h_layout5.addWidget(self.alpha_only_check_box)

        self.vertical_layout.addLayout(self.h_layout5)

        self.conform_button = QtWidgets.QPushButton(self.vertical_layout.widget())
        self.conform_button.setText('CONFORM ALL')
        self.vertical_layout.addWidget(self.conform_button)

        line1 = QtWidgets.QFrame(self.vertical_layout.parent())
        line1.setFrameShape(QtWidgets.QFrame.HLine)
        line1.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.vertical_layout.addWidget(line1)

        self.h_layout6 = QtWidgets.QHBoxLayout(self.vertical_layout.widget())

        self.date_label = QtWidgets.QLabel(self.h_layout6.widget())
        self.date_label.setText('check From:')
        self.date_label.setAlignment(QtCore.Qt.AlignCenter)
        self.h_layout6.addWidget(self.date_label)

        self.start_date = QtWidgets.QDateEdit(self.h_layout6.widget())
        self.start_date.setDate(QtCore.QDate(2021, 1, 1))
        self.start_date.setCurrentSection(QtWidgets.QDateTimeEdit.MonthSection)
        self.start_date.setCalendarPopup(True)
        self.h_layout6.addWidget(self.start_date)

        self.now_label = QtWidgets.QLabel(self.h_layout6.widget())
        self.now_label.setText(':until Now')
        self.now_label.setAlignment(QtCore.Qt.AlignCenter)
        self.h_layout6.addWidget(self.now_label)

        self.vertical_layout.addLayout(self.h_layout6)

        self.updated_shot_list = QtWidgets.QListWidget(self.vertical_layout.widget())
        self.updated_shot_list.setSelectionMode(QtWidgets.QAbstractItemView.NoSelection)
        self.vertical_layout.addWidget(self.updated_shot_list)

        self.status_button= QtWidgets.QPushButton(self.vertical_layout.widget())
        self.status_button.setText('LIST UPDATED SHOTS')
        self.vertical_layout.addWidget(self.status_button)

        self.conform_updates_button= QtWidgets.QPushButton(self.vertical_layout.widget())
        self.conform_updates_button.setText('CONFORM UPDATED SHOTS ONLY')
        self.vertical_layout.addWidget(self.conform_updates_button)

        line2 = QtWidgets.QFrame(self.vertical_layout.parent())
        line2.setFrameShape(QtWidgets.QFrame.HLine)
        line2.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.vertical_layout.addWidget(line2)

        self.info_label = QtWidgets.QLabel(self.vertical_layout.widget())
        self.info_label.setText('check Console for Progress Info...')
        self.vertical_layout.addWidget(self.info_label)

        self.fill_ui_with_stalker_projects()

    def _setup_signals(self):
        """setups signals
        """
        # project_combo_box is changed
        QtCore.QObject.connect(
            self.project_combo_box,
            QtCore.SIGNAL('currentIndexChanged(QString)'),
            self.project_combo_box_changed
        )

        # seq_combo_box is changed
        QtCore.QObject.connect(
            self.seq_combo_box,
            QtCore.SIGNAL('currentIndexChanged(QString)'),
            self.seq_combo_box_changed
        )

        # scene_combo_box is changed
        QtCore.QObject.connect(
            self.scene_combo_box,
            QtCore.SIGNAL('currentIndexChanged(QString)'),
            self.scene_combo_box_changed
        )

        # shot_in_combo_box is changed
        QtCore.QObject.connect(
            self.shot_in_combo_box,
            QtCore.SIGNAL('currentIndexChanged(QString)'),
            self.shot_in_combo_box_changed
        )

        # shot_out_combo_box is changed
        QtCore.QObject.connect(
            self.shot_out_combo_box,
            QtCore.SIGNAL('currentIndexChanged(QString)'),
            self.shot_out_combo_box_changed
        )

        # conform_button is clicked
        QtCore.QObject.connect(
            self.conform_button,
            QtCore.SIGNAL("clicked()"),
            self.conform
        )

        # status_button is clicked
        QtCore.QObject.connect(
            self.status_button,
            QtCore.SIGNAL("clicked()"),
            self.list_shot_update_status
        )

        # conform_updates_button is clicked
        QtCore.QObject.connect(
            self.conform_updates_button,
            QtCore.SIGNAL("clicked()"),
            self.conform_updated_shots
        )

    def _set_defaults(self):
        """sets defaults for UI
        """
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)

        self.seq_combo_box.clear()
        self.seq_combo_box.setEnabled(0)

        self.scene_combo_box.clear()
        self.scene_combo_box.setEnabled(0)

        self.shot_in_combo_box.clear()
        self.shot_in_combo_box.setEnabled(0)

        self.shot_out_combo_box.clear()
        self.shot_out_combo_box.setEnabled(0)

        self.task_name_combo_box.addItem('Comp', -1)

        self.ext_name_combo_box.addItem('exr', -1)
        self.ext_name_combo_box.addItem('png', 0)
        self.ext_name_combo_box.addItem('tga', 1)
        self.ext_name_combo_box.addItem('jpg', 2)

    # TODO: seeing stalker ids in UI might be confusing... keep id data hidden
    def add_data_as_text_to_ui(self, name, task_id):
        """returns a predefined text to combo boxes for this UI
        """
        return '%s - [%s]' % (name, task_id)

    def get_id_from_data_text(self, text):
        """separates id from combo box texts added with add_data_as_text_to_ui() for this UI
        """
        task_id = None
        try:
            task_id = text.split(' - [')[1].strip(']')
        except IndexError:
            pass
        return task_id

    def get_name_from_data_text(self, text):
        """separates name from combo box texts added with add_data_as_text_to_ui() for this UI
        """
        name = None
        try:
            name = text.split(' - [')[0]
        except IndexError:
            pass
        return name

    def fill_ui_with_stalker_projects(self):
        """fills project_combo_box with stalker projects in UI
        """
        projects = Project.query.order_by(Project.name).all()

        self.project_combo_box.clear()
        self.project_combo_box.addItem('Select Project...', -1)
        for project in projects:
            self.project_combo_box.addItem(self.add_data_as_text_to_ui(project.name, project.id))

    def project_combo_box_changed(self):
        """runs when the project_combo_box is changed
        """
        self.updated_shot_list.clear()
        if self.project_combo_box.currentText() == 'Select Project...':
            self.seq_combo_box.clear()
            self.seq_combo_box.setEnabled(0)
            self.scene_combo_box.clear()
            self.scene_combo_box.setEnabled(0)
            self.shot_in_combo_box.clear()
            self.shot_in_combo_box.setEnabled(0)
            self.shot_out_combo_box.clear()
            self.shot_out_combo_box.setEnabled(0)
        else:
            sequences = []
            stalker_project_text = self.project_combo_box.currentText()
            p_id = self.get_id_from_data_text(stalker_project_text)
            stalker_project = Project.query.get(p_id)

            self.seq_combo_box.clear()
            self.seq_combo_box.setEnabled(1)
            self.seq_combo_box.addItem('ALL', -1)
            for sequence in stalker_project.sequences:
                sequences.append(self.add_data_as_text_to_ui(sequence.name, sequence.id))

            sequences.sort()
            for item in sequences:
                self.seq_combo_box.addItem(item)

            self.scene_combo_box.clear()
            self.scene_combo_box.setEnabled(0)

            self.fps_line.setText('%s' % stalker_project.fps)
            self.width_line.setText('%s' % stalker_project.image_format.width)
            self.height_line.setText('%s' % stalker_project.image_format.height)

    def seq_combo_box_changed(self):
        """runs when the seq_combo_box is changed
        """
        self.updated_shot_list.clear()
        # fill scene_combo_box with scenes only if a sequence is selected
        if self.seq_combo_box.currentText() == 'ALL':
            self.scene_combo_box.clear()
            self.scene_combo_box.setEnabled(0)
            self.shot_in_combo_box.clear()
            self.shot_in_combo_box.setEnabled(0)
            self.shot_out_combo_box.clear()
            self.shot_out_combo_box.setEnabled(0)
        else:
            stalker_seq_text = self.seq_combo_box.currentText()
            seq_id = self.get_id_from_data_text(stalker_seq_text)
            if seq_id:
                scenes = []
                stalker_seq = Sequence.query.get(seq_id)

                self.scene_combo_box.clear()
                self.scene_combo_box.setEnabled(1)
                self.scene_combo_box.addItem('ALL', -1)
                # assume that scenes are 1st level children of sequences (default in Anima Pipeline Structure)
                for task in stalker_seq.children:
                    if isinstance(task, Scene):
                        scenes.append(self.add_data_as_text_to_ui(task.name, task.id))
                    else:
                        try:
                            if task.type.name == 'Scene':
                                scenes.append(self.add_data_as_text_to_ui(task.name, task.id))
                        except AttributeError:
                            pass

                scenes.sort()
                for item in scenes:
                    self.scene_combo_box.addItem(item)

    def scene_combo_box_changed(self):
        """runs when the scene_combo_box is changed
        """
        self.updated_shot_list.clear()
        stalker_project_text = self.project_combo_box.currentText()
        p_id = self.get_id_from_data_text(stalker_project_text)

        if p_id:
            stalker_project = Project.query.get(p_id)

            if self.scene_combo_box.currentText() == 'ALL':
                self.shot_in_combo_box.clear()
                self.shot_in_combo_box.setEnabled(0)
                self.shot_out_combo_box.clear()
                self.shot_out_combo_box.setEnabled(0)

                # Set properties from Project instance
                self.fps_line.setText('%s' % stalker_project.fps)
                self.width_line.setText('%s' % stalker_project.image_format.width)
                self.height_line.setText('%s' % stalker_project.image_format.height)
            else:
                scene_text = self.scene_combo_box.currentText()
                sc_id = self.get_id_from_data_text(scene_text)

                if sc_id:
                    scene = Task.query.get(sc_id)
                    # shots under different scenes might have various res, fps properties under same seq or project
                    # set properties from first shot under Scene (assume all shots under scene have the same res,fps)
                    for t in scene.walk_hierarchy():
                        if isinstance(t, Shot):
                            self.fps_line.setText('%s' % t.fps)
                            self.width_line.setText('%s' % t.image_format.width)
                            self.height_line.setText('%s' % t.image_format.height)
                            break

                    # fill shot_in_combo_box with shots
                    shots = []
                    stalker_seq_text = self.seq_combo_box.currentText()
                    stalker_seq = Sequence.query.get(self.get_id_from_data_text(stalker_seq_text))
                    for shot in stalker_seq.shots:
                        if scene in shot.parents:
                            shots.append(self.add_data_as_text_to_ui(shot.name, shot.id))
                    shots.sort()

                    self.shot_in_combo_box.clear()
                    self.shot_in_combo_box.setEnabled(1)
                    self.shot_in_combo_box.addItem('ALL', -1)
                    for item in shots:
                        self.shot_in_combo_box.addItem(item)

    def shot_in_combo_box_changed(self):
        """runs when the shot_in_combo_box is changed
        """
        # fills shot_out_combo_box with shots
        self.updated_shot_list.clear()
        shot_in_text = self.shot_in_combo_box.currentText()
        s_id = self.get_id_from_data_text(shot_in_text)

        if shot_in_text == 'ALL':
            self.shot_out_combo_box.clear()
            self.shot_out_combo_box.setEnabled(0)
        else:
            scene_text = self.scene_combo_box.currentText()
            sc_id = self.get_id_from_data_text(scene_text)
            seq_text = self.seq_combo_box.currentText()
            seq_id = self.get_id_from_data_text(seq_text)
            if s_id and sc_id and seq_id:
                shot_in = Shot.query.get(s_id)
                shot_in_num = int(shot_in.name.split('_')[-1])
                seq = Sequence.query.get(seq_id)
                scene = Task.query.get(sc_id)

                shots = []
                for shot in seq.shots:
                    if scene in shot.parents and int(shot.name.split('_')[-1]) > shot_in_num:
                        shots.append(self.add_data_as_text_to_ui(shot.name, shot.id))
                shots.sort()

                self.shot_out_combo_box.clear()
                self.shot_out_combo_box.setEnabled(1)
                for item in shots:
                    self.shot_out_combo_box.addItem(item)

    def shot_out_combo_box_changed(self):
        """runs when the shot_out_combo_box is changed
        """
        self.updated_shot_list.clear()

    def get_shots_from_ui(self):
        """returns Stalker Shot instances as a list based on selection from UI
        """
        # return if a project is not selected from ui
        if self.project_combo_box.currentText() == 'Select Project...':
            QtWidgets.QMessageBox.critical(
                    self,
                    'Error',
                    'Please Select a Stalker Project.'
            )
            return

        shots = []

        stalker_project_text = self.project_combo_box.currentText()
        p_id = self.get_id_from_data_text(stalker_project_text)
        stalker_project = Project.query.get(p_id)

        if self.seq_combo_box.currentText() == 'ALL':
            for sequence in stalker_project.sequences:
                for shot in sequence.shots:
                    shots.append(shot)
        else:
            stalker_seq_text = self.seq_combo_box.currentText()
            stalker_seq = Sequence.query.get(self.get_id_from_data_text(stalker_seq_text))
            if self.scene_combo_box.currentText() == 'ALL':
                for shot in stalker_seq.shots:
                    shots.append(shot)
            else:
                stalker_scene_text = self.scene_combo_box.currentText()
                stalker_scene = Task.query.get(self.get_id_from_data_text(stalker_scene_text))
                if self.shot_in_combo_box.currentText() == 'ALL':
                    for shot in stalker_seq.shots:
                        if stalker_scene in shot.parents:  # assume that a shot is always a parent of it's scene
                            shots.append(shot)
                else:
                    shot_in_text = self.shot_in_combo_box.currentText()
                    shot_in_id = self.get_id_from_data_text(shot_in_text)
                    shot_out_text = self.shot_out_combo_box.currentText()
                    shot_out_id = self.get_id_from_data_text(shot_out_text)
                    if shot_in_id and shot_out_id:
                        shot_in = Shot.query.get(shot_in_id)
                        shot_out = Shot.query.get(shot_out_id)
                        shot_in_num = int(shot_in.name.split('_')[-1])
                        shot_out_num = int(shot_out.name.split('_')[-1])
                        for shot in stalker_seq.shots:
                            shot_num = int(shot.name.split('_')[-1])
                            if stalker_scene in shot.parents and shot_in_num <= shot_num <= shot_out_num:
                                shots.append(shot)

        if not shots:
            QtWidgets.QMessageBox.critical(
                    self,
                    'Error',
                    'No Valid Shots found!.'
            )

        return shots

    def get_latest_output_path(self, shot, task_name, ext='exr'):
        """returns the Output/Main outputs path for resolve from a given Shot stalker instance
        """
        comp_task = Task.query.filter(Task.parent == shot).filter(Task.name == task_name).first()
        comp_path = comp_task.absolute_path
        output_path = os.path.join(comp_path, 'Outputs', 'Main')

        latest_comp_name = None
        if comp_task.versions:
            latest_comp_version = comp_task.versions[0].latest_version
            latest_comp_name = latest_comp_version.filename.strip('.comp')

        resolve_path = None
        if latest_comp_name:
            if not self.alpha_only_check_box.isChecked():
                file_paths = glob.glob("%s/*/%s/*%s.*.%s" % (output_path, ext, latest_comp_name, ext))
                if not file_paths:  # try outputs with no version folders
                    file_paths = glob.glob("%s/%s/*%s.*.%s" % (output_path, ext, latest_comp_name, ext))
            else:  # check for paths that contain "alpha" as text
                version_folder = latest_comp_name.split('_')[-1]
                file_paths = glob.glob("%s/%s/%s/*%s*.*.%s" % (output_path, version_folder, ext, 'alpha', ext))
                if not file_paths:  # try outputs with no version folders
                    file_paths = glob.glob("%s/%s/*%s*%s.*.%s" % (output_path, ext, 'alpha', version_folder, ext))

            if file_paths:
                regex = r'\d+$|#+$'
                dir_base = file_paths[0].split('.')[0]
                first_dir_base = os.path.splitext(file_paths[0])[0]
                first_frame = re.findall(regex, first_dir_base)
                last_dir_base = os.path.splitext(file_paths[-1])[0]
                last_frame = re.findall(regex, last_dir_base)
                resolve_path = '%s.[%s-%s].%s' % (dir_base, first_frame[0], last_frame[0], ext)
                resolve_path = os.path.normpath(resolve_path).replace('\\', '/')

        return resolve_path

    def create_resolve_timeline_from_clips(self, timeline_name, clip_paths):
        """creates timeline in resolve from given clip paths
        """
        print '---------Started creating Timeline----------'
        media_pool = self.project.GetMediaPool()
        media_storage = self.resolve.GetMediaStorage()

        clips = media_storage.AddItemListToMediaPool(clip_paths)
        media_pool.CreateTimelineFromClips(timeline_name, clips)
        print '---------Finished creating Timeline----------'

    # TODO: getting timecode from image must be done with proper exif library that supports any platform
    def get_timecode_from_image(self, fps, img_path):
        """queries timecode metadata from given image
        """
        import subprocess
        import timecode

        frame_number = 0

        info = {}
        exif_path = 'T:/DEV/lib/windows/py2/__extras__/exiftool.exe'
        process = subprocess.Popen([exif_path, img_path],
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.STDOUT,
                                   universal_newlines=True)

        for tag in process.stdout:
            line = tag.strip().split(':')
            info[line[0].strip()] = line[-1].strip()
        
        try:
            tc_exif = info['Time Code'].split(' ')[0]
            t = timecode.Timecode('%s' % fps, start_timecode=int(tc_exif))
            frame_number = t.frame_number
        except BaseException:
            pass

        print '[%s] frame number returned from [%s]' % (frame_number, os.path.basename(img_path))
        
        return frame_number

    # TODO: XML creation must be done better with Anima pipeline's xml class
    def clip_paths_to_xml(self, clip_path_list, xml_file_full_path):
        """creates fcpxml1.8 compatible xml file from given Resolve image sequence paths
        """
        import math
        import datetime

        today = datetime.datetime.today()
        now = '%s_%s_%s' % (today.hour, today.minute, today.second)
        proj_name = self.get_name_from_data_text(self.project_combo_box.currentText())
        seq_name = self.get_name_from_data_text(self.seq_combo_box.currentText())
        scn_name = self.get_name_from_data_text(self.scene_combo_box.currentText())
        extension = self.ext_name_combo_box.currentText()

        width = self.width_line.text()
        height = self.height_line.text()
        fps = self.fps_line.text()
        # for some reason fcpxml does not like float fps like 24.0
        # if the decimal is .0 than fps must be integer 24 so...
        if float(fps)/math.trunc(float(fps)) == 1.0:
            fps = '%s' % math.trunc(float(fps))

        timeline_name = '%s_%s_%s_%s' % (proj_name, seq_name, scn_name, now)

        with open(xml_file_full_path, 'w') as f:
            f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
            f.write('<!DOCTYPE fcpxml>\n')
            f.write('<fcpxml version="1.8">\n')
            f.write('    <resources>\n')
            f.write('        <format height="%s" '
                    'width="%s" id="r0" '
                    'frameDuration="1/%ss"/>\n' % (height, width, fps))
            ind = 0
            seq_frames = 0
            tc_frame_numbers = []
            for clip_path in clip_path_list:
                ind += 1
                first_frame = int(clip_path.split('.')[-2].split('-')[0].strip('['))
                last_frame = int(clip_path.split('.')[-2].split('-')[1].strip(']'))
                total_frames = (last_frame - first_frame) + 1
                seq_frames += total_frames
                str_first_frame = clip_path.split('.')[-2].split('-')[0].strip('[')
                first_image_path = '%s.%s.%s' % ('.'.join(clip_path.split('.')[:-2]), str_first_frame, extension)
                st = self.get_timecode_from_image(fps, first_image_path)
                tc_frame_numbers.append(st)
                f.write('        <asset src="file://localhost/%s" '
                        'duration="%s/%ss" '
                        'hasVideo="1" '
                        'id="r%s" '
                        'format="r0" '
                        'name="%s" '
                        'start="%s/%ss"/>\n' % (clip_path, str(total_frames), fps, str(ind),
                                                os.path.basename(clip_path), str(st), fps))
            f.write('    </resources>\n')
            f.write('    <library>\n')
            f.write('        <event name="%s">\n' % timeline_name)
            f.write('            <project name="%s">\n' % timeline_name)
            f.write('                <sequence duration="%s/%ss" tcFormat="NDF" '
                    'format="r0" tcStart="0/1s">\n' % (str(seq_frames), fps))
            f.write('                    <spine>\n')
            ind = 0
            offset_frame = 0
            for clip_path in clip_path_list:
                ind += 1
                first_frame = int(clip_path.split('.')[-2].split('-')[0].strip('['))
                last_frame = int(clip_path.split('.')[-2].split('-')[1].strip(']'))
                total_frames = (last_frame - first_frame) + 1
                st = tc_frame_numbers[ind-1]
                f.write('                        <asset-clip offset="%s/%ss" duration="%s/%ss" '
                        'tcFormat="NDF" enabled="1" format="r0" ref="r%s" '
                        'name="%s" start="%s/%ss">\n' % (str(offset_frame), fps, str(total_frames), fps,
                                                         str(ind), os.path.basename(clip_path), str(st), fps))
                f.write('                            <adjust-transform position="0 0" '
                        'anchor="0 0" scale="1 1"/>\n')
                f.write('                        </asset-clip>\n')
                offset_frame += total_frames
            f.write('                    </spine>\n')
            f.write('                </sequence>\n')
            f.write('            </project>\n')
            f.write('        </event>\n')
            f.write('    </library>\n')
            f.write('</fcpxml>')

    def conform_shots(self, shots):
        """conforms given Stalker Shot instances from UI to a Timeline for Resolve
        """
        if shots:
            t_name = self.task_name_combo_box.currentText()
            extension = self.ext_name_combo_box.currentText()
            clip_path_list = []
            none_path_list = []
            for shot in shots:
                clip_path = self.get_latest_output_path(shot, t_name, ext=extension)
                if clip_path:
                    clip_path_list.append(clip_path)
                else:
                    none_path_list.append('%s -> No Outputs/Main found.' % shot.name)
                print 'Checking Shot... - %s' % shot.name
            clip_path_list.sort()
            none_path_list.sort()

            print '--------------------------------------------------------------------------'
            for clip_path in clip_path_list:
                print clip_path
            print '--------------------------------------------------------------------------'
            for none_path in none_path_list:
                print none_path
            print '--------------------------------------------------------------------------'

            if clip_path_list:
                self.clip_paths_to_xml(clip_path_list, self.xml_path)
                print 'XML CREATED----------------------------'

                media_pool = self.project.GetMediaPool()
                media_pool.ImportTimelineFromFile(self.xml_path)
                print 'XML IMPORTED to Resolve'
            else:
                print 'No Outputs found with given specs!'

            # self.create_resolve_timeline_from_clips(timeline_name, clip_path_list)

    def list_shot_update_status(self):
        """checks if shot outputs are updated based on version path modification date
        """
        import time
        import datetime

        start_date = self.start_date.date()
        query_date = datetime.datetime(start_date.year(), start_date.month(), start_date.day())

        shots = self.get_shots_from_ui()

        self.updated_shot_list.clear()

        if shots:
            update_list = []
            t_name = self.task_name_combo_box.currentText()
            for shot in shots:
                print 'Checking Shot... - %s' % shot.name
                comp_task = Task.query.filter(Task.parent == shot).filter(Task.name == t_name).first()

                if not comp_task:
                    continue

                if comp_task.versions:
                    last_version = comp_task.versions[0].latest_version
                else:
                    continue

                try:
                    raw_seconds = os.path.getmtime(last_version.absolute_full_path)

                    # If we are looking for *Alpha*, comp name will not match with outputs...
                    # because the output is rendered from Main take with a different saver path
                    # so we have to look for the first file rendered which had *Alpha* in its name
                    if self.alpha_only_check_box.isChecked():
                        ext = self.ext_name_combo_box.currentText()
                        comp_path = comp_task.absolute_path
                        output_path = os.path.join(comp_path, 'Outputs', 'Main')
                        latest_comp_name = last_version.filename.strip('.comp')
                        version_folder = latest_comp_name.split('_')[-1]
                        file_paths = glob.glob("%s/%s/%s/*%s*.*.%s" % (output_path, version_folder,
                                                                       ext, 'alpha', ext))
                        if not file_paths:  # try outputs with no version folders
                            file_paths = glob.glob("%s/%s/*%s*%s.*.%s" % (output_path, ext, 'alpha',
                                                                          version_folder, ext))
                        if file_paths:
                            raw_seconds = os.path.getmtime(file_paths[0])

                    local_time = time.localtime(raw_seconds)
                    modification_date = datetime.datetime(local_time.tm_year,
                                                          local_time.tm_mon,
                                                          local_time.tm_mday)

                    if modification_date > query_date:
                        update_info = '%s : %s > %s' % (
                            comp_task.parent.name,
                            modification_date,
                            last_version.updated_by.name
                        )
                        update_string = self.add_data_as_text_to_ui(update_info, shot.id)
                        update_list.append(update_string)
                except BaseException:
                    continue

            update_list.sort()
            for update_string in update_list:
                self.updated_shot_list.addItem(update_string)

    def conform(self):
        """conforms given Stalker Shot instances to a Timeline in Reolve
        """
        shots = self.get_shots_from_ui()
        self.conform_shots(shots)

    def conform_updated_shots(self):
        """conforms only updated shots from listWidget in UI
        """
        items = []
        for ind in range(self.updated_shot_list.count()):
            items.append(self.updated_shot_list.item(ind).text())

        shots = []
        for item in items:
            sh_id = self.get_id_from_data_text(item)
            if sh_id:
                sh = Shot.query.get(sh_id)
                shots.append(sh)

        self.conform_shots(shots)
