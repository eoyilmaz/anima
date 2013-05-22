
import pymel.core as pm


class DrawNode(object):
    def __init__(self, name_in, nodeType):

        # Drawn Node
        self._drawnNode = None
        # Nodes Shapes reading from text file
        self._nodesDict = dict((line.strip().split(' : '))
                               for line in file("_New_createNodes.txt"))
        self._draw(name_in, nodeType)

        self._pointConst = None
        self._TO_pointConst = None

        self._parentConst = None
        self._TO_parentConst = None

        self._orientCons = None
        self._TO_orientConst = None

        self._transform = None
        self._axialCor = None
        self._ofsGrps = []



    def _draw(self, name_in, nodeType):
        # Draw the Node
        temp_drawn = eval(self._nodesDict[nodeType])
        if (isinstance(temp_drawn, list)):
            if (nodeType == 'cluster'):
                self._drawnNode = pm.rename(temp_drawn[1], name_in)
            else :
                self._drawnNode = pm.rename(temp_drawn[0], name_in)
        else :
            self._drawnNode = pm.rename(temp_drawn, name_in)
    def freeze_transformations(self):
        pm.makeIdentity(self._drawnNode, apply = True)

    def move(self, position):
        if not isinstance(position, pm.dt.Vector):
            raise TypeError("position should be Vector")
        pm.move(self._drawnNode, position, r = 1)

    def delete(self):
        pm.delete(self.drawnNode)
        if self._axialCor != None :
            pm.delete(self.axialCor)
        del self



#*****************************************************************************#
    # PROPERTIES
    @property
    def drawnNode(self):
        return self._drawnNode

    @property
    def pointConst(self):
        return self._pointConst

    @property
    def orientConst(self):
        return self._orientCons

    @property
    def parentConst(self):
        return self._parentConst

    @property
    def transform(self):
        self._transform = (pm.xform(self._drawnNode, q = 1, t = 1))
        return self._transform
    @transform.setter
    def transform(self, moveVal):
        self._transform = (pm.xform(self._drawnNode, t = moveVal))

    @property
    def axialCor(self):
        return self._axialCor

    @property
    def ofsGrps(self):
        return self._ofsGrps

    #*****************************************************************************#
    # POINT CONSTRAIN
    def point_const(self, object):
        # Creates Point Costrain to get transformation values
        self._pointConst = pm.pointConstraint(object, self.drawnNode, mo = 0)

    def del_point_const(self):
        # Deletes Point Costrain
        pm.delete(self._pointConst)
    def temp_point_const(self, object):
        # Create a temp constrain and delete to get the positions
        self.point_const(object)
        self.del_point_const()

    def TO_point_const(self, object, maintainOff = 0):
        self._TO_pointConst =  pm.pointConstraint(self.drawnNode, object,
                                                  mo = maintainOff)
    def del_TO_point_const(self):
        pm.delete(self._TO_pointConst)
    def temp_TO_point_const(self, object):
        self.TO_point_const(object)
        self.del_TO_point_const()

    #*****************************************************************************#
    # ORIENT CONSTRAIN
    # Constrain to Object
    def orient_const(self, object):
        # Creates Orient Costrain to get transformation values
        self._orientConst = pm.orientConstraint(object, self.drawnNode, mo = 0)
    def del_orient_const(self):
        # Deletes Orient Costrain
        pm.delete(self._orientConst)
    def temp_orient_const(self, object):
        # Create a temp constrain and delete to get the positions
        self._orient_const(object)
        self.del_orient_const()

    # Costrained to
    def TO_orient_const(self, object, maintainOff = 0):
        self._TO_orientConst =  pm.orientConstraint(self.drawnNode, object,
                                                    mo = maintainOff)
    def del_TO_orient_const(self):
        pm.delete(self._TO_orientConst)
    def temp_TO_orient_const(self, object):
        self.TO_orient_const()
        self.del_TO_orient_const(object)


    #*****************************************************************************#
    # PARENT CONSTRAIN
    # Constrain to Object
    def parent_const(self, object):
        # Creates Parent Costrain to get transformation values
        self._parentConst = pm.parentConstraint(object, self.drawnNode, mo = 0)

    def del_parent_const(self):
        # Deletes Parent Costrain
        pm.delete(self._parentConst)

    def temp_parent_const(self, object):
        # Create a temp constrain and delete to get the positions
        self.parent_const(object)
        self.del_parent_const()

    # Costrained to
    def TO_parent_const(self, object, maintainOff = 0):
        self._TO_parentConst =  pm.parentConstraint(self.drawnNode, object,
                                                    mo = maintainOff)
    def del_TO_parent_const(self):
        pm.delete(self._TO_parentConst)
    def temp_TO_parent_const(self, object):
        self.TO_parent_const(object)
        self.del_TO_parent_const()

    #delete Later
    def create_parentConst(self, source, dest, maintainOff = 0):
        return (pm.parentConstraint(source, dest, mo = maintainOff))
    def delete_parent(self, node_in):
        pm.delete(node_in)



#*****************************************************************************#
    def create_axialCor(self):
        # CREATE Axial Correction GROUP
        if self._axialCor != None:
            temp_grp = pm.group(self.drawnNode, n = (self._axialCor + "_#"))
            self.ofsGrps.append(temp_grp)
        else :
            self._axialCor = pm.rename(eval(self._nodesDict['transform']),
                                       (self.drawnNode + "_axialCor"))
            pm.delete(self.create_parentConst(self.drawnNode, self.axialCor))
            pm.parent(self._drawnNode, self.axialCor)