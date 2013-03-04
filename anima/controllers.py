import pymel.core as pm
from utilityFuncs import UtilityFuncs as utility


class Controller(object):
    instances = []
    def __init__(self, name, shape = "circle", position = [0, 0, 0]):

        self._name = name


        self._shape = self._check_shape(shape)

        self._position = position
        self._zeroGrp = None
        self._ofsGrp = None
        self._limb = None
        self._character = None


        self._create()

    def __del__(self):
        Controller.instances.remove(self)
   #****************************************************************************************************#
# Checks the types of the attibutes
    # Checks the type of the shape attribute: should be a member of ctrlsShape dictionary
    def _check_shape(self, shape):
        if shape is None:
            raise TypeError("shape can not be None")
        if not (utility.ctrlShapes.has_key(shape)) :
            raise TypeError("shape should be a member of utility.ctrlsShape")
        if shape is "":
            raise ValueError("shape can not be an empty string")
        return shape
    # Checks the type of limb parameter : type should be Limb
    def _check_limb(self, limb):
        if not isinstance(limb, (Limb)):
            raise TypeError("limb should be an instance of Limb")
        return limb
   # Checks the type of limb parameter : type should be Limb
    def _check_limb(self, limb):
        utility.typeCheck(limb, Limb)
        return limb
#****************************************************************************************************#

    def _create(self):
        #creates the controller curve, delete history, set the position
        pm.rename(eval(utility.ctrlShapes[self.shape])[0], self.name)
        pm.delete(self.name, ch=True )
        pm.xform(self.name, t = self.position)

        Controller.instances.append(self)
#****************************************************************************************************#



    def _attachToNetwork(self):
        pm.objExists(self._network)
        print "edaxxx"
        all_cons = pm.listConnections(self.network)
        for attrs in self.__dict__.values() :
            if attrs != self.network and isinstance(attrs, str):
                print "self e esit deil"
                if (pm.objExists(attrs)) :
                    print ("node maya da var : %s" % attrs)
                    print "********************************"
                    if len(all_cons) != 0:
                        for cons in all_cons:
                            print cons
                            print "ilk connetion yazildi"
                            if (cons != attrs):
                                print attrs
                                mayaCon = attrs + ('.message')
                                tempAttr = '%s[%s]' % ("affectedBy", self._networkId)
                                networkCon = self.network + "." + tempAttr
                                pm.connectAttr(mayaCon, networkCon)
                                self._networkId += 1
                    else:
                        print attrs
                        mayaCon = attrs + ('.message')
                        tempAttr = '%s[%s]' % ("affectedBy", self._networkId)
                        networkCon = self.network + "." + tempAttr
                        pm.connectAttr(mayaCon, networkCon)
                        self._networkId += 1

#****************************************************************************************************#

    def zeroGrp() :
    # returns and sets the _zeroGrp value
        def fget(self):
            return self._zeroGrp
        def fset(self, name):
            self._zeroGrp = name
        return locals()
    zeroGrp = property( **zeroGrp() )
#****************************************************************************************************#

    # returns and sets the _zeroGrp value
    def ofsGrp():
        def fget(self):
            return self._ofsGrp
        def fset(self, name):
            self._ofsGrp = name
        return locals()
    ofsGrp = property( **ofsGrp() )


#****************************************************************************************************#

    # returns and sets the _name value
    def name():
        def fget(self):
            return self._name
        def fset(self, name):
            self._name = name
        return locals()
    name = property( **name() )

#****************************************************************************************************#

    # returns and sets the _shape value
    def shape():
        def fget(self):
            return self._shape
        def fset(self, shape):
            self._shape = self._check_shape(shape)
        return locals()
    shape = property( **shape() )

#****************************************************************************************************#

    # returns and sets the _position value
    def position():
        def fget(self):
            return self._position
        def fset(self, position):
            self._position = position
        return locals()
    position = property( **position() )



#****************************************************************************************************#

    def createZeroGrps(self):
        try :
            pm.objExists( self.name )
            #Creating grps
            self.zeroGrp = self.name + "_ZeroGrp"
            self.ofsGrp = self.name + "_OfsGrp"

            pm.group(n= self.zeroGrp, em=1)
            pm.group(n= self.ofsGrp, em=1)
            pm.parent(self.ofsGrp, self.zeroGrp)
            parentName = pm.parentConstraint( self.name, self.zeroGrp, mo=0)
            pm.delete(parentName)

            #Parenting ctrl to Ofs grp
            pm.parent (self.name, self.ofsGrp)


        except pm.MayaNodeError:
            print ("The Controller Doesn't Exist:", self.name)

#****************************************************************************************************#


    def attachToLimb(self, limb):

        self._limb = self._check_limb(limb)
        print (self._limb)


    #****************************************************************************************************#
    def attachToCharacter(self, character):

        print character



#****************************************************************************************************#
#****************************************************************************************************#
#****************************************************************************************************#
#****************************************************************************************************#


#Class For the FK Controllers
class FkControllers(Controller) :
    def __init__(self, name, shape = "circle", position = [0, 0, 0]):
        super(FkControllers, self).__init__(name, shape = "circle", position = [0, 0, 0])
        self.controllers = []
        self.numOfCtrls = 1
        self.jointHierarchy = []




