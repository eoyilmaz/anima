# -*- coding: utf-8 -*-
# Copyright (c) 2012-2017, Anima Istanbul
#
# This module is part of anima-tools and is released under the BSD 2
# License: http://www.opensource.org/licenses/BSD-2-Clause

import os
import datetime

import pymel.core as pm
import maya.cmds as mc
import tempfile

from anima.publish import (clear_publishers, publisher, staging,
                           POST_PUBLISHER_TYPE, ProgressControllerBase)
from anima.exc import PublishError
from anima.representation import Representation
from anima.utils import utc_to_local
from anima.env.mayaEnv import auxiliary

clear_publishers()

MAX_NODE_DISPLAY = 80

# TODO: this should be depending on to the project some projects still can
#       use mental ray
VALID_MATERIALS = {
    'maya': [
        # DEFAULT MAYA SHADERS
        'blinn',
        'displacementShader',
        'hairPhysicalShader',  # for Maya2017
        'lambert',
        'layeredShader',
        'oceanShader',
        'phong',
        'phongE',
        'rampShader',
        'surfaceShader',
    ],
    'arnold': [
        # ARNOLD
        'aiAmbientOcclusion',
        'aiHair',
        'aiRaySwitch',
        'aiShadowCatcher',
        'aiSkin',
        'aiSkinSss',
        'aiStandard',
        'aiUtility',
        'aiWireframe',
    ],
    'redshift': [
        # REDSHIFT
        'RedshiftAmbientOcclusion',
        'RedshiftArchitectural',
        'RedshiftAttributeLookup',
        'RedshiftBokeh',
        'RedshiftBumpBlender',
        'RedshiftBumpMap',
        'RedshiftCameraMap',
        'RedshiftCarPaint',
        'RedshiftCurvature',
        'RedshiftDisplacement',
        'RedshiftDisplacementBlender',
        'RedshiftDomeLight',
        'RedshiftEnvironment',
        'RedshiftFresnel',
        'RedshiftLightGobo',
        'RedshiftIESLight',
        'RedshiftIncandescent',
        'RedshiftLensDistortion',
        'RedshiftMaterial',
        'RedshiftMaterialBlender',
        'RedshiftNormalMap',
        'RedshiftHair',
        'RedshiftHairPosition',
        'RedshiftHairRandomColor',
        'RedshiftMatteShadowCatcher',
        'RedshiftPhotographicExposure',
        'RedshiftPhysicalLight',
        'RedshiftPhysicalSky',
        'RedshiftPhysicalSun',
        'RedshiftPortalLight',
        'RedshiftRaySwitch',
        'RedshiftRoundCorners',
        'RedshiftShaderSwitch',
        'RedshiftSkin',
        'RedshiftSprite',
        'RedshiftState',
        'RedshiftSubSurfaceScatter',
        'RedshiftUserDataColor',
        'RedshiftUserDataInteger',
        'RedshiftUserDataVector',
        'RedshiftUserDataScalar',
        'RedshiftVertexColor',
        'RedshiftVolume',
        'RedshiftVolumeScattering',
        'RedshiftWireFrame',
    ]
}



LOOK_DEV_TYPES = ['LookDev', 'Look Dev', 'LookDevelopment', 'Look Development']
REALTIME_RIG_TYPES = ['RealtimeRig', 'Realtime Rig']


# ********* #
# GENERIC   #
# ********* #
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
def delete_unknown_nodes(progress_controller=None):
    """Delete unknown nodes

    :param progress_controller: It is an object to inform the progress.
    """
    # delete the unknown nodes
    if progress_controller is None:
        progress_controller = ProgressControllerBase()

    progress_controller.minimum = 0
    progress_controller.value = 0

    unknown_nodes = mc.ls(type='unknown')
    progress_controller.maximum = len(unknown_nodes)

    # unlock each possible locked unknown nodes
    for node in enumerate(unknown_nodes):
        try:
            mc.lockNode(node, lock=False)
        except TypeError:
            pass
        progress_controller.increment()

    if unknown_nodes:
        mc.delete(unknown_nodes)
    progress_controller.complete()


@publisher
def check_node_names_with_bad_characters(progress_controller=None):
    """No bad characters in node names

    checks node names and ensures that there are no nodes with ord(c) > 127
    """
    if progress_controller is None:
        progress_controller = ProgressControllerBase()

    progress_controller.maximum = len(mc.ls())

    nodes_with_bad_name = []
    for node_name in mc.ls():
        if ':' not in node_name \
           and any(map(lambda x: x == '?' or ord(x) > 127, node_name)):
            nodes_with_bad_name.append(node_name)
        progress_controller.increment()

    progress_controller.complete()

    if len(nodes_with_bad_name) > 0:
        pm.select(nodes_with_bad_name)
        raise PublishError(
            'There are nodes with <b>unknown characters</b> in their names:'
            '<br><br>'
            '%s' %
            '<br>'.join(nodes_with_bad_name[:MAX_NODE_DISPLAY])
        )


@publisher
def delete_unused_shading_nodes(progress_controller=None):
    """Delete unused shading nodes
    """
    if progress_controller is None:
        progress_controller = ProgressControllerBase()

    progress_controller.maximum = 1
    num_of_items_deleted = pm.mel.eval('MLdeleteUnused')
    progress_controller.complete()

    if num_of_items_deleted:
        # do not raise any error just warn the user
        pm.warning('Deleted unused nodes during Publish operation!!')


@publisher
def check_representations(progress_controller=None):
    """Representations are matching

    checks if the referenced versions are all matching the representation
    type of the current version
    """
    if progress_controller is None:
        progress_controller = ProgressControllerBase()

    ref_reprs = []
    wrong_reprs = []

    v = staging.get('version')

    if v:
        r = Representation(version=v)
        current_repr = r.repr

        # For **Base** representation
        # allow any type of representation to be present in the scene
        if r.is_base():
            progress_controller.complete()
            return

        references = pm.listReferences()
        progress_controller.maximum = len(references)
        for ref in references:
            ref_repr = ref.repr
            if ref_repr is None:
                # skip this one this is not related to a Stalker Version
                progress_controller.increment()
                continue

            ref_reprs.append([ref, ref_repr])
            if ref_repr != current_repr:
                wrong_reprs.append(ref)
            progress_controller.increment()
    else:
        progress_controller.complete()
        return

    progress_controller.complete()
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
def cleanup_intermediate_objects(progress_controller=None):
    """Delete unused intermediate objects

    deletes any unused intermediate object in the current scene
    """
    if progress_controller is None:
        progress_controller = ProgressControllerBase()

    unused_intermediate_objects = []
    all_meshes = pm.ls(type='mesh')
    progress_controller.maximum = len(all_meshes)
    for node in all_meshes:
        if len(node.inputs()) == 0 \
           and len(node.outputs()) == 0 \
           and node.intermediateObject.get() \
           and node.referenceFile() is None:
            unused_intermediate_objects.append(node)
        progress_controller.increment()
    pm.delete(unused_intermediate_objects)
    progress_controller.complete()


@publisher
def convert_old_object_smoothing_to_renderer_time_smoothing(progress_controller=None):
    """Convert old smoothing to render time smoothing

    convert objects with old type display smoothing to renderer smoothing.

    Currently supports Arnold only.
    """
    if progress_controller is None:
        progress_controller = ProgressControllerBase()

    all_meshes = pm.ls(type='mesh')
    progress_controller.maximum = len(all_meshes)
    for node in all_meshes:
        if node.displaySmoothMesh.get() != 0:
            node.displaySmoothMesh.set(0)
            node.setAttr('aiSubdivType', 1)
            node.setAttr('aiSubdivIterations', node.smoothLevel.get())
        progress_controller.increment()
    progress_controller.complete()


@publisher
def check_local_references(progress_controller=None):
    """Legitimate references

    check if all of the references are legit
    """
    if progress_controller is None:
        progress_controller = ProgressControllerBase()

    all_references = pm.listReferences()
    progress_controller.maximum = len(all_references)
    for ref in all_references:
        progress_controller.increment()
        if ref.version is None:
            progress_controller.complete()
            raise PublishError(
                'Please remove any <b>non-legit</b> references!!!'
            )
    progress_controller.complete()


@publisher
def check_if_previous_version_references(progress_controller=None):
    """No previous version is referenced

    check if a previous version of the same task is referenced to the scene
    """
    if progress_controller is None:
        progress_controller = ProgressControllerBase()

    from anima.env.mayaEnv import Maya
    m = Maya()
    ver = m.get_current_version()

    if ver is None:
        progress_controller.complete()
        return

    same_version_references = []
    all_references = pm.listReferences()
    progress_controller.maximum = len(all_references)
    for ref in all_references:  # check only 1st level references
        ref_version = m.get_version_from_full_path(ref.path)
        if ref_version:
            if ref_version.task == ver.task \
               and ref_version.take_name == ver.take_name:
                same_version_references.append(ref)
        progress_controller.increment()

    progress_controller.complete()
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
def delete_empty_namespaces(progress_controller=None):
    """Delete empty namespaces

    checks and deletes empty namespaces
    """
    if progress_controller is None:
        progress_controller = ProgressControllerBase()

    # only allow namespaces with DAG objects in it and no child namespaces
    empty_namespaces = []

    all_namespaces = mc.namespaceInfo(
        recurse=True,
        listOnlyNamespaces=True,
        internal=False
    ) or []

    progress_controller.maximum = len(all_namespaces)
    for ns in all_namespaces:
        if ns not in ['UI', 'shared']:
            child_namespaces = mc.namespaceInfo(ns, listNamespace=True)
            if not child_namespaces and len(
                    mc.ls(mc.namespaceInfo(ns, listOnlyDependencyNodes=True),
                          dag=True, mat=True)) == 0:
                empty_namespaces.append(ns)
        progress_controller.increment()

    for ns in empty_namespaces:
        mc.namespace(rm=ns, mnr=True)
    progress_controller.complete()


@publisher
def check_only_published_versions_are_used(progress_controller=None):
    """References are all Published

    checks if only published versions are used in this scene
    """
    if progress_controller is None:
        progress_controller = ProgressControllerBase()

    non_published_versions = []
    all_references = pm.listReferences()
    progress_controller.maximum = len(all_references)
    for ref in all_references:
        v = ref.version
        if v and not v.is_published:
            non_published_versions.append(v)
        progress_controller.increment()

    progress_controller.complete()
    if len(non_published_versions):
        raise PublishError(
            'Please use only <b>published</b> versions for:<br><br>%s' %
            '<br>'.join(
                map(lambda x: x.nice_name,
                    non_published_versions[:MAX_NODE_DISPLAY])
            )
        )


@publisher
def disable_all_performance_options(progress_controller=None):
    """Disable performance degradation settings

    disables any performance degradation settings
    """
    if progress_controller is None:
        progress_controller = ProgressControllerBase()
    pm.performanceOptions(
        ds=0, dt=0, pbf=0, pbs=0, pc=0, pf=0, pl=0, pp=0, ps=0, pw=0
    )
    progress_controller.complete()


# ******* #
# MODEL   #
# ******* #
@publisher('model')
def check_no_references(progress_controller=None):
    """No references in the model scene

    there should be no references
    """
    if progress_controller is None:
        progress_controller = ProgressControllerBase()
    if len(pm.listReferences()):
        progress_controller.complete()
        raise PublishError(
            'There should be no <b>References</b> in a <b>Model</b> scene.'
        )
    progress_controller.complete()


@publisher('model')
def check_no_namespace(progress_controller=None):
    """No namespaces

    there should be no namespaces in a model file
    """
    if progress_controller is None:
        progress_controller = ProgressControllerBase()
    if len(pm.listNamespaces()):
        progress_controller.complete()
        raise PublishError(
            'There should be no <b>Namespaces</b> in a <b>Model</b> scene.'
        )
    progress_controller.complete()


@publisher('model')
def check_history(progress_controller=None):
    """No history

    there should be no history on the objects
    """
    if progress_controller is None:
        progress_controller = ProgressControllerBase()
    excluded_types = ['mesh', 'shadingEngine', 'groupId', 'RedshiftProxyMesh']
    nodes_with_history = []

    # delete any objectSets with name textureEditorIsolateSelectSet for Maya 2018
    pm.delete(pm.ls('textureEditorIsolateSelectSet*'))

    # get all shapes
    all_shapes = pm.ls(type='mesh')
    progress_controller.maximum = len(all_shapes)
    for node in all_shapes:
        history_nodes = []
        for h_node in node.listHistory(pdo=1, lv=1):
            if h_node.type() not in excluded_types:
                history_nodes.append(h_node)

        if len(history_nodes) > 0:
            nodes_with_history.append(node)
        progress_controller.increment()

    progress_controller.complete()
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
def check_if_default_shader(progress_controller=None):
    """Default shader used

    check if only default shader is assigned
    """
    if progress_controller is None:
        progress_controller = ProgressControllerBase()

    # skip if this is a representation
    v = staging.get('version')
    if v and Representation.repr_separator in v.take_name:
        progress_controller.complete()
        return

    if len(pm.ls(mat=1)) > 2:
        progress_controller.complete()
        raise PublishError(
            'Use only lambert1 as the shader!'
        )
    progress_controller.complete()


@publisher(['model'] + LOOK_DEV_TYPES)
def check_if_root_nodes_have_no_transformation(progress_controller=None):
    """Root nodes have no transformation

    checks if transform nodes directly under world have 0 transformations
    """
    if progress_controller is None:
        progress_controller = ProgressControllerBase()

    root_transform_nodes = auxiliary.get_root_nodes()
    progress_controller.maximum = len(root_transform_nodes)

    non_freezed_root_nodes = []
    for node in root_transform_nodes:
        t = node.t.get()
        r = node.r.get()
        s = node.s.get()
        if t.x != 0 or t.y != 0 or t.z != 0 \
           or r.x != 0 or r.y != 0 or r.z != 0 \
           or s.x != 1 or s.y != 1 or s.z != 1:
            non_freezed_root_nodes.append(node)
        progress_controller.increment()

    progress_controller.complete()
    if len(non_freezed_root_nodes):
        pm.select(non_freezed_root_nodes)
        raise PublishError(
            'Please freeze the following node transformations:\n\n%s' %
            '\n'.join(
                map(lambda x: x.name(),
                    non_freezed_root_nodes[:MAX_NODE_DISPLAY])
            )
        )


@publisher(['model', 'rig' + 'layout'] + LOOK_DEV_TYPES)
def check_if_only_one_root_node(progress_controller=None):
    """Only one root node

    checks if there is only one root node with no shape (group)
    """
    if progress_controller is None:
        progress_controller = ProgressControllerBase()

    root_transform_nodes = auxiliary.get_root_nodes()
    progress_controller.maximum = 4

    # remove any group nodes that contains a foster parent
    local_root_nodes = []
    for node in root_transform_nodes:
        if not isinstance(node, pm.nt.FosterParent):
            local_root_nodes.append(node)
    root_transform_nodes = local_root_nodes
    progress_controller.increment()

    # check of no root node
    if len(root_transform_nodes) == 0:
        progress_controller.complete()
        raise PublishError(
            'There should be at least one root node in the scene'
        )
    progress_controller.increment()

    # check more than one root node
    if len(root_transform_nodes) > 1:
        progress_controller.complete()
        raise PublishError(
            'There is more than one root node in the scene'
        )
    progress_controller.increment()

    # check shape
    if root_transform_nodes[0].getShape():
        progress_controller.increment()
        progress_controller.complete()
        raise PublishError(
            'Root node should be a Group node!'
            # 'Root node should not have a shape'
        )
    progress_controller.increment()
    progress_controller.complete()


@publisher('model')
def check_if_leaf_mesh_nodes_have_no_transformation(progress_controller=None):
    """Leaf mesh nodes has no transformation

    checks if all the Mesh transforms have 0 transformation, but it is
    allowed to move the mesh nodes in space with a parent group node.
    """
    if progress_controller is None:
        progress_controller = ProgressControllerBase()

    mesh_nodes_with_transform_children = []
    all_meshes = pm.ls(dag=1, type='mesh')
    progress_controller.maximum = len(all_meshes)
    for node in all_meshes:
        parent = node.getParent()
        tra_under_shape = pm.ls(
            parent.listRelatives(),
            type='transform'
        )
        if len(tra_under_shape):
            mesh_nodes_with_transform_children.append(parent)
        progress_controller.increment()

    progress_controller.complete()
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
def check_model_quality(progress_controller=None):
    """Models have good quality

    checks the quality of the model
    """
    if progress_controller is None:
        progress_controller = ProgressControllerBase()

    progress_controller.maximum = 2

    # skip if this is a representation
    v = staging.get('version')
    if v and Representation.repr_separator in v.take_name:
        progress_controller.complete()
        return
    progress_controller.increment()

    pm.select(None)
    pm.mel.eval(
        'polyCleanupArgList 3 { "1","2","0","0","1","0","0","0","0","1e-005",'
        '"0","0","0","0","0","2","1" };'
    )
    progress_controller.increment()

    progress_controller.complete()
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
def check_anim_layers(progress_controller=None):
    """No animation layers

    check if there are animation layers on the scene
    """
    if progress_controller is None:
        progress_controller = ProgressControllerBase()
    if len(pm.ls(type='animLayer')) > 0:
        progress_controller.complete()
        raise PublishError(
            'There should be no <b>Animation Layers</b> in the scene!!!'
        )
    progress_controller.complete()


@publisher('model')
def check_display_layer(progress_controller=None):
    """No display layers

    check if there are display layers
    """
    if progress_controller is None:
        progress_controller = ProgressControllerBase()
    if len(pm.ls(type='displayLayer')) > 1:
        progress_controller.complete()
        raise PublishError(
            'There should be no <b>Display Layers</b> in the scene!!!'
        )
    progress_controller.complete()


@publisher('model')
def check_extra_cameras(progress_controller=None):
    """No extra cameras

    checking if there are extra cameras
    """
    if progress_controller is None:
        progress_controller = ProgressControllerBase()
    if len(pm.ls(type='camera')) > 4:
        progress_controller.complete()
        raise PublishError('There should be no extra cameras in your scene!')
    progress_controller.complete()


@publisher('model')
def check_empty_groups(progress_controller=None):
    """No empty groups

    check if there are empty groups
    """
    if progress_controller is None:
        progress_controller = ProgressControllerBase()
    # skip if this is a representation
    v = staging.get('version')
    if v and Representation.repr_separator in v.take_name:
        progress_controller.complete()
        return

    empty_groups = []
    all_transforms = pm.ls(type='transform')
    progress_controller.maximum = len(all_transforms)
    for node in all_transforms:
        # skip any instancer nodes
        if isinstance(node, pm.nt.Instancer):
            continue

        if len(node.listRelatives(children=1)) == 0:
            empty_groups.append(node)
        progress_controller.increment()

    progress_controller.complete()
    if len(empty_groups):
        pm.select(empty_groups)
        raise PublishError(
            'There are <b>empty groups</b> in your scene, '
            'please remove them!!!'
        )


@publisher('model')
def check_empty_shapes(progress_controller=None):
    """No empty mesh nodes

    checks if there are empty mesh nodes
    """
    if progress_controller is None:
        progress_controller = ProgressControllerBase()

    empty_shape_nodes = []
    all_meshes = pm.ls(type='mesh')
    progress_controller.maximum = len(all_meshes)
    for node in all_meshes:
        if node.numVertices() == 0:
            empty_shape_nodes.append(node)
        progress_controller.increment()

    progress_controller.complete()
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
def check_uv_existence(progress_controller=None):
    """All objects have UVs

    check if there are uvs in all objects
    """
    if progress_controller is None:
        progress_controller = ProgressControllerBase()

    # skip if this is a representation
    v = staging.get('version')
    if v and Representation.repr_separator in v.take_name:
        progress_controller.complete()
        return

    all_meshes = pm.ls(type='mesh')
    progress_controller.maximum = len(all_meshes)
    nodes_with_no_uvs = []
    for node in all_meshes:
        if not node.getAttr('intermediateObject'):
            if not len(node.getUVs()[0]):
                nodes_with_no_uvs.append(node)
        progress_controller.increment()

    progress_controller.complete()
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
def check_out_of_space_uvs(progress_controller=None):
    """UV values are smaller than 10.0

    checks if there are uvs with u values that are bigger than 10.0
    """
    if progress_controller is None:
        progress_controller = ProgressControllerBase()

    # skip if this is a representation
    v = staging.get('version')
    if v and Representation.repr_separator in v.take_name:
        progress_controller.complete()
        return

    all_meshes = pm.ls(type='mesh')
    mesh_count = len(all_meshes)
    progress_controller.maximum = mesh_count
    nodes_with_out_of_space_uvs = []

    # from anima.ui.progress_dialog import ProgressDialogManager
    # from anima.env.mayaEnv import MayaMainProgressBarWrapper
    # wrp = MayaMainProgressBarWrapper()
    # pdm = ProgressDialogManager(dialog=wrp)

    # if not pm.general.about(batch=1) and mesh_count:
    #     pdm.use_ui = True

    # caller = pdm.register(mesh_count, 'check_out_of_space_uvs()')

    for node in all_meshes:
        u, v = node.getUVs()
        u = sorted(u)
        if u[0] < 0.0 or u[-1] > 10.0 or v[0] < 0.0:
            nodes_with_out_of_space_uvs.append(node)

        progress_controller.increment()

    progress_controller.complete()
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
def check_uv_border_crossing(progress_controller=None):
    """UV shells are not crossing uv borders

    checks if any of the uv shells are crossing uv borders
    """
    if progress_controller is None:
        progress_controller = ProgressControllerBase()

    # skip if this is a representation
    v = staging.get('version')
    if v and Representation.repr_separator in v.take_name:
        progress_controller.complete()
        return

    all_meshes = pm.ls(type='mesh')
    mesh_count = len(all_meshes)
    progress_controller.maximum = mesh_count
    nodes_with_uvs_crossing_borders = []

    # from anima.ui.progress_dialog import ProgressDialogManager
    # from anima.env.mayaEnv import MayaMainProgressBarWrapper
    # wrp = MayaMainProgressBarWrapper()
    # pdm = ProgressDialogManager(dialog=wrp)

    # if not pm.general.about(batch=1) and mesh_count:
    #     pdm.use_ui = True

    # caller = pdm.register(mesh_count, 'check_out_of_space_uvs()')

    for node in all_meshes:
        all_uvs = node.getUVs()
        # before doing anything get all the uvs and skip if non of them is
        # bigger than 1.0
        if not (any(map(lambda x: x > 1.0, all_uvs[0])) or
                any(map(lambda x: x > 1.0, all_uvs[1]))):
            # skip this mesh
            continue

        uv_shell_ids = node.getUvShellsIds()

        # prepare an empty dict of lists
        uvs_per_shell = {}
        for shell_id in range(uv_shell_ids[1]):
            uvs_per_shell[shell_id] = {
                'u': [],
                'v': []
            }

        for uv_id in range(len(uv_shell_ids[0])):
            u = all_uvs[0][uv_id]
            v = all_uvs[1][uv_id]
            shell_id = uv_shell_ids[0][uv_id]

            uvs_per_shell[shell_id]['u'].append(u)
            uvs_per_shell[shell_id]['v'].append(v)

        # now check all uvs per shell
        for shell_id in range(uv_shell_ids[1]):
            us = sorted(uvs_per_shell[shell_id]['u'])
            vs = sorted(uvs_per_shell[shell_id]['v'])

            # check first and last u and v values
            if int(us[0]) != int(us[-1]) or int(vs[0]) != int(vs[-1]):
                # they are not equal it is crossing spaces
                nodes_with_uvs_crossing_borders.append(node)
                break

        progress_controller.increment()

    progress_controller.complete()
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
def check_uvs(progress_controller=None):
    """All polygons have non-zero uv area

    checks uvs with no uv area

    The area of a 2d polygon calculation is based on the answer of Darius Bacon
    in http://stackoverflow.com/questions/451426/how-do-i-calculate-the-surface-area-of-a-2d-polygon
    """
    if progress_controller is None:
        progress_controller = ProgressControllerBase()

    # skip if this is a representation
    v = staging.get('version')
    if v and Representation.repr_separator in v.take_name:
        progress_controller.complete()
        return

    def area(p):
        return 0.5 * abs(sum(x0 * y1 - x1 * y0
                             for ((x0, y0), (x1, y1)) in segments(p)))

    def segments(p):
        return zip(p, p[1:] + [p[0]])

    all_meshes = pm.ls(type='mesh')
    mesh_count = len(all_meshes)
    progress_controller.maximum = mesh_count

    # from anima.ui.progress_dialog import ProgressDialogManager
    # from anima.env.mayaEnv import MayaMainProgressBarWrapper
    # wrp = MayaMainProgressBarWrapper()
    # pdm = ProgressDialogManager(dialog=wrp)
    #
    # if not pm.general.about(batch=1) and mesh_count:
    #     pdm.use_ui = True

    # caller = pdm.register(mesh_count, 'check_uvs()')

    meshes_with_zero_uv_area = []
    for node in all_meshes:
        all_uvs = node.getUVs()
        try:
            for i in range(node.numFaces()):
                uvs = []
                for j in range(node.numPolygonVertices(i)):
                    # uvs.append(node.getPolygonUV(i, j))
                    uv_id = node.getPolygonUVid(i, j)
                    uvs.append((all_uvs[0][uv_id], all_uvs[1][uv_id]))
                if area(uvs) == 0.0:
                    meshes_with_zero_uv_area.append(node)
                    break
        except RuntimeError:
            meshes_with_zero_uv_area.append(node)

        progress_controller.increment()

    progress_controller.complete()
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


# ****************** #
# LOOK DEVELOPMENT   #
# ****************** #


@publisher(LOOK_DEV_TYPES + ['model'])
def set_pixel_error(progress_controller=None):
    """Set aiSubdivPixelError to 0

    sets the pixel error on objects which have a linear subdiv
    """
    if progress_controller is None:
        progress_controller = ProgressControllerBase()

    all_meshes = pm.ls(type='mesh')
    progress_controller.maximum = len(all_meshes)
    for node in all_meshes:
        pixel_error = node.getAttr('aiSubdivPixelError')
        if pixel_error > 0:
            node.setAttr('aiSubdivPixelError', 0)
        progress_controller.increment()
    progress_controller.complete()


@publisher(LOOK_DEV_TYPES)
def disable_internal_reflections_in_aiStandard(progress_controller=None):
    """Disable internal reflections in aiStandard

    disable internal reflections in aiStandard
    """
    if progress_controller is None:
        progress_controller = ProgressControllerBase()

    all_ai_standard_materials = pm.ls(type='aiStandard')
    progress_controller.maximum = len(all_ai_standard_materials)
    for mat in all_ai_standard_materials:
        if mat.referenceFile() is None:
            mat.setAttr('enableInternalReflections', 0)
        progress_controller.increment()
    progress_controller.complete()


@publisher(LOOK_DEV_TYPES)
def check_all_renderer_specific_textures(progress_controller=None):
    """TX or RSTEXBIN textures exists

    checks if tx or rstexbin textures are created for all of the texture nodes
    in the current scene
    """
    if progress_controller is None:
        progress_controller = ProgressControllerBase()

    excluded_extensions = ['.ptex']

    renderer_texture_extensions = {
        'arnold': '.tx',
        'redshift': '.rstexbin'
    }
    default_renderer = 'arnold'

    # set the default extension to default_renderer
    current_renderer = pm.PyNode('defaultRenderGlobals').currentRenderer.get()
    current_renderer_texture_extension = \
        renderer_texture_extensions.get(
            current_renderer,
            renderer_texture_extensions[default_renderer]
        )

    v = staging.get('version')
    if v and Representation.repr_separator in v.take_name:
        progress_controller.complete()
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

    maya_version = int(pm.about(v=1))
    all_file_nodes = pm.ls(type='file')
    all_ai_image_nodes = pm.ls(type='aiImage')

    progress_controller.maximum = len(all_file_nodes) + len(all_ai_image_nodes)

    for node in all_file_nodes:
        if maya_version <= 2014:
            file_path = node.fileTextureName.get()
        else:
            file_path = node.computedFileTextureNamePattern.get()

        if os.path.splitext(file_path)[-1] not in excluded_extensions:
            add_path(file_path)
        progress_controller.increment()

    for node in all_ai_image_nodes:
        file_path = node.filename.get()
        if os.path.splitext(file_path)[-1] not in excluded_extensions:
            add_path(file_path)
        progress_controller.increment()

    import glob
    # TODO: Also check .rstexbin files for Redshift
    textures_with_no_tx = []

    # add more iterations to progress_controller
    progress_controller.maximum += len(texture_file_paths)
    for path in texture_file_paths:
        expanded_path = path\
            .replace('<udim>', '*')\
            .replace('<UDIM>', '*')\
            .replace('<U>', '*')\
            .replace('<V>', '*')
        textures_found_on_path = glob.glob(expanded_path)

        for orig_texture_path in textures_found_on_path:
            # now check if there is a .tx for this texture
            bin_texture_path = \
                '%s%s' % (
                    os.path.splitext(orig_texture_path)[0],
                    current_renderer_texture_extension
                )

            if not os.path.exists(bin_texture_path):
                textures_with_no_tx.append(orig_texture_path)
        progress_controller.increment()

    # add event more steps to progress_controller
    number_of_textures_to_process = len(textures_with_no_tx)
    progress_controller.maximum += number_of_textures_to_process
    if number_of_textures_to_process:
        if current_renderer == 'redshift':
            # Generate the textures if it is Redshift
            from anima.env.mayaEnv import ai2rs
            for texture_path in textures_with_no_tx:
                rstp = ai2rs.RedShiftTextureProcessor(texture_path)
                rstp.convert()
                progress_controller.increment()
        else:
            for path in textures_with_no_tx:
                print(path)
            progress_controller.complete()
            raise PublishError(
                'There are textures with no <b>%s</b> file!!!<br><br>'
                '%s' % (
                    current_renderer_texture_extension.upper(),
                    '<br>'.join(textures_with_no_tx)
                )
            )
    progress_controller.complete()


@publisher(LOOK_DEV_TYPES + ['layout'])
def check_lights(progress_controller=None):
    """No lights in the scene

    checks if there are lights in the scene
    """
    if progress_controller is None:
        progress_controller = ProgressControllerBase()
    progress_controller.maximum = 2

    all_lights = pm.ls(
        type=['light', 'aiAreaLight', 'aiSkyDomeLight', 'aiPhotometricLight']
    )
    progress_controller.increment()

    if len(all_lights):
        pm.select(all_lights)
        progress_controller.increment()
        progress_controller.complete()
        raise PublishError(
            'There are <b>Lights</b> in the current scene:<br><br>%s<br><br>'
            'Please delete them!!!' %
            '<br>'.join(map(lambda x: x.name(), all_lights))
        )
    progress_controller.complete()


@publisher(LOOK_DEV_TYPES)
def check_only_supported_materials_are_used(progress_controller=None):
    """Only supported materials are used

    check if only supported materials are used
    """
    if progress_controller is None:
        progress_controller = ProgressControllerBase()

    non_arnold_materials = []
    all_valid_materials = []
    for renderer in VALID_MATERIALS.keys():
        all_valid_materials.extend(VALID_MATERIALS[renderer])

    all_materials = pm.ls(mat=1)
    progress_controller.maximum = len(all_materials)
    for material in all_materials:
        if material.name() not in ['lambert1', 'particleCloud1']:
            if material.type() not in all_valid_materials:
                non_arnold_materials.append(material)
        progress_controller.increment()

    if len(non_arnold_materials):
        pm.select(non_arnold_materials)
        progress_controller.complete()
        raise PublishError(
            'There are non-Arnold materials in the scene:<br><br>%s<br><br>'
            'Please remove them!!!' %
            '<br>'.join(map(lambda x: x.name(), non_arnold_materials))
        )
    progress_controller.complete()


@publisher(LOOK_DEV_TYPES)
def check_multiple_connections_for_textures(progress_controller=None):
    """No multiple connections for textures (Arnold)

    check if textures are only used in one material (not liking it very much
    but it is breaking ASS files.
    """
    if progress_controller is None:
        progress_controller = ProgressControllerBase()

    # load necessary plugins
    plugins = ['matrixNodes', 'quatNodes']
    for plugin in plugins:
        if not pm.pluginInfo(plugin, q=1, l=1):
            pm.loadPlugin(plugin)

    v = staging.get('version')
    if not v:
        progress_controller.complete()
        return

    # check if the current renderer is Arnold
    current_renderer = pm.PyNode('defaultRenderGlobals').currentRenderer.get()
    if current_renderer != 'arnold':
        # skip it
        progress_controller.complete()
        return

    # skip if
    skip_types = ['character', 'animation', 'previs']
    for t in v.naming_parents:
        for st in skip_types:
            if t.type and t.type.name.lower().startswith(st):
                progress_controller.complete()
                return

    # get all the texture nodes
    from anima.env.mayaEnv import repr_tools
    reload(repr_tools)

    # try to find the material it is been used by walking up the connections
    nodes_with_multiple_materials = []

    types_to_ignore = [
        'hyperLayout', 'shadingEngine', 'materialInfo', 'time',
        'unitConversion', 'hyperView'
    ] + VALID_MATERIALS['redshift']

    # by type
    nodes_to_ignore = [node for node in pm.ls()
                       if node.type() in types_to_ignore]

    # by name
    nodes_to_ignore += pm.ls('lambert1', r=1)
    nodes_to_ignore += pm.ls('defaultShaderList*', r=1)
    nodes_to_ignore += pm.ls('defaultTextureList*', r=1)
    nodes_to_ignore += pm.ls('defaultRenderUtilityList*', r=1)
    nodes_to_ignore += pm.ls('hyperShadePrimaryNodeEditorSavedTabsInfo*', r=1)
    nodes_to_ignore += pm.ls('MayaNodeEditorSavedTabsInfo*', r=1)

    all_nodes = [node for node in pm.ls()
                 if node.type() in repr_tools.RENDER_RELATED_NODE_TYPES]
    for node in nodes_to_ignore:
        if node in all_nodes:
            all_nodes.remove(node)

    progress_controller.maximum = len(all_nodes)
    for node in all_nodes:
        materials_connected_to_this_node = \
            pm.ls(node.listHistory(future=True), mat=True)

        # remove any Redshift Materials from this list
        # create a temp list
        new_materials_connected_to_this_node = []
        for mat in materials_connected_to_this_node:
            if mat.type() not in VALID_MATERIALS['redshift']:
                new_materials_connected_to_this_node.append(mat)
        materials_connected_to_this_node = new_materials_connected_to_this_node

        # remove self from all_nodes
        if node in materials_connected_to_this_node:
            materials_connected_to_this_node.remove(node)

        if len(materials_connected_to_this_node) > 1:
            nodes_with_multiple_materials.append(node)
        else:
            connections_out_of_this_node = node.outputs()

            # [connections_out_of_this_node.remove(h)
            #  for h in nodes_to_ignore
            #  if h in connections_out_of_this_node]
            connections_out_of_this_node = \
                [h for h in connections_out_of_this_node
                 if h not in nodes_to_ignore]

            if len(set(connections_out_of_this_node)) > 1:
                nodes_with_multiple_materials.append(node)
        progress_controller.increment()

    # if we find more than one material add it to the list
    # raise a PublishError if we have an item in the list
    if len(nodes_with_multiple_materials) > 0:
        pm.select(nodes_with_multiple_materials)
        progress_controller.complete()
        raise PublishError(
            'Please update the scene so the following nodes are connected <br>'
            'to only <b>one material</b> (duplicate them):<br><br>%s<br><br>' %
            '<br>'.join(map(lambda x: x.name(), nodes_with_multiple_materials))
        )
    progress_controller.complete()


@publisher(LOOK_DEV_TYPES)
def check_objects_still_using_default_shader(progress_controller=None):
    """Default shader is not used

    check if there are objects still using the default shader
    """
    if progress_controller is None:
        progress_controller = ProgressControllerBase()
    progress_controller.maximum = 3

    # skip if this is a representation
    v = staging.get('version')
    if v and Representation.repr_separator in v.take_name:
        progress_controller.complete()
        return
    progress_controller.increment()

    objects_with_default_material = \
        mc.ls(
            mc.sets('initialShadingGroup', q=1),
            type=['mesh', 'nurbsSurface']
        )
    progress_controller.increment()
    if objects_with_default_material and len(objects_with_default_material):
        mc.select(objects_with_default_material)
        progress_controller.increment()
        progress_controller.complete()
        raise PublishError(
            'There are objects still using <b>initialShadingGroup</b><br><br>'
            '%s<br><br>Please assign a proper material to them' %
            '<br>'.join(
                objects_with_default_material[:MAX_NODE_DISPLAY]
            )
        )
    progress_controller.increment()
    progress_controller.complete()


@publisher(LOOK_DEV_TYPES + ['layout'])
def check_component_edits_on_references(progress_controller=None):
    """No component edits

    check if there are component edits on references
    """
    if progress_controller is None:
        progress_controller = ProgressControllerBase()

    # skip if this is a representation
    v = staging.get('version')
    if v and Representation.repr_separator in v.take_name:
        progress_controller.complete()
        return

    import maya.cmds
    reference_query = maya.cmds.referenceQuery

    references_with_component_edits = []

    # from anima.ui.progress_dialog import ProgressDialogManager
    # from anima.env.mayaEnv import MayaMainProgressBarWrapper
    # wrp = MayaMainProgressBarWrapper()
    # pdm = ProgressDialogManager(dialog=wrp)

    all_refs = pm.listReferences(recursive=True)
    ref_count = len(all_refs)

    # if not pm.general.about(batch=1) and ref_count:
    #     pdm.use_ui = True

    # caller = pdm.register(
    #     ref_count,
    #     'Checking component edits on %i reference nodes' % ref_count
    # )

    progress_controller.maximum = ref_count
    for ref in all_refs:
        all_edits = reference_query(ref.refNode.name(), es=True)
        # joined_edits = '\n'.join(all_edits)
        # if '.pt[' in joined_edits or '.pnts[' in joined_edits:
        #     references_with_component_edits.append(ref)
        for edit in all_edits:
            if '.pt[' in edit or '.pnts[' in edit:
                references_with_component_edits.append(ref)
                break
        progress_controller.increment()

    progress_controller.complete()
    if len(references_with_component_edits):
        raise PublishError(
            'There are <b>component edits</b> on the following References:'
            '<br><br>%s<br><br>Please remove them!!!' %
            '<br>'.join(
                map(lambda x: x.refNode.name(),
                    references_with_component_edits[:MAX_NODE_DISPLAY])
            )
        )


@publisher()
def check_legacy_render_layers(progress_controller=None):
    """No legacy render layer is used

    Checks if there is no legacy render layers in Maya 2017
    """
    if progress_controller is None:
        progress_controller = ProgressControllerBase()

    maya_version = pm.about(v=1)
    if int(maya_version) >= 2017:
        legacy_render_layers = []

        all_render_layers = pm.ls(type='renderLayer')
        default_render_layer = all_render_layers[0].defaultRenderLayer()
        all_render_layers.remove(default_render_layer)

        # render_setup_layers = pm.renderSetup(q=1, renderLayers=1)
        render_setup_layers = pm.ls('rs_*', type='renderLayer')

        progress_controller.maximum = len(all_render_layers)
        for render_layer in all_render_layers:
            if render_layer.name()[-18:] != 'defaultRenderLayer' \
               and render_layer not in render_setup_layers:
                legacy_render_layers.append(render_layer)
            progress_controller.increment()

        progress_controller.complete()
        if legacy_render_layers:
            print(legacy_render_layers)
            raise PublishError(
                'There are <b>LEGACY RENDER LAYERS<b> in your current '
                'scene<br>'
                '<br>'
                'Please remove them!'
            )
    else:
        progress_controller.complete()


@publisher('rig')
def check_root_node_name(progress_controller=None):
    """Root node name is correct

    In rig scenes, the name of the root node should not end with a number
    """
    if progress_controller is None:
        progress_controller = ProgressControllerBase()
    progress_controller.maximum = 2

    root_nodes = auxiliary.get_root_nodes()
    progress_controller.increment()

    root_node_name = root_nodes[0].name()
    progress_controller.increment()
    if root_node_name[-1].isdigit():
        progress_controller.complete()
        raise PublishError(
            "The name of the root node should not end with a number"
        )
    progress_controller.complete()


@publisher('rig')
def check_cacheable_attr(progress_controller=None):
    """Cacheable attribute exists

    checks if there is at least one cacheable attr
    """
    if progress_controller is None:
        progress_controller = ProgressControllerBase()

    root_nodes = auxiliary.get_root_nodes()
    progress_controller.maximum = len(root_nodes)

    root_node_has_cacheable_attr = []
    for root_node in root_nodes:
        root_node_has_cacheable_attr.append(
            root_node.hasAttr('cacheable')
            and root_node.getAttr('cacheable') != '' and
            root_node.getAttr('cacheable') is not None
        )
        progress_controller.increment()

    root_node_has_cacheable_attr = any(root_node_has_cacheable_attr)

    if not root_node_has_cacheable_attr:
        # check children nodes
        progress_controller.maximum += len(root_nodes)
        for root_node in root_nodes:
            child_has_cacheable = False
            for child_node in root_node.listRelatives(c=1):
                if child_node.hasAttr('cacheable') \
                   and child_node.getAttr('cacheable') != '' \
                   and child_node.getAttr('cacheable') is not None:
                    child_has_cacheable = True
                    break
            progress_controller.increment()

        progress_controller.complete()
        if not child_has_cacheable:
            raise PublishError(
                'Please add <b>cacheable</b> attribute and set it to a '
                '<b>proper name</b>!'
            )


@publisher('rig')
def cacheable_attr_to_lowercase(progress_controller=None):
    """Cacheable -> lower case

    Converts the cacheable attribute value to lowercase
    """
    if progress_controller is None:
        progress_controller = ProgressControllerBase()

    progress_controller.maximum = 2
    root_nodes = auxiliary.get_root_nodes()
    progress_controller.increment()

    if root_nodes[0].hasAttr('cacheable'):
        progress_controller.increment()
        root_nodes[0].setAttr(
            'cacheable',
            root_nodes[0].getAttr('cacheable').lower()
        )
        progress_controller.increment()
        progress_controller.complete()
    progress_controller.complete()


@publisher('animation')
def check_smartass_animator(progress_controller=None):
    """Animator doesn't try to be a smart-ass

    checks if the smartass animator is silently trying to create a new
    version for a completed animation scene
    """
    if progress_controller is None:
        progress_controller = ProgressControllerBase()

    progress_controller.maximum = 2

    from stalker.models import walk_hierarchy
    # check the status of this task
    v = staging.get('version')
    t = v.task
    progress_controller.increment()

    if t.status.code in ['CMPL']:
        # get the dependent tasks
        dependent_tasks = t.dependent_of
        progress_controller.maximum += len(dependent_tasks)

        # generate a white list for the resources
        # so anybody in the white list can publish it
        white_list_resources = []
        dependent_tasks_all_hierarchy = []

        for dt in dependent_tasks:
            for task in walk_hierarchy(dt, 'dependent_of'):
                white_list_resources.extend(task.resources)
                white_list_resources.extend(task.responsible)
                dependent_tasks_all_hierarchy.append(task)
            progress_controller.increment()

        white_list_resources = list(set(white_list_resources))

        progress_controller.maximum += 2
        # get the logged in user
        from stalker.db.session import DBSession
        from stalker import LocalSession
        with DBSession.no_autoflush:
            local_session = LocalSession()
            logged_in_user = local_session.logged_in_user
        progress_controller.increment()

        # if any of the dependent task has been started so the status is not
        # WFD or RTS in any of then
        #
        # also check if the logged in user is one of the resources of the
        # dependent tasks
        if any([t.status.code not in ['WFD', 'RTS', 'HREV', 'DREV']
                for t in dependent_tasks_all_hierarchy]) \
           and logged_in_user not in white_list_resources:
            progress_controller.increment()
            progress_controller.complete()
            # so the animator is trying to stab behind us
            # simply fuck him/her
            # by not allowing to publish the file

            raise PublishError(
                "You're not allowed to publish for this task:<br><br>"
                "Please <b>Request a REVISION</b>!!!!<br>"
            )
    progress_controller.increment()
    progress_controller.complete()


@publisher
def check_time_logs(progress_controller=None):
    """TimeLogs entered

    do not allow publishing if there is no time logs for the task, do that
    only for non WFD tasks
    """
    if progress_controller is None:
        progress_controller = ProgressControllerBase()

    # skip if this is a representation
    v = staging.get('version')
    if v and Representation.repr_separator in v.take_name:
        progress_controller.complete()
        return

    if v:
        task = v.task
        if task.schedule_model == 'effort' and task.resources:
            now = datetime.datetime.now()
            task_start = \
                task.computed_start if task.computed_start else task.start
            task_start = utc_to_local(task_start)
            if task.status.code != 'WFD' and task_start <= now:
                num_tlogs = len(task.time_logs)
                if num_tlogs == 0 or task.status.code == 'HREV':
                    window_title = 'Please create a TimeLog for this task!!!'
                    if num_tlogs == 0:
                        window_title = 'There is no TimeLog for this task, ' \
                                       'please create one!!!'
                    elif task.status.code == 'HREV':
                        window_title = 'Task status is HREV, ' \
                                       'please create a TimeLog!!!'

                    # skip this if Maya is not running in UI mode
                    if not pm.general.about(batch=1):
                        from anima.ui import time_log_dialog
                        time_log_created = False
                        i = 0
                        while not time_log_created:
                            i += 1
                            dialog = time_log_dialog.MainDialog(task=task)
                            dialog.setWindowTitle(window_title)
                            dialog.exec_()
                            time_log_created = dialog.timelog_created
                        progress_controller.complete()
                    else:
                        progress_controller.complete()
                        raise PublishError(
                            '<p>Please create a TimeLog before publishing '
                            'this version, for task.id: %s' % task.id
                        )
    progress_controller.complete()


@publisher(['animation', 'previs', 'shot previs'])
def check_sequencer(progress_controller=None):
    """Sequencer node exists

    checks if there is a sequencer node in the scene
    """
    if progress_controller is None:
        progress_controller = ProgressControllerBase()
    sequencers = pm.ls(type='sequencer')
    if len(sequencers) == 0:
        progress_controller.complete()
        raise PublishError('There is no Sequencer node in the scene!!!')
    progress_controller.complete()


@publisher(['animation', 'previs', 'shot previs'])
def check_shot_nodes(progress_controller=None):
    """Shot node exists

    checks if there is at least one shot node
    """
    if progress_controller is None:
        progress_controller = ProgressControllerBase()
    shot_nodes = pm.ls(type='shot')
    progress_controller.complete()
    if len(shot_nodes) == 0:
        raise PublishError('There is no <b>Shot</b> node in the scene')


@publisher(['animation', 'previs', 'shot previs'])
def check_sequence_name(progress_controller=None):
    """Sequence name is properly set

    checks if the sequence name attribute is properly set
    """
    if progress_controller is None:
        progress_controller = ProgressControllerBase()

    # do not consider referenced shot nodes
    shots = pm.ls(type='shot')
    progress_controller.maximum = len(shots)
    shot = None
    for s in shots:
        if s.referenceFile() is None:
            shot = s
            break
        progress_controller.increment()

    progress_controller.complete()
    sequencer = shot.outputs(type='sequencer')[0]
    sequence_name = sequencer.sequence_name.get()
    if sequence_name == '' or sequence_name is None:
        raise PublishError('Please enter a sequence name!!!')


@publisher(['animation', 'previs', 'shot previs'])
def check_sequence_name_format(progress_controller=None):
    """Sequence name format is ok

    checks if the sequence name format is correct
    """
    if progress_controller is None:
        progress_controller = ProgressControllerBase()

    # do not consider referenced shot nodes
    shots = pm.ls(type='shot')
    progress_controller.maximum = len(shots) + 5
    shot = None
    for s in shots:
        if s.referenceFile() is None:
            shot = s
            break
        progress_controller.increment()

    sequencer = shot.outputs(type='sequencer')[0]
    sequence_name = sequencer.sequence_name.get()
    progress_controller.increment()

    # SEQ001_003_TNGI
    # SEQ001_003A_TNGI
    # EP001_001

    parts = sequence_name.split('_')
    if len(parts) not in [2, 3]:
        progress_controller.complete()
        raise PublishError(
            'Sequence name format is not correct!!!<br>'
            '<br>'
            'It should be in the following format:<br>'
            '<br>'
            'SEQXXX_XXX_XXXX or EPXXX_XXX'
            '<br>'
            'ex: SEQ001_003_TNGI or EP001_001'
        )

    sequence_code = parts[0]
    scene_number = parts[1]
    if len(parts) > 2:
        scene_code = parts[2]
    else:
        scene_code = ""

    # sequence_code should start with SEQ
    if not (sequence_code.upper().startswith('SEQ') or sequence_code.upper().startswith('EP')):
        progress_controller.complete()
        raise PublishError(
            'Sequence name should start with "SEQ" or "EP"!!!<br>'
            '<br>'
            'Not:<br>'
            '%s' % sequence_code
        )
    progress_controller.increment()

    # scene number should start with a number
    import re
    if not re.match(r'^[\d]+', scene_number):
        progress_controller.complete()
        raise PublishError(
            'Scene number in sequence name should start with a number!!!<br>'
            '<br>'
            'Not:<br>'
            '%s' % scene_number
        )
    progress_controller.increment()

    # scene number should a 3 digit and an optional letter
    if not len(scene_number) in [3, 4, 5]:
        progress_controller.complete()
        raise PublishError(
            'Scene number in sequence name should be a number with 3 digits '
            'and an optional uppercase letter!!!<br>'
            '<br>'
            'Not:<br>'
            '%s' %
            scene_number
        )
    progress_controller.increment()

    # scene code should be all upper case letters
    if scene_code != '' and scene_code != scene_code.upper():
        progress_controller.complete()
        raise PublishError(
            'Scene code in sequence name should be all upper case letters!!!'
            '<br><br>'
            'Not:'
            '<br>'
            '%s' % scene_code
        )
    progress_controller.increment()
    progress_controller.complete()


@publisher(['animation', 'previs', 'shot previs'])
def check_shot_name_format(progress_controller=None):
    """Shot name format is ok

    check shot name format
    """
    if progress_controller is None:
        progress_controller = ProgressControllerBase()

    import re
    regex = r'^[\d]+$'
    shot_nodes = pm.ls(type='shot')
    shots_with_wrong_shot_name_format = []
    progress_controller.maximum = len(shot_nodes)
    for shot in shot_nodes:
        shot_name = shot.shotName.get()

        # check if all digits
        if not re.match(regex, shot_name):
            shots_with_wrong_shot_name_format.append(shot)
            progress_controller.increment()
            continue

        # check if 4 digits used only
        if len(shot_name) != 4:
            shots_with_wrong_shot_name_format.append(shot)
            progress_controller.increment()
            continue
        progress_controller.increment()

    progress_controller.complete()
    if len(shots_with_wrong_shot_name_format) > 0:
        raise PublishError(
            'The following shots have wrongly formatted shot names:<br>'
            '<br>'
            '%s' % (
                ', '.join(
                    map(
                        lambda x: x.shotName.get(),
                        shots_with_wrong_shot_name_format
                    )
                )
            )
        )


@publisher('previs')
def check_unique_shot_names(progress_controller=None):
    """Shot names are unique

    check if the shot names are unique
    """
    if progress_controller is None:
        progress_controller = ProgressControllerBase()

    shot_nodes = pm.ls(type='shot')
    progress_controller.maximum = len(shot_nodes)

    shot_names = []
    shots_with_non_unique_shot_names = []
    for shot in shot_nodes:
        shot_name = shot.shotName.get()
        if shot_name in shot_names:
            shots_with_non_unique_shot_names.append(shot)
        else:
            shot_names.append(shot_name)
        progress_controller.increment()

    progress_controller.complete()
    if len(shots_with_non_unique_shot_names) > 0:
        raise PublishError(
            'The following shots have non-unique shot names:<br>'
            '<br>'
            '%s' % (
                ', '.join(
                    map(
                        lambda x: x.shotName.get(),
                        shots_with_non_unique_shot_names
                    )
                )
            )
        )


@publisher(['animation', 'shot previs'])
def check_multiple_shot_nodes(progress_controller=None):
    """Single shot node in the scene

    checks if there are multiple shot nodes
    """
    if progress_controller is None:
        progress_controller = ProgressControllerBase()

    shot_nodes = pm.ls(type='shot')
    progress_controller.maximum = len(shot_nodes)

    local_shot_nodes = []
    for shot in shot_nodes:
        if shot.referenceFile() is None:
            local_shot_nodes.append(shot)
        progress_controller.increment()

    progress_controller.complete()
    if len(local_shot_nodes) > 1:
        raise PublishError(
            'There are multiple <b>Shot</b> nodes in the scene!'
        )


@publisher(['animation', 'previs', 'shot previs'])
def check_frame_range_selection(progress_controller=None):
    """No frame range selection in time slider

    checks if there is any range selected in the time slider

    Because it breaks shots to be playblasted as a whole the user should not
    have selected a range in the time slider
    """
    if progress_controller is None:
        progress_controller = ProgressControllerBase()

    progress_controller.maximum = 1
    start, end = pm.timeControl(
        pm.melGlobals['$gPlayBackSlider'],
        q=1,
        rangeArray=True
    )
    progress_controller.increment()
    progress_controller.complete()
    if end - start > 1:
        raise PublishError(
            'Please deselect the playback range in <b>TimeSlider</b>!!!'
        )


@publisher(['animation', 'shot previs'])
def set_frame_range(progress_controller=None):
    """Set frame range

    sets the frame range from the shot node
    """
    if progress_controller is None:
        progress_controller = ProgressControllerBase()
    progress_controller.maximum = 5

    shot_nodes = pm.ls(type='shot')
    progress_controller.increment()
    if len(shot_nodes) == 0:
        raise PublishError('No shot nodes in the scene!')
    progress_controller.increment()

    shot_node = shot_nodes[0]
    start_frame = shot_node.startFrame.get()
    end_frame = shot_node.endFrame.get()
    progress_controller.increment()

    handle_count = 1
    try:
        handle_count = shot_node.getAttr('handle')
    except AttributeError:
        pass
    progress_controller.increment()

    # set it in the playback
    pm.playbackOptions(
        ast=start_frame,
        aet=end_frame,
        min=start_frame-handle_count,
        max=end_frame+handle_count
    )
    progress_controller.increment()
    progress_controller.complete()


@publisher('layout')
def check_reference_types(progress_controller=None):
    """No "ActiveProps" in the scene

    It is not allowed to publish a layout that contains:

    Active Prop
    """
    if progress_controller is None:
        progress_controller = ProgressControllerBase()

    allowed_types = \
        ['bg-building', 'building', 'building part', 'layout', 'prop',
         'interior', 'exterior']
    wrong_refs = []
    all_references = pm.listReferences(recursive=True)
    progress_controller.maximum = len(all_references)
    for ref in all_references:
        v = ref.version
        if not v:
            progress_controller.increment()
            continue
        t = v.task
        t_parent = t.parent
        if not t_parent:
            progress_controller.increment()
            continue

        task_type = t_parent.type
        if not task_type or task_type.name.lower() not in allowed_types:
            wrong_refs.append(ref)
        progress_controller.increment()

    progress_controller.complete()
    if wrong_refs:
        ref_paths = '<br>'.join(map(lambda x: x.path, wrong_refs))
        raise PublishError(
            'There are <b>Wrong Reference Types</b> in the current scene!!!<br>'
            '<br>'
            '%s'
            '<br>'
            'Please <b>REMOVE</b> them!' % ref_paths
        )


# @publisher('animation')
# def freezing_last_frame(progress_controller=None):
#     """
#
#     checks if the last frame of the shot is freezing
#     """
#     # get cacheable nodes
#     # check the last 2 frames
#     # if the character is in move in the last 2 frames
#     # then there should be movement in the first frame after the current
#     # playback range
#     pass


@publisher(publisher_type=POST_PUBLISHER_TYPE)
def update_audit_info(progress_controller=None):
    """Update audit info

    updates the audit info of the version
    """
    if progress_controller is None:
        progress_controller = ProgressControllerBase()
    progress_controller.maximum = 2

    from stalker.db.session import DBSession
    from stalker import LocalSession
    with DBSession.no_autoflush:
        local_session = LocalSession()
        logged_in_user = local_session.logged_in_user
    progress_controller.increment()

    if logged_in_user:
        # update the version updated_by
        from anima.env import mayaEnv
        m_env = mayaEnv.Maya()
        v = m_env.get_current_version()
        if v:
            v.updated_by = logged_in_user

            from stalker.db.session import DBSession
            DBSession.commit()
    progress_controller.increment()
    progress_controller.complete()


@publisher(publisher_type=POST_PUBLISHER_TYPE)
def generate_thumbnail(progress_controller=None):
    """Generate thumbnails

    generates thumbnail for the current scene
    """
    # TODO: For now skip if this is Maya2017
    import pymel
    if pymel.versions.current() >= 201700:
        return

    # skip this if maya is running in batch mode
    if pm.general.about(batch=1):
        return

    from anima.env.mayaEnv import auxiliary
    reload(auxiliary)
    auxiliary.generate_thumbnail()


@publisher(
    LOOK_DEV_TYPES + ['layout', 'model', 'vegetation', 'scene assembly'],
    publisher_type=POST_PUBLISHER_TYPE
)
def create_representations(progress_controller=None):
    """Create representations

    creates the representations of the scene
    """
    if progress_controller is None:
        progress_controller = ProgressControllerBase()
    progress_controller.maximum = 6

    from anima.env import mayaEnv
    m_env = mayaEnv.Maya()
    v = m_env.get_current_version()
    progress_controller.increment()

    if not v:
        progress_controller.complete()
        return

    if Representation.repr_separator in v.take_name:
        progress_controller.complete()
        return
    progress_controller.increment()

    # skip if it is a Character
    skip_types = ['character', 'animation', 'previs', 'vehicle']
    for t in v.naming_parents:
        for st in skip_types:
            if t.type and t.type.name.lower().startswith(st):
                progress_controller.complete()
                return
    progress_controller.increment()

    from anima.env.mayaEnv import repr_tools
    gen = repr_tools.RepresentationGenerator(version=v)
    gen.generate_all()
    progress_controller.increment()

    # re-open the original scene
    m_env = mayaEnv.Maya()
    current_version = m_env.get_current_version()
    progress_controller.increment()

    if current_version != v:
        m_env.open(v, force=True, skip_update_check=True)
    progress_controller.increment()
    progress_controller.complete()


@publisher(['animation', 'shot previs'], publisher_type=POST_PUBLISHER_TYPE)
def update_shot_range(progress_controller=None):
    """Update shot range

    update shot range
    """
    if progress_controller is None:
        progress_controller = ProgressControllerBase()
    progress_controller.maximum = 2

    from stalker import Shot
    from stalker.db.session import DBSession
    from anima.env import mayaEnv
    m = mayaEnv.Maya()
    v = m.get_current_version()
    progress_controller.increment()

    shot = v.task.parent
    if shot and isinstance(shot, Shot):
        shot_node = pm.ls(type='shot')[0]
        start_frame = shot_node.startFrame.get()
        end_frame = shot_node.endFrame.get()
        shot.cut_in = int(start_frame)
        shot.cut_out = int(end_frame)
        DBSession.commit()
    progress_controller.increment()
    progress_controller.complete()


@publisher(['animation', 'pose', 'mocap'], publisher_type=POST_PUBLISHER_TYPE)
def cache_animations(progress_controller=None):
    """Cache animations
    """
    if progress_controller is None:
        progress_controller = ProgressControllerBase()
    progress_controller.maximum = 1

    reload(auxiliary)
    auxiliary.export_alembic_from_cache_node(handles=1)
    progress_controller.increment()
    progress_controller.complete()


@publisher(['animation', 'previs', 'shot previs'], publisher_type=POST_PUBLISHER_TYPE)
def generate_playblast(progress_controller=None):
    """Generate playblast

    generates a playblast for the current scene
    """
    if progress_controller is None:
        progress_controller = ProgressControllerBase()

    import anima
    from anima import utils
    reload(anima)
    reload(utils)
    reload(auxiliary)

    # before doing a playblast set all shot handles to 48
    shots = pm.ls(type='shot')
    progress_controller.maximum = len(shots) + 2
    for shot in shots:
        if shot.hasAttr('handle'):
            shot.handle.set(0)
        progress_controller.increment()

    sp = auxiliary.Playblaster()
    sp.batch_mode = True
    video_files = sp.playblast()
    progress_controller.increment()
    sp.upload_outputs(sp.version, video_files)
    progress_controller.increment()
    progress_controller.complete()

    # revert the handles to 0
    # for shot in pm.ls(type='shot'):
    #     if shot.hasAttr('handle'):
    #         shot.handle.set(0)


@publisher(['animation', 'shot previs'], publisher_type=POST_PUBLISHER_TYPE)
def export_edl_and_xml(progress_controller=None):
    """Export EDL and XML

    exports edl and xml representations of animation scenes
    """
    if progress_controller is None:
        progress_controller = ProgressControllerBase()
    progress_controller.maximum = 11

    from anima.env.mayaEnv import Maya
    m = Maya()
    current_version = m.get_current_version()
    progress_controller.increment()

    if not current_version:
        progress_controller.complete()
        return

    # get sequenceManager1
    sm = pm.PyNode('sequenceManager1')
    seqs = sm.sequences.get()
    if not len(seqs):
        progress_controller.complete()
        return
    progress_controller.increment()

    seq1 = seqs[0]

    # EDL
    edl_path = tempfile.gettempdir()
    edl_file_name = '%s_v%03i.edl' % (
        current_version.nice_name,
        current_version.version_number
    )
    edl_file_full_path = os.path.join(edl_path, edl_file_name)
    progress_controller.increment()

    # XML
    xml_path = tempfile.gettempdir()
    xml_file_name = '%s_v%03i.xml' % (
        current_version.nice_name,
        current_version.version_number
    )
    xml_file_full_path = os.path.join(xml_path, xml_file_name)
    progress_controller.increment()

    # convert to MXF
    # from anima.ui.progress_dialog import ProgressDialogManager
    # from anima.env.mayaEnv import MayaMainProgressBarWrapper
    # wrp = MayaMainProgressBarWrapper()
    # pdm = ProgressDialogManager(dialog=wrp)

    # shots = seq1.shots.get()
    shots = pm.ls(type='shot')
    shot_count = len(shots)
    progress_controller.maximum += shot_count

    # before doing a playblast set all shot handles to 0
    for shot in pm.ls(type='shot'):
        if shot.hasAttr('handle'):
            shot.handle.set(0)

    # caller = pdm.register(shot_count, title='Converting To MXF')

    # update shot outputs to the correct place first
    # there should be only one shot in the current animation scene
    # if there is more than one shot, the other publisher will already warn the
    # user so the code path will not reach to this point

    # we also should already have a video output created by another publisher
    playblast_file = None
    for output in current_version.outputs:
        extension = os.path.splitext(output.full_path)[-1]
        if extension in ['.mov', '.avi', '.mp4']:
            playblast_file = output
            break

    if not playblast_file:
        return
    shot = shots[0]
    shot.output.set(playblast_file.full_path)

    for i in seq1.metafuze():
        progress_controller.increment()

    # create EDL and XML files
    from stalker.db.session import DBSession
    from anima import utils
    mm = utils.MediaManager()
    progress_controller.increment()

    # EDL
    l = sm.to_edl()
    with open(edl_file_full_path, 'w') as f:
        f.write(l.to_string())
    progress_controller.increment()

    with open(edl_file_full_path, 'r') as f:
        link = mm.upload_version_output(current_version, f, edl_file_name)
        DBSession.add(link)
    progress_controller.increment()

    # XML
    x = sm.to_xml()
    with open(xml_file_full_path, 'w') as f:
        f.write(x)
    progress_controller.increment()

    with open(xml_file_full_path, 'r') as f:
        link = mm.upload_version_output(current_version, f, xml_file_name)
        DBSession.add(link)
    progress_controller.increment()

    # add the link to database
    DBSession.commit()
    progress_controller.increment()

    # revert the handles to 0
    for shot in pm.ls(type='shot'):
        if shot.hasAttr('handle'):
            shot.handle.set(0)
    progress_controller.increment()
    progress_controller.complete()


@publisher(['animation', 'shot previs'], publisher_type=POST_PUBLISHER_TYPE)
def export_camera(progress_controller=None):
    """Export camera and shot node

    exports camera and the related shot node
    """
    if progress_controller is None:
        progress_controller = ProgressControllerBase()
    progress_controller.maximum = 7

    from stalker import Task, Version
    from anima.env import mayaEnv
    m = mayaEnv.Maya()
    v = m.get_current_version()
    progress_controller.increment()

    # do not consider referenced shot nodes
    shots = pm.ls(type='shot')
    shot = None
    for s in shots:
        if s.referenceFile() is None:
            shot = s
            break
    progress_controller.increment()

    try:
        sequencer = pm.ls(shot.message.connections(), type='sequencer')[0]
    except IndexError:
        sequencer = None
    progress_controller.increment()

    camera = None
    if shot:
        camera = shot.currentCamera.get()
    progress_controller.increment()

    from stalker.db.session import DBSession
    with DBSession.no_autoflush:
        camera_task = \
            Task.query\
                .filter(Task.parent == v.task.parent)\
                .filter(Task.name == 'Camera').first()
    progress_controller.increment()

    if camera_task:
        from stalker import LocalSession
        with DBSession.no_autoflush:
            local_session = LocalSession()
            logged_in_user = local_session.logged_in_user

        cam_v = Version(
            task=camera_task,
            description='Exported from %s task on Publish' % v.task.name
        )
        cam_v.update_paths()
        cam_v.extension = '.ma'
        cam_v.is_published = True
        cam_v.created_by = cam_v.updated_by = logged_in_user
        progress_controller.increment()

        pm.select([shot, camera, sequencer])

        m.allow_publish_on_export = True
        m.export_as(cam_v)
        progress_controller.increment()

    progress_controller.complete()


@publisher(REALTIME_RIG_TYPES, publisher_type=POST_PUBLISHER_TYPE)
def export_fbx(progress_controll=None):
    """Export FBX

    Exports FBX of this rig
    """
    # select all the root nodes
    # root_transform_nodes = auxiliary.get_root_nodes()
    # pm.select(root_transform_nodes)

    # create the output_fbx_path
    from anima.env import mayaEnv
    m = mayaEnv.Maya()
    v = m.get_current_version()

    # get the asset name
    asset = v.task.parent

    output_fbx_path = \
        '%s/Outputs/FBX/%s.fbx' % (v.absolute_path, asset.nice_name)

    # Create the folder first
    try:
        os.makedirs(
            os.path.dirname(output_fbx_path)
        )
    except OSError:
        # dir exists
        pass

    # do export
    pm.exportAll(
        output_fbx_path,
        force=1,
        options="v=0;mo=1;lo=0",
        typ="FBX export",
        pr=True,
        # es=True
    )
