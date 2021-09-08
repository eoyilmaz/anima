# -*- coding: utf-8 -*-

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
    """Conformer MainDialog
    """

    def __init__(self, *args, **kwargs):
        super(MainDialog, self).__init__(*args, **kwargs)
        self.vertical_layout = None
        self._setup_ui()

    def _setup_ui(self):
        self.vertical_layout = QtWidgets.QVBoxLayout(self)
        ConformerUI(self.vertical_layout)
        self.setWindowTitle('Conformer')
        self.resize(500, 100)
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)


class ConformerUI(object):
    """The main class that creates the UI widgets
    """

    def __init__(self, layout):
        import os
        import tempfile
        from anima.env import blackmagic
        from anima.utils import do_db_setup

        self.main_layout = layout

        self.resolve = blackmagic.get_resolve()
        self.resolve_project = self.resolve.GetProjectManager().GetCurrentProject()

        xml_path = tempfile.gettempdir()
        xml_file_name = 'conformer___temp__1.8_fcpxml.fcpxml'
        xml_file_path = os.path.join(xml_path, xml_file_name)
        self.xml_path = xml_file_path

        do_db_setup()

        self._setup_ui()
        self._set_defaults()

    def _setup_ui(self):
        """setups UI
        """
        from functools import partial
        try:
            _fromUtf8 = QtCore.QString.fromUtf8
        except AttributeError:
            _fromUtf8 = lambda s: s

        self.parent_widget = self.main_layout.parent()

        self.resolve_project_label = QtWidgets.QLabel(self.parent_widget)
        self.resolve_project_label.setText(
            '%s - [%s fps] / Resolve' % (
                self.resolve_project.GetName(),
                self.resolve_project.GetSetting('timelineFrameRate'))
        )
        self.resolve_project_label.setStyleSheet(_fromUtf8("color: rgb(71, 143, 202);\n""font: 12pt;"))
        self.main_layout.addWidget(self.resolve_project_label)

        line = QtWidgets.QFrame(self.parent_widget)
        line.setFrameShape(QtWidgets.QFrame.HLine)
        line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.main_layout.addWidget(line)

        self.h_layout1 = QtWidgets.QHBoxLayout()

        self.stalker_project_label = QtWidgets.QLabel(self.parent_widget)
        self.stalker_project_label.setText('Stalker Project:')
        self.h_layout1.addWidget(self.stalker_project_label)

        size_policy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        # self.project_combo_box = QtWidgets.QComboBox(self.parent_widget)
        from anima.ui.widgets.project import ProjectComboBox
        self.project_combo_box = ProjectComboBox(self.parent_widget)
        self.project_combo_box.setSizePolicy(size_policy)
        self.project_combo_box.currentIndexChanged.connect(partial(self.project_combo_box_changed))
        self.h_layout1.addWidget(self.project_combo_box)

        self.main_layout.addLayout(self.h_layout1)

        self.h_layout2 = QtWidgets.QHBoxLayout()

        self.stalker_seq_label = QtWidgets.QLabel(self.parent_widget)
        self.stalker_seq_label.setText('Stalker Seq:      ')
        self.h_layout2.addWidget(self.stalker_seq_label)

        size_policy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        from anima.ui.widgets.sequence import SequenceComboBox
        # self.seq_combo_box = QtWidgets.QComboBox(self.parent_widget)
        self.seq_combo_box = SequenceComboBox(self.parent_widget)
        self.seq_combo_box.setSizePolicy(size_policy)
        self.seq_combo_box.currentIndexChanged.connect(partial(self.seq_combo_box_changed))
        self.h_layout2.addWidget(self.seq_combo_box)

        self.main_layout.addLayout(self.h_layout2)

        self.h_layout3 = QtWidgets.QHBoxLayout()

        self.stalker_scene_label = QtWidgets.QLabel(self.parent_widget)
        self.stalker_scene_label.setText('Stalker Scene:  ')
        self.h_layout3.addWidget(self.stalker_scene_label)

        size_policy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        self.scene_combo_box = QtWidgets.QComboBox(self.parent_widget)
        self.scene_combo_box.setSizePolicy(size_policy)
        self.scene_combo_box.currentIndexChanged.connect(partial(self.scene_combo_box_changed))
        self.h_layout3.addWidget(self.scene_combo_box)

        self.main_layout.addLayout(self.h_layout3)

        self.h_layout_shots = QtWidgets.QHBoxLayout()

        self.shot_in_label = QtWidgets.QLabel(self.parent_widget)
        self.shot_in_label.setText('Shot In:')
        self.h_layout_shots.addWidget(self.shot_in_label)

        size_policy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        self.shot_in_combo_box = QtWidgets.QComboBox(self.parent_widget)
        self.shot_in_combo_box.setSizePolicy(size_policy)
        self.shot_in_combo_box.currentIndexChanged.connect(partial(self.shot_in_combo_box_changed))
        self.h_layout_shots.addWidget(self.shot_in_combo_box)

        self.shot_out_label = QtWidgets.QLabel(self.parent_widget)
        self.shot_out_label.setText('Shot Out:')
        self.h_layout_shots.addWidget(self.shot_out_label)

        size_policy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        self.shot_out_combo_box = QtWidgets.QComboBox(self.parent_widget)
        self.shot_out_combo_box.setSizePolicy(size_policy)
        self.shot_out_combo_box.currentIndexChanged.connect(partial(self.shot_out_combo_box_changed))
        self.h_layout_shots.addWidget(self.shot_out_combo_box)

        self.main_layout.addLayout(self.h_layout_shots)

        self.h_layout4 = QtWidgets.QHBoxLayout()

        self.width_label = QtWidgets.QLabel(self.parent_widget)
        self.width_label.setText('Width:')
        self.h_layout4.addWidget(self.width_label)

        self.width_line = QtWidgets.QLineEdit(self.parent_widget)
        self.width_line.setText('-')
        self.width_line.setEnabled(0)
        self.h_layout4.addWidget(self.width_line)

        self.height_label = QtWidgets.QLabel(self.parent_widget)
        self.height_label.setText('Height:')
        self.h_layout4.addWidget(self.height_label)

        self.height_line = QtWidgets.QLineEdit(self.parent_widget)
        self.height_line.setText('-')
        self.height_line.setEnabled(0)
        self.h_layout4.addWidget(self.height_line)

        self.fps_label = QtWidgets.QLabel(self.parent_widget)
        self.fps_label.setText('Fps:')
        self.h_layout4.addWidget(self.fps_label)

        self.fps_line = QtWidgets.QLineEdit(self.parent_widget)
        self.fps_line.setText('-')
        self.fps_line.setEnabled(0)
        self.h_layout4.addWidget(self.fps_line)

        self.main_layout.addLayout(self.h_layout4)

        self.h_layout4a = QtWidgets.QHBoxLayout()

        self.filter_statuses_check_box = QtWidgets.QCheckBox(self.parent_widget)
        self.filter_statuses_check_box.setText('Filter Statuses')
        self.filter_statuses_check_box.stateChanged.connect(partial(self.filter_statuses_check_box_changed))
        self.h_layout4a.addWidget(self.filter_statuses_check_box)

        self.wip_check_box = QtWidgets.QCheckBox(self.parent_widget)
        self.wip_check_box.setText('WIP')
        self.h_layout4a.addWidget(self.wip_check_box)

        self.hrev_check_box = QtWidgets.QCheckBox(self.parent_widget)
        self.hrev_check_box.setText('HREV')
        self.h_layout4a.addWidget(self.hrev_check_box)

        self.prev_check_box = QtWidgets.QCheckBox(self.parent_widget)
        self.prev_check_box.setText('PREV')
        self.h_layout4a.addWidget(self.prev_check_box)

        self.completed_check_box = QtWidgets.QCheckBox(self.parent_widget)
        self.completed_check_box.setText('CMLT')
        self.h_layout4a.addWidget(self.completed_check_box)

        self.main_layout.addLayout(self.h_layout4a)

        self.h_layout5 = QtWidgets.QHBoxLayout()

        self.task_name_label = QtWidgets.QLabel(self.parent_widget)
        self.task_name_label.setText('Task Name:')
        self.h_layout5.addWidget(self.task_name_label)

        size_policy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        self.task_name_combo_box = QtWidgets.QComboBox(self.parent_widget)
        self.task_name_combo_box.setSizePolicy(size_policy)
        self.task_name_combo_box.currentIndexChanged.connect(partial(self.task_name_combo_box_changed))
        self.h_layout5.addWidget(self.task_name_combo_box)

        self.ext_name_label = QtWidgets.QLabel(self.parent_widget)
        self.ext_name_label.setText('Extension:')
        self.h_layout5.addWidget(self.ext_name_label)

        size_policy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        self.ext_name_combo_box = QtWidgets.QComboBox(self.parent_widget)
        self.ext_name_combo_box.setSizePolicy(size_policy)
        self.h_layout5.addWidget(self.ext_name_combo_box)

        self.plus_plates_check_box = QtWidgets.QCheckBox(self.parent_widget)
        self.plus_plates_check_box.setText('+ Plates')
        self.h_layout5.addWidget(self.plus_plates_check_box)

        self.alpha_only_check_box = QtWidgets.QCheckBox(self.parent_widget)
        self.alpha_only_check_box.setText('Alpha Only')
        self.h_layout5.addWidget(self.alpha_only_check_box)
        
        self.main_layout.addLayout(self.h_layout5)

        self.h_layout6 = QtWidgets.QHBoxLayout()

        self.record_in_check_box = QtWidgets.QCheckBox(self.parent_widget)
        self.record_in_check_box.setText('Record In')
        self.record_in_check_box.stateChanged.connect(partial(self.record_in_check_box_changed))
        self.h_layout6.addWidget(self.record_in_check_box)

        self.slated_check_box = QtWidgets.QCheckBox(self.parent_widget)
        self.slated_check_box.setText('Include Slates')
        self.slated_check_box.stateChanged.connect(partial(self.slated_check_box_changed))
        self.h_layout6.addWidget(self.slated_check_box)

        self.main_layout.addLayout(self.h_layout6)

        self.conform_button = QtWidgets.QPushButton(self.parent_widget)
        self.conform_button.setText('CONFORM ALL')
        self.conform_button.clicked.connect(partial(self.conform))
        self.main_layout.addWidget(self.conform_button)

        line1 = QtWidgets.QFrame(self.parent_widget)
        line1.setFrameShape(QtWidgets.QFrame.HLine)
        line1.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.main_layout.addWidget(line1)

        self.h_layout6 = QtWidgets.QHBoxLayout()

        self.date_label = QtWidgets.QLabel(self.parent_widget)
        self.date_label.setText('check From:')
        self.date_label.setAlignment(QtCore.Qt.AlignCenter)
        self.h_layout6.addWidget(self.date_label)

        self.start_date = QtWidgets.QDateEdit(self.parent_widget)
        self.start_date.setDate(QtCore.QDate.currentDate()) # setDate(QtCore.QDate(2021, 1, 1))
        self.start_date.setCurrentSection(QtWidgets.QDateTimeEdit.MonthSection)
        self.start_date.setCalendarPopup(True)
        self.h_layout6.addWidget(self.start_date)

        self.now_label = QtWidgets.QLabel(self.parent_widget)
        self.now_label.setText(':until Now')
        self.now_label.setAlignment(QtCore.Qt.AlignCenter)
        self.h_layout6.addWidget(self.now_label)

        self.main_layout.addLayout(self.h_layout6)

        self.updated_shot_list = QtWidgets.QListWidget(self.parent_widget)
        self.updated_shot_list.setSelectionMode(QtWidgets.QAbstractItemView.NoSelection)
        self.main_layout.addWidget(self.updated_shot_list)

        self.status_button= QtWidgets.QPushButton(self.parent_widget)
        self.status_button.setText('LIST UPDATED SHOTS')
        self.status_button.clicked.connect(partial(self.list_shot_update_status))
        self.main_layout.addWidget(self.status_button)

        self.conform_updates_button = QtWidgets.QPushButton(self.parent_widget)
        self.conform_updates_button.setText('CONFORM UPDATED SHOTS ONLY')
        self.conform_updates_button.clicked.connect(partial(self.conform_updated_shots))
        self.main_layout.addWidget(self.conform_updates_button)

        line2 = QtWidgets.QFrame(self.parent_widget)
        line2.setFrameShape(QtWidgets.QFrame.HLine)
        line2.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.main_layout.addWidget(line2)

        self.info_label = QtWidgets.QLabel(self.parent_widget)
        self.info_label.setText('check Console for Progress Info...')
        self.main_layout.addWidget(self.info_label)

    def _set_defaults(self):
        """sets defaults for UI
        """
        self.seq_combo_box.clear()
        self.seq_combo_box.setEnabled(0)

        self.scene_combo_box.clear()
        self.scene_combo_box.setEnabled(0)

        self.shot_in_combo_box.clear()
        self.shot_in_combo_box.setEnabled(0)

        self.shot_out_combo_box.clear()
        self.shot_out_combo_box.setEnabled(0)

        self.task_name_combo_box.addItem('Comp', -1)
        self.task_name_combo_box.addItem('Plate', 0)

        self.ext_name_combo_box.addItem('exr', -1)
        self.ext_name_combo_box.addItem('png', 0)
        self.ext_name_combo_box.addItem('tga', 1)
        self.ext_name_combo_box.addItem('jpg', 2)

        self.wip_check_box.setEnabled(0)
        self.hrev_check_box.setEnabled(0)
        self.prev_check_box.setChecked(1)
        self.prev_check_box.setEnabled(0)
        self.completed_check_box.setChecked(1)
        self.completed_check_box.setEnabled(0)

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

    def project_combo_box_changed(self, *args):
        """runs when the project_combo_box is changed
        """
        self.updated_shot_list.clear()
        stalker_project = self.project_combo_box.get_current_project()
        self.seq_combo_box.project = stalker_project

        if not stalker_project:
            self.seq_combo_box.setEnabled(0)
            self.scene_combo_box.clear()
            self.scene_combo_box.setEnabled(0)
            self.shot_in_combo_box.clear()
            self.shot_in_combo_box.setEnabled(0)
            self.shot_out_combo_box.clear()
            self.shot_out_combo_box.setEnabled(0)
        else:
            self.seq_combo_box.setEnabled(1)
            self.seq_combo_box.insertItem(0, 'ALL', -1)
            self.seq_combo_box.setCurrentIndex(0)

            self.fps_line.setText('%s' % stalker_project.fps)
            self.width_line.setText('%s' % stalker_project.image_format.width)
            self.height_line.setText('%s' % stalker_project.image_format.height)

    def seq_combo_box_changed(self, *args):
        """runs when the seq_combo_box is changed
        """
        self.updated_shot_list.clear()
        # fill scene_combo_box with scenes only if a sequence is selected

        stalker_seq = self.seq_combo_box.get_current_sequence()
        if not stalker_seq:
            self.scene_combo_box.clear()
            self.scene_combo_box.setEnabled(0)
            self.shot_in_combo_box.clear()
            self.shot_in_combo_box.setEnabled(0)
            self.shot_out_combo_box.clear()
            self.shot_out_combo_box.setEnabled(0)
        else:
            self.scene_combo_box.clear()
            self.scene_combo_box.setEnabled(1)
            self.scene_combo_box.addItem('ALL', -1)
            # assume that scenes are 1st level children of sequences (default in Anima Pipeline Structure)
            from stalker import Task, Type
            scene_type = Type.query.filter(Type.name == 'Scene').first()
            all_scenes = Task.query\
                .filter(Task.parent == stalker_seq)\
                .filter(Task.type == scene_type)\
                .order_by(Task.name)\
                .all()
            for task in all_scenes:
                self.scene_combo_box.addItem(task.name, task.id)

    def scene_combo_box_changed(self, *args):
        """runs when the scene_combo_box is changed
        """
        self.updated_shot_list.clear()
        project = self.project_combo_box.get_current_project()

        if project:
            scene_id = self.scene_combo_box.itemData(self.scene_combo_box.currentIndex())

            if scene_id in [-1, None]:
                self.shot_in_combo_box.clear()
                self.shot_in_combo_box.setEnabled(0)
                self.shot_out_combo_box.clear()
                self.shot_out_combo_box.setEnabled(0)

                # Set properties from Project instance
                self.fps_line.setText('%s' % project.fps)
                self.width_line.setText('%s' % project.image_format.width)
                self.height_line.setText('%s' % project.image_format.height)
            else:
                from stalker import Task, Shot, Sequence
                scene = Task.query.get(scene_id)
                # shots under different scenes might have various res, fps properties under same seq or project
                # set properties from first shot under Scene (assume all shots under scene have the same res,fps)
                for t in scene.walk_hierarchy():
                    if isinstance(t, Shot):
                        self.fps_line.setText('%s' % t.fps)
                        self.width_line.setText('%s' % t.image_format.width)
                        self.height_line.setText('%s' % t.image_format.height)
                        break

                # fill shot_in_combo_box with shots
                self.shot_in_combo_box.clear()
                self.shot_in_combo_box.setEnabled(1)
                self.shot_in_combo_box.addItem('ALL', -1)

                seq = self.seq_combo_box.get_current_sequence()
                shots = Shot.query.filter(Shot.sequences.contains(seq)).order_by(Shot.name).all()
                for shot in shots:
                    if scene in shot.parents:
                        self.shot_in_combo_box.addItem(shot.name, shot.id)

    def shot_in_combo_box_changed(self, *args):
        """runs when the shot_in_combo_box is changed
        """
        # fills shot_out_combo_box with shots
        self.updated_shot_list.clear()
        shot_id = self.shot_in_combo_box.itemData(self.shot_in_combo_box.currentIndex())
        if shot_id in [-1, None]:
            self.shot_out_combo_box.clear()
            self.shot_out_combo_box.setEnabled(0)
        else:
            scene_id = self.scene_combo_box.itemData(self.scene_combo_box.currentIndex())
            seq_id = self.seq_combo_box.itemData(self.seq_combo_box.currentIndex())

            from stalker import Task, Shot, Sequence
            shot_in = Shot.query.get(shot_id)
            shot_in_num = int(shot_in.name.split('_')[-1])
            seq = Sequence.query.get(seq_id)
            scene = Task.query.get(scene_id)

            self.shot_out_combo_box.clear()
            self.shot_out_combo_box.setEnabled(1)
            shots = Shot.query.filter(Shot.sequences.contains(seq)).order_by(Shot.name).all()
            for shot in shots:
                if scene in shot.parents and int(shot.name.split('_')[-1]) >= shot_in_num:
                    self.shot_out_combo_box.addItem(shot.name, shot.id)

    def shot_out_combo_box_changed(self, *args):
        """runs when the shot_out_combo_box is changed
        """
        self.updated_shot_list.clear()

    def task_name_combo_box_changed(self, *args):
        """runs when the task_name_combo_box is changed
        """
        task_in_text = self.task_name_combo_box.currentText()
        if task_in_text == 'Comp':
            self.alpha_only_check_box.setChecked(0)
            self.alpha_only_check_box.setEnabled(1)
            self.plus_plates_check_box.setChecked(0)
            self.plus_plates_check_box.setEnabled(1)
        else:
            self.alpha_only_check_box.setChecked(0)
            self.alpha_only_check_box.setEnabled(0)
            self.plus_plates_check_box.setChecked(0)
            self.plus_plates_check_box.setEnabled(0)   

    def filter_statuses_check_box_changed(self, state):
        """runs when the filter_status_check_box is changed
        """
        if state == 0:
            self.wip_check_box.setEnabled(0)
            self.hrev_check_box.setEnabled(0)
            self.prev_check_box.setEnabled(0)
            self.completed_check_box.setEnabled(0)
        else:
            self.wip_check_box.setEnabled(1)
            self.hrev_check_box.setEnabled(1)
            self.prev_check_box.setEnabled(1)
            self.completed_check_box.setEnabled(1)

    def slated_check_box_changed(self, state):
        """runs when the slated_check_box is changed
        """
        if state != 0:
            self.record_in_check_box.setChecked(0)
            self.record_in_check_box.setEnabled(0)
        else:
            self.record_in_check_box.setEnabled(1)

    def record_in_check_box_changed(self, state):
        """runs when the slated_check_box is changed
        """
        if state != 0:
            self.slated_check_box.setChecked(0)
            self.slated_check_box.setEnabled(0)
        else:
            self.slated_check_box.setEnabled(1)

    def get_shots_from_ui(self):
        """returns Stalker Shot instances as a list based on selection from UI
        """
        # return if a project is not selected from ui
        stalker_project = self.project_combo_box.get_current_project()
        if not stalker_project:
            QtWidgets.QMessageBox.critical(
                self.parent_widget,
                'Error',
                'Please Select a Stalker Project.'
            )
            return

        shots = []

        from stalker import Sequence, Task, Shot

        if self.seq_combo_box.currentText() == 'ALL':
            for sequence in stalker_project.sequences:
                shots += sequence.shots
        else:
            stalker_seq = self.seq_combo_box.get_current_sequence()
            if self.scene_combo_box.currentText() == 'ALL':
                shots += stalker_seq.shots
            else:
                stalker_scene = Task.query.get(self.scene_combo_box.itemData(self.scene_combo_box.currentIndex()))
                if self.shot_in_combo_box.currentText() == 'ALL':
                    for shot in stalker_seq.shots:
                        if stalker_scene in shot.parents:  # assume that a shot is always a parent of it's scene
                            shots.append(shot)
                else:
                    shot_in_id = self.shot_in_combo_box.itemData(self.shot_in_combo_box.currentIndex())
                    shot_out_id = self.shot_out_combo_box.itemData(self.shot_out_combo_box.currentIndex())
                    if shot_in_id and shot_out_id:
                        shot_in = Shot.query.get(shot_in_id)
                        shot_out = Shot.query.get(shot_out_id)
                        shot_in_num = int(shot_in.name.split('_')[-1])
                        shot_out_num = int(shot_out.name.split('_')[-1])
                        for shot in stalker_seq.shots:
                            shot_num = int(shot.name.split('_')[-1])
                            if stalker_scene in shot.parents \
                               and shot_in_num <= shot_num <= shot_out_num \
                               and shot not in shots:
                                shots.append(shot)

        if not shots:
            QtWidgets.QMessageBox.critical(
                self.parent_widget,
                'Error',
                'No Valid Shots found!.'
            )

        return shots

    def get_valid_statuses_from_ui(self):
        """returns valisd statuses from ui
        """
        valid_status_names = []
        
        if self.wip_check_box.isChecked():
            valid_status_names.append('Work In Progress')
        if self.hrev_check_box.isChecked():
            valid_status_names.append('Has Revision')
        if self.prev_check_box.isChecked():
            valid_status_names.append('Pending Review')
        if self.completed_check_box.isChecked():
            valid_status_names.append('Completed')
        
        return valid_status_names

    def get_latest_output_path(self, shot, task_name, ext='exr'):
        """returns the Output/Main outputs path for resolve from a given Shot stalker instance
        """
        import os
        import glob
        import re
        from stalker import Task, Version
        task = Task.query.filter(Task.parent == shot).filter(Task.name == task_name).first()
        if not task and task_name == 'Comp': # try Cleanup task
            task = Task.query.filter(Task.parent == shot).filter(Task.name == 'Cleanup').first()
        if not task:
            return None

        if self.filter_statuses_check_box.isChecked():
            if task_name != 'Plate': # do not check status for plates
                valid_status_names = self.get_valid_statuses_from_ui()
                if task.status.name not in valid_status_names:
                    print('%s -> %s' % (shot.name, task.status.name))
                    return None

        task_path = task.absolute_path
        output_path = os.path.join(task_path, 'Outputs', 'Main')

        latest_task_name = None
        if task.versions:
            latest_task_version = Version.query.filter(Version.task == task).filter(Version.take_name == 'Main')\
                .order_by(Version.version_number.desc()).first()
            if latest_task_version:
                latest_task_name = os.path.splitext(latest_task_version.filename)[0]

        resolve_path = None
        if latest_task_name:
            if not self.alpha_only_check_box.isChecked():
                file_paths = glob.glob("%s/*/%s/*%s.*.%s" % (output_path, ext, latest_task_name, ext))
                if not file_paths:  # try outputs with no version folders
                    file_paths = glob.glob("%s/%s/*%s.*.%s" % (output_path, ext, latest_task_name, ext))
            else:  # check for paths that contain "alpha" as text
                version_folder = latest_task_name.split('_')[-1]
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
        # try to find path manually for plate tasks as they might not have default naming conventions or versions
        if not resolve_path and task_name == 'Plate':
            version_numbers = []
            main_dir = os.path.join(shot.absolute_path, 'Plate', 'Outputs', 'Main')
            if os.path.isdir(main_dir):
                dirs = glob.glob('%s/*' % main_dir)
                for dir in dirs:
                    if os.path.isdir(dir) and os.path.basename(dir)[0] == 'v' \
                            and os.path.basename(dir)[1:].isdigit() and len(os.path.basename(dir)) == 4:
                        version_numbers.append(int(os.path.basename(dir)[1:]))
            if version_numbers:
                latest_version_number = max(version_numbers)
                latest_version_folder_name = 'v%s' % str(latest_version_number).rjust(3, '0')
                plate_path = os.path.join(main_dir, latest_version_folder_name, ext)
                plate_path = os.path.normpath(plate_path).replace('\\', '/')

                file_paths = glob.glob('%s/*.%s' %(plate_path, ext))

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
        print('---------Started creating Timeline----------')
        media_pool = self.resolve_project.GetMediaPool()
        media_storage = self.resolve.GetMediaStorage()

        clips = media_storage.AddItemListToMediaPool(clip_paths)
        media_pool.CreateTimelineFromClips(timeline_name, clips)
        print('---------Finished creating Timeline----------')

    # TODO: getting timecode from image must be done with proper exif library that supports any platform
    def get_timecode_from_image(self, fps, img_path):
        """queries timecode metadata from given image
        """
        import os
        import subprocess
        import timecode

        frame_number = 0

        info = {}
        process = subprocess.Popen(['exiftool', img_path],
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

        print('[%s] frame number returned from [%s]' % (frame_number, os.path.basename(img_path)))
        
        return frame_number

    # TODO: XML creation must be done better with Anima pipeline's xml class
    def clip_paths_to_xml(self, clip_path_list, record_in_list, xml_file_full_path):
        """creates fcpxml1.8 compatible xml file from given Resolve image sequence paths
        """
        import os
        import math
        import datetime

        today = datetime.datetime.today()
        now = '%s%s%s_%s%s%s' % (today.year,
                                 str(today.month).rjust(2, '0'),
                                 str(today.day).rjust(2, '0'),
                                 str(today.hour).rjust(2, '0'),
                                 str(today.minute).rjust(2, '0'),
                                 str(today.second).rjust(2, '0'))
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
            f.write('        <format '
                    'id="r0" '
                    'frameDuration="1/%ss"/>\n' % fps)
            ind = 0
            seq_frames = 0
            tc_frame_numbers = []
            rc_ins = []
            for clip_path in clip_path_list:
                ind += 1
                first_frame = int(clip_path.split('.')[-2].split('-')[0].strip('['))
                last_frame = int(clip_path.split('.')[-2].split('-')[1].strip(']'))
                total_frames = (last_frame - first_frame) + 1
                seq_frames += total_frames
                str_first_frame = clip_path.split('.')[-2].split('-')[0].strip('[')
                first_image_path = '%s.%s.%s' % ('.'.join(clip_path.split('.')[:-2]), str_first_frame, extension)

                rc_in = None
                if self.record_in_check_box.isChecked():
                    for record_in_data in record_in_list:
                        if record_in_data[0] == clip_path:
                            rc_in = record_in_data[1]
                            break
                    rc_ins.append(rc_in)

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
                if self.record_in_check_box.isChecked():
                    offset_frame = rc_ins[ind-1]
                st = tc_frame_numbers[ind-1]
                if self.slated_check_box.isChecked():
                    if not self.record_in_check_box.isChecked():
                        f.write('                        <asset-clip offset="%s/%ss" duration="%s/%ss" '
                                'tcFormat="NDF" enabled="1" format="r0" ref="r%s" '
                                'name="%s" start="%s/%ss">\n' % (str(offset_frame), fps, '1', fps,
                                                                 str(ind), os.path.basename(clip_path), str(st), fps))
                        f.write('                            <adjust-transform position="0 0" '
                                'anchor="0 0" scale="1 1"/>\n')
                        f.write('                        </asset-clip>\n')
                        offset_frame += 1
                    else:
                        slate_frame = offset_frame - 1
                        f.write('                        <asset-clip offset="%s/%ss" duration="%s/%ss" '
                                'tcFormat="NDF" enabled="1" format="r0" ref="r%s" '
                                'name="%s" start="%s/%ss">\n' % (str(slate_frame), fps, '1', fps,
                                                                 str(ind), os.path.basename(clip_path), str(st), fps))
                        f.write('                            <adjust-transform position="0 0" '
                                'anchor="0 0" scale="1 1"/>\n')
                        f.write('                        </asset-clip>\n')
                f.write('                        <asset-clip offset="%s/%ss" duration="%s/%ss" '
                        'tcFormat="NDF" enabled="1" format="r0" ref="r%s" '
                        'name="%s" start="%s/%ss">\n' % (str(offset_frame), fps, str(total_frames), fps,
                                                         str(ind), os.path.basename(clip_path), str(st), fps))
                f.write('                            <adjust-transform position="0 0" '
                        'anchor="0 0" scale="1 1"/>\n')
                f.write('                        </asset-clip>\n')
                if not self.record_in_check_box.isChecked():
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
            record_in_list = []
            clip_path_list = []
            plate_path_list = []
            plate_not_found_list = []
            plate_range_mismatch_list = []
            none_path_list = []
            for shot in shots:
                clip_path = self.get_latest_output_path(shot, t_name, ext=extension)
                if t_name == 'Comp' and clip_path is None: # look for Cleanup task
                    clip_path = self.get_latest_output_path(shot, 'Cleanup', ext=extension)       
                
                if clip_path:
                    clip_path_list.append(clip_path)
                elif clip_path is None:
                    none_path_list.append('%s -> No Outputs/Main found.' % shot.name)

                if t_name == 'Comp' and clip_path and self.plus_plates_check_box.isChecked():
                    plate_path = self.get_latest_output_path(shot, 'Plate', ext=extension)
                    if plate_path:
                        plate_path_list.append(plate_path)
                    elif clip_path: # add comp or cleanup clip to match timelines
                        plate_path_list.append(clip_path)
                        plate_not_found_list.append(clip_path)

                if self.record_in_check_box.isChecked():
                    rc_in = shot.record_in
                    if not rc_in:
                        raise RuntimeError('%s -> No record in data! Turn off Record In check box.' % shot.name)
                    record_in_list.append([clip_path, rc_in])

                print('Checking Shot... - %s' % shot.name)
            clip_path_list.sort()
            record_in_list.sort()
            none_path_list.sort()
            plate_path_list.sort()
            plate_not_found_list.sort()
            plate_range_mismatch_list.sort()

            if plate_path_list and self.plus_plates_check_box.isChecked():
                if len(clip_path_list) != len(plate_path_list):
                    print('--------------------------------------------------------------------------')
                    print('ERROR: Comp / Plate mismatch! Contact Supervisor.')
                    print('--------------------------------------------------------------------------')
                    raise RuntimeError('Comp / Plate mismatch! Contact Supervisor.')

                for i in range(0, len(clip_path_list)):
                    try:
                        import os
                        clip_range = os.path.basename(clip_path_list[i]).split('.')[1]
                        plate_range = os.path.basename(plate_path_list[i]).split('.')[1]
                        print('Clip: %s -> Plate: %s' % (clip_range, plate_range))
                        if clip_range != plate_range:
                            plate_range_mismatch_list.append(clip_path_list[i])
                    except IndexError:
                        pass

            print('--------------------------------------------------------------------------')
            for i in range(0, len(clip_path_list)):
                if plate_path_list and self.plus_plates_check_box.isChecked():
                    print('%s  +  %s' % (clip_path_list[i], plate_path_list[i]))
                else:    
                    print(clip_path_list[i])
            print('--------------------------------------------------------------------------')
            if none_path_list:
                for none_path in none_path_list:
                    print(none_path)
                print('--------------------------------------------------------------------------')
            if plate_not_found_list:
                print('--------------------------PLATES NOT FOUND--------------------------------')
                for p_path in plate_not_found_list:
                    print(p_path)
                print('--------------------------------------------------------------------------')
            if plate_range_mismatch_list:
                print('-----------------------PLATES RANGE MISMATCH------------------------------')
                for p_path in plate_range_mismatch_list:
                    print(p_path)
                print('--------------------------------------------------------------------------')        

            if clip_path_list:
                self.clip_paths_to_xml(clip_path_list, record_in_list, self.xml_path)
                print('XML CREATED----------------------------')

                media_pool = self.resolve_project.GetMediaPool()
                media_pool.ImportTimelineFromFile(self.xml_path)
                print('XML IMPORTED to Resolve')
                if plate_path_list and self.plus_plates_check_box.isChecked():
                    print('CREATING + PLATES XML... Please Wait... ----------------------------')
                    self.clip_paths_to_xml(plate_path_list, record_in_list, self.xml_path)
                    print('+ PLATES XML CREATED----------------------------')
                    media_pool = self.resolve_project.GetMediaPool()
                    media_pool.ImportTimelineFromFile(self.xml_path)
                    print('+ PLATES XML IMPORTED to Resolve')
            else:
                print('No Outputs found with given specs!')

            # self.create_resolve_timeline_from_clips(timeline_name, clip_path_list)

    def list_shot_update_status(self):
        """checks if shot outputs are updated based on version path modification date
        """
        import os
        import glob
        import time
        import datetime

        start_date = self.start_date.date()
        query_date = datetime.datetime(start_date.year(), start_date.month(), start_date.day())

        shots = self.get_shots_from_ui()

        self.updated_shot_list.clear()

        if shots:
            update_list = []
            t_name = self.task_name_combo_box.currentText()
            from stalker import Task, Version
            for shot in shots:
                print('Checking Shot... - %s' % shot.name)
                task = Task.query.filter(Task.parent == shot).filter(Task.name == t_name).first()
                if not task and t_name == 'Comp':  # try Cleanup task
                    task = Task.query.filter(Task.parent == shot).filter(Task.name == 'Cleanup').first()

                has_valid_status = True
                if self.filter_statuses_check_box.isChecked():
                    if t_name != 'Plate': # do not check status for plates
                        try:
                            valid_status_names = self.get_valid_statuses_from_ui()
                            if task.status.name not in valid_status_names:
                                print('%s -> %s' % (shot.name, task.status.name))
                                has_valid_status = False
                        except AttributeError:
                            pass        

                if has_valid_status is True:            
                    if not task:
                        continue

                    if task.versions:
                        last_version = Version.query.filter(Version.task == task).filter(Version.take_name == 'Main')\
                            .order_by(Version.version_number.desc()).first()
                    else:
                        continue

                    try:
                        has_alpha = False
                        raw_seconds = os.path.getmtime(last_version.absolute_full_path)

                        # If we are looking for *Alpha*, comp name will not match with outputs...
                        # because the output is rendered from Main take with a different saver path
                        # so we have to look for the first file rendered which had *Alpha* in its name
                        if self.alpha_only_check_box.isChecked():
                            ext = self.ext_name_combo_box.currentText()
                            t_path = task.absolute_path
                            output_path = os.path.join(t_path, 'Outputs', 'Main')
                            latest_task_name = os.path.splitext(last_version.filename)[0]
                            version_folder = latest_task_name.split('_')[-1]
                            file_paths = glob.glob("%s/%s/%s/*%s*.*.%s" % (output_path, version_folder,
                                                                           ext, 'alpha', ext))
                            if not file_paths:  # try outputs with no version folders
                                file_paths = glob.glob("%s/%s/*%s*%s.*.%s" % (output_path, ext, 'alpha',
                                                                              version_folder, ext))
                            if file_paths:
                                raw_seconds = os.path.getmtime(file_paths[0])
                                has_alpha = True

                        local_time = time.localtime(raw_seconds)
                        modification_date = datetime.datetime(local_time.tm_year,
                                                              local_time.tm_mon,
                                                              local_time.tm_mday)

                        if modification_date >= query_date:
                            update_info = '%s - %s : %s > %s' % (
                                task.parent.name,
                                task.name,
                                str(modification_date).split(' ')[0],
                                last_version.updated_by.name
                            )
                            update_string = self.add_data_as_text_to_ui(update_info, shot.id)
                            if not self.alpha_only_check_box.isChecked():
                                update_list.append(update_string)
                            elif has_alpha is True:
                                update_list.append(update_string)    
                    except BaseException:
                        continue

            if update_list:
                update_list.sort()
                for update_string in update_list:
                    self.updated_shot_list.addItem(update_string)
            else:
                self.updated_shot_list.addItem('No Updated Shots found after specified date / ui specs.')

    def conform(self):
        """conforms given Stalker Shot instances to a Timeline in Reolve
        """
        shots = self.get_shots_from_ui()
        self.conform_shots(shots)

    def conform_updated_shots(self):
        """conforms only updated shots from listWidget in UI
        """
        from stalker import Shot
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
