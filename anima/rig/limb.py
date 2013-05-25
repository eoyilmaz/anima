
from anima.rig.character import Character
from anima.rig.controllers import FkController, Controller, JointController
from anima.rig.limbJoint import FkJoint, IkJoint
from anima.rig.network import Network
import pymel.core as pm
from anima.rig.utilityFuncs import UtilityFuncs as utiFuncs
from anima.rig.nodes import Nodes



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

#TODO : create Curve
class Limb(object):

    def __init__(self, name, mainCtrl = ''):

        self._name = name

        self._joints = []
        self._controllers = []

        self._network = Network(self._name)
        self._charName = None
        self._charSet = ""

        self.nodes = {}
        self.nodeName = []

        self._validate_mainCtrl(mainCtrl)


    def _validate_charName(self, name_in):

        """validates the given name value"""

        if name_in == None:
            raise TypeError("%s.name can not be None!" %
                            self.__class__.__name__)
        if not isinstance(name_in, (Character)):
            raise TypeError("%s.name should be an instance of Character!" %
                            self.__class__.__name__)
        if name_in == "":
            raise ValueError("%s.name can not be an empty string!" %
                             self.__class__.__name__)
        return name_in
    def _validate_mainCtrl(self, mainCtrl):
        if mainCtrl != '':
            self.mainCtrl =  pm.nt.Transform(mainCtrl)

    def checkJoints(self, fkJoints, ikJoints):
        print fkJoints

    @property
    #sets and returns self._name
    def name(self):
        return self._name
    @name.setter
    def name(self, name_in):
        self.name = self._validate_name(name_in)


    @property
    #sets and returns self._network
    def network(self):
        return self._network
    @network.setter
    def network(self, name_in):
        self._network.name = name_in


    @property
    def mainCtrl(self):
        return self._mainCtrl
    @mainCtrl.setter
    def mainCtrl(self, name_in):
        self._mainCtrl = name_in
        #should disconnect all the inputs outputs and reconnect again

    @property
    def charName(self):
        return self._charName.name
    @charName.setter
    def charName(self, name_in):
        self._charName = self._validate_charName(name_in)

    def validate_nodeName(self, node_in):
        for key in self.nodes.keys() :
            if node_in == key:
                raise ValueError("%s.nodes has already have %s node!" %
                                 (self.__class__.__name__, node_in))



    def append_toNode(self, node_in, controllers = "", joints = "", nodes = ""):
    #creates Nodes Object for the IK setup
    #adds all the nodes to Node Object
        self.nodes[node_in].controllers = controllers
        self.nodes[node_in].joints = joints
        self.nodes[node_in].nodes = nodes

    def append_toLimb(self, node_in):
        #attach Nodes to limbNetwork
        self.network.attach((self.nodes[node_in].network.name))

    def do_FK(self, name, joint, division = 1):
        """doFK creates the FKk setup for the limb
        """

        name = self.name + name
        fkNodes = name + "_fkNodes"

        fkJoints = FkJoint(name, joint)
        fkControllers = []
        for i in  xrange(0, fkJoints.len, division) :
            jntPosition = fkJoints.position[i]
            if i + division < fkJoints.len + 1:
                end_jntPosition = fkJoints.position[i + division]
                tempCtrl = FkController(fkJoints.hierarchy[i], jntPosition, "circle")
                tempCtrl.createZeroGrps()
                if i != 0  :
                    pm.parent(tempCtrl.zeroGrp, fkJoints.hierarchy[i - 1])
                    #Adding length - Scale attribute to the ctrl joints
                attributeName = "length"
                pm.addAttr(tempCtrl.name, ln = attributeName, at = "double", min = 1,
                           dv = 1, h = False, k = True)
                tempCtrl.attributes = attributeName
                for j in  range(i, (i + division), 1):
                    utiFuncs.connect(fkJoints.hierarchy[i], attributeName,
                                    fkJoints.hierarchy[j], "scaleX")
                fkControllers.append(tempCtrl.zeroGrp)

        # Attach FKJoints and FKControllers to Network

        self.nodes[fkNodes] = Nodes(fkNodes)
        self.append_toNode(fkNodes, fkControllers, fkJoints.hierarchy)
        self.append_toLimb(fkNodes)

    def do_IK(self, name, startJoint, endJoint, solver = "ikRPsolver"):
        """doIK creates the IK setup for the limb
        """
        name = self.name +  name
        ikNodes = name + "_ikNodes"

        ikJoints = IkJoint(name, startJoint, endJoint)

        pos = ikJoints.position[ikJoints.len]
        ikController = Controller(name, ikJoints.position[ikJoints.len],
                                  "ikCtrl")
        ikController.createZeroGrps()
        #print ("parentConstrain = %s" % parentConst)
        pm.delete(pm.parentConstraint(ikJoints.endJoint,
                                      ikController.zeroGrp, mo = 0))

        ikHandle = (name + "_ikHandle")
        ikHandleEff = (name  + "_effector")
        IKsolver = pm.ikHandle(sj = ikJoints.root, ee = ikJoints.endJoint,
                               sol = solver)
        IKsolver = [pm.rename(IKsolver[0], ikHandle),
                    pm.rename(IKsolver[1], ikHandleEff)]

        parentConst = ikController.parent(ikHandle)
        #creates IKNodes(node) Object for the IK setup
        #adds all the nodes to IKNodes(node) Object

        self.nodes[ikNodes] = Nodes(ikNodes)
        self.append_toNode(ikNodes, ikController.zeroGrp,  IKsolver,
                        ikJoints.hierarchy)
        self.append_toLimb(ikNodes)


    def do_SplineIK(self, name, startJoint, endJoint, stretchy = False,
                    maintainVolume = 0, curve = '', numOfCtrls = 2,
                    numOfSpans = 1):

        #sets the name of the limb Part
        name = self.name + name + "_SP"
        splineNode = name + "_ikSpline"
        self.validate_nodeName(splineNode )
        #creates spline node
        self.nodes[splineNode] = Nodes(splineNode)


        #creates Joints for Spline IK
        ikJoints = IkJoint(name, startJoint, endJoint)
        controller = []
        #Creates Control joints for bind splineCurve
        startController = JointController(name, startJoint, ikJoints.startPosition)
        endController = JointController(name, endJoint, ikJoints.endPosition)
        pm.delete(pm.parentConstraint(ikJoints.endJoint,
                                      endController.zeroGrp, mo = 0))
        distance = (endController.position - startController.position) \
                   / (numOfCtrls - 1)

        for j in range(1, numOfCtrls - 1, 1):
            new_pos = startController.position + (distance * j)
            tempCtrl = JointController(name, startJoint, position = new_pos)
            #self.append_toNode(splineNode, nodes = tempCtrl.zeroGrp)
            controller.append(tempCtrl.joint.root)
            #self.append_toNode(splineNode, joints = tempCtrl.joint.root)
            self.append_toNode(splineNode, tempCtrl.name, tempCtrl.zeroGrp,
                               tempCtrl.joint.root)


            #creates SplineSolver
        #if it is stretchy main ctrl should nt be an empty attribute
        if stretchy and self._mainCtrl == "":
            raise ValueError("if stretchy attribute is True %s._mainCtrl can not"
                             "be an empty string! " % self.__class__.__name__)
        if curve == "":
            splineIK = pm.ikHandle(sj = ikJoints.root, ee = ikJoints.endJoint,
                        sol = "ikSplineSolver")
            splineIK_curve = pm.rename(splineIK[2], (name  + "_curve"))
        else:
            splineIK = pm.ikHandle(sj = ikJoints.root, ee = ikJoints.endJoint,
                                   ccv = False, pcv = False,
                                   c = curve, fj = 0, sol = "ikSplineSolver")
            splineIK_curve = pm.rename(curve, (name  + "_curve"))

        splineIK_handle = pm.rename(splineIK[0], (name + "_ikHandle"))
        splineIK_eff = pm.rename(splineIK[1], (name  + "_effector"))


        splineIK = [splineIK_handle, splineIK_eff, splineIK_curve]
        #binds curve to CtrlJoints
        skinCluster = pm.skinCluster(splineIK_curve, startController.joint.root,
                       endController.joint.root, controller, tsb = True)
        skinCluster = pm.rename(skinCluster, splineIK_curve + "skinCluster" )
        splineIK.append(skinCluster)


        #stretchy spline setup
        #if maintain volume is off

        #creates IKNodes(node) Object for the IK setup
        #adds all the nodes to IKNodes(node) Object
        splineIK.append(pm.group(splineIK_curve, splineIK_handle,
                                 ikJoints.root, n = (name + "_stuff")))

        self.append_toNode(splineNode, [startController.zeroGrp, endController.zeroGrp],
                           ikJoints.hierarchy, splineIK)

        #connect splineNode Network to limbNetwork
        self.append_toLimb(splineNode)

        if stretchy == True:
            self.do_StretchySpline(splineIK_curve, ikJoints.hierarchy,
                                   splineIK_handle, splineNode, maintainVolume)









    def do_StretchySpline(self, curve, joints, ikHandle, nodeName,
                          maintainVolume = 0):

        if self.mainCtrl == "":
            raise ValueError("%s.mainCtrl can not be an empty string!" %
                             self.__class__.__name__)


        curveInfo = pm.createNode("curveInfo", n = curve + "_crvInfo")

        curveShape = (pm.listRelatives (curve, s = 1))[0]

        pm.connectAttr (curveShape.worldSpace[0], curveInfo.inputCurve)
        pm.addAttr(curveInfo, ln = "normalizedScale", at = "double",
                   h = False, k = True)

        normalizeMd = self.create_MD((curve + "_normalizedScale"),
                                     curveInfo.arcLength,
                                     (pm.getAttr(curveInfo.arcLength)), 2)

        pm.connectAttr (normalizeMd.outputX, curveInfo.normalizedScale)
        globalScaleMd = self.create_MD((curve + "_globalScale"),
                                       curveInfo.normalizedScale,
                                       self.mainCtrl.scaleX, 2)

        if maintainVolume == 0:
            for jnt in joints:
                pm.connectAttr (globalScaleMd.outputX, jnt.scaleX)
        else:
            pm.addAttr(curve, ln = "scalePower", at = "double", h = False, k = True)
            pm.setKeyframe(curve, at = 'scalePower', t = [1, 10])
            pm.keyTangent(curve, at = 'scalePower', edit = True, t =[1],  wt = True)
            pm.keyTangent(curve, at = 'scalePower', t = [1] , ia = 50, oa = 50,
                          iw = 3, ow = 3)
            pm.keyTangent(curve, at = 'scalePower', t = [10] , ia = -50, oa = -50,
                          iw = 3, ow = 3)


            normzScaleSqrt = self.create_MD((curve + "_normzScaleSqrt"),
                                            globalScaleMd.outputX, 0.5, 3)

            sqrtMult = self.create_MD((curve + "_sqrtMult"), 1.0,
                                      normzScaleSqrt.outputX, 2)

            k = 0
            cacheNodes = []
            scaleMultipliers= []
            for jnt in joints :
                pm.addAttr(jnt, ln = "pow", at = "double", h = False, k = True)
                cacheName = pm.createNode("frameCache", n= (jnt + "_frameCache"))
                pm.connectAttr(cacheName.varying, jnt.pow)
                pm.connectAttr(curve.scalePower, cacheName.stream)
                k = k + 1
                pm.setAttr(cacheName.varyTime, k)
                cacheNodes.append(cacheName)

                scaleMult = self.create_MD((jnt + "sclMult"), sqrtMult.outputX,
                                           jnt.pow, 3)
                scaleMultipliers.append((scaleMult))
                pm.connectAttr(globalScaleMd.outputX, jnt.scaleX)
                pm.connectAttr(scaleMult.outputX, jnt.scaleY)
                pm.connectAttr(scaleMult.outputX, jnt.scaleZ)

            self.append_toNode(nodeName, nodes = cacheNodes)
            self.append_toNode(nodeName, nodes = scaleMultipliers)
            self.append_toNode(nodeName, nodes = [curveInfo, sqrtMult, normalizeMd,
                                                    normzScaleSqrt, globalScaleMd])

    def create_MD(self, name, input1, input2, operation):
    #creates multiply Divide node
        mdNode = pm.createNode ('multiplyDivide', n = name)
        pm.setAttr (mdNode.operation,  operation)

        if isinstance(input1, (float)):
            pm.setAttr (mdNode.input1X, input1)
        else:
            pm.connectAttr (input1, mdNode.input1X)

        if isinstance(input2, (float)):
            pm.setAttr (mdNode.input2X, input2)
        else :
            pm.connectAttr (input2, mdNode.input2X)

        return mdNode



    def do_FK_IK_switch(self, fkJoints, ikJoints):
        pass
    def do_FK_IK_blend(self, fkJoints, ikJoints):
        pass

    def mainCtrl_setup(self, name_in):
        #should disconnect all the outputs and reconnect to the new one
        pass

    def create_multiplyDivide(self):
        pass


