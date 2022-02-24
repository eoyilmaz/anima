# -*- coding: utf-8 -*-

from bpy.types import Panel


class Main_Panel(Panel):
    bl_idname = "ANIMA_TOOLBOX_PT_Main"
    bl_label = "Anima Toolbox"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Anima'
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        """draws the ui
        """
        pass
