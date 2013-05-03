
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
                    self._networkId += 1__author__ = 'Morteza'


def do_fkSetup(self, joint, division = 1):
    """doFk creates the Fk setup for the limb
    fkJoints = Joint name attribute will be limbName_fk_jnt
    fkControllers = Controllers  will be limbName_fk_ctrl
    limbFK_joints
    """
    fkJoints = FkJoint(joint, self.name)
    for jnt in fkJoints.hierarchy :
        self.fkJoints.append(jnt)

    for i in  xrange(0, fkJoints.len, division) :
        jntPosition = fkJoints.position[i]
        end_jntPosition = fkJoints.position[i + division]
        tempCtrl = FkController(fkJoints.hierarchy[i], "circle", jntPosition)
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
        self.fkControllers.append(tempCtrl.name)

    # Attach FKJoints and FKControllers to Network
    self.network.attachList(self.fkJoints)
    self.network.attachList(self.fkControllers)



def do_ikSetup(self, startJoint, endJoint, solver = "ikRPsolver"):

    ikJoints = IkJoint(startJoint, endJoint, self.name)
    ikHandle = (ikJoints.root + "_ikHandle")
    ikHandleEff = (ikJoints.root  + "_effector")
    limbIkHandle = pm.ikHandle(sj = ikJoints.root, ee = ikJoints.endJoint,
                               sol = solver)
    pm.rename(limbIkHandle[0], ikHandle)
    pm.rename(limbIkHandle[1], ikHandleEff)

    pos = ikJoints.position[ikJoints.len]
    ikController = Controller(self.name, "ikCtrl",
                              ikJoints.position[ikJoints.len])
    ikController.createZeroGrps()
    self.ikNodes.append(ikController.parentConstrain(ikHandle))
    for jnt in ikJoints._hierarchy:
        self.ikJoints.append(jnt)

    self.ikControllers.append(ikController.zeroGrp)
    self.ikNodes.append(ikHandle)
    self.ikNodes.append(ikHandleEff)

    #Maybe I dont need to store the IKSetup
    self.network.attachList(self.ikNodes)
    self.network.attachList(self.ikJoints)
    self.network.attachList(self.ikControllers)


