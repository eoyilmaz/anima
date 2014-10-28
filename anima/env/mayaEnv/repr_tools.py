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

    def generate_all(self):
        """generates all representations at once
        """
        self.generate_bbox()
        self.generate_proxy()
        self.generate_gpu()

        # do not generate ASS for model scenes
        type_ = self.version.task.type
        if type_:
            if type_.name.lower() not in ['model']:
                self.generate_ass()
        else:
            self.generate_ass()

    def generate_bbox(self):
        """generates the BBox representation of the current scene
        """
        # replace all root references with their BBOX representation
        for ref in pm.listReferences():
            ref.to_repr('BBOX')

        # find all non referenced root nodes
        root_nodes = self.get_local_root_nodes()

        if len(root_nodes):
            all_children = []
            for root_node in root_nodes:
                for child in root_node.getChildren():
                    all_children.append(child)

            bboxes = auxiliary.replace_with_bbox(all_children)

            # correct bbox uvs
            pm.polyEditUV(
                pm.polyListComponentConversion(bboxes, tuv=1),
                su=0.95,
                sv=0.95,
                pu=0.5,
                pv=0.5
            )

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

        # 7. reopen the original version
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

            for root_node in root_nodes:
                # export each child of each root as separate nodes
                for child_node in root_node.getChildren():
                    child_name = child_node.name()
                    child_full_path = \
                        child_node.fullPath()[1:].replace('|', '_')
                    output_filename =\
                        '%s' % (
                            child_full_path
                        )

                    # check if file exists
                    pm.mel.eval(
                        gpu_command % {
                            'start_frame': start_frame,
                            'end_frame': end_frame,
                            'node': child_node.fullPath(),
                            'path': output_path,
                            'filename': output_filename
                        }
                    )

                    # delete the child and add a GPU node instead
                    pm.delete(child_node)
                    gpu_node = pm.createNode('gpuCache')
                    gpu_node_tra = gpu_node.getParent()

                    pm.parent(gpu_node_tra, root_node)
                    gpu_node_tra.rename(child_name)

                    cache_file_full_path = \
                        os.path\
                        .join(output_path, '%s.abc' % output_filename)\
                        .replace('\\', '/')

                    gpu_node.setAttr(
                        'cacheFileName',
                        cache_file_full_path,
                        type="string"
                    )

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
        """
        # convert all references to ASS
        for ref in pm.listReferences():
            # check if this is a Model reference
            v = ref.version
            type_ = v.task.type
            if type_ and type_.name.lower() in ['model']:
                # import the contents of this reference
                ref.importContents()
            else:
                ref.to_repr('ASS')

        # 1. select top group
        root_nodes = self.get_local_root_nodes()

        export_command = 'arnoldExportAss -f "%(path)s" -s -mask 255 ' \
                         '-lightLinks 1 -compressed -boundingBox ' \
                         '-shadowLinks 1 -cam perspShape;'

        # 2. calculate output path
        output_path = os.path.join(self.version.absolute_path, 'Outputs/ASS/')

        # 2a. go over each child node
        for root_node in root_nodes:
            for child_node in root_node.getChildren():
                child_name = child_node.name()

                pm.select(child_node)
                output_filename =\
                    '%s.ass' % (
                        child_name.replace(':', '_')
                    )

                output_full_path = os.path.join(output_path, output_filename)

                # 3. run mel command
                print(
                    export_command % {
                        'path': output_full_path.replace('\\', '/')
                    }
                )

                pm.mel.eval(
                    export_command % {
                        'path': output_full_path.replace('\\', '/')
                    }
                )

                # 5. generate an aiStandIn node and set the path
                ass_node = auxiliary.create_arnold_stand_in(
                    path=output_full_path + '.gz'
                )
                ass_tra = ass_node.getParent()

                #ass_node.setAttr("overrideDisplayType", 2)
                #ass_node.setAttr("overrideEnabled", 1)

                # delete the original object and replace it with the ass node
                pm.delete(child_node)

                pm.parent(ass_tra, root_node)
                ass_tra.rename(child_name)

        # 6. save the scene as {{original_take}}___ASS
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

        # 7. reopen the original version
        self.maya_env.open(self.version)
