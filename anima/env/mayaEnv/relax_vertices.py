# -*- coding: utf-8 -*-
# Copyright (c) 2012-2015, Anima Istanbul
#
# This module is part of anima-tools and is released under the BSD 2
# License: http://www.opensource.org/licenses/BSD-2-Clause
"""Relax Vertices by Erkan Ozgur Yilmaz

Relaxes vertices without shrinking/expanding the geometry.

Version History
---------------
v0.1.1
- script works with all kind of components

v0.1.0
- initial working version
"""
import pymel.core as pm


__version__ = "0.1.1"


def relax():
    # check the selection
    selection = pm.ls(sl=1)
    if not selection:
        return

    # convert the selection to vertices
    verts = pm.ls(pm.polyListComponentConversion(tv=1))

    if not verts:
        return

    shape = verts[0].node()

    # duplicate the geometry
    dup = shape.duplicate()[0]
    dup_shape = dup.getShape()

    # now relax the selected vertices of the original shape
    pm.polyAverageVertex(verts, i=1, ch=0)

    # now transfer point positions using transferAttributes
    ta_node = pm.transferAttributes(
        dup,
        verts,
        transferPositions=True,
        transferNormals=False,
        transferUVs=False,
        transferColors=False,
        sampleSpace=0,
        searchMethod=0,
        flipUVs=False,
        colorBorders=1,
    )
    # delete history
    pm.delete(shape, ch=1)

    # delete the duplicate surface
    pm.delete(dup)

    # reselect selection
    pm.select(selection)

