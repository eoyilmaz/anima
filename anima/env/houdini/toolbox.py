# -*- coding: utf-8 -*-
# Copyright (c) 2018-2019, Erkan Ozgur Yilmaz
#
# This module is part of anima and is released under the MIT
# License: http://www.opensource.org/licenses/MIT
"""
Use the following code in the Python Panel


def onCreateInterface():
    from anima.ui import SET_PYSIDE2
    SET_PYSIDE2()
    from anima.env.houdini import toolbox
    return toolbox.ui()
"""

from anima.ui.lib import QtCore, QtWidgets


def ui():
    """returns the widget to Houdini
    """
    root_widget = QtWidgets.QWidget()
    tlb = ToolboxLayout()
    root_widget.setLayout(tlb)
    return root_widget


class ToolboxLayout(QtWidgets.QVBoxLayout):
    """The toolbox
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

        # -------------------------------------------------------------------
        # Version Creator

        from anima.ui.utils import add_button
        add_button(
            'Version Creator',
            general_tab_vertical_layout,
            GenericTools.version_creator
        )

        add_button(
            'Browse $HIP',
            general_tab_vertical_layout,
            GenericTools.browse_hip
        )

        # Copy Path
        add_button(
            'Copy Node Path',
            general_tab_vertical_layout,
            GenericTools.copy_node_path
        )

        # Range from shot
        add_button(
            'Range From Shot',
            general_tab_vertical_layout,
            GenericTools.range_from_shot
        )

        # Update render settings
        add_button(
            'Update Render Settings',
            general_tab_vertical_layout,
            GenericTools.update_render_settings
        )

        # Export RSProxy Data As JSON
        add_button(
            'Export RSProxy Data As JSON',
            general_tab_vertical_layout,
            GenericTools.export_rsproxy_data_as_json
        )

        # -------------------------------------------------------------------
        # Add the stretcher
        general_tab_vertical_layout.addStretch()


class GenericTools(object):
    """Generic Tools
    """

    @classmethod
    def version_creator(cls):
        """version creator
        """
        from anima.ui.scripts import houdini
        houdini.version_creator()

    @classmethod
    def browse_hip(cls):
        """browse HIP folder
        """
        from anima.utils import open_browser_in_location
        import os
        hip = os.environ.get('HIP')
        if hip:
            open_browser_in_location(hip)

    @classmethod
    def copy_node_path(cls):
        """copies path to clipboard
        """
        import hou
        node = hou.selectedNodes()[0]
        hou.ui.copyTextToClipboard(node.path())

    @classmethod
    def range_from_shot(cls):
        """sets the playback range from the related shot item
        """
        from anima.env import houdini
        h = houdini.Houdini()
        v = h.get_current_version()
        if not v:
            print('no v, returning!')
            return

        from stalker import Shot
        if not v.task.parent or not isinstance(v.task.parent, Shot):
            return

        shot = v.task.parent
        h.set_frame_range(shot.cut_in, shot.cut_out)

    @classmethod
    def update_render_settings(cls):
        """updates the render settings (ex: fixes output path and AOV paths
        etc.)
        """
        from anima.env import houdini
        h = houdini.Houdini()
        v = h.get_current_version()
        if not v:
            print('no v, returning!')
            return

        h.set_render_filename(version=v)

    @classmethod
    def export_rsproxy_data_as_json(cls, geo=None, path=''):
        """exports RSProxy Data on points as json
        """
        import hou
        if geo is None:
            node = hou.selectedNodes()[0]
            geo = node.geometry()

        # Add code to modify contents of geo.
        # Use drop down menu to select examples.
        pos = geo.pointFloatAttribValues("P")
        rot = geo.pointFloatAttribValues("rot")
        sca = geo.pointFloatAttribValues("pscale")
        instance_file = geo.pointStringAttribValues("instancefile")
        node_name = geo.pointStringAttribValues("node_name")
        parent_name = geo.pointStringAttribValues("parent_name")

        import os
        import tempfile
        if path == '':
            path = os.path.normpath(
                os.path.join(
                    tempfile.gettempdir(),
                    '..',
                    'rsproxy_info.json'
                )
            )

        pos_data = []
        rot_data = []
        for i in range(len(pos) / 3):
            pos_data.append((pos[i * 3], pos[i * 3 + 1], pos[i * 3 + 2]))
            rot_data.append((rot[i * 3], rot[i * 3 + 1], rot[i * 3 + 2]))

        json_data = {
            "pos": pos_data,
            "rot": rot_data,
            "sca": sca,
            "instance_file": instance_file,
            "node_name": node_name,
            "parent_name": parent_name
        }

        import json
        with open(path, "w") as f:
            f.write(json.dumps(json_data))
