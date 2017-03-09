# -*- coding: utf-8 -*-
# Copyright (c) 2012-2015, Anima Istanbul
#
# This module is part of anima-tools and is released under the BSD 2
# License: http://www.opensource.org/licenses/BSD-2-Clause
"""Converts the scene from Arnold to RedShift
"""
import os
import pymel.core as pm

CONVERSION_SPEC_SHEET = {
    'aiStandard': {
        # rsMaterial
        'node_type': 'RedshiftMaterial',
        'secondary_type': 'shader',

        # aiStandard material attributes
        'attributes': {
            'color': [
                'diffuse_color',
                'transl_color',  # backlight color should be same with the
            ],                   # diffuse color
            'Kd': 'diffuse_weight',
            'diffuseRoughness': 'diffuse_roughness',

            # BackLight
            'Kb': 'transl_weight',

            # Extended Controls for Diffuse
            'directDiffuse': 'diffuse_direct',
            'indirectDiffuse': 'diffuse_indirect',

            # Specular
            'KsColor': 'refl_color',
            'Ks': 'refl_weight',
            'specularRoughness': 'refl_roughness',
            'specularAnisotropy': {
                'refl_aniso': lambda x: (x - 0.5) * 2,
            },
            'specularRotation': 'refl_aniso_rotation',
            'specularDistribution': 'refl_brdf',
            'specularFresnel': {
                # set it do "Color + Edge Tint"
                'refl_fresnel_mode': lambda x: 1 if x == 1 else 3
            },
            'Ksn': {
                # setting the ref_reflectivity to 0 kills all the
                # reflection, so set it to a very small number instead
                # to mimic Arnold's fresnel
                'refl_reflectivity':
                    lambda x: (x, x, x) if x > 0 else (0.001, 0.001, 0.001),
                'refl_edge_tint': (1, 1, 1)
            },

            # Extended Controls for Specular
            'directSpecular': 'refl_direct',
            'indirectSpecular': 'refl_indirect',

            # Just skip any Reflection attribute
            # KrColor, Kr, enableInternalReflections, Fresnel, Krn,
            # reflectionExitUseEnvironment, reflectionExitColor

            # Refraction
            'KtColor': 'refr_color',
            'Kt': 'refr_weight',
            'IOR': {
                'refr_ior': lambda x: x if x >= 1.0 else 1.0
            },
            'FresnelUseIOR': 'refr_use_base_IOR',
            'dispersionAbbe': 'refr_abbe',
            'refractionRoughness': 'refr_roughness',
            'transmittance': 'refr_transmittance',
            'opacity': 'opacity_color',

            # Skip refractionExitUseEnvironment, refractionExitColor

            # Bump
            'normalCamera': 'bump_input',

            # SSS
            # Use the first layer of RSMaterial for the SSS
            'KsssColor': 'ms_color0',
            'Ksss': 'ms_amount',
            'sssRadius': {
                # set to the mean value of the sssRadius which is a color in
                # Arnold
                'ms_radius0': lambda x: (x[0] + x[1] + x[2]) / 3.0
            },
            # skip sssProfile

            'emissionColor': 'emission_color',
            'emission': 'emission_weight',

            # skip caustics attributes
            # enableGlossyCaustics, enableReflectiveCaustics,
            # enableRefractiveCaustics
        }
    },

    'aiSkin': {
        # rsMaterial
        'node_type': 'RedshiftSkin',
        'secondary_type': 'shader',
    
        # aiSkin material attributes
        'attributes': {
            'sssWeight': 'overall_scale',
            'globalSssRadiusMultiplier': 'radius_scale',

            'shallowScatterColor': 'shallow_color',
            'shallowScatterWeight': 'shallow_weight',
            'shallowScatterRadius': 'shallow_radius',

            'midScatterColor': 'mid_color',
            'midScatterWeight': 'mid_weight',
            'midScatterRadius': 'mid_radius',

            'deepScatterColor': 'deep_color',
            'deepScatterWeight': 'deep_weight',
            'deepScatterRadius': 'deep_radius',

            'specularColor': 'refl_color0',
            'specularWeight': 'refl_weight0',
            'specularRoughness': 'refl_gloss0',
            'specularIor': 'refl_ior0',

            'sheenColor': 'refl_color1',
            'sheenWeight': 'refl_weight1',
            'sheenRoughness': 'refl_gloss1',
            'sheenIor': 'refl_ior1',

            # 'opacity': None,
            # 'opacityColor': None,
            # 'specularInSecondaryRays': None,
            # 'fresnelAffectSss': None,

            'normalCamera': 'bump_input',
        }
    },

    'file': {
        # A dirty one liner that converts textures to rstexbin files
        'call_before': lambda x: RedShiftTextureProcessor(
            os.path.expandvars(x.computedFileTextureNamePattern.get())
        ).convert()
    },
    
    'aiImage': {
        # A dirty one liner that converts textures to rstexbin files
        'call_before': lambda x: RedShiftTextureProcessor(
            os.path.expandvars(x.filename.get())
        ).convert()
    },

    # LIGHTS
    'areaLight': {
        'attributes': {
            'aiExposure': {
                'intensity': lambda x: 2 ** x
            },
            'aiSamples': {
                'shadowRays': 1  # TODO: Test it later
            },
            'aiDecayType': {
                'decayRate': lambda x: 0 if x == 0 else 2
            },
            'aiColorTemperature': {
                'color': lambda x, y: pm.arnoldTemperatureToColor(x) if x.getAttr('aiUseColorTemperature') else (0, 0, 0)
            },
            'color': 'color',
        }
    },

    # 'aiSkyDomeLight': {
    #     'node_type': 'RedshiftDomeLight',
    #     'secondary_type': 'light'
    # },

    'pointLight': {
        'attributes': {
            'aiExposure': {
                'intensity': lambda x: 2 ** x
            },
            'aiSamples': {
                'shadowRays': 1  # TODO: Test it later
            },
            'aiDecayType': {
                'decayRate': lambda x: 0 if x == 0 else 2
            },
            'aiColorTemperature': {
                'color': lambda x, y: pm.arnoldTemperatureToColor(x) if y.getAttr('aiUseColorTemperature') else y.getAttr('color')
            },
            'aiRadius': 'lightRadius',
            'color': 'color',
        }
    },

    'directionalLight': {
        'attributes': {
            'aiExposure': {
                'intensity': lambda x: 2 ** x
            },
            'aiSamples': {
                'shadowRays': 1  # TODO: Test it later
            },
            'aiColorTemperature': {
                'color': lambda x, y: pm.arnoldTemperatureToColor(
                    x) if y.getAttr('aiUseColorTemperature') else y.getAttr(
                    'color')
            },
            'aiAngle': 'lightAngle',
            'color': 'color',
        }
    },

    'mesh': {
        'attributes': {
            'aiSubdivType': {
                'rsEnableSubdivision': lambda x: 1 if x > 0 else 0,
                'rsSubdivisionRule': 0,
                'rsDoSmoothSubdivision': lambda x: 0 if x == 2 else 1
            },
            'aiSubdivAdaptiveSpace': {
                'rsScreenSpaceAdaptive': lambda x: 1 - x,
            },
            'aiSubdivIterations': 'rsMaxTessellationSubdivs',
            'aiDispHeight': 'rsDisplacementScale',
            'aiDispAutobump': 'rsAutoBumpMap',
        }
    }
}


class ConversionManager(object):
    """Manages the conversion from Arnold to RedShift
    """

    def convert(self, node):
        """converts the given node to redShift counterpart
        """
        # get the conversion lut
        node_type = pm.nodeType(node)
        conversion_specs = CONVERSION_SPEC_SHEET.get(node_type)
        if not conversion_specs:
            return

        # call any call_before
        call_before = conversion_specs.get('call_before')
        if call_before:
            call_before(node)

        node_creator = NodeCreator(conversion_specs)
        rs_node = node_creator.create()

        # rename the material to have a similar name with the original
        if rs_node:
            rs_node.rename(
                node.name().replace(
                    node_type, conversion_specs['node_type']
                )
            )
        else:
            rs_node = node

        # set attributes
        attributes = conversion_specs.get('attributes')
        if attributes:
            for source_attr, target_attr in attributes.items():
                # value can be a string
                if isinstance(target_attr, basestring):
                    # just read and set the value directly
                    rs_node.setAttr(target_attr, node.getAttr(source_attr))
    
                    # also connect any textures to the target node
                    for input_ in node.attr(source_attr).inputs(p=1):
                        input_ >> rs_node.attr(target_attr)
                elif isinstance(target_attr, list):
                    # or a list
                    # where we set multiple attributes in the rs_node to the
                    # same value
                    source_attr_value = node.getAttr(source_attr)
                    for attr in target_attr:
                        rs_node.setAttr(attr, source_attr_value)
                        for input_ in node.attr(source_attr).inputs(p=1):
                            input_ >> rs_node.attr(attr)
                elif isinstance(target_attr, dict):
                    # or another dictionary
                    # where we have a converter
                    source_attr_value = node.getAttr(source_attr)
                    for attr, converter in target_attr.items():
                        if callable(converter):
                            try:
                                attr_value = converter(source_attr_value)
                            except TypeError:
                                # it should use two parameters, also include
                                # the node itself
                                attr_value = converter(source_attr_value, node)
                        else:
                            attr_value = converter
                        rs_node.setAttr(attr, attr_value)

        # call any call_after
        call_after = conversion_specs.get('call_after')
        if call_after:
            call_after(node, rs_node)

        return rs_node


class NodeCreator(object):
    """Creates nodes according to the given specs
    """

    def __init__(self, specs):
        self.specs = specs

    def create(self):
        """creates the node
        """
        node_type = self.specs.get('node_type')
        secondary_type = self.specs.get('secondary_type')

        if secondary_type == 'shader':
            shader, shading_engine = pm.createSurfaceShader(node_type)
            return shader
        elif secondary_type == 'light':
            light_transform = pm.shadingNode(node_type, asLight=1)
            return light_transform.getShape()


class RedShiftTextureProcessor(object):
    """A wrapper for the ``redshiftTextureProcessor.exe``

    TextureProcessor <inputfile> [options]
    
    Options are:
            -l              Force linear gamma (recommended for floating point textures)
            -s              Force SRGB gamma (recommended for integer textures)
            (Note the default gamma operation is as follows: -l for floating point textures and -s for integer textures)
            -p              Photometric IES data (for IES profile types)
            -wx             Used as a tiled texture with wrapping/repeats
            -wy             Used as a tiled texture with wrapping/repeats
            -isphere        Image Based Light - Sphere projection
            -ihemisphere    Image Based Light - Hemisphere projection
            -imirrorball    Image Based Light - Mirrorball projection
            -iangularmap    Image Based Light - Angular Map projection
            -ocolor         Sprite Cut-Out Map opacity from color intensity
            -oalpha         Sprite Cut-Out Map opacity from alpha
            -noskip         Disable the skipping of already converted textures if the processor thinks no data has changed
            -r              Recursively process textures in sub directories
            -log            Enable logging to log file
    """
    executable = os.path.join(
        os.environ['REDSHIFT_COREDATAPATH'],
        'bin/redshiftTextureProcessor'
    )

    def __init__(self, input_file_full_path, l=None, s=None, p=None, wx=None,
                 wy=None, isphere=None, ihemisphere=None, imirrorball=None,
                 iangularmap=None, ocolor=None, oalpha=None, noskip=False,
                 r=None, log=None):

        self.input_file_full_path = input_file_full_path
        self.files_to_process = []
        self.expand_tiles()
        self.noskip = noskip

    def expand_tiles(self):
        """expands any tiles and returns a list of file paths
        """
        if '<' in self.input_file_full_path:
            # replace any <U> and <V> with an *
            self.input_file_full_path = \
                self.input_file_full_path.replace('<U>', '*')
            self.input_file_full_path = \
                self.input_file_full_path.replace('<V>', '*')
            self.input_file_full_path = \
                self.input_file_full_path.replace('<UDIM>', '*')

        import glob
        self.files_to_process = glob.glob(self.input_file_full_path)

    def convert(self):
        """converts the given input_file to an rstexbin
        """
        processed_files = []
        for file_path in self.files_to_process:
            command = '%s %s' % (self.executable, file_path)
            rsmap_full_path = \
                '%s.rstexbin' % os.path.splitext(file_path)[0]

            os.system(command)
            processed_files.append(rsmap_full_path)

        return processed_files
