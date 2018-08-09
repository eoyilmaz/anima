# -*- coding: utf-8 -*-
# Copyright (c) 2012-2017, Anima Istanbul
#
# This module is part of anima-tools and is released under the BSD 2
# License: http://www.opensource.org/licenses/BSD-2-Clause
"""previs_to_shots
This tool exports maya scenes from a Previs Task with multpile shots
to related Animation Tasks with single shot in relation with the Camera Sequencer (Maya).
"""


import os
import pymel.core as pm
from stalker import LocalSession
from anima.env import mayaEnv


class ShotExporter2(object):
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
            shot_name = shot.full_shot_name

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

        # moves all animation keys to where should they to be
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


def move_all_anim_curves():

    def check_overlapping(anim_curves, choice, current_time, offset_val):
        for anim_curve in anim_curves:
            key_cnt = anim_curve.numKeys()
            message = 'Some Keys are overlapping within Offset Value\n'
            message += 'Do you want continue on Moving other Keys ?\n'
            for i in range(0, key_cnt):
                key_time = anim_curve.getTime(i)
                if choice == 'forward':
                    if key_time <= current_time + offset_val:
                        range_dialog = pm.confirmDialog(title='Error',
                                                        message=message,
                                                        button=['Yes', 'No'],
                                                        cancelButton='No',
                                                        dismissString='No')
                        if range_dialog == 'Yes':
                            return 1
                        else:
                            raise RuntimeError('Move Keys process interrupted by User.')

                if choice == 'back':
                    if key_time >= current_time + offset_val:
                        range_dialog = pm.confirmDialog(title='Error',
                                                        message=message,
                                                        button=['Yes', 'No'],
                                                        cancelButton='No',
                                                        dismissString='No')
                        if range_dialog == 'Yes':
                            return 1
                        else:
                            raise RuntimeError('Move Keys process interrupted by User.')

    def move_all_keys(choice):
        offset_val = offset_intfield.getValue()

        if offset_val < 1:
            raise RuntimeError('Enter an Offset Value greater than 0.')

        if choice == 'back':
            offset_val = offset_intfield.getValue() * -1

        unlock_val = unlock_state.getValue1()

        current_time = pm.currentTime()

        anim_curves = pm.ls(type='animCurve')
        non_moved_curves = []

        if choice == 'back':
            check_overlapping(anim_curves, choice, current_time, offset_val)

        for anim_curve in anim_curves:
            try:
                if unlock_val is True and anim_curve.isLocked():
                    anim_curve.setLocked(0)

                key_cnt = anim_curve.numKeys()
                for i in range(1, key_cnt + 1):

                    if choice == 'forward':
                        ind = key_cnt - i
                    if choice == 'back':
                        ind = i - 1

                    if anim_curve.getTime(ind) >= current_time:
                        pm.keyframe(anim_curve,
                                    index=ind,
                                    iub=False,
                                    animation='objects',
                                    relative=True,
                                    option='move',
                                    tc=offset_val
                        )
            except:
                if anim_curve not in non_moved_curves:
                    non_moved_curves.append(anim_curve)
                continue

        if not non_moved_curves:
            pm.confirmDialog(title='Info', message='Keys Moved Successfully.', button='OK')
        else:
            message = 'Anim Curves can NOT be moved:\r\n'
            message += '\r'
            for i in range(0, len(non_moved_curves)):
                message += '%s\n' % non_moved_curves[i]
                if i > 30:
                    message += '+ More...\n'
                    break
            print non_moved_curves
            pm.confirmDialog(title='Error', message=message, button='OK')

        # pdm.close()

    window_name = 'move_keys_window'

    if pm.window(window_name, q=True, ex=True):
        pm.deleteUI(window_name, wnd=True)

    move_keys_win = pm.window(window_name, title='Move Keys', s=0, rtf=1)

    with pm.columnLayout(rs=5, cal='center'):
        pm.text(l='                      MOVE ALL KEYS')
        pm.text(l='             relatively from currentTime')
        pm.text(l='    (overlapping Keys will NOT be moved)')
        with pm.rowColumnLayout(nc=3, cw=[(1,70), (2, 70), (3, 70)]):
            def exec_move_all_keys_back(*args):
                move_all_keys('back')

            pm.button(l='-', c=exec_move_all_keys_back)
            offset_intfield= pm.intField()

            def exec_move_all_keys_forward(*args):
                move_all_keys('forward')

            pm.button(l='+', c=exec_move_all_keys_forward)

    with pm.columnLayout():
        unlock_state = pm.checkBoxGrp(l='Unlock & Move', v1=1)

    pm.showWindow(move_keys_win)


def one_cam_to_shots():
    if not pm.ls(type='shot'):
        raise RuntimeError('There are no Shots in this scene.')

    if len(pm.selected()) != 1 or pm.selected()[0].getShape().type() != 'camera':
        raise RuntimeError('Select just 1 camera.')

    the_cam = pm.selected()[0]

    for shot in pm.ls(type='shot'):
        shot.set_camera(the_cam)


def create_shots_from_scratch():
    shot_num_name = 'shotNumName'
    shot_length_name = 'shotLengthName'
    start_frame_name = 'startFrameName'
    end_frame_name = 'endFrameName'
    shot_name_name = 'shotNameName'

    def create_shots(with_cameras):
        cnt = 0
        while pm.textField('%s%s' % (shot_name_name, str(cnt)), ex=1):
            cnt += 1

        seqs = [seq for seq in pm.ls(type='sequencer') if seq.referenceFile() is None]
        if len(pm.ls(type='sequencer')) != 1:
            raise RuntimeError('There must be 1 sequencer in a scene.')

        seq = seqs[0]
        for i in range(0, cnt):
            shot_node_name = pm.textField('%s%s' % (shot_name_name, str(i)), q=1, text=1)
            start_frame = pm.intField('%s%s' % (start_frame_name, str(i)), q=1, v=1)
            end_frame = pm.intField('%s%s' % (end_frame_name, str(i)), q=1, v=1)
            shot_num = pm.textField('%s%s' % (shot_num_name, str(i)), q=1, text=1)
            shot = pm.createNode('shot', n=shot_node_name)
            shot.setAttr('startFrame', start_frame)
            shot.setAttr('sequenceStartFrame', start_frame)
            shot.setAttr('endFrame', end_frame)
            shot.setAttr('shotName', shot_num)

            seq.add_shot(shot)

            if with_cameras:
                camera_name = '%s%s' % (pm.textField('camera_prefix_name', q=1, text=1), str(i+1))
                cam = pm.mel.eval('camera -n "%s";' % camera_name)
                pm.PyNode(cam[1]).setAttr('farClipPlane', 1000000)
                pm.PyNode(cam[1]).setAttr('focalLength', 35)
                pm.PyNode(cam[0]).attr('scaleX').lock()
                pm.PyNode(cam[0]).attr('scaleY').lock()
                pm.PyNode(cam[0]).attr('scaleZ').lock()
                shot.set_camera(pm.PyNode(cam[1]))

    def set_parameters_from_length(*args):
        cnt = 0
        while pm.intField('%s%s' % (shot_length_name, str(cnt)), ex=1):
            cnt += 1

        for i in range(0, cnt):
            if i == 0:
                s_frame = pm.intField('%s%s' % (start_frame_name, str(i)), q=1, v=1)
                start_length = pm.intField('%s%s' % (shot_length_name, str(i)), q=1, v=1)
                pm.intField('%s%s' % (end_frame_name, str(i)), e=1, v=s_frame+start_length)
            else:
                prev_end_frame = pm.intField('%s%s' % (end_frame_name, str(i-1)), q=1, v=1)
                pm.intField('%s%s' % (start_frame_name, str(i)), e=1, v=prev_end_frame+1)
                start_length = pm.intField('%s%s' % (shot_length_name, str(i)), q=1, v=1)
                pm.intField('%s%s' % (end_frame_name, str(i)), e=1, v=prev_end_frame+1+start_length)

    def list_shots(*args):
        shot_num = pm.intFieldGrp('shotNum', q=1, v1=1)
        start_frame = pm.intFieldGrp('startFrame', q=1, v1=1)
        shot_count = pm.intFieldGrp('shotCount', q=1, v1=1)

        if len(str(shot_num)) < 2:
            raise RuntimeError('First Shot Number must be at east 2 digits.')

        for shot in pm.ls(type='shot'):
            try:
                cam = shot.get_camera()
                if cam.name() not in ['persp', 'top', 'front', 'side']:
                    pm.delete(cam)
            except:
                pm.delete(shot)

        for shot in pm.ls(type='shot'):
            pm.delete(shot)

        window_name = 'shot_creator_window'
        if pm.window(window_name, q=True, ex=True):
            pm.deleteUI(window_name, wnd=True)

        window_name = 'shot_list_window'
        if pm.window(window_name, q=True, ex=True):
            pm.deleteUI(window_name, wnd=True)

        shot_list_win = pm.window(
            window_name, title='Shot Creator', s=0, rtf=1
        )

        with pm.columnLayout():
            with pm.rowColumnLayout(nc=6, cw=[(1,20), (2, 70), (3, 70), (4, 70), (5, 70), (6, 70)]):
                pm.text(l='')
                pm.text(l='Shot Num')
                pm.text(l='Length')
                pm.text(l='Start Frame')
                pm.text(l='End Frame')
                pm.text(l='Shot Name')

                for i in range(0, shot_count):

                    def checkbox_state(*args):
                        check_cnt = 0
                        while pm.checkBox('%s%s' % ('shotCheckBox', str(check_cnt)), ex=1):
                            check_cnt += 1

                        for k in range(0, check_cnt):
                            state = pm.checkBox('shotCheckBox%s' % str(k), q=1, v=1)
                            if not state:
                                pm.textField('%s%s' % (shot_num_name, str(k)), e=1, en=0)
                                pm.textField('%s%s' % (shot_name_name, str(k)), e=1, en=0)
                            else:
                                pm.textField('%s%s' % (shot_num_name, str(k)), e=1, en=1)
                                pm.textField('%s%s' % (shot_name_name, str(k)), e=1, en=1)

                    pm.checkBox('shotCheckBox%s' % str(i), onc=checkbox_state, ofc=checkbox_state)

                    shot_number = ''
                    for j in range(0,4):
                        digit = len(str(shot_num))
                        if digit == 1:
                            shot_number = '000%s' % str(shot_num)
                        if digit == 2:
                            shot_number = '00%s' % str(shot_num)
                        if digit == 3:
                            shot_number = '0%s' % str(shot_num)
                        if digit == 4:
                            shot_number = '%s' % str(shot_num)

                    pm.textField('%s%s' % (shot_num_name, str(i)), text=str(shot_number), en=0)
                    shot_num += 10

                    pm.intField('%s%s' % (shot_length_name, str(i)), cc=set_parameters_from_length, v=1)

                    pm.intField('%s%s' % (start_frame_name, str(i)), en=0, v=1)
                    if i == 0:
                        pm.intField('%s%s' % (start_frame_name, str(i)), e=1, v=start_frame)

                    pm.intField('%s%s' % (end_frame_name, str(i)), en=0, v=1)

                    shot_node_name = 'shot%s' % str(i+1)
                    pm.textField('%s%s' % (shot_name_name, str(i)), text=shot_node_name, en=0)

        with pm.columnLayout():

            def exec_create_shots(*args):
                state = pm.checkBox('camera_checkbox_name', q=1, v=1)
                if not state:
                    create_shots(False)
                else:
                    create_shots(True)

            pm.button(l='CREATE SHOTS', w=370, c=exec_create_shots)

        with pm.rowColumnLayout(nc=3, cs=(3, 10), cw=[(1,60), (2, 120), (3, 100)]):
            pm.text(l='camPrefix')
            pm.textField('camera_prefix_name', text='camera__shotExp_', en=0)

            def checkbox_cameras(*args):
                state = pm.textField('camera_prefix_name', q=1, en=1)
                if not state:
                    pm.textField('camera_prefix_name', e=1, en=1)
                else:
                    pm.textField('camera_prefix_name', e=1, en=0)

            pm.checkBox('camera_checkbox_name', l='create Cameras', onc=checkbox_cameras, ofc=checkbox_cameras)

        pm.showWindow(shot_list_win)

    window_name = 'shot_creator_window'
    if pm.window(window_name, q=True, ex=True):
        pm.deleteUI(window_name, wnd=True)

    window_name1 = 'shot_list_window'
    if pm.window(window_name1, q=True, ex=True):
        pm.deleteUI(window_name1, wnd=True)

    shot_creator_win = pm.window(
        window_name, title='Shot Creator', s=0, rtf=1
    )

    with pm.columnLayout():
        pm.intFieldGrp('shotNum', l='First Shot Number', cw2=(120, 80), v1=10)
        pm.intFieldGrp('startFrame', l='Start Frame', cw2=(120, 80), v1=0)
        pm.intFieldGrp('shotCount', l='Shot Count', cw2=(120, 80), v1=10)
        pm.button(l='LIST SHOTS', w=200, c=list_shots)
        pm.text(l='            All Shots will be deleted...')
        pm.text(l='            ...to start from scratch.')

    pm.showWindow(shot_creator_win)


class ShotExporter(object):

    def __init__(self):
        from anima.utils import do_db_setup
        from stalker import Type, LocalSession
        from anima.env import mayaEnv

        do_db_setup()
        m = mayaEnv.Maya()

        local_session = LocalSession()
        self.logged_in_user = local_session.logged_in_user
        if not self.logged_in_user:
            raise RuntimeError('Please login to Stalker')

        if not m.get_current_version():
            raise RuntimeError('This scene is not saved with Stalker')

        self.anim_type = Type.query.filter(Type.name == "Animation").first()
        self.prev_type = Type.query.filter(Type.name == "Previs").first()

        # get current task info
        self.current_version = m.get_current_version()
        self.current_task = self.current_version.task
        self.current_type = self.current_task.type

        # check task type
        if self.current_type not in [self.anim_type, self.prev_type]:
            raise RuntimeError('Task must be either an Animation or Previs Task.')

        # query sequenceManager
        if len(pm.ls(type='sequenceManager')) is not 1:
            raise RuntimeError('There must be just 1 sequenceManager.')
        self.sm = pm.ls('sequenceManager1')[0]

        # query sequencer
        seqs = [seq for seq in pm.ls(type='sequencer') if seq.referenceFile() is None]
        if len(seqs) is not 1:
            raise RuntimeError('There must be just 1 sequencer.')

        self.sequencer = self.sm.sequences.get()[0]

        # query all shots in sequencer
        self.shot_list = self.sequencer.shots.get()

        # query shots in time based descending order
        shots = self.shot_list
        shots_sorted = []
        shots_mid_frames = []
        mid_frames = []
        for shot in shots:
            start = shot.getSequenceStartTime()
            end = shot.getSequenceEndTime()
            mid_frame = int(start+((end-start)/2))
            shots_mid_frames.append([shot, mid_frame])
            mid_frames.append(mid_frame)

        mid_frames.sort()
        inc = -1
        for frame in mid_frames:
            inc += 1
            for shot in shots_mid_frames:
                if frame == shot[1]:
                    if shot[0] not in shots_sorted:
                        shots_sorted.append(shot[0])

        self.shots_descending = shots_sorted

        # query all shot tasks from current scene
        shot_task = None
        parent_task = None
        if self.current_type is self.prev_type:
            parent_task = self.current_task.parent
        elif self.current_type is self.anim_type:
            parent_task = self.current_task.parent.parent
        if parent_task is None:
            raise RuntimeError('Current Task does not have Proper Parents.')
        for task in parent_task.walk_hierarchy():
            if task.nice_name == 'Shots':
                shot_task = task
                break
        if shot_task is None:
            raise RuntimeError('Shots Task can not be found.')

        self.scene_shot_tasks = shot_task.tasks

    def set_shot_frame_range(self, shot):
        min_frame = shot.getAttr('startFrame')
        max_frame = shot.getAttr('endFrame')
        pm.playbackOptions(ast=min_frame, aet=max_frame, min=min_frame, max=max_frame)

    def set_range_from_seq(self):
        """sets the playback range from the sequencer node in the scene
        """
        min_frame = self.sequencer.getAttr('minFrame')
        max_frame = self.sequencer.getAttr('maxFrame')

        pm.playbackOptions(ast=min_frame, aet=max_frame, min=min_frame, max=max_frame)

    def check_camera_assignment(self):
        """all shots must have cameras assigned to them
        """
        shots = self.shot_list
        shots_without_camera = []
        for shot in shots:
            try:
                shot.get_camera()
                if str(shot.get_camera()) in ['persp', 'top', 'side', 'front']:
                    shots_without_camera.append(shot)
            except:
                shots_without_camera.append(shot)

        if shots_without_camera:
            message = 'No Cameras assigned to shots:\r\n'
            message += '\r'
            for shot in shots_without_camera:
                message += 'shot %s\n' % (shot.getShotName())
            pm.confirmDialog(title='Error', message=message, button='OK')
            raise RuntimeError('No Cameras assigned to some shots.')

    def check_wrong_shot_names(self):
        """check if all shots have correct shot names
        """
        shots = self.shot_list
        shots_with_bad_names = []
        for shot in shots:
            if len(shot.getShotName()) != 4 or shot.getShotName().isnumeric() is not True:
                shots_with_bad_names.append(shot)

        if shots_with_bad_names:
            message = 'Wrong Shot Names:\r\n'
            message += '\r'
            for shot in shots_with_bad_names:
                message += '%s - %s\n' % (shot.getName(), shot.getShotName())
            pm.confirmDialog(title='Error', message=message, button='OK')
            raise RuntimeError(message)

    def check_unique_shot_names(self):
        """check if all shots have unique shot names
        """
        shots = self.shot_list
        shot_names = []
        shots_without_unique_names = []
        for shot in shots:
            if shot.getShotName() not in shot_names:
                shot_names.append(shot.getShotName())
            else:
                shots_without_unique_names.append(shot.getShotName())

        if shots_without_unique_names:
            message = 'More than 1 shot Numbered as:\r\n'
            message += '\r'
            for shot_name in shots_without_unique_names:
                message += 'shot [ %s ]\n' % shot_name
            pm.confirmDialog(title='Error', message=message, button='OK')
            raise RuntimeError('Non-Unique Shot Names.')

    def check_shot_overlapping(self):
        """check if any shots are overlapping
        """
        shots_sorted = self.shots_descending

        if len(shots_sorted) > 1:
            overlapping_shots = []
            ind = 0
            for shot in shots_sorted:
                ind += 1
                start = shots_sorted[ind].getSequenceStartTime()
                end = shot.getSequenceEndTime()
                if end >= start:
                    overlapping_shots.append('%s & %s' % (shot, shots_sorted[ind]))
                if ind == (len(shots_sorted)-1):
                    break

            if overlapping_shots:
                message = 'Overlapped Shots:\r\n'
                message += '\r'
                for shots_info in overlapping_shots:
                    message += '[ %s ] are overlapping\n' % shots_info
                pm.confirmDialog(title='Error', message=message, button='OK')
                raise RuntimeError('There Are overlapping shots in Sequencer.')

    def check_shot_order(self):
        """check if all shots are sequentially ordered with consecutive shot names
        """
        shots_sorted = self.shots_descending

        non_sequential_shots = []
        for i in range(len(shots_sorted)):
            if i is len(shots_sorted)-1:
                break
            if int(shots_sorted[i].getShotName()) >= int(shots_sorted[i+1].getShotName()):
                non_sequential_shots.append(shots_sorted[i])
        if non_sequential_shots:
            message = 'Shot Numbers are not Ordered in Sequencer:\r\n'
            message += '\r'
            for shot in non_sequential_shots:
                message += 'shot [ %s ]\n' % (shot.getShotName())
            message += '\r\n'
            message += 'Shots above seem to be placed randomly in Sequencer.\r'
            message += '\r\n'
            message += 'Is this on Purpose for Edit?\r'
            message += '\r\n'
            message += 'If NOT it is very IMPORTANT to correct Shot Numbers...\r'
            message += 'as Shots will be saved to its task in Stalker by looking at this number !!!\r'
            dialog = pm.confirmDialog(title='Important Warning',
                                      message=message,
                                      button=['On Purpose', 'No, I will Fix it'])
            if dialog == 'On Purpose':
                pass
            else:
                raise RuntimeError('Editorial Error in Sequencer')

    def check_shot_gaps(self):
        """check if there are any gaps between shots
        """
        min_frame = self.sequencer.getAttr('minFrame')
        max_frame = self.sequencer.getAttr('maxFrame')
        seq_length = (max_frame - min_frame) + 1
        shot_length = 0

        shots = self.shot_list
        for shot in shots:
            start_frame = shot.getAttr('startFrame')
            end_frame = shot.getAttr('endFrame')
            shot_length += (end_frame - start_frame) + 1

        if seq_length != shot_length:
            message = 'There are Gaps between shots:\r\n'
            message += '\r'
            message += 'Please fix gaps from Camera Sequencer.\r\n'
            pm.confirmDialog(title='Error', message=message, button='OK')
            raise RuntimeError('There are gaps between Shot Nodes.')

    def check_shot_seq_ranges(self):
        shots_with_bad_frame_range = []

        shots = self.shots_descending
        for shot in shots:
            shot_s_fr = shot.getStartTime()
            shot_e_fr = shot.getEndTime()
            seq_s_fr = shot.getSequenceStartTime()
            seq_e_fr = shot.getSequenceEndTime()
            if shot_s_fr != seq_s_fr or shot_e_fr != seq_e_fr:
                shots_with_bad_frame_range.append(shot)

        if shots_with_bad_frame_range:
            message = 'Shots below does NOT have equal shot/seq frame ranges :\r\n'
            message += '\r'
            for shot in shots_with_bad_frame_range:
                message += '[ %s ]\n' % shot
            message += '\r\n'
            message += 'Generally we do Not prefer this in our Projects.\r'
            message += '\r\n'
            message += 'Is this on Purpose for Edit?\r'
            dialog = pm.confirmDialog(title='Important Warning',
                                      message=message,
                                      button=['On Purpose', 'No, I will Fix it'])
            if dialog == 'On Purpose':
                pass
            else:
                raise RuntimeError('Editorial Error in Sequencer')

    def check_shot_attributes(self):
        """check some of mandatory attributes
        """
        shots_with_bad_attrs = []

        attrs = {
            'scale': 1.0,
            'preHold': 0.0,
            'postHold': 0.0
        }

        shots = self.shot_list
        for shot in shots:
            for item in attrs.iteritems():
                value = shot.getAttr(item[0])
                if value != item[1]:
                    shots_with_bad_attrs.append([shot, item[0], value, item[1]])

        if shots_with_bad_attrs:
            message = 'Shots below have restricted values for shot attrs:\r\n'
            message += '\r'
            for info in shots_with_bad_attrs:
                message += '[ %s ] - %s | su an %s -> %s olmali\n' % (info[0], info[1], info[2], info[3])
            pm.confirmDialog(title='Error', message=message, button='OK')
            raise RuntimeError('There Are restricted values in Shot Nodes.')

    def check_stalker_tasks(self):
        """check if all shots have proper stalker tasks
        """
        shot_tasks = self.scene_shot_tasks

        shots = self.shot_list
        shots_without_task = []
        for shot in shots:
            check = 0
            for t in shot_tasks:
                if shot.getShotName() == t.nice_name.split('_')[-1]:
                    check = 1
                else:
                    pass
            if check == 0:
                shots_without_task.append(shot)

        if shots_without_task:
            message = 'Shots do not have a Task to save:\r\n'
            message += '\r'
            for shot in shots_without_task:
                message += 'shot [ %s ]\n' % (shot.getShotName())
            pm.confirmDialog(title='Error', message=message, button='OK')
            raise RuntimeError('Some Shots do not have Stalker Tasks.')

    def set_sequencer_name(self):
        """set sequencer name for publish
        """
        from anima.exc import PublishError
        import anima.env.mayaEnv.publish as oy_publish

        try:
            oy_publish.check_sequence_name()
            oy_publish.check_sequence_name_format()
        except:
            seq_name = None
            if self.current_type == self.prev_type:
                seq_name = '_'.join(self.current_version.nice_name.split('_Previs')[0].split('_')[-3:]).upper()
            if self.current_type == self.anim_type:
                seq_name = '_'.join(self.current_version.nice_name.split('_')[:3]).upper()
            self.sequencer.set_sequence_name(seq_name)

            message = 'Scene Task name is Wrong.\n'
            # message += '%s\n' % seq_name
            message += '\n'
            message += 'Enter Seq Name Manually below like:\n'
            message += 'EP001_001_TEMP  or SEQ001_001_TEMP\n'
            message += '<Episode Num>_<Scene Num>_<Env>'
            pd = pm.promptDialog(title='Error', message=message, button='SET Seq Name')

            if pd == 'SET Seq Name':
                seq_name = pm.promptDialog(q=1, text=1)
                self.sequencer.set_sequence_name(seq_name)

            try:
                oy_publish.check_sequence_name_format()
            except PublishError as e:
                raise RuntimeError(e)

            # if pd == 'SET Seq Name':
            #     seq_name = pm.promptDialog(q=1, text=1)
            #     self.sequencer.set_sequence_name(seq_name)
            #     try:
            #         oy_publish.check_sequence_name_format()
            #     except:
            #         self.set_sequencer_name()
            # else:
            #     try:
            #         oy_publish.check_sequence_name_format()
            #     except:
            #         self.set_sequencer_name()

    def clear_scene(self, keep_shot):
        # delete all other shot nodes
        all_shots = pm.ls(type='shot')
        shots_to_delete = []
        for shot in all_shots:
            if shot.name() != keep_shot.name():
                shots_to_delete.append(shot)
        for shot in shots_to_delete:
            if shot:
                pm.delete(shot)

        # set some attrs and delete cameras
        if keep_shot:
            keep_shot.track.set(1)
            keep_shot.shotName.lock()

            shot_camera = keep_shot.currentCamera.get()
            exclude_cams = ['perspShape', 'frontShape', 'sideShape', 'topShape', shot_camera.getShape()]
            unused_cameras = [node.getParent()
                              for node in pm.ls(type='camera')
                              if node.name() not in exclude_cams]
            pm.delete(unused_cameras)

    def one_cam_to_shots(self):
        # make sure selected object is a camera
        sel = pm.selected()
        if len(sel) != 1:
            raise RuntimeError('Select just 1 camera.')
        the_cam = sel[0]
        if the_cam.getShape().type() != 'camera':
            message = 'Select just 1 Camera.\r\n'
            pm.confirmDialog(title='Error', message=message, button='OK')
            raise RuntimeError('Select just 1 camera.')

        # unlock locked attrs
        attributes_locked = []
        for attr in pm.listAttr(the_cam, locked=1):
            attributes_locked.append(attr)
        for attr in pm.listAttr(the_cam.getShape(), locked=1):
            attributes_locked.append(attr)

        for attr in attributes_locked:
            the_cam.attr(attr).unlock()

        id = 0
        for shot in self.shots_descending:
            s_frame = shot.getStartTime()
            e_frame = shot.getEndTime()

            # duplicate, clear parents and unparent shot cam from original
            pm.currentTime(s_frame)
            id += 1
            shot_camera = pm.duplicate(the_cam, rr=1, name='camera__shotExp_%s' % str(id))
            tr_parents = shot_camera[0].listRelatives(type='transform')
            for tr in tr_parents:
                pm.delete(tr)
            pm.parent(shot_camera, w=1)

            # connect animation curves from original to duplicated shot cam
            anim_curves = []
            connections = the_cam.getShape().listConnections()
            for connection in connections:
                if 'animCurve' in str(connection.type()):
                    attribute_name = str(connection.listConnections(p=1)[0].split('.')[-1:][0])
                    new_key = pm.duplicate(connection, rr=1)
                    anim_curves.append(new_key[0])
                    pm.connectAttr('%s.output' % new_key[0], '%s.%s' % (shot_camera[0].getShape(), attribute_name))

            # parent constraint shot cam to original
            constraint = pm.parentConstraint(the_cam, shot_camera[0], mo=0, weight=1)

            # isolate none to speed things up
            panel_list = pm.getPanel(type='modelPanel')
            pm.select(None)
            for panel in panel_list:
                pm.isolateSelect(panel, state=1)

            # bake all keyable attrs between shot frame range
            pm.mel.eval('bakeResults -simulation true -t "%s:%s" -sampleBy 1 -disableImplicitControl true '
                            '-preserveOutsideKeys true -sparseAnimCurveBake false -removeBakedAttributeFromLayer false '
                            '-bakeOnOverrideLayer false -minimizeRotation true -controlPoints false -shape true %s;'
                            % (int(s_frame), int(e_frame), shot_camera[0]))

            # restore isolation
            for panel in panel_list:
                pm.isolateSelect(panel, state=0)

            # set some forced attrs
            shot_camera[0].disconnectAttr('scaleX')
            shot_camera[0].setAttr('scaleX', 1)
            shot_camera[0].disconnectAttr('scaleY')
            shot_camera[0].setAttr('scaleY', 1)
            shot_camera[0].disconnectAttr('scaleZ')
            shot_camera[0].setAttr('scaleZ', 1)
            shot_camera[0].disconnectAttr('visibility')
            shot_camera[0].setAttr('visibility', 1)
            shot_camera[0].getShape().disconnectAttr('farClipPlane')
            shot_camera[0].getShape().setAttr('farClipPlane', 10000000)

            # make all camera anim curves linear
            for curve in shot_camera[0].listAttr(k=1):
                pm.selectKey(curve, add=1, k=1)
                pm.keyTangent(itt='linear', ott='linear')
            for curve in shot_camera[0].getShape().listAttr(k=1):
                pm.selectKey(curve, add=1, k=1)
                pm.keyTangent(itt='linear', ott='linear')

            # no need for constraint node
            pm.delete(constraint)

            # lock previously unlocked attrs again
            for attr in attributes_locked:
                the_cam.attr(attr).lock()

            # set shot camera
            pm.select(cl=1)
            shot.set_camera(shot_camera[0])

    def pre_publish_previs(self):
        """checks if all necessities are met for exporting previs to animation shots
        """
        if not pm.ls(type='shot'):
            message = 'No Shots exist in this scene.\r\n'
            message += '\r'
            pm.confirmDialog(title='Error', message=message, button='OK')
            raise RuntimeError('Non-Existing Shots.')

        self.set_sequencer_name()
        self.set_range_from_seq()

        self.check_camera_assignment()
        self.check_shot_attributes()
        self.check_wrong_shot_names()
        self.check_unique_shot_names()
        self.check_shot_seq_ranges()
        self.check_shot_overlapping()
        self.check_shot_order()
        self.check_shot_gaps()
        self.check_stalker_tasks()

        # from anima.publish import run_publishers
        # run_publishers('previs') # DetachedInstanceError: attribute refresh operation cannot proceed

        import anima.env.mayaEnv.publish as oy_publish

        oy_publish.check_sequencer()
        oy_publish.check_shot_nodes()
        oy_publish.check_sequence_name()
        oy_publish.check_sequence_name_format()
        oy_publish.check_shot_name_format()
        oy_publish.check_unique_shot_names()
        oy_publish.check_frame_range_selection()

        message = 'Publish Check SUCCESSFUL.\r\n'
        message += '\r'
        ok = pm.confirmDialog(title='Info', message=message, button='OK, Continue')
        if ok == 'OK, Continue':
            pass

    def save_previs_to_shots(self, take_name):
        """exports previs to animation shots
        """
        self.pre_publish_previs()

        shot_tasks = self.scene_shot_tasks
        shot_nodes = self.shot_list
        shots_to_export = []

        for shot_node in shot_nodes:
            for shot_task in shot_tasks:
                for task in shot_task.tasks:
                    if task.type == self.anim_type:
                        shot_number = shot_task.name.split('_')[-1]
                        if shot_node.getShotName() == shot_number:
                            shots_to_export.append([shot_node, task, shot_number])

        from anima.env import mayaEnv
        from stalker import Version
        from anima.ui.progress_dialog import ProgressDialogManager
        pdm = ProgressDialogManager()
        pdm.close()

        m_env = mayaEnv.Maya()

        versions = []
        description = 'Auto Created By Shot Exporter'
        # create versions to save and show in pop-up window
        for shot_info in shots_to_export:
            version = Version(
                task=shot_info[1],
                description=description,
                take_name=take_name,
                created_by=self.logged_in_user
            )
            versions.append(version)

        if len(versions) != len(shots_to_export):
            from stalker.db.session import DBSession
            DBSession.rollback()
            raise RuntimeError('Something is critically wrong. Contact Mehmet ERER.')

        # pop-up a window to show everything will be saved properly before actually doing it
        message = 'Shots will be Saved as Below:\r\n'
        message += '\r'
        index = 0
        for shot_info in shots_to_export:
            v = versions[index]
            message += 'shot[ %s ] -> %s\n' % (shot_info[2], v)
            index += 1
        dialog = pm.confirmDialog(title='Important Warning',
                                  message=message,
                                  button=['OK, Start Saving Shots', 'STOP, wrong paths!'])
        if dialog == 'OK, Start Saving Shots':
            pass
        else:
            from stalker.db.session import DBSession
            DBSession.rollback()
            raise RuntimeError('Process Interrupted by User.')

        previs_version = self.current_version

        errored_shots = []
        ind = 0
        caller = pdm.register(len(shots_to_export), 'Batch Saving Previs Shot Nodes to Animation Shot Tasks...')
        from anima.env.mayaEnv import toolbox
        reload(toolbox)
        from stalker.db.session import DBSession
        for shot_info in shots_to_export:
            shot_task = versions[ind].task.parent
            try:
                # open previs version
                m_env.open(previs_version, force=True, reference_depth=3, skip_update_check=True)

                # clear scene
                except_this_shot = pm.PyNode(shot_info[0].name())
                self.clear_scene(except_this_shot)

                # set frame range before save
                toolbox.Animation.set_range_from_shot()

                # update shot.cut_in and shot.cut_out info
                cut_in = pm.playbackOptions(q=1, min=1)
                cut_out = pm.playbackOptions(q=1, max=1)
                shot_task.cut_in = int(cut_in)
                shot_task.cut_out = int(cut_out)

                # save it
                m_env.save_as(versions[ind])
            except:
                errored_shots.append(shot_info[2])
            else:
                # store information to database
                DBSession.add(shot_task)
                DBSession.add(versions[ind])
                DBSession.commit()
            ind += 1

            caller.step()

        if errored_shots:
            message = 'Shots could not be saved:\r\n'
            message += '\r'
            for shot in errored_shots:
                message += '[ %s ]\n' % shot
            pm.confirmDialog(title='Error', message=message, button='OK')
            DBSession.rollback()
            raise RuntimeError('Some Shots could not be saved. Contact Mehmet ERER.')

        # leave it as empty new file
        pm.newFile(force=True)
        message = 'Previs to Shots\r\n'
        message += '\r'
        message += 'Completed Succesfully.\r\n'
        pm.confirmDialog(title='Info', message=message, button='OK')
