# -*- coding: utf-8 -*-
import copy
import os
import time
import logging
import functools

import af
import afcommon
import pymel.core as pm


logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)


renderer_to_block_type = {
    'arnold': 'maya_arnold',
    'redshift': 'maya_redshift',
    'mentalRay': 'maya_mental',
    '3delight': 'maya_delight'
}


class MayaRenderCommandBuilder(object):
    """Builds a render command from render flags
    """

    def __init__(self, name='', file_full_path='', render_engine='maya',
                 render_layer=None, camera=None, outputs=None, project='',
                 by_frame=1):
        self.name = name
        self.file_full_path = file_full_path
        self.render_engine = render_engine
        self.render_layer = render_layer  # -rl "%s"
        self.camera = camera  # -cam "%s"
        if outputs is None:
            outputs = []
        self.outputs = outputs
        self.project = project  # -proj "%s"
        self.by_frame = by_frame

    def build_command(self):
        """Builds the render command

        :return str: The render command
        """
        cmd_buffer = ['mayarender%s' % os.getenv('AF_CMDEXTENSION', '')]

        if self.render_engine == 'mentalRay':
            cmd_buffer.append('-r mr')
            cmd_buffer.append('-art -v 5')
        elif self.render_engine == 'maya_delight':
            cmd_buffer.append('-r 3delight')
        elif self.render_engine == 'maya':
            cmd_buffer.append('-r file')

        if self.render_engine == '3delight':
            cmd_buffer.append('-an 1 -s @#@ -e @#@ -inc %d' % self.by_frame)
        else:
            cmd_buffer.append('-s @#@ -e @#@ -b %d' % self.by_frame)

        if self.camera:
            cmd_buffer.append(' -cam "%s"' % self.camera)

        if self.render_layer:
            if self.render_engine == '3delight':
                cmd_buffer.append('-rp "%s"' % self.render_layer)
            else:
                cmd_buffer.append('-rl "%s"' % self.render_layer)

        if self.project:
            cmd_buffer.append('-proj "%s"' % os.path.normpath(self.project))

        cmd_buffer.append(self.file_full_path)

        return ' '.join(cmd_buffer)


class UI(object):
    """The render UI
    """

    def __init__(self):
        self.windows_name = 'cgru_afanasy_wnd'
        self.window = None

    def show(self):
        if pm.window(self.windows_name, exists=True):
            pm.deleteUI(self.windows_name)

        self.window = pm.window(self.windows_name, t='Afanasy')

        with pm.columnLayout(adj=True):
            labels_width = 90
            with pm.rowLayout(nc=4, adj=2, cw4=(labels_width, 40, 15, 15)):
                pm.text(l='Start Frame')
                start_time_int_field = pm.intField(
                    'cgru_afanasy__start_frame',
                    v=pm.optionVar.get('cgru_afanasy__start_frame_ov', 1)
                )
                pm.button(
                    l='<',
                    ann='Use minimum animation range',
                    c=functools.partial(
                        self.set_field_value,
                        start_time_int_field,
                        functools.partial(
                            pm.playbackOptions,
                            q=True,
                            min=True
                        )
                    )
                )
                pm.button(
                    l='<<',
                    ann='Use minimum playback range',
                    c=functools.partial(
                        self.set_field_value,
                        start_time_int_field,
                        functools.partial(
                            pm.playbackOptions,
                            q=True,
                            ast=True
                        )
                    )
                )

            with pm.rowLayout(nc=4, adj=2, cw4=(labels_width, 40, 15, 15)):
                pm.text(l='End Frame')
                end_time_int_field = pm.intField(
                    'cgru_afanasy__end_frame',
                    v=pm.optionVar.get('cgru_afanasy__end_frame_ov', 1)
                )
                pm.button(
                    l='<',
                    ann='Use maximum animation range',
                    c=functools.partial(
                        self.set_field_value,
                        end_time_int_field,
                        functools.partial(
                            pm.playbackOptions,
                            q=True,
                            max=True
                        )
                    )
                )
                pm.button(
                    l='<<',
                    ann='Use maximum playback range',
                    c=functools.partial(
                        self.set_field_value,
                        end_time_int_field,
                        functools.partial(
                            pm.playbackOptions,
                            q=True,
                            aet=True
                        )
                    )
                )

            with pm.rowLayout(nc=2, adj=2, cw2=(labels_width, 50)):
                pm.text(l='Frame Per Task')
                pm.intField(
                    'cgru_afanasy__frames_per_task',
                    v=pm.optionVar.get('cgru_afanasy__frames_per_task_ov', 1)
                )

            with pm.rowLayout(nc=2, adj=2, cw2=(labels_width, 50)):
                pm.text(l='By Frame')
                pm.intField(
                    'cgru_afanasy__by_frame',
                    v=pm.optionVar.get('cgru_afanasy__by_frame_ov', 1)
                )

            with pm.rowLayout(nc=2, adj=2, cw2=(labels_width, 50)):
                pm.text(l='Host Mask')
                pm.textField(
                    'cgru_afanasy__hosts_mask',
                    text=pm.optionVar.get('cgru_afanasy__hosts_mask_ov', '')
                )

            with pm.rowLayout(nc=2, adj=2, cw2=(labels_width, 50)):
                pm.text(l='Host Exclude')
                pm.textField(
                    'cgru_afanasy__hosts_exclude',
                    text=pm.optionVar.get('cgru_afanasy__hosts_exclude_ov', '')
                )

            with pm.rowLayout(nc=2, adj=2, cw2=(labels_width, 50)):
                pm.text(l='Life Time (hours)')
                pm.intField(
                    'cgru_afanasy__life_time',
                    v=pm.optionVar.get('cgru_afanasy__life_time_ov', 240)
                )

            pm.checkBox('cgru_afanasy__paused', l='Start Paused', v=0)
            pm.checkBox(
                'cgru_afanasy__separate_layers',
                l='Submit Render Layers as Separate Tasks',
                v=pm.optionVar.get('cgru_afanasy__separate_layers_ov', 1)
            )

            pm.button(
                l='LAUNCH',
                c=self.launch
            )

            pm.checkBox(
                'cgru_afanasy__close',
                l='Close After',
                v=1
            )

        pm.showWindow(self.window)

    def set_field_value(self, control, value, *args, **kwargs):
        """sets the given field value

        :param control: the UI control
        :param value: the value, can be a callable
        :return:
        """
        try:
            v = value()
        except TypeError:
            v = value
        control.setValue(v)

    @classmethod
    def generate_job_name(cls):
        """generates a job name according to the current scene
        """
        # first check if it is a Stalker Project
        from anima.env import mayaEnv
        m = mayaEnv.Maya()
        v = m.get_current_version()
        if v is not None:
            from stalker import Version
            assert isinstance(v, Version)
            return '%s:%s_v%03i%s' % (
                v.task.project.code,
                v.nice_name,
                v.version_number,
                v.extension
            )

        # check if it is a oyProjectManager job
        from oyProjectManager.environments import mayaEnv
        m = mayaEnv.Maya()
        v = m.get_current_version()
        if v is not None:
            from oyProjectManager.models.version import Version
            assert isinstance(v, Version)
            # get asset or shot
            versionable = v.version_of

            from oyProjectManager.models.asset import Asset
            from oyProjectManager.models.shot import Shot

            first_part = None
            if isinstance(versionable, Asset):
                first_part = '%s:%s' % (
                    versionable.project.code,
                    versionable.code
                )
            elif isinstance(versionable, Shot):
                first_part = '%s:%s' % (
                    versionable.project.code,
                    versionable.sequence.code
                )

            return '%s:%s' % (
                first_part,
                '%s_%s_%s_v%03i_%s%s' % (
                    v.base_name, v.take_name, v.type.code, v.version_number,
                    v.created_by.initials, v.extension
                )
            )

    def launch(self, *args, **kwargs):
        """launch renderer command
        """
        # do nothing if there is no window (called externally)
        if not self.window:
            return

        # warn the user about the ignore settings
        try:
            dAO = pm.PyNode('defaultArnoldRenderOptions')

            ignore_attrs = [
                'ignoreSubdivision',
                'ignoreDisplacement',
                'ignoreBump',
                'ignoreMotionBlur'
            ]

            attr_values = [
                (attr, dAO.getAttr(attr))
                for attr in ignore_attrs
                if dAO.getAttr(attr) is True
            ]

            if any(attr_values):
                msg_text = '<br>'.join(
                    map(
                        lambda x: '%s: %s' % (x[0], x[1]),
                        attr_values
                    )
                )

                response = pm.confirmDialog(
                    title='Ignore These Settings?',
                    message='You have ignored:<br><br>%s<br><br><b>Is that ok?</b>' % msg_text,
                    button=['Yes', 'No'],
                    defaultButton='No',
                    cancelButton='No',
                    dismissString='No'
                )

                if response == 'No':
                    return
        except pm.MayaNodeError:
            # no Arnold
            pass

        # check if rendering with persp camera
        try:
            wrong_camera_names = [
                'perspShape',
                'topShape',
                'sideShape',
                'fontShape',

                'persp1Shape',
                'perspShape1',
            ]
            renderable_cameras = [node for node in pm.ls(type='camera') if node.getAttr('renderable')]
            if any(map(lambda x: x.name() in wrong_camera_names, renderable_cameras)):
                response = pm.confirmDialog(
                    title='Rendering with Persp?',
                    message='You are rendering with <b>Persp Camera<b><br><br>Is that ok?</b>',
                    button=['Yes', 'No'],
                    defaultButton='No',
                    cancelButton='No',
                    dismissString='No'
                )

                if response == 'No':
                    return

            if len(renderable_cameras) > 1:
                response = pm.confirmDialog(
                    title='Rendering more than one Camera?',
                    message='You are rendering <b>more than one camera<b><br><br>Is that ok?</b>',
                    button=['Yes', 'No'],
                    defaultButton='No',
                    cancelButton='No',
                    dismissString='No'
                )

                if response == 'No':
                    return
            elif len(renderable_cameras) == 0:
                pm.confirmDialog(
                    title='No <b>Renderable</b> camera!!!',
                    message='There is no <b>renderable camera<b>!!!',
                    button=['Ok'],
                    defaultButton='Ok',
                    cancelButton='Ok',
                    dismissString='Ok'
                )
                return

        except pm.MayaNodeError:
            # no default render globals node
            pass

        drg = pm.PyNode('defaultRenderGlobals')
        render_engine = drg.getAttr('currentRenderer')
        # RENDERER SPECIFIC CHECKS

        if render_engine == 'redshift':
            # if the renderer is RedShift
            # check if unifiedDisableDivision is 1 which will take too much time
            # to render
            dro = pm.PyNode('redshiftOptions')
            if dro.unifiedDisableDivision.get() == 1:
                response = pm.confirmDialog(
                    title="Enabled **Don't Automatically Reduce Samples of Other Effects**",
                    message='It is not allowed to render with the following option is enabled:<br>'
                            '<br>'
                            "Don't Automatically Reduce Samples of Other Effects: Enabled<br>"
                            "<br>"
                            "Please DISABLE it!",
                    button=['OK'],
                    defaultButton='OK',
                    cancelButton='OK',
                    dismissString='OK'
                )
                return

        elif render_engine == 'arnold':
            # check if the samples are too high
            dAO = pm.PyNode('defaultArnoldRenderOptions')


            aa_samples = dAO.AASamples.get()
            diff_samples = dAO.GIDiffuseSamples.get()
            glossy_samples = dAO.GIGlossySamples.get()
            if int(pm.about(v=1)) >= 2017:
                sss_samples = dAO.GISssSamples.get()
            else:
                sss_samples = dAO.sssBssrdfSamples.get()

            total_diff_samples = aa_samples**2 * diff_samples**2
            total_glossy_samples = aa_samples**2 * glossy_samples**2
            total_sss_samples = aa_samples**2 * sss_samples**2

            max_allowed_diff_samples = 225
            max_allowed_glossy_samples = 100
            max_allowed_sss_samples = 800

            if total_diff_samples > max_allowed_diff_samples:
                pm.confirmDialog(
                    title="Too Much Diffuse Samples!!!",
                    message='You are using too much DIFFUSE SAMPLES (>%s)<br>'
                            '<br>'
                            'Please either reduce AA samples of Diffuse '
                            'Samples!!!' % max_allowed_diff_samples,
                    button=['OK'],
                    defaultButton='OK',
                    cancelButton='OK',
                    dismissString='OK'
                )
                return

            if total_glossy_samples > max_allowed_glossy_samples:
                pm.confirmDialog(
                    title="Too Much Glossy Samples!!!",
                    message='You are using too much GLOSSY SAMPLES (>%s)<br>'
                            '<br>'
                            'Please either reduce AA samples of Glossy '
                            'Samples!!!' % max_allowed_glossy_samples,
                    button=['OK'],
                    defaultButton='OK',
                    cancelButton='OK',
                    dismissString='OK'
                )
                return

            if total_sss_samples > max_allowed_sss_samples:
                pm.confirmDialog(
                    title="Too Much SSS Samples!!!",
                    message='You are using too much SSS SAMPLES (>%s)<br>'
                            '<br>'
                            'Please either reduce AA samples of SSS '
                            'Samples!!!' % max_allowed_sss_samples,
                    button=['OK'],
                    defaultButton='OK',
                    cancelButton='OK',
                    dismissString='OK'
                )
                return

            # check Light Samples
            # check point lights with zero radius but more than one samples
            all_point_lights = pm.ls(type='pointLight')
            ridiculous_point_lights = []
            for point_light in all_point_lights:
                if point_light.aiRadius.get() < 0.1 and point_light.aiSamples.get() > 1:
                    ridiculous_point_lights.append(point_light)

            if ridiculous_point_lights:
                pm.confirmDialog(
                    title="Unnecessary Samples on Point Lights!!!",
                    message='You are using too much SAMPLES (>1)<br>'
                            '<br>'
                            'on <b>Point lights with zero radius</b><br>'
                            '<br>'
                            'Please reduce the samples to 1',
                    button=['OK'],
                    defaultButton='OK',
                    cancelButton='OK',
                    dismissString='OK'
                )
                return

            # Check area lights with more than 2 samples
            all_area_lights = pm.ls(type=['areaLight', 'aiAreaLight'])
            ridiculous_area_lights = []
            for area_light in all_area_lights:
                if area_light.aiSamples.get() > 2:
                    ridiculous_area_lights.append(area_light)

            if ridiculous_area_lights:
                pm.confirmDialog(
                    title="Unnecessary Samples on Area Lights!!!",
                    message='You are using too much SAMPLES (>2) on<br>'
                            '<br>'
                            '<b>Area Lights</b><br>'
                            '<br>'
                            'Please reduce the samples to 2',
                    button=['OK'],
                    defaultButton='OK',
                    cancelButton='OK',
                    dismissString='OK'
                )
                return

            # Check directional lights with angle == 0 and samples > 1
            all_directional_lights = pm.ls(type='directionalLight')
            ridiculous_directional_lights = []
            dir_sample_attr_name = 'aiSamples'
            # if pm.about(v=1) == "2014":
            #     dir_sample_attr_name = 'aiSamples'

            for directional_light in all_directional_lights:
                if directional_light.aiAngle.get() == 0 and directional_light.attr(dir_sample_attr_name).get() > 1:
                    ridiculous_directional_lights.append(directional_light)

            if ridiculous_directional_lights:
                pm.confirmDialog(
                    title="Unnecessary Samples on Directional Lights!!!",
                    message='You are using too much SAMPLES (>1) on <br>'
                            '<br>'
                            '<b>Directional lights with zero angle</b><br>'
                            '<br>'
                            'Please reduce the samples to 1',
                    button=['OK'],
                    defaultButton='OK',
                    cancelButton='OK',
                    dismissString='OK'
                )
                return

        # get values
        start_frame = pm.intField('cgru_afanasy__start_frame', q=1, v=1)
        end_frame = pm.intField('cgru_afanasy__end_frame', q=1, v=1)
        frames_per_task = \
            pm.intField('cgru_afanasy__frames_per_task', q=1, v=1)
        by_frame = pm.intField('cgru_afanasy__by_frame', q=1, v=1)
        hosts_mask = pm.textField('cgru_afanasy__hosts_mask', q=1, text=True)
        hosts_exclude = pm.textField('cgru_afanasy__hosts_exclude', q=1, text=True)
        separate_layers = \
            pm.checkBox('cgru_afanasy__separate_layers', q=1, v=1)
        pause = pm.checkBox('cgru_afanasy__paused', q=1, v=1)
        life_time = pm.intField('cgru_afanasy__life_time', q=1, v=1)

        # check values
        if start_frame > end_frame:
            temp = end_frame
            end_frame = start_frame
            start_frame = temp

        frames_per_task = max(1, frames_per_task)
        by_frame = max(1, by_frame)

        # store without quota sign
        hosts_mask = hosts_mask.replace('"', '')
        hosts_exclude = hosts_exclude.replace('"', '')

        # store field values
        pm.optionVar['cgru_afanasy__start_frame_ov'] = start_frame
        pm.optionVar['cgru_afanasy__end_frame_ov'] = end_frame
        pm.optionVar['cgru_afanasy__frames_per_task_ov'] = frames_per_task
        pm.optionVar['cgru_afanasy__by_frame_ov'] = by_frame
        pm.optionVar['cgru_afanasy__hosts_mask_ov'] = hosts_mask
        pm.optionVar['cgru_afanasy__hosts_exclude_ov'] = hosts_exclude
        pm.optionVar['cgru_afanasy__separate_layers_ov'] = separate_layers
        pm.optionVar['cgru_afanasy__life_time_ov'] = life_time

        # get paths
        scene_name = pm.sceneName()
        datetime = '%s%s' % (
            time.strftime('%y%m%d-%H%M%S-'),
            str(time.time() - int(time.time()))[2:5]
        )

        filename = '%s.%s.mb' % (scene_name, datetime)

        project_path = pm.workspace(q=1, rootDirectory=1)

        outputs = \
            pm.renderSettings(fullPath=1, firstImageName=1, lastImageName=1)

        # job_name = os.path.basename(scene_name)
        job_name = self.generate_job_name()

        logger.debug('%ss %se %sr' % (start_frame, end_frame, by_frame))
        logger.debug('scene        = %s' % scene_name)
        logger.debug('file         = %s' % filename)
        logger.debug('job_name     = %s' % job_name)
        logger.debug('project_path = %s' % project_path)
        logger.debug('outputs      = %s' % outputs)

        if pm.checkBox('cgru_afanasy__close', q=1, v=1):
            pm.deleteUI(self.window)



        job = af.Job(job_name)

        stored_log_level = None
        if render_engine == 'arnold':
            # set the verbosity level to warning+info
            aro = pm.PyNode('defaultArnoldRenderOptions')
            stored_log_level = aro.getAttr('log_verbosity')
            aro.setAttr('log_verbosity', 1)
            # set output to console
            aro.setAttr("log_to_console", 1)
        elif render_engine == 'redshift':
            # set the verbosity level to detailed+info
            redshift = pm.PyNode('redshiftOptions')
            stored_log_level = redshift.logLevel.get()
            redshift.logLevel.set(2)

        # save file
        pm.saveAs(
            filename,
            force=1,
            type='mayaBinary'
        )

        # rename back to original name
        pm.renameFile(scene_name)

        # create the render command
        mrc = MayaRenderCommandBuilder(
            name=job_name, file_full_path=filename,
            render_engine=render_engine, project=project_path,
            by_frame=by_frame
        )

        # submit renders
        blocks = []
        if separate_layers:
            # render each layer separately
            rlm = pm.PyNode('renderLayerManager')
            layers = [layer for layer in rlm.connections()
                      if layer.renderable.get()]

            for layer in layers:
                mrc_layer = copy.copy(mrc)
                layer_name = layer.name()
                mrc_layer.name = layer_name
                mrc_layer.render_layer = layer_name

                # create a new block for this layer
                block = af.Block(
                    layer_name,
                    renderer_to_block_type.get(render_engine, 'maya')
                )

                block.setFiles(
                    afcommon.patternFromDigits(
                        afcommon.patternFromStdC(
                            afcommon.patternFromPaths(outputs[0], outputs[1])
                        )
                    ).split(';')
                )
                block.setNumeric(
                    start_frame, end_frame, frames_per_task, by_frame
                )
                block.setCommand(mrc_layer.build_command())

                blocks.append(block)
        else:
            # create only one block
            block = af.Block(
                'All Layers',
                renderer_to_block_type.get(render_engine, 'maya')
            )

            block.setFiles(
                afcommon.patternFromDigits(
                    afcommon.patternFromStdC(
                        afcommon.patternFromPaths(outputs[0], outputs[1])
                    )
                ).split(';')
            )
            block.setNumeric(
                start_frame, end_frame, frames_per_task, by_frame
            )
            block.setCommand(mrc.build_command())

            blocks.append(block)

        job.setFolder('input', os.path.dirname(filename))
        job.setFolder('output', os.path.dirname(outputs[0]))
        job.setHostsMask(hosts_mask)
        job.setHostsMaskExclude(hosts_exclude)
        if life_time > 0:
            job.setTimeLife(life_time * 3600)
        else:
            job.setTimeLife(240 * 3600)

        job.setCmdPost('deletefiles "%s"' % os.path.abspath(filename))
        if pause:
            job.offline()

        # add blocks
        job.blocks.extend(blocks)

        status, data = job.send()
        if not status:
            pm.PopupError('Something went wrong!')
        print('data: %s' % data)

        # restore log level
        if render_engine == 'arnold':
            aro = pm.PyNode('defaultArnoldRenderOptions')
            aro.setAttr('log_verbosity', stored_log_level)
            # disable set output to console
            aro.setAttr("log_to_console", 0)
        elif render_engine == 'redshift':
            redshift = pm.PyNode('redshiftOptions')
            redshift.logLevel.set(stored_log_level)
