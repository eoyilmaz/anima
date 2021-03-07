# v1.0.1

#import sys
import maya.OpenMaya as OpenMaya
import maya.OpenMayaMPx as OpenMayaMPx

kPluginNodeTypeName = "oyClosestPointOnMesh"
cpomPluginId = OpenMaya.MTypeId(0x00357)

# Node definition
class oyClosestPointOnMesh(OpenMayaMPx.MPxNode):
    # the plugs
    aInMesh = OpenMaya.MObject()

    aInPosition = OpenMaya.MObject()

    aOutPosition = OpenMaya.MObject()
    aOutPositionX = OpenMaya.MObject()
    aOutPositionY = OpenMaya.MObject()
    aOutPositionZ = OpenMaya.MObject()

    aOutNormal = OpenMaya.MObject()
    aOutNormalX = OpenMaya.MObject()
    aOutNormalY = OpenMaya.MObject()
    aOutNormalZ = OpenMaya.MObject()

    aOutUV = OpenMaya.MObject()
    aOutU = OpenMaya.MObject()
    aOutV = OpenMaya.MObject()

    def __init__(self):
        OpenMayaMPx.MPxNode.__init__(self)


    def compute(self, plug, dataBlock):
        if ( plug == oyClosestPointOnMesh.aOutPosition or \
                         plug == oyClosestPointOnMesh.aOutPositionX or \
                         plug == oyClosestPointOnMesh.aOutPositionY or \
                         plug == oyClosestPointOnMesh.aOutPositionZ or \
                         plug == oyClosestPointOnMesh.aOutNormal or \
                         plug == oyClosestPointOnMesh.aOutNormalX or \
                         plug == oyClosestPointOnMesh.aOutNormalY or \
                         plug == oyClosestPointOnMesh.aOutNormalZ or \
                         plug == oyClosestPointOnMesh.aOutUV or \
                         plug == oyClosestPointOnMesh.aOutU or \
                         plug == oyClosestPointOnMesh.aOutV ):
            dataHandle = dataBlock.inputValue(oyClosestPointOnMesh.aInMesh)
            inputAsMesh = dataHandle.asMesh()

            #if ( !inputAsCurve.hasFn(OpenMaya.MFn.kNurbsCurve) ):
            #	return OpenMaya.kUnknownParameter

            dataHandle = dataBlock.inputValue(oyClosestPointOnMesh.aInPosition)

            inPositionAsFloat3 = dataHandle.asFloat3()
            inPosition = OpenMaya.MPoint(inPositionAsFloat3[0],
                                         inPositionAsFloat3[1],
                                         inPositionAsFloat3[2])

            # connect the MFnMesh
            # and ask the closest point

            meshFn = OpenMaya.MFnMesh(inputAsMesh)

            outPosition = OpenMaya.MPoint()
            outNormal = OpenMaya.MVector()
            meshFn.getClosestPointAndNormal(inPosition, outPosition, outNormal,
                                            OpenMaya.MSpace.kWorld)

            outputHandle = dataBlock.outputValue(
                oyClosestPointOnMesh.aOutPosition)
            outputHandle.set3Float(outPosition.x, outPosition.y, outPosition.z)


            ## get and set outPosition
            #outParam = OpenMaya.MScriptUtil()
            #outParam.createFromDouble(0)
            #outParamPtr = outParam.asDoublePtr()

            ## get position and paramater
            #outPosition = nurbsCurveFn.closestPoint ( inPosition, outParamPtr, 0.001, OpenMaya.MSpace.kWorld )

            #outputHandle = dataBlock.outputValue( oyClosestPointOnMesh.aOutPosition )
            #outputHandle.set3Float( outPosition.x , outPosition.y , outPosition.z )

            ## get and set outNormal
            ##outNormal = nurbsCurveFn.normal ( parameter , OpenMaya.MSpace.kWorld )
            ##outputHandle = dataBlock.outputValue( oyClosestPointOnMesh.aOutNormal )
            ##outputHandle.set3Float ( outNormal.x , outNormal.y , outNormal.z )
            ##outputHandle.set3Float ( 0 , 1 , 0 )

            ## get and set the uvs
            #outputHandle = dataBlock.outputValue ( oyClosestPointOnMesh.aOutParam )
            #outputHandle.setFloat ( OpenMaya.MScriptUtil(outParamPtr).asDouble() )

            dataBlock.setClean(plug)
        else:
            return OpenMaya.kUnknownParameter


# creator
def nodeCreator():
    return OpenMayaMPx.asMPxPtr(oyClosestPointOnMesh())


# initializer
def nodeInitializer():
    tAttr = OpenMaya.MFnTypedAttribute()
    nAttr = OpenMaya.MFnNumericAttribute()

    # input mesh
    oyClosestPointOnMesh.aInMesh = tAttr.create("inMesh", "in",
                                                OpenMaya.MFnData.kMesh)
    tAttr.setStorable(0)
    oyClosestPointOnMesh.addAttribute(oyClosestPointOnMesh.aInMesh)

    # input position
    oyClosestPointOnMesh.aInPositionX = nAttr.create("inPositionX", "ipx",
                                                     OpenMaya.MFnNumericData.kFloat,
                                                     0.0)
    nAttr.setStorable(1)
    nAttr.setWritable(1)
    oyClosestPointOnMesh.addAttribute(oyClosestPointOnMesh.aInPositionX)

    oyClosestPointOnMesh.aInPositionY = nAttr.create("inPositionY", "ipy",
                                                     OpenMaya.MFnNumericData.kFloat,
                                                     0.0)
    nAttr.setStorable(1)
    nAttr.setWritable(1)
    oyClosestPointOnMesh.addAttribute(oyClosestPointOnMesh.aInPositionY)

    oyClosestPointOnMesh.aInPositionZ = nAttr.create("inPositionZ", "ipz",
                                                     OpenMaya.MFnNumericData.kFloat,
                                                     0.0)
    nAttr.setStorable(1)
    nAttr.setWritable(1)
    oyClosestPointOnMesh.addAttribute(oyClosestPointOnMesh.aInPositionZ)

    oyClosestPointOnMesh.aInPosition = nAttr.create("inPosition", "ip",
                                                    oyClosestPointOnMesh.aInPositionX,
                                                    oyClosestPointOnMesh.aInPositionY,
                                                    oyClosestPointOnMesh.aInPositionZ)
    nAttr.setStorable(1)
    nAttr.setKeyable(1)
    nAttr.setWritable(1)
    oyClosestPointOnMesh.addAttribute(oyClosestPointOnMesh.aInPosition)

    # output position
    oyClosestPointOnMesh.aOutPositionX = nAttr.create("outPositionX", "opx",
                                                      OpenMaya.MFnNumericData.kFloat,
                                                      0.0)
    nAttr.setStorable(0)
    nAttr.setWritable(0)
    oyClosestPointOnMesh.addAttribute(oyClosestPointOnMesh.aOutPositionX)

    oyClosestPointOnMesh.aOutPositionY = nAttr.create("outPositionY", "opy",
                                                      OpenMaya.MFnNumericData.kFloat,
                                                      0.0)
    nAttr.setStorable(0)
    nAttr.setWritable(0)
    oyClosestPointOnMesh.addAttribute(oyClosestPointOnMesh.aOutPositionY)

    oyClosestPointOnMesh.aOutPositionZ = nAttr.create("outPositionZ", "opz",
                                                      OpenMaya.MFnNumericData.kFloat,
                                                      0.0)
    nAttr.setStorable(0)
    nAttr.setWritable(0)
    oyClosestPointOnMesh.addAttribute(oyClosestPointOnMesh.aOutPositionZ)

    oyClosestPointOnMesh.aOutPosition = nAttr.create("outPosition", "op",
                                                     oyClosestPointOnMesh.aOutPositionX,
                                                     oyClosestPointOnMesh.aOutPositionY,
                                                     oyClosestPointOnMesh.aOutPositionZ)
    nAttr.setStorable(0)
    nAttr.setKeyable(0)
    nAttr.setWritable(1)
    oyClosestPointOnMesh.addAttribute(oyClosestPointOnMesh.aOutPosition)

    # output normal
    oyClosestPointOnMesh.aOutNormalX = nAttr.create("outNormalX", "onx",
                                                    OpenMaya.MFnNumericData.kFloat,
                                                    0.0)
    nAttr.setStorable(0)
    nAttr.setWritable(0)
    oyClosestPointOnMesh.addAttribute(oyClosestPointOnMesh.aOutNormalX)

    oyClosestPointOnMesh.aOutNormalY = nAttr.create("outNormalY", "ony",
                                                    OpenMaya.MFnNumericData.kFloat,
                                                    0.0)
    nAttr.setStorable(0)
    nAttr.setWritable(0)
    oyClosestPointOnMesh.addAttribute(oyClosestPointOnMesh.aOutNormalY)

    oyClosestPointOnMesh.aOutNormalZ = nAttr.create("outNormalZ", "onz",
                                                    OpenMaya.MFnNumericData.kFloat,
                                                    0.0)
    nAttr.setStorable(0)
    nAttr.setWritable(0)
    oyClosestPointOnMesh.addAttribute(oyClosestPointOnMesh.aOutNormalZ)

    oyClosestPointOnMesh.aOutNormal = nAttr.create("outNormal", "on",
                                                   oyClosestPointOnMesh.aOutNormalX,
                                                   oyClosestPointOnMesh.aOutNormalY,
                                                   oyClosestPointOnMesh.aOutNormalZ)
    nAttr.setStorable(0)
    nAttr.setKeyable(0)
    nAttr.setWritable(1)
    oyClosestPointOnMesh.addAttribute(oyClosestPointOnMesh.aOutNormal)

    # output uv
    oyClosestPointOnMesh.aOutU = nAttr.create("outU", "ou",
                                              OpenMaya.MFnNumericData.kFloat,
                                              0.0)
    nAttr.setStorable(0)
    nAttr.setWritable(0)
    oyClosestPointOnMesh.addAttribute(oyClosestPointOnMesh.aOutU)

    oyClosestPointOnMesh.aOutV = nAttr.create("outV", "ov",
                                              OpenMaya.MFnNumericData.kFloat,
                                              0.0)
    nAttr.setStorable(0)
    nAttr.setWritable(0)
    oyClosestPointOnMesh.addAttribute(oyClosestPointOnMesh.aOutV)

    oyClosestPointOnMesh.aOutUV = nAttr.create("outUV", "ouv",
                                               oyClosestPointOnMesh.aOutU,
                                               oyClosestPointOnMesh.aOutV)
    nAttr.setStorable(0)
    nAttr.setKeyable(0)
    nAttr.setWritable(1)
    oyClosestPointOnMesh.addAttribute(oyClosestPointOnMesh.aOutUV)

    # dependencies
    oyClosestPointOnMesh.attributeAffects(oyClosestPointOnMesh.aInMesh,
                                          oyClosestPointOnMesh.aOutPosition)
    oyClosestPointOnMesh.attributeAffects(oyClosestPointOnMesh.aInPosition,
                                          oyClosestPointOnMesh.aOutPosition)

    oyClosestPointOnMesh.attributeAffects(oyClosestPointOnMesh.aInMesh,
                                          oyClosestPointOnMesh.aOutNormal)
    oyClosestPointOnMesh.attributeAffects(oyClosestPointOnMesh.aInPosition,
                                          oyClosestPointOnMesh.aOutNormal)

    oyClosestPointOnMesh.attributeAffects(oyClosestPointOnMesh.aInMesh,
                                          oyClosestPointOnMesh.aOutUV)
    oyClosestPointOnMesh.attributeAffects(oyClosestPointOnMesh.aInPosition,
                                          oyClosestPointOnMesh.aOutUV)


# initialize the script plug-in
def initializePlugin(mobject):
    mplugin = OpenMayaMPx.MFnPlugin(mobject, "Ozgur Yilmaz", "1.0.0")
    try:
        mplugin.registerNode(kPluginNodeTypeName, cpomPluginId, nodeCreator,
                             nodeInitializer)
    except:
        sys.stderr.write("Failed to register node: %s" % kPluginNodeTypeName)
        raise


# uninitialize the script plug-in
def uninitializePlugin(mobject):
    mplugin = OpenMayaMPx.MFnPlugin(mobject)
    try:
        mplugin.deregisterNode(cpomPluginId)
    except:
        sys.stderr.write("Failed to deregister node: %s" % kPluginNodeTypeName)
        raise
	
