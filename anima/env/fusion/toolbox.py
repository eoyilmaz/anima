# -*- coding: utf-8 -*-
# Copyright (c) 2018-2019, Erkan Ozgur Yilmaz
#
# This module is part of anima and is released under the MIT
# License: http://www.opensource.org/licenses/MIT

from anima.ui.base import AnimaDialogBase
from anima.ui.lib import QtCore, QtWidgets
from anima.ui.utils import add_button


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
    from anima.ui.base import ui_caller
    return ui_caller(app_in, executor, ToolboxDialog, **kwargs)


class ToolboxDialog(QtWidgets.QDialog, AnimaDialogBase):
    """The toolbox dialog
    """

    def __init__(self, environment=None, parent=None):
        super(ToolboxDialog, self).__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        self.setWindowModality(QtCore.Qt.ApplicationModal)
        self.setModal(True)
        self.resize(300, 300)
        size_policy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Preferred,
            QtWidgets.QSizePolicy.Preferred
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
        general_tab_vertical_layout.setSizeConstraint(
            QtWidgets.QLayout.SetMaximumSize
        )
        general_tab_widget.setLayout(general_tab_vertical_layout)

        main_tab_widget.addTab(general_tab_widget, 'Generic')

        # Create tools for general tab

        # -------------------------------------------------------------------
        # Version Creator
        add_button(
            'Version Creator',
            general_tab_vertical_layout,
            GenericTools.version_creator,
            callback_kwargs={"parent": self.parent()}
        )

        # Update Outputs
        add_button(
            'Update Savers',
            general_tab_vertical_layout,
            GenericTools.update_savers
        )

        # Loader Report
        add_button(
            'Loader Report',
            general_tab_vertical_layout,
            GenericTools.loader_report
        )

        # PassThrough All Saver nodes
        add_button(
            'PassThrough All Savers',
            general_tab_vertical_layout,
            GenericTools.pass_through_all_savers
        )

        # Insert Pipe Router
        add_button(
            'Insert Pipe Router',
            general_tab_vertical_layout,
            GenericTools.insert_pipe_router_to_selected_node
        )

        # -------------------------------------------------------------------
        # Add the stretcher
        general_tab_vertical_layout.addStretch()


class GenericTools(object):
    """Generic Tools
    """

    @classmethod
    def version_creator(cls, **args):
        """version creator
        """
        # from anima.ui.scripts import fusion
        # fusion.version_creator(*args)
        from anima.utils import do_db_setup
        do_db_setup()
        from anima.env import fusion
        fusion_env = fusion.Fusion()
        fusion_env.name = 'Fusion'

        from anima.ui import version_creator

        ui_instance = version_creator.MainDialog(
            environment=fusion_env,
            **args
        )
        ui_instance.show()
        ui_instance.center_window()

    @classmethod
    def update_savers(cls):
        """updates savers, creates missing ones
        """
        from anima.utils import do_db_setup
        do_db_setup()
        from anima.env import fusion
        fusion_env = fusion.Fusion()
        v = fusion_env.get_current_version()
        fusion_env.create_main_saver_node(version=v)

    @classmethod
    def loader_report(cls):
        """returns the loaders in this comp
        """
        from anima.env import fusion
        fs = fusion.Fusion()
        comp = fs.comp

        paths = []

        all_loader_nodes = comp.GetToolList(False, 'Loader').values()
        for loader_node in all_loader_nodes:
            node_input_list = loader_node.GetInputList()
            for input_entry_key in node_input_list.keys():
                input_entry = node_input_list[input_entry_key]
                input_id = input_entry.GetAttrs()['INPS_ID']
                if input_id == 'Clip':
                    # value = node_input_list[input_entry_key]
                    # input_entry[0] = value
                    # break
                    value = input_entry[0]
                    if value != '' or value is not None:
                        paths.append(value)

        for path in sorted(paths):
            print(path)

    @classmethod
    def pass_through_all_savers(cls):
        """disables all saver nodes in the current comp
        """
        from anima.env import fusion
        fusion_env = fusion.Fusion()
        comp = fusion_env.comp
        saver_nodes = comp.GetToolList(False, 'Saver').values()
        for node in saver_nodes:
            node.SetAttrs({"TOOLB_PassThrough": True})

    @classmethod
    def insert_pipe_router_to_selected_node(cls):
        """inserts a Pipe Router node between the selected node and the nodes
        connected to its output
        """
        from anima.env import fusion
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
        """Updates Savers which are not a Main Saver node
        """
        # get all saver nodes
        from anima.env import fusion
        fusion_env = fusion.Fusion()
        comp = fusion_env.comp

        all_saver_nodes = fusion_env.comp.GetToolList(False, 'Saver').values()

        # filter all Main Saver nodes
        main_savers = fusion_env.get_main_saver_node()
        secondary_savers = [
            node for node in all_saver_nodes if node not in main_savers
        ]

        # get the output path from one of the main savers
