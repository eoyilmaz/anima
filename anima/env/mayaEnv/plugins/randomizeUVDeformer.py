# -*- coding: utf-8 -*-
# Copyright (c) 2012-2018, Anima Istanbul
#
# This module is part of anima-tools and is released under the BSD 2
# License: http://www.opensource.org/licenses/BSD-2-Clause
"""create deformer with::

  deformer -type "randomizeUVDeformer"

"""
import sys


from maya import OpenMaya, OpenMayaMPx

node_type_name = "randomizeUVDeformer"
plugin_id = OpenMaya.MTypeId(0x00380)


class RandomizeDeformer(OpenMayaMPx.MPxDeformerNode):
    """a node to randomize uvs (for now)
    """

    aMaxOffset = OpenMaya.MObject()

    def __init__(self):
        OpenMayaMPx.MPxDeformerNode.__init__(self)

    def get_deformer_input_geometry(self, data_block, geometry_index):
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
            self.get_deformer_input_geometry(data_block, geometry_index)

        # Obtain the list of normals for each vertex in the mesh.
        mesh_fn = OpenMaya.MFnMesh(input_geometry_object)

        uv_shell_array = OpenMaya.MIntArray()
        u_array = OpenMaya.MFloatArray()
        v_array = OpenMaya.MFloatArray()
        script_util = OpenMaya.MScriptUtil(0)
        shells_ptr = script_util.asUintPtr()

        mesh_fn.getUvShellsIds(uv_shell_array, shells_ptr)
        mesh_fn.getUVs(u_array, v_array)

        max_offset_attr_handle = \
            data_block.inputValue(RandomizeDeformer.aMaxOffset)
        max_offset = max_offset_attr_handle.asInt()

        # compute and write the new uvs
        for uv_id in xrange(len(u_array)):
            shell_id = uv_shell_array[uv_id]
            offset_u = shell_id % max_offset
            u_array[uv_id] += offset_u

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
        #     normal = OpenMaya.MVector(normals[vertex_index])
        #  Cast the MFloatVector into a simple vector.
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
    return_data = OpenMayaMPx.asMPxPtr(RandomizeDeformer())
    return return_data


def nodeInitializer():
    """initializes the node
    """
    nAttr = OpenMaya.MFnNumericAttribute()

    # input position
    RandomizeDeformer.aMaxOffset = nAttr.create(
        "maxOffset", "mo", OpenMaya.MFnNumericData.kInt, 4
    )
    nAttr.setMin(1)
    nAttr.setKeyable(True)
    nAttr.setWritable(True)
    nAttr.setReadable(True)
    nAttr.setStorable(True)

    RandomizeDeformer.addAttribute(RandomizeDeformer.aMaxOffset)
    RandomizeDeformer.attributeAffects(
        RandomizeDeformer.aMaxOffset,
        OpenMayaMPx.cvar.MPxDeformerNode_outputGeom
    )

    return True


def initializePlugin(obj):
    """
    """
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


def uninitializePlugin(mobject):
    """uninitialize the script plug-in
    """
    plugin = OpenMayaMPx.MFnPlugin(mobject)
    try:
        plugin.deregisterNode(plugin_id)
    except:
        sys.stderr.write("Failed to deregister node: %s" % node_type_name)
        raise
