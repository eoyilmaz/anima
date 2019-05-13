# -*- coding: utf-8 -*-
# Copyright (c) 2012-2019, Erkan Ozgur Yilmaz
#
# This module is part of anima and is released under the BSD 2
# License: http://www.opensource.org/licenses/BSD-2-Clause


class RSProxyDataManager(object):
    """Manages data
    """

    def __init__(self):
        self.data = []

    def load(self, path):
        import json
        with open(path, "r") as f:
            data = json.load(f)

        for i in range(len(data['instance_file'])):
            data_obj = RSProxyDataObject()
            self.data.append(data_obj)

            data_obj.pos = data['pos'][i]
            data_obj.rot = data['rot'][i]
            data_obj.sca = data['sca'][i]
            data_obj.parent_name = data['parent_name'][i]
            data_obj.instance_file = data['instance_file'][i]
            data_obj.node_name = data['node_name'][i]

    def create(self):
        """creates all nodes
        """
        for d in self.data:
            d.create()


class RSProxyDataObject(object):
    """Holds raw data
    """

    def __init__(self):
        self.pos = None
        self.rot = None
        self.sca = None
        self.instance_file = ''
        self.node_name = ''

        self.transform_node = None
        self.shape_node = None
        self.rs_proxy_node = None
        self.parent_node = None
        self.parent_name = None

    def get_parent(self):
        """gets the parent node or creates one
        """
        import pymel.core as pm

        parent_node_name = self.parent_name
        nodes_with_name = pm.ls('|%s' % parent_node_name)
        parent_node = None
        if nodes_with_name:
            parent_node = nodes_with_name[0]

        if not parent_node:
            # create one
            previous_parent = None
            current_node = None
            splits = self.parent_name.split("|")
            for i, node_name in enumerate(splits):
                full_node_name = '|' + '|'.join(splits[:i + 1])
                list_nodes = pm.ls(full_node_name)
                if list_nodes:
                    current_node = list_nodes[0]
                else:
                    current_node = pm.nt.Transform(name=node_name)
                if previous_parent:
                    pm.parent(current_node, previous_parent, r=1)
                previous_parent = current_node

            # parent_node = pm.nt.Transform(name=parent_node_name)
            parent_node = current_node

        return parent_node

    def create(self):
        """creates Maya objects
        """
        import pymel.core as pm
        self.parent_node = self.get_parent()
        self.shape_node = pm.nt.Mesh(name='%sShape' % self.node_name)
        self.transform_node = self.shape_node.getParent()
        self.transform_node.rename(self.node_name)

        self.rs_proxy_node = \
            pm.nt.RedshiftProxyMesh(name='%sRsProxy' % self.node_name)
        self.rs_proxy_node.outMesh >> self.shape_node.inMesh
        self.rs_proxy_node.fileName.set(self.instance_file)

        # self.transform_node.t.set(self.pos)
        # self.transform_node.r.set(self.rot)
        # self.transform_node.s.set([self.sca, self.sca, self.sca])
        self.parent_node.t.set(self.pos)
        self.parent_node.r.set(self.rot)
        self.parent_node.s.set([self.sca, self.sca, self.sca])

        # assign default shader
        lambert1 = pm.ls('lambert1')[0]
        lambert1_shading_group = \
            lambert1.outputs(type='shadingEngine')[0]
        pm.sets(lambert1_shading_group, fe=self.transform_node)

        pm.parent(self.transform_node, self.parent_node, r=1)

