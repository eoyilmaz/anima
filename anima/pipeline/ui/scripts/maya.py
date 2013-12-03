# -*- coding: utf-8 -*-
# Copyright (c) 2012-2013, Anima Istanbul
#
# This module is part of anima-tools and is released under the BSD 2
# License: http://www.opensource.org/licenses/BSD-2-Clause


class UI(object):
    """helper class that has all the methods to display the UI
    """

    @classmethod
    def pyqt(cls):
        """runs the ui with PyQt4

        :return:
        """
        pass

    @classmethod
    def pyside(cls):
        """runs the ui with PySide

        :return:
        """
        pass

    @classmethod
    def _show(cls):
        """the common part for both PyQt4 and PySide

        :return:
        """
        pass
