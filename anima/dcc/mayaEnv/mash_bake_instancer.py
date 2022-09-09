# -*- coding: utf-8 -*-
# ===========================================================================
# Copyright 2021 Autodesk, Inc. All rights reserved.
#
# Use of this software is subject to the terms of the Autodesk license
# agreement provided at the time of installation or download, or which
# otherwise accompanies this software in either electronic or hard copy form.
# ===========================================================================
"""mash_bake_instancer

This is based on Autodesk's version. But heavily edited and modernized with PyMEL.

This function takes an instancer, and turns all the particles being fed into it to
real geometry.
"""

import pymel.core as pm
import maya.OpenMaya as om
import gc


def mash_bake_instancer():
    """Bake MASH related instancer nodes."""
    # if animation is true, the playback range will be baked, otherwise just this frame
    # will be.

    # set settings
    animation_flag = False
    translate_flag = True
    rotation_flag = True
    scale_flag = True
    visibility_flag = True
    bake_to_instances_flag = True

    # Optimization settings
    express_baking = True
    flush_undo = True
    garbage_collect = True

    if express_baking:
        script_editor_open = pm.window("scriptEditorPanel1Window", q=True, exists=True)
        if script_editor_open:
            pm.deleteUI("scriptEditorPanel1Window", window=True)
            pm.flushIdleQueue()

    instancers = pm.ls(sl=True, type=pm.nt.Instancer)
    if len(instancers) == 0:
        raise Exception("Select an instancer node.")

    selection_list = []

    for instancer in instancers:
        # store the list of instanced objects in this instancer
        instanced_transforms = instancer.inputHierarchy.inputs()

        # start frame, end frame, animation
        start_frame = int(pm.playbackOptions(q=True, min=True)) - 1
        end_frame = int(pm.playbackOptions(q=True, max=True)) + 2

        if animation_flag is False:
            start_frame = pm.currentTime(q=True)
            end_frame = start_frame + 1

        for frame in range(int(start_frame), int(end_frame)):
            # set the time
            pm.currentTime(frame)
            group_name = "{}_objects".format(instancer.name())

            # get the visibility array - which isn't provided by the MFnInstancer
            # function set
            in_points_attribute = instancer.inputPoints
            in_points_plug = in_points_attribute.__apimplug__()
            in_points_obj = in_points_plug.asMObject()
            input_pp_data = om.MFnArrayAttrsData(in_points_obj)

            visibility_exists = input_pp_data.checkArrayExist("visibility")
            if visibility_exists[0]:
                vis_list = input_pp_data.getDoubleData("visibility")[:]
            else:
                vis_list = []

            # if this is the first frame, create a transform to store everything under
            if frame == start_frame:
                if pm.objExists(group_name) is True:
                    pm.delete(group_name)
                group = pm.createNode("transform", n=group_name)
                selection_list.append(group)

            if len(vis_list) == 0:
                vis_list = [True] * instancer.particleCount()

            # cycle through the particles
            for particle_index in range(instancer.particleCount()):
                visibility = vis_list[particle_index]
                # get the instancer object
                instance_data = instancer.instancesForParticle(particle_index)
                instanced_shape = instance_data[1][0]
                matrix = instance_data[2]
                # get the related transform from the instanced_objects

                instanced_transform = [
                    node for node in instanced_shape.getAllParents()
                    if node in instanced_transforms
                ][0]

                # get the instancer object name
                full_path_name = instanced_transform.fullPath()
                # support namespaces, references, crap names
                name_space_removed = full_path_name.rsplit(":", 1)[-1]
                pipes_removed = name_space_removed.rsplit("|", 1)[-1]
                new_name = pipes_removed + "_" + instancer + "_" + str(particle_index)

                # if we haven't got a node with the new name, make one,
                # give it a safe name (which we will continue to identify it by).
                if pm.objExists(new_name) is False:
                    # duplicate the object
                    if bake_to_instances_flag:
                        new_node = pm.instance(instanced_transform)[0]
                    else:
                        new_node = pm.duplicate(instanced_transform, rr=True, un=True)[0]

                    # rename it to the safe name
                    new_node.rename(new_name, ignoreShape=bake_to_instances_flag)

                    # parent it to the transform we created above
                    if new_node.listRelatives(p=True) != group:
                        try:
                            pm.parent(new_node, group)[0]
                        except:
                            pass

                    # if the object doesn't appear on frame 0 (animated creation),
                    # set the visibility when it first appears
                    pm.setKeyframe(new_node.visibility, v=0, t=frame - 1)
                    pm.setKeyframe(new_node.visibility, v=1)

                # empty transformMatrix for the particle

                # get the matrix from the instancer
                instanced_path_matrix = new_node.worldMatrix.get()
                final_matrix_for_path = instanced_path_matrix * matrix
                final_point = pm.dt.Point.origin * final_matrix_for_path
                # set the translate
                try:
                    new_node.t.set(final_point.x, final_point.y, final_point.z)
                    if translate_flag and animation_flag:
                        pm.setKeyframe(new_node.t)
                except:
                    pass

                # set the rotate
                rot = matrix.rotate.asEulerRotation()
                try:
                    new_node.r.set(
                        rot[0] * 57.29577951308232,
                        rot[1] * 57.29577951308232,
                        rot[2] * 57.29577951308232,
                    )
                    if rotation_flag and animation_flag:
                        pm.setKeyframe(new_node.r)
                except:
                    pass

                # set the scale
                scale = matrix.scale
                if scale_flag:
                    s = new_node.worldMatrix.get().scale
                    try:
                        new_node.s.set(scale.x * s.x, scale.y * s.y, scale.z * s.z)
                        if animation_flag:
                            pm.setKeyframe(new_node.s)
                    except:
                        pass

                # set visibility
                if visibility_flag:
                    new_node.v.set(visibility)
                    if animation_flag:
                        pm.setKeyframe(new_node.v)

        # flush undo
        if flush_undo:
            pm.flushUndo()

        # python garbage collect
        if garbage_collect:
            gc.collect()
