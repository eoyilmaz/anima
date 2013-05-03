__author__ = 'Eda'
import pymel.core as pm
from network import Network

class UtilityNodes(object):
    def __init__(self, name):
        self.name = name
        self.outputConnects = []
        self.inputConnections = []
        self.operation = None

    def connectOutput(self):
        pass
    def connectInput(self):
        pass


class Nodes(object):
    def __init__(self, name):

        self.name = name
        self._controllers = []
        self._nodes = []
        self._joints = []
        self._curves = []
        self.network = Network(self.name)

    def deleteNodes(self):
        pm.delete(self.network.name)
        del self.controllers
        del self.joints
        del self.nodes

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
    def nodes(self):
        return self._nodes
    @nodes.setter
    def nodes(self, object_in):
        self.appendObject(self._nodes, object_in)

    @nodes.deleter
    def nodes(self):
        self.deleter(self.nodes)



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
        if (nodeType == object_in):
            return False
        return True

    def append_to(self, nodeType, object_in):
        if self.checkMembers(nodeType, object_in):
            nodeType.append(object_in)
            self.network.attach(object_in)

    def deleter(self, nodeList):
        objects = pm.ls()
        for obj in objects :
            for nodes in nodeList:
                if (obj == nodes):
                    pm.delete(nodes)

        del nodeList [:]
