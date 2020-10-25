# -*- coding: utf-8 -*-
# Copyright (c) 2012-2020, Erkan Ozgur Yilmaz
#
# This module is part of anima and is released under the MIT
# License: http://www.opensource.org/licenses/MIT


from bpy.types import Panel


class Main_Panel(Panel):
    bl_idname = "ANIMA_TOOLBOX_PT_Main"
    bl_label = "Anima Toolbox"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'View'
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        """draws the ui
        """
        # layout = self.layout
        # scene = context.scene
        #
        # box = layout.box()
        # row = box.row()
        # if context.window_manager.measureit_run_opengl is False:
        #     icon = 'PLAY'
        #     txt = 'Show'
        # else:
        #     icon = "PAUSE"
        #     txt = 'Hide'
        pass