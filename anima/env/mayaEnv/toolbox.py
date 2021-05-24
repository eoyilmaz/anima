# -*- coding: utf-8 -*-

import functools
import os

from anima.env.mayaEnv.animation import Animation
from anima.env.mayaEnv.general import General
from anima.env.mayaEnv.modeling import Modeling
from anima.env.mayaEnv.previs import Previs
from anima.env.mayaEnv.reference import Reference
from anima.env.mayaEnv.render import Render
from anima.env.mayaEnv.rigging import Rigging

import pymel.core as pm
import maya.mel as mel

from anima.env.mayaEnv import auxiliary, camera_tools


__last_commands__ = []  # list of dictionaries

__last_tab__ = 'ANIMA_TOOLBOX_LAST_TAB_INDEX'


__commands__ = []


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
        'print \\"\\";python(\\\"from anima.env.mayaEnv.toolbox import ' \
        'repeater; repeater(%s);\\\");' % index

    repeat_last_command = 'repeatLast -ac "%(command)s" -acl "%(label)s";' % {
        'command': command,
        'label': callable_.__name__
    }
    print(repeat_last_command)

    pm.mel.eval(repeat_last_command)
    __last_commands__.append(call_data)

    # also call the callable
    callable_(*args, **kwargs)


def repeated_callback(callable_, *args, **kwargs):
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


def filter_tools(search_text):
    """filters toolbox
    :param str search_text: The search_text
    """
    for command in __commands__:
        uitype = command.type()
        if uitype == 'button':
            label = command.getLabel()
            if search_text.lower() not in label.lower():
                command.setVisible(False)
            else:
                command.setVisible(True)
        elif uitype == 'rowLayout':
            # get the children
            children = command.children()
            matched_children = False
            for c in children:
                c_uitype = c.type()
                if c_uitype in ['button', 'staticText'] and \
                    search_text in c.getLabel().lower():
                    matched_children = True
                    break

            if not matched_children:
                command.setVisible(False)
            else:
                command.setVisible(True)


def UI():
    # window setup
    width = 260
    height = 650
    row_spacing = 3

    color = Color()

    # init the __commands LUT
    global __commands__
    __commands__ = []

    if pm.dockControl("toolbox_dockControl", q=True, ex=True):
        pm.deleteUI("toolbox_dockControl")

    window_name = "toolbox_window"
    if pm.window(window_name, q=True, ex=True):
        pm.deleteUI(window_name, wnd=True)

    toolbox_window = pm.window(
        window_name,
        wh=(width, height),
        title="Anima ToolBox"
    )

    # the layout that holds the tabs
    main_form_layout = pm.formLayout(
        'main_form_layout', nd=100, parent=toolbox_window
    )
    search_field = pm.textField(
        'search_text_field',
        tcc=filter_tools,
        placeholderText='Search...',
        parent=main_form_layout
    )

    main_tab_layout = pm.tabLayout(
        'main_tab_layout', scr=True, cr=True, parent=main_form_layout
    )

    # attach the main_tab_layout to main_form_layout
    pm.formLayout(
        main_form_layout, edit=True,
        attachForm=[
            (search_field, "top", 0),
            (search_field, "left", 0),
            (search_field, "right", 0),

            # (main_tab_layout, "top", 0),
            (main_tab_layout, "bottom", 0),
            (main_tab_layout, "left", 0),
            (main_tab_layout, "right", 0)
        ],
        attachNone=[
            (search_field, "bottom")
        ],
        attachControl=[
            (main_tab_layout, "top", 0, search_field)
        ]
    )

    with main_tab_layout:
        # ----- GENERAL ------
        general_column_layout = pm.columnLayout(
            'general_column_layout',
            adj=True,
            cal="center",
            rs=row_spacing
        )
        with general_column_layout:
            color.change()

            pm.button(
                'open_version_button',
                l="Open Version",
                c=repeated_callback(General.version_dialog, mode=1),
                ann="Open Version",
                bgc=color.color
            )

            pm.button(
                'save_as_version_button',
                l="Save As Version",
                c=repeated_callback(General.version_dialog, mode=0),
                ann="Save As Version",
                bgc=color.color
            )

            color.change()
            pm.button(
                'selectionManager_button',
                l="Selection Manager",
                c=repeated_callback(General.selection_manager),
                ann="Selection Manager",
                bgc=color.color
            )

            color.change()
            pm.button(
                'publishChecker_button',
                l="Publish Checker",
                c=repeated_callback(General.publish_checker),
                ann="Publish Checker",
                bgc=color.color
            )

            color.change()
            pm.button(
                'rename_unique_button',
                l='Rename Unique',
                c=repeated_callback(General.rename_unique),
                ann=General.rename_unique.__doc__,
                bgc=color.color
            )

            pm.button(
                'removeColonFromNames_button',
                l="remove colon(:) from node names",
                c=repeated_callback(General.remove_colon_from_names),
                ann="removes the colon (:) character from all "
                    "selected object names",
                bgc=color.color
            )

            pm.button(
                'removePastedFromNames_button',
                l="remove \"pasted_\" from node names",
                c=repeated_callback(General.remove_pasted),
                ann="removes the \"passed__\" from all selected "
                    "object names",
                bgc=color.color
            )

            color.change()
            pm.button(
                'togglePolyMeshes_button',
                l="toggle polymesh visibility",
                c=repeated_callback(General.toggle_poly_meshes),
                ann="toggles the polymesh display in the active model "
                    "panel",
                bgc=color.color
            )

            color.change()
            pm.button(
                'selectSetMembers_button',
                l="select set members",
                c=repeated_callback(General.select_set_members),
                ann="selects the selected set members in correct "
                    "order",
                bgc=color.color
            )

            color.change()
            pm.button(
                'delete_unused_intermediate_shapes_button',
                l='Delete Unused Intermediate Shape Nodes',
                c=repeated_callback(General.delete_unused_intermediate_shapes),
                ann='Deletes unused (no connection) intermediate shape nodes',
                bgc=color.color
            )

            color.change()
            pm.button(
                'export_transform_info_button',
                l='Export Transform Info',
                c=repeated_callback(General.export_transform_info),
                ann='exports transform info',
                bgc=color.color
            )

            pm.button(
                'import_transform_info_button',
                l='Import Transform Info',
                c=repeated_callback(General.import_transform_info),
                ann='imports transform info',
                bgc=color.color
            )

            color.change()
            pm.button(
                'export_global_transform_info_button',
                l='Export Global Transform Info',
                c=repeated_callback(General.export_transform_info, True),
                ann='exports global transform info',
                bgc=color.color
            )

            pm.button(
                'import_global_transform_info_button',
                l='Import Global Transform Info',
                c=repeated_callback(General.import_transform_info, True),
                ann='imports global transform info',
                bgc=color.color
            )

            color.change()
            pm.button(
                'export_component_transform_info_button',
                l='Export Component Transform Info',
                c=repeated_callback(General.export_component_transform_info),
                ann='exports component transform info',
                bgc=color.color
            )

            pm.button(
                'import_component_transform_info_button',
                l='Import Component Transform Info',
                c=repeated_callback(General.import_component_transform_info),
                ann='imports component transform info',
                bgc=color.color
            )

            color.change()
            pm.button(
                'import_rsproxy_data_from_houdini_button',
                l='Import RSProxy Data From Houdini',
                c=repeated_callback(General.rsproxy_data_importer),
                ann=General.rsproxy_data_importer.__doc__,
                bgc=color.color
            )

            color.change()
            pm.button(
                'generate_thumbnail_button',
                l='Generate Thumbnail',
                c=repeated_callback(General.generate_thumbnail),
                ann='Generates thumbnail for current scene',
                bgc=color.color
            )

            color.change()
            pm.button(
                'cleanup_light_cameras_button',
                l='Cleanup Light Cameras',
                c=repeated_callback(General.cleanup_light_cameras),
                ann=General.cleanup_light_cameras.__doc__,
                bgc=color.color
            )

            color.change()
            from anima.env.mayaEnv.general import unknown_plugin_cleaner_ui
            pm.button(
                'cleanup_plugins_button',
                l='Cleanup Unknown Plugins',
                c=repeated_callback(unknown_plugin_cleaner_ui),
                ann=unknown_plugin_cleaner_ui.__doc__,
                bgc=color.color
            )

            color.change()
            pm.button(
                'unshape_parent_node_button',
                l='Unshape Parent Nodes',
                c=repeated_callback(General.unshape_parent_nodes),
                ann=General.unshape_parent_nodes.__doc__,
                bgc=color.color
            )

        # store commands
        __commands__.extend(general_column_layout.children())


        # ----- REFERENCE ------
        reference_columnLayout = pm.columnLayout(
            'reference_columnLayout',
            adj=True, cal="center", rs=row_spacing)
        with reference_columnLayout:
            color.reset()
            pm.text(l='===== Reference Tools =====')
            pm.button(
                'nsDelete_button',
                l="nsDelete",
                c=repeated_callback(General.namespace_deleter),
                ann=General.namespace_deleter.__doc__,
                bgc=color.color
            )

            color.change()
            pm.button(
                'duplicate_selected_reference_button',
                l='Duplicate Selected Reference',
                c=repeated_callback(Reference.duplicate_selected_reference),
                ann='Duplicates the selected reference',
                bgc=color.color
            )

            color.change()
            pm.button(
                'select_reference_in_reference_editor_button',
                l='Select Reference In Reference Editor',
                c=repeated_callback(
                    Reference.select_reference_in_reference_editor
                ),
                ann=Reference.select_reference_in_reference_editor.__doc__,
                bgc=color.color
            )

            color.change()
            pm.button(
                'get_selected_reference_path_button',
                l='Get Selected Reference Path',
                c=repeated_callback(Reference.get_selected_reference_path),
                ann='Prints the selected reference full path',
                bgc=color.color
            )

            pm.button(
                'open_selected_reference_button',
                l='Open Selected Reference in New Maya',
                c=repeated_callback(Reference.open_reference_in_new_maya),
                ann='Opens the selected reference in new Maya '
                    'instance',
                bgc=color.color
            )

            color.change()
            pm.button(
                'publish_model_as_look_dev_button',
                l='Model -> LookDev',
                c=repeated_callback(Reference.publish_model_as_look_dev),
                ann='References the current Model scene to the LookDev scene '
                    'of the same task, creates the LookDev scene if '
                    'necessary, also reopens the current model scene.',
                bgc=color.color
            )

            color.change()
            pm.button(
                'fix_reference_namespace_button',
                l='Fix Reference Namespace',
                c=repeated_callback(Reference.fix_reference_namespace),
                ann='Fixes old style reference namespaces with new one, '
                    'creates new versions if necessary.',
                bgc=color.color
            )

            color.change()
            pm.button(
                'fix_reference_paths_button',
                l='Fix Reference Paths',
                c=repeated_callback(Reference.fix_reference_paths),
                ann='Fixes reference paths deeply, so they will use'
                    '$REPO env var.',
                bgc=color.color
            )

            pm.button(
                'fix_student_license_on_references_button',
                l='Fix Student License Error On References',
                c=repeated_callback(
                    Reference.fix_student_license_on_references
                ),
                ann=Reference.fix_student_license.__doc__,
                bgc=color.color
            )
            pm.button(
                'fix_student_license_on_files_button',
                l='Fix Student License Error On Selected Files',
                c=repeated_callback(
                    Reference.fix_student_license_on_selected_file
                ),
                ann=Reference.fix_student_license.__doc__,
                bgc=color.color
            )

            color.change()
            pm.button(
                'archive_button',
                l='Archive Current Scene',
                c=repeated_callback(Reference.archive_current_scene),
                ann='Creates a ZIP file containing the current scene and its'
                    'references in a flat Maya default project folder '
                    'structure',
                bgc=color.color
            )

            pm.button(
                'bind_to_original_button',
                l='Bind To Original',
                c=repeated_callback(Reference.bind_to_original),
                ann='Binds the current local references to the ones on the '
                    'repository',
                bgc=color.color
            )

            pm.button(
                'unload_selected_references_button',
                l='Unload Selected References',
                c=repeated_callback(Reference.unload_selected_references),
                ann='Unloads the highest references that is related with the selected objects',
                bgc=color.color
            )

            pm.button(
                'unload_unselected_references_button',
                l='Unload UnSelected References',
                c=repeated_callback(Reference.unload_unselected_references),
                ann='Unloads any references that is not related with the '
                    'selected objects',
                bgc=color.color
            )

            color.change()
            pm.button(
                'remove_selected_references_button',
                l='Remove Selected References',
                c=repeated_callback(Reference.remove_selected_references),
                ann='Removes the highest references that is related with the selected objects',
                bgc=color.color
            )



            color.change()
            pm.text(l='===== Representation Tools =====')

            with pm.rowLayout(nc=2, adj=1):
                pm.checkBoxGrp(
                    'generate_repr_types_checkbox_grp',
                    l='Reprs',
                    numberOfCheckBoxes=3,
                    labelArray3=['GPU', 'ASS', 'RS'],
                    cl4=['left', 'left', 'left', 'left'],
                    cw4=[51, 50, 50, 50],
                    valueArray3=[1, 1, 1]
                )

            pm.checkBox(
                'generate_repr_skip_existing_checkBox',
                l='Skip existing Reprs.',
                value=0
            )

            pm.button(
                'generate_repr_of_all_references_button',
                l='Deep Generate Repr Of All References',
                c=repeated_callback(
                    Reference.generate_repr_of_all_references_caller
                ),
                ann='Deeply generates desired Representations of all '
                    'references of this scene',
                bgc=color.color
            )
            pm.button(
                'generate_repr_of_scene_button',
                l='Generate Repr Of This Scene',
                c=repeated_callback(Reference.generate_repr_of_scene_caller),
                ann='Generates desired Representations of this scene',
                bgc=color.color
            )
            color.change()

            with pm.rowLayout(nc=2, adj=1):
                pm.radioButtonGrp(
                    'repr_apply_to_radio_button_grp',
                    l='Apply To',
                    # ad3=1,
                    labelArray2=['Selected', 'All References'],
                    numberOfRadioButtons=2,
                    cl3=['left', 'left', 'left'],
                    cw3=[50, 65, 65],
                    sl=1
                )

            pm.button(
                'to_base_button',
                l='To Base',
                c=repeated_callback(Reference.to_base),
                ann='Convert selected to Base representation',
                bgc=color.color
            )

            pm.button(
                'to_gpu_button',
                l='To GPU',
                c=repeated_callback(Reference.to_gpu),
                ann='Convert selected to GPU representation',
                bgc=color.color
            )

            pm.button(
                'to_ass_button',
                l='To ASS',
                c=repeated_callback(Reference.to_ass),
                ann='Convert selected to ASS representation',
                bgc=color.color
            )

            pm.button(
                'to_rs_button',
                l='To RS',
                c=repeated_callback(Reference.to_rs),
                ann='Convert selected to RS representation',
                bgc=color.color
            )

            color.change()
            pm.button(
                'update_alembic_references_button',
                l='Update Alembic References',
                c=repeated_callback(auxiliary.update_alembic_references),
                ann=auxiliary.update_alembic_references.__doc__,
                bgc=color.color
            )

        # store commands
        __commands__.extend(reference_columnLayout.children())

        # ----- MODELING ------
        modeling_column_layout = pm.columnLayout(
            'modeling_column_layout',
            adj=True, cal="center", rs=row_spacing)
        with modeling_column_layout:
            color.reset()
            pm.button('toggleFaceNormalDisplay_button',
                      l="toggle face normal display",
                      c=repeated_callback(
                          pm.runtime.ToggleFaceNormalDisplay),
                      ann="toggles face normal display",
                      bgc=color.color)
            pm.button('reverseNormals_button', l="reverse normals",
                      c=repeated_callback(Modeling.reverse_normals),
                      ann="reverse normals",
                      bgc=color.color)
            pm.button('fixNormals_button', l="fix normals",
                      c=repeated_callback(Modeling.fix_normals),
                      ann="applies setToFace then conform and then "
                          "soften edge to all selected objects",
                      bgc=color.color)

            color.change()
            pm.button(
                'oyHierarchyInstancer_button',
                l="hierarchy_instancer on selected",
                c=repeated_callback(Modeling.hierarchy_instancer),
                ann="hierarchy_instancer on selected",
                bgc=color.color
            )

            color.change()
            pm.button(
                'relax_verts_button',
                l="Relax Vertices",
                c=repeated_callback(Modeling.relax_vertices),
                ann="opens relax_vertices",
                bgc=color.color
            )

            with pm.rowLayout(nc=4, adj=1):
                def smooth_edges_callback():
                    iteration = pm.intSliderGrp(
                        "smooth_edges_iteration_intField", q=1, v=1
                    )
                    Modeling.smooth_edges(iteration=iteration)
                pm.button(
                    'smooth_edges_button',
                    l="Smooth Edges",
                    c=repeated_callback(smooth_edges_callback),
                    ann=Modeling.smooth_edges.__doc__,
                    bgc=color.color
                )
                pm.intSliderGrp(
                    'smooth_edges_iteration_intField',
                    v=100,
                    min=0,
                    max=100
                )

            color.change()
            pm.button(
                'create_curve_from_mesh_edges_button',
                l="Curve From Mesh Edges",
                c=repeated_callback(Modeling.create_curve_from_mesh_edges),
                ann="Creates a curve from selected mesh edges",
                bgc=color.color
            )

            color.change()
            pm.button(
                'vertex_aligned_locator_button',
                l="Vertex Aligned Locator",
                c=repeated_callback(Modeling.vertex_aligned_locator),
                ann="Creates an aligned locator from selected vertices",
                bgc=color.color
            )

            color.change()
            with pm.rowLayout(nc=8, rat=(1, "both", 0), adj=1):
                pm.text('set_pivot_text', l='Set Pivot', bgc=color.color)
                pm.button(
                    'center_button',
                    l="C",
                    c=repeated_callback(
                        Modeling.set_pivot,
                        0
                    ),
                    bgc=(0.8, 0.8, 0.8)
                )
                pm.button(
                    'minus_X_button',
                    l="-X",
                    c=repeated_callback(
                        Modeling.set_pivot,
                        1
                    ),
                    bgc=(1.000, 0.500, 0.666)
                )
                pm.button(
                    'plus_X_button',
                    l="+X",
                    c=repeated_callback(
                        Modeling.set_pivot,
                        2
                    ),
                    bgc=(1.000, 0.500, 0.666)
                )
                pm.button(
                    'minus_Y_button',
                    l="-Y",
                    c=repeated_callback(
                        Modeling.set_pivot,
                        3
                    ),
                    bgc=(0.666, 1.000, 0.500)
                )
                pm.button(
                    'plus_Y_button',
                    l="+Y",
                    c=repeated_callback(
                        Modeling.set_pivot,
                        4
                    ),
                    bgc=(0.666, 1.000, 0.500)
                )
                pm.button(
                    'minus_Z_button',
                    l="-X",
                    c=repeated_callback(
                        Modeling.set_pivot,
                        5
                    ),
                    bgc=(0.500, 0.666, 1.000)
                )
                pm.button(
                    'plus_Z_button',
                    l="+X",
                    c=repeated_callback(
                        Modeling.set_pivot,
                        6
                    ),
                    bgc=(0.500, 0.666, 1.000)
                )

            color.change()
            with pm.rowLayout(nc=7, rat=(1, "both", 0), adj=1):
                pm.text(l='Text. Res', bgc=color.color)
                pm.button(
                    l="128",
                    c=repeated_callback(
                        Modeling.set_texture_res,
                        128
                    ),
                    bgc=Color.colors[0]
                )
                pm.button(
                    l="256",
                    c=repeated_callback(
                        Modeling.set_texture_res,
                        256
                    ),
                    bgc=Color.colors[1]
                )
                pm.button(
                    l="512",
                    c=repeated_callback(
                        Modeling.set_texture_res,
                        512
                    ),
                    bgc=Color.colors[2]
                )
                pm.button(
                    l="1024",
                    c=repeated_callback(
                        Modeling.set_texture_res,
                        1024
                    ),
                    bgc=Color.colors[3]
                )
                pm.button(
                    l='2048',
                    c=repeated_callback(
                        Modeling.set_texture_res,
                        2048
                    ),
                    bgc=Color.colors[4]
                )
                pm.button(
                    l='4096',
                    c=repeated_callback(
                        Modeling.set_texture_res,
                        4096
                    ),
                    bgc=Color.colors[5]
                )

            pm.text(l='========== UV Tools =============')

            color.change()
            pm.button(
                'fix_uvsets_button',
                l="Fix UVSets (DiffuseUV -> map1)",
                c=repeated_callback(Modeling.fix_uvsets),
                ann=Modeling.fix_uvsets,
                bgc=color.color
            )

            color.change()
            pm.button(
                'select_zero_uv_area_faces_button',
                l="Filter Zero UV Area Faces",
                c=repeated_callback(Modeling.select_zero_uv_area_faces),
                ann="Selects faces with zero uv area",
                bgc=color.color
            )

            color.change()
            pm.button(
                'create_auto_uvmap_button',
                l='Create Auto UVMap',
                c=repeated_callback(Modeling.create_auto_uvmap),
                ann=Modeling.create_auto_uvmap.__doc__,
                bgc=color.color
            )

            with pm.rowLayout(nc=6, adj=1):
                def transfer_uvs_button_callback(*args, **kwargs):
                    label_lut = {
                        'W': 0,
                        'L': 1,
                        'UV': 2,
                        'C': 3,
                        'T': 4
                    }
                    sample_space = label_lut[
                        pm.radioCollection(
                            'transfer_uvs_radio_collection',
                            q=1, sl=1
                        )
                    ]
                    Modeling.transfer_uvs(sample_space=sample_space)

                pm.button('transfer_uvs_button',
                          l="Transfer UVs",
                          c=repeated_callback(transfer_uvs_button_callback),
                          ann="Transfers UVs from one group to other, use it"
                              "for LookDev -> Alembic",
                          bgc=color.color)

                pm.radioCollection('transfer_uvs_radio_collection')
                button_with = 40
                pm.radioButton(
                    'W', w=button_with, al='left', ann='World'
                )
                pm.radioButton(
                    'L', w=button_with, al='left', ann='Local'
                )
                pm.radioButton(
                    'UV', w=button_with, al='left', ann='UV'
                )
                pm.radioButton(
                    'C', w=button_with, al='left', ann='Component', sl=1
                )
                pm.radioButton(
                    'T', w=button_with, al='left', ann='Topology'
                )

            color.change()
            pm.text(l='======= Manipulator Tools =======')
            pm.button('set_to_point_button',
                      l="Set To Point",
                      c=repeated_callback(pm.mel.eval, "manipMoveOrient 1;"),
                      ann="Set manipulator to the point",
                      bgc=color.color)

            pm.button('set_to_edge_button',
                      l="Set To Edge",
                      c=repeated_callback(pm.mel.eval, "manipMoveOrient 2;"),
                      ann="Set manipulator to the edge",
                      bgc=color.color)

            pm.button('set_to_face_button',
                      l="Set To Face",
                      c=repeated_callback(pm.mel.eval, "manipMoveOrient 3;"),
                      ann="Set manipulator to the face",
                      bgc=color.color)

            color.change()
            pm.button('create_bbox_from_selection_button',
                      l="Create BBOX from selection",
                      c=repeated_callback(Modeling.bbox_from_selection),
                      ann=Modeling.bbox_from_selection.__doc__,
                      bgc=color.color)

        # store commands
        __commands__.extend(modeling_column_layout.children())

        # ----- RIGGING ------
        rigging_columnLayout = pm.columnLayout(
            'rigging_columnLayout',
            adj=True, cal="center",
            rs=row_spacing
        )
        with rigging_columnLayout:
            color.reset()
            pm.button(
                'create_joints_on_curve_ui_button',
                l="Create Joints On Curve UI",
                c=repeated_callback(Rigging.create_joints_on_curve_ui),
                ann=Rigging.create_joints_on_curve_ui.__doc__,
                bgc=color.color
            )
            pm.button(
                'mirror_transformation_button',
                l="Mirror Transformation",
                c=repeated_callback(Rigging.mirror_transformation),
                ann=Rigging.mirror_transformation.__doc__,
                bgc=color.color
            )

            color.change()
            pm.button(
                'IKFKLimbRigger_button',
                l="IK/FK Limb Rigger",
                c=repeated_callback(Rigging.ik_fk_limb_rigger),
                ann=Rigging.ik_fk_limb_rigger.__doc__,
                bgc=color.color
            )
            with pm.rowLayout(nc=2, adj=1):
                def ik_fk_limb_rigger_callback():
                    subdivision = pm.intField('bendy_ik_fk_subdivision_count_field', q=1, v=1)
                    Rigging.bendy_ik_fk_limb_rigger(subdivision=subdivision)

                pm.button(
                    'bendy_ik_fk_limb_rigger_button',
                    l='IK/FK Limb Rigger (Bendy)',
                    c=repeated_callback(ik_fk_limb_rigger_callback),
                    ann=Rigging.bendy_ik_fk_limb_rigger.__doc__,
                    bgc=color.color
                )

                pm.intField('bendy_ik_fk_subdivision_count_field', min=0, v=2)
            pm.button(
                'ReverseFootRigger_button',
                l="Reverse Foot Rigger",
                c=repeated_callback(Rigging.reverse_foot_rigger),
                ann=Rigging.reverse_foot_rigger.__doc__,
                bgc=color.color
            )
            pm.button(
                'squashStretchBendRigger_button',
                l="Squash/Stretch/Bend Rigger",
                c=repeated_callback(Rigging.squash_stretch_bend_rigger),
                ann=Rigging.squash_stretch_bend_rigger.__doc__,
                bgc=color.color
            )
            pm.button(
                'setupStretchySplineIKCurve_button',
                l="setup stretchy splineIK curve",
                c=repeated_callback(Rigging.setup_stretchy_spline_ik_curve),
                ann="connects necessary nodes to calculate arcLength "
                    "change in percent",
                bgc=color.color
            )
            pm.button(
                'selectJointsDeformingTheObject_button',
                l="select joints deforming the object",
                c=repeated_callback(Rigging.select_joints_deforming_object),
                ann="select joints that deform the object",
                bgc=color.color
            )

            color.change()
            pm.button(
                'create_axial_correction_group_button',
                l="Create Axial Correction Groups",
                c=repeated_callback(Rigging.axial_correction_group),
                ann=Rigging.axial_correction_group.__doc__,
                bgc=color.color
            )
            pm.button(
                'create_zv_parent_compatible_groups_button',
                l="Create ZV Parent Compatible Groups",
                c=repeated_callback(Rigging.create_zv_parent_compatible_groups),
                ann=Rigging.axial_correction_group.__doc__,
                bgc=color.color
            )

            color.change()
            pm.button(
                'setClustersToAbsolute_button',
                l="set selected clusters to absolute",
                c=repeated_callback(Rigging.set_clusters_relative_state, 0),
                ann="set Clusters to Absolute",
                bgc=color.color
            )
            pm.button(
                'setClustersToRelative_button',
                l="set selected clusters to relative",
                c=repeated_callback(
                    Rigging.set_clusters_relative_state, 1
                ),
                ann="set Clusters to Relative",
                bgc=color.color
            )

            color.change()
            pm.button(
                'addControllerShape_button',
                l="add controller shape",
                c=repeated_callback(Rigging.add_controller_shape),
                ann="add the shape in the selected joint",
                bgc=color.color
            )
            pm.button(
                'replaceControllerShape_button',
                l="replace controller shape",
                c=repeated_callback(Rigging.replace_controller_shape),
                ann="replaces the shape in the selected joint",
                bgc=color.color
            )

            color.change()

            def pin_controller_callback(color, *args):
                """Creates Pin Controller on the selected Vertex
                """
                from anima.env.mayaEnv import rigging
                vertex = pm.ls(sl=1)[0]
                pc = rigging.PinController()
                pc.color = color
                pc.pin_to_vertex = vertex
                pc.setup()

            # TODO: Give the user the ability of selecting custom colors
            with pm.rowLayout(nc=4, adj=1):
                pm.text(l="Pin Controller")
                pm.button('pin_controller_red_button', l="R",
                          c=repeated_callback(pin_controller_callback, [1, 0, 0]),
                          ann=pin_controller_callback.__doc__,
                          bgc=[1, 0, 0])
                pm.button('pin_controller_green_button', l="G",
                          c=repeated_callback(pin_controller_callback, [0, 1, 0]),
                          ann=pin_controller_callback.__doc__,
                          bgc=[0, 1, 0])
                pm.button('pin_controller_blue_button', l="B",
                          c=repeated_callback(pin_controller_callback, [0, 0, 1]),
                          ann=pin_controller_callback.__doc__,
                          bgc=[0, 0, 1])

            pm.button('rivet_button', l="create rivet",
                      c=repeated_callback(mel.eval, 'rivet'),
                      ann="create rivet",
                      bgc=color.color)
            pm.button('oyAutoRivet_button', l="auto rivet",
                      c=repeated_callback(mel.eval, 'oyAutoRivet'),
                      ann="auto rivet",
                      bgc=color.color)
            pm.button(
                'oyAutoRivetFollicle_button',
                l="auto rivet (Follicle)",
                c=repeated_callback(auxiliary.auto_rivet),
                ann="creates a rivet setup by using hair follicles",
                bgc=color.color
            )
            pm.button(
                'rivet_per_face_button',
                l="rivet per face (Follicle)",
                c=repeated_callback(auxiliary.rivet_per_face),
                ann="creates a rivet setup per selected face by using hair "
                    "follicles",
                bgc=color.color
            )
            pm.button('create_hair_from_curves_button',
                      l="Create Hair From Curves",
                      c=repeated_callback(auxiliary.hair_from_curves),
                      ann="creates hair from curves",
                      bgc=color.color)

            color.change()
            pm.button('artPaintSkinWeightsTool_button',
                      l="paint weights tool",
                      c=repeated_callback(mel.eval, 'ArtPaintSkinWeightsTool'),
                      ann="paint weights tool",
                      bgc=color.color)

            def skin_tools_ui_caller(*args):
                from anima.env.mayaEnv.rigging import SkinToolsUI
                st = SkinToolsUI()
                st.ui()
            pm.button('skin_tools_button', l="Skin Tools",
                      c=skin_tools_ui_caller,
                      ann="skin tools",
                      bgc=color.color)
            pm.button('oyFixBoundJoint_button', l="fix_bound_joint",
                      c=repeated_callback(Rigging.fix_bound_joint),
                      ann="fix_bound_joint",
                      bgc=color.color)
            pm.button('toggle_local_rotation_axes_button',
                      l="Toggle Local Rotation Axes",
                      c=repeated_callback(General.toggle_attributes, "displayLocalAxis"),
                      ann="Toggle Local Rotation Axes",
                      bgc=color.color)
            pm.button('toggle_display_rotate_pivot_button',
                      l="Toggle Display Rotate Pivot",
                      c=repeated_callback(General.toggle_attributes, "displayRotatePivot"),
                      ann="Toggle Display Rotate Pivot",
                      bgc=color.color)
            pm.button('seroBlendController_button',
                      l="seroBlendController",
                      c=repeated_callback(mel.eval, 'seroBlendController'),
                      ann="seroBlendController",
                      bgc=color.color)
            pm.button('align_to_pole_vector_button',
                      l="Align To Pole Vector",
                      c=repeated_callback(auxiliary.align_to_pole_vector),
                      ann="align to pole vector",
                      bgc=color.color)

            color.change()
            pm.button('oyResetCharSet_button', l="oyResetCharSet",
                      c=repeated_callback(mel.eval, 'oyResetCharSet'),
                      ann="reset char set",
                      bgc=color.color)
            pm.button('export_blend_connections_button',
                      l="Export blend connections",
                      c=repeated_callback(auxiliary.export_blend_connections),
                      ann="export blend connections",
                      bgc=color.color)

            color.change()
            pm.button('createFollicles_button', l="create follicles",
                      c=repeated_callback(Rigging.create_follicles),
                      ann="create follicles",
                      bgc=color.color)

            color.change()
            pm.button('oyResetTweaks_button', l="reset tweaks",
                      c=repeated_callback(Rigging.reset_tweaks),
                      ann="reset tweaks",
                      bgc=color.color)

            color.change()

            def add_cacheable_attribute_callback():
                """add <b>cacheable</b> attribute to the selected nodes
                """
                for node in pm.selected():
                    Rigging.add_cacheable_attribute(node)

            pm.button('add_cacheable_attr_button', l="add `cacheable` attribute",
                      c=repeated_callback(add_cacheable_attribute_callback),
                      ann=add_cacheable_attribute_callback.__doc__,
                      bgc=color.color)

        # store commands
        __commands__.extend(rigging_columnLayout.children())


        # ----- RENDER ------
        render_columnLayout = pm.columnLayout(
            'render_columnLayout',
            adj=True,
            cal="center",
            rs=row_spacing
        )
        with render_columnLayout:
            color.reset()

            color.change()
            pm.button(
                'update_render_settings_button',
                l="Update Render Settings",
                c=repeated_callback(Render.update_render_settings),
                ann=Render.update_render_settings.__doc__,
                bgc=color.color
            )

            color.change()
            pm.button(
                'delete_render_layers_button',
                l="Delete Render Layers",
                c=repeated_callback(Render.delete_render_layers),
                ann=Render.delete_render_layers.__doc__,
                bgc=color.color
            )

            pm.button(
                'delete_display_layers_button',
                l="Delete Display Layers",
                c=repeated_callback(Render.delete_display_layers),
                ann=Render.delete_display_layers.__doc__,
                bgc=color.color
            )

            pm.button(
                'delete_render_and_display_layers_button',
                l="Delete Render and Display Layers",
                c=repeated_callback(Render.delete_render_and_display_layers),
                ann=Render.delete_render_and_display_layers.__doc__,
                bgc=color.color
            )

            color.change()
            pm.button(
                'delete_unused_shading_nodes_button',
                l="Delete Unused Shading Nodes",
                c=repeated_callback(Render.delete_unused_shading_nodes),
                ann=Render.delete_unused_shading_nodes.__doc__,
                bgc=color.color
            )

            color.change()
            pm.button(
                'duplicate_input_graph_button',
                l="Duplicate Input Graph",
                c=repeated_callback(Render.duplicate_input_graph),
                ann=Render.duplicate_input_graph.__doc__,
                bgc=color.color
            )
            pm.button(
                'duplicate_with_connections_button',
                l="Duplicate With Connections To Network",
                c=repeated_callback(Render.duplicate_with_connections),
                ann=Render.duplicate_with_connections.__doc__,
                bgc=color.color
            )

            color.change()
            pm.text(l='=========== RedShift Tools ===========')
            pm.button(
                'generate_rs_from_selection_button',
                l='Generate RSProxy From Selection',
                c=repeated_callback(Render.generate_rsproxy_from_selection),
                ann=Render.generate_rsproxy_from_selection.__doc__,
                bgc=color.color
            )

            pm.button(
                'generate_rs_from_selection_per_selection_button',
                l='Generate RSProxy From Selection (Per Selection)',
                c=repeated_callback(Render.generate_rsproxy_from_selection, True),
                ann=Render.generate_rsproxy_from_selection.__doc__,
                bgc=color.color
            )

            pm.button(
                'set_rsproxy_to_bbox_button',
                l='RSProxy -> Bounding Box',
                c=repeated_callback(Render.rsproxy_to_bounding_box),
                ann=Render.rsproxy_to_bounding_box.__doc__,
                bgc=color.color
            )

            pm.button(
                'set_rsproxy_to_preview_mesh_button',
                l='RSProxy -> Preview Mesh',
                c=repeated_callback(Render.rsproxy_to_preview_mesh),
                ann=Render.rsproxy_to_preview_mesh.__doc__,
                bgc=color.color
            )

            color.change()
            pm.text(l='===== RedShift IC + IPC Bake =====')
            pm.button(
                'redshift_ic_ipc_bake_button',
                l="Do Bake",
                c=repeated_callback(Render.redshift_ic_ipc_bake),
                ann=Render.redshift_ic_ipc_bake.__doc__,
                bgc=color.color
            )
            pm.button(
                'redshift_ic_ipc_bake_restore_button',
                l="Restore Settings",
                c=repeated_callback(Render.redshift_ic_ipc_bake_restore),
                ann=Render.redshift_ic_ipc_bake_restore.__doc__,
                bgc=color.color
            )
            pm.text(l='======================================')

            color.change()
            pm.button(
                'submit_afanasy_button',
                l="Afanasy Job Submitter",
                c=repeated_callback(Render.afanasy_job_submitter),
                ann=Render.afanasy_job_submitter.__doc__,
                bgc=color.color
            )

            color.change()
            pm.button(
                'open_node_in_browser_button',
                l="Open node in browser",
                c=repeated_callback(Render.open_node_in_browser),
                ann="Open node in browser",
                bgc=color.color
            )

            color.change()
            pm.button('auto_convert_to_redshift_button',
                      l="Auto Convert Scene To RedShift (BETA)",
                      c=repeated_callback(Render.auto_convert_to_redshift),
                      ann="Automatically converts the scene from Arnold to "
                          "Redshift, including materials and lights",
                      bgc=color.color)

            pm.button('convert_nodes_to_redshift_button',
                      l="Convert Selected To RedShift (BETA)",
                      c=repeated_callback(Render.convert_nodes_to_redshift),
                      ann="Automatically converts the selected node from "
                          "Arnold to Redshift",
                      bgc=color.color)

            def set_shape_attribute_wrapper(attr_name, value):
                """a wrapper function for set_shape_attribute
                """
                apply_to_hierarchy = pm.checkBox(
                    apply_to_hierarchy_checkBox,
                    q=True,
                    v=True
                )
                disable_undo = pm.checkBox(
                    disable_undo_queue_check_box,
                    q=True,
                    v=True
                )

                Render.set_shape_attribute(
                    attr_name,
                    value,
                    apply_to_hierarchy,
                    disable_undo
                )

            with pm.rowLayout(nc=3, rat=(1, "both", 0), adj=1):
                pm.text('renderThumbnailUpdate_text',
                        l="renderThumbnailUpdate",
                        bgc=color.color)
                pm.button('set_renderThumbnailUpdate_ON_button',
                          l="ON",
                          c=repeated_callback(pm.renderThumbnailUpdate, 1),
                          bgc=(0, 1, 0))
                pm.button('set_renderThumbnailUpdate_OFF_button',
                          l="OFF",
                          c=repeated_callback(pm.renderThumbnailUpdate, 0),
                          bgc=(1, 0, 0))

            color.change()
            pm.button('replaceShadersWithLast_button',
                      l="replace shaders with last",
                      c=repeated_callback(Render.replace_shaders_with_last),
                      ann="replace shaders with last",
                      bgc=color.color)

            color.change()
            pm.button('createTextureRefObject_button',
                      l="create texture ref. object",
                      c=repeated_callback(Render.create_texture_ref_object),
                      ann="create texture ref. object",
                      bgc=color.color)

            pm.text(l='========== Texture Tools =============')

            color.change()
            pm.button('assign_substance_textures_button',
                      l="Assign Substance Textures",
                      c=repeated_callback(Render.assign_substance_textures),
                      ann=Render.assign_substance_textures.__doc__,
                      bgc=color.color)

            color.change()
            pm.button('normalize_texture_paths_button',
                      l="Normalize Texture Paths (remove $)",
                      c=repeated_callback(Render.normalize_texture_paths),
                      ann=Render.normalize_texture_paths.__doc__,
                      bgc=color.color)

            pm.button('unnormalize_texture_paths_button',
                      l="Unnormalize Texture Paths (add $)",
                      c=repeated_callback(Render.unnormalize_texture_paths),
                      ann=Render.unnormalize_texture_paths.__doc__,
                      bgc=color.color)

            color.change()
            pm.button('assign_random_material_color_button',
                      l="Assign Material with Random Color",
                      c=repeated_callback(Render.assign_random_material_color),
                      ann=Render.assign_random_material_color.__doc__,
                      bgc=color.color)

            pm.button('randomize_material_color_button',
                      l="Randomize Material Color",
                      c=repeated_callback(Render.randomize_material_color),
                      ann=Render.randomize_material_color.__doc__,
                      bgc=color.color)

            color.change()
            pm.button('import_image_as_plane_button',
                      l="Import Image as Plane",
                      c=repeated_callback(Render.import_image_as_plane),
                      ann=Render.import_image_as_plane.__doc__,
                      bgc=color.color)

            pm.text(l='============ Camera Tools ============')
            color.change()
            pm.button(
                'CameraFilmOffsetTool_button',
                l="Camera Film Offset Tool",
                c=repeated_callback(
                    camera_tools.camera_film_offset_tool
                ),
                ann="Camera Film Offset Tool",
                bgc=color.color
            )

            def camera_focus_plane_tool_callback():
                """callback for the camera_focus_plane_tool
                """
                camera = pm.ls(sl=1)[0]
                camera_tools.camera_focus_plane_tool(camera)

            pm.button(
                'CameraFocusPlaneTool_button',
                l="Camera Focus Plane Tool",
                c=repeated_callback(camera_focus_plane_tool_callback),
                ann="Camera Film Offset Tool",
                bgc=color.color
            )

            pm.button(
                'lock_tracked_camera_channels_button',
                l="Lock Tracked Camera Channels",
                c=repeated_callback(camera_tools.lock_tracked_camera_channels),
                ann=camera_tools.lock_tracked_camera_channels.__doc__,
                bgc=color.color
            )

            color.change()
            pm.text(l='===== Vertigo =====')
            pm.button('vertigo_setup_look_at_button',
                      l="Setup -> Look At",
                      c=repeated_callback(Render.vertigo_setup_look_at),
                      ann="Setup Look At",
                      bgc=color.color)
            pm.button('vertigo_setup_vertigo_button',
                      l="Setup -> Vertigo",
                      c=repeated_callback(Render.vertigo_setup_vertigo),
                      ann="Setup Vertigo",
                      bgc=color.color)
            pm.button('vertigo_delete_button',
                      l="Delete",
                      c=repeated_callback(Render.vertigo_delete),
                      ann="Delete",
                      bgc=color.color)
            pm.text(l='===================')

            pm.button('oyTracker2Null_button', l="oyTracker2Null",
                      c=repeated_callback(mel.eval, 'oyTracker2Null'),
                      ann="Tracker2Null",
                      bgc=color.color)

            with pm.rowLayout(nc=3, adj=1):
                def import_3dequalizer_points_callback():
                    """callback for Import 3DEqualizer points
                    """
                    cam_width = pm.intField('import_3DEqualizer_points_width_int_field', q=1, v=1)
                    cam_height = pm.intField('import_3DEqualizer_points_height_int_field', q=1, v=1)
                    camera_tools.import_3dequalizer_points(cam_width, cam_height)

                pm.button(
                    'import_3DEqualizer_points_button', l="Import 3DEqualizer Points",
                    c=repeated_callback(import_3dequalizer_points_callback),
                    ann=camera_tools.import_3dequalizer_points.__doc__,
                    bgc=color.color
                )
                pm.intField('import_3DEqualizer_points_width_int_field', min=1, v=1920)
                pm.intField('import_3DEqualizer_points_height_int_field', min=1, v=1080)

            pm.text(l='===================')

            color.change()
            pm.button('reloadFileTextures_button',
                      l="reload file textures",
                      c=repeated_callback(Render.reload_file_textures),
                      ann="reload file textures",
                      bgc=color.color)

            color.change()
            pm.button('transfer_shaders_button',
                      l="Transfer Shaders",
                      c=repeated_callback(Render.transfer_shaders),
                      ann="Transfers shaders from one group to other, use it"
                          "for LookDev -> Alembic",
                      bgc=color.color)

            color.change()
            pm.button('fitPlacementToUV_button',
                      l="fit placement to UV",
                      c=repeated_callback(Render.fit_placement_to_UV),
                      ann="fit placement to UV",
                      bgc=color.color)

            pm.button(
                'connect_placement2d_to_file_texture_button',
                l='Connect Placement2D to File Texture',
                c=repeated_callback(Render.connect_placement2d_to_file),
                ann=Render.connect_placement2d_to_file.__doc__,
                bgc=color.color
            )

            color.change()
            with pm.rowLayout(nc=2, adj=1):
                def enable_subdiv_callback():
                    max_tess = pm.intField('enable_subdiv_int_field', q=1, v=1)
                    Render.enable_subdiv_on_selected(
                        max_subdiv=max_tess, fixed_tes=False
                    )

                pm.button(
                    'enable_subdiv_on_selected_objects_button',
                    l='Enable Subdiv (Adaptive)',
                    c=repeated_callback(enable_subdiv_callback),
                    ann='Enables Arnold/RedShift Subdiv (catclark) on '
                        'selected objects',
                    bgc=color.color
                )

                pm.intField('enable_subdiv_int_field', min=0, v=3)

            with pm.rowLayout(nc=2, adj=1):
                def fixed_tess_callback():
                    max_tess = pm.intField('fixed_tess_int_field', q=1, v=1)
                    Render.enable_subdiv_on_selected(
                        fixed_tes=True, max_subdiv=max_tess
                    )

                pm.button(
                    'enable_fixed_subdiv_on_selected_objects_button',
                    l='Enable Subdiv (Fixed Tes.)',
                    c=repeated_callback(fixed_tess_callback),
                    ann='Enables Arnold/RedShift Subdiv (catclark) on selected '
                        'objects with fixed tessellation',
                    bgc=color.color
                )

                pm.intField('fixed_tess_int_field', min=0, v=1)

            pm.button(
                'disable_subdiv_on_selected_objects_button',
                l='Disable Subdiv',
                c=repeated_callback(Render.disable_subdiv_on_selected),
                ann=Render.disable_subdiv.__doc__,
                bgc=color.color
            )

            color.change()
            pm.button(
                'export_shader_data_button',
                l='Export Shader Attributes',
                c=repeated_callback(Render.export_shader_attributes),
                ann=Render.export_shader_attributes.__doc__,
                bgc=color.color
            )
            pm.button(
                'import_shader_data_button',
                l='Import Shader Attributes',
                c=repeated_callback(Render.import_shader_attributes),
                ann=Render.import_shader_attributes.__doc__,
                bgc=color.color
            )

            color.change()
            pm.button(
                'export_shader_to_houdini_button',
                l='Export Shader Assignments To Houdini',
                c=repeated_callback(Render.export_shader_assignments_to_houdini),
                ann=Render.export_shader_assignments_to_houdini.__doc__,
                bgc=color.color
            )

            color.change()
            pm.button(
                'create_eye_shader_and_controls_button',
                l='Create Eye Shader and Controls',
                c=repeated_callback(Render.create_eye_shader_and_controls),
                ann='Creates eye shaders and controls for the selected eyes',
                bgc=color.color
            )
            pm.button(
                'setup_outer_eye_render_attributes_button',
                l='Setup Outer Eye Render Attributes',
                c=repeated_callback(Render.setup_outer_eye_render_attributes),
                ann=Render.setup_outer_eye_render_attributes.__doc__,
                bgc=color.color
            )
            pm.button(
                'setup_window_glass_render_attributes_button',
                l='Setup **Window Glass** Render Attributes',
                c=repeated_callback(Render.setup_window_glass_render_attributes),
                ann=Render.setup_window_glass_render_attributes.__doc__,
                bgc=color.color
            )
            pm.button(
                'setup_dummy_window_light_button',
                l='Setup/Update **Dummy Window** Light Plane',
                c=repeated_callback(Render.dummy_window_light_plane),
                ann=Render.dummy_window_light_plane.__doc__,
                bgc=color.color
            )

            color.change()
            pm.button(
                'create_generic_tooth_shader_button',
                l='Create Generic TOOTH Shader',
                c=repeated_callback(Render.create_generic_tooth_shader),
                ann=Render.create_generic_gum_shader.__doc__,
                bgc=color.color
            )
            pm.button(
                'create_generic_gum_shader_button',
                l='Create Generic GUM Shader',
                c=repeated_callback(Render.create_generic_gum_shader),
                ann=Render.create_generic_gum_shader.__doc__,
                bgc=color.color
            )
            pm.button(
                'create_generic_tongue_shader_button',
                l='Create Generic TONGUE Shader',
                c=repeated_callback(Render.create_generic_tongue_shader),
                ann=Render.create_generic_tongue_shader.__doc__,
                bgc=color.color
            )

            color.change()
            pm.button('convert_to_ai_image_button',
                      l="To aiImage",
                      c=repeated_callback(
                          Render.convert_file_node_to_ai_image_node),
                      ann="Converts the selected File (file texture) nodes to "
                          "aiImage nodes, also connects the place2dTexture "
                          "node if necessary",
                      bgc=color.color)

            color.change()
            pm.button('to_bbox_button',
                      l="aiStandIn To BBox",
                      c=repeated_callback(Render.standin_to_bbox),
                      ann="Convert selected stand ins to bbox",
                      bgc=color.color)

            pm.button('to_polywire_button',
                      l="aiStandIn To Polywire",
                      c=repeated_callback(Render.standin_to_polywire),
                      ann="Convert selected stand ins to polywire",
                      bgc=color.color)

            color.change()
            with pm.rowLayout(nc=3, adj=3, bgc=color.color):
                min_range_field = pm.floatField(
                    minValue=1000,
                    maxValue=50000,
                    step=1,
                    pre=0,
                    value=3500,
                    w=50,
                    bgc=color.color,
                    ann='Min Value'
                )
                max_range_field = pm.floatField(
                    minValue=1000,
                    maxValue=50000,
                    step=1,
                    pre=0,
                    value=6500,
                    w=50,
                    bgc=color.color,
                    ann='Max Value'
                )
                pm.button(
                    ann="Randomize Color Temperature",
                    l="Randomize Color Temp.",
                    w=70,
                    c=repeated_callback(
                        Render.randomize_light_color_temp,
                        min_range_field,
                        max_range_field
                    ),
                    bgc=color.color
                )

            with pm.rowLayout(nc=3, adj=3, bgc=color.color):
                min_range_field = pm.floatField(
                    minValue=0,
                    maxValue=200,
                    step=0.1,
                    pre=1,
                    value=10,
                    w=50,
                    bgc=color.color,
                    ann='Min Value'
                )
                max_range_field = pm.floatField(
                    minValue=0,
                    maxValue=200,
                    step=0.1,
                    pre=1,
                    value=20,
                    w=50,
                    bgc=color.color,
                    ann='Max Value'
                )
                pm.button(
                    ann="Randomize Exposure",
                    l="Randomize Exposure",
                    w=70,
                    c=repeated_callback(
                        Render.randomize_light_intensity,
                        min_range_field,
                        max_range_field
                    ),
                    bgc=color.color
                )

            color.change()
            pm.button(
                ann="Create Reflection Curve",
                l="Reflection Curve",
                c=repeated_callback(
                    Render.generate_reflection_curve
                ),
                bgc=color.color
            )

            color.change()
            pm.button(
                ann="Import GPU Content",
                l="Import GPU Content",
                c=repeated_callback(
                    Render.import_gpu_content
                ),
                bgc=color.color
            )

            color.change()
            with pm.rowLayout(nc=3, adj=3, bgc=color.color):
                source_driver_field = pm.textField(
                    text='S:',
                    w=50,
                    bgc=color.color,
                    ann='Source Driver'
                )
                target_driver_field = pm.textField(
                    text='L:',
                    w=50,
                    bgc=color.color,
                    ann='Target Driver'
                )
                pm.button(
                    ann="Move Cache Files to Another Location",
                    l="Move Cache Files",
                    w=70,
                    c=repeated_callback(
                        Render.move_cache_files_wrapper,
                        source_driver_field,
                        target_driver_field
                    ),
                    bgc=color.color
                )

        # store commands
        __commands__.extend(render_columnLayout.children())


        # ----- PREVIS ------
        previs_columnLayout = pm.columnLayout(
            'previs_columnLayout',
            adj=True,
            cal="center",
            rs=row_spacing
        )
        with previs_columnLayout:
            color.reset()

            pm.button('split_camera_button',
                      l="Split Camera",
                      c=repeated_callback(Previs.split_camera),
                      ann=Previs.split_camera.__doc__,
                      bgc=color.color)

            color.change()
            pm.button('shots_from_camera_button',
                      l="Shots From Camera",
                      c=repeated_callback(Previs.shots_from_cams),
                      ann=Previs.shots_from_cams.__doc__,
                      bgc=color.color)

            color.change()
            pm.button('auto_rename_shots_button',
                      l="Auto Rename Shots",
                      c=repeated_callback(Previs.auto_rename_shots),
                      ann=Previs.auto_rename_shots.__doc__,
                      bgc=color.color)

            color.change()
            pm.button('save_previs_to_shots_button',
                      l="Save Previs To Shots",
                      c=repeated_callback(Previs.save_previs_to_shots),
                      ann=Previs.save_previs_to_shots.__doc__,
                      bgc=color.color)

            color.change()
            pm.button('very_nice_camera_rig_button',
                      l="Create a Very Nice Camera Rig",
                      c=repeated_callback(camera_tools.very_nice_camera_rig),
                      ann=camera_tools.very_nice_camera_rig.__doc__,
                      bgc=color.color)

        # store commands
        __commands__.extend(previs_columnLayout.children())


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
                      c=repeated_callback(picker.set_parent),
                      ann="Set Parent",
                      bgc=color.color)
            pm.button('picker_releaseObject_button',
                      l="Release",
                      c=repeated_callback(picker.release_object),
                      ann="Release Object",
                      bgc=color.color)
            pm.button('picker_editKeyframes_button',
                      l="Edit Keyframes",
                      c=repeated_callback(picker.edit_keyframes),
                      ann="Edit Keyframes",
                      bgc=color.color)
            pm.button('picker_fixJump_button',
                      l="Fix Jump",
                      c=repeated_callback(picker.fix_jump),
                      ann="Fix Jump",
                      bgc=color.color)
            pm.button('picker_explodeSetup_button',
                      l="Explode",
                      c=repeated_callback(picker.explode_setup),
                      ann="Explode Setup",
                      bgc=color.color)

            color.change()
            from anima.env.mayaEnv import pivot_switcher

            pm.text(l='===== Pivot Switcher =====')
            pm.button('oyPivotSwitcher_setupPivot_button',
                      l="Setup",
                      c=repeated_callback(pivot_switcher.setup_pivot),
                      ann="Setup Pivot",
                      bgc=color.color)
            pm.button('oyPivotSwitcher_switchPivot_button',
                      l="Switch",
                      c=repeated_callback(pivot_switcher.switch_pivot),
                      ann="Switch Pivot",
                      bgc=color.color)
            pm.button('oyPivotSwitcher_togglePivot_button',
                      l="Toggle",
                      c=repeated_callback(pivot_switcher.toggle_pivot),
                      ann="Toggle Pivot",
                      bgc=color.color)

            color.change()
            pm.text(l='===== Alembic Tools =====')

            pm.button('bake_all_constraints_button',
                      l="Bake All Constraints",
                      c=repeated_callback(Animation.bake_all_constraints),
                      ann=Animation.bake_all_constraints.__doc__,
                      bgc=color.color)

            pm.button('bake_alembic_animations_button',
                      l="Bake Alembic Animations",
                      c=repeated_callback(Animation.bake_alembic_animations),
                      ann=Animation.bake_alembic_animations.__doc__,
                      bgc=color.color)

            rowLayout = pm.rowLayout(nc=2, adj=1, bgc=color.color)
            with rowLayout:
                pm.button(
                    'abc_from_selected_button',
                    l='From Selected',
                    c=repeated_callback(Animation.create_alembic_command),
                    ann='Creates Alembic Cache from selected nodes',
                    bgc=color.color
                )
                from_top_node_checkBox = pm.checkBox(
                    'from_top_node_checkBox',
                    l="Top Node",
                    value=True,
                    bgc=color.color
                )

            # pm.button(
            #     'abc_from_source_to_target_button',
            #     l='Source -> Target',
            #     c=repeated_callback(Animation.copy_alembic_data),
            #     ann='Copy Alembic Data from Source to Target by the matching '
            #         'node names',
            #     bgc=color.color
            # )

            # rowLayout = pm.rowLayout(nc=2, adj=1, bgc=color.color)
            pm.text(l='===== EXPORT =====')
            with pm.rowLayout(nc=3, adj=3):
                pm.checkBoxGrp(
                    'export_alembic_of_nodes_checkbox_grp',
                    l='Alembic Options',
                    numberOfCheckBoxes=2,
                    labelArray2=['Isolate', 'Unload Refs'],
                    cl3=['left', 'left', 'left'],
                    cw3=[100, 60, 60],
                    valueArray2=[1, 1]
                )

            pm.intFieldGrp(
                'export_alembic_of_nodes_handles_int_slider_grp',
                l='Handles',
                el='frames',
                nf=1,
                adj=2,
                cw3=[65, 1, 20],
                v1=1,
            )

            def export_alembic_callback_with_options(func):
                """calls the function with the parameters from the ui

                :param func:
                :return:
                """
                isolate, unload_refs = pm.checkBoxGrp(
                    'export_alembic_of_nodes_checkbox_grp',
                    q=1,
                    valueArray2=1
                )
                handles = pm.intFieldGrp('export_alembic_of_nodes_handles_int_slider_grp', q=1, v1=1)
                func(isolate=isolate, unload_refs=unload_refs, handles=handles)

            pm.button(
                'export_alembic_of_selected_cacheable_nodes_button',
                l='Selected Cacheable Nodes',
                c=repeated_callback(export_alembic_callback_with_options, auxiliary.export_alembic_of_selected_cacheable_nodes),
                ann=auxiliary.export_alembic_of_selected_cacheable_nodes.__doc__.split('\n')[0],
                bgc=color.color
            )
            pm.button(
                'export_alembic_of_all_cacheable_nodes_button',
                l='ALL Cacheable Nodes',
                c=repeated_callback(export_alembic_callback_with_options, auxiliary.export_alembic_of_all_cacheable_nodes),
                ann=auxiliary.export_alembic_of_all_cacheable_nodes.__doc__.split('\n')[0],
                bgc=color.color
            )

            pm.button(
                'export_alembic_on_farm_button',
                l='Export Alembic On Farm',
                c=repeated_callback(Animation.export_alembics_on_farm),
                ann=Animation.export_alembics_on_farm.__doc__.split('\n')[0],
                bgc=color.color
            )

            pm.text(l='===== Playblast Tools =====')
            color.change()
            pm.button(
                'playblast_on_farm_button',
                l='PLayblast On Farm',
                c=repeated_callback(Animation.playblast_on_farm),
                ann=Animation.playblast_on_farm.__doc__.split('\n')[0],
                bgc=color.color
            )

            pm.text(l='===== Exporters =====')
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
                          c=repeated_callback(
                              Animation.cam_2_chan,
                              startButtonField,
                              endButtonField
                          ),
                          bgc=color.color)

            pm.text(l='===== Component Animation =====')
            color.change()
            smooth_selected_keyframes_text_fbg = pm.textFieldButtonGrp(
                'smooth_selected_keyframes_text_fbg_button',
                bl="Smooth Selected Keyframes",
                adj=2, tx=1, cw=(1, 40),
                ann="select keyframes in graph editor to smooth",
                bgc=color.color
            )

            def smooth_selected_keyframes_text_fbg_callback():
                iteration = int(
                    pm.textFieldButtonGrp(
                        "smooth_selected_keyframes_text_fbg_button", q=1, tx=1
                    )
                )
                Animation.smooth_selected_keyframes(iteration)

            pm.textFieldButtonGrp(
                smooth_selected_keyframes_text_fbg,
                e=1,
                bc=repeated_callback(
                    smooth_selected_keyframes_text_fbg_callback
                )
            )

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
                bc=repeated_callback(
                    Animation.smooth_component_animation,
                    smooth_component_anim
                )
            )

            color.change()
            pm.button(
                'bake_component_animation_button',
                l='Bake component animation to Locator',
                c=repeated_callback(Animation.bake_component_animation),
                ann='Creates a locator at the center of selected components '
                    'and moves it with the components along the current '
                    'frame range',
                bgc=color.color
            )

            pm.button(
                'create_follicle_button',
                l='Attach Follicle',
                c=repeated_callback(Animation.attach_follicle),
                ann='Attaches a follicle in the selected components',
                bgc=color.color
            )

            pm.button(
                'equalize_node_speed_button',
                l='Equalize Node Speed',
                c=repeated_callback(Animation.equalize_node_speed),
                ann=Animation.equalize_node_speed.__doc__,
                bgc=color.color
            )

            pm.text(l='===== Generic Tools =====')

            color.change()
            pm.button(
                'set_range_from_shot_node_button',
                l='Range From Shot',
                c=repeated_callback(Animation.set_range_from_shot),
                ann='Sets the playback range from the shot node in the scene',
                bgc=color.color
            )

            color.change()
            pm.button(
                'delete_base_anim_layer_button',
                l='Delete Base Anim Layer',
                c=repeated_callback(Animation.delete_base_anim_layer),
                ann=Animation.delete_base_anim_layer.__doc__,
                bgc=color.color
            )

        # store commands
        __commands__.extend(animation_columnLayout.children())


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
                      c=repeated_callback(Render.add_miLabel),
                      ann="add miLabel to selected",
                      bgc=color.color)

            color.change()
            pm.button('connectFacingRatioToVCoord_button',
                      l="connect facingRatio to vCoord",
                      c=repeated_callback(
                          Render.connect_facingRatio_to_vCoord),
                      ann="connect facingRatio to vCoord",
                      bgc=color.color)
            color.change()

            with pm.rowLayout(nc=3, rat=(1, "both", 0), adj=1):
                pm.text('miFinalGatherCast_text',
                        l="miFinalGatherCast",
                        bgc=color.color)
                pm.button('set_miFinalGatherCast_ON_button', l="ON",
                          c=repeated_callback(
                              set_shape_attribute_wrapper,
                              "miFinalGatherCast",
                              1
                          ),
                          bgc=(0, 1, 0))
                pm.button('set_miFinalGatherCast_OFF_button', l="OFF",
                          c=repeated_callback(
                              set_shape_attribute_wrapper,
                              "miFinalGatherCast",
                              0
                          ),
                          bgc=(1, 0, 0))

            with pm.rowLayout(nc=3, rat=(1, "both", 0), adj=1):
                pm.text('miFinalGatherReceive_text',
                        l="miFinalGatherReceive",
                        bgc=color.color)
                pm.button('set_miFinalGatherReceive_ON_button', l="ON",
                          c=repeated_callback(
                              set_shape_attribute_wrapper,
                              "miFinalGatherReceive",
                              1
                          ),
                          bgc=(0, 1, 0))
                pm.button('set_miFinalGatherReceive_OFF_button',
                          l="OFF",
                          c=repeated_callback(
                              set_shape_attribute_wrapper,
                              "miFinalGatherReceive",
                              0
                          ),
                          bgc=(1, 0, 0))

            with pm.rowLayout(nc=3, rat=(1, "both", 0), adj=1):
                pm.text('miFinalGatherHide_text',
                        l="miFinalGatherHide",
                        bgc=color.color)
                pm.button('set_miFinalGatherHide_ON_button', l="ON",
                          c=repeated_callback(Render.set_finalGatherHide, 1),
                          bgc=(0, 1, 0))
                pm.button('set_miFinalGatherHide_OFF_button', l="OFF",
                          c=repeated_callback(Render.set_finalGatherHide, 0),
                          bgc=(1, 0, 0))

            color.change()
            pm.button('convertToMRTexture_button',
                      l="use mib_texture_filter_lookup",
                      c=repeated_callback(
                          Render.use_mib_texture_filter_lookup),
                      ann=(
                          "adds an mib_texture_filter_lookup node in \n" +
                          "between the file nodes and their outputs, to \n" +
                          "get a sharper look output from the texture file"),
                      bgc=color.color)
            pm.button('convertToLinear_button',
                      l="convert to Linear texture",
                      c=repeated_callback(Render.convert_to_linear),
                      ann="convert to Linear texture",
                      bgc=color.color)
            pm.button('useImageSequence_button',
                      l="use image sequence for \nmentalrayTexture",
                      c=repeated_callback(Render.use_image_sequence),
                      ann="use image sequence for \nmentalrayTexture",
                      bgc=color.color)

            color.change()
            pm.button('oyAddToSelectedContainer_button',
                      l="add to selected container",
                      c=repeated_callback(Render.add_to_selected_container),
                      ann="add to selected container",
                      bgc=color.color)
            pm.button('oyRemoveFromContainer_button',
                      l="remove from selected container",
                      c=repeated_callback(Render.remove_from_container),
                      ann="remove from selected container",
                      bgc=color.color)

            color.change()
            pm.button('oySmedgeRenderSlicer_button',
                      l="oySmedgeRenderSlicer",
                      c=repeated_callback(mel.eval, 'oySmedgeRenderSlicer'),
                      ann="SmedgeRenderSlicer",
                      bgc=color.color)

            color.change()
            pm.button(
                'exponentialSmooth_button',
                l="exponential smooth",
                c=repeated_callback(Modeling.polySmoothFace, 0),
                ann="applies exponential smooth to selected objects",
                bgc=color.color
            )
            pm.button(
                'linearSmooth_button',
                l="linear smooth",
                c=repeated_callback(Modeling.polySmoothFace, 1),
                ann="applies linear smooth to selected objects",
                bgc=color.color
            )
            pm.button(
                'deActivateSmooth_button',
                l="deActivate smooth",
                c=repeated_callback(Modeling.activate_deActivate_smooth, 1),
                ann="deActivates all polySmoothFace nodes in the "
                    "scene",
                bgc=color.color
            )
            pm.button(
                'activateSmooth_button',
                l="activate smooth",
                c=repeated_callback(Modeling.activate_deActivate_smooth, 0),
                ann="activates all deActivated polySmoothFace nodes "
                    "in the scene",
                bgc=color.color
            )
            pm.button(
                'deleteSmooth_button',
                l="delete smooth",
                c=repeated_callback(Modeling.delete_smooth),
                ann="deletes all the polySmoothFace nodes from the "
                    "scene",
                bgc=color.color
            )
            pm.button(
                'deleteSmoothOnSelected_button',
                l="delete smooth on selected",
                c=repeated_callback(Modeling.delete_smooth_on_selected),
                ann="deletes selected polySmoothFace nodes from scene",
                bgc=color.color
            )

            color.change()
            pm.button(
                'deleteAllSound_button', l="delete all sound",
                c=repeated_callback(General.delete_all_sound),
                ann="delete all sound",
                bgc=color.color
            )

            pm.button(
                'displayHandlesOfSelectedObjects_button',
                l="toggle handles of selected objects",
                c=repeated_callback(
                    General.toggle_attributes,
                    "displayHandle"
                ),
                ann="select objects to toggle handle",
                bgc=color.color
            )

            color.change()
            pm.button(
                'referenceSelectedObjects_button',
                l="reference selected objects",
                c=repeated_callback(
                    General.reference_selected_objects
                ),
                ann="sets objects display override to reference",
                bgc=color.color
            )

            pm.button(
                'dereferenceSelectedObjects_button',
                l="de-reference selected objects",
                c=repeated_callback(
                    General.dereference_selected_objects
                ),
                ann="sets objects display override to reference",
                bgc=color.color
            )

            color.change()
            pm.button(
                'oyDeReferencer_button', l="dereferencer",
                c=repeated_callback(General.dereferencer),
                ann="sets all objects display override  to normal",
                bgc=color.color
            )

            color.change()
            enable_matte_row_layout = pm.rowLayout(nc=6, adj=1)
            with enable_matte_row_layout:
                pm.text(
                    l='Enable Arnold Matte',
                )
                pm.button(
                    l='Default',
                    c=repeated_callback(Render.enable_matte, 0),
                    ann='Enables Arnold Matte on selected objects with <b>No Color</b>',
                    bgc=color.color
                )
                pm.button(
                    l='R',
                    c=repeated_callback(Render.enable_matte, 1),
                    ann='Enables Arnold Matte on selected objects with <b>Red</b>',
                    bgc=[1, 0, 0]
                )
                pm.button(
                    l='G',
                    c=repeated_callback(Render.enable_matte, 2),
                    ann='Enables Arnold Matte on selected objects with <b>Green</b>',
                    bgc=[0, 1, 0]
                )
                pm.button(
                    l='B',
                    c=repeated_callback(Render.enable_matte, 3),
                    ann='Enables Arnold Matte on selected objects with <b>Blue</b>',
                    bgc=[0, 0, 1]
                )
                pm.button(
                    l='A',
                    c=repeated_callback(Render.enable_matte, 4),
                    ann='Enables Arnold Matte on selected objects with <b>Alpha</b>',
                    bgc=[0.5, 0.5, 0.5]
                )

            color.change()
            pm.button(
                'fix_render_layer_out_adjustment_errors_button',
                l="fixRenderLayerOutAdjustmentErrors",
                c='pm.mel.eval("fixRenderLayerOutAdjustmentErrors();")',
                ann="fixRenderLayerOutAdjustmentErrors",
                bgc=color.color
            )

            pm.separator()
            color.change()
            with pm.rowLayout(nc=2, adj=2):
                apply_to_hierarchy_checkBox = pm.checkBox(
                    'apply_to_hierarchy_checkBox',
                    l="Apply to Hierarchy",
                    value=True,
                    bgc=color.color
                )

                disable_undo_queue_check_box = pm.checkBox(
                    'disable_undo_queue_checkBox',
                    l="Disable Undo",
                    value=False,
                    bgc=color.color
                )

            attr_names = [
                'castsShadows', 'receiveShadows', 'motionBlur',
                'primaryVisibility', 'visibleInReflections',
                'visibleInRefractions', 'aiSelfShadows', 'aiOpaque',
                'aiVisibleInDiffuse', 'aiVisibleInGlossy', 'aiMatte',
                'overrideShaders'
            ]
            for attr_name in attr_names:
                with pm.rowLayout(nc=4, rat=(1, "both", 0), adj=1):
                    pm.text('%s_text' % attr_name, l=attr_name, bgc=color.color)
                    pm.button(
                        'set_%s_ON_button' % attr_name,
                        l="ON",
                        c=repeated_callback(
                            set_shape_attribute_wrapper,
                            attr_name,
                            1,
                        ),
                        bgc=(0, 1, 0)
                    )
                    pm.button(
                        'set_%s_OFF_button' % attr_name,
                        l="OFF",
                        c=repeated_callback(
                            set_shape_attribute_wrapper,
                            attr_name,
                            0
                        ),
                        bgc=(1, 0, 0)
                    )
                    pm.button(
                        'set_%s_REMOVE_button' % attr_name,
                        l="REM",
                        ann='Remove Override',
                        c=repeated_callback(
                            set_shape_attribute_wrapper,
                            attr_name,
                            -1
                        ),
                        bgc=(0, 0.5, 1)
                    )

            pm.separator()
            color.change()

            pm.button(
                l='Setup Z-Layer',
                c=repeated_callback(Render.create_z_layer),
                ann=Render.create_z_layer.__doc__,
                bgc=color.color
            )

            pm.button(
                l='Setup EA Matte',
                c=repeated_callback(Render.create_ea_matte),
                ann=Render.create_ea_matte.__doc__,
                bgc=color.color
            )

            color.change()
            pm.text(l='===== BarnDoor Simulator =====')

            pm.button(
                'barn_door_simulator_setup_button',
                l='Setup',
                c=repeated_callback(Render.barndoor_simulator_setup),
                ann='Creates a arnold barn door simulator to the selected '
                    'light',
                bgc=color.color
            )

            pm.button(
                'barn_door_simulator_unsetup_button',
                l='Un-Setup',
                c=repeated_callback(Render.barndoor_simulator_unsetup),
                ann='Removes the barn door simulator nodes from the selected '
                    'light',
                bgc=color.color
            )

            pm.button(
                'fix_barndoors_button',
                l='Fix BarnDoors',
                c=repeated_callback(Render.fix_barndoors),
                ann=Render.fix_barndoors.__doc__,
                bgc=color.color
            )

            color.change()
            pm.button(
                'ai_skin_sss_to_ai_skin_button',
                l='aiSkinSSS --> aiSkin',
                c=repeated_callback(Render.convert_aiSkinSSS_to_aiSkin),
                ann=Render.convert_aiSkinSSS_to_aiSkin.__doc__,
                bgc=color.color
            )
            pm.button(
                'normalize_sss_weights_button',
                l='Normalize SSS Weights',
                c=repeated_callback(Render.normalize_sss_weights),
                ann=Render.normalize_sss_weights.__doc__,
                bgc=color.color
            )

        # store commands
        __commands__.extend(obsolete_columnLayout.children())


    pm.tabLayout(
        main_tab_layout,
        edit=True,
        tabLabel=[
            (general_column_layout, "Gen"),
            (reference_columnLayout, "Ref"),
            (modeling_column_layout, "Mod"),
            (rigging_columnLayout, "Rig"),
            (render_columnLayout, "Ren"),
            (previs_columnLayout, "Prev"),
            (animation_columnLayout, "Ani"),
            (obsolete_columnLayout, "Obs")
        ],
        cc=functools.partial(store_tab_index, main_tab_layout)
    )

    dock_control = pm.dockControl(
        "toolbox_dockControl",
        l='toolbox',
        content=toolbox_window,
        area="left",
        allowedArea=["left", "right"],
        width=width
    )

    # switch to last tab
    last_tab_index = get_last_tab_index()
    if last_tab_index:
        pm.tabLayout(
            main_tab_layout,
            e=1,
            sti=last_tab_index
        )


def store_tab_index(tab_layout):
    val = pm.tabLayout(tab_layout, q=1, sti=1)
    os.environ[__last_tab__] = str(val)


def get_last_tab_index():
    """returns the last tab index from settings
    """
    return int(os.environ.get(__last_tab__, 0))
