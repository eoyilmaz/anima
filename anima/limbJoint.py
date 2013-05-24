# -*- coding: utf-8 -*-
# Copyright (c) 2012-2013, Anima Istanbul
#
# This module is part of oyProjectManager and is released under the BSD 2
# License: http://www.opensource.org/licenses/BSD-2-Clause

import pymel.core as pm
from utilityFuncs import UtilityFuncs as utiFuncs

# TODO: use this logging instead of print statements
import logging
from anima import logging_level
logger = logging.getLogger(__name__)
logger.setLevel(logging_level)


class Joint(object):

    def __init__(self, name, joints):
        self._root = ""
        self._hierarchy = []

        self._orientAxis = None
        self._secAxisOrient = None
        self._len = None
        self.symetricJoints = []
        self._preferredAngle = None


        self._setJoints((self._validate_name( name)), (self._check_joints(joints)) )


    def _setJoints(self, name, joints):
        #creates and rename the joints
        self._root = utiFuncs.duplicateObject(joints)
        self._renameJoints(name)
        self._position = []
        print (pm.listRelatives(self._root, p = 1))
        if pm.listRelatives(self._root, p = 1):
            pm.parent(self._root, w = 1)
            logger.debug("dsdasd")
        else :
            logger.debug("aesd")



        #Sets Rotation value
        self._rotation = (pm.xform(self.root, q = 1, ws = 1, ro = 1))
        for jnt in self._hierarchy:
            pos = pm.datatypes.Vector(pm.xform(jnt, q = 1, ws = 1, t = 1))
            self._position.append(pos)
        self._len = self.len
        pm.joint(self.hierarchy[len(self.hierarchy) - 1 ], e=1, o=[0, 0, 0])



    def _renameJoints(self, name):
        #rename the jointHierarchy and update the root joint variable
        self._hierarchy = utiFuncs.renameHierarchy((utiFuncs.selHierarchy(self._root)), (name))
        self._root = self._hierarchy[0]




    def _check_joints(self, joints):
        # Checks the type of the init parameter joints : type should be pm.joint
        if not (pm.nodeType(joints) == "joint"):
            raise TypeError("%s class root should be a joint node" %
                            self.__class__.__name__)
        return joints



    def _validate_name(self, name_in):
        # TODO: Check the type of the initialized parameter charName :
        # TODO: type should be Character
        """validates the given name value"""

        if name_in == None:
            raise TypeError("%s.name can not be None!" %
                            self.__class__.__name__)
        if not isinstance(name_in, (str)):
            raise TypeError("%s.name should be an instance of Character!" %
                            self.__class__.__name__)
        if name_in == "":
            raise ValueError("%s.name can not be an empty string!" %
                             self.__class__.__name__)
        return name_in


    @property
    #return the _hierarchy list
    def hierarchy(self):
        return self._hierarchy

    @property
    #return the joints position
    def position(self):
        return self._position

    @property
    def rotation(self):
        return self._rotation

    @property
    def len(self):
        return len(self.hierarchy) - 1


    @property
    #return the root, and change the name of the root and hierarchy
    def root(self):
        return self._root
    @root.setter
    def root(self, name_in):
        self._root = name_in
        self._renameJoints(self._root)

    @property
    def startPosition(self):
        return self.position[0]
    @property
    def endPosition(self):
        return self.position[self.len]

    @property
    #return and change the orientAxis of the joints
    def orientAxis(self):
        return self._orientAxis, self._secAxisOrient
    @orientAxis.setter
    def orientAxis(self, axis_in = "xyz", secOrientAxis_in = "yup"):
        self._orientAxis = axis_in
        pm.makeIdentity(self.root, apply=True, t=1, r=1, s=1)
        for jnt in self.len:
            pm.joint(self.root, e=1, oj= axis_in, sao = secOrientAxis_in)
        #sets the last joint orientation
        #pm.joint(self.hierarchy[len(self.hierarchy) - 1 ], e=1, o=[0, 0, 0])


    def mirrorJoints(self):
        pass
    def splitJoints(self):
        pass


class FkJoint(Joint):
    def __init__(self, name, joint):
        name += "_FK_jnt"
        super(FkJoint, self).__init__(name, joint)
        pm.makeIdentity( self.root, apply=True, rotate=True )

class IkJoint(Joint):
    """
    IKJoints creates joints for IKsetup and IKSplineSetup
    self.hierarchy is different from the base Joint class

    """
    def __init__(self, name, startJoint, endJoint):
        name += "_IK_jnt"
        endIndex =  (self._validate_endJoint(startJoint, endJoint))
        super(IkJoint, self).__init__(name, startJoint)
        self._endJoint = self.hierarchy[endIndex]
        tempHierarchy = utiFuncs.selHierarchy(self._endJoint)
        for jnt in range(1, len(tempHierarchy),1):
            self.hierarchy.remove(tempHierarchy[jnt])


    def _validate_endJoint(self, startJoint, endJoint):
        tempHierarchy = utiFuncs.selHierarchy(startJoint)
        for jnt in tempHierarchy:
            if jnt == endJoint:
                return tempHierarchy.index(jnt)


    @property
    def endJoint(self):
        return self._endJoint
    @endJoint.setter
    def endJoint(self, joint_in):
        self._endJoint = joint_in


class ControlJoint(Joint):
    """ControlJoints creates standAlone joints
    _setJoints will overridden to create a single hierarchy
    """
    def __init__(self, name, joint,  position):
        name += "_jnt"
        self._position = position
        super(ControlJoint, self).__init__(name, joint)


    def _setJoints(self, name, joints):
        #ovverridden method to create StandAlone joints
        #creates and rename the joints

        """

        :param joints:
        :param name:
        """
        self._hierarchy = pm.duplicate(joints, po=1)

        self._hierarchy = pm.rename(self._hierarchy[0], name)
        self.root = self._hierarchy
        pm.xform(self.root, ws = 1, t = self._position)
        self._rotation = (pm.xform(self.root, q = 1, ws = 1, ro = 1))

        if  len((pm.listRelatives(self.root, p= True))):
            pm.parent(self.root, w = 1)









