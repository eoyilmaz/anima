import pymel.core as pm
from utilityFuncs import UtilityFuncs as utiFuncs

from limbJoint import ControlJoint

class Controller(object):

    def __init__(self, name, position = [0, 0, 0], shape = "circle"):

        self._name = name
        self._shape = self._validate_shape(shape)
        self._position = position
        self._zeroGrp = None

        self._limb = None
        self._character = None

        self._attributes = []
        self._effectedNodes = []
        self._create()



    def _validate_shape(self, shape):
    # Checks the types of the attributes
    # Checks the type of the shape attribute: should be a member of
    # ctrlsShape dictionary
        if shape is None:
            raise TypeError("shape can not be None")
        if not (utiFuncs.ctrlShapes.has_key(shape)) :
            raise TypeError("shape should be a member of utiFuncs.ctrlsShape")
        if shape is "":
            raise ValueError("shape can not be an empty string")
        return shape
        # Checks the type of limb parameter : type should be Limb



    def _validate_limb(self, limb):
        if not isinstance(limb, (Limb)):
            raise TypeError("limb should be an instance of Limb")
        return limb
        # Checks the type of limb parameter : type should be Limb


    def _validate_limb(self, limb):
        utiFuncs.typeCheck(limb, Limb)
        return limb

    def _create(self):
        #creates the controller curve, delete history, set the position

        curve = eval(utiFuncs.ctrlShapes[self.shape])
        self._name = pm.rename(curve , (self._name + "#"))
        pm.delete(self._name, ch=True )
        pm.xform(self._name, t = self.position)

        tempAttr = pm.listAttr(self.name, k = 1)
        for at in tempAttr :
            self.attributes = at




    @property
    def zeroGrp(self):
        return self._zeroGrp
    @zeroGrp.setter
    def zeroGrp(self, name_in):
        self._zeroGrp = name_in

    @property
    def ofsGrp(self):
        # returns and sets the _zeroGrp value
        return self._ofsGrp
    @ofsGrp.setter
    def ofsGrp(self, name_in):
        self._ofsGrp = name_in

    @property
    def effectedNodes(self):
        return self._effectedNodes



    @property
    # returns and sets the _name value
    def name(self):
        return self._name
    @name.setter
    def name(self, name_in):
        self._name = name_in



    @property
    #returns and sets the _shape
    def shape(self):
        return self._shape
    @shape.setter
    def shape(self, shape_in):
        self._shape = self._validate_shape(shape_in)



    @property
    # returns and sets the controller to a given position
    def position(self):
        return self._position
    @position.setter
    def position(self, newPosition):
        self._position = newPosition
        pm.xform(self.name, t = self._position)



    @property

    def attributes(self):
        return self._attributes
    @attributes.setter
    def attributes(self, attr_in):
        tempName = self.name + '.' + attr_in
        self._attributes.append(tempName)



    def createZeroGrps(self):
        try :
            pm.objExists( self.name )
            #Creating grps
            self.zeroGrp = self.name + "_ZeroGrp"

            pm.group(n= self.zeroGrp, em=1)
            parentName = pm.parentConstraint( self.name, self.zeroGrp, mo=0)
            pm.delete(parentName)

            #Parenting ctrl to Ofs grp
            pm.parent (self.name, self.zeroGrp)

        except pm.MayaNodeError:
            print ("The Controller Doesn't Exist:", self.name)




    def attachToLimb(self, limb):
        self._limb = self._validate_limb(limb)



    def parentConstrain(self, object):
        effectedNode = object + "_parentConstrain"
        pm.parentConstraint(self.name, object, mo = 1, n = effectedNode)
        self._effectedNodes.append(effectedNode)
        return effectedNode

    def parent(self, object):
        pm.parent(object, self.name)
        return self.name

class FkController(Controller) :
    #Class For the FK Controllers
    def _create(self):
        #creates the controller curve, delete history
        curve = pm.rename((eval(utiFuncs.ctrlShapes[self.shape])), "tempCurve")
        pm.delete(curve, ch=True )
        objShape = pm.listRelatives(curve, s = 1)
        objShape = pm.rename(objShape, (self._name + "Shape"))
        pm.parent(objShape, self._name, add=True, s = 1)
        pm.delete(curve)



    def _validate_joint(self):
        #name should be joint
        pass

class JointController(Controller):
    def __init__(self, name, joint, shape = "circle", position = [0, 0, 0]):
        # TODO: Vector olan Position ve Rotation degerlerini joint e tasi
        name = name + "_ctrl"
        if (position == [0, 0,0]):
            position = pm.datatypes.Vector(utiFuncs.position(joint))
        self._joint = ControlJoint(name, joint, position)

        super(JointController, self).__init__(name, position, shape = "circle")

        self.setRotation(self.name, self.joint.root)
        self._createJoints()


    def _createJoints(self):
        self.createZeroGrps()
        self.parent(self.joint.root)



    @property
    def joint(self):
        return self._joint

    def setRotation(self, object1, object2):

        pm.xform(object1, ro = self.joint.rotation)
        pm.xform(object2, ro = [0,0,0])

