# -*- coding: utf-8 -*-
# Copyright (c) 2012-2019, Anima Istanbul
#
# This module is part of anima and is released under the MIT
# License: http://www.opensource.org/licenses/MIT


class Character(object):
    def __init__(self, name):
        self._name = name
        self._setName = ""
        self._mainCtrl = None
        self.limbs = []
        self.nodes = []


        self._network = None
        self._charSet = None



    def __del__(self):
        pass

    @property
    def name(self):
        return self._name
    @name.setter
    def name(self, name_in):
        self._name = name_in


    def createHierarchy(self):
        pass
    def createCharset(self):
        pass
    def createFlow(self):
        pass

