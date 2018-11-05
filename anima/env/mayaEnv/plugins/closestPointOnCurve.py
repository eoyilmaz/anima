# -*- coding: utf-8 -*-
# Copyright (c) 2012-2018, Anima Istanbul
#
# This module is part of anima-tools and is released under the BSD 2
# License: http://www.opensource.org/licenses/BSD-2-Clause


import sys
import maya.OpenMaya as OpenMaya
import maya.OpenMayaMPx as OpenMayaMPx

kPluginNodeTypeName = "spClosestPointOnCurve"
cpocPluginId = OpenMaya.MTypeId(0x00349)

# Node definition
class closestPointOnCurve(OpenMayaMPx.MPxNode):
    # the plugs
    aInCurve = OpenMaya.MObject()
    
    aInPosition = OpenMaya.MObject()
    
    aOutPosition = OpenMaya.MObject()
    aOutPositionX = OpenMaya.MObject()
    aOutPositionY = OpenMaya.MObject()
    aOutPositionZ = OpenMaya.MObject()
    
    aOutNormal = OpenMaya.MObject()
    aOutNormalX = OpenMaya.MObject()
    aOutNormalY = OpenMaya.MObject()
    aOutNormalZ = OpenMaya.MObject()
    
    aOutParam = OpenMaya.MObject()
    
    def __init__(self):
        OpenMayaMPx.MPxNode.__init__(self)
    
    def compute(self, plug, dataBlock):
        if plug == closestPointOnCurve.aOutPosition or plug == closestPointOnCurve.aOutParam:
            dataHandle = dataBlock.inputValue(closestPointOnCurve.aInCurve)
            inputAsCurve = dataHandle.asNurbsCurve()
            
            #if not inputAsCurve.hasFn(OpenMaya.MFn.kNurbsCurve):
            #    return OpenMaya.kUnknownParameter
            
            dataHandle = dataBlock.inputValue(closestPointOnCurve.aInPosition)
            
            inPositionAsFloat3 = dataHandle.asFloat3()
            inPosition = OpenMaya.MPoint(
                inPositionAsFloat3[0],
                inPositionAsFloat3[1],
                inPositionAsFloat3[2]
            )
            
            # connect the MFnNurbsCurve
            # and ask the closest point
            
            nurbsCurveFn = OpenMaya.MFnNurbsCurve(inputAsCurve)
            
            # get and set outPosition
            outParam = OpenMaya.MScriptUtil()
            outParam.createFromDouble(0)
            outParamPtr = outParam.asDoublePtr() 
            
            # get position and paramater
            outPosition = nurbsCurveFn.closestPoint(
                inPosition, True, outParamPtr, 0.001, OpenMaya.MSpace.kWorld
            )
            
            outputHandle = dataBlock.outputValue(
                closestPointOnCurve.aOutPosition
            )
            outputHandle.set3Float(outPosition.x, outPosition.y, outPosition.z)
            
            # get and set outNormal
            #outNormal = nurbsCurveFn.normal(parameter, OpenMaya.MSpace.kWorld)
            #outputHandle = dataBlock.outputValue(closestPointOnCurve.aOutNormal)
            #outputHandle.set3Float(outNormal.x, outNormal.y, outNormal.z)
            #outputHandle.set3Float(0, 1, 0 )
            
            # get and set the uvs
            outputHandle = dataBlock.outputValue(closestPointOnCurve.aOutParam)
            #outputHandle.setFloat(OpenMaya.MScriptUtil(outParamPtr).asDouble())
            outputHandle.setFloat(OpenMaya.MScriptUtil.getDouble(outParamPtr))
            
            dataBlock.setClean(plug)
        else:
            return OpenMaya.kUnknownParameter

# creator
def nodeCreator():
    return OpenMayaMPx.asMPxPtr(closestPointOnCurve())

# initializer
def nodeInitializer():
    tAttr = OpenMaya.MFnTypedAttribute()
    nAttr = OpenMaya.MFnNumericAttribute()
    
    # input curve
    closestPointOnCurve.aInCurve = tAttr.create(
        "inCurve", "ic", OpenMaya.MFnData.kNurbsCurve
    )
    tAttr.setStorable(0)
    closestPointOnCurve.addAttribute(closestPointOnCurve.aInCurve)
    
    # input position
    closestPointOnCurve.aInPositionX = nAttr.create(
        "inPositionX", "ipx", OpenMaya.MFnNumericData.kFloat, 0.0
    )
    nAttr.setStorable(1)
    nAttr.setWritable(1)
    closestPointOnCurve.addAttribute(closestPointOnCurve.aInPositionX)
    
    closestPointOnCurve.aInPositionY = nAttr.create(
        "inPositionY", "ipy", OpenMaya.MFnNumericData.kFloat, 0.0
    )
    nAttr.setStorable(1)
    nAttr.setWritable(1)
    closestPointOnCurve.addAttribute(closestPointOnCurve.aInPositionY)
    
    
    closestPointOnCurve.aInPositionZ = nAttr.create(
        "inPositionZ", "ipz", OpenMaya.MFnNumericData.kFloat, 0.0
    )
    nAttr.setStorable(1)
    nAttr.setWritable(1)
    closestPointOnCurve.addAttribute(closestPointOnCurve.aInPositionZ)
    
    closestPointOnCurve.aInPosition = nAttr.create(
        "inPosition", "ip",
        closestPointOnCurve.aInPositionX,
        closestPointOnCurve.aInPositionY,
        closestPointOnCurve.aInPositionZ
    )
    nAttr.setStorable(1)
    nAttr.setKeyable(1)
    nAttr.setWritable(1)
    closestPointOnCurve.addAttribute(closestPointOnCurve.aInPosition)
    
    # output position
    closestPointOnCurve.aOutPositionX = nAttr.create(
        "outPositionX", "opx", OpenMaya.MFnNumericData.kFloat, 0.0
    )
    nAttr.setStorable(0)
    nAttr.setWritable(0)
    closestPointOnCurve.addAttribute(closestPointOnCurve.aOutPositionX)
    
    closestPointOnCurve.aOutPositionY = nAttr.create(
        "outPositionY", "opy", OpenMaya.MFnNumericData.kFloat, 0.0
    )
    nAttr.setStorable(0)
    nAttr.setWritable(0)
    closestPointOnCurve.addAttribute(closestPointOnCurve.aOutPositionY)
    
    
    closestPointOnCurve.aOutPositionZ = nAttr.create(
        "outPositionZ", "opz", OpenMaya.MFnNumericData.kFloat, 0.0
    )
    nAttr.setStorable(0)
    nAttr.setWritable(0)
    closestPointOnCurve.addAttribute(closestPointOnCurve.aOutPositionZ)
    
    closestPointOnCurve.aOutPosition = nAttr.create(
        "outPosition", "op",
        closestPointOnCurve.aOutPositionX,
        closestPointOnCurve.aOutPositionY,
        closestPointOnCurve.aOutPositionZ
    )
    nAttr.setStorable(0)
    nAttr.setKeyable(0)
    nAttr.setWritable(1)
    closestPointOnCurve.addAttribute(closestPointOnCurve.aOutPosition)
    
    # output normal
    closestPointOnCurve.aOutNormalX = nAttr.create(
        "outNormalX", "onx", OpenMaya.MFnNumericData.kFloat, 0.0
    )
    nAttr.setStorable(0)
    nAttr.setWritable(0)
    closestPointOnCurve.addAttribute(closestPointOnCurve.aOutNormalX)
    
    closestPointOnCurve.aOutNormalY = nAttr.create(
        "outNormalY", "ony", OpenMaya.MFnNumericData.kFloat, 0.0
    )
    nAttr.setStorable(0)
    nAttr.setWritable(0)
    closestPointOnCurve.addAttribute(closestPointOnCurve.aOutNormalY)
    
    closestPointOnCurve.aOutNormalZ = nAttr.create(
        "outNormalZ", "onz", OpenMaya.MFnNumericData.kFloat, 0.0
    )
    nAttr.setStorable(0)
    nAttr.setWritable(0)
    closestPointOnCurve.addAttribute(closestPointOnCurve.aOutNormalZ)
    
    closestPointOnCurve.aOutNormal = nAttr.create(
        "outNormal", "on",
        closestPointOnCurve.aOutNormalX,
        closestPointOnCurve.aOutNormalY,
        closestPointOnCurve.aOutNormalZ
    )
    nAttr.setStorable(0)
    nAttr.setKeyable(0)
    nAttr.setWritable(1)
    closestPointOnCurve.addAttribute(closestPointOnCurve.aOutNormal)
    
    closestPointOnCurve.aOutParam = nAttr.create(
        "outParam", "opa", OpenMaya.MFnNumericData.kFloat, 0.0
    )
    nAttr.setStorable(0)
    nAttr.setKeyable(0)
    nAttr.setWritable(1)
    closestPointOnCurve.addAttribute(closestPointOnCurve.aOutParam)
    
    closestPointOnCurve.attributeAffects(
        closestPointOnCurve.aInCurve,
        closestPointOnCurve.aOutPosition
    )
    closestPointOnCurve.attributeAffects(
        closestPointOnCurve.aInPosition,
        closestPointOnCurve.aOutPosition
    )
    
    closestPointOnCurve.attributeAffects(
        closestPointOnCurve.aInCurve,
        closestPointOnCurve.aOutParam
    )
    closestPointOnCurve.attributeAffects(
        closestPointOnCurve.aInPosition,
        closestPointOnCurve.aOutParam
    )
    
    closestPointOnCurve.attributeAffects(
        closestPointOnCurve.aInCurve,
        closestPointOnCurve.aOutNormal
    )
    closestPointOnCurve.attributeAffects(
        closestPointOnCurve.aInPosition,
        closestPointOnCurve.aOutNormal
    )
    
    closestPointOnCurve.attributeAffects(
        closestPointOnCurve.aOutParam,
        closestPointOnCurve.aOutPosition
    )
    
# initialize the script plug-in
def initializePlugin(mobject):
    mplugin = OpenMayaMPx.MFnPlugin(mobject, "Erkan Ozgur Yilmaz","1.0.2")
    try:
        mplugin.registerNode(
            kPluginNodeTypeName,
            cpocPluginId,
            nodeCreator,
            nodeInitializer
        )
    except:
        sys.stderr.write("Failed to register node: %s" % kPluginNodeTypeName)
        raise

# uninitialize the script plug-in
def uninitializePlugin(mobject):
    mplugin = OpenMayaMPx.MFnPlugin(mobject)
    try:
        mplugin.deregisterNode(cpocPluginId)
    except:
        sys.stderr.write("Failed to deregister node: %s" % kPluginNodeTypeName)
        raise
