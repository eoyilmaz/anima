#import pymel.core as pm
#
#
# class Nodes(object):
#     def __init__(self, name, id):
#
#         self.name = name
#         self._controllers = []
#         self._nodes = []
#         self._joints = []
#         self._id = id
#
#     def deleteNodes(self):
#         del self.controllers
#         del self.joints
#         del self.nodes
#         print ("ddddddddd")
#
#
#
#     @property
#     def id(self):
#         return self._id
#
#
#
#     @property
#     def controllers(self):
#         return self._controllers
#     @controllers.setter
#     def controllers(self, object_in):
#         self._controllers.append(object_in)
#     @controllers.deleter
#     def controllers(self):
#         objects = pm.ls()
#         for obj in objects :
#             for ctrl in self.controllers:
#                 if (obj == ctrl):
#                     pm.delete(ctrl)
#
#         del self.controllers [:]
#
#
#
#
#     @property
#     def joints(self):
#         return self._joints
#     @joints.setter
#     def joints(self, object_in):
#         self._joints.append(object_in)
#     @joints.deleter
#     def joints(self):
#         objects = pm.ls()
#         for obj in objects :
#             for jnt in self.joints:
#                 if (obj == jnt):
#                     pm.delete(jnt)
#
#         del self.joints [:]
#
#
#     @property
#     def nodes(self):
#         return self._nodes
#     @nodes.setter
#     def nodes(self, object_in):
#         self._nodes.append(object_in)
#     @nodes.deleter
#     def nodes(self):
#         objects = pm.ls()
#         for obj in objects :
#             for nodes in self.nodes:
#                 if (obj == nodes):
#                     pm.delete(nodes)
#
#         del self.nodes [:]




class Ndict(dict):
    def __getattr__(self, attr):
        return self.get(attr, None)
    __setattr__= dict.__setitem__
    __delattr__= dict.__delitem__
    def __iadd__(self, other):
        self.update(other)
        return self