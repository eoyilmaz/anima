import copy
from functools import reduce
import glob
import os
import re
import shutil
import tempfile
import time
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Tuple, Union

import maya.cmds as cmds
import maya.mel as mel
import pymel.core as pm

from stalker import (
    File,
    LocalSession,
    Project,
    Repository,
    Shot,
    Task,
    Type,
    Variant,
    Version,
)
from stalker.db.session import DBSession


from anima import ALEMBIC, USD, CACHE_FORMAT_DATA
from anima.dcc.maya import mash_bake_instancer
from anima.exc import PublishError
from anima.log import logger
from anima.publish import (
    run_publishers,
    staging,
    POST_PUBLISHER_TYPE,
)
from anima.representation import Representation
from anima.ui.utils import initialize_post_publish_dialog
from anima.utils import (
    get_unique_variant_names,
    upload_thumbnail,
)
from anima.utils.progress import ProgressManagerFactory


if TYPE_CHECKING:
    from pymel.core.nodetypes import AiStandIn


FIRST_CAP_RE = re.compile("(.)([A-Z][a-z]+)")
ALL_CAP_RE = re.compile("([a-z0-9])([A-Z])")
VERSION_NUMBER_RE = r"([\w\d/_\\\:\$]+v)([0-9]+)([\w\d._]+)"


def kill_all_torn_off_panels() -> None:
    """Delete all torn off panels."""
    panel_list = pm.getPanel(type="modelPanel")

    # remove all torn off panels
    for panel in panel_list:
        if panel.getTearOff():
            panel.delete(pnl=1)


def maximize_first_model_panel() -> None:
    """Maximize the first model panel it can find."""
    panel_list = pm.getPanel(type="modelPanel")
    if len(panel_list) == 0:
        return

    # maximize one panel in default layout
    g_main_pane = pm.melGlobals["gMainPane"]

    pane_config = pm.paneLayout(g_main_pane, q=1, configuration=1)
    if pane_config != "single":
        # call mel here
        pm.mel.eval('doSwitchPanes(1, {{ "single", "{}"}})'.format(panel_list[0]))
        pm.mel.eval("updateToolbox();")


def get_valid_dag_node(node) -> Union[None, pm.nodetypes.DagNode]:
    """Return a valid DagNode even the input is string.

    Returns:
        Union[None, pm.nodetypes.DagNode]: The DagNode if found one, None
            otherwise.
    """
    try:
        dag_node = pm.nodetypes.DagNode(node)
    except pm.MayaNodeError:
        print("Error: no node named : {}".format(node))
        return None

    return dag_node


def get_valid_node(node) -> Union[None, pm.PyNode]:
    """Return a valid PyNode even the input is string.

    Returns:
        Union[None, pm.PyNode]: The PyNode instance if found, None otherwise.
    """
    try:
        PyNode = pm.PyNode(node)
    except pm.MayaNodeError:
        print("Error: no node named : {}".format(node))
        return None

    return PyNode


def get_anim_curves(node) -> List[pm.PyNode]:
    """Return all the animation curves connected to the given node.

    Returns:
        List[pm.PyNode]: The related anim curves.
    """
    # list all connections to the node
    connected_nodes = pm.listConnections(node)

    anim_curve = "animCurve"

    return_list = []
    for cNode in connected_nodes:
        if pm.nodeType(cNode)[0 : len(anim_curve)] == anim_curve:
            return_list.append(cNode)

    return return_list


def set_anim_curve_color(anim_curve, color: List[float]) -> None:
    """Set animCurve color to the given color.

    Args:
        anim_curve (pm.nt.AnimCurve): The AnimCurve instance.
        color (List[float]): A list of floats representing RGB channels.
    """
    anim_curve = get_valid_node(anim_curve)
    anim_curve.setAttr("useCurveColor", True)
    anim_curve.setAttr("curveColor", color, type="double3")


def axial_correction_group(
    obj: Union[str, pm.PyNode],
    to_parents_origin: bool = False,
    name_prefix: str = "",
    name_postfix: str = "_ACGroup#",
) -> pm.nt.Transform:
    """Create a new parent to zero out the transformations.

    Args:
        obj (Union[str, PyNode]): A str as the object name or PyNode
            representing the object to work on.
        to_parents_origin (bool): If set to True, it doesn't zero out the
            transformations but creates a new parent at the same place of the
            original parent.

    Returns:
        pymel.core.nodeTypes.Transform: The newly created Transform node.
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


def go_home(node) -> None:
    """Set all the transformations to zero."""
    if node.attr("t").isSettable():
        node.setAttr("t", (0, 0, 0))
    if node.attr("r").isSettable():
        node.setAttr("r", (0, 0, 0))
    if node.attr("s").isSettable():
        node.setAttr("s", (1, 1, 1))


def rivet() -> pm.nt.Transform:
    """Python version of the famous rivet setup from Michael Bazhutkin.

    Returns:
        pm.nt.Transform: The locator objects.
    """
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


def create_follicle(shape, uv) -> Tuple[pm.nt.Transform, pm.nt.Follicle]:
    """Create follicle on the given shape at given uv coordinates.

    Args:
        shape (pm.nt.Mesh): The shape node.
        uv (List[float]): The UV coordinates.

    Returns:
        Tuple[pm.nt.Transform, pm.nt.Follicle]: The follicle transform and
            follicle node.
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


def auto_rivet(
    objects: Optional[List[pm.nt.Transform]] = None,
    geo: Optional[Union[pm.nt.Transform, pm.nt.Mesh]] = None,
) -> List[pm.nt.Follicle]:
    """Create hair follicles around selection.

    Args:
        objects (Optional[List[pm.nt.Transform]]): A list of objects to attach
            to the geometry. If None is given the selected object except the
            last one will be used.
        geo (Optional[Union[pm.nt.Transform, pm.nt.Mesh]]): A geometry to
            attach the objects to. If None is given, the last selected object
            will be used.

    Returns:
        List[pm.nt.Follicle]: The follicles.
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


def rivet_per_face() -> Tuple[List[pm.nt.Follicle], List[pm.nt.Transform]]:
    """Create hair follicles per selected face.

    Returns:
        Tuple[List[pm.nt.Follicle], List[pm.nt.Transform]]: The follicles and
            the locators.
    """
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


def hair_from_curves() -> None:
    """Create hairs from curves."""
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
            (f"{cpom}.ip"),
            (first_cv_tra[0], first_cv_tra[1], first_cv_tra[2]),
            type="double3",
        )

        pu = pm.getAttr(f"{cpom}.r.u")
        pv = pm.getAttr(f"{cpom}.r.v")

        hair_curve_name_prefix = mesh + "Follicle"
        naming_index = num_of_curves * int(pu * float(num_of_curves - 1) + 0.5) + int(
            pv * float(num_of_curves - 1) + 0.5
        )

        new_name = hair_curve_name_prefix + str(naming_index)

        # create follicle
        hair = pm.createNode("follicle")
        pm.setAttr(pu, f"{hair}.parameterU")
        pm.setAttr(pv, f"{hair}.parameterV")

        pm.connectAttr((f"{curve_shapes[i]}.worldSpace[0]"), (f"{hair}.sp"))

        transforms = pm.listTransforms(hair)
        hair_dag = transforms[0]

        pm.connectAttr((f"{mesh_shape}.worldMatrix[0]"), (f"{hair}.inputWorldMatrix"))

        pm.connectAttr((f"{mesh_shape}.outMesh"), (f"{hair}.inputMesh"))
        current_uv_set = pm.polyUVSet(q=True, currentUVSet=mesh_shape)
        pm.setAttr(current_uv_set[0], (f"{hair}.mapSetName"), type="string")

        pm.connectAttr((f"{hair}.outTranslate"), (f"{hair_dag}.translate"))
        pm.connectAttr((f"{hair}.outRotate"), (f"{hair_dag}.rotate"))
        pm.setAttr((f"{hair_dag}.translate"), lock=True)
        pm.setAttr((f"{hair_dag}.rotate"), lock=True)

        pm.setAttr(f"{hair}.degree", 3)
        pm.setAttr(f"{hair}.startDirection", 1)
        pm.setAttr(f"{hair}.restPose", 3)

        pm.parent(hair_system_group, relative=hair_dag)

        pm.parent(hair_dag, absolute=curves[i])

        pm.setAttr(f"{hair}.simulationMethod", 2)

        # initHairCurveDisplay(curves[i], "start")

        hair_index = i
        pm.connectAttr((f"{hair}.outHair"), (f"{hair_system}.inputHair[{hair_index}]"))
        pm.connectAttr(
            (f"{hair_system}.inputHair[{hair_index}]"), (f"{hair}.currentPosition")
        )

        crv = dup_shape[0]
        pm.connectAttr((f"{hair}.outCurve"), (f"{crv}.create"))
        # initHairCurveDisplay(crv, "current")

        transforms = pm.listTransforms(crv)
        pm.parent(transforms[0], hair_system_out_hair_group, r=True)

        pm.rename(hair_dag, new_name)

    pm.select(hair_system, r=True)
    mel.eval('displayHairCurves("current", true')
    pm.delete(cpom)


def align_to_pole_vector() -> None:
    """Align the object to the pole vector of the selected ikHandle."""
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


def export_blend_connections() -> None:
    """Export blendShape connection commands from selected objects.

    The resulting text file contains MEL scripts to reconnect objects to the
    blendShape node.

    So after exporting the connection commands you can export the blendShape
    targets as another maya file and delete them from the scene, thus your
    scene gets lite and loads much more quickly.
    """
    selection_list = pm.ls(tr=1, sl=1, l=1)
    dialog_return = pm.fileDialog2(cap="Save As", fm=0, ff="Text Files(*.txt)")
    filename = dialog_return[0]
    print(filename)
    print("\n\nFiles written:\n--------------------------------------------\n")
    commands_to_write = []
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

        cmd = "connectAttr -f {}.worldMesh[0] {};".format(
            "".join(map(str, main_shape)),
            "".join(map(str, con[0].name())),
        )
        print("{}\n".format(cmd))
        commands_to_write.append(cmd)

    with open(filename, "w") as fileId:
        fileId.write("\n".join(commands_to_write))

    print("\n------------------------------------------------------\n")
    print("filename: {}     ...done\n".format(filename))


def transfer_shaders(source, target, allow_component_assignments=False) -> None:
    """Transfer shader from source to target.

    Args:
        source (Union[pm.nt.Mesh, pm.nt.Transform]): Source geo.
        target (Union[pm.nt.Mesh, pm.nt.Transform]): Target geo.
        allow_component_assignments (bool): If True will transfer component
            level shader assignments.
    """
    if isinstance(source, pm.nt.Transform):
        source_shape = source.getShape()
    else:
        source_shape = source

    # get the shadingEngines
    shapes_and_engines = source_shape.outputs(type=pm.nt.ShadingEngine, c=1)
    if not len(shapes_and_engines):
        return

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
            if target.instanceCount() <= 1:
                continue

            for i in range(1, target.instanceCount()):
                target.attr("instObjGroups[{}]".format(i)).disconnect()
                (
                    target.attr("instObjGroups[{}]".format(i))
                    >> shading_engine.attr("dagSetMembers").next_available
                )


def benchmark(iter_cnt) -> None:
    """Benchmark playback rate.

    Args:
        iter_cnt: Count of iteration.
    """
    start = pm.playbackOptions(q=1, min=1)
    stop = pm.playbackOptions(q=1, max=1)

    start_time = time.time()

    for j in range(iter_cnt):
        for i in range(start, stop + 1):
            pm.currentTime(e=i)

    total_time = time.time() - start_time
    print("------------------------------")
    print(f"BenchmarkTime : {total_time:0.3f}")
    print(f"Total iterCnt : {iter_cnt:0.3f}")
    print("Average FPS   : {:0.3f}".format((stop - start) * iter_cnt / total_time))


def load_shelf_tab(shelf_path) -> None:
    """Load the given shelf tab.

    Args:
        shelf_path (str): The path to the shelf mel file.
    """
    # look in to the shelf mel file from user folders
    if not os.path.exists(shelf_path):
        return

    try:
        pm.mel.eval(f'loadNewShelf "{shelf_path}"')
    except Exception:
        # probably not in GUI mode
        return


def delete_shelf_tab(shelf_name: str, confirm: bool = True) -> None:
    """The python version of the original mel script of Maya.

    Args:
        shelf_name (str): The name of the shelf to delete.
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
            message=f"Delete {shelf_name}?",
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
        if pm.optionVar[f"shelfName{i}"] == shelf_name:
            shelf_number = i
            break

    if shelf_number == -1:
        # there should be no shelf with this name
        return

    # offset shelves
    for i in range(shelf_number, number_of_shelves):
        pm.optionVar[f"shelfLoad{i}"] = pm.optionVar[f"shelfLoad{(i + 1)}"]
        pm.optionVar[f"shelfName{i}"] = pm.optionVar[f"shelfName{(i + 1)}"]
        pm.optionVar[f"shelfFile{i}"] = pm.optionVar[f"shelfFile{(i + 1)}"]

    pm.optionVar.pop(f"shelfLoad{number_of_shelves}")
    number_of_shelves -= 1
    pm.optionVar["numShelves"] = number_of_shelves

    pm.windows.deleteUI(f"{shelf_top_level_path}|{shelf_name}", layout=1)

    # remove the shelf mel file from user folders
    for path in pm.internalVar(userShelfDir=1).split(os.path.pathsep):
        shelf_file_name = f"shelf_{shelf_name}.mel"
        shelf_file_full_path = os.path.join(path, shelf_file_name)

        deleted_file_name = f"{shelf_file_name}.deleted"
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


def cube_from_bbox(bbox: pm.dt.BoundingBox) -> None:
    """Create a polyCube from the given bounding box.

    Args:
        bbox (pm.dt.BoundingBox): pm.dt.BoundingBox instance.
    """
    cube = pm.polyCube(
        width=bbox.width(), height=bbox.height(), depth=bbox.depth(), ch=False
    )
    cube[0].setAttr("t", bbox.center())
    return cube[0]


def create_bbox(
    nodes: List[pm.nt.Transform], per_selection: bool = False
) -> Union[pm.dt.BoundingBox, List[pm.dt.BoundingBox]]:
    """Create bounding boxes for the selected objects.

    Args:
        per_selection (bool): If True will create a BBox for each given object.

    Returns:
        Union[pm.dt.BoundingBox, List[pm.dt.BoundingBox]]: The BBox or list of
            BBoxes.
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


def replace_with_bbox(nodes: List[pm.nt.Transform]) -> List[pm.nt.Transform]:
    """Replace the given nodes with a bbox object.

    Args:
        nodes (List[pm.nt.Transform]): A list of nodes to replace with bbox.

    Returns:
        List[pm.nt.Transform]: The list of bbox objects.
    """
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


def get_root_nodes(
    reference_node: Optional[pm.nt.Reference] = None,
) -> List[pm.nt.Transform]:
    """Return the root DAG nodes.

    Args:
        reference_node (Optional[pm.nt.Reference]): If given, the root node of
            that reference and all the subReference nodes will be returned.

    Returns:
        List[pm.nt.Transform]: The root transform nodes.
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


def create_arnold_stand_in(path: Optional[str] = None) -> "AiStandIn":
    """Create Arnold Stand-In node.

    This is a fixed version of original arnold script of SolidAngle Arnold core
    API.

    Args:
        path (Optional[str]): The path to the stand-in file. If None is given
            the an empty AiStandIn node will be created.

    Returns:
        pm.nt.AiStandIn: The created stand-in node.
    """
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


def create_rs_proxy_node(
    path: Optional[str] = None,
) -> Tuple[pm.nt.RedshiftProxyMesh, pm.nt.Mesh]:
    """Create Redshift Proxies showing a proxy object.

    Args:
        path (Optional[str]): The path to the proxy file.

    Returns:
        Tuple[pm.nt.RedshiftProxyMesh, pm.nt.Mesh]: The created proxy node and
            the shape node.
    """
    proxy_mesh_node = pm.createNode("RedshiftProxyMesh")
    proxy_mesh_node.fileName.set(path)
    proxy_mesh_shape = pm.createNode("mesh")
    proxy_mesh_node.outMesh >> proxy_mesh_shape.inMesh

    # assign default material
    pm.sets("initialShadingGroup", fe=proxy_mesh_shape)

    return proxy_mesh_node, proxy_mesh_shape


def run_pre_publishers() -> None:
    """Run pre publishers if the current scene is a published version.

    This is written to prevent users to save on top of a Published version and
    create a back door to skip un-publishable scene from being published.
    """
    from anima.dcc.maya.common import Maya

    m_env = Maya()

    file = m_env.get_current_file()
    version = m_env.get_current_version()

    # check if we have a proper version
    if not file or not version:
        return

    # check if it is a Representation
    if file.is_representation():
        return

    if version.is_published:
        # before doing anything run all publishers
        type_name = ""
        task = version.task
        variant = None
        if isinstance(task, Variant):
            variant = task
            task = variant.parent

        if task.type:
            type_name = task.type.name

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
                message="<b>{}</b><br/><br/>{}".format("SCENE NOT SAVED!!!", e),
                button=["Ok"],
            )
            raise e
        # do not forget to clean up the staging area
        staging.clear()
    else:
        # run some of the publishers
        try:
            from anima.dcc.maya import publish as publish_scripts

            publish_scripts.check_node_names_with_bad_characters()
        except (PublishError, RuntimeError) as e:
            # pop up a message box with the error
            pm.confirmDialog(
                title="SaveError",
                icon="critical",
                message="<b>{}</b><br/><br/>{}".format("SCENE NOT SAVED!!!", e),
                button=["Ok"],
            )
            raise e

        # update updated_by field of the current version
        ls = LocalSession()
        logged_in_user = ls.logged_in_user
        if logged_in_user:
            version.updated_by = logged_in_user
            DBSession.commit()


def run_post_publishers() -> None:
    """Run post publishers if the current scene is a published version.

    This is written to prevent users to save on top of a Published version and
    create a back door to skip un-publishable scene from being published.
    """
    from anima.dcc.maya.common import Maya

    m_env = Maya()

    version = m_env.get_current_version()

    # check if we have a proper version
    if not version:
        return

    # check if it is a Representation
    if Representation.repr_separator in version.variant_name:
        return

    if version.is_published:
        # before doing anything run all publishers
        type_name = ""
        if version.task.type:
            type_name = version.task.type.name

        # before running use the staging area to store the current version
        staging["version"] = version

        # show dialog during post publish progress and lock maya
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
                message="<b>{}</b><br/><br/>{}".format("POST PUBLISH FAILED!!!", e),
                button=["Ok"],
            )
            raise e

        # close dialog in any case
        d.close()
        # do not forget to clean up the staging area
        staging.clear()


def get_default_render_layer() -> pm.nt.RenderLayer:
    """Return the default render layer.

    Returns:
        pm.nt.RenderLayer: The default render layer.
    """
    return pm.ls(type="renderLayer")[0].defaultRenderLayer()


def switch_to_default_render_layer() -> None:
    """Set the current layer to defaultRenderLayer."""
    try:
        default_render_layer = get_default_render_layer()
        current_layer = get_current_render_layer()
        if current_layer != default_render_layer:
            default_render_layer.setCurrent()
    except (NameError, RuntimeError):
        pass


def get_current_render_layer() -> pm.nt.RenderLayer:
    """Return the current render layer.

    Returns:
        pm.nt.RenderLayer: The current render layer.
    """
    default_render_layer = get_default_render_layer()
    return default_render_layer.currentLayer()


def fix_external_paths() -> None:
    """Fixe external paths in a maya scene."""
    from anima.dcc.maya.common import Maya

    m_env = Maya()
    if m_env.get_current_version():
        m_env.replace_external_paths()


def has_shape(node: pm.nt.Transform) -> bool:
    """Check if the given node has at least one child that has a shape.

    Args:
        node (pm.nt.Transform): The node to check.

    Returns:
        bool: True if the node has at least one child with a shape.
    """
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


def generate_thumbnail() -> Union[None, List[str]]:
    """Generate thumbnail for current scene.

    Returns:
        Union[None, List[str]]: The list of generated thumbnails.
    """
    from anima.dcc.maya.common import Maya

    maya_dcc = Maya()
    v = maya_dcc.get_current_version()

    if not v:
        return

    # do not generate a thumbnail from a Repr
    if "@" in v.variant_name:
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
        upload_thumbnail(task, output_file)

    return found_output_file


def set_range_from_shot(shot: pm.nt.Shot) -> None:
    """Set the playback range from a shot node in the scene.

    Args:
        shot (pm.nt.Shot): Maya Shot node.
    """
    min_frame = shot.getAttr("startFrame")
    max_frame = shot.getAttr("endFrame")

    pm.playbackOptions(
        ast=min_frame,
        aet=max_frame,
        min=min_frame,
        max=max_frame,
    )


def get_cacheable_nodes(
    reference_node: Optional[pm.system.FileReference] = None,
) -> List[pm.nt.Transform]:
    """Return the cacheable nodes from the current scene or in the given reference node.

    Args:
        reference_node (Optional[pm.system.FileReference]): An optional Maya
            FIleReference node. When supplied only the recursive content of
            this reference will be searched for a cacheable node.

    Returns:
        List[pm.nt.Transform]: A list of cacheable nodes.
    """
    pdm = ProgressManagerFactory.get_progress_manager()
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


def get_reference_copy_number(node: Union[pm.PyNode, pm.system.FileReference]) -> int:
    """Return the reference number of the given reference file.

    Args:
        node (Union[pm.PyNode, pm.system.FileReference]): This can
            be a regular Maya node or a ReferenceFile.

    Returns:
        int: The reference number.
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
    cacheable_nodes: List[pm.nt.Transform],
    start_frame: Optional[int] = None,
    end_frame: Optional[int] = None,
    handles: int = 0,
    step: int = 1,
    isolate: bool = True,
    unload_refs: bool = True,
    cache_format: str = ALEMBIC,
) -> List[str]:
    """Export Alembic/USD caches of the given nodes.

    Args:
        cacheable_nodes (List[pm.nt.Transform]): The top transform nodes to
            export the caches from.
        start_frame (Optional[int]): Start frame. If same as end frame and
            handle is 0, exports static file.
        end_frame (Optional[int]): End frame. If same as start frame and
            handle is 0, exports static file.
        handles (int): Handles from start and end. If same as start and end
            frame and handle is 0, exports static file.
        step (int): Frame step.
        isolate (bool): Isolate exported object for faster playback. Default is
            True.
        unload_refs (bool): Unload references to speed playback. Default is
            True.
        cache_format (str): Cache format, "alembic" or "usd". Default is
            "alembic".

    Returns:
        List[str]: List of exported file paths.
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

    pdm = ProgressManagerFactory.get_progress_manager()
    cacheable_nodes.sort(key=lambda x: x.getAttr("cacheable"))
    caller = pdm.register(len(cacheable_nodes), "Exporting Alembic Caches")

    # set default start_frame and end_frame values
    if start_frame is None:
        start_frame = int(pm.playbackOptions(q=1, ast=1))
    if end_frame is None:
        end_frame = int(pm.playbackOptions(q=1, aet=1))

    export_animation: bool = (end_frame - start_frame + 2 * handles) > 0

    current_file_full_path = str(pm.sceneName())
    current_file_path = os.path.dirname(current_file_full_path)
    current_file_name = os.path.basename(current_file_full_path)

    # export caches
    # deselect everything first
    pm.select(None)

    exclude_node_names = ["_rig_", "_proxy_"]
    exclude_node_names_starts_with = ["rig_"]
    exclude_node_names_ends_with = ["_rig"]

    default_playback_option = pm.playbackOptions(q=1, v=True)

    # leave off only one panel in the viewport and maximize it
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
                            if related_ref is None:
                                continue
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

    cache_file_full_paths = []
    for cacheable_node_name in sorted(cacheable_node_references):
        logger.info("INFO: exporting: {}".format(cacheable_node_name))

        if unload_refs:
            # load the reference first
            if ref := cacheable_node_references[cacheable_node_name]["ref"]:
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
                any([n in underscored_name for n in exclude_node_names])
                or any(
                    [
                        underscored_name.startswith(n)
                        for n in exclude_node_names_starts_with
                    ]
                )
                or any(
                    [underscored_name.endswith(n) for n in exclude_node_names_ends_with]
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

        cache_file_full_path = os.path.join(output_path, output_filename).replace(
            "\\", "/"
        )
        os.makedirs(os.path.dirname(cache_file_full_path), exist_ok=True)

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
        elif cache_format == USD:
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
        shutil.move(temp_cache_file_path, cache_file_full_path)
        cache_file_full_paths.append(cache_file_full_path)

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
    add_files_to_current_version(cache_file_full_paths, cache_format)

    return cache_file_full_paths


def add_files_to_current_version(
    file_full_paths: List[str], file_type_name: str
) -> List[File]:
    """Add the given file as a `File` to the current `Version.files`.

    Args:
        file_full_paths (List[str]): A list of file paths.
        file_type_name (str): The file type, e.g Alembic, USD, Image,
            Video, Audio etc.

    Returns:
        List[File]: List of File instances that are newly created.
    """
    from anima.dcc.maya.common import Maya

    maya_dcc = Maya()
    current_version: Version = maya_dcc.get_current_version()

    if current_version is None:
        return

    # get related Type instance
    with DBSession.no_autoflush:
        file_type = Type.query.filter(Type.name == file_type_name).first()

    if not file_type:
        file_type = Type(
            name=file_type_name,
            code=file_type_name,
            target_entity_type="File",
        )

    local_session = LocalSession()
    with DBSession.no_autoflush:
        logged_in_user = local_session.logged_in_user

    # Create a File with the file path and add it to the current Version.files
    for output_file_path in file_full_paths:
        new_file = File(
            full_path=Repository.to_os_independent_path(output_file_path),
            original_filename=os.path.basename(output_file_path),
            type=file_type,
            created_by=logged_in_user,
        )
        DBSession.add(new_file)
        current_version.files.append(new_file)
    DBSession.commit()


def export_cache_of_selected_cacheable_nodes(
    start_frame: Optional[int] = None,
    end_frame: Optional[int] = None,
    handles: int = 0,
    step: int = 1,
    isolate: bool = True,
    unload_refs: bool = True,
    cache_format: str = ALEMBIC,
) -> List[str]:
    """Export Alembic/USD caches of the selected cacheable nodes.

    Args:
        start_frame (Optional[int]): Start frame. If same as end frame and
            handle is 0, exports static file.
        end_frame (Optional[int]): End frame. If same as start frame and
            handle is 0, exports static file.
        handles (int): Handles from start and end. If same as start and end
            frame and handle is 0, exports static file.
        step (int): Frame step.
        isolate (bool): Isolate exported object for faster playback. Default is
            True.
        unload_refs (bool): Unload references to speed playback. Default is
            True.
        cache_format (str): Cache format, "alembic" or "usd". Default is
            "alembic".

    Returns:
        List[str]: List of exported file paths.
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
    start_frame: Optional[int] = None,
    end_frame: Optional[int] = None,
    handles: int = 0,
    step: int = 1,
    isolate: bool = True,
    unload_refs: bool = True,
    cache_format: str = ALEMBIC,
) -> List[str]:
    """Export Alembic/USD caches for transform nodes with "cacheable" attribute.

    Args:
        start_frame (Optional[int]): Start frame. If same as end frame and
            handle is 0, exports static file.
        end_frame (Optional[int]): End frame. If same as start frame and
            handle is 0, exports static file.
        handles (int): Handles from start and end. If same as start and end
            frame and handle is 0, exports static file.
        step (int): Frame step.
        isolate (bool): Isolate exported object for faster playback. Default is
            True.
        unload_refs (bool): Unload references to speed playback. Default is
            True.
        cache_format (str): Cache format, "alembic" or "usd". Default is
            "alembic".

    Returns:
        List[str]: List of exported file paths.
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


def extract_version_number_from_path(path: str) -> int:
    """Extract version number ("_v{:03d}") as an integer from the given path.

    Args:
        path (str): The path to extract the version number from.

    Returns:
        int: The extracted version number.
    """
    version_matcher = re.compile(VERSION_NUMBER_RE)
    m = re.match(version_matcher, path)
    if m:
        return int(m.group(2))


def auto_reference_caches(cache_type: str = ALEMBIC) -> None:
    """Reference caches from Animation scene of the same shot.

    cache_type (str): Desired cache type, one of `ALEMBIC` or `USD`, default
        value is ALEMBIC and USD is meaningless for now.
    """
    # update all references first
    from anima.dcc.maya.common import Maya

    update_cache_references(cache_type=cache_type)

    maya_dcc = Maya()
    version = maya_dcc.get_current_version()
    if not isinstance(version, Version):
        raise RuntimeError("Active scene is not related to a Version.")

    # get the task
    task = version.task
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
        glob_pattern = "{}/*{}*".format(dir_abs_path, asset_instance_name).replace(
            "\\", "/"
        )

        all_cache_files = sorted(
            glob.glob(glob_pattern), key=extract_version_number_from_path
        )
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


def update_cache_references(cache_type: str = ALEMBIC) -> None:
    """Update referenced cache files in the current scene.

    Args:
        cache_type (str): Desired cache type, one of `ALEMBIC` or `USD`,
            default value is ALEMBIC and USD is meaningless for now.
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
    version_matcher = re.compile(VERSION_NUMBER_RE)

    updated_path_info = []
    for ref in pm.listReferences():
        is_loaded = ref.isLoaded()
        if not (path := str(ref.path)).endswith(
            CACHE_FORMAT_DATA[cache_type]["file_extension"]
        ):
            continue

        if not (m := re.match(version_matcher, path)):
            continue

        prefix = m.group(1)

        # glob the files
        glob_pattern = f"{prefix}*"
        # The versions will always be sorted properly
        # we don't need to check if the last path in the is the latest one
        all_abc_files = sorted(glob.glob(glob_pattern))
        # there may be different variants,
        # but, we don't need check for that too, because we are globbing for a path
        # that includes the ``variant_name``

        if (last_abc_file := all_abc_files[-1]) != os.path.expandvars(path):
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
        print(f"{old_ref_path} -> {new_ref_path}")


# noinspection PyStatementEffect
class BarnDoorSimulator(object):
    """A aiBarnDoor simulator."""

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

    def create_barn_door(self) -> None:
        """Create the barn door node."""
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

    def store_data(self, data: str) -> None:
        """Store the given data.

        Args:
            data (str): The data to store.
        """
        if not self.light.hasAttr(self.custom_data_storage_attr_name):
            pm.addAttr(self.light, ln=self.custom_data_storage_attr_name, dt="string")

        self.light.setAttr(self.custom_data_storage_attr_name, data)

    def store_nodes(self, nodes: List[pm.nt.Transform]) -> None:
        """Store the given nodes.

        Args:
            nodes (List[pm.nt.Transform])
        """
        for node in nodes:
            self.store_node(node)

    def store_node(self, node: pm.nt.Transform) -> None:
        """Store the node in the storage attribute.

        Args:
            node (pm.nt.Transform): The node to store.
        """
        if not self.light.hasAttr(self.message_storage_attr_name):
            pm.addAttr(self.light, ln=self.message_storage_attr_name, m=1)

        node.message >> self.light.attr(self.message_storage_attr_name).next_available

    def create_frame_curve(self) -> None:
        """Create the frame curve."""
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

    def create_preview_curve(self, side: str) -> None:
        """Create preview curves.

        Args:
            side (str): The side name.
        """
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
        """Create the expression."""
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

    def create_script_job(self) -> None:
        """Create the script job that disables the affected highlight."""
        script_job_no = pm.scriptJob(
            e=[
                "SelectionChanged",
                f'if pm.ls(sl=1) and pm.ls(sl=1)[0].name() == "{self.light.name()}":\n'
                "    pm.displayPref(displayAffected=False)\n"
                "else:\n"
                "    pm.displayPref(displayAffected=True)",
            ]
        )
        self.store_data(f"{script_job_no}")

    def setup(self) -> None:
        """Setup the magic."""
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
            all_preview_curves, n=f"{self.light.name()}_barndoor_preview_curves"
        )

        self.store_node(shapes_group)

        # create script job
        self.create_script_job()

        # select the light again
        pm.select(self.light)

    def delete(self) -> None:
        """Delete the barn door setup."""
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
                    if light_parent.hasAttr(self.message_storage_attr_name) and (
                        node
                        in light_parent.attr(self.message_storage_attr_name).inputs()
                    ):
                        self.light = light_parent
                        found_light = True
                        self.delete()

                # if the code comes here than this node is not listed in any
                # lights, so delete it if it contains the string
                # "barndoor_preview_curves" in its name
                if not found_light and "barndoor_preview_curves" in node.name():
                    pm.delete(node)


def create_shader(shader_tree: Dict, name: Optional[str] = None) -> pm.PyNode:
    """Create a shader tree from the given shader tree definition.

    Args:
        shader_tree (Dict): The shader tree definition. The shader_tree is a
            Python dictionary showing node types and attribute values.

            Each shader_tree can create only one shading network. The format of
            the dictionary should be as follows::

            shader_tree: {
                'type': <- The maya node type of the highest shader node
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

        name (Optional[str]): The name of the shader to create.

    Returns:
        pm.PyNode: The created shader node.
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


def match_hierarchy(
    source: pm.PyNode,
    target: pm.PyNode,
    node_types: Optional[Tuple] = None,
    use_long_names: bool = False,
) -> Dict:
    """Match the objects in two different hierarchy by looking at their names.

    Args:
        source (pm.PyNode): The source node. It can be a parent node. So the match
            includes the descendants.
        target (pm.PyNode): The target node.
        node_types (Optional[Tuple]): A tuple showing the node types to match.
            The default value is (pm.nt.Mesh, pm.nt.NurbsSurface).
        use_long_names (bool): Precisely match the placement in the hierarchy.

    Returns:
        Dict: A dictionary where you can look up for matches by using the
            object name.
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
            try:
                index = source_node_names.index(tmp_target_node_name)
            except ValueError:
                # try removing the "Deformed" part
                if target_node_name.endswith("Deformed"):
                    tmp_target_node_name = target_node_name.replace("Deformed", "", 1)
                index = source_node_names.index(tmp_target_node_name)
        except ValueError:
            lut["no_match"].append(target_node)
        else:
            lut["match"].append((source_nodes[index], target_nodes[i]))

    return lut


def camel_case_to_underscore(name: str) -> str:
    """Convert the given CamelCase formatted string to underscore formatted one.

    Args:
        name (str): The CamelCase formatted string.

    Returns:
        str: The underscore formatted string.
    """
    name = FIRST_CAP_RE.sub(r"\1_\2", name)
    return ALL_CAP_RE.sub(r"\1_\2", name).lower()


class Cell(object):
    """An implementation for a grid cell.

    Holds points in space. It is easy to find a corresponding point with using
    a cell.
    """

    def __init__(self):
        self.index = [0, 0, 0]
        self.singular_index = None
        self.points = []
        self.bbox = None


class Grid(object):
    """A simple grid implementation for component search."""

    def __init__(self):
        self.divisions = [1, 1, 1]
        self.bbox = None
        self.tree = []

    def add_point(self, point: List[float]) -> None:
        """Add the given point to a cell.

        Args:
            point (List[float]): The point to add.
        """
        raise NotImplementedError()

    def to_index(self, pos: List[float]) -> List[int]:
        """Convert the given position in space to a cell index.

        Args:
            pos (List[float]): A point position in space.

        Returns:
            List[int]: The cell index.
        """
        raise NotImplementedError()

    def to_cell(self, pos: List[float]) -> Cell:
        """Return a cell in the given position in space or none if no cell contains that point.

        Args:
            pos (List[float]): A point position in space.

        Return:
            Cell: The cell that contains the given point.
        """
        raise NotImplementedError()


class DummyWindowLight(object):
    """Generate dummy plane for given lights."""

    shader_name = "dummy_window_light_shader"
    shading_engine_name = "dummy_window_light_shaderSG"

    kelvin_min = 1000
    kelvin_max = 30000

    def __init__(self, light=None):
        self.light = light
        self._shader = None
        self._shading_engine = None
        self._plane = None

    def update(self) -> None:
        """Update the node."""
        plane = self.plane
        self._update_plane_color()
        self._set_light_attributes()

    def _set_light_attributes(self) -> None:
        """Set the default light attributes."""
        light_shape = self.light.getShape()
        light_shape.aiIndirect.set(0)
        light_shape.aiSamples.set(1)

    @property
    def shader(self) -> pm.PyNode:
        """Return the shader.

        Returns:
            pm.PyNode: The shader node.
        """
        if self._shader:
            return self._shader

        shader = pm.ls(self.shader_name)
        if not shader:
            self._create_shader()
            return self._shader

        self._shader = shader[0]
        shading_engine = self._shader.outColor.outputs(type=pm.nt.ShadingEngine)
        if shading_engine:
            self._shading_engine = shading_engine[0]
        else:
            self._create_shading_engine()

        return shader[0]

    @property
    def shading_engine(self) -> pm.nt.ShadingEngine:
        """Return the shading engine."""
        if self._shading_engine:
            return self._shading_engine
        else:
            self._shading_engine = self._create_shading_engine()
            return self._shading_engine

    @property
    def plane(self) -> pm.nt.Transform:
        """Return the plane.

        Returns:
            pm.nt.Transform: The transform node of the plane.
        """
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

            return self._create_plane()

        # create the plane
        return self._create_plane()

    def _create_shading_engine(self) -> pm.nt.ShadingEngine:
        """Create the shading engine."""
        if self.shader:
            # get the shading engine from shader
            if shading_engines := self.shader.outputs(type=pm.nt.ShadingEngine):
                self._shading_engine = shading_engines[0]

        if not self._shading_engine:
            self._shading_engine = pm.sets(
                renderable=True,
                noSurfaceShader=True,
                empty=True,
                name=self.shading_engine_name,
            )

        return self._shading_engine

    def _create_shader(self) -> None:
        """Create the shader."""
        self._shader = pm.shadingNode("surfaceShader", asShader=1)
        self._shader.rename(self.shader_name)

        self._shader.outColor >> self.shading_engine.surfaceShader

        # create the ramp
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

    def _validate_light(self, light: pm.nt.Light) -> pm.nt.Light:
        """Validate the light.

        Args:
            light (pm.nt.Light): The light to validate.

        Returns:
            pm.nt.Light: The validated light node.
        """
        if light is None:
            raise RuntimeError("No Light specified")

        return light

    def _create_plane(self) -> None:
        """Create the plane for the light."""
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

    def _update_plane_color(self) -> None:
        """Update the plane uv according to the light color."""
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

        pm.polyEditUV(f"{shape.name()}.map[0:10000]", u=u, v=v, r=False)

        # update the texture
        try:
            self.shader.resolution.set(1024)
        except AttributeError:
            pass


def fix_joint_hierarchy_scale(source_joint: pm.nt.Joint) -> None:
    """Duplicate the given joint hierarchy and fix the scale of the duplicated one.

    Args:
        source_joint (pm.nt.Joint): A maya joint.
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


def orphan_rig_finder(project: Project) -> Dict:
    """Find rig tasks that doesn't have a corresponding LookDev tasks.

    Args:
        project (stalker.Project): A Stalker Project instance to look in to.
    """
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
    orphan_rigs = {}  # (rig_variant_id, rig_version_variant)

    for i, rig_task in enumerate(all_rig_tasks):
        print("{}/{}".format(i + 1, total_rig_task_count))
        print("Checking: {} ({})".format(rig_task.parent.name, rig_task.parent.id))

        checked.append(rig_task.parent.name)
        # get the latest published rig version
        # we need to consider all the variants differently

        unique_variants = get_unique_variant_names(rig_task.id)

        # check LookDev first
        # if no LookDev with the same variant_name
        # we found an orphan rig
        look_dev_task = (
            Task.query.filter(Task.parent_id == rig_task.parent.id)
            .filter(Task.type == look_dev_type)
            .first()
        )

        rig_task_id_as_str = str(rig_task.id)
        for variant_name in unique_variants:
            # -----------------------------
            # get the latest published rig version
            latest_published_rig_version = (
                Version.query.filter(Version.task_id == rig_task.id)
                .filter(Version.variant_name == variant_name)
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

                orphan_rigs[rig_task_id_as_str][variant_name] = {
                    None: "no look dev task",
                    "look_dev_task_id": None,
                    "look_dev_variant_name": "Main",
                    "no_render": [],
                }

                continue

            # -----------------------------
            # get latest published look dev version with the same variant name
            latest_published_look_dev_version = (
                Version.query.filter(Version.task_id == look_dev_task.id)
                .filter(Version.variant_name == variant_name)
                .filter(Version.is_published == True)
                .order_by(Version.version_number.desc())
                .first()
            )
            if latest_published_look_dev_version is None:
                # no look dev version
                if rig_task_id_as_str not in orphan_rigs:
                    orphan_rigs[rig_task_id_as_str] = {}

                orphan_rigs[rig_task_id_as_str][variant_name] = {
                    None: "no look dev published with same variant name",
                    "look_dev_task_id": None,
                    "look_dev_variant_name": "Main",
                    "no_render": [],
                }

                continue

    return orphan_rigs


def bake_mash_nodes() -> None:
    """Convert MASH instances to normal nodes in the current scene."""
    logger.debug("bake_mash_nodes start!")
    if not pm.pluginInfo("MASH", q=1, loaded=1):
        # no MASH no cash!
        logger.debug("no MASH plugin loaded, bake_mash_nodes returns early!")
        return

    # first convert all MASH_Repro to instancers
    from MASH import switchGeometryType

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
