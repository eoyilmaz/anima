# -*- coding: utf-8 -*-
# Copyright (c) 2012-2013, Anima Istanbul
#
# This module is part of oyProjectManager and is released under the BSD 2
# License: http://www.opensource.org/licenses/BSD-2-Clause

import pymel.core as pm
from utilityFuncs import UtilityFuncs as utility

class Joint(object):
    jointInstances = []
    def __init__(self, joints, name, axis = "xyz"):
        self._root = ""
        self._hierarchy = []
        self._orientAxis = axis
        self.symetricJoints = []

        self._setJoints( (self._check_joints(joints)) ,(self._check_name(name)) )

    def __del__(self):
        """deletes the instances and remove from static jointInstances list
        """
        Joint.jointInstances.remove(self._root)
        pm.delete(self._root)

    #****************************************************************************************************#
    #creates and rename the joints
    def _setJoints(self, joints, name):
        self._root = utility.duplicateObject(joints)
        self._renameJoints(name)
        self.orientAxis = self._orientAxis
        Joint.jointInstances.append(self._root)

    #****************************************************************************************************#
    #rename the jointHierarchy and update the root joint variable
    def _renameJoints(self, name):
        self._hierarchy = utility.renameHierarchy((utility.selHierarchy(self._root)), (name))
        self._root = self._hierarchy[0]

    #****************************************************************************************************#


    # Checks the type of the init parameter joints : type should be pm.joint
    def _check_joints(self, joints):
        if not (pm.nodeType(joints) == "joint"):
            raise TypeError("Joint should be a joint node")
        return joints

    # Checks the type of the init parameter charName : type should be Character
    def _check_name(self, name):
        if name is None:
            raise TypeError("name can not be None")
        if not isinstance(name, (str)):
            raise TypeError("name should be an instance of string")
        if name is "":
            raise ValueError("name can not be an empty string")
        return name



    #****************************************************************************************************#
    #return the _hierarchy list
    def hierarchy():
        def fget(self):
            return self._hierarchy
        return locals()
    hierarchy = property( **hierarchy() )


    #****************************************************************************************************#
    #return the root, and change the name of the root and hierarchy
    def root():
        def fget(self):
            return self._root

        def fset(self, name):
            self._name = name
            self._renameJoints(self._name)

        return locals()

    root = property( **root() )



    #****************************************************************************************************#


    #return and change the orientAxis of the joints
    def orientAxis():
        def fget(self):
            return self._orientAxis
        def fset(self, axis):
            #print"orient set"
            self._orientAxis = axis
            pm.makeIdentity(self.root, apply=True, t=1, r=1, s=1)
            pm.joint(self.root, e=1, oj= axis, ch=1)
            #setting the last joint orientation
            pm.joint(self.hierarchy[len(self.hierarchy) - 1 ], e=1, o=[0, 0, 0])
        return locals()
    orientAxis = property( **orientAxis() )

    #****************************************************************************************************#



    #****************************************************************************************************#
    def mirrorJoints(self):
        pass
    def splitJoints(self):
        pass

class FkJoint(Joint):
    def __init__(self, joints, name, axis = "xyz"):
        super(FkJoint, self).__init__(joints, name, axis)

    def ppp(self):
        print self.root



