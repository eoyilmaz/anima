# -*- coding: utf-8 -*-
# Copyright (c) 2012-2018, Anima Istanbul
#
# This module is part of anima-tools and is released under the BSD 2
# License: http://www.opensource.org/licenses/BSD-2-Clause

from drawNode import DrawNode
from shapes import Shape


class Controllers(object):
    def __init__(self, drawer, name_in):
        self._ctrl = None

        self._inPoint  = None
        self._outPoint = None

        self._inOrient  = None
        self._outOrient = None

        self._inParent  = None
        self._outParent = None


    def _create(self, drawer, args):
        # Draw the Node
        self._ctrl = DrawNode(drawer, args)


    @property
    def ctrl(self):
        return self._ctrl

    @property
    def inPoint(self):
        return self._inPoint
    @inPoint.setter
    def inPoint(self, node_in):
        self._inPoint = self.po

class SpineControllers(Controllers):
    def __init__(self):
        self._hipCtrl = None
        self._shoulderCtrl = None
        self._COGCtrl = None

class FkControllers(Controllers):
    def __init__(self, numOfCtrls = 1):
        self._controllers = []



class Test(object):
    def attributes(self):

        pass












