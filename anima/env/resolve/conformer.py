# -*- coding: utf-8 -*-
# Copyright (c) 2021, Mehmet Erer
#
# This module is part of anima and is released under the MIT
# License: http://www.opensource.org/licenses/MIT

import os
import re
import glob
from stalker import Project, Task

from anima.ui.base import AnimaDialogBase, ui_caller
from anima.ui.lib import QtCore, QtGui, QtWidgets
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

        self._setup_ui()

        self._setup_signals()

    def _setup_ui(self):
        """setups UI
        """
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)

        bmgc_project_name = self.project.GetName()
        bmgc_project_fps = self.project.GetSetting('timelineFrameRate')

        self.setWindowTitle('Conformer')
        self.resize(400, 100)

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

        size_policy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        self.project_combo_box = QtWidgets.QComboBox(self.h_layout1.widget())
        self.project_combo_box.setSizePolicy(size_policy)
        self.h_layout1.addWidget(self.project_combo_box)

        self.vertical_layout.addLayout(self.h_layout1)

        self.conform_button = QtWidgets.QPushButton(self.vertical_layout.widget())
        self.conform_button.setText('CONFORM')
        self.vertical_layout.addWidget(self.conform_button)

        self.info_label = QtWidgets.QLabel(self.vertical_layout.widget())
        self.info_label.setText('check Console for Progress Info...')
        self.vertical_layout.addWidget(self.info_label)

        self.fill_ui_with_stalker_projects()

    def _setup_signals(self):
        """setups signals
        """
        # conform button signal
        QtCore.QObject.connect(
            self.conform_button,
            QtCore.SIGNAL("clicked()"),
            self.conform
        )

    def fill_ui_with_stalker_projects(self):
        """fills ui with stalker projects
        """
        projects = Project.query.order_by(Project.name).all()
        self.project_combo_box.addItem('Select Project...', -1)
        for project in projects:
            self.project_combo_box.addItem(project.name)

    def get_latest_comp_output_path(self, shot, ext='exr'):
        """returns the Output/Main outputs path for resolve from a given Shot stalker instance
        """
        comp_task = Task.query.filter(Task.parent == shot).filter(Task.name == 'Comp').first()
        comp_path = comp_task.absolute_path
        output_path = os.path.join(comp_path, 'Outputs', 'Main')

        latest_comp_name = None
        if comp_task.versions:
            latest_comp_version = comp_task.versions[0].latest_version
            latest_comp_name = latest_comp_version.filename.strip('.comp')

        resolve_path = None
        if latest_comp_name:
            file_paths = glob.glob("%s/*/%s/*%s.*.%s" % (output_path, ext, latest_comp_name, ext))
            if not file_paths:  # try outputs with no version folders
                file_paths = glob.glob("%s/%s/*%s.*.%s" % (output_path, ext, latest_comp_name, ext))
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

    def create_resolve_timeline_from_xml_path(self, xml_path):
        """creates timeline in resolve from given xml path
        """
        print '---------Started creating Timeline----------'
        media_pool = self.project.GetMediaPool()
        media_pool.ImportTimelineFromFile(xml_path)
        print '---------Finished creating Timeline----------'

    def create_resolve_timeline_from_clips(self, clip_paths):
        """creates timeline in resolve from given clip paths
        """
        print '---------Started creating Timeline----------'
        timeline_name = self.project.GetName()
        media_pool = self.project.GetMediaPool()
        media_storage = self.resolve.GetMediaStorage()

        clips = media_storage.AddItemListToMediaPool(clip_paths)
        media_pool.CreateTimelineFromClips(timeline_name, clips)
        print '---------Finished creating Timeline----------'

    def conform(self):
        """conforms
        """
        # return if a project is not selected from ui
        if self.project_combo_box.currentText() == 'Select Project...':
            QtWidgets.QMessageBox.critical(
                    self,
                    'Error',
                    'Please Select a Stalker Project.'
            )
            return

        stalker_project_name = self.project_combo_box.currentText()
        stalker_project = Project.query.filter_by(name=stalker_project_name).first()

        clip_path_list = []
        none_path_list = []
        sequences = stalker_project.sequences
        for sequence in sequences:
            for shot in sequence.shots:
                clip_path = self.get_latest_comp_output_path(shot, ext='exr')
                if clip_path:
                    clip_path_list.append(clip_path)
                else:
                    none_path_list.append('%s -> No Outputs/Main found.' % shot.name)
                print 'Checking Shot... - %s' % shot.name
        clip_path_list.sort()
        none_path_list.sort()

        print '--------------------------------------------------------------------------'
        for none_path in none_path_list:
            print none_path
        print '--------------------------------------------------------------------------'
        for clip_path in clip_path_list:
            print clip_path
        print '--------------------------------------------------------------------------'
        print 'All comp outputs will be imported as timeline for [%s] Project.' % stalker_project_name

        #self.create_resolve_timeline_from_clips(clip_path_list)
        #self.create_resolve_timeline_from_xml_path(xml_path)
