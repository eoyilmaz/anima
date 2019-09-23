from anima.env.mayaEnv import auxiliary
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

        target_node.r.set(map(math.degrees, wm.eulerRotation()))
        # pm.makeIdentity(
        #     target_node, apply=1, t=False, r=False, s=False, n=False,
        #     jointOrient=True
        # )


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



