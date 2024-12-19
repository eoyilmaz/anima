# -*- coding: utf-8 -*-
"""Helper functions and classes for Houdini.

The name of this module is inspired from the Maya module.
"""
import hou


def get_network_pane():
    """returns the network pane"""
    return hou.ui.paneTabOfType(hou.paneTabType.NetworkEditor)


def get_scene_viewer():
    """returns the scene viewer"""
    return hou.ui.paneTabOfType(hou.paneTabType.SceneViewer)


def create_spare_input(node, value=""):
    """creates spare inputs for the given node and sets the value

    :param hou.Node node: The node to insert the spare input to.
    :param str value: The value of the parameter
    """
    # Create space input0 for rs proxy output node
    parm_template_group = node.parmTemplateGroup()
    parm_template_group.append(
        hou.StringParmTemplate(
            "spare_input0",
            "Spare Input 0",
            1,
            string_type=hou.stringParmType.NodeReference,
        )
    )
    node.setParmTemplateGroup(parm_template_group)
    node.parm("spare_input0").set(value)


def very_nice_camera_rig(
    focal_length=35, horizontal_film_aperture=36, vertical_film_aperture=24
):
    """creates a very nice camera rig where the Heading, Pitch and Roll controls are on different transform nodes
    allowing more control on the camera movement

    :param focal_length:
    :param horizontal_film_aperture:
    :param vertical_film_aperture:
    """

    obj_context = hou.node("/obj")

    camera = obj_context.createNode("cam")
    # set camera attributes
    camera.parm("focal").set(focal_length)
    # set the film back in millimeters (yeah)
    camera.parm("aperture").set(horizontal_film_aperture)

    main_ctrl = obj_context.createNode("null", "main_ctrl1")
    heading_ctrl = obj_context.createNode("null", "heading_ctrl1")
    pitch_ctrl = obj_context.createNode("null", "pitch_ctrl1")
    roll_ctrl = obj_context.createNode("null", "roll_ctrl1")

    # create DAG hierarchy
    camera.setInput(0, roll_ctrl)
    roll_ctrl.setInput(0, pitch_ctrl)
    pitch_ctrl.setInput(0, heading_ctrl)
    heading_ctrl.setInput(0, main_ctrl)

    # Parameters
    # -----------------------------------------------------------
    # Focal Length And Focal Plane Controls
    # Create space input0 for rs proxy output node

    # Focal Length
    ptg = main_ctrl.parmTemplateGroup()
    ptg.append(
        hou.FloatParmTemplate(
            "focal",
            "Focal Length",
            1,
            default_value=[focal_length],
            min=1.0,
            min_is_strict=True,
        )
    )
    ptg.append(
        hou.FloatParmTemplate(
            "aperture",
            "Aperture",
            1,
            default_value=[horizontal_film_aperture],
            min=1.0,
            min_is_strict=True,
        )
    )
    ptg.append(
        hou.ToggleParmTemplate(
            "useDepthOfField", "Use Depth Of Field", default_value=False
        )
    )
    ptg.append(
        hou.FloatParmTemplate(
            "fstop", "f-stop", 1, default_value=[2.8], min=0.01, min_is_strict=True
        )
    )
    ptg.append(
        hou.FloatParmTemplate("focusOffset", "Focus Offset", 1, default_value=[0])
    )
    ptg.append(
        hou.FloatParmTemplate("offsetX", "Offset X (PanH)", 1, default_value=[0])
    )
    ptg.append(
        hou.FloatParmTemplate("offsetY", "Offset Y (PanV)", 1, default_value=[0])
    )
    ptg.append(
        hou.FloatParmTemplate("offsetZ", "Offset Z (Depth)", 1, default_value=[0])
    )
    ptg.append(hou.FloatParmTemplate("roll1", "Roll", 1, default_value=[0]))
    ptg.append(hou.FloatParmTemplate("pitch", "Pitch", 1, default_value=[0]))
    ptg.append(hou.FloatParmTemplate("heading", "Heading", 1, default_value=[0]))
    ptg.append(hou.FloatParmTemplate("camerar", "Camera Rotation", 3))

    main_ctrl.setParmTemplateGroup(ptg)
    translate_parm = ptg.find("t")
    ptg

    main_ctrl.parm("focal").set(focal_length)
    main_ctrl.parm("aperture").set(horizontal_film_aperture)
    main_ctrl_name = main_ctrl.name()
    camera.parm("focal").setExpression('ch("../%s/focal")' % main_ctrl_name)
    camera.parm("aperture").setExpression('ch("../%s/aperture")' % main_ctrl_name)

    # Depth Of Field
    camera.parm("RS_campro_dofEnable").setExpression(
        'ch("../%s/useDepthOfField")' % main_ctrl_name
    )

    # F-Stop
    camera.parm("fstop").setExpression('ch("../%s/fstop")' % main_ctrl_name)

    # Camera Local Position and Offsets
    # Focus Offset
    camera.parm("tx").setExpression('ch("../%s/offsetX")' % main_ctrl_name)
    camera.parm("ty").setExpression('ch("../%s/offsetY")' % main_ctrl_name)
    camera.parm("tz").setExpression('ch("../%s/offsetZ")' % main_ctrl_name)

    # Back to focal plane
    camera.parm("focus").setExpression(
        'ch("../{main_ctrl}/offsetZ") + ch("../{main_ctrl}/focusOffset")'.format(
            main_ctrl=main_ctrl_name
        )
    )

    # -----------------------------------------------------------
    # Camera Orientation

    roll_ctrl.parm("rz").setExpression('ch("../%s/roll1")' % main_ctrl_name)
    pitch_ctrl.parm("rx").setExpression('ch("../%s/pitch")' % main_ctrl_name)
    heading_ctrl.parm("ry").setExpression('ch("../%s/heading")' % main_ctrl_name)

    camera.parm("rx").setExpression('ch("../%s/camerarx")' % main_ctrl_name)
    camera.parm("ry").setExpression('ch("../%s/camerary")' % main_ctrl_name)
    camera.parm("rz").setExpression('ch("../%s/camerarz")' % main_ctrl_name)

    heading_ctrl.parm("tx").lock(True)
    heading_ctrl.parm("ty").lock(True)
    heading_ctrl.parm("tz").lock(True)
    heading_ctrl.parm("rx").lock(True)
    heading_ctrl.parm("ry").lock(True)
    heading_ctrl.parm("rz").lock(True)
    heading_ctrl.parm("sx").lock(True)
    heading_ctrl.parm("sy").lock(True)
    heading_ctrl.parm("sz").lock(True)

    pitch_ctrl.parm("tx").lock(True)
    pitch_ctrl.parm("ty").lock(True)
    pitch_ctrl.parm("tz").lock(True)
    pitch_ctrl.parm("rx").lock(True)
    pitch_ctrl.parm("ry").lock(True)
    pitch_ctrl.parm("rz").lock(True)
    pitch_ctrl.parm("sx").lock(True)
    pitch_ctrl.parm("sy").lock(True)
    pitch_ctrl.parm("sz").lock(True)

    roll_ctrl.parm("tx").lock(True)
    roll_ctrl.parm("ty").lock(True)
    roll_ctrl.parm("tz").lock(True)
    roll_ctrl.parm("rx").lock(True)
    roll_ctrl.parm("ry").lock(True)
    roll_ctrl.parm("rz").lock(True)
    roll_ctrl.parm("sx").lock(True)
    roll_ctrl.parm("sy").lock(True)
    roll_ctrl.parm("sz").lock(True)

    camera.parm("tx").lock(True)
    camera.parm("ty").lock(True)
    camera.parm("tz").lock(True)
    camera.parm("rx").lock(True)
    camera.parm("ry").lock(True)
    camera.parm("rz").lock(True)
    camera.parm("sx").lock(True)
    camera.parm("sy").lock(True)
    camera.parm("sz").lock(True)
