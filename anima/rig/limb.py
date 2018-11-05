# -*- coding: utf-8 -*-
# Copyright (c) 2012-2018, Anima Istanbul
#
# This module is part of anima-tools and is released under the BSD 2
# License: http://www.opensource.org/licenses/BSD-2-Clause

import pymel.core as pm

from shapes import Shape
from character import Character
from joint import SpineJoints, JointChain
from curve import Curve
from anima.rig.drawNode import DrawNode


class Limb(object):
    def __init__(self, limbName_in):

        # Name of the Limb
        self._limbName = limbName_in

        # MainCtrl of the Limb
        self._mainCtrl = None

        # Creates a network for the Limb
        self._network = Network(limbName_in) # TODO: What is network

        # Character Link
        self._charName = None

    def _validate_charName(self, charName_in):
        """validates the given charName_in"""
        if charName_in == None:
            raise TypeError("%s.name can not be None!" %
                            self.__class__.__name__)
        if not isinstance(charName_in, (Character)):
            raise TypeError("%s.name should be an instance of Character!" %
                            self.__class__.__name__)
        if charName_in == "":
            raise ValueError("%s.name can not be an empty string!" %
                             self.__class__.__name__)
        return charName_in

    def _validate_mainCtrl(self, mainCtrl):
        """validates the given mainCtrl"""
        if mainCtrl != None:
            self.mainCtrl = pm.nt.Transform(mainCtrl)

    def do_spine_ik(self, curve_in):
        print self.curve_in
        print self.name


class FkLimb(object):
    def __init__(self):
        # Name of the FK LIMB
        self._fkLimbName = None

        # FK Controllers
        self._fkControllers = None

        # FK Joints
        self._fkJoints = None

        # FK Utilities
        self._fkUtilities = None

        # FK NODES  : self.fkLimbNodes = Nodes(fkLimbName)
        # Used for network connection
        self.fkLimbNodes = None

    def create_fk_limb(self, name_in, positions, frontAxis=None):

        self._fkLimbName = name_in
        self._fkJoints = JointChain(name_in, positions)
        self._fkJoints.orient_joint_chain(frontAxis=frontAxis)


class IkSpineLimb(object):
    def __init__(self):
        self._limbName = None
        self._joints = None
        self._curve = None
        self._ikHandle = None
        self._effector = None

        self._clusters = []

        self._network = None
        self._scaleMD = None
        self._factors = None

        self._hipCtrl = None
        self._shoulderCtrl = None
        self._COGCtrl = None

        self._stuff = []

    # *************************************************************************
    # IKSPINE BASE SETUP METHODS
    def create_spine(self, name_in, curve_in, frontAxis="z"):
        #self._network = Network(name_in)
        self._limbName = name_in
        # You can change createion method with a Joint Chain Class
        # JointChain(name_in, jointPositions)
        # self.joint.orientChain

        self.joints = SpineJoints(name_in, curve_in)
        self.joints.orient_spine(frontAxis)

        ikSolver = pm.ikHandle(sj=self.joints.startJoint,
                               ee=self.joints.endJoint,
                               tws="linear",
                               cra=True,
                               pcv=False,
                               ns=2,
                               sol="ikSplineSolver",
                               name=(name_in + "_IKSpine"))

        self._ikHandle = pm.rename(ikSolver[0], (name_in + "_IK_Spine"))
        self._effector = pm.rename(ikSolver[0],
                                   (name_in + "_IK_SpineEffector"))
        self._curve = Curve((name_in + "_IKSpineCurve"), ikSolver[2])


    def create_clusters(self):
        for i in range(0, self._curve.numCVs):
            pm.select(self._curve.curveNode.cv[i])
            tempClstr = DrawNode(
                Shape.cluster,
                self._limbName + "IK_SpineCl_#"
            )
            tempClstr.create_axialCor()
            self.clusters.append(tempClstr)
            #self.clusters[i].create_axialCor()


    def make_stretchy(self):
        #check joints
        """


        """
        self._scaleMD = pm.createNode("multiplyDivide",
                                      n=self.limbName + "_scaleMD")
        pm.connectAttr(self.curve.curveInfo.arcLength, self.scaleMD.input1X)
        pm.setAttr(self.scaleMD.input2X, self.curve.arclen)
        pm.setAttr(self.scaleMD.operation, 2)

        for jnt in self.joints.jointChain:
            factor = pm.createNode("multiplyDivide", n="factor_" + jnt)
            pm.connectAttr(self.scaleMD.outputX, factor.input1X)
            pm.setAttr(factor.input2X, (pm.getAttr(jnt.ty)))
            pm.connectAttr(factor.outputX, jnt.ty)


    def create_controllers(self):
        #Check if clusters is not an empty list
        # Hip Ctrl Create

        """


        """
        self._hipCtrl = DrawNode(Shape.ikCtrl, 'hip_ctrl')
        self.hipCtrl.temp_constrain(self.clusters[0].drawnNode)

        self.hipCtrl.create_axialCor()


        #parent Hip Clusters to Hip Control
        pm.parent(self.clusters[0].axialCor, self.clusters[1].axialCor,
                  self.hipCtrl.drawnNode)


        # Shoulder Ctrl Create

        self._shoulderCtrl = DrawNode(Shape.circle, 'shoulder_ctrl')
        self.shoulderCtrl.temp_constrain(
            self.clusters[(len(self.clusters) - 1)].drawnNode)

        self.shoulderCtrl.create_axialCor()


        # COG Ctrl Create

        self._COGCtrl = DrawNode(Shape.cube, 'COG_ctrl')
        self._COGCtrl.temp_constrain(self.hipCtrl.drawnNode)

        self._COGCtrl.create_axialCor()

        #parent Shoulder Clusters to Shoulder Control

        pm.parent(self.clusters[(len(self.clusters) - 1)].axialCor,
                  self.clusters[(len(self.clusters) - 2)].axialCor,
                  self._shoulderCtrl.drawnNode)

        # Create Mid Cluster Control Transforms and Constrains
        mid_cluster = self.clusters[2].drawnNode
        tempCluster_const_1 = DrawNode(Shape.transform,
                                       "C_IK_SpineCl_ConstGrp")

        tempCluster_const_1.temp_constrain(mid_cluster)
        pm.parent(tempCluster_const_1.drawnNode, self.hipCtrl.drawnNode)

        tempCluster_const_2 = DrawNode(Shape.transform,
                                       "C_IK_SpineCl_ConstGrp")
        tempCluster_const_2.temp_constrain(mid_cluster)
        pm.parent(tempCluster_const_2.drawnNode, self.shoulderCtrl.drawnNode)

        tempCluster_const_1.constrain(mid_cluster, targetType='targetObj')
        tempCluster_const_2.constrain(mid_cluster, targetType='targetObj')

        self.stuff = tempCluster_const_1
        self.stuff = tempCluster_const_2

        #if spine has zero joint it calls an unique function
        self.unique_spine_zero_controller()

    def unique_spine_zero_controller(self):
    # Create Root Costrain Jnt Unde Hip cotrol
        # Duplicate zero Jnt

        tempConst = pm.duplicate(self.joints.zeroJoint, po=True,
                                 name=("Const_" + self.joints.zeroJoint ))
        rootConst_jnt = tempConst[0]

        pm.parent(rootConst_jnt, self.hipCtrl.drawnNode)
        pm.pointConstraint(rootConst_jnt, self.joints.zeroJoint)
        pm.orientConstraint(rootConst_jnt, self.joints.zeroJoint)
        pm.setAttr(rootConst_jnt.visibility, 0)
        self._stuff.append(rootConst_jnt)

    def organize_DAG(self):
        pass
    def fk_create(self, numOfFkCtrl = 3):
        fkJointsPos = []
        fkJointsPos.append(self.joints.zeroPos)
        for i in  xrange(numOfFkCtrl, self.joints._numOfJoints - numOfFkCtrl,
                         numOfFkCtrl):

            fkJointsPos.append(self.joints.jointPos[i])
        fkJointsPos.append(self.joints.endPos)
        print fkJointsPos
        fkSetup = FkLimb()
        fkSetup.create_fk_limb("back_FK_", fkJointsPos)

    # *************************************************************************
    # PROPERTIES
    @property
    def spineJoints(self):
        return self._joints

    @spineJoints.setter
    def spineJoints(self, joints_in):
        self._joints = joints_in

    @property
    def curve(self):
        return self._curve

    @property
    def clusters(self):
        return self._clusters

    @clusters.setter
    def clusters(self, node_in):
        self._clusters.append(node_in)


    @property
    def hipCtrl(self):
        return self._hipCtrl

    @hipCtrl.setter
    def hipCtrl(self, name_in):
        if self._hipCtrl is not None:
            pm.rename(self._hipCtrl.drawnNode, name_in)

    @property
    def shoulderCtrl(self):
        return self._shoulderCtrl

    @shoulderCtrl.setter
    def shoulderCtrl(self, name_in):
        if self._shoulderCtrl != None:
            pm.rename(self._shoulderCtrl.drawnNode, name_in)

    @property
    def stuff(self):
        return self._stuff

    @stuff.setter
    def stuff(self, stuff_in):
        self._stuff.append(stuff_in)


    @property
    def limbName(self):
        return self._limbName

    @property
    def scaleMD(self):
        return self._scaleMD



