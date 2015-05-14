# -*- coding: utf-8 -*-
# Copyright (c) 2012-2015, Anima Istanbul
#
# This module is part of anima-tools and is released under the BSD 2
# License: http://www.opensource.org/licenses/BSD-2-Clause

import pymel.core as pm
from network import Network


class Nodes(object):
    def __init__(self, nodesName_in):

        self.nodesName = nodesName_in
        self._controllers = []
        self._utilities = []
        self._joints = []
        self._curves = []

        self.network = Network(self.nodesName)

    def deleteNodes(self):
        pm.delete(self.network.nodesName)
        del self.controllers
        del self.joints
        del self.utilities

        del self

    @property
    def controllers(self):
        return self._controllers

    @controllers.setter
    def controllers(self, object_in):
        self.appendObject(self._controllers, object_in)

    @controllers.deleter
    def controllers(self):
        self.deleter(self.controllers)


    @property
    def joints(self):
        return self._joints

    @joints.setter
    def joints(self, object_in):
        self.appendObject(self._joints, object_in)

    @joints.deleter
    def joints(self):
        self.deleter(self.joints)


    @property
    def utilities(self):
        return self._utilities

    @utilities.setter
    def utilities(self, object_in):
        self.appendObject(self._utilities, object_in)

    @utilities.deleter
    def utilities(self):
        self.deleter(self.utilities)


    def appendObject(self, nodeType, object_in):
        #appends the given objects to the node Network
        if isinstance(object_in, (list)):
            for obj in object_in:
                if isinstance(obj, (list)):
                    for ob in obj:
                        self.append_to(nodeType, ob)
                else:
                    self.append_to(nodeType, obj)
        else:
            self.append_to(nodeType, object_in)


    def checkMembers(self, nodeType, object_in):
        if nodeType == object_in:
            return False
        return True

    def append_to(self, nodeType, object_in):
        if self.checkMembers(nodeType, object_in):
            nodeType.append(object_in)
            self.network.attach(object_in)

    def deleter(self, nodeList):
        objects = pm.ls()
        for obj in objects:
            for nodes in nodeList:
                if obj == nodes:
                    pm.delete(nodes)

        del nodeList[:]
