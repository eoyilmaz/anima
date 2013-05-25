# -*- coding: utf-8 -*-
import pymel.core as pm
from anima.rig.shapes import Shape


class DrawNode(object):
    """
    """
    # TODO: add documentation here!

    def __init__(self, drawer, name):

        # Drawn Node
        self._drawnNode = None

        self._draw(drawer, name)

        self._pointConst = None
        self._to_pointConst = None

        self._parentConst = None
        self._to_parentConst = None

        self._orientCons = None
        self._to_orientConst = None

        self._transform = None
        self._axialCor = None
        self._ofsGrps = []

    def _draw(self, drawer, args):
        # Draw the Node
        self._drawnNode = drawer(*args)

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
    def ofsGrps(self):
        return self._ofsGrps

    # *************************************************************************
    # POINT CONSTRAIN
    def point_const(self, node):
        # Creates Point Costrain to get transformation values
        self._pointConst = pm.pointConstraint(node, self.drawnNode, mo=0)

    def del_point_const(self):
        # Deletes Point Costrain
        pm.delete(self._pointConst)

    def temp_point_const(self, node):
        # Create a temp constrain and delete to get the positions
        self.point_const(node)
        self.del_point_const()

    def to_point_const(self, node, maintainOff=0):
        self._to_pointConst = pm.pointConstraint(self.drawnNode, node,
                                                 mo=maintainOff)

    def del_to_point_const(self):
        pm.delete(self._to_pointConst)

    def temp_to_point_const(self, node):
        self.to_point_const(node)
        self.del_to_point_const()

    # *************************************************************************
    # ORIENT CONSTRAIN
    # Constrain to Object
    def orient_const(self, node):
        # Creates Orient Costrain to get transformation values
        self._orientConst = pm.orientConstraint(node, self.drawnNode, mo=0)

    def del_orient_const(self):
        # Deletes Orient Costrain
        pm.delete(self._orientConst)

    def temp_orient_const(self, node):
        # Create a temp constrain and delete to get the positions
        self.orient_const(node)
        self.del_orient_const()

    # Costrained to
    def to_orient_const(self, node, maintainOff=0):
        self._to_orientConst = pm.orientConstraint(
            self.drawnNode, node, mo=maintainOff
        )

    def del_to_orient_const(self):
        pm.delete(self._to_orientConst)

    def temp_to_orient_const(self, node):
        self.to_orient_const(node)
        self.del_to_orient_const()

    # *************************************************************************
    # PARENT CONSTRAIN
    # Constrain to Object
    def parent_const(self, node):
        # Creates Parent Costrain to get transformation values
        self._parentConst = pm.parentConstraint(node, self.drawnNode, mo=0)

    def del_parent_const(self):
        # Deletes Parent Costrain
        pm.delete(self._parentConst)

    def temp_parent_const(self, node):
        # Create a temp constrain and delete to get the positions
        self.parent_const(node)
        self.del_parent_const()

    # Costrained to
    def to_parent_const(self, node, maintainOff=0):
        self._to_parentConst = pm.parentConstraint(
            self.drawnNode, node, mo=maintainOff
        )

    def del_to_parent_const(self):
        pm.delete(self._to_parentConst)

    def temp_to_parent_const(self, node):
        self.to_parent_const(node)
        self.del_to_parent_const()

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
            self.ofsGrps.append(temp_grp)
        else:
            self._axialCor = self._draw(Shape.transform,
                                        self.drawnNode + "_axialCor")
            pm.delete(self.create_parentConst(self.drawnNode, self.axialCor))
            pm.parent(self._drawnNode, self.axialCor)

