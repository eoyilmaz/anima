# -*- coding: utf-8 -*-
# Copyright (c) 2012-2019, Erkan Ozgur Yilmaz
#
# This module is part of anima and is released under the MIT
# License: http://www.opensource.org/licenses/MIT
import os


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


class RedShiftTextureProcessor(object):
    """A wrapper for the ``redshiftTextureProcessor.exe``

    TextureProcessor <inputfile> [options]

    Options are:
            -l              Force linear gamma (recommended for floating point textures)
            -s              Force SRGB gamma (recommended for integer textures)
            (Note the default gamma operation is as follows: -l for floating point textures and -s for integer textures)
            -p              Photometric IES data (for IES profile types)
            -wx             Used as a tiled texture with wrapping/repeats
            -wy             Used as a tiled texture with wrapping/repeats
            -isphere        Image Based Light - Sphere projection
            -ihemisphere    Image Based Light - Hemisphere projection
            -imirrorball    Image Based Light - Mirrorball projection
            -iangularmap    Image Based Light - Angular Map projection
            -ocolor         Sprite Cut-Out Map opacity from color intensity
            -oalpha         Sprite Cut-Out Map opacity from alpha
            -noskip         Disable the skipping of already converted textures if the processor thinks no data has changed
            -r              Recursively process textures in sub directories
            -log            Enable logging to log file
    """
    executable = os.path.join(
        os.environ.get('REDSHIFT_COREDATAPATH', ''),
        'bin/redshiftTextureProcessor'
    )

    def __init__(self, input_file_full_path, l=None, s=None, p=None, wx=None,
                 wy=None, isphere=None, ihemisphere=None, imirrorball=None,
                 iangularmap=None, ocolor=None, oalpha=None, noskip=False,
                 r=None, log=None):

        self.input_file_full_path = os.path.normpath(
            os.path.expandvars(
                input_file_full_path
            )
        ).replace('\\', '/')
        self.files_to_process = []
        self.expand_tiles()
        self.noskip = noskip

    def expand_tiles(self):
        """expands any tiles and returns a list of file paths
        """
        if '<' in self.input_file_full_path:
            # replace any <U> and <V> with an *
            self.input_file_full_path = \
                self.input_file_full_path\
                    .replace('<U>', '*')\
                    .replace('<V>', '*')\
                    .replace('<UDIM>', '*')

        import glob
        self.files_to_process = glob.glob(self.input_file_full_path)

    def convert(self):
        """converts the given input_file to an rstexbin
        """
        processed_files = []

        import subprocess
        from anima.ui.progress_dialog import ProgressDialogManager
        pdm = ProgressDialogManager()
        caller = pdm.register(
            len(self.files_to_process),
            title='Converting Textures'
        )
        for file_path in self.files_to_process:
            command = '%s "%s"' % (self.executable, file_path)
            rsmap_full_path = \
                '%s.rstexbin' % os.path.splitext(file_path)[0]

            # os.system(command)
            if os.name == 'nt':
                proc = subprocess.Popen(
                    command,
                    creationflags=subprocess.SW_HIDE,
                    shell=True
                )
            else:
                proc = subprocess.Popen(
                    command,
                    shell=True
                )
            proc.wait()

            processed_files.append(rsmap_full_path)
            caller.step()
        caller.end_progress()

        return processed_files
