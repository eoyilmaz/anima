__author__ = 'Morteza'


class Nodes(object):
    def __init__(self, name):
        self.name = name
        self.outputConnects = []
        self.inputConnections = []
        self.operation = None

    def connectOutput(self):
        pass
    def connectInput(self):
        pass

