# -*- coding: utf-8 -*-
# Copyright (c) 2012-2018, Anima Istanbul
#
# This module is part of anima-tools and is released under the BSD 2
# License: http://www.opensource.org/licenses/BSD-2-Clause

import pymel.core as pm
class Curve(object):
    def __init__(self, name_in, curve):

        self._curveNode = pm.nt.Transform(pm.rename(curve, name_in))

        self._curveInfo = self._create_curveInfo()

        self._degree = None
        self._spans = None
        self._arcLen = None
        self._numCVs = None

        self._cvPositions = []
        for j in range (0, self.numCVs):
            self._cvPositions.append(pm.pointPosition(self.curveNode.cv[j], w = 1))

    @property
    # Curve Node Getter
    def curveNode(self):
        return self._curveNode


    @property
    # Curve Degree : self._degree Setter - Getter
    def degree(self):
        self._degree = pm.getAttr(self.curveNode.degree)
        return self._degree
    @degree.setter
    def degree(self, degree):
        self._degree = degree


    @property
    # Curve Spans : self._spans Setter - Getter
    def spans(self):
        self._spans =  pm.getAttr(self.curveNode.spans)
        return self._spans
    @spans.setter
    def spans(self, span):
        self._spans = span


    @property
    # Number of CVs : self._numCvs Setter - Getter
    def numCVs(self):
        self._numCVs = self.degree + self.spans
        return self._numCVs


    @property
    # CV Positions : Gets the positions of cvs
    def cvPositions(self):

        return self._cvPositions


    @property
    # CurveInfo Getter - Setter
    def curveInfo(self):
        return self._curveInfo
    @curveInfo.setter
    def curveInfo(self, infoNode):
        self._curveInfo = infoNode
        pm.connectAttr(self.curveNode.worldSpace, infoNode.inputCurve)



    @property
    # ArcLength of the Curve Getter
    def arclen(self):
        self._arcLen = pm.getAttr(self.curveInfo.arcLength)
        return self._arcLen



    def rebuildCurve(self, spans):
        # Rebuild the curveNode
        pm.rebuildCurve(self.curveNode, rpo = 1, rt = 0, end = 1, kr = 0, kcp = 0,
                        kep = 1, kt = 0, s = spans, d = 3, tol = 0.01)
        del self._cvPositions[:]

        for j in range (0, self.numCVs):
            self._cvPositions.append(pm.pointPosition(self.curveNode.cv[j], w = 1))

    def _create_curveInfo(self):
        #create a new CurveInfo Node
        self._curveInfo = pm.createNode("curveInfo", n= self._curveNode +
                                                        "_curveInfo")
        pm.connectAttr(self._curveNode.worldSpace, self._curveInfo.inputCurve)
        return self._curveInfo
