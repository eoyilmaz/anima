#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2012-2013, Anima Istanbul
#
# This module is part of anima-tools and is released under the BSD 2
# License: http://www.opensource.org/licenses/BSD-2-Clause
"""This is a utility module which helps finding and compiling uic files using
the system python.
"""

import os
import subprocess
import glob
import logging


from PyQt4 import uic


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

if __name__ == '__main__':
    # scan for the ui_files directory *.ui files
    uicFilePaths = []
    pyFilePaths_PyQt4 = []
    pyFilePaths_PySide = []

    path = os.path.dirname(__file__)
    ui_path = os.path.join(path, "ui_files")
    
    print 'path    : %s' % path
    print 'ui_path : %s' % ui_path

    for ui_file in glob.glob1(ui_path, '*.ui'):
        uicFilePaths.append(os.path.join(ui_path, ui_file))
        # create the PyQt4 file
        base_name = os.path.splitext(ui_file)[0]
        pyFilePaths_PyQt4.append(
            os.path.join(
                path,
                'ui_compiled',
                base_name + '_UI_pyqt4.py'
            )
        )
        pyFilePaths_PySide.append(
            os.path.join(
                path,
                'ui_compiled',
                base_name + '_UI_pyside.py'
            )
        )

    print '----------'
    print uicFilePaths
    print pyFilePaths_PyQt4
    print pyFilePaths_PySide
    
    
    for i,uicFilePath in enumerate(uicFilePaths):
        
        pyFilePath_PyQt4 = pyFilePaths_PyQt4[i]
        pyFilePath_PySide = pyFilePaths_PySide[i]
        
        # with PySide
        # call the external pyside-uic tool
        print "compiling %s to %s for PySide" % (uicFilePath, pyFilePath_PySide)
        subprocess.call(["pyside-uic", "-o", pyFilePath_PySide, uicFilePath])
        
        # with PyQt4
        uicFile = file(uicFilePath)
        pyFile  = file(pyFilePath_PyQt4, 'w')
        
        print "compiling %s to %s for PyQt4" % (uicFilePath, pyFilePath_PyQt4)
        
        uic.compileUi( uicFile, pyFile )
        uicFile.close()
        pyFile.close()    
    
    print "finished compiling"
