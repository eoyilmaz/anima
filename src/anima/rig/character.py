# -*- coding: utf-8 -*-


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
