# -*- coding: utf-8 -*-

bl_info = {
    "name": "Anima Toolbox",
    "author": "Erkan Ozgur Yilmaz",
    "location": "View3D > Sidebar > View Tab",
    "version": (1, 0, 0),
    "blender": (2, 80, 0),
    "description": "Anima Toolbox for Blender",
    "doc_url": "{BLENDER_MANUAL_URL}/addons" "/3d_view/anima_toolbox.html",
    "category": "3D View",
}


if "bpy" in locals():
    import importlib

    importlib.reload(toolbox)
    importlib.reload(general)
    importlib.reload(render)
else:
    from anima.dcc.blender import toolbox
    from anima.dcc.blender.toolbox import general, render

# the following import is needed somehow
import bpy


panels = (
    toolbox.Main_Panel,
    general.General,
    render.Render,
)

classes = (
    toolbox.Main_Panel,
    general.General,
    general.OpenVersion,
    general.SaveAsVersion,
    general.VersionUpdater,
    general.Playblast,
    general.RangeFromShot,
    general.FitStencilToView,
    general.NudgeStencilToUp,
    general.NudgeStencilToLeft,
    general.NudgeStencilToRight,
    general.NudgeStencilToDown,
    render.Render,
    render.SetImageTextureNodesToRAW,
    render.SetImageTextureNodesTosRGB,
)


def register():
    from bpy.utils import register_class

    for cls in classes:
        register_class(cls)


def unregister():
    from bpy.utils import unregister_class

    for cls in reversed(classes):
        unregister_class(cls)


if __name__ == "__main__":
    register()
