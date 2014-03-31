# -*- coding: utf-8 -*-
# Copyright (c) 2012-2014, Anima Istanbul
#
# This module is part of anima-tools and is released under the BSD 2
# License: http://www.opensource.org/licenses/BSD-2-Clause
"""Module for generic Maya PyMel extensions through anima.extension module
"""

from pymel.core.uitypes import CheckBox, TextField
from pymel.core.general import Attribute
from anima.extension import extends


class MayaExtension(object):
    """Extension to PyMel classes
    """

    @extends(Attribute)
    @property
    def next_available(self):
        """returns the next available attr in a multi attr

        :return: The available index as an attribute
        """
        try:
            indices = self.getArrayIndices()
        except TypeError:
            return self

        available_index = 0

        try:
            for i in xrange(max(indices) + 2):
                if not self[i].connections():
                    available_index = i
                    break
        except ValueError:
            available_index = 0

        return self[available_index]

    @extends(CheckBox)
    def value(self, value=None):
        """returns or set the check box value
        """
        from pymel.core import checkBox
        if value is not None:
            # set the value
            checkBox(self, e=1, v=value)
        else:
            # get the value
            return checkBox(self, q=1, v=1)

    @extends(TextField)
    def text(self, value=None):
        """returns or sets the text field value
        """
        from pymel.core import textField
        if value is not None:
            # set the value
            textField(self, e=1, tx=value)
        else:
            # get the value
            return textField(self, q=1, tx=1)
