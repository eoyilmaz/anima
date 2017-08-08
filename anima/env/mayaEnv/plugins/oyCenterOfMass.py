# oyCenterOfMass by E. Ozgur Yilmaz (c) 2009
# 
# v0.1.0
# 
# Description :
# -------------
# Center of mass node, simply calculates the center of the mass of the given
# object group and outputs the trajectory as an MVectorArray in the given frame
# range
# 
# Version History :
# -----------------
# v0.0.1
# - development version
# 
# TODO List :
# -----------
# ------------------------------------------------------------------------------

import math, sys

import maya.OpenMaya as OpenMaya
import maya.OpenMayaMPx as OpenMayaMPx

kPluginNodeTypeName = "oyCenterOfMass"
kPluginNodeId = OpenMaya.MTypeId(0x360)



__version__ = "0.0.1"




class oyCenterOfMass(OpenMayaMPx.MPxNode):
    # class variables
    
    # ----------------------------------------------
    # ---- INPUTS ----
    # compound
    aInput = OpenMaya.MObject()
    
    # objectList ( unknown for now )
    aObjectList = OpenMaya.MObject()
    
    ## inMesh ( array of mesh )
    #aInMesh = OpenMaya.MObject()
    
    # start frame and end frame (kInt)
    aStartFrame = OpenMaya.MObject()
    aEndFrame = OpenMaya.MObject()
    
    
    # ----------------------------------------------
    # ---- OUTPUTS ----
    # output compound
    aOutput = OpenMaya.MObject()
    
    # vectorArray
    aCOMPos = OpenMaya.MObject()
    # ----------------------------------------------
    
    
    
    def __init__(self):
        OpenMayaMPx.MPxNode.__init__(self)
    
    
    
    def compute(self, plug, dataBlock):
        
        if plug == oyCenterOfMass.aCOMPos:
            
            # get the mesh vertices for time from start to end
            
            # get the meshes
            arrayDataHandle = dataBlock.inputArrayValue( oyCenterOfMass.aObjectList )
            numOfConnections = arrayDataHandle.elementCount()
            
            inputDataHandle = OpenMaya.MDataHandle()
            inputGeometryDataHandle = OpenMaya.MDataHandle()
            
            mesh = OpenMaya.MObject()
            meshList = OpenMaya.MObjectArray()
            
            for i in range(numOfConnections):
                arrayDataHandle.jumpToElement(i)
                
                inputDataHandle = arrayDataHandle.inputValue()
                inputGeometryDataHandle = inputDataHandle.child( oyCenterOfMass.aObjectList )
                
                mesh = inputGeometryDataHandle.asMesh()
                
                if mesh.hasFn( OpenMaya.MFn.kMesh ):
                    meshList.append( mesh )
            
            
            numOfMesh = meshList.length()
            
            # return if no mesh
            if numOfMesh == 0:
                return OpenMaya.MStatus.kSuccess
            
            # read the mesh vertices in to one big array
            verticesOfOneMesh = OpenMaya.MPointArray()
            allVertices = OpenMaya.MPointArray()
            
            meshFn = OpenMaya.MFnMesh()
            
            for i in range(numOfMesh):
                meshFn.getPoints ( verticesOfOneMesh, OpenMaya.MSpace.kWorld )
                
                for j in range(verticesOfOneMesh.length()):
                    allVertices.append( verticesOfOneMesh[j] )
                
            
            
            
            
            
            
            
            # set the time
            
            return OpenMaya.MStatus.kSuccess
        else:
            return OpenMaya.kUnknownParameter
    
    
    
    def getVerticesForFrame(self, dataBlock, mesh, frame):
        """returns the vertex positions for given frame
        """
        


def nodeCreator():
    """creator
    """
    return OpenMayaMPx.asMPxPtr( oyCenterOfMass() )



def nodeInitializer():
    """node initializer
    """
    
    # create attributes
    mAttrFn = OpenMaya.MFnMessageAttribute()
    tAttrFn = OpenMaya.MFnTypedAttribute()
    cAttrFn = OpenMaya.MFnCompoundAttribute()
    
    # lets try calculating with mesh vertices
    # so create an attribute like inMesh that accepts
    # mesh objects
    
    # ----------------------------------------------
    # ---- INPUTS ----

    # ----------------
    # objectList
    # 
    # object list should be an array that accepts mesh
    oyCenterOfMass.aInMesh = tAttrFn.create( "inMesh", "im", OpenMaya.MFnData.kMesh )
    tAttrFn.setStorable(False)
    tAttrFn.setKeyable(False)
    tAttrFn.setArray(True)
    oyCenterOfMass.addAttribute( oyCenterOfMass.aInMesh )
    
    # ----------------
    # input it self
    oyCenterOfMass.aInput = cAttrFn.create( "input", "in" )
    cAttrFn.addChild( oyCenterOfMass.aInMesh )
    oyCenterOfMass.addAttribute( oyCenterOfMass.aInput )
    
    # ----------------------------------------------
    # ---- OUTPUTS ----
    
    # ----------------
    # center of mass positions
    defaultVectorArray = OpenMaya.MVectorArray()
    vectorArrayDataFn = OpenMaya.MFnVectorArrayData()
    vectorArrayDataFn.crate( defaultVectorArray )
    
    oyCenterOfMass.aCOMPos = tAttrFn.create( "centerOfMass", "com", OpenMaya.MFnData.kVectorArray, vectorArrayDataFn.object() )
    tAttr.setWritable(False)
    tAttr.setStorable(False)
    oyCenterOfMass.addAttribute( oyCenterOfMass.aCOMPos )
    
    # output itself
    oyCenterOfMass.aOutput = cAttrFn.create( "output", "op" )
    oyCenterOfMass.addAttribute( oyCenterOfMass.aOutput )
    
    # set releations
    oyCenterOfMass.attributeAffects( oyCenterOfMass.aObjectList, oyCenterOfMass.aCOMPos )
    oyCenterOfMass.attributeAffects( oyCenterOfMass.aStartFrame, oyCenterOfMass.aCOMPos )
    oyCenterOfMass.attributeAffects( oyCenterOfMass.aEndFrame  , oyCenterOfMass.aCOMPos )






def initializePlugn(mobject):
    """plugin initializer
    """
    mplugin = OpenMayaMPx.MFnPlugin(mobject, "E. Ozgur Yilmaz", __version__, "Any" )
    try:
        mplugin.registerNode( kPluginNodeTypeName, kPluginNodeId, nodeCreator, nodeInitializer )
    except:
        sys.stderr.write( "Failed to register node: %s" % kPluginNodeTypeName )
        raise



def uninitializerPlugin(mobject):
    """plugin uninitializer
    """
    mplugin = OpenMayaMPx.MFnPlugin(mobject)
    try:
        mplugin.deregisterNode( kPluginNodeId )
    except:
        sys.stderr.write( "Failed to deregister node: %s" % kPluginNodeTypeName )
        raise
