
# -*- coding: utf-8 -*-
from _New_drawNode import DrawNode
from shapes import Shape

class Controllers(object):
    def __init__(self, drawer, name_in):
        self._ctrl= None

        self._constSources = None
        self._constTargets = None
        self._create()

    def _create(self, drawer, args):
        # Draw the Node
        self._ctrl = DrawNode(drawer, name_in)

    # def point_const(self, node, maintainOffset=0):
    #     self._controller.point_const(node, maintainOffset)
    # def del_point_const(self):
    #     self._controller.del_point_const()
    # def temp_point_const(self, node, maintainOffset=0):
    #     self._controller.temp_point_const(node, maintainOffset)
    #
    # def orient_const(self, node, maintainOffset=0):
    #     self._controller.orient_const(node, maintainOffset)
    # def del_orient_const(self):
    #     self._controller.del_orient_const()
    # def temp_orient_const(self):
    #     self._controller.del_orient_const()
    #
    # def parent_const(self, node, maintainOffset=0):
    #     self._controller.parent_const(node, maintainOff)
    # def del_parent_const(self):
    #     self._controller.del_parent_const()
    # def temp_parent_const(self, node, maintainOffset=0):
    #     self._controller.temp_parent_const(node, maintainOff)

    @property
    def ctrl(self):
        return self._ctrl

    @property
    def pointConstSources(self):
        return self._ctrl.pointConst


class SpineControllers(Controllers):
    def __init__(self):
        self._hipCtrl = None
        self._shoulderCtrl = None
        self._COGCtrl = None


    def _create_hipCtrl(self, constObj,
                        targetConstObj = None,
                        parentObj = None,
                        targetParentObj = None,
                        constMethod, ):
        self._shoulderCtrl = DrawNode(Shape.circle, 'shoulder_ctrl')
        self.shoulderCtrl.temp_point_const(constObj)
        self.shoulderCtrl.create_axialCor()














