# -*- coding: utf-8 -*-
# Copyright (c) 2012-2015, Anima Istanbul
#
# This module is part of anima-tools and is released under the BSD 2
# License: http://www.opensource.org/licenses/BSD-2-Clause
"""Fix Bound Joint

v0.1.0

Description
-----------

Fixes bound joints to the correct worldOrientation in connected skinClusters

Usage
-----

Select a joint which is an influence for a skinCluster, open up the script UI,
select "freeze transformations" if you want to zero rotation values, select
"Apply to children" if you want to apply the same fix to child joints...

Change Log
----------

0.1.0
-----

- Moved the script to Python
- It also fixes any joint with input connection, thus it can fix joints which
  are in character set or have an input connection

"""

__version__ = "0.1.0"

import pymel.core as pm


def UI():
    """The UI of the script
    """

    window_width = 153
    window_height = 80

    window_name = "oyFixBoundJoint_Window"
    if pm.window(window_name, ex=True):
        pm.deleteUI(window_name, window=True)

    window = pm.window(
        window_name,
        tlb=True,
        title="fixBoundJoint " + __version__,
        widthHeight=(window_width, window_height)
    )

    pm.columnLayout("FBJ_columnLayout1", adj=True)

    pm.checkBox(
        "FBJ_checkBox1",
        l="Freeze transformations",
        al="left",
        v=1
    )

    pm.checkBox(
        "FBJ_checkBox2",
        l="Apply to children",
        al="left"
    )

    pm.button(
        "FBJ_button1",
        l="Apply",
        c=get_check_box_states_and_run
    )

    pm.setParent()

    window.show()
    window.setWidthHeight(val=(window_width, window_height))


def get_check_box_states_and_run(*args, **kwargs):
    """Gets the data from UI and runs the script
    """
    freeze = pm.checkBox("FBJ_checkBox1", q=True, v=True)
    apply_to_children = pm.checkBox("FBJ_checkBox2", q=True, v=True)
    selection_list = pm.ls(sl=1, type="joint")
    do_fix(selection_list, freeze, apply_to_children)
    pm.select(selection_list)


def do_fix(joints, freeze=True, apply_to_children=False):
    """Fixes the given list of bound joints by copying the current worldMatrix
    information to the related skinClusters.

    :param freeze: If freeze is given as True (default) it will also set the
      rotations of the joint to (0, 0, 0). The default value is True.

    :param apply_to_children: If given as True it will also apply the operation
      to the children of the given joints
    """
    new_selection_list = joints

    if apply_to_children:
        pm.select(joints, hi=True)
        new_selection_list = pm.ls(sl=1, type="joint")

    for joint in new_selection_list:

        connections = joint.worldMatrix.outputs(
            c=1,
            p=1,
            t="skinCluster",
            et=True
        )

        if freeze:
            freeze_joint(joint)

        matrix = joint.worldInverseMatrix.get()

        for attribute_data in connections:
            skinCluster_attribute = attribute_data[1]
            skinCluster_node = skinCluster_attribute.node()
            index = skinCluster_attribute.index()

            skinCluster_node.bindPreMatrix[index].set(matrix)


def freeze_joint(joint):
    """Freezes the given joint by duplicating it and applying the freeze to the
    duplicate and then copy the joint orientation values to the original joint.

    :param joint: The joint which wanted to be frozen
    """
    dup_joint = pm.duplicate(joint, rc=1)[0]

    # if the duplicate has any children delete them
    pm.delete(dup_joint.getChildren())

    # unlock rotate channels
    dup_joint.rotateX.unlock()
    dup_joint.rotateY.unlock()
    dup_joint.rotateZ.unlock()

    # freeze the joint
    pm.makeIdentity(dup_joint, apply=1, r=1)

    # set rotation to zero
    if not joint.rotateX.isLocked():
        joint.rotateX.set(0)
    else:
        # unlock and lock it again
        joint.rotateX.unlock()
        joint.rotateX.set(0)
        joint.rotateX.lock()

    if not joint.rotateY.isLocked():
        joint.rotateY.set(0)
    else:
        # unlock and lock it again
        joint.rotateY.unlock()
        joint.rotateY.set(0)
        joint.rotateY.lock()

    if not joint.rotateZ.isLocked():
        joint.rotateZ.set(0)
    else:
        # unlock and lock it again
        joint.rotateZ.unlock()
        joint.rotateZ.set(0)
        joint.rotateZ.lock()

    # get the joint orient
    joint.jointOrient.set(dup_joint.jointOrient.get())

    # delete the duplicate joint
    pm.delete(dup_joint)
