# oyTrajectoryDrawer by E. Ozgur Yilmaz (c) 2009
#
# v0.1.0
#
# Description :
# -------------
# draws lines and spheres to the 3D viewport
#
# the input is the trajectoryPositions array attribute, by filling the attribute
# with coordinates you can get your trajectory been drawn
#
# Version History :
# -----------------
# v0.1.0
# - changed: changed the data structure to VectorArray for trajectoryPosition
#   attribute
#
# v0.0.2
# - added: added drawing of path aligned circles instead of junky squares
#
# v0.0.1
# - development version
#
# TODO List :
# -----------
# - optimize circle creation by a LUT for circle data
#
# ------------------------------------------------------------------------------

import maya.OpenMaya as OpenMaya
import maya.OpenMayaMPx as OpenMayaMPx
import maya.OpenMayaRender as OpenMayaRender
import maya.OpenMayaUI as OpenMayaUI

import math
import sys

__version__ = "0.1.0"

pi = 3.14159265358979323846

kPluginNodeTypeName = "oyTrajectoryDrawer"

oyTrajectoryDrawerNodeId = OpenMaya.MTypeId(0x358)
glRenderer = OpenMayaRender.MHardwareRenderer.theRenderer()
glFT = glRenderer.glFunctionTable()


class oyTrajectoryDrawer(OpenMayaMPx.MPxLocatorNode):
    aSize = OpenMaya.MObject()
    aTPos = OpenMaya.MObject()

    circleDivision = 16
    unitAngle = 2 * pi / float(circleDivision)

    def __init__(self):
        OpenMayaMPx.MPxLocatorNode.__init__(self)

    def compute(self, plug, dataBlock):
        return OpenMaya.kUnknownParameter

    def draw(self, view, path, style, status):
        size = self.getSize() * 0.5

        tPosition = self.getTPositions()

        numOfTPos = tPosition.length()

        if numOfTPos != 0:

            view.beginGL()
            glFT.glBegin(OpenMayaRender.MGL_LINES)

            # draw circles
            for i in range(1, numOfTPos - 1):

                direction = tPosition[i + 1] - tPosition[i]

                upVector = self.getTangent(direction)
                upVector = upVector ^ direction
                upVector.normalize()

                origin = tPosition[i]

                circleData = self.getCircleData(origin, direction, upVector, size)

                for j in range(self.circleDivision):
                    glFT.glVertex3f(
                        circleData[j][0], circleData[j][1], circleData[j][2]
                    )
                    glFT.glVertex3f(
                        circleData[j + 1][0], circleData[j + 1][1], circleData[j + 1][2]
                    )

            # draw lines
            for i in range(numOfTPos - 1):
                glFT.glVertex3f(tPosition[i].x, tPosition[i].y, tPosition[i].z)
                glFT.glVertex3f(
                    tPosition[i + 1].x, tPosition[i + 1].y, tPosition[i + 1].z
                )

            glFT.glEnd()
            view.endGL()

    def isBounded(self):
        return True

    def boundingBox(self):

        # get the tPositions
        tPositions = self.getTPositions()

        # get the multiplier
        size = self.getSize()

        # create the bounding box
        bbox = OpenMaya.MBoundingBox()

        # add the positions one by one
        numOfTPos = tPositions.length()

        # print("numOfTPos in bbox : %s " % numOfTPos)

        for i in range(numOfTPos):

            # add the positive one
            bbox.expand(
                OpenMaya.MPoint(tPositions[i] + OpenMaya.MVector(size, size, size))
            )

            # add the negative one
            bbox.expand(
                OpenMaya.MPoint(tPositions[i] - OpenMaya.MVector(size, size, size))
            )

        return bbox

    def getSize(self):
        thisNode = self.thisMObject()
        plug = OpenMaya.MPlug(thisNode, self.aSize)

        sizeVal = plug.asMDistance()

        return sizeVal.asCentimeters()

    def getTPositions(self):
        """reads the trajectory positions from the attribute
        by using the plug instead of the dataBlock
        """

        thisNode = self.thisMObject()
        plug = OpenMaya.MPlug(thisNode, self.aTPos)

        vectorArrayDataFn = OpenMaya.MFnVectorArrayData(plug.asMObject())

        tPosVectArray = vectorArrayDataFn.array()

        return tPosVectArray

    def getTangent(self, normal):
        """returns a tangent vector of normal"""
        tangent = OpenMaya.MVector()

        if abs(normal.x) > 0.5 or abs(normal.y) > 0.5:
            tangent.x = normal.y
            tangent.y = -1.0 * normal.x
            tangent.z = 0.0
        else:
            tangent.x = -1.0 * normal.z
            tangent.y = 0.0
            tangent.z = normal.x

        return tangent

    def getCircleData(self, origin, normal, tangent, scale):
        """creates the circleData"""
        quat = OpenMaya.MQuaternion()
        # create the circle data
        circleData = [] * 0

        for i in range(self.circleDivision):
            quat.setAxisAngle(normal.normal(), float(i) * self.unitAngle)
            pointOnCircle = tangent.rotateBy(quat)

            circleData.append(
                [
                    pointOnCircle.x * scale + origin.x,
                    pointOnCircle.y * scale + origin.y,
                    pointOnCircle.z * scale + origin.z,
                ]
            )

        # close the circle
        # append the first to last
        circleData.append(circleData[0])

        return circleData


def nodeCreator():
    """creator"""
    return OpenMayaMPx.asMPxPtr(oyTrajectoryDrawer())


def nodeInitializer():
    """initializer"""
    # create the size attr
    uAttrFn = OpenMaya.MFnUnitAttribute()
    oyTrajectoryDrawer.aSize = uAttrFn.create(
        "size", "in", OpenMaya.MFnUnitAttribute.kDistance
    )
    uAttrFn.setDefault(1.0)
    oyTrajectoryDrawer.addAttribute(oyTrajectoryDrawer.aSize)

    # create the trajectory positions attr
    nAttrFn = OpenMaya.MFnNumericAttribute()
    tAttrFn = OpenMaya.MFnTypedAttribute()
    mAttrFn = OpenMaya.MFnMessageAttribute()

    defaultVectorArray = OpenMaya.MVectorArray()
    vectorArrayDataFn = OpenMaya.MFnVectorArrayData()
    vectorArrayDataFn.create(defaultVectorArray)

    oyTrajectoryDrawer.aTPos = tAttrFn.create(
        "trajectoryPosition",
        "tp",
        OpenMaya.MFnData.kVectorArray,
        vectorArrayDataFn.object(),
    )

    tAttrFn.setWritable(True)
    tAttrFn.setStorable(True)

    oyTrajectoryDrawer.addAttribute(oyTrajectoryDrawer.aTPos)


def initializePlugin(mobject):
    """initialize the script plug-in"""
    mplugin = OpenMayaMPx.MFnPlugin(mobject, "E. Ozgur Yilmaz", __version__, "Any")
    try:
        mplugin.registerNode(
            kPluginNodeTypeName,
            oyTrajectoryDrawerNodeId,
            nodeCreator,
            nodeInitializer,
            OpenMayaMPx.MPxNode.kLocatorNode,
        )
    except:
        sys.stderr.write("Failed to register node: %s" % kPluginNodeTypeName)
        raise


def uninitializePlugin(mobject):
    """uninitialize the script plug-in"""
    mplugin = OpenMayaMPx.MFnPlugin(mobject)
    try:
        mplugin.deregisterNode(oyTrajectoryDrawerNodeId)
    except:
        sys.stderr.write("Failed to deregister node: %s" % kPluginNodeTypeName)
        raise
