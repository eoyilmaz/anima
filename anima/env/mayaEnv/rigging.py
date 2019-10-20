# -*- coding: utf-8 -*-
# Copyright (c) 2012-2019, Erkan Ozgur Yilmaz
#
# This module is part of anima and is released under the BSD 2
# License: http://www.opensource.org/licenses/BSD-2-Clause

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


class PinController(object):
    """A pin controller is a snappy type of controller where the object is free
    too move but because its movement is compensated with a parent group it
    stays at the same position in the space.

    It is mainly used in facial rigs. Where the controller seems to be
    controlling the object that it is deforming without any cyclic dependency
    """
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

        vtx_coord = pm.xform(self.pin_to_vertex, ws=1, t=1)

        self.pin_to_shape = self.pin_to_vertex.node()
        self.pin_uv = self.pin_to_shape.getUVAtPoint(vtx_coord, space='world')

        # create a sphere with the size of pin_size
        self.pin_transform, self.pin_shape = pm.sphere(radius=self.size)

        # create two axial correction groups
        self.compensation_group = \
            auxiliary.axial_correction_group(self.pin_node)

        self.axial_correction_group = \
            auxiliary.axial_correction_group(self.compensation_group)

        # create compensation setup
        decompose_matrix = pm.nt.DecomposeMatrix()
        self.pin_transform.inverseMatrix >> decompose_matrix.inputMatrix
        decompose_matrix.outputTranslate >> self.compensation_group.t
        decompose_matrix.outputRotate >> self.compensation_group.r
        decompose_matrix.outputScale >> self.compensation_group.s

        # create a follicle on the shape at the given uv
        self.follicle_transform, self.follicle_shape = \
            auxiliary.create_follicle(self.pin_to_shape, self.pin_uv)

        # move the axial correction group
        pm.xform(self.axial_correction_group, ws=1, t=vtx_coord)


class SkinTools(object):
    """A helper utility for easy joint influence edit.

    Developers Note: This is converted from a very old MEL script, so don't
    judge me on the code quality. I will probably update it to a more modern
    Python implementation as I keep using it.
    """
    __version__ = "2.3.1"
    weight_threshold = 0.00001

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

    def ui(self):
        """the ui
        """
        import functools
        width = 300
        height = 380

        if pm.window("skinTools_window", q=1, ex=1):
            pm.deleteUI("skinTools_window", window=1)

        self.window = pm.window("skinTools_window", w=width, h=height,
                                t="skinTools %s" % self.__version__)

        self.form_layout1 = pm.formLayout("skinTools_formLayout1", nd=100)
        with self.form_layout1:

            self.column_layout1 = \
                pm.columnLayout("skinTools_columnLayout1", adj=1, cal="center")
            with self.column_layout1:
                pm.button(
                    l="find skinCluster from selection",
                    c=self.find_skin_cluster_from_selection_button_proc
                )

                with pm.rowLayout("skinTools_skin_cluster_row_layout", nc=2):
                    pm.text(l="skinCluster: ")
                    self.skin_cluster_text = pm.text(l="")

                with pm.rowLayout("skinTools_mesh_name_row_layout", nc=2):
                    pm.text(l="mesh name: ")
                    self.mesh_name_text = pm.text()

                pm.button(
                    l="find influenced Vertices",
                    c=self.find_influenced_vertices_button_proc
                )

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
                def set_joint_weight_callback(weight, *args):
                    print("weight: %s" % weight)
                    print("args: %s" % args)
                    self.set_joint_weight(weight)
                self.remove_selected_button = \
                    pm.button(l="remove selected",
                              c=functools.partial(set_joint_weight_callback, 0))
                self.add_selected_button = \
                    pm.button(l="add selected",
                              c=functools.partial(set_joint_weight_callback, 1))

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

        self.find_skin_cluster_from_selection_button_proc()
        pm.showWindow(self.window)
        pm.window(self.window, e=1, w=width, h=height)

    @measure_time("find_skin_cluster_from_selection_button_proc")
    def find_skin_cluster_from_selection_button_proc(self, *args):
        """the skinCluster_text should be filled with the skinCluster name
        """
        self.fill_skin_cluster_text_field()
        self.fill_mesh_name_text_field()
        self.update_list()

    @measure_time("find_influenced_vertices_button_proc")
    def find_influenced_vertices_button_proc(self, *args):
        """
        """
        # get the joint name from list
        mesh = self.get_mesh_name_from_interface()
        joint = self.get_selected_item_in_list()
        skin_cluster = self.get_skin_cluster_from_interface()
        influenced_vertices = \
            self.find_influenced_vertices(mesh, joint, skin_cluster)
        pm.select(influenced_vertices)

    @measure_time("fill_skin_cluster_text_field")
    def fill_skin_cluster_text_field(self):
        """
        """
        # try to get the skinCluster from selection
        skin_cluster = self.find_skin_cluster_from_selection()
        pm.text(
            self.skin_cluster_text,
            e=1,
            l=skin_cluster
        )

    @measure_time("fill_mesh_name_text_field")
    def fill_mesh_name_text_field(self):
        """
        """
        mesh_name = self.find_mesh_name_from_selection()
        pm.text(self.mesh_name_text, e=True, l=mesh_name)

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
            compacted_list.append("%s:%s" % (start_index, current_index))
        else:
            compacted_list.append("%s" % start_index)

        return compacted_list

    @measure_time("get_selected_item_in_list")
    def get_selected_item_in_list(self):
        items = pm.textScrollList(
            self.influence_list_text_scroll_list, q=1, si=1
        )

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

    @measure_time("set_joint_weight")
    def set_joint_weight(self, value):
        selected_index = self.get_selected_index()
        joint_name = self.get_selected_item_in_list()

        temp3 = pm.ls(sl=1, type="joint")
        pm.select(temp3, d=1)
        sel_list = pm.ls(sl=1)
        pm.select(temp3, add=1)

        skin_cluster = self.get_skin_cluster(sel_list[0])

        if not skin_cluster:
            # try to get it from the interface
            skin_cluster = self.get_skin_cluster_from_interface()

        if value:
            temp3 = pm.ls(sl=1, type="joint")
            joint_name = temp3[0]

        print("skin_cluster: %s" % skin_cluster)
        print("sel_list    : %s" % sel_list)
        print("join_name   : %s" % joint_name)
        print("value       : %s" % value)
        pm.skinPercent(skin_cluster, sel_list, tv=[(joint_name, value)])

        self.update_list()

        if value == 0:
            number_of_items = self.get_number_of_items()
            selected_index = selected_index if selected_index < number_of_items else number_of_items
            pm.textScrollList(
                self.influence_list_text_scroll_list, e=1, sii=selected_index
            )

    @measure_time("find_mesh_name_from_selection")
    def find_mesh_name_from_selection(self):
        sel_list = pm.ls(sl=1, o=1)
        if sel_list:
            return sel_list[0]
        return

    @measure_time("find_skin_cluster_from_selection")
    def find_skin_cluster_from_selection(self):
        sel_list = pm.ls(sl=1, l=1)
        return self.find_skin_cluster(sel_list)

    @measure_time("find_skin_cluster")
    def find_skin_cluster(self, input_list):
        """finds the skin cluster

        :param input_list:
        :return:
        """
        # if not input_list:
        #     return
        #
        # # get the selected objects only
        # new_list = pm.ls(input_list, l=1, o=1, type="transform")
        #
        # if not new_list:
        #     # some components should have been given as the inputList
        #     new_list = pm.ls(input_list, l=1, o=1)
        #
        #     # try to find the parent transform node
        #     # just use the first shape node
        #     if isinstance(new_list[0], pm.nt.Mesh):
        #         new_list = pm.listRelatives(p=1, f=new_list[0])
        #
        # if not new_list:
        #     return
        #
        # # we need to find a mesh or a transform node that has the mesh
        # print("new_list: %s" % new_list)
        # for node in new_list:
        #     shape = node if isinstance(node, pm.nt.Mesh) else node.getShape()
        #     history = shape.listHistory()
        #     skin_clusters = pm.ls(history, type=pm.nt.SkinCluster)
        #     if len(skin_clusters):
        #         return skin_clusters[0]
        for node in input_list:
            if isinstance(node, pm.MeshVertex):
                shape = node.node()
            elif isinstance(node, pm.nt.Mesh):
                shape = node
            elif isinstance(node, pm.nt.Transform):
                if not isinstance(node, pm.nt.Joint):
                    shape = node.getShape()
                else:
                    continue

            # shape = node if isinstance(node, pm.nt.Mesh) else node.getShape()
            history = shape.listHistory()
            skin_clusters = pm.ls(history, type=pm.nt.SkinCluster)
            if len(skin_clusters):
                return skin_clusters[0]

    @measure_time("get_skin_cluster")
    def get_skin_cluster(self, element):
        """

        :param element:
        :return:
        """
        if isinstance(element, pm.MeshVertex):
            shape = element.node()
            transform = shape.getParent()
            shapes = transform.getShapes()
        elif isinstance(element, pm.nt.Transform):
            shapes = element.getShapes()
        elif isinstance(element, pm.nt.Mesh):
            transform = element.getParent()
            shapes = transform.getShapes()

        real_shape = None
        for shape in shapes:
            if shape.intermediateObject.get():
                real_shape = shape

        if not real_shape:
            return

        object_sets = real_shape.listConnections(
            p=0, s=1, d=1, c=1, t="objectSet", et=1
        )
        for object_set in object_sets:
            con_from_obj_sets = object_set.listConnections(
                p=0, s=1, d=1, c=1, t="skinCluster", et=1
            )
            for c in con_from_obj_sets:
                if isinstance(c, pm.nt.SkinCluster):
                    return c

    @measure_time("get_skin_cluster_from_interface")
    def get_skin_cluster_from_interface(self):
        text = pm.text(self.skin_cluster_text, q=1, l=1)
        print("text: %s" % text)
        try:
            return pm.PyNode(text)
        except pm.MayaNodeError:
            pass

    @measure_time("get_mesh_name_from_interface")
    def get_mesh_name_from_interface(self):
        text = pm.text(self.mesh_name_text, q=1, l=1)
        if text:
            return pm.PyNode(text)

    @measure_time("update_list")
    def update_list(self):
        # clear the list
        pm.textScrollList(self.influence_list_text_scroll_list, e=1, ra=1)

        # remove joints from selection list
        sel_joints = pm.ls(sl=1, type="joint")
        pm.select(sel_joints, d=1)

        # get the vertex list without joints
        sel_list = pm.ls(sl=1)

        new_list = self.convert_to_vertex_list(sel_list)
        sel_list = new_list
        skin_cluster = self.get_skin_cluster_from_interface()

        # get joint names that influence currently selected vertices
        joints = self.get_joints_affecting_components(sel_list, skin_cluster)


        # and add the new joint names to the list
        # add the hold status to the name of the joint
        for joint in joints:
            display_string = joint.name()

            if joint.liw.get():
                display_string = "%s (h)" % display_string

            pm.textScrollList(
                self.influence_list_text_scroll_list,
                e=1, append=display_string
            )

    @measure_time("get_joints_affecting_components")
    def get_joints_affecting_components(self, component_list, skin_cluster):
        """returns the list of joints affecting the items in the given
        component_list

        :param component_list:
        :param skin_cluster:
        :return:
        """
        # flatten the component list
        joint_list = []
        joints_lut = skin_cluster.getInfluence()
        component_list = pm.ls(component_list, fl=1)
        for component in component_list:
            # print("component: %s" % component)
            index = component.index()

            weight_attr = skin_cluster.wl[index].w
            num_elements = weight_attr.numElements()

            # all_weights = weight_attr.get()
            # map(lambda x, y: x > 0.001, range(num_elements), all_weights)

            # print("len(all_weights): %s" % len(all_weights))
            # print("num_elements    : %s" % num_elements)

            for element_index in range(num_elements):
                weight = weight_attr[element_index].get()
                if weight > 0.00001:
                    try:
                        joint_list.append(joints_lut[element_index])
                    except IndexError:
                        # this happens sometimes
                        pass

        return sorted(list(set(joint_list)), key=lambda x: x.name())

    @measure_time("convert_to_vertex_list")
    def convert_to_vertex_list(self, input_list):
        """converts the given input list to vertex list

        :param input_list:
        :return:
        """
        # start by assuming the inputList is all components
        # convert them all to vertices
        input_list = pm.polyListComponentConversion(
            input_list, fv=1, fe=1, ff=1, fuv=1, fvf=1, tv=1
        )

        # we should all have vertices
        # but some of the items could be meshes or transform nodes
        # try to find them
        possible_non_component_list = \
            pm.ls(input_list, type=["transform", "mesh"])

        if possible_non_component_list:
            for node in possible_non_component_list:
                if isinstance(node, pm.nt.Mesh):
                    shape = node
                elif isinstance(node, pm.nt.Transform):
                    # try to get the mesh
                    shape = node.getShape()

                if shape and isinstance(shape, pm.nt.Mesh):
                    input_list.append("%s.vtx[:]" % shape.name())

        return input_list

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

    @measure_time("find_influenced_vertices")
    def find_influenced_vertices(self, mesh, joint, skin_cluster):
        """returns the vertices of the mesh that influenced by the given joint

        :param mesh:
        :param joint:
        :param skin_cluster:
        :return:
        """
        # if also a joint is selected from the interface use the joint
        sel_list = pm.ls(sl=1, type=pm.nt.Joint)
        if sel_list:
            joint = sel_list[0]

        # get  the joint index
        joint_index = None
        for output_attr, input_attr in \
            joint.worldMatrix.listConnections(
                c=1, d=1, s=1, p=1, t=pm.nt.SkinCluster, et=1
            ):
            connected_skin_cluster = input_attr.node()
            if connected_skin_cluster == skin_cluster:
                joint_index = input_attr.index()
                break

        if joint_index is None:
            return

        vertex_count = pm.polyEvaluate(mesh, v=1)
        index_list = []
        for i in range(vertex_count):
            # get the weights
            weight = skin_cluster.wl[i].w[joint_index].get()

            if weight > self.weight_threshold:
                index_list.append(i)

        new_index_list = self.squeeze_index_list(index_list)

        new_sel_list = []
        for i in range(len(new_index_list)):
            new_sel_list.append(
                "%s.vtx[%s]" % (mesh.name(), new_index_list[i])
            )

        # pm.select(new_sel_list)
        return new_sel_list
