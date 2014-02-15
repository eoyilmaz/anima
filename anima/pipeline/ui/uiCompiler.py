#!../../../../bin/python
# -*- coding: utf-8 -*-
# Copyright (c) 2012-2014, Anima Istanbul
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

logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)


class UIFile(object):
    """a simple class to manage *.ui files
    """

    def __init__(self, full_path):
        self.filename = ''
        self.path = ''
        self.md5_filename = ''
        self.md5_file_full_path = ''
        self.pyqt4_filename = ''
        self.pyqt4_full_path = ''
        self.pyside_filename = ''
        self.pyside_full_path = ''
        self.full_path = self._validate_full_path(full_path)
        self.md5 = self.generate_md5()

    def generate_md5(self):
        """generates the md5 checksum of the UI file
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
        if full_path == '' or full_path is None:
            raise TypeError('UIFile.full_path can not be None or empty '
                            'string')

        # update filename
        self.filename = os.path.basename(full_path)
        self.path = os.path.dirname(full_path)
        base_name = os.path.splitext(self.filename)[0]
        self.md5_filename = base_name + '.md5'
        self.md5_file_full_path = os.path.join(
            self.path, self.md5_filename
        )
        self.pyqt4_filename = base_name + '_UI_pyqt4.py'
        self.pyqt4_full_path = os.path.normpath(
            os.path.join(self.path, '../ui_compiled', self.pyqt4_filename)
        )
        self.pyside_filename = base_name + '_UI_pyside.py'
        self.pyside_full_path = os.path.normpath(
            os.path.join(self.path, '../ui_compiled', self.pyside_filename)
        )
        return full_path

if __name__ == '__main__':
    # scan for the ui_files directory *.ui files
    uiFiles = []

    args = sys.argv[1:]

    path = os.path.dirname(__file__)
    ui_path = os.path.join(path, "ui_files")

    for ui_file in glob.glob1(ui_path, '*.ui'):
        full_path = os.path.join(ui_path, ui_file)
        uiFiles.append(
            UIFile(full_path)
        )

    from PyQt4 import uic

    for uiFile in uiFiles:
        # if there are already files compare the md5 checksum
        # and decide if it needs to be compiled again
        assert isinstance(uiFile, UIFile)
        if uiFile.isNew():
            # just save the md5 and generate the modules
            uiFile.update_md5_file()

            # with PySide
            # call the external pyside-uic tool
            print "compiling %s to %s for PySide" % (uiFile.filename,
                                                     uiFile.pyside_filename)
            subprocess.call(["pyside-uic", "-o", uiFile.pyside_full_path,
                             uiFile.full_path])

            # with PyQt4d
            temp_uiFile = file(uiFile.full_path)
            temp_pyqt4_file = file(uiFile.pyqt4_full_path, 'w')

            print "compiling %s to %s for PyQt4" % (uiFile.filename,
                                                    uiFile.pyqt4_filename)

            uic.compileUi(temp_uiFile, temp_pyqt4_file)
            temp_uiFile.close()
            temp_pyqt4_file.close()
        #else:
        #    #print '%s is not changed' % uiFile.full_path

    print "finished compiling"
