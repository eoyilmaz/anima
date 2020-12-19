# -*- coding: utf-8 -*-
# Copyright (c) 2012-2020, Erkan Ozgur Yilmaz
#
# This module is part of anima and is released under the MIT
# License: http://www.opensource.org/licenses/MIT


from bpy.types import Panel, Operator


class General(Panel):
    bl_idname = "ANIMA_TOOLBOX_PT_General"
    bl_label = "General"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'View'
    bl_parent_id = 'ANIMA_TOOLBOX_PT_Main'

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        box = layout.box()
        # box.label(text="Box Label")
        operators = [OpenVersion, SaveAsVersion, Playblast]
        for op in operators:
            row = box.row()
            row.operator(op.bl_idname, text=op.bl_label)

        # split = row.split(factor=0.10, align=True)
        # split.separator()


class OpenVersion(Operator):
    bl_idname = "anima_toolbox.general_open_version"
    bl_label = "Open Version"
    bl_description = "Opens Version Dialog in Open mode"
    # bl_icon = "FILE"

    def execute(self, context):
        from anima.ui.scripts.blender import version_dialog
        version_dialog()
        # redraw
        # context.area.tag_redraw()
        return {'FINISHED'}


class SaveAsVersion(Operator):
    bl_idname = "anima_toolbox.general_save_as_version"
    bl_label = "Save As Version"
    bl_description = "Opens Version Dialog in Save mode"
    # bl_icon = "FILE_NEW"

    def execute(self, context):
        from anima.ui.scripts.blender import version_dialog
        version_dialog()
        # redraw
        # context.area.tag_redraw()
        return {'FINISHED'}


class Playblast(Operator):
    bl_idname = "anima_toolbox.general_playblast"
    bl_label = "Playblast"
    bl_description = "Create a playblast"
    # bl_icon = "CAMERA_DATA"

    def execute(self, context):
        from anima.env import blender
        bl = blender.Blender()
        bl.viewport_render_animation(context)
        # redraw
        # context.area.tag_redraw()
        return {'FINISHED'}
