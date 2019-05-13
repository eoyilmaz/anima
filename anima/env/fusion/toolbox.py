# -*- coding: utf-8 -*-
# Copyright (c) 2018-2019, Erkan Ozgur Yilmaz
#
# This module is part of anima-tools and is released under the BSD 2
# License: http://www.opensource.org/licenses/BSD-2-Clause

from anima.ui.base import AnimaDialogBase
from anima.ui.lib import QtCore, QtWidgets


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


def add_button(label, layout, callback, tooltip=''):
    """A wrapper for button creation

    :param label: The label of the button
    :param layout: The layout that the button is going to be placed under.
    :param callback: The callable that will be called when the button is
      clicked.
    :param str tooltip: Optional tooltip for the button
    :return:
    """
    # button
    button = QtWidgets.QPushButton(layout.parentWidget())
    button.setText(label)
    layout.addWidget(button)

    button.setToolTip(tooltip)

    # Signal
    QtCore.QObject.connect(
        button,
        QtCore.SIGNAL("clicked()"),
        callback
    )

    return button


class ToolboxDialog(QtWidgets.QDialog, AnimaDialogBase):
    """The toolbox dialog
    """

    def __init__(self, environment=None, parent=None):
        super(ToolboxDialog, self).__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        self.setWindowModality(QtCore.Qt.ApplicationModal)
        self.setModal(True)
        self.resize(300, 800)
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
            GenericTools.version_creator.__doc__
        )

        # Loader Report
        add_button(
            'Loader Report',
            general_tab_vertical_layout,
            GenericTools.loader_report,
            GenericTools.loader_report.__doc__
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
        from anima.ui.scripts import fusion
        fusion.version_creator()

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
