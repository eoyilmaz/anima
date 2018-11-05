#!../../../bin/python
# -*- coding: utf-8 -*-
# Copyright (c) 2012-2018, Anima Istanbul
#
# This module is part of anima-tools and is released under the BSD 2
# License: http://www.opensource.org/licenses/BSD-2-Clause
"""This is a utility module which helps finding and compiling uic files using
the system python.
"""

import os
import glob

from anima import utils, logger


# PyQt4
try:
    from PyQt4.uic import compileUi as pyqt4_compileUi
    pyqt4_compiler = pyqt4_compileUi
except ImportError:
    pyqt4_compiler = None

# PySide
try:
    from pysideuic import compileUi as pyside_compileUi
    pyside_compiler = pyside_compileUi
except ImportError:
    pyside_compiler = None

# PySide2
try:
    from pyside2uic import compileUi as pyside2_compileUi
    pyside2_compiler = pyside2_compileUi
except ImportError:
    pyside2_compiler = None


compiler_config = {
    'pyqt4': {
        'compiler': pyqt4_compiler,
        'postfix': '_UI_pyqt4.py'
    },
    'pyside': {
        'compiler': pyside_compiler,
        'postfix': '_UI_pyside.py',
    },
    'pyside2': {
        'compiler': pyside2_compiler,
        'postfix': '_UI_pyside2.py'
    }
}


class Compiler(object):
    """compiler
    """

    def __init__(self, name=None, compiler=None, postfix=None):
        self.name = name
        self.compiler = compiler
        self.postfix = postfix

    def get_py_file_name(self, ui_file_name):
        """returns the corresponding py file name from ui_file_name
        """
        return '%s%s' % (
            os.path.splitext(os.path.basename(ui_file_name))[0],
            self.postfix
        )

    def get_py_file(self, ui_file, path):
        """returns the corresponding py file
        """
        py_file_name = self.get_py_file_name(ui_file.full_path)
        return PyFile(py_file_name, path)

    def compile(self, ui_file, output_path):
        if self.compiler:
            py_file_full_path = os.path.join(
                output_path,
                self.get_py_file_name(ui_file.full_path)
            )

            temp_ui_file = file(ui_file.full_path)
            temp_py_file = file(py_file_full_path, 'w')
            try:
                self.compiler(temp_ui_file, temp_py_file)
            except TypeError:
                pass
            finally:
                temp_ui_file.close()
                temp_py_file.close()
        else:
            raise RuntimeError('No Compiler!')


class CompilerManager(object):
    """
    """

    def __init__(self):
        self.compilers = []
        self._generate_compilers_()

    def _generate_compilers_(self):
        # generate compilers
        for key, value in compiler_config.items():
            name = key
            compiler = value['compiler']
            postfix = value['postfix']

            self.compilers.append(
                Compiler(name=name, compiler=compiler, postfix=postfix)
            )

    def find_compiler(self, name):
        for c in self.compilers:
            if c.name.lower() == name.lower():
                return c


class UIFile(object):
    """a simple class to manage *.ui files
    """

    def __init__(self, full_path):
        self.filename = ''
        self.path = ''
        self.md5_filename = ''
        self.md5_file_full_path = ''

        self.full_path = self._validate_full_path(full_path)
        self.md5 = self.generate_md5()

    def generate_md5(self):
        """generates the md5 checksum of the UI file
        """
        return utils.md5_checksum(self.full_path).replace('\n', '')

    def update_md5_file(self):
        """saves the md5 checksum to a file
        """
        # write down the md5 checksum to the file
        with open(self.md5_file_full_path, 'w+') as f:
            f.writelines([self.md5])

    def is_new(self):
        """checks if the file is new or old by comparing it with the stored md5
        file
        """
        try:
            logger.debug('checking md5 file')
            with open(self.md5_file_full_path) as f:
                md5 = f.readline()
            logger.debug('md5     : %s' % md5)
            logger.debug('self.md5: %s' % self.md5)
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

        return full_path


class PyFile(object):
    """PyFile the compiled *.py file
    """

    def __init__(self, filename, path):
        self.filename = filename
        self.path = path

    @property
    def full_path(self):
        """returns the full path
        """
        return os.path.join(self.path, self.filename)

    def exists(self):
        return os.path.exists(self.full_path)


def main():
    """the main procedure
    """
    # generate compilers
    manager = CompilerManager()
    compiler_pyqt4 = manager.find_compiler('PyQt4')
    compiler_pyside = manager.find_compiler('PySide')
    compiler_pyside2 = manager.find_compiler('PySide2')

    # scan for the ui_files directory *.ui files
    ui_files = []

    path = os.path.dirname(__file__)
    ui_path = os.path.join(path, "ui_files")
    output_path = os.path.join(path, 'ui_compiled')

    for ui_file in glob.glob1(ui_path, '*.ui'):
        full_path = os.path.join(ui_path, ui_file)
        ui_files.append(
            UIFile(full_path)
        )

    for ui_file in ui_files:
        print('--------------------------')
        print('ui_file: %s' % ui_file.filename)
        # if there are already files compare the md5 checksum
        # and decide if it needs to be compiled again
        assert isinstance(ui_file, UIFile)
        py_file_pyqt4 = compiler_pyqt4.get_py_file(ui_file, output_path)
        py_file_pyside = compiler_pyside.get_py_file(ui_file, output_path)
        py_file_pyside2 = compiler_pyside2.get_py_file(ui_file, output_path)

        renew_md5 = False
        print('ui_file.is_new()        : %s' % ui_file.is_new())
        print('py_file_pyqt4.exists()  : %s' % py_file_pyqt4.exists())
        print('py_file_pyside.exists() : %s' % py_file_pyside.exists())
        print('py_file_pyside2.exists(): %s' % py_file_pyside2.exists())

        if ui_file.is_new() or not py_file_pyqt4.exists():
            print('re-compiling PyQt4 version')
            renew_md5 = True
            try:
                compiler_pyqt4.compile(ui_file, output_path)
            except RuntimeError:
                pass

        if ui_file.is_new() or not py_file_pyside.exists():
            print('re-compiling PySide version')
            renew_md5 = True
            try:
                compiler_pyside.compile(ui_file, output_path)
            except RuntimeError:
                pass

        if ui_file.is_new() or not py_file_pyside2.exists():
            print('re-compiling PySide2 version')
            renew_md5 = True
            try:
                compiler_pyside2.compile(ui_file, output_path)
            except RuntimeError:
                pass

        if renew_md5:
            # just save the md5 and generate the modules
            print('Renewing the MD5 file!')
            ui_file.update_md5_file()

    print "Finished compiling"


if __name__ == '__main__':
    main()
