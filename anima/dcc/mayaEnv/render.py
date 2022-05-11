# -*- coding: utf-8 -*-

import os
import re
import tempfile

from anima.dcc.mayaEnv import auxiliary
from anima.utils.progress import ProgressManager
from maya import cmds as cmds, mel as mel
from pymel import core as pm


class Render(object):
    """Tools for render"""

    rso_options = {
        "bake": {
            # motion blur settings
            "motionBlurEnable": 1,
            "motionBlurDeformationEnable": 1,
            "motionBlurNumTransformationSteps": 31,
            "motionBlurFrameDuration": 100,
            "motionBlurShutterStart": 0,
            "motionBlurShutterEnd": 1,
            "motionBlurShutterPosition": 1,
            # set GI Engines
            "primaryGIEngine": 3,
            "secondaryGIEngine": 2,
            # set file paths
            "irradiancePointCloudMode": 2,  # Rebuild (prepass only)
            "irradianceCacheMode": 2,  # Rebuild (prepass only)
            "irradiancePointCloudFilename": "Outputs/rs/ipc_baked.rsmap",
            "irradianceCacheFilename": "Outputs/rs/im_baked.rsmap",
        },
        "orig": {},
        "current_frame": 1,
    }

    node_attr_info_temp_file_path = os.path.join(tempfile.gettempdir(), "attr_info")

    shader_data_temp_file_path = os.path.join(tempfile.gettempdir(), "shader_data")

    @classmethod
    def assign_random_material_color(cls):
        """assigns a lambert with a random color to the selected object"""
        selected = pm.selected()

        # create the lambert material
        lambert = pm.shadingNode("lambert", asShader=1)

        # create the shading engine
        shading_engine = pm.nt.ShadingEngine()
        lambert.outColor >> shading_engine.surfaceShader

        # randomize the lambert color
        import random

        h = random.random()  # 0-1
        s = random.random() * 0.5 + 0.25  # 0.25-0.75
        v = random.random() * 0.5 + 0.5  # 0.5 - 1

        from anima.utils import hsv_to_rgb

        r, g, b = hsv_to_rgb(h, s, v)
        lambert.color.set(r, g, b)

        pm.sets(shading_engine, fe=selected)
        pm.select(selected)

    @classmethod
    def randomize_material_color(cls):
        """randomizes material color of selected nodes"""
        selected = pm.selected()
        all_materials = []
        for node in selected:
            shading_engines = node.listHistory(f=1, type="shadingEngine")
            if not shading_engines:
                continue
            shading_engine = shading_engines[0]
            materials = shading_engine.surfaceShader.inputs()
            if not materials:
                continue
            else:
                for material in materials:
                    if material not in all_materials:
                        all_materials.append(material)

        import random
        from anima.utils import hsv_to_rgb

        attr_lut = {
            "lambert": "color",
        }
        for material in all_materials:
            h = random.random()  # 0-1
            s = random.random() * 0.5 + 0.25  # 0.25-0.75
            v = random.random() * 0.5 + 0.5  # 0.5 - 1
            r, g, b = hsv_to_rgb(h, s, v)
            attr_name = attr_lut[material.type()]
            material.attr(attr_name).set(r, g, b)

    @classmethod
    def vertigo_setup_look_at(cls):
        """sets up a the necessary locator for teh Vertigo effect for the
        selected camera
        """
        from anima.dcc.mayaEnv import vertigo

        cam = pm.ls(sl=1)[0]
        vertigo.setup_look_at(cam)

    @classmethod
    def vertigo_setup_vertigo(cls):
        """sets up a Vertigo effect for the selected camera"""
        from anima.dcc.mayaEnv import vertigo

        cam = pm.ls(sl=1)[0]
        vertigo.setup_vertigo(cam)

    @classmethod
    def vertigo_delete(cls):
        """deletes the Vertigo setup for the selected camera"""
        from anima.dcc.mayaEnv import vertigo

        cam = pm.ls(sl=1)[0]
        vertigo.delete(cam)

    @classmethod
    def duplicate_with_connections(cls):
        """duplicates the selected nodes with connections to the network"""
        return pm.duplicate(ic=1, rr=1)

    @classmethod
    def duplicate_input_graph(cls):
        """duplicates the selected nodes with all their inputs"""
        return pm.duplicate(un=1, rr=1)

    @classmethod
    def delete_render_and_display_layers(cls):
        """Deletes the display and render layers in the current scene"""
        cls.delete_display_layers()
        cls.delete_render_layers()

    @classmethod
    def delete_display_layers(cls):
        """Deletes the display layers in the current scene"""
        # switch to default render layer before deleting anything
        # this will prevent layers to be non-deletable
        from anima.dcc.mayaEnv import auxiliary

        auxiliary.switch_to_default_render_layer()
        pm.delete(pm.ls(type=["displayLayer"]))

    @classmethod
    def delete_render_layers(cls):
        """Deletes the render layers in the current scene"""
        # switch to default render layer before deleting anything
        # this will prevent layers to be non-deletable
        from anima.dcc.mayaEnv import auxiliary

        auxiliary.switch_to_default_render_layer()
        pm.delete(pm.ls(type=["renderLayer"]))

    @classmethod
    def delete_unused_shading_nodes(cls):
        """Deletes unused shading nodes"""
        pm.mel.eval("MLdeleteUnused")

    @classmethod
    def normalize_texture_paths(cls):
        """Expands the environment variables in texture paths"""
        import os

        for node in pm.ls(type="file"):
            if node.hasAttr("colorSpace"):
                color_space = node.colorSpace.get()
            node.fileTextureName.set(os.path.expandvars(node.fileTextureName.get()))
            if node.hasAttr("colorSpace"):
                node.colorSpace.set(color_space)

    @classmethod
    def unnormalize_texture_paths(cls):
        """Contracts the environment variables in texture paths bu adding
        the repository environment variable to the file paths
        """
        from anima.dcc import mayaEnv

        m = mayaEnv.Maya()
        m.replace_external_paths()

    @classmethod
    def assign_substance_textures(cls):
        """auto assigns textures to selected materials.

        Supports both Arnold and Redshift materials
        """
        #
        # Substance Texture Assigner
        #

        # material_subfixes = {
        #     "BaseColor": {
        #         "aiStandardSurface": {
        #             "attr": "baseColor"
        #         },
        #         "RedshiftMaterial": {
        #             "attr": "diffuse_color"
        #         },
        #     },
        #     "Height": {},
        #     "Metalness": {
        #         "aiStandarSurface": {
        #             "attr": "metalness"
        #         }
        #     },
        #     "Normal": {
        #         "aiStandardSurface": {
        #             "tree": {
        #                 "type": "aiBump2D",
        #                 "class": "asUtility",
        #                 "attr": {
        #                     "bumpMap": {
        #                         "output": "outColorR"
        #                         "type": "aiImage",
        #                         "attr": {
        #                             "filename": "%TEXTUREFILE%"
        #                         }
        #                     }
        #                 }
        #                 "target": "normalCamera"
        #             }
        #         }
        #     },
        #     "Roughness": {
        #         "aiStandardSurface": {
        #             "attr": "specularRoughness"
        #         }
        #     }
        # }

        def connect_place2d_to_file(place2d_node, file_node):
            """connects place2dtexture node to file image node"""
            place2d_outputs = ["outUV", "outUvFilterSize"]
            texture_inputs = ["uvCoord", "uvFilterSize"]
            place2d_attrs = [
                "coverage",
                "translateFrame",
                "rotateFrame",
                "mirrorU",
                "mirrorV",
                "stagger",
                "wrapU",
                "wrapV",
                "repeatUV",
                "offset",
                "rotateUV",
                "noiseUV",
                "vertexUvOne",
                "vertexUvTwo",
                "vertexUvThree",
                "vertexCameraOne",
            ]

            for i in range(0, len(place2d_outputs)):
                place2d_node.attr(place2d_outputs[i]).connect(
                    file_node.attr(texture_inputs[i])
                )

            for attr in place2d_attrs:
                place2d_node.attr(attr).connect(file_node.attr(attr))

        import glob

        materials = []

        # support both object and material selections
        nodes = pm.selected()
        accepted_materials = [
            "aiStandardSurface", "RedshiftMaterial", "RedshiftStandardMaterial"
        ]
        for node in nodes:
            if node.type() in accepted_materials:
                materials.append(node)
            elif node.type() == "transform":
                try:
                    se = node.getShape().listConnections(type="shadingEngine")[0]
                    material = se.attr("surfaceShader").inputs()[0]
                    if material not in materials:
                        materials.append(material)
                except (AttributeError, IndexError):
                    pass

        # ask the texture folder
        texture_path = pm.fileDialog2(cap="Choose Texture Folder", okc="Choose", fm=2)[
            0
        ]

        for material in materials:
            # textures should start with the same name of the material
            material_name = material.name().split(":")[-1]  # strip namespaces
            print("material.name: %s" % material_name)

            pattern = "%s/%s_*" % (texture_path, material_name)
            print("pattern: %s" % pattern)

            files = glob.glob(pattern)
            print(files)

            # TODO: Make it beautiful by using the auxiliary.create_shader()
            # For now do it ugly!

            if material.type() == "aiStandardSurface":
                # create place2dTexture node
                place2d = pm.shadingNode("place2dTexture", asUtility=1)
                # *********************************************
                # BaseColor
                # create a new aiImage
                base_color_file_path = glob.glob(
                    "%s/%s_BaseColor*" % (texture_path, material_name)
                )
                if base_color_file_path:
                    # fix diffuse weight
                    material.base.set(1)
                    base_color_file_path = base_color_file_path[0]

                    base_color_file = pm.shadingNode("file", asTexture=1)
                    connect_place2d_to_file(place2d, base_color_file)
                    base_color_file.setAttr("ignoreColorSpaceFileRules", 1)
                    base_color_file.fileTextureName.set(base_color_file_path)
                    base_color_file.colorSpace.set("sRGB")
                    base_color_file.outColor >> material.baseColor

                # *********************************************
                # Height
                # height_file_path = glob.glob("%s/%s_Height*" % (texture_path, material_name))
                height_channel_names = [
                    "Height",
                    "DisplaceHeightField",
                    "DisplacementHeight",
                ]
                for height_channel_name in height_channel_names:
                    height_file_path = glob.glob(
                        "%s/%s_%s*" % (texture_path, material_name, height_channel_name)
                    )
                    if height_file_path:
                        height_file_path = height_file_path[0]

                        # create a displacement node
                        shading_node = material.attr("outColor").outputs(
                            type="shadingEngine"
                        )[0]
                        disp_shader = pm.shadingNode("displacementShader", asShader=1)
                        disp_shader.displacement >> shading_node.displacementShader

                        # create texture
                        disp_file = pm.shadingNode("file", asTexture=1)
                        connect_place2d_to_file(place2d, disp_file)
                        disp_file.setAttr("ignoreColorSpaceFileRules", 1)
                        disp_file.fileTextureName.set(height_file_path)
                        disp_file.colorSpace.set("Raw")
                        disp_file.alphaIsLuminance.set(1)
                        disp_file.outAlpha >> disp_shader.displacement

                # *********************************************
                # Metalness
                metalness_file_path = glob.glob(
                    "%s/%s_Metalness*" % (texture_path, material_name)
                )
                if metalness_file_path:
                    metalness_file_path = metalness_file_path[0]

                    metalness_file = pm.shadingNode("file", asTexture=1)
                    connect_place2d_to_file(place2d, metalness_file)
                    metalness_file.setAttr("ignoreColorSpaceFileRules", 1)
                    metalness_file.fileTextureName.set(metalness_file_path)
                    metalness_file.colorSpace.set("Raw")
                    metalness_file.alphaIsLuminance.set(1)
                    metalness_file.outAlpha >> material.metalness

                # *********************************************
                # Normal
                normal_file_path = glob.glob(
                    "%s/%s_Normal*" % (texture_path, material_name)
                )
                if normal_file_path:
                    normal_file_path = normal_file_path[0]

                    normal_ai_normalmap = pm.shadingNode("aiNormalMap", asUtility=1)
                    normal_file = pm.shadingNode("file", asTexture=1)
                    connect_place2d_to_file(place2d, normal_file)
                    normal_file.setAttr("ignoreColorSpaceFileRules", 1)

                    normal_file.fileTextureName.set(normal_file_path)
                    normal_file.colorSpace.set("Raw")
                    normal_file.outColor >> normal_ai_normalmap.input

                    normal_ai_normalmap.outValue >> material.normalCamera

                # *********************************************
                # Roughness
                # specularRoughness
                roughness_file_path = glob.glob(
                    "%s/%s_Roughness*" % (texture_path, material_name)
                )
                if roughness_file_path:
                    roughness_file_path = roughness_file_path[0]
                    roughness_file = pm.shadingNode("file", asTexture=1)
                    connect_place2d_to_file(place2d, roughness_file)
                    roughness_file.setAttr("ignoreColorSpaceFileRules", 1)
                    roughness_file.fileTextureName.set(roughness_file_path)
                    roughness_file.colorSpace.set("Raw")
                    roughness_file.alphaIsLuminance.set(1)
                    roughness_file.outAlpha >> material.specularRoughness
            elif material.type() in ["RedshiftMaterial", "RedshiftStandardMaterial"]:
                # create place2dTexture node
                place2d = pm.shadingNode("place2dTexture", asUtility=1)

                # *********************************************
                # BaseColor
                # create a new aiImage
                diffuse_color_file_path = glob.glob(
                    "%s/%s_Diffuse*" % (texture_path, material_name)
                )
                if diffuse_color_file_path:
                    use_udim = False
                    if len(diffuse_color_file_path) > 1:
                        use_udim = True
                    diffuse_color_file_path = diffuse_color_file_path[0]
                    if use_udim:
                        diffuse_color_file_path = \
                            diffuse_color_file_path.replace("1001", "<udim>")

                    diffuse_color_file = pm.shadingNode("file", asTexture=1)
                    connect_place2d_to_file(place2d, diffuse_color_file)
                    diffuse_color_file.setAttr("ignoreColorSpaceFileRules", 1)
                    diffuse_color_file.fileTextureName.set(diffuse_color_file_path)
                    diffuse_color_file.colorSpace.set("sRGB")
                    diffuse_color_file.outColor >> material.diffuse_color

                # Accept also BaseColor
                # create a new aiImage
                base_color_file_path = glob.glob(
                    "%s/%s_BaseColor*" % (texture_path, material_name)
                )
                if base_color_file_path:
                    use_udim = False
                    if len(base_color_file_path) > 1:
                        use_udim = True
                    base_color_file_path = base_color_file_path[0]
                    if use_udim:
                        base_color_file_path = \
                            base_color_file_path.replace("1001", "<udim>")

                    base_color_file = pm.shadingNode("file", asTexture=1)
                    connect_place2d_to_file(place2d, base_color_file)
                    base_color_file.setAttr("ignoreColorSpaceFileRules", 1)
                    base_color_file.fileTextureName.set(base_color_file_path)
                    base_color_file.colorSpace.set("sRGB")
                    try:
                        base_color_file.outColor >> material.diffuse_color
                    except AttributeError:
                        # RedshiftStandardMaterial
                        base_color_file.outColor >> material.base_color

                # *********************************************
                # Height
                height_channel_names = [
                    "Height",
                    "DisplaceHeightField",
                    "DisplacementHeight",
                ]
                for height_channel_name in height_channel_names:
                    height_file_path = glob.glob(
                        "%s/%s_%s*" % (texture_path, material_name, height_channel_name)
                    )
                    if height_file_path:
                        use_udim = False
                        if len(height_file_path) > 1:
                            use_udim = True
                        height_file_path = height_file_path[0]
                        if use_udim:
                            height_file_path = \
                                height_file_path.replace("1001", "<udim>")

                        # create a displacement node
                        shading_node = material.attr("outColor").outputs(
                            type="shadingEngine"
                        )[0]
                        disp_shader = pm.shadingNode(
                            "RedshiftDisplacement", asUtility=1
                        )
                        # if os.path.splitext(height_file_path)[1] == '.exr':  # might not be necessary
                        #     disp_shader.setAttr('newrange_min', -1)
                        disp_shader.out >> shading_node.displacementShader

                        # create texture
                        disp_file = pm.shadingNode("file", asTexture=1)
                        connect_place2d_to_file(place2d, disp_file)
                        disp_file.fileTextureName.set(height_file_path)
                        disp_file.colorSpace.set("Raw")
                        disp_file.setAttr("ignoreColorSpaceFileRules", 1)
                        disp_file.alphaIsLuminance.set(1)
                        disp_file.outColor >> disp_shader.texMap

                        break

                # *********************************************
                # Metalness
                # set material BRDF to GGX and set fresnel type to metalness
                try:
                    material.refl_brdf.set(1)
                    material.refl_fresnel_mode.set(2)
                except AttributeError:
                    # RedshiftStandardMaterial
                    pass

                metalness_file_path = glob.glob(
                    "%s/%s_Metal*" % (texture_path, material_name)
                )
                if metalness_file_path:
                    use_udim = False
                    if len(metalness_file_path) > 1:
                        use_udim = True
                    metalness_file_path = metalness_file_path[0]
                    if use_udim:
                        metalness_file_path = \
                            metalness_file_path.replace("1001", "<udim>")

                    metalness_file = pm.shadingNode("file", asTexture=1)
                    connect_place2d_to_file(place2d, metalness_file)
                    metalness_file.fileTextureName.set(metalness_file_path)
                    metalness_file.colorSpace.set("Raw")
                    metalness_file.setAttr("ignoreColorSpaceFileRules", 1)
                    metalness_file.alphaIsLuminance.set(1)
                    try:
                        metalness_file.outAlpha >> material.refl_metalness
                    except AttributeError:
                        # RedshiftStandardMaterial
                        metalness_file.outAlpha >> material.metalness

                # *********************************************
                # Reflectivity
                reflectivity_file_path = glob.glob(
                    "%s/%s_Reflectivity*" % (texture_path, material_name)
                )
                if reflectivity_file_path:
                    use_udim = False
                    if len(reflectivity_file_path) > 1:
                        use_udim = True
                    reflectivity_file_path = reflectivity_file_path[0]
                    if use_udim:
                        reflectivity_file_path = \
                            reflectivity_file_path.replace("1001", "<udim>")

                    reflectivity_file = pm.shadingNode("file", asTexture=1)
                    connect_place2d_to_file(place2d, reflectivity_file)
                    reflectivity_file.fileTextureName.set(reflectivity_file_path)
                    reflectivity_file.colorSpace.set("sRGB")
                    reflectivity_file.setAttr("ignoreColorSpaceFileRules", 1)
                    reflectivity_file.alphaIsLuminance.set(1)
                    try:
                        reflectivity_file.outColor >> material.refl_reflectivity
                    except AttributeError:
                        # RedshiftStandardMaterial
                        reflectivity_file.outColor >> material.refl_weight

                # *********************************************
                # Normal
                normal_file_path = glob.glob(
                    "%s/%s_Normal*" % (texture_path, material_name)
                )
                if normal_file_path:
                    use_udim = False
                    if len(normal_file_path) > 1:
                        use_udim = True
                    normal_file_path = normal_file_path[0]
                    if use_udim:
                        normal_file_path = normal_file_path.replace("1001", "<udim>")

                    # Redshift BumpMap doesn't work properly with Substance normals
                    rs_normal_map = pm.shadingNode("RedshiftBumpMap", asUtility=1)
                    # rs_normal_map = pm.shadingNode("RedshiftNormalMap", asUtility=1)
                    # set to tangent-space normals
                    rs_normal_map.inputType.set(1)
                    normal_file = pm.shadingNode("file", asTexture=1)
                    connect_place2d_to_file(place2d, normal_file)
                    normal_file.fileTextureName.set(normal_file_path)
                    normal_file.colorSpace.set("Raw")
                    normal_file.setAttr("ignoreColorSpaceFileRules", 1)
                    normal_file.outColor >> rs_normal_map.input
                    # rs_normal_map.tex0.set(normal_file_path)

                    rs_normal_map.out >> material.bump_input
                    rs_normal_map.scale.set(1)

                # *********************************************
                # Roughness
                # specularRoughness
                roughness_file_path = glob.glob(
                    "%s/%s_Roughness*" % (texture_path, material_name)
                )
                if roughness_file_path:
                    use_udim = False
                    if len(roughness_file_path) > 1:
                        use_udim = True
                    roughness_file_path = roughness_file_path[0]
                    if use_udim:
                        roughness_file_path = \
                            roughness_file_path.replace("1001", "<udim>")
                    roughness_file = pm.shadingNode("file", asTexture=1)
                    connect_place2d_to_file(place2d, roughness_file)
                    roughness_file.fileTextureName.set(roughness_file_path)
                    roughness_file.colorSpace.set("Raw")
                    roughness_file.setAttr("ignoreColorSpaceFileRules", 1)
                    roughness_file.alphaIsLuminance.set(1)
                    roughness_file.outAlpha >> material.refl_roughness

    @classmethod
    def redshift_ic_ipc_bake(cls):
        """Sets the render settings for IC + IPC bake"""
        # set motion blur
        start_frame = int(pm.playbackOptions(q=True, ast=True))
        end_frame = int(pm.playbackOptions(q=True, aet=True))

        cls.rso_options["bake"]["motionBlurFrameDuration"] = end_frame - start_frame + 1

        rso = pm.PyNode("redshiftOptions")

        # store and set attributes
        for attr in cls.rso_options["bake"]:
            cls.rso_options["orig"][attr] = rso.attr(attr).get()
            rso.attr(attr).set(cls.rso_options["bake"][attr])

        # go to the first frame
        current_frame = pm.currentTime(q=1)
        cls.rso_options["current_frame"] = current_frame
        pm.currentTime(start_frame)

        # do a render
        pm.mel.eval('rsRender -render -rv -cam "<renderview>";')

    @classmethod
    def redshift_ic_ipc_bake_restore(cls):
        """restores the previous render settings"""
        rso = pm.PyNode("redshiftOptions")

        # revert settings back
        for attr in cls.rso_options["orig"]:
            rso.attr(attr).set(cls.rso_options["orig"][attr])

        # set the GI engines
        rso.primaryGIEngine.set(cls.rso_options["bake"]["primaryGIEngine"])
        rso.secondaryGIEngine.set(cls.rso_options["bake"]["secondaryGIEngine"])

        # set the irradiance method to load
        rso.irradiancePointCloudMode.set(1)  # Load
        rso.irradianceCacheMode.set(1)  # Load

        # set the cache paths
        rso.irradiancePointCloudFilename.set(
            cls.rso_options["bake"]["irradiancePointCloudFilename"]
        )
        rso.irradianceCacheFilename.set(
            cls.rso_options["bake"]["irradianceCacheFilename"]
        )

        # go to current frame
        current_frame = cls.rso_options["current_frame"]
        pm.currentTime(current_frame)

    @classmethod
    def update_render_settings(cls):
        """updates render settings for current renderer"""
        from anima.dcc import mayaEnv

        m = mayaEnv.Maya()
        v = m.get_current_version()
        if v:
            m.set_render_filename(version=v)

    @classmethod
    def afanasy_job_submitter(cls):
        """Opens the Afanasy job sumitter UI"""
        from anima.dcc.mayaEnv import afanasy

        ui = afanasy.UI()
        ui.show()

    @classmethod
    def auto_convert_to_redshift(cls):
        """converts the current scene to Redshift"""
        from anima.dcc.mayaEnv import ai2rs

        cm = ai2rs.ConversionManager()
        cm.auto_convert()

    @classmethod
    def convert_nodes_to_redshift(cls):
        """converts the selected nodes to Redshift"""
        from anima.dcc.mayaEnv import ai2rs

        cm = ai2rs.ConversionManager()
        for node in pm.selected():
            cm.convert(node)

    @classmethod
    def rsproxy_to_bounding_box(cls):
        """sets the display mode to bounding box on selected proxy nodes"""
        cls.rsproxy_display_mode_toggle(display_mode=0)

    @classmethod
    def rsproxy_to_preview_mesh(cls):
        """sets the display mode to preview mesh on selected proxy nodes"""
        cls.rsproxy_display_mode_toggle(display_mode=1)

    @classmethod
    def rsproxy_display_mode_toggle(cls, display_mode=0):
        """sets the display mode on selected proxies

        :param display_mode:

          0: Bounding Box
          1: Preview Mesh
          2: Linked Mesh
          3: Hide In Viewport
        :return:
        """
        for node in pm.ls(sl=1):
            hist = node.getShape().listHistory()
            proxy = hist[1]
            proxy.displayMode.set(display_mode)

    @classmethod
    def standin_to_bbox(cls):
        """convert the selected stand-in nodes to bbox"""
        [
            node.mode.set(0)
            for node in pm.ls(sl=1)
            if isinstance(node.getShape(), pm.nt.AiStandIn)
        ]

    @classmethod
    def standin_to_polywire(cls):
        """convert the selected stand-in nodes to bbox"""
        [
            node.mode.set(2)
            for node in pm.ls(sl=1)
            if isinstance(node.getShape(), pm.nt.AiStandIn)
        ]

    @classmethod
    def add_miLabel(cls):
        selection = pm.ls(sl=1)

        for node in selection:
            if node.type() == "Transform":
                if node.hasAttr("miLabel"):
                    pass
                else:
                    pm.addAttr(node, ln="miLabel", at="long", keyable=True)

    @classmethod
    def connect_facingRatio_to_vCoord(cls):
        selection = pm.ls(sl=1)
        for i in range(1, len(selection)):
            selection[0].facingRatio.connect((selection[i] + ".vCoord"), force=True)

    @classmethod
    def set_shape_attribute(
        cls, attr_name, value, apply_to_hierarchy, disable_undo_queue=False
    ):
        """sets shape attributes"""
        undo_state = pm.undoInfo(q=1, st=1)
        if disable_undo_queue:
            pm.undoInfo(st=False)

        supported_shapes = ["aiStandIn", "mesh", "nurbsCurve"]

        attr_mapper = {
            "castsShadows": "overrideCastsShadows",
            "receiveShadows": "overrideReceiveShadows",
            "primaryVisibility": "overridePrimaryVisibility",
            "visibleInReflections": "overrideVisibleInReflections",
            "visibleInRefractions": "overrideVisibleInRefractions",
            "doubleSided": "overrideDoubleSided",
            "aiSelfShadows": "overrideSelfShadows",
            "aiOpaque": "overrideOpaque",
            "aiVisibleInDiffuse": "overrideVisibleInDiffuse",
            "aiVisibleInGlossy": "overrideVisibleInGlossy",
            "aiMatte": "overrideMatte",
        }

        pre_selection_list = pm.ls(sl=1)
        if apply_to_hierarchy:
            pm.select(hierarchy=1)

        objects = pm.ls(sl=1, type=supported_shapes)

        # get override_attr_name from dictionary
        if attr_name in attr_mapper:
            override_attr_name = attr_mapper[attr_name]
        else:
            override_attr_name = None

        # register a caller
        pdm = ProgressManager()
        caller = pdm.register(len(objects), "Setting Shape Attribute")

        layers = pm.ls(type="renderLayer")
        is_default_layer = layers[0].currentLayer() == layers[0].defaultRenderLayer()

        if value != -1:
            for item in objects:
                attr_full_name = "%s.%s" % (item.name(), attr_name)
                override_attr_full_name = "%s.%s" % (item.name(), override_attr_name)
                caller.step(message=attr_full_name)

                if not is_default_layer:
                    pm.editRenderLayerAdjustment(attr_full_name)

                item.setAttr(attr_name, value)
                # if there is an accompanying override attribute like it is
                # found in aiStandIn node
                # then also set override{Attr} to True
                if override_attr_name and cmds.attributeQuery(
                    override_attr_name, n=item.name(), ex=1
                ):
                    if not is_default_layer:
                        pm.editRenderLayerAdjustment(override_attr_full_name)
                    item.setAttr(override_attr_name, True)
        else:
            for item in objects:
                attr_full_name = "%s.%s" % (item.name(), attr_name)
                override_attr_full_name = "%s.%s" % (item.name(), override_attr_name)
                caller.step(message=attr_full_name)

                # remove any overrides
                if not is_default_layer:
                    pm.editRenderLayerAdjustment(attr_full_name, remove=1)

                if (
                    override_attr_name
                    and cmds.attributeQuery(override_attr_name, n=item.name(), ex=1)
                    and not is_default_layer
                ):
                    pm.editRenderLayerAdjustment(override_attr_full_name, remove=1)

        # caller.end_progress()

        pm.undoInfo(st=undo_state)

        pm.select(pre_selection_list)

    @classmethod
    def set_finalGatherHide(cls, value):
        """sets the finalGatherHide to on or off for the given list of objects"""
        attr_name = "miFinalGatherHide"
        objects = pm.ls(sl=1)

        for obj in objects:

            shape = obj

            if isinstance(obj, pm.nt.Transform):
                shape = obj.getShape()

            if not isinstance(shape, (pm.nt.Mesh, pm.nt.NurbsSurface)):
                continue

            # add the attribute if it doesn't already exists
            if not shape.hasAttr(attr_name):
                pm.addAttr(shape, ln=attr_name, at="long", min=0, max=1, k=1)

            obj.setAttr(attr_name, value)

    @classmethod
    def replace_shaders_with_last(cls):
        """Assigns the last shader selected to all the objects using the shaders
        on the list
        """
        sel_list = pm.ls(sl=1)
        target_node = sel_list[-1]

        for node in sel_list[:-1]:
            pm.hyperShade(objects=node)
            pm.hyperShade(assign=target_node)

        pm.select(None)

    @classmethod
    def create_texture_ref_object(cls):
        selection = pm.ls(sl=1)
        for obj in selection:
            pm.select(obj)
            pm.runtime.CreateTextureReferenceObject()
        pm.select(selection)

    @classmethod
    def use_mib_texture_filter_lookup(cls):
        """Adds texture filter lookup node to the selected file texture nodes for
        better texture filtering.

        The function is smart enough to use the existing nodes, if there is a
        connection from the selected file nodes to a mib_texture_filter_lookup node
        then it will not create any new node and just use the existing ones.

        It will also not create any place2dTexture nodes if the file node doesn't
        have a place2dTexture node but is connected to a filter lookup node which
        already has a connection to a place2dTexture node.
        """

        file_nodes = pm.ls(sl=1, type="file")

        for file_node in file_nodes:
            # set the filter type to none
            file_node.filterType.set(0)

            # check if it is already connected to a mib_texture_filter_lookup node
            message_outputs = file_node.message.outputs(
                type="mib_texture_filter_lookup"
            )

            if len(message_outputs):
                # use the first one
                mib_texture_filter_lookup = message_outputs[0]
            else:
                # create a texture filter lookup node
                mib_texture_filter_lookup = pm.createNode("mib_texture_filter_lookup")

                # do the connection
                file_node.message >> mib_texture_filter_lookup.tex

            # check if the mib_texture_filter_lookup has any connection to a
            # placement node

            mib_t_f_l_to_placement = mib_texture_filter_lookup.inputs(
                type="place2dTexture"
            )

            placement_node = None
            if len(mib_t_f_l_to_placement):
                # do nothing
                placement_node = mib_t_f_l_to_placement[0].node()
            else:
                # get the texture placement
                placement_connections = file_node.inputs(
                    type="place2dTexture", p=1, c=1
                )

                # if there is no placement create one
                placement_node = None
                if len(placement_connections):
                    placement_node = placement_connections[0][1].node()
                    # disconnect connections from placement to file node
                    for conn in placement_connections:
                        conn[1] // conn[0]
                else:
                    placement_node = pm.createNode("place2dTexture")

                # connect placement to mr_texture_filter_lookup
                placement_node.outU >> mib_texture_filter_lookup.coordX
                placement_node.outV >> mib_texture_filter_lookup.coordY

            # connect color
            for output in file_node.outColor.outputs(p=1):
                mib_texture_filter_lookup.outValue >> output

            # connect alpha
            for output in file_node.outAlpha.outputs(p=1):
                mib_texture_filter_lookup.outValueA >> output

    @classmethod
    def convert_to_linear(cls):
        """adds a gamma_gain node in between the selected nodes outputs to make the
        result linear
        """

        #
        # convert to linear
        #

        selection = pm.ls(sl=1)

        for file_node in selection:
            # get the connections
            outputs = file_node.outputs(plugs=True)

            if not len(outputs):
                continue

            # and insert a mip_gamma_gain
            gamma_node = pm.createNode("mip_gamma_gain")
            gamma_node.setAttr("gamma", 2.2)
            gamma_node.setAttr("reverse", True)

            # connect the file_node to gamma_node
            try:
                file_node.outValue >> gamma_node.input
                file_node.outValueA >> gamma_node.inputA
            except AttributeError:
                file_node.outColor >> gamma_node.input

            # do all the connections from the output of the gamma
            for output in outputs:
                try:
                    gamma_node.outValue >> output
                except RuntimeError:
                    gamma_node.outValueA >> output

        pm.select(selection)

    @classmethod
    def use_image_sequence(cls):
        """creates an expression to make the mentalrayTexture node also able to read
        image sequences

        Select your mentalrayTexture nodes and then run the script.

        The filename should use the file.%nd.ext format
        """

        textures = pm.ls(sl=1, type="mentalrayTexture")

        for texture in textures:
            # get the filename
            filename = texture.getAttr("fileTextureName")

            splits = filename.split(".")
            if len(splits) == 3:
                base = ".".join(splits[0:-2]) + "."
                pad = len(splits[-2])
                extension = "." + splits[-1]

                expr = (
                    "string $padded_frame = python(\"'%0"
                    + str(pad)
                    + "d'%\" + string(frame));\n"
                    + 'string $filename = "'
                    + base
                    + '" + \
                       $padded_frame + ".tga";\n'
                    + 'setAttr -type "string" '
                    + texture.name()
                    + ".fileTextureName $filename;\n"
                )

                # create the expression
                pm.expression(s=expr)

    @classmethod
    def add_to_selected_container(cls):
        selection = pm.ls(sl=1)
        conList = pm.ls(sl=1, con=1)
        objList = list(set(selection) - set(conList))
        if len(conList) == 0:
            pm.container(addNode=selection)
        elif len(conList) == 1:
            pm.container(conList, edit=True, addNode=objList)
        else:
            length = len(conList) - 1
            for i in range(0, length):
                containerList = conList[i]
                pm.container(conList[-1], edit=True, f=True, addNode=containerList)
                pm.container(conList[-1], edit=True, f=True, addNode=objList)

    @classmethod
    def remove_from_container(cls):
        selection = pm.ls(sl=1)
        for i in range(0, len(selection)):
            con = pm.container(q=True, fc=selection[i])
            pm.container(con, edit=True, removeNode=selection[i])

    @classmethod
    def reload_file_textures(cls):
        fileList = pm.ls(type="file")
        for fileNode in fileList:
            mel.eval("AEfileTextureReloadCmd(%s.fileTextureName)" % fileNode)

    @classmethod
    def transfer_shaders(cls):
        """transfer shaders between selected objects. It can search for
        hierarchies both in source and target sides.
        """
        selection = pm.ls(sl=1)
        pm.select(None)
        source = selection[0]
        target = selection[1]
        # auxiliary.transfer_shaders(source, target)
        # pm.select(selection)

        attr_names = [
            "castsShadows",
            "receiveShadows",
            "motionBlur",
            "primaryVisibility",
            "smoothShading",
            "visibleInReflections",
            "visibleInRefractions",
            "doubleSided",
            "opposite",
            "aiSelfShadows",
            "aiOpaque",
            "aiVisibleInDiffuse",
            "aiVisibleInGlossy",
            "aiExportTangents",
            "aiExportColors",
            "aiExportRefPoints",
            "aiExportRefNormals",
            "aiExportRefTangents",
            "color",
            "interpolation",
            "aiTranslator",
            "intensity",
            "aiExposure",
            "aiColorTemperature",
            "emitDiffuse",
            "emitSpecular",
            "aiDecayType",
            "lightVisible",
            "aiSamples",
            "aiNormalize",
            "aiCastShadows",
            "aiShadowDensity",
            "aiShadowColor",
            "aiAffectVolumetrics",
            "aiCastVolumetricShadows",
            "aiVolumeSamples",
            "aiDiffuse",
            "aiSpecular",
            "aiSss",
            "aiIndirect",
            "aiMaxBounces",
            "aiSubdivType",
            "aiSubdivIterations",
            "aiSubdivAdaptiveMetric",
            "aiSubdivPixelError",
            "aiSubdivUvSmoothing",
            "aiSubdivSmoothDerivs",
            "aiDispHeight",
            "aiDispPadding",
            "aiDispZeroValue",
            "aiDispAutobump",
            "aiStepSize",
            "rsEnableSubdivision",
            "rsSubdivisionRule",
            "rsScreenSpaceAdaptive",
            "rsDoSmoothSubdivision",
            "rsMinTessellationLength",
            "rsMaxTessellationSubdivs",
            "rsOutOfFrustumTessellationFactor",
            "rsLimitOutOfFrustumTessellation",
            "rsMaxOutOfFrustumTessellationSubdivs",
            "rsEnableDisplacement",
            "rsMaxDisplacement",
            "rsDisplacementScale",
            "rsAutoBumpMap",
            "rsObjectId",
        ]

        # check if they are direct parents of mesh or nurbs shapes
        source_shape = source.getShape()
        target_shape = target.getShape()

        if (
            source_shape
            and not isinstance(source_shape, pm.nt.NurbsCurve)
            and target_shape
            and not isinstance(target_shape, pm.nt.NurbsCurve)
        ):
            # do a direct assignment from source to target
            # shading_engines = source_shape.outputs(type=pm.nt.ShadingEngine)
            # pm.sets(shading_engines[0], fe=target)
            # pm.select(selection)
            lut = {"match": [(source_shape, target_shape)], "no_match": []}
        else:
            lut = auxiliary.match_hierarchy(source, target)

        for source_node, target_node in lut["match"]:
            auxiliary.transfer_shaders(source_node, target_node)
            # also transfer render attributes
            for attr_name in attr_names:
                try:
                    target_node.setAttr(attr_name, source_node.getAttr(attr_name))
                except (pm.MayaAttributeError, RuntimeError):
                    pass

                # input connections to attributes
                try:
                    for plug in source_node.attr(attr_name).inputs(p=1):
                        plug >> target_node.attr(attr_name)
                except pm.MayaAttributeError:
                    pass

            # caller.step()
        # caller.end_progress()

        if len(lut["no_match"]):
            pm.select(lut["no_match"])
            print(
                "The following nodes has no corresponding source:\n%s"
                % ("\n".join([node.name() for node in lut["no_match"]]))
            )

    @classmethod
    def fit_placement_to_UV(cls):
        selection = pm.ls(sl=1)
        uvs = [n for n in selection if isinstance(n, pm.general.MeshUV)]
        placements = [p for p in selection if isinstance(p, pm.nt.Place2dTexture)]

        # get the uv extends
        temp_data = pm.polyEditUV(uvs, q=1)
        u = sorted(temp_data[0::2])
        v = sorted(temp_data[1::2])
        umin = u[0]
        umax = u[-1]
        vmin = v[0]
        vmax = v[-1]

        for p in placements:
            p.setAttr("coverage", (umax - umin, vmax - vmin))
            p.setAttr("translateFrame", (umin, vmin))

    @classmethod
    def connect_placement2d_to_file(cls):
        """connects the selected placement node to the selected file textures"""
        attr_lut = [
            "coverage",
            "translateFrame",
            "rotateFrame",
            "mirrorU",
            "mirrorV",
            "stagger",
            "wrapU",
            "wrapV",
            "repeatUV",
            "offset",
            "rotateUV",
            "noiseUV",
            "vertexUvOne",
            "vertexUvTwo",
            "vertexUvThree",
            "vertexCameraOne",
            ("outUV", "uvCoord"),
            ("outUvFilterSize", "uvFilterSize"),
        ]

        # get placement and file nodes
        placement_node = pm.ls(sl=1, type=pm.nt.Place2dTexture)[0]
        file_nodes = pm.ls(sl=1, type=pm.nt.File)

        from anima import __string_types__

        for file_node in file_nodes:
            for attr in attr_lut:
                if isinstance(attr, __string_types__):
                    source_attr_name = attr
                    target_attr_name = attr
                elif isinstance(attr, tuple):
                    source_attr_name = attr[0]
                    target_attr_name = attr[1]
                placement_node.attr(source_attr_name) >> file_node.attr(
                    target_attr_name
                )

    @classmethod
    def open_node_in_browser(cls):
        # get selected nodes
        node_attrs = {
            "file": "fileTextureName",
            "aiImage": "filename",
            "aiStandIn": "dso",
        }
        import os
        from anima.utils import open_browser_in_location

        for node in pm.ls(sl=1):
            type_ = pm.objectType(node)
            # special case: if transform use shape
            if type_ == "transform":
                node = node.getShape()
                type_ = pm.objectType(node)
            attr_name = node_attrs.get(type_)
            if attr_name:
                # if any how it contains a "#" character use the path
                path = node.getAttr(attr_name)
                if "#" in path:
                    path = os.path.dirname(path)
                open_browser_in_location(path)

    @classmethod
    def enable_matte(cls, color=0):
        """enables matte on selected objects"""
        #
        # Enable Matte on Selected Objects
        #
        colors = [
            [0, 0, 0, 0],  # Not Visible
            [1, 0, 0, 0],  # Red
            [0, 1, 0, 0],  # Green
            [0, 0, 1, 0],  # Blue
            [0, 0, 0, 1],  # Alpha
        ]
        arnold_shaders = (pm.nt.AiStandard, pm.nt.AiHair, pm.nt.AiSkin, pm.nt.AiUtility)

        for node in pm.ls(
            sl=1, dag=1, type=[pm.nt.Mesh, pm.nt.NurbsSurface, "aiStandIn"]
        ):
            obj = node
            # if isinstance(node, pm.nt.Mesh):
            #    obj = node
            # elif isinstance(node, pm.nt.Transform):
            #    obj = node.getShape()

            shading_nodes = pm.listConnections(obj, type="shadingEngine")
            for shadingNode in shading_nodes:
                shader = shadingNode.attr("surfaceShader").connections()[0]
                if isinstance(shader, arnold_shaders):
                    try:
                        pm.editRenderLayerAdjustment(shader.attr("aiEnableMatte"))
                        pm.editRenderLayerAdjustment(shader.attr("aiMatteColor"))
                        pm.editRenderLayerAdjustment(shader.attr("aiMatteColorA"))
                        shader.attr("aiEnableMatte").set(1)
                        shader.attr("aiMatteColor").set(
                            colors[color][0:3], type="double3"
                        )
                        shader.attr("aiMatteColorA").set(colors[color][3])
                    except RuntimeError as e:
                        # there is some connections
                        print(str(e))

    @classmethod
    def disable_subdiv(cls, node):
        """Disables the subdiv on the given nodes

        :param node:
        :return:
        """
        if isinstance(node, pm.nt.Transform):
            shapes = node.getShapes()
        else:
            shapes = [node]

        for shape in shapes:
            try:
                shape.aiSubdivType.set(0)
            except AttributeError:
                pass

            try:
                shape.rsEnableSubdivision.set(0)
            except AttributeError:
                pass

    @classmethod
    def disable_subdiv_on_selected(cls):
        """disables subdiv on selected nodes"""
        for node in pm.ls(sl=1):
            cls.disable_subdiv(node)

    @classmethod
    def enable_subdiv_on_selected(cls, fixed_tes=False, max_subdiv=3):
        """enables subdiv on selected objects

        :param fixed_tes: Uses fixed tessellation.
        :param max_subdiv: The max subdivision iteration. Default 3.
        """
        #
        # Set SubDiv to CatClark on Selected nodes
        #
        for node in pm.ls(sl=1):
            cls.enable_subdiv(node, fixed_tes=fixed_tes, max_subdiv=max_subdiv)

    @classmethod
    def enable_subdiv(cls, node, fixed_tes=False, max_subdiv=3):
        """enables subdiv on selected objects

        :param node: The node to enable the subdiv too
        :param fixed_tes: Uses fixed tessellation.
        :param max_subdiv: The max subdivision iteration. Default 3.
        """
        if isinstance(node, pm.nt.Transform):
            shapes = node.getShapes()
        else:
            shapes = [node]

        for shape in shapes:
            try:
                shape.aiSubdivIterations.set(max_subdiv)
                shape.aiSubdivType.set(1)
                shape.aiSubdivPixelError.set(0)
            except AttributeError:
                pass

            try:
                shape.rsEnableSubdivision.set(1)
                shape.rsMaxTessellationSubdivs.set(max_subdiv)
                if not fixed_tes:
                    shape.rsScreenSpaceAdaptive.set(1)
                    shape.rsLimitOutOfFrustumTessellation.set(1)
                    shape.rsMaxOutOfFrustumTessellationSubdivs.set(1)
                else:
                    shape.rsScreenSpaceAdaptive.set(0)
                    shape.rsMinTessellationLength.set(0)
            except AttributeError:
                pass

    @classmethod
    def export_shader_attributes(cls):
        """exports the selected shader attributes to a JSON file"""
        # get data
        data = []
        nodes = pm.ls(sl=1)
        for node in nodes:
            node_attr_data = {}
            attrs = node.listAttr()
            for attr in attrs:
                try:
                    value = attr.get()
                    if not isinstance(value, pm.PyNode):
                        node_attr_data[attr.shortName()] = value
                except TypeError:
                    continue
            data.append(node_attr_data)

        # write data
        import json

        with open(cls.node_attr_info_temp_file_path, "w") as f:
            json.dump(data, f)

    @classmethod
    def export_shader_assignments_to_houdini(cls):
        """Exports shader assignments to Houdini via a JSON file.

        Use the Houdini counterpart to import the assignment data
        """
        # get the shaders from viewport selection
        shaders = []
        for node in pm.selected():
            shape = node.getShape()
            shading_engines = shape.outputs(type=pm.nt.ShadingEngine)

            for shading_engine in shading_engines:
                inputs = shading_engine.surfaceShader.inputs()
                for shader in inputs:
                    shaders.append(shader)

        # get the shapes for each shader
        shader_assignments = {}

        for shader in shaders:
            shader_name = shader.name()
            shading_engines = shader.outputs(type=pm.nt.ShadingEngine)
            if not shading_engines:
                continue
            shading_engine = shading_engines[0]
            shader_assignments[shader_name] = []

            assigned_nodes = pm.sets(shading_engine, q=1)
            for assigned_node in assigned_nodes:
                shape = assigned_node.node()

                # get the full path of the shape
                shape_full_path = shape.fullPath().replace("|", "/")
                shader_assignments[shader_name].append(shape_full_path)

        # write data
        try:
            import json

            with open(cls.shader_data_temp_file_path, "w") as f:
                json.dump(shader_assignments, f, indent=4)
        except BaseException as e:
            pm.confirmDialog(title="Error", message="%s" % e, button="OK")
        else:
            pm.confirmDialog(
                title="Successful",
                message="Shader Data exported successfully!",
                button="OK",
            )

    @classmethod
    def import_shader_attributes(cls):
        """imports shader attributes from a temp JSON file"""
        # read data
        import json

        with open(cls.node_attr_info_temp_file_path) as f:
            data = json.load(f)

        # set data
        nodes = pm.ls(sl=1)
        for i, node in enumerate(nodes):
            i = i % len(data)
            node_data = data[i]
            for key in node_data:
                value = node_data[key]
                try:
                    node.setAttr(key, value)
                except RuntimeError:
                    continue

    @classmethod
    def barndoor_simulator_setup(cls):
        """creates a barndoor simulator"""
        bs = auxiliary.BarnDoorSimulator()
        bs.light = pm.ls(sl=1)[0]
        bs.setup()

    @classmethod
    def barndoor_simulator_unsetup(cls):
        """removes the barndoor simulator"""
        bs = auxiliary.BarnDoorSimulator()
        for light in pm.ls(sl=1):
            light_shape = light.getShape()
            if isinstance(light_shape, pm.nt.Light):
                bs.light = light
            bs.unsetup()

    @classmethod
    def fix_barndoors(cls):
        """fixes the barndoors on scene lights created in MtoA 1.0 to match the
        new behaviour of barndoors in MtoA 1.1
        """
        for light in pm.ls(type="spotLight"):
            # calculate scale
            cone_angle = light.getAttr("coneAngle")
            penumbra_angle = light.getAttr("penumbraAngle")
            if penumbra_angle < 0:
                light.setAttr("coneAngle", max(cone_angle + penumbra_angle, 0.1))
            else:
                light.setAttr("coneAngle", max(cone_angle - penumbra_angle, 0.1))

    @classmethod
    def convert_aiSkinSSS_to_aiSkin(cls):
        """converts aiSkinSSS nodes in the current scene to aiSkin + aiStandard
        nodes automatically
        """
        attr_mapper = {
            # diffuse
            "color": {"node": "aiStandard", "attr_name": "color"},
            "diffuseWeight": {
                "node": "aiStandard",
                "attr_name": "Kd",
                "multiplier": 0.7,
            },
            "diffuseRoughness": {"node": "aiStandard", "attr_name": "diffuseRoughness"},
            # sss
            "sssWeight": {"node": "aiSkin", "attr_name": "sssWeight"},
            # shallowScatter
            "shallowScatterColor": {
                "node": "aiSkin",
                "attr_name": "shallowScatterColor",
            },
            "shallowScatterWeight": {
                "node": "aiSkin",
                "attr_name": "shallowScatterWeight",
            },
            "shallowScatterRadius": {
                "node": "aiSkin",
                "attr_name": "shallowScatterRadius",
            },
            # midScatter
            "midScatterColor": {
                "node": "aiSkin",
                "attr_name": "midScatterColor",
            },
            "midScatterWeight": {"node": "aiSkin", "attr_name": "midScatterWeight"},
            "midScatterRadius": {"node": "aiSkin", "attr_name": "midScatterRadius"},
            # deepScatter
            "deepScatterColor": {
                "node": "aiSkin",
                "attr_name": "deepScatterColor",
            },
            "deepScatterWeight": {"node": "aiSkin", "attr_name": "deepScatterWeight"},
            "deepScatterRadius": {"node": "aiSkin", "attr_name": "deepScatterRadius"},
            # primaryReflection
            "primaryReflectionColor": {"node": "aiSkin", "attr_name": "specularColor"},
            "primaryReflectionWeight": {
                "node": "aiSkin",
                "attr_name": "specularWeight",
            },
            "primaryReflectionRoughness": {
                "node": "aiSkin",
                "attr_name": "specularRoughness",
            },
            # secondaryReflection
            "secondaryReflectionColor": {"node": "aiSkin", "attr_name": "sheenColor"},
            "secondaryReflectionWeight": {"node": "aiSkin", "attr_name": "sheenWeight"},
            "secondaryReflectionRoughness": {
                "node": "aiSkin",
                "attr_name": "sheenRoughness",
            },
            # bump
            "normalCamera": {"node": "aiSkin", "attr_name": "normalCamera"},
            # sss multiplier
            "globalSssRadiusMultiplier": {
                "node": "aiSkin",
                "attr_name": "globalSssRadiusMultiplier",
            },
        }

        all_skin_sss = pm.ls(type="aiSkinSss")
        for skin_sss in all_skin_sss:
            skin = pm.shadingNode("aiSkin", asShader=1)
            standard = pm.shadingNode("aiStandard", asShader=1)

            skin.attr("outColor") >> standard.attr("emissionColor")
            standard.setAttr("emission", 1.0)
            skin.setAttr("fresnelAffectSss", 0)  # to match the previous behaviour

            node_mapper = {"aiSkin": skin, "aiStandard": standard}

            for attr in attr_mapper.keys():
                inputs = skin_sss.attr(attr).inputs(p=1, c=1)
                if inputs:
                    # copy inputs
                    destination_attr_name = inputs[0][0].name().split(".")[-1]
                    source = inputs[0][1]

                    if destination_attr_name in attr_mapper:
                        node = attr_mapper[destination_attr_name]["node"]
                        attr_name = attr_mapper[destination_attr_name]["attr_name"]
                        source >> node_mapper[node].attr(attr_name)
                    else:
                        source >> skin.attr(destination_attr_name)
                else:
                    # copy values
                    node = node_mapper[attr_mapper[attr]["node"]]
                    attr_name = attr_mapper[attr]["attr_name"]
                    multiplier = attr_mapper[attr].get("multiplier", 1.0)

                    attr_value = skin_sss.getAttr(attr)
                    if isinstance(attr_value, tuple):
                        attr_value = map(lambda x: x * multiplier, attr_value)
                    else:
                        attr_value *= multiplier
                    node.attr(attr_name).set(attr_value)

            # after everything is set up
            # connect the aiStandard to the shadingEngine
            for source, dest in skin_sss.outputs(p=1, c=1):
                standard.attr("outColor") >> dest

            # and rename the materials
            orig_name = skin_sss.name()

            # delete the skinSSS node
            pm.delete(skin_sss)

            skin_name = orig_name
            standard_name = "%s_aiStandard" % orig_name

            skin.rename(skin_name)
            standard.rename(standard_name)

            print("updated %s" % skin_name)

    @classmethod
    def normalize_sss_weights(cls):
        """normalizes the sss weights so their total weight is 1.0

        if a aiStandard is assigned to the selected object it searches for an
        aiSkin in the emission channel.

        the script considers 0.7 as the highest diffuse value for aiStandard
        """
        # get the shader of the selected object
        assigned_shader = pm.ls(
            pm.ls(sl=1)[0].getShape().outputs(type="shadingEngine")[0].inputs(), mat=1
        )[0]

        if assigned_shader.type() == "aiStandard":
            sss_shader = assigned_shader.attr("emissionColor").inputs()[0]
            diffuse_weight = assigned_shader.attr("Kd").get()
        else:
            sss_shader = assigned_shader
            diffuse_weight = 0

        def get_attr_or_texture(attr):
            if attr.inputs():
                # we probably have a texture assigned
                # so use its multiply attribute
                texture = attr.inputs()[0]
                attr = texture.attr("multiply")
                if isinstance(texture, pm.nt.AiImage):
                    attr = texture.attr("multiply")
                elif isinstance(texture, pm.nt.File):
                    attr = texture.attr("colorGain")
            return attr

        shallow_attr = get_attr_or_texture(sss_shader.attr("shallowScatterWeight"))
        mid_attr = get_attr_or_texture(sss_shader.attr("midScatterWeight"))
        deep_attr = get_attr_or_texture(sss_shader.attr("deepScatterWeight"))

        shallow_weight = shallow_attr.get()
        if isinstance(shallow_weight, tuple):
            shallow_weight = (
                shallow_weight[0] + shallow_weight[1] + shallow_weight[2]
            ) / 3.0

        mid_weight = mid_attr.get()
        if isinstance(mid_weight, tuple):
            mid_weight = (mid_weight[0] + mid_weight[1] + mid_weight[2]) / 3.0

        deep_weight = deep_attr.get()
        if isinstance(deep_weight, tuple):
            deep_weight = (deep_weight[0] + deep_weight[1] + deep_weight[2]) / 3.0

        total_sss_weight = shallow_weight + mid_weight + deep_weight

        mult = (1 - diffuse_weight / 0.7) / total_sss_weight
        try:
            shallow_attr.set(shallow_weight * mult)
        except RuntimeError:
            w = shallow_weight * mult
            shallow_attr.set(w, w, w)

        try:
            mid_attr.set(mid_weight * mult)
        except RuntimeError:
            w = mid_weight * mult
            mid_attr.set(w, w, w)

        try:
            deep_attr.set(deep_weight * mult)
        except RuntimeError:
            w = deep_weight * mult
            deep_attr.set(w, w, w)

    @classmethod
    def create_eye_shader_and_controls(cls):
        """This is pretty much specific to the way we are creating eye shaders
        for characters in KKS project, but it is a useful trick, select the
        inner eye objects before running
        """
        eyes = pm.ls(sl=1)
        if not eyes:
            return

        char = eyes[0].getAllParents()[-1]
        place = pm.shadingNode("place2dTexture", asUtility=1)
        emission_image = pm.shadingNode("aiImage", asTexture=1)
        ks_image = pm.shadingNode("aiImage", asTexture=1)

        texture_paths = {
            "emission": "$REPO1977/KKS/Assets/Characters/Body_Parts/Textures/"
            "char_eyeInner_light_v001.png",
            "Ks": "$REPO1977/KKS/Assets/Characters/Body_Parts/Textures/"
            "char_eyeInner_spec_v002.png",
        }

        emission_image.setAttr("filename", texture_paths["emission"])
        ks_image.setAttr("filename", texture_paths["Ks"])

        place.outUV >> emission_image.attr("uvcoords")

        if not char.hasAttr("eyeLightStrength"):
            char.addAttr("eyeLightStrength", at="double", min=0, dv=0.0, k=1)
        else:
            # set the default
            char.attr("eyeLightStrength").set(0)

        if not char.hasAttr("eyeLightAngle"):
            char.addAttr("eyeLightAngle", at="double", dv=0, k=1)

        if not char.hasAttr("eyeDiffuseWeight"):
            char.addAttr("eyeDiffuseWeight", at="double", dv=0.15, k=1, min=0, max=1)

        if not char.hasAttr("eyeSpecularWeight"):
            char.addAttr("eyeSpecularWeight", at="double", dv=1.0, k=1, min=0, max=1)

        if not char.hasAttr("eyeSSSWeight"):
            char.addAttr("eyeSSSWeight", at="double", dv=0.5, k=1, min=0, max=1)

        # connect eye light strength
        char.eyeLightStrength >> emission_image.attr("multiplyR")
        char.eyeLightStrength >> emission_image.attr("multiplyG")
        char.eyeLightStrength >> emission_image.attr("multiplyB")

        # connect eye light angle
        char.eyeLightAngle >> place.attr("rotateFrame")

        # connect specular weight
        char.eyeSpecularWeight >> ks_image.attr("multiplyR")
        char.eyeSpecularWeight >> ks_image.attr("multiplyG")
        char.eyeSpecularWeight >> ks_image.attr("multiplyB")

        for eye in eyes:
            shading_engine = eye.getShape().outputs(type="shadingEngine")[0]
            shader = pm.ls(shading_engine.inputs(), mat=1)[0]

            # connect the diffuse shader input to the emissionColor
            diffuse_texture = shader.attr("color").inputs(p=1, s=1)[0]
            diffuse_texture >> shader.attr("emissionColor")
            emission_image.outColorR >> shader.attr("emission")

            # also connect it to specular color
            diffuse_texture >> shader.attr("KsColor")
            # connect the Ks image to the specular weight
            ks_image.outColorR >> shader.attr("Ks")

            # also connect it to sss color
            diffuse_texture >> shader.attr("KsssColor")

            char.eyeDiffuseWeight >> shader.attr("Kd")
            char.eyeSSSWeight >> shader.attr("Ksss")

            # set some default values
            shader.attr("diffuseRoughness").set(0)
            shader.attr("Kb").set(0)
            shader.attr("directDiffuse").set(1)
            shader.attr("indirectDiffuse").set(1)
            shader.attr("specularRoughness").set(0.4)
            shader.attr("specularAnisotropy").set(0.5)
            shader.attr("specularRotation").set(0)
            shader.attr("specularFresnel").set(0)
            shader.attr("Kr").set(0)
            shader.attr("enableInternalReflections").set(0)
            shader.attr("Kt").set(0)
            shader.attr("transmittance").set([1, 1, 1])
            shader.attr("opacity").set([1, 1, 1])
            shader.attr("sssRadius").set([1, 1, 1])

        pm.select(eyes)

    @classmethod
    def randomize_attr(cls, nodes, attr, min, max, pre=0.1):
        """Randomizes the given attributes of the given nodes

        :param list nodes:
        :param str attr:
        :param float, int min:
        :param float, int max:
        :return:
        """
        import random
        import math

        rand = random.random
        floor = math.floor
        for node in nodes:
            r = rand() * float(max - min) + float(min)
            r = floor(r / pre) * pre
            node.setAttr(attr, r)

    @classmethod
    def randomize_light_color_temp(cls, min_field, max_field):
        """Randomizes the color temperature of selected lights

        :param min:
        :param max:
        :return:
        """
        min = pm.floatField(min_field, q=1, v=1)
        max = pm.floatField(max_field, q=1, v=1)
        cls.randomize_attr(
            [node.getShape() for node in pm.ls(sl=1)], "aiColorTemperature", min, max, 1
        )

    @classmethod
    def randomize_light_intensity(cls, min_field, max_field):
        """Randomizes the intensities of selected lights

        :param min:
        :param max:
        :return:
        """
        min = pm.floatField(min_field, q=1, v=1)
        max = pm.floatField(max_field, q=1, v=1)
        cls.randomize_attr(
            [node.getShape() for node in pm.ls(sl=1)], "aiExposure", min, max, 0.1
        )

    @classmethod
    def setup_outer_eye_render_attributes(cls):
        """sets outer eye render attributes for characters, select outer eye
        objects and run this
        """
        for node in pm.ls(sl=1):
            shape = node.getShape()
            shape.setAttr("castsShadows", 0)
            shape.setAttr("visibleInReflections", 0)
            shape.setAttr("visibleInRefractions", 0)
            shape.setAttr("aiSelfShadows", 0)
            shape.setAttr("aiOpaque", 0)
            shape.setAttr("aiVisibleInDiffuse", 0)
            shape.setAttr("aiVisibleInGlossy", 0)

    @classmethod
    def setup_window_glass_render_attributes(cls):
        """sets window glass render attributes for environments, select window
        glass objects and run this
        """
        shader_name = "toolbox_glass_shader"
        shaders = pm.ls("%s*" % shader_name)
        selection = pm.ls(sl=1)
        if len(shaders) > 0:
            shader = shaders[0]
        else:
            shader = pm.shadingNode("aiStandard", asShader=1, name="%s#" % shader_name)
            shader.setAttr("Ks", 1)
            shader.setAttr("specularRoughness", 0)
            shader.setAttr("Kr", 0)
            shader.setAttr("enableInternalReflections", 0)
            shader.setAttr("Kt", 0)
            shader.setAttr("KtColor", (0, 0, 0))

        shape_attributes = [
            ("castsShadows", 0),
            ("visibleInReflections", 0),
            ("visibleInRefractions", 0),
            ("aiSelfShadows", 0),
            ("aiOpaque", 1),
            ("aiVisibleInDiffuse", 0),
            ("aiVisibleInGlossy", 0),
        ]

        for node in selection:
            shape = node.getShape()
            map(lambda x: shape.setAttr(*x), shape_attributes)

            if isinstance(shape, pm.nt.AiStandIn):
                # get the glass shader or create one
                shape.overrideShaders.set(1)

            # assign it to the stand in
            pm.select(node)
            pm.hyperShade(assign=shader)

    @classmethod
    def dummy_window_light_plane(cls):
        """creates or updates the dummy window plane for the given area light"""
        area_light_list = pm.selected()
        from anima.dcc.mayaEnv import auxiliary

        for light in area_light_list:
            dwl = auxiliary.DummyWindowLight()
            dwl.light = light
            dwl.update()

    @classmethod
    def setup_z_limiter(cls):
        """creates z limiter setup"""
        shader_name = "z_limiter_shader#"
        shaders = pm.ls("%s*" * shader_name)
        if len(shaders) > 0:
            shader = shaders[0]
        else:
            shader = pm.shadingNode(
                "surfaceShader", asShader=1, name="%s#" % shader_name
            )

    @classmethod
    def convert_file_node_to_ai_image_node(cls):
        """converts the file node to aiImage node"""
        default_values = {
            "coverageU": 1,
            "coverageV": 1,
            "translateFrameU": 0,
            "translateFrameV": 0,
            "rotateFrame": 0,
            "repeatU": 1,
            "repeatV": 1,
            "offsetU": 0,
            "offsetV": 0,
            "rotateUV": 0,
            "noiseU": 0,
            "noiseV": 0,
        }

        for node in pm.ls(sl=1, type="file"):
            node_name = node.name()
            path = node.getAttr("fileTextureName")
            ai_image = pm.shadingNode("aiImage", asTexture=1)
            ai_image.setAttr("filename", path)

            # check the placement node
            placements = node.listHistory(type="place2dTexture")
            if len(placements):
                placement = placements[0]
                # check default values
                if any(
                    [
                        placement.getAttr(attr_name) != default_values[attr_name]
                        for attr_name in default_values
                    ]
                ):
                    # connect the placement to the aiImage
                    placement.outUV >> ai_image.uvcoords
                else:
                    # delete it
                    pm.delete(placement)

            # connect the aiImage
            for attr_out, attr_in in node.outputs(p=1, c=1):
                attr_name = attr_out.name().split(".")[-1]
                if attr_name == "message":
                    continue
                ai_image.attr(attr_name) >> attr_in

            # delete the File node
            pm.delete(node)
            # rename the aiImage node
            ai_image.rename(node_name)

    @classmethod
    def create_generic_tooth_shader(cls):
        """creates generic tooth shader for selected objects"""
        shader_name = "toolbox_generic_tooth_shader#"
        selection = pm.ls(sl=1)

        shader_tree = {
            "type": "aiStandard",
            "class": "asShader",
            "attr": {
                "color": [1, 0.909, 0.815],
                "Kd": 0.2,
                "KsColor": [1, 1, 1],
                "Ks": 0.5,
                "specularRoughness": 0.10,
                "specularFresnel": 1,
                "Ksn": 0.05,
                "enableInternalReflections": 0,
                "KsssColor": [1, 1, 1],
                "Ksss": 1,
                "sssRadius": [1, 0.853, 0.68],
                "normalCamera": {
                    "output": "outNormal",
                    "type": "bump2d",
                    "class": "asTexture",
                    "attr": {
                        "bumpDepth": 0.05,
                        "bumpValue": {
                            "output": "outValue",
                            "type": "aiNoise",
                            "class": "asUtility",
                            "attr": {
                                "scaleX": 4,
                                "scaleY": 0.250,
                                "scaleZ": 4,
                            },
                        },
                    },
                },
            },
        }

        shader = auxiliary.create_shader(shader_tree, shader_name)

        for node in selection:
            # assign it to the stand in
            pm.select(node)
            pm.hyperShade(assign=shader)

    @classmethod
    def create_generic_gum_shader(self):
        """set ups generic gum shader for selected objects"""
        shader_name = "toolbox_generic_gum_shader#"
        selection = pm.ls(sl=1)

        shader_tree = {
            "type": "aiStandard",
            "class": "asShader",
            "attr": {
                "color": [0.993, 0.596, 0.612],
                "Kd": 0.35,
                "KsColor": [1, 1, 1],
                "Ks": 0.010,
                "specularRoughness": 0.2,
                "enableInternalReflections": 0,
                "KsssColor": [1, 0.6, 0.6],
                "Ksss": 0.5,
                "sssRadius": [0.5, 0.5, 0.5],
                "normalCamera": {
                    "output": "outNormal",
                    "type": "bump2d",
                    "class": "asTexture",
                    "attr": {
                        "bumpDepth": 0.1,
                        "bumpValue": {
                            "output": "outValue",
                            "type": "aiNoise",
                            "class": "asUtility",
                            "attr": {
                                "scaleX": 4,
                                "scaleY": 1,
                                "scaleZ": 4,
                            },
                        },
                    },
                },
            },
        }

        shader = auxiliary.create_shader(shader_tree, shader_name)

        for node in selection:
            # assign it to the stand in
            pm.select(node)
            pm.hyperShade(assign=shader)

    @classmethod
    def create_generic_tongue_shader(self):
        """set ups generic tongue shader for selected objects"""
        shader_name = "toolbox_generic_tongue_shader#"
        selection = pm.ls(sl=1)

        shader_tree = {
            "type": "aiStandard",
            "class": "asShader",
            "attr": {
                "color": [0.675, 0.174, 0.194],
                "Kd": 0.35,
                "KsColor": [1, 1, 1],
                "Ks": 0.010,
                "specularRoughness": 0.2,
                "enableInternalReflections": 0,
                "KsssColor": [1, 0.3, 0.3],
                "Ksss": 0.5,
                "sssRadius": [0.5, 0.5, 0.5],
                "normalCamera": {
                    "output": "outNormal",
                    "type": "bump2d",
                    "class": "asTexture",
                    "attr": {
                        "bumpDepth": 0.1,
                        "bumpValue": {
                            "output": "outValue",
                            "type": "aiNoise",
                            "class": "asUtility",
                            "attr": {
                                "scaleX": 4,
                                "scaleY": 1,
                                "scaleZ": 4,
                            },
                        },
                    },
                },
            },
        }

        shader = auxiliary.create_shader(shader_tree, shader_name)

        for node in selection:
            # assign it to the stand in
            pm.select(node)
            pm.hyperShade(assign=shader)

    @classmethod
    def create_ea_matte(cls):
        """creates "ebesinin ami" matte shader with opacity for selected
        objects.

        It is called "EA Matte" for one reason, this matte is not necessary in
        normal working conditions. That is you change the color and look of
        some 3D element in 3D application and do an artistic grading at post to
        the whole plate, not to individual elements in the render.

        And because we are forced to create this matte layer, we thought that
        we should give it a proper name.
        """
        # get the selected objects
        # for each object create a new surface shader with the opacity
        # channel having the opacity of the original shader

        # create a lut for objects that have the same material not to cause
        # multiple materials to be created
        daro = pm.PyNode("defaultArnoldRenderOptions")

        attrs = {
            "AASamples": 4,
            "GIDiffuseSamples": 0,
            "GIGlossySamples": 0,
            "GIRefractionSamples": 0,
            "sssBssrdfSamples": 0,
            "volumeIndirectSamples": 0,
            "GITotalDepth": 0,
            "GIDiffuseDepth": 0,
            "GIGlossyDepth": 0,
            "GIReflectionDepth": 0,
            "GIRefractionDepth": 0,
            "GIVolumeDepth": 0,
            "ignoreTextures": 1,
            "ignoreAtmosphere": 1,
            "ignoreLights": 1,
            "ignoreShadows": 1,
            "ignoreBump": 1,
            "ignoreSss": 1,
        }

        for attr in attrs:
            pm.editRenderLayerAdjustment(daro.attr(attr))
            daro.setAttr(attr, attrs[attr])

        try:
            aov_z = pm.PyNode("aiAOV_Z")
            pm.editRenderLayerAdjustment(aov_z.attr("enabled"))
            aov_z.setAttr("enabled", 0)
        except pm.MayaNodeError:
            pass

        try:
            aov_mv = pm.PyNode("aiAOV_motionvector")
            pm.editRenderLayerAdjustment(aov_mv.attr("enabled"))
            aov_mv.setAttr("enabled", 0)
        except pm.MayaNodeError:
            pass

        dad = pm.PyNode("defaultArnoldDriver")
        pm.editRenderLayerAdjustment(dad.attr("autocrop"))
        dad.setAttr("autocrop", 0)

    @classmethod
    def create_z_layer(cls):
        """creates z layer with arnold render settings"""
        daro = pm.PyNode("defaultArnoldRenderOptions")

        attrs = {
            "AASamples": 4,
            "GIDiffuseSamples": 0,
            "GIGlossySamples": 0,
            "GIRefractionSamples": 0,
            "sssBssrdfSamples": 0,
            "volumeIndirectSamples": 0,
            "GITotalDepth": 0,
            "GIDiffuseDepth": 0,
            "GIGlossyDepth": 0,
            "GIReflectionDepth": 0,
            "GIRefractionDepth": 0,
            "GIVolumeDepth": 0,
            "ignoreShaders": 1,
            "ignoreAtmosphere": 1,
            "ignoreLights": 1,
            "ignoreShadows": 1,
            "ignoreBump": 1,
            "ignoreNormalSmoothing": 1,
            "ignoreDof": 1,
            "ignoreSss": 1,
        }

        for attr in attrs:
            pm.editRenderLayerAdjustment(daro.attr(attr))
            daro.setAttr(attr, attrs[attr])

        try:
            aov_z = pm.PyNode("aiAOV_Z")
            pm.editRenderLayerAdjustment(aov_z.attr("enabled"))
            aov_z.setAttr("enabled", 1)
        except pm.MayaNodeError:
            pass

        try:
            aov_mv = pm.PyNode("aiAOV_motionvector")
            pm.editRenderLayerAdjustment(aov_mv.attr("enabled"))
            aov_mv.setAttr("enabled", 1)
        except pm.MayaNodeError:
            pass

        dad = pm.PyNode("defaultArnoldDriver")
        pm.editRenderLayerAdjustment(dad.attr("autocrop"))
        dad.setAttr("autocrop", 1)

    @classmethod
    def generate_reflection_curve(self):
        """Generates a curve which helps creating specular at the desired point"""
        from maya.OpenMaya import MVector
        from anima.dcc.mayaEnv import auxiliary

        vtx = pm.ls(sl=1)[0]
        normal = vtx.getNormal(space="world")
        panel = auxiliary.Playblaster.get_active_panel()
        camera = pm.PyNode(pm.modelPanel(panel, q=1, cam=1))
        camera_axis = MVector(0, 0, -1) * camera.worldMatrix.get()

        refl = camera_axis - 2 * normal.dot(camera_axis) * normal

        # create a new curve
        p1 = vtx.getPosition(space="world")
        p2 = p1 + refl

        curve = pm.curve(d=1, p=[p1, p2])

        # move pivot to the first point
        pm.xform(curve, rp=p1, sp=p1)

    @classmethod
    def import_gpu_content(self):
        """imports the selected GPU content"""
        import os

        imported_nodes = []

        for node in pm.ls(sl=1):
            gpu_node = node.getShape()
            gpu_path = gpu_node.getAttr("cacheFileName")

            new_nodes = pm.mel.eval(
                'AbcImport -mode import -reparent "%s" "%s";'
                % (node.fullPath(), os.path.expandvars(gpu_path))
            )

            # get imported nodes
            new_nodes = node.getChildren()
            new_nodes.remove(gpu_node)

            imported_node = None

            # filter material node
            for n in new_nodes:
                if n.name() != "materials":
                    imported_node = n
                else:
                    pm.delete(n)

            if imported_node:
                imported_node.t.set(0, 0, 0)
                imported_node.r.set(0, 0, 0)
                imported_node.s.set(1, 1, 1)
                pm.parent(imported_node, world=1)

                imported_nodes.append(imported_node)

        pm.select(imported_nodes)

    @classmethod
    def render_slicer(self):
        """A tool for slicing big render scenes
        :return:
        """
        # TODO: Add UI call for Render Slicer
        raise NotImplementedError("This UI is not implemented yet!")

    @classmethod
    def move_cache_files_wrapper(cls, source_driver_field, target_driver_field):
        """Wrapper for move_cache_files() command

        :param source_driver_field: Text field for source driver
        :param target_driver_field: Text field for target driver
        :return:
        """
        source_driver = source_driver_field.text()
        target_driver = target_driver_field.text()

        Render.move_cache_files(source_driver, target_driver)

    @classmethod
    def move_cache_files(cls, source_driver, target_driver):
        """moves the selected cache files to another location

        :param source_driver:
        :param target_driver:
        :return:
        """
        #
        # Move fur caches to new server
        #
        import os
        import shutil
        import glob

        pdm = ProgressManager()

        selected_nodes = pm.ls(sl=1)
        caller = pdm.register(len(selected_nodes), title="Moving Cache Files")

        for node in selected_nodes:
            ass_node = node.getShape()

            if not isinstance(ass_node, (pm.nt.AiStandIn, pm.nt.AiVolume)):
                continue

            if isinstance(ass_node, pm.nt.AiStandIn):
                ass_path = ass_node.dso.get()
            elif isinstance(ass_node, pm.nt.AiVolume):
                ass_path = ass_node.filename.get()

            ass_path = os.path.normpath(os.path.expandvars(ass_path))

            # give info to user
            caller.title = "Moving: %s" % ass_path

            # check if it is in the source location
            if source_driver not in ass_path:
                continue

            # check if it contains .ass.gz in its path
            if isinstance(ass_node, pm.nt.AiStandIn):
                if ".ass.gz" not in ass_path:
                    continue
            elif isinstance(ass_node, pm.nt.AiVolume):
                if ".vdb" not in ass_path:
                    continue

            # get the dirname
            ass_source_dir = os.path.dirname(ass_path)
            ass_target_dir = ass_source_dir.replace(source_driver, target_driver)

            # create the intermediate folders at destination
            try:
                os.makedirs(ass_target_dir)
            except OSError:
                # dir already exists
                pass

            # get all files list
            pattern = re.subn(r"[#]+", "*", ass_path)[0].replace(".ass.gz", ".ass*")
            all_cache_files = glob.glob(pattern)

            inner_caller = pdm.register(len(all_cache_files))
            for source_f in all_cache_files:
                target_f = source_f.replace(source_driver, target_driver)
                # move files to new location
                shutil.move(source_f, target_f)
                inner_caller.step(message="Moving: %s" % source_f)
            inner_caller.end_progress()

            # finally update DSO path
            if isinstance(ass_node, pm.nt.AiStandIn):
                ass_node.dso.set(ass_path.replace(source_driver, target_driver))
            elif isinstance(ass_node, pm.nt.AiVolume):
                ass_node.filename.set(ass_path.replace(source_driver, target_driver))

            caller.step()
        caller.end_progress()

    @classmethod
    def generate_rsproxy_from_selection(cls, per_selection=False):
        """generates a temp rs file from selected nodes and hides the selected
        nodes

        :param bool per_selection: Generates one rs file per selected objects
          if True. Default is False.
        """
        import os
        import tempfile
        import shutil
        from anima.dcc.mayaEnv import auxiliary
        from anima.dcc import mayaEnv

        m = mayaEnv.Maya()
        v = m.get_current_version()

        nodes = pm.ls(sl=1)

        temp_rs_proxies_grp = None
        if pm.ls("temp_rs_proxies_grp"):
            temp_rs_proxies_grp = pm.ls("temp_rs_proxies_grp")[0]
        else:
            temp_rs_proxies_grp = pm.nt.Transform(name="temp_rs_proxies_grp")

        rs_output_folder_path = os.path.join(v.absolute_path, "Outputs/rs").replace(
            "\\", "/"
        )
        try:
            os.makedirs(rs_output_folder_path)
        except OSError:
            pass

        def _generate_rs():
            export_command = 'rsProxy -fp "%(path)s" -c -z -sl;'
            temp_rs_full_path = tempfile.mktemp(suffix=".rs")
            rs_full_path = os.path.join(
                rs_output_folder_path, os.path.basename(temp_rs_full_path)
            ).replace("\\", "/")

            pm.mel.eval(export_command % {"path": temp_rs_full_path.replace("\\", "/")})

            shutil.move(temp_rs_full_path, rs_full_path)

            [n.v.set(0) for n in pm.ls(sl=1)]
            rs_proxy_node, rs_proxy_mesh = auxiliary.create_rs_proxy_node(
                path=rs_full_path
            )
            rs_proxy_tra = rs_proxy_mesh.getParent()

            rs_proxy_tra.rename("temp_rs_proxy#")
            pm.parent(rs_proxy_tra, temp_rs_proxies_grp)

        if per_selection:
            for node in nodes:
                pm.select(node)
                _generate_rs()
        else:
            pm.select(nodes)
            _generate_rs()

    @classmethod
    def import_image_as_plane(cls):
        """The replica of Blender tool"""
        # get the image path
        image_path = pm.fileDialog2(fileMode=1)

        # get the image width and height
        image_path = image_path[0] if image_path else ""

        from PIL import Image

        img = Image.open(image_path)
        w, h = img.size

        # create a new plane with that ratio
        # keep the height 1
        transform, poly_plane = pm.polyPlane(
            axis=[0, 0, 1], cuv=1, h=1, w=float(w) / float(h), texture=2, sh=1, sw=1
        )
        shape = transform.getShape()
        shape.instObjGroups[0].disconnect()

        # assign a surface shader
        surface_shader = pm.shadingNode("surfaceShader", asShader=1)
        shading_engine = pm.nt.ShadingEngine()
        surface_shader.outColor >> shading_engine.surfaceShader

        # assign the given file as texture
        placement = pm.nt.Place2dTexture()
        file_texture = pm.nt.File()

        pm.select([placement, file_texture])
        cls.connect_placement2d_to_file()

        file_texture.fileTextureName.set(image_path)
        file_texture.outColor >> surface_shader.outColor
        file_texture.outTransparency >> surface_shader.outTransparency

        # pm.sets(shading_engine, fe=transform)
        pm.select(shape)
        pm.hyperShade(assign=surface_shader)


class RenderSlicer(object):
    """A tool to help slice single frame renders in to many little parts which
    will help it to be rendered in small parts in a render farm.
    """

    def __init__(self, camera=None):
        self._camera = None
        self.camera = camera

    @property
    def slices_in_x(self):
        """getter for _slices_in_x attribute"""
        return self.camera.slicesInX.get()

    @slices_in_x.setter
    def slices_in_x(self, slices_in_x):
        """setter for _slices_in_x attribute"""
        self.camera.slicesInX.set(self._validate_slices_in_x(slices_in_x))

    @classmethod
    def _validate_slices_in_x(cls, slices_in_x):
        """validates the slices_in_x value"""
        if not isinstance(slices_in_x, int):
            raise TypeError(
                "%s.slices_in_x should be a non-zero positive integer, not %s"
                % (cls.__name__, slices_in_x.__class__.__name__)
            )

        if slices_in_x <= 0:
            raise ValueError(
                "%s.slices_in_x should be a non-zero positive integer" % cls.__name__
            )

        return slices_in_x

    @property
    def slices_in_y(self):
        """getter for _slices_in_y attribute"""
        return self.camera.slicesInY.get()

    @slices_in_y.setter
    def slices_in_y(self, slices_in_y):
        """setter for _slices_in_y attribute"""
        self.camera.slicesInY.set(self._validate_slices_in_y(slices_in_y))

    @classmethod
    def _validate_slices_in_y(cls, slices_in_y):
        """validates the slices_in_y value"""
        if not isinstance(slices_in_y, int):
            raise TypeError(
                "%s.slices_in_y should be a non-zero positive integer, not %s"
                % (cls.__name__, slices_in_y.__class__.__name__)
            )

        if slices_in_y <= 0:
            raise ValueError(
                "%s.slices_in_y should be a non-zero positive integer" % cls.__name__
            )

        return slices_in_y

    @property
    def camera(self):
        """getter for the _camera attribute"""
        return self._camera

    @camera.setter
    def camera(self, camera):
        """setter for the _camera attribute

        :param camera: A Maya camera
        :return: None
        """
        camera = self._validate_camera(camera)
        self._create_data_attributes(camera)
        self._camera = camera

    @classmethod
    def _validate_camera(cls, camera):
        """validates the given camera"""
        if camera is None:
            raise TypeError("Please supply a Maya camera")

        if not isinstance(camera, pm.nt.Camera):
            raise TypeError(
                "%s.camera should be a Maya camera, not %s"
                % (cls.__name__, camera.__class__.__name__)
            )

        return camera

    @classmethod
    def _create_data_attributes(cls, camera):
        """creates slicer data attributes inside the camera

        :param pm.nt.Camera camera: A maya camera
        """
        # store the original resolution
        # slices in x
        # slices in y

        # is_sliced
        # non_sliced_resolution_x
        # non_sliced_resolution_y
        # slices_in_x
        # slices_in_y

        if not camera.hasAttr("isSliced"):
            camera.addAttr("isSliced", at="bool")

        if not camera.hasAttr("nonSlicedResolutionX"):
            camera.addAttr("nonSlicedResolutionX", at="short")

        if not camera.hasAttr("nonSlicedResolutionY"):
            camera.addAttr("nonSlicedResolutionY", at="short")

        if not camera.hasAttr("slicesInX"):
            camera.addAttr("slicesInX", at="short")

        if not camera.hasAttr("slicesInY"):
            camera.addAttr("slicesInY", at="short")

    def _store_data(self):
        """stores slicer data inside the camera"""
        self._create_data_attributes(self.camera)
        self.camera.isSliced.set(self.is_sliced)

        # get the current render resolution
        dres = pm.PyNode("defaultResolution")
        width = dres.width.get()
        height = dres.height.get()

        self.camera.nonSlicedResolutionX.set(width)
        self.camera.nonSlicedResolutionY.set(height)
        self.camera.slicesInX.set(self.slices_in_x)
        self.camera.slicesInY.set(self.slices_in_y)

    @property
    def is_sliced(self):
        """A shortcut for the camera.isSliced attribute"""
        if self.camera.hasAttr("isSliced"):
            return self.camera.isSliced.get()
        return False

    @is_sliced.setter
    def is_sliced(self, is_sliced):
        """A shortcut for the camera.isSliced attribute"""
        if not self.camera.hasAttr("isSliced"):
            self._create_data_attributes(self.camera)

        self.camera.isSliced.set(is_sliced)

    def unslice(self):
        """resets the camera to original non-sliced state"""
        # unslice the camera
        dres = pm.PyNode("defaultResolution")

        # set the resolution to original
        dres.width.set(self.camera.getAttr("nonSlicedResolutionX"))
        dres.height.set(self.camera.getAttr("nonSlicedResolutionY"))
        dres.pixelAspect.set(1)

        self.camera.panZoomEnabled.set(0)

        self.camera.isSliced.set(False)

    def unslice_scene(self):
        """scans the scene cameras and unslice the scene"""
        dres = pm.PyNode("defaultResolution")
        dres.aspectLock.set(0)

        # TODO: check multi sliced camera
        for cam in pm.ls(type=pm.nt.Camera):
            if cam.hasAttr("isSliced") and cam.isSliced.get():
                dres.width.set(cam.nonSlicedResolutionX.get())
                dres.height.set(cam.nonSlicedResolutionY.get())
                dres.pixelAspect.set(1)
                cam.isSliced.set(False)

    def slice(self, slices_in_x, slices_in_y):
        """slices all renderable cameras"""
        # set render resolution
        self.unslice_scene()
        self.is_sliced = True
        self._store_data()

        sx = self.slices_in_x = slices_in_x
        sy = self.slices_in_y = slices_in_y

        # set render resolution
        d_res = pm.PyNode("defaultResolution")
        h_res = d_res.width.get()
        v_res = d_res.height.get()

        # this system only works when the
        d_res.aspectLock.set(0)
        d_res.pixelAspect.set(1)
        d_res.width.set(h_res / float(sx))
        d_res.pixelAspect.set(1)
        d_res.height.set(v_res / float(sy))
        d_res.pixelAspect.set(1)

        # use h_aperture to calculate v_aperture
        h_aperture = self.camera.getAttr("horizontalFilmAperture")

        # recalculate the other aperture
        v_aperture = h_aperture * v_res / h_res
        self.camera.setAttr("verticalFilmAperture", v_aperture)

        v_aperture = self.camera.getAttr("verticalFilmAperture")

        self.camera.setAttr("zoom", 1.0 / float(sx))

        t = 0
        for i in range(sy):
            v_pan = v_aperture / (2.0 * sy) * (1 + 2 * i - sy)
            for j in range(sx):
                h_pan = h_aperture / (2.0 * sx) * (1 + 2 * j - sx)
                pm.currentTime(t)
                pm.setKeyframe(self.camera, at="horizontalPan", v=h_pan)
                pm.setKeyframe(self.camera, at="verticalPan", v=v_pan)
                t += 1

        self.camera.panZoomEnabled.set(1)
        self.camera.renderPanZoom.set(1)

        d_res.pixelAspect.set(1)


class LightingSceneBuilder(object):
    """Build lighting scenes.

    This is a class that helps building lighting scenes by looking at the animation
    scenes, gathering data and then using that data to reference assets and cache files
    to the lighting scene.
    """

    LOOK_DEVS_GROUP_NAME = "LOOK_DEVS"
    ANIMS_GROUP_NAME = "ANIMS"
    LAYOUTS_GROUP_NAME = "LAYOUTS"
    CAMERA_GROUP_NAME = "CAMERA"

    def __init__(self):
        self.custom_rig_to_look_dev_lut = {}

    def update_rig_to_look_dev_lut(self, path):
        """Update the ``custom_rig_to_look_dev_lut.

        :param str path: The path to the custom json file.
        """
        import json
        with open(path, "r") as f:
            self.custom_rig_to_look_dev_lut = json.load(f)

    def get_cacheable_to_look_dev_version_lut(self, animation_version):
        """Build the lighting scene

        :param Version animation_version: The animation Version to open.

        :return:
        """
        from stalker import Type, Task, Version
        look_dev_type = Type.query.filter(Type.name == "Look Development").first()
        if not look_dev_type:
            raise RuntimeError(
                "No Look Development task type found, please create one!"
            )

        # open the animation version
        from anima.dcc import mayaEnv
        # get the current version
        m = mayaEnv.Maya()
        # store the current version to open later on
        lighting_version = m.get_current_version()
        m.open(
            animation_version,
            force=True,
            skip_update_check=True,
            prompt=False,
            reference_depth=1
        )
        # this version may uploaded with Stalker Pyramid, so update referenced versions
        # to get a proper version.inputs list
        m.update_version_inputs()

        # now load all references
        for ref in pm.listReferences():
            ref.load()

        # get all cacheable nodes
        cacheable_to_look_dev_version_lut = {}
        cacheable_nodes = auxiliary.get_cacheable_nodes()
        references_with_no_look_dev_task = []
        references_with_no_look_dev_version = []
        for cacheable_node in cacheable_nodes:
            non_renderable_objects = []
            cacheable_attr_value = cacheable_node.cacheable.get()
            ref = cacheable_node.referenceFile()
            if not ref:
                # this is not a referenced cacheable node,
                # it is probably the camera, skip it
                continue
            ref_version = ref.version
            copy_number = auxiliary.get_reference_copy_number(cacheable_node)
            cacheable_attr_value_with_copy_number = "{}{}".format(
                cacheable_attr_value, copy_number
            )
            rig_task = ref_version.task
            rig_task_id = rig_task.id
            rig_task_id_as_str = str(rig_task_id)
            rig_take_name = ref_version.take_name

            look_dev_take_name = None
            look_dev_task = None
            if rig_task_id_as_str in self.custom_rig_to_look_dev_lut:
                # there is a custom mapping for this rig use it
                if rig_take_name in self.custom_rig_to_look_dev_lut[rig_task_id_as_str]:
                    lut_data = \
                        self.custom_rig_to_look_dev_lut[rig_task_id_as_str][rig_take_name]
                    look_dev_task_id = lut_data['look_dev_task_id']
                    look_dev_take_name = lut_data['look_dev_take_name']
                    look_dev_task = Task.query.get(look_dev_task_id)
                    if "no_render" in lut_data:
                        # there are object not to be rendered
                        non_renderable_objects = lut_data["no_render"]
            else:
                # try to get the sibling look dev task
                look_dev_take_name = ref_version.take_name
                look_dev_task = Task.query\
                    .filter(Task.parent == rig_task.parent)\
                    .filter(Task.type == look_dev_type)\
                    .first()

            # no look_dev_task, we can't do anything about this asset, report it
            if not look_dev_task:
                references_with_no_look_dev_task.append(ref_version)
                # skip to the next cacheable node
                continue

            # get the latest published look dev version for this cacheable node
            latest_published_look_dev_version = Version.query\
                .filter(Version.task == look_dev_task)\
                .filter(Version.take_name == look_dev_take_name)\
                .filter(Version.is_published == True)\
                .order_by(Version.version_number.desc())\
                .first()

            if not latest_published_look_dev_version:
                references_with_no_look_dev_version.append(ref_version)

            cacheable_to_look_dev_version_lut[cacheable_attr_value_with_copy_number] = {
                "look_dev_version": latest_published_look_dev_version,
                "no_render": non_renderable_objects
            }

        # re-open the lighting version
        m.open(lighting_version, force=True, skip_update_check=True, prompt=False)

        print("\nReferences With No Look Dev Task")
        print("================================")
        print("\n".join([v.absolute_full_path for v in references_with_no_look_dev_task]))

        print("\nReferences With No Look Dev Version")
        print("===================================")
        print("\n".join([v.absolute_full_path for v in references_with_no_look_dev_version]))

        import pprint
        print("\nCacheable To LookDev Version Lut")
        print("================================")
        pprint.pprint(cacheable_to_look_dev_version_lut)

        return cacheable_to_look_dev_version_lut

    def create_item_group(self, group_name, hidden=False):
        """Crete item group.

        :param str group_name: The group name.
        :param bool hidden: If the group should be invisible.
        """
        query = pm.ls(group_name)
        if not query:
            group = pm.nt.Transform(name=group_name)
            group.v.set(not hidden)  # It should be hidden
        else:
            group = query[0]
        return group

    def build(
            self,
            transfer_shaders=True,
            transfer_uvs=False,
            cache_type=auxiliary.ALEMBIC
        ):
        """Build the lighting scene

        :return:
        """
        from anima.dcc import mayaEnv
        # get the current version
        m = mayaEnv.Maya()
        v = m.get_current_version()
        if not v:
            raise RuntimeError(
                "No version found! Please save an empty scene as a version under the "
                "Lighting task"
            )

        # check if this is really a lighting task
        from stalker import Type
        lighting_task = v.task
        lighting_type = Type.query.filter(Type.name == "Lighting").first()
        if not lighting_type:
            raise RuntimeError("No Lighting task type found, please create one!")

        if not lighting_task.type or not lighting_task.type == lighting_type:
            raise RuntimeError(
                "This is not a lighting task, please run this in a scene related to a "
                "Lighting task."
            )

        from stalker import Shot
        shot = lighting_task.parent
        if not shot:
            raise RuntimeError(
                "No parent task found! It is not possible to find sibling tasks!"
            )

        # get the animation task
        animation_type = Type.query.filter(Type.name == "Animation").first()
        if not animation_type:
            raise RuntimeError("No Animation task type found, please create one!")

        from stalker import Task
        animation_task = Task.query.filter(Task.parent == shot)\
            .filter(Task.type == animation_type).first()

        if not animation_task:
            raise RuntimeError("No Animation task found!")

        # get latest animation version
        from stalker import Version
        animation_version = Version.query\
            .filter(Version.task == animation_task)\
            .filter(Version.take_name == "Main")\
            .order_by(Version.version_number.desc())\
            .first()

        if not animation_version:
            raise RuntimeError("No Animation Version under Main take is found!")

        # get the cacheable_to_look_dev_lut
        cacheable_to_look_dev_version_lut = \
            self.get_cacheable_to_look_dev_version_lut(animation_version)

        # reference all caches
        # (we are assuming that these are all generated before)
        auxiliary.auto_reference_caches()

        # create the LOOK_DEVS group if it doesn't exist
        look_devs_group = self.create_item_group(self.LOOK_DEVS_GROUP_NAME, hidden=True)
        anims_group = self.create_item_group(self.ANIMS_GROUP_NAME)
        camera_group = self.create_item_group(self.CAMERA_GROUP_NAME)

        # get all referenced cache files
        # to prevent referencing the same look dev more than once,
        # store the referenced look dev version in a dictionary
        look_dev_version_to_ref_node_lut = {}
        for cache_ref_node in pm.listReferences():
            if not cache_ref_node.path.endswith(
                auxiliary.CACHE_FORMAT_DATA[cache_type]["file_extension"]
            ):
                continue

            # ref namespace is equal to the cacheable_attr_value
            cacheable_attr_value = cache_ref_node.namespace

            # if this is the shotCam, renderCam or the camera, just skip it
            if any([cam.lower() in cacheable_attr_value.lower() for cam in ("shotCam", "renderCam")]):
                # parent it under CAMERA group
                pm.parent(cache_ref_node.nodes()[0], camera_group)
                # and skip the rest
                continue

            # now use the cacheable_to_look_dev_version_lut to reference the look_dev
            # file
            look_dev_version = \
                cacheable_to_look_dev_version_lut[cacheable_attr_value]['look_dev_version']
            if look_dev_version in look_dev_version_to_ref_node_lut:
                # use the same ref_node
                look_dev_ref_node = look_dev_version_to_ref_node_lut[look_dev_version]
            else:
                # reference the look dev file
                look_dev_ref_node = m.reference(look_dev_version)
                look_dev_version_to_ref_node_lut[look_dev_version] = look_dev_ref_node
            # now we should have a reference node for the cache and a reference node for
            # the look dev

            look_dev_root_node = list(look_dev_ref_node.subReferences().values())[0].nodes()[0]
            cache_root_node = cache_ref_node.nodes()[0]
            if transfer_shaders:
                # transfer shaders from the look dev to the cache nodes
                pm.select(None)
                # look dev scenes references the model scene and the geometry is in the
                # model scene
                pm.select([look_dev_root_node, cache_root_node])
                Render.transfer_shaders()

            if transfer_uvs:
                from anima.dcc.mayaEnv import modeling
                pm.select(None)
                pm.select([look_dev_root_node, cache_root_node])
                modeling.Model.transfer_uvs()

            # hide non renderable objects
            cache_ref_node_nodes = cache_ref_node.nodes()
            for no_render_name in cacheable_to_look_dev_version_lut["no_render"]:
                for cached_node in cache_ref_node_nodes:
                    if cached_node.stripNamespace() == no_render_name:
                        cached_node.v.set(0)
                        continue

            # deselect everything to prevent unpredicted errors
            pm.select(None)

            # parent the look_dev_root_node under the LOOK_DEVS group
            pm.parent(look_dev_root_node, look_devs_group)

            # parent the alembic under the ANIMS group
            pm.parent(cache_root_node, anims_group)

        # animation version inputs should have been updated
        # reference any Layouts
        layouts_group = self.create_item_group(self.LAYOUTS_GROUP_NAME)
        layout_type = Type.query.filter(Type.name == "Layout").first()
        for input_version in animation_version.inputs:
            if input_version.task.type and input_version.task.type == layout_type:
                # reference this version here too
                # use the RSProxy repr
                rs_proxy_take_name = "{}@RS".format(
                    input_version.take_name.split("@")[0]
                )
                input_version = Version.query\
                    .filter(Version.task==input_version.task)\
                    .filter(Version.take_name==rs_proxy_take_name)\
                    .filter(Version.is_published==True)\
                    .order_by(Version.version_number.desc())\
                    .first()
                if input_version:
                    ref_node = m.reference(input_version)
                    # parent it to the LAYOUTS group
                    pm.parent(ref_node.nodes()[0], layouts_group)
