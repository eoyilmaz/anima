# -*- coding: utf-8 -*-
# Copyright (c) 2012-2015, Anima Istanbul
#
# This module is part of anima-tools and is released under the BSD 2
# License: http://www.opensource.org/licenses/BSD-2-Clause


import os
import pymel.core as pm
from stalker import LocalSession
from anima.env import mayaEnv


class ShotExporter(object):
    """exports shots from a Previs scene
    """

    def __init__(self):

        self.working_file_name = pm.env.sceneName()
        self.working_scene_name = os.path.basename(pm.env.sceneName())
        self.working_folder = pm.workspace(fn=True)

        self.sm = pm.ls('sequenceManager1')[0]
        self.sequencer = self.sm.sequences.get()[0]
        self.shot_list = self.sequencer.shots.get()

        self.m_env = mayaEnv.Maya()

    def check_shot_existence(self):
        """checks if there are shot tasks for all of the shots
        """
        shots_with_no_task = []
        for shot in self.shot_list:
            shot_name = shot.full_shot_name()

    def export_all_shots(self):
        """exports all shots in the scene
        """
        for shot in self.shot_list:
            self.export(shot)

    def export(self, shot):
        """exports the given shot
        """
        # collect some data which will be needed
        start_frame = shot.startFrame.get()
        end_frame = shot.endFrame.get()

        sequence_start = shot.sequenceStartFrame.get()

        offset_value = sequence_start - start_frame
        sequence_len = shot.endFrame.get() - shot.startFrame.get()

        shot.startFrame.set(sequence_start)
        shot.endFrame.set(shot.startFrame.get() + sequence_len)

        print("data is ready")

        #moves all animation keys to where should they to be
        anim_curves = pm.ls(type='animCurve')
        pm.keyframe(
            anim_curves,
            iub=False,
            animation='objects',
            relative=True,
            option='move',
            tc=offset_value
        )
        print("animation curves are ready")

        self.delete_all_others(shot)
        self.get_shot_frame_range(shot)
        self.save_as(shot)
        self.open_again(self.working_file_name)

    def delete_all_others(self, shot):  # delete all useless shots and cameras
        special_cams = ['perspShape', 'frontShape', 'sideShape', 'topShape']
        unused_shots = pm.ls(type="shot")
        # unused_camera = pm.ls("camera*", type="transform")
        unused_camera = [node.getParent()
                         for node in pm.ls(type='camera')
                         if node.name() not in special_cams]

        clear_cams_list = set(unused_camera)
        sel_camera = shot.currentCamera.get()

        unused_shots.remove(shot)
        clear_cams_list.remove(sel_camera)

        pm.delete(unused_shots)
        pm.delete(clear_cams_list)
        shot.track.set(1)
        print("shot is in order")

    def get_shot_frame_range(self, shot):
        """returns the shot
        """
        # set start and end frame of time slider

        start_frame = shot.startFrame.get()
        end_frame = shot.endFrame.get()
        pm.playbackOptions(min=start_frame, max=end_frame)

    def save_as(self, shot_name, child_task_name='Previs'):
        """saves the file under the given shot name
        """
        # first find the shot
        from stalker import Version, Shot, Task
        shot = Shot.query.filter(Shot.name == shot_name).first()
        if not shot:
            raise RuntimeError('No shot found with shot name: %s' % shot_name)

        # get the child task
        child_task = Task.query\
            .filter(Task.parent == shot)\
            .filter(Task.name == child_task_name)\
            .first()

        logged_in_user = LocalSession().logged_in_user

        v = Version(task=child_task, created_by=logged_in_user)
        self.m_env.save_as(v)

    def open_again(self, working_file_name):  # open base file again!
        pm.openFile(working_file_name, force=True, loadReferenceDepth="none")
        print("reopening scene: " + str(working_file_name))
