# -*- coding: utf-8 -*-
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

        # *********************************************************************
        #
        # GENERAL TAB
        #
        # *********************************************************************
        # add the General Tab
        general_tab_widget = QtWidgets.QWidget(self.widget())
        general_tab_vertical_layout = QtWidgets.QVBoxLayout()
        general_tab_widget.setLayout(general_tab_vertical_layout)

        main_tab_widget.addTab(general_tab_widget, 'Generic')

        # Create tools for general tab

        # -------------------------------------------------------------------
        # Version Dialog

        from anima.ui.utils import add_button
        add_button(
            'Open Version',
            general_tab_vertical_layout,
            GeneralTools.version_dialog,
            callback_kwargs={"mode": 1}
        )

        add_button(
            'Save As Version',
            general_tab_vertical_layout,
            GeneralTools.version_dialog,
            callback_kwargs={"mode": 0}
        )

        # Browse $HIP
        add_button(
            'Browse $HIP',
            general_tab_vertical_layout,
            GeneralTools.browse_hip
        )

        # Copy Path
        add_button(
            'Copy Node Path',
            general_tab_vertical_layout,
            GeneralTools.copy_node_path
        )

        # Range from shot
        add_button(
            'Range From Shot',
            general_tab_vertical_layout,
            GeneralTools.range_from_shot
        )

        # Update render settings
        add_button(
            'Update Render Settings',
            general_tab_vertical_layout,
            GeneralTools.update_render_settings
        )

        def export_rsproxy_data_as_json_callback():
            """
            """
            import hou
            try:
                GeneralTools.export_rsproxy_data_as_json()
            except (BaseException, hou.OperationFailed) as e:
                QtWidgets.QMessageBox.critical(
                    main_tab_widget,
                    "Export",
                    "Error!<br><br>%s" % e
                )
            else:
                QtWidgets.QMessageBox.information(
                    main_tab_widget,
                    "Export",
                    "Data has been exported correctly!"
                )

        # Export RSProxy Data As JSON
        add_button(
            'Export RSProxy Data As JSON',
            general_tab_vertical_layout,
            export_rsproxy_data_as_json_callback
        )

        # Batch Rename
        batch_rename_layout = QtWidgets.QHBoxLayout()
        general_tab_vertical_layout.addLayout(batch_rename_layout)

        search_field = QtWidgets.QLineEdit()
        search_field.setPlaceholderText("Search")
        replace_field = QtWidgets.QLineEdit()
        replace_field.setPlaceholderText("Replace")
        replace_in_child_nodes_check_box = QtWidgets.QCheckBox()
        replace_in_child_nodes_check_box.setToolTip("Replace In Child Nodes")
        replace_in_child_nodes_check_box.setChecked(False)

        batch_rename_layout.addWidget(search_field)
        batch_rename_layout.addWidget(replace_field)
        batch_rename_layout.addWidget(replace_in_child_nodes_check_box)

        def search_and_replace_callback():
            search_str = search_field.text()
            replace_str = replace_field.text()
            GeneralTools.rename_selected_nodes(
                search_str,
                replace_str,
                replace_in_child_nodes_check_box.isChecked()
            )

        add_button(
            "Search && Replace",
            batch_rename_layout,
            search_and_replace_callback
        )

        # Import Shaders From Maya
        add_button(
            'Import Shaders From Maya',
            general_tab_vertical_layout,
            GeneralTools.import_shaders_from_maya
        )

        # Create Focus Plane
        add_button(
            'Creat Focus Plane',
            general_tab_vertical_layout,
            GeneralTools.create_focus_plane
        )

        # Create Focus Plane
        from anima.env.houdini import auxiliary
        add_button(
            'Create A Very Nice Camera Rig',
            general_tab_vertical_layout,
            auxiliary.very_nice_camera_rig
        )

        # -------------------------------------------------------------------
        # Add the stretcher
        general_tab_vertical_layout.addStretch()

        # *********************************************************************
        #
        # CROWD TAB
        #
        # *********************************************************************

        # add the Crowd Tab
        crowd_tab_widget = QtWidgets.QWidget(self.widget())
        crowd_tab_vertical_layout = QtWidgets.QVBoxLayout()
        crowd_tab_widget.setLayout(crowd_tab_vertical_layout)

        main_tab_widget.addTab(crowd_tab_widget, 'Crowd')

        # crowd_tools_label = QtWidgets.QLabel("Crowd Tools")
        # crowd_tab_vertical_layout.addWidget(crowd_tools_label)

        from anima.env.houdini import crowd_tools
        # Bake Setup
        add_button(
            'Create Bake Setup',
            crowd_tab_vertical_layout,
            crowd_tools.create_bake_setup
        )
        # Bake Setup
        add_button(
            'Create Render Setup',
            crowd_tab_vertical_layout,
            crowd_tools.create_render_setup
        )

        # -------------------------------------------------------------------
        # Add the stretcher
        crowd_tab_vertical_layout.addStretch()


class GeneralTools(object):
    """General Tools
    """

    @classmethod
    def version_dialog(cls, mode=2):
        """version dialog
        """
        from anima.ui.scripts import houdini
        houdini.version_dialog(mode=mode)

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

    @classmethod
    def rename_selected_nodes(cls, search_str, replace_str, replace_in_child_nodes=False):
        """Batch renames selected nodes

        :param str search_str: Search for this
        :param str replace_str: And replace with this
        :return:
        """
        import hou
        selection = hou.selectedNodes()
        for node in selection:
            name = node.name()
            node.setName(name.replace(search_str, replace_str))
            if replace_in_child_nodes:
                for child_node in node.children():
                    name = child_node.name()
                    child_node.setName(name.replace(search_str, replace_str))

    @classmethod
    def import_shaders_from_maya(cls):
        """Imports shader assignment info from Maya.

        Use the Maya counterpart to export the assignment data
        """
        import os
        import tempfile
        shader_data_temp_file_path = os.path.join(
            tempfile.gettempdir(),
            'shader_data'
        )

        import hou
        selected_nodes = hou.selectedNodes()
        if not selected_nodes:
            raise RuntimeError("Please select a node!")

        base_node = selected_nodes[0]

        # read the json data
        import json
        with open(shader_data_temp_file_path, "r") as f:
            shader_assignment_data = json.load(f)

        current_context = base_node.parent()
        # create Material SOP node
        material_sop_node = current_context.createNode(
            "material"
        )

        # create material slots
        material_sop_node\
            .parm("num_materials")\
            .set(len(shader_assignment_data))

        # connect the material to the selected node
        material_sop_node.setInput(0, base_node)

        material_context = hou.node('/mat')
        for i, shader_name in enumerate(shader_assignment_data):
            # create a new material for each shader name
            # Use RSMaterial for now

            # first check if the shader exists
            shader = hou.node("/mat/%s" % shader_name)

            if not shader:
                # create an RSMaterial
                shader = material_context.createNode(
                    "redshift::Material",
                    shader_name,
                )

            # create entries in the Material SOP
            # set group field
            material_sop_node.parm("group%s" % (i + 1)).set(
                " ".join(
                    map(
                        lambda x: "@path=%s" % x,
                        shader_assignment_data[shader_name]
                    )
                )
            )

            # set material field
            material_sop_node.parm("shop_materialpath%s" % (i + 1)).set(
                shader.path()
            )

    @classmethod
    def create_focus_plane(cls):
        """Creates a focus plane tool for the selected camera
        """
        import hou
        selected = hou.selectedNodes()
        if not selected:
            return

        camera = selected[0]

        # create a grid
        parent_context = camera.parent()
        focus_plane_node = parent_context.createNode("geo", "focus_plane1")
        grid_node = focus_plane_node.createNode("grid")

        # Set orient to XZ Plane
        grid_node.parm("orient").set(0)

        # set color and alpha
        attr_wrangle = focus_plane_node.createNode("attribwrangle", "set_color_and_alpha")
        attr_wrangle.setInput(0, grid_node)
        attr_wrangle.parm("snippet").set("v@Cd = {1, 0, 0};\nv@Alpha = {0.5, 0.5, 0.5};")

        # Create Display node
        display_null = focus_plane_node.createNode("null", "DISPLAY")
        display_null.setDisplayFlag(1)
        display_null.setInput(0, attr_wrangle)

        # Make it not renderable
        render_null = focus_plane_node.createNode("null", "RENDER")
        render_null.setRenderFlag(1)

        # connect the tz parameter of the grid node to the cameras focus distance
        focus_plane_node.setInput(0, camera)
        focus_plane_node.parm("tz").set(-1)
        camera.parm("focus").setExpression('-ch("../%s/tz")' % focus_plane_node.name())

        # align the nodes
        from anima.env.houdini import auxiliary
        network_editor = auxiliary.get_network_pane()
        import nodegraphalign  # this is a houdini module
        nodegraphalign.alignConnected(
            network_editor, grid_node, None, "down"
        )
        nodegraphalign.alignConnected(
            network_editor, camera, None, "down"
        )

    @classmethod
    def archive_current_scene(cls):
        """archives the current scene
        """
        from anima.env import houdini
        from anima.env.houdini.archive import Archiver
        from anima.utils.archive import archive_current_scene
        h_env = houdini.Houdini()
        version = h_env.get_current_version()
        archiver = Archiver()

        archive_current_scene(version, archiver)
