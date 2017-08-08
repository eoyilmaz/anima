# oyBallisticRuller by E. Ozgur Yilmaz (c) 2009
# 
# v0.1.0
# 
# Description :
# -------------
# a balistic ruler which is based on to the talk of Ari Shapiro in Siggraph 2009
# 
# description right from the siggraph notes:
# 
# A graphics system that significantly improves the visual quality of certain
# types of 3D character motion animated with traditional means by inferring
# physical properties and correcting the results through the use of dynamics.
# 
# Version History :
# -----------------
# v0.1.0
# - changed: changed the data structure to VectorArray for trajectoryPosition
#   attribute
# 
# v0.0.3
# - added: added speed attribute
# - added: added mode attribute to select one of the three modes of
#   Start-End-Time, Start-Vel-Time, End-Vel-Time
# - removed: startFrame and endFrame attributes are removed
#   frameInterval should be directly used as an integer
# 
# v0.0.2
# - added: all attributes are created
# 
# v0.0.1
# - development version
# 
# TODO List :
# -----------
# - add a gravity vector to make the user change the gravity to the direction
#   he/she wants
# 
# ------------------------------------------------------------------------------



import math, sys

import maya.OpenMaya as OpenMaya
import maya.OpenMayaMPx as OpenMayaMPx

kPluginNodeTypeName = "oyBallisticRuler"
kPluginNodeId = OpenMaya.MTypeId(0x359)


__version__ = "0.1.0"



# Node definition
class oyBallisticRuler(OpenMayaMPx.MPxNode):
    # class variables
    
    # ----------------------------------------------
    # ---- INPUTS ----
    # compound
    aInput = OpenMaya.MObject()
    
    # regular attributes
    # StartPos (compound)
    aStartPos = OpenMaya.MObject()
    aStartPosX = OpenMaya.MObject()
    aStartPosY = OpenMaya.MObject()
    aStartPosZ = OpenMaya.MObject()
    
    # endPos (compound)
    aEndPos = OpenMaya.MObject()
    aEndPosX = OpenMaya.MObject()
    aEndPosY = OpenMaya.MObject()
    aEndPosZ = OpenMaya.MObject()
    
    # frameInterval (Integer)
    aFrameInterval = OpenMaya.MObject()
    
    # velocityVector (compound)
    aVelocityVector = OpenMaya.MObject()
    aVelocityVectorX = OpenMaya.MObject()
    aVelocityVectorY = OpenMaya.MObject()
    aVelocityVectorZ = OpenMaya.MObject()
    
    # speed (float)
    aSpeed = OpenMaya.MObject()
    
    # scale (float)
    aScale = OpenMaya.MObject()
    
    # gravity (float)
    aGravity = OpenMaya.MObject()
    
    # frameRate (float)
    aFrameRate = OpenMaya.MObject()
    
    # mode (enum)
    aMode = OpenMaya.MObject()
    # ----------------------------------------------
    
    
    
    # ----------------------------------------------
    # ---- OUTPUTS ----
    # output compound
    aOutput = OpenMaya.MObject()
    
    # vectorArray
    aTPos = OpenMaya.MObject()
    # ----------------------------------------------
    
    
    def __init__(self):
        OpenMayaMPx.MPxNode.__init__(self)
    
    
    
    def compute(self, plug, data):
        
        if plug == oyBallisticRuler.aTPos:
            # Compute different things for different inputs
            
            # get the scale
            scale = data.inputValue( oyBallisticRuler.aScale ).asFloat()
            
            # get the frameRate
            frameRate = data.inputValue( oyBallisticRuler.aFrameRate ).asFloat()
            
            # get the gravity
            gravity = data.inputValue( oyBallisticRuler.aGravity ).asFloat()
            
            # calculate g' ( cm/fr^2 ) with all the scale and frameRate changes
            gravity_prime = 4.0 * gravity / ( frameRate * scale )
            
            # get startPos
            startPos = data.inputValue( oyBallisticRuler.aStartPos ).asFloat3()
            
            # get endPos
            endPos = data.inputValue( oyBallisticRuler.aEndPos ).asFloat3()
            
            
            # get frame interval
            frameInterval = data.inputValue( oyBallisticRuler.aFrameInterval ).asInt()
            frameInterval_asFloat = float(frameInterval)
            
            # calculate the velocity components
            # vx, vy and vz
            vx = ( endPos[0] - startPos[0] ) / frameInterval_asFloat
            vy = ( endPos[1] - startPos[1] ) / frameInterval_asFloat + 0.5 * gravity_prime * frameInterval_asFloat
            vz = ( endPos[2] - startPos[2] ) / frameInterval_asFloat
            
            
            tPos = OpenMaya.MVectorArray()
            tPosX = tPosY = tPosZ = 0.0
            
            # calculate trajectory positions
            for i in range( frameInterval + 1 ):
                i_asFloat = float(i)
                tPosX = startPos[0] + vx * i_asFloat;
                tPosY = startPos[1] + vy * i_asFloat - 0.5 * gravity_prime * i_asFloat * i_asFloat
                tPosZ = startPos[2] + vz * i_asFloat;
                
                tPos.append( OpenMaya.MVector(tPosX, tPosY, tPosZ) )
            
            # output trajectories
            vectorArrayDataFn = OpenMaya.MFnVectorArrayData()
            
            outputDataHandle = data.outputValue( self.aTPos )
            outputDataHandle.setMObject( vectorArrayDataFn.create( tPos ) )
            
            outputDataHandle.setClean()
            
            return OpenMaya.MStatus.kSuccess
        else:
            return OpenMaya.kUnknownParameter
    
    
    
    def setPositions (self, data):
        
        #MDataHandle inputValueDataHandle = data.inputValue( aParticlePositions, &stat );
        inputValueDataHandle = data.inputValue( oyBallisticRuler.aTPos )
        
        #MFnVectorArrayData vectArrayData( inputValueDataHandle.data() );
        vectArrayData = OpenMaya.MFnVectorArrayData( inputValueDataHandle.data() )
        
        trajectoryPosVectArray = vectArrayData.array();
        
        return trajectoryPosVectArray


# creator
def nodeCreator():
    return OpenMayaMPx.asMPxPtr( oyBallisticRuler() )



# initializer
def nodeInitializer():
    
    # create attributes
    nAttr = OpenMaya.MFnNumericAttribute()
    tAttr = OpenMaya.MFnTypedAttribute()
    cAttr = OpenMaya.MFnCompoundAttribute()
    eAttr = OpenMaya.MFnEnumAttribute()
    
    # ----------------------------------------------
    # ---- INPUTS ----
    
    # ----------------
    # startPosX
    oyBallisticRuler.aStartPosX = nAttr.create( "startPosX", "spx", OpenMaya.MFnNumericData.kFloat )
    nAttr.setKeyable(True)
    oyBallisticRuler.addAttribute( oyBallisticRuler.aStartPosX )
    
    
    
    # startPosY
    oyBallisticRuler.aStartPosY = nAttr.create( "startPosY", "spy", OpenMaya.MFnNumericData.kFloat )
    nAttr.setKeyable(True)
    oyBallisticRuler.addAttribute( oyBallisticRuler.aStartPosY )
    
    
    
    # startPosZ
    oyBallisticRuler.aStartPosZ = nAttr.create( "startPosZ", "spz", OpenMaya.MFnNumericData.kFloat )
    nAttr.setKeyable(True)
    oyBallisticRuler.addAttribute( oyBallisticRuler.aStartPosZ )
    
    
    
    # startPos
    oyBallisticRuler.aStartPos = nAttr.create( "startPos", "sp", oyBallisticRuler.aStartPosX, oyBallisticRuler.aStartPosY, oyBallisticRuler.aStartPosZ )
    nAttr.setKeyable(True)
    oyBallisticRuler.addAttribute( oyBallisticRuler.aStartPos )
    
    
    
    # ----------------
    # endPosX
    oyBallisticRuler.aEndPosX = nAttr.create( "endPosX", "epx", OpenMaya.MFnNumericData.kFloat )
    nAttr.setKeyable(True)
    oyBallisticRuler.addAttribute( oyBallisticRuler.aEndPosX )
    
    
    
    # endPosY
    oyBallisticRuler.aEndPosY = nAttr.create( "endPosY", "epy", OpenMaya.MFnNumericData.kFloat )
    nAttr.setKeyable(True)
    oyBallisticRuler.addAttribute( oyBallisticRuler.aEndPosY )
    
    
    
    # endPosZ
    oyBallisticRuler.aEndPosZ = nAttr.create( "endPosZ", "epz", OpenMaya.MFnNumericData.kFloat )
    nAttr.setKeyable(True)
    oyBallisticRuler.addAttribute( oyBallisticRuler.aEndPosZ )
    
    
    
    # endPos
    oyBallisticRuler.aEndPos = nAttr.create( "endPos", "ep", oyBallisticRuler.aEndPosX, oyBallisticRuler.aEndPosY, oyBallisticRuler.aEndPosZ )
    nAttr.setKeyable(True)
    oyBallisticRuler.addAttribute( oyBallisticRuler.aEndPos )
    
    
    
    # ----------------
    # frameInterval
    oyBallisticRuler.aFrameInterval = nAttr.create( "frameInterval", "fi", OpenMaya.MFnNumericData.kInt )
    nAttr.setKeyable(True)
    nAttr.setMin(1)
    nAttr.setDefault(1)
    oyBallisticRuler.addAttribute( oyBallisticRuler.aFrameInterval )
    
    
    
    # ----------------
    # velocityVectorX
    oyBallisticRuler.aVelocityVectorX = nAttr.create( "velocityVectorX", "vvx", OpenMaya.MFnNumericData.kFloat )
    nAttr.setKeyable(True)
    oyBallisticRuler.addAttribute( oyBallisticRuler.aVelocityVectorX )
    
    
    
    # velocityVectorY
    oyBallisticRuler.aVelocityVectorY = nAttr.create( "velocityVectorY", "vvy", OpenMaya.MFnNumericData.kFloat )
    nAttr.setKeyable(True)
    oyBallisticRuler.addAttribute( oyBallisticRuler.aVelocityVectorY )
    
    
    
    # velocityVectorZ
    oyBallisticRuler.aVelocityVectorZ = nAttr.create( "velocityVectorZ", "vvz", OpenMaya.MFnNumericData.kFloat )
    nAttr.setKeyable(True)
    oyBallisticRuler.addAttribute( oyBallisticRuler.aVelocityVectorZ )
    
    
    
    # velocityVector
    oyBallisticRuler.aVelocityVector = nAttr.create( "velocityVector", "vv", oyBallisticRuler.aVelocityVectorX, oyBallisticRuler.aVelocityVectorY, oyBallisticRuler.aVelocityVectorZ )
    nAttr.setKeyable(True)
    nAttr.setDefault(0.0, 1.0, 0.0)
    oyBallisticRuler.addAttribute( oyBallisticRuler.aVelocityVector )
    
    
    
    # ----------------
    # speed
    oyBallisticRuler.aSpeed = nAttr.create( "speed", "spd", OpenMaya.MFnNumericData.kFloat )
    nAttr.setKeyable(True)
    nAttr.setDefault(1.0)
    oyBallisticRuler.addAttribute( oyBallisticRuler.aSpeed )
    
    
    
    # ----------------
    # scale
    oyBallisticRuler.aScale = nAttr.create( "scale", "s", OpenMaya.MFnNumericData.kFloat )
    nAttr.setKeyable(True)
    nAttr.setDefault(1.0)
    oyBallisticRuler.addAttribute( oyBallisticRuler.aScale )
    
    
    
    # ----------------
    # gravity
    oyBallisticRuler.aGravity = nAttr.create( "gravity", "g", OpenMaya.MFnNumericData.kFloat )
    nAttr.setKeyable(True)
    nAttr.setDefault(9.81)
    oyBallisticRuler.addAttribute( oyBallisticRuler.aGravity)
    
    
    
    # ----------------
    # frameRate
    oyBallisticRuler.aFrameRate = nAttr.create( "frameRate", "fr", OpenMaya.MFnNumericData.kFloat )
    nAttr.setKeyable(True)
    nAttr.setDefault(25.0)
    oyBallisticRuler.addAttribute( oyBallisticRuler.aFrameRate )
    
    
    
    # ----------------
    # mode
    oyBallisticRuler.aMode = eAttr.create( "mode", "m" )
    eAttr.addField( "Start-End-Time", 0 )
    eAttr.addField( "Start-Vel-Time", 1 )
    eAttr.addField( "End-Vel-Time", 2 )
    eAttr.setKeyable(False)
    eAttr.setChannelBox(True)
    oyBallisticRuler.addAttribute( oyBallisticRuler.aMode )
    
    
    # ----------------
    # input it self
    oyBallisticRuler.aInput = cAttr.create( "input", "in" )
    
    # add the child attributes
    cAttr.addChild( oyBallisticRuler.aStartPos )
    cAttr.addChild( oyBallisticRuler.aEndPos )
    cAttr.addChild( oyBallisticRuler.aFrameInterval )
    cAttr.addChild( oyBallisticRuler.aVelocityVector )
    cAttr.addChild( oyBallisticRuler.aScale )
    cAttr.addChild( oyBallisticRuler.aGravity )
    cAttr.addChild( oyBallisticRuler.aFrameRate )
    cAttr.addChild( oyBallisticRuler.aMode )
    
    oyBallisticRuler.addAttribute( oyBallisticRuler.aInput )
    # ----------------------------------------------
    
    
    
    # ----------------------------------------------
    # ---- OUTPUTS ----
    
    # ----------------
    # trajectoryPos
    defaultVectorArray = OpenMaya.MVectorArray()
    vectorArrayDataFn = OpenMaya.MFnVectorArrayData()
    vectorArrayDataFn.create( defaultVectorArray )
    
    oyBallisticRuler.aTPos = tAttr.create( "trajectoryPosition", "tp", OpenMaya.MFnData.kVectorArray, vectorArrayDataFn.object() )
    tAttr.setWritable(False)
    tAttr.setStorable(False)
    oyBallisticRuler.addAttribute( oyBallisticRuler.aTPos )
    
    
    
    # output itself
    oyBallisticRuler.aOutput = cAttr.create( "output", "op" )
    
    # add the child attributes
    cAttr.addChild( oyBallisticRuler.aTPos )
    
    # create the attribute
    oyBallisticRuler.addAttribute( oyBallisticRuler.aOutput )
    
    
    
    # set effects
    oyBallisticRuler.attributeAffects( oyBallisticRuler.aStartPos, oyBallisticRuler.aTPos )
    oyBallisticRuler.attributeAffects( oyBallisticRuler.aEndPos, oyBallisticRuler.aTPos )
    oyBallisticRuler.attributeAffects( oyBallisticRuler.aFrameInterval, oyBallisticRuler.aTPos )
    oyBallisticRuler.attributeAffects( oyBallisticRuler.aVelocityVector, oyBallisticRuler.aTPos )
    oyBallisticRuler.attributeAffects( oyBallisticRuler.aSpeed, oyBallisticRuler.aTPos )
    oyBallisticRuler.attributeAffects( oyBallisticRuler.aScale, oyBallisticRuler.aTPos )
    oyBallisticRuler.attributeAffects( oyBallisticRuler.aGravity, oyBallisticRuler.aTPos )
    oyBallisticRuler.attributeAffects( oyBallisticRuler.aFrameRate, oyBallisticRuler.aTPos )
    oyBallisticRuler.attributeAffects( oyBallisticRuler.aMode, oyBallisticRuler.aTPos )



# initialize the script plug-in
def initializePlugin(mobject):
    mplugin = OpenMayaMPx.MFnPlugin(mobject, "E. Ozgur Yilmaz", __version__ , "Any")
    try:
        mplugin.registerNode( kPluginNodeTypeName, kPluginNodeId, nodeCreator, nodeInitializer )
    except:
        sys.stderr.write( "Failed to register node: %s" % kPluginNodeTypeName )
        raise



# uninitialize the script plug-in
def uninitializePlugin(mobject):
    mplugin = OpenMayaMPx.MFnPlugin(mobject)
    try:
        mplugin.deregisterNode( kPluginNodeId )
    except:
        sys.stderr.write( "Failed to deregister node: %s" % kPluginNodeTypeName )
        raise
