# -*- coding: utf-8 -*-
# Copyright (c) 2012-2014, Anima Istanbul
#
# This module is part of anima-tools and is released under the BSD 2
# License: http://www.opensource.org/licenses/BSD-2-Clause
import os

import pymel.core as pm
from stalker import LocalSession

from anima.repr import Representation
from anima.env.mayaEnv import auxiliary


class RepresentationGenerator(object):
    """Generates different representations of the current scene
    """

    def __init__(self):
        local_session = LocalSession()
        self.logged_in_user = local_session.logged_in_user

        if not self.logged_in_user:
            raise RuntimeError('Please login first!')

        from anima.env.mayaEnv import Maya
        self.maya_env = Maya()
        v = self.maya_env.get_current_version()
        if not v:
            raise RuntimeError(
                'Please save the current scene as a valid Stalker version '
                'first'
            )

        r = Representation(version=v)

        self.base_take_name = r.get_base_take_name(v)

        if not r.is_base():
            raise RuntimeError(
                'This is not a Base take for this representation series, '
                'please open the base (%s) take!!!' % r.get_base_take_name(v)
            )

        self.version = v

    @classmethod
    def get_local_root_nodes(cls):
        """returns the root nodes that are not referenced
        """
        return [node for node in auxiliary.get_root_nodes()
                if node.referenceFile() is None]

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

        task = self.version.task

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

        # save the scene as {{original_take}}___BBOX
        # use maya
        from stalker import Version
        v = Version(
            created_by=self.logged_in_user,
            task=self.version.task,
            take_name='%s%s%s' % (
                self.base_take_name, Representation.repr_separator, 'BBOX'
            )
        )
        v.is_published = True
        self.maya_env.save_as(v)

        # reopen the original version
        self.maya_env.open(self.version)

    def generate_proxy(self):
        """generates the Proxy representation of the current scene
        """
        pass

    def generate_gpu(self):
        """generates the GPU representation of the current scene
        """
        # load necessary plugins
        pm.loadPlugin('gpuCache')
        pm.loadPlugin('AbcExport')
        pm.loadPlugin('AbcImport')

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
                        child_shape_name = child_node.name()

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

        # 6. save the scene as {{original_take}}___GPU
        # use maya
        from stalker import Version
        v = Version(
            created_by=self.logged_in_user,
            task=self.version.task,
            take_name='%s%s%s' % (
                self.base_take_name, Representation.repr_separator, 'GPU'
            )
        )
        v.is_published = True
        self.maya_env.save_as(v)

        # 7. reopen the original version
        self.maya_env.open(self.version)

    def generate_ass(self):
        """generates the ASS representation of the current scene

        For Model Tasks the ASS is generated over the LookDev Task because it
        is not possible to assign a material to an object inside an ASS file.
        """
        # before doing anything, check if this is a look dev task
        # and export the objects from the referenced files with their current
        # shadings, then replace all of the references to ASS repr and than
        # add Stand-in nodes and parent them under the referenced models

        task = self.version.task

        export_command = 'arnoldExportAss -f "%(path)s" -s -mask 255 ' \
                         '-lightLinks 1 -compressed -boundingBox ' \
                         '-shadowLinks 1 -cam perspShape;'

        # calculate output path
        output_path = os.path.join(self.version.absolute_path, 'Outputs/ass/')

        allowed_shapes = (
            pm.nt.Mesh,
            pm.nt.NurbsCurve,
            pm.nt.NurbsSurface
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

            # export all root ass files as they are
            for root_node in auxiliary.get_root_nodes():
                for child_node in root_node.getChildren():
                    print('processing %s' % child_node.name())
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
                    print('processing %s' % child_node.name())
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

        # convert all references to ASS
        for ref in pm.listReferences():
            ref.to_repr('ASS')

        # fix an arnold bug
        for node_name in ['initialShadingGroup', 'initialParticleSE']:
            node = pm.PyNode(node_name)
            node.setAttr("ai_surface_shader", (0, 0, 0), type="float3")
            node.setAttr("ai_volume_shader", (0, 0, 0), type="float3")

        # save the scene as {{original_take}}___ASS
        # use maya
        from stalker import Version
        v = Version(
            created_by=self.logged_in_user,
            task=self.version.task,
            take_name='%s%s%s' % (
                self.base_take_name, Representation.repr_separator, 'ASS'
            )
        )
        v.is_published = True
        self.maya_env.save_as(v)

        # reopen the original version
        self.maya_env.open(self.version)
