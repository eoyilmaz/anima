# -*- coding: utf-8 -*-
# Copyright (c) 2012-2014, Anima Istanbul
#
# This module is part of anima-tools and is released under the BSD 2
# License: http://www.opensource.org/licenses/BSD-2-Clause

import os
import datetime
import uuid

import pymel.core as pm
import maya.cmds as mc

from anima import stalker_server_internal_address
from anima.publish import (clear_publishers, publisher, staging,
                           PRE_PUBLISHER_TYPE, POST_PUBLISHER_TYPE)
from anima.exc import PublishError
from anima.repr import Representation
from anima.utils import utc_to_local
from anima.env.mayaEnv import auxiliary

clear_publishers()

MAX_NODE_DISPLAY = 80

# TODO: this should be depending on to the project some projects still can
#       use mental ray
VALID_MATERIALS = [
    u'aiAmbientOcclusion',
    u'aiHair',
    u'aiRaySwitch',
    u'aiShadowCatcher',
    u'aiSkin',
    u'aiSkinSss',
    u'aiStandard',
    u'aiUtility',
    u'aiWireframe',
    u'displacementShader',
    u'lambert',
    u'blinn',
    u'layeredShader',
    u'oceanShader',
    u'phong',
    u'phongE',
    u'rampShader',
    u'surfaceShader',
]


#*********#
# GENERIC #
#*********#
# @publisher
# def delete_turtle_nodes():
#     """deletes the Turtle related nodes
#     """
#     # deletes Turtle from scene
#     turtle_node_names = [
#         'TurtleRenderOptions',
#         'TurtleDefaultBakeLayer',
#         'TurtleBakeLayerManager',
#         'TurtleUIOptions'
#     ]
#
#     for node_name in turtle_node_names:
#         try:
#             node = pm.PyNode(node_name)
#             node.unlock()
#             pm.delete(node)
#         except pm.MayaNodeError:
#             pass
#
#     try:
#         pymel_undo_node = pm.PyNode('__pymelUndoNode')
#         pymel_undo_node.unlock()
#         pm.delete(pymel_undo_node)
#     except pm.MayaNodeError:
#         pass
#
#     pm.unloadPlugin('Turtle', force=1)
#
#     pm.warning('Turtle deleted successfully.')


@publisher
def delete_unknown_nodes():
    """deletes unknown nodes
    """
    # delete the unknown nodes
    unknown_nodes = pm.ls(type='unknown')
    # unlock each possible locked unknown nodes
    for node in unknown_nodes:
        node.unlock()
    pm.delete(unknown_nodes)


@publisher
def check_time_logs():
    """do not allow publishing if there is no time logs for the task, do that
    only for non WFD tasks
    """
    v = staging.get('version')

    if v:
        task = v.task
        now = datetime.datetime.now()
        task_start = task.computed_start if task.computed_start else task.start
        task_start = utc_to_local(task_start)
        if task.status.code != 'WFD' and task_start <= now:
            if len(task.time_logs) == 0:
                raise PublishError(
                    '<p>Please create a TimeLog before publishing this '
                    'asset:<br><br>'
                    '<a href="%s/tasks/%s/view">Open In WebBrowser</a>'
                    '</p>' % (stalker_server_internal_address, task.id)
                )


@publisher
def check_node_names_with_bad_characters():
    """checks node names and ensures that there are no nodes with ord(c) > 127
    """
    nodes_with_bad_name = []
    for node in pm.ls():
        if any(map(lambda x: x == '?' or ord(x) > 127, node.name())):
            nodes_with_bad_name.append(node)

    if len(nodes_with_bad_name) > 0:
        pm.select(nodes_with_bad_name)
        raise PublishError(
            'There are nodes with <b>unknown characters</b> in their names:'
            '<br><br>'
            '%s' %
            '<br>'.join(
                map(lambda x: x.name(),
                    nodes_with_bad_name)[:MAX_NODE_DISPLAY]
            )
        )


@publisher
def delete_unused_nodes():
    """deletes unused shading nodes
    """
    num_of_items_deleted = pm.mel.eval('MLdeleteUnused')
    if num_of_items_deleted:
        # do not raise any error just warn the user
        pm.warning('Deleted unused nodes during Publish operation!!')


@publisher
def check_representations():
    """checks if the referenced versions are all matching the representation
    type of the current version
    """
    ref_reprs = []
    wrong_reprs = []

    v = staging.get('version')

    if v:
        r = Representation(version=v)
        current_repr = r.repr

        # For **Base** representation
        # allow any type of representation to be present in the scene
        if r.is_base():
            return

        for ref in pm.listReferences():
            ref_repr = ref.repr
            if ref_repr is None:
                # skip this one this is not related to a Stalker Version
                continue

            ref_reprs.append([ref, ref_repr])
            if ref_repr != current_repr:
                wrong_reprs.append(ref)
    else:
        return

    if len(wrong_reprs):
        ref_repr_labels = []
        for ref_repr in ref_reprs:
            ref = ref_repr[0]
            repr_name = ref_repr[1]

            color = 'red' if current_repr != repr_name else 'green'

            ref_repr_labels.append(
                '<span style="color: %(color)s">%(repr_name)s</span> -> '
                '%(ref)s' %
                {
                    'color': color,
                    'repr_name': repr_name,
                    'ref': ref.refNode.name()
                }
            )

        raise PublishError(
            'You are saving as the <b>%s</b> representation<br>'
            'for the current scene, but the following references<br>'
            'are not <b>%s</b> representations of their versions:<br><br>'
            '%s' % (
                current_repr, current_repr,
                '<br>'.join(ref_repr_labels[:MAX_NODE_DISPLAY])
            )
        )


@publisher
def cleanup_intermediate_objects():
    """deletes any unused intermediate object in the current scene
    """
    pm.delete(
        [node
         for node in pm.ls(type='mesh')
         if len(node.inputs()) == 0 and len(node.outputs()) == 0 and
            node.intermediateObject.get() and node.referenceFile() is None]
    )


@publisher
def check_old_object_smoothing():
    """checking if there are objects with
    """
    meshes_with_smooth_mesh_preview = []
    for node in pm.ls(type='mesh'):
        if node.displaySmoothMesh.get() != 0:
            meshes_with_smooth_mesh_preview.append(node.getParent())

    if len(meshes_with_smooth_mesh_preview) > 0:
        pm.select(meshes_with_smooth_mesh_preview)
        raise PublishError(
            'Please do not use <b>Smooth Mesh</b> on following nodes:<br><br>'
            '%s' %
            '<br>'.join(
                map(lambda x: x.name(),
                    meshes_with_smooth_mesh_preview[:MAX_NODE_DISPLAY])
            )
        )


@publisher
def check_if_previous_version_references():
    """check if a previous version of the same task is referenced to the scene
    """
    from anima.env.mayaEnv import Maya
    m = Maya()
    ver = m.get_current_version()

    if ver is None:
        return

    same_version_references = []
    for ref in pm.listReferences():  # check only 1st level references
        ref_version = m.get_version_from_full_path(ref.path)
        if ref_version:
            if ref_version.task == ver.task \
               and ref_version.take_name == ver.take_name:
                same_version_references.append(ref)

    if len(same_version_references):
        print('The following nodes are references to an older version of this '
              'scene')
        print(
            '\n'.join(map(lambda x: x.refNode.name(), same_version_references))
        )
        raise PublishError(
            'The current scene contains a <b>reference</b> to a<br>'
            '<b>previous version</b> of itself.<br><br>'
            'Please remove it!!!'
        )


@publisher
def delete_empty_namespaces():
    """checks and deletes empty namespaces
    """
    # only allow namespaces with DAG objects in it and no child namespaces
    empty_namespaces = [
        ns for ns in pm.listNamespaces(recursive=True)
        if len(pm.ls(ns.listNodes(), dag=True, mat=True)) == 0
        and len(ns.listNamespaces()) == 0
    ]

    # remove all empty
    for ns in empty_namespaces:
        pm.namespace(rm=ns, mnr=1)

    # if len(empty_namespaces):
    #     raise PublishError(
    #         'There are empty <b>namespaces</b><br><br>'
    #         'Please remove them!!!'
    #     )


#*******#
# MODEL #
#*******#
@publisher('model')
def check_no_references():
    """there should be no references
    """
    if len(pm.listReferences()):
        raise PublishError(
            'There should be no <b>References</b> in a <b>Model</b> scene.'
        )


@publisher('model')
def check_history():
    """there should be no history on the objects
    """
    excluded_types = ['mesh', 'shadingEngine', 'groupId']
    nodes_with_history = []

    # get all shapes
    all_shapes = pm.ls(type='mesh')
    for node in all_shapes:
        history_nodes = []
        for h_node in node.listHistory(pdo=1, lv=1):
            if h_node.type() not in excluded_types:
                history_nodes.append(h_node)

        if len(history_nodes) > 0:
            nodes_with_history.append(node)

    if len(nodes_with_history):
        pm.select(nodes_with_history)
        # there is history
        raise PublishError(
            'There is history on:\n\n'
            '%s'
            '\n\n'
            'there should be no '
            'history in Model versions' %
            '\n'.join(
                map(lambda x: x.name(),
                    nodes_with_history[:MAX_NODE_DISPLAY])
            )
        )


@publisher('model')
def check_if_default_shader():
    """check if only default shader is assigned
    """
    # skip if this is a representation
    v = staging.get('version')
    if v and Representation.repr_separator in v.take_name:
        return

    if len(pm.ls(mat=1)) > 2:
        raise PublishError(
            'Use only lambert1 as the shader!'
        )


@publisher('model')
def check_if_root_nodes_have_no_transformation():
    """checks if transform nodes directly under world have 0 transformations
    """
    root_transform_nodes = auxiliary.get_root_nodes()

    non_freezed_root_nodes = []
    for node in root_transform_nodes:
        t = node.t.get()
        r = node.r.get()
        s = node.s.get()
        if t.x != 0 or t.y != 0 or t.z != 0 \
           or r.x != 0 or r.y != 0 or r.z != 0 \
           or s.x != 1 or s.y != 1 or s.z != 1:
            non_freezed_root_nodes.append(node)

    if len(non_freezed_root_nodes):
        pm.select(non_freezed_root_nodes)
        raise PublishError(
            'Please freeze the following node transformations:\n\n%s' %
            '\n'.join(
                map(lambda x: x.name(),
                    non_freezed_root_nodes[:MAX_NODE_DISPLAY])
            )
        )


@publisher('model')
def check_if_leaf_mesh_nodes_have_no_transformation():
    """checks if all the Mesh transforms have 0 transformation, but it is
    allowed to move the mesh nodes in space with a parent group node.
    """
    mesh_nodes_with_transform_children = []
    for node in pm.ls(dag=1, type='mesh'):
        parent = node.getParent()
        tra_under_shape = pm.ls(
            parent.listRelatives(),
            type='transform'
        )
        if len(tra_under_shape):
            mesh_nodes_with_transform_children.append(parent)

    if len(mesh_nodes_with_transform_children):
        pm.select(mesh_nodes_with_transform_children)
        raise PublishError(
            'The following meshes have other objects parented to them:'
            '\n\n%s'
            '\n\nPlease remove any object under them!' %
            '\n'.join(
                map(lambda x: x.name(),
                    mesh_nodes_with_transform_children[:MAX_NODE_DISPLAY])
            )
        )


@publisher('model')
def check_model_quality():
    """checks the quality of the model
    """
    # skip if this is a representation
    v = staging.get('version')
    if v and Representation.repr_separator in v.take_name:
        return

    pm.select(None)
    pm.mel.eval(
        'polyCleanupArgList 3 { "1","2","0","0","1","0","0","0","0","1e-005",'
        '"0","0","0","0","0","2","1" };'
    )

    if len(pm.ls(sl=1)) > 0:
        raise RuntimeError(
            """There are issues in your model please run:<br><br>
            <b>PolygonMesh -> Mesh -> Cleanup...</b><br><br>
            <ul>Check:
            <li>Faces with more than 4 sides</li>
            <li>Faces with holes</li>
            <li>Lamina Faces</li>
            <li>Non-manifold Geometry</li>
            </ul>"""
        )


@publisher('model')
def check_anim_layers():
    """check if there are animation layers on the scene
    """
    if len(pm.ls(type='animLayer')) > 0:
        raise PublishError(
            'There should be no <b>Animation Layers</b> in the scene!!!'
        )


@publisher('model')
def check_display_layer():
    """check if there are display layers
    """
    if len(pm.ls(type='displayLayer')) > 1:
        raise PublishError(
            'There should be no <b>Display Layers</b> in the scene!!!'
        )


@publisher('model')
def check_extra_cameras():
    """checking if there are extra cameras
    """
    if len(pm.ls(type='camera')) > 4:
        raise PublishError('There should be no extra cameras in your scene!')


@publisher('model')
def check_empty_groups():
    """check if there are empty groups
    """
    # skip if this is a representation
    v = staging.get('version')
    if v and Representation.repr_separator in v.take_name:
        return

    empty_groups = []
    for node in pm.ls(type='transform'):
        if len(node.listRelatives(children=1)) == 0:
            empty_groups.append(node)

    if len(empty_groups):
        pm.select(empty_groups)
        raise PublishError(
            'There are <b>empty groups</b> in your scene, '
            'please remove them!!!'
        )


@publisher('model')
def check_empty_shapes():
    """checks if there are empty mesh nodes
    """
    empty_shape_nodes = []
    for node in pm.ls(type='mesh'):
        if node.numVertices() == 0:
            empty_shape_nodes.append(node)

    if len(empty_shape_nodes) > 0:
        pm.select(map(
            lambda x: x.getParent(),
            empty_shape_nodes
        ))
        raise PublishError(
            'There are <b>meshes with no geometry</b> in your scene, '
            'please delete them!!!'
        )


@publisher('model')
def check_uv_existence():
    """check if there are uvs in all objects
    """
    # skip if this is a representation
    v = staging.get('version')
    if v and Representation.repr_separator in v.take_name:
        return

    all_meshes = pm.ls(type='mesh')
    nodes_with_no_uvs = []
    for node in all_meshes:
        if not node.getAttr('intermediateObject'):
            if not len(node.getUVs(uvSet='map1')[0]):
                nodes_with_no_uvs.append(node)

    if len(nodes_with_no_uvs) > 0:
        # get transform nodes
        tra_nodes = map(
            lambda x: x.getParent(),
            nodes_with_no_uvs
        )
        pm.select(tra_nodes)
        raise RuntimeError(
            """There are nodes with <b>no UVs</b>:
            <br><br>%s""" %
            '<br>'.join(
                map(lambda x: x.name(),
                    tra_nodes[:MAX_NODE_DISPLAY])
            )
        )


@publisher('model')
def check_out_of_space_uvs():
    """checks if there are uvs with u values that are bigger than 10.0
    """

    # skip if this is a representation
    v = staging.get('version')
    if v and Representation.repr_separator in v.take_name:
        return

    all_meshes = pm.ls(type='mesh')
    mesh_count = len(all_meshes)
    nodes_with_out_of_space_uvs = []

    from anima.ui.progress_dialog import ProgressDialogManager
    pdm = ProgressDialogManager()

    if not pm.general.about(batch=1) and mesh_count:
        pdm.use_ui = True

    caller = pdm.register(mesh_count, 'check_out_of_space_uvs()')

    for node in all_meshes:
        u, v = node.getUVs()
        u = sorted(u)
        if u[0] < 0.0 or u[-1] > 10.0 or v[0] < 0.0:
            nodes_with_out_of_space_uvs.append(node)

        caller.step()

    if len(nodes_with_out_of_space_uvs):
        # get transform nodes
        tra_nodes = map(
            lambda x: x.getParent(),
            nodes_with_out_of_space_uvs
        )
        pm.select(tra_nodes)
        raise RuntimeError(
            """There are nodes which have a UV value bigger than <b>10</b>:
            <br><br>%s""" %
            '<br>'.join(
                map(lambda x: x.name(),
                    tra_nodes[:MAX_NODE_DISPLAY])
            )
        )


@publisher('model')
def check_uv_border_crossing():
    """checks if any of the uv shells are crossing uv borders
    """
    # skip if this is a representation
    v = staging.get('version')
    if v and Representation.repr_separator in v.take_name:
        return

    all_meshes = pm.ls(type='mesh')
    mesh_count = len(all_meshes)

    nodes_with_uvs_crossing_borders = []

    from anima.ui.progress_dialog import ProgressDialogManager
    pdm = ProgressDialogManager()

    if not pm.general.about(batch=1) and mesh_count:
        pdm.use_ui = True

    caller = pdm.register(mesh_count, 'check_out_of_space_uvs()')

    for node in all_meshes:
        all_uvs = node.getUVs()
        uv_shell_ids = node.getUvShellsIds()

        # prepare an empty dict of lists
        uvs_per_shell = {}
        for shell_id in range(uv_shell_ids[1]):
            uvs_per_shell[shell_id] = [[], []]

        for uv_id in range(len(uv_shell_ids[0])):
            u = all_uvs[0][uv_id]
            v = all_uvs[1][uv_id]
            shell_id = uv_shell_ids[0][uv_id]

            uvs_per_shell[shell_id][0].append(u)
            uvs_per_shell[shell_id][1].append(v)

        # now check all uvs per shell
        for shell_id in range(uv_shell_ids[1]):
            us = sorted(uvs_per_shell[shell_id][0])
            vs = sorted(uvs_per_shell[shell_id][1])

            #check first and last u and v values
            if int(us[0]) != int(us[-1]) or int(vs[0]) != int(vs[-1]):
                # they are not equal it is crossing spaces
                nodes_with_uvs_crossing_borders.append(node)
                break

        caller.step()

    if len(nodes_with_uvs_crossing_borders):
        # get transform nodes
        tra_nodes = map(
            lambda x: x.getParent(),
            nodes_with_uvs_crossing_borders
        )
        pm.select(tra_nodes)
        raise RuntimeError(
            """There are nodes with <b>UV-Shells</b> that are crossing
            <b>UV BORDERS</b>:<br><br>%s""" %
            '<br>'.join(
                map(lambda x: x.name(),
                    tra_nodes[:MAX_NODE_DISPLAY])
            )
        )


@publisher('model')
def check_uvs():
    """checks uvs with no uv area

    The area of a 2d polygon calculation is based on the answer of Darius Bacon
    in http://stackoverflow.com/questions/451426/how-do-i-calculate-the-surface-area-of-a-2d-polygon
    """

    # skip if this is a representation
    v = staging.get('version')
    if v and Representation.repr_separator in v.take_name:
        return

    def area(p):
        return 0.5 * abs(sum(x0 * y1 - x1 * y0
                             for ((x0, y0), (x1, y1)) in segments(p)))

    def segments(p):
        return zip(p, p[1:] + [p[0]])

    all_meshes = pm.ls(type='mesh')
    mesh_count = len(all_meshes)

    from anima.ui.progress_dialog import ProgressDialogManager
    pdm = ProgressDialogManager()

    if not pm.general.about(batch=1) and mesh_count:
        pdm.use_ui = True

    caller = pdm.register(mesh_count, 'check_uvs()')

    meshes_with_zero_uv_area = []
    for node in all_meshes:
        all_uvs = node.getUVs()
        try:
            for i in range(node.numFaces()):
                uvs = []
                for j in range(node.numPolygonVertices(i)):
                    #uvs.append(node.getPolygonUV(i, j))
                    uv_id = node.getPolygonUVid(i, j)
                    uvs.append((all_uvs[0][uv_id], all_uvs[1][uv_id]))
                if area(uvs) == 0.0:
                    meshes_with_zero_uv_area.append(node)
                    break
        except RuntimeError:
            meshes_with_zero_uv_area.append(node)

        caller.step()

    if len(meshes_with_zero_uv_area):
        pm.select([node.getParent() for node in meshes_with_zero_uv_area])
        raise RuntimeError(
            """There are meshes with no uvs or faces with zero uv area:<br><br>
            %s""" %
            '<br>'.join(
                map(lambda x: x.name(),
                    meshes_with_zero_uv_area[:MAX_NODE_DISPLAY])
            )
        )


#******************#
# LOOK DEVELOPMENT #
#******************#
LOOK_DEV_TYPES = ['LookDev', 'Look Dev', 'LookDevelopment', 'Look Development']


@publisher(LOOK_DEV_TYPES)
def disable_internal_reflections_in_aiStandard():
    """disable internal reflections in aiStandard
    """
    for mat in pm.ls(type='aiStandard'):
        if mat.referenceFile() is None:
            mat.setAttr('enableInternalReflections', 0)


@publisher(LOOK_DEV_TYPES)
def check_all_tx_textures():
    """checks if tx textures are created for all of the texture nodes in the
    current scene
    """
    v = staging.get('version')
    if v and Representation.repr_separator in v.take_name:
        return

    texture_file_paths = []
    workspace_path = pm.workspace.path

    def add_path(path):
        if path != '':
            path = os.path.expandvars(path)
            if not os.path.isabs(path):
                path = \
                    os.path.normpath(os.path.join(workspace_path, path))
            texture_file_paths.append(path)

    for node in pm.ls(type='file'):
        add_path(node.fileTextureName.get())

    for node in pm.ls(type='aiImage'):
        add_path(node.filename.get())

    import glob

    textures_with_no_tx = []
    for path in texture_file_paths:
        tx_path = '%s.tx' % os.path.splitext(path)[0]
        # replace any <udim> value with *
        tx_path = tx_path.replace('<udim>', '*')

        if not len(glob.glob(tx_path)):
            textures_with_no_tx.append(path)

    if len(textures_with_no_tx):
        raise PublishError('There are textures with no <b>TX</b> file!!!')


@publisher(LOOK_DEV_TYPES)
def check_lights():
    """checks if there are lights in the scene
    """
    all_lights = pm.ls(
        type=['light', 'aiAreaLight', 'aiSkyDomeLight', 'aiPhotometricLight']
    )
    if len(all_lights):
        pm.select(all_lights)
        raise PublishError(
            'There are <b>Lights</b> in the current scene:<br><br>%s<br><br>'
            'Please delete them!!!' %
            '<br>'.join(map(lambda x: x.name(), all_lights))
        )


@publisher(LOOK_DEV_TYPES)
def check_only_supported_materials_are_used():
    """check if only supported materials are used
    """
    non_arnold_materials = []

    for material in pm.ls(mat=1):
        if material.name() not in ['lambert1', 'particleCloud1']:
            if material.type() not in VALID_MATERIALS:
                non_arnold_materials.append(material)

    if len(non_arnold_materials):
        pm.select(non_arnold_materials)
        raise PublishError(
            'There are non-Arnold materials in the scene:<br><br>%s<br><br>'
            'Please remove them!!!' %
            '<br>'.join(map(lambda x: x.name(), non_arnold_materials))
        )


@publisher(LOOK_DEV_TYPES)
def check_objects_still_using_default_shader():
    """check if there are objects still using the default shader
    """
    # skip if this is a representation
    v = staging.get('version')
    if v and Representation.repr_separator in v.take_name:
        return

    objects_with_default_material = mc.sets('initialShadingGroup', q=1)
    if objects_with_default_material and len(objects_with_default_material):
        mc.select(objects_with_default_material)
        raise PublishError(
            'There are objects still using <b>initialShadingGroup</b><br><br>'
            '%s<br><br>Please assign a proper material to them' %
            '<br>'.join(
                objects_with_default_material[:MAX_NODE_DISPLAY]
            )
        )


@publisher(LOOK_DEV_TYPES + ['layout'])
def check_component_edits_on_references():
    """check if there are component edits on references
    """

    # skip if this is a representation
    v = staging.get('version')
    if v and Representation.repr_separator in v.take_name:
        return

    import maya.cmds
    reference_query = maya.cmds.referenceQuery

    references_with_component_edits = []

    for ref in pm.listReferences(recursive=True):
        all_edits = reference_query(ref.refNode.name(), es=True)
        joined_edits = '\n'.join(all_edits)
        if '.pt[' in joined_edits or '.pnts[' in joined_edits:
            references_with_component_edits.append(ref)
            continue

    if len(references_with_component_edits):
        raise PublishError(
            'There are <b>component edits</b> on the following References:'
            '<br><br>%s<br><br>Please remove them!!!' %
            '<br>'.join(
                map(lambda x: x.refNode.name(),
                    references_with_component_edits[:MAX_NODE_DISPLAY])
            )
        )


@publisher(LOOK_DEV_TYPES)
def make_material_names_unique():
    """makes the material names unique
    """
    v = staging.get('version')

    if not v:
        from anima.env import mayaEnv
        mEnv = mayaEnv.Maya()
        v = mEnv.get_current_version()

    if not v:
        return

    asset_nice_name = v.naming_parents[0].nice_name

    non_referenced_materials = [
        mat
        for mat in pm.ls(mat=1, type=VALID_MATERIALS)
        if mat.referenceFile() is None
    ]

    for mat in non_referenced_materials:
        # material type name
        mat_type_name = mat.type()

        # find the first object using this material
        shading_engine = None
        outputs = mat.outputs(type='shadingEngine')
        if len(outputs):
            shading_engine = outputs[0]

        if not shading_engine:
            # skip this one
            continue

        objects_using_this_material = pm.sets(shading_engine, q=1)

        object_name = 'node'
        if len(objects_using_this_material):
            object_name = \
                objects_using_this_material[0].getParent().name().split(':')[-1]

        base_material_name = \
            '%s_%s_%s' % (asset_nice_name, object_name, mat_type_name)

        random_part = uuid.uuid4().hex[0:4]

        desired_material_name = \
            '%s_%s' % (base_material_name, random_part)

        desired_shading_engine_name = '%sSG' % desired_material_name

        if mat.name() not in ['lambert1', 'particleCloud1']:
            if not mat.name().startswith(base_material_name):
                mat.rename(desired_material_name)

            if not shading_engine.name().startswith(base_material_name):
                shading_engine.rename(desired_shading_engine_name)


@publisher(publisher_type=POST_PUBLISHER_TYPE)
def create_representations():
    """creates the representations of the scene
    """
    v = staging.get('version')

    from anima.env import mayaEnv
    if not v:
        m_env = mayaEnv.Maya()
        v = m_env.get_current_version()

    if not v:
        return

    if Representation.repr_separator in v.take_name:
        return

    from anima.env.mayaEnv import repr_tools
    gen = repr_tools.RepresentationGenerator(version=v)
    gen.generate_all()

    # re-open the original scene
    m_env = mayaEnv.Maya()
    current_version = m_env.get_current_version()

    if current_version != v:
        m_env.open(v, force=True)
