# -*- coding: utf-8 -*-
# Copyright (c) 2012-2015, Anima Istanbul
#
# This module is part of anima-tools and is released under the BSD 2
# License: http://www.opensource.org/licenses/BSD-2-Clause

import sys
import os
import traceback
import maya.cmds as cmds

__version__ = "1.0.0"

# ----------------------------------------------------------------------------
# add environment variables relative to this path
here = ""
try:
    here = os.path.dirname(__file__)
except NameError as e:
    tb = traceback.extract_tb(sys.exc_info()[2])
    here = tb[0][0]

env_paths = [
    '../../../',
    '../../../mayaEnv',
    '../../../mayaEnv/config',
    '../../../mayaEnv/config/%s' % cmds.about(v=1),
    '../../../mayaEnv/plugins'
]

for path in env_paths:
    resolved_path = os.path.normpath(
        os.path.join(here, path)
    )

    print('appending : %s' % resolved_path)
    sys.path.append(resolved_path)

# add path from os.environ['PYTHONPATH']
for path in os.environ['PYTHONPATH'].split(os.path.pathsep):
    path = os.path.normpath(path)
    if path not in os.sys.path:
        os.sys.path.append(path)

# now we can import pymel and others
import pymel
import pymel.core as pm
from pymel import mayautils
# import maya.cmds as cmds

try:
    pm.Mel.source("HKLocalTools")
except pm.MelError:
    pass


def __pluginLoader(pluginName):
    if not pm.pluginInfo(pluginName, q=1, loaded=1):
        pm.loadPlugin(pluginName)


def __pluginUnloader(pluginName):
    if not pm.pluginInfo(pluginName, q=1, loaded=1):
        pm.unloadPlugin(pluginName)


if 'ANIMA_TEST_SETUP' not in os.environ.keys():
    #
    __pluginUnloader('Mayatomr')
    __pluginLoader('objExport')
    __pluginLoader('closestPointOnCurve.py')
    __pluginLoader('fbxmaya')
    __pluginLoader('OpenEXRLoader')
    __pluginLoader('tiffFloatReader')
    __pluginLoader('tiffFloatReader')

    def load_arnold():
        __pluginLoader('mtoa')

        # create defaultArnoldRenderOptions
        # to disable autotx
        # TODO: Make this beautiful
        if int(pm.about(v=1)) > 2014:
            try:
                pm.PyNode('defaultArnoldRenderOptions')
            except pm.MayaNodeError:
                pm.createNode(
                    'aiOptions',
                    name='defaultArnoldRenderOptions'
                )
            finally:
                daro = pm.PyNode('defaultArnoldRenderOptions')
                try:
                    daro.setAttr("autotx", 0)
                except AttributeError:  # Maya2014
                    pass
            pm.select(None)

    mayautils.executeDeferred(load_arnold)
    mayautils.executeDeferred(__pluginLoader, 'AbcExport')
    mayautils.executeDeferred(__pluginLoader, 'AbcImport')
    mayautils.executeDeferred(__pluginLoader, 'gpuCache')


# set the optionVar that enables hidden mentalray shaders
if pymel.versions.current() <= pymel.versions.v2012:
    pm.optionVar['MIP_SHD_EXPOSE'] = 1
    pm.runtime.SavePreferences()


# Change the default camera to Alexa
try:
    persp = pm.PyNode("persp")
    perspShape = persp.getShape()

    perspShape.horizontalFilmAperture.set(23.76/25.4)
    perspShape.verticalFilmAperture.set(13.365/25.4)
except pm.MayaNodeError:
    pass

# create environment variables for each Repository
from stalker import db
db.setup()

# set ui to PySide2 for maya2017
if pymel.versions.current() > 201500:
    print('setting QtLib to PySide2 inside userSetup.py')
    from anima import ui
    ui.SET_PYSIDE2()
else:
    print('setting QtLib to PySide inside userSetup.py')
    from anima import ui
    ui.SET_PYSIDE()


if not pm.general.about(batch=1):
    # load shelves
    # DO NOT DELETE THE FOLLOWING LINE
    from anima.env.mayaEnv import auxiliary

    custom_shelves_env_var_name = 'ANIMA_MAYA_SHELVES_PATH'
    if custom_shelves_env_var_name in os.environ:
        print(
            '**%s**: %s' % (
                custom_shelves_env_var_name,
                os.environ[custom_shelves_env_var_name]
            )
        )
        shelves_paths = \
            os.environ[custom_shelves_env_var_name].split(os.path.pathsep)

        for shelves_path in shelves_paths:
            print('current shelves_path: %s' % shelves_path)
            import glob

            shelf_paths = glob.glob('%s/shelf_*.mel' % shelves_path)
            print('shelf_paths: %s' % shelf_paths)
            for shelf_path in shelf_paths:
                shelf_path = shelf_path.replace('\\', '/')
                print('loading shelf: %s' % shelf_path)
                shelf_name = os.path.splitext(os.path.basename(shelf_path))[0][6:]
                pm.evalDeferred('auxiliary.delete_shelf_tab("%s", confirm=False)' % shelf_name)
                pm.evalDeferred('auxiliary.load_shelf_tab("%s")' % shelf_path)
    else:
        print('no **%s** env var for shelves' % custom_shelves_env_var_name)

    # patch auto-tx option in arnold for Maya 2017
    if pymel.versions.current() >= 201700:
        from anima.env.mayaEnv.config import arnold_patches
        from mtoa.ui.globals import settings
        settings.createArnoldTextureSettings = \
            arnold_patches.createArnoldTextureSettings
