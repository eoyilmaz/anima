# -*- coding: utf-8 -*-
"""
Test code

from anima.env.resolve import toolbox
reload(toolbox)
dialog = toolbox.UI()

"""
import os


from anima.ui.base import ui_caller
from anima.ui.lib import QtGui, QtWidgets


__here__ = os.path.abspath(__file__)


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
        tlb = ToolboxLayout()
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

        # add the General Tab
        general_tab_widget = QtWidgets.QWidget(self.widget())
        general_tab_vertical_layout = QtWidgets.QVBoxLayout()
        general_tab_widget.setLayout(general_tab_vertical_layout)

        main_tab_widget.addTab(general_tab_widget, 'Generic')

        # Create tools for general tab
        from anima.ui.utils import add_button
        # -------------------------------------------------------------------
        # Template
        template_line_edit = QtWidgets.QLineEdit()
        # template_line_edit.setPlaceHolder("Template")
        template_line_edit.setText(GenericTools.default_output_template)

        general_tab_vertical_layout.addWidget(template_line_edit)

        # -------------------------------------------------------------------
        # Per Clip Output Generator
        # create a new layout
        layout = QtWidgets.QHBoxLayout()
        general_tab_vertical_layout.addLayout(layout)

        per_clip_version_label = QtWidgets.QLabel()
        per_clip_version_label.setText("Version")
        per_clip_version_spinbox = QtWidgets.QSpinBox()
        per_clip_version_spinbox.setMinimum(1)

        def per_clip_output_generator_wrapper():
            version_number = per_clip_version_spinbox.value()
            template = template_line_edit.text()
            GenericTools.per_clip_output_generator(version_number=version_number, template=template)

        add_button(
            'Per Clip Output Generator',
            layout,
            per_clip_output_generator_wrapper
        )

        layout.addWidget(per_clip_version_label)
        layout.addWidget(per_clip_version_spinbox)

        # Clip Output Generator
        # create a new layout
        layout = QtWidgets.QHBoxLayout()
        general_tab_vertical_layout.addLayout(layout)

        clip_index_label = QtWidgets.QLabel()
        clip_index_label.setText("Clip Index")
        clip_index_spinbox = QtWidgets.QSpinBox()
        clip_index_spinbox.setMinimum(1)

        version_label = QtWidgets.QLabel()
        version_label.setText("Version")
        version_spinbox = QtWidgets.QSpinBox()
        version_spinbox.setMinimum(1)

        def clip_output_generator_wrapper():
            clip_index = clip_index_spinbox.value()
            version_number = version_spinbox.value()
            GenericTools.clip_output_generator(clip_index, version_number)

        add_button(
            'Clip Output Generator',
            layout,
            clip_output_generator_wrapper
        )
        layout.addWidget(clip_index_label)
        layout.addWidget(clip_index_spinbox)
        layout.addWidget(version_label)
        layout.addWidget(version_spinbox)

        add_button(
            "Get Shot Code",
            general_tab_vertical_layout,
            GenericTools.get_shot_code,
            GenericTools.get_shot_code.__doc__
        )

        # -------------------------------------------------------------------
        # Set Shot Code

        layout = QtWidgets.QHBoxLayout()
        general_tab_vertical_layout.addLayout(layout)

        set_clip_code_label = QtWidgets.QLabel()
        set_clip_code_label.setText("Code")
        set_clip_code_line_edit = QtWidgets.QLineEdit()

        def set_shot_code_wrapper():
            shot_code = set_clip_code_line_edit.text()
            GenericTools.set_shot_code(shot_code)

        layout.addWidget(set_clip_code_label)
        layout.addWidget(set_clip_code_line_edit)
        add_button(
            "Set Shot Code",
            layout,
            set_shot_code_wrapper,
            GenericTools.set_shot_code.__doc__,
        )

        add_button(
            "Plate Injector",
            general_tab_vertical_layout,
            GenericTools.plate_injector,
            GenericTools.plate_injector.__doc__
        )


        # -------------------------------------------------------------------
        # Add the stretcher
        general_tab_vertical_layout.addStretch()


class GenericTools(object):
    """Generic Tools
    """

    default_output_template = "%{Timeline Name}_CL%{Clip #}_v{version_number:03i}"

    @classmethod
    def per_clip_output_generator(cls, version_number=1, template=""):
        """generates render tasks per clips on the current timeline
        """
        from anima.env import blackmagic
        resolve = blackmagic.get_resolve()

        pm = resolve.GetProjectManager()
        proj = pm.GetCurrentProject()
        timeline = proj.GetCurrentTimeline()

        clips = timeline.GetItemsInTrack("video", 1)

        if template == "":
            template = cls.default_output_template

        for clip_index in clips:
            GenericTools.clip_output_generator(
                clip_index=clip_index,
                version_number=version_number,
                template=template
            )

    @classmethod
    def clip_output_generator(cls, clip_index=1, version_number=1, template=""):
        """generates render tasks for the clip with the given index

        :param int clip_index:
        :param int version_number:
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

        resolve_keywords.update({
            'clip_number': clip_index,
            'version_number': version_number
        })

        from anima.env import blackmagic
        resolve = blackmagic.get_resolve()

        pm = resolve.GetProjectManager()
        proj = pm.GetCurrentProject()
        timeline = proj.GetCurrentTimeline()

        clips = timeline.GetItemsInTrack("video", 1)
        clip = clips[clip_index]

        # create a new render output for each clip
        proj.SetRenderSettings({
            'MarkIn': clip.GetStart(),
            'MarkOut': clip.GetEnd()-1,
            'CustomName': template
        })

        proj.AddRenderJob()

    @classmethod
    def get_shot_code(cls):
        """returns the shot code of the current clip
        """
        from anima.env import blackmagic
        resolve = blackmagic.get_resolve()

        pm = resolve.GetProjectManager()
        proj = pm.GetCurrentProject()
        timeline = proj.GetCurrentTimeline()

        clip = timeline.GetCurrentVideoItem()

        from anima.env.resolve import shot_tools
        import importlib
        importlib.reload(shot_tools)

        clips = timeline.GetItemsInTrack("video", 1)
        plate_injector = shot_tools.PlateInjector()
        for clip in clips:
            plate_injector.clip = clip
            plate_injector.create_render_job()

    @classmethod
    def set_shot_code(cls, shot_code):
        """sets the shot code
        """
        from anima.env import blackmagic
        resolve = blackmagic.get_resolve()

        pm = resolve.GetProjectManager()
        proj = pm.GetCurrentProject()
        timeline = proj.GetCurrentTimeline()

        clip = timeline.GetCurrentVideoItem()

        from anima.env.resolve import shot_tools
        import importlib
        importlib.reload(shot_tools)
        plate_injector = shot_tools.PlateInjector()
        plate_injector.set_shot_code(clip, shot_code)

    @classmethod
    def plate_injector(cls):
        """calls the plate injector
        """
        from anima.env import blackmagic
        resolve = blackmagic.get_resolve()

        pm = resolve.GetProjectManager()
        proj = pm.GetCurrentProject()
        timeline = proj.GetCurrentTimeline()

        from anima.env.resolve import shot_tools
        import importlib
        importlib.reload(shot_tools)

        clips = timeline.GetItemsInTrack("video", 1)
        print('clips: %s' % clips)
        plate_injector = shot_tools.PlateInjector()

        from anima.utils import do_db_setup
        do_db_setup()

        from stalker import Project, Sequence
        project_name = ''  # TODO: This is for development
        project = Project.query.filter(Project.name==project_name).first()
        sequence = Sequence.query.filter(Sequence.project==project).first()

        # for clip in clips:
        plate_injector.project = project
        plate_injector.sequence = sequence
        for clip_id in clips:
            clip = clips[clip_id]
            plate_injector.clip = clip
            plate_injector.create_render_job()

        # plate_injector = shot_tools.PlateInjectorUI()
        # plate_injector.show()
