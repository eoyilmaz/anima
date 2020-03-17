# -*- coding: utf-8 -*-
# Copyright (c) 2018-2020, Erkan Ozgur Yilmaz
#
# This module is part of anima and is released under the MIT
# License: http://www.opensource.org/licenses/MIT
"""UI for baking crowd simulations to individual RSProxies and creating
necessary nodes to be able to render them

"""

import hou


def create_bake_setup():
    """creates the necessary nodes to bake the crowd to RSProxies
    """
    nodes = hou.selectedNodes()
    if not nodes:
        raise RuntimeError("Select a node please")

    node_to_bake = nodes[0]

    # get the parent
    parent_node = node_to_bake.parent()

    nodes_created = []

    # *************************************
    #
    # The Bake Branch
    #
    # *************************************

    # create a for each loop
    block_begin_node = parent_node.createNode("block_begin")
    # set it to "Fetch Piece or Point"
    block_begin_node.parm("method").set(1)
    block_begin_node.setInput(0, node_to_bake)
    nodes_created.append(block_begin_node)

    # create attr wrangle
    attr_wrangle_node = parent_node.createNode("attribwrangle")
    attr_wrangle_node.parm("snippet").set("@P = {0, 0, 0};")
    attr_wrangle_node.setInput(0, block_begin_node)
    nodes_created.append(attr_wrangle_node)

    # Redshift Proxy Output
    rs_proxy_output = parent_node.createNode("Redshift_Proxy_Output")
    rs_proxy_output.parm("RS_archive_file").set(
        '$HIP/Outputs/rs/$F/Crowd_`detail(-1, "iteration", 0)`.$F.rs'
    )
    rs_proxy_output.parm("RS_archive_removeAtt").set(False)
    rs_proxy_output.parm("RS_archive_skipFiles").set(True)
    rs_proxy_output.parm("RS_renderCamera").set("proxy_export")
    rs_proxy_output.parm("RS_multihreadLoader").set(False)
    rs_proxy_output.parm("RS_nonBlockingRendering").set(False)
    rs_proxy_output.parm("RS_addDefaultLight").set(False)
    rs_proxy_output.parm("RS_arbitraryUVMapNames").set(True)
    rs_proxy_output.setInput(0, attr_wrangle_node)
    nodes_created.append(rs_proxy_output)

    # Python node
    python_node = parent_node.createNode("python")
    python_node.parm("python").set("""# run only in batch mode
if hou.applicationName() == 'hbatch':
    rs_node = hou.node("../%s")
    rs_node.parm("execute").pressButton()""" % rs_proxy_output.name())
    python_node.setInput(0, attr_wrangle_node)
    nodes_created.append(python_node)

    # block end node
    block_end_node = parent_node.createNode("block_end")
    block_end_node.parm("itermethod").set(1)  # By Pieces or Point
    block_end_node.parm("method").set(1)  # Merge Each Iteration
    block_end_node.parm("class").set(0)  # Primitives
    block_end_node.parm("useattrib").set(0)  # Use Piece Attrib
    block_end_node.parm("blockpath").set("../%s" % block_begin_node.name())
    block_end_node.parm("templatepath").set("../%s" % block_begin_node.name())
    block_end_node.parm("stopcondition").set(0)
    block_end_node.setInput(0, python_node)
    nodes_created.append(block_end_node)

    # The second block begin node
    metadata_node = parent_node.createNode("block_begin")
    metadata_node.parm("method").set(2)  # Fetch Metadata
    metadata_node.parm("blockpath").set("../%s" % block_end_node.name())
    # also set the block path of the block_begin_node
    block_begin_node.parm("blockpath").set("../%s" % block_end_node.name())
    nodes_created.append(metadata_node)

    from anima.env.houdini import auxiliary
    # Create space input0 for rs proxy output node
    auxiliary.create_spare_input(
        rs_proxy_output, "../%s" % metadata_node.name()
    )

    # delete node
    delete_node = parent_node.createNode("delete")
    delete_node.parm("group").set("*")
    delete_node.parm("entity").set(1)
    delete_node.setInput(0, block_end_node)
    nodes_created.append(delete_node)

    # attribute delete
    attr_delete_node = parent_node.createNode("attribdelete")
    attr_delete_node.parm("ptdel").set("*")
    attr_delete_node.parm("vtxdel").set("*")
    attr_delete_node.parm("primdel").set("*")
    attr_delete_node.parm("dtldel").set("*")
    attr_delete_node.setInput(0, delete_node)
    nodes_created.append(attr_delete_node)

    # file cache node
    file_cache_node = parent_node.createNode("filecache")
    file_cache_node.parm("file").set("$TEMP/null.bgeo")
    file_cache_node.setInput(0, attr_delete_node)
    nodes_created.append(file_cache_node)

    # align the nodes
    network_editor = auxiliary.get_network_pane()
    import nodegraphalign  # this is a houdini module
    nodegraphalign.alignConnected(
        network_editor, block_begin_node, None, "down"
    )

    # select newly created nodes
    nodes_created[0].setSelected(True, True)
    for node in nodes_created:
        node.setSelected(True, False)


def do_bake():
    """bakes the crowd to RSProxies
    """
    pass


def create_render_setup():
    """creates the render setup
    """
    nodes = hou.selectedNodes()
    if not nodes:
        raise RuntimeError("Select a node please")

    node_to_bake = nodes[0]

    # get the parent
    parent_node = node_to_bake.parent()

    nodes_created = []

    # *************************************
    #
    # The Render branch
    #
    # *************************************
    # add node
    add_node = parent_node.createNode("add")
    add_node.parm("keep").set(1)
    add_node.setInput(0, node_to_bake)
    nodes_created.append(add_node)

    # the second attr delete node
    attr_delete_node = parent_node.createNode("attribdelete")
    attr_delete_node.parm("ptdel").set("*")
    attr_delete_node.parm("vtxdel").set("*")
    attr_delete_node.parm("primdel").set("*")
    attr_delete_node.parm("dtldel").set("*")
    attr_delete_node.setInput(0, add_node)
    nodes_created.append(attr_delete_node)

    # attr wrangle - load proxies
    attr_wrangle_node = parent_node.createNode("attribwrangle")
    attr_wrangle_node.parm("snippet").set("""s@instancefile = concat(
    "$HIP/Outputs/rs/", itoa(@Frame), "/Crowd_", itoa(@ptnum), ".", itoa(@Frame), ".rs"
);""")
    attr_wrangle_node.setInput(0, attr_delete_node)
    nodes_created.append(attr_wrangle_node)

    # attr wrangle - set materials
    import random
    attr_wrangle_node2 = parent_node.createNode("attribwrangle")
    attr_wrangle_node2.parm("snippet").set("""int material_ids[] = {1,2,3,4,5,6,7,8,9,10};
int material_id = material_ids[sample_discrete(len(material_ids), rand(@ptnum + %0.3f))];
s@shop_materialpath = concat("/mat/Material", itoa(material_id));
""" % random.random())
    attr_wrangle_node2.setInput(0, attr_wrangle_node)
    nodes_created.append(attr_wrangle_node2)
    # attr_wrangle_node3.setDisplayFlag(True)
    # attr_wrangle_node3.setRenderFlag(True)
    # align the nodes
    from anima.env.houdini import auxiliary
    network_editor = auxiliary.get_network_pane()
    import nodegraphalign
    nodegraphalign.alignConnected(
        network_editor, add_node, None, "down"
    )

    # select newly created nodes
    nodes_created[0].setSelected(True, True)
    for node in nodes_created:
        node.setSelected(True, False)
