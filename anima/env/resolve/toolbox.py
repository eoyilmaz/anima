# -*- coding: utf-8 -*-
"""
Test code

from anima.env.resolve import toolbox
reload(toolbox)
dialog = toolbox.UI()

"""
import sys
import os
import functools

from anima.ui.base import ui_caller
from anima.ui.lib import QtGui, QtWidgets


__here__ = os.path.abspath(__file__)


def reload_lib(lib):
    """helper funtion to reload a lib
    """
    if sys.version_info[0] >= 3:  # Python 3
        import importlib
        importlib.reload(lib)
    else:
        reload(lib)


def UI(app_in=None, executor=None, **kwargs):
    """
    :param app_in: A Qt Application instance, which you can pass to let the UI
      be attached to the given applications event process.

    :param executor: Instead of calling app.exec_ the UI will call this given
      function. It also passes the created app instance to this executor.

    """
    return ui_caller(app_in, executor, ToolboxDialog, **kwargs)


class ToolboxDialog(QtWidgets.QDialog):
    """The toolbox dialog
    """

    def __init__(self, *args, **kwargs):
        super(ToolboxDialog, self).__init__(*args, **kwargs)
        self.setup_ui()

    def setup_ui(self):
        """create the main
        """
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
    """The toolbox layout
    """

    def __init__(self, *args, **kwargs):
        super(ToolboxLayout, self).__init__(*args, **kwargs)
        self.setup_ui()

    def setup_ui(self):
        """add tools
        """
        # create the main tab layout
        main_tab_widget = QtWidgets.QTabWidget(self.widget())
        self.addWidget(main_tab_widget)

        # add the ShotTools Tab
        shot_tools_tab_widget = QtWidgets.QWidget(self.widget())
        conformer_tab_widget = QtWidgets.QWidget(self.widget())

        # add the Output Tab
        output_tab_widget = QtWidgets.QWidget(self.widget())
        output_tab_vertical_layout = QtWidgets.QVBoxLayout(self.widget())
        output_tab_form_layout = QtWidgets.QFormLayout(self.widget())
        output_tab_vertical_layout.addLayout(output_tab_form_layout)
        output_tab_widget.setLayout(output_tab_vertical_layout)

        # main_tab_widget.addTab(general_tab_widget, 'Generic')
        main_tab_widget.addTab(conformer_tab_widget, 'Conformer')
        main_tab_widget.addTab(shot_tools_tab_widget, 'Shot Tools')
        main_tab_widget.addTab(output_tab_widget, 'Output')

        # add the shot tools
        from anima.env.resolve import shot_tools
        st = shot_tools.ShotToolsLayout(self.widget())
        shot_tools_tab_widget.setLayout(st)

        label_role = QtWidgets.QFormLayout.LabelRole
        field_role = QtWidgets.QFormLayout.FieldRole

        # Create tools for general tab
        from anima.ui.utils import add_button
        i = -1

        current_vertical_layout = output_tab_vertical_layout
        current_form_layout = output_tab_form_layout
        # -------------------------------------------------------------------
        # Common Controls
        i += 1
        common_output_controls_label = QtWidgets.QLabel()
        common_output_controls_label.setText("=========== Common Output Controls ===========")
        current_form_layout.setWidget(i, field_role, common_output_controls_label)

        # -------------------------------------------------------------------
        # Template
        i += 1
        template_label = QtWidgets.QLabel()
        template_label.setText("Template")
        current_form_layout.setWidget(i, label_role, template_label)

        template_line_edit = QtWidgets.QLineEdit()
        template_line_edit.setText(GenericTools.default_output_template)
        current_form_layout.setWidget(i, field_role, template_line_edit)

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
            template = template_line_edit.text()
            extend_start = extend_start_spinbox.value()
            extend_end = extend_end_spinbox.value()

            from anima.env.resolve import shot_tools
            sm = shot_tools.ShotManager()
            clip = sm.get_current_clip()

            GenericTools.clip_output_generator(
                clip=clip,
                template=template,
                extend_start=extend_start,
                extend_end=extend_end
            )

        clip_output_generator_button = QtWidgets.QPushButton()
        clip_output_generator_button.setText("Output - Current Clip")
        clip_output_generator_button.clicked.connect(clip_output_generator_wrapper)

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
            template = template_line_edit.text()
            extend_start = extend_start_spinbox.value()
            extend_end = extend_end_spinbox.value()
            GenericTools.clip_output_generator_by_clip_index(
                clip_index=clip_index,
                template=template,
                extend_start=extend_start,
                extend_end=extend_end
            )

        output_clip_by_clip_index_push_button = QtWidgets.QPushButton()
        output_clip_by_clip_index_push_button.setText('Output - Clip By Index')
        output_clip_by_clip_index_push_button.clicked.connect(clip_output_generator_by_index_wrapper)
        current_form_layout.setWidget(i, field_role, output_clip_by_clip_index_push_button)

        # -------------------------------------------------------------------
        # Add Divider
        i += 1
        line = QtWidgets.QFrame()
        line.setFrameShape(QtWidgets.QFrame.HLine)
        line.setFrameShadow(QtWidgets.QFrame.Sunken)
        current_form_layout.setWidget(i, field_role, line)

        # -------------------------------------------------------------------
        from anima.env.resolve import shot_tools

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

        def get_in_out_point_callback(spin_box):
            from anima.env.resolve import shot_tools
            shot_manager = shot_tools.ShotManager()
            timeline = shot_manager.get_current_timeline()
            current_timecode = timeline.GetCurrentTimecode()
            fps = timeline.GetSetting("timelineFrameRate")
            import timecode
            tc1 = timecode.Timecode(fps, current_timecode)
            spin_box.setValue(tc1.frames - 1)

        get_in_point_push_button.clicked.connect(functools.partial(get_in_out_point_callback, in_point_spin_box))

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

        get_out_point_push_button.clicked.connect(functools.partial(get_in_out_point_callback, out_point_spin_box))

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
        current_form_layout.setWidget(i, label_role, padding_label)

        padding_spin_box = QtWidgets.QSpinBox()
        padding_spin_box.setValue(4)
        padding_spin_box.setMinimum(0)
        padding_spin_box.setMaximum(10)
        current_form_layout.setWidget(i, field_role, padding_spin_box)

        # Per Clip Output Generator
        i += 1

        def per_clip_output_generator_wrapper():
            template = template_line_edit.text()
            extend_start = extend_start_spinbox.value()
            extend_end = extend_end_spinbox.value()
            start_clip_number = start_clip_number_spin_box.value()
            clip_number_by = clip_number_by_spin_box.value()
            start_frame = in_point_spin_box.value()
            end_frame = out_point_spin_box.value()
            padding = padding_spin_box.value()
            GenericTools.per_clip_output_generator(
                template=template,
                extend_start=extend_start,
                extend_end=extend_end,
                start_frame=start_frame,
                end_frame=end_frame,
                start_clip_number=start_clip_number,
                clip_number_by=clip_number_by,
                padding=padding
            )

        per_clip_output_generator_push_button = QtWidgets.QPushButton()
        per_clip_output_generator_push_button.setText("Output - Per Clip")
        per_clip_output_generator_push_button.clicked.connect(per_clip_output_generator_wrapper)

        current_form_layout.setWidget(i, field_role, per_clip_output_generator_push_button)

        # -------------------------------------------------------------------
        # Add the stretcher
        current_vertical_layout.addStretch()


class GenericTools(object):
    """Generic Tools
    """

    default_output_template = "%{Timeline Name}_CL%{Clip #}_v001"

    @classmethod
    def per_clip_output_generator(cls, template="", extend_start=0, extend_end=0, start_frame=None, end_frame=None, start_clip_number=10, clip_number_by=10, padding=4):
        """generates render tasks per clips on the current timeline

        :param str template:
        :param int extend_start:
        :param int extend_end:
        :param int start_frame:
        :param int end_frame:
        :param int start_clip_number:
        :param int clip_number_by:
        :param int padding: Defaults to 4
        """
        from anima.env import blackmagic
        resolve = blackmagic.get_resolve()

        pm = resolve.GetProjectManager()
        proj = pm.GetCurrentProject()
        timeline = proj.GetCurrentTimeline()

        clips = timeline.GetItemsInTrack("video", 1)

        if template == "":
            template = cls.default_output_template

        i = 0
        for clip_index in clips:
            clip = clips[clip_index]
            clip_start = clip.GetStart()
            clip_end = clip.GetEnd()
            if clip_start >= start_frame and clip_end <= end_frame:
                calculated_clip_number = start_clip_number + clip_number_by * i
                i += 1
                calculated_clip_number_as_str = "%s" % calculated_clip_number
                temp_template = template.replace("%{Clip #}", calculated_clip_number_as_str.zfill(padding))
                GenericTools.clip_output_generator_by_clip_index(
                    clip_index=clip_index,
                    template=temp_template,
                    extend_start=extend_start,
                    extend_end=extend_end,
                )

    @classmethod
    def clip_output_generator_by_clip_index(cls, clip_index=1, template="", extend_start=0, extend_end=0):
        """Generators

        :param clip_index:
        :param template:
        :param int extend_start:
        :param int extend_end:
        :return:
        """
        from anima.env import blackmagic
        resolve = blackmagic.get_resolve()

        pm = resolve.GetProjectManager()
        proj = pm.GetCurrentProject()
        timeline = proj.GetCurrentTimeline()

        clips = timeline.GetItemsInTrack("video", 1)
        clip = clips[clip_index]

        cls.clip_output_generator(
            clip,
            template=template,
            extend_start=extend_start,
            extend_end=extend_end
        )

    @classmethod
    def clip_output_generator(cls, clip, template="", extend_start=0, extend_end=0):
        """Generates render tasks for the clip with the given index

        :param clip: A Resolve TimelineItem
        :param str template: Output template,

          The Resolve template variables can be directly used like:

            %{2nd Asst}
            %{2nd Continuity}
            %{2nd Dir Asst}
            %{2nd Dir Reviewed}
            %{2nd Dir}
            %{2nd DIT}
            %{2nd DOP Reviewed}
            %{2nd DOP}
            %{3D Rig ID #}
            %{3D Rig Type}
            %{Angle}
            %{Asp Ratio Notes}
            %{Associated Mattes}
            %{Asst Director}
            %{Asst Producer}
            %{Audio Bit Depth}
            %{Audio Channels}
            %{Audio Dur TC}
            %{Audio End TC}
            %{Audio File Type}
            %{Audio FPS}
            %{Audio Media}
            %{Audio Notes}
            %{Audio Offset}
            %{Audio Recorder}
            %{Audio Sample Rate}
            %{Audio Start TC}
            %{Audio TC Type}
            %{Aux 1}
            %{Aux 2}
            %{BG}
            %{Bit Depth}
            %{Bit Rate}
            %{Cam #}
            %{Cam Aperture}
            %{Cam Asst}
            %{Cam Firmware}
            %{Cam Format}
            %{Cam FPS}
            %{Cam ID}
            %{Cam Notes}
            %{Cam Operator}
            %{Cam Serial #}
            %{Cam TC Type}
            %{Cam Type}
            %{Camera Aperture Type}
            %{Camera Manufacturer}
            %{CDL SAT}
            %{CDL SOP}
            %{Clip #}
            %{Clip Directory}
            %{Clip Name}
            %{Clip Type}
            %{Codec Bitrate}
            %{Collaborative Update}
            %{Color Chart}
            %{Color Space Notes}
            %{Colorist Asst}
            %{Colorist Notes}
            %{Colorist Reviewed}
            %{Colorist}
            %{Comments}
            %{Continuity Reviewed}
            %{Continuity}
            %{Convergence Adj}
            %{Crew Comments}
            %{CV}
            %{Dailies Colorist}
            %{Data Level}
            %{Data Wrangler}
            %{Date Modified}
            %{Date Recorded}
            %{Day / Night}
            %{Deck Firmware}
            %{Deck Serial #}
            %{Description}
            %{Dialog Duration}
            %{Dialog Notes}
            %{Dialog Starts As}
            %{Different Frame Rate}
            %{Digital Tech}
            %{Director Reviewed}
            %{Director}
            %{Distance}
            %{DOP Reviewed}
            %{DOP}
            %{Drop Frame}
            %{Duration TC}
            %{Edit Sizing}
            %{Editing Asst}
            %{Editor}
            %{EDL Clip Name}
            %{EDL Event Number}
            %{EDL Tape Number}
            %{Embedded Audio}
            %{End Dialog TC}
            %{End Frame}
            %{End TC}
            %{Environment}
            %{Episode #}
            %{Episode Name}
            %{Eye}
            %{FG}
            %{File Name}
            %{File Path}
            %{Filter}
            %{Focal Point (mm)}
            %{Focus Puller}
            %{Focus Reviewed}
            %{Format}
            %{Frame Rate}
            %{Frames}
            %{Framing Chart}
            %{FSD}
            %{Fusion Composition}
            %{Gamma Notes}
            %{Genre}
            %{Good Take}
            %{Graded}
            %{Grey Chart}
            %{Group}
            %{H-Flip}
            %{Has Keyframes}
            %{IA}
            %{IDT}
            %{Input Color Space}
            %{Input LUT}
            %{Input Sizing Preset}
            %{Input Sizing}
            %{In}
            %{ISO}
            %{Key Grip}
            %{KeyKode}
            %{Keywords}
            %{Lab Roll #}
            %{Lens #}
            %{Lens Chart}
            %{Lens Notes}
            %{Lens Type}
            %{Line Producer}
            %{Location}
            %{LUT 1}
            %{LUT 2}
            %{LUT 3}
            %{LUT Used On Set}
            %{LUT Used}
            %{Marker Keywords}
            %{Marker Name}
            %{Marker Notes}
            %{Matte Nodes}
            %{Media Type}
            %{Modified}
            %{Mon Color Space}
            %{Monitor LUT}
            %{Move}
            %{ND Filter}
            %{Noise Reduction}
            %{Out}
            %{PAR Notes}
            %{PAR}
            %{People}
            %{Post Producer}
            %{Producer}
            %{Production Asst}
            %{Production Co}
            %{Production Name}
            %{Program Name}
            %{Project Name}
            %{RAW}
            %{Reel Name}
            %{Reel Number}
            %{Render Codec}
            %{Render Resolution}
            %{Resolution}
            %{Reviewers Notes}
            %{Rig Inverted}
            %{Roll Card #}
            %{S3D Eye}
            %{S3D Notes}
            %{S3D Shot}
            %{S3D Sync}
            %{Safe Area}
            %{Sample Rate (KHz)}
            %{Scene}
            %{Script Suprvisr}
            %{Send to Studio}
            %{Send to}
            %{Sensor Area Captured}
            %{Sensor}
            %{Series #}
            %{Setup}
            %{Shared Nodes}
            %{Shoot Day}
            %{Shot During Ep}
            %{Shot Type}
            %{Shot}
            %{Shutter Type}
            %{Shutter}
            %{Slate TC}
            %{Sound Mixer}
            %{Sound Reviewed}
            %{Sound Roll #}
            %{Source Name}
            %{Start Dialog TC}
            %{Start Frame}
            %{Start TC}
            %{Subclip}
            %{Take}
            %{Time-lapse Interval}
            %{Timeline Index}
            %{Timeline Name}
            %{Tone}
            %{Track 1}
            %{Track 2}
            %{Track 3}
            %{Track 4}
            %{Track 5}
            %{Track 6}
            %{Track 7}
            %{Track 8}
            %{Track 9}
            %{Track 10}
            %{Track 11}
            %{Track 12}
            %{Track 13}
            %{Track 14}
            %{Track 15}
            %{Track 16}
            %{Track 17}
            %{Track 18}
            %{Track 19}
            %{Track 20}
            %{Track Name}
            %{Track Number}
            %{Tracked}
            %{Unit Manager}
            %{Unit Name}
            %{Unrendered}
            %{Usage}
            %{V-Flip}
            %{Version}
            %{VFX Grey Ball}
            %{VFX Markers}
            %{VFX Mirror Ball}
            %{VFX Notes}
            %{VFX Shot #}
            %{VFX Svsr Reviewed}
            %{Video Codec}
            %{Wardrobe Reviewed}
            %{White Balance Tint}
            %{White Point}

          These will be passed to Resolve directly.

        :param extend_start: Include this many frames at the start of the clip. Default is 0.
        :param extend_end: Include this many frames at the end of the clip. Default is 0.

        """

        if template == "":
            import copy
            template = copy.copy(cls.default_output_template)

        resolve_keywords = {
            'Angle': '%{Angle}',
            'Asp Ratio Notes': '%{Asp Ratio Notes}',
            'Associated Mattes': '%{Associated Mattes}',
            'Asst Director': '%{Asst Director}',
            'Asst Producer': '%{Asst Producer}',
            'Audio Bit Depth': '%{Audio Bit Depth}',
            'Audio Channels': '%{Audio Channels}',
            'Audio Dur TC': '%{Audio Dur TC}',
            'Audio End TC': '%{Audio End TC}',
            'Audio File Type': '%{Audio File Type}',
            'Audio FPS': '%{Audio FPS}',
            'Audio Media': '%{Audio Media}',
            'Audio Notes': '%{Audio Notes}',
            'Audio Offset': '%{Audio Offset}',
            'Audio Recorder': '%{Audio Recorder}',
            'Audio Sample Rate': '%{Audio Sample Rate}',
            'Audio Start TC': '%{Audio Start TC}',
            'Audio TC Type': '%{Audio TC Type}',
            'Aux 1': '%{Aux 1}',
            'Aux 2': '%{Aux 2}',
            'BG': '%{BG}',
            'Bit Depth': '%{Bit Depth}',
            'Bit Rate': '%{Bit Rate}',
            'Cam #': '%{Cam #}',
            'Cam Aperture': '%{Cam Aperture}',
            'Cam Asst': '%{Cam Asst}',
            'Cam Firmware': '%{Cam Firmware}',
            'Cam Format': '%{Cam Format}',
            'Cam FPS': '%{Cam FPS}',
            'Cam ID': '%{Cam ID}',
            'Cam Notes': '%{Cam Notes}',
            'Cam Operator': '%{Cam Operator}',
            'Cam Serial #': '%{Cam Serial #}',
            'Cam TC Type': '%{Cam TC Type}',
            'Cam Type': '%{Cam Type}',
            'Camera Aperture Type': '%{Camera Aperture Type}',
            'Camera Manufacturer': '%{Camera Manufacturer}',
            'CDL SAT': '%{CDL SAT}',
            'CDL SOP': '%{CDL SOP}',
            'Clip #': '%{Clip #}',
            'Clip Directory': '%{Clip Directory}',
            'Clip Name': '%{Clip Name}',
            'Clip Type': '%{Clip Type}',
            'Codec Bitrate': '%{Codec Bitrate}',
            'Collaborative Update': '%{Collaborative Update}',
            'Color Chart': '%{Color Chart}',
            'Color Space Notes': '%{Color Space Notes}',
            'Colorist Asst': '%{Colorist Asst}',
            'Colorist Notes': '%{Colorist Notes}',
            'Colorist Reviewed': '%{Colorist Reviewed}',
            'Colorist': '%{Colorist}',
            'Comments': '%{Comments}',
            'Continuity Reviewed': '%{Continuity Reviewed}',
            'Continuity': '%{Continuity}',
            'Convergence Adj': '%{Convergence Adj}',
            'Crew Comments': '%{Crew Comments}',
            'CV': '%{CV}',
            'Dailies Colorist': '%{Dailies Colorist}',
            'Data Level': '%{Data Level}',
            'Data Wrangler': '%{Data Wrangler}',
            'Date Modified': '%{Date Modified}',
            'Date Recorded': '%{Date Recorded}',
            'Day / Night': '%{Day / Night}',
            'Deck Firmware': '%{Deck Firmware}',
            'Deck Serial #': '%{Deck Serial #}',
            'Description': '%{Description}',
            'Dialog Duration': '%{Dialog Duration}',
            'Dialog Notes': '%{Dialog Notes}',
            'Dialog Starts As': '%{Dialog Starts As}',
            'Different Frame Rate': '%{Different Frame Rate}',
            'Digital Tech': '%{Digital Tech}',
            'Director Reviewed': '%{Director Reviewed}',
            'Director': '%{Director}',
            'Distance': '%{Distance}',
            'DOP Reviewed': '%{DOP Reviewed}',
            'DOP': '%{DOP}',
            'Drop Frame': '%{Drop Frame}',
            'Duration TC': '%{Duration TC}',
            'Edit Sizing': '%{Edit Sizing}',
            'Editing Asst': '%{Editing Asst}',
            'Editor': '%{Editor}',
            'EDL Clip Name': '%{EDL Clip Name}',
            'EDL Event Number': '%{EDL Event Number}',
            'EDL Tape Number': '%{EDL Tape Number}',
            'Embedded Audio': '%{Embedded Audio}',
            'End Dialog TC': '%{End Dialog TC}',
            'End Frame': '%{End Frame}',
            'End TC': '%{End TC}',
            'Environment': '%{Environment}',
            'Episode #': '%{Episode #}',
            'Episode Name': '%{Episode Name}',
            'Eye': '%{Eye}',
            'FG': '%{FG}',
            'File Name': '%{File Name}',
            'File Path': '%{File Path}',
            'Filter': '%{Filter}',
            'Focal Point (mm)': '%{Focal Point (mm)}',
            'Focus Puller': '%{Focus Puller}',
            'Focus Reviewed': '%{Focus Reviewed}',
            'Format': '%{Format}',
            'Frame Rate': '%{Frame Rate}',
            'Frames': '%{Frames}',
            'Framing Chart': '%{Framing Chart}',
            'FSD': '%{FSD}',
            'Fusion Composition': '%{Fusion Composition}',
            'Gamma Notes': '%{Gamma Notes}',
            'Genre': '%{Genre}',
            'Good Take': '%{Good Take}',
            'Graded': '%{Graded}',
            'Grey Chart': '%{Grey Chart}',
            'Group': '%{Group}',
            'H-Flip': '%{H-Flip}',
            'Has Keyframes': '%{Has Keyframes}',
            'IA': '%{IA}',
            'IDT': '%{IDT}',
            'Input Color Space': '%{Input Color Space}',
            'Input LUT': '%{Input LUT}',
            'Input Sizing Preset': '%{Input Sizing Preset}',
            'Input Sizing': '%{Input Sizing}',
            'In': '%{In}',
            'ISO': '%{ISO}',
            'Key Grip': '%{Key Grip}',
            'KeyKode': '%{KeyKode}',
            'Keywords': '%{Keywords}',
            'Lab Roll #': '%{Lab Roll #}',
            'Lens #': '%{Lens #}',
            'Lens Chart': '%{Lens Chart}',
            'Lens Notes': '%{Lens Notes}',
            'Lens Type': '%{Lens Type}',
            'Line Producer': '%{Line Producer}',
            'Location': '%{Location}',
            'LUT 1': '%{LUT 1}',
            'LUT 2': '%{LUT 2}',
            'LUT 3': '%{LUT 3}',
            'LUT Used On Set': '%{LUT Used On Set}',
            'LUT Used': '%{LUT Used}',
            'Marker Keywords': '%{Marker Keywords}',
            'Marker Name': '%{Marker Name}',
            'Marker Notes': '%{Marker Notes}',
            'Matte Nodes': '%{Matte Nodes}',
            'Media Type': '%{Media Type}',
            'Modified': '%{Modified}',
            'Mon Color Space': '%{Mon Color Space}',
            'Monitor LUT': '%{Monitor LUT}',
            'Move': '%{Move}',
            'ND Filter': '%{ND Filter}',
            'Noise Reduction': '%{Noise Reduction}',
            'Out': '%{Out}',
            'PAR Notes': '%{PAR Notes}',
            'PAR': '%{PAR}',
            'People': '%{People}',
            'Post Producer': '%{Post Producer}',
            'Producer': '%{Producer}',
            'Production Asst': '%{Production Asst}',
            'Production Co': '%{Production Co}',
            'Production Name': '%{Production Name}',
            'Program Name': '%{Program Name}',
            'Project Name': '%{Project Name}',
            'RAW': '%{RAW}',
            'Reel Name': '%{Reel Name}',
            'Reel Number': '%{Reel Number}',
            'Render Codec': '%{Render Codec}',
            'Render Resolution': '%{Render Resolution}',
            'Resolution': '%{Resolution}',
            'Reviewers Notes': '%{Reviewers Notes}',
            'Rig Inverted': '%{Rig Inverted}',
            'Roll Card #': '%{Roll Card #}',
            'S3D Eye': '%{S3D Eye}',
            'S3D Notes': '%{S3D Notes}',
            'S3D Shot': '%{S3D Shot}',
            'S3D Sync': '%{S3D Sync}',
            'Safe Area': '%{Safe Area}',
            'Sample Rate (KHz)': '%{Sample Rate (KHz)}',
            'Scene': '%{Scene}',
            'Script Suprvisr': '%{Script Suprvisr}',
            'Send to Studio': '%{Send to Studio}',
            'Send to': '%{Send to}',
            'Sensor Area Captured': '%{Sensor Area Captured}',
            'Sensor': '%{Sensor}',
            'Series #': '%{Series #}',
            'Setup': '%{Setup}',
            'Shared Nodes': '%{Shared Nodes}',
            'Shoot Day': '%{Shoot Day}',
            'Shot During Ep': '%{Shot During Ep}',
            'Shot Type': '%{Shot Type}',
            'Shot': '%{Shot}',
            'Shutter Type': '%{Shutter Type}',
            'Shutter': '%{Shutter}',
            'Slate TC': '%{Slate TC}',
            'Sound Mixer': '%{Sound Mixer}',
            'Sound Reviewed': '%{Sound Reviewed}',
            'Sound Roll #': '%{Sound Roll #}',
            'Source Name': '%{Source Name}',
            'Start Dialog TC': '%{Start Dialog TC}',
            'Start Frame': '%{Start Frame}',
            'Start TC': '%{Start TC}',
            'Subclip': '%{Subclip}',
            'Take': '%{Take}',
            'Time-lapse Interval': '%{Time-lapse Interval}',
            'Timeline Index': '%{Timeline Index}',
            'Timeline Name': '%{Timeline Name}',
            'Tone': '%{Tone}',
            'Track 1': '%{Track 1}',
            'Track 2': '%{Track 2}',
            'Track 3': '%{Track 3}',
            'Track 4': '%{Track 4}',
            'Track 5': '%{Track 5}',
            'Track 6': '%{Track 6}',
            'Track 7': '%{Track 7}',
            'Track 8': '%{Track 8}',
            'Track 9': '%{Track 9}',
            'Track 10': '%{Track 10}',
            'Track 11': '%{Track 11}',
            'Track 12': '%{Track 12}',
            'Track 13': '%{Track 13}',
            'Track 14': '%{Track 14}',
            'Track 15': '%{Track 15}',
            'Track 16': '%{Track 16}',
            'Track 17': '%{Track 17}',
            'Track 18': '%{Track 18}',
            'Track 19': '%{Track 19}',
            'Track 20': '%{Track 20}',
            'Track Name': '%{Track Name}',
            'Track Number': '%{Track Number}',
            'Tracked': '%{Tracked}',
            'Unit Manager': '%{Unit Manager}',
            'Unit Name': '%{Unit Name}',
            'Unrendered': '%{Unrendered}',
            'Usage': '%{Usage}',
            'V-Flip': '%{V-Flip}',
            'Version': '%{Version}',
            'VFX Grey Ball': '%{VFX Grey Ball}',
            'VFX Markers': '%{VFX Markers}',
            'VFX Mirror Ball': '%{VFX Mirror Ball}',
            'VFX Notes': '%{VFX Notes}',
            'VFX Shot #': '%{VFX Shot #}',
            'VFX Svsr Reviewed': '%{VFX Svsr Reviewed}',
            'Video Codec': '%{Video Codec}',
            'Wardrobe Reviewed': '%{Wardrobe Reviewed}',
            'White Balance Tint': '%{White Balance Tint}',
            'White Point': '%{White Point}',
        }

        from anima.env import blackmagic
        resolve = blackmagic.get_resolve()

        pm = resolve.GetProjectManager()
        proj = pm.GetCurrentProject()
        timeline = proj.GetCurrentTimeline()
        clips = timeline.GetItemsInTrack("video", 1)

        clip_index = -1
        for i in range(len(clips)):
            if clips[i + 1] == clip:
                clip_index = i + 1

        resolve_keywords.update({
            'clip_number': clip_index,
        })

        # create a new render output for each clip
        proj.SetRenderSettings({
            'MarkIn': clip.GetStart() - extend_start,
            'MarkOut': clip.GetEnd() - 1 + extend_end,
            'CustomName': template
        })

        proj.AddRenderJob()
