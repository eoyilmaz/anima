# -*- coding: utf-8 -*-
# Copyright (c) 2012-2014, Anima Istanbul
#
# This module is part of anima-tools and is released under the BSD 2
# License: http://www.opensource.org/licenses/BSD-2-Clause
import os
import re
import subprocess
import uuid

import pymel.core as pm
from stalker import LocalSession

from anima.repr import Representation
from anima.env.mayaEnv import auxiliary


RENDER_RELATED_NODE_TYPES = [
    'shadingEngine',

    'anisotropic',
    'blinn',
    'lambert',
    'layeredShader',
    'oceanShader',
    'phong',
    'phongE',
    'rampShader',
    'shadingMap',
    'surfaceShader',
    'useBackground',

    'bulge',
    'checker',
    'cloth',
    'file',
    'fluidTexture2D',
    'fractal',
    'grid',
    'mandelbrot',
    'mountain',
    'movie',
    'noise',
    'ocean',
    'psdFileTex',
    'ramp',
    'water',

    'brownian',
    'cloud',
    'crater',
    'fluidTexture3D',
    'granite',
    'leather',
    'mandelbrot3D',
    'marble',
    'rock',
    'snow',
    'solidFractal',
    'stucco',
    'volumeNoise',
    'wood',

    'bump2d',
    'bump3d',
    'place2dTexture',
    'place3dTexture',
    'plusMinusAverage',
    'samplerInfo',
    'stencil',
    'uvChooser',
    'surfaceInfo',
    'blendColors',
    'clamp',
    'contrast',
    'gammaCorrect',
    'hsvToRgb',
    'luminance',
    'remapColor',
    'remapHsv',
    'remapValue',
    'rgbToHsv',
    'surfaceLuminance',
    'imagePlane',

    'aiImage',
    'aiNoise',
    'aiAmbientOcclusion',
    'aiHair',
    'aiRaySwitch',
    'aiShadowCatcher',
    'aiSkin',
    'aiSkinSss',  # To be removed
    'aiStandard',
    'aiUtility',
    'aiWireframe',
]


READ_ONLY_NODE_NAMES = [
    'lambert1',
    'particleCloud1',
    'shaderGlow1',
    'initialParticleSE',
    'initialShadingGroup'
]


class RepresentationGenerator(object):
    """Generates different representations of the current scene
    """

    def __init__(self, version=None):
        local_session = LocalSession()
        self.logged_in_user = local_session.logged_in_user

        if not self.logged_in_user:
            raise RuntimeError('Please login first!')

        from anima.env.mayaEnv import Maya
        self.maya_env = Maya()

        self.base_take_name = None
        self.version = version

    @classmethod
    def get_local_root_nodes(cls):
        """returns the root nodes that are not referenced
        """
        return [node for node in auxiliary.get_root_nodes()
                if node.referenceFile() is None]

    def get_latest_repr_version(self, take_name):
        """returns the latest published version or creates a new version

        :param str take_name: The take_name
        :return:
        """
        from stalker import Version

        # filter to get the latest published version
        v = Version.query\
            .filter(Version.task == self.version.task)\
            .filter(Version.take_name == take_name)\
            .filter(Version.is_published == True)\
            .order_by(Version.version_number.desc())\
            .first()

        if v is None:
            # create a new version
            v = Version(
                created_by=self.logged_in_user,
                task=self.version.task,
                take_name=take_name
            )
            v.is_published = True
        else:
            # change updated by
            v.updated_by = self.logged_in_user

        return v

    @classmethod
    def is_model_task(cls, task):
        """checks if the given task is a model task

        :param task: A Stalker Task instance
        """
        task_type = task.type
        if task_type:
            # check the task type name
            if task_type.name.lower() in ['model']:
                return True
        else:
            # check the task name
            if task.name.lower() in ['model']:
                return True

        # if we came here it must not be a model task
        return False

    @classmethod
    def is_look_dev_task(cls, task):
        """checks if the given task is a look development task

        :param task: A Stalker Task instance
        """
        task_type = task.type
        if task_type:
            # check the task type name
            if task_type.name.lower() in ['look development']:
                return True
        else:
            # check the task name
            if task.name.lower() in ['look_dev', 'lookdev', 'look dev']:
                return True

        # if we came here it must not be a look dev task task
        return False

    @classmethod
    def is_vegetation_task(cls, task):
        """checks if the given task is a vegetation task

        :param task: A Stalker Task instance
        """
        task_type = task.type
        if task_type:
            # check the task type name
            if task_type.name.lower() in ['vegetation']:
                return True
        else:
            # check the task name
            if task.name.lower() in ['vegetation']:
                return True

        # if we came here it must not be a vegetation task task
        return False

    @classmethod
    def is_exterior_or_interior_task(cls, task):
        """checks if the given task is the first Layout task of an
        Exterior or Interior task.

        :param task: a stalker.task
        :return:
        """

        if task.type and task.type.name.lower() == 'layout':
            parent = task.parent
            if parent and parent.parent and parent.parent.type \
               and parent.parent.type.name.lower() in ['exterior', 'interior']:
                return True

        return False

    def _validate_version(self, version):
        """validates the given version value

        :param version: A stalker.model.version.Version instance
        :return:
        """
        if not version:
            raise RuntimeError(
                'Please supply a valid Stalker version!'
            )

        from stalker import Version
        if not isinstance(version, Version):
            raise TypeError(
                'version should be a stalker.models.version.Version instance'
            )

        r = Representation(version=version)

        self.base_take_name = r.get_base_take_name(version)
        if not r.is_base():
            raise RuntimeError(
                'This is not a Base take for this representation series, '
                'please open the base (%s) take!!!' % self.base_take_name
            )

        return version

    def open_version(self, version=None):
        """Opens the given version

        :param version: A stalker.models.version.Version instance
        :return:
        """
        current_v = self.maya_env.get_current_version()
        if current_v is not version:
            self.maya_env.open(version, force=True, skip_update_check=True)

    def generate_all(self):
        """generates all representations at once
        """
        self.generate_bbox()
        self.generate_proxy()
        self.generate_gpu()
        self.generate_ass()

    def generate_bbox(self):
        """generates the BBox representation of the current scene
        """
        # validate the version first
        self.version = self._validate_version(self.version)

        self.open_version(self.version)

        task = self.version.task

        # check if all references have an BBOX repr first
        refs_with_no_bbox_repr = []
        for ref in pm.listReferences():
            if not ref.has_repr('BBOX'):
                refs_with_no_bbox_repr.append(ref)

        if len(refs_with_no_bbox_repr):
            raise RuntimeError(
                'Please generate the BBOX Representation of the references '
                'first!!!\n%s' %
                '\n'.join(map(lambda x: str(x.path), refs_with_no_bbox_repr))
            )

        # do different things for Vegetation tasks
        if self.is_vegetation_task(task):
            # find the _pfxPolygons node
            pfx_polygons_node = pm.PyNode('kks___vegetation_pfxPolygons')

            all_children = []
            for node in pfx_polygons_node.getChildren():
                for child_node in node.getChildren():
                    all_children.append(child_node)

            auxiliary.replace_with_bbox(all_children)

            # clean up other nodes
            pm.delete('kks___vegetation_pfxStrokes')
            pm.delete('kks___vegetation_paintableGeos')

        else:
            # replace all root references with their BBOX representation
            for ref in pm.listReferences():
                ref.to_repr('BBOX')
                ref.unload()

            # find all non referenced root nodes
            root_nodes = self.get_local_root_nodes()

            if len(root_nodes):
                all_children = []
                for root_node in root_nodes:
                    for child in root_node.getChildren():
                        all_children.append(child)

                auxiliary.replace_with_bbox(all_children)

            # reload all references
            for ref in pm.listReferences():
                ref.load()

        # if this is an Exterior/Interior -> Layout -> Hires task flatten it
        if self.is_exterior_or_interior_task(task):
            # and import all of the references
            all_refs = pm.listReferences()
            while len(all_refs) != 0:
                for ref in all_refs:
                    ref.importContents()
                all_refs = pm.listReferences()

        # save the scene as {{original_take}}___BBOX
        # use maya
        take_name = '%s%s%s' % (
            self.base_take_name, Representation.repr_separator, 'BBOX'
        )
        v = self.get_latest_repr_version(take_name)

        self.maya_env.save_as(v)

        # reopen the original version
        pm.newFile(force=True)

    def generate_proxy(self):
        """generates the Proxy representation of the current scene
        """
        pass

    def generate_gpu(self):
        """generates the GPU representation of the current scene
        """
        # validate the version first
        self.version = self._validate_version(self.version)

        self.open_version(self.version)

        # load necessary plugins
        pm.loadPlugin('gpuCache')
        pm.loadPlugin('AbcExport')
        pm.loadPlugin('AbcImport')

        # check if all references have an GPU repr first
        refs_with_no_gpu_repr = []
        for ref in pm.listReferences():
            if not ref.has_repr('GPU'):
                refs_with_no_gpu_repr.append(ref)

        if len(refs_with_no_gpu_repr):
            raise RuntimeError(
                'Please generate the GPU Representation of the references '
                'first!!!\n%s' %
                '\n'.join(map(lambda x: str(x.path), refs_with_no_gpu_repr))
            )

        # convert all references to GPU
        for ref in pm.listReferences():
            # check if this is a Model reference
            ref.to_repr('GPU')
            # unload all references
            ref.unload()

        root_nodes = self.get_local_root_nodes()

        if len(root_nodes):
            abc_command = \
                'AbcExport -j "-frameRange %(start_frame)s %(end_frame)s ' \
                '-ro -stripNamespaces ' \
                '-uvWrite ' \
                '-wholeFrameGeo ' \
                '-worldSpace ' \
                '-root |%(node)s -file %(file_path)s";'

            gpu_command = \
                'gpuCache -startTime %(start_frame)s -endTime %(end_frame)s ' \
                '-optimize -optimizationThreshold 40000 ' \
                '-writeMaterials ' \
                '-directory "%(path)s" ' \
                '-fileName "%(filename)s" ' \
                '%(node)s;'

            # for local models generate an ABC file
            output_path = os.path.join(self.version.absolute_path,
                                       'Outputs/alembic/')

            start_frame = end_frame = int(pm.currentTime(q=1))

            allowed_shapes = (
                pm.nt.Mesh,
                pm.nt.NurbsCurve,
                pm.nt.NurbsSurface
            )

            for root_node in root_nodes:
                # export each child of each root as separate nodes
                for child_node in root_node.getChildren():

                    # check if it is a transform node
                    if not isinstance(child_node, pm.nt.Transform):
                        continue

                    # check the shape
                    node_shape = child_node.getShape()
                    if not node_shape:
                        # check if it has child nodes
                        if len(child_node.getChildren()) == 0:
                            continue
                    elif not isinstance(node_shape, allowed_shapes):
                        continue

                    child_name = child_node.name()
                    child_shape = child_node.getShape()
                    child_shape_name = None
                    if child_shape:
                        child_shape_name = child_shape.name()

                    child_full_path = \
                        child_node.fullPath()[1:].replace('|', '_')
                    output_filename =\
                        '%s' % (
                            child_full_path
                        )

                    # check if file exists
                    try:
                        pm.mel.eval(
                            gpu_command % {
                                'start_frame': start_frame,
                                'end_frame': end_frame,
                                'node': child_node.fullPath(),
                                'path': output_path,
                                'filename': output_filename
                            }
                        )
                    except pm.MelError:
                        # just pass it
                        pass

                    # delete the child and add a GPU node instead
                    pm.delete(child_node)
                    cache_file_full_path = \
                        os.path\
                        .join(output_path, '%s.abc' % output_filename)\
                        .replace('\\', '/')

                    # check if file exists
                    if os.path.exists(cache_file_full_path):
                        gpu_node = pm.createNode('gpuCache')
                        gpu_node_tra = gpu_node.getParent()

                        pm.parent(gpu_node_tra, root_node)
                        gpu_node_tra.rename(child_name)

                        if child_shape_name is not None:
                            gpu_node.rename(child_shape_name)

                        gpu_node.setAttr(
                            'cacheFileName',
                            cache_file_full_path,
                            type="string"
                        )

        # load all references again
        for ref in pm.listReferences():
            # load all references
            ref.load()

        # if this is an Exterior/Interior -> Layout -> Hires task flatten it
        task = self.version.task
        if self.is_exterior_or_interior_task(task):
            # and import all of the references
            all_refs = pm.listReferences()
            while len(all_refs) != 0:
                for ref in all_refs:
                    ref.importContents()
                all_refs = pm.listReferences()

        # 6. save the scene as {{original_take}}___GPU
        # use maya
        take_name = '%s%s%s' % (
            self.base_take_name, Representation.repr_separator, 'GPU'
        )
        v = self.get_latest_repr_version(take_name)
        self.maya_env.save_as(v)

        # clear scene
        pm.newFile(force=True)

    def make_tx(self, texture_path):
        """converts the given texture to TX
        """
        tx_path = ''.join([os.path.splitext(texture_path)[0], '.tx'])

        # generate if not exists
        if not os.path.exists(tx_path):
            cmd = 'maketx -o "%s" -u --oiio %s' % (tx_path, texture_path)

            if os.name == 'nt':
                proc = subprocess.Popen(
                    cmd,
                    creationflags=subprocess.SW_HIDE,
                    shell=True
                )
            else:
                proc = subprocess.Popen(
                    cmd,
                    shell=True
                )

            proc.wait()
        return tx_path

    def generate_ass(self):
        """generates the ASS representation of the current scene

        For Model Tasks the ASS is generated over the LookDev Task because it
        is not possible to assign a material to an object inside an ASS file.
        """
        # before doing anything, check if this is a look dev task
        # and export the objects from the referenced files with their current
        # shadings, then replace all of the references to ASS repr and than
        # add Stand-in nodes and parent them under the referenced models

        # load necessary plugins
        pm.loadPlugin('mtoa')

        # validate the version first
        self.version = self._validate_version(self.version)

        self.open_version(self.version)

        task = self.version.task

        export_command = 'arnoldExportAss -f "%(path)s" -s -mask 24 ' \
                         '-lightLinks 0 -compressed -boundingBox ' \
                         '-shadowLinks 0 -cam perspShape;'

        # calculate output path
        output_path = os.path.join(self.version.absolute_path, 'Outputs/ass/')

        allowed_shapes = (
            pm.nt.Mesh,
            pm.nt.NurbsCurve,
            pm.nt.NurbsSurface
        )

        # check if all references have an ASS repr first
        refs_with_no_ass_repr = []
        for ref in pm.listReferences():
            if not ref.has_repr('ASS'):
                refs_with_no_ass_repr.append(ref)

        if len(refs_with_no_ass_repr):
            raise RuntimeError(
                'Please generate the ASS Representation of the references '
                'first!!!\n%s' %
                '\n'.join(map(lambda x: str(x.path), refs_with_no_ass_repr))
            )

        if self.is_look_dev_task(task):
            # in look dev files, we export the ASS files directly from the Base
            # version and parent the resulting Stand-In node to the parent of
            # the child node

            # unload any references that is not a Model file
            for ref in pm.listReferences():
                v = ref.version
                unload_ref = True
                if v:
                    ref_task = v.task
                    if self.is_model_task(ref_task):
                        unload_ref = False

                if unload_ref:
                    ref.unload()

            # Make all texture paths relative
            # replace all "$REPO#" from all texture paths first
            types_and_attrs = {
                'aiImage': 'filename',
                'file': 'fileTextureName',
                'imagePlane': 'imageName'
            }

            for node_type in types_and_attrs.keys():
                attr_name = types_and_attrs[node_type]
                for node in pm.ls(type=node_type):
                    orig_path = node.getAttr(attr_name).replace("\\", "/")
                    path = re.sub(
                        r'(\$REPO[0-9/]+)',
                        '',
                        orig_path
                    )
                    tx_path = self.make_tx(path)
                    node.setAttr(attr_name, tx_path)

            # randomize all render node names
            for node in pm.ls(type=RENDER_RELATED_NODE_TYPES):
                if node.referenceFile() is None and \
                   node.name() not in READ_ONLY_NODE_NAMES:
                    node.rename('%s_%s' % (node.name(), uuid.uuid4().hex))

            # export all root ass files as they are
            for root_node in auxiliary.get_root_nodes():
                for child_node in root_node.getChildren():
                    #print('processing %s' % child_node.name())
                    # check if it is a transform node
                    if not isinstance(child_node, pm.nt.Transform):
                        continue

                    # check if it is an empty node
                    # check the shape
                    node_shape = child_node.getShape()
                    if not node_shape:
                        # check if it has child nodes
                        if len(child_node.getChildren()) == 0:
                            continue
                    elif not isinstance(node_shape, allowed_shapes):
                        continue

                    child_name = child_node.name()

                    pm.select(child_node)
                    output_filename =\
                        '%s.ass' % (
                            child_name.replace(':', '_').replace('|', '_')
                        )

                    output_full_path = \
                        os.path.join(output_path, output_filename)

                    # run the mel command
                    pm.mel.eval(
                        export_command % {
                            'path': output_full_path.replace('\\', '/')
                        }
                    )

                    # 5. generate an aiStandIn node and set the path
                    ass_node = auxiliary.create_arnold_stand_in(
                        path='%s.gz' % output_full_path
                    )
                    ass_tra = ass_node.getParent()

                    #ass_node.setAttr("overrideDisplayType", 2)
                    #ass_node.setAttr("overrideEnabled", 1)

                    # parent the ass node under the child_node so it will move
                    # with the parent node
                    pm.parent(ass_tra, child_node)
                    # rename it to something meaningful
                    ass_tra.rename('%s_ass' % (child_name.split(':')[-1]))

        elif self.is_vegetation_task(task):
            # in vegetation files, we export the ASS files directly from the
            # Base version, also we use the geometry under "pfxPolygons"
            # and parent the resulting Stand-In nodes to the
            # pfxPolygons

            # find the _pfxPolygons node
            pfx_polygons_node = pm.PyNode('kks___vegetation_pfxPolygons')

            for node in pfx_polygons_node.getChildren():
                for child_node in node.getChildren():
                    #print('processing %s' % child_node.name())
                    child_name = child_node.name().split('___')[-1]

                    pm.select(child_node)
                    output_filename =\
                        '%s.ass' % (
                            child_name.replace(':', '_').replace('|', '_')
                        )

                    output_full_path = \
                        os.path.join(output_path, output_filename)

                    # run the mel command
                    pm.mel.eval(
                        export_command % {
                            'path': output_full_path.replace('\\', '/')
                        }
                    )

                    # generate an aiStandIn node and set the path
                    ass_node = auxiliary.create_arnold_stand_in(
                        path='%s.gz' % output_full_path
                    )
                    ass_tra = ass_node.getParent()

                    # parent the ass node under the current node
                    # under pfx_polygons_node
                    pm.parent(ass_tra, node)

                    # delete the child_node
                    pm.delete(child_node)

                    # give it the same name with the original
                    ass_tra.rename('%s' % child_name)

            # clean up other nodes
            pm.delete('kks___vegetation_pfxStrokes')
            pm.delete('kks___vegetation_paintableGeos')

        elif self.is_model_task(task):
            # delete all grandchildren of the root node
            # and save it as it is
            root_nodes = self.get_local_root_nodes()

            for root_node in root_nodes:
                for child_node in root_node.getChildren():
                    pm.delete(child_node.getChildren())

        # There is a bug about StandIns light linking so
        # set the aiStandIn.overrideLightLinking to False
        [node.setAttr('overrideLightLinking', False)
         for node in pm.ls(type='aiStandIn')
         if node.referenceFile() is None]

        # convert all references to ASS
        for ref in pm.listReferences():
            ref.to_repr('ASS')

        # fix an arnold bug
        for node_name in ['initialShadingGroup', 'initialParticleSE']:
            node = pm.PyNode(node_name)
            node.setAttr("ai_surface_shader", (0, 0, 0), type="float3")
            node.setAttr("ai_volume_shader", (0, 0, 0), type="float3")

        # if this is an Exterior/Interior -> Layout -> Hires task flatten it
        if self.is_exterior_or_interior_task(task):
            # and import all of the references
            all_refs = pm.listReferences()
            while len(all_refs) != 0:
                for ref in all_refs:
                    ref.importContents()
                all_refs = pm.listReferences()

        # save the scene as {{original_take}}___ASS
        # use maya
        take_name = '%s%s%s' % (
            self.base_take_name, Representation.repr_separator, 'ASS'
        )
        v = self.get_latest_repr_version(take_name)
        self.maya_env.save_as(v)

        # new scene
        pm.newFile(force=True)
