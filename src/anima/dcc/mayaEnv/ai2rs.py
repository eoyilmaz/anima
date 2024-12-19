# -*- coding: utf-8 -*-
"""Converts the scene from Arnold to RedShift
"""
import pymel.core as pm
from anima.render.mat_converter import ConversionManagerBase, NodeCreatorBase

CONVERSION_SPEC_SHEET = {
    "aiStandard": {
        # rsMaterial
        "node_type": "RedshiftMaterial",
        "secondary_type": "shader",
        "call_after": lambda x, y: y.outColor >> x.outputs(type="shadingEngine", p=1)[0]
        if x.outputs(type="shadingEngine", p=1)
        else None,
        # aiStandard material attributes
        "attributes": {
            "color": [
                "diffuse_color",
                "transl_color",  # backlight color should be same with the
            ],  # diffuse color
            "Kd": "diffuse_weight",
            "diffuseRoughness": "diffuse_roughness",
            # BackLight
            "Kb": "transl_weight",
            # Extended Controls for Diffuse
            "directDiffuse": "diffuse_direct",
            "indirectDiffuse": "diffuse_indirect",
            # Specular
            "KsColor": "refl_color",
            "Ks": "refl_weight",
            "specularRoughness": "refl_roughness",
            "specularAnisotropy": {
                "refl_aniso": lambda x: (x - 0.5) * 2,
            },
            "specularRotation": "refl_aniso_rotation",
            "specularDistribution": "refl_brdf",
            "specularFresnel": {
                # set it do "Color + Edge Tint"
                "refl_fresnel_mode": lambda x: 1
                if x == 1
                else 3
            },
            "Ksn": {
                # setting the ref_reflectivity to 0 kills all the
                # reflection, so set it to a very small number instead
                # to mimic Arnold's fresnel
                "refl_reflectivity": lambda x: (x, x, x)
                if x > 0
                else (0.001, 0.001, 0.001),
                "refl_edge_tint": (1, 1, 1),
            },
            # Extended Controls for Specular
            "directSpecular": "refl_direct",
            "indirectSpecular": "refl_indirect",
            # Just skip any Reflection attribute
            # KrColor, Kr, enableInternalReflections, Fresnel, Krn,
            # reflectionExitUseEnvironment, reflectionExitColor
            # Refraction
            "KtColor": "refr_color",
            "Kt": "refr_weight",
            "IOR": {"refr_ior": lambda x: x if x >= 1.0 else 1.0},
            "FresnelUseIOR": "refr_use_base_IOR",
            "dispersionAbbe": "refr_abbe",
            "refractionRoughness": "refr_roughness",
            "transmittance": "refr_transmittance",
            "opacity": "opacity_color",
            # Skip refractionExitUseEnvironment, refractionExitColor
            # Bump
            "normalCamera": "bump_input",
            # SSS
            # Use the first layer of RSMaterial for the SSS
            "KsssColor": "ms_color0",
            "Ksss": "ms_amount",
            "sssRadius": {
                # set to the mean value of the sssRadius which is a color in
                # Arnold
                "ms_radius0": lambda x: (x[0] + x[1] + x[2])
                / 3.0
            },
            # skip sssProfile
            "emissionColor": "emission_color",
            "emission": "emission_weight",
            # skip caustics attributes
            # enableGlossyCaustics, enableReflectiveCaustics,
            # enableRefractiveCaustics
        },
    },
    "aiStandardSurface": {
        # rsMaterial
        "node_type": "RedshiftMaterial",
        "secondary_type": "shader",
        "call_after": lambda x, y: y.outColor >> x.outputs(type="shadingEngine", p=1)[0]
        if x.outputs(type="shadingEngine", p=1)
        else None,
        # aiStandard material attributes
        "attributes": {
            "baseColor": [
                "diffuse_color",
                "transl_color",  # backlight color should be same with the
            ],  # diffuse color
            "base": "diffuse_weight",
            "diffuseRoughness": "diffuse_roughness",
            # # BackLight
            # 'Kb': 'transl_weight',
            # Extended Controls for Diffuse
            # 'directDiffuse': 'diffuse_direct',
            "indirectDiffuse": "diffuse_indirect",
            # Specular
            "specular": "refl_weight",
            "specularColor": "refl_color",
            "specularRoughness": "refl_roughness",
            "specularIOR": "refl_ior",
            "specularAnisotropy": "refl_aniso",
            "specularRotation": "refl_aniso_rotation",
            "metalness": {
                "refl_metalness": lambda x, y, z: connect_input(
                    y, "metalness", z, "refl_metalness"
                ),
                "refl_fresnel_mode": 2,
                "refl_brdf": 1,  # set to GGX
            },
            # 'specularDistribution': 'refl_brdf',
            # 'specularFresnel': {
            #     # set it do "Color + Edge Tint"
            #     'refl_fresnel_mode': lambda x: 1 if x == 1 else 3
            # },
            # 'Ksn': {
            #     # setting the ref_reflectivity to 0 kills all the
            #     # reflection, so set it to a very small number instead
            #     # to mimic Arnold's fresnel
            #     'refl_reflectivity':
            #         lambda x: (x, x, x) if x > 0 else (0.001, 0.001, 0.001),
            #     'refl_edge_tint': (1, 1, 1)
            # },
            # Extended Controls for Specular
            # 'directSpecular': 'refl_direct',
            "indirectSpecular": "refl_indirect",
            # Just skip any Reflection attribute
            # KrColor, Kr, enableInternalReflections, Fresnel, Krn,
            # reflectionExitUseEnvironment, reflectionExitColor
            # Refraction
            "transmission": "refr_weight",
            "transmissionColor": "refr_color",
            # 'IOR': {
            #     'refr_ior': lambda x: x if x >= 1.0 else 1.0
            # },
            "transmissionScatter": "ss_scatter_coeff",
            "transmissionDispersion": "refr_abbe",
            "thinWalled": "refr_thin_walled",
            # For now skip SSS attributes
            # 'subsurface': 'ss_amount',
            # 'subsurfaceColor': 'ss_scatter_coeff',
            # 'subsurfaceScale': ''
            # Skip refractionExitUseEnvironment, refractionExitColor
            # Bump
            "normalCamera": "bump_input",
            # SSS
            # Use the first layer of RSMaterial for the SSS
            "subsurface": "ms_amount",
            "subsurfaceColor": "ms_color0",
            "subsurfaceRadius": {
                # set to the mean value of the sssRadius which is a color in
                # Arnold
                "ms_radius0": lambda x: (x[0] + x[1] + x[2])
                / 3.0
            },
            # skip sssProfile
            "emissionColor": "emission_color",
            "emission": "emission_weight",
            # skip caustics attributes
            # enableGlossyCaustics, enableReflectiveCaustics,
            # enableRefractiveCaustics
        },
    },
    "aiSkin": {
        # rsMaterial
        "node_type": "RedshiftSkin",
        "secondary_type": "shader",
        "call_after": lambda x, y: y.outColor >> x.outputs(type="shadingEngine", p=1)[0]
        if x.outputs(type="shadingEngine", p=1)
        else None,
        # aiSkin material attributes
        "attributes": {
            "sssWeight": "overall_scale",
            "globalSssRadiusMultiplier": "radius_scale",
            "shallowScatterColor": "shallow_color",
            "shallowScatterWeight": "shallow_weight",
            "shallowScatterRadius": "shallow_radius",
            "midScatterColor": "mid_color",
            "midScatterWeight": "mid_weight",
            "midScatterRadius": "mid_radius",
            "deepScatterColor": "deep_color",
            "deepScatterWeight": "deep_weight",
            "deepScatterRadius": "deep_radius",
            "specularColor": "refl_color0",
            "specularWeight": "refl_weight0",
            "specularRoughness": "refl_gloss0",
            "specularIor": "refl_ior0",
            "sheenColor": "refl_color1",
            "sheenWeight": "refl_weight1",
            "sheenRoughness": "refl_gloss1",
            "sheenIor": "refl_ior1",
            # 'opacity': None,
            # 'opacityColor': None,
            # 'specularInSecondaryRays': None,
            # 'fresnelAffectSss': None,
            "normalCamera": "bump_input",
        },
    },
    "aiAmbientOcclusion": {
        "node_type": "RedshiftAmbientOcclusion",
        "secondary_type": "utility",
        "call_after": lambda x, y: y.outColor >> x.outColor.outputs(p=1)[0],
        "attributes": {
            "white": "bright",
            "black": "dark",
            "spread": "spread",
            "falloff": {"fallOff": lambda x: x + 1},
            "farClip": "maxDistance",
            "invertNormals": "invert",
        },
    },
    "aiNormalMap": {
        "node_type": "RedshiftBumpMap",
        "secondary_type": "texture",
        "call_after": lambda old_node, new_node: connect_output(
            old_node, "outValue", new_node, "out"
        ),
        "attributes": {
            "input": "input",
            "strength": {
                "scale": lambda x: x,  # set the strength directly
                "inputType": lambda x: 1,  # set to normal map
            },
        },
    },
    "aiColorCorrect": {
        "node_type": "RedshiftColorCorrection",
        "secondary_type": "utility",
        "call_after": lambda old_node, new_node: connect_output(
            old_node, "outColor", new_node, "outColor"
        ),
        "attributes": {
            "input": "input",
            "gamma": "gamma",
            "hueShift": {
                "hue": lambda x: (x * 360) % 360,
            },
            "saturation": "saturation",
            "contrast": {
                "contrast": lambda x: x * 0.5,
            },
            "exposure": {"level": lambda x: pow(2, x)},
        },
    },
    "aiRoundCorners": {
        "node_type": "RedshiftRoundCorners",
        "secondary_type": "texture",
        "call_after": lambda old_node, new_node: connect_output(
            old_node, "outValue", new_node, "out"
        ),
        "attributes": {
            "samples": "numSamples",
            "radius": "radius",
            "selfOnly": "sameObjectOnly",
        },
    },
    "aiImage": {
        "node_type": "file",
        "secondary_type": "texture",
        "call_after": lambda old_node, new_node: connect_output(
            old_node, "outColor", new_node, "outColor"
        ),
        "attributes": {"filename": "fileTextureName"},
    },
    # LIGHTS
    "areaLight": {
        "attributes": {
            "aiExposure": {"intensity": lambda x: 2**x},
            "aiSamples": {"shadowRays": 1},
            "aiDecayType": {"decayRate": lambda x: 0 if x == 0 else 2},
            "aiColorTemperature": {
                "color": lambda x, y: pm.arnoldTemperatureToColor(x)
                if y.getAttr("aiUseColorTemperature")
                else y.getAttr("color")
            },
            "color": "color",
        }
    },
    "aiSkyDomeLight": {
        "node_type": "RedshiftDomeLight",
        "secondary_type": "light",
        "attributes": {
            "color": {
                "tex0": lambda x, y: y.attr("color")
                .inputs()[0]
                .getAttr("fileTextureName")
                if y.type() == "file"
                else y.attr("color").inputs()[0].getAttr("filename")
            }
        },
    },
    "pointLight": {
        "attributes": {
            "aiExposure": {"intensity": lambda x: 2**x},
            "aiSamples": {"shadowRays": 1},
            "aiDecayType": {"decayRate": lambda x: 0 if x == 0 else 2},
            "aiColorTemperature": {
                "color": lambda x, y: pm.arnoldTemperatureToColor(x)
                if y.getAttr("aiUseColorTemperature")
                else y.getAttr("color")
            },
            "aiRadius": "lightRadius",
            "color": "color",
        }
    },
    "directionalLight": {
        "attributes": {
            "aiExposure": {"intensity": lambda x: 2**x},
            "aiSamples": {"shadowRays": 1},
            "aiColorTemperature": {
                "color": lambda x, y: pm.arnoldTemperatureToColor(x)
                if y.getAttr("aiUseColorTemperature")
                else y.getAttr("color")
            },
            "aiAngle": "lightAngle",
            "color": "color",
        }
    },
    "mesh": {
        "attributes": {
            "aiSubdivType": {
                "rsEnableSubdivision": lambda x: 1 if x > 0 else 0,
                "rsSubdivisionRule": 0,
                "rsDoSmoothSubdivision": lambda x: 0 if x == 2 else 1,
            },
            "aiSubdivAdaptiveSpace": {
                "rsScreenSpaceAdaptive": lambda x: 1 - x,
            },
            "aiSubdivIterations": "rsMaxTessellationSubdivs",
            "aiDispHeight": "rsDisplacementScale",
            "aiDispAutobump": "rsAutoBumpMap",
        }
    },
}


def connect_input(source_node, source_attr_name, target_node, target_attr_name):
    """Basic connection from source to target node

    :param source_node:
    :param source_attr_name:
    :param target_node:
    :param target_attr_name:
    :return:
    """
    inputs = source_node.attr(source_attr_name).inputs(p=1)
    if inputs:
        inputs[0] >> target_node.attr(target_attr_name)
    else:
        # or set it to the same value
        target_node.attr(target_attr_name).set(source_node.attr(source_attr_name).get())


def connect_output(old_node, old_attr_name, new_node, new_attr_name):
    """Connects the new_node.new_attr_name to the same inputs that the old_node
    was connecting

    :param old_node:
    :param old_attr_name:
    :param new_node:
    :param new_attr_name:
    :return:
    """
    new_plug = new_node.attr(new_attr_name)
    for plug in old_node.attr(old_attr_name).outputs(p=1):
        new_plug >> plug


class ConversionManager(ConversionManagerBase):
    """Manages the conversion from Arnold to RedShift"""

    def __init__(self):
        super(ConversionManager, self).__init__()
        self.conversion_spec_sheet = CONVERSION_SPEC_SHEET
        self.node_creator_factory = NodeCreator

    def get_node_type(self, node):
        """overridden get_node_type method"""
        return pm.nodeType(node)

    def list_nodes(self, type_):
        """

        :param type_:
        :return:
        """
        return pm.ls(type=type_)

    def rename_node(self, node, new_name):
        """renames the node to new_name

        :param node:
        :param new_name:
        :return:
        """
        node.rename(new_name)

    def get_node_name(self, node):
        """returns the node name"""
        return node.name()

    def get_node_inputs(self, node, attr=None):
        """

        :param node:
        :param attr:
        :return:
        """
        if attr:
            if node.hasAttr(attr):
                return node.attr(attr).inputs(p=1)
            else:
                return []
        else:
            return node.inputs(p=1)

    def connect_attr(self, source_attr, target_node, target_attr):
        """creates a connection from source_Attr

        :param source_attr:
        :param target_node:
        :param target_attr:
        :return:
        """
        source_attr >> target_node.attr(target_attr)

    def get_attr(self, node, attr):
        """gets node.attr

        :param node:
        :param attr:
        :return:
        """
        from pymel.core import MayaAttributeError

        try:
            return node.getAttr(attr)
        except MayaAttributeError:
            return

    def set_attr(self, node, attr, value):
        """sets node.attr to value

        :param node:
        :param attr:
        :param value:
        :return:
        """
        try:
            node.setAttr(attr, value)
        except Exception as e:
            print(e)


class NodeCreator(NodeCreatorBase):
    """Creates nodes according to the given specs"""

    def create(self):
        """creates the node"""
        node_type = self.specs.get("node_type")
        secondary_type = self.specs.get("secondary_type")

        if secondary_type == "shader":
            shader, shading_engine = pm.createSurfaceShader(node_type)
            return shader
        elif secondary_type == "utility":
            shader = pm.shadingNode(node_type, asUtility=1)
            return shader
        elif secondary_type == "texture":
            shader = pm.shadingNode(node_type, asTexture=1)
            return shader
        elif secondary_type == "light":
            light_transform = pm.shadingNode(node_type, asLight=1)
            return light_transform.getShape()


class TextureProcessorQueue(object):
    """A queue to convert textures"""

    queue = None
