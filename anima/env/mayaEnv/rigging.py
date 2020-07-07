# -*- coding: utf-8 -*-
# Copyright (c) 2012-2020, Erkan Ozgur Yilmaz
#
# This module is part of anima and is released under the MIT
# License: http://www.opensource.org/licenses/MIT

from anima.env.mayaEnv import auxiliary
from anima.perf import measure_time
from pymel import core as pm

from anima.ui.lib import QtCore, QtWidgets


class Rigging(object):
    """Rigging tools
    """

    @classmethod
    def add_cacheable_attribute(cls):
        """adds the cacheable attribute to the selected node
        """
        selection = pm.selected()
        if selection:
            node = selection[0]
            if not node.hasAttr('cacheable'):
                node.addAttr('cacheable', dt='string')
                node.setAttr('cacheable', node.name().lower())

    @classmethod
    def setup_stretchy_spline_ik_curve(cls):
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

    @classmethod
    def axial_correction_group(cls):
        """Creates a group node above the selected objects to zero-out the
        transformations. Also works for clusters.
        """
        selection = pm.ls(sl=1)
        for item in selection:
            auxiliary.axial_correction_group(item)

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
        follicle_shape = pm.createNode('follicle')

        geometry = component.node()
        uv = None

        if isinstance(geometry, pm.nt.Mesh):
            geometry.attr('outMesh') >> follicle_shape.attr('inputMesh')
            # get uv
            uv = component.getUV()
        elif isinstance(geometry, pm.nt.NurbsSurface):
            geometry.attr('local') >> follicle_shape.attr('inputSurface')
            # get uv
            # TODO: Fix this
            uv = [0, 0]

        geometry.attr('worldMatrix[0]') >> follicle_shape.attr(
            'inputWorldMatrix')

        follicle_shape.setAttr('pu', uv[0])
        follicle_shape.setAttr('pv', uv[1])

        # set simulation to static
        follicle_shape.setAttr('simulationMethod', 0)

        # connect to its transform node
        follicle = follicle_shape.getParent()

        follicle_shape.attr('outTranslate') >> follicle.attr('t')
        follicle_shape.attr('outRotate') >> follicle.attr('r')

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

    @classmethod
    def create_joints_on_curve_ui(cls):
        """Creates joints on selected curve
        """
        from anima.env import mayaEnv
        main_window = mayaEnv.get_maya_main_window()
        jocd = JointOnCurveDialog(parent=main_window)
        jocd.show()

    @classmethod
    def create_joints_on_curve(cls, number_of_joints=2, orientation="xyz",
                               second_axis="+x", align_to_world=False,
                               reverse_dir=False, joint_name_string="joint",
                               suffix_string=""):
        """Creates joints on selected curve
        """

        sel_list = pm.ls(sl=1)
        if len(sel_list) < 1:
            pm.error("Please select one curve")

        curve = sel_list[0]
        curve_shape = curve.getShape()

        if not isinstance(curve_shape, (pm.nt.NurbsCurve, pm.nt.BezierCurve)):
            pm.error("Please select one curve")

        if not curve_shape:
            pm.error("Please select one curve")

        if joint_name_string == "":
            joint_name_string = "joint"

        motion_path1 = pm.nt.MotionPath()
        motion_path1.rename("CJOC_motionPath#")

        curve_shape.worldSpace[0] >> motion_path1.geometryPath
        motion_path1.fractionMode.set(1)

        vector_lut = {
            "xyz": {
                'aim_vector': pm.dt.Vector(1, 0, 0),
                'world_up_vector': pm.dt.Vector(0, 1, 0)
            },
            "xzy": {
                'aim_vector': pm.dt.Vector(1, 0, 0),
                'world_up_vector': pm.dt.Vector(0, 0, 1)
            },
            "yzx": {
                'aim_vector': pm.dt.Vector(0, 1, 0),
                'world_up_vector': pm.dt.Vector(0, 0, 1)
            },
            "yxz": {
                'aim_vector': pm.dt.Vector(0, 1, 0),
                'world_up_vector': pm.dt.Vector(1, 0, 0)
            },
            "zxy": {
                'aim_vector': pm.dt.Vector(0, 0, 1),
                'world_up_vector': pm.dt.Vector(1, 0, 0)
            },
            "zyx": {
                'aim_vector': pm.dt.Vector(0, 0, 1),
                'world_up_vector': pm.dt.Vector(0, 1, 0)
            },
        }

        aim_vector = vector_lut[orientation]["aim_vector"]
        world_up_vector = vector_lut[orientation]["world_up_vector"]

        up_vector_lut = {
            '+x': pm.dt.Vector(1, 0, 0),
            '-x': pm.dt.Vector(-1, 0, 0),
            '+y': pm.dt.Vector(0, 1, 0),
            '-y': pm.dt.Vector(0, -1, 0),
            '+z': pm.dt.Vector(0, 0, 1),
            '-z': pm.dt.Vector(0, 0, -1)
        }
        up_vector = up_vector_lut[second_axis]

        orientations = [
            "xyz",
            "yzx",
            "zxy",
            "xzy",
            "yxz",
            "zyx",
        ]

        joints = []
        for i in range(number_of_joints):
            u_value = (1.0 * float(i) / (float(number_of_joints) - 1.0))

            if reverse_dir:
                u_value = 1.0 - u_value

            motion_path1.uValue.set(u_value)

            world_pos = pm.dt.Vector(
                motion_path1.xCoordinate.get(),
                motion_path1.yCoordinate.get(),
                motion_path1.zCoordinate.get()
            )

            pm.select(None)
            joint = pm.nt.Joint()
            joint.rename("%s#" % joint_name_string)
            joint.t.set(world_pos)

            joint.rotateOrder.set(orientations.index(orientation))
            joints.append(joint)

        if suffix_string is not None:
            for joint in joints:
                joint.rename("%s%s" % (joint.name(), suffix_string))

        for i in range(len(joints) - 1):
            if not align_to_world:
                aim_constraint = pm.aimConstraint(
                    joints[i + 1],
                    joints[i],
                    wut="vector",
                    aim=aim_vector,
                    wu=up_vector,
                    u=world_up_vector,
                )
                pm.delete(aim_constraint)

            pm.parent(joints[i + 1], joints[i], a=True)

        # fix the last joint
        pm.makeIdentity(
            joints[-1],
            apply=1, t=False, r=False, s=False, n=False, jointOrient=True
        )

        pm.delete(motion_path1)
        pm.select(joints[0])

        # fix first joints orientation
        pm.makeIdentity(
            apply=True, t=False, r=True, s=False, n=False
        )

    @classmethod
    def mirror_transformation(cls):
        """Mirrors transformation from first selected object to the second
        selected object
        """
        # TODO: This needs more generalization
        import math
        sel_list = pm.selected()

        source_node = sel_list[0]
        target_node = sel_list[1]

        m = source_node.worldMatrix.get()

        local_y_axis = pm.dt.Vector(m[1][0], m[1][1], m[1][2])
        local_z_axis = pm.dt.Vector(m[2][0], m[2][1], m[2][2])

        # reflection
        reflected_local_y_axis = local_y_axis.deepcopy()
        reflected_local_y_axis.x *= -1

        reflected_local_z_axis = local_z_axis.deepcopy()
        reflected_local_z_axis.x *= -1

        reflected_local_x_axis = reflected_local_y_axis.cross(
            reflected_local_z_axis)
        reflected_local_x_axis.normalize()

        wm = pm.dt.TransformationMatrix()

        wm[0, :3] = reflected_local_x_axis
        wm[1, :3] = reflected_local_y_axis
        wm[2, :3] = reflected_local_z_axis

        pm.xform(target_node, ws=1, ro=map(math.degrees, wm.eulerRotation()))
        # pm.makeIdentity(
        #     target_node, apply=1, t=False, r=False, s=False, n=False,
        #     jointOrient=True
        # )

    @classmethod
    def ik_fk_limb_rigger(cls):
        """Creates IK/FK Limb Setup from selected start and end joint
        """
        selection = pm.selected()

        start_joint = selection[0]
        end_joint = selection[1]

        rigger = IKFKLimbRigger(start_joint, end_joint)

        rigger.create_ik_hierarchy()
        rigger.create_fk_hierarchy()
        rigger.create_switch_setup()

    @classmethod
    def bendy_ik_fk_limb_rigger(cls, subdivision=2):
        """Creates Bendy IK/FK Limb Setup from selected start and end joint
        """
        selection = pm.selected()

        start_joint = selection[0]
        end_joint = selection[1]

        rigger = IKFKLimbRigger(start_joint, end_joint)

        rigger.create_ik_hierarchy()
        rigger.create_fk_hierarchy()
        rigger.create_switch_setup()
        rigger.create_bendy_hierarchy(subdivision=subdivision)

    @classmethod
    def squash_stretch_bend_rigger(cls):
        """Creates Squash/Stretch/Bend rig for the selected geometry
        """
        geo = pm.selected()[0]
        ssbr = SquashStretchBendRigger(geo)
        ssbr.setup()


class JointOnCurveDialog(QtWidgets.QDialog):
    """Dialog for create_joint_on_curve utility
    """

    def __init__(self, parent=None):
        super(JointOnCurveDialog, self).__init__(parent)

        self.version = "1.0.0"
        self.dialog_name = "createJointOnCurve"

        self._setup_ui()

    def _setup_ui(self):
        """the ui
        """
        self.resize(243, 209)

        # from anima.ui.lib import QtWidgets
        # if False:
        #     from PySide2 import QtWidgets
        # assert QtWidgets is QtWidgets
        from PySide2 import QtWidgets

        self.vertical_layout = QtWidgets.QVBoxLayout(self)
        self.setLayout(self.vertical_layout)
        self.vertical_layout.setStretch(2, 1)

        self.setWindowTitle(self.dialog_name)

        self.form_layout = QtWidgets.QFormLayout()
        self.form_layout.setFieldGrowthPolicy(
            QtWidgets.QFormLayout.AllNonFixedFieldsGrow
        )
        self.form_layout.setLabelAlignment(
            QtCore.Qt.AlignRight |
            QtCore.Qt.AlignTrailing |
            QtCore.Qt.AlignVCenter
        )

        label_role = QtWidgets.QFormLayout.LabelRole
        field_role = QtWidgets.QFormLayout.FieldRole

        form_field_index = -1
        # --------------------
        # Number of Joints Field
        form_field_index += 1

        # Label
        self.number_of_joints_label = QtWidgets.QLabel(self)
        self.number_of_joints_label.setText("Number Of Joints")

        self.form_layout.setWidget(
            form_field_index, label_role, self.number_of_joints_label,
        )

        # Field
        self.number_of_joints_spin_box = QtWidgets.QSpinBox(self)
        self.form_layout.setWidget(
            form_field_index, field_role, self.number_of_joints_spin_box
        )
        self.number_of_joints_spin_box.setValue(2)
        self.number_of_joints_spin_box.setMinimum(2)

        # -----------------------
        # Orientation
        form_field_index += 1

        # Label
        self.orientation_label = QtWidgets.QLabel(self)
        self.orientation_label.setText("Orientation")
        self.form_layout.setWidget(
            form_field_index, label_role, self.orientation_label
        )

        # Field
        self.orientation_combo_box = QtWidgets.QComboBox(self)
        self.orientation_combo_box.addItems(
            [
                "xyz",
                "yzx",
                "zxy",
                "xzy",
                "yxz",
                "zyx",
            ]
        )

        self.form_layout.setWidget(
            form_field_index, field_role, self.orientation_combo_box
        )

        # ---------------------------
        # Second Axis World Orientation
        form_field_index += 1

        # Label
        self.second_axis_world_orientation_label = QtWidgets.QLabel(self)
        self.second_axis_world_orientation_label.setText(
            "Second Axis World Orientation"
        )
        self.form_layout.setWidget(
            form_field_index, label_role,
            self.second_axis_world_orientation_label
        )

        # Field
        self.second_axis_world_orientation_combo_box = \
            QtWidgets.QComboBox(self)
        self.second_axis_world_orientation_combo_box.addItems(
            [
                "+x",
                "-x",
                "+y",
                "-y",
                "+z",
                "-z",
            ]
        )
        self.form_layout.setWidget(
            form_field_index, field_role,
            self.second_axis_world_orientation_combo_box
        )

        # --------------------------------
        # Align To World
        form_field_index += 1

        # Label
        self.align_to_world_label = QtWidgets.QLabel(self)
        self.align_to_world_label.setText("Align To World")
        self.form_layout.setWidget(
            form_field_index, label_role, self.align_to_world_label
        )

        # Field
        self.align_to_world_check_box = QtWidgets.QCheckBox(self)
        self.form_layout.setWidget(
            form_field_index, field_role, self.align_to_world_check_box
        )

        # ----------------------------------
        # Reverse Curve
        form_field_index += 1

        # Label
        self.reverse_curve_label = QtWidgets.QLabel(self)
        self.reverse_curve_label.setText("Reverse Curve")
        self.form_layout.setWidget(
            form_field_index, label_role, self.reverse_curve_label
        )

        self.reverse_curve_check_box = QtWidgets.QCheckBox(self)
        self.form_layout.setWidget(
            form_field_index, field_role, self.reverse_curve_check_box
        )

        # -------------------------------
        # Joint Names
        form_field_index += 1

        # Label
        self.joint_names_label = QtWidgets.QLabel(self)
        self.joint_names_label.setText("Joint Names")
        self.form_layout.setWidget(
            form_field_index, label_role, self.joint_names_label
        )

        # Field
        self.joint_names_layout = QtWidgets.QHBoxLayout(self)
        self.joint_names_check_box = QtWidgets.QCheckBox(self)
        self.joint_names_line_edit = QtWidgets.QLineEdit(self)
        self.joint_names_line_edit.setText("joint")
        self.joint_names_line_edit.setEnabled(False)

        self.joint_names_layout.addWidget(self.joint_names_check_box)
        self.joint_names_layout.addWidget(self.joint_names_line_edit)

        self.form_layout.setLayout(
            form_field_index, field_role, self.joint_names_layout
        )

        # setup signals
        QtCore.QObject.connect(
            self.joint_names_check_box,
            QtCore.SIGNAL("stateChanged(int)"),
            self.joint_names_line_edit.setEnabled
        )

        # ------------------------
        # Suffix Joint Names
        form_field_index += 1

        # Label
        self.suffix_joint_names_label = QtWidgets.QLabel(self)
        self.suffix_joint_names_label.setText("Suffix Joint Names")
        self.form_layout.setWidget(
            form_field_index, label_role, self.suffix_joint_names_label
        )

        # Field
        self.suffix_joint_names_layout = QtWidgets.QHBoxLayout(self)
        self.suffix_joint_names_check_box = QtWidgets.QCheckBox(self)
        self.suffix_joint_names_line_edit = QtWidgets.QLineEdit(self)
        self.suffix_joint_names_line_edit.setText("_suffix")
        self.suffix_joint_names_line_edit.setEnabled(False)

        self.suffix_joint_names_layout.addWidget(
            self.suffix_joint_names_check_box
        )
        self.suffix_joint_names_layout.addWidget(
            self.suffix_joint_names_line_edit
        )

        self.form_layout.setLayout(
            form_field_index, field_role, self.suffix_joint_names_layout
        )

        # setup signals
        QtCore.QObject.connect(
            self.suffix_joint_names_check_box,
            QtCore.SIGNAL("stateChanged(int)"),
            self.suffix_joint_names_line_edit.setEnabled
        )

        # ----------------
        self.vertical_layout.addLayout(self.form_layout)

        # ----------------
        # Create Joints Button
        self.create_joints_button = QtWidgets.QPushButton()
        self.create_joints_button.setText("Create Joints")
        self.vertical_layout.addWidget(self.create_joints_button)

        # setup signals
        QtCore.QObject.connect(
            self.create_joints_button,
            QtCore.SIGNAL("clicked()"),
            self.create_joints
        )

    def create_joints(self):
        """
        """
        joint_name_string = ""
        suffix_string = ""

        number_of_joints = self.number_of_joints_spin_box.value()
        orientation = self.orientation_combo_box.currentText()
        second_axis = self.second_axis_world_orientation_combo_box.currentText()
        align_to_world = self.align_to_world_check_box.isChecked()
        reverse_dir = self.reverse_curve_check_box.isChecked()

        if self.joint_names_check_box.isChecked():
            joint_name_string = self.joint_names_line_edit.text()

        if self.suffix_joint_names_check_box.isChecked():
            suffix_string = self.suffix_joint_names_line_edit.text()

        Rigging.create_joints_on_curve(
            number_of_joints=number_of_joints,
            orientation=orientation,
            second_axis=second_axis,
            align_to_world=align_to_world,
            reverse_dir=reverse_dir,
            joint_name_string=joint_name_string,
            suffix_string=suffix_string
        )


class PinController(object):
    """A pin controller is a snappy type of controller where the object is free
    too move but because its movement is compensated with a parent group it
    stays at the same position in the space.

    It is mainly used in facial rigs. Where the controller seems to be
    controlling the object that it is deforming without any cyclic dependency
    """

    pin_shader_prefix = "PinController_Shader"
    pin_name_prefix = "PinController"

    def __init__(self, pin_size=0.1):
        self.size = pin_size
        self.shader_type = 'lambert'
        self.color = [0, 1, 0]
        self.pin_transform = None
        self.pin_shape = None

        self.pin_to_vertex = None
        self.pin_to_shape = None
        self.pin_uv = [0, 0]
        self.follicle_shape = None
        self.follicle_transform = None

        self.compensation_group = None
        self.axial_correction_group = None

    def setup(self):
        """creates the setup
        """
        from anima.env.mayaEnv import auxiliary

        vtx_coord = pm.xform(self.pin_to_vertex, q=1, ws=1, t=1)

        self.pin_to_shape = self.pin_to_vertex.node()
        self.pin_uv = self.pin_to_shape.getUVAtPoint(vtx_coord, space='world', uvSet='map1')

        # create a sphere with the size of pin_size
        self.pin_transform, make_nurbs_node = pm.sphere(radius=self.size)
        self.pin_transform.rename("%s#" % self.pin_name_prefix)

        self.pin_shape = self.pin_transform.getShape()

        # create two axial correction groups
        self.compensation_group = \
            auxiliary.axial_correction_group(self.pin_transform)
        self.compensation_group.rename("%s_CompensationGrp" % self.pin_transform.name())

        self.axial_correction_group = \
            auxiliary.axial_correction_group(self.compensation_group)

        # create compensation setup
        decompose_matrix = pm.nt.DecomposeMatrix()
        self.pin_transform.inverseMatrix >> decompose_matrix.inputMatrix
        decompose_matrix.outputTranslate >> self.compensation_group.t
        decompose_matrix.outputRotate >> self.compensation_group.r
        decompose_matrix.outputScale >> self.compensation_group.s

        # limit movement
        # set the transform limit of the pin to [-1, 1] range
        pm.transformLimits(
            self.pin_transform,
            tx=[-1, 1], etx=[1, 1],
            ty=[-1, 1], ety=[1, 1],
            tz=[-1, 1], etz=[1, 1],
        )

        # create a follicle on the shape at the given uv
        self.follicle_transform, self.follicle_shape = \
            auxiliary.create_follicle(self.pin_to_shape, self.pin_uv)
        self.follicle_transform.rename("%s_Follicle" % self.pin_transform.name())

        # move the axial correction group
        pm.xform(self.axial_correction_group, ws=1, t=vtx_coord)

        # parent the axial correction group to the follicle
        pm.parent(self.axial_correction_group, self.follicle_transform)

        # hide the follicle shape
        self.follicle_shape.v.set(0)

        # assign shader
        shader = self.get_pin_shader()
        shading_engine = shader.outputs(type='shadingEngine')[0]
        pm.sets("initialShadingGroup", rm=self.pin_shape)
        pm.sets(shading_engine, fe=self.pin_shape)

    def get_pin_shader(self):
        """this creates or returns the existing pin shader
        """
        shaders = pm.ls("%s*" % self.pin_shader_prefix)
        if shaders:
            # try to find the shader with the same color
            for shader in shaders:
                if list(shader.color.get()) == self.color:
                    return shader

        # so we couldn't find a shader
        # lets create one
        shader = pm.shadingNode("lambert", asShader=1)
        shader.rename("%s#" % self.pin_shader_prefix)
        shader.color.set(self.color)

        # also create the related shadingEngine
        shading_engine = pm.nt.ShadingEngine()
        shading_engine.rename("%sSG#" % self.pin_shader_prefix)
        shader.outColor >> shading_engine.surfaceShader

        return shader


class SkinTools(object):
    """A helper utility for easy joint influence edit.
    """
    weight_threshold = 0.00001

    def __init__(self, mesh=None, skin_cluster=None):
        self.mesh = None
        if mesh:
            self.set_mesh(mesh)

        self.skin_cluster = None
        if skin_cluster:
            self.set_skin_cluster(skin_cluster)
        else:
            self.set_skin_cluster(self.get_skin_cluster())

    def set_mesh(self, mesh):
        """sets the mesh

        :param mesh:
        :return:
        """
        self.mesh = mesh
        self.skin_cluster = self.get_skin_cluster()

    def set_skin_cluster(self, skin_cluster):
        """sets the skin cluster

        :param skin_cluster:
        :return:
        """
        self.skin_cluster = skin_cluster

    def get_skin_cluster(self):
        """returns the skin cluster affecting the mesh
        """
        if self.skin_cluster:
            return self.skin_cluster
        else:
            if self.mesh:
                skin_clusters = \
                    pm.ls(self.mesh.listHistory(), type=pm.nt.SkinCluster)
                if skin_clusters:
                    return skin_clusters[0]

    @measure_time("get_joints_effecting_components")
    def get_joints_effecting_components(self, component_list):
        """returns the list of joints effecting the items in the given
        component_list

        :param component_list:
        :return:
        """
        # performance shortcuts
        weight_threshold = self.weight_threshold
        skin_cluster = self.skin_cluster

        # flatten the component list
        joint_list = []
        joints_lut = skin_cluster.getInfluence()
        num_joints = len(joints_lut)

        # for speed concerns the component_list is considered to be a list of
        # flattened vertices
        # so skipping the following line
        # component_list = self.convert_to_vertex_list(component_list)

        for component in component_list:
            # print("component: %s" % component)
            component_index = component.index()

            # query all the weights at once
            weight_attr = skin_cluster.wl[component_index].w
            all_weights = weight_attr.get()

            array_indices = enumerate(
                filter(
                    lambda x: x < num_joints,
                    weight_attr.getArrayIndices())
            )

            for i, joint_index in array_indices:
                weight = all_weights[i]
                if weight > weight_threshold:
                    joint_list.append(joints_lut[joint_index])

        return sorted(list(set(joint_list)), key=lambda x: x.name())

    def find_influenced_vertices(self, joints):
        """returns the vertices of the mesh that influenced by the given joint

        :param joints: Can be a single joint or a list of joints
        :return:
        """
        # remove any selection which will
        stored_selection = pm.ls(sl=1)
        pm.select(None)
        self.skin_cluster.selectInfluenceVerts(joints)
        influenced_vertices = pm.ls(sl=1, fl=1)
        pm.select(stored_selection)
        return influenced_vertices

    @measure_time("set_joint_weight")
    def set_joint_weight(self, joint, vertices, value):
        """sets joint weights to the given value

        :param joint:
        :param vertices:
        :param value:
        :return:
        """
        pm.skinPercent(self.skin_cluster, vertices, tv=[(joint, value)])

    @measure_time("squeeze_index_list")
    def squeeze_index_list(self, index_list):
        """Squeezes index list to a string with continues indexes are
        represented by the first_index:last_index style.
        :param index_list:
        :return:
        """
        compacted_list = []
        last_index = index_list[0]
        start_index = last_index
        for i in index_list[1:]:
            current_index = i
            if current_index > (last_index + 1):
                if start_index != last_index:
                    compacted_list.append("%s:%s" % (start_index, last_index))
                else:
                    compacted_list.append("%s" % start_index)
                start_index = current_index
            last_index = current_index

        if start_index != last_index:
            compacted_list.append("%s:%s" % (start_index, index_list[-1]))
        else:
            compacted_list.append("%s" % start_index)

        return compacted_list

    @measure_time("convert_to_vertex_list")
    def convert_to_vertex_list(self, input_list):
        """converts the given input list to vertex list

        :param input_list:
        :return:
        """
        return pm.ls(
            pm.polyListComponentConversion(
                input_list, fv=1, fe=1, ff=1, fuv=1, fvf=1, tv=1
            ),
            fl=1
        )


class SkinToolsUI(object):
    """UI for SkinTools

    Developers Note: This is converted from a very old MEL script, so don't
    judge me on the code quality. I will probably update it to a more modern
    Python implementation as I keep using it.
    """

    def __init__(self):
        self.window = None
        self.form_layout1 = None
        self.column_layout1 = None
        self.column_layout3 = None

        self.skin_cluster_text = None
        self.mesh_name_text = None
        self.influence_list_text_scroll_list = None
        self.remove_selected_button = None
        self.add_selected_button = None

        self.mesh = None
        self.skin_cluster = None
        self.skin_tools = SkinTools()
        self.joints = []

    def ui(self):
        """the ui
        """
        import functools
        width = 300
        height = 380

        if pm.window("skinTools_window", q=1, ex=1):
            pm.deleteUI("skinTools_window", window=1)

        self.window = pm.window(
            "skinTools_window", w=width, h=height, t="skinTools"
        )

        self.form_layout1 = pm.formLayout("skinTools_formLayout1", nd=100)
        with self.form_layout1:

            self.column_layout1 = \
                pm.columnLayout("skinTools_columnLayout1", adj=1, cal="center")
            with self.column_layout1:
                pm.button(
                    l="Set Mesh",
                    c=self.set_mesh_button_proc
                )

                with pm.rowLayout("skinTools_mesh_name_row_layout", nc=2):
                    pm.text(l="mesh name: ")
                    self.mesh_name_text = pm.text(l="")

                with pm.rowLayout("skinTools_skin_cluster_row_layout", nc=2):
                    pm.text(l="skinCluster: ")
                    self.skin_cluster_text = pm.text(l="")

                pm.button(
                    l="update",
                    c=lambda x: self.update_list()
                )

            self.influence_list_text_scroll_list = \
                pm.textScrollList(numberOfRows=20, sc=self.select)
            pm.popupMenu(parent=self.influence_list_text_scroll_list)
            pm.menuItem(l="switch hold", c=self.switch_hold)

            self.column_layout3 = pm.columnLayout(adj=1, cal="center")
            with self.column_layout3:
                pm.button(
                    l="find influenced Vertices",
                    c=self.find_influenced_vertices_button_proc
                )

                def set_joint_weight_callback(weight, *args):
                    selection = pm.ls(sl=1)
                    joints = \
                        filter(lambda x: isinstance(x, pm.nt.Joint), selection)
                    vertices = \
                        filter(
                            lambda x: isinstance(x, pm.MeshVertex),
                            selection
                        )
                    for joint in joints:
                        self.skin_tools.set_joint_weight(
                            joint,
                            vertices,
                            weight
                        )

                self.remove_selected_button = \
                    pm.button(
                        l="remove selected",
                        c=functools.partial(set_joint_weight_callback, 0)
                    )
                self.add_selected_button = \
                    pm.button(
                        l="add selected",
                        c=functools.partial(set_joint_weight_callback, 1)
                    )

        pm.formLayout(
            "skinTools_formLayout1",
            e=1,
            af=[
                [self.column_layout1, "left", 0],
                [self.column_layout1, "right", 0],
                [self.column_layout1, "top", 0],

                [self.influence_list_text_scroll_list, "left", 0],
                [self.influence_list_text_scroll_list, "right", 0],

                [self.column_layout3, "left", 0],
                [self.column_layout3, "right", 0],

                [self.column_layout3, "bottom", 0],
            ],
            an=[
                [self.column_layout1, "bottom"],
                [self.column_layout3, "top"],
            ],

            ac=[
                [self.influence_list_text_scroll_list, "top", 0, self.column_layout1],
                [self.influence_list_text_scroll_list, "bottom", 0, self.column_layout3],
            ]
        )

        pm.showWindow(self.window)
        pm.window(self.window, e=1, w=width, h=height)

    @measure_time("set_mesh_button_proc")
    def set_mesh_button_proc(self, *args):
        """the skinCluster_text should be filled with the skinCluster name
        """
        # get the mesh from scene selection
        selection = pm.ls(sl=1)
        if selection:
            # get the node type
            node = selection[0]
            if isinstance(node, pm.nt.Transform):
                shape = node.getShape()
            elif isinstance(node, pm.nt.Mesh):
                shape = node
            elif isinstance(node, pm.MeshVertex):
                shape = node.node()
            else:
                shape = node

            self.skin_tools.set_mesh(shape)
            pm.text(
                self.mesh_name_text,
                e=1,
                l=self.skin_tools.mesh.name()
            )
            pm.text(
                self.skin_cluster_text,
                e=1,
                l=self.skin_tools.skin_cluster.name()
            )

            self.update_list()

    @measure_time("find_influenced_vertices_button_proc")
    def find_influenced_vertices_button_proc(self, *args):
        """
        """
        # get the joint name from list
        joint = pm.ls(sl=1)
        influenced_vertices = \
            self.skin_tools.find_influenced_vertices(joint)
        pm.select(influenced_vertices)

    @measure_time("fill_skin_cluster_text_field")
    def fill_skin_cluster_text_field(self):
        """
        """
        if self.skin_tools.skin_cluster:
            pm.text(
                self.skin_cluster_text,
                e=1,
                l=self.skin_tools.skin_cluster.name()
            )

    @measure_time("fill_mesh_name_text_field")
    def fill_mesh_name_text_field(self):
        """
        """
        if self.skin_tools.mesh:
            pm.text(self.mesh_name_text, e=True, l=self.skin_tools.mesh.name())

    @measure_time("get_selected_item_in_list")
    def get_selected_item_in_list(self):
        items = pm.textScrollList(
            self.influence_list_text_scroll_list, q=1, si=1
        )

        if items:
            if items[0].endswith(" (h)"):
                items[0] = items[0].replace(" (h)", "")

            return pm.PyNode(items[0])

    @measure_time("get_selected_item_index_in_list")
    def get_selected_item_index_in_list(self):
        index_list = \
            pm.textScrollList(
                self.influence_list_text_scroll_list, q=True, sii=True
            )
        return index_list[0]

    @measure_time("get_number_of_items")
    def get_number_of_items(self):
        return pm.textScrollList(
            self.influence_list_text_scroll_list, q=True, ni=True
        )

    @measure_time("get_selected_index")
    def get_selected_index(self):
        temp_arr = \
            pm.textScrollList(
                self.influence_list_text_scroll_list, q=1, sii=1
            )
        return temp_arr[0]

    @measure_time("switch_hold")
    def switch_hold(self, *args):
        item = self.get_selected_item_in_list()
        item_index = self.get_selected_item_index_in_list()

        if item.liw.get():
            item.liw.set(0)
            self.replace_item_in_list(item_index, item)
        else:
            item.liw.set(1)
            self.replace_item_in_list(item_index, "%s (h)" % item.name())

        pm.textScrollList(
            self.influence_list_text_scroll_list, e=1, sii=item_index
        )

    @measure_time("replace_item_in_list")
    def replace_item_in_list(self, index, item_name):
        pm.textScrollList(
            self.influence_list_text_scroll_list, e=True, rii=index
        )
        pm.textScrollList(
            self.influence_list_text_scroll_list, e=True, ap=[index, item_name]
        )

    @measure_time("update_list")
    def update_list(self):
        """updates the scroll list with influences
        """
        # clear the list
        pm.textScrollList(self.influence_list_text_scroll_list, e=1, ra=1)

        # remove joints from selection list
        sel_joints = pm.ls(sl=1, type="joint")
        pm.select(sel_joints, d=1)

        # get the vertex list without joints
        sel_list = pm.ls(sl=1)
        transform_nodes = \
            filter(lambda x: isinstance(x, pm.nt.Transform), sel_list)
        if transform_nodes:
            # use only one transform node
            # this UI operates only on one mesh
            transform_node = transform_nodes[0]

            # get the shape
            shape = transform_node.getShape()

            # set the mesh for the skin_tools
            self.skin_tools.set_mesh(shape)
            # no problem
            # component_list = self.skin_tools.convert_to_vertex_list(shape)
            self.joints = self.skin_tools.skin_cluster.getInfluence()
        else:
            # check if any vertices are selected
            vertices = \
                filter(lambda x: isinstance(x, pm.MeshVertex), sel_list)
            component_list = self.skin_tools.convert_to_vertex_list(vertices)

            if not component_list:
                # do nothing
                print("no components")
                return

            self.joints = \
                self.skin_tools.get_joints_effecting_components(component_list)

        # and add the new joint names to the list
        # add the hold status to the name of the joint
        for joint in self.joints:
            display_string = joint.name()

            if joint.liw.get():
                display_string = "%s (h)" % display_string

            pm.textScrollList(
                self.influence_list_text_scroll_list,
                e=1, append=display_string
            )

    @measure_time("select")
    def select(self):
        """selects the joint that is selected in the list in the scene
        """
        pm.select(pm.ls(sl=1, type="joint"), d=1)
        selected_item = self.get_selected_item_in_list()
        pm.select(selected_item, add=1)

        # change the skin influence to current selection
        if selected_item != "":
            pm.mel.eval("setSmoothSkinInfluence %s" % selected_item.name())


class JointHierarchy(object):
    """Represents a joint hierarchy
    """

    def __init__(self, start_joint, end_joint):
        """
        :param start_joint:
        :param end_joint:
        """
        self.joints = []

        self.start_joint = start_joint
        self.end_joint = end_joint

        self.init_hierarchy()

    def init_hierarchy(self):
        """Initialize the hierarchy joints from start_joint to the given end_joint

        :return:
        """
        self.joints = [self.start_joint]
        found_end_joint = False
        for j in reversed(self.start_joint.listRelatives(ad=1, type=pm.nt.Joint)):
            self.joints.append(j)
            if j == self.end_joint:
                found_end_joint = True
                break

        if not found_end_joint:
            raise RuntimeError(
                "Cannot reach end joint (%s) from start joint (%s)" %
                (self.end_joint, self.start_joint)
            )

    def duplicate(self, class_=None, prefix="", suffix="", subdivision=0):
        """duplicates itself and returns a new joint hierarchy

        :param class_: The class of the created JointHierarchy. Default value
          is JointHierarchy
        :param prefix: Prefix for newly created joints
        :param suffix: Suffix for newly created joints
        :param int subdivision: Adds extra joints in between the original
          joints. Setting subdivision to 2 will add 2 more joints between the
          original joints.
        """
        if class_ is None:
            class_ = self.__class__

        new_start_joint = pm.duplicate(self.start_joint)[0]
        all_hierarchy = list(reversed(new_start_joint.listRelatives(ad=1, type=pm.nt.Joint)))
        new_end_joint = all_hierarchy[len(self.joints) - 2]

        # delete anything below
        pm.delete(new_end_joint.listRelatives(ad=1))

        # insert subdivision amount of joints between joints
        if subdivision > 0:
            all_new_joints = [new_start_joint] + list(reversed(new_start_joint.listRelatives(ad=1, type=pm.nt.Joint)))
            new_parent = all_new_joints[0]
            for j_i, j in enumerate(all_new_joints[:-1]):
                if new_parent != j:
                    pm.parent(j, new_parent)
                child_joint = all_new_joints[j_i + 1]
                child_offset = child_joint.tx.get()
                new_parent = j
                for i in range(subdivision):
                    j_sub = pm.duplicate(j)[0]
                    pm.delete(j_sub.listRelatives(ad=1))
                    pm.parent(j_sub, new_parent)
                    j_sub.tx.set(child_offset / (subdivision + 1))
                    new_parent = j_sub
            # parent the last joint
            pm.parent(all_new_joints[-1], new_parent)

        new_hierarchy = class_(start_joint=new_start_joint, end_joint=new_end_joint)
        for i, j in enumerate(self.joints):
            if subdivision > 0:
                for s in range(subdivision + 1):
                    current_index = i * (subdivision + 1) + s
                    if current_index >= len(new_hierarchy.joints):
                        continue
                    nj = new_hierarchy.joints[current_index]
                    nj.rename("{prefix}{joint}{suffix}_{subdiv}".format(prefix=prefix, suffix=suffix, joint=j.name(), subdiv=s + 1))
            else:
                nj = new_hierarchy.joints[i]
                nj.rename("{prefix}{joint}{suffix}".format(prefix=prefix, suffix=suffix, joint=j.name()))

        return new_hierarchy


class IKJointHierarchyBase(JointHierarchy):
    """A base class for IK joint hierarchies
    """

    def __init__(self, start_joint, end_joint, do_stretchy=True):
        JointHierarchy.__init__(self, start_joint, end_joint)

        self.do_stretchy = do_stretchy
        self.default_scale_multiply_divide = None

        self.ik_handle = None
        self.ik_end_effector = None

        self.ik_end_controller = None
        self.ik_pole_controller = None

        self.main_group = None

    def create_ik_setup(self, solver='', controller_radius=0.5):
        """Do create ik setup here

        :param solver:
        :param controller_radius:
        :return:
        """
        raise NotImplementedError("create_ik_setup is not implemented")

    def create_stretch_setup(self):
        """Do create stretch setup here
        """
        raise NotImplementedError("create_ik_setup is not implemented")


class IKLimbJointHierarchy(IKJointHierarchyBase):
    """IK variant of the JointHierarchy
    """

    def create_ik_setup(self, solver='ikRPsolver', controller_radius=0.5):
        """Creates IK setup
        """
        self.ik_handle, self.ik_end_effector = \
            pm.ikHandle(sj=self.start_joint, ee=self.end_joint, solver=solver)

        self.ik_end_controller, shape = pm.circle(
            normal=(0, 1, 0),
            radius=controller_radius
        )
        pm.parent(self.ik_end_controller, self.ik_end_effector)

        self.ik_end_controller.t.set(0, 0, 0)
        self.ik_end_controller.r.set(0, 0, 0)

        # create default scale attribute
        pm.addAttr(self.ik_end_controller, sn="minScale", at="float", dv=1.0, k=True)
        pm.addAttr(self.ik_end_controller, sn="maxScale", at="float", dv=2.0, k=True)
        for j in self.joints[:-1]:  # do not scale the last joint
            self.ik_end_controller.minScale >> j.sx

        pm.parent(self.ik_end_controller, w=1)
        from anima.env.mayaEnv import auxiliary
        auxiliary.axial_correction_group(self.ik_end_controller)

        # constraint the orientation of the last joint to the controller
        pm.orientConstraint(self.ik_end_controller, self.joints[-1], mo=1)

        # create the point constraint
        pm.pointConstraint(self.ik_end_controller, self.ik_handle)

        # create pole controller
        self.ik_pole_controller = pm.spaceLocator(name='ikPoleController#')
        # place it to the extension of the pole vector
        pm.parent(self.ik_pole_controller, self.joints[1], r=1)
        pm.parent(self.ik_pole_controller, w=1)

        # I don't like this but it will help a lot
        move_amount = [0, -1, 0]
        if pm.xform(self.ik_pole_controller, q=1, ws=1, t=1)[0] < 0:
            move_amount = [0, 1, 0]
        pm.move(self.ik_pole_controller, move_amount, r=1, os=1, wd=1)

        pm.poleVectorConstraint(self.ik_pole_controller, self.ik_handle)
        auxiliary.axial_correction_group(self.ik_pole_controller)

        # group everything under the main_group
        self.main_group = pm.nt.Transform(name='IKLimbJointHierarchy_Grp#')
        pm.parent(self.ik_handle, self.main_group)
        pm.parent(self.ik_end_controller.getParent(), self.main_group)
        pm.parent(self.ik_pole_controller.getParent(), self.main_group)

        if self.do_stretchy:
            self.create_stretch_setup()

    def create_stretch_setup(self):
        """create IK Stretch setup
        """
        start_locator = pm.spaceLocator(name='ikStretchMeasureLoc#')
        end_locator = pm.spaceLocator(name='ikStretchMeasureLoc#')

        pm.parent(start_locator, self.start_joint, r=1)
        pm.parent(start_locator, self.start_joint.getParent())
        pm.parent(end_locator, self.start_joint.getParent())

        pm.pointConstraint(self.ik_end_controller, end_locator)

        distance_between = pm.nt.DistanceBetween()
        start_locator.t >> distance_between.point1
        end_locator.t >> distance_between.point2

        default_length = distance_between.distance.get()

        # create multiply divide1
        multiply_divide1 = pm.nt.MultiplyDivide()
        multiply_divide1.operation.set(2)  # divide
        distance_between.distance >> multiply_divide1.input1X
        multiply_divide1.input2X.set(default_length)

        # create clamp node
        clamp = pm.nt.Clamp()
        self.ik_end_controller.minScale >> clamp.minR
        self.ik_end_controller.maxScale >> clamp.maxR
        multiply_divide1.outputX >> clamp.inputR

        for j in self.joints:
            clamp.outputR >> j.sx


class FKLimbJointHierarchy(JointHierarchy):
    """FK variant of the JointHierarchy
    """
    pass


class BendyLimbJointHierarchy(JointHierarchy):
    """Bendy variant of JointHierarchy
    """

    def __init__(self, start_joint, end_joint):
        super(BendyLimbJointHierarchy, self).__init__(start_joint, end_joint)
        self.bendy_curves = []
        self.cluster_data = []
        self.joints_to_curves = []

    def create_bendy_setup(self, control_hierarchy=None):
        """creates the necessary nodes and connections for the bendy setup
        """
        if not control_hierarchy:
            raise RuntimeError("Please supply a JointHierarchy instance as the control hierarchy!")

        subdivision = int((len(self.joints) - 3) / 2)

        # create the curves
        for i in range(len(control_hierarchy.joints) - 1):
            curve = pm.curve(
                d=3,
                ep=map(lambda x: pm.xform(x, q=1, ws=1, t=1), control_hierarchy.joints[i:i+2]),
            )
            print('curve: %s' % curve)
            self.bendy_curves.append(curve)

        # cluster curve CV points
        for i, curve in enumerate(self.bendy_curves):

            # create a cluster for first two and last two cvs of the curve
            for j in range(2):
                cluster, cluster_handle = pm.cluster('%s.cv[%s:%s]' % (curve.name(), j * 2, j * 2 + 1))

                # move the cluster to the start or end of the curve
                if j == 0:
                    cv_index = j * 2
                else:
                    cv_index = j * 2 + 1
                tra = pm.xform('%s.cv[%s]' % (curve.name(), cv_index), q=1, ws=1, t=1)
                cluster_handle.t.set(tra)
                cluster_handle.getShape().origin.set(tra)

                data = dict()
                data['cluster'] = cluster
                data['cluster_handle'] = cluster_handle
                data['curve'] = curve
                data['curve_index'] = i
                data['cluster_index'] = j
                self.cluster_data.append(data)

        # parentConstraint the clusters to the control joints
        for cluster_data in self.cluster_data:
            cluster_handle = cluster_data['cluster_handle']
            cluster_acg1 = auxiliary.axial_correction_group(cluster_handle, name_postfix='_Ctrl')
            cluster_acg2 = auxiliary.axial_correction_group(cluster_acg1)

            joint_index = cluster_data['curve_index'] + cluster_data['cluster_index']
            pc = pm.parentConstraint(control_hierarchy.joints[joint_index], cluster_acg2, mo=1)
            pc.interpType.set(2)  # shortest

            joint_index = cluster_data['curve_index'] + cluster_data['cluster_index'] - 1
            if joint_index >= 0:
                pc = pm.parentConstraint(control_hierarchy.joints[joint_index], cluster_acg2, mo=1)
                pc.interpType.set(2)  # shortest

        # Motion Path stuff
        for i, j in enumerate(self.joints[:-1]):
            # directly attach them to the curves
            # which curve????
            curve_index = i // (subdivision + 1)
            joint_index_by_curve = i % (subdivision + 1)
            # curve_index = min(curve_index, len(self.bendy_curves) - 1)
            curve = self.bendy_curves[curve_index]
            curve_shape = curve.getShape()
            world_up_obj = control_hierarchy.joints[curve_index]

            locator = pm.spaceLocator()
            u_value = float(joint_index_by_curve) / (float(subdivision + 1))

            # create motion path
            motion_path = pm.nt.MotionPath()

            motion_path.uValue.set(u_value)
            motion_path.fractionMode.set(1)
            motion_path.worldUpType.set(2)  # object rotation up
            motion_path.worldUpVectorX.set(0)
            motion_path.worldUpVectorY.set(1)
            motion_path.worldUpVectorZ.set(0)
            world_up_obj.worldMatrix[0] >> motion_path.worldUpMatrix
            motion_path.inverseUp.set(1)
            motion_path.inverseFront.set(0)
            motion_path.frontAxis.set(1)  # Y
            motion_path.upAxis.set(0)  # X

            curve_shape.worldSpace[0] >> motion_path.geometryPath
            motion_path.message >> locator.specifiedManipLocation

            # Translate
            motion_path.xCoordinate >> locator.translateX
            motion_path.yCoordinate >> locator.translateY
            motion_path.zCoordinate >> locator.translateZ

            # Rotate
            motion_path.rotateX >> locator.rotateX
            motion_path.rotateY >> locator.rotateY
            motion_path.rotateZ >> locator.rotateZ
            motion_path.rotateOrder >> locator.rotateOrder

            # point constraint joint
            parent_constraint = pm.parentConstraint(locator, j, mo=1)
            parent_constraint.interpType.set(2)


class ReverseFootJointHierarchy(JointHierarchy):
    """Reverse foot joint hierarchy
    """
    pass


class IKSpineJointHierarchy(IKJointHierarchyBase):
    """Creates IK spine joint hierarchy
    """

    def __init__(self, start_joint, end_joint, do_stretchy=True):
        IKJointHierarchyBase.__init__(start_joint, end_joint, do_stretchy)
        self.spine_curve = None

    def create_ik_setup(self, solver='', controller_radius=0.5):
        """Create spine ik setup

        :param solver:
        :param controller_radius:
        :return:
        """
        # create spine curve
        pos = list(map(lambda x: pm.xform(x, q=1, ws=1, t=1), self.joints))
        self.spine_curve = pm.curve(ep=pos)
        spine_curve_shape = self.spine_curve.getShape()

        # attach each joint to a motion path
        for i, joint in enumerate(self.joints):
            u_value = (1.0 * float(i) / (float(len(self.joints)) - 1.0))

            locator = pm.spaceLocator(name='ikSplineJointPlacementLoc#')

            motion_path = pm.nt.MotionPath
            motion_path.uValue.set(u_value)

            # TranslateX
            add_double_linear = pm.nt.AddDoubleLinear()
            locator.transMinusRotatePivotX >> add_double_linear.input1
            motion_path.allCoordinates.xCoordinate >> add_double_linear.input2

            add_double_linear.output >> locator.translateX

            # TranslateY
            add_double_linear = pm.nt.AddDoubleLinear()
            locator.transMinusRotatePivotY >> add_double_linear.input1
            motion_path.allCoordinates.yCoordinate >> add_double_linear.input2

            add_double_linear.output >> locator.translateY

            # TranslateZ
            add_double_linear = pm.nt.AddDoubleLinear()
            locator.transMinusRotatePivotZ >> add_double_linear.input1
            motion_path.allCoordinates.zCoordinate >> add_double_linear.input2

            add_double_linear.output >> locator.translateZ

            spine_curve_shape.worldSpace[0] >> motion_path.geometryPath
            motion_path.fractionMode.set(1)

    def create_stretch_setup(self):
        """Creates the stretchy setup
        """
        pass


class RiggerBase(object):
    """Base class for rigger classes
    """

    def __init__(self, start_joint, end_joint):
        self.start_joint = start_joint
        self.end_joint = end_joint

        self.ik_fk_switch_handle = None

        self.base_hierarchy = JointHierarchy(start_joint, end_joint)
        self.ik_hierarchy = None
        self.fk_hierarchy = None

    def create_ik_hierarchy(self):
        """Creates the ik hierarchy
        """
        self.ik_hierarchy = self.base_hierarchy.duplicate(class_=JointHierarchy, suffix="_ik")

    def create_fk_hierarchy(self):
        """Creates the fk hierarchy
        """
        self.fk_hierarchy = self.base_hierarchy.duplicate(class_=JointHierarchy, suffix="_fk")

    def create_switch_setup(self):
        """Creates the required IK/FK blend setup
        """
        if self.ik_hierarchy is None:
            raise RuntimeError("No IK hierarchy!")

        if self.fk_hierarchy is None:
            raise RuntimeError("No FK_hierarchy!")

        self.ik_fk_switch_handle, shape = pm.circle(normal=(1, 0, 0), radius=0.5)
        pm.parent(self.ik_fk_switch_handle, self.base_hierarchy.joints[0], r=1)
        pm.parent(self.ik_fk_switch_handle, self.base_hierarchy.joints[0].getParent())
        pm.addAttr(self.ik_fk_switch_handle, sn="ikFkSwitch", dv=0, at="float", min=0, max=1, k=True)

        # reverser
        reverser = pm.nt.Reverse()
        self.ik_fk_switch_handle.ikFkSwitch >> reverser.inputX

        for i in range(len(self.base_hierarchy.joints)):
            bj = self.base_hierarchy.joints[i]
            ikj = self.ik_hierarchy.joints[i]
            fkj = self.fk_hierarchy.joints[i]
            parent_constraint1 = pm.parentConstraint(ikj, bj)
            parent_constraint2 = pm.parentConstraint(fkj, bj)

            # get the weight alias list
            wal = pm.parentConstraint(parent_constraint1, q=1, wal=1)

            reverser.outputX >> wal[0]
            self.ik_fk_switch_handle.ikFkSwitch >> wal[1]

        # lock the transforms
        self.ik_fk_switch_handle.t.setKeyable(False)
        self.ik_fk_switch_handle.t.lock()
        self.ik_fk_switch_handle.r.setKeyable(False)
        self.ik_fk_switch_handle.r.lock()
        self.ik_fk_switch_handle.s.setKeyable(False)
        self.ik_fk_switch_handle.s.lock()
        self.ik_fk_switch_handle.v.setKeyable(False)


class IKFKLimbRigger(RiggerBase):
    """Creates a simple IK/FK Limb rig

    The class creates a fully switchable IK/FK limb setup between the start and
    end joints.

    Test Code:

from anima.env.mayaEnv import rigging

selection = pm.selected()

start_joint = selection[0]
end_joint = selection[1]

rigger = rigging.IKFKLimbRigger(start_joint, end_joint)

rigger.create_ik_hierarchy()
rigger.create_fk_hierarchy()
rigger.create_switch_setup()
    """

    def __init__(self, start_joint, end_joint):
        super(IKFKLimbRigger, self).__init__(start_joint, end_joint)
        self.bendy_hierarchy = None

    def create_ik_hierarchy(self):
        """Creates the ik hierarchy
        """
        self.ik_hierarchy = self.base_hierarchy.duplicate(class_=IKLimbJointHierarchy, suffix="_ik")
        # set joint radius
        base_radius = self.base_hierarchy.joints[0].radius.get()
        for j in self.ik_hierarchy.joints:
            j.radius.set(base_radius * 2)
        assert isinstance(self.ik_hierarchy, IKLimbJointHierarchy)
        self.ik_hierarchy.create_ik_setup()

    def create_fk_hierarchy(self):
        """Creates the fk hierarchy
        """
        self.fk_hierarchy = self.base_hierarchy.duplicate(class_=FKLimbJointHierarchy, suffix="_fk")
        # set joint radius
        base_radius = self.base_hierarchy.joints[0].radius.get()
        for j in self.fk_hierarchy.joints:
            j.radius.set(base_radius * 3)
        assert isinstance(self.fk_hierarchy, FKLimbJointHierarchy)

    def create_bendy_hierarchy(self, subdivision=2):
        """Creates bendy hierarchy
        """
        self.bendy_hierarchy = self.base_hierarchy.duplicate(
            class_=BendyLimbJointHierarchy, suffix="_bendy", subdivision=subdivision
        )
        base_radius = self.base_hierarchy.joints[0].radius.get()
        for j in self.bendy_hierarchy.joints:
            j.radius.set(base_radius * 0.5)
        assert isinstance(self.bendy_hierarchy, BendyLimbJointHierarchy)
        self.bendy_hierarchy.create_bendy_setup(control_hierarchy=self.base_hierarchy)


class SpineRigger(RiggerBase):
    """creates a stretchy spine setup
    """
    pass


class ReverseFootRigger(RiggerBase):
    """Creates reverse foot rig
    """
    pass

    def create(self):
        # reverse_foot_controller = pm.selected()[0]
        # foot_ik_ankle_joint = pm.selected()[0]
        # foot_ik_ball_joint = pm.selected()[0]
        # foot_ik_tip_joint = pm.selected()[0]
        #
        # attrs = [
        #     'tipHeading',
        #     'tipRoll',
        #     'tipBank',
        #     'ballRoll',
        #     'ballBank'
        # ]
        #
        #
        # for attr in attrs:
        #     pm.addAttr(reverse_foot_controller, ln=attr, at='float', k=1)
        #
        # reverse_foot_controller.tipHeading >> foot_ik_tip_joint.ry
        # reverse_foot_controller.tipRoll >> foot_ik_tip_joint.rx
        # reverse_foot_controller.tipBank >> foot_ik_tip_joint.rz
        #
        # reverse_foot_controller.ballRoll >> foot_ik_ball_joint.rx
        # reverse_foot_controller.ballBank >> foot_ik_ball_joint.rz
        pass


class SquashStretchBendRigger(object):
    """creates squash/stretch/bend rig

    :param geo: The geometry to create the rig for.
    """

    def __init__(self, geo=None, use_squash=True, use_delta_mush=True):
        self.geo = geo
        self.bend_deformer = None
        self.bend_handle = None

        self.use_squash = use_squash
        self.squash_deformer = None
        self.squash_handle = None

        self.use_delta_mush = use_delta_mush
        self.delta_mush = None

        self.decompose_matrix = None
        self.distance_between1 = None
        self.distance_between2 = None

        self.aim_locator1 = None
        self.aim_locator2 = None
        self.main_control = None

    def check_main_control(self):
        """checks the existence of the main control
        """
        if self.main_control is None:
            raise RuntimeError("Please create the main controller first")

    def setup(self):
        """creates all the necessary nodes
        """
        self.create_main_controller()

        if self.use_squash:
            self.create_squash_deformer()

        self.create_bend_deformer()

        if self.use_delta_mush:
            self.create_delta_mush_deformer()

        self.finalize_setup()

    def create_main_controller(self):
        """creates the main controller
        """
        bbox = self.geo.getBoundingBox()
        y_min = bbox.min().y
        y_max = bbox.max().y
        h = bbox.height()

        # create main controller
        self.main_control = pm.spaceLocator(name="ssb_main_control")
        self.main_control.t.set(bbox.center())
        self.main_control.ty.set(y_max)
        auxiliary.axial_correction_group(self.main_control)
        self.decompose_matrix = pm.nt.DecomposeMatrix()
        self.main_control.worldMatrix[0] >> self.decompose_matrix.inputMatrix

    def create_squash_deformer(self):
        """creates the squash deformer
        """
        self.check_main_control()

        bbox = self.geo.getBoundingBox()
        y_min = bbox.min().y
        h = bbox.height()

        # create squash deformer
        self.squash_deformer, self.squash_handle = pm.nonLinear(self.geo, type='squash')
        self.squash_deformer.lowBound.set(0)
        self.squash_handle.ty.set(y_min)
        self.squash_handle.s.set(h, h, h)

        # create distance between node1
        self.distance_between1 = pm.nt.DistanceBetween()
        self.squash_handle.t >> self.distance_between1.point1
        self.decompose_matrix.outputTranslate >> self.distance_between1.point2

        # Squash
        pm.setDrivenKeyframe(self.squash_deformer.factor, cd=self.distance_between1.distance, itt="clamped", ott="clamped")
        self.main_control.ty.set(-h * 0.5)
        self.squash_deformer.factor.set(-1)
        pm.setDrivenKeyframe(self.squash_deformer.factor, cd=self.distance_between1.distance, itt="clamped", ott="clamped")
        self.main_control.ty.set(0)

        # adjust infinity of the keyframes to be linear
        anim_curve = self.squash_deformer.factor.inputs(type=pm.nt.AnimCurve)[0]
        anim_curve.setPreInfinityType(infinityType='linear')
        anim_curve.setPostInfinityType(infinityType='linear')

    def create_bend_deformer(self):
        """creates the bend deformer
        """
        self.check_main_control()

        bbox = self.geo.getBoundingBox()
        y_min = bbox.min().y
        h = bbox.height()

        # create aim locator1 (for bend direction)
        self.aim_locator1 = pm.spaceLocator(name="ssb_aim_locator#")
        self.aim_locator1.t.set(bbox.center())
        self.aim_locator1.ty.set(y_min)

        # create aim locator2 (for bend curvature)
        self.aim_locator2 = pm.spaceLocator(name="ssb_aim_locator#")

        # create bend deformer
        self.bend_deformer, self.bend_handle = pm.nonLinear(self.geo, type='bend')
        self.bend_deformer.lowBound.set(0)
        self.bend_deformer.highBound.set(1)
        self.bend_handle.ty.set(y_min)
        self.bend_handle.s.set(h, h, h)
        pm.parent(self.aim_locator2, self.bend_handle, r=1)

        # create aim constraint for the bend.curvature control
        pm.aimConstraint(self.main_control, self.aim_locator2, skip=["x", "y"], aimVector=[1, 0, 0], upVector=[0, 1, 0])

        # create constraints
        # main to aim locator
        pm.pointConstraint(self.main_control, self.aim_locator1, skip="y")

        # create aim constraint
        pm.aimConstraint(self.aim_locator1, self.bend_handle, upVector=[0, 1, 0], aimVector=[1, 0, 0])

        # create set driven keys
        # bend
        pm.setDrivenKeyframe(self.bend_deformer.curvature, cd=self.aim_locator2.rz, itt="clamped", ott="clamped")
        self.main_control.tx.set(h)
        self.bend_deformer.curvature.set(90)
        pm.setDrivenKeyframe(self.bend_deformer.curvature, cd=self.aim_locator2.rz, itt="clamped", ott="clamped")
        self.main_control.tx.set(0)
        # adjust infinity of the keyframes to be linear
        anim_curve = self.bend_deformer.curvature.inputs(type=pm.nt.AnimCurve)[0]
        anim_curve.setPreInfinityType(infinityType='linear')
        anim_curve.setPostInfinityType(infinityType='linear')

    def create_delta_mush_deformer(self):
        self.check_main_control()

        # finally add delta mush
        self.delta_mush = pm.deltaMush(
            self.geo,
            smoothingIterations=10,
            smoothingStep=0.5,
            pinBorderVertices=1,
            envelope=1
        )
        self.delta_mush.inwardConstraint.set(0.25)
        self.delta_mush.outwardConstraint.set(0.25)
        self.delta_mush.distanceWeight.set(0.25)

    def finalize_setup(self):
        """does final clean up
        """
        self.check_main_control()

        # group the node together
        parent_group = pm.nt.Transform(name='SquashStretchBendRiggerGroup#')
        pm.parent(self.main_control.getParent(), parent_group)
        pm.parent(self.aim_locator1, parent_group)
        if self.use_squash:
            pm.parent(self.squash_handle, parent_group)

        pm.parent(self.bend_handle, parent_group)

        # set visibilities
        self.aim_locator1.v.set(0)
        if self.use_squash:
            self.squash_handle.v.set(0)
        self.bend_handle.v.set(0)

        # as a gesture select the main control
        pm.select(self.main_control)
