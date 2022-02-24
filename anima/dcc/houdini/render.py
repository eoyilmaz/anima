# -*- coding: utf-8 -*-

import hou


class RenderSlicer(object):
    """A tool to help slice single frame renders in to many little parts which
    will help it to be rendered in small parts in a render farm.
    """

    def __init__(self, camera=None):
        self._camera = None
        self.camera = camera

    @classmethod
    def slice(cls, camera, slices_in_x, slices_in_y):
        """slices all renderable cameras
        """
        # set render resolution
        # self.unslice_scene()
        # self.is_sliced = True
        # self._store_data()

        sx = slices_in_x
        sy = slices_in_y

        # set render resolution
        # use the camera for that

        h_res = camera.evalParm("resx")
        v_res = camera.evalParm("resy")

        # this system only works when the
        camera.setParms({
            "resx": int(h_res / float(sx)),
            "resy": int(v_res / float(sy)),
            "aspect": 1
        })

        camera.setParms({
            'winsizex': 1.0/float(sx),
            'winsizey': 1.0/float(sx),
        })

        t = 0
        for i in range(sy):
            v_pan = 1.0 / (2.0 * sy) * (1 + 2 * i - sy)
            for j in range(sx):
                h_pan = 1.0 / (2.0 * sx) * (1 + 2 * j - sx)

                winx_parm = camera.parm("winx")
                winy_parm = camera.parm("winy")

                keyframe = hou.Keyframe()
                keyframe.setFrame(t)  # or myKey.setTime()
                keyframe.setValue(h_pan)
                winx_parm.setKeyframe(keyframe)

                keyframe = hou.Keyframe()
                keyframe.setFrame(t)  # or myKey.setTime()
                keyframe.setValue(v_pan)
                winy_parm.setKeyframe(keyframe)

                t += 1
