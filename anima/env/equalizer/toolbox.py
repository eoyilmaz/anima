# -*- coding: utf-8 -*-
"""

import os
import sys
os.environ['STALKER_PATH'] = '/mnt/T/STALKER_CONFIG'

sys.path.append("/home/eoyilmaz/Documents/development/anima/anima")
sys.path.append("/home/eoyilmaz/Documents/development/anima/extra_libraries/py2")
sys.path.append("/home/eoyilmaz/Documents/development/anima/extra_libraries/py2/__extras__")
from anima.env.equalizer import toolbox

toolbox.Toolbox.bake_3d_to_2d()
"""


class Toolbox(object):
    """toolbox for 3DEqualizer
    """

    @classmethod
    def bake_3d_to_2d(cls):
        """bakes the selected points projected 3D position with distortion to the 2D space
        """
        import tde4

        camera_id = tde4.getCurrentCamera()
        pgroup_id = tde4.getCurrentPGroup()

        point_ids = tde4.getPointList(pgroup_id, True)
        calc_range = tde4.getCameraCalculationRange(camera_id)
        for point_id in point_ids:
            for frame in range(calc_range[0], calc_range[1] + 1):
                # tde4.setCurrentFrame(frame)
                point_pos = tde4.calcPointBackProjection2D(pgroup_id, point_id, camera_id, frame, True)
                tde4.setPointPosition2D(pgroup_id, point_id, camera_id, frame, point_pos)
