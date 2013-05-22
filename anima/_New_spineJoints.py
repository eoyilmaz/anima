__author__ = 'Eda'
import pymel.core as pm
from utilityFuncs import UtilityFuncs as utiFuncs
from curve import Curve


class SpineJoint(object):
    def __init__(self, name_in, curve, horizontalSpine = 0):
        self._curve = Curve(name_in, curve)

        self._jointSpine = None
        self._root = None
        self._frontAxis = None
        self._numOfJoints = None
        #self.horizontalSpine = horizontalSpine
        #self.zeroCVsPosition = None


    @property
    # Spine Curve Getter
    def curve(self):
        return self._curve

    @property
    # Number of Joints Getter
    def numOfJoints(self):
        self._numOfJoints = self.curve.spans + self.curve.degree - 2
        return self._numOfJoints

"""
Spine Orient Joints reload yapilicak
    def orientJoints(self, joint, aimAxis = [1, 0, 0], upAxis = [0, 0, 1],
                     worldUpVector = [0, 1, 0], frontAxis = "z"):
    # if FrontAxis is Z : World Up Object should transform at Positive Z
    # if FrontAxis is X : World Up Object should transform at Positive X
    # if FrontAxis is -Z : World Up Object should transform at Negative Z
    # if FrontAxis is -X : World Up Object should transform at Negative X
    #  Aim Axis == 1 0 0 (x, 0, 0)
        if not isinstance(joint, pm.nt.Joint):
            raise TypeError ("%s sholud be an instance of pm.nt.Joint Class"
                             % joint)
        jointUnder = pm.listRelatives(joint, c = 1, type = "joint")
        if not len(jointUnder):
            pm.setAttr(joint.jointOrient, (0, 0, 0))
            return 0
        temporalGroup = DrawNode('temporalGroup', 'transform')
        pm.parent(jointUnder, temporalGroup.drawnNode)

        pm.setAttr(joint.jointOrient, (0, 0, 0))
        temporalTransform = DrawNode('temporalTransform', 'transform')
        temporalTransform.temp_point_const(jointUnder)
        temporalTransform.freeze_transformations()
        #Draw class a tasinacal
        moveAxis = self._move_axis(frontAxis)
        pm.move(moveAxis.x, moveAxis.y, moveAxis.z,
                temporalTransform.drawnNode, r = 1)

"""