# -*- coding: utf-8 -*-
# Copyright (c) 2012-2017, Anima Istanbul
#
# This module is part of anima-tools and is released under the BSD 2
# License: http://www.opensource.org/licenses/BSD-2-Clause

import MaxPlus
from anima.render.mat_converter import ConversionManagerBase, NodeCreatorBase


CONVERSION_SPEC_SHEET = {
    'VRayMtl': {
        # RedShitt Material
        'node_type': MaxPlus.Mtl,
        'secondary_type': 'Redshift Material',

        # 'call_after': # write the code here to assign this material to
        # all of the objects that is using the VRayMtl

        'attributes': {
            'diffuse': 'diffuse_color',
            'diffuse_roughness': 'diffuse_roughness',
            'selfIllumination': 'emission_color',
            # 'selfIllumination_gi': '',
            'selfIllumination_multiplier': 'emission_weight',
            'reflection': 'refl_color',
            'reflection_glossiness': 'refl_roughness',
            # 'hilight_glossiness': '',
            # 'reflection_subdivs': {
            #     'refl_samples': lambda x: 16,
            # },

            # 'reflection_fresnel': '',

            'reflection_maxDepth': 'refl_depth',
            # 'reflection_exitColor': '',

            # 'reflection_useInterpolation': '',
            'reflection_ior': 'refl_ior',
            # 'reflection_lockGlossiness': '',
            # 'reflection_lockIOR': '',

            # 'reflection_dimDistance': '',
            # 'reflection_dimDistance_on': '',
            # 'reflection_dimDistance_falloff': '',

            # 'reflection_affectAlpha': '',

            'refraction': 'refr_color',
            'refraction_glossiness': {
                'refr_roughness': lambda x: x,
                'refr_isGlossiness': True,
            },
            # 'refraction_subdivs': '',
            'refraction_ior': 'refr_ior',

            # 'refraction_fogColor': '',
            # 'refraction_fogMult': '',
            # 'refraction_fogBias': '',
            # 'refraction_affectShadows': '',
            # 'refraction_affectAlpha': '',

            'refraction_maxDepth': 'refr_depth',
            # 'refraction_exitColor': '',
            # 'refraction_useExitColor': '',
            # 'refraction_useInterpolation': '',

            # 'refraction_dispersion': 'refr_abbe',
            'refraction_dispersion_on': {
                'refr_abbe': lambda x, y:
                y.ParameterBlock.GetParamByName('refraction_dispersion').GetValue()
                if ((x - 1.0) / 149.0) else 0  # VRay uses a value between 1-150
                                               # fit it in to 0-100 range
            },

            # 'translucency_on': '',
            # 'translucency_thickness': '',
            # 'translucency_scatterCoeff': '',
            # 'translucency_fbCoeff': '',

            'translucency_multiplier': 'transl_weight',
            'translucency_color': 'transl_color',

            'brdf_type': {
                'refl_brdf': lambda x: {0: 0, 1: 0, 2: 2, 4: 1}[x],
            },

            'anisotropy': 'refl_aniso',
            'anisotropy_rotation': 'refl_aniso_rotation',

            # 'anisotropy_derivation': '',
            # 'anisotropy_axis': '',
            # 'anisotropy_channel': '',

            # 'soften': '',  # Couldn't find it in the UI

            # 'brdf_fixDarkEdges': '',
            # 'gtr_gamma': '',
            # 'gtr_oldGamma': '',

            'brdf_useRoughness': {
                'refl_isGlossiness': lambda x: not x,
            },

            # 'option_traceDiffuse': '',
            # 'option_traceReflection': '',
            # 'option_traceRefraction': '',
            # 'option_doubleSided': '',
            # 'option_reflectOnBack': '',
            # 'option_useIrradMap': '',

            # 'refraction_fogUnitsScale_on': '',
            # 'option_traceDiffuseAndGlossy': '',
            'option_cutOff': {
                'refl_cutoff': lambda x: x,
                'refr_cutoff': lambda x: x,
            },

            'preservationMode': {
                'energyCompMode': lambda x: 1 - x
            },

            # 'option_environment_priority': '',
            # 'effect_id': '',  # There should have been a material_id but
                                # like the one in Maya, but I couldn't find it
            # 'override_effect_id': '',
            # 'option_clampTextures': '',
            # 'option_opacityMode': '',  # May be related with the
                                         # affects_alpha option

            # 'option_glossyFresnel':,

            'texmap_diffuse': 'diffuse_color_map',
            'texmap_diffuse_on': 'diffuse_color_mapenable',
            'texmap_diffuse_multiplier': 'diffuse_color_mapamount',

            'texmap_reflection': 'refl_color_map',
            'texmap_reflection_on': 'refl_color_mapenable',
            'texmap_reflection_multiplier': 'refl_color_mapamount',

            'texmap_refraction': 'refr_color_map',
            'texmap_refraction_on': 'refr_color_mapenable',
            'texmap_refraction_multiplier': 'refr_color_mapamount',

            'texmap_bump': 'bump_input_map',
            'texmap_bump_on': 'bump_input_mapenable',
            'texmap_bump_multiplier': 'bump_input_mapamount',

            'texmap_reflectionGlossiness': 'refl_roughness_map',
            'texmap_reflectionGlossiness_on': 'refl_roughness_mapenable',
            'texmap_reflectionGlossiness_multiplier': 'refl_roughness_mapamount',

            'texmap_refractionGlossiness': 'refr_roughness_map',
            'texmap_refractionGlossiness_on': 'refr_roughness_mapenable',
            'texmap_refractionGlossiness_multiplier': 'refr_roughness_mapamount',

            'texmap_refractionIOR': 'refr_ior_map',
            'texmap_refractionIOR_on': 'refr_ior_mapenable',
            'texmap_refractionIOR_multiplier': 'refr_ior_mapamount',

            'texmap_displacement': 'displacement_input_map',
            'texmap_displacement_on': 'displacement_input_mapenable',
            'texmap_displacement_multiplier': 'displacement_input_mapamount',

            'texmap_translucent': 'transl_color_map',
            'texmap_translucent_on': 'transl_color_mapenable',
            'texmap_translucent_multiplier': 'transl_color_mapamount',

            # 'texmap_environment': '',
            # 'texmap_environment_on': '',
            #
            # 'texmap_hilightGlossiness': '',
            # 'texmap_hilightGlossiness_on': '',
            # 'texmap_hilightGlossiness_multiplier': '',

            'texmap_reflectionIOR': 'refl_ior_map',
            'texmap_reflectionIOR_on': 'refl_ior_mapenable',
            'texmap_reflectionIOR_multiplier': 'refl_ior_mapamount',

            'texmap_opacity': 'opacity_color_map',
            'texmap_opacity_on': 'opacity_color_mapenable',
            'texmap_opacity_multiplier': 'opacity_color_mapamount',

            'texmap_roughness': 'diffuse_roughness_map',
            'texmap_roughness_on': 'diffuse_roughness_mapenable',
            'texmap_roughness_multiplier': 'diffuse_roughness_mapamount',

            'texmap_anisotropy': 'refl_aniso_map',
            'texmap_anisotropy_on': 'refl_aniso_mapenable',
            'texmap_anisotropy_multiplier': 'refl_aniso_mapamount',

            'texmap_anisotropy_rotation': 'refl_aniso_rotation_map',
            'texmap_anisotropy_rotation_on': 'refl_aniso_rotation_mapenable',
            'texmap_anisotropy_rotation_multiplier': 'refl_aniso_rotation_mapamount',

            # 'texmap_refraction_fog': '',
            # 'texmap_refraction_fog_on': '',
            # 'texmap_refraction_fog_multiplier': '',

            'texmap_self_illumination': 'emission_color_map',
            'texmap_self_illumination_on': 'emission_color_mapenable',
            'texmap_self_illumination_multiplier': 'emission_color_mapamount',

            # 'reflect_minRate': '',
            # 'reflect_maxRate': '',
            # 'reflect_interpSamples': '',
            # 'reflect_colorThreshold': '',
            # 'reflect_normalThreshold': '',
            # 'refract_minRate': '',
            # 'refract_maxRate': '',
            # 'refract_interpSamples': '',
            # 'refract_colorThreshold': '',
            # 'refract_normalThreshold': '',
        }

    }
}


class NodeCreator(NodeCreatorBase):
    """Creates nodes according to the given specs
    """

    def create(self):
        """creates the node
        """
        node_class = self.specs.get('node_type')
        secondary_class = self.specs.get('secondary_type')

        new_node = self.create_node_by_type(node_class, secondary_class)

        # add it to Material manager slot
        MaxPlus.MaterialManager.PutMtlToMtlEditor(new_node, 0)
        return new_node

    @classmethod
    def create_node_by_type(cls, node_class, secondary_class):
        """Creates nodes by type name

        :param node_class: The MaxPlus class object (ex: MaxPlus.MtlBase)
        :param str secondary_class: A string for the node type name
        :return:
        """
        # get the class, its id and its super class id
        class_ = ConversionManager.get_class_by_name(secondary_class)

        class_id = class_.ClassId
        super_class_id = class_.SuperClassId

        # create an animatable
        animatable = MaxPlus.Factory.CreateAnimatable(
            super_class_id, class_id, False
        )

        # and cast it to the node_type
        new_node = node_class._CastFrom(animatable)

        return new_node


class ConversionManager(ConversionManagerBase):
    """Manages the conversion from VRay to RedShift
    """

    def __init__(self):
        super(ConversionManager, self).__init__()
        self.conversion_spec_sheet = CONVERSION_SPEC_SHEET
        self.node_creator_factory = NodeCreator

    def rename_node(self, node, new_name):
        """Renames the node

        :param node:
        :param new_name:
        :return:
        """
        node.SetName(MaxPlus.WStr(new_name))

    def get_node_name(self, node):
        """Returns the node name

        :param node:
        :return:
        """
        return node.GetName()

    def get_node_inputs(self, node, attr=None):
        """returns the node inputs

        :param node:
        :param attr:
        :return:
        """
        inputs = []
        if attr is None:
            # return all connected nodes
            for i in range(node.ParameterBlock.Count()):
                param = node.ParameterBlock[i]
                value = param.GetValue()
                if isinstance(value, MaxPlus.Animatable) \
                   and str(value) != 'None':
                    inputs.append(value)
        else:
            param = node.ParameterBlock.GetParamByName(attr)
            value = param.GetValue()
            inputs.append(value)

        return inputs

    def connect_attr(self, source_attr, target_node, target_attr):
        """creates a connection from source_attr to target_attr target_node

        :param source_attr:
        :param target_node:
        :param target_attr:
        :return:
        """
        print('source_attr: %s' % source_attr)
        print('target_node: %s' % target_node)
        print('target_attr: %s' % target_attr)
        param = target_node.ParameterBlock.GetParamByName(target_attr)
        param.Value = source_attr

    @classmethod
    def get_class_by_name(cls, class_name):
        """returns the class_id from the given class_name

        :param str class_name: The class name
        :return MaxPlus.Class_ID:
        """
        for c in MaxPlus.PluginManager.GetClassList().Classes:
            if c.Name == class_name:
                return c

    @classmethod
    def get_class_id_by_name(cls, class_name):
        """returns the class_id from the given class_name

        :param str class_name: The class name
        :return MaxPlus.Class_ID:
        """
        c = cls.get_class_by_name(class_name)
        return c.ClassId

    @classmethod
    def get_super_class_id_by_name(cls, class_name):
        """returns the super class id of the given class

        :param str class_name: Class Name
        :return:
        """
        c = cls.get_class_by_name(class_name)
        return c.SuperClassId

    @classmethod
    def get_class_name(cls, class_id):
        """returns the class_name from the given class_id

        :param class_id:
        :return:
        """
        for cd in MaxPlus.PluginManager.GetClassList().Classes:
            if cd.ClassId == class_id:
                return cd.Name

    def get_node_type(self, node):
        """returns the node type name

        :param node:
        :return:
        """
        return self.get_class_name(node.ClassID)

    def list_nodes(self, type_):
        """list nodes of given type

        :param type_:
        :return:
        """
        # just return materials for now
        mat_lib = MaxPlus.MaterialLibrary.GetSceneMaterialLibrary()

        nodes_to_return = []

        num_materials = mat_lib.GetNumMaterials()
        for i in range(num_materials):
            mat = mat_lib.GetMaterial(i)
            # print('mat.GetFullName: %s' % mat.GetFullName())
            if self.get_node_type(mat) == type_:
                nodes_to_return.append(mat)

        return nodes_to_return

    def get_attr(self, node, attr):
        """returns node attribute value

        :param node:
        :param attr:
        :return:
        """
        return node.ParameterBlock.GetParamByName(attr).GetValue()

    def set_attr(self, node, attr, value):
        """sets parameter value

        :param node:
        :param attr:
        :param value:
        :return:
        """
        node.ParameterBlock.GetParamByName(attr).SetValue(value)

