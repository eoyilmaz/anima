# -*- coding: utf-8 -*-
# Copyright (c) 2012-2020, Erkan Ozgur Yilmaz
#
# This module is part of anima and is released under the MIT
# License: http://www.opensource.org/licenses/MIT


from bpy.types import Panel, Operator


class Render(Panel):
    bl_idname = "ANIMA_TOOLBOX_PT_Render"
    bl_label = "Render"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'View'
    bl_parent_id = 'ANIMA_TOOLBOX_PT_Main'

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        box = layout.box()
        row = box.row()

        row.operator("anima_toolbox.render_set_image_texture_nodes_to_srgb", text="set to sRGB")
        row.operator("anima_toolbox.render_set_image_texture_nodes_to_raw", text="set to RAW")
        split = row.split(factor=0.10, align=True)
        split.separator()


class SetImageTextureNodesTosRGB(Operator):
    bl_idname = "anima_toolbox.render_set_image_texture_nodes_to_srgb"
    bl_label = "set to sRGB"
    bl_description = "Sets the selected Image Texture nodes color space attribute to sRGB"

    def execute(self, context):
        from anima.env.blender import auxiliary
        r = auxiliary.Render()
        r.set_selected_image_texture_nodes_to_srgb()
        return {'FINISHED'}


class SetImageTextureNodesToRAW(Operator):
    bl_idname = "anima_toolbox.render_set_image_texture_nodes_to_raw"
    bl_label = "set to RAW"
    bl_description = "Sets the selected Image Texture nodes color space attribute to RAW"

    def execute(self, context):
        from anima.env.blender import auxiliary
        r = auxiliary.Render()
        r.set_selected_image_texture_nodes_to_raw()
        return {'FINISHED'}

