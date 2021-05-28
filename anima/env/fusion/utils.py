# -*- coding: utf-8 -*-


class NodeUtils(object):
    """Node related utils for Fusion
    """

    def get_active_node(self):
        """returns the active node
        """
        from anima.env.blackmagic import get_fusion
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
        from anima.env.blackmagic import get_fusion
        self.fusion = get_fusion()
        self.comp = self.fusion.GetCurrentComp()

    def import_(self, lens_file_path):
        """imports the
        """
        # load 3de4 lens info
        from anima.env.equalizer import TDE4Lens
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
