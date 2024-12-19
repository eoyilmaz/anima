# -*- coding: utf-8 -*-
"""
Test code

from anima.dcc.resolve import toolbox
dialog = toolbox.UI()

"""
import os

from anima.ui.base import ui_caller
from anima.ui.lib import QtGui, QtWidgets
from anima.ui.utils import ColorList, set_widget_bg_color


__here__ = os.path.abspath(__file__)


def UI(app_in=None, executor=None, **kwargs):
    """Show the UI.

    Args:
        app_in: A Qt Application instance, which you can pass to let the UI be attached
            to the given applications event process.
        executor: Instead of calling app.exec_ the UI will call this given function. It
            also passes the created app instance to this executor.

    Returns:
        QtWidgets.QDialog: The UI dialog/window.
    """
    return ui_caller(app_in, executor, ToolboxDialog, **kwargs)


class ToolboxDialog(QtWidgets.QDialog):
    """The toolbox dialog."""

    def __init__(self, *args, **kwargs):
        super(ToolboxDialog, self).__init__(*args, **kwargs)
        self._setup_ui()

    def _setup_ui(self):
        """create the main"""
        tlb = ToolboxLayout(self)
        self.setLayout(tlb)

        # setup icon
        global __here__
        icon_path = os.path.abspath(
            os.path.join(__here__, "../../../ui/images/DaVinciResolve.png")
        )
        try:
            icon = QtWidgets.QIcon(icon_path)
        except AttributeError:
            icon = QtGui.QIcon(icon_path)

        self.setWindowIcon(icon)

        self.setWindowTitle("DaVinci Resolve Toolbox")


class ToolboxLayout(QtWidgets.QVBoxLayout):
    """The toolbox layout"""

    def __init__(self, *args, **kwargs):
        super(ToolboxLayout, self).__init__(*args, **kwargs)
        self._setup_ui()

    def _setup_ui(self):
        """add tools"""
        gamma = 1.0
        if os.name == "darwin":
            gamma = 0.455

        color_list = ColorList(gamma=gamma)

        # create the main tab layout
        main_tab_widget = QtWidgets.QTabWidget()
        self.addWidget(main_tab_widget)

        # add the ShotTools Tab
        conformer_tab_widget = QtWidgets.QWidget()
        shot_tools_tab_widget = QtWidgets.QWidget()
        review_tools_tab_widget = QtWidgets.QWidget()

        # add the Output Tab
        output_tab_widget = QtWidgets.QWidget()
        output_tab_vertical_layout = QtWidgets.QVBoxLayout()
        output_tab_form_layout = QtWidgets.QFormLayout()
        output_tab_vertical_layout.addLayout(output_tab_form_layout)
        output_tab_widget.setLayout(output_tab_vertical_layout)

        # main_tab_widget.addTab(general_tab_widget, 'Generic')
        main_tab_widget.addTab(conformer_tab_widget, "Conformer")
        main_tab_widget.addTab(shot_tools_tab_widget, "Shot Tools")
        main_tab_widget.addTab(review_tools_tab_widget, "Review Tools")
        main_tab_widget.addTab(output_tab_widget, "Output")

        # add the conformer
        conformer_layout = QtWidgets.QVBoxLayout(conformer_tab_widget)
        from anima.dcc.resolve import conformer

        conformer.ConformerUI(conformer_layout)

        # add the shot tools
        from anima.dcc.resolve.shot_tools import ShotManagerUI, ReviewManagerUI

        shot_tools_layout = QtWidgets.QVBoxLayout(shot_tools_tab_widget)
        ShotManagerUI(shot_tools_layout)

        # add review tools
        review_tools_layout = QtWidgets.QVBoxLayout(review_tools_tab_widget)
        ReviewManagerUI(review_tools_layout)

        label_role = QtWidgets.QFormLayout.LabelRole
        field_role = QtWidgets.QFormLayout.FieldRole

        # Create tools for general tab
        from anima.ui.utils import create_button

        i = -1

        current_vertical_layout = output_tab_vertical_layout
        current_form_layout = output_tab_form_layout

        # -------------------------------------------------------------------
        # Render Preset
        i += 1
        render_preset_label = QtWidgets.QLabel()
        render_preset_label.setText("Render Preset")
        current_form_layout.setWidget(i, label_role, render_preset_label)

        render_preset_horizontal_layout = QtWidgets.QHBoxLayout()
        current_form_layout.setLayout(i, field_role, render_preset_horizontal_layout)

        self.render_presets_combo_box = QtWidgets.QComboBox()
        self.fill_preset_combo_box()
        render_preset_horizontal_layout.addWidget(self.render_presets_combo_box)

        from functools import partial

        self.refresh_render_presets_button = QtWidgets.QPushButton()
        self.refresh_render_presets_button.setIcon(
            self.parent().style().standardIcon(QtWidgets.QStyle.SP_BrowserReload)
        )
        self.refresh_render_presets_button.setFixedWidth(24)
        self.refresh_render_presets_button.clicked.connect(
            partial(self.fill_preset_combo_box)
        )
        render_preset_horizontal_layout.addWidget(self.refresh_render_presets_button)

        # -------------------------------------------------------------------
        # Filename Template
        i += 1
        filename_template_label = QtWidgets.QLabel()
        filename_template_label.setText("Filename")
        current_form_layout.setWidget(i, label_role, filename_template_label)

        # template_line_edit.setText()
        filename_template_combo_box = QtWidgets.QComboBox()
        filename_template_combo_box.setEditable(True)
        filename_template_combo_box.addItems(GenericTools.default_output_templates)
        current_form_layout.setWidget(i, field_role, filename_template_combo_box)

        # -------------------------------------------------------------------
        # Output Template
        i += 1
        location_template_label = QtWidgets.QLabel()
        location_template_label.setText("Location")
        current_form_layout.setWidget(i, label_role, location_template_label)

        location_template_line_edit = QtWidgets.QLineEdit()
        current_form_layout.setWidget(i, field_role, location_template_line_edit)

        # -------------------------------------------------------------------
        # Extend Start/End Controls
        i += 1

        extend_start_label = QtWidgets.QLabel()
        extend_start_label.setText("Extend Start")
        current_form_layout.setWidget(i, label_role, extend_start_label)

        extend_start_spinbox = QtWidgets.QSpinBox()
        extend_start_spinbox.setMinimum(0)
        current_form_layout.setWidget(i, field_role, extend_start_spinbox)

        i += 1
        extend_end_label = QtWidgets.QLabel()
        extend_end_label.setText("Extend End")
        current_form_layout.setWidget(i, label_role, extend_end_label)

        extend_end_spinbox = QtWidgets.QSpinBox()
        extend_end_spinbox.setMinimum(0)
        current_form_layout.setWidget(i, field_role, extend_end_spinbox)

        # -------------------------------------------------------------------
        # Clip Output Generator
        i += 1

        def clip_output_generator_wrapper():
            #  = version_spinbox.value()
            filename_template = filename_template_combo_box.currentText()
            location_template = location_template_line_edit.text()
            extend_start = extend_start_spinbox.value()
            extend_end = extend_end_spinbox.value()
            render_preset = self.render_presets_combo_box.currentText()

            from anima.dcc.resolve import shot_tools

            sm = shot_tools.ShotManager()
            clip = sm.get_current_clip()

            GenericTools.clip_output_generator(
                clip=clip,
                filename_template=filename_template,
                location_template=location_template,
                extend_start=extend_start,
                extend_end=extend_end,
                render_preset=render_preset,
            )

        clip_output_generator_button = QtWidgets.QPushButton()
        clip_output_generator_button.setText("Output - Current Clip")
        clip_output_generator_button.clicked.connect(clip_output_generator_wrapper)
        set_widget_bg_color(clip_output_generator_button, color_list)
        color_list.next()

        current_form_layout.setWidget(i, field_role, clip_output_generator_button)

        # -------------------------------------------------------------------
        # Clip Output Generator By Index
        i += 1
        clip_index_label = QtWidgets.QLabel()
        clip_index_label.setText("Clip Index")
        current_form_layout.setWidget(i, label_role, clip_index_label)

        clip_index_spinbox = QtWidgets.QSpinBox()
        clip_index_spinbox.setMinimum(1)
        current_form_layout.setWidget(i, field_role, clip_index_spinbox)

        i += 1

        def clip_output_generator_by_index_wrapper():
            clip_index = clip_index_spinbox.value()
            template = filename_template_combo_box.currentText()
            extend_start = extend_start_spinbox.value()
            extend_end = extend_end_spinbox.value()
            render_preset = self.render_presets_combo_box.currentText()
            GenericTools.clip_output_generator_by_clip_index(
                clip_index=clip_index,
                filename_template=template,
                extend_start=extend_start,
                extend_end=extend_end,
                render_preset=render_preset,
            )

        output_clip_by_clip_index_push_button = QtWidgets.QPushButton()
        output_clip_by_clip_index_push_button.setText("Output - Clip By Index")
        output_clip_by_clip_index_push_button.clicked.connect(
            clip_output_generator_by_index_wrapper
        )
        current_form_layout.setWidget(
            i, field_role, output_clip_by_clip_index_push_button
        )
        set_widget_bg_color(output_clip_by_clip_index_push_button, color_list)
        color_list.next()

        # -------------------------------------------------------------------
        # Add Divider
        i += 1
        line = QtWidgets.QFrame()
        line.setFrameShape(QtWidgets.QFrame.HLine)
        line.setFrameShadow(QtWidgets.QFrame.Sunken)
        current_form_layout.setWidget(i, field_role, line)

        # -------------------------------------------------------------------
        from anima.dcc.resolve import shot_tools

        start_frame = end_frame = 0
        try:
            shot_manager = shot_tools.ShotManager()
            timeline = shot_manager.get_current_timeline()
            start_frame = timeline.GetStartFrame()
            end_frame = timeline.GetEndFrame()
        except AttributeError:
            # Resolve is not open yet
            pass

        # Get In Point
        i += 1
        in_point_label = QtWidgets.QLabel()
        in_point_label.setText("In Point")
        current_form_layout.setWidget(i, label_role, in_point_label)

        layout = QtWidgets.QHBoxLayout()
        current_form_layout.setLayout(i, field_role, layout)

        in_point_spin_box = QtWidgets.QSpinBox()
        in_point_spin_box.setMaximum(99999999)
        in_point_spin_box.setValue(start_frame)
        layout.addWidget(in_point_spin_box)

        get_in_point_push_button = QtWidgets.QPushButton()
        get_in_point_push_button.setText("<<< In Point")
        layout.addWidget(get_in_point_push_button)
        set_widget_bg_color(get_in_point_push_button, color_list)

        def get_in_out_point_callback(spin_box):
            from anima.dcc.resolve import shot_tools

            shot_manager = shot_tools.ShotManager()
            timeline = shot_manager.get_current_timeline()
            current_timecode = timeline.GetCurrentTimecode()
            fps = timeline.GetSetting("timelineFrameRate")
            import timecode

            tc1 = timecode.Timecode(fps, current_timecode)
            spin_box.setValue(tc1.frames - 1)

        from functools import partial

        get_in_point_push_button.clicked.connect(
            partial(get_in_out_point_callback, in_point_spin_box)
        )

        # Get Out Point
        i += 1
        out_point_label = QtWidgets.QLabel()
        out_point_label.setText("Out Point")
        current_form_layout.setWidget(i, label_role, out_point_label)

        layout = QtWidgets.QHBoxLayout()
        current_form_layout.setLayout(i, field_role, layout)

        out_point_spin_box = QtWidgets.QSpinBox()
        out_point_spin_box.setMaximum(99999999)
        out_point_spin_box.setValue(end_frame)
        layout.addWidget(out_point_spin_box)

        get_out_point_push_button = QtWidgets.QPushButton()
        get_out_point_push_button.setText("<<< Out Point")
        layout.addWidget(get_out_point_push_button)
        set_widget_bg_color(get_out_point_push_button, color_list)
        color_list.next()

        get_out_point_push_button.clicked.connect(
            partial(get_in_out_point_callback, out_point_spin_box)
        )

        # Start Clip Number
        i += 1
        start_clip_number_label = QtWidgets.QLabel()
        start_clip_number_label.setText("Start Clip #")
        current_form_layout.setWidget(i, label_role, start_clip_number_label)

        start_clip_number_spin_box = QtWidgets.QSpinBox()
        start_clip_number_spin_box.setMinimum(0)
        start_clip_number_spin_box.setMaximum(1e7)
        current_form_layout.setWidget(i, field_role, start_clip_number_spin_box)

        i += 1
        clip_number_by_label = QtWidgets.QLabel()
        clip_number_by_label.setText("Clip # By")
        current_form_layout.setWidget(i, label_role, clip_number_by_label)

        clip_number_by_spin_box = QtWidgets.QSpinBox()
        clip_number_by_spin_box.setValue(10)
        clip_number_by_spin_box.setMaximum(99990)
        current_form_layout.setWidget(i, field_role, clip_number_by_spin_box)

        # Padding
        i += 1
        padding_label = QtWidgets.QLabel()
        padding_label.setText("Padding")
        current_form_layout.setWidget(i, label_role, padding_label)

        padding_spin_box = QtWidgets.QSpinBox()
        padding_spin_box.setValue(4)
        padding_spin_box.setMinimum(0)
        padding_spin_box.setMaximum(10)
        current_form_layout.setWidget(i, field_role, padding_spin_box)

        # Per Clip Output Generator
        i += 1

        def per_clip_output_generator_wrapper():
            filename_template = filename_template_combo_box.currentText()
            location_template = location_template_line_edit.text()
            extend_start = extend_start_spinbox.value()
            extend_end = extend_end_spinbox.value()
            start_clip_number = start_clip_number_spin_box.value()
            clip_number_by = clip_number_by_spin_box.value()
            start_frame = in_point_spin_box.value()
            end_frame = out_point_spin_box.value()
            padding = padding_spin_box.value()
            render_preset = self.render_presets_combo_box.currentText()

            GenericTools.per_clip_output_generator(
                filename_template=filename_template,
                location_template=location_template,
                extend_start=extend_start,
                extend_end=extend_end,
                start_frame=start_frame,
                end_frame=end_frame,
                start_clip_number=start_clip_number,
                clip_number_by=clip_number_by,
                padding=padding,
                render_preset=render_preset,
            )

        per_clip_output_generator_push_button = QtWidgets.QPushButton()
        per_clip_output_generator_push_button.setText("Output - Per Clip")
        per_clip_output_generator_push_button.clicked.connect(
            per_clip_output_generator_wrapper
        )
        set_widget_bg_color(per_clip_output_generator_push_button, color_list)
        color_list.next()

        current_form_layout.setWidget(
            i, field_role, per_clip_output_generator_push_button
        )

        # -------------------------------------------------------------------
        # Add the stretcher
        current_vertical_layout.addStretch()

    def fill_preset_combo_box(self):
        """fills the preset comboBox"""
        from anima.dcc.resolve.shot_tools import ShotManager

        shot_manager = ShotManager()
        render_preset_list = shot_manager.resolve_project.GetRenderPresetList()
        current_text = self.render_presets_combo_box.currentText()
        self.render_presets_combo_box.clear()
        self.render_presets_combo_box.addItems(sorted(render_preset_list))
        if current_text:
            # select the previous preset
            index = self.render_presets_combo_box.findText(current_text)
            if index:
                self.render_presets_combo_box.setCurrentIndex(index)


class GenericTools(object):
    """Generic Tools"""

    default_output_templates = [
        "%{Clip Name}",
        "%{Clip Base Name}_Denoised",
        "%{Timeline Name}_CL%{Clip #}_v001",
    ]

    @classmethod
    def per_clip_output_generator(
        cls,
        filename_template="",
        location_template="",
        extend_start=0,
        extend_end=0,
        start_frame=None,
        end_frame=None,
        start_clip_number=10,
        clip_number_by=10,
        padding=4,
        render_preset="",
        use_relative_clip_index=False,
    ):
        """generates render tasks per clips on the current timeline

        :param str filename_template:
        :param str location_template:
        :param int extend_start:
        :param int extend_end:
        :param int start_frame:
        :param int end_frame:
        :param int start_clip_number:
        :param int clip_number_by:
        :param int padding: Defaults to 4
        :param str render_preset: Render preset name
        :param bool use_relative_clip_index: If True, a relative clip index will be used which is the clip index in the
          current export, meaning if disabled clips are present, the index will not be incremented for those clips.
        """
        from anima.dcc import blackmagic

        resolve = blackmagic.get_resolve()

        pm = resolve.GetProjectManager()
        proj = pm.GetCurrentProject()
        timeline = proj.GetCurrentTimeline()

        clips = timeline.GetItemsInTrack("video", 1)

        if filename_template == "":
            filename_template = cls.default_output_templates[0]

        import copy
        from anima.dcc.resolve import template, shot_tools

        resolve_template_vars = copy.copy(template.RESOLVE_TEMPLATE_VARS)

        i = 0
        for clip_index in clips:
            clip = clips[clip_index]
            shot_clip = shot_tools.ShotClip(clip=clip, timeline=timeline)
            if not shot_clip.is_enabled():
                continue

            clip_start = clip.GetStart()
            clip_end = clip.GetEnd()
            if clip_start >= start_frame and clip_end <= end_frame:
                if use_relative_clip_index:
                    calculated_clip_number = start_clip_number + clip_number_by * i
                    i += 1
                else:
                    calculated_clip_number = start_clip_number + clip_number_by * (
                        int(clip_index) - 1
                    )

                calculated_clip_number_as_str = "%s" % calculated_clip_number
                resolve_template_vars["Clip #"] = calculated_clip_number_as_str.zfill(
                    padding
                )
                cls.clip_output_generator_by_clip_index(
                    clip_index=clip_index,
                    filename_template=template.format_resolve_template(
                        filename_template, resolve_template_vars
                    ),
                    location_template=template.format_resolve_template(
                        location_template, resolve_template_vars
                    ),
                    extend_start=extend_start,
                    extend_end=extend_end,
                    render_preset=render_preset,
                )

    @classmethod
    def clip_output_generator_by_clip_index(
        cls,
        clip_index=1,
        filename_template="",
        location_template="",
        extend_start=0,
        extend_end=0,
        render_preset="",
    ):
        """Generators

        :param int clip_index:
        :param str filename_template: The filename template.
        :param str location_template: The output location template.
        :param int extend_start:
        :param int extend_end:
        :param str render_preset: Render preset name.
        :return:
        """
        from anima.dcc import blackmagic

        resolve = blackmagic.get_resolve()

        pm = resolve.GetProjectManager()
        proj = pm.GetCurrentProject()
        timeline = proj.GetCurrentTimeline()

        clips = timeline.GetItemsInTrack("video", 1)
        clip = clips[clip_index]

        cls.clip_output_generator(
            clip,
            filename_template=filename_template,
            location_template=location_template,
            extend_start=extend_start,
            extend_end=extend_end,
            render_preset=render_preset,
        )

    @classmethod
    def clip_output_generator(
        cls,
        clip,
        filename_template="",
        location_template="",
        extend_start=0,
        extend_end=0,
        render_preset="",
        padding=4,
    ):
        """Generate render tasks for the clip with the given index.

        Args:
            clip (TimelineItem): A Resolve TimelineItem
            filename_template (str): Output template,

                See the ``anima.dcc.resolve.template.RESOLVE_TEMPLATE_VARS`` for Resolve
                template variables that can be directly used like.

                These will be passed to Resolve directly.

            location_template (str): The output location template.
            extend_start (int): Include this many frames at the start of the clip.
                Default is 0.
            extend_end (int): Include this many frames at the end of the clip. Default
                is 0.
            render_preset (str): The render preset to use.
            padding (int): Padding in used in the clip number. Default is 4.
        """

        if filename_template == "":
            filename_template = cls.default_output_templates[0]

        from anima.dcc.resolve import template
        import copy

        resolve_template_vars = copy.copy(template.RESOLVE_TEMPLATE_VARS)

        from anima.dcc import blackmagic

        resolve = blackmagic.get_resolve()

        pm = resolve.GetProjectManager()
        proj = pm.GetCurrentProject()
        timeline = proj.GetCurrentTimeline()
        clips = timeline.GetItemsInTrack("video", 1)
        media_pool_item = clip.GetMediaPoolItem()
        clip_properties = media_pool_item.GetClipProperty()

        from anima.dcc.resolve import shot_tools

        shot_clip = shot_tools.ShotClip(clip=clip, timeline=timeline)
        marker = shot_clip.get_shot_related_marker()
        if marker:
            clip_properties["Marker Name"] = marker["name"]
            clip_properties["Marker Note"] = marker["note"]

        # Modify Clip Directory
        clip_properties["Clip Base Name"] = os.path.splitext(
            clip_properties["Clip Name"]
        )[0]
        clip_properties["Clip Directory"] = os.path.dirname(
            clip_properties["File Path"]
        )

        # Modify "Clip #" variable
        clip_index = -1
        i = 0
        for index in clips:
            if clips[index].GetUniqueId() == clip.GetUniqueId():
                clip_index = index
                break

        clip_properties["Clip #"] = f"{clip_index:0{padding}d}"

        # update clip variables in Python side so that we can use it in folder template
        resolve_template_vars.update(clip_properties)

        result = proj.LoadRenderPreset(render_preset)
        if not result:
            print("No preset named: %s" % render_preset)
        else:
            print("Preset loaded successfully: %s" % render_preset)

        # create a new render output for each clip
        proj.SetRenderSettings(
            {
                "MarkIn": clip.GetStart() - extend_start,
                "MarkOut": clip.GetEnd() - 1 + extend_end,
                "CustomName": template.format_resolve_template(
                    filename_template, resolve_template_vars
                ),
                "TargetDir": template.format_resolve_template(
                    location_template, resolve_template_vars
                ),
            }
        )

        proj.AddRenderJob()
