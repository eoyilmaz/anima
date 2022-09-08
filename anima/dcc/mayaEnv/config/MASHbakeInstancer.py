# MASHbakeInstancer
# This function takes an instancer, and turns all the particles being fed into it to
# real geometry.

from builtins import range
import maya.cmds as cmds
import maya.OpenMaya as om
import maya.OpenMayaFX as omfx
import gc


def mashGetMObjectFromName(node_name):
    sel = om.MSelectionList()
    sel.add(node_name)
    this_node = om.MObject()
    sel.getDependNode(0, this_node)
    return this_node


def MASHbakeInstancer():
    # if animation is true, the playback range will be baked, otherwise just this frame
    # will be.
    animation_flag = False
    # set settings
    translate_flag = True
    rotation_flag = True
    scale_flag = True
    visibility_flag = True
    bake_to_instances_flag = True
    express_baking = True
    flush_undo = True
    garbage_collect = True

    if express_baking:
        script_editor_open = cmds.window("scriptEditorPanel1Window", exists=True)
        if script_editor_open:
            cmds.deleteUI("scriptEditorPanel1Window", window=True)
            cmds.flushIdleQueue()

    # get the selection
    li = []
    l = cmds.ls(sl=True) or []
    # check it's an instancer
    for instancerNode in l:
        if cmds.nodeType(instancerNode) != "instancer":
            continue
        li.append(instancerNode)

    # did we find at least 1?
    if len(li) == 0:
        raise Exception("Select an instancer node.")

    l = []

    for instancerNode in li:
        cmds.select(instancerNode)
        # reused vars for the particles
        m = om.MMatrix()
        dp = om.MDagPath()
        dpa = om.MDagPathArray()
        sa = om.MScriptUtil()
        sa.createFromList([0.0, 0.0, 0.0], 3)
        sp = sa.asDoublePtr()

        # Get the instancer function set
        thisNode = mashGetMObjectFromName(instancerNode)
        fnThisNode = om.MFnDependencyNode(thisNode)

        # start frame, end frame, animation
        sf = int(cmds.playbackOptions(q=True, min=True)) - 1
        ef = int(cmds.playbackOptions(q=True, max=True)) + 2

        if animation_flag == False:
            sf = cmds.currentTime(query=True)
            ef = sf + 1

        for i in range(int(sf), int(ef)):
            # set the time
            cmds.currentTime(i)
            g = instancerNode + "_objects"

            # get the visibility array - which isn't provided by the MFnInstancer
            # function set
            in_points_attribute = fnThisNode.attribute("inputPoints")
            in_points_plug = om.MPlug(thisNode, in_points_attribute)
            in_points_obj = in_points_plug.asMObject()
            input_pp_data = om.MFnArrayAttrsData(in_points_obj)
            visibility_exists = input_pp_data.checkArrayExist("visibility")
            if visibility_exists[0]:
                vis_list = input_pp_data.getDoubleData("visibility")[:]
            else:
                vis_list = []

            # if this is the first frame, create a transform to store everything under
            if i == sf:
                if cmds.objExists(g) is True:
                    cmds.delete(g)
                g = cmds.createNode("transform", n=g)
                l.append(g)

            # get the instancer
            sl = om.MSelectionList()
            sl.add(instancerNode)
            sl.getDagPath(0, dp)
            # create MFnInstancer function set
            fni = omfx.MFnInstancer(dp)

            if len(vis_list) == 0:
                vis_list = [True] * fni.particleCount()

            # cycle through the particles
            for j in range(fni.particleCount()):
                visibility = vis_list[j]
                # get the instancer object
                fni.instancesForParticle(j, dpa, m)
                for ki in range(dpa.length()):
                    # get the instancer object name
                    full_path_name = dpa[ki].partialPathName()
                    # support namespaces, references, crap names
                    name_space_removed = full_path_name.rsplit(":", 1)[-1]
                    pipes_removed = name_space_removed.rsplit("|", 1)[-1]
                    num_created_points = len(cmds.listRelatives(g, shapes=False) or [])
                    n = pipes_removed + "_" + instancerNode + "_" + str(j)

                    # if we haven't got a node with the new name, make one,
                    # give it a safe name (which we will continue to identify it by).
                    if cmds.objExists(n) is False:
                        # duplicate the object
                        if bake_to_instances_flag:
                            n2 = cmds.instance(dpa[ki].fullPathName(), leaf=True)[0]
                        else:
                            n2 = cmds.duplicate(
                                dpa[ki].fullPathName(), rr=True, un=True
                            )[0]
                        # rename it to the safe name
                        n = cmds.rename(n2, n, ignoreShape=bake_to_instances_flag)

                        # parent it to the transform we created above
                        if cmds.listRelatives(n, p=True) != g:
                            try:
                                n = cmds.parent(n, g)[0]
                            except:
                                pass

                        # if the object doesn't appear on frame 0 (animated creation),
                        # set the visibility when it first appears
                        cmds.setKeyframe(
                            n + ".visibility", v=0, t=cmds.currentTime(q=True) - 1
                        )
                        cmds.setKeyframe(n + ".visibility", v=1)

                    # empty transformMatrix for the particle
                    tm = om.MTransformationMatrix(m)
                    instanced_path = dpa[ki]
                    # get the matrix from the instancer
                    instanced_path_matrix = instanced_path.inclusiveMatrix()
                    final_matrix_for_path = instanced_path_matrix * m
                    final_point = om.MPoint.origin * final_matrix_for_path

                    t = tm.getTranslation(om.MSpace.kWorld)
                    # set the translate
                    try:
                        cmds.setAttr(
                            n + ".t", final_point.x, final_point.y, final_point.z
                        )
                        if translate_flag and animation_flag:
                            cmds.setKeyframe(n + ".t")
                    except:
                        pass

                    # set the rotate
                    r = tm.eulerRotation().asVector()
                    try:
                        cmds.setAttr(
                            n + ".r",
                            r[0] * 57.2957795,
                            r[1] * 57.2957795,
                            r[2] * 57.2957795,
                        )
                        if rotation_flag and animation_flag:
                            cmds.setKeyframe(n + ".r")
                    except:
                        pass

                    # set the scale
                    tm.getScale(sp, om.MSpace.kWorld)
                    if scale_flag:
                        double_array_item = lambda i: om.MScriptUtil.getDoubleArrayItem(
                            sp, i
                        )
                        sx, sy, sz = (
                            double_array_item(0),
                            double_array_item(1),
                            double_array_item(2),
                        )

                        s = om.MTransformationMatrix(
                            dpa[ki].inclusiveMatrix()
                        ).getScale(sp, om.MSpace.kWorld)
                        sx2, sy2, sz2 = (
                            double_array_item(0),
                            double_array_item(1),
                            double_array_item(2),
                        )

                        try:
                            cmds.setAttr(n + ".s", sx * sx2, sy * sy2, sz * sz2)
                            if animation_flag:
                                cmds.setKeyframe(n + ".s")
                        except:
                            pass

                    # set visibility
                    if visibility_flag:
                        cmds.setAttr(n + ".v", visibility)
                        if animation_flag:
                            cmds.setKeyframe(n + ".v")

        # flush undo
        if flush_undo:
            cmds.flushUndo()

        # python garbage collect
        if garbage_collect:
            gc.collect()


# ===========================================================================
# Copyright 2021 Autodesk, Inc. All rights reserved.
#
# Use of this software is subject to the terms of the Autodesk license
# agreement provided at the time of installation or download, or which
# otherwise accompanies this software in either electronic or hard copy form.
# ===========================================================================
