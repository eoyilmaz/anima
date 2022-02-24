# -*- coding: utf-8 -*-
"""A tool for easy animating of picking and releasing of objects.

Version History :
-----------------

1.2.2
-----

- New version numbering theme
- Renamed methods and functions to conform PEP8

10.5.17
-------
- modifications for Maya 2011 and PyMel 1.0.2

10.5.12
--------

- added support for exploding the whole setup

9.11.16
-------

- moved to new version numbers system
- reflected the change in axialCorrectionGroup command

1.2.1
-----
- fixed a little bug in editKeyframesOfObject and addDefaultOptionsToDAGMenu

1.2.0
-----

- added the ability to use the script from DAGMenu with object specific
  commands
- added setObjectsParent, releaseObjectWithName, fixJumpOnObject,
  editKeyframesOfObject which uses string inputs, to be able to use them in the
  DAGMenu

1.1.10
------

- renamed: selectKeyframers is renamed to selectAnimCurves
- improved: setParent now checks for cycle before seting up anything
- improved: releaseObject, editKeyframes, fix_jump now checks for empty
  selection list, and the selList is sustained after they finish their job
- improved: setupToBePicked is rewritten
- improved: creating the localParent is improved
- removed: _isOnTop is removed
- removed: _getUsableParents is replaced with _getParents
- removed: _hasEnoughParents is removed

1.1.9
-----

- fixed: localParent attribute has been left as multi attribute

1.1.8
-----

- fixed: axialCorrection groups of referenced objects are moving as they are
  setup and the objects transformations become non-zero

1.1.7
-----

- fixed: the object can now be setup if it is on top of the hierarchy and even
  it is referenced
- fixed: _getUsableParents now returns the correct nodes
- added: now the parent is checked for cycle before setup

1.1.6
-----

- fixed: _isSetup is causing problems problems to setup the object
- changed: selectKeyframers now selects athe animCurves instead of the
  objects

1.1.5
-----

- added: setParent, releaseObject, editKeyframes, fix_jump functions

1.1.0
-----

- removed: the concept of remote parents, it doesn't need to be saved in an
  attribute, because it can easly be get from the parentConstraint node
- removed: the setupToBePickedUp from __init__, objects need to be setup
  separatedly from the initilization
- changed: internal private functions are now starting with underscore (_)
  following the Python convention
- changed: all the targets changed to parents
- code cleanup

1.0.0
-----

- fixed: fix_jump now works correctly
- organized the code

0.9.0RC
-------

- the code is working now, will stay in this version for a while just to
  observe if animators will have any problems

0.0.2.preAlpha
--------------

- changed: rigger uses no remote parents anymore

0.0.1.preAlpha
---------------

- developing version

TODO :
------

- use scriptJobs for auto fix_jump functionality
- support for scale constraining
- one click multiple object setup

"""

__version__ = "1.2.2"

import pymel.core as pm
from anima.dcc.mayaEnv import auxiliary


class PickedObject(object):
    """PickedObject class to setup picking and releasing of objects
    """

    def __init__(self, node):
        # the object
        self._object = pm.nodetypes.DagNode(node)
        assert(isinstance(self._object, pm.nodetypes.Transform))

        # the data
        self._constrained_parent = None
        self._stabilizer_parent = None
        self._local_parent = None
        self._parent_constraint = None

        self._is_setup = False
        # read settings
        self.read_settings()

    def save_settings(self):
        """saves settings inside objects oyPickerData attribute
        """
        # 
        # data to be save :
        # -----------------
        # 
        # constrainedPrarent node
        # stabilizerParent node
        # parentConstraint node
        # localParent node

        # create attributes
        self.create_data_attribute()

        # connect constrainedParent node
        pm.connectAttr(self._constrained_parent.name() + ".message",
                       self._object.attr("pickedData.constrainedParent"),
                       f=True)

        # connect constrainedParent node
        pm.connectAttr(self._stabilizer_parent.name() + ".message",
                       self._object.attr("pickedData.stabilizerParent"),
                       f=True)

        # connect parentConstraint node
        pm.connectAttr(self._parent_constraint.name() + ".message",
                       self._object.attr("pickedData.parentConstraint"),
                       f=True)

        # connect localParent node
        pm.connectAttr(self._local_parent.name() + ".message",
                       self._object.attr("pickedData.localParent"), f=True)

        # set stabilizer parent values
        tra = self._stabilizer_parent.getAttr('t')
        rot = self._stabilizer_parent.getAttr('r')
        sca = self._stabilizer_parent.getAttr('s')

        self._object.setAttr('pickedData.stabilizerParentInitialData.sPIDposition', tra)
        self._object.setAttr('pickedData.stabilizerParentInitialData.sPIDrotation', rot)
        self._object.setAttr('pickedData.stabilizerParentInitialData.sPIDscale', sca)

    def read_settings(self):
        """reads settings from objects pickedData attribute\n
        if there is no attribute to read it returns False
        """
        # check if it has pickedData attribute
        if self._object.hasAttr("pickedData"):
            # get stabilizerParent node
            self._stabilizer_parent = pm.nodetypes.DagNode(pm.listConnections(
                self._object.attr("pickedData.stabilizerParent"))[0])

            # get constrainedParent node
            self._constrained_parent = pm.nodetypes.DagNode(pm.listConnections(
                self._object.attr("pickedData.constrainedParent"))[0])

            # get parentConstraint node
            self._parent_constraint = pm.nodetypes.DagNode(pm.listConnections(
                self._object.attr("pickedData.parentConstraint"))[0])

            # get localParent node
            self._local_parent = pm.nodetypes.DagNode(pm.listConnections(
                self._object.attr("pickedData.localParent"))[0])

            # set isSetup flag
            self._is_setup = True

            return True

        return False

    def create_data_attribute(self):
        """creates attribute in self._object to hold the rawData
        """
        if not self._object.hasAttr("pickedData"):
            pm.addAttr(self._object, ln="pickedData", at="compound", nc=6)

        if not self._object.hasAttr("constrainedParent"):
            pm.addAttr(self._object, ln="constrainedParent", at="message",
                       p="pickedData")

        if not self._object.hasAttr("stabilizerParent"):
            pm.addAttr(self._object, ln="stabilizerParent", at="message",
                       p="pickedData")

        if not self._object.hasAttr("parentConstraint"):
            pm.addAttr(self._object, ln="parentConstraint", at="message",
                       p="pickedData")

        if not self._object.hasAttr("localParent"):
            pm.addAttr(self._object, ln="localParent", at="message",
                       p="pickedData")

        if not self._object.hasAttr("createdNodes"):
            pm.addAttr(self._object, ln="createdNodes", at="message", m=1,
                       p="pickedData")

        if not self._object.hasAttr("stabilizerParentInitialData"):
            # this attribute should store the default position of the
            # stabilizer parent when the setup is exploded the stabilizer
            # parent should be returned to this local position
            pm.addAttr(self._object, ln="stabilizerParentInitialData",
                       at="compound", nc=3, p="pickedData")

            pm.addAttr(self._object, ln="sPIDposition", at="compound", nc=3,
                       p="stabilizerParentInitialData")
            pm.addAttr(self._object, ln="sPIDpositionX", at="float",
                       p="sPIDposition")
            pm.addAttr(self._object, ln="sPIDpositionY", at="float",
                       p="sPIDposition")
            pm.addAttr(self._object, ln="sPIDpositionZ", at="float",
                       p="sPIDposition")

            pm.addAttr(self._object, ln="sPIDrotation", at="compound", nc=3,
                       p="stabilizerParentInitialData")
            pm.addAttr(self._object, ln="sPIDrotationX", at="float",
                       p="sPIDrotation")
            pm.addAttr(self._object, ln="sPIDrotationY", at="float",
                       p="sPIDrotation")
            pm.addAttr(self._object, ln="sPIDrotationZ", at="float",
                       p="sPIDrotation")

            pm.addAttr(self._object, ln="sPIDscale", at="compound", nc=3,
                       p="stabilizerParentInitialData")
            pm.addAttr(self._object, ln="sPIDscaleX", at="float",
                       p="sPIDscale")
            pm.addAttr(self._object, ln="sPIDscaleY", at="float",
                       p="sPIDscale")
            pm.addAttr(self._object, ln="sPIDscaleZ", at="float",
                       p="sPIDscale")

    def setup_to_be_picked_up(self):
        """setups specified object for pick/release sequence
        """

        # if it is setup before, don't do anything
        if self._is_setup:
            return
        else:
            self._is_setup = True

        # if it is a referenced object and it is not on top of its
        # hierarchy the parents can't be created
        # 
        # so ask the user to use the function
        # in the original scene
        is_ref = self.is_referenced(self._object)

        parents = self.get_parents(self._object)
        parent_cnt = len(parents)

        # create attributes for data holding
        self.create_data_attribute()

        if is_ref:
            if parent_cnt == 0:
                # create parents
                self.create_stabilizer_parent()
                self.create_constrained_parent()

            elif parent_cnt == 1:
                # set the available parent as the stabilizer parent
                # and create constrainedParent
                self._stabilizer_parent = pm.nodetypes.DagNode(parents[0])
                self.create_constrained_parent()

            elif parent_cnt >= 2:
                # use directly the parents
                self._stabilizer_parent = pm.nodetypes.DagNode(parents[0])
                self._constrained_parent = pm.nodetypes.DagNode(parents[1])

        else: # is not referenced
            # create the parents
            self.create_stabilizer_parent()
            self.create_constrained_parent()

        # create localParent
        self.create_local_parent()

        # create the parent constraint
        self.create_parent_constraint()

        # set keyframe colors of the parentConstraint and stabilizerParent
        self.set_keyframe_colors()

        # save the settings
        self.save_settings()

        # create DAGMenu default commands
        # self.add_default_options_to_DAG_menu()

    def explode_setup(self):
        """breaks all the setup objects
        """
        if not self._is_setup:
            return

        # delete all the constraints
        pm.delete(self._parent_constraint)

        # delete stabilizer parent animation curves
        pm.delete(self._stabilizer_parent.attr('tx').inputs(),
                  self._stabilizer_parent.attr('ty').inputs(),
                  self._stabilizer_parent.attr('tz').inputs(),
                  self._stabilizer_parent.attr('rx').inputs(),
                  self._stabilizer_parent.attr('ry').inputs(),
                  self._stabilizer_parent.attr('rz').inputs(),
                  self._stabilizer_parent.attr('sx').inputs(),
                  self._stabilizer_parent.attr('sy').inputs(),
                  self._stabilizer_parent.attr('sz').inputs(), )

        # move the stabilizer parent to its default position
        # ( if there is a stabilizerParentInitialData attr )
        if self._object.hasAttr('stabilizerParentInitialData'):
            # position
            self._stabilizer_parent.setAttr('tx', self._object.getAttr(
                'pickedData.stabilizerParentInitialData.sPIDposition.sPIDpositionX'))
            self._stabilizer_parent.setAttr('ty', self._object.getAttr(
                'pickedData.stabilizerParentInitialData.sPIDposition.sPIDpositionY'))
            self._stabilizer_parent.setAttr('tz', self._object.getAttr(
                'pickedData.stabilizerParentInitialData.sPIDposition.sPIDpositionZ'))

            # rotation
            self._stabilizer_parent.setAttr('rx', self._object.getAttr(
                'pickedData.stabilizerParentInitialData.sPIDrotation.sPIDrotationX'))
            self._stabilizer_parent.setAttr('ry', self._object.getAttr(
                'pickedData.stabilizerParentInitialData.sPIDrotation.sPIDrotationY'))
            self._stabilizer_parent.setAttr('rz', self._object.getAttr(
                'pickedData.stabilizerParentInitialData.sPIDrotation.sPIDrotationZ'))

            # scale
            self._stabilizer_parent.setAttr('sx', self._object.getAttr(
                'pickedData.stabilizerParentInitialData.sPIDscale.sPIDscaleX'))
            self._stabilizer_parent.setAttr('sy', self._object.getAttr(
                'pickedData.stabilizerParentInitialData.sPIDscale.sPIDscaleY'))
            self._stabilizer_parent.setAttr('sz', self._object.getAttr(
                'pickedData.stabilizerParentInitialData.sPIDscale.sPIDscaleZ'))

        if self._object.hasAttr('pickedData.createdNodes'):
            # delete created nodes
            object_to_parent = None
            parent_obj = None

            nodes_to_delete = self._object.attr('pickedData.createdNodes').inputs()
            if self._constrained_parent in nodes_to_delete:
                # parent the stabilizer parent to the constrained parents
                # parent
                object_to_parent = self._stabilizer_parent
                parent_obj = self._constrained_parent.getParent()
                if self._stabilizer_parent in nodes_to_delete:
                    object_to_parent = self._object

            if object_to_parent is not None:
                if parent_obj is not None:
                    pm.parent(object_to_parent, parent_obj)
                else:
                    pm.parent(object_to_parent, w=True)

            # then delete the nodes
            pm.delete(nodes_to_delete)

        # delete picked data attribute on the object
        self._object.attr('pickedData').delete()

        # also delete special commands
        self._object.attr('specialCommands').delete()
        self._object.attr('specialCommandLabels').delete()

    def create_local_parent(self):
        """creates local parent and axial correction group of local parent
        """
        # create the localParent group
        self._local_parent = pm.group(
            em=True,
            n=self._object.name() + "_local_parent"
        )

        # move it to the same place where constrainedParent is
        matrix = pm.xform(self._constrained_parent, q=True, ws=True, m=True)
        pm.xform(self._local_parent, ws=True, m=matrix)

        # parent it to the constrained parents parent
        parents = pm.listRelatives(self._constrained_parent, p=True)

        if len(parents) != 0:
            temp = pm.parent(self._local_parent, parents[0], a=True)
            self._local_parent = temp[0]

        self._local_parent = pm.nodetypes.DagNode(self._local_parent)
        index = self._object.attr('pickedData.createdNodes').numElements()
        self._local_parent.attr('message') >> \
            self._object.attr('pickedData.createdNodes[' + str(index) + ']')

    def create_parent_constraint(self):
        """creates parentConstraint between _local_parent and the
        _constrained_parent
        """
        self._parent_constraint = pm.parentConstraint(
            self._local_parent,
            self._constrained_parent,
            w=1
        )

        # set also a keyframe for the localParent to weight 1

        # get the weight alias of localParent
        weight_alias = self.get_weight_alias(self._local_parent)

        frame = 0

        weight_alias.setKey(t=frame, ott="step")

        self.set_stabilizer_keyframe(frame)

    def set_stabilizer_keyframe(self, frame):
        """sets keyframe for stabilizer at the current values
        """
        # set keyframes for stabilizerParent
        self._stabilizer_parent.attr('tx').setKey(t=frame, ott='step')
        self._stabilizer_parent.attr('ty').setKey(t=frame, ott='step')
        self._stabilizer_parent.attr('tz').setKey(t=frame, ott='step')

        self._stabilizer_parent.attr('rx').setKey(t=frame, ott='step')
        self._stabilizer_parent.attr('ry').setKey(t=frame, ott='step')
        self._stabilizer_parent.attr('rz').setKey(t=frame, ott='step')

        self._stabilizer_parent.attr('sx').setKey(t=frame, ott='step')
        self._stabilizer_parent.attr('sy').setKey(t=frame, ott='step')
        self._stabilizer_parent.attr('sz').setKey(t=frame, ott='step')

    def get_parents(self, node):
        """returns hierarchical parents of the given node
        """
        node = pm.nodetypes.DagNode(node)

        # TODO: fix this when they fix pymel
        # pymel bug
        # this raises a NameError
        # hope them fix later
        # return  node.getAllParents()
        parents = node.getParent(generations=None)
        if parents is None:
            parents = []

        return parents

    def is_referenced(self, node):
        """checks if the node is referenced\n
        returns True or False
        """
        node = pm.nodetypes.DagNode(node)

        return node.isReferenced()

    def create_stabilizer_parent(self):
        """creates the stabilizer parent
        """
        # the new stabilizer parent should be at the origin of the original
        # objects parent so that the keyframes of the object should not be altered

        self._stabilizer_parent = pm.nodetypes.DagNode(
            auxiliary.axial_correction_group(
                self._object,
                to_parents_origin=True
            )
        )

        self._stabilizer_parent = pm.nodetypes.DagNode(
            pm.rename(
                self._stabilizer_parent,
                self._object.name() + "_stabilizer_parent"
            )
        )

        # connect it to the created nodes attribute
        index = self._object.attr('pickedData.createdNodes').numElements()
        self._stabilizer_parent.attr('message') >> \
            self._object.attr('pickedData.createdNodes[' + str(index) + ']')

    def create_constrained_parent(self):
        """creates parents for the object
        """
        # check if there is a stabilizerParent
        try:
            pm.nodetypes.DagNode(self._stabilizer_parent)
        except pm.MayaNodeError:
            return

        self._constrained_parent = pm.nodetypes.DagNode(
            auxiliary.axial_correction_group(self._stabilizer_parent))
        self._constrained_parent = pm.nodetypes.DagNode(
            pm.rename(self._constrained_parent,
                      self._object.name() + "_constrained_parent"))

        index = self._object.attr('pickedData.createdNodes').numElements()
        self._constrained_parent.attr('message') >> \
            self._object.attr('pickedData.createdNodes[' + str(index) + ']')

    def get_weight_alias_list(self):
        """returns weight alias list
        """
        if not self._is_setup:
            return

        return self._parent_constraint.getWeightAliasList()

    def get_active_parent(self):
        """returns the current parent
        """
        if not self._is_setup:
            return

        # from all the weightAlias return the one with weight 1
        weight_aliases = self.get_weight_alias_list()
        parents = self.get_parent_list()

        for i in range(0, len(weight_aliases)):
            if weight_aliases[i].get() >= 1:
                return parents[i]

        return None

    def get_parent_list(self):
        """returns parent list
        """
        if not self._is_setup:
            return

        return self._parent_constraint.getTargetList()

    def get_weight_alias(self, parent):
        """finds weightAlias of given parent\n
        if it couldn't find any it returns None
        """
        if not self._is_setup:
            return

        parent = pm.nodetypes.DagNode(parent)

        assert isinstance(parent, pm.nodetypes.Transform)

        weight_alias_list = self.get_weight_alias_list()
        parent_list = self.get_parent_list()

        weight_alias = None

        for i in range(len(parent_list)):
            if parent_list[i] == parent:
                weight_alias = weight_alias_list[i]
                break

        return weight_alias

    def add_new_parent(self, parent):
        """adds a new parent
        """
        if not self._is_setup:
            return

        parent = pm.nodetypes.DagNode(parent)

        # check if this object is already a parent
        if self.get_weight_alias(parent) is not None:
            return

        # check if there is a cycle between parent and self._object
        if self.check_cycle(parent):
            pm.PopupError(
                "Cycle Warning!!!\nnode is one of the special objects")
            return

        # create parent constraint between new parent and constrained parent
        pm.parentConstraint(parent, self._constrained_parent, w=0, mo=True)

        # set a keyframe for the new parent
        weight_alias = self.get_weight_alias(parent)
        weight_alias.setKey(t=0, v=0, ott='step')

        # add the parent to the DAG Menu
        self.add_parent_to_dag_menu(parent)

    def add_parent_to_dag_menu(self, parent):
        """adds the given parent to the DAG menu

        oyParSw - switch to --> %PARENTNAME%
        """
        # simply add "python(import oyObjectPicker as oyOP; oyOP.setObjectsParentTo( %s, %s+\".pickedData.constrainedParent[ %number% ]\" ))"

        command_label = "oyObjectPicker - switch to --> " + parent.name()
        parent_index = self.get_parent_index(parent)

        if parent_index == -1:
            return

        command_string = "{\n \
        int $parentIndex = " + str(parent_index) + ";\n \
        string $parentConstraint[] = `listConnections (\"%s.pickedData.parentConstraint\")`;\n \
        string $parents[] = `parentConstraint -q -tl $parentConstraint[0]`;\n \
        string $parentName = $parents[ $parentIndex ];\n \
        python(\"import oyObjectPicker as oyOP; oyOP.set_objects_parent( '%s', '\"+$parentName+\"')\");\n \
        }"

        # pm.mel.source("oyAddDAGMenuCommands")
        # pm.mel.oyADMC_addSpecialCommandsToObject(
        #     self._object.name(), commandLabel, command_string
        # )

    def add_default_options_to_dag_menu(self):
        """adds the default menu options to the DAG menu

        oyObjectPicker --> fix jump
        oyObjectPicker --> edit keyframes
        """
        pm.mel.source("oyAddDAGMenuCommands")

        command_label = "oyObjectPicker --> release object"
        command_string = "python(\"import oyObjectPicker as oyOP; oyOP.relaseObjectWithName('%s')\");"
        pm.mel.oyADMC_addSpecialCommandsToObject(
            self._object.name(),
            command_label,
            command_string
        )

        command_label = "oyObjectPicker --> edit_keyframes"
        command_string = "python(\"import oyObjectPicker as oyOP; oyOP.edit_keyframes_of_object('%s')\");"
        pm.mel.oyADMC_addSpecialCommandsToObject(
            self._object.name(),
            command_label,
            command_string
        )

        command_label = "oyObjectPicker --> fix jump"
        command_string = "python(\"import oyObjectPicker as oyOP; oyOP.fix_jump_on_object('%s')\");"
        pm.mel.oyADMC_addSpecialCommandsToObject(
            self._object.name(),
            command_label,
            command_string
        )

    def get_parent_index(self, parent):
        """returns the given parents index
        """
        parent = pm.nodetypes.DagNode(parent)

        parents = self.get_parent_list()

        for i in range(0, len(parents)):
            if parents[i] == parent.name():
                return i

        return -1

    def get_parent_name_at_index(self, index):
        """returns the parent name at the index

        the index is used in the parent list of the parent constraint
        """
        parents = self.get_parent_list()
        return parents[index]

    def check_cycle(self, node):
        """checks if the given parent is a child of the self._object
        or if it is setup before to be the pickedObject and self._object
        is a parent for it
        """
        # CHECK LEVEL 1
        # check if parent is one of the special object
        if self.is_special_object(node):
            return True

        # CHECK LEVEL 2
        # check if its a pickedObject and self._object is a parent for node

        # create a PickedObject with parent and get the parent list
        node = pm.nodetypes.DagNode(node)
        node_as_picked_object = PickedObject(node)

        parent_list = node_as_picked_object.get_parent_list()

        if parent_list is None:
            return False
        elif len(parent_list) != 0:
            # TRUE if one of the parents of the node is self._object
            if self._object in parent_list:
                return True

            # TRUE if one of the parents of the node is a special object
            for p in parent_list:
                if self.is_special_object(p):
                    return True
        else:
            return False

    def is_special_object(self, node):
        """checks if node is one of the special object:\n
        constrainedParent
        stabilizerParent
        localParent
        """
        node = pm.nodetypes.DagNode(node)

        if node == self._object or\
           node == self._constrained_parent or\
           node == self._local_parent or\
           node == self._stabilizer_parent:
            return True
        else:
            return False

    def set_active_parent(self, parent):
        """sets specified parent as the active parent
        """
        if not self._is_setup:
            return

        parent = pm.nodetypes.DagNode(parent)

        # get the active parent
        # if it is the same parent return
        active_parent = self.get_active_parent()
        if parent == active_parent:
            return

        # get the weightAlias of the specified parent
        parent_weight_alias = self.get_weight_alias(parent)

        # setup a new parent if it is not in the list
        if parent_weight_alias is None:
            # for now just return without doing anything
            return

        # get the worldMatrix of the stabilizerParent
        self.set_dg_dirty()
        matrix = self.get_stabilizer_matrix()

        # set the weight of the other parents to 0 and the current to 1
        self.set_parent_weight(parent)

        # fix dirty flag bug
        self.set_dg_dirty()

        # move the stabilizer to its new position
        self.set_stabilizer_matrix(matrix)

        # set keyframe for stabilizer
        self.set_stabilizer_keyframe(pm.currentTime(q=True))

    def set_dg_dirty(self):
        """sets the DG to dirty for parentConstraint, constrainedParent and
        stabilizerParent
        """
        pm.dgdirty(
            self._parent_constraint,
            self._constrained_parent,
            self._stabilizer_parent
        )

    def set_parent_weight(self, parent):
        """sets the weight of the parent to 1 and the others to 0
        """
        parent = pm.nodetypes.DagNode(parent)

        # get the weightAlias of the parent
        parent_weight_alias = self.get_weight_alias(parent)

        # set the weight of the other parents to 0 and the current to 1
        weight_alias_list = self.get_weight_alias_list()

        for weightAlias in weight_alias_list:
            if weightAlias == parent_weight_alias:
                weightAlias.setKey(v=1, ott="step")
            else:
                current_weight = weightAlias.get()
                if current_weight > 0:
                    weightAlias.setKey(v=0, ott="step")

    def release_object(self):
        """release the object
        """
        if not self._is_setup:
            return

        # set_active_parent to localParent
        self.set_active_parent(self._local_parent)

    def fix_jump(self):
        """fixes the jump in current frame
        """
        if not self._is_setup:
            return

        # delete the current parent key and set it again
        parent = self.get_active_parent()

        # remove the parent key at the current frame
        self.delete_current_parent_key()

        # and set the active parent again
        self.set_active_parent(parent)

    def get_stabilizer_matrix(self):
        """returns stabilizer matrix
        """
        return pm.xform(self._stabilizer_parent, q=True, ws=True, m=True)

    def set_stabilizer_matrix(self, matrix):
        """sets stabilizer matrix to matrix
        """
        pm.xform(self._stabilizer_parent, ws=True, m=matrix)

    def select_anim_curves(self):
        """selects animCurves of parentConstraint and stabilizerParent nodes for
        keyframe editing
        """
        if not self._is_setup:
            return

        pm.select(
            auxiliary.get_anim_curves(self._parent_constraint),
            auxiliary.get_anim_curves(self._stabilizer_parent)
        )

    def set_keyframe_colors(self):
        """sets the keyframe colors for the parentConstraint and stabilizerParent
        """
        # get all anim_curves
        anim_curves = auxiliary.get_anim_curves(self._parent_constraint) + \
            auxiliary.get_anim_curves(self._stabilizer_parent)

        color = [0, 1, 0]  # green

        # set anim curve colors to green
        for animCurve in anim_curves:
            auxiliary.set_anim_curve_color(animCurve, color)

    def delete_parent_key(self, frame):
        """deletes parent keyframes at the given keyframe
        """
        if not self._is_setup:
            return

        pm.cutKey(
            self._parent_constraint,
            self._stabilizer_parent,
            cl=True,
            time=(frame, frame)
        )

    def delete_current_parent_key(self):
        """deletes parent keyframes at the current keyframe
        """
        current_frame = pm.currentTime(q=True)
        self.delete_parent_key(current_frame)


def set_parent():
    selection = pm.ls(sl=True)

    if len(selection) >= 2:
        parent = selection[0]
        _object = selection[1]

        set_objects_parent(_object, parent)

    else:
        pm.PopupError(
            "please select first the parent, secondly the child object!!!")


def set_objects_parent(object_, parent):
    selection = pm.ls(sl=True)

    my_picked_obj = PickedObject(object_)

    # before setting up check if there is a cycle with the parent
    if my_picked_obj.check_cycle(parent):
        object_ = pm.nodetypes.DagNode(object_)
        parent = pm.nodetypes.DagNode(parent)
        pm.PopupError(
            "CYCLE ERROR!!!\n%s is a parent or special object for %s" %
            (object_.name(), parent.name())
        )
        # do not setup any object
        return

    my_picked_obj.setup_to_be_picked_up()
    my_picked_obj.add_new_parent(parent)
    my_picked_obj.set_active_parent(parent)
    # reselect selList
    pm.select(selection)


def release_object():
    selection = pm.ls(sl=True)
    if len(selection) <= 0:
        return

    release_object_with_name(selection[0])

    # reselect selection
    pm.select(selection)


def release_object_with_name(object_):
    my_picked_obj = PickedObject(object_)
    my_picked_obj.release_object()


def edit_keyframes():
    sel_list = pm.ls(sl=True)
    if len(sel_list) <= 0:
        return
    edit_keyframes_of_object(sel_list[0])


def edit_keyframes_of_object(node):
    my_picked_obj = PickedObject(node)
    my_picked_obj.select_anim_curves()


def fix_jump():
    sel_list = pm.ls(sl=True)
    fix_jump_on_object(sel_list[0])

    # reselect sel_list
    pm.select(sel_list)


def fix_jump_on_object(node):
    my_picked_obj = PickedObject(node)
    my_picked_obj.fix_jump()


def explode_setup():
    objects = pm.ls(sl=1)
    for obj in objects:
        my_picked_obj = PickedObject(obj)
        my_picked_obj.explode_setup()
