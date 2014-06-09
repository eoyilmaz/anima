# -*- coding: utf-8 -*-
"""create deformer with::

  deformer -type "randomizeUVDeformer"

"""
import random

import sys


from maya import OpenMaya, OpenMayaMPx
#from maya.OpenMaya import MItGeometry, MTypeId, MDataBlock
#from maya.OpenMayaMPx import MFnPlugin, MPxDeformerNode, MPxNode, asMPxPtr

node_type_name = "randomizeUVDeformer"
plugin_id = OpenMaya.MTypeId(0x00380)


class RandomizeDeformer(OpenMayaMPx.MPxDeformerNode):
    """a node to randomize uvs (for now)
    """

    def __init__(self):
        OpenMayaMPx.MPxDeformerNode.__init__(self)

    def getDeformerInputGeometry(self, data_block, geometry_index):
        """Obtain a reference to the input mesh. This mesh will be used to
        compute our bounding box, and we will also require its normals.

        We use MDataBlock.outputArrayValue() to avoid having to recompute the
        mesh and propagate this recomputation throughout theDependency Graph.

        OpenMayaMPx.cvar.MPxDeformerNode_input and
        OpenMayaMPx.cvar.MPxDeformerNode_inputGeom are SWIG-generated
        variables which respectively contain references to the deformer's
        'input' attribute and 'inputGeom' attribute.
        """
        input_attribute = OpenMayaMPx.cvar.MPxDeformerNode_input
        input_geometry_attribute = OpenMayaMPx.cvar.MPxDeformerNode_inputGeom

        input_handle = data_block.outputArrayValue(input_attribute)
        input_handle.jumpToElement(geometry_index)
        input_geometry_object =\
            input_handle.outputValue().child(input_geometry_attribute).asMesh()

        return input_geometry_object

    def deform(self, data_block, geometry_iterator, local_to_world_matrix, geometry_index):
        """do deformation
        """
        envelope_attribute = OpenMayaMPx.cvar.MPxDeformerNode_envelope
        envelope_value = data_block.inputValue(envelope_attribute).asFloat()

        input_geometry_object = \
            self.getDeformerInputGeometry(data_block, geometry_index)

        # Obtain the list of normals for each vertex in the mesh.
        mesh_fn = OpenMaya.MFnMesh(input_geometry_object)

        uv_shell_array = OpenMaya.MIntArray()
        u_array = OpenMaya.MFloatArray()
        v_array = OpenMaya.MFloatArray()
        script_util = OpenMaya.MScriptUtil(0)
        # script_util.createFromInt(0)
        shells_ptr = script_util.asUintPtr()

        mesh_fn.getUvShellsIds(uv_shell_array, shells_ptr)
        mesh_fn.getUVs(u_array, v_array)

        div = 4

        uv_dict = {}
        uv_off_dict = {}
        for i in range(u_array.length()):
            if not uv_shell_array[i] in uv_dict:
                uv_off_dict[uv_shell_array[i]] = random.randint(0, (div-1))
                uv_dict[uv_shell_array[i]] = [i]
            else:
                uv_dict[uv_shell_array[i]].append(i)

        sys.stdout.write(str(uv_dict))
        sys.stdout.write('\n')

        cell_offsets = []
        for u in range(0, div):
            cell_offsets.append((float(u), 0.0))

        sys.stdout.write('cell_offsets: ')
        sys.stdout.write(str(cell_offsets))
        sys.stdout.write('\n')

        # compute and write the new uvs
        for i in range(script_util.getUint(shells_ptr)):
            for j in uv_dict[i]:
                u_array.set(cell_offsets[uv_off_dict[i]][0] + u_array[j], j)
                v_array.set(cell_offsets[uv_off_dict[i]][1] + v_array[j], j)

        #sys.stdout.write(str(u_array))
        #sys.stdout.write('\n')
        #sys.stdout.write(str(v_array))

        mesh_fn.setUVs(u_array, v_array)

        uv_shell_array.clear()
        u_array.clear()
        v_array.clear()



        # # Iterate over the vertices to move them.
        # while not geometry_iterator.isDone():
        #     # Obtain the vertex normal of the geometry.
        #     # This normal is the vertex's averaged normal value if that
        #     # vertex is shared among several polygons.
        #     vertex_index = geometry_iterator.index()
        #     normal = OpenMaya.MVector(normals[vertex_index]) # Cast the MFloatVector into a simple vector.
        #
        #     # Increment the point along the vertex normal.
        #     point = geometry_iterator.position()
        #     newPoint = \
        #         point + (normal * vertexIncrement * meshInflation * envelopeValue)
        #
        #     # Clamp the new point within the bounding box.
        #     self.clampPointInBoundingBox(newPoint, boundingBox)
        #
        #     # Set the position of the current vertex to the new point.
        #     geometry_iterator.setPosition(newPoint)
        #
        #     # Jump to the next vertex.
        #     geometry_iterator.next()


def nodeCreator():
    """creates the node
    """
    print 'nodeCreate start'
    return_data = OpenMayaMPx.asMPxPtr(RandomizeDeformer())
    print 'nodeCreate stop'
    return return_data


def nodeInitializer():
    """initializes the node
    """
    print 'nodeInitialize is running!'
    pass


def initializePlugin(obj):
    """
    """
    print 'initializePlugin start'
    plugin = OpenMayaMPx.MFnPlugin(obj, "Erkan Ozgur Yilmaz", "0.1.0", "Any")
    try:
        plugin.registerNode(
            node_type_name,
            plugin_id,
            nodeCreator,
            nodeInitializer,
            OpenMayaMPx.MPxNode.kDeformerNode
        )
    except:
        sys.stderr.write('Failed to register node: %s' % node_type_name)
    print 'initializePlugin stop'


def uninitializePlugin(mobject):
    """uninitialize the script plug-in
    """
    print 'uninitializePlugin start'
    plugin = OpenMayaMPx.MFnPlugin(mobject)
    try:
        plugin.deregisterNode(plugin_id)
    except:
        sys.stderr.write("Failed to unregister node: %s" % node_type_name)
        raise
    print 'uninitializePlugin stop'
