# -*- coding: utf-8 -*-

import os
from anima.ui.base import AnimaDialogBase
from anima.ui.lib import QtCore, QtGui, QtWidgets
from anima.ui.utils import create_button, create_separator

__here__ = os.path.abspath(__file__)


def UI(app_in=None, executor=None, **kwargs):
    """
    :param app_in: A Qt Application instance, which you can pass to let the UI
      be attached to the given applications event process.

    :param executor: Instead of calling app.exec_ the UI will call this given
      function. It also passes the created app instance to this executor.

    """
    from anima.ui.base import ui_caller

    return ui_caller(app_in, executor, ToolboxDialog, **kwargs)


class ToolboxDialog(QtWidgets.QDialog, AnimaDialogBase):
    """The toolbox dialog"""

    def __init__(self, environment=None, parent=None):
        super(ToolboxDialog, self).__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        self.setWindowModality(QtCore.Qt.ApplicationModal)
        self.setModal(True)
        self.resize(300, 300)
        size_policy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred
        )

        size_policy.setHorizontalStretch(1)
        size_policy.setVerticalStretch(1)
        size_policy.setHeightForWidth(self.sizePolicy().hasHeightForWidth())
        self.setSizePolicy(size_policy)
        self.setSizeGripEnabled(True)

        self.horizontal_layout = QtWidgets.QHBoxLayout(self)
        self.toolbox_widget = QtWidgets.QWidget(self)
        self.horizontal_layout.addWidget(self.toolbox_widget)

        self.toolbox_layout = ToolboxLayout(self.toolbox_widget)
        self.toolbox_layout.setSizeConstraint(QtWidgets.QLayout.SetMaximumSize)
        self.toolbox_layout.setContentsMargins(0, 0, 0, 0)

        # setup icon
        global __here__
        icon_path = os.path.abspath(
            os.path.join(__here__, "../../../ui/images/fusion9.png")
        )
        icon = QtGui.QIcon(icon_path)

        self.setWindowIcon(icon)


class ToolboxLayout(QtWidgets.QVBoxLayout):
    """The toolbox"""

    def __init__(self, *args, **kwargs):
        super(ToolboxLayout, self).__init__(*args, **kwargs)
        self._setup_ui()

    def _setup_ui(self):
        """add tools"""
        # create the main tab layout
        main_tab_widget = QtWidgets.QTabWidget(self.widget())
        self.addWidget(main_tab_widget)

        # add the General Tab
        general_tab_widget = QtWidgets.QWidget(self.widget())
        general_tab_vertical_layout = QtWidgets.QVBoxLayout()
        general_tab_vertical_layout.setSizeConstraint(QtWidgets.QLayout.SetMaximumSize)
        general_tab_widget.setLayout(general_tab_vertical_layout)

        main_tab_widget.addTab(general_tab_widget, "Generic")

        # Create tools for general tab

        # -------------------------------------------------------------------
        # Open Version
        create_button(
            "Open Version",
            general_tab_vertical_layout,
            GenericTools.version_dialog,
            callback_kwargs={"parent": self.parent(), "mode": 1},
        )

        # Save As Version
        create_button(
            "Save As Version",
            general_tab_vertical_layout,
            GenericTools.version_dialog,
            callback_kwargs={"parent": self.parent(), "mode": 0},
        )

        # Update Outputs
        create_button(
            "Update Savers", general_tab_vertical_layout, GenericTools.update_savers
        )

        # Loader Report
        create_button(
            "Loader Report", general_tab_vertical_layout, GenericTools.loader_report
        )

        # PassThrough All Saver nodes
        create_button(
            "PassThrough All Savers",
            general_tab_vertical_layout,
            GenericTools.pass_through_all_savers,
        )

        # Insert Pipe Router
        create_button(
            "Insert Pipe Router",
            general_tab_vertical_layout,
            GenericTools.insert_pipe_router_to_selected_node,
        )

        # Loader From Saver
        create_button(
            "Loader from Saver",
            general_tab_vertical_layout,
            GenericTools.loader_from_saver,
        )

        # Delete Recent Comps
        create_button(
            "Delete Recent Comps",
            general_tab_vertical_layout,
            GenericTools.delete_recent_comps,
        )

        # Set Frames At Once To 1, 5 and 10
        hbox_layout = QtWidgets.QHBoxLayout()
        general_tab_vertical_layout.addLayout(hbox_layout)
        set_frames_at_once_label = QtWidgets.QLabel()
        set_frames_at_once_label.setText("Set Frames At Once To")
        hbox_layout.addWidget(set_frames_at_once_label)

        for i in [1, 5, 10]:
            button = create_button(
                "%s" % i,
                hbox_layout,
                GenericTools.set_frames_at_once,
                callback_kwargs={"count": i},
            )
            button.setMinimumSize(QtCore.QSize(25, 0))

        general_tab_vertical_layout.addWidget(
            create_separator(general_tab_vertical_layout.parent())
        )

        # Range From Shot
        create_button(
            "Get Comp Range From Database",
            general_tab_vertical_layout,
            GenericTools.range_from_shot,
        )

        # Shot From Range
        create_button(
            "Set Comp Range To Database",
            general_tab_vertical_layout,
            GenericTools.shot_from_range,
        )

        general_tab_vertical_layout.addWidget(
            create_separator(general_tab_vertical_layout.parent())
        )

        # Render Merger
        create_button(
            "Render Merger",
            general_tab_vertical_layout,
            GenericTools.render_merger,
            tooltip="Creates comp setup to merge renders created with Render Slicer.",
        )

        # 3DE4 Lens Distort Node
        import functools

        create_button(
            "3DE4 Lens Distort",
            general_tab_vertical_layout,
            functools.partial(
                GenericTools.tde4_lens_distort_node_creator, self.parent()
            ),
            tooltip=GenericTools.tde4_lens_distort_node_creator.__doc__,
        )

        # 3DE4 Track Point Importer
        import functools

        create_button(
            "3DE4 Import Track Point",
            general_tab_vertical_layout,
            functools.partial(GenericTools.tde4_import_track_point, self.parent()),
            tooltip=GenericTools.tde4_import_track_point.__doc__,
        )

        # Create slate for Current Version
        import functools

        create_button(
            "Create Slate for Current version",
            general_tab_vertical_layout,
            functools.partial(GenericTools.create_slate_for_current_version),
            tooltip=GenericTools.create_slate_for_current_version.__doc__,
        )

        # -------------------------------------------------------------------
        # Add the stretcher
        general_tab_vertical_layout.addStretch()


class GenericTools(object):
    """Generic Tools"""

    @classmethod
    def version_dialog(cls, **args):
        """version dialog"""
        # from anima.ui.scripts import fusion
        # fusion.version_dialog(*args)
        from anima.utils import do_db_setup

        do_db_setup()
        from anima.dcc import fusion

        fusion_env = fusion.Fusion()
        fusion_env.name = "Fusion"

        from anima.ui import version_dialog

        ui_instance = version_dialog.MainDialog(environment=fusion_env, **args)
        ui_instance.show()
        ui_instance.center_window()

    @classmethod
    def update_savers(cls):
        """updates savers, creates missing ones"""
        from anima.utils import do_db_setup

        do_db_setup()
        from anima.dcc import fusion

        fusion_env = fusion.Fusion()
        v = fusion_env.get_current_version()
        fusion_env.create_main_saver_node(version=v)

    @classmethod
    def loader_report(cls):
        """returns the loaders in this comp"""
        from anima.dcc import fusion

        fs = fusion.Fusion()
        comp = fs.comp

        paths = []

        all_loader_nodes = comp.GetToolList(False, "Loader").values()
        for loader_node in all_loader_nodes:
            node_input_list = loader_node.GetInputList()
            for input_entry_key in node_input_list.keys():
                input_entry = node_input_list[input_entry_key]
                input_id = input_entry.GetAttrs()["INPS_ID"]
                if input_id == "Clip":
                    # value = node_input_list[input_entry_key]
                    # input_entry[0] = value
                    # break
                    value = input_entry[0]
                    if value != "" or value is not None:
                        paths.append(value)

        for path in sorted(paths):
            print(path)

    @classmethod
    def pass_through_all_savers(cls):
        """disables all saver nodes in the current comp"""
        from anima.dcc import fusion

        fusion_env = fusion.Fusion()
        comp = fusion_env.comp
        saver_nodes = comp.GetToolList(False, "Saver").values()
        for node in saver_nodes:
            node.SetAttrs({"TOOLB_PassThrough": True})

    @classmethod
    def insert_pipe_router_to_selected_node(cls):
        """inserts a Pipe Router node between the selected node and the nodes
        connected to its output
        """
        from anima.dcc import fusion

        fusion_env = fusion.Fusion()
        comp = fusion_env.comp

        # get active node
        node = comp.ActiveTool

        # get all node outputs
        output = node.FindMainOutput(1)
        connected_inputs = output.GetConnectedInputs()

        # create pipe router
        pipe_router = comp.PipeRouter({"Input": node})

        # connect it to the other nodes
        for connected_input in connected_inputs.values():
            connected_input.ConnectTo(pipe_router)

    @classmethod
    def update_secondary_savers(cls):
        """Updates Savers which are not a Main Saver node"""
        # get all saver nodes
        from anima.dcc import fusion

        fusion_env = fusion.Fusion()
        comp = fusion_env.comp

        all_saver_nodes = fusion_env.comp.GetToolList(False, "Saver").values()

        # filter all Main Saver nodes
        main_savers = fusion_env.get_main_saver_node()
        secondary_savers = [node for node in all_saver_nodes if node not in main_savers]

        # get the output path from one of the main savers

    @classmethod
    def loader_from_saver(cls):
        """creates a loader from the selected saver node"""
        from anima.dcc import fusion

        fusion_env = fusion.Fusion()
        comp = fusion_env.comp

        node = comp.ActiveTool
        flow = comp.CurrentFrame.FlowView
        x, y = flow.GetPosTable(node).values()

        node_input_list = node.GetInputList()

        path = ""
        key = "Clip"
        for input_entry_key in node_input_list.keys():
            input_entry = node_input_list[input_entry_key]
            input_id = input_entry.GetAttrs()["INPS_ID"]
            if input_id == key:
                path = input_entry[0]
                break

        comp.Lock()
        loader_node = comp.AddTool("Loader")
        comp.Unlock()

        node_input_list = loader_node.GetInputList()
        for input_entry_key in node_input_list.keys():
            input_entry = node_input_list[input_entry_key]
            input_id = input_entry.GetAttrs()["INPS_ID"]
            if input_id == key:
                input_entry[0] = path
                break

        # set position near to the saver node
        flow.SetPos(loader_node, x, y + 1.0)
        flow.Select(node, False)
        flow.Select(loader_node, True)
        comp.SetActiveTool(loader_node)

    @classmethod
    def delete_recent_comps(cls):
        """Deletes the Recent Comps value in the current preferences. This was
        created to remedy the low performance bug under Fusion 9 and Windows.
        It is not clear for now what happens under the other OSes.
        """
        import BlackmagicFusion as bmf

        fusion = bmf.scriptapp("Fusion")
        print("Erasing RecentComps value!")
        fusion.SetPrefs("Global.RecentComps", {})
        fusion.SavePrefs()

    @classmethod
    def set_frames_at_once(cls, count=1):
        """Sets the frames at once value to the given number
        :param count:
        :return:
        """
        import BlackmagicFusion as bmf

        fusion = bmf.scriptapp("Fusion")
        comp = fusion.GetCurrentComp()
        comp.SetPrefs("Comp.Memory.FramesAtOnce", count)

    @classmethod
    def afanasy_job_submitter(cls):
        """alpha feature"""
        # call the lua script from /opt/cgru/plugins/fusion/
        pass

    @classmethod
    def range_from_shot(cls):
        """sets the range from the shot"""
        from anima.utils import do_db_setup

        do_db_setup()
        from anima.dcc import fusion

        fusion_env = fusion.Fusion()
        version = fusion_env.get_current_version()
        fusion_env.set_range_from_shot(version)

    @classmethod
    def shot_from_range(cls):
        """updates the Shot.cut_in and Shot.cut_out attributes from the current range"""
        from anima.utils import do_db_setup

        do_db_setup()
        from anima.dcc import fusion

        fusion_env = fusion.Fusion()
        version = fusion_env.get_current_version()
        try:
            fusion_env.set_shot_from_range(version)
        except BaseException as e:
            QtWidgets.QMessageBox.critical(None, "Error", "%s" % e)
        finally:
            QtWidgets.QMessageBox.information(
                None, "Success", "Shot Range has been updated successfully!"
            )

    @classmethod
    def render_merger(cls):
        """calls the render merger"""
        from anima.dcc.fusion import render_merger

        rm = render_merger.RenderMerger()
        rm.ui()

    @classmethod
    def tde4_lens_distort_node_creator(cls, parent):
        """creates lens distort nodes from the given 3de4 lens file"""
        # show a file browser
        dialog = QtWidgets.QFileDialog(parent, "Choose file")
        dialog.setNameFilter("3DE4 Lens Files (*.txt)")
        dialog.setFileMode(QtWidgets.QFileDialog.ExistingFile)
        if dialog.exec_():
            file_path = dialog.selectedFiles()[0]
            if not file_path:
                return
            from anima.dcc.fusion.utils import TDE4LensDistortionImporter

            lens_importer = TDE4LensDistortionImporter()
            lens_importer.import_(file_path)

    @classmethod
    def tde4_import_track_point(cls, parent):
        """imports 3DEqualizer track point as a Tracker"""
        # show a file browser
        dialog = QtWidgets.QFileDialog(parent, "Choose file")
        dialog.setNameFilter("3DE4 Track Point (*.txt)")
        dialog.setFileMode(QtWidgets.QFileDialog.ExistingFile)
        if dialog.exec_():
            file_path = dialog.selectedFiles()[0]
            if not file_path:
                return
            from anima.dcc.fusion.utils import TDE4PointImporter

            # use the project x and y resolution
            from anima.dcc import fusion

            f = fusion.Fusion()
            comp = f.comp
            width = comp.GetPrefs("Comp.FrameFormat.Width")
            height = comp.GetPrefs("Comp.FrameFormat.Height")

            lens_importer = TDE4PointImporter(xres=width, yres=height)
            lens_importer.load_points(file_path)

    @classmethod
    def create_slate_for_current_version(cls):
        """creates slate for the current version"""
        from anima.dcc import fusion

        f = fusion.Fusion()
        v = f.get_current_version()
        f.create_slate_node(v)
