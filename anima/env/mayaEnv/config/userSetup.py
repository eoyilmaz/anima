# -*- coding: utf-8 -*-
# Copyright (c) 2012-2014, Anima Istanbul
#
# This module is part of anima-tools and is released under the BSD 2
# License: http://www.opensource.org/licenses/BSD-2-Clause

import os
import sys
import platform
import traceback

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
    '../../../mayaEnv/config/2014',
    '../../../mayaEnv/plugins'
]

for path in env_paths:
    resolved_path = os.path.normpath(
        os.path.join(here, path)
    )
    sys.path.append(resolved_path)

# now we can import pymel and others
import pymel
import pymel.core as pm
import maya.cmds as cmds

from stalker import db
from anima.env import create_repo_vars
from anima.env.mayaEnv import auxiliary

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


__pluginUnloader('Mayatomr')
__pluginLoader('objExport')
__pluginLoader('closestPointOnCurve.py')
__pluginLoader('fbxmaya')
__pluginLoader('OpenEXRLoader')
__pluginLoader('tiffFloatReader')


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


db.setup()
create_repo_vars()

if not pm.general.about(batch=1):
    # load shelves
    shelves_path = '../../../../shelves'
    shelf_names = ['kks_Tools', 'kks_Animation']

    for shelf_name in shelf_names:
        shelf_path = os.path.normpath(
            os.path.join(here, shelves_path, 'shelf_%s.mel' % shelf_name)
        ).replace('\\', '/')

        pm.evalDeferred('auxiliary.delete_shelf_tab("%s", confirm=False)' % shelf_name)
        pm.evalDeferred('auxiliary.load_shelf_tab("%s")' % shelf_path)

        print('shelf_path: %s' % shelf_path)
