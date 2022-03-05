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
    if not pm.pluginInfo(plugin_name, q=1, loaded=1):
        start_time = time.time()
        logprint("loading %s!" % plugin_name)
        pm.loadPlugin(plugin_name)
        end_time = time.time()
        duration = end_time - start_time
        logprint("%s loaded! in %0.3f sec" % (plugin_name, duration))


def __plugin_unloader(plugin_name):
    if not pm.pluginInfo(plugin_name, q=1, loaded=1):
        logprint("unloading %s!" % plugin_name)
        pm.unloadPlugin(plugin_name)
        logprint("%s unloaded!" % plugin_name)


# set ui to PySide2 for maya2017 and up
if pymel.versions.current() > 201651:
    logprint("setting QtLib to PySide2 inside userSetup.py")
    from anima import ui

    ui.SET_PYSIDE2()
    logprint("successfully set QtLib to PySide2 inside userSetup.py")
else:
    logprint("setting QtLib to PySide inside userSetup.py")
    from anima import ui

    ui.SET_PYSIDE()
    logprint("successfully QtLib to PySide inside userSetup.py")

if not pm.general.about(batch=1):
    # load shelves
    # DO NOT DELETE THE FOLLOWING LINE
    from anima.dcc.mayaEnv import auxiliary

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
                    'auxiliary.delete_shelf_tab("%s", confirm=False)' % shelf_name
                )
                pm.evalDeferred('auxiliary.load_shelf_tab("%s")' % shelf_path)
    else:
        logprint("no **%s** env var for shelves" % custom_shelves_env_var_name)

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
        # mayautils.executeDeferred(__plugin_loader, 'gpuCache')
        mayautils.executeDeferred(__plugin_loader, "objExport")
        # mayautils.executeDeferred(__plugin_loader, 'closestPointOnCurve.py')
        # mayautils.executeDeferred(__plugin_loader, 'fbxmaya')
        # mayautils.executeDeferred(__plugin_loader, 'OpenEXRLoader')
        # mayautils.executeDeferred(__plugin_loader, 'tiffFloatReader')
        mayautils.executeDeferred(__plugin_loader, "MayaScanner")
        mayautils.executeDeferred(__plugin_loader, "MayaScannerCB")
    else:
        logprint("ANIMA_TEST_SETUP detected, skipping auto plugin loads!")

# set CMD_EXTENSION for Afanasy
# os.environ['AF_CMDEXTENSION'] = pm.about(v=1)

pm.evalDeferred("from anima.dcc import mayaEnv; mayaEnv.Maya.clean_malware();")

# create environment variables for each Repository
pm.evalDeferred("from anima import utils; utils.do_db_setup();")

user_setup_end = time.time()
user_setup_duration = user_setup_end - user_setup_start
logprint("UserSetup.py run in %0.3f sec" % user_setup_duration)
