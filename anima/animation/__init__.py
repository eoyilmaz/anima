# -*- coding: utf-8 -*-
# Copyright (c) 2012-2014, Anima Istanbul
#
# This module is part of anima-tools and is released under the BSD 2
# License: http://www.opensource.org/licenses/BSD-2-Clause

import os
import pymel.core


def create_shot_playblasts(handle=10, showOrnaments=True):
    """creates the selected shot playblasts
    """
    shots = pymel.core.ls(sl=1, type=pymel.core.nt.Shot)
    #active_panel = pymel.core.playblast(activeEditor=1)

    path_template = os.path.join(
        pymel.core.workspace.name,
        'Outputs/Playblast/AllShots/'
    ).replace('\\', '/')

    filename_template = '%(scene)s_%(shot)s.mov'

    # template vars
    scene_name = os.path.basename(pymel.core.env.sceneName()).split('.')[0]

    for shot in shots:
        shot_name = shot.name()
        start_frame = shot.startFrame.get() - handle
        end_frame = shot.endFrame.get() + handle
        width = shot.wResolution.get()
        height = shot.hResolution.get()

        rendered_path = path_template % {}
        rendered_filename = filename_template % {
            'shot': shot_name,
            'scene': scene_name
        }

        movie_full_path = os.path.join(
            rendered_path,
            rendered_filename
        ).replace('\\', '/')

        pymel.core.playblast(
            fmt="qt",
            startTime=start_frame,
            endTime=end_frame,
            sequenceTime=1,
            forceOverwrite=1,
            filename=movie_full_path,
            clearCache=True,
            showOrnaments=showOrnaments,
            percent=100,
            wh=[width, height],
            offScreen=True,
            viewer=0,
            useTraxSounds=True,
            compression="PNG",
            quality=70
        )
