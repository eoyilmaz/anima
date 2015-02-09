# -*- coding: utf-8 -*-
# Copyright (c) 2012-2014, Anima Istanbul
#
# This module is part of anima-tools and is released under the BSD 2
# License: http://www.opensource.org/licenses/BSD-2-Clause
import os
from pprint import pprint
import tempfile
import shutil

import pymel.core as pm
import maya.mel as mel


__version__ = "v10.1.13"


def get_valid_dag_node(node):
    """returns a valid dag node even the input is string
    """
    try:
        dag_node = pm.nodetypes.DagNode(node)
    except pm.MayaNodeError:
        print('Error: no node named : %s' % node)
        return None

    return dag_node


def get_valid_node(node):
    """returns a valid PyNode even the input is string
    """
    try:
        PyNode = pm.PyNode(node)
    except pm.MayaNodeError:
        print('Error: no node named : %s' % node)
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
        if pm.nodeType(cNode)[0:len(anim_curve)] == anim_curve:
            return_list.append(cNode)

    return return_list


def set_anim_curve_color(anim_curve, color):
    """sets animCurve color to color
    """
    anim_curve = get_valid_node(anim_curve)
    anim_curve.setAttr("useCurveColor", True)
    anim_curve.setAttr("curveColor", color, type="double3")


def axial_correction_group(obj,
                           to_parents_origin=False,
                           name_prefix="",
                           name_postfix="_ACGroup#"):
    """creates a new parent to zero out the transformations

    if to_parents_origin is set to True, it doesn't zero outs the
    transformations but creates a new parent at the same place of the original
    parent

    :returns: pymel.core.nodeTypes.Transform
    """
    obj = get_valid_dag_node(obj)

    if name_postfix == "":
        name_postfix = "_ACGroup#"

    ac_group = pm.group(
        em=True,
        n=(name_prefix + obj.name() + name_postfix)
    )

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
        obj.setAttr('r', (0, 0, 0))
        obj.setAttr('jo', (0, 0, 0))

    return ac_group


def go_home(node):
    """sets all the transformations to zero
    """
    if node.attr('t').isSettable():
        node.setAttr('t', (0, 0, 0))
    if node.attr('r').isSettable():
        node.setAttr('r', (0, 0, 0))
    if node.attr('s').isSettable():
        node.setAttr('s', (1, 1, 1))


def rivet():
    """the python version of the famous rivet setup from Bazhutkin
    """
    selection_list = pm.filterExpand(sm=32)

    if selection_list is not None and len(selection_list) > 0:
        size = len(selection_list)
        if size != 2:
            raise pm.MayaObjectError('No two edges selected')

        edge1 = pm.PyNode(selection_list[0])
        edge2 = pm.PyNode(selection_list[1])

        edge1Index = edge1.indices()[0]
        edge2Index = edge2.indices()[0]

        shape = edge1.node()

        cFME1 = pm.createNode('curveFromMeshEdge', n='rivetCurveFromMeshEdge#')
        cFME1.setAttr('ihi', 1)
        cFME1.setAttr('ei[0]', edge1Index)

        cFME2 = pm.createNode('curveFromMeshEdge', n='rivetCurveFromMeshEdge#')
        cFME2.setAttr('ihi', 1)
        cFME2.setAttr('ei[0]', edge2Index)

        loft = pm.createNode('loft', n='rivetLoft#')
        loft.setAttr('ic', s=2)
        loft.setAttr('u', 1)
        loft.setAttr('rsn', 1)

        pOSI = pm.createNode('pointOnSurfaceInfo',
                             n='rivetPointOnSurfaceInfo#')
        pOSI.setAttr('turnOnPercentage', 1)
        pOSI.setAttr('parameterU', 0.5)
        pOSI.setAttr('parameterV', 0.5)

        loft.attr('os') >> pOSI.attr('is')
        cFME1.attr('oc') >> loft.attr('ic[0]')
        cFME2.attr('oc') >> loft.attr('ic[1]')
        shape.attr('w') >> cFME1.attr('im')
        shape.attr('w') >> cFME2.attr('im')
    else:
        selection_list = pm.filterExpand(sm=41)

        if selection_list is not None and len(selection_list) > 0:
            size = len(selection_list)
            if size != 1:
                raise pm.MayaObjectError('No one point selected')

            point = pm.PyNode(selection_list[0])
            shape = point.node()
            u = float(point.name().split('][')[0].split('[')[1])
            v = float(point.name().split('][')[1].split(']')[0])

            pOSI = pm.createNode('pointOnSurfaceInfo',
                                 n='rivetPointOnSurfaceInfo#')
            pOSI.setAttr('turnOnPercentage', 0)
            pOSI.setAttr('parameterU', u)
            pOSI.setAttr('parameterV', v)
            shape.attr('ws') >> pOSI.attr('is')
        else:
            raise pm.MayaObjectError('No edges or point selected')

    locator = pm.spaceLocator(n='rivet#')
    aimCons = pm.createNode('aimConstraint',
                            p=locator,
                            n=locator.name() + '_rivetAimConstraint#')
    aimCons.setAttr('tg[0].tw', 1)
    aimCons.setAttr('a', (0, 1, 0))
    aimCons.setAttr('u', (0, 0, 1))
    aimCons.setAttr('v', k=0)
    aimCons.setAttr('tx', k=0)
    aimCons.setAttr('ty', k=0)
    aimCons.setAttr('tz', k=0)
    aimCons.setAttr('rx', k=0)
    aimCons.setAttr('ry', k=0)
    aimCons.setAttr('rz', k=0)
    aimCons.setAttr('sx', k=0)
    aimCons.setAttr('sy', k=0)
    aimCons.setAttr('sz', k=0)

    pOSI.attr('position') >> locator.attr('translate')
    pOSI.attr('n') >> aimCons.attr('tg[0].tt')
    pOSI.attr('tv') >> aimCons.attr('wu')
    aimCons.attr('crx') >> locator.attr('rx')
    aimCons.attr('cry') >> locator.attr('ry')
    aimCons.attr('crz') >> locator.attr('rz')

    pm.select(locator)
    return locator


def auto_rivet():
    """creates hair follicles around selection
    """
    sel_list = pm.ls(sl=1)

    # the last selection is the mesh
    objects = sel_list[:-1]
    geo = sel_list[-1]

    # get the closest point to the surface
    geo_shape = geo.getShape()

    follicles = []

    for obj in objects:
        # pivot point of the obj
        pivot = obj.getRotatePivot(space='world')
        uv = geo_shape.getUVAtPoint(pivot, space='world')

        # create a hair follicle
        follicle = pm.nt.Follicle()
        follicles.append(follicle)
        follicle.simulationMethod.set(0)
        geo_shape.worldMatrix >> follicle.inputWorldMatrix
        geo_shape.outMesh >> follicle.inputMesh
        follicle.parameterU.set(uv[0])
        follicle.parameterV.set(uv[1])

        # parent the object to the follicles transform node
        follicle_transform = follicle.getParent()

        follicle.outTranslate >> follicle_transform.translate
        follicle.outRotate >> follicle_transform.rotate

        pm.parent(obj, follicle_transform)

    return follicles


def hair_from_curves():
    """creates hairs from curves
    """
    selection_list = pm.ls(sl=1)

    curves = []
    curve_shapes = []

    mesh = ""
    mesh_shape = ""

    for i in range(0, len(selection_list)):
        shapes = pm.listRelatives(selection_list[i], s=True)
        node_type = pm.nodeType(shapes[0])

        if node_type == 'nurbsCurve':
            curves.append(selection_list[i])
            curve_shapes.append(shapes[0])
        elif node_type == 'mesh':
            mesh = selection_list[i]
            mesh_shape = shapes[0]

    do_output_curve = 1
    hide_output_curve = 0

    #create hair
    hair_system = pm.createNode('hairSystem')
    pm.connectAttr('time1.outTime', (hair_system + '.currentTime'))

    hair_system_group = ""
    hair_system_out_hair_group = ""
    hair_system_parent = pm.listTransforms(hair_system)
    if len(hair_system_parent) > 0:
        hair_system_group = hair_system_parent[0] + "Follicles"
        if not pm.objExists(hair_system_group):
            hair_system_group = pm.group(em=1, name='hsysGroup')
        if do_output_curve:
            hair_system_out_hair_group = hair_system_parent[0] + "OutputCurves"
            if not pm.objExists(hair_system_out_hair_group):
                hair_system_out_hair_group = \
                    pm.group(em=1, name='hsysOutHairGroup')
            if hide_output_curve:
                pm.setAttr(hair_system_out_hair_group + '.visibility', False)

    #create closestPointOnMesh to read the closest point parameter
    cpom = pm.createNode('closestPointOnMesh')
    pm.connectAttr((mesh_shape + '.worldMesh[0]'), (cpom + '.inMesh'))

    num_of_curves = len(curves)

    for i in range(0, num_of_curves):
        dup_name = pm.duplicate(curves[i])
        dup_shape = pm.listRelatives(dup_name[0], s=True)

        first_cv_tra = pm.xform(q=True, ws=True, t=(curves[i] + '.cv[0'))

        pm.setAttr(
            (cpom + '.ip'),
            (first_cv_tra[0], first_cv_tra[1], first_cv_tra[2]),
            type="double3"
        )

        pu = pm.getAttr(cpom + '.r.u')
        pv = pm.getAttr(cpom + '.r.v')

        hair_curve_name_prefix = mesh + "Follicle"
        naming_index = \
            num_of_curves * int(pu * float(num_of_curves - 1) + 0.5) + \
            int(pv * float(num_of_curves - 1) + 0.5)

        new_name = hair_curve_name_prefix + str(naming_index)

        #create follicle
        hair = pm.createNode('follicle')
        pm.setAttr(pu, hair + '.parameterU')
        pm.setAttr(pv, hair + '.parameterV')

        pm.connectAttr((curve_shapes[i] + '.worldSpace[0]'), (hair + '.sp'))

        transforms = pm.listTransforms(hair)
        hair_dag = transforms[0]

        pm.connectAttr((mesh_shape + '.worldMatrix[0]'), (hair + '.inputWorldMatrix'))

        pm.connectAttr((mesh_shape + '.outMesh'), (hair + '.inputMesh'))
        current_uv_set = pm.polyUVSet(q=True, currentUVSet=mesh_shape)
        pm.setAttr(current_uv_set[0], (hair + '.mapSetName'), type="string")

        pm.connectAttr((hair + '.outTranslate'), (hair_dag + '.translate'))
        pm.connectAttr((hair + '.outRotate'), (hair_dag + '.rotate'))
        pm.setAttr((hair_dag + '.translate'), lock=True)
        pm.setAttr((hair_dag + '.rotate'), lock=True)

        pm.setAttr(hair + '.degree', 3)
        pm.setAttr(hair + '.startDirection', 1)
        pm.setAttr(hair + '.restPose', 3)

        pm.parent(hair_system_group, relative=hair_dag)

        pm.parent(hair_dag, absolute=curves[i])

        pm.setAttr(hair + '.simulationMethod', 2)

        #initHairCurveDisplay(curves[i], "start")

        hair_index = i
        pm.connectAttr(
            (hair + '.outHair'),
            (hair_system + '.inputHair[%f]' % hair_index)
        )
        pm.connectAttr(
            (hair_system + '.inputHair[%f]' % hair_index),
            (hair + '.currentPosition')
        )

        crv = dup_shape[0]
        pm.connectAttr((hair + '.outCurve'), (crv + '.create'))
        #initHairCurveDisplay(crv, "current")

        transforms = pm.listTransforms(crv)
        pm.parent(transforms[0], hair_system_out_hair_group, r=True)

        pm.rename(hair_dag, new_name)

    pm.select(hair_system, r=True)
    mel.eval('displayHairCurves("current", true')

    pm.delete(cpom)


def align_to_pole_vector():
    """aligns the object to the pole vector of the selected ikHandle
    """
    selection_list = pm.ls(sl=1)

    ik_handle = ""
    control_object = ""

    for obj in selection_list:
        if pm.nodeType(obj) == 'ikHandle':
            ik_handle = obj
        else:
            control_object = obj

    temp = pm.listConnections((ik_handle + '.startJoint'), s=1)
    start_joint = temp[0]
    start_joint_pos = pm.xform(start_joint, q=True, ws=True, t=True)

    temp = pm.listConnections((ik_handle + '.endEffector'), s=1)
    end_effector = temp[0]
    pm.xform(
        control_object,
        ws=True,
        t=(start_joint_pos[0], start_joint_pos[1], start_joint_pos[2])
    )

    pm.parent(control_object, end_effector)
    pm.setAttr(control_object + '.r', 0, 0, 0)

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

    dialog_return = pm.fileDialog2(cap="Save As", fm=0, ff='Text Files(*.txt)')

    filename = dialog_return[0]
    print(filename)

    print("\n\nFiles written:\n--------------------------------------------\n")

    with open(filename, 'w') as fileId:
        for i in range(0, len(selection_list)):
            shapes = pm.listRelatives(selection_list[i], s=True, f=True)

            main_shape = ""
            for j in range(0, len(shapes)):
                if pm.getAttr(shapes[j] + '.intermediateObject') == 0:
                    main_shape = shapes
                    break
            if main_shape == "":
                main_shape = shapes[0]

            con = pm.listConnections(main_shape, t="blendShape", c=1, s=1, p=1)

            cmd = "connectAttr -f %s.worldMesh[0] %s;" % (
                ''.join(map(str, main_shape)),
                ''.join(map(str, con[0].name()))
            )
            print (cmd + "\n")
            fileId.write("%s\n" % cmd)

    print("\n------------------------------------------------------\n")
    print("filename: %s     ...done\n" % filename)


def transfer_shaders(source, target):
    """transfers shader from source to target
    """
    if isinstance(source, pm.nt.Transform):
        source_shape = source.getShape()
    else:
        source_shape = source

    if isinstance(target, pm.nt.Transform):
        target_shape = target.getShape()
    else:
        target_shape = target

    # get the shadingEngines
    shading_engines = source_shape.outputs(type=pm.nt.ShadingEngine)

    data_storage = []

    # get the assigned faces
    for shading_engine in shading_engines:
        faces = pm.sets(shading_engine, q=1)
        for faceGroup in faces:
            str_face = str(faceGroup)
            # replace the objectName
            new_face = \
                str_face.replace(source_shape.name(), target_shape.name())
            data_storage.append((shading_engine.name(), new_face))

    for data in data_storage:
        shading_engine = data[0]
        new_face = data[1]
        pm.select(new_face)
        # now assign the newFaces to the set
        pm.sets(shading_engine, fe=1)


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
    """loads the given shelf tab
    """
    # look in to the shelf mel file from user folders
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
        shelf_top_level_path = pm.melGlobals['gShelfTopLevel']
    except KeyError:
        # not in GUI mode
        return

    shelf_top_level = pm.windows.tabLayout(shelf_top_level_path, e=1)

    if len(shelf_top_level.children()) < 0:
        return

    if confirm:
        # before doing anything ask it
        response = pm.confirmDialog(
            title='Delete Shelf?',
            message='Delete %s?' % shelf_name,
            button=['Yes', 'No'],
            defaultButton='No',
            cancelButton='No',
            dismissString='No'
        )
        if response == 'No':
            return

    # update the preferences
    shelf_number = -1
    number_of_shelves = pm.optionVar['numShelves']
    for i in range(1, number_of_shelves + 1):
        if pm.optionVar['shelfName%s' % i] == shelf_name:
            shelf_number = i
            break

    if shelf_number == -1:
        # there should be no shelf with this name
        return

    # offset shelves
    for i in range(shelf_number, number_of_shelves):
        pm.optionVar['shelfLoad%s' % i] = pm.optionVar['shelfLoad%s' % (i + 1)]
        pm.optionVar['shelfName%s' % i] = pm.optionVar['shelfName%s' % (i + 1)]
        pm.optionVar['shelfFile%s' % i] = pm.optionVar['shelfFile%s' % (i + 1)]

    pm.optionVar.pop('shelfLoad%s' % number_of_shelves)
    number_of_shelves -= 1
    pm.optionVar['numShelves'] = number_of_shelves

    pm.windows.deleteUI('%s|%s' % (shelf_top_level_path, shelf_name), layout=1)

    # remove the shelf mel file from user folders
    for path in pm.internalVar(userShelfDir=1).split(os.path.pathsep):
        shelf_file_name = 'shelf_%s.mel' % shelf_name
        shelf_file_full_path = os.path.join(path, shelf_file_name)

        deleted_file_name = '%s.deleted' % shelf_file_name
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
    pm.mel.eval('shelfTabChange();')


def cube_from_bbox(bbox):
    """creates a polyCube from the given bbox

    :param bbox: pymel.core.dt.BoundingBox instance
    """
    cube = pm.polyCube(
        width=bbox.width(),
        height=bbox.height(),
        depth=bbox.depth(),
        ch=False
    )
    cube[0].setAttr('t', bbox.center())
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
    """replaces the given nodes with a bbox object
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


def get_root_nodes():
    """returns the root DAG nodes
    """
    root_transform_nodes = []
    for node in pm.ls(dag=1, transforms=1):
        if node.getParent() is None:
            shape = node.getShape()
            if shape:
                if shape.type() not in ['camera']:
                    root_transform_nodes.append(node)
            else:
                root_transform_nodes.append(node)

    return root_transform_nodes


def create_arnold_stand_in(path=None):
    """A fixed version of original arnold script of SolidAngle Arnold core API
    """
    if not pm.objExists('ArnoldStandInDefaultLightSet'):
        pm.createNode(
            "objectSet",
            name="ArnoldStandInDefaultLightSet",
            shared=True
        )
        pm.lightlink(
            object='ArnoldStandInDefaultLightSet',
            light='defaultLightSet'
        )

    stand_in = pm.createNode('aiStandIn', n='ArnoldStandInShape')
    # temp fix until we can correct in c++ plugin
    stand_in.setAttr('visibleInReflections', True)
    stand_in.setAttr('visibleInRefractions', True)

    pm.sets('ArnoldStandInDefaultLightSet', add=stand_in)
    if path:
        stand_in.setAttr('dso', path)

    return stand_in


def run_pre_publishers():
    """runs pre publishers if the current scene is a published version

    This is written to prevent users to save on top of a Published version and
    create a back door to skip un publishable scene to publish
    """
    from anima.env import mayaEnv
    m_env = mayaEnv.Maya()

    version = m_env.get_current_version()

    # check if we have a proper version
    if not version:
        return

    # check if it is a Representation
    from anima.repr import Representation
    if Representation.repr_separator in version.take_name:
        return

    if version.is_published:
        from anima.publish import (run_publishers, staging, PRE_PUBLISHER_TYPE,
                                   POST_PUBLISHER_TYPE)
        # before doing anything run all publishers
        type_name = ''
        if version.task.type:
            type_name = version.task.type.name

        # before running use the staging area to store the current version
        staging['version'] = version
        run_publishers(type_name)
        # do not forget to clean up the staging area
        staging.clear()


def run_post_publishers():
    """runs post publishers if the current scene is a published version

    This is written to prevent users to save on top of a Published version and
    create a back door to skip un publishable scene to publish
    """
    from anima.env import mayaEnv
    m_env = mayaEnv.Maya()

    version = m_env.get_current_version()

    # check if we have a proper version
    if not version:
        return

    # check if it is a Representation
    from anima.repr import Representation
    if Representation.repr_separator in version.take_name:
        return

    if version.is_published:
        from anima.publish import (run_publishers, staging, PRE_PUBLISHER_TYPE,
                                   POST_PUBLISHER_TYPE)
        # before doing anything run all publishers
        type_name = ''
        if version.task.type:
            type_name = version.task.type.name

        # before running use the staging area to store the current version
        staging['version'] = version
        run_publishers(type_name, publisher_type=POST_PUBLISHER_TYPE)
        # do not forget to clean up the staging area
        staging.clear()


def fix_external_paths():
    """fixes external paths in a maya scene
    """
    from anima.env import mayaEnv
    m_env = mayaEnv.Maya()
    m_env.replace_external_paths()


def has_shape(node):
    """checks if the given node has at least one child that has a shape
    """
    allowed_shapes = (
        pm.nt.Mesh,
        pm.nt.NurbsCurve,
        pm.nt.NurbsSurface
    )

    has_it = False

    children = node.getChildren()
    while len(children) and not has_it:
        child = children.pop(0)
        if isinstance(child, allowed_shapes):
            has_it = True
            break
        children += child.getChildren()

    return has_it


def perform_playblast(action):
    """the patched version of the original perform playblast
    """
    # check if the current scene is a Stalker related version
    print('called anima.env.mayaEnv.auxiliary.perform_playblast(%s)' % action)

    # if not call the default playblast
    # if it is call out ShotPlayblaster
    from anima.env.mayaEnv import Maya
    m = Maya()
    v = m.get_current_version()

    if v:
        # do shot playblaster
        sp = ShotPlayblaster()
        # TODO: make the viewer=1 and offScreen=0 options user selectable
        outputs = sp.playblast(
            options={
                'viewer': 1,
                'offScreen': 0,
                'compression': 'MPEG-4 Video',
                'quality': 85
            }
        )
        from anima import utils
        for output in outputs:
            utils.open_browser_in_location(output)
    else:
        # call the original playblast
        return pm.mel.eval('performPlayblast_orig(%s);' % action)


class ShotPlayblaster(object):
    """Generates playblasts for each shot in the scene and uploads it to the
    server
    """

    display_flags = [
        'nurbsCurves', 'nurbsSurfaces', 'cv', 'hulls', 'polymeshes',
        'subdivSurfaces', 'planes', 'lights', 'cameras', 'imagePlane',
        'joints', 'ikHandles', 'deformers', 'dynamics', 'fluids',
        'hairSystems', 'follicles', 'nCloths', 'nParticles', 'nRigids',
        'dynamicConstraints', 'locators', 'dimensions', 'pivots',
        'handles', 'textures', 'strokes', 'motionTrails', 'pluginShapes',
        'clipGhosts', 'greasePencils', 'manipulators', 'grid'
    ]

    cam_attribute_names = [
        'overscan',
        'filmFit',
        'displayFilmGate',
        'displayResolution',
        'displayGateMask',
        'displayFieldChart',
        'displaySafeAction',
        'displaySafeTitle',
        'displayFilmPivot',
        'displayFilmOrigin'
    ]

    def __init__(self):
        from stalker import LocalSession
        local_session = LocalSession()
        self.logged_in_user = local_session.logged_in_user

        if not self.logged_in_user:
            raise RuntimeError('Please login first!')

        self.version = None
        from anima.env.mayaEnv import Maya
        self.m_env = Maya()
        self.version = self.m_env.get_current_version()

        self.user_view_options = {}
        self.reset_user_view_options_storage()

    def get_hud_data(self):
        """
        """
        current_shot = pm.sequenceManager(q=1, currentShot=1)

        if not current_shot:
            return ''

        shot_name = pm.getAttr('%s.shotName' % current_shot)
        current_cam = pm.shot(current_shot, q=1, cc=1)
        focal_length = pm.PyNode(current_cam).getShape().getAttr('focalLength')
        sequencer = pm.ls(type='sequencer')[0]
        if sequencer.getAttr('sequence_name') != '':
            shot_info = sequencer.getAttr('sequence_name')
        else:
            shot_info = 'INVALID'

        cf = pm.currentTime(q=1) + 1

        import timecode
        # TODO: This should use project frame rate
        tc = timecode.Timecode('24', frames=cf)

        start_time = pm.shot(current_shot, q=1, st=1)
        end_time = pm.shot(current_shot, q=1, et=1)

        cs_frame = int(cf - start_time)

        length = int(end_time - start_time) + 1

        user_name = self.logged_in_user.name

        hud_string = \
            '%s | %s:%smm | tc:%s [%s] | Shot: %s | Length: %s/%sfr | [%s]' % (
                shot_info,
                current_cam.split(':')[-1],
                int(focal_length),
                tc,
                str(int(cf)-1).zfill(4),
                shot_name.split(':')[-1],
                cs_frame,
                str(length).zfill(3),
                user_name
            )
        return hud_string

    def create_hud(self, hud_name):
        """creates HUD
        """
        if pm.headsUpDisplay(hud_name, q=1, ex=1):
            #pm.warning('HUD already exists.')
            pm.headsUpDisplay(hud_name, rem=1)

        pm.headsUpDisplay(
            hud_name,
            section=7,
            block=1,
            ao=1,
            blockSize="medium",
            labelFontSize="large",
            dfs="large",
            command=self.get_hud_data,
            atr=1
        )

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

    def get_frame_range(self):
        """returns the playback range
        """
        return map(
            int,
            pm.timeControl(
                pm.melGlobals['$gPlayBackSlider'],
                q=1,
                range=1
            )[1:-1].split(':')
        )

    def get_audio_node(self):
        """returns the audio node from the time slider
        """
        audio_node_name = pm.timeControl(
            pm.melGlobals['$gPlayBackSlider'],
            q=1,
            sound=1
        )
        nodes = pm.ls(audio_node_name)
        if nodes:
            return nodes[0]
        else:
            return None

    def reset_user_view_options_storage(self):
        """resets the user view options storage
        """
        self.user_view_options = {
            'display_flags': {},
            'hud_flags': {},
            'camera_flags': {}
        }

    def store_user_options(self):
        """stores user options
        """
        # query active model panel
        active_panel = self.get_active_panel()

        # store show/hide display options for active panel
        self.reset_user_view_options_storage()

        for flag in self.display_flags:
            val = pm.modelEditor(active_panel, **{'q': 1, flag: True})
            self.user_view_options['display_flags'][flag] = val

        # store hud display options
        hud_flags = pm.headsUpDisplay(lh=1)
        for flag in hud_flags:
            val = pm.headsUpDisplay(flag, q=1, vis=1)
            self.user_view_options['hud_flags'][flag] = val

        for camera in self.get_shot_cameras():
            camera_name = camera.name()
            per_camera_attr_dict = {}
            for attr in self.cam_attribute_names:
                per_camera_attr_dict[attr] = camera.getAttr(attr)
            self.user_view_options['camera_flags'][camera_name] = \
                per_camera_attr_dict

    def set_view_options(self):
        """set view options for playblast
        """
        active_panel = self.get_active_panel()
        # turn all show/hide display options off except for polygons and
        # surfaces
        pm.modelEditor(active_panel, e=1, allObjects=False)
        pm.modelEditor(active_panel, e=1, manipulators=False)
        pm.modelEditor(active_panel, e=1, grid=False)

        pm.modelEditor(active_panel, e=1, polymeshes=True)
        pm.modelEditor(active_panel, e=1, nurbsSurfaces=True)
        pm.modelEditor(active_panel, e=1, subdivSurfaces=True)
        pm.modelEditor(active_panel, e=1,
                       pluginObjects=('gpuCacheDisplayFilter', True))
        pm.modelEditor(active_panel, e=1, planes=True)

        # turn all hud displays off
        hud_flags = pm.headsUpDisplay(lh=1)
        for flag in hud_flags:
            pm.headsUpDisplay(flag, e=1, vis=0)

        # set camera options for playblast
        for camera in self.get_shot_cameras():
            camera.setAttr('overscan', 1)
            camera.setAttr('filmFit', 1)
            camera.setAttr('displayFilmGate', 1)
            camera.setAttr('displayResolution', 0)

    def restore_user_options(self):
        """restores user options
        """
        active_panel = self.get_active_panel()
        for flag, value in self.user_view_options['display_flags'].items():
            pm.modelEditor(active_panel, **{'e': 1, flag: value})

        # reassign original hud display options
        for flag, value in self.user_view_options['hud_flags'].items():
            pm.headsUpDisplay(flag, e=1, vis=value)

        # reassign original camera options
        for camera in self.get_shot_cameras():
            camera_name = camera.name()
            camera_flags = self.user_view_options['camera_flags'][camera_name]
            for attr, value in camera_flags.items():
                camera.setAttr(attr, value)

    @classmethod
    def get_active_panel(cls):
        """returns the active model panel
        """
        active_panel = None
        panel_list = pm.getPanel(type='modelPanel')
        for panel in panel_list:
            if pm.modelEditor(panel, q=1, av=1):
                active_panel = panel
                break

        return active_panel

    def playblast(self, options=None):
        """does the real thing
        """

        default_options = {
            'fmt': 'qt',
            'sequenceTime': 1,
            'forceOverwrite': 1,
            'clearCache': 1,
            'showOrnaments': 1,
            'percent': 100,
            'offScreen': 1,
            'viewer': 0,
            'compression': 'PNG',
            'quality': 85
        }
        if options:
            default_options.update(options)

        # check camera sequencer nodes
        if len(pm.ls(type='sequenceManager')) != 1:
            raise RuntimeError(
                'Only 1 Sequence Manager node must be present in your scene.'
            )

        if len(pm.ls(type='sequencer')) != 1:
            raise RuntimeError(
                'Just 1 Sequencer node must be present in your scene.'
            )

        shots = pm.sequenceManager(listShots=1)
        if len(shots) <= 0:
            raise RuntimeError('There are no Shots in your Camera Sequencer.')

        self.store_user_options()
        self.set_view_options()

        # deselect all
        pm.select(cl=1)

        from anima.ui.progress_dialog import ProgressDialogManager
        pdm = ProgressDialogManager()
        pdm.close()

        caller = pdm.register(len(shots), 'Exporting Playblast...')

        # playblast
        # get project resolution
        if self.version:
            project = self.version.task.project
            # get the resolution
            imf = project.image_format
            width = int(imf.width * 0.5)
            height = int(imf.height * 0.5)
        else:
            # use half HD
            width = 960
            height = 540

        extra_frame = 0
        import platform
        if platform.system() == 'Windows':
            # windows Maya version drops 1 frame from end where as Linux
            # doesn't do that
            extra_frame = 1

        # if the time range is selected from the time line
        # just use this range
        global_start, global_end = self.get_frame_range()
        use_global_start_end = False
        if global_end - global_start > 1:
            use_global_start_end = 1

        audio_node = self.get_audio_node()

        playblast_outputs = []

        for shot in shots:
            video_temp_output = tempfile.mktemp(suffix='.mov')

            shot_start_frame = int(pm.shot(shot, q=1, st=1))
            shot_end_frame = int(pm.shot(shot, q=1, et=1))

            output_file_name = '%s_%s%s' % (
                os.path.splitext(self.version.filename)[0],
                shot.name().split(':')[-1] if shot else 'None',
                '.mov'
            )

            if use_global_start_end:
                if not global_start >= shot_start_frame \
                   or not global_end <= shot_end_frame:
                    continue
                shot_start_frame = global_start
                shot_end_frame = global_end

                output_file_name = '%s_%s_%s_%s%s' % (
                    os.path.splitext(self.version.filename)[0],
                    shot.name().split(':')[-1] if shot else 'None',
                    shot_start_frame,
                    shot_end_frame,
                    '.mov'
                )

            self.create_hud('kksCameraHUD')
            # create video playblast
            per_shot_options = {
                'startTime': shot_start_frame,
                'endTime': shot_end_frame + extra_frame,
                'filename': video_temp_output,
                'wh': (width, height),
                'sound': audio_node,
            }
            default_options.update(per_shot_options)
            pprint(default_options)
            pm.playblast(**default_options)

            # upload output to server
            output_path = self.set_as_output(
                output_file_name=output_file_name,
                version=self.version,
                output_file_full_path=video_temp_output,
            )

            playblast_outputs.append(output_path)

            caller.step()

        self.restore_user_options()

        return playblast_outputs

    def set_as_output(self, output_file_name='', version=None, output_file_full_path=''):
        """sets the given file as the output of the given version, also
        generates a thumbnail and a web version if it is a movie file

        :param output_file_name: The output file name
        :param version: The stalker version instance
        :param output_file_full_path: the path of the media file
        """
        hires_extension = '.mov'
        webres_extension = '.webm'
        thumbnail_extension = '.png'

        # TODO: we shouldn't need a "shot" parameter, just ask the desired output name
        hires_output_file_name = '%s%s' % (
            os.path.splitext(output_file_name)[0],
            hires_extension
        )

        webres_output_file_name = '%s%s' % (
            os.path.splitext(output_file_name)[0],
            webres_extension
        )

        thumbnail_output_file_name = '%s%s' % (
            os.path.splitext(output_file_name)[0],
            thumbnail_extension
        )

        task = version.task

        hires_path = os.path.join(
            task.absolute_path, 'Outputs', 'Stalker_Pyramid',
            hires_output_file_name
        )
        webres_path = os.path.join(
            task.absolute_path, 'Outputs', 'Stalker_Pyramid', 'ForWeb',
            webres_output_file_name
        )
        thumbnail_path = os.path.join(
            task.absolute_path, 'Outputs', 'Stalker_Pyramid', 'Thumbnail',
            thumbnail_output_file_name
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

        shutil.copy(output_file_full_path, hires_path)

        # generate the web version
        from anima.utils import MediaManager
        m = MediaManager()
        temp_web_version_full_path = \
            m.generate_media_for_web(output_file_full_path)

        try:
            shutil.copy(temp_web_version_full_path, webres_path)
        except IOError:
            pass

        temp_thumbnail_full_path = \
            m.generate_thumbnail(output_file_full_path)
        try:
            # also upload thumbnail
            shutil.copy(temp_thumbnail_full_path, thumbnail_path)
        except IOError:
            pass

        project = task.project
        repo = project.repository

        from stalker import db, Link

        # try to find a file with the same name assigned to the version as
        # output
        found = None
        hires_repo_relative_path = repo.make_relative(hires_path)
        for output in version.outputs:
            if output.full_path == hires_repo_relative_path:
                found = True
                break

        # if we found a file with the same name as the output, just overwrite
        # it
        if not found:
            l_hires = Link(
                full_path=repo.make_relative(hires_path),
                original_filename=hires_output_file_name
            )

            l_for_web = Link(
                full_path=repo.make_relative(webres_path),
                original_filename=hires_output_file_name
            )

            l_hires.thumbnail = l_for_web

            version.outputs.append(l_hires)

            l_thumb = Link(
                full_path=repo.make_relative(thumbnail_path),
                original_filename=hires_output_file_name
            )
            l_for_web.thumbnail = l_thumb

            db.DBSession.add_all([l_hires, l_for_web, l_thumb])
            db.DBSession.commit()

        return hires_path


def export_alembic_from_cache_node():
    from anima.ui.progress_dialog import ProgressDialogManager
    import os

    pdm = ProgressDialogManager()
    pdm.close()

    # list all cacheable nodes
    cacheable_nodes = []
    tr_list = pm.ls(tr=1, type='transform')

    caller = pdm.register(len(tr_list), 'Searching for Cacheable Nodes')

    for tr in tr_list:
        if tr.hasAttr('cacheable') and tr.getAttr('cacheable'):
            # check if any of its parents has a cacheable attribute
            has_cacheable_parent = False
            for parent in tr.getAllParents():
                if parent.hasAttr('cacheable'):
                    has_cacheable_parent = True
                    break

            if not has_cacheable_parent:
                # only include direct references
                ref = tr.referenceFile()
                if ref is not None and ref.parent() is None:
                    cacheable_nodes.append(tr)

        caller.step()

    # stop if there are no cacheable nodes in the scene
    if not cacheable_nodes:
        return

    cacheable_nodes.sort(key=lambda x: x.getAttr('cacheable'))

    caller = pdm.register(len(cacheable_nodes), 'Exporting Alembic Caches')

    start_frame = pm.playbackOptions(q=1, ast=1)
    end_frame = pm.playbackOptions(q=1, aet=1)

    current_file_full_path = pm.sceneName()
    current_file_path = os.path.dirname(current_file_full_path)
    current_file_name = os.path.basename(current_file_full_path)

    # export alembic caches
    previous_cacheable_attr_value = ''
    i = 1
    for cacheable_node in cacheable_nodes:
        cacheable_attr_value = cacheable_node.getAttr('cacheable')
        if cacheable_attr_value == previous_cacheable_attr_value:
            i += 1
        else:
            i = 1

        # hide any child node that has "rig" or "proxy" or "low" in its name
        wrong_node_names = ['rig', 'proxy', 'low']
        hidden_nodes = []
        for child in pm.ls(cacheable_node.getChildren(), type='transform'):
            if any([n in child.name() for n in wrong_node_names]):
                if child.v.get() is True:
                    child.v.set(False)
                    hidden_nodes.append(child)

        output_path = os.path.join(
            current_file_path,
            'Outputs/alembic/%s%i/' % (cacheable_attr_value, i)
        )

        output_filename = '%s_%i_%i_%s%i%s' % (
            os.path.splitext(current_file_name)[0],
            start_frame, end_frame, cacheable_attr_value, i, '.abc'
        )

        output_full_path = \
            os.path.join(output_path, output_filename).replace('\\', '/')
        if not os.path.exists(os.path.dirname(output_full_path)):
            os.makedirs(os.path.dirname(output_full_path))

        command = 'AbcExport -j "-frameRange %s %s -ro -stripNamespaces ' \
                  '-uvWrite -wholeFrameGeo -worldSpace -root %s -file %s";'
        # command = 'AbcExport -j "-frameRange %s %s -ro ' \
        #           '-uvWrite -wholeFrameGeo -worldSpace -root |%s -file %s";'

        pm.mel.eval(
            command % (
                int(start_frame),
                int(end_frame),
                cacheable_node.fullPath(),
                output_full_path
            )
        )
        previous_cacheable_attr_value = cacheable_attr_value

        # reveal any previously hidden nodes
        for node in hidden_nodes:
            node.v.set(True)

        caller.step()


# noinspection PyStatementEffect
class BarnDoorSimulator(object):
    """A aiBarnDoor simulator
    """

    sides = ['top', 'bottom', 'left', 'right']
    message_storage_attr_name = 'barnDoorSimulatorData'
    custom_data_storage_attr_name = 'barnDoorSimulatorCustomData'

    def __init__(self):
        self.frame_curve = None
        self.light = None
        self.barn_door = None

        self.script_job_no = -1

        self.preview_curves = {
            'top': [],
            'bottom': [],
            'left': [],
            'right': []
        }

        self.joints = {
            'top': [],
            'bottom': [],
            'left': [],
            'right': [],
        }

    def create_barn_door(self):
        """creates the barn door node
        """
        light_shape = self.light.getShape()
        inputs = light_shape.inputs(type='aiBarndoor')
        if inputs:
            self.barn_door = inputs[0]
        else:
            self.barn_door = pm.createNode('aiBarndoor')
            self.barn_door.attr('message') >> \
                light_shape.attr('aiFilters').next_available

    def store_data(self, data):
        """stores the given data
        """
        if not self.light.hasAttr(self.custom_data_storage_attr_name):
            pm.addAttr(
                self.light,
                ln=self.custom_data_storage_attr_name,
                dt='string'
            )

        self.light.setAttr(self.custom_data_storage_attr_name, data)

    def store_nodes(self, nodes):
        """stores the nodes
        """
        for node in nodes:
            self.store_node(node)

    def store_node(self, node):
        """stores the node in the storage attribute
        """
        if not self.light.hasAttr(self.message_storage_attr_name):
            pm.addAttr(
                self.light,
                ln=self.message_storage_attr_name,
                m=1
            )

        node.message >> self.light.attr(self.message_storage_attr_name).next_available

    def create_frame_curve(self):
        """creates the frame curve
        """
        self.frame_curve = pm.curve(
            d=1,
            p=[(-0.5, 0.5, 0),
               (0.5, 0.5, 0),
               (0.5, -0.5, 0),
               (-0.5, -0.5, 0),
               (-0.5, 0.5, 0)],
            k=[0, 1, 2, 3, 4]
        )
        self.store_node(self.frame_curve)

    def create_preview_curve(self, side):
        """creates preview curves
        """
        # create two joints
        j1 = pm.createNode('joint')
        j2 = pm.createNode('joint')

        j1.t.set(-0.5, 0, 0)
        j2.t.set(0.5, 0, 0)

        self.joints[side] += [j1, j2]

        # create one nurbs curve
        preview_curve = pm.curve(
            d=1,
            p=[(-0.5, 0, 0),
               (0.5, 0, 0)],
            k=[0, 1]
        )
        self.preview_curves[side].append(preview_curve)

        # bind the joints to the curveShape
        pm.select([preview_curve, j1, j2])
        skin_cluster = pm.skinCluster()

        self.store_nodes([
            j1, j2, preview_curve, skin_cluster
        ])

    def create_expression(self):
        """creates the expression
        """
        expr = """float $frame_scale, $cone_angle;

if({light}.penumbraAngle < 0){{
    $cone_angle = {light}.coneAngle;
}} else {{
    $cone_angle = {light}.coneAngle + {light}.penumbraAngle;
}}

$frame_scale = tan(deg_to_rad({light}.coneAngle * 0.5));
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
                'light': self.light.name(),
                'frame': self.frame_curve.name(),
                'barn_door': self.barn_door.name(),

                'top_left_joint': self.joints['top'][0],
                'top_right_joint': self.joints['top'][1],

                'top_edge_left_joint': self.joints['top'][2],
                'top_edge_right_joint': self.joints['top'][3],

                'bottom_left_joint': self.joints['bottom'][0],
                'bottom_right_joint': self.joints['bottom'][1],

                'bottom_edge_left_joint': self.joints['bottom'][2],
                'bottom_edge_right_joint': self.joints['bottom'][3],

                'left_top_joint': self.joints['left'][0],
                'left_bottom_joint': self.joints['left'][1],

                'left_edge_top_joint': self.joints['left'][2],
                'left_edge_bottom_joint': self.joints['left'][3],

                'right_top_joint': self.joints['right'][0],
                'right_bottom_joint': self.joints['right'][1],

                'right_edge_top_joint': self.joints['right'][2],
                'right_edge_bottom_joint': self.joints['right'][3],
            }
        )

        expr_node = pm.expression(s=expr)
        self.store_node(expr_node)

    def create_script_job(self):
        """creates the script job that disables the affected highlight
        """
        script_job_no = pm.scriptJob(
            e=["SelectionChanged",
                'if pm.ls(sl=1) and pm.ls(sl=1)[0].name() == "%s":\n'
                '    pm.displayPref(displayAffected=False)\n'
                'else:\n'
                '    pm.displayPref(displayAffected=True)' % self.light.name()
            ]
        )
        self.store_data('%s' % script_job_no)

    def setup(self):
        """setup the magic
        """
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
        pm.parent(
            self.frame_curve,
            self.light
        )

        self.frame_curve.setAttr('t', [0, 0, -0.5])
        self.frame_curve.setAttr('r', [0, 0, 0])
        self.frame_curve.setAttr('s', [1, 1, 1])

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
            all_preview_curves,
            n='%s_barndoor_preview_curves' % self.light.name()
        )

        self.store_node(shapes_group)

        # create script job
        self.create_script_job()

        # select the light again
        pm.select(self.light)

    def unsetup(self):
        """deletes the barn door setup
        """
        try:
            pm.delete(self.light.attr(self.message_storage_attr_name).inputs())
        except AttributeError:
            pass

        pm.scriptJob(
            k=int(self.light.getAttr(self.custom_data_storage_attr_name))
        )