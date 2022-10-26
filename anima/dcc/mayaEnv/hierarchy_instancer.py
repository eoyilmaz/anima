# -*- coding: utf-8 -*-
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

__version__ = "10.6.12"


class HierarchyInstancer(object):
    """the hierarchy object"""

    def __init__(self):
        self._instantiable_types = []

        self.add_instantiable(pm.nodetypes.Mesh)
        self.add_instantiable(pm.nodetypes.NurbsCurve)
        self.add_instantiable(pm.nodetypes.NurbsSurface)
        self.add_instantiable(pm.nodetypes.Subdiv)
        self.add_instantiable(pm.nodetypes.Locator)

    def add_instantiable(self, node_type):
        """Adds new instantiable node type, the type should be a
        pymel.core.nodeType class
        """
        self._instantiable_types.append(node_type)

    def walk_hierarchy(self, node):
        """for the given dag node, walks through the hierarchy"""
        nodes = []
        for node in node.getChildren():
            # try to get children if it is a transform node
            if isinstance(node, pm.nodetypes.Transform):
                child_nodes = self.walk_hierarchy(node)
                nodes.append(node)
                nodes += child_nodes
        return nodes

    def instance(self, source_transform_node):
        """instances the given nodes hierarchy"""

        # duplicate the given node
        # then replace the instantiable nodes with instances

        # find instantiable nodes in the node and dupNode
        source_hierarchy = self.walk_hierarchy(source_transform_node)

        # if there is no node in the sourceHierarchy just return
        # the instance of the given node
        if len(source_hierarchy) < 1:
            dup_node = pm.duplicate(source_transform_node, ilf=1, rc=True)[0]
            pm.select(dup_node)
            return dup_node

        dup_node = pm.duplicate(source_transform_node, rc=True)[0]
        dup_hierarchy = self.walk_hierarchy(dup_node)

        for i, node in enumerate(dup_hierarchy):

            shape = node.getShape()
            if shape is not None and isinstance(shape, tuple(self._instantiable_types)):
                # instance the corresponding sourceNode
                source_node = source_hierarchy[i]
                new_instance_node = pm.duplicate(source_node, ilf=True)[0]

                pm.parent(new_instance_node, node.getParent(), r=False)
                pm.delete(node)

        return dup_node
