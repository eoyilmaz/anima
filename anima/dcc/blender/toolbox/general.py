# -*- coding: utf-8 -*-

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
        operators = [OpenVersion, SaveAsVersion, VersionUpdater, Playblast, RangeFromShot, FitStencilToView,
                     NudgeStencilToUp, NudgeStencilToDown, NudgeStencilToLeft, NudgeStencilToRight]
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
        version_dialog(mode=1)
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
        version_dialog(mode=0)
        # redraw
        # context.area.tag_redraw()
        return {'FINISHED'}


class VersionUpdater(Operator):
    bl_idname = "anima_toolbox.version_updater"
    bl_label = "Version Updater"
    bl_description = "Updates versions"

    def execute(self, context):
        from anima.ui.scripts.blender import version_updater
        version_updater()
        # redraw
        # context.area.tag_redraw()
        return {'FINISHED'}


class Playblast(Operator):
    bl_idname = "anima_toolbox.general_playblast"
    bl_label = "Playblast"
    bl_description = "Create a playblast"
    # bl_icon = "CAMERA_DATA"

    def execute(self, context):
        from anima.dcc import blender
        bl = blender.Blender()
        bl.viewport_render_animation(context)
        # redraw
        # context.area.tag_redraw()
        return {'FINISHED'}


class RangeFromShot(Operator):
    bl_idname = "anima.general_range_from_shot"
    bl_label = "Range From Shot"
    bl_description = "Adjust playback range to shot range"

    def execute(self, context):
        from anima.dcc import blender
        bl = blender.Blender()
        version = bl.get_current_version()
        if not version:
            return {'FINISHED'}

        shot = bl.get_shot(version)
        if shot:
            bl.set_frame_range(shot.cut_in, shot.cut_out)

        return {'FINISHED'}


class FitStencilToView(Operator):
    bl_idname = "anima.general_fit_stencil_to_view"
    bl_label = "Fit Stencil To View"
    bl_description = "Fits the stencil to view"

    def execute(self, context):
        """

        :param context:
        :return:
        """
        # get the current camera view size relative to the current view
        # set it to the current brush stencil
        import bpy
        # print("***************************************************")

        brush = bpy.data.brushes['TexDraw']
        stencil_dimension = brush.stencil_dimension
        stencil_pos = brush.stencil_pos

        region = context.region
        region_view_3d = context.region_data
        print("region_view_3d.view_camera_offset   : %s" % region_view_3d.view_camera_offset)
        print("region_view_3d.view_camera_offset[0]: %s" % region_view_3d.view_camera_offset[0])
        print("region_view_3d.view_camera_offset[1]: %s" % region_view_3d.view_camera_offset[1])
        print("region_view_3d.view_camera_zoom     : %s" % region_view_3d.view_camera_zoom)
        print("-------------------")
        print("Estimated goal values:")
        print("stencil_dimension.x                   : %s" % stencil_dimension.x)
        print("stencil_dimension.y                   : %s" % stencil_dimension.y)
        print("stencil_pos.x                         : %s" % stencil_pos.x)
        print("stencil_pos.y                         : %s" % stencil_pos.y)
        print("-------------------")

        bpy.ops.view3d.view_center_camera()

        # make the stencil to use the image aspect
        bpy.ops.brush.stencil_reset_transform()
        bpy.ops.brush.stencil_fit_image_aspect()

        # store the image ratio first
        ratio = stencil_dimension.x / stencil_dimension.y

        # set the width of the stencil to the same size of the region
        stencil_dimension.x = region.width * 0.5 - 3

        # set the height of the image to the correct ratio
        stencil_dimension.y = stencil_dimension.x / ratio

        # center the image horizontally to the region
        stencil_pos.x = stencil_dimension.x + 1

        # center the image vertically to the region
        stencil_pos.y = region.height * 0.5

        # print("context.region.height                 : %s" % region.height)
        # print("context.region.width                  : %s" % region.width)
        # print("stencil_pos.x                         : %s" % stencil_pos.x)
        # print("stencil_pos.y                         : %s" % stencil_pos.y)
        # print("stencil_dimension.x                   : %s" % stencil_dimension.x)
        # print("stencil_dimension.y                   : %s" % stencil_dimension.y)

        return {'FINISHED'}


class NudgeStencilToLeft(Operator):
    bl_idname = "anima.general_nudge_stencil_to_left"
    bl_label = "Nudge Stencil To Left"
    bl_description = "Nudges the stencil 1 pixel to left"

    def execute(self, context):
        """
        :param context:
        :return:
        """
        import bpy
        brush = bpy.data.brushes['TexDraw']
        stencil_pos = brush.stencil_pos
        stencil_pos.x -= 1
        return {'FINISHED'}


class NudgeStencilToRight(Operator):
    bl_idname = "anima.general_nudge_stencil_to_right"
    bl_label = "Nudge Stencil To Right"
    bl_description = "Nudges the stencil 1 pixel to right"

    def execute(self, context):
        """
        :param context:
        :return:
        """
        import bpy
        brush = bpy.data.brushes['TexDraw']
        stencil_pos = brush.stencil_pos
        stencil_pos.x += 1
        return {'FINISHED'}


class NudgeStencilToUp(Operator):
    bl_idname = "anima.general_nudge_stencil_to_up"
    bl_label = "Nudge Stencil To Up"
    bl_description = "Nudges the stencil 1 pixel to up"

    def execute(self, context):
        """
        :param context:
        :return:
        """
        import bpy
        brush = bpy.data.brushes['TexDraw']
        stencil_pos = brush.stencil_pos
        stencil_pos.y += 1
        return {'FINISHED'}


class NudgeStencilToDown(Operator):
    bl_idname = "anima.general_nudge_stencil_to_down"
    bl_label = "Nudge Stencil To Down"
    bl_description = "Nudges the stencil 1 pixel to Down"

    def execute(self, context):
        """
        :param context:
        :return:
        """
        import bpy
        brush = bpy.data.brushes['TexDraw']
        stencil_pos = brush.stencil_pos
        stencil_pos.y -= 1
        return {'FINISHED'}
