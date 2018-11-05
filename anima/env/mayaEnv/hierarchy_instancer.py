# -*- coding: utf-8 -*-
# Copyright (c) 2012-2018, Anima Istanbul
#
# This module is part of anima-tools and is released under the BSD 2
# License: http://www.opensource.org/licenses/BSD-2-Clause
"""
hierarchy_instancer by

v10.6.17

Given a group, it instances the hierarchy. It is written to avoid having
instanced groups in the scene. Thus multi instancing is avoided.

ChangeLog:
----------

10.6.17
- the script now works with single object hierarchies
- after the script finishes it job, it selects the created top most node

10.6.12
- initial working version
"""

import pymel.core as pm

__version__ = '10.6.12'


class HierarchyInstancer(object):
    """the hierarchy object
    """

    def __init__(self):
        self._instanceables = []

        self.add_instanceable(pm.nodetypes.Mesh)
        self.add_instanceable(pm.nodetypes.NurbsCurve)
        self.add_instanceable(pm.nodetypes.NurbsSurface)
        self.add_instanceable(pm.nodetypes.Subdiv)
        self.add_instanceable(pm.nodetypes.Locator)

    def add_instanceable(self, node_type):
        """Adds new instanceable node type, the type should be a
        pymel.core.nodeType class
        """
        self._instanceables.append(node_type)

    def walk_hierarchy(self, node):
        """for the given dag node, walks through the hierarchy
        """
        assert(isinstance(node, pm.nodetypes.Transform))

        nodes = []

        for node in node.getChildren():
            # try to get children if it is a transform node
            if isinstance(node, pm.nodetypes.Transform):
                child_nodes = self.walk_hierarchy(node)

                nodes.append(node)
                nodes += child_nodes

        return nodes

    def instance(self, source_transform_node):
        """instances the given nodes hierarchy
        """

        # duplicate the given node
        # then replace the instanceable nodes with instances

        # find instanceable nodes in the node and dupNode
        source_hierarchy = self.walk_hierarchy(source_transform_node)

        # if there is no node in the sourceHierarchy just return
        # the instance of the given node
        if len(source_hierarchy) < 1:
            dup_node = pm.duplicate(source_transform_node, ilf=1, rc=True)[0]
            pm.select(dup_node)
            return

        dup_node = pm.duplicate(source_transform_node, rc=True)[0]
        dup_hierarchy = self.walk_hierarchy(dup_node)

        for i, node in enumerate(dup_hierarchy):

            shape = node.getShape()
            if shape is not None and isinstance(shape,
                                                tuple(self._instanceables)):
                # instance the corresponding sourceNode
                source_node = source_hierarchy[i]
                new_instance_node = pm.duplicate(source_node, ilf=True)[0]

                pm.parent(new_instance_node, node.getParent(), r=False)
                pm.delete(node)

        pm.select(dup_node)
        return dup_node
