__author__ = 'Morteza'
#Bu sinif dictionary ve node name i alir ve network node u olusturur.
#network node un connectionlari geri dondurur
#objeleri siler
#vs.. vs..
import pymel.core as pm
class Network(object):
    def __init__(self, name):
        self._name = name
        self._connections = []

        self._createNetwork()

    def __del__(self):
        pass

    def _createNetwork(self):
        #it creates a network node
        pass

    def _createNetwork(self):
        """creates a networkNode. This node holds all the limb nodes
        """
        #creates a networkNode. This node holds all the maya nodes
        self._name = self._name + "_Network"
        pm.createNode("network", n= self.name)



    def attach(self, object):
        #it connects the given object to the network and return an id number for the object
        #all_cons = pm.listConnections(self.name)
        if object in self.connections:
            print ("the %s is already connected to network", object)
        else:
            print "eda"
            mayaCon = object + ('.message')
            networkId = len(self.connections)
            tempAttr = '%s[%s]' % ("affectedBy", networkId)
            networkCon = self.name + "." + tempAttr
            pm.connectAttr(mayaCon, networkCon)
            self.connections.append(object)



    def remove(self, object):
        #it removes the given object from a network
        pass
    def select(self):
        pass

    #****************************************************************************************************#

    # returns and sets the _zeroGrp value
    def name():
        def fget(self):
            return self._name
        def fset(self, name):
            self._name = name
        return locals()
    name = property( **name() )

    def connections():
        def fget(self):
            return self._connections
        return locals()

    connections = property( **connections() )


#****************************************************************************************************#

