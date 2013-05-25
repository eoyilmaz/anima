# -*- coding: utf-8 -*-
# Copyright (c) 2009-2012, Erkan Ozgur Yilmaz
# 
# This module is part of oyProjectManager and is released under the BSD 2
# License: http://www.opensource.org/licenses/BSD-2-Clause

import os

from PySide.scripts import uic

import subprocess

global uicFile
global pyFile

uicFilePaths = []
pyFilePaths_PyQt4 = []
pyFilePaths_PySide = []

path = os.path.dirname(__file__)
ui_path = os.path.join(path, "ui")

## version_creator
# uicFilePaths.append(os.path.join(ui_path, "ui/version_creator.ui"))
# pyFilePaths_PyQt4.append(os.path.join(ui_path, "version_creator_UI_pyqt4.py"))
# pyFilePaths_PySide.append(os.path.join(ui_path, "version_creator_UI_pyside.py"))

## project_manager
#uicFilePaths.append(os.path.join(ui_path, "project_manager.ui"))
#pyFilePaths_PyQt4.append(os.path.join(ui_path, "project_manager_UI_pyqt4.py"))
#pyFilePaths_PySide.append(os.path.join(ui_path, "project_manager_UI_pyside.py"))

# project_properties
#uicFilePaths.append(os.path.join(ui_path, "project_properties.ui"))
#pyFilePaths_PyQt4.append(os.path.join(ui_path, "project_properties_UI_pyqt4.py"))
#pyFilePaths_PySide.append(os.path.join(ui_path, "project_properties_UI_pyside.py"))

# version_updater
#uicFilePaths.append(os.path.join(ui_path, "version_updater.ui"))
#pyFilePaths_PyQt4.append(os.path.join(ui_path, "version_updater_UI_pyqt4.py"))
#pyFilePaths_PySide.append(os.path.join(ui_path, "version_updater_UI_pyside.py"))

# shot_editor
#uicFilePaths.append(os.path.join(ui_path, "shot_editor.ui"))
#pyFilePaths_PyQt4.append(os.path.join(ui_path, "shot_editor_UI_pyqt4.py"))
#pyFilePaths_PySide.append(os.path.join(ui_path, "shot_editor_UI_pyside.py"))

# version_replacer
#uicFilePaths.append(os.path.join(ui_path, "version_replacer.ui"))
#pyFilePaths_PyQt4.append(os.path.join(ui_path, "version_replacer_UI_pyqt4.py"))
#pyFilePaths_PySide.append(os.path.join(ui_path, "version_replacer_UI_pyside.py"))

# create_asset_dialog
#uicFilePaths.append(os.path.join(ui_path, "create_asset_dialog.ui"))
#pyFilePaths_PyQt4.append(os.path.join(ui_path, "create_asset_dialog_UI_pyqt4.py"))
#pyFilePaths_PySide.append(os.path.join(ui_path, "create_asset_dialog_UI_pyside.py"))

## status_manager
#uicFilePaths.append(os.path.join(ui_path, "status_manager.ui"))
#pyFilePaths_PyQt4.append(os.path.join(ui_path, "status_manager_UI_pyqt4.py"))
#pyFilePaths_PySide.append(os.path.join(ui_path, "status_manager_UI_pyside.py"))

for i,uicFilePath in enumerate(uicFilePaths):
    
    pyFilePath_PyQt4 = pyFilePaths_PyQt4[i]
    pyFilePath_PySide = pyFilePaths_PySide[i]
    
    # with PySide
    # call the external pyside-uic tool
    print "compiling %s to %s for PySide" % (uicFilePath, pyFilePath_PySide)
    subprocess.call(["pyside-uic", "-o", pyFilePath_PySide, uicFilePath])
    
    # with PyQt4
    uicFile = file(uicFilePath)
    pyFile  = file(pyFilePath_PyQt4,'w')
    
    print "compiling %s to %s for PyQt4" % (uicFilePath, pyFilePath_PyQt4)
    
    uic.compileUi( uicFile, pyFile )
    uicFile.close()
    pyFile.close()    

print "finished compiling"
