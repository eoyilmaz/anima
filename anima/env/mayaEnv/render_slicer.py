# -*- coding: utf-8 -*-
# Copyright (c) 2012-2015, Anima Istanbul
#
# This module is part of anima-tools and is released under the BSD 2
# License: http://www.opensource.org/licenses/BSD-2-Clause

import pymel.core as pm


class RenderSlicer(object):
    """A tool to help slice single frame renders in to many little parts which
    will help it to be rendered in small parts in a render farm.
    """

    def __init__(self):
        pass

    def do_slice(self):
        cam = pm.ls(sl=1)[0]
        camShape = cam.getShape()

        slices_per_edge = 5

        # set render resolution
        dRes = pm.PyNode("defaultResolution")
        h_res = dRes.width.get()
        v_res = dRes.height.get()

        dRes.width.set(h_res / float(slices_per_edge))
        dRes.height.set(v_res / float(slices_per_edge))

        # use h_aperture to calculate v_aperture
        h_aperture = camShape.getAttr('horizontalFilmAperture')

        # recalculate the other aperture
        camShape.setAttr('verticalFilmAperture', h_aperture * v_res / h_res)

        v_aperture = camShape.getAttr('verticalFilmAperture')

        camShape.setAttr('zoom', 1.0/float(slices_per_edge))

        t = 0
        for i in range(slices_per_edge):
            v_pan = v_aperture / (2.0 * slices_per_edge) * (1 + 2 * i - slices_per_edge)
            for j in range(slices_per_edge):
                h_pan = h_aperture / (2.0 * slices_per_edge) * (1 + 2 * j - slices_per_edge)
                pm.currentTime(t)
                pm.currentTime()
                pm.setKeyframe(camShape, at='horizontalPan', v=h_pan)
                pm.setKeyframe(camShape, at='verticalPan', v=v_pan)
                t += 1


class UI(object):
    """The UI for the slicer
    """
    pass
