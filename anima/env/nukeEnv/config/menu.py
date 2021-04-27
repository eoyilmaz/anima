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
    "Pipeline/Version Dialog",
    """from anima.ui.scripts import nuke_ui as nuke_ui;nuke_ui.version_dialog();"""
)
m.addCommand('Pipeline/Create\/Update Output Nodes', 'from anima.env.nukeEnv import auxiliary; auxiliary.update_outputs()')
# m.addCommand('Pipeline/Package Script', 'import packageScript; packageScript.Package_Proj();')
# m.addCommand('Pipeline/Open Nodes in Browser', 'import pipeline; pipeline.open_selected_nodes_in_file_browser();')


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
