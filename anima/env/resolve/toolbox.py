# -*- coding: utf-8 -*-
# Copyright (c) 2018-2019, Erkan Ozgur Yilmaz
#
# This module is part of anima and is released under the MIT
# License: http://www.opensource.org/licenses/MIT
"""
Test code

from anima.env.resolve import toolbox
reload(toolbox)
dialog = toolbox.UI()

"""

from anima.ui.base import AnimaDialogBase, ui_caller
from anima.ui.lib import QtCore, QtWidgets


# def ui():
#     """returns the widget to Houdini
#     """
#     root_widget = QtWidgets.QWidget()
#     tlb = ToolboxLayout()
#     root_widget.setLayout(tlb)
#     return root_widget

def UI(app_in=None, executor=None, **kwargs):
    """
    :param environment: The
      :class:`~stalker.models.env.EnvironmentBase` can be None to let the UI to
      work in "environmentless" mode in which it only creates data in database
      and copies the resultant version file path to clipboard.

    :param mode: Runs the UI either in Read-Write (0) mode or in Read-Only (1)
      mode.

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
        pass


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
        # Per Clip Output Generator
        add_button(
            'Per Clip Output Generator',
            general_tab_vertical_layout,
            GenericTools.per_clip_output_generator
        )

        # Clip Output Generator
        # create a new layout
        layout = QtWidgets.QHBoxLayout()
        general_tab_vertical_layout.addLayout(layout)

        clip_index_spinbox = QtWidgets.QSpinBox()
        clip_index_spinbox.setMinimum(1)

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
        layout.addWidget(clip_index_spinbox)
        layout.addWidget(version_spinbox)

        # -------------------------------------------------------------------
        # Add the stretcher
        general_tab_vertical_layout.addStretch()


class GenericTools(object):
    """Generic Tools
    """

    @classmethod
    def per_clip_output_generator(cls, version_number=1):
        """generates render tasks per clips on the current timeline
        """
        from anima.env import blackmagic
        resolve = blackmagic.get_resolve()

        pm = resolve.GetProjectManager()
        proj = pm.GetCurrentProject()
        timeline = proj.GetCurrentTimeline()

        clips = timeline.GetItemsInTrack("video", 1)

        for clip_index in clips:
            GenericTools.clip_output_generator(clip_index, version_number)

    @classmethod
    def clip_output_generator(cls, clip_index, version_number=1):
        """generates render tasks for the clip with the given index
        """
        from anima.env import blackmagic
        resolve = blackmagic.get_resolve()

        pm = resolve.GetProjectManager()
        proj = pm.GetCurrentProject()
        timeline = proj.GetCurrentTimeline()

        # media_pool = proj.GetMediaPool()

        clips = timeline.GetItemsInTrack("video", 1)
        clip = clips[clip_index]

        # create a new render output for each clip
        proj.SetRenderSettings({
            'MarkIn': clip.GetStart(),
            'MarkOut': clip.GetEnd()-1,
            'CustomName': "%s_CL%04i_v%03i" % (
                # timeline.GetName(),
                "%{Timeline Name}",
                int(clip_index),
                version_number
            )
        })

        proj.AddRenderJob()
