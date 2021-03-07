# -*- coding: utf-8 -*-

import os
import unittest

# prepare for test
os.environ['ANIMA_TEST_SETUP'] = ""

from pymel import core as pm
from anima.env.mayaEnv import ai2rs


class Ai2RSTester(unittest.TestCase):
    """tests for anima.env.mayaEnv.ai2rs classes
    """

    def setUp(self):
        """create the test setup
        """
        # be sure that arnold and redshift is loaded
        if not pm.pluginInfo('mtoa', q=1, loaded=1):
            pm.loadPlugin('mtoa')

        if not pm.pluginInfo('redshift4maya', q=1, loaded=1):
            pm.loadPlugin('redshift4maya')

    def tearDown(self):
        """clean the test
        """
        # create a new file
        pm.newFile(f=True)

        # delete any .rsmap in the test_data folder
        import os
        import glob
        test_data_path = os.path.abspath('./test_data/')
        for f in glob.glob('%s/*.rstexbin' % test_data_path):
            try:
                os.remove(f)
            except OSError:
                pass

    def test_conversion_of_ai_standard_to_red_shift_material_created(self):
        """test conversion of aiStandard material
        """
        # create one aiStandard material
        ai_standard, ai_standardSG = pm.createSurfaceShader('aiStandard')

        conversion_man = ai2rs.ConversionManager()
        rs_material = conversion_man.convert(ai_standard)

        # check if the material is created
        self.assertIsInstance(
            rs_material, pm.nt.RedshiftMaterial
        )

    def test_conversion_of_ai_standard_to_red_shift_material_diffuse_properties(self):
        """test conversion of aiStandard material to RedshiftMaterial diffuse
        properties
        """
        # create one aiStandard material
        ai_standard, ai_standardSG = pm.createSurfaceShader('aiStandard')
        diffuse_color = (1, 0.5, 0)
        diffuse_weight = 0.532
        diffuse_roughness = 0.8
        transl_weight = 0.25
        diffuse_direct = 0.95
        diffuse_indirect = 0.89

        ai_standard.color.set(diffuse_color)
        ai_standard.Kd.set(diffuse_weight)
        ai_standard.diffuseRoughness.set(diffuse_roughness)
        ai_standard.Kb.set(transl_weight)
        ai_standard.directDiffuse.set(diffuse_direct)
        ai_standard.indirectDiffuse.set(diffuse_indirect)

        conversion_man = ai2rs.ConversionManager()
        rs_material = conversion_man.convert(ai_standard)

        # check diffuse properties
        self.assertAlmostEqual(
            rs_material.diffuse_color.get(), diffuse_color, places=3
        )
        self.assertAlmostEqual(
            rs_material.diffuse_weight.get(), diffuse_weight, places=3
        )
        self.assertAlmostEqual(
            rs_material.diffuse_roughness.get(), diffuse_roughness, places=3
        )
        self.assertAlmostEqual(
            rs_material.transl_weight.get(), transl_weight, places=3
        )
        self.assertAlmostEqual(
            rs_material.diffuse_direct.get(), diffuse_direct, places=3
        )
        self.assertAlmostEqual(
            rs_material.diffuse_indirect.get(), diffuse_indirect, places=3
        )

    def test_conversion_of_ai_standard_to_red_shift_material_specular_properties(self):
        """test conversion of aiStandard material to RedshiftMaterial specular
        properties
        """
        # create one aiStandard material
        ai_standard, ai_standardSG = pm.createSurfaceShader('aiStandard')

        refl_color = (1, 0.5, 0)
        refl_weight = 0.532
        refl_roughness = 0.8
        refl_aniso = 0.25
        refl_aniso_rotation = 0.5
        refl_brdf = 1
        refl_fresnel_mode = 1
        refl_reflectivity = 0.01
        refl_direct = 0.95
        refl_indirect = 0.89

        ai_standard.KsColor.set(refl_color)
        ai_standard.Ks.set(refl_weight)
        ai_standard.specularRoughness.set(refl_roughness)
        ai_standard.specularAnisotropy.set(refl_aniso)

        ai_standard.specularRotation.set(refl_aniso_rotation)
        ai_standard.specularDistribution.set(refl_brdf)
        ai_standard.specularFresnel.set(refl_fresnel_mode)
        ai_standard.Ksn.set(refl_reflectivity)

        ai_standard.directSpecular.set(refl_direct)
        ai_standard.indirectSpecular.set(refl_indirect)

        conversion_man = ai2rs.ConversionManager()
        rs_material = conversion_man.convert(ai_standard)

        # check specular properties
        self.assertAlmostEqual(
            rs_material.refl_color.get(), refl_color, places=3
        )
        self.assertAlmostEqual(
            rs_material.refl_weight.get(), refl_weight, places=3
        )
        self.assertAlmostEqual(
            rs_material.refl_roughness.get(), refl_roughness, places=3
        )
        self.assertAlmostEqual(
            rs_material.refl_aniso.get(), -0.5, places=3
        )

        self.assertAlmostEqual(
            rs_material.refl_reflectivity.get()[0], refl_reflectivity, places=3
        )
        self.assertAlmostEqual(
            rs_material.refl_reflectivity.get()[1], refl_reflectivity, places=3
        )
        self.assertAlmostEqual(
            rs_material.refl_reflectivity.get()[2], refl_reflectivity, places=3
        )

        self.assertEqual(
            rs_material.refl_edge_tint.get(), (1, 1, 1)
        )
        self.assertAlmostEqual(
            rs_material.refl_direct.get(), refl_direct, places=3
        )
        self.assertAlmostEqual(
            rs_material.refl_indirect.get(), refl_indirect, places=3
        )

    def test_conversion_of_ai_standard_to_red_shift_material_refraction_properties(self):
        """test conversion of aiStandard material to RedshiftMaterial
        refraction properties
        """
        # create one aiStandard material
        ai_standard, ai_standardSG = pm.createSurfaceShader('aiStandard')

        refr_color = (1, 0.5, 0)
        refr_weight = 0.532

        refr_ior = 1.434

        refr_abbe = 29.942196
        refr_roughness = 0.8
        refr_transmittance = (0.57, 0.34, 0.54)
        opacity_color = (0.5, 0.87, 0.12)

        ai_standard.KtColor.set(refr_color)
        ai_standard.Kt.set(refr_weight)
        ai_standard.FresnelUseIOR.set(0)
        ai_standard.IOR.set(refr_ior)
        ai_standard.dispersionAbbe.set(refr_abbe)
        ai_standard.refractionRoughness.set(refr_roughness)
        ai_standard.transmittance.set(refr_transmittance)
        ai_standard.opacity.set(opacity_color)

        conversion_man = ai2rs.ConversionManager()
        rs_material = conversion_man.convert(ai_standard)

        self.assertAlmostEqual(
            rs_material.refr_color.get()[0], refr_color[0], places=3
        )
        self.assertAlmostEqual(
            rs_material.refr_color.get()[1], refr_color[1], places=3
        )
        self.assertAlmostEqual(
            rs_material.refr_color.get()[2], refr_color[2], places=3
        )

        self.assertAlmostEqual(
            rs_material.refr_weight.get(), refr_weight, places=3
        )

        self.assertAlmostEqual(rs_material.refr_ior.get(), refr_ior, places=3)
        self.assertEqual(rs_material.refr_use_base_IOR.get(), 0)
        self.assertAlmostEqual(
            rs_material.refr_abbe.get(), refr_abbe, places=3
        )
        self.assertAlmostEqual(
            rs_material.refr_roughness.get(), refr_roughness, places=3
        )

        self.assertAlmostEqual(
            rs_material.refr_transmittance.get()[0], refr_transmittance[0],
            places=3
        )
        self.assertAlmostEqual(
            rs_material.refr_transmittance.get()[1], refr_transmittance[1],
            places=3
        )
        self.assertAlmostEqual(
            rs_material.refr_transmittance.get()[2], refr_transmittance[2],
            places=3
        )

        self.assertAlmostEqual(
            rs_material.opacity_color.get()[0], opacity_color[0], places=3
        )
        self.assertAlmostEqual(
            rs_material.opacity_color.get()[1], opacity_color[1], places=3
        )
        self.assertAlmostEqual(
            rs_material.opacity_color.get()[2], opacity_color[2], places=3
        )

    def test_conversion_of_ai_standard_to_red_shift_material_sss_properties(self):
        """test conversion of aiStandard material to RedshiftMaterial sss
        properties
        """
        # create one aiStandard material
        ai_standard, ai_standardSG = pm.createSurfaceShader('aiStandard')

        ms_color0 = (1, 0.5, 0)
        ms_amount = 0.532
        ms_radius0 = 1.434
        emission_color = (0.57, 0.34, 0.54)
        emission_weight = 0.5

        ai_standard.KsssColor.set(ms_color0)
        ai_standard.Ksss.set(ms_amount)
        ai_standard.sssRadius.set([ms_radius0, ms_radius0, ms_radius0])
        ai_standard.emissionColor.set(emission_color)
        ai_standard.emission.set(emission_weight)

        conversion_man = ai2rs.ConversionManager()
        rs_material = conversion_man.convert(ai_standard)

        self.assertAlmostEqual(
            rs_material.ms_color0.get()[0], ms_color0[0], places=3
        )
        self.assertAlmostEqual(
            rs_material.ms_color0.get()[1], ms_color0[1], places=3
        )
        self.assertAlmostEqual(
            rs_material.ms_color0.get()[2], ms_color0[2], places=3
        )

        self.assertAlmostEqual(
            rs_material.ms_amount.get(), ms_amount, places=3
        )
        self.assertAlmostEqual(
            rs_material.ms_radius0.get(), ms_radius0, places=3
        )

        self.assertAlmostEqual(
            rs_material.emission_color.get()[0], emission_color[0], places=3
        )
        self.assertAlmostEqual(
            rs_material.emission_color.get()[1], emission_color[1], places=3
        )
        self.assertAlmostEqual(
            rs_material.emission_color.get()[2], emission_color[2], places=3
        )

        self.assertAlmostEqual(
            rs_material.emission_weight.get(), emission_weight, places=3
        )

    def test_conversion_of_ai_standard_to_red_shift_material_channels_with_textures(self):
        """test conversion of aiStandard material to RedshiftMaterial channels
        with textures
        """
        # create one aiStandard material
        ai_standard, ai_standardSG = pm.createSurfaceShader('aiStandard')

        # create a diffuse texture
        file_node = pm.shadingNode('file', asTexture=1)

        file_node.outColor >> ai_standard.color

        conversion_man = ai2rs.ConversionManager()
        rs_material = conversion_man.convert(ai_standard)

        # now expect the corresponding channel to also have the same connection
        # from the file_node

        self.assertIn(
            file_node,
            rs_material.diffuse_color.inputs()
        )

    def test_conversion_of_ai_standard_to_red_shift_material_bump_properties(self):
        """test conversion of aiStandard material to RedshiftMaterial channels
        with textures
        """
        # create one aiStandard material
        ai_standard, ai_standardSG = pm.createSurfaceShader('aiStandard')

        # create a diffuse texture
        file_node = pm.shadingNode('file', asTexture=1)
        bump2d_node = pm.shadingNode('bump2d', asUtility=1)

        file_node.outAlpha >> bump2d_node.bumpValue
        bump2d_node.outNormal >> ai_standard.normalCamera

        conversion_man = ai2rs.ConversionManager()
        rs_material = conversion_man.convert(ai_standard)

        # now expect the corresponding channel to also have the same connection
        # from the file_node

        self.assertIn(
            bump2d_node,
            rs_material.bump_input.inputs()
        )

    def test_node_type_is_not_on_the_spec_sheet(self):
        """testing if no error will be raised when the given node type is not
        on the conversion spec sheet
        """
        # create a surface node
        node = pm.createNode('surface')
        conversion_man = ai2rs.ConversionManager()
        rs_material = conversion_man.convert(node)
        self.assertIsNone(rs_material)

    def test_texture_files_converted_to_rsmap(self):
        """testing if texture files are converted to rsmap files
        """
        import os
        file_texture_node = pm.shadingNode('file', asTexture=1)
        texture_full_path = os.path.abspath('./test_data/texture.png')
        rstexbin_full_path = '%s.rstexbin' % \
                             os.path.splitext(texture_full_path)[0]
        file_texture_node.fileTextureName.set(texture_full_path)
        conversion_man = ai2rs.ConversionManager()
        conversion_man.convert(file_texture_node)

        self.assertTrue(os.path.exists(rstexbin_full_path))

    def test_mesh_subdiv_attributes(self):
        """testing if mesh attributes are transferred correctly
        """
        mesh_node = pm.createNode('mesh')

        # set arnold attributes
        mesh_node.aiSubdivType.set(1)
        mesh_node.aiSubdivIterations.set(2)
        mesh_node.aiSubdivAdaptiveSpace.set(1)
        mesh_node.aiDispAutobump.set(1)
        mesh_node.aiDispHeight.set(1.3)

        conversion_man = ai2rs.ConversionManager()
        conversion_man.convert(mesh_node)

        self.assertEqual(mesh_node.rsEnableSubdivision.get(), 1)
        self.assertEqual(mesh_node.rsMaxTessellationSubdivs.get(), 2)
        self.assertEqual(mesh_node.rsSubdivisionRule.get(), 0)
        self.assertEqual(mesh_node.rsScreenSpaceAdaptive.get(), 0)
        self.assertEqual(mesh_node.rsDoSmoothSubdivision.get(), 1)
        self.assertAlmostEqual(
            mesh_node.rsDisplacementScale.get(), 1.3, places=3
        )
        self.assertEqual(mesh_node.rsAutoBumpMap.get(), 1)


class RedShiftTextureProcessorTester(unittest.TestCase):
    """tests for anima.env.mayaEnv.ai2rs.RedShiftTextureProcessor class
    """

    def setUp(self):
        """create the test setup
        """
        if not pm.pluginInfo('redshift4maya', q=1, loaded=1):
            pm.loadPlugin('redshift4maya')

    def tearDown(self):
        """clean the test
        """
        # create a new file
        pm.newFile(f=True)

        # delete any .rsmap in the test_data folder
        import os
        import glob
        test_data_path = os.path.abspath('./test_data/')
        for f in glob.glob('%s/*.rstexbin' % test_data_path):
            try:
                os.remove(f)
            except OSError:
                pass

    def test_convert_is_working_properly(self):
        """testing if convert is working properly
        """
        import os
        from anima.env.mayaEnv.redshift import RedShiftTextureProcessor
        texture_full_path = os.path.abspath('./test_data/texture.png')
        rstp = RedShiftTextureProcessor(texture_full_path)
        result = rstp.convert()

        rsmap_full_path = os.path.abspath('./test_data/texture.rstexbin')
        self.assertEqual(
            result[0].replace('\\', '/'),
            rsmap_full_path.replace('\\', '/')
        )

        self.assertTrue(
            os.path.exists(rsmap_full_path)
        )
