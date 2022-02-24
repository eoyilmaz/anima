# -*- coding: utf-8 -*-


class NodeUtils(object):
    """Node related utils for Fusion
    """

    def get_active_node(self):
        """returns the active node
        """
        from anima.dcc.blackmagic import get_fusion
        fusion = get_fusion()
        comp = fusion.GetCurrentComp()
        return comp.ActiveTool

    @classmethod
    def list_input_ids(cls, node):
        """List input ids of the given node
        :param node:
        :return:
        """
        node_input_list = node.GetInputList()
        for input_entry_key in node_input_list.keys():
            input_entry = node_input_list[input_entry_key]
            input_id = input_entry.GetAttrs()['INPS_ID']
            print("%s: %s" % (input_entry_key, input_id))

    @classmethod
    def get_node_attr(cls, node, attr):
        """gets node attr, sadly we need that

        :param node:
        :param attr:
        :return:
        """
        node_input_list = node.GetInputList()
        for input_entry_key in node_input_list.keys():
            input_entry = node_input_list[input_entry_key]
            input_id = input_entry.GetAttrs()['INPS_ID']
            if input_id == attr:
                return input_entry[0]

    @classmethod
    def set_node_attr(cls, node, attr, value):
        """sets node attr, sadly we need that too

        :param node:
        :param attr:
        :param value:
        :return:
        """
        node_input_list = node.GetInputList()
        for input_entry_key in node_input_list.keys():
            input_entry = node_input_list[input_entry_key]
            input_id = input_entry.GetAttrs()['INPS_ID']
            if input_id == attr:
                input_entry[0] = value
                break


class TDE4LensDistortionImporter(object):
    """Imports lens files
    """

    lens_model_mapper = {
        "3DE4 Radial - Standard, Degree 4": "DE4RadialStandardDegree4",
    }

    def __init__(self):
        from anima.dcc.blackmagic import get_fusion
        self.fusion = get_fusion()
        self.comp = self.fusion.GetCurrentComp()

    def import_(self, lens_file_path):
        """imports the
        """
        # load 3de4 lens info
        from anima.dcc.equalizer import TDE4Lens
        lens = TDE4Lens()
        lens.load(lens_file_path)

        # create the lens distortion node
        lens_distort = self.comp.LensDistort()
        NodeUtils.set_node_attr(lens_distort, "Mode", "Distort")
        NodeUtils.set_node_attr(lens_distort, "Model", self.lens_model_mapper[lens.distortion_model])
        NodeUtils.set_node_attr(lens_distort, "DE4RadialStandardDegree4.DistortionDegree2", lens.distortion_degree_2)
        NodeUtils.set_node_attr(lens_distort, "DE4RadialStandardDegree4.UDegree2", lens.u_degree_2)
        NodeUtils.set_node_attr(lens_distort, "DE4RadialStandardDegree4.VDegree2", lens.v_degree_2)
        NodeUtils.set_node_attr(lens_distort, "DE4RadialStandardDegree4.QuarticDistortionDegree4", lens.distortion_degree_4)
        NodeUtils.set_node_attr(lens_distort, "DE4RadialStandardDegree4.UDegree4", lens.u_degree_4)
        NodeUtils.set_node_attr(lens_distort, "DE4RadialStandardDegree4.VDegree4", lens.v_degree_4)
        NodeUtils.set_node_attr(lens_distort, "DE4RadialStandardDegree4.PhiCylindricDirection", lens.phi)
        NodeUtils.set_node_attr(lens_distort, "DE4RadialStandardDegree4.BCylindricBending", lens.beta)
        NodeUtils.set_node_attr(lens_distort, "FLength", lens.focal_length)
        NodeUtils.set_node_attr(lens_distort, "FilmGate", "User")
        NodeUtils.set_node_attr(lens_distort, "ApertureW", lens.horizontal_aperture / 25.4)
        NodeUtils.set_node_attr(lens_distort, "ApertureH", lens.vertical_aperture / 25.4)
        NodeUtils.set_node_attr(lens_distort, "ResolutionGateFit", "Width")
        NodeUtils.set_node_attr(lens_distort, "LensShiftX", lens.lens_center_offset_x)
        NodeUtils.set_node_attr(lens_distort, "LensShiftY", lens.lens_center_offset_y)
        # NodeUtils.set_node_attr(lens_distort, "FocusDist", )


class TDE4PointImporter(object):
    """Imports 3DEqualizer points as tracker point data
    """

    def __init__(self, xres=1920, yres=1080):
        self.xres = xres
        self.yres = yres

    def load_points(self, path):
        """loads the points from the given path
        """
        from anima.dcc import equalizer
        pm = equalizer.TDE4PointManager()
        pm.read(path)

        from anima.dcc import fusion
        f = fusion.Fusion()
        comp = f.comp

        node_template = """{{
        Tools = ordered() {{
            Tracker1 = Tracker {{
                Trackers = {{
                    {{
                        PatternTime = 0,
                        PatternX = 0.5,
                        PatternY = 0.5
                    }}
                }},
                CtrlWZoom = false,
                Inputs = {{
                    Name = Input {{ Value = "Tracker1", }},
                    PatternCenter1 = Input {{ Value = {{ 0.5, 0.5 }}, }},
                    TrackedCenter1 = Input {{
                        SourceOp = "XYPath1",
                        Source = "Value",
                    }},
                }},
                ViewInfo = OperatorInfo {{ Pos = {{ 715, 82.5 }} }},
            }},
            XYPath1 = XYPath {{
                ShowKeyPoints = false,
                DrawMode = "ModifyOnly",
                CtrlWZoom = false,
                Inputs = {{
                    X = Input {{
                        SourceOp = "XYPath1X",
                        Source = "Value",
                    }},
                    Y = Input {{
                        SourceOp = "XYPath1Y",
                        Source = "Value",
                    }},
                }},
            }},
            XYPath1X = BezierSpline {{
                SplineColor = {{ Red = 255, Green = 0, Blue = 0 }},
                NameSet = true,
                KeyFrames = {{
{x_keyframe_data}
                }}
            }},
            XYPath1Y = BezierSpline {{
                SplineColor = {{ Red = 0, Green = 255, Blue = 0 }},
                NameSet = true,
                KeyFrames = {{
{y_keyframe_data}
                }}
            }}
        }},
        ActiveTool = "Tracker1"
}}
"""

        keyframe_template = "                    [{frame}] = {{ {value}, LH = {{ {frame}.666666666667, {value} }}, " \
                            "RH = {{ {frame}.3333333333333, {value} }}, Flags = {{ Linear = true }} }}"

        x_keyframe_data = []
        y_keyframe_data = []

        float_x_res = float(self.xres)
        float_y_res = float(self.yres)
        # print("float_x_res: %s" % float_x_res)
        # print("float_y_res: %s" % float_y_res)

        for point in pm.points:
            assert isinstance(point, equalizer.TDE4Point)
            for frame in sorted(point.data):
                pos_data = point.data[frame]
                # print("pos_data: %s" % pos_data)

                x_keyframe_data.append(keyframe_template.format(frame=frame, value=float(pos_data[0]) / float_x_res))
                y_keyframe_data.append(keyframe_template.format(frame=frame, value=float(pos_data[1]) / float_y_res))

        rendered_data = node_template.format(
            x_keyframe_data=",\n".join(x_keyframe_data),
            y_keyframe_data=",\n".join(y_keyframe_data)
        )

        # print("rendered_data: %s" % rendered_data)
        # print(f.fusion.SetClipboard([rendered_data]))
        # from anima.dcc import blackmagic as bmd
        # bmf = bmd.get_bmd()
        # print(bmf.setclipboard(rendered_data))
        # print(f.fusion.SetClipboard(rendered_data))
        # print(f.fusion.GetClipboard())
        # print(comp.Paste())
        # table = f.fusion.GetClipboard()
        # f.comp.Paste(table)

        # TODO: Fuck you Fusion...
        from anima.ui.lib import QtWidgets
        clipboard = QtWidgets.QApplication.clipboard()
        clipboard.setText(rendered_data)
        print("Please Ctrl+V to create the node!")
