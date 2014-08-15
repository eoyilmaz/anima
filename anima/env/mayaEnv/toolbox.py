# -*- coding: utf-8 -*-
# Copyright (c) 2012-2014, Anima Istanbul
#
# This module is part of anima-tools and is released under the BSD 2
# License: http://www.opensource.org/licenses/BSD-2-Clause
from anima.env.mayaEnv.camera_tools import cam_to_chan
from anima.utils import do_db_setup

__version__ = "0.1.9"

import pymel.core as pm
import maya.mel as mel

from anima.env.mayaEnv import auxiliary, camera_tools


__last_commands__ = []  # list of dictionaries


def repeater(index):
    """repeats the last command with the given index
    """
    global __last_commands__
    try:
        call_data = __last_commands__[index]
        return call_data[0](*call_data[1], **call_data[2])
    except IndexError:
        return None


def repeat_last(call_data):
    """own implementation of pm.repeatLast
    """
    global __last_commands__
    index = len(__last_commands__)

    callable_ = call_data[0]
    args = call_data[1]
    kwargs = call_data[2]

    command = \
        'print \\"\\";python(\\\"from anima.env.mayaEnv.toolbox import repeater; repeater(%s);\\\");' % index

    repeat_last_command = 'repeatLast -ac "%(command)s" -acl "%(label)s";' % {
        'command': command,
        'label': callable_.__name__
    }
    print repeat_last_command

    pm.mel.eval(repeat_last_command)
    __last_commands__.append(call_data)

    # also call the callable
    call_data[0](*call_data[1], **call_data[2])


def RepeatedCallback(callable_, *args, **kwargs):
    """Adds the given callable to the last commands list and adds a caller to
    the pm.repeatLast
    """
    return pm.Callback(
        repeat_last, [callable_, args, kwargs]
    )


class Color(object):
    """a simple color class
    """
    colors = [
        (1.000, 0.500, 0.666),
        (1.000, 0.833, 0.500),
        (0.666, 1.000, 0.500),
        (0.500, 1.000, 0.833),
        (0.500, 0.666, 1.000),
        (0.833, 0.500, 1.000)
    ]

    def __init__(self, index=0):
        self.index = index
        self.max_colors = len(self.colors)

    def change(self):
        """updates the index to the next one
        """
        self.index = int((self.index + 1) % self.max_colors)

    def reset(self):
        """resets the color index
        """
        self.index = 0

    @property
    def color(self):
        """returns the current color values
        """
        return self.colors[self.index]


def UI():
    #window setup
    width = 260
    height = 650
    row_spacing = 3

    color = Color()

    if pm.dockControl("toolbox_dockControl", q=True, ex=True):
        pm.deleteUI("toolbox_dockControl")

    if pm.window("toolbox_window", q=True, ex=True):
        pm.deleteUI("toolbox_window", wnd=True)

    toolbox_window = pm.window(
        'toolbox_window',
        wh=(width, height),
        title="Anima ToolBox v%s" % __version__
    )

    #the layout that holds the tabs
    main_formLayout = pm.formLayout(
        'main_formLayout', nd=100, parent=toolbox_window
    )

    main_tabLayout = pm.tabLayout(
        'main_tabLayout', scr=True, cr=True, parent=main_formLayout)

    #attach the main_tabLayout to main_formLayout
    pm.formLayout(
        main_formLayout, edit=True,
        attachForm=[
            (main_tabLayout, "top", 0),
            (main_tabLayout, "bottom", 0),
            (main_tabLayout, "left", 0),
            (main_tabLayout, "right", 0)
        ]
    )

    with main_tabLayout:
        # ----- GENERAL ------
        general_columnLayout = pm.columnLayout(
            'general_columnLayout',
            adj=True,
            cal="center",
            rs=row_spacing
        )
        with general_columnLayout:
            color.change()
            pm.button(
                'deleteAllSound_button', l="delete all sound",
                c=RepeatedCallback(General.delete_all_sound),
                ann="delete all sound",
                bgc=color.color
            )

            pm.button(
                'displayHandlesOfSelectedObjects_button',
                l="toggle handles of selected objects",
                c=RepeatedCallback(
                    General.toggle_attributes,
                    "displayHandle"
                ),
                ann="select objects to toggle handle",
                bgc=color.color
            )

            color.change()
            pm.button(
                'selectionManager_button',
                l="Selection Manager",
                c=RepeatedCallback(General.selection_manager),
                ann="Selection Manager",
                bgc=color.color
            )

            color.change()
            pm.button(
                'referenceSelectedObjects_button',
                l="reference selected objects",
                c=RepeatedCallback(
                    General.reference_selected_objects
                ),
                ann="sets objects display override to reference",
                bgc=color.color
            )

            pm.button(
                'dereferenceSelectedObjects_button',
                l="de-reference selected objects",
                c=RepeatedCallback(
                    General.dereference_selected_objects
                ),
                ann="sets objects display override to reference",
                bgc=color.color
            )

            color.change()
            pm.button(
                'oyDeReferencer_button', l="dereferencer",
                c=RepeatedCallback(General.dereferencer),
                ann="sets all objects display override  to normal",
                bgc=color.color
            )

            color.change()
            pm.button(
                'removeColonFromNames_button',
                l="remove colon(:) from node names",
                c=RepeatedCallback(General.remove_colon_from_names),
                ann="removes the colon (:) character from all "
                    "selected object names",
                bgc=color.color
            )

            pm.button(
                'removePastedFromNames_button',
                l="remove \"pasted_\" from node names",
                c=RepeatedCallback(General.remove_pasted),
                ann="removes the \"passed__\" from all selected "
                    "object names",
                bgc=color.color
            )

            color.change()
            pm.button(
                'togglePolyMeshes_button',
                l="toggle polymesh visibility",
                c=RepeatedCallback(General.toggle_poly_meshes),
                ann="toggles the polymesh display in the active model "
                    "panel",
                bgc=color.color
            )

            color.change()
            pm.button(
                'selectSetMembers_button',
                l="select set members",
                c=RepeatedCallback(General.select_set_members),
                ann="selects the selected set members in correct "
                    "order",
                bgc=color.color
            )

            color.change()
            pm.button(
                'duplicate_selected_reference_button',
                l='Duplicate Selected Reference',
                c=RepeatedCallback(General.duplicate_selected_reference),
                ann='Duplicates the selected reference',
                bgc=color.color
            )

            color.change()
            pm.button(
                'open_selected_reference_button',
                l='Open Selected Reference in New Maya',
                c=RepeatedCallback(General.open_reference_in_new_maya),
                ann='Opens the selected reference in new Maya '
                    'instance',
                bgc=color.color
            )

            color.change()
            pm.button(
                'publish_model_as_look_dev_button',
                l='Model -> LookDev',
                c=RepeatedCallback(General.publish_model_as_look_dev),
                ann='References the current Model scene to the LookDev scene '
                    'of the same task, creates the LookDev scene if '
                    'necessary, also reopens the current model scene.',
                bgc=color.color
            )

            color.change()
            pm.button(
                'delete_unused_intermediate_shapes_button',
                l='Delete Unused Intermediate Shape Nodes',
                c=RepeatedCallback(General.delete_unused_intermediate_shapes),
                ann='Deletes unused (no connection) intermediate shape nodes',
                bgc=color.color
            )

            color.change()
            pm.button(
                'fix_reference_namespace_button',
                l='Fix Reference Namespace',
                c=RepeatedCallback(General.fix_reference_namespace),
                ann='Fixes old style reference namespaces with new one, '
                    'creates new versions if necessary.',
                bgc=color.color
            )

            color.change()
            pm.button(
                'fix_reference_paths_button',
                l='Fix Reference Paths',
                c=RepeatedCallback(General.fix_reference_paths),
                ann='Fixes reference paths deeply, so they will use'
                    '$REPO env var.',
                bgc=color.color
            )

            pm.button(
                'archive_button',
                l='Archive Current Scene',
                c=RepeatedCallback(General.archive_current_scene),
                ann='Creates a ZIP file containing the current scene and its'
                    'references in a flat Maya default project folder '
                    'structure',
                bgc=color.color
            )

        # ----- MODELING ------
        modeling_columnLayout = pm.columnLayout(
            'modeling_columnLayout',
            adj=True, cal="center", rs=row_spacing)
        with modeling_columnLayout:
            color.reset()
            pm.button('toggleFaceNormalDisplay_button',
                      l="toggle face normal display",
                      c=RepeatedCallback(
                          pm.runtime.ToggleFaceNormalDisplay),
                      ann="toggles face normal display",
                      bgc=color.color)
            pm.button('reverseNormals_button', l="reverse normals",
                      c=RepeatedCallback(Modeling.reverse_normals),
                      ann="reverse normals",
                      bgc=color.color)
            pm.button('fixNormals_button', l="fix normals",
                      c=RepeatedCallback(Modeling.fix_normals),
                      ann="applies setToFace then conform and then "
                          "soften edge to all selected objects",
                      bgc=color.color)

            color.change()
            pm.button('oyUVTools_button', l="oyUVTools",
                      c=RepeatedCallback(Modeling.uvTools),
                      ann="opens oyUVTools",
                      bgc=color.color)

            color.change()
            pm.button(
                'oyHierarchyInstancer_button',
                l="hierarchy_instancer on selected",
                c=RepeatedCallback(Modeling.hierarchy_instancer),
                ann="hierarchy_instancer on selected",
                bgc=color.color
            )

            color.change()
            pm.button(
                'oyRelaxVerts_button',
                l="relax_vertices",
                c=RepeatedCallback(Modeling.relax_vertices),
                ann="opens relax_vertices",
                bgc=color.color
            )

        # ----- RIGGING ------
        rigging_columnLayout = pm.columnLayout(
            'rigging_columnLayout',
            adj=True, cal="center",
            rs=row_spacing
        )
        with rigging_columnLayout:
            color.reset()
            pm.button(
                'oyCreateJointOnCurve_button',
                l="oyCreateJointOnCurve",
                c=RepeatedCallback(mel.eval, 'oyCreateJointOnCurve'),
                ann="opens oyCreateJointOnCurve",
                bgc=color.color
            )
            pm.button(
                'oyIKFKSetup_button',
                l="oyIKFKSetup",
                c=RepeatedCallback(mel.eval, 'oyIKFKSetup'),
                ann="opens oyIKFKSetup",
                bgc=color.color
            )
            pm.button(
                'oySpineSetupSetup_button',
                l="oySpineSetupSetup",
                c=RepeatedCallback(mel.eval, 'oyStretchySpineSetup'),
                ann="opens oySpineSetupSetup",
                bgc=color.color
            )
            pm.button(
                'setupStretchySplineIKCurve_button',
                l="setup stretchy splineIK curve",
                c=RepeatedCallback(Rigging.setup_stretchy_spline_IKCurve),
                ann="connects necessary nodes to calculate arcLength "
                    "change in percent",
                bgc=color.color
            )
            pm.button(
                'selectJointsDeformingTheObject_button',
                l="select joints deforming the object",
                c=RepeatedCallback(Rigging.select_joints_deforming_object),
                ann="select joints that deform the object",
                bgc=color.color
            )

            color.change()
            pm.button(
                'oyCreateAxialCorrectionGroup_button',
                l="create axialCorrectionGroups",
                c=RepeatedCallback(Rigging.axial_correction_group),
                ann="creates a group node above the selected objects "
                    "to zero-out the transformations",
                bgc=color.color
            )
            pm.button(
                'createAxialCorrectionGroupForClusters_button',
                l="create axialCorrectionGroup for clusters",
                c=RepeatedCallback(
                    Rigging.create_axial_correction_group_for_clusters
                ),
                ann="create Axial Correction Group For Clusters",
                bgc=color.color
            )

            color.change()
            pm.button(
                'setClustersToAbsolute_button',
                l="set selected clusters to absolute",
                c=RepeatedCallback(Rigging.set_clusters_relative_state, 0),
                ann="set Clusters to Absolute",
                bgc=color.color
            )
            pm.button(
                'setClustersToRelative_button',
                l="set selected clusters to relative",
                c=RepeatedCallback(
                    Rigging.set_clusters_relative_state, 1
                ),
                ann="set Clusters to Relative",
                bgc=color.color
            )

            color.change()
            pm.button(
                'addControllerShape_button',
                l="add controller shape",
                c=RepeatedCallback(Rigging.add_controller_shape),
                ann="add the shape in the selected joint",
                bgc=color.color
            )
            pm.button(
                'replaceControllerShape_button',
                l="replace controller shape",
                c=RepeatedCallback(Rigging.replace_controller_shape),
                ann="replaces the shape in the selected joint",
                bgc=color.color
            )

            color.change()
            pm.button('rivet_button', l="create rivet",
                      c=RepeatedCallback(mel.eval, 'rivet'),
                      ann="create rivet",
                      bgc=color.color)
            pm.button('oyAutoRivet_button', l="auto rivet",
                      c=RepeatedCallback(mel.eval, 'oyAutoRivet'),
                      ann="auto rivet",
                      bgc=color.color)
            pm.button(
                'oyAutoRivetFollicle_button',
                l="auto rivet (Follicle)",
                c=RepeatedCallback(auxiliary.auto_rivet),
                ann="creates a rivet setup by using hair follicles",
                bgc=color.color
            )
            pm.button('create_hair_from_curves_button',
                      l="Create Hair From Curves",
                      c=RepeatedCallback(auxiliary.hair_from_curves),
                      ann="creates hair from curves",
                      bgc=color.color)

            color.change()
            pm.button('artPaintSkinWeightsTool_button',
                      l="paint weights tool",
                      c=RepeatedCallback(mel.eval, 'ArtPaintSkinWeightsTool'),
                      ann="paint weights tool",
                      bgc=color.color)
            pm.button('oySkinTools_button', l="oySkinTools",
                      c=RepeatedCallback(mel.eval, 'oySkinTools'),
                      ann="skin tools",
                      bgc=color.color)
            pm.button('oyFixBoundJoint_button', l="fix_bound_joint",
                      c=RepeatedCallback(Rigging.fix_bound_joint),
                      ann="fix_bound_joint",
                      bgc=color.color)
            pm.button('toggleLocalRotationAxes_button',
                      l="toggle local rotation axes",
                      c=RepeatedCallback(General.toggle_attributes,
                                    "displayLocalAxis"),
                      ann="toggle local rotation axes",
                      bgc=color.color)
            pm.button('seroBlendController_button',
                      l="seroBlendController",
                      c=RepeatedCallback(mel.eval, 'seroBlendController'),
                      ann="seroBlendController",
                      bgc=color.color)
            pm.button('align_to_pole_vector_button',
                      l="Align To Pole Vector",
                      c=RepeatedCallback(auxiliary.align_to_pole_vector),
                      ann="align to pole vector",
                      bgc=color.color)

            color.change()
            pm.button('oyResetCharSet_button', l="oyResetCharSet",
                      c=RepeatedCallback(mel.eval, 'oyResetCharSet'),
                      ann="reset char set",
                      bgc=color.color)
            pm.button('export_blend_connections_button',
                      l="Export blend connections",
                      c=RepeatedCallback(auxiliary.export_blend_connections),
                      ann="export blend connections",
                      bgc=color.color)

            color.change()
            pm.button('createFollicles_button', l="create follicles",
                      c=RepeatedCallback(Rigging.create_follicles),
                      ann="create follicles",
                      bgc=color.color)

            color.change()
            pm.button('oyResetTweaks_button', l="reset tweaks",
                      c=RepeatedCallback(Rigging.reset_tweaks),
                      ann="reset tweaks",
                      bgc=color.color)

        # ----- RENDER ------
        render_columnLayout = pm.columnLayout(
            'render_columnLayout',
            adj=True,
            cal="center",
            rs=row_spacing
        )
        with render_columnLayout:
            color.reset()
            pm.button(
                'open_node_in_browser_button',
                l="Open node in browser",
                c=RepeatedCallback(Render.open_node_in_browser),
                ann="Open node in browser",
                bgc=color.color
            )

            pm.separator()
            color.change()
            apply_to_hierarchy_checkBox = pm.checkBox(
                'apply_to_hierarchy_checkBox',
                l="Apply to Hierarchy",
                value=True,
                bgc=color.color
            )

            hierarchyCheckBox = pm.checkBox(
                apply_to_hierarchy_checkBox,
                q=True,
                v=True
            )

            with pm.rowLayout(nc=3, rat=(1, "both", 0), adj=1):
                pm.text(
                    'castsShadows_text',
                    l="castShadows",
                    bgc=color.color
                )
                pm.button(
                    'set_castsShadows_ON_button',
                    l="ON",
                    c=RepeatedCallback(
                        Render.set_shape_attribute,
                        "castsShadows",
                        1,
                        hierarchyCheckBox
                    ),
                    bgc=(0, 1, 0)
                )
                pm.button(
                    'set_castsShadows_OFF_button',
                    l="OFF",
                    c=RepeatedCallback(
                        Render.set_shape_attribute,
                        "castsShadows",
                        0,
                        hierarchyCheckBox
                    ),
                    bgc=(1, 0, 0)
                )

            with pm.rowLayout(nc=3, rat=(1, "both", 0), adj=1):
                pm.text(
                    'receiveShadows_text',
                    l="receive shadows",
                    bgc=color.color
                )
                pm.button(
                    'set_receiveShadows_ON_button',
                    l="ON",
                    c=RepeatedCallback(
                        Render.set_shape_attribute,
                        "receiveShadows",
                        1,
                        hierarchyCheckBox
                    ),
                    bgc=(0, 1, 0)
                )
                pm.button(
                    'set_receiveShadows_OFF_button',
                    l="OFF",
                    c=RepeatedCallback(
                        Render.set_shape_attribute,
                        "receiveShadows",
                        0,
                        hierarchyCheckBox
                    ),
                    bgc=(1, 0, 0)
                )

            with pm.rowLayout(nc=3, rat=(1, "both", 0), adj=1):
                pm.text(
                    'motion_blur_text',
                    l="motion blur",
                    bgc=color.color
                )
                pm.button(
                    'set_motion_blur_ON_button',
                    l="ON",
                    c=RepeatedCallback(
                        Render.set_shape_attribute,
                        "motionBlur", 1, hierarchyCheckBox
                    ),
                    bgc=(0, 1, 0)
                )
                pm.button(
                    'set_motion_blur_OFF_button',
                    l="OFF",
                    c=RepeatedCallback(
                        Render.set_shape_attribute,
                        "motionBlur", 0, hierarchyCheckBox
                    ),
                    bgc=(1, 0, 0)
                )

            with pm.rowLayout(nc=3, rat=(1, "both", 0), adj=1):
                pm.text('primaryVisibility_text',
                        l="primary visibility",
                        bgc=color.color)
                pm.button('set_primaryVisibility_ON_button', l="ON",
                          c=RepeatedCallback(Render.set_shape_attribute,
                                        "primaryVisibility", 1,
                                        hierarchyCheckBox),
                          bgc=(0, 1, 0))
                pm.button('set_primaryVisibility_OFF_button', l="OFF",
                          c=RepeatedCallback(Render.set_shape_attribute,
                                        "primaryVisibility", 0,
                                        hierarchyCheckBox),
                          bgc=(1, 0, 0))

            with pm.rowLayout(nc=3, rat=(1, "both", 0), adj=1):
                pm.text('visibleInReflections_text',
                        l="visible in Reflection",
                        bgc=color.color)
                pm.button('set_visibleInReflections_ON_button', l="ON",
                          c=RepeatedCallback(Render.set_shape_attribute,
                                        "visibleInReflections", 1,
                                        hierarchyCheckBox),
                          bgc=(0, 1, 0))
                pm.button('set_visibleInReflections_OFF_button',
                          l="OFF",
                          c=RepeatedCallback(Render.set_shape_attribute,
                                        "visibleInReflections", 0,
                                        hierarchyCheckBox),
                          bgc=(1, 0, 0))

            with pm.rowLayout(nc=3, rat=(1, "both", 0), adj=1):
                pm.text('visibleInRefractions_text',
                        l="visible in Refractions",
                        bgc=color.color)
                pm.button('set_visibleInRefractions_ON_button', l="ON",
                          c=RepeatedCallback(Render.set_shape_attribute,
                                        "visibleInRefractions", 1,
                                        hierarchyCheckBox),
                          bgc=(0, 1, 0))
                pm.button('set_visibleInRefractions_OFF_button',
                          l="OFF",
                          c=RepeatedCallback(Render.set_shape_attribute,
                                        "visibleInRefractions", 0,
                                        hierarchyCheckBox),
                          bgc=(1, 0, 0))

            pm.separator()
            color.change()

            with  pm.rowLayout(nc=3, rat=(1, "both", 0), adj=1):
                pm.text('renderThumbnailUpdate_text',
                        l="renderThumbnailUpdate",
                        bgc=color.color)
                pm.button('set_renderThumbnailUpdate_ON_button',
                          l="ON",
                          c=RepeatedCallback(pm.renderThumbnailUpdate, 1),
                          bgc=(0, 1, 0))
                pm.button('set_renderThumbnailUpdate_OFF_button',
                          l="OFF",
                          c=RepeatedCallback(pm.renderThumbnailUpdate, 0),
                          bgc=(1, 0, 0))

            color.change()
            pm.button('replaceShadersWithLast_button',
                      l="replace shaders with last",
                      c=RepeatedCallback(Render.replace_shaders_with_last),
                      ann="replace shaders with last",
                      bgc=color.color)

            color.change()
            pm.button('createTextureRefObject_button',
                      l="create texture ref. object",
                      c=RepeatedCallback(Render.create_texture_ref_object),
                      ann="create texture ref. object",
                      bgc=color.color)

            color.change()

            pm.button(
                'CameraFilmOffsetTool_button',
                l="Camera Film Offset Tool",
                c=RepeatedCallback(
                    camera_tools.camera_film_offset_tool
                ),
                ann="Camera Film Offset Tool",
                bgc=color.color
            )
            pm.button(
                'CameraFocusPlaneTool_button',
                l="Camera Focus Plane Tool",
                c=RepeatedCallback(
                    camera_tools.camera_focus_plane_tool
                ),
                ann="Camera Film Offset Tool",
                bgc=color.color
            )
            pm.button('oyTracker2Null_button', l="oyTracker2Null",
                      c=RepeatedCallback(mel.eval, 'oyTracker2Null'),
                      ann="Tracker2Null",
                      bgc=color.color)

            color.change()
            pm.button('reloadFileTextures_button',
                      l="reload file textures",
                      c=RepeatedCallback(Render.reload_file_textures),
                      ann="reload file textures",
                      bgc=color.color)

            color.change()
            pm.button('oyTransferShaders_button',
                      l="transfer_shaders",
                      c=RepeatedCallback(Render.transfer_shaders),
                      ann="TransferShaders",
                      bgc=color.color)

            color.change()
            pm.button('fitPlacementToUV_button',
                      l="fit placement to UV",
                      c=RepeatedCallback(Render.fit_placement_to_UV),
                      ann="fit placement to UV",
                      bgc=color.color)

            color.change()
            enable_matte_row_layout = pm.rowLayout(nc=6, adj=1)
            with enable_matte_row_layout:
                pm.text(
                    l='Enable Arnold Matte',
                )
                pm.button(
                    l='Default',
                    c=RepeatedCallback(Render.enable_matte, 0),
                    ann='Enables Arnold Matte on selected objects with <b>No Color</b>',
                    bgc=color.color
                )
                pm.button(
                    l='R',
                    c=RepeatedCallback(Render.enable_matte, 1),
                    ann='Enables Arnold Matte on selected objects with <b>Red</b>',
                    bgc=color.color
                )
                pm.button(
                    l='G',
                    c=RepeatedCallback(Render.enable_matte, 2),
                    ann='Enables Arnold Matte on selected objects with <b>Green</b>',
                    bgc=color.color
                )
                pm.button(
                    l='B',
                    c=RepeatedCallback(Render.enable_matte, 3),
                    ann='Enables Arnold Matte on selected objects with <b>Blue</b>',
                    bgc=color.color
                )
                pm.button(
                    l='A',
                    c=RepeatedCallback(Render.enable_matte, 4),
                    ann='Enables Arnold Matte on selected objects with <b>Alpha</b>',
                    bgc=color.color
                )

            color.change()
            pm.button(
                'enable_subdiv_on_selected_objects_button',
                l='Enable Arnold Subdiv',
                c=RepeatedCallback(Render.enable_subdiv),
                ann='Enables Arnold Subdiv (catclark 2) on selected objects',
                bgc=color.color
            )

            color.change()
            pm.text(l='===== ASS Tools =====')
            pm.button(
                'to_ass_button',
                l='To ASS',
                c=RepeatedCallback(Render.selected_to_ass),
                ann='Convert selected to ASS take',
                bgc=color.color
            )

            pm.button(
                'to_original_button',
                l='To Original',
                c=RepeatedCallback(Render.selected_to_original),
                ann='Convert selected to Original take',
                bgc=color.color
            )


        # ----- ANIMATION ------
        animation_columnLayout = pm.columnLayout(
            'animation_columnLayout',
            adj=True,
            cal="center",
            rs=row_spacing
        )
        with animation_columnLayout:
            color.reset()

            color.change()
            from anima.env.mayaEnv import picker

            pm.text(l='===== Object Picker =====')

            pm.button('picker_setParent_button',
                      l="Set Parent",
                      c=RepeatedCallback(picker.set_parent),
                      ann="Set Parent",
                      bgc=color.color)
            pm.button('picker_releaseObject_button',
                      l="Release",
                      c=RepeatedCallback(picker.release_object),
                      ann="Release Object",
                      bgc=color.color)
            pm.button('picker_editKeyframes_button',
                      l="Edit Keyframes",
                      c=RepeatedCallback(picker.edit_keyframes),
                      ann="Edit Keyframes",
                      bgc=color.color)
            pm.button('picker_fixJump_button',
                      l="Fix Jump",
                      c=RepeatedCallback(picker.fix_jump),
                      ann="Fix Jump",
                      bgc=color.color)
            pm.button('picker_explodeSetup_button',
                      l="Explode",
                      c=RepeatedCallback(picker.explode_setup),
                      ann="Explode Setup",
                      bgc=color.color)

            color.change()
            from anima.env.mayaEnv import pivot_switcher

            pm.text(l='===== Pivot Switcher =====')
            pm.button('oyPivotSwitcher_setupPivot_button',
                      l="Setup",
                      c=RepeatedCallback(pivot_switcher.setup_pivot),
                      ann="Setup Pivot",
                      bgc=color.color)
            pm.button('oyPivotSwitcher_switchPivot_button',
                      l="Switch",
                      c=RepeatedCallback(pivot_switcher.switch_pivot),
                      ann="Switch Pivot",
                      bgc=color.color)
            pm.button('oyPivotSwitcher_togglePivot_button',
                      l="Toggle",
                      c=RepeatedCallback(pivot_switcher.toggle_pivot),
                      ann="Toggle Pivot",
                      bgc=color.color)

            color.change()
            pm.text(l='===== Vertigo =====')
            pm.button('oyVertigo_setupLookAt_button',
                      l="Setup -> Look At",
                      c=RepeatedCallback(Animation.vertigo_setup_look_at),
                      ann="Setup Look At",
                      bgc=color.color)
            pm.button('oyVertigo_setupVertigo_button',
                      l="Setup -> Vertigo",
                      c=RepeatedCallback(Animation.vertigo_setup_vertigo),
                      ann="Setup Vertigo",
                      bgc=color.color)
            pm.button('oyVertigo_delete_button',
                      l="Delete",
                      c=RepeatedCallback(Animation.vertigo_delete),
                      ann="Delete",
                      bgc=color.color)

            color.change()
            pm.text(l='===== Alembic Tools =====')
            rowLayout = pm.rowLayout(nc=2, adj=1, bgc=color.color)
            with rowLayout:
                pm.button(
                    'abc_from_selected_button',
                    l='From Selected',
                    c=RepeatedCallback(Animation.create_alembic_command),
                    ann='Creates Alembic Cache from selected nodes',
                    bgc=color.color
                )
                from_top_node_checkBox = pm.checkBox(
                    'from_top_node_checkBox',
                    l="Top Node",
                    value=True,
                    bgc=color.color
                )

            pm.button(
                'abc_from_source_to_target_button',
                l='Source -> Target',
                c=RepeatedCallback(Animation.copy_alembic_data),
                ann='Copy Alembic Data from Source to Target by the matching '
                    'node names',
                bgc=color.color
            )

            color.change()
            rowLayout = pm.rowLayout(nc=3, adj=3, bgc=color.color)
            with rowLayout:
                start = int(pm.playbackOptions(q=1, minTime=1))
                end = int(pm.playbackOptions(q=1, maxTime=1))
                startButtonField = pm.textField(
                    text=start, w=50, bgc=color.color, ann='start frame'
                )
                endButtonField = pm.textField(
                    text=end, w=50, bgc=color.color, ann='end frame'
                )
                pm.button(ann="Exports maya camera to nuke",
                          l="cam2chan", w=70,
                          c=RepeatedCallback(Animation.cam_2_chan,
                                             startButtonField,
                                             endButtonField),
                          bgc=color.color)

            color.change()
            smooth_component_anim = pm.textFieldButtonGrp(
                'oySmoothComponentAnimation_button',
                bl="Smooth Component Animation",
                adj=2, tx=1, cw=(1, 40),
                ann="select components to smooth",
                bgc=color.color
            )
            pm.textFieldButtonGrp(
                smooth_component_anim,
                e=1,
                bc=RepeatedCallback(
                    Animation.oySmoothComponentAnimation,
                    smooth_component_anim
                )
            )

            color.change()
            pm.button(
                'bake_component_animation_button',
                l='Bake component animation to Locator',
                c=RepeatedCallback(Animation.bake_component_animation),
                ann='Creates a locator at the center of selected components '
                    'and moves it with the components along the current '
                    'frame range',
                bgc=color.color
            )

        # Obsolete
        obsolete_columnLayout = pm.columnLayout(
            'obsolete_columnLayout',
            adj=True,
            cal="center",
            ann="Obsolete",
            rs=row_spacing
        )
        with obsolete_columnLayout:
            color.reset()
            pm.button('addMiLabel_button', l="add miLabel to selected",
                      c=RepeatedCallback(Render.add_miLabel),
                      ann="add miLabel to selected",
                      bgc=color.color)

            color.change()
            pm.button('connectFacingRatioToVCoord_button',
                      l="connect facingRatio to vCoord",
                      c=RepeatedCallback(
                          Render.connect_facingRatio_to_vCoord),
                      ann="connect facingRatio to vCoord",
                      bgc=color.color)
            color.change()

            with pm.rowLayout(nc=3, rat=(1, "both", 0), adj=1):
                pm.text('miFinalGatherCast_text',
                        l="miFinalGatherCast",
                        bgc=color.color)
                pm.button('set_miFinalGatherCast_ON_button', l="ON",
                          c=RepeatedCallback(Render.set_shape_attribute,
                                        "miFinalGatherCast", 1,
                                        hierarchyCheckBox),
                          bgc=(0, 1, 0))
                pm.button('set_miFinalGatherCast_OFF_button', l="OFF",
                          c=RepeatedCallback(Render.set_shape_attribute,
                                        "miFinalGatherCast", 0,
                                        hierarchyCheckBox),
                          bgc=(1, 0, 0))

            with pm.rowLayout(nc=3, rat=(1, "both", 0), adj=1):
                pm.text('miFinalGatherReceive_text',
                        l="miFinalGatherReceive",
                        bgc=color.color)
                pm.button('set_miFinalGatherReceive_ON_button', l="ON",
                          c=RepeatedCallback(Render.set_shape_attribute,
                                        "miFinalGatherReceive", 1,
                                        hierarchyCheckBox),
                          bgc=(0, 1, 0))
                pm.button('set_miFinalGatherReceive_OFF_button',
                          l="OFF",
                          c=RepeatedCallback(Render.set_shape_attribute,
                                        "miFinalGatherReceive", 0,
                                        hierarchyCheckBox),
                          bgc=(1, 0, 0))

            with pm.rowLayout(nc=3, rat=(1, "both", 0), adj=1):
                pm.text('miFinalGatherHide_text',
                        l="miFinalGatherHide",
                        bgc=color.color)
                pm.button('set_miFinalGatherHide_ON_button', l="ON",
                          c=RepeatedCallback(Render.set_finalGatherHide, 1),
                          bgc=(0, 1, 0))
                pm.button('set_miFinalGatherHide_OFF_button', l="OFF",
                          c=RepeatedCallback(Render.set_finalGatherHide, 0),
                          bgc=(1, 0, 0))

            color.change()
            pm.button('convertToMRTexture_button',
                      l="use mib_texture_filter_lookup",
                      c=RepeatedCallback(
                          Render.use_mib_texture_filter_lookup),
                      ann=(
                          "adds an mib_texture_filter_lookup node in \n" +
                          "between the file nodes and their outputs, to \n" +
                          "get a sharper look output from the texture file"),
                      bgc=color.color)
            pm.button('convertToLinear_button',
                      l="convert to Linear texture",
                      c=RepeatedCallback(Render.convert_to_linear),
                      ann="convert to Linear texture",
                      bgc=color.color)
            pm.button('useImageSequence_button',
                      l="use image sequence for \nmentalrayTexture",
                      c=RepeatedCallback(Render.use_image_sequence),
                      ann="use image sequence for \nmentalrayTexture",
                      bgc=color.color)

            color.change()
            pm.button('oyAddToSelectedContainer_button',
                      l="add to selected container",
                      c=RepeatedCallback(Render.add_to_selected_container),
                      ann="add to selected container",
                      bgc=color.color)
            pm.button('oyRemoveFromContainer_button',
                      l="remove from selected container",
                      c=RepeatedCallback(Render.remove_from_container),
                      ann="remove from selected container",
                      bgc=color.color)

            color.change()
            pm.button('oySmedgeRenderSlicer_button',
                      l="oySmedgeRenderSlicer",
                      c=RepeatedCallback(mel.eval, 'oySmedgeRenderSlicer'),
                      ann="SmedgeRenderSlicer",
                      bgc=color.color)

            color.change()
            pm.button(
                'exponentialSmooth_button',
                l="exponential smooth",
                c=RepeatedCallback(Modeling.polySmoothFace, 0),
                ann="applies exponential smooth to selected objects",
                bgc=color.color
            )
            pm.button(
                'linearSmooth_button',
                l="linear smooth",
                c=RepeatedCallback(Modeling.polySmoothFace, 1),
                ann="applies linear smooth to selected objects",
                bgc=color.color
            )
            pm.button(
                'deActivateSmooth_button',
                l="deActivate smooth",
                c=RepeatedCallback(Modeling.activate_deActivate_smooth, 1),
                ann="deActivates all polySmoothFace nodes in the "
                    "scene",
                bgc=color.color
            )
            pm.button(
                'activateSmooth_button',
                l="activate smooth",
                c=RepeatedCallback(Modeling.activate_deActivate_smooth, 0),
                ann="activates all deActivated polySmoothFace nodes "
                    "in the scene",
                bgc=color.color
            )
            pm.button(
                'deleteSmooth_button',
                l="delete smooth",
                c=RepeatedCallback(Modeling.delete_smooth),
                ann="deletes all the polySmoothFace nodes from the "
                    "scene",
                bgc=color.color
            )
            pm.button(
                'deleteSmoothOnSelected_button',
                l="delete smooth on selected",
                c=RepeatedCallback(Modeling.delete_smooth_on_selected),
                ann="deletes selected polySmoothFace nodes from scene",
                bgc=color.color
            )

    pm.tabLayout(
        main_tabLayout,
        edit=True,
        tabLabel=[
            (general_columnLayout, "Gen"),
            (modeling_columnLayout, "Mod"),
            (rigging_columnLayout, "Rig"),
            (render_columnLayout, "Ren"),
            (animation_columnLayout, "Ani"),
            (obsolete_columnLayout, "Obs")
        ]
    )

    # pm.showWindow(toolbox_window)
    # pm.window(toolbox_window, edit=True, w=width)

    #print toolbox_window.name()

    dock_control = pm.dockControl(
        "toolbox_dockControl",
        l='toolbox v%s' % __version__,
        content=toolbox_window,
        area="left",
        allowedArea=["left", "right"],
        width=width
    )


class General(object):
    """General tools
    """

    @classmethod
    def toggle_attributes(cls, attribute_name):
        """toggles the given attribute for the given list of objects
        """
        objs = pm.ls(sl=1)
        new_list = []

        attribute_count = 0
        set_to_state = 1

        for obj in objs:
            if obj.hasAttr(attribute_name):
                if obj.getAttr(attribute_name):
                    attribute_count += 1
                new_list.append(obj)

        obj_count = len(new_list)

        if attribute_count == obj_count:
            set_to_state = 0

        for obj in new_list:
            obj.setAttr(attribute_name, set_to_state)

    @classmethod
    def dereferencer(cls):
        """calls dereferencer
        """
        selection = pm.ls()
        for item in selection:
            if pm.attributeQuery('overrideEnabled', node=item, exists=True):
                if not item.overrideEnabled.get(l=True):
                    connections = pm.listConnections(item, d=True)
                    in_layer = 0
                    for i in range(0, len(connections)):
                        if connections[i].type() == "displayLayer":
                            in_layer = 1
                            break
                    if not in_layer:
                        if not item.overrideDisplayType.get(l=True):
                            item.overrideDisplayType.set(0)
    @classmethod
    def selection_manager(cls):
        from anima.env.mayaEnv import selection_manager
        selection_manager.UI()

    @classmethod
    def reference_selected_objects(cls):
        selection = pm.ls(sl=True)
        for item in selection:
            if item.overrideEnabled.get(se=True):
                item.overrideEnabled.set(1)
            if item.overrideDisplayType.get(se=True):
                item.overrideDisplayType.set(2)

        pm.select(cl=True)

    @classmethod
    def dereference_selected_objects(cls):
        selection = pm.ls(sl=True)
        for item in selection:
            if item.overrideEnabled.get(se=True):
                item.overrideEnabled.set(0)
            if item.overrideDisplayType.get(se=True):
                item.overrideDisplayType.set(0)

        pm.select(cl=True)

    @classmethod
    def remove_colon_from_names(cls):
        selection = pm.ls(sl=1)
        for item in selection:
            temp = item.split(':')[-1]
            pm.rename(item, temp)
            pm.ls(sl=1)

    @classmethod
    def remove_pasted(cls):
        """removes the string 'pasted__' from selected object names
        """
        rmv_str = "pasted__"
        [
            obj.rename(obj.name()[len(rmv_str):])
            for obj in pm.ls(sl=1)
            if obj.name().startswith(rmv_str)
        ]

    @classmethod
    def toggle_poly_meshes(cls):
        """toggles mesh selection in the current panel
        """
        panel_in_focus = pm.getPanel(wf=True)
        panel_type = pm.getPanel(typeOf=panel_in_focus)
        if panel_type == "modelPanel":
            poly_vis_state = pm.modelEditor(
                panel_in_focus,
                q=True,
                polymeshes=True
            )
            pm.modelEditor(
                panel_in_focus,
                e=True,
                polymeshes=(not poly_vis_state)
            )

    @classmethod
    def select_set_members(cls):
        selection = pm.ls(sl=1)
        if not selection:
            pass
        else:
            pm.select(selection[0].inputs())

    @classmethod
    def get_no_parent_transform(cls, ref):
        """returns the top most parent node in the given subReferences

        :param ref: pm.nt.FileReference instance
        """
        all_referenced_nodes = ref.nodes()
        for node in all_referenced_nodes:
            if isinstance(node, pm.nt.Transform):
                #print '%s has parent' % node.name()
                parent_node = node.getParent()
                if parent_node not in all_referenced_nodes:
                    return node

        # check sub references
        sub_refs = pm.listReferences(ref)
        for sub_ref in sub_refs:
            no_parent_transform = cls.get_no_parent_transform(sub_ref)
            if no_parent_transform:
                return no_parent_transform

    @classmethod
    def duplicate_selected_reference(cls):
        """duplicates the selected referenced object as reference
        """
        from pymel.core import xform

        ref = pm.ls(sl=1)[0].referenceFile()
        # get the highest parent ref
        if ref.parent():
            while ref.parent():
                ref = ref.parent()

        namespace = ref.namespace
        dup_ref = pm.createReference(
            ref.path,
            gl=True,
            namespace=namespace,
            options='v=0'
        )

        top_parent = cls.get_no_parent_transform(ref)
        if top_parent:
            node = top_parent
            tra = xform(node, q=1, ws=1, t=1)
            rot = xform(node, q=1, ws=1, ro=1)
            sca = xform(node, q=1, ws=1, s=1)

            new_top_parent_node = cls.get_no_parent_transform(dup_ref)
            xform(new_top_parent_node, ws=1, t=tra)
            xform(new_top_parent_node, ws=1, ro=rot)
            xform(new_top_parent_node, ws=1, s=sca)

            # parent to the same group
            group = node.getParent()
            if group:
                pm.parent(new_top_parent_node, group)

            # select the top node
            pm.select(new_top_parent_node)

    @classmethod
    def publish_model_as_look_dev(cls):
        """Publishes Model versions as LookDev versions of the same task.

        Also handles references etc.
        """
        #
        # Create LookDev for Current Model Task
        #

        from stalker import db, Task, Version, Type, LocalSession, defaults
        from anima.env import mayaEnv

        do_db_setup()
        m = mayaEnv.Maya()

        local_session = LocalSession()
        logged_in_user = local_session.logged_in_user
        if not logged_in_user:
            raise RuntimeError('Please login to Stalker')

        model_type = Type.query.filter(Type.name=="Model").first()
        look_dev_type = \
            Type.query.filter(Type.name=="Look Development").first()

        current_version = m.get_current_version()
        model_task = current_version.task

        if model_task.type != model_type:
            raise RuntimeError('This is not a Model version')

        if not current_version.is_published:
            raise RuntimeError('Please Publish this maya scene')

        if current_version.take_name != 'Main':
            raise RuntimeError('This is not the Main take')

        # find lookDev
        look_dev = Task.query\
            .filter(Task.parent==model_task.parent)\
            .filter(Task.type==look_dev_type).first()

        if not look_dev:
            raise RuntimeError(
                'There is no LookDev task, please inform your Stalker admin'
            )

        previous_look_dev_version = \
            Version.query\
                .filter(Version.task==look_dev)\
                .filter(Version.take_name=='Main')\
                .first()

        description = 'Auto Created By %s ' % logged_in_user.name
        take_name = defaults.version_take_name
        if not previous_look_dev_version:
            # do the trick
            pm.newFile(f=1)

            # create a new version
            new_version = Version(
                task=look_dev,
                description=description,
                take_name=take_name,
                created_by=logged_in_user
            )
            new_version.is_published = True

            m.save_as(new_version)

            # reference the model version
            pm.createReference(
                current_version.absolute_full_path,
                gl=True,
                namespace=current_version.nice_name,
                options='v=0'
            )

            pm.saveFile()
            db.DBSession.add(new_version)

        else:
            latest_look_dev_version = previous_look_dev_version.latest_version
            reference_resolution = m.open(latest_look_dev_version, force=True)
            m.update_versions(reference_resolution)

            if reference_resolution['update'] \
               or reference_resolution['create']:
                # create a new version
                new_version = Version(
                    task=look_dev,
                    description=description,
                    take_name=take_name,
                    created_by=logged_in_user,
                    parent=latest_look_dev_version
                )
                new_version.is_published = True

                m.save_as(new_version)

        # reopen model scene
        m.open(current_version, force=True)

    @classmethod
    def open_reference_in_new_maya(cls):
        """opens the selected references in new maya session
        """
        import subprocess

        node = pm.ls(sl=1)[0]
        if node:
            process = subprocess.Popen(
                ['maya',
                 node.referenceFile().path],
                stderr=subprocess.PIPE
            )

    @classmethod
    def delete_unused_intermediate_shapes(cls):
        """clears unused intermediate shape nodes
        """
        unused_nodes = []
        for node in pm.ls(type=pm.nt.Mesh):
            if len(node.inputs()) == 0 and len(node.outputs()) == 0 \
               and node.attr('intermediateObject').get():
                unused_nodes.append(node)
        pm.delete(unused_nodes)

    @classmethod
    def fix_reference_namespace(cls):
        """fixes reference namespace
        """
        ref_count = len(pm.listReferences(recursive=True))

        if ref_count > 25:
            result = pm.windows.confirmBox(
                'Fix Reference Namespace',
                'You have %s references in your scene,\n'
                'this will take too much time\n\nIs that Ok?' % ref_count
            )
            if not result:
                return

        from stalker import db, LocalSession
        from anima.env import mayaEnv
        m = mayaEnv.Maya()

        local_session = LocalSession()
        logged_in_user = local_session.logged_in_user

        if not logged_in_user:
            raise RuntimeError('Please login before running the script')

        versions = m.fix_reference_namespaces()
        for version in versions:
            version.created_by = logged_in_user

        db.DBSession.commit()

    @classmethod
    def delete_all_sound(cls):
        selection = pm.ls(type="audio")
        pm.delete(selection)

    @classmethod
    def fix_reference_paths(cls):
        """Fixes reference paths that are not using environment vars
        """
        # list current scene references
        from anima.env import mayaEnv
        m_env = mayaEnv.Maya()
        current_version = m_env.get_current_version()

        all_refs = pm.listReferences(recursive=True)
        refs_with_wrong_prefix = []

        for ref in all_refs:
            if '$REPO' not in ref.unresolvedPath():
                parent = ref.parent()
                if parent:
                    refs_with_wrong_prefix.append(parent)

        ref_paths = [ref.path for ref in refs_with_wrong_prefix]
        for ref_path in ref_paths:
            version = m_env.get_version_from_full_path(ref_path)
            if version:
                m_env.open(version, force=True)
                pm.saveFile()

        if pm.env.sceneName() != current_version.absolute_full_path:
            m_env.open(current_version, force=True)

    @classmethod
    def archive_current_scene(cls):
        """archives the current scene
        """
        # before doing anything ask it
        response = pm.confirmDialog(
            title='Do Archive?',
            message='This will create a ZIP file containing\n'
                    'the current scene and all its references\n'
                    '\n'
                    'Is that OK?',
            button=['Yes', 'No'],
            defaultButton='No',
            cancelButton='No',
            dismissString='No'
        )
        if response == 'No':
            return

        import os
        import shutil
        import anima
        from anima.env.mayaEnv import Maya
        from anima.env.mayaEnv.archive import Archiver
        m_env = Maya()
        version = m_env.get_current_version()
        if version:
            path = version.absolute_full_path
            arch = Archiver()
            task = version.task
            if False:
                from stalker import Version, Task
                assert(isinstance(version, Version))
                assert(isinstance(task, Task))
            project_name = version.nice_name
            project_path = arch.flatten(path, project_name=project_name)

            # append link file
            stalker_link_file_path = os.path.join(project_path,
                                                  'scenes/stalker_links.txt')
            version_upload_link = '%s/tasks/%s/versions/list' % (
                anima.stalker_server_external_address,
                task.id
            )
            request_review_link = '%s/tasks/%s/view' % (
                anima.stalker_server_external_address,
                task.id
            )
            with open(stalker_link_file_path, 'w+') as f:
                f.write("Version Upload Link: %s\n"
                        "Request Review Link: %s\n" % (version_upload_link,
                                                       request_review_link))
            zip_path = arch.archive(project_path)
            new_zip_path = os.path.join(
                version.absolute_path,
                os.path.basename(zip_path)
            )

            # move the zip right beside the original version file
            shutil.move(zip_path, new_zip_path)

            # open the zip file in browser
            from anima.utils import open_browser_in_location
            open_browser_in_location(new_zip_path)


class Modeling(object):
    @classmethod
    def reverse_normals(cls):
        selection = pm.ls(sl=1)
        for item in selection:
            pm.polyNormal(item, normalMode=0, userNormalMode=0, ch=1)
        pm.delete(ch=1)
        pm.select(selection)

    @classmethod
    def fix_normals(cls):
        selection = pm.ls(sl=1)
        pm.polySetToFaceNormal()
        for item in selection:
            pm.polyNormal(item, normalMode=2, userNormalMode=0, ch=1)
            pm.polySoftEdge(item, a=180, ch=1)
        pm.delete(ch=1)
        pm.select(selection)

    @classmethod
    def polySmoothFace(cls, method):
        selection = pm.ls(sl=1)
        for item in selection:
            pm.polySmooth(
                item, mth=method, dv=1, c=1, kb=0, ksb=0, khe=0, kt=1, kmb=0,
                suv=1, peh=0, sl=1, dpe=1, ps=0.1, ro=1, ch=1
            )
        pm.select(selection)

    @classmethod
    def activate_deActivate_smooth(cls, nodeState):
        selection = pm.ls(type='polySmoothFace')
        for item in selection:
            item.nodeState.set(nodeState)

    @classmethod
    def delete_smooth(cls):
        Modeling.activate_deActivate_smooth(0)
        selection = pm.ls(type='polySmoothFace')
        if len(selection) > 0:
            pm.delete(selection)

    @classmethod
    def delete_smooth_on_selected(cls):
        selection = pm.ls(sl=1)
        deleteList = []
        for item in selection:
            hist = pm.listHistory(item)
            for i in range(0, len(hist)):
                if hist[i].type() == 'polySmoothFace':
                    deleteList.append(hist[i])
        pm.delete(deleteList)

    @classmethod
    def hierarchy_instancer(cls):
        from anima.env.mayaEnv import hierarchy_instancer

        instancer = hierarchy_instancer.HierarchyInstancer()
        for node in pm.ls(sl=1):
            instancer.instance(node)

    @classmethod
    def relax_vertices(cls):
        from anima.env.mayaEnv import relax_vertices
        relax_vertices.relax()

    @classmethod
    def uvTools(cls):
        """opens the mel script oyUVTools
        """
        pm.mel.eval('oyUVTools;')


class Rigging(object):
    """Rigging tools
    """

    @classmethod
    def setup_stretchy_spline_IKCurve(cls):
        """
        """
        selection = pm.ls(sl=1)
        curve = selection[0]
        curve_info = pm.createNode("curveInfo")
        mult_div = pm.createNode("multiplyDivide")
        curve_shape = pm.listRelatives(curve, s=1)

        curve_shape[0].worldSpace >> curve_info.ic
        curve_info.arcLength >> mult_div.input1X

        curve_length = curve_info.arcLength.get()
        mult_div.input2X.set(curve_length)
        mult_div.operation.set(2)
        pm.select(mult_div, curve_info, curve_shape[0], add=True)

    @classmethod
    def select_joints_deforming_object(cls):
        selection = pm.ls(sl=1)
        conn = pm.listHistory(selection[0])
        skin_cluster = ""
        for i in range(0, len(conn)):
            if conn[i].type() == "skinCluster":
                skin_cluster = conn[i]
                break
        conn = pm.listConnections(skin_cluster)
        joints = []
        for item in conn:
            if item.type() == "joint":
                joints.append(item)
        pm.select(joints)
        print pm.ls(sl=1).sort

    @classmethod
    def axial_correction_group(cls):
        selection = pm.ls(sl=1)
        for item in selection:
            auxiliary.axial_correction_group(item)

    @classmethod
    def create_axial_correction_group_for_clusters(cls):
        selection = pm.ls(sl=1)
        Rigging.axial_correction_group()
        pm.select(cl=1)
        for cluster_handle in selection:
            cluster_handle_shape = pm.listRelatives(cluster_handle, s=True)
            cluster_parent = pm.listRelatives(cluster_handle, p=True)
            trans = cluster_handle_shape[0].origin.get()
            cluster_parent[0].translate.set(trans[0], trans[1], trans[2])
        pm.select(selection)

    @classmethod
    def set_clusters_relative_state(cls, relative_state):
        selection = pm.ls(sl=1)
        cluster = ""
        for clusterHandle in selection:
            conn = pm.listConnections(clusterHandle)
            for i in range(0, len(conn)):
                if conn[i].type() == "cluster":
                    cluster = conn[i]
                    break
            cluster.relative.set(relative_state)

    @classmethod
    def add_controller_shape(cls):
        selection = pm.ls(sl=1)
        if len(selection) < 2:
            return
        objects = []
        for i in range(0, (len(selection) - 1)):
            objects.append(selection[i])
        joints = selection[len(selection) - 1]
        for i in range(0, len(objects)):
            parents = pm.listRelatives(objects[i], p=True)
            if len(parents) > 0:
                temp_list = pm.parent(objects[i], w=1)
                objects[i] = temp_list[0]
            temp_list = pm.parent(objects[i], joints)
            objects[i] = temp_list[0]
            pm.makeIdentity(objects[i], apply=True, t=1, r=1, s=1, n=0)
            temp_list = pm.parent(objects[i], w=True)
            objects[i] = temp_list[0]
        shapes = pm.listRelatives(objects, s=True, pa=True)
        for i in range(0, len(shapes)):
            temp_list = pm.parent(shapes[i], joints, r=True, s=True)
            shapes[i] = temp_list[0]
        joint_shapes = pm.listRelatives(joints, s=True, pa=True)
        for i in range(0, len(joint_shapes)):
            name = "%sShape%f" % (joints, (i + 1))
            temp = ''.join(name.split('|', 1))
            pm.rename(joint_shapes[i], temp)
        pm.delete(objects)
        pm.select(joints)

    @classmethod
    def replace_controller_shape(cls):
        selection = pm.ls(sl=1)
        if len(selection) < 2:
            return
        objects = selection[0]
        joints = selection[1]
        shape = pm.listRelatives(objects, s=True)
        joint_shape = pm.listRelatives(joints, s=True)
        parents = pm.listRelatives(objects, p=True)
        if len(parents):
            temp_list = pm.parent(objects, w=True)
            objects = temp_list
        temp_list = pm.parent(objects, joints)
        objects = temp_list[0]
        pm.makeIdentity(objects, apply=True, t=1, r=1, s=1, n=0)
        temp_list = pm.parent(objects, w=True)
        objects = temp_list[0]
        if len(joint_shape):
            pm.delete(joint_shape)
        for i in range(0, len(shape)):
            name = "%sShape%f" % (joints, (i + 1))
            shape[i] = pm.rename(shape[i], name)
            temp_list = pm.parent(shape[i], joints, r=True, s=True)
            shape[i] = temp_list[0]
        pm.delete(objects)
        pm.select(joints)

    @classmethod
    def fix_bound_joint(cls):
        from anima.env.mayaEnv import fix_bound_joint
        fix_bound_joint.UI()

    @classmethod
    def create_follicle(cls, component):
        """creates a follicle at given component
        """
        follicleShape = pm.createNode('follicle')

        geometry = component.node()
        uv = None

        if isinstance(geometry, pm.nt.Mesh):
            geometry.attr('outMesh') >> follicleShape.attr('inputMesh')
            # get uv
            uv = component.getUV()
        elif isinstance(geometry, pm.nt.NurbsSurface):
            geometry.attr('local') >> follicleShape.attr('inputSurface')
            # get uv
            # TODO: Fix this
            uv = [0, 0]

        geometry.attr('worldMatrix[0]') >> follicleShape.attr(
            'inputWorldMatrix')

        follicleShape.setAttr('pu', uv[0])
        follicleShape.setAttr('pv', uv[1])

        # set simulation to static
        follicleShape.setAttr('simulationMethod', 0)

        # connect to its transform node
        follicle = follicleShape.getParent()

        follicleShape.attr('outTranslate') >> follicle.attr('t')
        follicleShape.attr('outRotate') >> follicle.attr('r')

        return follicle

    @classmethod
    def create_follicles(cls):
        for comp in pm.ls(sl=1, fl=1):
            Rigging.create_follicle(comp)

    @classmethod
    def reset_tweaks(cls):
        """Resets the tweaks on the selected deformed objects
        """
        for obj in pm.ls(sl=1):
            for tweak_node in pm.ls(obj.listHistory(), type=pm.nt.Tweak):

                try:
                    for i in tweak_node.pl[0].cp.get(mi=1):
                        tweak_node.pl[0].cv[i].vx.set(0)
                        tweak_node.pl[0].cv[i].vy.set(0)
                        tweak_node.pl[0].cv[i].vz.set(0)
                except TypeError:
                    try:
                        for i in tweak_node.vl[0].vt.get(mi=1):
                            tweak_node.vl[0].vt[i].vx.set(0)
                            tweak_node.vl[0].vt[i].vy.set(0)
                            tweak_node.vl[0].vt[i].vz.set(0)
                    except TypeError:
                        pass


class Render(object):
    """Tools for render
    """

    @classmethod
    def add_miLabel(cls):
        selection = pm.ls(sl=1)

        for node in selection:
            if node.type() == 'Transform':
                if node.hasAttr('miLabel'):
                    pass
                else:
                    pm.addAttr(node, ln='miLabel', at='long', keyable=True)

    @classmethod
    def connect_facingRatio_to_vCoord(cls):
        selection = pm.ls(sl=1)
        for i in range(1, len(selection)):
            selection[0].facingRatio.connect((selection[i] + '.vCoord'),
                                             force=True)

    @classmethod
    def set_shape_attribute(cls, attributeName, value, applyToHierarchy):
        preSelectionList = pm.ls(sl=1)
        hier = str(applyToHierarchy)
        if hier:
            pm.select(hierarchy=1)
        objects = pm.ls(sl=1)
        for item in objects:
            if item.hasAttr(attributeName):
                item.setAttr(attributeName, value)
        pm.select(preSelectionList)

    @classmethod
    def set_finalGatherHide(cls, value):
        """sets the finalGatherHide to on or off for the given list of objects
        """
        attr_name = "miFinalGatherHide"
        objects = pm.ls(sl=1)

        for obj in objects:

            shape = obj

            if isinstance(obj, pm.nt.Transform):
                shape = obj.getShape()

            if not isinstance(shape, (pm.nt.Mesh, pm.nt.NurbsSurface)):
                continue

            # add the attribute if it doesn't already exists
            if not shape.hasAttr(attr_name):
                pm.addAttr(shape, ln=attr_name, at="long", min=0, max=1, k=1)

            obj.setAttr(attr_name, value)

    @classmethod
    def replace_shaders_with_last(cls):
        """Assigns the last shader selected to all the objects using the shaders
        on the list
        """
        sel_list = pm.ls(sl=1)
        target_node = sel_list[-1]

        for node in sel_list[:-1]:
            pm.hyperShade(objects=node)
            pm.hyperShade(assign=target_node)

        pm.select(None)

    @classmethod
    def create_texture_ref_object(cls):
        selection = pm.ls(sl=1)
        for obj in selection:
            pm.select(obj)
            pm.runtime.CreateTextureReferenceObject()
        pm.select(selection)

    @classmethod
    def use_mib_texture_filter_lookup(cls):
        """Adds texture filter lookup node to the selected file texture nodes for
        better texture filtering.

        The function is smart enough to use the existing nodes, if there is a
        connection from the selected file nodes to a mib_texture_filter_lookup node
        then it will not create any new node and just use the existing ones.

        It will also not create any place2dTexture nodes if the file node doesn't
        have a place2dTexture node but is connected to a filter lookup node which
        already has a connection to a place2dTexture node.
        """

        file_nodes = pm.ls(sl=1, type="file")

        for file_node in file_nodes:
            # set the filter type to none
            file_node.filterType.set(0)

            # check if it is already connected to a mib_texture_filter_lookup node
            message_outputs = \
                file_node.message.outputs(type="mib_texture_filter_lookup")

            if len(message_outputs):
                # use the first one
                mib_texture_filter_lookup = message_outputs[0]
            else:
                # create a texture filter lookup node
                mib_texture_filter_lookup = \
                    pm.createNode("mib_texture_filter_lookup")

                # do the connection
                file_node.message >> mib_texture_filter_lookup.tex

            # check if the mib_texture_filter_lookup has any connection to a
            # placement node

            mib_t_f_l_to_placement = \
                mib_texture_filter_lookup.inputs(type="place2dTexture")

            placement_node = None
            if len(mib_t_f_l_to_placement):
                # do nothing
                placement_node = mib_t_f_l_to_placement[0].node()
            else:
                # get the texture placement
                placement_connections = \
                    file_node.inputs(type="place2dTexture", p=1, c=1)

                # if there is no placement create one
                placement_node = None
                if len(placement_connections):
                    placement_node = placement_connections[0][1].node()
                    # disconnect connections from placement to file node
                    for conn in placement_connections:
                        conn[1] // conn[0]
                else:
                    placement_node = pm.createNode("place2dTexture")

                # connect placement to mr_texture_filter_lookup
                placement_node.outU >> mib_texture_filter_lookup.coordX
                placement_node.outV >> mib_texture_filter_lookup.coordY

            # connect color
            for output in file_node.outColor.outputs(p=1):
                mib_texture_filter_lookup.outValue >> output

            # connect alpha
            for output in file_node.outAlpha.outputs(p=1):
                mib_texture_filter_lookup.outValueA >> output

    @classmethod
    def convert_to_linear(cls):
        """adds a gamma_gain node in between the selected nodes outputs to make the
        result linear
        """

        #
        # convert to linear
        #

        selection = pm.ls(sl=1)

        for file_node in selection:
            # get the connections
            outputs = file_node.outputs(plugs=True)

            if not len(outputs):
                continue

            # and insert a mip_gamma_gain
            gamma_node = pm.createNode('mip_gamma_gain')
            gamma_node.setAttr('gamma', 2.2)
            gamma_node.setAttr('reverse', True)

            # connect the file_node to gamma_node
            try:
                file_node.outValue >> gamma_node.input
                file_node.outValueA >> gamma_node.inputA
            except AttributeError:
                file_node.outColor >> gamma_node.input

            # do all the connections from the output of the gamma
            for output in outputs:
                try:
                    gamma_node.outValue >> output
                except RuntimeError:
                    gamma_node.outValueA >> output

        pm.select(selection)

    @classmethod
    def use_image_sequence(cls):
        """creates an expression to make the mentalrayTexture node also able to read
        image sequences

        Select your mentalrayTexture nodes and then run the script.

        The filename should use the file.%nd.ext format
        """

        textures = pm.ls(sl=1, type="mentalrayTexture")

        for texture in textures:
            # get the filename
            filename = texture.getAttr("fileTextureName")

            splits = filename.split(".")
            if len(splits) == 3:
                base = ".".join(splits[0:-2]) + "."
                pad = len(splits[-2])
                extension = "." + splits[-1]

                expr = 'string $padded_frame = python("\'%0' + str(pad) + \
                       'd\'%" + string(frame));\n' + \
                       'string $filename = "' + base + '" + \
                       $padded_frame + ".tga";\n' + \
                       'setAttr -type "string" ' + texture.name() + \
                       '.fileTextureName $filename;\n'

                # create the expression
                pm.expression(s=expr)

    @classmethod
    def add_to_selected_container(cls):
        selection = pm.ls(sl=1)
        conList = pm.ls(sl=1, con=1)
        objList = list(set(selection) - set(conList))
        if len(conList) == 0:
            pm.container(addNode=selection)
        elif len(conList) == 1:
            pm.container(conList, edit=True, addNode=objList)
        else:
            length = len(conList) - 1
            for i in range(0, length):
                containerList = conList[i]
                pm.container(conList[-1], edit=True, f=True,
                             addNode=containerList)
                pm.container(conList[-1], edit=True, f=True, addNode=objList)

    @classmethod
    def remove_from_container(cls):
        selection = pm.ls(sl=1)
        for i in range(0, len(selection)):
            con = pm.container(q=True, fc=selection[i])
            pm.container(con, edit=True, removeNode=selection[i])

    @classmethod
    def reload_file_textures(cls):
        fileList = pm.ls(type="file")
        for fileNode in fileList:
            mel.eval('AEfileTextureReloadCmd(%s.fileTextureName)' % fileNode)

    @classmethod
    def transfer_shaders(cls):
        selection = pm.ls(sl=1)
        pm.select(None)
        source = selection[0]
        target = selection[1]
        auxiliary.transfer_shaders(source, target)
        pm.select(selection)

    @classmethod
    def fit_placement_to_UV(cls):
        selection = pm.ls(sl=1, fl=1)
        uvs = []
        placements = []
        for uv in selection:
            if isinstance(uv, pm.general.MeshUV):
                uvs.append(uv)
        for p in selection:
            if isinstance(p, pm.nodetypes.Place2dTexture):
                placements.append(p)
        minU = 1000
        minV = 1000
        maxU = -1000
        maxV = -1000
        for uv in uvs:
            uvCoord = pm.polyEditUV(uv, q=1)
            if uvCoord[0] > maxU:
                maxU = uvCoord[0]
            if uvCoord[0] < minU:
                minU = uvCoord[0]
            if uvCoord[1] > maxV:
                maxV = uvCoord[1]
            if uvCoord[1] < minV:
                minV = uvCoord[1]
        for p in placements:
            p.setAttr('coverage', (maxU - minU, maxV - minV))
            p.setAttr('translateFrame', (minU, minV))

    @classmethod
    def open_node_in_browser(cls):
        # get selected nodes
        node_attrs = {
            'File': 'fileTextureName',
            'aiImage': 'filename',
            'aiStandIn': 'dso',
        }
        import os
        from anima.utils import open_browser_in_location

        for node in pm.ls(sl=1):
            type_ = pm.objectType(node)
            # special case: if transform use shape
            if type_ == 'transform':
                node = node.getShape()
                type_ = pm.objectType(node)
            attr_name = node_attrs.get(type_)
            if attr_name:
                # if any how it contains a "#" character use the path
                path = node.getAttr(attr_name)
                if "#" in path:
                    path = os.path.dirname(path)
                open_browser_in_location(path)

    @classmethod
    def enable_matte(cls, color=0):
        """enables matte on selected objects
        """
        #
        # Enable Matte on Selected Objects
        #
        colors = [
            [0, 0, 0, 0],  # Not Visible
            [1, 0, 0, 0],  # Red
            [0, 1, 0, 0],  # Green
            [0, 0, 1, 0],  # Blue
            [0, 0, 0, 1],  # Alpha
        ]
        arnold_shaders = (
            pm.nt.AiStandard, pm.nt.AiHair, pm.nt.AiSkinSss, pm.nt.AiUtility
        )

        for node in pm.ls(sl=1, dag=1, type=[pm.nt.Mesh, pm.nt.NurbsSurface,
                                             'aiStandIn']):
            obj = node
            #if isinstance(node, pm.nt.Mesh):
            #    obj = node
            #elif isinstance(node, pm.nt.Transform):
            #    obj = node.getShape()

            shading_nodes = pm.listConnections(obj, type='shadingEngine')
            for shadingNode in shading_nodes:
                shader = shadingNode.attr('surfaceShader').connections()[0]
                if isinstance(shader, arnold_shaders):
                    try:
                        pm.editRenderLayerAdjustment(shader.attr("aiEnableMatte"))
                        pm.editRenderLayerAdjustment(shader.attr("aiMatteColor"))
                        pm.editRenderLayerAdjustment(shader.attr("aiMatteColorA"))
                        shader.attr("aiEnableMatte").set(1)
                        shader.attr("aiMatteColor").set(colors[color][0:3], type='double3')
                        shader.attr("aiMatteColorA").set(colors[color][3])
                    except RuntimeError as e:
                        # there is some connections
                        print str(e)

    @classmethod
    def enable_subdiv(cls):
        """enables subdiv on selected objects
        """
        #
        # Set SubDiv to CatClark on Selected nodes
        #
        for node in pm.ls(sl=1):
            shape = node.getShape()
            try:
                shape.aiSubdivIterations.set(2)
                shape.aiSubdivType.set(1)
            except AttributeError:
                pass

    @classmethod
    def generate_ass_take(cls):
        """generates an ASS take for the current scene
        """
        pass

    @classmethod
    def selected_to_ass(cls):
        """replaces the related references of the selected objects with ASS
        versions if available
        """
        # work on every selected object
        selection = pm.ls(sl=1)

        # collect reference files first
        references = []
        for node in selection:
            ref = node.referenceFile()
            if ref is not None and ref not in references:
                references.append(ref)

        # now go over each reference
        for ref in references:
            # check if it has an ass
            if ref.has_ass():
                ref.to_ass()
                continue
            else:
                ## use the highest parent ref with ASS take
                #parent = ref.parent()
                #all_parents = []
                #while parent:
                #    all_parents.append(parent)
                #    ref = parent
                #    parent = ref.parent()
                #
                ## go from the highest parent
                #for p_ref in reversed(all_parents):
                #    if p_ref.has_ass():
                #        p_ref.to_ass()
                #        break

                # use the first parent ref with ASS take
                ass_ref = None
                parent = ref.parent()
                while parent:
                    ref = parent
                    if ref.has_ass():
                        ass_ref = ref
                        break
                    parent = ref.parent()

                if ass_ref:
                    ass_ref.to_ass()

    @classmethod
    def selected_to_original(cls):
        """replaces the related references of the selected ASS with original
        versions if available
        """
        # work on every selected object
        selection = pm.ls(sl=1)

        # collect reference files first
        references = []
        for node in selection:
            ref = node.referenceFile()
            if ref is not None and ref not in references and ref.is_ass():
                references.append(ref)

        # now go over each reference
        for ref in references:
            ref.to_original()


class Animation(object):
    """animation tools
    """

    @classmethod
    def oySmoothComponentAnimation(cls, ui_item):
        """calls the mel script oySmoothComponentAnimation
        """
        # get the frame range
        frame_range = pm.textFieldButtonGrp(
            ui_item, q=1, tx=1
        )
        pm.mel.eval('oySmoothComponentAnimation(%s)' % frame_range)


    @classmethod
    def vertigo_setup_look_at(cls):
        """sets up a the necessary locator for teh Vertigo effect for the selected
        camera
        """
        from anima.env.mayaEnv import vertigo
        cam = pm.ls(sl=1)[0]
        vertigo.setup_look_at(cam)

    @classmethod
    def vertigo_setup_vertigo(cls):
        """sets up a Vertigo effect for the selected camera
        """
        from anima.env.mayaEnv import vertigo
        cam = pm.ls(sl=1)[0]
        vertigo.setup_vertigo(cam)

    @classmethod
    def vertigo_delete(cls):
        """deletes the Vertigo setup for the selected camera
        """
        from anima.env.mayaEnv import vertigo
        cam = pm.ls(sl=1)[0]
        vertigo.delete(cam)

    @classmethod
    def cam_2_chan(cls, startButton, endButton):
        start = int(pm.textField(startButton, q=True, tx=True))
        end = int(pm.textField(endButton, q=True, tx=True))
        cam_to_chan(start, end)

    @classmethod
    def create_alembic_command(cls):
        """for ui
        """
        from_top_node = pm.checkBox('from_top_node_checkBox', q=1, v=1)
        cls.create_alembic(from_top_node)

    @classmethod
    def create_alembic(cls, from_top_node=1):
        """creates alembic cache from selected nodes
        """
        import os
        root_flag = '-root %(node)s'
        mel_command = 'AbcExport -j "-frameRange %(start)s %(end)s -ro ' \
                      '-stripNamespaces -uvWrite -wholeFrameGeo -worldSpace ' \
                      '%(roots)s ' \
                      '-file %(path)s";'

        current_path = pm.workspace.path
        abc_path = os.path.join(current_path, 'cache', 'alembic')
        try:
            os.makedirs(abc_path)
        except OSError:
            pass

        abc_full_path = pm.fileDialog2(startingDirectory=abc_path)

        def find_top_parent(node):
            parents = node.listRelatives(p=1)
            parent = None
            while parents:
                parent = parents[0]
                parents = parent.listRelatives(p=1)
                if parents:
                    parent = parents[0]
                else:
                    return parent
            if not parent:
                return node
            else:
                return parent

        if abc_full_path:
            abc_full_path = abc_full_path[0]  # this is dirty
            abc_full_path = os.path.splitext(abc_full_path)[0] + '.abc'

            # get nodes
            selection = pm.ls(sl=1)
            nodes = []
            for node in selection:
                if from_top_node:
                    node = find_top_parent(node)
                if node not in nodes:
                    nodes.append(node)

            # generate root flags
            roots = []
            for node in nodes:
                roots.append(
                    root_flag % {
                        'node': node.fullPath()
                    }
                )

            roots_as_string = ' '.join(roots)

            start = int(pm.playbackOptions(q=1, minTime=1))
            end = int(pm.playbackOptions(q=1, maxTime=1))
            rendered_mel_command = mel_command % {
                'start': start,
                'end': end,
                'roots': roots_as_string,
                'path': abc_full_path
            }
            pm.mel.eval(rendered_mel_command)

    @classmethod
    def copy_alembic_data(cls, source=None, target=None):
        """Copies alembic data from source to target hierarchy
        """
        selection = pm.ls(sl=1)
        if not source or not target:
            source = selection[0]
            target = selection[1]

        #
        # Move Alembic Data From Source To Target
        #
        #selection = pm.ls(sl=1)
        #
        #source = selection[0]
        #target = selection[1]

        source_nodes = source.listRelatives(
            ad=1,
            type=(pm.nt.Mesh, pm.nt.NurbsSurface)
        )
        target_nodes = target.listRelatives(
            ad=1,
            type=(pm.nt.Mesh, pm.nt.NurbsSurface)
        )

        source_node_names = []
        target_node_names = []

        for node in source_nodes:
            name = node.name().split(':')[-1].split('|')[-1]
            source_node_names.append(name)

        for node in target_nodes:
            name = node.name().split(':')[-1].split('|')[-1]
            target_node_names.append(name)

        lut = []

        for i, target_node in enumerate(target_nodes):
            target_node_name = target_node_names[i]
            try:
                index = source_node_names.index(target_node_name)
            except ValueError:
                pass
            else:
                lut.append((source_nodes[index], target_nodes[i]))

        for source_node, target_node in lut:
            if isinstance(source_node, pm.nt.Mesh):
                in_attr_name = 'inMesh'
                out_attr_name = 'outMesh'
            else:
                in_attr_name = 'create'
                out_attr_name = 'worldSpace'

            conns = source_node.attr(in_attr_name).inputs(p=1)
            if conns:
                for conn in conns:
                    if isinstance(conn.node(), pm.nt.AlembicNode):
                        conn >> target_node.attr(in_attr_name)
                        break
            else:
                # no connection
                # just connect the shape itself
                source_node.attr(out_attr_name) >> \
                    target_node.attr(in_attr_name)

    @classmethod
    def bake_component_animation(cls):
        """bakes the selected component animation to a space locator
        """
        from pymel.core import spaceLocator, setKeyframe, xform

        start = int(pm.playbackOptions(q=1, minTime=1))
        end = int(pm.playbackOptions(q=1, maxTime=1))

        vertices = pm.ls(sl=1, fl=1)

        locator = spaceLocator()

        for i in range(start, end+1):
            pm.currentTime(i)
            point_positions = xform(vertices, q=1, ws=1, t=1)
            point_count = len(point_positions) / 3
            px = reduce(lambda x, y: x+y, point_positions[0::3]) / point_count
            py = reduce(lambda x, y: x+y, point_positions[1::3]) / point_count
            pz = reduce(lambda x, y: x+y, point_positions[2::3]) / point_count

            locator.t.set(px, py, pz)
            setKeyframe(locator.tx)
            setKeyframe(locator.ty)
            setKeyframe(locator.tz)


def fur_map_unlocker(furD, lock=False):
    """unlocks all the fur map attributes for the given furDescription node
    """
    fur_attrs = [
        "BaseColorMap",
        "TipColorMap",
        "BaseAmbientColorMap",
        "TipAmbientColorMap",
        "SpecularColorMap",
        "SpecularSharpnessMap",
        "LengthMap",
        "BaldnessMap",
        "InclinationMap",
        "RollMap",
        "PolarMap",
        "BaseOpacityMap",
        "TipOpacityMap",
        "BaseWidthMap",
        "TipWidthMap",
        "BaseCurlMap",
        "TipCurlMap",
        "ScraggleMap",
        "ScraggleFrequencyMap",
        "ScraggleCorrelationMap",
        "ClumpingMap",
        "ClumpingFrequencyMap",
        "ClumpShapeMap",
        "SegmentsMap",
        "AttractionMap",
        "OffsetMap",
        "CustomEqualizerMap",
    ]

    # set lock state
    for attr in fur_attrs:
        try:
            print "setting lock: %s for %s.%s" % (lock, furD.name(), attr)
            furD.attr(attr).setLocked(lock)
        except pm.MayaAttributeError as e:
            print e
            print "%s attribute is not mapped" % attr
            pass
