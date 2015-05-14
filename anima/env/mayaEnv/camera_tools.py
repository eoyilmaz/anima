# -*- coding: utf-8 -*-
# Copyright (c) 2012-2015, Anima Istanbul
#
# This module is part of anima-tools and is released under the BSD 2
# License: http://www.opensource.org/licenses/BSD-2-Clause

import pymel.core as pm


def camera_film_offset_tool():
    """Adds a locator to the selected camera with which you can adjust the 2d
    pan and zoom.

    Usage :
    -------
    - to add it, select the camera and use oyCameraFilmOffsetTool
    - to remove it, set the transformations to 0 0 1 and then simply delete
    the curve
    """
    sel_list = pm.ls(sl=1)

    camera_shape = ""
    found_camera = 0

    for obj in sel_list:
        #if it is a transform node query for shapes
        if isinstance(obj, pm.nt.Transform):
            for shape in obj.listRelatives(s=True):
                if isinstance(shape, pm.nt.Camera):
                    camera_shape = shape
                    found_camera = 1
                    break
        elif isinstance(obj, pm.nt.Camera):
            camera_shape = obj
            found_camera = 1
            break

    if found_camera:
        pass
    else:
        raise RuntimeError("please select one camera!")

    #get the camera transform node
    temp = camera_shape.listRelatives(p=True)
    camera_transform = temp[0]

    pm.getAttr("defaultResolution.deviceAspectRatio")
    pm.getAttr("defaultResolution.pixelAspect")

    #create the outer box
    frame_curve = pm.curve(
        d=1,
        p=[(-0.5, 0.5, 0),
           (0.5, 0.5, 0),
           (0.5, -0.5, 0),
           (-0.5, -0.5, 0),
           (-0.5, 0.5, 0)],
        k=[0, 1, 2, 3, 4]
    )
    pm.parent(frame_curve, camera_transform, r=True)

    #transform the frame curve
    frame_curve.tz.set(-10.0)

    #create the locator
    temp = pm.spaceLocator()
    adj_locator = temp
    adj_locator_shape = temp

    adj_locator.addAttr('enable', at='bool', dv=True, k=True)

    pm.parent(adj_locator, frame_curve, r=True)

    pm.transformLimits(adj_locator, tx=(-0.5, 0.5), etx=(True, True))
    pm.transformLimits(adj_locator, ty=(-0.5, 0.5), ety=(True, True))
    pm.transformLimits(adj_locator, sx=(0.01, 2.0), esx=(True, True))

    #connect the locator tx and ty to film offset x and y
    adj_locator.tx >> camera_shape.pan.horizontalPan
    adj_locator.ty >> camera_shape.pan.verticalPan

    exp = 'float $flen = %s.focalLength;\n\n' \
          'float $hfa = %s.horizontalFilmAperture * 25.4;\n' \
          '%s.sx = %s.sy = -%s.translateZ * $hfa/ $flen;' % (
          camera_shape, camera_shape, frame_curve, frame_curve, frame_curve)
    pm.expression(s=exp, o='', ae=1, uc="all")

    adj_locator.sx >> adj_locator.sy
    adj_locator.sx >> adj_locator.sz
    adj_locator.sx >> camera_shape.zoom
    adj_locator.enable >> camera_shape.panZoomEnabled

    adj_locator_shape.localScaleZ.set(0)

    adj_locator.tz.set(lock=True, keyable=False)
    adj_locator.rx.set(lock=True, keyable=False)
    adj_locator.ry.set(lock=True, keyable=False)
    adj_locator.rz.set(lock=True, keyable=False)
    adj_locator.sy.set(lock=True, keyable=False)
    adj_locator.sz.set(lock=True, keyable=False)


def camera_focus_plane_tool():
    """sets up a focus plane for the selected camera
    """
    camera = pm.ls(sl=1)[0]
    camera_shape = camera.getShape()

    frame = pm.nurbsPlane(
        n='focusPlane#',
        p=(0, 0, 0), ax=(0, 0, 1), w=1, lr=1, d=1, u=1, v=1, ch=0
    )[0]
    frame_shape = frame.getShape()
    pm.parent(frame, camera, r=True)

    #transform the frame surface
    frame.tz.set(-10.0)

    exp = """float $flen = %(camera)s.focalLength;
    float $hfa = %(camera)s.horizontalFilmAperture * 25.4;
    %(frame)s.sx = -%(frame)s.translateZ * $hfa/ $flen;
    %(frame)s.sy = %(frame)s.sx / defaultResolution.deviceAspectRatio;
    %(camera)s.focusDistance = -%(frame)s.tz;
    %(camera)s.aiFocusDistance = %(camera)s.focusDistance;
    %(camera)s.aiApertureSize = %(camera)s.focalLength / %(camera)s.fStop * 0.1;
    """ % {
        'camera': camera_shape.name(),
        'frame': frame.name()
    }
    pm.expression(s=exp, ae=1, uc="all")

    # set material
    surface_shader = pm.shadingNode('surfaceShader', asShader=1)
    pm.select(frame)
    pm.hyperShade(a=surface_shader.name())

    surface_shader.setAttr('outColor', (0.4, 0, 0))
    surface_shader.setAttr('outTransparency', (0.5, 0.5, 0.5))

    # prevent it from being rendered
    frame_shape.setAttr('castsShadows', 0)
    frame_shape.setAttr('receiveShadows', 0)
    frame_shape.setAttr('motionBlur', 0)
    frame_shape.setAttr('primaryVisibility', 0)
    frame_shape.setAttr('smoothShading', 0)
    frame_shape.setAttr('visibleInReflections', 0)
    frame_shape.setAttr('visibleInRefractions', 0)

    # Arnold attributes
    frame_shape.setAttr('aiSelfShadows', 0)
    frame_shape.setAttr('aiVisibleInDiffuse', 0)
    frame_shape.setAttr('aiVisibleInGlossy', 0)

    # hide unnecessary attributes
    frame.setAttr('tx', lock=True, keyable=False)
    frame.setAttr('ty', lock=True, keyable=False)
    frame.setAttr('rx', lock=True, keyable=False)
    frame.setAttr('ry', lock=True, keyable=False)
    frame.setAttr('rz', lock=True, keyable=False)
    frame.setAttr('sx', lock=True, keyable=False)
    frame.setAttr('sy', lock=True, keyable=False)
    frame.setAttr('sz', lock=True, keyable=False)


def cam_to_chan(start_frame, end_frame):
    """Exports maya camera to nuke

    Select camera to export and call cam2Chan(startFrame, endFrame)


    :param start_frame: start frame
    :param end_frame: end frame
    :return:
    """
    selection = pm.ls(sl=1)
    chan_file = pm.fileDialog2(cap="Save", fm=0, ff="(*.chan)")[0]

    camera = selection[0]

    template = "%(frame)s\t%(posx)s\t%(posy)s\t%(posz)s\t" \
               "%(rotx)s\t%(roty)s\t%(rotz)s\t%(vfv)s"

    lines = []

    for i in range(start_frame, end_frame + 1):
        pm.currentTime(i, e=True)

        pos = pm.xform(camera, q=True, ws=True, t=True)
        rot = pm.xform(camera, q=True, ws=True, ro=True)
        vfv = pm.camera(camera, q=True, vfv=True)

        lines.append(
            template % {
                'frame': i,
                'posx': pos[0],
                'posy': pos[1],
                'posz': pos[2],
                'rotx': rot[0],
                'roty': rot[1],
                'rotz': rot[2],
                'vfv': vfv
            }
        )

    with open(chan_file, 'w') as f:
        f.writelines('\n'.join(lines))
