# -*- coding: utf-8 -*-
# Copyright (c) 2012-2015, Anima Istanbul
#
# This module is part of anima-tools and is released under the BSD 2
# License: http://www.opensource.org/licenses/BSD-2-Clause

from pymel.core import curve, spaceLocator, select
from pymel.core.nodetypes import ClusterHandle, Cluster
from pymel.core.runtime import ClusterCurve


class BarnDoor(object):
    """Previews barn door
    """
    def __init__(self):
        self.top = None
        self.bottom = None
        self.left = None
        self.right = None


class BarnDoorFlip(object):
    """One flip of barn door
    """
    def __init__(self):
        self.corner1 = 0
        self.corner2 = 0
        self.edge = 0


class BarnDoorPreviewLine(object):
    """Previews the barn door
    """

    def __init__(self):
        self.curve = None
        self.corner1_locator = None
        self.corner2_locator = None
        self.cluster1 = None
        self.cluster2 = None
        self.cluster_handle1 = None
        self.cluster_handle2 = None

    def build(self):
        """builds it self
        """
        self.curve = curve(d=1, p=[(1, 0, 0), (-1, 0, 0)], k=(0, 1))
        self.corner1_locator = spaceLocator()
        self.corner2_locator = spaceLocator()
        select(self.curve)
        ClusterCurve()

        # try to find the clusterHandles
        curve_shape = curve.getShape()
        clusters = []
        handles = []
        for node in curve_shape.listHistroy():
            if isinstance(node, ClusterHandle):
                handles.append(node)
            elif isinstance(node, Cluster):
                clusters.append(node)

        self.cluster1 = clusters[0]
        self.cluster2 = clusters[0]

        self.cluster_handle1 = handles[0]
        self.cluster_handle2 = handles[1]

        # set clusters to absolute
        self.cluster1.setAttr('relative', 0)
        self.cluster2.setAttr('relative', 0)






