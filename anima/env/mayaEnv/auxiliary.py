# -*- coding: utf-8 -*-
# Copyright (c) 2012-2014, Anima Istanbul
#
# This module is part of anima-tools and is released under the BSD 2
# License: http://www.opensource.org/licenses/BSD-2-Clause

import os

import pymel.core as pm
import maya.mel as mel


__version__ = "v10.1.13"


def get_valid_dag_node(node):
    """returns a valid dag node even the input is string
    """
    try:
        dag_node = pm.nodetypes.DagNode(node)
    except pm.MayaNodeError:
        print 'Error: no node named : %s' % node
        return None

    return dag_node


def get_valid_node(node):
    """returns a valid PyNode even the input is string
    """
    try:
        PyNode = pm.PyNode(node)
    except pm.MayaNodeError:
        print 'Error: no node named : %s' % node
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
                hair_system_out_hair_group = pm.group(em=1, name='hsysOutHairGroup')
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
        naming_index = num_of_curves * int(pu * float(num_of_curves - 1) + 0.5) + int(pv * float(num_of_curves - 1) + 0.5)

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
    print filename

    print "\n\nFiles written:\n---------------------------------------------\n"

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
            fileId.write("%s\n"%cmd)

    print "\n------------------------------------------------------\n"
    print ("filename: %s     ...done\n" % filename)


def transfer_shaders(source, target):
    """transfers shader from source to target
    """
    source_shape = source.getShape()
    target_shape = target.getShape()

    # get the shadingEngines
    shading_engines = [shEn
                       for shEn in source.getShape().inputs()
                       if isinstance(shEn, pm.nodetypes.ShadingEngine)]

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
    allowed_shapes = (
        pm.nt.Mesh,
        pm.nt.NurbsCurve,
        pm.nt.NurbsSurface
    )

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
        node_shape = node.getShape()
        if not node_shape:
            # check if it has child nodes
            if len(node.getChildren()) == 0:
                continue
        elif not isinstance(node_shape, allowed_shapes):
            continue

        bbox = cube_from_bbox(node.boundingBox())
        bbox.setParent(node.getParent())

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