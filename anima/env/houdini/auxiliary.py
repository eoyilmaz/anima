# -*- coding: utf-8 -*-
# Copyright (c) 2018-2020, Erkan Ozgur Yilmaz
#
# This module is part of anima and is released under the MIT
# License: http://www.opensource.org/licenses/MIT
"""Helper functions and classes for Houdini.

The name of this module is inspired from the Maya module.
"""
import hou


def get_network_pane():
    """returns the active network pane
    """
    # This will return the first network pane, not the active one
    network_pane = None
    for pane_tab in hou.ui.paneTabs():
        if isinstance(pane_tab, hou.NetworkEditor):
            return pane_tab


def create_spare_input(node, value=''):
    """creates spare inputs for the given node and sets the value

    :param hou.Node node: The node to insert the spare input to.
    :param str value: The value of the parameter
    """
    # Create space input0 for rs proxy output node
    parm_template_group = node.parmTemplateGroup()
    parm_template_group.append(
        hou.StringParmTemplate(
            'spare_input0', 'Spare Input 0', 1,
            string_type=hou.stringParmType.NodeReference
        )
    )
    node.setParmTemplateGroup(parm_template_group)
    node.parm('spare_input0').set(value)
