# -*- coding: utf-8 -*-

import os
import pymel.core as pm


def camera_2d_pan_zoom_tool():
    """Adds a locator to the selected camera with which you can adjust the 2d
    pan and zoom.

    Usage :
    -------
    - To add it, select the camera and use camera_2d_pan_zoom_tool
    - To remove it, set the transformations to 0 0 1 and then simply delete
    the curve
    - You can also use the ``enable`` option to temporarily disable the effect
    """
    camera_shape = get_selected_camera()
    if not camera_shape:
        raise RuntimeError("please select one camera!")

    # get the camera transform node
    camera_transform = camera_shape.getParent()

    frustum_curve = create_frustum_geo(camera_transform)
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

    handle.addAttr("enable", at="bool", dv=True, k=True)
    handle.enable >> camera_shape.panZoomEnabled


def create_camera_space_locator(frustum_curve, use_limits=True):
    """Creates a locator under the given frame_curve

    :param frustum_curve:
    :param use_limits: Limits the point translation, default is True.
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
    if use_limits:
        pm.transformLimits(locator, tx=(-0.5, 0.5), etx=(True, True))
        pm.transformLimits(locator, ty=(-0.5, 0.5), ety=(True, True))

    locator_shape.localScaleZ.set(0)
    return locator


def create_frustum_geo(camera, shape_type=0, name=""):
    """Create a geometry showing the frustum of the given camera.

    :param pm.PyNode camera: The camera transform or shape node.
    :param int shape_type: The shape type to use. 0=NurbsCurve, 1=NurbsPlane, default is
        0.
    :param str name: The name of the frustum geo.
    :return: The newly created frustum geometry.
    """

    if not name:
        name = "frustumGeo#"
    if not name.endswith("#"):
        name = "{}#".format(name)

    camera_transform = None
    if isinstance(camera, pm.nt.Transform):
        camera_transform = camera
        camera = camera_transform.getShape()
    elif isinstance(camera, pm.nt.Camera):
        camera_transform = camera.getParent()

    # validate the camera
    if not isinstance(camera, pm.nt.Camera):
        raise RuntimeError("Please select a camera")

    # create the outer box
    if shape_type == 0:
        # use a curve
        frustum_geo = pm.curve(
            n=name,
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
    else:
        # use a nurbs plane
        frustum_geo = pm.nurbsPlane(
            n=name, p=(0, 0, 0), ax=(0, 0, 1), w=1, lr=1, d=1, u=1, v=1, ch=0
        )[0]
        frame_shape = frustum_geo.getShape()
        # set material
        surface_shader = pm.shadingNode("surfaceShader", asShader=1)
        pm.select(frustum_geo)
        pm.hyperShade(a=surface_shader.name())

        surface_shader.setAttr("outColor", (0.4, 0, 0))
        surface_shader.setAttr("outTransparency", (0.5, 0.5, 0.5))

        # prevent it from being rendered
        frame_shape.setAttr("castsShadows", 0)
        frame_shape.setAttr("receiveShadows", 0)
        frame_shape.setAttr("motionBlur", 0)
        frame_shape.setAttr("primaryVisibility", 0)
        frame_shape.setAttr("smoothShading", 0)
        frame_shape.setAttr("visibleInReflections", 0)
        frame_shape.setAttr("visibleInRefractions", 0)

        # Arnold attributes
        try:
            frame_shape.setAttr("aiSelfShadows", 0)
            frame_shape.setAttr("aiVisibleInDiffuse", 0)
            frame_shape.setAttr("aiVisibleInGlossy", 0)
        except pm.MayaAttributeError:
            pass

    pm.parent(frustum_geo, camera_transform, r=True)
    # transform the frame curve
    frustum_geo.tz.set(-10.0)

    exp = """float $flen = {camera}.focalLength;
float $hfa = {camera}.horizontalFilmAperture * 25.4;
float $vfa = {camera}.verticalFilmAperture * 25.4;
float $fa;
if ({camera}.filmFit == 1){{
    // horizontal - fit resolution gate
    $fa = $hfa;
}} else {{
    // vertical and others - fit resolution gate
    $fa = $vfa;
}}
{frustum_geo}.sx = {frustum_geo}.sy = {frustum_geo}.sz = -{frustum_geo}.translateZ * $hfa/ $flen;
""".format(
        camera=camera.name(), frustum_geo=frustum_geo.name()
    )
    pm.expression(s=exp, o="", ae=1, uc="all")

    # hide unnecessary attributes
    frustum_geo.setAttr("tx", lock=True, keyable=False)
    frustum_geo.setAttr("ty", lock=True, keyable=False)
    frustum_geo.setAttr("rx", lock=True, keyable=False)
    frustum_geo.setAttr("ry", lock=True, keyable=False)
    frustum_geo.setAttr("rz", lock=True, keyable=False)
    frustum_geo.setAttr("sx", lock=True, keyable=False)
    frustum_geo.setAttr("sy", lock=True, keyable=False)
    frustum_geo.setAttr("sz", lock=True, keyable=False)

    return frustum_geo


def get_selected_camera():
    """Returns the selected camera"""
    for obj in pm.ls(sl=1, type=pm.nt.Transform):
        # if it is a transform node query for shapes
        if isinstance(obj, pm.nt.Transform):
            for shape in obj.listRelatives(s=True):
                if isinstance(shape, pm.nt.Camera):
                    return shape
        elif isinstance(obj, pm.nt.Camera):
            return obj


def camera_focus_plane_tool(camera):
    """sets up a focus plane for the selected camera"""
    camera_shape = camera.getShape()

    frustum_geo = create_frustum_geo(camera, shape_type=1)

    exp_focus_distance = """%(camera)s.focusDistance = -%(frustum_geo)s.tz;
    %(camera)s.aiFocusDistance = %(camera)s.focusDistance;
    %(camera)s.aiApertureSize = %(camera)s.focalLength / %(camera)s.fStop * 0.1;
    """ % {
        "camera": camera_shape.name(),
        "frustum_geo": frustum_geo.name(),
    }
    try:
        pm.expression(s=exp_focus_distance, ae=1, uc="all")
    except RuntimeError:
        pass

    return frustum_geo


def camera_near_far_clip_plane_tool(camera):
    """Set up a near and a far plane for the selected camera."""
    if isinstance(camera, pm.nt.Transform):
        camera = camera.getShape()

    # get the default values for the planes
    near_plane_dist = camera.nearClipPlane.get()
    far_plane_dist = camera.farClipPlane.get()

    near_plane = create_frustum_geo(camera, shape_type=1, name="nearPlane#")
    far_plane = create_frustum_geo(camera, shape_type=1, name="farPlane#")
    near_plane.tz.set(-near_plane_dist)
    far_plane.tz.set(-far_plane_dist)

    # connect to the near/far clip attributes
    exp = """{camera}.nearClipPlane = -{near_plane}.tz;
{camera}.farClipPlane = -{far_plane}.tz;
""".format(
        camera=camera.name(), near_plane=near_plane.name(), far_plane=far_plane.name()
    )
    pm.expression(s=exp, o="", ae=1, uc="all")
    return near_plane, far_plane


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

    template = (
        "%(frame)s\t%(posx)s\t%(posy)s\t%(posz)s\t"
        "%(rotx)s\t%(roty)s\t%(rotz)s\t%(vfv)s"
    )

    lines = []

    for i in range(start_frame, end_frame + 1):
        pm.currentTime(i, e=True)

        pos = pm.xform(camera, q=True, ws=True, t=True)
        rot = pm.xform(camera, q=True, ws=True, ro=True)
        vfv = pm.camera(camera, q=True, vfv=True)

        lines.append(
            template
            % {
                "frame": i,
                "posx": pos[0],
                "posy": pos[1],
                "posz": pos[2],
                "rotx": rot[0],
                "roty": rot[1],
                "rotz": rot[2],
                "vfv": vfv,
            }
        )

    with open(chan_file, "w") as f:
        f.writelines("\n".join(lines))


def import_3dequalizer_points(width, height):
    """creates 3d equalizer points under the selected camera

    :param width: The width of the plate
    :param height: The height of the plate
    """
    width = float(width)
    height = float(height)

    # get the text file
    path = pm.fileDialog()

    # parse the file
    from anima.dcc.equalizer import TDE4PointManager

    man = TDE4PointManager()
    man.read(path)

    # get the camera
    cam_shape = get_selected_camera()

    pm.getAttr("defaultResolution.deviceAspectRatio")
    pm.getAttr("defaultResolution.pixelAspect")

    frustum_curve = create_frustum_geo(cam_shape)

    for point in man.points:
        # create a locator
        loc = create_camera_space_locator(frustum_curve, use_limits=False)
        loc.rename("p%s" % point.name)

        # animate the locator
        for frame in point.data.keys():
            frame_data = point.data[frame]
            local_x = frame_data[0] / width - 0.5
            local_y = frame_data[1] / width - 0.5 * height / width
            pm.setKeyframe(loc.tx, t=frame, v=local_x)
            pm.setKeyframe(loc.ty, t=frame, v=local_y)


def export_camera_curves_to_3de4_ui():
    """UI for export_camera_curves_to_3de4."""
    # Use PySide2 for the UI
    # from anima.ui.lib import QtCore, QtGui, QtWidgets
    from PySide2 import QtCore, QtGui, QtWidgets

    class UI(QtWidgets.QDialog):
        """The UI."""

        def __init__(self, parent, *args, **kwargs):
            super(UI, self).__init__(parent, *args, **kwargs)
            self.main_layout = None
            self.camera_line_edit = None
            self.pick_camera_button = None
            self.start_frame_spin_box = None
            self.end_frame_spin_box = None
            self.start_frame_picker_button = None
            self.end_frame_picker_button = None
            self.frame_offset_spin_box = None
            self.button_box = None
            self.setup_ui()

        def setup_ui(self):
            """Create UI elements."""
            self.setWindowTitle("Export Camera Curves To 3DE4")
            self.setFixedWidth(350)
            self.main_layout = QtWidgets.QVBoxLayout()
            self.setLayout(self.main_layout)
            form_layout = QtWidgets.QFormLayout()
            self.main_layout.addLayout(form_layout)
            label_role = QtWidgets.QFormLayout.LabelRole
            field_role = QtWidgets.QFormLayout.FieldRole

            i = -1

            # Camera Name
            i += 1
            form_layout.setWidget(i, label_role, QtWidgets.QLabel("Camera"))
            camera_fields_layout = QtWidgets.QHBoxLayout()
            self.camera_line_edit = QtWidgets.QLineEdit(self)
            self.camera_line_edit.setEnabled(False)
            camera_fields_layout.addWidget(self.camera_line_edit)
            self.pick_camera_button = QtWidgets.QPushButton("<<")
            self.pick_camera_button.setFixedWidth(20)
            self.pick_camera_button.clicked.connect(self.pick_camera_button_clicked)
            camera_fields_layout.addWidget(self.pick_camera_button)
            camera_fields_layout.setStretch(0, 1)
            camera_fields_layout.setStretch(1, 0)
            form_layout.setLayout(i, field_role, camera_fields_layout)

            # start - end frame
            i += 1
            form_layout.setWidget(i, label_role, QtWidgets.QLabel("Frame Range"))
            self.start_frame_picker_button = QtWidgets.QPushButton(">>")
            self.start_frame_picker_button.setToolTip("Get start frame from Maya")
            self.start_frame_picker_button.setFixedWidth(20)
            self.start_frame_picker_button.clicked.connect(
                self.start_frame_picker_button_clicked
            )
            self.start_frame_spin_box = QtWidgets.QSpinBox(self)
            self.start_frame_spin_box.setMaximum(-10000000)
            self.start_frame_spin_box.setMaximum(10000000)
            self.end_frame_spin_box = QtWidgets.QSpinBox(self)
            self.end_frame_spin_box.setMaximum(-10000000)
            self.end_frame_spin_box.setMaximum(10000000)
            self.end_frame_picker_button = QtWidgets.QPushButton("<<")
            self.end_frame_picker_button.setToolTip("Get end frame from Maya")
            self.end_frame_picker_button.setFixedWidth(20)
            self.end_frame_picker_button.clicked.connect(
                self.end_frame_picker_button_clicked
            )
            frame_range_layout = QtWidgets.QHBoxLayout()
            frame_range_layout.addWidget(self.start_frame_picker_button)
            frame_range_layout.addWidget(self.start_frame_spin_box)
            frame_range_layout.addWidget(self.end_frame_spin_box)
            frame_range_layout.addWidget(self.end_frame_picker_button)
            frame_range_layout.setStretch(0, 0)
            frame_range_layout.setStretch(1, 1)
            frame_range_layout.setStretch(2, 1)
            frame_range_layout.setStretch(3, 0)
            form_layout.setLayout(i, field_role, frame_range_layout)
            self.start_frame_picker_button_clicked()
            self.end_frame_picker_button_clicked()

            # Frame offset
            i += 1
            form_layout.setWidget(i, label_role, QtWidgets.QLabel("Frame Offset"))
            self.frame_offset_spin_box = QtWidgets.QSpinBox(self)
            self.frame_offset_spin_box.setMinimumWidth(50)
            self.frame_offset_spin_box.setMaximum(-10000000)
            self.frame_offset_spin_box.setMaximum(10000000)
            self.frame_offset_spin_box.setValue(0)
            form_layout.setWidget(i, field_role, self.frame_offset_spin_box)

            # Button box
            self.button_box = QtWidgets.QDialogButtonBox(self)
            self.button_box.setStandardButtons(
                QtWidgets.QDialogButtonBox.Cancel | QtWidgets.QDialogButtonBox.Ok
            )
            self.button_box.accepted.connect(self.accept)
            self.button_box.rejected.connect(self.reject)
            self.main_layout.addWidget(self.button_box)

        def pick_camera_button_clicked(self):
            """Get the camera name from Maya."""
            selection = pm.ls(sl=1)
            if not selection:
                return

            camera = selection[0]
            if isinstance(camera, pm.nt.Transform) and isinstance(
                camera.getShape(), pm.nt.Camera
            ):
                self.camera_line_edit.setText(camera.name())

        def start_frame_picker_button_clicked(self):
            """Get start frame from Maya."""
            self.start_frame_spin_box.setValue(int(pm.playbackOptions(q=1, min=1)))

        def end_frame_picker_button_clicked(self):
            """Get end frame from Maya."""
            self.end_frame_spin_box.setValue(int(pm.playbackOptions(q=1, max=1)))

        def accept(self):
            """Do export the data."""
            # get the file path
            # show a file browser
            dialog = QtWidgets.QFileDialog(self, "Choose file")
            dialog.setNameFilter("Text Files (*.txt)")
            dialog.setFileMode(QtWidgets.QFileDialog.AnyFile)
            if not dialog.exec_():
                return

            selected_files = dialog.selectedFiles()
            if not selected_files:
                return

            file_path = selected_files[0]
            if not file_path:
                return

            camera_name = self.camera_line_edit.text()
            camera = pm.PyNode(camera_name)
            start_frame = self.start_frame_spin_box.value()
            end_frame = self.end_frame_spin_box.value()
            frame_offset = self.frame_offset_spin_box.value()
            output_path = os.path.dirname(file_path)
            file_base_name = os.path.basename(file_path)

            export_camera_curves_to_3de4(
                camera,
                output_path,
                file_base_name,
                start_frame,
                end_frame,
                frame_offset,
            )
            super(UI, self).accept()

    from anima.dcc.mayaEnv import get_maya_main_window

    ui = UI(parent=get_maya_main_window())
    ui.show()


def export_camera_curves_to_3de4(
    camera,
    output_path,
    file_base_name="",
    start_frame=None,
    end_frame=None,
    frame_offset=0,
):
    """Export camera curves to 3DE4 as text files.

    This will output 6 text files representing the tx, ty, tz and rx, ry, rz suitable to
    be imported to 3DE4 as an animation curve by using
    ``Edit -> File -> Import Curve...`` menu on the curve editor.

    :param pm.nt.Transform camera: A Maya pm.nt.Transform node of a Camera.
    :param str output_path: The output path.
    :param str file_base_name: The file base name, if skipped or set as None the string
        value of ``camera`` will be used.
    :param (int, None) start_frame: The start frame, if None the minimum playback range
        will be used.
    :param (int, None) end_frame: The end frame, if None the maximum playback range will
        be used.
    :param int frame_offset: The frame offset to be added to the output data. Defaults
        to 0.

    :return:
    """
    if file_base_name == "" or file_base_name is None:
        file_base_name = "camera"

    # filter out any file ext
    file_base_name, ext = os.path.splitext(file_base_name)
    if ext == "":
        ext = ".txt"

    file_base_name = "{}_{}{}".format(
        file_base_name, "{transform_name}{channel_name}", ext
    )

    if isinstance(camera, pm.nt.Camera):
        camera = camera.getParent()

    if start_frame is None:
        start_frame = int(pm.playbackOptions(q=1, min=1))

    if end_frame is None:
        end_frame = int(pm.playbackOptions(q=1, max=1))

    tra_data = []
    rot_data = []

    for i in range(start_frame, end_frame + 1):
        pm.currentTime(i)
        tra_data.append([i] + pm.xform(camera, q=1, ws=1, t=1))
        rot_data.append([i] + pm.xform(camera, q=1, ws=1, ro=1))

    data_template = (
        "{frame} {data} "
        "-1.000000000000000 0.000000000000000 "
        "1.000000000000000 0.000000000000000 LINEAR"
    )

    channel_names = {0: "x", 1: "y", 2: "z"}
    transform_data = {"t": tra_data, "r": rot_data}

    for transform_name in transform_data:
        transform = transform_data[transform_name]
        for channel_id in channel_names:
            channel_name = channel_names[channel_id]
            file_name = os.path.join(
                output_path,
                file_base_name.format(
                    transform_name=transform_name, channel_name=channel_name
                ),
            )

            content = [str(len(transform))]
            for i in range(len(transform)):
                frame = transform[i][0] + frame_offset
                data = transform[i][channel_id + 1]
                content.append(data_template.format(frame=frame, data=data))
            # add an empty line
            content.append("")

            with open(file_name, "w") as f:
                f.write("\n".join(content))


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


def very_nice_camera_rig(
    focal_length=35, horizontal_film_aperture=36, vertical_film_aperture=24
):
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

    # add cacheable attribute
    from anima.dcc.mayaEnv import rigging

    rigging.Rigging.add_cacheable_attribute(camera_transform, "shot_camera")

    main_ctrl = pm.spaceLocator(name="main_ctrl#")
    heading_ctrl = pm.nt.Transform(name="heading_ctrl#")
    pitch_ctrl = pm.nt.Transform(name="pitch_ctrl#")
    roll_ctrl = pm.nt.Transform(name="roll_ctrl#")

    # create DAG hierarchy
    pm.parent(camera_transform, roll_ctrl)
    pm.parent(roll_ctrl, pitch_ctrl)
    pm.parent(pitch_ctrl, heading_ctrl)
    pm.parent(heading_ctrl, main_ctrl)

    # Attributes
    # -----------------------------------------------------------
    # Focal Length And Focal Plane Controls
    main_ctrl.addAttr("divider1", at="enum", niceName="----", enumName="----", k=False)
    main_ctrl.divider1.showInChannelBox(True)

    main_ctrl.addAttr("focalLength", at="float", k=True, min=1)
    main_ctrl.focalLength.set(focal_length)
    main_ctrl.focalLength >> camera_shape.focalLength

    main_ctrl.addAttr("useDepthOfField", at="enum", enumName="false:true", k=False)
    main_ctrl.useDepthOfField.showInChannelBox(True)
    main_ctrl.useDepthOfField >> camera_shape.depthOfField

    main_ctrl.addAttr("fStop", at="float", k=True, min=0.1, dv=2.8)
    main_ctrl.fStop >> camera_shape.fStop

    main_ctrl.addAttr("focusOffset", at="float", k=True, dv=0)

    # -----------------------------------------------------------
    # Camera Local Position and Offsets
    main_ctrl.addAttr("divider2", at="enum", niceName="----", enumName="----", k=False)
    main_ctrl.divider2.showInChannelBox(True)
    main_ctrl.addAttr("offsetX", niceName="Offset X (PanH)", at="float", k=True)
    main_ctrl.addAttr("offsetY", niceName="Offset Y (PanV)", at="float", k=True)
    main_ctrl.addAttr("offsetZ", niceName="Offset Z (Depth)", at="float", k=True, min=0)

    main_ctrl.offsetX >> camera_transform.tx
    main_ctrl.offsetY >> camera_transform.ty
    main_ctrl.offsetZ >> camera_transform.tz

    # Back to focal plane
    add_double_linear = pm.shadingNode("addDoubleLinear", asUtility=True)
    main_ctrl.offsetZ >> add_double_linear.input1
    main_ctrl.focusOffset >> add_double_linear.input2
    add_double_linear.output >> camera_shape.focusDistance

    # -----------------------------------------------------------
    # Camera Orientation
    main_ctrl.addAttr("divider3", at="enum", niceName="----", enumName="----", k=False)
    main_ctrl.divider3.showInChannelBox(True)
    main_ctrl.addAttr("roll", k=True, at="float")
    main_ctrl.addAttr("pitch", k=True, at="float")
    main_ctrl.addAttr("heading", k=True, at="float")

    main_ctrl.roll >> roll_ctrl.rz
    main_ctrl.pitch >> pitch_ctrl.rx
    main_ctrl.heading >> heading_ctrl.ry

    main_ctrl.addAttr("cameraRx", k=True, at="float")
    main_ctrl.addAttr("cameraRy", k=True, at="float")
    main_ctrl.addAttr("cameraRz", k=True, at="float")

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


def lock_tracked_camera_channels():
    """Locks tracked camera translate channels"""
    for node in pm.selected():
        node.t.lock()
        node.r.lock()
        node.s.lock()
        shape = node.getShape()
        if shape and isinstance(shape, pm.nt.Camera):
            shape.horizontalFilmAperture.lock()
            shape.verticalFilmAperture.lock()
            shape.focalLength.lock()
