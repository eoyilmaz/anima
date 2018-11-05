# -*- coding: utf-8 -*-
# Copyright (c) 2012-2018, Anima Istanbul
#
# This module is part of anima-tools and is released under the BSD 2
# License: http://www.opensource.org/licenses/BSD-2-Clause

import pymel.core as pm
from shapes import Shape


class DrawNode(object):
    """
    """
    # TODO: add documentation here!

    def __init__(self, drawer, name):

        # Drawn Node
        """

        :param drawer:
        :param name:
        """

        self._drawnNode = None

        self._set_drawnNode(drawer, name)

        self._pointConst = None
        self._pointConstTarget = None

        self._parentConst = None
        self._parentConstTarget = None

        self._orientCons = None
        self._orientConstTarget = None

        self._transform = None
        self._axialCor = None
        self._ofsGrp = []
        ##########################################
        #DEL LATER
        self._constrainedPoint = None
        self._targetPoint = None

        self._constrainedParent = None
        self._targetParent = None

        self._constrainedOrient = None
        self._targetOrient = None
        ########################################
        self._inputPoint = None
        self._outputPoint = None

        self._inputOrient = None
        self._outputOrient = None

        self._inputParent = None
        self._outputParent = None


    def _draw(self, drawer, args):
    # Draw the Node
        return drawer(args)

    def _set_drawnNode(self, drawer, args):
        self._drawnNode = self._draw(drawer, args)

    def freeze_transformations(self):
        pm.makeIdentity(self._drawnNode, apply=True)

    def move(self, position):
        if not isinstance(position, pm.dt.Vector):
            raise TypeError("position should be Vector")
        pm.move(self._drawnNode, position, r=1)

    def delete(self):
        pm.delete(self.drawnNode)
        if self._axialCor is not None:
            pm.delete(self.axialCor)
        del self

    # *************************************************************************
    # PROPERTIES
    @property
    def drawnNode(self):
        return self._drawnNode

    @property
    def pointConst(self):
        return self._pointConst

    @property
    def orientConst(self):
        return self._orientCons

    @property
    def parentConst(self):
        return self._parentConst

    @property
    def transform(self):
        self._transform = (pm.xform(self._drawnNode, q=1, t=1))
        return self._transform

    @transform.setter
    def transform(self, moveVal):
        self._transform = (pm.xform(self._drawnNode, t=moveVal))

    @property
    def axialCor(self):
        return self._axialCor

    @property
    def ofsGrp(self):
        return self._ofsGrp

    @property
    def constrainedPoint(self):
        return self._constrainedPoint


    #delete Later
    def create_parentConst(self, source, dest, maintainOff=0):
        return (pm.parentConstraint(source, dest, mo=maintainOff))

    def delete_parent(self, node_in):
        pm.delete(node_in)

    # *************************************************************************
    def create_axialCor(self):
        # Create Axial Correction group
        if self._axialCor is not None:
            temp_grp = pm.group(self.drawnNode, n=(self._axialCor + "_#"))
            self.ofsGrp.append(temp_grp)
        else:
            name = (self.drawnNode + "_axialCor")
            self._axialCor = self._draw(Shape.transform,
                                        (name))

            pm.delete(pm.parentConstraint(self.drawnNode, self.axialCor, mo=0))
            pm.parent(self._drawnNode, self._axialCor)
            #pm.delete(self.create_parentConst(self.drawnNode, self.axialCor))
            #pm.parent(self._drawnNode, self.axialCor)

    # Create Point Constrain
    def inputPoint(self, target=None, maintainOff=None):
        if target is None and maintainOff is None:
            return self._inputPoint
        else:
            self._inputPoint = pm.pointConstraint(target, self.drawnNode,
                                                  mo=maintainOff)

    def outputPoint(self, constrained=None, maintainOff=None):
        if constrained is None and maintainOff is None:
            return self._outputPoint
        else:
            self._outputPoint = pm.pointConstraint(self.drawnNode, constrained,
                                                   mo=maintainOff)
    def temp_inputPoint(self, target, maintainOff=1):
        tempConst = self.inputPoint(target, maintainOff)
        pm.delete(tempConst)
    def temp_outputPoint(self, constrained, maintainOff=1):
        tempConst = self.inputPoint(constrained, maintainOff)
        pm.delete(tempConst)

    # Create Orient Constrain
    def inputOrient(self, target=None, maintainOff=None):
        if target is None and maintainOff is None:
            return self._inputOrient
        else:
            self._inputOrient = pm.orientConstraint(target, self.drawnNode,
                                                    mo=maintainOff)

    def outputOrient(self, constrained=None, maintainOff=None):
        if constrained is None and maintainOff is None:
            return self._outputOrient
        else:
            self._outputOrient = pm.orientConstraint(constrained,
                                                     self.drawnNode,
                                                     mo=maintainOff)
    def temp_inputOrient(self, target, maintainOff=1):
        tempConst = self.inputPoint(target, maintainOff)
        pm.delete(tempConst)
    def temp_outputOrient(self, constrained, maintainOff=1):
        tempConst = self.inputPoint(constrained, maintainOff)
        pm.delete(tempConst)

    # Create Parent Constrain
    def constrain(self, node_in, constType='point',
                  targetType='constObj',
                  maintainOff=0):

        """
        :param constType: It can bePoint Orient or Parent
        :param targetType: It can be constObj or targetObj
                if targetType is constObj node in object Constrain drawnNode
                if targetType is targetObj drawnNode Constrain node in object
        :param node_in: if it is 1 preserve the constrained object’s position
        :param target: it should be constObj or targetObj
        :param maintainOffset: if it is 1 preserve the constrained
                object’s position
        """
        tempConst = None
        target, constrained, setObjType = self._validate_targetType(node_in,
                                                                    targetType)

        if constType is 'point':
            tempConst = pm.pointConstraint(target, constrained, mo=maintainOff)
            if setObjType is 'setConstrainedPoint':
                self._constrainedPoint = tempConst
            else:
                self._targetPoint = tempConst
        elif constType is 'orient':
            tempConst = pm.orienConstraint(target, constrained, mo=maintainOff)
            if setObjType is 'setConstrainedPoint':
                self._constrainedOrient = tempConst
            else:
                self._targetOrient = tempConst
        elif constType is 'parent':
            tempConst = pm.parentConstraint(target, constrained,
                                            mo=maintainOff)
            if setObjType is 'setConstrainedPoint':
                self._constrainedParent = tempConst
            else:
                self._targetParent = tempConst

        return tempConst


    def _validate_targetType(self, node_in, targetType):
        """

        :param node_in:
        :param targetType:
        :return: :raise:
        """
        if (targetType is not 'constObj') and (targetType is not 'targetObj'):
            raise TypeError(
                '%s parameter should be constObj or targetObj' % targetType)

        elif targetType is 'constObj':
            return node_in, self.drawnNode, 'setConstrainedPoint'
        else:
            return self.drawnNode, node_in, 'setTargetPoint'

    def temp_constrain(self, node_in, constType='point',
                       targetType='constObj',
                       maintainOff=0):

        """
        :param constType: It can bePoint Orient or Parent
        :param targetType: It can be constObj or targetObj
                if targetType is constObj node in object Constrain drawnNode
                if targetType is targetObj drawnNode Constrain node in object
        :param node_in: if it is 1 preserve the constrained object’s position
        :param target: it should be constObj or targetObj
        :param maintainOffset: if it is 1 preserve the constrained
                object’s position
        """
        pm.delete(self.constrain(node_in, constType, targetType, maintainOff))



