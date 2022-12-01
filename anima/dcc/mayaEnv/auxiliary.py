# -*- coding: utf-8 -*-

import copy
import json
import os
import re
import tempfile

import pymel.core as pm

from anima import logger, ALEMBIC, USD, CACHE_FORMAT_DATA
import anima.utils
from anima.utils.progress import ProgressManager

FIRST_CAP_RE = re.compile("(.)([A-Z][a-z]+)")
ALL_CAP_RE = re.compile("([a-z0-9])([A-Z])")
VERSION_NUMBER_RE = r"([\w\d/_\:\$]+v)([0-9]+)([\w\d._]+)"


def kill_all_torn_off_panels():
    """deletes all torn off panels"""
    panel_list = pm.getPanel(type="modelPanel")

    # remove all torn off panels
    for panel in panel_list:
        if panel.getTearOff():
            panel.delete(pnl=1)


def maximize_first_model_panel():
    """maximizes the first model panel it can find

    :return:
    """
    panel_list = pm.getPanel(type="modelPanel")
    if len(panel_list) == 0:
        return

    # maximize one panel in default layout
    g_main_pane = pm.melGlobals["gMainPane"]

    pane_config = pm.paneLayout(g_main_pane, q=1, configuration=1)
    if pane_config != "single":
        # call mel here
        pm.mel.eval('doSwitchPanes(1, { "single", "%s"})' % panel_list[0])
        pm.mel.eval("updateToolbox();")


def get_valid_dag_node(node):
    """returns a valid dag node even the input is string"""
    try:
        dag_node = pm.nodetypes.DagNode(node)
    except pm.MayaNodeError:
        print("Error: no node named : %s" % node)
        return None

    return dag_node


def get_valid_node(node):
    """returns a valid PyNode even the input is string"""
    try:
        PyNode = pm.PyNode(node)
    except pm.MayaNodeError:
        print("Error: no node named : %s" % node)
        return None

    return PyNode


def get_anim_curves(node):
    """returns all the animation curves connected to the
    given node
    """
    # list all connections to the node
    connected_nodes = pm.listConnections(node)

    anim_curve = "animCurve"

    return_list = []
    for cNode in connected_nodes:
        if pm.nodeType(cNode)[0 : len(anim_curve)] == anim_curve:
            return_list.append(cNode)

    return return_list


def set_anim_curve_color(anim_curve, color):
    """sets animCurve color to color"""
    anim_curve = get_valid_node(anim_curve)
    anim_curve.setAttr("useCurveColor", True)
    anim_curve.setAttr("curveColor", color, type="double3")


def axial_correction_group(
    obj, to_parents_origin=False, name_prefix="", name_postfix="_ACGroup#"
):
    """creates a new parent to zero out the transformations

    if to_parents_origin is set to True, it doesn't zero outs the
    transformations but creates a new parent at the same place of the original
    parent

    :returns: pymel.core.nodeTypes.Transform
    """
    obj = get_valid_dag_node(obj)

    if name_postfix == "":
        name_postfix = "_ACGroup#"

    ac_group = pm.group(em=True, n=(name_prefix + obj.name() + name_postfix))

    ac_group = pm.parent(ac_group, obj)[0]

    pm.setAttr(ac_group + ".t", [0, 0, 0])
    pm.setAttr(ac_group + ".r", [0, 0, 0])
    pm.setAttr(ac_group + ".s", [1, 1, 1])

    parent = pm.listRelatives(obj, p=True)
    if len(parent) != 0:
        pm.parent(ac_group, parent[0], a=True)
    else:
        pm.parent(ac_group, w=True)

    if to_parents_origin:
        pm.setAttr(ac_group + ".t", [0, 0, 0])
        pm.setAttr(ac_group + ".r", [0, 0, 0])
        pm.setAttr(ac_group + ".s", [1, 1, 1])

    pm.parent(obj, ac_group, a=True)

    # for joints also set the joint orient to zero
    if isinstance(obj, pm.nodetypes.Joint):
        # set the joint rotation and joint orient to zero
        obj.setAttr("r", (0, 0, 0))
        obj.setAttr("jo", (0, 0, 0))

    # do extra steps if this is a cluster
    cluster_handle = obj.getShape()
    if isinstance(cluster_handle, pm.nt.ClusterHandle):
        t = cluster_handle.origin.get()
        ac_group.t.set(*t)
        cluster_handle.origin.set(0, 0, 0)
        cluster_transform = obj
        cluster_transform.rp.set(0, 0, 0)
        cluster_transform.sp.set(0, 0, 0)

        cluster = cluster_transform.worldMatrix[0].outputs(type=pm.nt.Cluster)[0]
        cluster_transform.worldInverseMatrix[0] >> cluster.bindPreMatrix
        cluster.bindPreMatrix.disconnect()

    return ac_group


def go_home(node):
    """sets all the transformations to zero"""
    if node.attr("t").isSettable():
        node.setAttr("t", (0, 0, 0))
    if node.attr("r").isSettable():
        node.setAttr("r", (0, 0, 0))
    if node.attr("s").isSettable():
        node.setAttr("s", (1, 1, 1))


def rivet():
    """the python version of the famous rivet setup from Bazhutkin"""
    selection_list = pm.filterExpand(sm=32)

    if selection_list is not None and len(selection_list) > 0:
        size = len(selection_list)
        if size != 2:
            raise pm.MayaObjectError("No two edges selected")

        edge1 = pm.PyNode(selection_list[0])
        edge2 = pm.PyNode(selection_list[1])

        edge1Index = edge1.indices()[0]
        edge2Index = edge2.indices()[0]

        shape = edge1.node()

        cFME1 = pm.createNode("curveFromMeshEdge", n="rivetCurveFromMeshEdge#")
        cFME1.setAttr("ihi", 1)
        cFME1.setAttr("ei[0]", edge1Index)

        cFME2 = pm.createNode("curveFromMeshEdge", n="rivetCurveFromMeshEdge#")
        cFME2.setAttr("ihi", 1)
        cFME2.setAttr("ei[0]", edge2Index)

        loft = pm.createNode("loft", n="rivetLoft#")
        loft.setAttr("ic", s=2)
        loft.setAttr("u", 1)
        loft.setAttr("rsn", 1)

        pOSI = pm.createNode("pointOnSurfaceInfo", n="rivetPointOnSurfaceInfo#")
        pOSI.setAttr("turnOnPercentage", 1)
        pOSI.setAttr("parameterU", 0.5)
        pOSI.setAttr("parameterV", 0.5)

        loft.attr("os") >> pOSI.attr("is")
        cFME1.attr("oc") >> loft.attr("ic[0]")
        cFME2.attr("oc") >> loft.attr("ic[1]")
        shape.attr("w") >> cFME1.attr("im")
        shape.attr("w") >> cFME2.attr("im")
    else:
        selection_list = pm.filterExpand(sm=41)

        if selection_list is not None and len(selection_list) > 0:
            size = len(selection_list)
            if size != 1:
                raise pm.MayaObjectError("No one point selected")

            point = pm.PyNode(selection_list[0])
            shape = point.node()
            u = float(point.name().split("][")[0].split("[")[1])
            v = float(point.name().split("][")[1].split("]")[0])

            pOSI = pm.createNode("pointOnSurfaceInfo", n="rivetPointOnSurfaceInfo#")
            pOSI.setAttr("turnOnPercentage", 0)
            pOSI.setAttr("parameterU", u)
            pOSI.setAttr("parameterV", v)
            shape.attr("ws") >> pOSI.attr("is")
        else:
            raise pm.MayaObjectError("No edges or point selected")

    locator = pm.spaceLocator(n="rivet#")
    aimCons = pm.createNode(
        "aimConstraint", p=locator, n=locator.name() + "_rivetAimConstraint#"
    )
    aimCons.setAttr("tg[0].tw", 1)
    aimCons.setAttr("a", (0, 1, 0))
    aimCons.setAttr("u", (0, 0, 1))
    aimCons.setAttr("v", k=0)
    aimCons.setAttr("tx", k=0)
    aimCons.setAttr("ty", k=0)
    aimCons.setAttr("tz", k=0)
    aimCons.setAttr("rx", k=0)
    aimCons.setAttr("ry", k=0)
    aimCons.setAttr("rz", k=0)
    aimCons.setAttr("sx", k=0)
    aimCons.setAttr("sy", k=0)
    aimCons.setAttr("sz", k=0)

    pOSI.attr("position") >> locator.attr("translate")
    pOSI.attr("n") >> aimCons.attr("tg[0].tt")
    pOSI.attr("tv") >> aimCons.attr("wu")
    aimCons.attr("crx") >> locator.attr("rx")
    aimCons.attr("cry") >> locator.attr("ry")
    aimCons.attr("crz") >> locator.attr("rz")

    pm.select(locator)
    return locator


def create_follicle(shape, uv):
    """creates follicle on the given shape at given uv coordinates

    :param shape:
    :param uv:
    :return:
    """
    # create a hair follicle
    follicle = pm.nt.Follicle()
    follicle.simulationMethod.set(0)
    shape.worldMatrix >> follicle.inputWorldMatrix
    shape.outMesh >> follicle.inputMesh
    follicle.parameterU.set(uv[0])
    follicle.parameterV.set(uv[1])
    # parent the object to the follicles transform node
    follicle_transform = follicle.getParent()
    follicle.outTranslate >> follicle_transform.translate
    follicle.outRotate >> follicle_transform.rotate

    return follicle_transform, follicle


def auto_rivet(objects=None, geo=None):
    """creates hair follicles around selection

    :param objects: list of objects to attach to the geometry
    :param geo: A geometry to attach the objects to.
    """
    if not objects or not geo:
        sel_list = pm.ls(sl=1)

        # the last selection is the mesh
        objects = sel_list[:-1]
        geo = sel_list[-1]

    # meshes = filter(lambda x: isinstance(x, pm.nt.Mesh), sel_list)
    # if meshes
    # objects = filter(lambda x: not isinstance(x, pm.nt.Mesh), sel_list)

    # get the closest point to the surface
    shape = None
    if isinstance(geo, pm.nt.Transform):
        shape = geo.getShape()
    elif isinstance(geo, pm.nt.Mesh):
        shape = geo

    follicles = []

    for obj in objects:
        # pivot point of the obj
        pivot = obj.getRotatePivot(space="world")
        uv = shape.getUVAtPoint(pivot, space="world")

        follicle_transform, follicle = create_follicle(shape, uv)
        pm.parent(obj, follicle_transform)

        follicles.append(follicle)

    return follicles


def rivet_per_face():
    """creates hair follicles per selected face"""
    from functools import reduce

    sel_list = pm.ls(sl=1, fl=1)

    follicles = []
    locators = []
    for face in sel_list:
        # use the center of the face as the follicle position
        p = reduce(lambda x, y: x + y, face.getPoints()) / face.numVertices()
        obj = pm.spaceLocator(p=p)
        locators.append(obj)
        shape = face.node()
        uv = face.getUVAtPoint(p, space="world")

        follicle_transform, follicle = create_follicle(shape, uv)

        pm.parent(obj, follicle_transform)
        follicles.append(follicle)

    return follicles, locators


def hair_from_curves():
    """creates hairs from curves"""
    selection_list = pm.ls(sl=1)

    curves = []
    curve_shapes = []

    mesh = ""
    mesh_shape = ""

    for i in range(0, len(selection_list)):
        shapes = pm.listRelatives(selection_list[i], s=True)
        node_type = pm.nodeType(shapes[0])

        if node_type == "nurbsCurve":
            curves.append(selection_list[i])
            curve_shapes.append(shapes[0])
        elif node_type == "mesh":
            mesh = selection_list[i]
            mesh_shape = shapes[0]

    do_output_curve = 1
    hide_output_curve = 0

    # create hair
    hair_system = pm.createNode("hairSystem")
    pm.connectAttr("time1.outTime", (hair_system + ".currentTime"))

    hair_system_group = ""
    hair_system_out_hair_group = ""
    hair_system_parent = pm.listTransforms(hair_system)
    if len(hair_system_parent) > 0:
        hair_system_group = hair_system_parent[0] + "Follicles"
        if not pm.objExists(hair_system_group):
            hair_system_group = pm.group(em=1, name="hsysGroup")
        if do_output_curve:
            hair_system_out_hair_group = hair_system_parent[0] + "OutputCurves"
            if not pm.objExists(hair_system_out_hair_group):
                hair_system_out_hair_group = pm.group(em=1, name="hsysOutHairGroup")
            if hide_output_curve:
                pm.setAttr(hair_system_out_hair_group + ".visibility", False)

    # create closestPointOnMesh to read the closest point parameter
    cpom = pm.createNode("closestPointOnMesh")
    pm.connectAttr((mesh_shape + ".worldMesh[0]"), (cpom + ".inMesh"))

    num_of_curves = len(curves)

    for i in range(0, num_of_curves):
        dup_name = pm.duplicate(curves[i])
        dup_shape = pm.listRelatives(dup_name[0], s=True)

        first_cv_tra = pm.xform(q=True, ws=True, t=(curves[i] + ".cv[0"))

        pm.setAttr(
            (cpom + ".ip"),
            (first_cv_tra[0], first_cv_tra[1], first_cv_tra[2]),
            type="double3",
        )

        pu = pm.getAttr(cpom + ".r.u")
        pv = pm.getAttr(cpom + ".r.v")

        hair_curve_name_prefix = mesh + "Follicle"
        naming_index = num_of_curves * int(pu * float(num_of_curves - 1) + 0.5) + int(
            pv * float(num_of_curves - 1) + 0.5
        )

        new_name = hair_curve_name_prefix + str(naming_index)

        # create follicle
        hair = pm.createNode("follicle")
        pm.setAttr(pu, hair + ".parameterU")
        pm.setAttr(pv, hair + ".parameterV")

        pm.connectAttr((curve_shapes[i] + ".worldSpace[0]"), (hair + ".sp"))

        transforms = pm.listTransforms(hair)
        hair_dag = transforms[0]

        pm.connectAttr((mesh_shape + ".worldMatrix[0]"), (hair + ".inputWorldMatrix"))

        pm.connectAttr((mesh_shape + ".outMesh"), (hair + ".inputMesh"))
        current_uv_set = pm.polyUVSet(q=True, currentUVSet=mesh_shape)
        pm.setAttr(current_uv_set[0], (hair + ".mapSetName"), type="string")

        pm.connectAttr((hair + ".outTranslate"), (hair_dag + ".translate"))
        pm.connectAttr((hair + ".outRotate"), (hair_dag + ".rotate"))
        pm.setAttr((hair_dag + ".translate"), lock=True)
        pm.setAttr((hair_dag + ".rotate"), lock=True)

        pm.setAttr(hair + ".degree", 3)
        pm.setAttr(hair + ".startDirection", 1)
        pm.setAttr(hair + ".restPose", 3)

        pm.parent(hair_system_group, relative=hair_dag)

        pm.parent(hair_dag, absolute=curves[i])

        pm.setAttr(hair + ".simulationMethod", 2)

        # initHairCurveDisplay(curves[i], "start")

        hair_index = i
        pm.connectAttr(
            (hair + ".outHair"), (hair_system + ".inputHair[%f]" % hair_index)
        )
        pm.connectAttr(
            (hair_system + ".inputHair[%f]" % hair_index), (hair + ".currentPosition")
        )

        crv = dup_shape[0]
        pm.connectAttr((hair + ".outCurve"), (crv + ".create"))
        # initHairCurveDisplay(crv, "current")

        transforms = pm.listTransforms(crv)
        pm.parent(transforms[0], hair_system_out_hair_group, r=True)

        pm.rename(hair_dag, new_name)

    pm.select(hair_system, r=True)

    import maya.mel as mel

    mel.eval('displayHairCurves("current", true')

    pm.delete(cpom)


def align_to_pole_vector():
    """aligns the object to the pole vector of the selected ikHandle"""
    selection_list = pm.ls(sl=1)

    ik_handle = ""
    control_object = ""

    for obj in selection_list:
        if pm.nodeType(obj) == "ikHandle":
            ik_handle = obj
        else:
            control_object = obj

    temp = pm.listConnections((ik_handle + ".startJoint"), s=1)
    start_joint = temp[0]
    start_joint_pos = pm.xform(start_joint, q=True, ws=True, t=True)

    temp = pm.listConnections((ik_handle + ".endEffector"), s=1)
    end_effector = temp[0]
    pm.xform(
        control_object,
        ws=True,
        t=(start_joint_pos[0], start_joint_pos[1], start_joint_pos[2]),
    )

    pm.parent(control_object, end_effector)
    pm.setAttr(control_object + ".r", 0, 0, 0)

    pm.parent(control_object, w=True)


def export_blend_connections():
    """Exports the connection commands from selected objects to the blendShape
    of another object. The resulted text file contains all the MEL scripts to
    reconnect the objects to the blendShape node. So after exporting the
    connection commands you can export the blendShape targets as another maya
    file and delete them from the scene, thus your scene gets lite and loads
    much more quickly.
    """
    selection_list = pm.ls(tr=1, sl=1, l=1)

    dialog_return = pm.fileDialog2(cap="Save As", fm=0, ff="Text Files(*.txt)")

    filename = dialog_return[0]
    print(filename)

    print("\n\nFiles written:\n--------------------------------------------\n")

    with open(filename, "w") as fileId:
        for i in range(0, len(selection_list)):
            shapes = pm.listRelatives(selection_list[i], s=True, f=True)

            main_shape = ""
            for j in range(0, len(shapes)):
                if pm.getAttr(shapes[j] + ".intermediateObject") == 0:
                    main_shape = shapes
                    break
            if main_shape == "":
                main_shape = shapes[0]

            con = pm.listConnections(main_shape, t="blendShape", c=1, s=1, p=1)

            cmd = "connectAttr -f %s.worldMesh[0] %s;" % (
                "".join(map(str, main_shape)),
                "".join(map(str, con[0].name())),
            )
            print("%s\n" % cmd)
            fileId.write("%s\n" % cmd)

    print("\n------------------------------------------------------\n")
    print("filename: %s     ...done\n" % filename)


def transfer_shaders(source, target, allow_component_assignments=False):
    """Transfer shader from source to target.
    :param source: Source geo.
    :param target: Target geo.
    :param (bool) allow_component_assignments: If True will transfer component level
        shader assignments.
    """
    if isinstance(source, pm.nt.Transform):
        source_shape = source.getShape()
    else:
        source_shape = source

    # get the shadingEngines
    shapes_and_engines = source_shape.outputs(type=pm.nt.ShadingEngine, c=1)
    if len(shapes_and_engines):
        # possible fix for locked shading engines
        for source_attribute, shading_engine in shapes_and_engines:
            pm.lockNode(shading_engine, l=0, lockUnpublished=0)

            # check if there is component assignments
            is_component_assignment = "objectgroups" in source_attribute.lower()
            if is_component_assignment and allow_component_assignments:
                # try to get the same components on the target
                components = []
                target_shape = target
                if isinstance(target, pm.nt.Transform):
                    target_shape = target.getShape()
                for component in pm.sets(shading_engine, q=1):
                    if source_shape.name() in str(component):
                        target_component = component.replace(
                            source_shape.name(), target_shape.name()
                        )
                        components.append(target_component)
                pm.sets(shading_engine, fe=components)
            else:
                pm.sets(shading_engine, fe=target)
                # also assign instances to the same shader
                if target.instanceCount() > 1:
                    for i in range(1, target.instanceCount()):
                        target.attr("instObjGroups[%s]" % i).disconnect()
                        (
                            target.attr("instObjGroups[%s]" % i)
                            >> shading_engine.attr("dagSetMembers").next_available
                        )


def benchmark(iter_cnt):
    """benchmarks playback rate

    :param iter_cnt: Count of iteration
    """
    import time

    start = pm.playbackOptions(q=1, min=1)
    stop = pm.playbackOptions(q=1, max=1)

    start_time = time.time()

    for j in range(iter_cnt):
        for i in range(start, stop + 1):
            pm.currentTime(e=i)

    total_time = time.time() - start_time
    print("------------------------------")
    print("BenchmarkTime : %s" % total_time)
    print("Total iterCnt : %s" % iter_cnt)
    print("Average FPS   : %s" % ((stop - start) * iter_cnt / total_time))


def load_shelf_tab(shelf_path):
    """loads the given shelf tab"""
    # look in to the shelf mel file from user folders
    import os

    if os.path.exists(shelf_path):
        try:
            pm.mel.eval('loadNewShelf "%s"' % shelf_path)
        except Exception:
            # probably not in GUI mode
            return


def delete_shelf_tab(shelf_name, confirm=True):
    """The python version of the original mel script of Maya
    :param shelf_name: The name of the shelf to delete
    """
    try:
        shelf_top_level_path = pm.melGlobals["gShelfTopLevel"]
    except KeyError:
        # not in GUI mode
        return

    shelf_top_level = pm.windows.tabLayout(shelf_top_level_path, e=1)

    if len(shelf_top_level.children()) < 0:
        return

    if confirm:
        # before doing anything ask it
        response = pm.confirmDialog(
            title="Delete Shelf?",
            message="Delete %s?" % shelf_name,
            button=["Yes", "No"],
            defaultButton="No",
            cancelButton="No",
            dismissString="No",
        )
        if response == "No":
            return

    # update the preferences
    shelf_number = -1
    number_of_shelves = pm.optionVar["numShelves"]
    for i in range(1, number_of_shelves + 1):
        if pm.optionVar["shelfName%s" % i] == shelf_name:
            shelf_number = i
            break

    if shelf_number == -1:
        # there should be no shelf with this name
        return

    # offset shelves
    for i in range(shelf_number, number_of_shelves):
        pm.optionVar["shelfLoad%s" % i] = pm.optionVar["shelfLoad%s" % (i + 1)]
        pm.optionVar["shelfName%s" % i] = pm.optionVar["shelfName%s" % (i + 1)]
        pm.optionVar["shelfFile%s" % i] = pm.optionVar["shelfFile%s" % (i + 1)]

    pm.optionVar.pop("shelfLoad%s" % number_of_shelves)
    number_of_shelves -= 1
    pm.optionVar["numShelves"] = number_of_shelves

    pm.windows.deleteUI("%s|%s" % (shelf_top_level_path, shelf_name), layout=1)

    # remove the shelf mel file from user folders
    import os

    for path in pm.internalVar(userShelfDir=1).split(os.path.pathsep):
        shelf_file_name = "shelf_%s.mel" % shelf_name
        shelf_file_full_path = os.path.join(path, shelf_file_name)

        deleted_file_name = "%s.deleted" % shelf_file_name
        deleted_file_full_path = os.path.join(path, deleted_file_name)

        try:
            os.remove(deleted_file_full_path)
        except OSError:
            pass

        try:
            os.remove(shelf_file_full_path)
            break
        except OSError:
            pass

    # Make sure the new active shelf tab has buttons
    pm.mel.eval("shelfTabChange();")


def cube_from_bbox(bbox):
    """creates a polyCube from the given bbox

    :param bbox: pymel.core.dt.BoundingBox instance
    """
    cube = pm.polyCube(
        width=bbox.width(), height=bbox.height(), depth=bbox.depth(), ch=False
    )
    cube[0].setAttr("t", bbox.center())
    return cube[0]


def create_bbox(nodes, per_selection=False):
    """creates bounding boxes for the selected objects

    :param bool per_selection: If True will create a BBox for each
      given object
    """

    if per_selection:
        for node in nodes:
            return cube_from_bbox(node.boundingBox())
    else:
        bbox = pm.dt.BoundingBox()
        for node in nodes:
            bbox.expand(node.boundingBox().min())
            bbox.expand(node.boundingBox().max())
        return cube_from_bbox(bbox)


def replace_with_bbox(nodes):
    """replaces the given nodes with a bbox object"""
    node_names = []
    bboxes = []
    processed_nodes = []
    for node in nodes:
        # create a bbox and parent it to the parent of
        # the original node

        # check if it is a transform node
        if not isinstance(node, pm.nt.Transform):
            continue

        # check the shape
        # check if it has at least one shape under it
        if not has_shape(node):
            continue

        bbox = cube_from_bbox(node.boundingBox())
        bbox.setParent(node.getParent())

        # set pivots
        rp = pm.xform(node, q=1, ws=1, rp=1)
        sp = pm.xform(node, q=1, ws=1, sp=1)
        pm.xform(bbox, ws=1, rp=rp)
        pm.xform(bbox, ws=1, sp=sp)

        node_name = node.name()
        node_shape = node.getShape()
        node_shape_name = None
        if node_shape is not None:
            node_shape_name = node_shape.name()

        node_names.append((node_name, node_shape_name))
        bboxes.append(bbox)
        processed_nodes.append(node)

    # delete the nodes
    if len(processed_nodes):
        pm.delete(processed_nodes)

        # rename the bboxes
        for name, bbox in zip(node_names, bboxes):
            bbox.rename(name[0])
            if name[1]:
                bbox.getShape().rename(name[1])

    return bboxes


def get_root_nodes(reference_node=None):
    """returns the root DAG nodes.

    :param reference_node: If given, the root node of that reference and all the
        subReference nodes will be returned.

    :return: list
    """
    root_transform_nodes = []

    if not reference_node:
        nodes_to_consider = pm.ls(dag=1, transforms=1)
    else:
        nodes_to_consider = pm.ls(
            reference_node.nodes(recursive=1), type=pm.nt.Transform
        )

    for node in nodes_to_consider:
        parent = node.getParent()
        if not reference_node:
            no_parent = parent is None
        else:
            # check if the parent is from the same reference file,
            # consider the topmost parent reference file
            no_parent = (
                parent.referenceFile().topmost_parent != reference_node.topmost_parent
                if parent and parent.referenceFile() is not None
                else True
            )

        if no_parent:
            shape = node.getShape()
            if shape:
                if shape.type() not in ["camera", "displayPoints"]:
                    root_transform_nodes.append(node)
            else:
                root_transform_nodes.append(node)

    return root_transform_nodes


def create_arnold_stand_in(path=None):
    """A fixed version of original arnold script of SolidAngle Arnold core API"""
    if not pm.objExists("ArnoldStandInDefaultLightSet"):
        pm.createNode("objectSet", name="ArnoldStandInDefaultLightSet", shared=True)
        pm.lightlink(object="ArnoldStandInDefaultLightSet", light="defaultLightSet")

    stand_in = pm.createNode("aiStandIn", n="ArnoldStandInShape")
    # temp fix until we can correct in c++ plugin
    stand_in.setAttr("visibleInReflections", True)
    stand_in.setAttr("visibleInRefractions", True)

    pm.sets("ArnoldStandInDefaultLightSet", add=stand_in)
    if path:
        stand_in.setAttr("dso", path)

    return stand_in


def create_rs_proxy_node(path=None):
    """Creates Redshift Proxies showing a proxy object"""
    proxy_mesh_node = pm.createNode("RedshiftProxyMesh")
    proxy_mesh_node.fileName.set(path)
    proxy_mesh_shape = pm.createNode("mesh")
    proxy_mesh_node.outMesh >> proxy_mesh_shape.inMesh

    # assign default material
    pm.sets("initialShadingGroup", fe=proxy_mesh_shape)

    return proxy_mesh_node, proxy_mesh_shape


def run_pre_publishers():
    """runs pre publishers if the current scene is a published version

    This is written to prevent users to save on top of a Published version and
    create a back door to skip un publishable scene to publish
    """
    from anima.dcc.mayaEnv.publish import PublishError
    from anima.dcc import mayaEnv

    m_env = mayaEnv.Maya()

    version = m_env.get_current_version()

    # check if we have a proper version
    if not version:
        return

    # check if it is a Representation
    from anima.representation import Representation

    if Representation.repr_separator in version.take_name:
        return

    if version.is_published:
        from anima.publish import (
            run_publishers,
            staging,
            POST_PUBLISHER_TYPE,
        )

        # before doing anything run all publishers
        type_name = ""
        if version.task.type:
            type_name = version.task.type.name

        # before running use the staging area to store the current version
        staging["version"] = version
        try:
            run_publishers(type_name)
        except (PublishError, RuntimeError) as e:
            # do not forget to clean up the staging area
            staging.clear()
            # pop up a message box with the error
            pm.confirmDialog(
                title="SaveError",
                icon="critical",
                message="<b>%s</b><br/><br/>%s" % ("SCENE NOT SAVED!!!", e),
                button=["Ok"],
            )
            raise e
        # do not forget to clean up the staging area
        staging.clear()
    else:
        # run some of the publishers
        from anima.dcc.mayaEnv import publish as publish_scripts

        try:
            publish_scripts.check_node_names_with_bad_characters()
        except (PublishError, RuntimeError) as e:
            # pop up a message box with the error
            pm.confirmDialog(
                title="SaveError",
                icon="critical",
                message="<b>%s</b><br/><br/>%s" % ("SCENE NOT SAVED!!!", e),
                button=["Ok"],
            )
            raise e

        # update updated_by field of the current version
        from stalker import LocalSession

        ls = LocalSession()
        logged_in_user = ls.logged_in_user
        if logged_in_user:
            version.updated_by = logged_in_user
            from stalker.db.session import DBSession

            DBSession.commit()


def run_post_publishers():
    """runs post publishers if the current scene is a published version

    This is written to prevent users to save on top of a Published version and
    create a back door to skip un publishable scene to publish
    """
    from anima.dcc.mayaEnv.publish import PublishError
    from anima.dcc import mayaEnv

    m_env = mayaEnv.Maya()

    version = m_env.get_current_version()

    # check if we have a proper version
    if not version:
        return

    # check if it is a Representation
    from anima.representation import Representation

    if Representation.repr_separator in version.take_name:
        return

    if version.is_published:
        from anima.publish import (
            run_publishers,
            staging,
            POST_PUBLISHER_TYPE,
        )

        # before doing anything run all publishers
        type_name = ""
        if version.task.type:
            type_name = version.task.type.name

        # before running use the staging area to store the current version
        staging["version"] = version

        # show dialog during post publish progress and lock maya
        from anima.ui.utils import initialize_post_publish_dialog

        d = initialize_post_publish_dialog()
        d.show()

        try:
            run_publishers(type_name, publisher_type=POST_PUBLISHER_TYPE)
            d.close()
        except (PublishError, RuntimeError) as e:
            d.close()
            # do not forget to clean up the staging area
            staging.clear()
            # pop up a message box with the error
            pm.confirmDialog(
                title="PublishError",
                icon="critical",
                message="<b>%s</b><br/><br/>%s" % ("POST PUBLISH FAILED!!!", e),
                button=["Ok"],
            )
            raise e

        # close dialog in any case
        d.close()
        # do not forget to clean up the staging area
        staging.clear()


def get_default_render_layer():
    """Returns the default render layer
    :return:
    """
    return pm.ls(type="renderLayer")[0].defaultRenderLayer()


def switch_to_default_render_layer():
    """sets the current layer to defaultRenderLayer"""
    try:
        default_render_layer = get_default_render_layer()
        current_layer = get_current_render_layer()
        if current_layer != default_render_layer:
            default_render_layer.setCurrent()
    except (NameError, RuntimeError):
        pass


def get_current_render_layer():
    """Returns the current render layer

    :return:
    """
    default_render_layer = get_default_render_layer()
    return default_render_layer.currentLayer()


def fix_external_paths():
    """fixes external paths in a maya scene"""
    from anima.dcc import mayaEnv

    m_env = mayaEnv.Maya()
    if m_env.get_current_version():
        m_env.replace_external_paths()


def has_shape(node):
    """checks if the given node has at least one child that has a shape"""
    allowed_shapes = (pm.nt.Mesh, pm.nt.NurbsCurve, pm.nt.NurbsSurface)

    has_it = False

    children = node.getChildren()
    while len(children) and not has_it:
        child = children.pop(0)
        if isinstance(child, allowed_shapes):
            has_it = True
            break
        children += child.getChildren()

    return has_it


def generate_thumbnail():
    """generates thumbnail for current scene"""
    import tempfile
    import glob
    from anima.dcc import mayaEnv

    m_env = mayaEnv.Maya()
    v = m_env.get_current_version()

    if not v:
        return

    # do not generate a thumbnail from a Repr
    if "@" in v.take_name:
        return

    task = v.task
    project = task.project
    # repo = project.repository
    imf = project.image_format
    width = int(imf.width * 0.5)
    height = int(imf.height * 0.5)

    temp_output = tempfile.mktemp()

    current_frame = pm.currentTime(q=1)
    output_file = pm.playblast(
        fmt="image",
        startTime=current_frame,
        endTime=current_frame,
        sequenceTime=1,
        forceOverwrite=1,
        filename=temp_output,
        clearCache=1,
        showOrnaments=1,
        percent=100,
        wh=(width, height),
        offScreen=1,
        viewer=0,
        compression="PNG",
        quality=70,
        framePadding=0,
    )
    pm.currentTime(current_frame)

    output_file = output_file.replace("####", "*")
    found_output_file = glob.glob(output_file)
    if found_output_file:
        output_file = found_output_file[0]

        from anima.ui import utils

        anima.utils.upload_thumbnail(task, output_file)

    return found_output_file


def perform_playblast(
    action=0,
    resolution=100,
    playblast_view_options=None,
    upload_to_server=None,
    force_batch_mode=False,
):
    """The patched version of the original perform playblast.

    Args:
        action (int): Passed directly to the Maya version of the playblast if the
            current scene is not related to a Stalker Version.
        resolution(int): An integer value one of 25, 50, 100 defining the playblast
            resolution as a percent fraction of the original scene resolution.
            Default value is 100. If given as None, the value or this argument will be
            asked to the user.
        playblast_view_options (dict): A dictionary containing the view options.
            ``auxiliary.get_default_playblast_view_options`` can be used to get one. If
            given as None, the value or this argument will be asked to the user.
        upload_to_server (bool): A bool value to specify if the resultant video should
            be uploaded to the server or not. If given as None, the value or this
            argument will be asked to the user.
    """
    # check if the current scene is a Stalker related version
    # if not call the default playblast
    # if it is call out ShotPlayblaster
    from anima.dcc.mayaEnv import Maya

    m = Maya()
    v = m.get_current_version()

    if v:
        # do use playblaster
        extra_playblast_options = {"viewer": 0}

        # always use PNG as image format which now properly supports audio files
        extra_playblast_options["fmt"] = "image"
        extra_playblast_options["compression"] = "png"

        # ask resolution
        if resolution is None:
            resolution = ask_playblast_resolution()

        if resolution is None:
            return

        extra_playblast_options["percent"] = resolution

        # ask for playblast view options
        if playblast_view_options is None:
            playblast_view_options = ask_playblast_view_options()

        pb = Playblaster(
            playblast_view_options=playblast_view_options,
            force_batch_mode=force_batch_mode,
        )
        outputs = pb.playblast(extra_playblast_options=extra_playblast_options)

        if outputs:
            if upload_to_server is None:  # so no default options
                response = pm.confirmDialog(
                    title="Upload To Server?",
                    message="Upload To Server?",
                    button=["Yes", "No"],
                    defaultButton="No",
                    cancelButton="No",
                    dismissString="No",
                )
            else:
                response = "Yes" if upload_to_server else "No"

            if response == "Yes":
                for output in outputs:
                    pb.upload_output(pb.version, output)

    else:
        # call the original playblast
        return pm.mel.eval("performPlayblast_orig(%s);" % action)


def set_range_from_shot(shot):
    """sets the playback range from a shot node in the scene

    :param shot: Maya Shot
    """
    min_frame = shot.getAttr("startFrame")
    max_frame = shot.getAttr("endFrame")

    pm.playbackOptions(ast=min_frame, aet=max_frame, min=min_frame, max=max_frame)


def ask_playblast_resolution():
    """Asks the user the playblast resolution"""
    # ask resolution
    response = pm.confirmDialog(
        title="Resolution?",
        message="Resolution?",
        button=["Default", "Full", "Half", "Quarter", "Cancel"],
        defaultButton="Default",
        cancelButton="Default",
        dismissString="Default",
    )
    if response == "Default":
        return 50
    elif response == "Full":
        return 100
    elif response == "Half":
        return 50
    elif response == "Quarter":
        return 25
    elif response == "Cancel":
        return None

    return 100


def get_default_playblast_view_options():
    """returns a copy of the default_playblast_View_options"""
    import copy

    return copy.copy(Playblaster.default_view_options)


def ask_playblast_view_options():
    """asks the user the playblast view options

    It will store the last selected view options and if there are no previously
    selected view options it will use the defaults from the Playblaster
    """
    # storage
    user_playblast_view_options_storage = os.path.join(
        tempfile.gettempdir(), "playblast_view_options.json"
    )

    use_defaults = False
    if os.path.exists(user_playblast_view_options_storage):
        try:
            with open(user_playblast_view_options_storage, "r") as f:
                user_playblast_view_options = json.load(f)
        except ValueError:
            use_defaults = True
    else:
        use_defaults = True

    if use_defaults:
        user_playblast_view_options = get_default_playblast_view_options()

    # display the current options and ask the user to change them
    # sadly we need to use Qt to display a proper modal dialog
    from anima.ui.lib import QtCore, QtWidgets
    from anima.dcc import mayaEnv

    class PlayblastViewOptionsDialog(QtWidgets.QDialog):
        def __init__(self, options=None):
            parent = mayaEnv.get_maya_main_window()
            super(PlayblastViewOptionsDialog, self).__init__(parent=parent)
            self.options = options
            self.checkers = []
            self.setup_dialog()

        def setup_dialog(self):
            self.setWindowTitle("Playblast View Options")
            # self.resize(517, 545)
            vertical_layout = QtWidgets.QVBoxLayout(self)

            use_defaults_button = QtWidgets.QPushButton(self)
            use_defaults_button.setText("Use Defaults")
            vertical_layout.addWidget(use_defaults_button)

            horizontal_layout = QtWidgets.QHBoxLayout(self)
            vertical_layout.addLayout(horizontal_layout)

            current_vertical_layout = QtWidgets.QVBoxLayout(self)
            horizontal_layout.addLayout(current_vertical_layout)

            vertical_button_count = 10

            i = 0
            for k in sorted(self.options.keys()):
                v = self.options[k]
                i += 1
                if isinstance(v, bool):
                    checker = QtWidgets.QCheckBox(k, parent=self)
                    checker.setChecked(v)
                    current_vertical_layout.addWidget(checker)
                    self.checkers.append(checker)

                if i % vertical_button_count == 0:
                    # create a new vertical layout
                    current_vertical_layout = QtWidgets.QVBoxLayout(self)
                    horizontal_layout.addLayout(current_vertical_layout)

            # add a spacer to the last column layout
            spacer_item = QtWidgets.QSpacerItem(
                20, 20, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding
            )
            current_vertical_layout.addItem(spacer_item)

            button_box = QtWidgets.QDialogButtonBox(self)
            button_box.setOrientation(QtCore.Qt.Horizontal)
            button_box.setStandardButtons(
                QtWidgets.QDialogButtonBox.Cancel | QtWidgets.QDialogButtonBox.Ok
            )
            vertical_layout.addWidget(button_box)
            vertical_layout.setStretch(2, 1)

            # Button box
            QtCore.QObject.connect(button_box, QtCore.SIGNAL("accepted()"), self.accept)
            QtCore.QObject.connect(button_box, QtCore.SIGNAL("rejected()"), self.reject)
            QtCore.QObject.connect(
                use_defaults_button,
                QtCore.SIGNAL("clicked()"),
                self.use_defaults_push_button_clicked,
            )

        def use_defaults_push_button_clicked(self):
            """sets the default values"""
            for checker in self.checkers:
                checker.setChecked(
                    Playblaster.default_view_options[str(checker.text())]
                )

        def get_playblast_options(self):
            """returns the current selected options"""
            playblast_options = {}
            for checker in self.checkers:
                playblast_options[str(checker.text())] = checker.isChecked()
            return playblast_options

    pvod = PlayblastViewOptionsDialog(options=user_playblast_view_options)
    pvod.exec_()

    user_playblast_view_options = pvod.get_playblast_options()
    # write it down
    with open(user_playblast_view_options_storage, "w") as f:
        json.dump(user_playblast_view_options, f)

    return user_playblast_view_options


def perform_playblast_shot(shot_name):
    """Performs shot playblast, this is written to replace the menu action in
    Camera Sequencer.

    :param shot_name: Shot name
    :return:
    """
    if not shot_name:
        return

    response = pm.confirmDialog(
        title="Perform Playblast?",
        message="Perform Playblast?",
        button=["Yes", "No"],
        defaultButton="No",
        cancelButton="No",
        dismissString="No",
    )
    if response == "No":
        return

    # ask resolution
    resolution = 100

    extra_playblast_options = {"viewer": 0, "percent": resolution}

    if " " in shot_name:
        # there are probabaly more than one shot
        shots = [pm.PyNode(s_name) for s_name in shot_name.split(" ")]
    else:
        shots = [pm.PyNode(shot_name)]

    pb = Playblaster()
    video_file_outputs = []
    for shot in shots:
        video_file_output = pb.playblast_shot(
            shot, extra_playblast_options=extra_playblast_options
        )
        video_file_outputs.append(video_file_output)

    response = pm.confirmDialog(
        title="Upload To Server?",
        message="Upload To Server?",
        button=["Yes", "No"],
        defaultButton="No",
        cancelButton="No",
        dismissString="No",
    )
    if response == "Yes":
        for video_file_output in video_file_outputs:
            pb.upload_output(pb.version, video_file_output)


class Playblaster(object):
    """Generates playblasts.
    If there are shots in the current scene then it generates playblasts for
    each of them and uploads it to the server
    """

    default_view_options = {
        "cameras": False,
        "clipGhosts": False,
        "cv": False,
        "deformers": False,
        "dimensions": False,
        "displayAppearance": "smoothShaded",  # Smooth shaded
        "displayLights": "default",  # default lighting
        "shadows": False,  # No Shadows
        # "udm": True,  # use default material
        "dynamics": True,
        "dynamicConstraints": False,
        "fluids": True,
        "follicles": False,
        "greasePencils": False,
        "grid": False,
        "handles": False,
        "hairSystems": False,
        "hulls": False,
        "ikHandles": False,
        "imagePlane": True,
        "joints": False,
        "lights": False,
        "locators": False,
        "manipulators": False,
        "motionTrails": False,
        "nCloths": True,
        "nParticles": True,
        "nRigids": False,
        "nurbsCurves": False,
        "nurbsSurfaces": False,
        "particleInstancers": True,
        "pivots": False,
        "planes": True,
        "pluginShapes": False,
        "pluginObjects": ("gpuCacheDisplayFilter", True),
        "polymeshes": True,
        "strokes": False,
        "subdivSurfaces": True,
        "textures": False,
    }

    cam_attribute_names = [
        "overscan",
        "filmFit",
        "displayFilmGate",
        "displayResolution",
        "displayGateMask",
        "displayFieldChart",
        "displaySafeAction",
        "displaySafeTitle",
        "displayFilmPivot",
        "displayFilmOrigin",
    ]

    hardware_rendering_globals_attr_names = [
        "ssaoEnable",
        "motionBlurEnable",
        "multiSampleEnable",
    ]

    global_playblast_options = {
        "fmt": "image",
        "forceOverwrite": 1,
        "clearCache": 1,
        "showOrnaments": 1,
        "percent": 100,
        "offScreen": 1,
        "viewer": 0,
        "compression": "png",
        "quality": 85,
        "sequenceTime": 1,
    }

    hud_name = "PlayblasterHUD"

    def __init__(self, playblast_view_options=None, force_batch_mode=False):
        self._playblast_view_options = None
        self.playblast_view_options = playblast_view_options
        self.batch_mode = force_batch_mode or pm.general.about(batch=1)

        self.logged_in_user = None
        if not self.batch_mode:
            from stalker import LocalSession

            local_session = LocalSession()
            self.logged_in_user = local_session.logged_in_user

            if not self.logged_in_user:
                raise RuntimeError("Please login first!")

        self.version = None
        from anima.dcc.mayaEnv import Maya

        self.m_env = Maya()
        self.version = self.m_env.get_current_version()

        self.user_view_options = {}
        self.reset_user_view_options_storage()

    def check_sequence_name(self):
        """checks sequence name and asks the user to set one if maya is in UI
        mode and there is no sequence name set
        """
        local_sequencers = [
            seq for seq in pm.ls(type="sequencer") if seq.referenceFile() is None
        ]
        if not local_sequencers:
            sequencer = pm.nt.Sequencer()
        else:
            sequencer = local_sequencers[0]

        try:
            sequence_name = sequencer.getAttr("sequence_name")
        except pm.MayaAttributeError:
            from anima.dcc.mayaEnv import previs

            previs.Previs.add_sequence_name_attribute_to_sequencer(sequencer)
            sequence_name = sequencer.getAttr("sequence_name")

        if sequence_name == "" and not self.batch_mode:
            result = pm.promptDialog(
                title="Please enter a Sequence Name",
                message="Sequence Name:",
                button=["OK", "Cancel"],
                defaultButton="OK",
                cancelButton="Cancel",
                dismissString="Cancel",
            )

            if result == "OK":
                sequencer.setAttr(
                    "sequence_name", pm.promptDialog(query=True, text=True)
                )

    def get_hud_data(self):
        """ """
        # try to get the shot from sequencer
        current_shot = pm.sequenceManager(q=1, currentShot=1)

        current_cam_name = "NoCameraFound"
        if current_shot:
            shot_name = pm.getAttr("%s.shotName" % current_shot)
            current_cam_name = pm.shot(current_shot, q=1, cc=1)
            if current_cam_name:
                current_cam = pm.PyNode(current_cam_name)
            else:
                # there is no camera in this shot
                # use the first camera in the scene
                # TODO: using the first camera is not a good idea
                current_cam = pm.ls(type=pm.nt.Camera)[0].getParent()
                current_cam_name = current_cam.name()
        else:
            # then try to get the shot name from the file name
            import os

            shot_name = os.path.split(pm.sceneName())[1].split("_")[0]
            # use the active panel camera
            current_cam = self.get_active_panel_camera()

            if current_cam is not None:
                current_cam_name = current_cam.name()

        if isinstance(current_cam, pm.nt.Transform):
            current_cam = current_cam.getShape()

        focal_length = 0

        if current_cam is not None:
            focal_length = current_cam.getAttr("focalLength")

        sequencers = pm.ls(type="sequencer")
        if sequencers:
            sequencer = sequencers[0]
            if not sequencer.hasAttr("sequence_name"):
                from anima.dcc.mayaEnv import previs

                previs.Previs.add_sequence_name_attribute_to_sequencer(sequencer)
            if sequencer.getAttr("sequence_name") != "":
                shot_info = sequencer.getAttr("sequence_name")
            else:
                shot_info = "INVALID"
        else:
            shot_info = shot_name

        cf = int(pm.currentTime(q=1)) + 1

        import timecode

        frame_rate = 25
        from anima.dcc import mayaEnv

        maya_env = mayaEnv.Maya()
        v = maya_env.get_current_version()
        if v:
            frame_rate = v.task.project.fps
        tc = timecode.Timecode(frame_rate, frames=cf)

        if current_shot:
            start_time = pm.shot(current_shot, q=1, st=1)
            end_time = pm.shot(current_shot, q=1, et=1)
        else:
            # no shot node use the current playback range
            start_time = pm.playbackOptions(q=1, min=1)
            end_time = pm.playbackOptions(q=1, max=1)

        cs_frame = int(cf - start_time)

        length = int(end_time - start_time) + 1

        if self.version:
            user_name = (
                self.version.updated_by.name if self.version.updated_by else "None"
            )
        else:
            # get the user name from the login info
            if self.logged_in_user:
                user_name = self.logged_in_user.name
            else:
                # ok try to use the filename
                user_name = pm.sceneName().split("_")[-1]

        hud_string = "%s | %s:%smm | tc:%s [%s] | Shot: %s | Length: %s/%sfr | [%s]" % (
            shot_info,
            current_cam_name.split(":")[-1],
            int(focal_length),
            tc,
            str(int(cf) - 1).zfill(4),
            shot_name.split(":")[-1],
            cs_frame,
            str(length).zfill(3),
            user_name,
        )
        return hud_string

    def get_active_panel_camera(self):
        """returns the active view camera"""
        active_panel = self.get_active_panel()
        current_cam = None
        try:
            current_cam = pm.modelEditor(active_panel, q=1, cam=1)
        except pm.MayaNodeError as e:
            pass

        # really return the camera node and not the transform node
        if isinstance(current_cam, pm.nt.Transform):
            current_cam = current_cam.getShape()

        return current_cam

    def create_hud(self, hud_name):
        """creates HUD"""
        self.remove_hud(hud_name)

        try:
            # create our HUD
            pm.headsUpDisplay(
                hud_name,
                section=7,
                block=1,
                ao=1,
                blockSize="medium",
                labelFontSize="large",
                dfs="large",
                command=self.get_hud_data,
                atr=1,
            )
        except RuntimeError:
            # there is another HUD in that position remove it
            pm.headsUpDisplay(removePosition=(7, 1))
            self.create_hud(hud_name)

    def remove_hud(self, hud_name=None):
        """removes the HUD"""
        if hud_name and pm.headsUpDisplay(hud_name, q=1, ex=1):
            pm.headsUpDisplay(hud_name, rem=1)

    @classmethod
    def get_shot_cameras(cls):
        # store camera display options
        cameras = []
        for shot in pm.sequenceManager(listShots=1):
            camera_name = pm.shot(shot, q=1, cc=1)
            camera = pm.PyNode(camera_name)
            if isinstance(camera, pm.nt.Transform):
                camera = camera.getShape()
            cameras.append(camera)
        return cameras

    def get_selected_frame_range(self):
        """returns the playback range"""
        start_time = int(pm.playbackOptions(q=1, ast=1))
        end_time = int(pm.playbackOptions(q=1, aet=1))

        if not self.batch_mode:
            selected_start_time, selected_end_time = list(
                map(
                    int,
                    pm.timeControl(
                        pm.melGlobals["$gPlayBackSlider"], q=1, rangeArray=True
                    ),
                )
            )

            if selected_end_time - selected_start_time > 1:
                # the selection is valid
                start_time = selected_start_time
                end_time = selected_end_time

        return [start_time, end_time]

    def is_frame_range_selected(self):
        """returns true if a range in the time line is selected"""
        if not self.batch_mode:
            start, end = list(
                map(
                    int,
                    pm.timeControl(
                        pm.melGlobals["$gPlayBackSlider"], q=1, rangeArray=True
                    ),
                )
            )
            return (end - start) > 1
        else:
            return False

    @classmethod
    def get_audio_node(cls):
        """returns the audio node from the time slider"""
        audio_node_name = pm.timeControl(
            pm.melGlobals["$gPlayBackSlider"], q=1, sound=1
        )
        try:
            audio_node = pm.PyNode(audio_node_name)
        except pm.MayaNodeError:
            return
        return audio_node

    def reset_user_view_options_storage(self):
        """resets the user view options storage"""
        self.user_view_options = {
            "view_options": {},
            "huds": {},
            "camera_flags": {},
            "hardware_rendering_globals": {},
        }

    def store_user_options(self):
        """stores user options"""
        # query active model panel
        active_panel = self.get_active_panel()

        # store show/hide display options for active panel
        self.reset_user_view_options_storage()

        for flag in self.default_view_options.keys():
            try:
                self.user_view_options["view_options"][flag] = pm.modelEditor(
                    active_panel, **{"q": 1, flag: True}
                )
            except TypeError:
                pass

        # store hud display options
        hud_names = pm.headsUpDisplay(lh=1)
        if hud_names:  # in batch mode there is no hud_names
            for hud_name in hud_names:
                self.user_view_options["huds"][hud_name] = pm.headsUpDisplay(
                    hud_name, q=1, vis=1
                )

        for camera in pm.ls(type="camera"):
            camera_name = camera.name()
            per_camera_attr_dict = {}
            for attr in self.cam_attribute_names:
                per_camera_attr_dict[attr] = camera.getAttr(attr)
            self.user_view_options["camera_flags"][camera_name] = per_camera_attr_dict

        hrg = pm.PyNode("hardwareRenderingGlobals")
        for attr in self.hardware_rendering_globals_attr_names:
            self.user_view_options["hardware_rendering_globals"][attr] = hrg.getAttr(
                attr
            )

    @property
    def playblast_view_options(self):
        """the getter for the playblast_view_options"""
        return self._playblast_view_options

    @playblast_view_options.setter
    def playblast_view_options(self, playblast_view_options):
        """setter for the playblast view options

        :param dict playblast_view_options: A dict for the desired options
        :return:
        """
        # use defaults if empty
        if not playblast_view_options:
            playblast_view_options = self.default_view_options

        self._playblast_view_options = playblast_view_options

    def set_view_options(self):
        """set view options for playblast"""
        active_panel = self.get_active_panel()
        pm.modelEditor(active_panel, e=1, **self.playblast_view_options)

        # turn all hud displays off
        hud_flags = pm.headsUpDisplay(lh=1)
        if hud_flags:  # in batch mode there is node headsUpDisplay
            for flag in hud_flags:
                pm.headsUpDisplay(flag, e=1, vis=0)

        # set camera options for playblast
        for camera in pm.ls(type="camera"):
            try:
                camera.setAttr("overscan", 1)
            except RuntimeError:
                pass

            try:
                camera.setAttr("filmFit", 1)
            except RuntimeError:
                pass

            try:
                camera.setAttr("displayFilmGate", 1)
            except RuntimeError:
                pass

            try:
                camera.setAttr("displayResolution", 0)
            except RuntimeError:
                pass

        # pm.mel.eval('displayStyle("-ss")')

        # set hardwareRenderingGlobals attributes for playblast
        hrg = pm.PyNode("hardwareRenderingGlobals")
        hrg.setAttr("ssaoEnable", False)
        hrg.setAttr("multiSampleEnable", True)

    def restore_user_options(self):
        """restores user options"""
        active_panel = self.get_active_panel()
        for flag, value in self.user_view_options["view_options"].items():
            try:
                pm.modelEditor(active_panel, **{"e": 1, flag: value})
            except TypeError:
                pass

        # reassign original hud display options
        for hud, value in self.user_view_options["huds"].items():
            if pm.headsUpDisplay(hud, q=1, ex=1):
                pm.headsUpDisplay(hud, e=1, vis=value)

        # reassign original camera options
        for camera in pm.ls(type="camera"):
            camera_name = camera.name()

            try:
                camera_flags = self.user_view_options["camera_flags"][camera_name]
            except KeyError:
                continue

            for attr, value in camera_flags.items():
                try:
                    camera.setAttr(attr, value)
                except RuntimeError:
                    pass

        # re-set original hardware rendering globals
        hrg = pm.PyNode("hardwareRenderingGlobals")
        for attr in self.hardware_rendering_globals_attr_names:
            value = self.user_view_options["hardware_rendering_globals"][attr]
            hrg.setAttr(attr, value)

        self.remove_hud(self.hud_name)

    @classmethod
    def get_active_panel(cls):
        """returns the active model panel"""
        active_panel = None
        panel_list = pm.getPanel(type="modelPanel")
        for panel in panel_list:
            if pm.modelEditor(panel, q=1, av=1):
                active_panel = panel
                break

        return active_panel

    def playblast(self, extra_playblast_options=None):
        """Do a scene playblast.

        Decides what kind of playblast it needs to do.

        :param extra_playblast_options: A dictionary for extra playblast
          options.
        :return: The resultant movie file or files
        """
        # if there is a shot in the scene do a shot playblast
        shots = pm.ls(type="shot")
        if not extra_playblast_options:
            extra_playblast_options = {}

        # if a time range is selected do a simple playblast
        # the following will return ``False`` in batch mode
        start, end = self.get_selected_frame_range()
        if len(shots) and not self.is_frame_range_selected():
            if not self.batch_mode:
                response = pm.confirmDialog(
                    title="Which Camera?",
                    message="Which Camera?",
                    button=["Current", "Shot Camera", "Cancel"],
                    defaultButton="Shot Camera",
                    cancelButton="Cancel",
                    dismissString="Cancel",
                )
            else:
                response = "Shot Camera"

            if response == "Current":
                extra_playblast_options["sequenceTime"] = 0
            elif response == "Shot Camera":
                extra_playblast_options["sequenceTime"] = 1
            else:
                return []
            return self.playblast_all_shots(extra_playblast_options)
        else:
            extra_playblast_options["startTime"] = start
            extra_playblast_options["endTime"] = end
            return self.playblast_simple(extra_playblast_options)

    def playblast_simple(self, extra_playblast_options=None):
        """Do a simple playblast

        :param extra_playblast_options: A dictionary for extra playblast
          options.
        :return: A string showing the path of the resultant movie file
        """
        import copy

        playblast_options = copy.copy(self.global_playblast_options)
        playblast_options["sequenceTime"] = False
        playblast_options["percent"] = 100

        if extra_playblast_options:
            playblast_options.update(extra_playblast_options)

        # find some audio
        audio_node = self.get_audio_node()
        if audio_node:
            playblast_options["sound"] = audio_node
            playblast_options["useTraxSounds"] = False
        else:
            playblast_options["useTraxSounds"] = True

        # width height
        if "wh" not in playblast_options:
            # get project resolution
            # use half HD by default
            width = 1920
            height = 1080
            if self.version:
                project = self.version.task.project
                # get the resolution
                imf = project.image_format
                width = int(imf.width)
                height = int(imf.height)

            playblast_options["wh"] = (width, height)

        # output path
        import os

        if "filename" not in playblast_options:
            if self.version:
                # use version.base_name plus the camera name
                current_camera = self.get_active_panel_camera()
                current_camera_name = "Camera"
                if current_camera is not None:
                    # use the transform
                    current_camera_name = (
                        current_camera.getParent().name().split(":")[-1]
                    )
                filename = "%s_%s" % (
                    os.path.splitext(self.version.filename)[0],
                    current_camera_name,
                )  # node name
            else:
                # use the current scene name
                filename = os.path.splitext(os.path.basename(pm.sceneName()))[0]
            # also render to the same folder with the file
            output_dir = os.path.join(os.path.dirname(pm.sceneName()), "temp")
            import tempfile

            playblast_options["filename"] = os.path.join(output_dir, filename).replace(
                "\\", "/"
            )

        from anima.dcc import mayaEnv

        menv = mayaEnv.Maya()
        fps = menv.get_fps()

        result = []
        try:
            self.store_user_options()
            self.set_view_options()
            self.create_hud(self.hud_name)
            import pprint

            pprint.pprint(playblast_options)

            # update all cameras in the scene to have correct film back
            for cam in pm.ls(type="camera"):
                try:
                    cam.verticalFilmAperture.set(
                        cam.horizontalFilmAperture.get()
                        * float(playblast_options["wh"][1])
                        / float(playblast_options["wh"][0])
                    )
                except (AttributeError, RuntimeError) as e:
                    pass

            result = [
                {
                    "video": pm.playblast(**playblast_options),
                    "audio": {
                        "node": audio_node,
                        "offset": playblast_options.get("startTime", 0)
                        - audio_node.offset.get()
                        if audio_node
                        else 0,
                        "duration": (
                            playblast_options.get("endTime", 0)
                            - playblast_options.get("startTime", 0)
                            + 1
                        ),
                    },
                }
            ]
        finally:
            self.restore_user_options()

        video = self.convert_image_sequence_to_video(
            result, delete_source_sequence=True
        )
        return video

    @classmethod
    def convert_image_sequence_to_video(cls, data, delete_source_sequence=False):
        """converts image sequence to video

        :param data: A dictionary containing audio and video information in the following format:

          {
              'video': 'video_path',
              'audio': {
                  'node': audio_node_path,
                  'offset': in frames,
                  'duration': in frames
              }
          }

        :param bool delete_source_sequence: If True, this option will let the function to delete the source image
          sequence.
        """
        import os
        import glob

        frame_rate = 25
        from anima.dcc import mayaEnv

        maya_env = mayaEnv.Maya()
        v = maya_env.get_current_version()
        if v:
            frame_rate = v.task.project.fps

        # convert image sequences to h264
        new_result = []
        original_image_sequence_path = ""
        for output in data:
            # convert each output to a mp4 if the output is a frame
            # sequence
            video_file_path = output
            audio_data = None
            if isinstance(output, dict):
                # this is possibly a more complex output that includes audio
                video_file_path = output.get("video")
                audio_data = output.get("audio")

            original_image_sequence_path = video_file_path
            if video_file_path and "#" in video_file_path:
                # convert to mp4

                # add start_number option
                temp_str = video_file_path.replace("#", "*")
                sequence = sorted(glob.glob(temp_str))
                options = dict()
                if sequence:
                    # Ep002_004_0210_v007.mov.####.png
                    # fix start number for %04d to %05d passage (eg. 9900 to 10010)
                    smallest_start_number = 1e10
                    for file_in_seq in sequence:
                        filename = os.path.basename(file_in_seq)
                        filename = filename.replace(".mov", "")
                        start_number = int(filename.split(".")[1])
                        if start_number < smallest_start_number:
                            smallest_start_number = start_number

                    options["start_number"] = smallest_start_number

                # use the correct frame rate
                options["framerate"] = frame_rate
                options["r"] = frame_rate

                # first convert the #'s to %03d format
                temp_str = video_file_path.replace("#", "")
                hash_count = len(video_file_path) - len(temp_str)
                splits = video_file_path.split("#")
                video_file_path = "%s%s%s" % (
                    splits[0],
                    "%0{hash_count}d".format(hash_count=hash_count),
                    splits[-1],
                )
                video_file_path_h264 = splits[0].replace(".mov.", ".")

                # check audio output
                if audio_data:
                    audio_node = audio_data.get("node")
                    if audio_node:
                        audio_file_path = os.path.expandvars(audio_node.filename.get())
                        # audio offset should be subtracted from the current playblast range
                        # and should be converted to a TimeCode
                        audio_offset = audio_data.get("offset", 0)
                        audio_duration = audio_data.get("duration", 0)

                        options["i"] = [
                            os.path.normpath(video_file_path),
                            os.path.normpath(audio_file_path),
                        ]
                        options["map"] = ["0:0", "1:0"]

                        audio_offset_in_milli_seconds = int(
                            audio_offset * 1000 / frame_rate
                        )
                        duration_in_milli_seconds = int(
                            audio_duration * 1000 / frame_rate
                        )

                        from anima import utils

                        options["ss"] = [
                            None,
                            utils.milliseconds_to_tc(
                                abs(audio_offset_in_milli_seconds)
                            ),
                        ]
                        options["to"] = [
                            None,
                            utils.milliseconds_to_tc(
                                abs(audio_offset_in_milli_seconds)
                                + duration_in_milli_seconds
                            ),
                        ]

                from anima.utils import MediaManager

                mm = MediaManager()
                video_file_path = mm.convert_to_h264(
                    video_file_path, video_file_path_h264, options=options
                )

            new_result.append(video_file_path)

        # delete all the temp files
        if delete_source_sequence and "#" in original_image_sequence_path:
            try:
                video_file_pattern = original_image_sequence_path.replace("#", "*")
                import glob

                for filename in glob.glob(video_file_pattern):
                    os.remove(filename)
            except (OSError, AttributeError):
                pass

        return new_result

    def playblast_shot(self, shot, extra_playblast_options=None):
        """does the real thing"""
        import copy

        shot_playblast_options = copy.copy(self.global_playblast_options)

        shot_playblast_options.update(
            {
                "sequenceTime": 1,
            }
        )
        if extra_playblast_options:
            shot_playblast_options.update(extra_playblast_options)

        # deselect all
        pm.select(cl=1)

        self.check_sequence_name()

        if "wh" not in shot_playblast_options:
            # get project resolution
            # use half HD by default
            width = 1920
            height = 1080
            if self.version:
                project = self.version.task.project
                # get the resolution
                imf = project.image_format
                width = int(imf.width)
                height = int(imf.height)

            shot_playblast_options["wh"] = (width, height)

        try:
            self.store_user_options()
            self.set_view_options()
            self.create_hud(self.hud_name)

            # create video playblast
            temp_video_file_full_path = shot.playblast(options=shot_playblast_options)
        finally:
            self.restore_user_options()

        return temp_video_file_full_path

    def playblast_all_shots(self, extra_playblast_options=None):
        """Playblast all shots.

        :return:
        """
        shots = pm.ls(type="shot")
        if len(shots) <= 0:
            raise RuntimeError("There are no Shots in your Camera Sequencer.")

        pdm = ProgressManager()
        pdm.end_progress()

        caller = pdm.register(len(shots), "Generating Playblasts...")

        generic_playblast_options = {}
        if extra_playblast_options:
            generic_playblast_options.update(extra_playblast_options)

        # if the time range is selected from the time line
        # just use this range
        range_start, range_end = self.get_selected_frame_range()
        generic_playblast_options["startTime"] = range_start
        generic_playblast_options["endTime"] = range_end

        # check audio
        audio_node = self.get_audio_node()
        if audio_node:
            generic_playblast_options.update(
                {"useTraxSounds": False, "sound": audio_node}
            )
        else:
            generic_playblast_options["useTraxSounds"] = True

        temp_video_file_full_paths = []
        import copy

        for shot in shots:
            per_shot_playblast_options = copy.copy(generic_playblast_options)

            shot_start_frame = shot.startFrame.get()
            shot_end_frame = shot.endFrame.get()
            per_shot_playblast_options["startTime"] = shot_start_frame
            per_shot_playblast_options["endTime"] = shot_end_frame

            if self.is_frame_range_selected():
                # skip this shot if the selected playback range do not
                # coincide with this shot range
                if (
                    range_start > shot_start_frame and range_start > shot_end_frame
                ) or (range_end < shot_start_frame and range_end < shot_end_frame):
                    caller.step()
                    continue

            temp_video_file_full_path = self.playblast_shot(
                shot, per_shot_playblast_options
            )
            temp_video_file_full_paths.append(
                {
                    "video": temp_video_file_full_path[0],
                    "audio": {
                        "node": audio_node,
                        "offset": audio_node.offset.get() - shot_start_frame
                        if audio_node
                        else 0,
                        "duration": shot_end_frame - shot_start_frame + 1,
                    },
                }
            )

            caller.step()

        return self.convert_image_sequence_to_video(
            temp_video_file_full_paths, delete_source_sequence=True
        )

    @classmethod
    def upload_outputs(cls, version, video_file_full_paths):
        """Bulk upload outputs to given version

        :param version: Stalker Version instance
        :param list video_file_full_paths: List of file paths
        :return:
        """
        pdm = ProgressManager()
        pdm.end_progress()

        outputs = []
        # register a new caller
        caller = pdm.register(len(video_file_full_paths), "Uploading Playblasts...")
        for output_file_full_path in video_file_full_paths:
            # upload output to server
            output_path = cls.upload_output(
                version=version,
                output_file_full_path=output_file_full_path,
            )

            outputs.append(output_path)
            caller.step()

        return outputs

    @classmethod
    def upload_output(cls, version, output_file_full_path):
        """sets the given file as the output of the given version, also
        generates a thumbnail and a web version if it is a movie file

        :param version: The stalker version instance
        :param output_file_full_path: the path of the media file
        """
        from stalker import Version

        if not isinstance(version, Version):
            raise RuntimeError("version should be a stalker version instance!")

        hires_extension = ".mp4"
        webres_extension = ".webm"
        thumbnail_extension = ".png"

        import os

        if not os.path.exists(output_file_full_path):
            raise RuntimeError("Output file does not exits: %s" % output_file_full_path)

        import os

        output_file_name = os.path.basename(output_file_full_path)

        hires_output_file_name = "%s%s" % (
            os.path.splitext(output_file_name)[0],
            hires_extension,
        )

        webres_output_file_name = "%s%s" % (
            os.path.splitext(output_file_name)[0],
            webres_extension,
        )

        thumbnail_output_file_name = "%s%s" % (
            os.path.splitext(output_file_name)[0],
            thumbnail_extension,
        )

        task = version.task

        hires_path = os.path.join(
            task.absolute_path, "Outputs", "Stalker_Pyramid", hires_output_file_name
        )
        webres_path = os.path.join(
            task.absolute_path,
            "Outputs",
            "Stalker_Pyramid",
            "ForWeb",
            webres_output_file_name,
        )
        thumbnail_path = os.path.join(
            task.absolute_path,
            "Outputs",
            "Stalker_Pyramid",
            "Thumbnail",
            thumbnail_output_file_name,
        )

        # create folders
        try:
            os.makedirs(os.path.dirname(hires_path))
        except OSError:
            pass

        try:
            os.makedirs(os.path.dirname(webres_path))
        except OSError:
            pass

        try:
            os.makedirs(os.path.dirname(thumbnail_path))
        except OSError:
            pass

        import shutil

        shutil.copy(output_file_full_path, hires_path)

        # generate the web version
        from anima.utils import MediaManager

        m = MediaManager()
        temp_web_version_full_path = m.generate_media_for_web(output_file_full_path)

        try:
            shutil.copy(temp_web_version_full_path, webres_path)
        except IOError:
            pass

        temp_thumbnail_full_path = m.generate_thumbnail(output_file_full_path)
        try:
            # also upload thumbnail
            shutil.copy(temp_thumbnail_full_path, thumbnail_path)
        except IOError:
            pass

        project = task.project
        repo = project.repository

        from stalker import Link
        from stalker.db.session import DBSession

        # try to find a file with the same name assigned to the version as
        # output
        found = None
        hires_os_independent_path = repo.to_os_independent_path(hires_path)
        for output in version.outputs:
            if output.full_path == hires_os_independent_path:
                found = True
                break

        # if we found a file with the same name as the output, just overwrite
        # it
        if not found:
            l_hires = Link(
                full_path=repo.to_os_independent_path(hires_path),
                original_filename=hires_output_file_name,
            )

            l_for_web = Link(
                full_path=repo.to_os_independent_path(webres_path),
                original_filename=hires_output_file_name,
            )

            l_hires.thumbnail = l_for_web
            version.outputs.append(l_hires)

            l_thumb = Link(
                full_path=repo.to_os_independent_path(thumbnail_path),
                original_filename=hires_output_file_name,
            )
            l_for_web.thumbnail = l_thumb

            DBSession.add_all([l_hires, l_for_web, l_thumb])
            DBSession.commit()

        return hires_path


def get_cacheable_nodes(reference_node=None):
    """Return the cacheable nodes from the current scene or in the given reference node.

    :param reference_node: A Maya FileReference node. When supplied only the recursive
        content of this reference will be searched for a cacheable node.

    :return:
    """
    pdm = ProgressManager()
    pdm.end_progress()

    # list all cacheable nodes
    cacheable_nodes = []

    if not reference_node:
        transform_nodes = pm.ls(type=pm.nt.Transform)
    else:
        transform_nodes = pm.ls(
            reference_node.nodes(recursive=True), type=pm.nt.Transform
        )

    caller = pdm.register(len(transform_nodes), "Searching for Cacheable Nodes")
    for node in transform_nodes:
        if node.hasAttr("cacheable") and node.getAttr("cacheable"):
            # check if any of its parents has a cacheable attribute
            has_cacheable_parent = False
            for parent in node.getAllParents():
                if parent.hasAttr("cacheable"):
                    has_cacheable_parent = True
                    break

            if not has_cacheable_parent:
                # only include direct references
                ref = node.referenceFile()
                if ref is not None and ref.parent() is None:
                    # skip cacheable nodes coming from layout
                    if (
                        ref.version
                        and ref.version.task.type
                        and ref.version.task.type.name.lower() == "layout"
                    ):
                        caller.step()
                        continue
                cacheable_nodes.append(node)

        caller.step()

    return cacheable_nodes


def get_reference_copy_number(node):
    """Return the reference number of the given reference file.

    :param node: This can be a regular Maya node or a ReferenceFile.
    """
    if not isinstance(node, pm.system.FileReference):
        ref_node = node.referenceFile()
    else:
        ref_node = node

    if not ref_node:
        # not a referenced file
        return 1

    copy_number_list = ref_node.copyNumberList()
    if copy_number_list == ["0"]:
        # there is only one copy of this node
        return 1

    path_with_copy_number = ref_node.withCopyNumber()
    path = ref_node.path
    if path_with_copy_number == path:
        return 1
    else:
        ref_number = int(path_with_copy_number.split("{")[1].split("}")[0]) + 1
        return ref_number


def export_cache_of_nodes(
    cacheable_nodes,
    start_frame=None,
    end_frame=None,
    handles=0,
    step=1,
    isolate=True,
    unload_refs=True,
    cache_format=ALEMBIC,
):
    """Export Alembic/USD caches of the given nodes.

    Args:
        cacheable_nodes (list): The top transform nodes
        start_frame (int): The start frame. If both start and end frame are the same and
            the handle is 0 then a static file will be exported.
        end_frame (int): The end frame. If both start and end frame are the same and
            the handle is 0 then a static file will be exported.
        handles (int): An integer that shows the desired handles from start and end. If
            both start and end frame are the same and the handle is 0 then a static file
            will be exported.
        step (int): Frame step.
        isolate (bool): Isolate the exported object, so it is faster to playback. This
            can sometimes create a problem of constraints not to work on some scenes.
            Default value is True.
        unload_refs (bool): Unloads the references in the scene to speed playback
            performance.
        cache_format (str): Cache format, "alembic" or "usd". The default is "alembic".

    Returns:
        list: List of exported file paths.
    """
    logger.info("INFO: Start export_cache_of_nodes!")
    # stop if there are no cacheable nodes given
    if not cacheable_nodes:
        return

    # load Abc plugin first
    if cache_format == ALEMBIC:
        if not pm.pluginInfo("AbcExport", q=1, l=1):
            pm.loadPlugin("AbcExport")
    elif cache_format == USD:
        if not pm.pluginInfo("mayaUsdPlugin", q=1, l=1):
            try:
                pm.loadPlugin("mayaUsdPlugin")
            except RuntimeError:
                # mayaUsdPlugin not found, skip this
                return

    pdm = ProgressManager()

    cacheable_nodes.sort(key=lambda x: x.getAttr("cacheable"))

    caller = pdm.register(len(cacheable_nodes), "Exporting Alembic Caches")

    if start_frame is None:
        start_frame = int(pm.playbackOptions(q=1, ast=1))
    if end_frame is None:
        end_frame = int(pm.playbackOptions(q=1, aet=1))

    export_animation = bool((end_frame - start_frame + 2 * handles) > 0)

    current_file_full_path = pm.sceneName()
    current_file_path = os.path.dirname(current_file_full_path)
    current_file_name = os.path.basename(current_file_full_path)

    # export caches
    pm.select(None)

    wrong_node_names = ["_rig_", "_proxy_"]
    wrong_node_names_starts_with = ["rig_"]
    wrong_node_names_ends_with = ["_rig"]

    default_playback_option = pm.playbackOptions(q=1, v=True)

    # leave off only one panel in the viewport
    kill_all_torn_off_panels()
    maximize_first_model_panel()

    # create a lut for cacheable_node to its related reference
    cacheable_node_references = {}
    if unload_refs:
        for cacheable_node in cacheable_nodes:
            ref = cacheable_node.referenceFile()
            if ref:
                # get the top most reference
                parent_ref = ref.parent()
                while parent_ref:
                    ref = parent_ref
                    parent_ref = ref.parent()

            # get related references
            # sometimes the node is parented or constrained to an object
            # try to find all the required references to load for this cacheable node
            # to work properly
            related_references = set()
            references_to_traverse = {cacheable_node.referenceFile()}
            references_already_visited = set()

            while references_to_traverse:
                current_ref = references_to_traverse.pop()
                if current_ref in references_already_visited:
                    # already scanned this reference
                    continue
                else:
                    references_already_visited.add(current_ref)
                roots_of_ref_node = get_root_nodes(current_ref)
                nodes_to_evaluate = copy.copy(roots_of_ref_node)
                for root_node in roots_of_ref_node:
                    nodes_to_evaluate += root_node.listRelatives(
                        ad=1, type=pm.nt.Transform
                    )
                for node in nodes_to_evaluate:
                    for constraint_node in pm.ls(
                        node.listHistory(), type=pm.nt.Constraint
                    ):
                        for input_node in constraint_node.inputs():
                            related_ref = input_node.referenceFile()
                            if related_ref is not None:
                                # go to the top most reference
                                related_ref = related_ref.topmost_parent
                                if related_ref != ref:
                                    related_references.add(related_ref)
                                    references_to_traverse.add(related_ref)

            # make it a list of unique values
            related_references = list(set(related_references))

            cacheable_node_references[cacheable_node.name()] = {
                "ref": ref,
                "related_refs": related_references,
            }
    else:
        for cacheable_node in cacheable_nodes:
            cacheable_node_references[cacheable_node.name()] = {
                "ref": None,
                "related_refs": [],
            }

    # unload all references
    ref_load_states = {}
    if unload_refs:
        for ref in pm.listReferences():
            is_loaded = ref.isLoaded()
            ref_load_states[ref] = is_loaded
            if is_loaded:
                ref.unload()

    import tempfile
    import shutil

    output_full_paths = []
    for cacheable_node_name in sorted(cacheable_node_references):
        logger.info("INFO: exporting: {}".format(cacheable_node_name))

        if unload_refs:
            # load the reference first
            ref = cacheable_node_references[cacheable_node_name]["ref"]
            if ref:
                ref.load()

            # load related_references
            related_refs = cacheable_node_references[cacheable_node_name][
                "related_refs"
            ]
            for related_ref in related_refs:
                related_ref.load()

        cacheable_node = pm.PyNode(cacheable_node_name)

        cacheable_attr_value = cacheable_node.getAttr("cacheable")
        copy_number = get_reference_copy_number(cacheable_node)

        # get cacheable_attributes | attributes that needs to be exported
        cacheable_attrs = ""
        if cacheable_node.hasAttr("cacheable_attrs"):
            cacheable_attrs = cacheable_node.cacheable_attrs.get().strip().split(" ")

        # isolate in all panels
        if isolate:
            panel_list = pm.getPanel(type="modelPanel")
            for panel in panel_list:
                pm.isolateSelect(panel, state=1)
                pm.isolateSelect(panel, ado=cacheable_node)

        hidden_nodes = []
        nodes_to_consider = cacheable_node.getChildren(type="transform")
        while len(nodes_to_consider):
            current_node = nodes_to_consider.pop(0)
            underscored_name = camel_case_to_underscore(
                current_node.name().split(":")[-1]
            )

            if (
                any([n in underscored_name for n in wrong_node_names])
                or any(
                    [
                        underscored_name.startswith(n)
                        for n in wrong_node_names_starts_with
                    ]
                )
                or any(
                    [underscored_name.endswith(n) for n in wrong_node_names_ends_with]
                )
            ):
                if current_node.v.get() is True and not current_node.v.isLocked():
                    current_node.v.set(False)
                    hidden_nodes.append(current_node)
            else:
                nodes_to_consider.extend(current_node.getChildren(type="transform"))

        output_path = os.path.join(
            current_file_path,
            "Outputs/{dir_name}/{cacheable_attr}{copy_number}/".format(
                dir_name=CACHE_FORMAT_DATA[cache_format]["output_dir"],
                cacheable_attr=cacheable_attr_value,
                copy_number=copy_number,
            ),
        )

        if cache_format == ALEMBIC:
            cache_file_name_template = (
                "{base_name}_{start_frame}_{end_frame}_{cacheable_attr}{copy_number}"
                "{ext}"
            )
        else:
            # dont use start and end frame numbers in the filename for the USD format
            cache_file_name_template = "{base_name}_{cacheable_attr}{copy_number}{ext}"
        output_filename = cache_file_name_template.format(
            base_name=os.path.splitext(current_file_name)[0],
            start_frame=start_frame,
            end_frame=end_frame,
            cacheable_attr=cacheable_attr_value,
            copy_number=copy_number,
            ext=CACHE_FORMAT_DATA[cache_format]["file_extension"],
        )

        output_full_path = os.path.join(output_path, output_filename).replace("\\", "/")
        try:
            os.makedirs(os.path.dirname(output_full_path))
        except OSError:
            pass

        if cache_format == ALEMBIC:
            if int(pm.about(v=1)) >= 2017:
                command = (
                    'AbcExport -j "-frameRange {start_frame} {end_frame} -step {step} '
                    "-ro -stripNamespaces -uvWrite -wholeFrameGeo "
                    "-worldSpace -autoSubd -writeUVSets -dataFormat "
                    " ogawa -writeVisibility -eulerFilter "
                )
            else:
                command = (
                    'AbcExport -j "-frameRange {start_frame} {end_frame} -step {step}'
                    " -ro -stripNamespaces -uvWrite -wholeFrameGeo "
                    "-worldSpace -writeUVSets -writeVisibility "
                )

            # add cacheable_attrs if any
            if cacheable_attrs:
                command = "{} {}".format(
                    command,
                    " ".join(map(lambda x: "-attr {}".format(x), cacheable_attrs)),
                )

            command += ' -root {node} -file {file_path}";'
        else:
            command = (
                'file -force -options ";exportUVs=1;exportSkels=none;exportSkin=none;'
                "exportBlendShapes=0;exportColorSets=1;defaultMeshScheme=catmullClark;"
                "defaultUSDFormat=usdc;animation={export_animation};eulerFilter=0;"
                "staticSingleSample=0;startTime={start_frame};endTime={end_frame};"
                "frameStride={step};frameSample=0.0;parentScope={parentScope};"
                "exportDisplayColor=0;shadingMode=useRegistry;"
                "convertMaterialsTo=UsdPreviewSurface;exportInstances=1;"
                'exportVisibility=1;mergeTransformAndShape=1;stripNamespaces=1" '
                '-typ "USD Export" -pr -es "{file_path}";'
            )

        # use a temp file to export the cache
        # and then move it in to place
        temp_cache_file_path = tempfile.mktemp(
            suffix=CACHE_FORMAT_DATA[cache_format]["file_extension"]
        ).replace("\\", "/")

        command_to_exec = ""
        if cache_format == ALEMBIC:
            command_to_exec = command.format(
                start_frame=int(start_frame - handles),
                end_frame=int(end_frame + handles),
                step=step,
                node=cacheable_node.fullPath(),
                file_path=temp_cache_file_path,
            )
        elif cache_format == USD:
            logger.info(
                "cacheable_node.fullPath(): {}".format(cacheable_node.fullPath())
            )
            pm.select(cacheable_node)
            command_to_exec = command.format(
                parentScope=cacheable_node.namespace()[:-1],
                start_frame=int(start_frame - handles),
                end_frame=int(end_frame + handles),
                export_animation=1 if export_animation else 0,
                step=step,
                file_path=temp_cache_file_path,
            )

        logger.info("INFO: Executing command: {}".format(command_to_exec))
        pm.mel.eval(command_to_exec)
        # move in to place
        shutil.move(temp_cache_file_path, output_full_path)
        output_full_paths.append(output_full_path)

        # reveal any previously hidden nodes
        for node in hidden_nodes:
            node.v.set(True)

        # restore isolation in all panels
        if isolate:
            panel_list = pm.getPanel(type="modelPanel")
            for panel in panel_list:
                pm.isolateSelect(panel, state=0)

        if unload_refs:
            # unload the reference
            if ref:
                ref.unload()
            # and unload the related references
            for related_ref in related_refs:
                related_ref.unload()

        caller.step()
        print("INFO: Export successful: {}".format(cacheable_node_name))

    if unload_refs:
        # load all references back
        for ref in pm.listReferences():
            if ref_load_states[ref]:
                ref.load()

    # restore playback option
    pm.playbackOptions(v=default_playback_option)
    print("INFO: End export_cache_of_nodes!")

    # add the outputs as an output for the current version
    add_outputs_to_current_version(output_full_paths, cache_format)

    return output_full_paths


def add_outputs_to_current_version(output_full_paths, output_type_name):
    """Add the given file as a Link to the current version.

    :param list output_full_paths: A list of file paths.
    :param str output_type_name: The output type, e.g Alembic, USD, Image, Video, Audio
        etc.
    :return: List of Link instances that are newly created
    """
    from anima.dcc import mayaEnv

    m = mayaEnv.Maya()
    current_version = m.get_current_version()

    if current_version is None:
        return

    import os
    from stalker import Link, Repository, Type, LocalSession
    from stalker.db.session import DBSession

    # get Alembic type
    with DBSession.no_autoflush:
        output_type = Type.query.filter(Type.name == output_type_name).first()

    if not output_type:
        output_type = Type(
            name=output_type_name, code=output_type_name, target_entity_type="Link"
        )

    local_session = LocalSession()
    with DBSession.no_autoflush:
        logged_in_user = local_session.logged_in_user

    # Create a Link with the output file and link it to the current version
    for output_file_path in output_full_paths:
        new_link = Link(
            full_path=Repository.to_os_independent_path(output_file_path),
            original_filename=os.path.basename(output_file_path),
            type=output_type,
            created_by=logged_in_user,
        )
        DBSession.add(new_link)
        current_version.outputs.append(new_link)
    DBSession.commit()


def export_cache_of_selected_cacheable_nodes(
    start_frame=None,
    end_frame=None,
    handles=0,
    step=1,
    isolate=True,
    unload_refs=True,
    cache_format=ALEMBIC,
):
    """Export Alembic/USD caches of the selected cacheable nodes.

    Args:
        start_frame (int): The start frame. If both start and end frame are the same and
            the handle is 0 then a static file will be exported.
        end_frame (int): The end frame. If both start and end frame are the same and
            the handle is 0 then a static file will be exported.
        handles (int): An integer that shows the desired handles from start and end. If
            both start and end frame are the same and the handle is 0 then a static file
            will be exported.
        step (int): Frame step.
        isolate (bool): Isolate the exported object, so it is faster to playback. This
            can sometimes create a problem of constraints not to work on some scenes.
            Default value is True.
        unload_refs (bool): Unloads the references in the scene to speed playback
            performance.
        cache_format (str): Cache format, "alembic" or "usd". The default is "alembic".

    Returns:
        list: List of exported file paths.
    """
    # get selected cacheable nodes in the current scene
    cacheable_nodes = [
        n for n in pm.selected() if n.hasAttr("cacheable") and n.getAttr("cacheable")
    ]
    return export_cache_of_nodes(
        cacheable_nodes=cacheable_nodes,
        start_frame=start_frame,
        end_frame=end_frame,
        handles=handles,
        step=step,
        isolate=isolate,
        unload_refs=unload_refs,
        cache_format=cache_format,
    )


def export_cache_of_all_cacheable_nodes(
    start_frame=None,
    end_frame=None,
    handles=0,
    step=1,
    isolate=True,
    unload_refs=True,
    cache_format=ALEMBIC,
):
    """Export Alembic/USD caches by looking at the current scene and try to find
    transform nodes which has an attribute called "cacheable".

    Args:
        start_frame (int): The start frame. If both start and end frame are the same and
            the handle is 0 then a static file will be exported.
        end_frame (int): The end frame. If both start and end frame are the same and
            the handle is 0 then a static file will be exported.
        handles (int): An integer that shows the desired handles from start and end. If
            both start and end frame are the same and the handle is 0 then a static file
            will be exported.
        step (int): Frame step.
        isolate (bool): Isolate the exported object, so it is faster to playback. This
            can sometimes create a problem of constraints not to work on some scenes.
            Default value is True.
        unload_refs (bool): Unloads the references in the scene to speed playback
            performance.
        cache_format (str): Cache format, "alembic" or "usd". The default is "alembic".

    Returns:
        list: List of exported file paths.
    """
    # get cacheable nodes in the current scene
    cacheable_nodes = get_cacheable_nodes()
    return export_cache_of_nodes(
        cacheable_nodes=cacheable_nodes,
        start_frame=start_frame,
        end_frame=end_frame,
        handles=handles,
        step=step,
        isolate=isolate,
        unload_refs=unload_refs,
        cache_format=cache_format,
    )


def extract_version_from_path(path):
    """extracts version number ("_v%03d") as an integer from the given path

    :param str path: The path to extract the version number from
    """
    import re

    version_matcher = re.compile(VERSION_NUMBER_RE)
    m = re.match(version_matcher, path)
    if m:
        return int(m.group(2))


def auto_reference_caches(cache_type=ALEMBIC):
    """Reference caches from Animation scene of the same shot.

    :param str cache_type: Desired cache type, one of ``auxiliary.ALEMBIC`` or
        ``auxiliary.USD``, default value is ALEMBIC and USD is meaningless for now.
    """
    # update all references first
    update_cache_references(cache_type=cache_type)

    import glob
    from anima.dcc import mayaEnv
    from stalker import Shot, Task, Type, Version

    m = mayaEnv.Maya()
    v = m.get_current_version()
    if not isinstance(v, Version):
        raise RuntimeError("Active scene is not related to a Version.")

    # get the task
    task = v.task
    if not task.parent:
        raise RuntimeError("This is a root task, please open a Shot based version!")

    shot = task.parent
    if not isinstance(shot, Shot):
        raise RuntimeError("This is not a shot task!")

    # find the animation task
    anim_type = Type.query.filter(Type.name == "Animation").first()
    anim_task = (
        Task.query.filter(Task.parent == shot).filter(Task.type == anim_type).first()
    )

    if not anim_task:
        raise RuntimeError(
            "Cannot find anim task under shot with id: {}".format(shot.id)
        )

    # get the cache folder
    cache_path = os.path.join(
        anim_task.absolute_path, "Outputs", CACHE_FORMAT_DATA[cache_type]["output_dir"]
    )

    # there should be one folder for each asset
    for dir_name in os.listdir(cache_path):
        dir_abs_path = os.path.join(cache_path, dir_name)
        if not os.path.isdir(dir_abs_path):
            # this is not a directory skip it
            continue

        # the directory name is also the instance name
        asset_instance_name = dir_name
        glob_pattern = "{}/*{}*".format(dir_abs_path, asset_instance_name)

        all_cache_files = sorted(glob.glob(glob_pattern), key=extract_version_from_path)
        if not all_cache_files:
            continue
        latest_cache_file_name = all_cache_files[-1]
        # do an exception for ``rendercam`` and do not use the _fixed one
        if "rendercam" in asset_instance_name and latest_cache_file_name.endswith(
            "_fixed{}".format(CACHE_FORMAT_DATA[cache_type]["file_extension"])
        ):
            # use the non fixed one
            latest_cache_file_name = all_cache_files[-2]

        latest_cache_file_path = latest_cache_file_name.replace("\\", "/")

        # check if it is already referenced in the current scene
        already_referenced = False
        for ref in pm.listReferences():
            if ref.path == latest_cache_file_path:
                already_referenced = True
                break

        if already_referenced:
            # skip this cache
            continue

        # reference the cache file
        pm.createReference(
            latest_cache_file_path,
            gl=True,
            namespace=asset_instance_name,
            options="v=0",
        )


def update_cache_references(cache_type=ALEMBIC):
    """Update referenced alembic files in the current scene.

    :param str cache_type: Desired cache type, one of ``auxiliary.ALEMBIC`` or
        ``auxiliary.USD``, default value is ALEMBIC and USD is meaningless for now.
    """
    # TODO: This tool needs improvement
    # There is a need for a UI similar to the ``VersionUpdater``
    # It is even possible to directly use that UI
    # So, this tool need to return the updatable references coupled with the
    # possible new path to update to
    # the user should select what to update
    # and then another tool should update it
    #
    # But, this is exactly what VersionUpdater does.

    import glob

    version_matcher = re.compile(VERSION_NUMBER_RE)

    updated_path_info = []
    for ref in pm.listReferences():
        is_loaded = ref.isLoaded()
        path = ref.path
        if not path.endswith(CACHE_FORMAT_DATA[cache_type]["file_extension"]):
            continue

        m = re.match(version_matcher, path)
        if not m:
            continue

        prefix = m.group(1)

        # glob the files
        glob_pattern = "%s*" % prefix
        # The versions will always be sorted properly
        # we don't need to check if the last path in the is the latest one
        all_abc_files = sorted(glob.glob(glob_pattern))
        # there may be different takes,
        # but, we don't need check for that too, because we are globbing for a path
        # that includes the ``take_name``

        last_abc_file = all_abc_files[-1]
        if last_abc_file != os.path.expandvars(path):
            # replace it
            updated_path_info.append((path, last_abc_file))
            ref.replaceWith(last_abc_file)
            # preserve the loaded state
            if not is_loaded:
                ref.unload()

    if updated_path_info:
        print("###################")
        print("Updated:")

    for old_ref_path, new_ref_path in updated_path_info:
        print("%s -> %s" % (old_ref_path, new_ref_path))


# noinspection PyStatementEffect
class BarnDoorSimulator(object):
    """A aiBarnDoor simulator"""

    sides = ["top", "bottom", "left", "right"]
    message_storage_attr_name = "barnDoorSimulatorData"
    custom_data_storage_attr_name = "barnDoorSimulatorCustomData"

    def __init__(self):
        self.frame_curve = None
        self.light = None
        self.barn_door = None

        self.script_job_no = -1

        self.preview_curves = {"top": [], "bottom": [], "left": [], "right": []}

        self.joints = {
            "top": [],
            "bottom": [],
            "left": [],
            "right": [],
        }

    def create_barn_door(self):
        """creates the barn door node"""
        light_shape = self.light.getShape()
        inputs = light_shape.inputs(type="aiBarndoor")
        if inputs:
            self.barn_door = inputs[0]
        else:
            self.barn_door = pm.createNode("aiBarndoor")
            (
                self.barn_door.attr("message")
                >> light_shape.attr("aiFilters").next_available
            )

    def store_data(self, data):
        """stores the given data"""
        if not self.light.hasAttr(self.custom_data_storage_attr_name):
            pm.addAttr(self.light, ln=self.custom_data_storage_attr_name, dt="string")

        self.light.setAttr(self.custom_data_storage_attr_name, data)

    def store_nodes(self, nodes):
        """stores the nodes"""
        for node in nodes:
            self.store_node(node)

    def store_node(self, node):
        """stores the node in the storage attribute"""
        if not self.light.hasAttr(self.message_storage_attr_name):
            pm.addAttr(self.light, ln=self.message_storage_attr_name, m=1)

        node.message >> self.light.attr(self.message_storage_attr_name).next_available

    def create_frame_curve(self):
        """creates the frame curve"""
        self.frame_curve = pm.curve(
            d=1,
            p=[
                (-0.5, 0.5, 0),
                (0.5, 0.5, 0),
                (0.5, -0.5, 0),
                (-0.5, -0.5, 0),
                (-0.5, 0.5, 0),
            ],
            k=[0, 1, 2, 3, 4],
        )
        self.store_node(self.frame_curve)

    def create_preview_curve(self, side):
        """creates preview curves"""
        # create two joints
        j1 = pm.createNode("joint")
        j2 = pm.createNode("joint")

        j1.t.set(-0.5, 0, 0)
        j2.t.set(0.5, 0, 0)

        self.joints[side] += [j1, j2]

        # create one nurbs curve
        preview_curve = pm.curve(d=1, p=[(-0.5, 0, 0), (0.5, 0, 0)], k=[0, 1])
        self.preview_curves[side].append(preview_curve)

        # bind the joints to the curveShape
        pm.select([preview_curve, j1, j2])
        skin_cluster = pm.skinCluster()

        self.store_nodes([j1, j2, preview_curve, skin_cluster])

    def create_expression(self):
        """creates the expression"""
        expr = """float $frame_scale, $cone_angle;

if({light}.penumbraAngle < 0){{
    $cone_angle = {light}.coneAngle;
}} else {{
    $cone_angle = {light}.coneAngle + {light}.penumbraAngle;
}}

$frame_scale = tan(deg_to_rad($cone_angle * 0.5));
{frame}.sx = {frame}.sy = {frame}.sz = $frame_scale;

// top
{top_left_joint}.ty = -{barn_door}.barndoorTopLeft + 0.5;
{top_left_joint}.tx = -0.5;
{top_right_joint}.ty = -{barn_door}.barndoorTopRight + 0.5;
{top_right_joint}.tx = 0.5;

// top edge
{top_edge_left_joint}.ty = {top_left_joint}.ty + {barn_door}.barndoorTopEdge;
{top_edge_left_joint}.tx = -0.5;
{top_edge_right_joint}.ty = {top_right_joint}.ty + {barn_door}.barndoorTopEdge;
{top_edge_right_joint}.tx = 0.5;

// bottom
{bottom_left_joint}.ty = -{barn_door}.barndoorBottomLeft + 0.5;
{bottom_left_joint}.tx = -0.5;
{bottom_right_joint}.ty = -{barn_door}.barndoorBottomRight + 0.5;
{bottom_right_joint}.tx = 0.5;

// bottom edge
{bottom_edge_left_joint}.ty = {bottom_left_joint}.ty - {barn_door}.barndoorBottomEdge;
{bottom_edge_left_joint}.tx = -0.5;
{bottom_edge_right_joint}.ty = {bottom_right_joint}.ty - {barn_door}.barndoorBottomEdge;
{bottom_edge_right_joint}.tx = 0.5;

// left
{left_top_joint}.tx = {barn_door}.barndoorLeftTop - 0.5;
{left_top_joint}.ty = 0.5;
{left_bottom_joint}.tx = {barn_door}.barndoorLeftBottom - 0.5;
{left_bottom_joint}.ty = -0.5;

// left edge
{left_edge_top_joint}.tx = {left_top_joint}.tx - {barn_door}.barndoorLeftEdge;
{left_edge_top_joint}.ty = 0.5;
{left_edge_bottom_joint}.tx = {left_bottom_joint}.tx - {barn_door}.barndoorLeftEdge;
{left_edge_bottom_joint}.ty = -0.5;

// right
{right_top_joint}.tx = {barn_door}.barndoorRightTop - 0.5;
{right_top_joint}.ty = 0.5;
{right_bottom_joint}.tx = {barn_door}.barndoorRightBottom - 0.5;
{right_bottom_joint}.ty = -0.5;

// right edge
{right_edge_top_joint}.tx = {right_top_joint}.tx + {barn_door}.barndoorRightEdge;
{right_edge_top_joint}.ty = 0.5;
{right_edge_bottom_joint}.tx = {right_bottom_joint}.tx + {barn_door}.barndoorRightEdge;
{right_edge_bottom_joint}.ty = -0.5;""".format(
            **{
                "light": self.light.name(),
                "frame": self.frame_curve.name(),
                "barn_door": self.barn_door.name(),
                "top_left_joint": self.joints["top"][0],
                "top_right_joint": self.joints["top"][1],
                "top_edge_left_joint": self.joints["top"][2],
                "top_edge_right_joint": self.joints["top"][3],
                "bottom_left_joint": self.joints["bottom"][0],
                "bottom_right_joint": self.joints["bottom"][1],
                "bottom_edge_left_joint": self.joints["bottom"][2],
                "bottom_edge_right_joint": self.joints["bottom"][3],
                "left_top_joint": self.joints["left"][0],
                "left_bottom_joint": self.joints["left"][1],
                "left_edge_top_joint": self.joints["left"][2],
                "left_edge_bottom_joint": self.joints["left"][3],
                "right_top_joint": self.joints["right"][0],
                "right_bottom_joint": self.joints["right"][1],
                "right_edge_top_joint": self.joints["right"][2],
                "right_edge_bottom_joint": self.joints["right"][3],
            }
        )

        expr_node = pm.expression(s=expr)
        self.store_node(expr_node)

    def create_script_job(self):
        """creates the script job that disables the affected highlight"""
        script_job_no = pm.scriptJob(
            e=[
                "SelectionChanged",
                'if pm.ls(sl=1) and pm.ls(sl=1)[0].name() == "%s":\n'
                "    pm.displayPref(displayAffected=False)\n"
                "else:\n"
                "    pm.displayPref(displayAffected=True)" % self.light.name(),
            ]
        )
        self.store_data("%s" % script_job_no)

    def setup(self):
        """setup the magic"""
        # create 4 preview curves
        self.create_frame_curve()

        for side in self.sides:
            self.create_preview_curve(side)
            # and one for the edge
            self.create_preview_curve(side)

            # set main curve to reference
            preview_curve = self.preview_curves[side][0]
            preview_curve.setAttr("overrideEnabled", 1)
            preview_curve.setAttr("overrideColor", 6)

            # set edge curve to template
            edge_curve = self.preview_curves[side][1]
            edge_curve.setAttr("overrideEnabled", 1)
            edge_curve.setAttr("overrideColor", 13)

            # parent the joints to the frame curve
            pm.parent(self.joints[side][0], self.frame_curve)
            pm.parent(self.joints[side][1], self.frame_curve)
            pm.parent(self.joints[side][2], self.frame_curve)
            pm.parent(self.joints[side][3], self.frame_curve)

        # parent it to the light
        pm.parent(self.frame_curve, self.light)

        self.frame_curve.setAttr("t", [0, 0, -0.5])
        self.frame_curve.setAttr("r", [0, 0, 0])
        self.frame_curve.setAttr("s", [1, 1, 1])

        self.create_barn_door()
        self.create_expression()

        # hide joints
        for side in self.sides:
            self.joints[side][0].v.set(0)
            self.joints[side][1].v.set(0)

            # and edge
            self.joints[side][2].v.set(0)
            self.joints[side][3].v.set(0)

        # group curves
        all_preview_curves = []
        map(all_preview_curves.extend, self.preview_curves.values())
        shapes_group = pm.group(
            all_preview_curves, n="%s_barndoor_preview_curves" % self.light.name()
        )

        self.store_node(shapes_group)

        # create script job
        self.create_script_job()

        # select the light again
        pm.select(self.light)

    def unsetup(self):
        """deletes the barn door setup"""
        if self.light:
            try:
                pm.delete(self.light.attr(self.message_storage_attr_name).inputs())
            except AttributeError:
                pass
            pm.scriptJob(k=int(self.light.getAttr(self.custom_data_storage_attr_name)))
        else:
            # try to delete the by using the barndoor group
            found_light = False
            for node in pm.ls(sl=1, type="transform"):
                # list all lights and try to find the light that has this group
                for light in pm.ls(type=pm.nt.Light):
                    light_parent = light.getParent()
                    if light_parent.hasAttr(self.message_storage_attr_name):
                        if (
                            node
                            in light_parent.attr(
                                self.message_storage_attr_name
                            ).inputs()
                        ):
                            self.light = light_parent
                            found_light = True
                            self.unsetup()

                # if the code comes here than this node is not listed in any
                # lights, so delete it if it contains the string
                # "barndoor_preview_curves" in its name
                if not found_light and "barndoor_preview_curves" in node.name():
                    pm.delete(node)


def create_shader(shader_tree, name=None):
    """Creates a shader tree from the given shader tree.

    The shader_tree is a Python dictionary showing node types and attribute
    values.

    Each shader_tree can create only one shading network. The format of the
    dictionary should be as follows.

    shader_tree: {
        'type': <- The maya node type of the toppest shader
        'class': <- The type of the shading node, one of
            "asLight", "asPostProcess", "asRendering", "asShader", "asTexture"
             "asUtility"
        'attr': {
            <- A dictionary that contains attribute names and values.
            'attr1': {
                'type': --- type name of the connected node
                'attr': {
                    <- attribute values ->
                }
            }
        }
    }

    :param dict shader_tree: A dictionary showing the shader tree attributes.
    :return:
    """
    shader_type = shader_tree["type"]

    if "class" in shader_tree:
        class_ = shader_tree["class"]
    else:
        class_ = "asShader"

    shader = pm.shadingNode(shader_type, **{class_: 1})

    if name:
        shader.rename(name)

    attributes = shader_tree["attr"]

    for key in attributes:
        value = attributes[key]
        if isinstance(value, dict):
            node = create_shader(value)
            output_attr = value["output"]
            node.attr(output_attr) >> shader.attr(key)
        else:
            shader.setAttr(key, value)

    return shader


def match_hierarchy(source, target, node_types=None, use_long_names=False):
    """Matches the objects in two different hierarchy by looking at their
    names.

    Returns a dictionary where you can look up for matches by using the object
    name.

    :param source: The source node. It can be a parent node. So the match
      includes the descendants.
    :param target: The target node.
    :param node_types: A tuple showing the node types to match. The default
      value is (pm.nt.Mesh, pm.nt.NurbsSurface).
    :param use_long_names: Precisely match the placement in the hierarchy.
    """
    if node_types is None:
        node_types = (pm.nt.Mesh, pm.nt.NurbsSurface)

    source_nodes = source.listRelatives(ad=1, type=node_types)
    target_nodes = target.listRelatives(ad=1, type=node_types)

    source_node_names = []
    target_node_names = []

    lut = {"match": [], "no_match": []}
    # exit early if there is only one source and one target
    # match them in any case
    if len(source_nodes) == 1 and len(target_nodes) == 1:
        lut["match"] = [(source_nodes[0], target_nodes[0])]
        return lut

    for node in source_nodes:
        if not use_long_names:
            name = node.name().split(":")[-1].split("|")[-1]
        else:
            # use the long name
            name = "|".join(map(lambda x: x.split(":")[-1], node.longName().split("|")))

        source_node_names.append(name)

    for node in target_nodes:
        if not use_long_names:
            name = node.name().split(":")[-1].split("|")[-1]
        else:
            name = "|".join(map(lambda x: x.split(":")[-1], node.longName().split("|")))
        target_node_names.append(name)

    for i, target_node in enumerate(target_nodes):
        target_node_name = target_node_names[i]
        try:
            tmp_target_node_name = target_node_name
            # replace only the first occurrence of "Deformed"
            if target_node_name.endswith("Deformed"):
                tmp_target_node_name = target_node_name.replace("Deformed", "", 1)
            index = source_node_names.index(tmp_target_node_name)
        except ValueError:
            lut["no_match"].append(target_node)
        else:
            lut["match"].append((source_nodes[index], target_nodes[i]))

    return lut


def camel_case_to_underscore(name):
    """Converts the given CamelCase formatted string to underscore formatted
    one

    :param name:
    :return:
    """
    name = FIRST_CAP_RE.sub(r"\1_\2", name)
    return ALL_CAP_RE.sub(r"\1_\2", name).lower()


class Cell(object):
    """An implementation for a grid cell

    Holds points in space. It is easy to find a corresponding point with using
    a cell.
    """

    def __init__(self):
        self.index = [0, 0, 0]
        self.singular_index = None
        self.points = []
        self.bbox = None


class Grid(object):
    """A simple grid implementation for component search"""

    def __init__(self):
        self.divisions = [1, 1, 1]
        self.bbox = None
        self.tree = []

    def add_point(self, point):
        """Adds the given point to a cell.

        :param point:
        :return:
        """
        raise NotImplementedError()

    def to_index(self, pos):
        """converts the given position in space to a cell index

        :param pos: A point position in space
        """
        raise NotImplementedError()

    def to_cell(self, pos):
        """returns a cell in the given position in space or none if no cell
        contains that point.

        :param pos: A point position in space
        :return:
        """
        raise NotImplementedError()


class DummyWindowLight(object):
    """generates dummy plane for given lights"""

    shader_name = "oyToolbox_dummy_window_light_shader"
    shading_engine_name = "oyToolbox_dummy_window_light_shaderSG"

    kelvin_min = 1000
    kelvin_max = 30000

    def __init__(self, light=None):
        self.light = light
        self._shader = None
        self._shading_engine = None
        self._plane = None

    def update(self):
        """updates the node"""
        plane = self.plane
        self._update_plane_color()
        self._set_light_attributes()

    def _set_light_attributes(self):
        """sets the default light attributes"""
        light_shape = self.light.getShape()
        light_shape.aiIndirect.set(0)
        light_shape.aiSamples.set(1)

    @property
    def shader(self):
        """returns the shader"""
        if self._shader:
            return self._shader
        else:
            shader = pm.ls(self.shader_name)
            if not shader:
                self._create_shader()
                return self._shader
            else:
                self._shader = shader[0]
                shading_engine = self._shader.outColor.outputs(type=pm.nt.ShadingEngine)
                if shading_engine:
                    self._shading_engine = shading_engine[0]
                else:
                    self._create_shading_engine()
                return shader[0]

    @property
    def shading_engine(self):
        """returns the shading engine"""
        if self._shading_engine:
            return self._shading_engine
        else:
            self._shading_engine = self._create_shading_engine()
            return self._shading_engine

    @property
    def plane(self):
        """returns the plane"""
        self._validate_light(self.light)

        # get the first polygon object under the light
        children_shapes = [
            n.getShape()
            for n in self.light.getChildren(type=pm.nt.Transform)
            if n is not None
        ]

        if children_shapes:
            plane_shape = None
            while children_shapes:
                plane_shape = children_shapes.pop(0)
                if plane_shape is not None:
                    break

            if plane_shape:
                self._plane = plane_shape.getParent()
                return self._plane
            else:
                return self._create_plane()
        else:
            # create the plane
            return self._create_plane()

    def _create_shading_engine(self):
        """creates the shading engine"""
        if self.shader:
            # get the shading engine from shader
            shading_engines = self.shader.outputs(type=pm.nt.ShadingEngine)
            if shading_engines:
                self._shading_engine = shading_engines[0]

        if not self._shading_engine:
            self._shading_engine = pm.sets(
                renderable=True,
                noSurfaceShader=True,
                empty=True,
                name=self.shading_engine_name,
            )

        return self._shading_engine

    def _create_shader(self):
        self._shader = pm.shadingNode("surfaceShader", asShader=1)
        self._shader.rename(self.shader_name)

        self._shader.outColor >> self.shading_engine.surfaceShader

        # create the ramp
        import maya.cmds as cmds

        kelvin_ramp = pm.shadingNode("ramp", asTexture=1)
        intensity_ramp = pm.shadingNode("ramp", asTexture=1)
        intensity_ramp.attr("type").set(1)
        intensity_ramp.interpolation.set(2)

        intensity_ramp.colorEntryList[0].color.set(0, 0, 0)
        intensity_ramp.colorEntryList[0].position.set(0)

        kelvin_ramp.outColor >> intensity_ramp.colorEntryList[1].color
        intensity_ramp.colorEntryList[1].position.set(0.707)

        intensity_ramp.colorEntryList[2].color.set(1, 1, 1)
        intensity_ramp.colorEntryList[2].position.set(1)

        # set the colors of the ramp
        kelvin_range = range(self.kelvin_min, self.kelvin_max, 1000)
        total_colors = len(kelvin_range)
        for i, kelvin in enumerate(kelvin_range):
            color = cmds.arnoldTemperatureToColor(kelvin)
            kelvin_ramp.colorEntryList[i].color.set(color)
            kelvin_ramp.colorEntryList[i].position.set(float(i) / float(total_colors))

        # connect ramp to the surfaceShaders.outColor
        intensity_ramp.outColor >> self.shader.outColor

    def _validate_light(self, light):
        if light is None:
            raise RuntimeError("No Light specified")

        return light

    def _create_plane(self):
        """there should be a light"""
        self._validate_light(self.light)

        trans, pplane = pm.polyPlane()
        shape = trans.getShape()
        self._plane = trans

        # parent it under the light
        pm.parent(self._plane, self.light, r=1)
        self._plane.t.set(0, 0, 0.05)
        self._plane.r.set(90, 0, 0)
        self._plane.s.set(2, 2, 2)

        # close any indirect rays
        shape.aiVisibleInDiffuse.set(0)
        shape.aiVisibleInGlossy.set(0)

        # ask the shader to create it
        a = self.shader

        # assign the shader
        pm.sets(self.shading_engine, fe=[self._plane])
        self._update_plane_color()

    def _update_plane_color(self):
        """updates the plane uv according to the light color"""
        self._validate_light(self.light)

        # assign the shader
        pm.sets(self.shading_engine, fe=[self._plane])

        # set the uv's of the plane according to the light color
        kelvin = self.light.getShape().aiColorTemperature.get()

        min_exp = 0
        max_exp = 20

        u = (min(max_exp, self.light.aiExposure.get()) - min_exp) / (max_exp - min_exp)
        v = float(min(max(kelvin - self.kelvin_min, 0), self.kelvin_max)) / float(
            (self.kelvin_max - self.kelvin_min)
        )

        shape = self.plane.getShape()
        # close any indirect rays
        shape.aiVisibleInDiffuse.set(0)
        shape.aiVisibleInGlossy.set(0)

        pm.polyEditUV("%s.map[0:10000]" % shape.name(), u=u, v=v, r=False)

        # update the texture
        try:
            self.shader.resolution.set(1024)
        except AttributeError:
            pass


def fix_joint_hierarchy_scale(source_joint):
    """Duplicates the given joint hierarchy

    :param source_joint: A maya joint
    """
    data = {}
    joints = [source_joint]
    while joints:
        joint = joints.pop(0)
        data[joint.name()] = {
            "t": pm.xform(joint, q=1, ws=1, t=1),
            "r": pm.xform(joint, q=1, ws=1, ro=1),
        }
        # add children to list
        joints.extend(joint.getChildren(type="joint"))

    # fix parent scale
    pm.selected()[0].getParent().s.set(1, 1, 1)

    joints = pm.selected()
    while joints:
        joint = joints.pop(0)
        j_data = data[joint.name()]
        # add children to list
        joints.extend(joint.getChildren(type="joint"))
        pm.general.transformLimits(
            joint, etx=(False, False), ety=(False, False), etz=(False, False)
        )
        pm.xform(joint, ws=1, t=j_data["t"])
        # pm.xform(joint, ws=1, t=j_data['r'])


def orphan_rig_finder(project):
    """Find rig tasks that doesn't have a corresponding LookDev tasks.

    :param project: A Stalker Project instance to look in to.
    """
    from stalker import Task, Type, Version
    from stalker.db.session import DBSession

    # get all the rig tasks
    rig_type = Type.query.filter(Type.name == "Rig").first()
    look_dev_type = Type.query.filter(Type.name == "Look Development").first()

    all_rig_tasks = (
        Task.query.filter(Task.project == project).filter(Task.type == rig_type).all()
    )
    total_rig_task_count = len(all_rig_tasks)
    print("found rig count: {}".format(total_rig_task_count))
    skipped = []
    checked = []
    cacheable_attrs_that_appear_more_than_once = {}
    orphan_rigs = {}  # (rig_take_id, rig_version_take)

    for i, rig_task in enumerate(all_rig_tasks):
        print("{}/{}".format(i + 1, total_rig_task_count))
        print("Checking: {} ({})".format(rig_task.parent.name, rig_task.parent.id))

        checked.append(rig_task.parent.name)
        # get the latest published rig version
        # we need to consider all the takes differently

        unique_takes = anima.utils.get_unique_take_names(rig_task.id)

        # check LookDev first
        # if no LookDev with the same take_name
        # we found an orphan rig
        look_dev_task = (
            Task.query.filter(Task.parent_id == rig_task.parent.id)
            .filter(Task.type == look_dev_type)
            .first()
        )

        rig_task_id_as_str = str(rig_task.id)
        for take_name in unique_takes:
            # -----------------------------
            # get the latest published rig version
            latest_published_rig_version = (
                Version.query.filter(Version.task_id == rig_task.id)
                .filter(Version.take_name == take_name)
                .filter(Version.is_published == True)
                .order_by(Version.version_number.desc())
                .first()
            )

            if latest_published_rig_version is None:
                # no rig published
                # directly skip it
                continue

            # -----------------------------
            # get the look dev task
            if look_dev_task is None:
                # no look dev task
                if rig_task_id_as_str not in orphan_rigs:
                    orphan_rigs[rig_task_id_as_str] = {}

                orphan_rigs[rig_task_id_as_str][take_name] = {
                    None: "no look dev task",
                    "look_dev_task_id": None,
                    "look_dev_take_name": "Main",
                    "no_render": [],
                }

                continue

            # -----------------------------
            # get latest published look dev version with the same take name
            latest_published_look_dev_version = (
                Version.query.filter(Version.task_id == look_dev_task.id)
                .filter(Version.take_name == take_name)
                .filter(Version.is_published == True)
                .order_by(Version.version_number.desc())
                .first()
            )
            if latest_published_look_dev_version is None:
                # no look dev version
                if rig_task_id_as_str not in orphan_rigs:
                    orphan_rigs[rig_task_id_as_str] = {}

                orphan_rigs[rig_task_id_as_str][take_name] = {
                    None: "no look dev published with same take",
                    "look_dev_task_id": None,
                    "look_dev_take_name": "Main",
                    "no_render": [],
                }

                continue

    return orphan_rigs


def bake_mash_nodes():
    """Convert MASH instances to normal nodes in the current scene."""
    logger.debug("bake_mash_nodes start!")
    if not pm.pluginInfo("MASH", q=1, loaded=1):
        # no MASH no cash!
        logger.debug("no MASH plugin loaded, bake_mash_nodes returns early!")
        return

    # first convert all MASH_Repro to instancers
    from MASH import switchGeometryType
    from anima.dcc.mayaEnv import mash_bake_instancer

    logger.debug("Converting MASH_Repro to instancers if any!")
    for mash_waiter in pm.ls(type=pm.nt.MASH_Waiter):
        nodes_to_convert = []
        instancers = mash_waiter.instancerMessage.listConnections(d=True, s=False)
        for instancer in instancers:
            current_instancer_type = instancer.type()
            # MASH_Repro or instancer
            if current_instancer_type != "instancer":
                nodes_to_convert.append(instancer)
        if nodes_to_convert:
            mash_repro = mash_waiter.outputs()[0]
            repro_mesh = mash_repro.outputs()[0]
            pm.select(mash_waiter, ne=1)
            pm.select([repro_mesh], add=1)
            switchGeometryType.switch()

    logger.debug("Baking instancers!")
    # bake the instancer to normal objects
    for mash_waiter in pm.ls(type=pm.nt.MASH_Waiter):
        nodes_to_convert = []
        instancers = mash_waiter.instancerMessage.listConnections(d=True, s=False)
        for instancer in instancers:
            current_instancer_type = instancer.type()
            # MASH_Repro or instancer
            if current_instancer_type == "instancer":
                nodes_to_convert.append(instancer)

        for node in nodes_to_convert:
            parent_node = node.getParent()
            new_group_name = "{}_objects".format(node.name())

            pm.select(node)
            mash_bake_instancer.mash_bake_instancer()
            # move the newly created MASH1_Instancer_objects node to the same level
            # of the instancer node
            new_group = pm.PyNode(new_group_name)
            pm.parent(new_group, parent_node)

    # delete all MASH related nodes
    logger.debug("Deleting MASH nodes!")
    pm.delete(pm.ls(type=pm.nt.MASH_Waiter))
    logger.debug("bake_mash_nodes end!")
