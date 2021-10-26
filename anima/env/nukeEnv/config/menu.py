# -*- coding: utf-8 -*-
# export path for project manager
import os
import sys
# import mari_bridge
import nuke

toolbar = nuke.menu("Nodes")

m = toolbar.addMenu("Anima")

# Pipeline tools
m.addCommand(
    "Pipeline/Open Version",
    """from anima.ui.scripts import nuke_ui as nuke_ui;nuke_ui.version_dialog(1);"""
)
m.addCommand(
    "Pipeline/Save As Version",
    """from anima.ui.scripts import nuke_ui as nuke_ui;nuke_ui.version_dialog(0);"""
)
m.addCommand(
    'Pipeline/Create/Update Output Nodes',
    'from anima.env.nukeEnv import auxiliary; auxiliary.update_outputs()'
)


# Comp tools
# m.addCommand("Comp Tools/create slate", "nuke.createNode('slate')")
# m.addCommand("Comp Tools/oyDefocus", "nuke.createNode('oyDefocus')")
# m.addCommand("Comp Tools/oyTiler", "nuke.createNode('oyTiler')")
# m.addCommand("Comp Tools/labelExtractor", "nuke.createNode('labelExtractor')")
# m.addCommand("Comp Tools/Clean-Up Nodes", "import nodeCleanUp; nodeCleanUp.doCleanUp();", "")
# m.addCommand("Comp Tools/Frame Generator", "nuke.createNode('frameGenerator')")
# m.addCommand("Comp Tools/jdVibrance", "nuke.createNode('jdVibrance')")
# m.addCommand('Comp Tools/gfxAlexa3DLut800.gizmo', 'nuke.createNode("gfxAlexa3DLut800")')
# m.addCommand('Comp Tools/create autocrop writer', 'import oyTools; oyTools.create_auto_crop_writer()')
