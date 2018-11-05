# -*- coding: utf-8 -*-
# Copyright (c) 2012-2018, Anima Istanbul
#
# This module is part of anima-tools and is released under the BSD 2
# License: http://www.opensource.org/licenses/BSD-2-Clause

import pymel.core as pm
from anima.rig.drawNode import DrawNode
from shapes import Shape
from curve import Curve


# JOINT CLASS
class Joint(object):
    def __init__(self, jointName_in, position):

        self._jointPos = self._getPosition(position)
        pm.select(cl=1)
        self._jointName = pm.joint(n=(jointName_in + "#"), p=self._jointPos)

    # BASE SETUP METHODS
    def _getPosition(self, position):
        # Checks the type of the Position and Return Position vector
        if isinstance(position, pm.dt.Vector):
            self._jointPos = position
        elif isinstance(position, pm.dt.Point):
            self._jointPos = position
        elif isinstance(position, pm.nt.Transform):
            self._jointPos = pm.getAttr(position.translate)
        elif not isinstance(position, pm.dt.Vector):
            self._jointPos = pm.dt.Vector(0, 0, 0)

        return self._jointPos


    # PROPERTIES
    @property
    # Joint Name Getter - Setter
    def jointName(self):
        return self._jointName

    @jointName.setter
    def jointName(self, name_in):
        self._jointName = pm.rename(self._jointName, name_in)

    @property
    #Joint Position Getter
    def jointPos(self):
        return self._jointPos


# JOINT CHAIN CLASS
class JointChain(object):
    def __init__(self, jointsName, positions):

        """

        :param jointsName:
        :param positions:
        """
        self._jointChain = []
        self._jointsPos = []
        # Creates Joints
        self._createJoints(jointsName, positions)
        self._jointRoot = self.jointChain[0]
        self._numOfJoints = len(self._jointChain)

        self._startJoint = None
        self._endJoint = None

        self._startPos = None
        self._endPos = None


     # BASE SETUP METHODS
    def _createJoints(self, jointsName, positions):
        self._validate_positions(positions)
        for pos in positions:
            tempJnt = Joint(jointsName, pos)
            self._jointChain.append(tempJnt.jointName)
            self._jointsPos.append(tempJnt.jointPos)
        for i in range(1, len(self.jointChain), 1):
            pm.parent(self._jointChain[i], self._jointChain[i - 1])

    def _validate_positions(self, positions):
        if not isinstance(positions, (list)):
            raise TypeError("%s.name should be an instance of List!" %
                            self.__class__.__name__)

    # PROPERTIES
    @property
    def startJoint(self):
        return self._jointChain[0]

    @property
    def endJoint(self):
        return self._jointChain[self.numOfJoints - 1]

    @property
    # Joint Chain Getter
    def jointChain(self):
        return self._jointChain

    @property
    # Positions of the Joints Getter
    def jointPos(self):
        return self._jointsPos

    @property
    def jointRoot(self):
        return self._jointRoot

    @property
    def numOfJoints(self):
        return self._numOfJoints

    @property
    def startPos(self):
        return self._jointsPos[0]

    @property
    def endPos(self):
        return self._jointsPos[self.numOfJoints - 1]


    # ORIENTATION  SET  METHODS
    def orient_joint(self, joint, aimAxis=[1, 0, 0], upAxis=[0, 0, 1],
                     worldUpType="vector",
                     worldUpVector=[0, 1, 0]):

        #joint should be pm.nt.Joint type
        if not isinstance(joint, pm.nt.Joint):
            raise TypeError("%s sholud be an instance of pm.nt.Joint Class"
                            % joint)
        jointUnder = self.jointUnder(joint)
        if jointUnder is None:
            return 0
        temporalGroup = DrawNode(Shape.transform, 'temporalGroup')
        pm.parent(jointUnder, temporalGroup.drawnNode)

        pm.setAttr(joint.jointOrient, (0, 0, 0))

        if worldUpType == "object":
            aimConst = pm.aimConstraint(jointUnder, joint, aimVector=aimAxis,
                                        upVector=upAxis,
                                        worldUpType=worldUpType,
                                        worldUpObject=worldUpVector)
        elif worldUpType == "vector":
            aimConst = pm.aimConstraint(jointUnder, joint, aimVector=aimAxis,
                                        upVector=upAxis,
                                        worldUpType=worldUpType,
                                        worldUpVector=worldUpVector)
        pm.delete(aimConst)
        pm.parent(jointUnder, joint)

        pm.setAttr(joint.jointOrient, (pm.getAttr(joint.rotate)))
        pm.setAttr((joint.rotate), [0, 0, 0])
        pm.delete(temporalGroup.drawnNode)


    def orient_joint_frontAxis(self, joint, aimAxis=[0, 1, 0],
                               upAxis=[0, 0, 1],
                               worldUpType="object",
                               frontAxis="z"):
        #TODO : Validate frontAxis
        # orient_joint Function OverLoading
        # Creates a temporal Trasnform node for WorldUpVector.
        # Calls orient_joint method

        jointUnder = self.jointUnder(joint)
        if jointUnder is None:
            return 0
        moveAxis = [0, 0]
        if frontAxis == "x":
            moveAxis[0] = -1
        elif frontAxis == "z":
            moveAxis[1] = -1

        temporalTrans = DrawNode(Shape.transform, 'temporalTransform')
        temporalTrans.temp_constrain(jointUnder)
        temporalTrans.freeze_transformations()

        temporalTransMove = self.orient_choose_direction(joint, jointUnder,
                                                         frontAxis)
        temporalTrans.move(pm.dt.Vector([moveAxis[0],
                                         (temporalTransMove * 0.001),
                                         moveAxis[1]]))
        worldUpVector = temporalTrans.drawnNode
        self.orient_joint(joint, aimAxis, upAxis, worldUpType, worldUpVector)
        temporalTrans.delete()


    def orient_choose_direction(self, joint, jointUnder, frontAxis):
        #TODO : Validate frontAxis
        if frontAxis == "x":
            frontInt = 0
        elif frontAxis == "z":
            frontInt = 2
        returnVal = 1

        transform_1 = DrawNode(Shape.transform, 'direction1')
        transform_1.temp_constrain(joint)

        transform_2 = DrawNode(Shape.transform, "direction2")
        transform_2.temp_constrain(jointUnder)

        frontTransform = transform_1.transform[frontInt] - \
                         transform_2.transform[frontInt]
        if frontTransform > 0:
            returnVal = -1
        transform_1.delete()
        transform_2.delete()

        return returnVal

    def jointUnder(self, joint):
        jointUnder = pm.listRelatives(joint, c=1, type="joint")
        if not len(jointUnder):
            pm.setAttr(joint.jointOrient, (0, 0, 0))
            return None
        return jointUnder

    def orient_joint_chain(self, startJoint=None, endJoint=None,
                           frontAxis=None):
        #TODO: Validate front axis
        startIndex, endIndex = self.get_start_end_index(startJoint,
                                                            endJoint)
        for j in range(startIndex, (endIndex + 1)):
            if frontAxis is None:
                self.orient_joint(self.jointChain[j])
            else:
                self.orient_joint_frontAxis(self.jointChain[j],
                                            frontAxis=frontAxis)



    def get_start_end_index(self, startJoint=None, endJoint=None):
        # Sets the default values
        if startJoint is None:
            startJoint = self.jointRoot
        if endJoint is None:
            endJoint = self.jointChain[self.numOfJoints - 1]
            #Gets the Index of the Start Joint and End Joint
        startIndex = self.get_index_of_joint(startJoint)
        endIndex = self.get_index_of_joint(endJoint)
        return startIndex, endIndex

    def get_index_of_joint(self, joint_in):
        # Return the index of the joint_in
        for index in range(0, self.numOfJoints):
            if joint_in == self.jointChain[index]:
                return index
        raise TypeError("%s is not a member joint of %s" %
                        (joint_in, self.__class__.__name__))


# SPINE JOINT CLASS
class SpineJoints(JointChain):
    def __init__(self, jointsName, curve, spans=10, horizontalSpine=0):

        """

:param jointsName:
:param curve:
:param spans:
:param horizontalSpine:
"""
        jointsName = jointsName + "_jnt_"
        curveName = jointsName + "baseCrv"
        #Position of the Joints
        self._jointsPos = []

        # Curve Node creation
        self._curve = Curve(curveName, curve)
        self._curve.rebuildCurve(spans)

        self._startJoint = None
        self._endJoint = None
        #get cv positions for to create a joint chain

        self._horizontalSpine = horizontalSpine

        self._frontAxis = None
        self._zeroJoint = None
        self._zeroPos = None

        self._get_curve_points()

        super(SpineJoints, self).__init__(jointsName, self._jointsPos)
        self.set_zero_joint()

    # BASE SETUP METHODS
    def set_zero_joint(self):

        #Removes Zero Joint from Joint Chain
        pm.joint(self.jointChain[0], e=True, zso=True, oj='xyz', sao='xup')
        self.zeroJoint = self.jointChain[0]

        self._zeroPos = pm.dt.Point(pm.getAttr(self._zeroJoint.translate))
        self.jointChain.remove(self.jointChain[0])
        self.jointPos.remove(self.jointPos[0])
        pm.joint(self.jointChain[1], e=True, zso=True, oj='xyz', sao='yup')
        for i in range(1, len(self.jointChain)):
            pm.joint(self.jointChain[i], e=True, zso=True, oj='xyz', sao='yup')
            #sets Start End Num Of Joints again
        self._numOfJoints = len(self._jointChain)
        #Orient Zero Joint
        temporalGroup = DrawNode(Shape.transform, 'temporalGroup')
        pm.parent(self.startJoint, temporalGroup.drawnNode)

        print (pm.getAttr(self.zeroJoint.jointOrient))
        pm.setAttr(self.zeroJoint.jointOrientX, 0)
        pm.parent(self.startJoint, self.zeroJoint)
        temporalGroup.delete()

    def _get_curve_points(self):
        self._jointPos = []

        firstCVPos = self._curve.cvPositions[0]
        zeroCVsPos = pm.dt.Vector(self._curve.cvPositions[0])

        if not self.horizontalSpine:
            zeroCVsPos[1] = zeroCVsPos[1] - (self._curve.arclen / 10)
        else:
            zeroCVsPos[2] = zeroCVsPos[2] - (self._curve.arclen / 10)

        self._jointsPos.append(zeroCVsPos)
        self._jointsPos.append(firstCVPos)

        for i in range(2, (self._curve.numCVs - 2)):
            self._jointsPos.append(self._curve.cvPositions[i])
        lastCVPos = self._curve.cvPositions[self._curve.numCVs - 1]
        self._jointsPos.append(lastCVPos)

    # PROPERTIES
    @property
    def curve(self):
        return self._curve

    @property
    def horizontalSpine(self):
        return self._horizontalSpine

    @horizontalSpine.setter
    def horizontalSpine(self, horizontal_in):
        self._horizontalSpine = horizontal_in

    @property
    def frontAxis(self):
        return self._frontAxis

    @frontAxis.setter
    def frontAxis(self, frontAxis):
        self._frontAxis = frontAxis

    @property
    def zeroJoint(self):
        return self._zeroJoint

    @zeroJoint.setter
    def zeroJoint(self, joint_in):
        self._zeroJoint = pm.nt.Joint(joint_in)

    @property
    def zeroPos(self):
        return self._zeroPos

    # METHODS
    def orient_spine(self, frontAxis):
        self.orient_joint_chain(self.startJoint, self.endJoint, frontAxis)






















