# -*- coding: utf-8 -*-
# Copyright (c) 2012-2020, Anima Istanbul
#
# This module is part of anima and is released under the MIT
# License: http://www.opensource.org/licenses/MIT

import pymel.core as pm


def camera_film_offset_tool():
    """Adds a locator to the selected camera with which you can adjust the 2d
    pan and zoom.

    Usage :
    -------
    - To add it, select the camera and use camera_film_offset_tool
    - To remove it, set the transformations to 0 0 1 and then simply delete
    the curve
    - You can also use the ``enable`` option to temporarily disable the effect
    """
    camera_shape = get_selected_camera()
    if not camera_shape:
        raise RuntimeError("please select one camera!")

    # get the camera transform node
    camera_transform = camera_shape.getParent()

    frustum_curve = create_frustum_curve(camera_transform)
    handle = create_camera_space_locator(frustum_curve)

    # connect the locator tx and ty to film offset x and y
    handle.tx >> camera_shape.pan.horizontalPan
    handle.ty >> camera_shape.pan.verticalPan

    handle.sy.set(lock=False)
    handle.sz.set(lock=False)
    handle.sx >> handle.sy
    handle.sx >> handle.sz
    handle.sy.set(lock=True, keyable=False)
    handle.sz.set(lock=True, keyable=False)

    handle.sx >> camera_shape.zoom

    pm.transformLimits(handle, sx=(0.01, 2.0), esx=(True, True))

    handle.addAttr('enable', at='bool', dv=True, k=True)
    handle.enable >> camera_shape.panZoomEnabled


def create_camera_space_locator(frustum_curve):
    """Creates a locator under the given frame_curve

    :param frustum_curve:
    :return:
    """
    # create the locator
    locator = pm.spaceLocator()
    locator_shape = locator.getShape()
    pm.parent(locator, frustum_curve, r=True)
    locator.tz.set(lock=True, keyable=False)
    locator.rx.set(lock=True, keyable=False)
    locator.ry.set(lock=True, keyable=False)
    locator.rz.set(lock=True, keyable=False)
    pm.transformLimits(locator, tx=(-0.5, 0.5), etx=(True, True))
    pm.transformLimits(locator, ty=(-0.5, 0.5), ety=(True, True))
    locator_shape.localScaleZ.set(0)
    return locator


def create_frustum_curve(camera):
    """Creates a curve showing the frustum of the given camera

    :param camera:
    :return:
    """

    if isinstance(camera, pm.nt.Transform):
        camera_tranform = camera
        camera = camera_tranform.getShape()
    elif isinstance(camera, pm.nt.Camera):
        camera_tranform = camera.getParent()

    # validate the camera
    if not isinstance(camera, pm.nt.Camera):
        raise RuntimeError('Please select a camera')
    
    # create the outer box
    frame_curve = pm.curve(
        d=1,
        p=[(-0.5, 0.5, 0),
           (0.5, 0.5, 0),
           (0.5, -0.5, 0),
           (-0.5, -0.5, 0),
           (-0.5, 0.5, 0)],
        k=[0, 1, 2, 3, 4]
    )

    pm.parent(frame_curve, camera_tranform, r=True)
    # transform the frame curve
    frame_curve.tz.set(-10.0)

    exp = """float $flen = {camera}.focalLength;
float $hfa = {camera}.horizontalFilmAperture * 25.4;
{curve}.sx = {curve}.sy = -{curve}.translateZ * $hfa/ $flen;""".format(
        camera=camera.name(),
        curve=frame_curve.name()
    )
    pm.expression(s=exp, o='', ae=1, uc="all")

    return frame_curve


def get_selected_camera():
    """Returns the selected camera
    """
    for obj in pm.ls(sl=1, type=pm.nt.Transform):
        # if it is a transform node query for shapes
        if isinstance(obj, pm.nt.Transform):
            for shape in obj.listRelatives(s=True):
                if isinstance(shape, pm.nt.Camera):
                    return shape
        elif isinstance(obj, pm.nt.Camera):
            return obj


def camera_focus_plane_tool(camera):
    """sets up a focus plane for the selected camera
    """
    camera_shape = camera.getShape()

    frame = pm.nurbsPlane(
        n='focusPlane#',
        p=(0, 0, 0), ax=(0, 0, 1), w=1, lr=1, d=1, u=1, v=1, ch=0
    )[0]
    frame_shape = frame.getShape()
    pm.parent(frame, camera, r=True)

    # transform the frame surface
    frame.tz.set(-10.0)

    exp = """float $flen = %(camera)s.focalLength;
    float $hfa = %(camera)s.horizontalFilmAperture * 25.4;
    %(frame)s.sx = -%(frame)s.translateZ * $hfa / $flen;
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
    try:
        frame_shape.setAttr('aiSelfShadows', 0)
        frame_shape.setAttr('aiVisibleInDiffuse', 0)
        frame_shape.setAttr('aiVisibleInGlossy', 0)
    except pm.MayaAttributeError:
        pass

    # hide unnecessary attributes
    frame.setAttr('tx', lock=True, keyable=False)
    frame.setAttr('ty', lock=True, keyable=False)
    frame.setAttr('rx', lock=True, keyable=False)
    frame.setAttr('ry', lock=True, keyable=False)
    frame.setAttr('rz', lock=True, keyable=False)
    frame.setAttr('sx', lock=True, keyable=False)
    frame.setAttr('sy', lock=True, keyable=False)
    frame.setAttr('sz', lock=True, keyable=False)

    return frame


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


def create_3dequalizer_points(width, height):
    """creates 3d equalizer points under the selected camera

    :param width: The width of the plate
    :param height: The height of the plate
    """
    width = float(width)
    height = float(height)

    # get the text file
    path = pm.fileDialog()

    # parse the file
    from anima import utils
    man = utils.C3DEqualizerPointManager()
    man.read(path)

    # get the camera
    cam_shape = get_selected_camera()

    pm.getAttr("defaultResolution.deviceAspectRatio")
    pm.getAttr("defaultResolution.pixelAspect")

    frustum_curve = create_frustum_curve(cam_shape)

    for point in man.points:
        # create a locator
        loc = create_camera_space_locator(frustum_curve)
        loc.rename('p%s' % point.name)

        # animate the locator
        for frame in point.data.keys():
            pm.currentTime(frame)
            frame_data = point.data[frame]
            local_x = frame_data[0] / width - 0.5
            local_y = frame_data[1] / width - 0.5 * height / width
            loc.tx.set(local_x)
            loc.ty.set(local_y)
            loc.tx.setKey()
            loc.ty.setKey()


def find_cut_info(cam):
    """Finds cuts of the given camera.

    This tool works only for

    :param cam: A Maya cameras transform node
    :return:
    """
    # check if this is really a camera
    cam_shape = cam.getShape()

    if not isinstance(cam_shape, pm.nt.Camera):
        raise RuntimeError("Please supply a camera")

    # find cuts
    # for now use the tx attribute to find the cuts
    keyframes = pm.keyframe(cam.tx, q=1, timeChange=True)

    cut_info = []

    i = 0
    iter_count = 0
    while i < range(len(keyframes) - 2) and iter_count < 1000:
        iter_count += 1
        start_frame = keyframes[i]

        try:
            end_frame = keyframes[i + 1]
        except IndexError:
            break

        j = 2
        while (i + j) < len(keyframes):
            start_frame_of_next_cam = keyframes[i + j]
            if int(start_frame_of_next_cam - end_frame) == 1:
                cut_info.append([start_frame, end_frame])
                # print(i, start_frame, end_frame)
                i += j
                break

            end_frame = start_frame_of_next_cam
            j += 1

    return cut_info


def very_nice_camera_rig(focal_length=35, horizontal_film_aperture=36, vertical_film_aperture=24):
    """creates a very nice camera rig where the Heading, Pitch and Roll controls are on different transform nodes
    allowing more control on the camera movement

    :param focal_length:
    :param horizontal_film_aperture:
    :param vertical_film_aperture:
    """
    camera_transform, camera_shape = pm.camera()

    # set camera attributes
    camera_shape.focalLength.set(focal_length)
    # set the film back in inches (sadly)
    camera_shape.horizontalFilmAperture.set(horizontal_film_aperture / 25.4)
    camera_shape.verticalFilmAperture.set(vertical_film_aperture / 25.4)

    main_ctrl = pm.spaceLocator(name='main_ctrl#')
    heading_ctrl = pm.nt.Transform(name='heading_ctrl#')
    pitch_ctrl = pm.nt.Transform(name='pitch_ctrl#')
    roll_ctrl = pm.nt.Transform(name='roll_ctrl#')

    # create DAG hierarchy
    pm.parent(camera_transform, roll_ctrl)
    pm.parent(roll_ctrl, pitch_ctrl)
    pm.parent(pitch_ctrl, heading_ctrl)
    pm.parent(heading_ctrl, main_ctrl)

    # Attributes
    # -----------------------------------------------------------
    # Focal Length And Focal Plane Controls
    main_ctrl.addAttr('divider1', at='enum', niceName='----', enumName='----', k=False)
    main_ctrl.divider1.showInChannelBox(True)

    main_ctrl.addAttr('focalLength', at='float', k=True, min=1)
    main_ctrl.focalLength.set(focal_length)
    main_ctrl.focalLength >> camera_shape.focalLength

    main_ctrl.addAttr('useDepthOfField', at='enum', enumName='false:true', k=False)
    main_ctrl.useDepthOfField.showInChannelBox(True)
    main_ctrl.useDepthOfField >> camera_shape.depthOfField

    main_ctrl.addAttr('fStop', at='float', k=True, min=0.1, dv=2.8)
    main_ctrl.fStop >> camera_shape.fStop

    main_ctrl.addAttr('focusOffset', at='float', k=True, dv=0)

    # -----------------------------------------------------------
    # Camera Local Position and Offsets
    main_ctrl.addAttr('divider2', at='enum', niceName='----', enumName='----', k=False)
    main_ctrl.divider2.showInChannelBox(True)
    main_ctrl.addAttr('offsetX', niceName='Offset X (PanH)', at='float', k=True)
    main_ctrl.addAttr('offsetY', niceName='Offset Y (PanV)', at='float', k=True)
    main_ctrl.addAttr('offsetZ', niceName='Offset Z (Depth)', at='float', k=True, min=0)

    main_ctrl.offsetX >> camera_transform.tx
    main_ctrl.offsetY >> camera_transform.ty
    main_ctrl.offsetZ >> camera_transform.tz

    # Back to focal plane
    add_double_linear = pm.shadingNode('addDoubleLinear', asUtility=True)
    main_ctrl.offsetZ >> add_double_linear.input1
    main_ctrl.focusOffset >> add_double_linear.input2
    add_double_linear.output >> camera_shape.focusDistance

    # -----------------------------------------------------------
    # Camera Orientation
    main_ctrl.addAttr('divider3', at='enum', niceName='----', enumName='----', k=False)
    main_ctrl.divider3.showInChannelBox(True)
    main_ctrl.addAttr('roll', k=True, at='float')
    main_ctrl.addAttr('pitch', k=True, at='float')
    main_ctrl.addAttr('heading', k=True, at='float')

    main_ctrl.roll >> roll_ctrl.rz
    main_ctrl.pitch >> pitch_ctrl.rx
    main_ctrl.heading >> heading_ctrl.ry

    main_ctrl.addAttr('cameraRx', k=True, at='float')
    main_ctrl.addAttr('cameraRy', k=True, at='float')
    main_ctrl.addAttr('cameraRz', k=True, at='float')

    main_ctrl.cameraRx >> camera_transform.rx
    main_ctrl.cameraRy >> camera_transform.ry
    main_ctrl.cameraRz >> camera_transform.rz

    # lock all the other transforms
    main_ctrl.v.setKeyable(False)
    main_ctrl.v.showInChannelBox(True)

    heading_ctrl.t.lock(True)
    heading_ctrl.r.lock(True)
    heading_ctrl.s.lock(True)

    pitch_ctrl.t.lock(True)
    pitch_ctrl.r.lock(True)
    pitch_ctrl.s.lock(True)

    roll_ctrl.t.lock(True)
    roll_ctrl.r.lock(True)
    roll_ctrl.s.lock(True)

    # also lock camera transforms
    camera_transform.t.lock(True)
    camera_transform.r.lock(True)
    camera_transform.s.lock(True)

    pm.select(main_ctrl)
