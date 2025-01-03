# -*- coding: utf-8 -*-

import sys
import os
import traceback
import time
import maya.cmds as cmds


user_setup_start = time.time()


def logprint(log):
    """wrapper for printing data inside userSetup.py

    :param log: The string to print
    :return:
    """
    print("userSetup.py: %s" % log)


# ----------------------------------------------------------------------------
# add environment variables relative to this path
here = ""
try:
    here = os.path.dirname(__file__)
except NameError as e:
    tb = traceback.extract_tb(sys.exc_info()[2])
    here = tb[0][0]

env_paths = [
    "../../../",
    "../../../mayaEnv",
    "../../../mayaEnv/config",
    "../../../mayaEnv/config/%s" % cmds.about(v=1),
    "../../../mayaEnv/plugins" "../../../mayaEnv/plugins/%s" % cmds.about(v=1),
]

for path in env_paths:
    resolved_path = os.path.normpath(os.path.join(here, path))

    logprint("appending : %s" % resolved_path)
    sys.path.append(resolved_path)

# add path from os.environ['PYTHONPATH']
for path in os.environ["PYTHONPATH"].split(os.path.pathsep):
    path = os.path.normpath(path)
    if path not in os.sys.path:
        os.sys.path.append(path)

# now we can import pymel and others
start = time.time()
import pymel
import pymel.core as pm
from pymel import mayautils

end = time.time()
duration = end - start
logprint("pymel loaded in %0.3f sec" % duration)


def __plugin_loader(plugin_name):
    logprint("loading {}!".format(plugin_name))
    if not pm.pluginInfo(plugin_name, q=1, loaded=1):
        start_time = time.time()
        try:
            pm.loadPlugin(plugin_name)
        except RuntimeError:
            logprint("{} not found!".format(plugin_name))
            pass
        else:
            end_time = time.time()
            duration = end_time - start_time
            logprint("%s loaded! in %0.3f sec" % (plugin_name, duration))
    else:
        logprint("Plugin already loaded: {}".format(plugin_name))


def __plugin_unloader(plugin_name):
    logprint("unloading {}!".format(plugin_name))
    if not pm.pluginInfo(plugin_name, q=1, loaded=1):
        pm.unloadPlugin(plugin_name)
        logprint("{} unloaded!".format(plugin_name))
    else:
        logprint("plugin not loaded: {}".format(plugin_name))


if not pm.general.about(batch=1):
    # set progress manager display type
    from anima.utils.progress import ProgressManagerFactory
    pdm = ProgressManagerFactory.get_progress_manager()

    # load shelves
    custom_shelves_env_var_name = "ANIMA_MAYA_SHELVES_PATH"
    if custom_shelves_env_var_name in os.environ:
        logprint(
            "**%s**: %s"
            % (custom_shelves_env_var_name, os.environ[custom_shelves_env_var_name])
        )
        shelves_paths = os.environ[custom_shelves_env_var_name].split(os.path.pathsep)

        for shelves_path in shelves_paths:
            logprint("current shelves_path: %s" % shelves_path)
            import glob

            shelf_paths = glob.glob("%s/shelf_*.mel" % shelves_path)
            logprint("shelf_paths: %s" % shelf_paths)
            for shelf_path in shelf_paths:
                shelf_path = shelf_path.replace("\\", "/")
                logprint("loading shelf: %s" % shelf_path)
                shelf_name = os.path.splitext(os.path.basename(shelf_path))[0][6:]
                pm.evalDeferred(
                    'from anima.dcc.mayaEnv import auxiliary; '
                    'auxiliary.delete_shelf_tab("%s", confirm=False);' % shelf_name
                )
                pm.evalDeferred(
                    'from anima.dcc.mayaEnv import auxiliary; '
                    'auxiliary.load_shelf_tab("%s");' % shelf_path
                )
    else:
        logprint("no **%s** env var for shelves" % custom_shelves_env_var_name)

    def create_menus():
        # add menus
        # delete previous menu
        main_menu_name = "AnimaMenu"
        main_menu_label = "Anima"
        maya_main_window = pm.mel.globals["$gMainWindow"]
        if pm.menu(main_menu_name, exists=1, p=maya_main_window):
            pm.menu(main_menu_name, e=True, deleteAllItems=True)
            pm.deleteUI(main_menu_name)

        pm.menu(main_menu_name, label=main_menu_label, tearOff=True, p=maya_main_window)
        pm.menuItem(label="Open Version",
                    c="from anima.ui.scripts import maya; maya.version_dialog(mode=1);")
        pm.menuItem(label="Save As Version",
                    c="from anima.ui.scripts import maya; maya.version_dialog(mode=0);")
        pm.menuItem(label="Publish",
                    c="from anima.ui.scripts import maya; maya.version_dialog(mode=0);")
        pm.menuItem(divider=True)
        pm.menuItem(label="Toolbox",
                    c="from anima.dcc.mayaEnv import toolbox; toolbox.UI();")

    mayautils.executeDeferred(create_menus)

    # MayaScanner only if Maya is not in batch mode.
    mayautils.executeDeferred(__plugin_loader, "MayaScanner")
    mayautils.executeDeferred(__plugin_loader, "MayaScannerCB")

if "ANIMA_TEST_SETUP" not in os.environ:

    def load_arnold():
        try:
            __plugin_loader("mtoa")

            # patch auto-tx option in arnold for Maya 2017
            if pymel.versions.current() >= 201700:
                from anima.dcc.mayaEnv.config import arnold_patches
                from mtoa.ui.globals import settings

                settings.createArnoldTextureSettings = (
                    arnold_patches.createArnoldTextureSettings
                )

        except RuntimeError:
            pass

    def load_redshift():
        try:
            # For Maya 2020 and RS 3.0.44+ if the XGenToolkit is not loaded Redshift will not load too
            __plugin_loader("xgenToolkit")
            __plugin_loader("redshift4maya")
        except RuntimeError:
            pass

    # mayautils.executeDeferred(load_arnold)
    mayautils.executeDeferred(load_redshift)
    mayautils.executeDeferred(__plugin_loader, "AbcExport")
    mayautils.executeDeferred(__plugin_loader, "AbcImport")
    mayautils.executeDeferred(__plugin_loader, "objExport")
    mayautils.executeDeferred(__plugin_loader, "mayaUsdPlugin")

    # unload bifrost plugins as they are causing render issues on farm
    # the renders don't complete
    def unload_bifrost():
        __plugin_unloader("bifmeshio")
        __plugin_unloader("bifrostGraph")
        __plugin_unloader("bifrostshellnode")
        __plugin_unloader("bifrostvisplugin")
        __plugin_unloader("ArubaTessellator")
        __plugin_unloader("OneClick")

    mayautils.executeDeferred(unload_bifrost)
    mayautils.executeDeferred(__plugin_unloader, "ATFPlugin")
    mayautils.executeDeferred(__plugin_unloader, "stereoCamera")
else:
    logprint("ANIMA_TEST_SETUP detected, skipping auto plugin loads!")

# set CMD_EXTENSION for Afanasy
# os.environ['AF_CMDEXTENSION'] = pm.about(v=1)


def setup_maya_color_management():
    # set color management
    logprint("Setting up Color Management Preferences.")
    # be sure the color management is not set to legacy
    from anima.dcc.mayaEnv.render import MayaColorManagementConfigurator
    MayaColorManagementConfigurator.configure()


pm.evalDeferred("from anima.dcc import mayaEnv; mayaEnv.Maya.clean_malware();")

# create environment variables for each Repository
pm.evalDeferred(
    "from anima import utils; "
    "utils.do_db_setup(); "
    "setup_maya_color_management();"
)

user_setup_end = time.time()
user_setup_duration = user_setup_end - user_setup_start
logprint("UserSetup.py run in %0.3f sec" % user_setup_duration)
