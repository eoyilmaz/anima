# -*- coding: utf-8 -*-
"""Tests for anima.dcc.mayaEnv.ai2rs classes."""
import glob
import os

import pytest

# prepare for test
from anima.dcc.mayaEnv import ai2rs


HERE = os.path.dirname(__file__)


def remove_rstextbin():
    """Delete any .rsmap in the test_data folder."""
    test_data_path = os.path.abspath("./test_data/")
    for f in glob.glob("{}/*.rstexbin".format(test_data_path)):
        try:
            os.remove(f)
        except OSError:
            pass


def load_plugin(pm, plugin_name):
    """Load the plugin with the given name."""
    if not pm.pluginInfo(plugin_name, q=1, loaded=1):
        pm.loadPlugin(plugin_name)


@pytest.fixture(scope="function")
def setup_scene(create_pymel):
    """Create the test setup."""
    pm = create_pymel
    # be sure that arnold and redshift is loaded
    load_plugin(pm, "mtoa")
    load_plugin(pm, "redshift4maya")
    yield
    # clean the test
    # create a new file
    pm.newFile(f=True)
    remove_rstextbin()


@pytest.fixture(scope="function")
def setup_scene_2(create_pymel):
    """Create the test setup."""
    # be sure that arnold and redshift is loaded
    pm = create_pymel
    load_plugin(pm, "redshift4maya")
    yield
    # clean the test
    # create a new file
    pm.newFile(f=True)


def test_conversion_of_ai_standard_to_red_shift_material_created(
    create_pymel, setup_scene
):
    """test conversion of aiStandard material."""
    pm = create_pymel
    # create one aiStandard material
    ai_standard, ai_standard_sg = pm.createSurfaceShader("aiStandard")

    conversion_man = ai2rs.ConversionManager()
    rs_material = conversion_man.convert(ai_standard)

    # check if the material is created
    assert isinstance(rs_material, pm.nt.RedshiftMaterial)


def test_conversion_of_ai_standard_to_red_shift_material_diffuse_properties(
    create_pymel, setup_scene
):
    """test conversion of aiStandard material to RedshiftMaterial diffuse
    properties
    """
    pm = create_pymel
    # create one aiStandard material
    ai_standard, ai_standard_sg = pm.createSurfaceShader("aiStandard")
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
    assert rs_material.diffuse_color.get() == pytest.approx(diffuse_color, abs=1e-3)
    assert rs_material.diffuse_weight.get() == pytest.approx(diffuse_weight, abs=1e-3)
    assert rs_material.diffuse_roughness.get() == pytest.approx(
        diffuse_roughness, abs=1e-3
    )
    assert rs_material.transl_weight.get() == pytest.approx(transl_weight, abs=1e-3)
    assert rs_material.diffuse_direct.get() == pytest.approx(diffuse_direct, abs=1e-3)
    assert rs_material.diffuse_indirect.get() == pytest.approx(
        diffuse_indirect, abs=1e-3
    )


def test_conversion_of_ai_standard_to_red_shift_material_specular_properties(
    create_pymel, setup_scene
):
    """test conversion of aiStandard material to RedshiftMaterial specular
    properties
    """
    pm = create_pymel
    # create one aiStandard material
    ai_standard, ai_standard_sg = pm.createSurfaceShader("aiStandard")

    refl_color = (1, 0.5, 0)
    refl_weight = 0.532
    refl_roughness = 0.8
    refl_anisotropy = 0.25
    refl_anisotropy_rotation = 0.5
    refl_brdf = 1
    refl_fresnel_mode = 1
    refl_reflectivity = 0.01
    refl_direct = 0.95
    refl_indirect = 0.89

    ai_standard.KsColor.set(refl_color)
    ai_standard.Ks.set(refl_weight)
    ai_standard.specularRoughness.set(refl_roughness)
    ai_standard.specularAnisotropy.set(refl_anisotropy)

    ai_standard.specularRotation.set(refl_anisotropy_rotation)
    ai_standard.specularDistribution.set(refl_brdf)
    ai_standard.specularFresnel.set(refl_fresnel_mode)
    ai_standard.Ksn.set(refl_reflectivity)

    ai_standard.directSpecular.set(refl_direct)
    ai_standard.indirectSpecular.set(refl_indirect)

    conversion_man = ai2rs.ConversionManager()
    rs_material = conversion_man.convert(ai_standard)

    # check specular properties
    assert rs_material.refl_color.get() == pytest.approx(refl_color, abs=1e-3)
    assert rs_material.refl_weight.get() == pytest.approx(refl_weight, abs=1e-3)
    assert rs_material.refl_roughness.get() == pytest.approx(refl_roughness, abs=1e-3)
    assert rs_material.refl_aniso.get() == pytest.approx(-0.5, abs=1e-3)

    assert rs_material.refl_reflectivity.get()[0] == pytest.approx(
        refl_reflectivity, abs=1e-3
    )
    assert rs_material.refl_reflectivity.get()[1] == pytest.approx(
        refl_reflectivity, abs=1e-3
    )
    assert rs_material.refl_reflectivity.get()[2] == pytest.approx(
        refl_reflectivity, abs=1e-3
    )

    assert rs_material.refl_edge_tint.get() == (1, 1, 1)
    assert rs_material.refl_direct.get() == pytest.approx(refl_direct, abs=1e-3)
    assert rs_material.refl_indirect.get() == pytest.approx(refl_indirect, abs=1e-3)


def test_conversion_of_ai_standard_to_red_shift_material_refraction_properties(
    create_pymel, setup_scene
):
    """test conversion of aiStandard material to RedshiftMaterial
    refraction properties
    """
    pm = create_pymel
    # create one aiStandard material
    ai_standard, ai_standard_sg = pm.createSurfaceShader("aiStandard")

    refraction_color = (1, 0.5, 0)
    refraction_weight = 0.532

    refraction_ior = 1.434

    refraction_abbe = 29.942196
    refraction_roughness = 0.8
    refraction_transmittance = (0.57, 0.34, 0.54)
    opacity_color = (0.5, 0.87, 0.12)

    ai_standard.KtColor.set(refraction_color)
    ai_standard.Kt.set(refraction_weight)
    ai_standard.FresnelUseIOR.set(0)
    ai_standard.IOR.set(refraction_ior)
    ai_standard.dispersionAbbe.set(refraction_abbe)
    ai_standard.refractionRoughness.set(refraction_roughness)
    ai_standard.transmittance.set(refraction_transmittance)
    ai_standard.opacity.set(opacity_color)

    conversion_man = ai2rs.ConversionManager()
    rs_material = conversion_man.convert(ai_standard)

    assert rs_material.refr_color.get()[0] == pytest.approx(
        refraction_color[0], abs=1e-3
    )
    assert rs_material.refr_color.get()[1] == pytest.approx(
        refraction_color[1], abs=1e-3
    )
    assert rs_material.refr_color.get()[2] == pytest.approx(
        refraction_color[2], abs=1e-3
    )

    assert rs_material.refr_weight.get() == pytest.approx(refraction_weight, abs=1e-3)

    assert rs_material.refr_ior.get() == pytest.approx(refraction_ior, abs=1e-3)
    assert rs_material.refr_use_base_IOR.get() == 0
    assert rs_material.refr_abbe.get() == pytest.approx(refraction_abbe, abs=1e-3)
    assert rs_material.refr_roughness.get() == pytest.approx(
        refraction_roughness, abs=1e-3
    )

    assert rs_material.refr_transmittance.get()[0] == pytest.approx(
        refraction_transmittance[0], abs=1e-3
    )
    assert rs_material.refr_transmittance.get()[1] == pytest.approx(
        refraction_transmittance[1], abs=1e-3
    )
    assert rs_material.refr_transmittance.get()[2] == pytest.approx(
        refraction_transmittance[2], abs=1e-3
    )

    assert rs_material.opacity_color.get()[0] == pytest.approx(
        opacity_color[0], abs=1e-3
    )
    assert rs_material.opacity_color.get()[1] == pytest.approx(
        opacity_color[1], abs=1e-3
    )
    assert rs_material.opacity_color.get()[2] == pytest.approx(
        opacity_color[2], abs=1e-3
    )


def test_conversion_of_ai_standard_to_red_shift_material_sss_properties(
    create_pymel, setup_scene
):
    """test conversion of aiStandard material to RedshiftMaterial sss
    properties
    """
    pm = create_pymel
    # create one aiStandard material
    ai_standard, ai_standard_sg = pm.createSurfaceShader("aiStandard")

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

    assert rs_material.ms_color0.get()[0] == pytest.approx(ms_color0[0], abs=1e-3)
    assert rs_material.ms_color0.get()[1] == pytest.approx(ms_color0[1], abs=1e-3)
    assert rs_material.ms_color0.get()[2] == pytest.approx(ms_color0[2], abs=1e-3)

    assert rs_material.ms_amount.get() == pytest.approx(ms_amount, abs=1e-3)
    assert rs_material.ms_radius0.get() == pytest.approx(ms_radius0, abs=1e-3)

    assert rs_material.emission_color.get()[0] == pytest.approx(
        emission_color[0], abs=1e-3
    )
    assert rs_material.emission_color.get()[1] == pytest.approx(
        emission_color[1], abs=1e-3
    )
    assert rs_material.emission_color.get()[2] == pytest.approx(
        emission_color[2], abs=1e-3
    )

    assert rs_material.emission_weight.get() == pytest.approx(emission_weight, abs=1e-3)


def test_conversion_of_ai_standard_to_red_shift_material_channels_with_textures(
    create_pymel, setup_scene
):
    """test conversion of aiStandard material to RedshiftMaterial channels
    with textures
    """
    pm = create_pymel
    # create one aiStandard material
    ai_standard, ai_standard_sg = pm.createSurfaceShader("aiStandard")

    # create a diffuse texture
    file_node = pm.shadingNode("file", asTexture=1)

    file_node.outColor.connect(ai_standard.color)

    conversion_man = ai2rs.ConversionManager()
    rs_material = conversion_man.convert(ai_standard)

    # now expect the corresponding channel to also have the same connection
    # from the file_node

    assert file_node in rs_material.diffuse_color.inputs()


def test_conversion_of_ai_standard_to_red_shift_material_bump_properties(
    create_pymel, setup_scene
):
    """test conversion of aiStandard material to RedshiftMaterial channels
    with textures
    """
    pm = create_pymel
    # create one aiStandard material
    ai_standard, ai_standard_sg = pm.createSurfaceShader("aiStandard")

    # create a diffuse texture
    file_node = pm.shadingNode("file", asTexture=1)
    bump2d_node = pm.shadingNode("bump2d", asUtility=1)

    file_node.outAlpha.connect(bump2d_node.bumpValue)
    bump2d_node.outNormal.connect(ai_standard.normalCamera)

    conversion_man = ai2rs.ConversionManager()
    rs_material = conversion_man.convert(ai_standard)

    # now expect the corresponding channel to also have the same connection
    # from the file_node

    assert bump2d_node in rs_material.bump_input.inputs()


def test_node_type_is_not_on_the_spec_sheet(create_pymel, setup_scene):
    """testing if no error will be raised when the given node type is not
    on the conversion spec sheet
    """
    pm = create_pymel
    # create a surface node
    node = pm.createNode("surface")
    conversion_man = ai2rs.ConversionManager()
    rs_material = conversion_man.convert(node)
    assert rs_material is None


# def test_texture_files_converted_to_rsmap(create_pymel, setup_scene):
#     """testing if texture files are converted to rstexbin files"""
#     pm = create_pymel
#     file_texture_node = pm.shadingNode("file", asTexture=1)
#     texture_full_path = os.path.join(HERE, "test_data", "texture.png")
#     print("texture_full_path: {}".format(texture_full_path))
#     rstexbin_full_path = "{}.rstexbin".format(
#         os.path.splitext(texture_full_path)[0]
#     )
#     print("rstexbin_full_path: {}".format(rstexbin_full_path))
#     file_texture_node.fileTextureName.set(texture_full_path)
#     conversion_man = ai2rs.ConversionManager()
#     conversion_man.convert(file_texture_node)
#     assert os.path.exists(rstexbin_full_path)


def test_mesh_subdiv_attributes(create_pymel, setup_scene):
    """testing if mesh attributes are transferred correctly"""
    pm = create_pymel
    mesh_node = pm.createNode("mesh")

    # set arnold attributes
    mesh_node.aiSubdivType.set(1)
    mesh_node.aiSubdivIterations.set(2)
    mesh_node.aiSubdivAdaptiveSpace.set(1)
    mesh_node.aiDispAutobump.set(1)
    mesh_node.aiDispHeight.set(1.3)

    conversion_man = ai2rs.ConversionManager()
    conversion_man.convert(mesh_node)

    print("mesh_node.aiSubdivType: {}".format(mesh_node.aiSubdivType.get()))

    print(
        "mesh_node.rsEnableSubdivision.get(): {}".format(
            mesh_node.rsEnableSubdivision.get()
        )
    )

    assert mesh_node.rsEnableSubdivision.get() == 1
    assert mesh_node.rsMaxTessellationSubdivs.get() == 2
    assert mesh_node.rsSubdivisionRule.get() == 0
    assert mesh_node.rsScreenSpaceAdaptive.get() == 0
    assert mesh_node.rsDoSmoothSubdivision.get() == 1
    assert mesh_node.rsDisplacementScale.get() == pytest.approx(1.3, abs=1e-3)
    assert mesh_node.rsAutoBumpMap.get() == 1


def test_convert_is_working_properly(setup_scene_2):
    """testing if convert is working properly"""
    from anima.render.redshift import RedShiftTextureProcessor

    texture_full_path = os.path.join(HERE, "test_data", "texture.png")
    rstp = RedShiftTextureProcessor(texture_full_path)
    result = rstp.convert()

    rsmap_full_path = os.path.join(HERE, "test_data", "texture.rstexbin")
    assert result[0].replace("\\", "/") == rsmap_full_path.replace("\\", "/")
    assert os.path.exists(rsmap_full_path)
