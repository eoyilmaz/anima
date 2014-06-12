# -*- coding: utf-8 -*-
# Copyright (c) 2012-2014, Anima Istanbul
#
# This module is part of anima-tools and is released under the BSD 2
# License: http://www.opensource.org/licenses/BSD-2-Clause
import os

import pymel.core as pm
from anima.repr import Representation


class RepresentationGenerator(object):
    """Generates different representations of the current scene
    """

    def __init__(self):
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

    def generate_all(self):
        """generates all representations at once
        """
        pass

    def generate_ass(self):
        """generates the ASS representation of the current scene
        """
        export_command = 'arnoldExportAss -f "%(path)s" -s -mask 255 ' \
                         '-lightLinks 1 -compressed -boundingBox ' \
                         '-shadowLinks 1 -cam perspShape;'
        # 1. select top group
        root_transform_nodes = []
        for node in pm.ls(dag=1, transforms=1):
            if node.getParent() is None:
                shape = node.getShape()
                if shape:
                    if shape.type() not in ['camera']:
                        root_transform_nodes.append(node)
                else:
                    root_transform_nodes.append(node)

        if not len(root_transform_nodes):
            raise RuntimeError('No root nodes!!!')

        pm.select(root_transform_nodes)

        # 2. calculate output path
        output_path = os.path.join(self.version.absolute_path, 'Outputs/ASS/')
        output_filename =\
            '%s%s' % (
                os.path.splitext(
                    os.path.basename(
                        self.version.filename
                    )
                )[0],
                '.ass'
            )

        output_full_path = os.path.join(output_path, output_filename)

        # 3. run mel command
        print export_command % {'path': output_full_path.replace('\\', '/')}
        pm.mel.eval(
            export_command % {'path': output_full_path.replace('\\', '/')}
        )

        # 4. clear the scene
        pm.newFile(force=True)

        # 5. generate an aiStandIn node and set the path
        from mtoa import core
        core.createStandIn(path=output_full_path + '.gz')

        # 6. save the scene as {{original_take}}___ASS
        # use maya
        from stalker import Version
        v = Version(
            task=self.version.task,
            take_name='%s%s%s' % (
                self.base_take_name, Representation.repr_separator, 'ASS'
            )
        )
        v.is_published = True
        self.maya_env.save_as(v)

        # 7. reopen the original version
        self.maya_env.open(self.version)

    def generate_bbox(self):
        """generates the BBox representation of the current scene
        """
        pass

    def generate_gpu(self):
        """generates the GPU representation of the current scene
        """
        pass