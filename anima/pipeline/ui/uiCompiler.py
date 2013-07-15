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
import sys
import subprocess
import glob
import logging

from anima.pipeline import utils

from PyQt4 import uic


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)



class UICFile(object):
    """a simple class to manage UICFiles
    """

    def __init__(self, full_path):
        self.filename = ''
        self.path = ''
        self.md5_filename = ''
        self.md5_file_full_path = ''
        self.full_path = self._validate_full_path(full_path)
        self.md5 = self.generate_md5()

    def generate_md5(self):
        """generates the md5 checksum of the UIC file
        """
        return utils.md5_checksum(self.full_path)

    def update_md5_file(self):
        """saves the md5 checksum to a file
        """
        # write down the md5 checksum to the file
        with open(self.md5_file_full_path, 'w+') as f:
            f.writelines([self.md5])

    def isNew(self):
        """checks if the file is new or old by comparing it with the stored md5
        file
        """
        try:
            logger.debug('checking md5 file')
            with open(self.md5_file_full_path) as f:
                md5 = f.readline()
            logger.debug('md5: %s' % md5)
            return md5 != self.md5
        except IOError:
            logger.debug('no md5 file')
            return True

    def _validate_full_path(self, full_path):
        """validates the given full_path
        """
        # update filename
        self.filename = os.path.basename(full_path)
        self.path = os.path.dirname(full_path)
        self.md5_filename = os.path.splitext(self.filename)[0] + '.md5'
        self.md5_file_full_path = os.path.join(
            self.path, self.md5_filename
        )

        return full_path



if __name__ == '__main__':
    # scan for the ui_files directory *.ui files
    uicFilePaths = []
    pyFilePaths_PyQt4 = []
    pyFilePaths_PySide = []

    args = sys.argv[1:]

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

    for i, uicFilePath in enumerate(uicFilePaths):
        pyFilePath_PyQt4 = pyFilePaths_PyQt4[i]
        pyFilePath_PySide = pyFilePaths_PySide[i]

        # if there are already files compare the md5 checksum
        # and decide if it needs to be compiled again
        if os.path.exists(uicFilePath):
            # generate md5 checksum for files
            md5_checksum = utils.md5_checksum(uicFilePath)
            # get the stored checksum
            md5_checksum_file_path = os.path.splitext(uicFilePath)[0] + '.md5'
            

        # with PySide
        # call the external pyside-uic tool
        print "compiling %s to %s for PySide" % (
        uicFilePath, pyFilePath_PySide)
        subprocess.call(["pyside-uic", "-o", pyFilePath_PySide, uicFilePath])

        # with PyQt4
        uicFile = file(uicFilePath)
        pyFile = file(pyFilePath_PyQt4, 'w')

        print "compiling %s to %s for PyQt4" % (uicFilePath, pyFilePath_PyQt4)

        uic.compileUi(uicFile, pyFile)
        uicFile.close()
        pyFile.close()

    print "finished compiling"
