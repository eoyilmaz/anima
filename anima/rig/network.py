# -*- coding: utf-8 -*-
# Copyright (c) 2012-2018, Anima Istanbul
#
# This module is part of anima-tools and is released under the BSD 2
# License: http://www.opensource.org/licenses/BSD-2-Clause

import pymel.core as pm

class Network(object):
    def __init__(self, name):
        self._name = name
        self._connections = []

        self._createNetwork()

    def __del__(self):
        pass


    def _createNetwork(self):
        """creates a networkNode. This node holds all the limb nodes
        """
        #creates a networkNode. This node holds all the maya nodes
        self._name = self._name + "_Network"
        pm.createNode("network", n= self.name)



    def attach(self, object):
        #it connects the given object to the network and return an id number
        # for the object
        #all_cons = pm.listConnections(self.name)
        if not object in self.connections:
            mayaCon = object + ('.message')
            networkId = len(self.connections)
            tempAttr = '%s[%s]' % ("affectedBy", networkId)
            networkCon = self.name + "." + tempAttr
            pm.connectAttr(mayaCon, networkCon)
            self.connections.append(object)


    def attachList(self, objectList):
        for obj in objectList :
            self.attach(obj)

    def remove(self, object):
        #it removes the given object from a network
        pass
    def select(self):
        pass


    @property
    # returns and sets the _zeroGrp value
    def name(self):
        return self._name
    @name.setter
    def name(self, name_in):
        self._name = pm.rename(self._name, name_in)



    @property
    #returns connections
    def connections(self):
        return self._connections





