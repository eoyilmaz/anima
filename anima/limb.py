
from character import Character
from controllers import Controller
from limbJoint import Joint, FkJoint
import pymel.core as pm
"""
Creates the limbs of the character
.name: it will store the name of the limb
.instance static list :  will store all the instances objects
__del__ overriden method will remove the instance of the object from .instance

._limbJoints: [Joint,] will store all the joints of the limb.
            members should be the instance of Joint Class
._limbControllers: [Controllers,] will store all the controllers of the limb.
            members should be the instance of Controllers Class
._limbNodes: [Nodes,] will store all the nodes of the limb.
            members should be the instance of Nodes Class
._limbChar:  Character()
            all limbs should have a connection to a character

"""



class Limb(object):
    instances = []

    def __init__(self, name, charName):

        self._name = name
        self._charName = self._check_charName(charName)

        self._setName = ""
        self._joints = []
        self._controllers = []
        self._nodes = []
#        self._network =

        self.fkJoints = []
        self.fkControllers = None

    def _check_name(self, name):
        """Check the type of the initialized parameter name : type should be
        string
        """
        if name is None:
            raise TypeError("name can not be None")
        if not isinstance(name, (str, unicode)):
            raise TypeError("name should be an instance of string")
        if name is "":
            raise ValueError("name can not be an empty string")
        return name

    # TODO: Check the type of the initialized parameter charName : type should be Character

    def _check_charName(self, charName):
        if not isinstance(charName, (Character)):
            raise TypeError("charName should be an instance of Character")
        return charName

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name_in):
        self.name = self._validate_name(name_in)

    def _validate_name(self, name_in):
        """validates the given name value
        """
        if name_in == None:
            raise TypeError("%s.name can not be None!" %
                            self.__class__.__name__)
        return name_in

    def _format_name(self, name_in):
        """formats the name value
        """
        return name_in

    def do_fk(self, joint):
        """doFk creates the Fk setup for the limb
        fkJoints = Joint name attribute will be limbName_fk_jnt
        fkControllers = Controllers  will be limbName_fk_ctrl
        limbFK_joints
        """
        joints_name = self.name + "_FK_jnt"
        fkJoints = FkJoint(joint, joints_name)
        self.fkJoints.append(fkJoints)

        for jnt in fkJoints.hierarchy :
            print jnt
            jntPosition = pm.xform(jnt, q=1, t=1)

    def do_ik(self):
        pass

    def do_fk_ik_blender(self):
        pass

    def do_spline(self):
        pass



